import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import infra_manager as m

class InfrastructureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.db=m.Store(self.root/'test.sqlite')
    def tearDown(self): self.tmp.cleanup()
    def test_asset_and_tcp_check(self):
        self.db.add_asset('SW','127.0.0.1','switch',1)
        with patch.object(m.socket,'create_connection',side_effect=OSError('down')):
            result=self.db.check_assets(timeout=.01)
        self.assertEqual(result[0]['status'],'DOWN')
    def test_asset_reject_invalid_port(self):
        with self.assertRaises(ValueError):self.db.add_asset('a','127.0.0.1',port=0)
    def test_ticket_lifecycle(self):
        tid=self.db.add_ticket('Printer down','Office','High','HR')
        self.db.set_ticket(tid,'Resolved','IT A')
        self.assertEqual(self.db.tickets()[0]['status'],'Resolved')
        path=self.root/'tickets.csv'
        self.assertEqual(self.db.export_tickets(path),1)
        self.assertTrue(path.exists())
    def test_ipam_reserve_different(self):
        a=self.db.allocate_ip('192.168.42.0/29','Scanner',reserved=['192.168.42.1'])
        b=self.db.allocate_ip('192.168.42.0/29','Printer',reserved=['192.168.42.1'])
        self.assertEqual(a,'192.168.42.2');self.assertNotEqual(a,b)
    def test_ipam_reject_large(self):
        with self.assertRaises(ValueError):self.db.allocate_ip('10.0.0.0/8','a')
    def test_backup_and_verify(self):
        src=self.root/'source';src.mkdir();(src/'a.txt').write_text('hello')
        target=self.root/'backup'
        self.assertEqual(m.backup_folder(src,target),1)
        self.assertEqual(m.verify_backup(target),(1,[]))
        (target/'a.txt').write_text('different')
        self.assertEqual(m.verify_backup(target)[1],['a.txt'])
    def test_backup_refuses_overwrite_or_nested(self):
        src=self.root/'src';src.mkdir()
        with self.assertRaises(ValueError):m.backup_folder(src,src/'copy')
        target=self.root/'existing';target.mkdir()
        with self.assertRaises(FileExistsError):m.backup_folder(src,target)
    def test_ad_draft_does_not_execute(self):
        self.assertIn('-WhatIf',m.draft_access_script('alice','Employees'))
        with self.assertRaises(ValueError):m.draft_access_script("x';Remove-Item C:\\",'Employees')
    def test_cleanup_is_preview_only(self):
        f=self.root/'cache';f.mkdir();(f/'file.log').write_text('keep')
        import os,time
        os.utime(f/'file.log',(time.time()-50*86400,time.time()-50*86400))
        self.assertEqual(len(m.old_files_preview(f,30)),1)
        self.assertTrue((f/'file.log').exists())

if __name__=='__main__':unittest.main()
