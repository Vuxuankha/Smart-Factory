import tempfile, unittest
from pathlib import Path
from pmc_advanced import PMCAdvanced

class AdvancedTest(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory();self.p=PMCAdvanced(Path(self.dir.name)/'x.db')
        c=self.p.core;c.order('SO1','P1',10,'2030-05-01');c.set_bom('P1','M1',2);c.center('A',5)
    def tearDown(self):self.dir.cleanup()
    def test_lots_and_picking(self):
        self.p.lot('L1','M1',8,'2026-01-01','2030-01-01');self.p.lot('L2','M1',10,'2026-01-02','2031-01-01')
        r=self.p.picking_suggestion('M1',11);self.assertEqual([v['qty'] for v in r['picks']],[8,3])
        self.assertEqual(r['unfilled'],0)
    def test_invalid_date(self):
        with self.assertRaises(ValueError): self.p.lot('L1','M1',1,'2026-01-02','2025-12-01')
    def test_safety(self):self.assertEqual(self.p.safety_stock(10,4,2)['reorder_point'],46.6)
    def test_maintenance_conflict(self):
        self.p.core.plan('2030-01-01',persist=True)
        self.p.maintenance('A','2030-01-02','2030-01-03','Maintenance')
        self.assertEqual(len(self.p.maintenance_conflicts()),1)
    def test_kit_bom_guard(self):
        self.p.allocate_kit('SO1','M1',20)
        with self.assertRaises(ValueError):self.p.allocate_kit('SO1','M1',21)
    def test_matching(self):
        self.p.record_po('PO1','M1',10,5)
        self.p.record_receipt('GR1','PO1',10)
        self.p.record_invoice('INV1','PO1',11,5)
        self.assertEqual(self.p.matching()[0]['status'],'MISMATCH')
    def test_subcontract_and_delay(self):
        self.p.subcontract('S1','SO1','Vendor',4,'2020-01-01')
        self.assertEqual(len(self.p.late_subcontracts()),1)
        self.p.delay('SO1','MATERIAL','late')
        self.assertEqual(self.p.delay_summary()[0]['incidents'],1)
    def test_eco_and_audit(self):
        result=self.p.eco('P1','A','B')
        self.assertEqual(result['affected_orders'][0]['id'],'SO1')
        self.assertTrue(self.p.audit_log())
if __name__=='__main__':unittest.main()
