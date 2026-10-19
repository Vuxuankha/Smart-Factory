import os
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch
from auth_local import AuthStore
from auth_ui import AuthDialog
from app import Application

PASSWORD='SeparateAccountPassword2026!'

@unittest.skipUnless(os.environ.get('DISPLAY'),'Needs X display')
class AuthGuiFlowV1613(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=AuthStore(Path(self.tmp.name)/'a.sqlite3')
        self.root=tk.Tk();self.root.withdraw()
        self.app=None
    def tearDown(self):
        self.root.destroy();self.tmp.cleanup()

    def test_first_registration_starts_application_without_mail_account(self):
        def logged_in(session):self.app=Application(self.root,session,self.store)
        gate=AuthDialog(self.root,self.store,logged_in)
        gate.username.insert(0,'rootadmin')
        gate.fullname.insert(0,'Factory IT')
        gate.password.insert(0,PASSWORD)
        gate.confirm.insert(0,PASSWORD)
        gate.submit()
        self.root.update()
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.session.role,'it_admin')
        self.assertEqual(self.app.account.get(),'')
        self.assertTrue(self.app.main_panel.winfo_exists())

    def test_login_existing_registered_admin(self):
        self.store.register('rootadmin',PASSWORD)
        result=[]
        gate=AuthDialog(self.root,self.store,lambda session:result.append(session))
        self.assertEqual(gate.form,'login')
        gate.username.insert(0,'rootadmin')
        gate.password.insert(0,PASSWORD)
        gate.submit()
        self.assertEqual(len(result),1)
        self.assertEqual(result[0].username,'rootadmin')

    def test_employee_registration_waits_admin(self):
        self.store.register('rootadmin',PASSWORD)
        gate=AuthDialog(self.root,self.store,lambda s:None)
        gate.toggle()
        gate.username.insert(0,'worker123')
        gate.fullname.insert(0,'Worker 123')
        gate.password.insert(0,PASSWORD)
        gate.confirm.insert(0,PASSWORD)
        with patch('auth_ui.messagebox.showinfo') as alert:
            gate.submit()
            alert.assert_called_once()
        self.assertEqual(self.store.list_users(self.store.authenticate('rootadmin',PASSWORD))[0]['username'],'worker123')
        gate.win.destroy()

if __name__=='__main__':unittest.main()
