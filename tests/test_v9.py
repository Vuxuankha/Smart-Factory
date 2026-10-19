import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from app import safe_file_name, unique_attachment_name, safe_write, verified_email_folder, file_digest

class V9Tests(unittest.TestCase):
    def test_names_and_collision(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / 'Thu muc'
            dest.mkdir()
            claimed = set()
            a = unique_attachment_name(dest, 'Báo cáo中文' * 35 + '.pdf', claimed)
            b = unique_attachment_name(dest, 'Báo cáo中文' * 35 + '.pdf', claimed)
            self.assertNotEqual(a.casefold(), b.casefold())
            self.assertTrue(a.endswith('.pdf') and b.endswith('.pdf'))
            self.assertLessEqual(len(str(dest / a).encode('utf-16-le'))//2+8,240)

    def test_integrity_and_missing(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            raw=b'From: a@example.com\r\nSubject: test\r\n\r\nhello'
            attachment=b'HELLO'
            safe_write(folder/'email.eml',raw)
            safe_write(folder/'001_Hop_dong.docx',attachment)
            meta={'account':'a@example.com','mailbox_imap_name':'INBOX','uid':'12','uidvalidity':'25',
                  'raw_bytes':len(raw),'eml_sha256':hashlib.sha256(raw).hexdigest(),
                  'attachments':1,'attachment_files':[{'saved_name':'001_Hop_dong.docx','size':len(attachment),
                          'sha256':hashlib.sha256(attachment).hexdigest()}]}
            safe_write(folder/'metadata.json',json.dumps(meta).encode())
            safe_write(folder/'.completed',b'OK')
            args=(folder,'a@example.com',b'INBOX','25','12')
            self.assertTrue(verified_email_folder(*args))
            (folder/'001_Hop_dong.docx').write_bytes(b'BYE!!')
            self.assertFalse(verified_email_folder(*args))
            (folder/'001_Hop_dong.docx').unlink()
            self.assertFalse(verified_email_folder(*args))

    def test_partial_cleanup(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'example.txt'
            safe_write(target,b'hello')
            self.assertEqual(target.read_bytes(),b'hello')
            self.assertFalse((Path(td)/'example.txt.partial').exists())

if __name__=='__main__':
    unittest.main(verbosity=2)
