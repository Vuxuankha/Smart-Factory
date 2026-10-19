import unittest
from unittest.mock import patch
import lan_discovery


class HiddenConsoleTests(unittest.TestCase):
    def test_windows_ping_is_hidden(self):
        with patch.object(lan_discovery.platform, 'system', return_value='Windows'), patch.object(lan_discovery.subprocess, 'run') as run:
            run.return_value.returncode = 0
            self.assertTrue(lan_discovery.ping_host('192.168.1.1'))
            self.assertEqual(run.call_args.kwargs['creationflags'] & 0x08000000, 0x08000000)

    def test_windows_arp_is_hidden(self):
        with patch.object(lan_discovery.platform, 'system', return_value='Windows'), patch.object(lan_discovery.subprocess, 'run') as run:
            run.return_value.stdout = '192.168.1.1 00-11-22-33-44-55 dynamic'
            lan_discovery.get_arp_table()
            self.assertEqual(run.call_args.kwargs['creationflags'] & 0x08000000, 0x08000000)

    def test_linux_does_not_use_windows_flags(self):
        with patch.object(lan_discovery.platform, 'system', return_value='Linux'), patch.object(lan_discovery.subprocess, 'run') as run:
            run.return_value.returncode = 0
            lan_discovery.ping_host('192.168.1.1')
            self.assertNotIn('creationflags', run.call_args.kwargs)
