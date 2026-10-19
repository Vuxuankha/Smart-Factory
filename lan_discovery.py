"""Conservative opt-in LAN discovery. Only local IPv4 private subnets; no port sweeping."""
from __future__ import annotations
import concurrent.futures
import ipaddress
import platform
import re
import socket
import subprocess
import threading
import time

COMMON_PORTS = (80, 443, 445, 22, 3389, 554)


def _hidden_subprocess_options():
    """Prevent console flashes when invoking Windows CLI tools from a GUI app."""
    if platform.system() != 'Windows':
        return {}
    options = {'creationflags': getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)}
    if hasattr(subprocess, 'STARTUPINFO'):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= getattr(subprocess, 'STARTF_USESHOWWINDOW', 1)
        startupinfo.wShowWindow = getattr(subprocess, 'SW_HIDE', 0)
        options['startupinfo'] = startupinfo
    return options



def validate_network(cidr: str):
    net = ipaddress.ip_network(cidr.strip(), strict=False)
    if not isinstance(net, ipaddress.IPv4Network) or not net.is_private:
        raise ValueError('Chỉ hỗ trợ dải IPv4 nội bộ (private LAN).')
    if net.num_addresses > 256 or net.prefixlen < 24:
        raise ValueError('Giới hạn tối đa 256 địa chỉ mỗi lần quét (/24 hoặc nhỏ hơn).')
    if net.num_addresses < 4:
        raise ValueError('Dải cần tối thiểu 4 địa chỉ.')
    return net


def suggest_local_subnet():
    """Best-effort recommendation, never silently scan."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('192.0.2.1', 80))  # UDP connect doesn't send traffic.
            ip = s.getsockname()[0]
        finally:
            s.close()
        addr = ipaddress.ip_address(ip)
        if addr.is_private and not addr.is_loopback and not addr.is_link_local:
            return str(ipaddress.ip_network(f'{ip}/24', strict=False))
    except OSError:
        pass
    return '192.168.1.0/24'


def ping_host(ip: str, timeout_ms=750):
    is_win = platform.system() == 'Windows'
    args = ['ping', '-n', '1', '-w', str(timeout_ms), ip] if is_win else ['ping', '-n', '-c', '1', '-W', '1', ip]
    try:
        res = subprocess.run(args, capture_output=True, timeout=3, check=False, **_hidden_subprocess_options())
        return res.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def get_arp_table():
    """ARP table can only include devices recently seen, no privileged ARP injection."""
    try:
        proc = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5, errors='replace', **_hidden_subprocess_options())
        text = proc.stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    found = {}
    for line in text.splitlines():
        match = re.search(r'(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5})\b', line)
        if match:
            try:
                ip = str(ipaddress.IPv4Address(match.group(1)))
                mac = match.group(2).replace('-', ':').upper()
                found[ip] = mac
            except ipaddress.AddressValueError:
                continue
    return found


def probe_host(ip: str, ports=COMMON_PORTS):
    start = time.monotonic()
    responded_ping = ping_host(ip)
    alive = responded_ping
    open_ports = []
    # Only a few common ports, not a comprehensive port scan.
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=0.18):
                open_ports.append(port)
                alive = True
        except OSError:
            pass
    return {'ip': ip, 'online': alive, 'ping': responded_ping,
            'open_ports': open_ports, 'latency_ms': round((time.monotonic()-start)*1000, 1)}


def scan_network(cidr, *, workers=24, progress=None, cancel=None, ports=COMMON_PORTS):
    """Bounded, cancel-aware private LAN discovery; one failed host cannot abort a scan."""
    net = validate_network(cidr)
    hosts = iter(str(ip) for ip in net.hosts())
    total = net.num_addresses - 2
    workers = max(1, min(int(workers), 32))
    cancel = cancel if cancel is not None else threading.Event()
    results = []
    done = 0
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
    pending = set()
    try:
        for _ in range(min(workers, total)):
            if cancel.is_set():
                break
            pending.add(pool.submit(probe_host, next(hosts), ports))
        while pending and not cancel.is_set():
            finished, pending = concurrent.futures.wait(
                pending, timeout=0.15, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in finished:
                done += 1
                try:
                    result = future.result()
                    if result['online']:
                        results.append(result)
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    # One inaccessible host must not hide other discovered hosts.
                    pass
                if progress and not cancel.is_set():
                    progress(done, total, len(results))
                if not cancel.is_set():
                    host = next(hosts, None)
                    if host is not None:
                        pending.add(pool.submit(probe_host, host, ports))
    finally:
        for future in pending:
            future.cancel()
        pool.shutdown(wait=False, cancel_futures=True)
    if cancel.is_set():
        return []  # Never present a canceled/incomplete sweep as a full result.
    macs = get_arp_table()
    for item in results:
        item['mac'] = macs.get(item['ip'], '')
    return sorted(results, key=lambda row: ipaddress.IPv4Address(row['ip']))
