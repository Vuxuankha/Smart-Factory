"""Opt-in local IT operations. No automatic remote changes or credentials storage."""
from __future__ import annotations
import csv
import hashlib
import ipaddress
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from urllib.request import urlopen

SCHEMA = '''
CREATE TABLE IF NOT EXISTS assets(id INTEGER PRIMARY KEY, name TEXT NOT NULL, host TEXT NOT NULL UNIQUE, kind TEXT NOT NULL, port INTEGER NOT NULL, site TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS observations(id INTEGER PRIMARY KEY, asset_id INTEGER NOT NULL, at TEXT NOT NULL, status TEXT NOT NULL, latency_ms REAL, detail TEXT NOT NULL, FOREIGN KEY(asset_id) REFERENCES assets(id));
CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL, priority TEXT NOT NULL, requester TEXT NOT NULL, assignee TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Open', created TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ip_leases(id INTEGER PRIMARY KEY, address TEXT NOT NULL UNIQUE, owner TEXT NOT NULL, note TEXT NOT NULL DEFAULT '', created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, at TEXT NOT NULL, action TEXT NOT NULL, detail TEXT NOT NULL);
'''

def stamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def default_db():
    base = Path(os.environ.get('LOCALAPPDATA') or (Path.home() / '.local' / 'share')) / 'AlibabaMailIT'
    base.mkdir(parents=True, exist_ok=True)
    return base / 'infrastructure.sqlite3'

class Store:
    def __init__(self, path=None):
        self.path = str(path or default_db())
        with self.conn() as db:
            db.executescript(SCHEMA)
    @contextmanager
    def conn(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()
    def audit(self, action, detail):
        with self.conn() as db:
            db.execute('INSERT INTO audit(at,action,detail) VALUES(?,?,?)', (stamp(), action, str(detail)[:2000]))
    def add_asset(self, name, host, kind='Other', port=443, site=''):
        if not name.strip() or not host.strip(): raise ValueError('Name and host are required')
        if not isinstance(port, int) or not 1 <= port <= 65535: raise ValueError('Port must be 1..65535')
        # Host is only used as a socket destination, never interpolated in a shell command.
        if len(host) > 253 or any(c.isspace() for c in host): raise ValueError('Invalid host')
        with self.conn() as db:
            db.execute('INSERT INTO assets(name,host,kind,port,site) VALUES(?,?,?,?,?)', (name.strip(),host.strip(),kind,port,site.strip()))
        self.audit('asset_add', host)
    def assets(self):
        with self.conn() as db: return [dict(r) for r in db.execute('SELECT * FROM assets ORDER BY name')]
    def check_assets(self, timeout=1.5):
        results=[]
        for asset in self.assets():
            start=time.monotonic()
            try:
                with socket.create_connection((asset['host'], asset['port']),timeout=timeout): pass
                status='UP'; detail='TCP port reachable'
            except OSError as exc:
                status='DOWN'; detail=type(exc).__name__
            ms=round((time.monotonic()-start)*1000,1)
            with self.conn() as db:
                db.execute('INSERT INTO observations(asset_id,at,status,latency_ms,detail) VALUES(?,?,?,?,?)',(asset['id'],stamp(),status,ms,detail))
            results.append({**asset,'status':status,'latency_ms':ms,'detail':detail})
        return results
    def add_ticket(self,title,category,priority,requester,assignee=''):
        if not title.strip(): raise ValueError('Title required')
        if priority not in ('Low','Normal','High','Critical'): raise ValueError('Invalid priority')
        now=stamp()
        with self.conn() as db:
            row=db.execute('INSERT INTO tickets(title,category,priority,requester,assignee,created,updated) VALUES(?,?,?,?,?,?,?)',(title.strip(),category,priority,requester.strip(),assignee.strip(),now,now))
            tid=row.lastrowid
        self.audit('ticket_create', tid)
        return tid
    def tickets(self):
        with self.conn() as db: return [dict(r) for r in db.execute('SELECT * FROM tickets ORDER BY id DESC LIMIT 500')]
    def set_ticket(self,tid,status,assignee):
        if status not in ('Open','In Progress','Resolved','Closed'): raise ValueError('Invalid status')
        with self.conn() as db:
            cur=db.execute('UPDATE tickets SET status=?,assignee=?,updated=? WHERE id=?',(status,assignee,stamp(),int(tid)))
            if not cur.rowcount: raise ValueError('Ticket not found')
        self.audit('ticket_update',tid)
    def allocate_ip(self,cidr,owner,note='',reserved=()):
        network=ipaddress.ip_network(cidr,strict=False)
        if network.version != 4 or network.num_addresses > 65536: raise ValueError('Only IPv4 pools up to /16 are supported')
        if not owner.strip(): raise ValueError('Owner required')
        blocked={str(ipaddress.ip_address(s)) for s in reserved if s.strip()}
        with self.conn() as db:
            existing={r[0] for r in db.execute('SELECT address FROM ip_leases')}
            for addr in network.hosts():
                val=str(addr)
                if val not in blocked and val not in existing:
                    db.execute('INSERT INTO ip_leases(address,owner,note,created) VALUES(?,?,?,?)',(val,owner.strip(),note,stamp()))
                    break
            else: raise ValueError('No free IP in pool')
        self.audit('ip_reserve',val)
        return val
    def leases(self):
        with self.conn() as db: return [dict(r) for r in db.execute('SELECT * FROM ip_leases ORDER BY address')]
    def export_tickets(self,destination):
        rows=self.tickets()
        with open(destination,'w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=['id','title','category','priority','requester','assignee','status','created','updated']);w.writeheader();w.writerows(rows)
        self.audit('ticket_export',Path(destination).name)
        return len(rows)

def public_ip(timeout=4):
    with urlopen('https://api.ipify.org',timeout=timeout) as response:
        return str(ipaddress.ip_address(response.read(64).decode('ascii').strip()))

def backup_folder(source,destination):
    """Copy a local folder to a NEW destination and write a SHA256 manifest; never overwrite."""
    src=Path(source).resolve(); dst=Path(destination).resolve()
    if not src.is_dir(): raise ValueError('Source directory does not exist')
    if src==dst or src in dst.parents or dst in src.parents: raise ValueError('Nested source/destination is not allowed')
    if dst.exists(): raise FileExistsError('Backup destination already exists')
    if (src/'backup_manifest.json').exists(): raise ValueError('Source root contains reserved backup_manifest.json')
    dst.mkdir(parents=True)
    manifest=[]
    try:
        for p in src.rglob('*'):
            if p.is_symlink(): continue
            rel=p.relative_to(src)
            if p.is_dir(): (dst/rel).mkdir(parents=True,exist_ok=True);continue
            if not p.is_file(): continue
            target=dst/rel;target.parent.mkdir(parents=True,exist_ok=True)
            h=hashlib.sha256()
            with p.open('rb') as inp,target.open('xb') as out:
                while chunk:=inp.read(1024*1024): h.update(chunk);out.write(chunk)
            manifest.append({'path':rel.as_posix(),'size':p.stat().st_size,'sha256':h.hexdigest()})
        (dst/'backup_manifest.json').write_text(json.dumps({'created':stamp(),'files':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception:
        # Preserve incomplete backup for inspection; never report as successful.
        raise
    return len(manifest)

def verify_backup(folder):
    root=Path(folder).resolve(); manifest=json.loads((root/'backup_manifest.json').read_text(encoding='utf-8'))
    errors=[]
    for item in manifest['files']:
        p=(root/item['path']).resolve()
        if root not in p.parents or not p.is_file(): errors.append(item['path']);continue
        h=hashlib.sha256()
        with p.open('rb') as f:
            while chunk:=f.read(1024*1024):h.update(chunk)
        if h.hexdigest()!=item['sha256'] or p.stat().st_size!=item['size']:errors.append(item['path'])
    return len(manifest['files']),errors

def windows_update_status():
    if sys.platform != 'win32': raise OSError('Windows only')
    code='Get-Service wuauserv | Select-Object Name,Status | ConvertTo-Json -Compress'
    proc=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',code],capture_output=True,text=True,timeout=20,check=True,creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if os.name == 'nt' else 0)
    return proc.stdout.strip()

def old_files_preview(folder,days=30):
    root=Path(folder).resolve()
    if not root.is_dir(): raise ValueError('Folder not found')
    if not 1 <= days <= 3650:raise ValueError('Invalid number of days')
    cutoff=time.time()-days*86400
    return [(str(p),p.stat().st_size) for p in root.rglob('*') if p.is_file() and not p.is_symlink() and p.stat().st_mtime<cutoff][:1000]

def draft_access_script(username,group,add=True):
    """Only generate a reviewable AD PowerShell command. Do not execute it."""
    import re
    for value in (username,group):
        if not re.fullmatch(r'[A-Za-z0-9_.@ -]{1,100}',value): raise ValueError('Unsupported account/group characters')
    # Single quotes in input are prohibited. No remote execution.
    verb='Add-ADGroupMember' if add else 'Remove-ADGroupMember'
    return f'Import-Module ActiveDirectory\n{verb} -Identity \'{group}\' -Members \'{username}\' -WhatIf\n# Review, authorize, then remove -WhatIf manually.'
