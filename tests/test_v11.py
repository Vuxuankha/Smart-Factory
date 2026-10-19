import tempfile
import unittest
from pathlib import Path
import app

class MailboxListTests(unittest.TestCase):
    class Fake:
        def __init__(self, rows): self.rows=rows
        def list(self): return 'OK', self.rows
    def test_mailbox_parse_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, 'chua phan tich'):
            app.mailbox_names(self.Fake([b'(\\HasNoChildren) "/" "INBOX"', b'bad-list-response']))
    def test_mailbox_normal(self):
        self.assertEqual(app.mailbox_names(self.Fake([b'(\\HasNoChildren) "/" "INBOX"', b'(\\HasNoChildren) "/" "Sent"'])), [b'INBOX', b'Sent'])
    def test_mailbox_dedup(self):
        self.assertEqual(app.mailbox_names(self.Fake([b'() "/" "INBOX"', b'() "/" "INBOX"'])), [b'INBOX'])
    def test_empty_rejected(self):
        with self.assertRaises(RuntimeError): app.mailbox_names(self.Fake([]))
if __name__=='__main__': unittest.main(verbosity=2)
