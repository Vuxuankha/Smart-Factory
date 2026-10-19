import email
import tempfile
import time
import threading
import random
import logging
from collections import defaultdict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import base64
import hashlib
import imaplib
import json
import os
import unicodedata
from contextlib import contextmanager
import re
import ssl
import shutil
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime, parseaddr, getaddresses
from email.parser import BytesHeaderParser
from pathlib import Path

SERVER = 'imap.qiye.aliyun.com'
PORT = 993
APP_NAME = 'Sao Luu Alibaba Mail V16'
VERSION = '16.0.1'



@contextmanager
def exclusive_backup_lock(destination):
    """Prevent two app processes writing to the same destination concurrently."""
    folder = Path(destination)
    folder.mkdir(parents=True, exist_ok=True)
    lockfile = folder / '.alibaba_backup.lock'
    with lockfile.open('a+b') as handle:
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                if handle.read(1) == b'':
                    handle.write(b'0')
                    handle.flush()
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise RuntimeError('Thu muc dang duoc sao luu boi mot tien trinh khac') from exc
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def csv_safe(item):
    if isinstance(item, str) and item.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + item
    return item

def clean(value, limit=95):
    value = unicodedata.normalize('NFC', str(value or 'unknown'))
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f-\x9f]', '_', value)
    value = value.strip(' .')
    if value.split('.')[0].upper() in {'CON','PRN','AUX','NUL', *(f'COM{i}' for i in range(1,10)), *(f'LPT{i}' for i in range(1,10))}:
        value = '_' + value
    # Cutting at the Windows name limit must not reintroduce trailing dots/spaces.
    value = value[:limit].rstrip(' .')
    if not value:
        return 'unknown'
    if value.split('.')[0].upper() in {'CON','PRN','AUX','NUL', *(f'COM{i}' for i in range(1,10)), *(f'LPT{i}' for i in range(1,10))}:
        value = '_' + value
    return value[:limit].rstrip(' .') or 'unknown'


def decoded(value):
    if not value:
        return ''
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return str(value)


# Conservative Windows-compatible limit (includes temporary .partial suffix).
# Windows legacy Win32 paths often fail near 260 UTF-16 code units.
MAX_PATH_UNITS = 240


def units(value):
    return len(str(value).encode('utf-16-le')) // 2


def prefix_units(value, budget):
    output = []
    spent = 0
    for ch in str(value):
        n = units(ch)
        if spent + n > budget:
            break
        output.append(ch)
        spent += n
    return ''.join(output)


def truncate_name(value, budget, extension=False):
    """Keep the recognizable beginning, and preserve the complete extension."""
    name = clean(value, 10000)
    if units(name) <= budget:
        return name
    if budget < 8:
        raise OSError('Duong dan luu qua dai, hay chon thu muc ngan hon (vi du D:\\MAIL)')
    suffix = Path(name).suffix if extension else ''
    if suffix and units(suffix) >= budget - 2:
        suffix = ''
    stem = name[:-len(suffix)] if suffix else name
    clipped = prefix_units(stem, budget - units(suffix)).rstrip(' .')
    if not clipped:
        raise OSError('Khong du cho de luu ten tep, hay chon thu muc luu ngan hon')
    return clipped + suffix


def safe_file_name(directory, original, suffix='.partial'):
    """Fit one filename into a safe full Windows path, incl. temporary extension."""
    directory = Path(directory)
    budget = MAX_PATH_UNITS - units(str(directory)) - 1 - max(units(suffix), 15)
    return truncate_name(original, budget, extension=True)


def safe_write(path, contents):
    """Atomic, durable write in the destination directory with a random temp name."""
    path = Path(path)
    if units(str(path)) > MAX_PATH_UNITS:
        raise OSError('Duong dan tep qua dai: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise OSError('Tu choi ghi qua lien ket tep: ' + str(path))
    fd, temp_path = tempfile.mkstemp(prefix='.w_', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        Path(temp_path).unlink(missing_ok=True)

def message_date(msg):
    try:
        value = parsedate_to_datetime(msg.get('Date'))
        if value:
            return value
    except Exception:
        pass
    return datetime.now(timezone.utc)


def mailbox_names(imap):
    status, rows = imap.list()
    if status != 'OK' or not rows:
        raise RuntimeError('Khong lay duoc danh sach thu muc IMAP')
    result = []
    unparsed = []
    for raw in rows:
        if not isinstance(raw, bytes):
            unparsed.append(repr(raw))
            continue
        # LIST returns: (flags) "separator" mailbox; preserve IMAP modified-UTF7 bytes.
        match = re.match(rb'^\([^)]*\)\s+(?:"(?:\\.|[^"])*"|NIL)\s+(.+)$', raw)
        if not match:
            unparsed.append(repr(raw)[:160])
            continue
        token = match.group(1).strip()
        if token.startswith(b'"') and token.endswith(b'"'):
            token = token[1:-1].replace(b'\\"', b'"').replace(b'\\\\', b'\\')
        if b'\\noselect' in raw.split(b')', 1)[0].lower():
            continue
        result.append(token)
    if unparsed:
        raise RuntimeError('IMAP LIST chua phan tich duoc %d thu muc: %s' % (len(unparsed), '; '.join(unparsed[:3])))
    if not result:
        raise RuntimeError('IMAP LIST khong co thu muc nao co the truy cap')
    return list(dict.fromkeys(result))



def readable_mailbox(mailbox):
    """Decode IMAP modified UTF-7 folder names (e.g. Vietnamese folders)."""
    text = mailbox.decode('ascii', 'replace') if isinstance(mailbox, bytes) else str(mailbox)
    def convert(match):
        encoded = match.group(1)
        if not encoded:
            return '&'
        try:
            data = encoded.replace(',', '/')
            data += '=' * (-len(data) % 4)
            return base64.b64decode(data).decode('utf-16-be')
        except Exception:
            return match.group(0)
    return re.sub(r'&([A-Za-z0-9+,]*?)-', convert, text)


def address_people(msg, header):
    """Decode RFC 2047 display names while retaining every address in To/Cc."""
    entries = []
    try:
        pairs = getaddresses(msg.get_all(header, []))
    except (TypeError, ValueError):
        pairs = []
    for label, email_address in pairs:
        name = unicodedata.normalize('NFC', decoded(label).strip())
        addr = str(email_address or '').strip()
        if name or addr:
            entries.append({'name': name, 'email': addr})
    return entries


def contact_name(person, unknown):
    if not person:
        return unknown
    return person.get('name') or person.get('email') or unknown


def full_contact(person):
    name = person.get('name', '')
    addr = person.get('email', '')
    return f'{name} <{addr}>' if name and addr and name.casefold() != addr.casefold() else (name or addr)


def contact_details(msg):
    """For names use From and To; keep all To/Cc recipients in metadata/report."""
    senders = address_people(msg, 'From')
    to_people = address_people(msg, 'To')
    cc_people = address_people(msg, 'Cc')
    sender = senders[0] if senders else {}
    main_receivers = to_people or cc_people
    first_receiver = main_receivers[0] if main_receivers else {}
    more = len(main_receivers) - 1
    recipient_folder = contact_name(first_receiver, 'Khong_ro_nguoi_nhan')
    if more > 0:
        recipient_folder += f'_va_{more}_nguoi'
    return {
        'sender_name': contact_name(sender, 'Khong_ro_nguoi_gui'),
        'sender_display': full_contact(sender),
        'sender_email': sender.get('email', ''),
        'recipient_folder': recipient_folder,
        'recipients_display': '; '.join(full_contact(p) for p in main_receivers),
        'recipients': to_people,
        'cc_display': '; '.join(full_contact(p) for p in cc_people),
        'cc': cc_people,
    }


def message_folder_name(stamp, subject, sender, uid, recipient=None, layout='date_people', budget=180):
    """Readable sorted name with both people ALWAYS preserved before the UID suffix.

    The date-first and people-first modes are lexicographically sortable in Explorer.
    On long paths, shorten each label independently rather than dropping To entirely.
    """
    if layout not in ('date_people', 'people_date', 'legacy'):
        raise ValueError('Che do sap xep thu muc khong hop le')
    day = stamp.strftime('%Y-%m-%d_%H%M')
    tail = '_UID' + str(uid)
    if layout == 'legacy':
        old_sender = parseaddr(sender)[1] or sender or 'khong_ro_nguoi_gui'
        old = f'{day}_{clean(subject or "Khong_co_tieu_de", 55)}_{clean(old_sender, 36)}'
        if budget < units(tail) + 8:
            raise OSError('Duong dan goc qua dai; chon D:\\MAIL')
        return truncate_name(old, budget - units(tail)) + tail

    pieces = [clean(sender or 'Khong_ro_nguoi_gui', 1000),
              clean(recipient or 'Khong_ro_nguoi_nhan', 1000),
              clean(subject or 'Khong_co_tieu_de', 1000)]
    if layout == 'date_people':
        # Fixed tags deliberately short to save Windows path space.
        fixed = f'{day}_GUI-_NHAN-_TD-{tail}'
    else:
        fixed = f'GUI-_NHAN-_{day}_TD-{tail}'
    room = budget - units(fixed)
    if room < 14:
        raise OSError('Duong dan goc qua dai; chon D:\\MAIL hoac C:\\MAIL')
    caps = [min(units(pieces[0]), 42), min(units(pieces[1]), 42), min(units(pieces[2]), 56)]
    # Give both correspondents some space before allocating to the subject.
    allot = [min(caps[0], 5), min(caps[1], 5), min(caps[2], 2)]
    if sum(allot) > room:
        raise OSError('Khong du cho de luu ten nguoi gui/nhan')
    remaining = room - sum(allot)
    while remaining > 0:
        progress = False
        for i in (0, 1, 2):
            if allot[i] < caps[i] and remaining:
                allot[i] += 1
                remaining -= 1
                progress = True
        if not progress:
            break
    sender_name, recipient_name, title = [
        (prefix_units(value, allowance).rstrip(' .') or '_')
        for value, allowance in zip(pieces, allot)
    ]
    if layout == 'date_people':
        name = f'{day}_GUI-{sender_name}_NHAN-{recipient_name}_TD-{title}{tail}'
    else:
        name = f'GUI-{sender_name}_NHAN-{recipient_name}_{day}_TD-{title}{tail}'
    assert units(name) <= budget
    return name


def readable_mailbox_dir(mailbox, validity):
    name = readable_mailbox(mailbox)
    hashpart = hashlib.sha256(mailbox).hexdigest()[:8]
    return clean(name.replace('/', ' - ').replace('\\', ' - '), 55) + '_box' + hashpart + '_v' + clean(validity, 20)


def tree_mailbox_name(mailbox):
    """Stable, readable mailbox names matching Explorer's mail-folder tree."""
    raw = readable_mailbox(mailbox).replace('\\', '/').strip('/')
    leaf = raw.split('/')[-1].strip()
    names = {
        'inbox': 'Inbox', 'sent': 'Sent Items', 'sent items': 'Sent Items',
        'sent messages': 'Sent Items', 'sent mail': 'Sent Items',
        'drafts': 'Drafts', 'draft': 'Drafts',
        'trash': 'Deleted Items', 'deleted items': 'Deleted Items',
        'deleted messages': 'Deleted Items',
        'junk': 'Junk Email', 'junk email': 'Junk Email',
        'spam': 'Junk Email', 'bulk mail': 'Junk Email',
    }
    normalized = leaf.casefold()
    if normalized in names:
        return names[normalized]
    # Preserve namespace identity for custom folders, avoiding ambiguous leaf names.
    return clean(raw.replace('/', ' - '), 52) + '_box' + hashlib.sha256(mailbox).hexdigest()[:6]


def tree_contact_name(mailbox, sender, recipient):
    leaf = tree_mailbox_name(mailbox)
    if leaf == 'Sent Items' or leaf == 'Drafts':
        return recipient or 'Khong_ro_nguoi_nhan'
    # Inbox and all other folders group by From, including Deleted/Junk.
    return sender or 'Khong_ro_nguoi_gui'


def named_destination(destination, account, mailbox, validity, stamp, subject, sender, uid,
                      recipient=None, layout='date_people'):
    if layout in ('year_mailbox_contact', 'year_month_mailbox_contact'):
        mailbox_label = tree_mailbox_name(mailbox)
        contact = tree_contact_name(mailbox, sender, recipient)
        # Short contact labels are sufficient to keep the total Windows path below
        # MAX_PATH_UNITS. The full headers remain in metadata.json and the .eml.
        root = Path(destination) / clean(account) / f'{stamp:%Y}'
        if layout == 'year_month_mailbox_contact':
            root = root / f'Thang {stamp:%m}'
        root = root / mailbox_label
        suffix = '_UID' + str(uid)
        fixed_name = f'{stamp:%Y-%m-%d_%H%M}_'
        # Save per-message directory under the contact. UID and UIDVALIDITY
        # prevent collisions when two messages share a timestamp and subject.
        short_validity = clean(validity, 30)
        email_tail = f'_V{short_validity}{suffix}'
        # Avoid silent collisions when contacts differ only after truncation:
        # include an immutable short hash of the full contact in the directory.
        contact_hash = hashlib.sha256(contact.encode('utf-8')).hexdigest()[:8]
        contact_fixed = '_' + contact_hash
        minimum_msg = units(fixed_name) + units(email_tail) + 8
        contact_budget = MAX_PATH_UNITS - units(str(root)) - 3 - units(contact_fixed) - minimum_msg - 32
        if contact_budget < 6:
            raise OSError('Duong dan qua dai. Hay chon D:\\MAIL hoac C:\\MAIL')
        contact_label = prefix_units(clean(contact, 1000), min(62, contact_budget)).rstrip(' .')
        contact_dir = root / (contact_label + contact_fixed)
        msg_budget = MAX_PATH_UNITS - units(str(contact_dir)) - 1 - 32
        remaining = msg_budget - units(fixed_name) - units(email_tail)
        if remaining < 8:
            raise OSError('Duong dan qua dai. Hay chon D:\\MAIL hoac C:\\MAIL')
        subject_label = prefix_units(clean(subject or 'Khong_co_tieu_de', 1000), remaining).rstrip(' .')
        name = fixed_name + subject_label + email_tail
        result = contact_dir / name
        if units(str(result)) > MAX_PATH_UNITS:
            raise OSError('Duong dan thu muc email qua dai')
        return result
    base = (Path(destination) / clean(account) /
            readable_mailbox_dir(mailbox, validity) /
            f'{stamp:%Y}' / f'{stamp:%m}')
    budget = MAX_PATH_UNITS - units(str(base)) - 1 - 32
    if budget < 50:
        raise OSError('Thu muc goc qua dai; hay chon D:\\MAIL hoac C:\\MAIL')
    return base / message_folder_name(stamp, subject, sender, uid, recipient, layout, budget)


def existing_contacts(folder):
    """Read sender/recipient for already verified V13 messages without refetching IMAP."""
    folder = Path(folder)
    try:
        meta = json.loads((folder / 'metadata.json').read_text(encoding='utf-8-sig'))
        sender = meta.get('sender_display') or meta.get('from') or ''
        recipients = meta.get('recipients_display') or meta.get('to') or ''
        if sender and recipients:
            return sender, recipients
        # Historical V13 metadata did not contain the To header. Read ONLY
        # the RFC822 header, not the entire (possibly huge) attachment/body.
        data = bytearray()
        with (folder / 'email.eml').open('rb') as file:
            while len(data) < 256 * 1024:
                line = file.readline(min(8192, 256 * 1024 - len(data)))
                if not line:
                    break
                data.extend(line)
                if line in (b'\r\n', b'\n'):
                    break
        headers = BytesHeaderParser().parsebytes(bytes(data), headersonly=True)
        fields = contact_details(headers)
        return sender or fields['sender_display'], recipients or fields['recipients_display']
    except (OSError, ValueError, TypeError, UnicodeError):
        return '', ''


def _legacy_is_complete(target):
    try:
        meta = json.loads((target / 'metadata.json').read_text(encoding='utf-8'))
        files = meta.get('attachment_files')
        return (isinstance(files, list) and len(files) == meta.get('attachments', -1) and
                all((target / f['saved_name']).is_file() for f in files))
    except (OSError, ValueError, KeyError, TypeError):
        return False



def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def unique_attachment_name(directory, proposed, claimed):
    # Truncation must never make two different attachments overwrite each other.
    candidate = safe_file_name(directory, proposed)
    if candidate.casefold() not in claimed:
        claimed.add(candidate.casefold())
        return candidate
    suffix = Path(proposed).suffix
    stem = proposed[:-len(suffix)] if suffix else proposed
    for num in range(2, 10000):
        number = f'_{num}'
        budget = MAX_PATH_UNITS - units(str(Path(directory))) - 1 - units('.partial')
        reserved = units(number) + units(suffix)
        candidate = truncate_name(stem, budget-reserved) + number + suffix
        if candidate.casefold() not in claimed:
            claimed.add(candidate.casefold())
            return candidate
    raise OSError('Qua nhieu ten dinh kem trung nhau')


def verified_email_folder(target, account=None, mailbox=None, validity=None, uid=None):
    """Never skip without verifying actual complete files IN the selected root."""
    target = Path(target)
    try:
        if not target.is_dir() or not (target / '.completed').is_file() or target.is_symlink():
            return False
        raw = target / 'email.eml'
        if raw.is_symlink() or not raw.is_file() or raw.stat().st_size <= 0:
            return False
        meta = json.loads((target / 'metadata.json').read_text(encoding='utf-8'))
        if account is not None and meta.get('account', '').casefold() != account.casefold():
            return False
        if uid is not None and str(meta.get('uid')) != str(uid):
            return False
        if validity is not None and str(meta.get('uidvalidity')) != str(validity):
            return False
        if mailbox is not None and meta.get('mailbox_imap_name') != mailbox.decode('ascii', 'replace'):
            return False
        # Old marker-only backups are NOT trusted without a recorded checksum.
        if not meta.get('eml_sha256'):
            return False
        if 'raw_bytes' in meta and int(meta['raw_bytes']) != raw.stat().st_size:
            return False
        if meta.get('eml_sha256') and file_digest(raw) != meta['eml_sha256']:
            return False
        files = meta.get('attachment_files')
        if not isinstance(files, list) or len(files) != meta.get('attachments'):
            return False
        for item in files:
            name = item.get('saved_name')
            if (not isinstance(name, str) or Path(name).name != name or
                    clean(name, 10000) != name or '/' in name or '\\' in name):
                return False
            file = target / name
            if file.is_symlink() or not file.is_file() or file.stat().st_size != int(item.get('size', -1)):
                return False
            if not item.get('sha256'):
                return False
            if item.get('sha256') and file_digest(file) != item['sha256']:
                return False
        return True
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return False


def index_verified_backups(destination, account, log=lambda line: None):
    """Find completed messages regardless of V3/V4/V5 folder naming schemes."""
    base = Path(destination) / clean(account)
    found = {}
    if not base.is_dir():
        return found
    for meta_file in base.rglob('metadata.json'):
        folder = meta_file.parent
        if meta_file.is_symlink() or folder.is_symlink():
            continue
        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
            box = meta['mailbox_imap_name']
            key = (box, str(meta['uidvalidity']), str(meta['uid']))
            if verified_email_folder(folder, account, box.encode('ascii'), key[1], key[2]):
                found[key] = folder
        except (OSError, ValueError, KeyError, TypeError, UnicodeEncodeError):
            continue
    log(f'Da xac minh {len(found)} email co day du file trong: {base}')
    return found


# -------------------------- Reliable IMAP backup --------------------------
# One immutable UID manifest per run; workers never enumerate the server again.

@dataclass(frozen=True)
class MailTask:
    mailbox: bytes
    validity: str
    uid: bytes
    label: str


class SnapshotChanged(RuntimeError):
    """UIDVALIDITY changed; continuing could associate the wrong message with UID."""


class AuthenticationDenied(RuntimeError):
    """Authentication rejected; retrying credentials is not appropriate."""


def _connect(account, password, ctx=None):
    context = ctx or ssl.create_default_context()
    if hasattr(ssl, 'TLSVersion'):
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    client = imaplib.IMAP4_SSL(SERVER, PORT, ssl_context=context, timeout=45)
    try:
        result, _ = client.login(account, password)
        if result != 'OK':
            raise AuthenticationDenied('Dang nhap IMAP bi tu choi')
    except imaplib.IMAP4.error as exc:
        _close(client)
        raise AuthenticationDenied('Tai khoan/mat khau IMAP khong duoc chap nhan') from exc
    except Exception:
        _close(client)
        raise
    return client


def _close(imap):
    if imap is not None:
        try:
            imap.logout()
        except (OSError, EOFError, imaplib.IMAP4.error, ssl.SSLError):
            pass


def quote_mailbox(mailbox):
    """Quote LIST mailbox tokens that contain IMAP specials or whitespace."""
    token = bytes(mailbox)
    if any(ch in token for ch in (b'\r', b'\n', b'\x00')):
        raise ValueError('Ten thu muc IMAP co ky tu dieu khien')
    if not re.search(rb'[\s()"\\]', token):
        return token
    return b'"' + token.replace(b'\\', b'\\\\').replace(b'"', b'\\"') + b'"'


def _selected_validity(imap, mailbox):
    status, data = imap.select(quote_mailbox(mailbox), readonly=True)
    if status != 'OK':
        raise RuntimeError('Khong duoc truy cap thu muc IMAP: ' + readable_mailbox(mailbox))
    validity_resp = imap.response('UIDVALIDITY')[1]
    value = validity_resp[0] if validity_resp and validity_resp[0] else None
    if not value:
        raise RuntimeError('May chu khong cung cap UIDVALIDITY: ' + readable_mailbox(mailbox))
    validity = value.decode('ascii', 'replace') if isinstance(value, bytes) else str(value)
    if not validity.isdecimal() or int(validity) < 1:
        raise RuntimeError('UIDVALIDITY khong hop le: ' + readable_mailbox(mailbox))
    exists = int(data[0]) if data and data[0] else 0
    return validity, exists


def discover_manifest(account, password, log):
    """Take ONE immutable snapshot of mailboxes and UID lists for all workers."""
    client = None
    tasks = []
    folders = []
    try:
        client = _connect(account, password)
        boxes = mailbox_names(client)
        for box in boxes:
            label = readable_mailbox(box)
            validity, exists = _selected_validity(client, box)
            status, reply = client.uid('SEARCH', None, 'ALL')
            if status != 'OK' or not reply or reply[0] is None:
                raise RuntimeError('SEARCH ALL that bai: ' + label)
            uids = reply[0].split()
            if any(not uid.isascii() or not uid.isdigit() or int(uid) <= 0 for uid in uids):
                raise RuntimeError('UID khong hop le: ' + label)
            if len(uids) != len(set(uids)):
                raise RuntimeError('UID bi trung: ' + label)
            folders.append({'folder': label, 'imap_name': box.decode('ascii', 'replace'),
                            'uidvalidity': validity, 'uids': len(uids), 'exists': exists})
            if exists != len(uids):
                log(f'CANH BAO: {label} EXISTS={exists}, UID SEARCH={len(uids)}; '
                    'may chu co the dang thay doi. Se doi chieu theo UID snapshot.')
            for uid in uids:
                tasks.append(MailTask(box, validity, uid, label))
            try:
                client.close()
            except imaplib.IMAP4.error:
                pass
        log(f'IMAP snapshot: {len(folders)} thu muc, {len(tasks)} UID. '
            'Moi luong xu ly danh sach co dinh nay.')
        return tasks, folders
    finally:
        _close(client)


def _fetch_message(imap, uid):
    """Fetch message without setting the Seen flag; validate RFC822.SIZE if sent."""
    status, chunks = imap.uid('FETCH', uid, '(UID RFC822.SIZE BODY.PEEK[])')
    if status != 'OK' or not chunks:
        raise RuntimeError('IMAP FETCH that bai')
    parts = [item for item in chunks if isinstance(item, tuple) and
             len(item) >= 2 and isinstance(item[1], bytes)]
    if len(parts) != 1 or not parts[0][1]:
        raise RuntimeError('IMAP tra ve khong du noi dung email')
    header, raw = parts[0][:2]
    # Reject a server response that explicitly identifies a different message.
    uid_match = re.search(rb'\bUID\s+(\d+)\b', header or b'', re.IGNORECASE)
    if uid_match and int(uid_match.group(1)) != int(uid):
        raise RuntimeError('IMAP FETCH tra ve UID khac voi UID da yeu cau')
    size_match = re.search(rb'RFC822\.SIZE\s+(\d+)', header or b'', re.IGNORECASE)
    server_size = int(size_match.group(1)) if size_match else None
    if server_size is not None and len(raw) != server_size:
        raise RuntimeError(f'Kich thuoc FETCH sai: server={server_size}, nhan={len(raw)}')
    return raw, server_size


class RateLimiter:
    """Account-wide average throughput cap, shared by all threads."""
    def __init__(self, mb_per_second, stop):
        self.speed = float(mb_per_second) * 1048576
        self.stop = stop
        self.start = time.monotonic()
        self.bytes = 0
        self.lock = threading.Lock()

    def charge(self, amount):
        if self.speed <= 0:
            return
        with self.lock:
            self.bytes += amount
            delay = self.bytes / self.speed - (time.monotonic() - self.start)
        if delay > 0:
            self.stop.wait(delay)


def _save_one(raw, task, account, destination, verified_index, server_size=None,
              layout='date_people'):
    if server_size is not None and len(raw) != server_size:
        raise RuntimeError('Kich thuoc EML khong khop voi RFC822.SIZE may chu')
    msg = email.message_from_bytes(raw)
    stamp = message_date(msg)
    people = contact_details(msg)
    target = named_destination(destination, account, task.mailbox, task.validity,
                               stamp, decoded(msg.get('Subject')),
                               (decoded(msg.get('From')) if layout == 'legacy'
                                else people['sender_name']),
                               task.uid.decode('ascii'), people['recipient_folder'],
                               layout=layout)
    uid_text = task.uid.decode('ascii')
    if verified_email_folder(target, account, task.mailbox, task.validity, uid_text):
        return target, False, decoded(msg.get('Subject')), False, people
    if target.is_symlink():
        raise OSError('Thu muc dich la symlink; tu choi ghi')
    was_incomplete = target.exists() and any(
        (target / name).exists() for name in ('email.eml', 'metadata.json', '.completed'))
    target.mkdir(parents=True, exist_ok=True)
    # Never accept a prior marker while a new save is in progress.
    (target / '.completed').unlink(missing_ok=True)
    free = shutil.disk_usage(target).free
    if free < max(len(raw) * 3, 64 * 1024 * 1024):
        raise OSError('Khong du dung luong dia: can it nhat 64MB hoac 3 lan email')
    safe_write(target / 'email.eml', raw)
    claimed = {'email.eml', 'metadata.json', '.completed'}
    attachments = []
    for part in msg.walk():
        if part.is_multipart() or not part.get_filename():
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            raise RuntimeError('Khong giai ma duoc tep dinh kem')
        original = decoded(part.get_filename())
        proposed = f'{len(attachments)+1:03d}_{clean(original, 10000)}'
        saved = unique_attachment_name(target, proposed, claimed)
        safe_write(target / saved, payload)
        attachments.append({'original_name': original, 'saved_name': saved,
                            'size': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()})
    meta = {'backup_version': VERSION, 'account': account,
            'mailbox_imap_name': task.mailbox.decode('ascii', 'replace'),
            'mailbox_display_name': task.label, 'uidvalidity': task.validity,
            'uid': uid_text, 'subject': decoded(msg.get('Subject')),
            'from': decoded(msg.get('From')), 'to': decoded(msg.get('To')),
            'cc_header': decoded(msg.get('Cc')),
            'sender_name': people['sender_name'],
            'sender_display': people['sender_display'],
            'sender_email': people['sender_email'],
            'recipient_folder_name': people['recipient_folder'],
            'recipients_display': people['recipients_display'],
            'recipients': people['recipients'],
            'cc_display': people['cc_display'],
            'cc': people['cc'], 'folder_layout': layout,
            'date': stamp.isoformat(),
            'raw_bytes': len(raw), 'imap_rfc822_size': server_size,
            'eml_sha256': hashlib.sha256(raw).hexdigest(),
            'attachments': len(attachments), 'attachment_files': attachments}
    safe_write(target / 'metadata.json', json.dumps(meta, ensure_ascii=False, indent=2).encode('utf-8'))
    safe_write(target / '.completed', b'OK')
    if not verified_email_folder(target, account, task.mailbox, task.validity, uid_text):
        (target / '.completed').unlink(missing_ok=True)
        raise RuntimeError('Xac minh du lieu sau ghi that bai')
    return target, True, meta['subject'], was_incomplete, people


def _worker(account, password, destination, tasks, verified, log, stop, event, issue, limiter, layout='date_people'):
    counts = {'saved': 0, 'skipped': 0, 'errors': 0, 'bytes': 0, 'expected': len(tasks)}
    client = None
    selected = None
    verified_count = 0
    try:
        for task in tasks:
            if stop.is_set():
                break
            identity = (task.mailbox.decode('ascii', 'replace'), task.validity, task.uid.decode('ascii'))
            old = verified.get(identity)
            if old and verified_email_folder(old, account, task.mailbox, task.validity, identity[2]):
                counts['skipped'] += 1
                verified_count += 1
                event('skipped', 0)
                prior_sender, prior_recipients = existing_contacts(old)
                issue('BO_QUA_DA_XAC_MINH', task,
                      reason='EML va tep dinh kem da xac minh', path=old,
                      sender=prior_sender, recipients=prior_recipients)
                if verified_count % 100 == 0:
                    log(f'[{task.label}] Da kiem tra va bo qua {verified_count} email hop le')
                continue
            last_error = None
            finished = False
            for attempt in range(4):
                if stop.is_set():
                    break
                try:
                    if client is None:
                        client = _connect(account, password)
                        selected = None
                    if selected != (task.mailbox, task.validity):
                        live_validity, _ = _selected_validity(client, task.mailbox)
                        if live_validity != task.validity:
                            raise SnapshotChanged('UIDVALIDITY thay doi trong khi sao luu; phai quet lai')
                        selected = (task.mailbox, task.validity)
                    raw, server_size = _fetch_message(client, task.uid)
                    target, newly_saved, subject, was_incomplete, people = _save_one(
                        raw, task, account, destination, verified, server_size, layout=layout)
                    if was_incomplete:
                        issue('CAN_TAI_LAI', task, subject=subject,
                              reason='Ban cu thieu/hong; da tai va xac minh lai', path=target,
                              sender=people['sender_display'], recipients=people['recipients_display'])
                    if newly_saved:
                        counts['saved'] += 1
                        counts['bytes'] += len(raw)
                        event('saved', len(raw))
                        limiter.charge(len(raw))
                        issue('DA_LUU', task, subject=subject,
                              reason='EML va tep dinh kem da luu va xac minh', path=target,
                              sender=people['sender_display'], recipients=people['recipients_display'])
                    else:
                        counts['skipped'] += 1
                        event('skipped', 0)
                        issue('BO_QUA_DA_XAC_MINH', task, subject=subject,
                              reason='File tai dich da duoc xac minh', path=target,
                              sender=people['sender_display'], recipients=people['recipients_display'])
                    finished = True
                    break
                except (AuthenticationDenied, SnapshotChanged):
                    raise
                except Exception as exc:
                    last_error = exc
                    _close(client)
                    client, selected = None, None
                    # Exponential backoff with jitter, including EOF/SSL/timeout.
                    log(f'UID {identity[2]} ({task.label}) loi lan {attempt+1}/4: '
                        f'{type(exc).__name__}: {str(exc).replace(password, "[REDACTED]")}')
                    if attempt < 3 and not stop.is_set():
                        stop.wait(min(3 * (2 ** attempt) + random.random(), 24))
            if not finished and not stop.is_set():
                counts['errors'] += 1
                event('error', 0)
                issue('LOI_CHUA_LUU', task, reason=str(last_error or 'Khong tai duoc').replace(password, '[REDACTED]'))
        return counts
    finally:
        _close(client)


def backup_parallel(account, password, destination, log, stop, on_message=None,
                    limit_mbps=0, on_issue=None, worker_count=3, layout='date_people'):
    if layout not in ('date_people', 'people_date', 'legacy', 'year_mailbox_contact', 'year_month_mailbox_contact'):
        raise ValueError('Che do sap xep email khong hop le')
    if not isinstance(limit_mbps, (int, float)) or not (0 <= limit_mbps <= 10000) or limit_mbps != limit_mbps or limit_mbps == float('inf'):
        raise ValueError('Gioi han toc do khong hop le')
    if worker_count not in (1, 2, 3, 5):
        raise ValueError('Chi ho tro 1, 2, 3 hoac 5 luong')
    tasks, folders = discover_manifest(account, password, log)
    verified = index_verified_backups(destination, account, log)
    uid_groups = [[] for _ in range(worker_count)]
    for idx, task in enumerate(tasks):
        uid_groups[idx % worker_count].append(task)
    result = {'saved': 0, 'skipped': 0, 'errors': 0, 'bytes': 0, 'expected': len(tasks)}
    count_lock = threading.Lock()
    limiter = RateLimiter(limit_mbps, stop)
    def event(kind, size):
        if on_message:
            with count_lock:
                on_message(kind, size)
    def issue(kind, task, subject='', reason='', path='', sender='', recipients=''):
        if on_issue:
            on_issue({'time': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                      'account': account, 'status': kind, 'folder': task.label,
                      'uid': task.uid.decode('ascii'), 'subject': str(subject),
                      'sender': str(sender), 'recipients': str(recipients),
                      'reason': str(reason), 'path': str(path)})
    with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix='IMAPBackup') as pool:
        futures = [pool.submit(_worker, account, password, destination, group, verified,
                               log, stop, event, issue, limiter, layout) for group in uid_groups if group]
        try:
            for future in as_completed(futures):
                part = future.result()
                for key in ('saved', 'skipped', 'errors', 'bytes'):
                    result[key] += part[key]
        except Exception:
            stop.set()
            for future in futures:
                future.cancel()
            raise
    handled = result['saved'] + result['skipped'] + result['errors']
    if not stop.is_set() and handled != result['expected']:
        raise RuntimeError(f'LOI DOI CHIEU: phai xu ly {result["expected"]} UID nhung chi co {handled}')
    if result['errors']:
        log(f'CHUA HOAN TAT: {result["errors"]} email tai loi, khong duoc bao thanh cong.')
    return result


def backup_one(account, password, destination, log, stop, on_message=None,
               limit_mbps=0, on_issue=None, layout='date_people', **unused):
    """Compatibility wrapper for older callers."""
    return backup_parallel(account, password, destination, log, stop, on_message,
                           limit_mbps, on_issue, worker_count=1, layout=layout)
