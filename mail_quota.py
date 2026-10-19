"""Read-only IMAP QUOTA probe and portable CSV quota reports.

An admin mailbox cannot inherently inspect other mailboxes over IMAP.
Never persist mailbox passwords. QUOTA is optional and server-dependent.
"""
from __future__ import annotations
import csv
import imaplib
import re
import ssl
from dataclasses import dataclass
from pathlib import Path

HOST = 'imap.qiye.aliyun.com'
PORT = 993
_RESOURCE = re.compile(rb'\bSTORAGE\s+(\d+)\s+(\d+)\b', re.I)


@dataclass(frozen=True)
class QuotaResult:
    email: str
    used_bytes: int | None
    limit_bytes: int | None
    status: str
    detail: str = ''

    @property
    def free_bytes(self):
        if self.used_bytes is None or self.limit_bytes is None:
            return None
        return max(0, self.limit_bytes - self.used_bytes)

    @property
    def percent(self):
        if self.used_bytes is None or not self.limit_bytes:
            return None
        return 100.0 * self.used_bytes / self.limit_bytes


def parse_storage_quota(response):
    """Parse RFC 2087 STORAGE resource (KiB), retaining unbounded/unknown as None."""
    parts = []
    def collect(obj):
        if isinstance(obj, bytes):
            parts.append(obj)
        elif isinstance(obj, str):
            parts.append(obj.encode('utf-8', 'replace'))
        elif isinstance(obj, (list, tuple)):
            for part in obj:
                collect(part)
    collect(response)
    for part in parts:
        match = _RESOURCE.search(part)
        if match:
            used, limit = (int(match.group(1)), int(match.group(2)))
            return used * 1024, limit * 1024
    return None, None


def probe_quota(email, password, host=HOST, port=PORT, timeout=20):
    """Queries only the authenticated mailbox; never modifies messages or quota."""
    email = email.strip()
    if not email or not password:
        raise ValueError('Email và mật khẩu không được để trống.')
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError('Cổng IMAP không hợp lệ.')
    with imaplib.IMAP4_SSL(host=host, port=port,
                          ssl_context=ssl.create_default_context(), timeout=timeout) as conn:
        conn.login(email, password)
        caps = {c.decode('ascii', 'replace').upper() if isinstance(c, bytes) else str(c).upper()
                for c in conn.capabilities}
        if not any(c == 'QUOTA' or c.startswith('QUOTA=') for c in caps):
            return QuotaResult(email, None, None, 'UNSUPPORTED', 'IMAP không công bố QUOTA')
        try:
            state, data = conn.getquotaroot('INBOX')
        except imaplib.IMAP4.error:
            return QuotaResult(email, None, None, 'DENIED', 'Máy chủ từ chối truy vấn QUOTA')
        if state != 'OK':
            return QuotaResult(email, None, None, 'DENIED', 'Không được phép đọc quota')
        used, limit = parse_storage_quota(data)
        if used is None:
            return QuotaResult(email, None, None, 'UNKNOWN', 'Không tìm thấy STORAGE trong phản hồi QUOTA')
        return QuotaResult(email, used, limit, 'OK')


def csv_safe(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value


def export_quota_csv(path, rows):
    dest = Path(path)
    if dest.exists():
        raise FileExistsError('Tệp báo cáo đã tồn tại. Hãy chọn tên khác.')
    with dest.open('x', newline='', encoding='utf-8-sig') as handle:
        writer = csv.writer(handle)
        writer.writerow(['Email', 'Used bytes', 'Limit bytes', 'Free bytes', 'Percent', 'Status', 'Detail'])
        for row in rows:
            writer.writerow([csv_safe(row.email), row.used_bytes if row.used_bytes is not None else '',
                             row.limit_bytes if row.limit_bytes is not None else '',
                             row.free_bytes if row.free_bytes is not None else '',
                             f'{row.percent:.2f}' if row.percent is not None else '', csv_safe(row.status), csv_safe(row.detail)])
    return dest
