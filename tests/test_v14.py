"""V14: from/to names in folders, report and metadata, while preserving UID safety."""
import csv
import email
import json
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import patch

import mail_backend as m
from issue_journal import IssueJournal, make_sender_recipient_sorted_csv
from test_v13 import FakeServer, FastStop


def multilingual_email():
    msg = EmailMessage()
    msg['From'] = 'Nguyễn Văn A <sender@example.com>'
    msg['To'] = 'Trần Thị B <receiver@example.com>, 张伟 <zhang@example.cn>'
    msg['Cc'] = 'Lê Văn C <cc@example.vn>'
    msg['Subject'] = 'Báo cáo tháng 10 中文 🧾'
    msg['Date'] = 'Mon, 19 Oct 2026 10:30:00 +0700'
    msg.set_content('Đây là nội dung thư')
    msg.add_attachment(b'data attachment', maintype='application', subtype='octet-stream', filename='Tài liệu 中文.docx')
    return msg.as_bytes()


class V14ContactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fake = FakeServer()
        self.fake.messages[b'INBOX'][b'10'] = multilingual_email()
        self.mock = patch.object(m.imaplib, 'IMAP4_SSL', side_effect=self.fake.make_imap)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def backup(self, layout='date_people'):
        issues = []
        result = m.backup_parallel('backup@example.com', 'test-only', self.root,
                                   lambda _: None, FastStop(), on_issue=issues.append,
                                   worker_count=2, layout=layout)
        return result, issues

    def find_msg(self):
        for file in self.root.rglob('metadata.json'):
            meta = json.loads(file.read_text(encoding='utf-8'))
            if meta['uid'] == '10' and meta['mailbox_imap_name'] == 'INBOX':
                return file.parent, meta
        raise AssertionError('Missing saved UID')

    def test_name_people_and_multiple_recipients(self):
        counts, issues = self.backup()
        self.assertEqual(counts['saved'], 4)
        folder, meta = self.find_msg()
        self.assertTrue(folder.name.startswith('2026-10-19_1030_GUI-'))
        self.assertIn('Nguyễn Văn A', folder.name)
        self.assertIn('Trần Thị B', folder.name)
        self.assertIn('va_1_nguoi', folder.name)
        self.assertTrue(folder.name.endswith('_UID10'))
        self.assertEqual(meta['sender_name'], 'Nguyễn Văn A')
        self.assertEqual(meta['sender_email'], 'sender@example.com')
        self.assertEqual([x['name'] for x in meta['recipients']], ['Trần Thị B','张伟'])
        self.assertEqual(meta['cc'][0]['name'], 'Lê Văn C')
        self.assertIn('张伟', meta['recipients_display'])
        self.assertIn('Tài liệu 中文.docx', meta['attachment_files'][0]['original_name'])
        self.assertEqual(m.verified_email_folder(folder,'backup@example.com',b'INBOX','55','10'), True)
        row = next(x for x in issues if x['uid'] == '10' and x['status'] == 'DA_LUU')
        self.assertIn('Nguyễn Văn A', row['sender'])
        self.assertIn('Trần Thị B', row['recipients'])
        self.assertIn('张伟', row['recipients'])

    def test_people_first_sort_mode_and_v13_compatibility(self):
        result, _ = self.backup('people_date')
        self.assertEqual(result['saved'], 4)
        folder, meta = self.find_msg()
        self.assertTrue(folder.name.startswith('GUI-Nguyễn Văn A_NHAN-Trần Thị B'))
        self.assertEqual(meta['folder_layout'],'people_date')
        fetches = self.fake.fetch_count
        second, skipped = self.backup('legacy')
        self.assertEqual(second['saved'], 0)
        self.assertEqual(second['skipped'], 4)
        self.assertEqual(self.fake.fetch_count, fetches)
        self.assertTrue(any('Trần Thị B' in x['recipients'] for x in skipped))
        self.assertEqual(len(list(self.root.rglob('email.eml'))), 4)

    def test_legacy_layout_still_contains_recipient_metadata(self):
        self.backup('legacy')
        folder, meta = self.find_msg()
        self.assertNotIn('_NHAN-', folder.name)
        self.assertEqual(meta['recipients'][0]['name'], 'Trần Thị B')
        self.assertTrue(folder.name.endswith('_UID10'))

    def test_old_metadata_recipient_read_from_eml_header(self):
        self.backup('legacy')
        folder, meta = self.find_msg()
        for key in ('to', 'sender_display', 'recipients_display', 'recipients', 'cc_display', 'cc'):
            meta.pop(key, None)
        (folder/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False), encoding='utf-8')
        sender, recipients = m.existing_contacts(folder)
        self.assertIn('Nguyễn Văn A', sender)
        self.assertIn('Trần Thị B', recipients)
        self.assertIn('张伟', recipients)
        skip, issues = self.backup('date_people')
        self.assertEqual((skip['saved'], skip['skipped']), (0,4))
        self.assertTrue(any('张伟' in x['recipients'] for x in issues))

    def test_very_long_windows_path_keeps_both_tags_and_uid(self):
        stamp = datetime(2026,10,19,tzinfo=timezone.utc)
        for layout in ('date_people','people_date'):
            first = m.named_destination(self.root, 'backup@example.com', b'INBOX', '55', stamp,
                                        'Báo cáo 中文 🧾' * 100, 'Nguyễn' * 40, '999',
                                        'Trần 🧾' * 40, layout=layout)
            second = m.named_destination(self.root, 'backup@example.com', b'INBOX', '55', stamp,
                                         'Báo cáo 中文 🧾' * 100, 'Nguyễn' * 40, '1000',
                                         'Trần 🧾' * 40, layout=layout)
            self.assertLessEqual(m.units(str(first)),m.MAX_PATH_UNITS)
            self.assertIn('GUI-',first.name)
            self.assertIn('NHAN-',first.name)
            self.assertTrue(first.name.endswith('_UID999'))
            self.assertNotEqual(first,second)

    def test_missing_sender_or_recipient_uses_clear_fallback(self):
        msg = email.message_from_bytes(b'Subject: Only subject\r\nDate: Mon, 19 Oct 2026 09:00:00 +0700\r\n\r\nBody')
        people = m.contact_details(msg)
        self.assertEqual(people['sender_name'], 'Khong_ro_nguoi_gui')
        self.assertEqual(people['recipient_folder'], 'Khong_ro_nguoi_nhan')
        folder = m.named_destination(self.root,'backup@example.com',b'INBOX','55',
                                     datetime.now(timezone.utc),'Only subject',
                                     people['sender_name'],'777',people['recipient_folder'])
        self.assertIn('_NHAN-',folder.name)
        self.assertTrue(folder.name.endswith('_UID777'))

    def test_report_contains_sorted_from_and_to_and_formula_safe(self):
        with IssueJournal(self.root) as log:
            for a,b in [('Trần','Ngọc'),('An','Tâm'),('An','Đức'),('=HYPERLINK(1)','Tôi')]:
                log.add({'sender':a,'recipients':b,'uid':'1','status':'DA_LUU'})
        self.assertTrue(log.sorted_path.is_file())
        with log.sorted_path.open(encoding='utf-8-sig',newline='') as file:
            data=list(csv.DictReader(file))
        self.assertEqual(len(data),4)
        self.assertEqual([x['sender'] for x in data], ["'=HYPERLINK(1)",'An','An','Trần'])
        self.assertEqual([x['recipients'] for x in data if x['sender']=='An'], ['Đức','Tâm'])
        self.assertTrue((self.root/'_BAO_CAO_LOI'/'email_loi_bo_qua_moi_nhat.csv').is_file())

if __name__ == '__main__':
    unittest.main()
