import os
import tkinter as tk
import unittest
from app import Application

@unittest.skipUnless(os.environ.get('DISPLAY'), 'GUI needs DISPLAY')
class ThreeLaneUITests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = Application(self.root)
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def test_three_lanes_and_shortcuts_present(self):
        self.assertTrue(self.app.sidebar.winfo_exists())
        self.assertTrue(self.app.main_panel.winfo_exists())
        self.assertTrue(self.app.quick.winfo_exists())
        for hotkey in ('<Control-Return>', '<Control-Shift-s>', '<Control-l>', '<Control-k>'):
            self.assertTrue(self.root.bind(hotkey), hotkey)

    def test_bottom_console_toggle(self):
        self.assertEqual(self.app.log_details.winfo_manager(), '')
        self.app.toggle_logs()
        self.assertEqual(self.app.log_details.winfo_manager(), 'pack')
        self.app.toggle_logs()
        self.assertEqual(self.app.log_details.winfo_manager(), '')

    def test_quick_search_opens(self):
        self.app.open_command_palette()
        self.root.update()
        matching = [x for x in self.root.winfo_children() if isinstance(x, tk.Toplevel)]
        self.assertEqual(len(matching), 1)
        matching[0].destroy()

    def test_health_not_simulated(self):
        self.app.refresh_health()
        self.assertIn('GB trống', self.app.health_var.get())

if __name__ == '__main__': unittest.main()
