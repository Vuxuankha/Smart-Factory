"""GUI regression cases for distinct app/mail identity and responsive dark layout."""
import os
import tkinter as tk
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock
from app import Application
from auth_local import AuthStore, Session
from auth_ui import AuthDialog

PASS='SeparatePass2026!'

@unittest.skipUnless(os.environ.get('DISPLAY'), 'Requires a display or xvfb-run')
class IndustrialUIV1613(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.store=AuthStore(Path(self.tmp.name)/'accounts.sqlite3')
        self.store.register('rootadmin',PASS)
        self.admin=self.store.authenticate('rootadmin',PASS)
        self.root=tk.Tk()
        self.root.withdraw()
        self.app=Application(self.root,self.admin,self.store)
        self.root.update()

    def tearDown(self):
        try:self.root.destroy()
        finally:self.tmp.cleanup()

    def test_01_main_window_has_real_three_lanes(self):
        for obj in (self.app.sidebar,self.app.main_panel,self.app.quick):
            self.assertTrue(obj.winfo_exists())

    def test_02_console_at_bottom(self):
        self.assertEqual(self.app.logs_card.pack_info()['side'],'bottom')

    def test_03_main_scrolling_supported(self):
        self.assertIsInstance(self.app.main_viewport,tk.Canvas)
        self.assertTrue(self.app.main_viewport.cget('yscrollcommand'))

    def test_04_no_mail_password_on_local_diagnostics(self):
        with patch('app.simpledialog.askstring') as prompt, patch.object(self.app,'_diagnostic_worker',return_value=None):
            self.app.diagnose()
            prompt.assert_not_called()

    def test_05_no_mail_password_open_pmc(self):
        with patch('app.simpledialog.askstring') as prompt:
            ui=self.app.open_pmc('mrp')
            self.root.update()
            prompt.assert_not_called()
            self.assertEqual(ui.notebook.select(),str(ui.tabs['mrp']))
            ui.win.destroy()

    def test_06_no_mail_password_open_infrastructure(self):
        with patch('app.simpledialog.askstring') as prompt:
            ui=self.app.open_infrastructure('monitor')
            self.root.update()
            prompt.assert_not_called()
            self.assertTrue(ui.win.winfo_exists())
            ui.win.destroy()

    def test_07_reopen_pmc_reuses_one_window(self):
        first=self.app.open_pmc('mrp')
        second=self.app.open_pmc('orders')
        self.assertIs(first,second)
        self.assertEqual(first.notebook.select(),str(first.tabs['orders']))
        first.win.destroy()

    def test_08_reopen_infra_reuses_one_window(self):
        first=self.app.open_infrastructure('ticket')
        second=self.app.open_infrastructure('monitor')
        self.assertIs(first,second)
        self.assertEqual(first.notebook.select(),str(first.tabs['monitor']))
        first.win.destroy()

    def test_09_console_toggle_shortcut(self):
        self.app.toggle_logs()
        self.assertEqual(self.app.log_details.winfo_manager(),'pack')
        self.app.toggle_logs()
        self.assertEqual(self.app.log_details.winfo_manager(),'')
        self.assertTrue(self.root.bind('<Control-l>'))

    def test_10_sidebar_toggle_keeps_navigation(self):
        old=self.app.sidebar.cget('width')
        self.app.toggle_sidebar()
        self.assertNotEqual(self.app.sidebar.cget('width'),old)
        self.app.toggle_sidebar()
        self.assertEqual(self.app.sidebar.cget('width'),old)

    def test_11_system_metrics_not_fabricated(self):
        self.app.refresh_health()
        self.assertIn('GB trống',self.app.health_var.get())
        self.assertTrue(self.app.metric_cards['cpu'].value.get())

    def test_12_user_name_in_header(self):
        self.assertIn('rootadmin',self.app.identity_var.get())

    def test_13_multi_mail_mode_not_app_admin_role(self):
        self.app.mode.set('admin');self.app.switch_mode()
        self.assertEqual(self.app.session.role,'it_admin')
        self.assertEqual(self.app.multi_frame.winfo_manager(),'pack')

    def test_14_auth_roles_on_nav(self):
        self.assertTrue(self.app.can_access_nav(3))
        self.app.session=Session('auditor1','auditor','Auditor')
        self.assertFalse(self.app.can_access_nav(3))
        self.assertFalse(self.app.can_access_nav(4))
        self.assertTrue(self.app.can_access_nav(6))

    def test_15_no_network_access_for_employee(self):
        self.app.session=Session('employee1','employee','Employee')
        with patch('app.messagebox.showwarning') as warn:
            self.assertIsNone(self.app.open_network_manager())
            warn.assert_called_once()

    def test_16_no_running_backup_can_logout(self):
        self.app.active=True
        with patch('app.messagebox.showinfo') as warn:
            self.app.logout()
            warn.assert_called_once()
            self.assertTrue(self.app.shell.winfo_exists())

    def test_17_password_prompt_only_explicit_imap_action(self):
        self.app.account.set('tester@example.org')
        self.app.destination.set(self.tmp.name)
        with patch('app.simpledialog.askstring',return_value=None) as prompt:
            self.app.start()
            prompt.assert_called_once()
            self.assertIn('IMAP',prompt.call_args.args[0].upper() + prompt.call_args.args[1].upper() if len(prompt.call_args.args)>1 else repr(prompt.call_args))

    def test_18_header_has_search_and_accessible_menu(self):
        self.assertTrue(hasattr(self.app,'menubar'))
        self.app.open_command_palette()
        self.root.update()
        child=[w for w in self.root.winfo_children() if isinstance(w,tk.Toplevel)]
        self.assertEqual(len(child),1)
        child[0].destroy()


@unittest.skipUnless(os.environ.get('DISPLAY'),'Requires DISPLAY')
class RegistrationScreenV1613(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.store=AuthStore(Path(self.tmp.name)/'accounts.sqlite3')
        self.root=tk.Tk();self.root.withdraw()

    def tearDown(self):
        self.root.destroy();self.tmp.cleanup()

    def test_19_first_run_registration_visible(self):
        ui=AuthDialog(self.root,self.store,lambda session:None)
        self.assertEqual(ui.form,'register')
        self.assertTrue(ui.win.winfo_exists())
        ui.win.destroy()

    def test_20_after_admin_login_screen_visible(self):
        self.store.register('rootadmin',PASS)
        ui=AuthDialog(self.root,self.store,lambda session:None)
        self.assertEqual(ui.form,'login')
        ui.win.destroy()

    def test_21_registration_can_be_requested_without_mail(self):
        self.store.register('rootadmin',PASS)
        ui=AuthDialog(self.root,self.store,lambda session:None)
        ui.toggle()
        self.assertEqual(ui.form,'register')
        ui.win.destroy()

if __name__=='__main__':unittest.main()
