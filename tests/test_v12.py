import unittest, tempfile, json, hashlib
from pathlib import Path
from app import verified_email_folder, unique_attachment_name
class V12Tests(unittest.TestCase):
 def test_integrity_v12(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); data=b'From: a@example.com\nSubject: hello\n\nbody'; (p/'email.eml').write_bytes(data)
   m={'account':'a@example.com','mailbox_imap_name':'INBOX','uid':'10','uidvalidity':'1','raw_bytes':len(data),'attachments':0,'attachment_files':[],'backup_version':'12.0.0','eml_sha256':hashlib.sha256(data).hexdigest()}
   (p/'metadata.json').write_text(json.dumps(m)); (p/'.completed').write_text('OK')
   self.assertTrue(verified_email_folder(p,'a@example.com',b'INBOX','1','10'))
   (p/'email.eml').write_bytes(data+b'x')
   self.assertFalse(verified_email_folder(p,'a@example.com',b'INBOX','1','10'))
 def test_truncated_names_unique(self):
  with tempfile.TemporaryDirectory() as d:
   claimed=set(); x=unique_attachment_name(d,'name'*60+'.docx',claimed); y=unique_attachment_name(d,'name'*60+'.docx',claimed)
   self.assertNotEqual(x,y)
if __name__=='__main__': unittest.main()
