"""Regression tests for V15 physical year/mailbox/contact hierarchy."""
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
import mail_backend as m
from test_v13 import FakeServer, FastStop
from test_v14 import multilingual_email

class V15TreeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.fake=FakeServer()
        self.fake.messages[b'INBOX'][b'10']=multilingual_email()
        self.fake.messages[b'Sent'][b'10']=multilingual_email()
        self.mock=patch.object(m.imaplib,'IMAP4_SSL',side_effect=self.fake.make_imap)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def test_inbox_groups_by_sender_and_sent_by_recipient(self):
        result=m.backup_parallel('backup@example.com','test-only',self.root,lambda line:None, FastStop(),worker_count=2,layout='year_mailbox_contact')
        self.assertEqual(result['errors'],0)
        files=list(self.root.rglob('metadata.json'))
        self.assertTrue(files)
        for meta in files:
            parts=meta.parts
            self.assertIn('2026',parts)
            if 'Inbox' in parts and meta.parent.name.endswith('_UID10'):
                self.assertIn('Nguyễn Văn A', meta.parent.parent.name)
            if 'Sent Items' in parts and meta.parent.name.endswith('_UID10'):
                self.assertIn('Trần Thị B',meta.parent.parent.name)
        again=m.backup_parallel('backup@example.com','test-only',self.root,lambda line:None,FastStop(),worker_count=2,layout='year_mailbox_contact')
        self.assertEqual(again['saved'],0)
        self.assertEqual(again['skipped'],result['expected'])

    def test_old_layout_is_not_moved_or_downloaded_again(self):
        first=m.backup_parallel('backup@example.com','test-only',self.root,lambda line:None,FastStop(),worker_count=1,layout='date_people')
        existing={p for p in self.root.rglob('metadata.json')}
        second=m.backup_parallel('backup@example.com','test-only',self.root,lambda line:None,FastStop(),worker_count=1,layout='year_mailbox_contact')
        self.assertEqual(second['saved'],0)
        self.assertEqual(second['skipped'],first['expected'])
        self.assertEqual(existing,{p for p in self.root.rglob('metadata.json')})

    def test_long_contact_keeps_bounded_path_and_distinct_uid(self):
        stamp=datetime(2026,10,19,tzinfo=timezone.utc)
        args=(self.root,'backup@example.com',b'INBOX','55',stamp,'书面报告'*200,'Nguyễn'*150)
        a=m.named_destination(*args,'10','Trần'*120,layout='year_mailbox_contact')
        b=m.named_destination(*args,'11','Trần'*120,layout='year_mailbox_contact')
        self.assertLessEqual(m.units(a),m.MAX_PATH_UNITS)
        self.assertNotEqual(a,b)
        self.assertEqual(a.parent,b.parent)
        self.assertTrue(a.name.endswith('_UID10'))

    def test_custom_mailbox_hash_and_fallback(self):
        self.assertEqual(m.tree_mailbox_name(b'INBOX'),'Inbox')
        self.assertEqual(m.tree_mailbox_name(b'Trash'),'Deleted Items')
        self.assertEqual(m.tree_contact_name(b'Sent','A','B'),'B')
        self.assertEqual(m.tree_contact_name(b'INBOX','A','B'),'A')
        self.assertNotEqual(m.tree_mailbox_name(b'Folder/A'),m.tree_mailbox_name(b'Other/A'))

if __name__=='__main__': unittest.main()
