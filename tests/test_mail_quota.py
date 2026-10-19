import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mail_quota import QuotaResult, parse_storage_quota, probe_quota, export_quota_csv

class QuotaTests(unittest.TestCase):
    def test_parse_rfc2087_kib(self):
        self.assertEqual(parse_storage_quota([b'(STORAGE 1024 4096)']), (1048576, 4194304))
    def test_none_when_unsupported_resource(self):
        self.assertEqual(parse_storage_quota([b'(MESSAGE 4 100)']), (None,None))
    def test_remaining(self):
        result=QuotaResult('test@example.com', 30,100,'OK')
        self.assertEqual(result.free_bytes,70)
        self.assertEqual(result.percent,30)
    def test_no_quota_capability(self):
        class MockIMAP:
            capabilities=(b'IMAP4rev1',)
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def login(self,*args):return 'OK', []
        with patch('mail_quota.imaplib.IMAP4_SSL',return_value=MockIMAP()):
            self.assertEqual(probe_quota('test@example.com','secret').status,'UNSUPPORTED')
    def test_csv_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'results.csv'
            export_quota_csv(path,[QuotaResult('test@example.com',100,200,'OK')])
            self.assertIn('test@example.com',path.read_text(encoding='utf-8-sig'))
            with self.assertRaises(FileExistsError):export_quota_csv(path,[])

if __name__=='__main__':unittest.main()
