import tempfile
import unittest
from pathlib import Path
from pmc_manager import PMC

class PMCTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=PMC(Path(self.tmp.name)/'pmc.db')
    def tearDown(self):self.tmp.cleanup()
    def setup_data(self):
        self.db.order('SO1','A',100,'2026-10-31',5)
        self.db.set_bom('A','M1',2)
        self.db.set_stock('M1',70,20)
        self.db.center('Line A',40)
    def test_mrp_netting(self):
        self.setup_data();r=self.db.mrp()[0]
        self.assertEqual(r['required'],200);self.assertEqual(r['shortage'],110)
    def test_missing_bom(self):
        self.db.order('S1','B',10,'2026-10-25');self.assertEqual(self.db.missing_bom()[0]['product'],'B')
    def test_capacity_plan_and_late(self):
        self.setup_data();p=self.db.plan('2026-10-30',True)
        self.assertEqual(p[0]['days'],3);self.assertTrue(p[0]['late'])
        self.assertEqual(self.db.work_orders(True)[0]['id'],'WO-SO1')
    def test_pr_refresh_no_duplication(self):
        self.setup_data();self.db.create_pr();self.db.create_pr()
        self.assertEqual(len(self.db.query('SELECT * FROM requests')),1)
    def test_issue_is_atomic(self):
        self.setup_data()
        with self.assertRaises(ValueError):self.db.issue('SO1','M1',100)
        self.assertEqual(self.db.query('SELECT onhand FROM stock')[0]['onhand'],70)
        self.db.issue('SO1','M1',25)
        self.assertEqual(self.db.query('SELECT onhand FROM stock')[0]['onhand'],45)
    def test_progress_no_overfill(self):
        self.setup_data();self.db.produce('SO1',60)
        with self.assertRaises(ValueError):self.db.produce('SO1',50)
        self.assertEqual(self.db.dashboard()['completion_pct'],60)
    def test_inventory_reconciliation(self):
        self.db.set_stock('X',12,0,10)
        self.assertEqual(self.db.reconcile()[0]['difference'],-2)
    def test_scrap_variance(self):
        self.setup_data();self.db.scrap('SO1','M1',30,10)
        self.assertEqual(self.db.scrap_report()[0]['loss_percent'],50)
    def test_csv_export_and_import(self):
        f=Path(self.tmp.name)/'orders.csv';f.write_text('id,product,qty,due\nS1,P,10,2026-11-01\n',encoding='utf8')
        self.assertEqual(self.db.import_csv(f,'orders'),1)
        dest=Path(self.tmp.name)/'report.csv';self.assertEqual(self.db.report_csv(dest,'orders'),1)
        self.assertIn('S1',dest.read_text(encoding='utf-8-sig'))
    def test_invalid_negative_nan(self):
        with self.assertRaises(ValueError):self.db.set_bom('X','M',float('nan'))
        with self.assertRaises(ValueError):self.db.center('X',0)
        with self.assertRaises(ValueError):self.db.order('O','X',-1,'2026-10-21')

if __name__=='__main__':unittest.main()
