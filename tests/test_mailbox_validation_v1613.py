import unittest
from app import Application

class MailboxValidationV1613(unittest.TestCase):
    def test_accept_simple_work_mail(self):
        self.assertTrue(Application.valid_mailbox_identifier('employee@factory.vn'))
    def test_reject_double_at(self):
        self.assertFalse(Application.valid_mailbox_identifier('operator@@factory.vn'))
    def test_reject_missing_domain(self):
        self.assertFalse(Application.valid_mailbox_identifier('operator@'))
    def test_reject_control_characters(self):
        self.assertFalse(Application.valid_mailbox_identifier('operator@example.com\rnext'))
    def test_reject_overlong(self):
        self.assertFalse(Application.valid_mailbox_identifier('x'*255+'@example.com'))

if __name__=='__main__':unittest.main()
