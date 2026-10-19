import unittest
import tkinter as tk
from app import Application
from pmc_ui import PMCWindow
from infra_ui import InfraWindow

@unittest.skipUnless(bool(__import__('os').environ.get('DISPLAY')), 'GUI needs DISPLAY')
class UIRegressionTests(unittest.TestCase):
    def setUp(self):
        self.root=tk.Tk();self.root.withdraw();self.app=Application(self.root)
        self.root.update()
    def tearDown(self):
        self.root.destroy()
    def test_admin_switch_keeps_account_selection(self):
        self.app.account.set('example@example.com')
        self.app.mode.set('admin');self.app.switch_mode();self.root.update()
        self.assertTrue(self.app.multi_frame.winfo_manager() == 'pack')
        self.assertIn('example@example.com',self.app.accounts_box.get('1.0','end'))
        self.app.mode.set('employee');self.app.switch_mode();self.root.update()
        self.assertEqual(self.app.single_frame.winfo_manager(),'pack')
        self.assertEqual(self.app.account.get(),'example@example.com')
    def test_open_windows_and_select_pmc(self):
        pmc=PMCWindow(self.root,'mrp');self.root.update()
        self.assertEqual(pmc.notebook.select(),str(pmc.tabs['mrp']))
        self.assertTrue(pmc.section_choice.get().startswith('MC'))
        infra=InfraWindow(self.root,'ticket');self.root.update()
        self.assertTrue(infra.win.winfo_exists())
        infra.win.destroy();pmc.win.destroy()
if __name__=='__main__':unittest.main()
