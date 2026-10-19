import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import network_manager as net


class NetworkTests(unittest.TestCase):
    def test_valid_static(self):
        self.assertEqual(net.validate_static('192.168.1.23', '255.255.255.0', '192.168.1.1', '1.1.1.1'),
                         ('192.168.1.23', '255.255.255.0', '192.168.1.1', '1.1.1.1'))

    def test_bad_static(self):
        cases = [
            ('bad', '255.255.255.0', '', ''),
            ('127.0.0.1', '255.0.0.0', '', ''),
            ('192.168.1.0', '255.255.255.0', '', ''),
            ('192.168.1.255', '255.255.255.0', '', ''),
            ('192.168.1.22', '255.255.255.0', '10.1.0.1', ''),
            ('192.168.1.22', '255.255.255.0', '', 'bad'),
            ('192.168.1.22', '255.0.255.0', '', ''),
        ]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(net.NetworkError):
                net.validate_static(*args)

    @patch.object(net, 'require_windows')
    @patch.object(net, 'adapter_names', return_value=['Wi-Fi'])
    @patch.object(net, 'run_command', return_value='ok')
    def test_static_command_argument_array(self, run, names, windows):
        net.set_static('Wi-Fi', '192.168.0.12', '255.255.255.0', '192.168.0.1', '8.8.8.8')
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0].args[0][0], 'netsh')
        self.assertIn('name=Wi-Fi', run.call_args_list[0].args[0])

    @patch.object(net, 'require_windows')
    @patch.object(net, 'adapter_names', return_value=['Ethernet'])
    @patch.object(net, 'run_command', return_value='ok')
    def test_dhcp_sets_both_ip_and_dns(self, run, names, windows):
        net.set_dhcp('Ethernet')
        self.assertEqual(run.call_count, 2)
        self.assertIn('source=dhcp', run.call_args_list[1].args[0])

    @patch.object(net, 'require_windows')
    @patch.object(net, 'adapter_names', return_value=['Ethernet'])
    def test_adapter_allowlist(self, names, windows):
        with self.assertRaises(net.NetworkError):
            net.set_dhcp('Other adapter')

    @patch.object(net, 'vpn_profiles', return_value=['Company VPN'])
    @patch.object(net, 'run_command', return_value='ok')
    def test_vpn_does_not_pass_credentials(self, run, profiles):
        net.connect_vpn('Company VPN')
        run.assert_called_once_with(['rasdial.exe', 'Company VPN'], timeout=45)
        net.disconnect_vpn('Company VPN')
        self.assertEqual(run.call_args[0][0], ['rasdial.exe', 'Company VPN', '/disconnect'])

    @patch.object(net, 'vpn_profiles', return_value=['Company VPN'])
    def test_vpn_invalid_name(self, profiles):
        with self.assertRaises(net.NetworkError):
            net.connect_vpn('unknown')

    def test_windows_only(self):
        with patch.object(net.platform, 'system', return_value='Linux'):
            with self.assertRaises(net.NetworkError):
                net.require_windows()


if __name__ == '__main__':
    unittest.main()
