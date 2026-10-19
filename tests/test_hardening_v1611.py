import csv
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
import lan_discovery
import mail_quota
from pmc_manager import PMC

class HardeningTests(unittest.TestCase):
    def test_lan_canceled_before_start(self):
        flag = threading.Event(); flag.set()
        with patch.object(lan_discovery, 'probe_host') as probe, patch.object(lan_discovery, 'get_arp_table') as arp:
            self.assertEqual(lan_discovery.scan_network('192.168.1.0/30', cancel=flag), [])
            probe.assert_not_called(); arp.assert_not_called()

    def test_lan_host_failure_does_not_discard_other_results(self):
        def probe(ip, ports):
            if ip.endswith('.1'): raise OSError('unreachable')
            return dict(ip=ip, online=True, ping=True, open_ports=[], latency_ms=1)
        with patch.object(lan_discovery, 'probe_host', side_effect=probe), patch.object(lan_discovery, 'get_arp_table', return_value={}):
            rows = lan_discovery.scan_network('192.168.1.0/30')
        self.assertEqual([r['ip'] for r in rows], ['192.168.1.2'])

    def test_quota_csv_formula_escape(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'mail.csv'
            mail_quota.export_quota_csv(p, [mail_quota.QuotaResult('=2+2', 2, 10, 'OK', '@formula')])
            with p.open(encoding='utf-8-sig', newline='') as fh:
                item=list(csv.DictReader(fh))[0]
            self.assertEqual(item['Email'], "'=2+2")
            self.assertEqual(item['Detail'], "'@formula")

    def test_pmc_csv_late_invalid_row_no_partial_write(self):
        with tempfile.TemporaryDirectory() as d:
            db = PMC(Path(d)/'pmc.sqlite3')
            f = Path(d)/'input.csv'
            f.write_text('id,product,qty,due\nA,SKU,10,2026-11-01\nB,SKU,-2,2026-11-02\n', encoding='utf-8')
            with self.assertRaises(ValueError): db.import_csv(f, 'orders')
            self.assertEqual(db.orders(), [])

    def test_pmc_duplicate_input_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            db = PMC(Path(d)/'pmc.sqlite3')
            f = Path(d)/'input.csv'
            f.write_text('id,product,qty,due\nA,SKU,10,2026-11-01\nA,SKU,2,2026-11-02\n', encoding='utf-8')
            with self.assertRaises(ValueError): db.import_csv(f, 'orders')
            self.assertEqual(db.orders(), [])

    def test_pmc_export_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            db = PMC(Path(d)/'pmc.sqlite3')
            p = Path(d)/'report.csv';p.write_text('important', encoding='utf-8')
            with self.assertRaises(FileExistsError):db.report_csv(p)
            self.assertEqual(p.read_text(encoding='utf-8'), 'important')

if __name__ == '__main__': unittest.main()
