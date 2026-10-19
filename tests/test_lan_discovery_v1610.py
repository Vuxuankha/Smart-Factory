import unittest
from unittest.mock import patch
import lan_discovery as d

class LANDiscoveryTests(unittest.TestCase):
    def test_private_small_subnet(self):
        self.assertEqual(str(d.validate_network('192.168.5.22/24')), '192.168.5.0/24')
    def test_blocks_public_and_broad(self):
        for subnet in ('8.8.8.0/24','192.168.0.0/16','10.0.0.0/8','invalid'):
            with self.subTest(subnet=subnet), self.assertRaises(ValueError):
                d.validate_network(subnet)
    def test_detects_tcp_without_ping(self):
        class FakeSocket:
            def __enter__(self): return self
            def __exit__(self,*args): pass
        def conn(args,timeout):
            if args[1] == 80:return FakeSocket()
            raise OSError('closed')
        with patch.object(d,'ping_host',return_value=False), patch.object(d.socket,'create_connection',side_effect=conn):
            result=d.probe_host('192.168.1.1',ports=(80,443))
        self.assertTrue(result['online'])
        self.assertFalse(result['ping'])
        self.assertEqual(result['open_ports'],[80])
    def test_scan_collects_only_responsive(self):
        def probe(ip,ports):return {'ip':ip,'online':ip.endswith('.1'),'ping':True,'open_ports':[],'latency_ms':1.0}
        with patch.object(d,'probe_host',side_effect=probe),patch.object(d,'get_arp_table',return_value={'192.168.1.1':'AA:BB:CC:DD:EE:FF'}):
            rows=d.scan_network('192.168.1.0/30',workers=2)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['mac'],'AA:BB:CC:DD:EE:FF')
if __name__=='__main__':unittest.main()
