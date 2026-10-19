"""Regression tests for V16 physical year/month/mailbox/contact hierarchy."""
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import mail_backend as m
from test_v13 import FakeServer, FastStop
from test_v14 import multilingual_email

class V16Tests(unittest.TestCase):
    def test_year_month_inbox_sent_and_uid(self):
        with tempfile.TemporaryDirectory() as directory:
            server=FakeServer()
            server.messages[b'INBOX'][b'10']=multilingual_email()
            server.messages[b'Sent'][b'10']=multilingual_email()
            with patch.object(m.imaplib,'IMAP4_SSL',side_effect=server.make_imap):
                first=m.backup_parallel('new@example.com','test-only',directory,lambda x:None,FastStop(),worker_count=2,layout='year_month_mailbox_contact')
                self.assertEqual(first['errors'],0)
                metas=list(Path(directory).rglob('metadata.json'))
                self.assertGreaterEqual(len(metas),2)
                for item in metas:
                    self.assertIn('2026',item.parts)
                    self.assertIn('Thang 10',item.parts) if item.parent.name.endswith('_UID10') else None
                    if 'Inbox' in item.parts and item.parent.name.endswith('_UID10'):self.assertIn('Nguyễn Văn A',item.parent.parent.name)
                    if 'Sent Items' in item.parts and item.parent.name.endswith('_UID10'):self.assertIn('Trần Thị B',item.parent.parent.name)
                again=m.backup_parallel('new@example.com','test-only',directory,lambda x:None,FastStop(),worker_count=2,layout='year_month_mailbox_contact')
                self.assertEqual(again['saved'],0)
                self.assertEqual(again['skipped'],first['expected'])
    def test_month_padding_and_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            args=(directory,'acc@example.com',b'INBOX','99')
            jan=m.named_destination(*args,datetime(2026,1,3,tzinfo=timezone.utc),'Subject','Sender','10','Recipient',layout='year_month_mailbox_contact')
            nov=m.named_destination(*args,datetime(2026,11,3,tzinfo=timezone.utc),'Subject','Sender','11','Recipient',layout='year_month_mailbox_contact')
            self.assertIn('Thang 01',jan.parts)
            self.assertIn('Thang 11',nov.parts)
            self.assertNotEqual(jan,nov)
            self.assertLessEqual(m.units(jan),m.MAX_PATH_UNITS)
if __name__=='__main__':unittest.main()
