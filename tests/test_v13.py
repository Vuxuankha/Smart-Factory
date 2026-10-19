"""Integration-style tests. All IMAP mailboxes are FAKE; no network or real emails."""
import email
import hashlib
import io
import json
import tempfile
import threading
import unittest
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import patch

import mail_backend as m
from issue_journal import IssueJournal
from kiem_tra import scan_local


class FastStop:
    def is_set(self): return False
    def wait(self, _): return False
    def set(self): return None


def sample(subject='Bao cao 中文', attach=True, body='Hello'):
    message = EmailMessage()
    message['From'] = 'person@example.com'
    message['To'] = 'backup@example.com'
    message['Date'] = 'Sun, 18 Oct 2026 18:00:00 +0700'
    message['Subject'] = subject
    message.set_content(body)
    if attach:
        message.add_attachment(b'hello doc', maintype='application', subtype='octet-stream', filename='Bao cao 中文.docx')
        message.add_attachment(b'another', maintype='application', subtype='octet-stream', filename='Bao cao 中文.docx')
    return message.as_bytes()


class FakeServer:
    def __init__(self):
        self.messages = {b'INBOX': {b'10': sample('Hop dong - thang 10'), b'11': sample('Bao cao 中 文')},
                         b'Sent': {b'7': sample('Don hang di')},
                         b'Trash': {b'5': sample('File cu')}}
        self.validities = {b'INBOX': '55', b'Sent': '66', b'Trash': '77'}
        self.list_count = 0
        self.search_count = 0
        self.fetch_count = 0
        self.fetched_uids = []
        self.active = 0
        self.fail_first = set()
        self.failed = set()
        self.lock = threading.Lock()

    def make_imap(self, *args, **kwargs):
        server = self
        class Client:
            def __init__(self):
                self.mailbox = None
                with server.lock: server.active += 1
            def login(self, account, password):
                if password != 'test-only': raise m.imaplib.IMAP4.error('invalid credentials')
                return 'OK', [b'OK']
            def list(self):
                with server.lock: server.list_count += 1
                return 'OK', [b'(\\HasNoChildren) "/" "' + x + b'"' for x in server.messages]
            def select(self, box, readonly=True):
                if not readonly: raise AssertionError('MUST SELECT READ-ONLY')
                self.mailbox = box
                return 'OK', [str(len(server.messages[box])).encode()]
            def response(self, name):
                return name, [server.validities[self.mailbox].encode()]
            def uid(self, op, *args):
                if op.upper() == 'SEARCH':
                    with server.lock: server.search_count += 1
                    return 'OK', [b' '.join(server.messages[self.mailbox])]
                uid = args[0]
                assert op.upper() == 'FETCH'
                with server.lock:
                    server.fetch_count += 1
                    server.fetched_uids.append((self.mailbox, uid))
                    if uid in server.fail_first and uid not in server.failed:
                        server.failed.add(uid)
                        raise OSError('Simulated SSL EOF')
                raw = server.messages[self.mailbox][uid]
                head = b'1 (UID '+uid+b' RFC822.SIZE '+str(len(raw)).encode()+b' BODY[] {'+str(len(raw)).encode()+b'}'
                return 'OK', [(head, raw), b')']
            def close(self): return 'OK', [b'OK']
            def logout(self):
                if not getattr(self, 'closed', False):
                    self.closed = True
                    with server.lock: server.active -= 1
                return 'BYE', [b'OK']
        return Client()


class TestBackupV13(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.fake = FakeServer()
        self.patcher = patch.object(m.imaplib, 'IMAP4_SSL', side_effect=self.fake.make_imap)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.addCleanup(self.temp.cleanup)
        self.log = []

    def run_backup(self, workers=3):
        issues = []
        counts = m.backup_parallel('backup@example.com', 'test-only', self.directory,
                                   self.log.append, FastStop(), on_issue=issues.append,
                                   worker_count=workers)
        return counts, issues

    def test_snapshot_once_and_parallel_complete(self):
        counts, issues = self.run_backup(3)
        self.assertEqual((counts['saved'], counts['errors'], counts['expected']), (4, 0, 4))
        self.assertEqual(self.fake.list_count, 1)
        self.assertEqual(self.fake.search_count, 3)
        self.assertEqual(self.fake.active, 0)
        self.assertEqual(len([v for v in issues if v['status']=='LOI_CHUA_LUU']), 0)
        base = self.directory / 'backup@example.com'
        self.assertEqual(len(list(base.rglob('email.eml'))), 4)
        self.assertTrue(all(p.parent.joinpath('metadata.json').exists() for p in base.rglob('email.eml')))

    def test_skip_only_verified_and_redownload_corrupt_attachment(self):
        self.run_backup(3)
        prior_fetches = self.fake.fetch_count
        second, issues = self.run_backup(2)
        self.assertEqual((second['saved'], second['skipped']), (0,4))
        self.assertEqual(self.fake.fetch_count, prior_fetches)
        self.assertEqual(sum(v['status']=='BO_QUA_DA_XAC_MINH' for v in issues), 4)
        file = next(self.directory.rglob('001_*.docx'))
        file.unlink()
        third, issues = self.run_backup(2)
        self.assertEqual((third['saved'], third['skipped']), (1,3))
        self.assertEqual(len(list(self.directory.rglob('email.eml'))),4)
        self.assertEqual(scan_local(self.directory,'backup@example.com')[1], set())

    def test_recovers_transient_socket_disconnect(self):
        self.fake.fail_first.add(b'10')
        counts, _ = self.run_backup(1)
        self.assertEqual(counts['errors'], 0)
        self.assertEqual(counts['saved'], 4)
        self.assertGreaterEqual(self.fake.fetch_count, 5)
        self.assertEqual(self.fake.active, 0)

    def test_fails_closed_when_uidvalidity_changes(self):
        # Simulate UIDVALIDITY change after snapshot, before fetching.
        original = m.discover_manifest
        def discover_then_change(account,password,log):
            result = original(account,password,log)
            self.fake.validities[b'INBOX'] = '999'
            return result
        with patch.object(m,'discover_manifest',side_effect=discover_then_change):
            with self.assertRaisesRegex(m.SnapshotChanged,'UIDVALIDITY'):
                self.run_backup(1)
        self.assertEqual(self.fake.active,0)

    def test_corrupt_fetch_not_marked_complete(self):
        original = m._fetch_message
        def corrupted(imap, uid):
            raw, size = original(imap, uid)
            if uid == b'10':
                return raw[:-5], size
            return raw,size
        with patch.object(m,'_fetch_message',side_effect=corrupted):
            # Current new fetch verifies server size before returning; force source error.
            counts, issues = self.run_backup(1)
            self.assertEqual(counts['expected'],4)
            self.assertEqual(counts['saved'],3)
            self.assertEqual(counts['errors'],1)
            self.assertIn('LOI_CHUA_LUU',[x['status'] for x in issues])

    def test_suffix_survives_subject_truncation(self):
        from datetime import datetime, timezone
        a = m.named_destination(self.directory,'backup@example.com',b'INBOX','55',
                                datetime.now(timezone.utc), 'tieu de' * 100, 'a@x.vn','1')
        b = m.named_destination(self.directory,'backup@example.com',b'INBOX','55',
                                datetime.now(timezone.utc), 'tieu de' * 100, 'a@x.vn','2')
        self.assertNotEqual(a,b)
        self.assertTrue(a.name.endswith('_UID1'))
        self.assertLessEqual(m.units(str(a)),m.MAX_PATH_UNITS)

    def test_csv_journal_full_output(self):
        with IssueJournal(self.directory) as journal:
            for i in range(3450):
                journal.add({'time':'now','status':'BO_QUA_DA_XAC_MINH','uid':str(i),
                             'subject': '=HYPERLINK("bad")'})
        with journal.path.open(encoding='utf-8-sig',newline='') as handle:
            import csv
            rows=list(csv.DictReader(handle))
        self.assertEqual(len(rows),3450)
        self.assertTrue(rows[0]['subject'].startswith("'="))

    def test_rejects_bad_password(self):
        with self.assertRaises(m.AuthenticationDenied):
            m.discover_manifest('backup@example.com', 'invalid', self.log.append)
        self.assertEqual(self.fake.active, 0)

    def test_mailbox_name_quoting_for_spaces(self):
        self.assertEqual(m.quote_mailbox(b'Sent Items'), b'"Sent Items"')
        self.assertEqual(m.quote_mailbox(b'INBOX'), b'INBOX')
        with self.assertRaises(ValueError):
            m.quote_mailbox(b'bad\r\nmailbox')

    def test_atomic_writer_leaves_existing_file_if_replace_fails(self):
        with tempfile.TemporaryDirectory() as dest:
            target=Path(dest)/'data.txt'
            target.write_bytes(b'old')
            with patch.object(m.os,'replace',side_effect=OSError('disk disconnected')):
                with self.assertRaises(OSError):
                    m.safe_write(target,b'new')
            self.assertEqual(target.read_bytes(),b'old')
            self.assertEqual(sorted(x.name for x in Path(dest).iterdir()),['data.txt'])

    def test_missing_sha_never_skip_marker(self):
        with tempfile.TemporaryDirectory() as dest:
            folder=Path(dest)
            (folder/'.completed').write_bytes(b'OK')
            (folder/'email.eml').write_bytes(sample())
            (folder/'metadata.json').write_text(json.dumps({
                'account':'backup@example.com','mailbox_imap_name':'INBOX',
                'uid':'123','uidvalidity':'1','raw_bytes':len(sample()),
                'attachments':0,'attachment_files':[]}),encoding='utf-8')
            self.assertFalse(m.verified_email_folder(folder,'backup@example.com',b'INBOX','1','123'))

    def test_suspicious_metadata_attachment_path_is_not_verified(self):
        with tempfile.TemporaryDirectory() as dest:
            folder=Path(dest)
            raw=sample(attach=False)
            (folder/'.completed').write_bytes(b'OK')
            (folder/'email.eml').write_bytes(raw)
            meta={'account':'backup@example.com','mailbox_imap_name':'INBOX','uid':'123',
                  'uidvalidity':'1','raw_bytes':len(raw),
                  'eml_sha256':hashlib.sha256(raw).hexdigest(),
                  'attachments':1,'attachment_files':[{'saved_name':'../secret.txt','size':1,
                                                       'sha256':hashlib.sha256(b'x').hexdigest()}]}
            (folder/'metadata.json').write_text(json.dumps(meta),encoding='utf-8')
            self.assertFalse(m.verified_email_folder(folder,'backup@example.com',b'INBOX','1','123'))

    def test_inspection_and_usage_report(self):
        from usage_stats import UsageDB, export_reports
        self.run_backup(2)
        good,damaged=scan_local(self.directory,'backup@example.com')
        self.assertEqual(len(good),4)
        self.assertFalse(damaged)
        db=UsageDB(self.directory)
        session=db.start('backup@example.com')
        db.finish(session,{'saved':4,'skipped':0,'errors':0,'bytes':123},'completed',999)
        output=export_reports(self.directory)
        self.assertTrue((output/'lich_su_sao_luu.csv').exists())
        self.assertTrue((output/'bao_cao_sao_luu.xlsx').exists())


if __name__=='__main__':
    unittest.main(verbosity=2)
