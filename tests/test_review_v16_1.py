import math
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
import mail_backend as mb

class ReviewRegressionTests(unittest.TestCase):
    def test_version_matches_release(self):
        self.assertEqual(mb.APP_NAME, 'Sao Luu Alibaba Mail V16')
        self.assertEqual(mb.VERSION, '16.0.1')

    def test_windows_name_without_trailing_dot(self):
        self.assertEqual(mb.clean('abc. def', 4), 'abc')
        self.assertNotEqual(mb.clean('CON.value', 3).upper(), 'CON')

    def test_fetch_detects_mismatched_uid(self):
        class Fake:
            def uid(self, *args):
                return 'OK', [(b'1 (UID 999 RFC822.SIZE 4 BODY[] {4}', b'test')]
        with self.assertRaisesRegex(RuntimeError, 'UID'):
            mb._fetch_message(Fake(), b'10')

    def test_fetch_correct_uid(self):
        class Fake:
            def uid(self, *args):
                return 'OK', [(b'1 (UID 10 RFC822.SIZE 4 BODY[] {4}', b'test')]
        raw, size = mb._fetch_message(Fake(), b'10')
        self.assertEqual((raw, size), (b'test', 4))

    def test_bad_speed_fails_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            for value in [float('nan'), float('inf'), -1, 10001]:
                with self.assertRaises(ValueError), patch.object(mb, 'discover_manifest', side_effect=AssertionError('network should not be called')):
                    mb.backup_parallel('a@b.com', 'secret', tmp, lambda _: None, threading.Event(), limit_mbps=value)

if __name__ == '__main__':
    unittest.main()
