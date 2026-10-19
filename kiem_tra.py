"""Read-only IMAP inventory and reconciliation for V14.

No SMTP, mailbox flags, deleting or resetting of data. No password storage.
"""
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from mail_backend import (_connect, _close, _selected_validity, mailbox_names,
                          readable_mailbox, verified_email_folder, clean, csv_safe)


def scan_local(destination, account):
    """Scan local metadata ONE time for the full inspection, not once per mailbox."""
    base = Path(destination) / clean(account)
    good, damaged = set(), set()
    if not base.is_dir():
        return good, damaged
    for path in base.rglob('metadata.json'):
        try:
            meta = json.loads(path.read_text(encoding='utf-8-sig'))
            box = str(meta['mailbox_imap_name'])
            validity = str(meta['uidvalidity'])
            uid = str(meta['uid'])
            key = (box, validity, uid)
            if verified_email_folder(path.parent, account, box.encode('ascii'), validity, uid):
                good.add(key)
            else:
                damaged.add(key)
        except (OSError, ValueError, KeyError, TypeError, UnicodeEncodeError):
            continue
    return good, damaged - good


def inspect_account(account, password, destination, log, stop):
    rows = []
    good, damaged = scan_local(destination, account)
    client = None
    try:
        client = _connect(account, password)
        mailboxes = mailbox_names(client)
        log(f'{account}: phat hien {len(mailboxes)} thu muc IMAP')
        for mailbox in mailboxes:
            if stop.is_set():
                break
            encoded = mailbox.decode('ascii', 'replace')
            label = readable_mailbox(mailbox)
            row = {'account': account, 'folder': label, 'imap_folder': encoded,
                   'uidvalidity': '', 'server_exists': '', 'server_uids': '',
                   'locally_saved': '', 'missing': '', 'damaged': '', 'status': ''}
            selected = False
            try:
                validity, exists = _selected_validity(client, mailbox)
                selected = True
                row['uidvalidity'] = validity
                status, reply = client.uid('SEARCH', None, 'ALL')
                if status != 'OK' or not reply or reply[0] is None:
                    raise RuntimeError('UID SEARCH khong thanh cong')
                uids = {uid.decode('ascii') for uid in reply[0].split()}
                row['server_exists'] = exists
                row['server_uids'] = len(uids)
                row['locally_saved'] = len([u for u in uids if (encoded, validity, u) in good])
                row['missing'] = len(uids) - row['locally_saved']
                row['damaged'] = len([u for u in uids if (encoded, validity, u) in damaged])
                row['status'] = ('OK' if exists == len(uids) else
                                 'CANH BAO: so EXISTS khac UID SEARCH')
                log(f'{label}: may chu={len(uids)}, da xac minh={row["locally_saved"]}, '
                    f'thieu={row["missing"]}, hong={row["damaged"]}')
            except Exception as exc:
                row['status'] = f'LOI: {type(exc).__name__}: {str(exc).replace(password, "[REDACTED]")}'
                log(f'LOI kiem tra thu muc {label}: {row["status"]}')
            finally:
                if selected:
                    try:
                        client.close()
                    except Exception:
                        pass
            rows.append(row)
    finally:
        _close(client)
    output = Path(destination) / '_BAO_CAO_KIEM_TRA'
    output.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    out = output / (re.sub(r'[^A-Za-z0-9._-]', '_', account) + '_' + stamp + '.csv')
    fields = ('account', 'folder', 'imap_folder', 'uidvalidity', 'server_exists',
              'server_uids', 'locally_saved', 'missing', 'damaged', 'status')
    with out.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: csv_safe(row[k]) for k in fields} for row in rows])
    log(f'Da xuat doi chieu IMAP: {out}')
    return rows
