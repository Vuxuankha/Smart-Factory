"""Local application identity; distinct from any IMAP/SMTP credentials.

This is workstation authentication, not domain SSO. A first-run admin must
bootstrap the database; later registrations remain pending until approved.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time

SCHEMA_VERSION = 1
MAX_FAILED = 5
LOCK_SECONDS = 15 * 60
ROLES = ('employee', 'it_admin', 'auditor')
ROLE_LABELS = {'employee': 'Nhân viên', 'it_admin': 'Quản trị IT', 'auditor': 'Kiểm toán'}
PERMISSIONS = {
    'employee': frozenset({'mail', 'pmc', 'system_check'}),
    'it_admin': frozenset({'mail', 'pmc', 'system_check', 'network', 'infra', 'users', 'audit'}),
    'auditor': frozenset({'reports', 'system_check', 'audit'}),
}

# Smart Factory uses additional per-plant/domain checks in factory_core.
PERMISSIONS = {role: permissions | {'factory'} for role, permissions in PERMISSIONS.items()}

class AuthError(ValueError):
    pass

@dataclass(frozen=True)
class Session:
    username: str
    role: str
    display_name: str
    def allows(self, feature):
        return feature in PERMISSIONS.get(self.role, ())


def default_auth_path():
    root = os.environ.get('ALIBABA_OPERATIONS_DATA')
    if root:
        return Path(root).expanduser().resolve() / 'accounts.sqlite3'
    base = os.environ.get('LOCALAPPDATA')
    if base:
        return Path(base) / 'AlibabaOperationsCenter' / 'accounts.sqlite3'
    return Path.home() / '.local' / 'share' / 'AlibabaOperationsCenter' / 'accounts.sqlite3'


def normalize_username(value):
    name = str(value).strip().casefold()
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{2,63}', name):
        raise AuthError('Tên đăng nhập từ 3 đến 64 ký tự: a-z, 0-9, dấu chấm, gạch dưới hoặc gạch ngang.')
    return name


def validate_password(password):
    if not isinstance(password, str) or not (12 <= len(password) <= 256):
        raise AuthError('Mật khẩu ứng dụng cần ít nhất 12 ký tự (tối đa 256).')
    if not any(x.isalpha() for x in password) or not any(x.isdigit() for x in password):
        raise AuthError('Mật khẩu phải chứa cả chữ và số.')
    if any(ord(x) < 32 or ord(x) == 127 for x in password):
        raise AuthError('Mật khẩu không được chứa ký tự điều khiển.')


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    return salt.hex(), hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1, dklen=32).hex()


class AuthStore:
    def __init__(self, path=None, clock=None):
        self.path = Path(path or default_auth_path())
        self.clock = clock or time.time
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name == 'posix':
            try: self.path.parent.chmod(0o700)
            except OSError: pass
        with self._db() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS users(
                username TEXT PRIMARY KEY, display_name TEXT NOT NULL,
                role TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 0,
                salt TEXT NOT NULL, password_hash TEXT NOT NULL,
                failed INTEGER NOT NULL DEFAULT 0, locked_until REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL, approved_by TEXT)''')
            con.execute('''CREATE TABLE IF NOT EXISTS audit(
                id INTEGER PRIMARY KEY AUTOINCREMENT, when_utc TEXT NOT NULL,
                actor TEXT NOT NULL, action TEXT NOT NULL, detail TEXT NOT NULL)''')
            con.execute('CREATE INDEX IF NOT EXISTS idx_audit_when ON audit(id DESC)')
        if os.name == 'posix':
            try: self.path.chmod(0o600)
            except OSError: pass

    @contextmanager
    def _db(self):
        con = sqlite3.connect(self.path, timeout=15)
        con.row_factory = sqlite3.Row
        try:
            con.execute('PRAGMA busy_timeout=15000')
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def first_run(self):
        with self._db() as con:
            return con.execute('SELECT NOT EXISTS(SELECT 1 FROM users WHERE role=?)', ('it_admin',)).fetchone()[0] == 1

    def _audit(self, con, actor, action, detail=''):
        # Never write a password, token or mailbox secret here.
        con.execute('INSERT INTO audit(when_utc, actor, action, detail) VALUES (?,?,?,?)',
                    (datetime.now(timezone.utc).isoformat(), str(actor)[:64], str(action)[:80], str(detail)[:180]))
        con.execute('DELETE FROM audit WHERE id <= (SELECT COALESCE(MAX(id),0)-10000 FROM audit)')

    def register(self, username, password, display_name=''):
        username = normalize_username(username)
        validate_password(password)
        display_name = (str(display_name).strip() or username)[:100]
        salt, key = hash_password(password)
        now = datetime.now(timezone.utc).isoformat()
        with self._db() as con:
            # First-run bootstrap is serialized by BEGIN IMMEDIATE.
            con.execute('BEGIN IMMEDIATE')
            first = con.execute("SELECT NOT EXISTS(SELECT 1 FROM users WHERE role='it_admin')").fetchone()[0]
            role, active = ('it_admin', 1) if first else ('employee', 0)
            try:
                con.execute('''INSERT INTO users(username, display_name, role, active, salt, password_hash,
                    created_at, approved_by) VALUES(?,?,?,?,?,?,?,?)''',
                    (username, display_name, role, active, salt, key, now, 'bootstrap' if first else None))
            except sqlite3.IntegrityError as exc:
                raise AuthError('Tên đăng nhập đã tồn tại.') from exc
            self._audit(con, username, 'REGISTER', 'bootstrap_admin' if first else 'pending_approval')
        return 'admin_created' if first else 'pending'

    def authenticate(self, username, password):
        if not isinstance(password, str): password = ''
        try: username = normalize_username(username)
        except AuthError:
            hash_password(password[:256], b'\x00'*16)
            raise AuthError('Tên đăng nhập hoặc mật khẩu không đúng.')
        if len(password)>256: raise AuthError('Tên đăng nhập hoặc mật khẩu không đúng.')
        with self._db() as con:
            con.execute('BEGIN IMMEDIATE')
            row = con.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
            if row is None:
                # Same hash primitive even for non-existing names, reducing differences.
                hash_password(password, b'\x00' * 16)
                raise AuthError('Tên đăng nhập hoặc mật khẩu không đúng.')
            now = self.clock()
            if row['locked_until'] > now:
                raise AuthError('Tài khoản tạm khóa sau nhiều lần nhập sai. Hãy thử sau 15 phút.')
            test = hashlib.scrypt(password.encode('utf-8'), salt=bytes.fromhex(row['salt']), n=2**14, r=8, p=1, dklen=32)
            matched = hmac.compare_digest(test, bytes.fromhex(row['password_hash']))
            if not matched:
                failed = row['failed'] + 1
                locked_until = now + LOCK_SECONDS if failed >= MAX_FAILED else 0
                con.execute('UPDATE users SET failed=?, locked_until=? WHERE username=?', (failed, locked_until, username))
                self._audit(con, username, 'LOGIN_FAILED')
                con.commit()  # Retain the lockout counter on rejected logins.
                raise AuthError('Tên đăng nhập hoặc mật khẩu không đúng.' if failed < MAX_FAILED else 'Tài khoản tạm khóa 15 phút.')
            con.execute('UPDATE users SET failed=0, locked_until=0 WHERE username=?', (username,))
            if not row['active']:
                self._audit(con, username, 'LOGIN_PENDING')
                raise AuthError('Tài khoản chưa được quản trị viên phê duyệt.')
            self._audit(con, username, 'LOGIN')
            return Session(row['username'], row['role'], row['display_name'])

    def session_current(self, session):
        if not isinstance(session,Session):return False
        with self._db() as con:
            row=con.execute('SELECT active,role FROM users WHERE username=?',(session.username,)).fetchone()
            return bool(row and row['active'] and row['role']==session.role)

    def list_users(self, admin):
        self._require(admin, 'users')
        with self._db() as con:
            return [dict(x) for x in con.execute('SELECT username, display_name, role, active, created_at, approved_by FROM users ORDER BY active, username')]

    def approve(self, admin, username, role='employee'):
        self._require(admin, 'users')
        username = normalize_username(username)
        if role not in ROLES: raise AuthError('Vai trò không hợp lệ.')
        with self._db() as con:
            old=con.execute('SELECT role,active FROM users WHERE username=?',(username,)).fetchone()
            if old is None:
                raise AuthError('Không tìm thấy tài khoản.')
            if old['role']=='it_admin' and old['active'] and role!='it_admin':
                if username == admin.username:
                    raise AuthError('Không thể tự thay đổi vai trò quản trị viên đang dùng.')
                n=con.execute("SELECT COUNT(*) FROM users WHERE role='it_admin' AND active=1").fetchone()[0]
                if n<=1:
                    raise AuthError('Không thể hạ quyền quản trị viên cuối cùng.')
            con.execute('UPDATE users SET active=1,role=?,approved_by=? WHERE username=?',
                        (role, admin.username, username))
            self._audit(con, admin.username, 'APPROVE_USER', f'{username}:{role}')

    def deactivate(self, admin, username):
        self._require(admin, 'users')
        username = normalize_username(username)
        if username == admin.username:
            raise AuthError('Không thể tự vô hiệu hóa tài khoản đang dùng.')
        with self._db() as con:
            row = con.execute('SELECT role, active FROM users WHERE username=?', (username,)).fetchone()
            if row is None: raise AuthError('Không tìm thấy tài khoản.')
            if row['role'] == 'it_admin' and row['active']:
                n = con.execute("SELECT COUNT(*) FROM users WHERE role='it_admin' AND active=1").fetchone()[0]
                if n <= 1: raise AuthError('Không thể khóa quản trị viên cuối cùng.')
            con.execute('UPDATE users SET active=0 WHERE username=?', (username,))
            self._audit(con, admin.username, 'DISABLE_USER', username)

    def change_password(self, session, current, replacement):
        validate_password(replacement)
        with self._db() as con:
            row = con.execute('SELECT salt,password_hash FROM users WHERE username=? AND active=1', (session.username,)).fetchone()
            if row is None: raise AuthError('Tài khoản không hoạt động.')
            digest = hashlib.scrypt(current.encode('utf-8'), salt=bytes.fromhex(row['salt']), n=2**14, r=8, p=1, dklen=32)
            if not hmac.compare_digest(digest, bytes.fromhex(row['password_hash'])):
                raise AuthError('Mật khẩu hiện tại không đúng.')
            salt, new_digest = hash_password(replacement)
            con.execute('UPDATE users SET salt=?,password_hash=?,failed=0,locked_until=0 WHERE username=?',
                        (salt, new_digest, session.username))
            self._audit(con, session.username, 'CHANGE_PASSWORD')

    def audit_events(self, session, limit=200):
        self._require(session, 'audit')
        with self._db() as con:
            return [dict(row) for row in con.execute('SELECT when_utc,actor,action,detail FROM audit ORDER BY id DESC LIMIT ?',
                                                     (min(500, max(1, int(limit))),))]

    @staticmethod
    def _require(session, permission):
        if not isinstance(session, Session) or not session.allows(permission):
            raise PermissionError('Bạn không có quyền thực hiện chức năng này.')
