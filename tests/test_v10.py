import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import app
from usage_stats import spreadsheet_safe

class RegressionV10(unittest.TestCase):
    def test_windows_safe_unicode_names(self):
        self.assertEqual(app.clean('Báo cáo 中文.pdf'), 'Báo cáo 中文.pdf')
        self.assertEqual(app.clean('CON.txt'), '_CON.txt')
        self.assertNotIn('\x7f', app.clean('a\x7fb'))
    def test_csv_injection(self):
        self.assertEqual(app.csv_safe('=1+1'), "'=1+1")
        self.assertEqual(spreadsheet_safe('  @SUM(A:A)'), "'  @SUM(A:A)")
        self.assertEqual(app.csv_safe('Báo cáo'), 'Báo cáo')
    def test_exclusive_lock(self):
        with tempfile.TemporaryDirectory() as d:
            with app.exclusive_backup_lock(d):
                with self.assertRaises(RuntimeError):
                    with app.exclusive_backup_lock(d):
                        pass
            with app.exclusive_backup_lock(d):
                pass
    def test_attachment_shortening(self):
        with tempfile.TemporaryDirectory() as d:
            longname = '合同' * 200 + '.docx'
            p = app.safe_file_name(Path(d),longname)
            self.assertTrue(p.endswith('.docx'))
            self.assertLessEqual(app.units(str(Path(d)/p))+app.units('.partial'),app.MAX_PATH_UNITS)
if __name__=='__main__': unittest.main(verbosity=2)
