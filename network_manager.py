"""Windows network settings helper. No credentials or admin elevation are stored."""
import ipaddress
import json
import platform
import re
import subprocess
import urllib.request


class NetworkError(RuntimeError):
    pass


def require_windows():
    if platform.system() != 'Windows':
        raise NetworkError('Tinh nang doi mang chi ho tro Windows 10/11.')


def run_command(args, timeout=20):
    require_windows()
    try:
        result = subprocess.run(args, capture_output=True, text=True, errors='replace', timeout=timeout, shell=False, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise NetworkError('Khong chay duoc lenh mang: ' + str(exc)) from exc
    if result.returncode:
        raise NetworkError((result.stderr or result.stdout or 'Lenh mang that bai').strip()[:500])
    return result.stdout.strip()


def powershell(script):
    return run_command(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script])


def adapter_names():
    script = "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -ExpandProperty Name | ConvertTo-Json -Compress"
    output = powershell(script)
    if not output:
        return []
    result = json.loads(output)
    return [result] if isinstance(result, str) else list(result)


def network_snapshot():
    return powershell("Get-NetIPConfiguration | Format-List InterfaceAlias,IPv4Address,IPv4DefaultGateway,DNSServer | Out-String -Width 180")


def validate_adapter(adapter):
    if adapter not in adapter_names():
        raise NetworkError('Hay chon card mang dang ket noi tu danh sach.')
    return adapter


def validate_static(ip, mask, gateway, dns):
    try:
        address = ipaddress.IPv4Address(ip)
        net = ipaddress.IPv4Network((ip, mask), strict=False)
        if address.is_multicast or address.is_unspecified or address.is_loopback or address == net.network_address or address == net.broadcast_address:
            raise ValueError('IP khong phu hop')
        if gateway and ipaddress.IPv4Address(gateway) not in net:
            raise ValueError('Gateway phai nam cung subnet')
        if dns:
            ipaddress.IPv4Address(dns)
        prefix = net.prefixlen
        if prefix < 1 or prefix > 30:
            raise ValueError('Subnet mask khong hop le')
    except (ValueError, ipaddress.AddressValueError) as exc:
        raise NetworkError('IP / Subnet / Gateway / DNS khong hop le: ' + str(exc)) from exc
    return str(address), str(net.netmask), gateway.strip(), dns.strip()


def set_static(adapter, ip, mask, gateway='', dns=''):
    require_windows()
    validate_adapter(adapter)
    ip, mask, gateway, dns = validate_static(ip, mask, gateway, dns)
    command = ['netsh', 'interface', 'ipv4', 'set', 'address', 'name=' + adapter, 'source=static', 'address=' + ip, 'mask=' + mask]
    if gateway:
        command.append('gateway=' + gateway)
    else:
        command.append('gateway=none')
    run_command(command)
    if dns:
        run_command(['netsh', 'interface', 'ipv4', 'set', 'dnsservers', 'name=' + adapter, 'source=static', 'address=' + dns, 'register=primary'])
    return 'Da ap dung IP tinh. Kiem tra lai ket noi va DNS.'


def set_dhcp(adapter):
    require_windows()
    validate_adapter(adapter)
    run_command(['netsh', 'interface', 'ipv4', 'set', 'address', 'name=' + adapter, 'source=dhcp'])
    run_command(['netsh', 'interface', 'ipv4', 'set', 'dnsservers', 'name=' + adapter, 'source=dhcp'])
    return 'Da chuyen IP va DNS ve DHCP.'


def vpn_profiles():
    output = powershell("@(Get-VpnConnection -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) + @(Get-VpnConnection -AllUserConnection -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) | Sort-Object -Unique | ConvertTo-Json -Compress")
    if not output or output == 'null':
        return []
    data = json.loads(output)
    return [data] if isinstance(data, str) else [x for x in data if x]


def validate_vpn(name):
    if name not in vpn_profiles():
        raise NetworkError('VPN khong co trong cac ket noi da cau hinh tren Windows.')
    return name


def connect_vpn(name):
    validate_vpn(name)
    # Uses credentials already held by the Windows VPN connection; never pass passwords.
    return run_command(['rasdial.exe', name], timeout=45)


def disconnect_vpn(name):
    validate_vpn(name)
    return run_command(['rasdial.exe', name, '/disconnect'], timeout=30)


def public_ip(timeout=7):
    # HTTPS endpoint is for display only. No email content or local credentials sent.
    request = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'AlibabaMailNetworkManager/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read(100).decode('ascii').strip()
        return str(ipaddress.ip_address(data))
    except Exception as exc:
        raise NetworkError('Khong kiem tra duoc IP cong cong: ' + str(exc)) from exc
