"""Local Smart Factory service, deliberately NOT a PLC/ERP/robot controller.

All public data operations require a current application session. SQLite
transactions serialize stock posting and audit insertion; record revisions
prevent lost updates. No mailbox credentials are accepted by this module.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path
import csv
import hashlib
import html
import ipaddress
import json
import os
import re
import sqlite3
import tempfile
import uuid
import zipfile
from auth_local import AuthError, Session
from factory_schema import ENTITIES

D=Decimal
UTC=timezone.utc
SCHEMA_VERSION=1
MAX_RECORDS=20000

class FactoryError(ValueError): pass
class AccessDenied(FactoryError): pass
class Conflict(FactoryError): pass

def now(): return datetime.now(UTC).isoformat(timespec='seconds')
def ident(value):
    v=str(value).strip()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}',v):
        raise FactoryError('M\u00e3 g\u1ed3m 1-64 k\u00fd t\u1ef1: ch\u1eef kh\u00f4ng d\u1ea5u, s\u1ed1, . _ -')
    return v

def text(value, maxlen=2000):
    v=str(value).strip()
    if len(v)>maxlen or any(ord(x)<32 or ord(x)==127 for x in v):
        raise FactoryError('V\u0103n b\u1ea3n qu\u00e1 d\u00e0i ho\u1eb7c ch\u1ee9a k\u00fd t\u1ef1 \u0111i\u1ec1u khi\u1ec3n.')
    return v

def number(value, positive=False, signed=False, integer=False):
    if len(str(value))>80: raise FactoryError('S\u1ed1 qu\u00e1 l\u1edbn.')
    try: v=D(str(value))
    except (InvalidOperation,ValueError): raise FactoryError('S\u1ed1 kh\u00f4ng h\u1ee3p l\u1ec7.')
    if not v.is_finite() or abs(v)>D('1e15') or (not signed and v<0) or (positive and v<=0):
        raise FactoryError('S\u1ed1 ph\u1ea3i h\u1eefu h\u1ea1n, \u0111\u00fang mi\u1ec1n gi\u00e1 tr\u1ecb v\u00e0 kh\u00f4ng v\u01b0\u1ee3t 10^15.')
    if integer and v!=v.to_integral_value(): raise FactoryError('C\u1ea7n s\u1ed1 nguy\u00ean.')
    # No silent rounding of inventory quantities. Precision contract is six decimals.
    if v!=v.quantize(D('0.000001')): raise FactoryError('T\u1ed1i \u0111a 6 ch\u1eef s\u1ed1 th\u1eadp ph\u00e2n.')
    return v

def dec(v):
    result=format(v,'f')
    return result.rstrip('0').rstrip('.') if '.' in result else result

def iso_date(v):
    try:
        s=str(v); dt=date.fromisoformat(s)
        if s!=dt.isoformat(): raise ValueError()
        return s
    except ValueError: raise FactoryError('Ng\u00e0y c\u1ea7n \u0111\u00fang YYYY-MM-DD.')

def stamp(v):
    try:
        dt=datetime.fromisoformat(str(v).replace('Z','+00:00'))
        if dt.tzinfo is None or dt.utcoffset() is None: raise ValueError()
        return dt.astimezone(UTC).isoformat(timespec='seconds')
    except (ValueError,OverflowError): raise FactoryError('Th\u1eddi gian c\u1ea7n m\u00fai gi\u1edd, v\u00ed d\u1ee5 2026-10-19T08:00:00+07:00.')

def dt(v): return datetime.fromisoformat(v)
def overlap(a,b,c,d): return a<d and c<b

def csv_safe(v):
    s='' if v is None else str(v)
    return "'"+s if s.lstrip().startswith(('=','+','-','@')) or s.startswith(('\t','\r','\n')) else s

def packed(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def clean_input(kind, values):
    if kind not in ENTITIES: raise FactoryError('Ph\u00e2n h\u1ec7 kh\u00f4ng h\u1ee3p l\u1ec7.')
    schema=ENTITIES[kind]
    if not isinstance(values,dict) or set(values)-{f.key for f in schema['fields']}:
        raise FactoryError('Tr\u01b0\u1eddng d\u1eef li\u1ec7u kh\u00f4ng \u0111\u01b0\u1ee3c h\u1ed7 tr\u1ee3.')
    out={}
    for f in schema['fields']:
        v=values.get(f.key,f.default)
        v='' if v is None else str(v).strip()
        if not v:
            if f.required: raise FactoryError('Thi\u1ebfu '+f.label)
            out[f.key]='';continue
        if f.type in ('decimal','positive','signed','integer'):
            v=dec(number(v,positive=f.type=='positive',signed=f.type=='signed',integer=f.type=='integer'))
        elif f.type=='date': v=iso_date(v)
        elif f.type=='datetime': v=stamp(v)
        elif f.type=='ip':
            try: v=str(ipaddress.ip_address(v))
            except ValueError: raise FactoryError('IP kh\u00f4ng h\u1ee3p l\u1ec7.')
        elif f.type=='choice':
            if v not in f.choices: raise FactoryError('L\u1ef1a ch\u1ecdn kh\u00f4ng h\u1ee3p l\u1ec7: '+f.label)
        else: v=text(v)
        if f.ref: v=ident(v)
        out[f.key]=v
    return out

DDL='''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS plants(code TEXT PRIMARY KEY,name TEXT NOT NULL,currency TEXT NOT NULL,capacity TEXT NOT NULL,utc_offset INTEGER NOT NULL DEFAULT 420);
CREATE TABLE IF NOT EXISTS grants(username TEXT NOT NULL,plant TEXT NOT NULL REFERENCES plants(code),domain INTEGER NOT NULL,can_write INTEGER NOT NULL CHECK(can_write IN (0,1)),PRIMARY KEY(username,plant,domain));
CREATE TABLE IF NOT EXISTS records(plant TEXT NOT NULL REFERENCES plants(code),kind TEXT NOT NULL,code TEXT NOT NULL,data TEXT NOT NULL,rev INTEGER NOT NULL,updated TEXT NOT NULL,actor TEXT NOT NULL,PRIMARY KEY(plant,kind,code));
CREATE INDEX IF NOT EXISTS idx_records_list ON records(plant,kind,updated DESC);
CREATE TABLE IF NOT EXISTS postings(plant TEXT NOT NULL REFERENCES plants(code),request_id TEXT NOT NULL,action TEXT NOT NULL,payload TEXT NOT NULL,result TEXT NOT NULL,created TEXT NOT NULL,actor TEXT NOT NULL,PRIMARY KEY(plant,request_id));
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,at TEXT NOT NULL,actor TEXT NOT NULL,plant TEXT NOT NULL,action TEXT NOT NULL,detail TEXT NOT NULL,prev TEXT NOT NULL,digest TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_factory_audit ON audit(plant,id DESC);
CREATE TABLE IF NOT EXISTS preferences(username TEXT PRIMARY KEY,data TEXT NOT NULL);
'''

class Factory:
    def __init__(self,path,auth_store,session):
        self.path=Path(path);self.auth=auth_store;self.session=session
        self._session()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connection() as db:
            # Do not downgrade or silently open future schemas.
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='meta' AND type='table'").fetchone():
                v=db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
                if v and int(v[0])!=SCHEMA_VERSION: raise FactoryError('Phi\u00ean b\u1ea3n CSDL kh\u00f4ng t\u01b0\u01a1ng th\u00edch. Kh\u00f4ng ghi \u0111\u00e8.')
            db.executescript(DDL)
            db.execute("INSERT OR IGNORE INTO meta VALUES('schema_version',?)",(str(SCHEMA_VERSION),))
        if os.name=='posix': self.path.chmod(0o600)

    @contextmanager
    def connection(self,write=False):
        con=sqlite3.connect(self.path,timeout=12,isolation_level=None)
        con.row_factory=sqlite3.Row
        try:
            con.execute('PRAGMA foreign_keys=ON');con.execute('PRAGMA busy_timeout=12000')
            con.execute('PRAGMA synchronous=FULL')
            con.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield con
            con.commit()
        except BaseException:
            con.rollback();raise
        finally: con.close()

    def _session(self):
        if not isinstance(self.session,Session) or not self.auth or not self.auth.session_current(self.session):
            raise AccessDenied('Phi\u00ean \u0111\u0103ng nh\u1eadp \u1ee9ng d\u1ee5ng h\u1ebft hi\u1ec7u l\u1ef1c.')

    def _admin(self):
        self._session()
        if self.session.role!='it_admin': raise AccessDenied('C\u1ea7n quy\u1ec1n Qu\u1ea3n tr\u1ecb IT.')

    def _require(self,db,plant,domain,write=False,admin=False):
        self._session();plant=ident(plant)
        if not db.execute('SELECT 1 FROM plants WHERE code=?',(plant,)).fetchone():
            raise FactoryError('Ch\u01b0a c\u00f3 nh\u00e0 m\u00e1y n\u00e0y.')
        if self.session.role=='it_admin': return
        if admin: raise AccessDenied('T\u00e1c v\u1ee5 d\u00e0nh cho Qu\u1ea3n tr\u1ecb IT.')
        if self.session.role=='auditor':
            if write: raise AccessDenied('Ki\u1ec3m to\u00e1n vi\u00ean ch\u1ec9 \u0111\u01b0\u1ee3c \u0111\u1ecdc.')
            return
        r=db.execute('SELECT can_write FROM grants WHERE username=? AND plant=? AND domain=?',(self.session.username,plant,int(domain))).fetchone()
        if not r or (write and not r[0]): raise AccessDenied('Ch\u01b0a \u0111\u01b0\u1ee3c c\u1ea5p quy\u1ec1n cho nh\u00e0 m\u00e1y / ph\u00e2n h\u1ec7 n\u00e0y.')

    def can(self,plant,domain,write=False):
        try:
            with self.connection() as db:self._require(db,plant,domain,write)
            return True
        except (AccessDenied,FactoryError):return False

    def _local_date(self,db,plant,at=None):
        r=db.execute('SELECT utc_offset FROM plants WHERE code=?',(plant,)).fetchone()
        zone=timezone(timedelta(minutes=r[0]))
        value=dt(at) if at else datetime.now(UTC)
        return value.astimezone(zone).date().isoformat()

    def _issues(self,db,plant):
        returned={json.loads(r[0])['issue_request'] for r in db.execute("SELECT payload FROM postings WHERE plant=? AND action='RETURN'",(plant,))}
        return [dict(request=r['request_id'],payload=json.loads(r['payload']),result=json.loads(r['result']),created=r['created'],actor=r['actor']) for r in db.execute("SELECT * FROM postings WHERE plant=? AND action='ISSUE'",(plant,)) if r['request_id'] not in returned]

    def _audit(self,db,plant,action,detail):
        previous=db.execute('SELECT digest FROM audit ORDER BY id DESC LIMIT 1').fetchone()
        prev=previous[0] if previous else '0'*64
        at=now();body=packed(detail)
        digest=hashlib.sha256(packed([prev,at,self.session.username,plant,action,body]).encode()).hexdigest()
        db.execute('INSERT INTO audit(at,actor,plant,action,detail,prev,digest) VALUES(?,?,?,?,?,?,?)',(at,self.session.username,plant,action,body,prev,digest))

    def plants(self):
        self._session()
        with self.connection() as db:
            if self.session.role in ('it_admin','auditor'): return [dict(r) for r in db.execute('SELECT * FROM plants ORDER BY code')]
            return [dict(r) for r in db.execute('SELECT DISTINCT p.* FROM plants p JOIN grants g ON p.code=g.plant WHERE g.username=? ORDER BY p.code',(self.session.username,))]

    def add_plant(self,code,name,currency='VND',capacity='0',utc_offset=420):
        self._admin();code=ident(code);name=text(name,200);currency=text(currency,3).upper()
        if not name or not re.fullmatch('[A-Z]{3}',currency):raise FactoryError('Thi\u1ebfu t\u00ean / m\u00e3 ti\u1ec1n t\u1ec7 3 k\u00fd t\u1ef1.')
        capacity=dec(number(capacity));utc_offset=int(number(utc_offset,signed=True,integer=True))
        if not -720<=utc_offset<=840:raise FactoryError('UTC offset ngoai pham vi -720..840 phut.')
        with self.connection(True) as db:
            try:db.execute('INSERT INTO plants VALUES(?,?,?,?,?)',(code,name,currency,capacity,utc_offset))
            except sqlite3.IntegrityError:raise Conflict('M\u00e3 nh\u00e0 m\u00e1y \u0111\u00e3 t\u1ed3n t\u1ea1i.')
            self._audit(db,code,'CREATE_PLANT',{'name':name,'currency':currency,'capacity':capacity,'utc_offset':utc_offset})
        return code

    def update_plant(self,code,name,currency,capacity,utc_offset):
        self._admin();code=ident(code);name=text(name,200);currency=text(currency,3).upper();capacity=dec(number(capacity));utc_offset=int(number(utc_offset,signed=True,integer=True))
        if not name or not re.fullmatch('[A-Z]{3}',currency) or not -720<=utc_offset<=840:raise FactoryError('Thong tin nha may khong hop le.')
        with self.connection(True) as db:
            self._require(db,code,1,True)
            old=dict(db.execute('SELECT * FROM plants WHERE code=?',(code,)).fetchone())
            if db.execute('SELECT 1 FROM records WHERE plant=? LIMIT 1',(code,)).fetchone():
                if old['currency']!=currency or old['utc_offset']!=utc_offset:raise FactoryError('Da co du lieu: khong doi tien te / mui gio de tranh sai lich su.')
            db.execute('UPDATE plants SET name=?,currency=?,capacity=?,utc_offset=? WHERE code=?',(name,currency,capacity,utc_offset,code))
            self._audit(db,code,'UPDATE_PLANT',{'before':old,'after':{'name':name,'currency':currency,'capacity':capacity,'utc_offset':utc_offset}})
        return code

    def grant(self,plant,username,domain,write=False):
        self._admin();domain=int(domain)
        if domain not in range(1,11) or not isinstance(write,bool):raise FactoryError('Ph\u00e2n h\u1ec7 / quy\u1ec1n kh\u00f4ng h\u1ee3p l\u1ec7.')
        if not any(x['username']==username and x['active'] for x in self.auth.list_users(self.session)):
            raise FactoryError('T\u00e0i kho\u1ea3n ch\u01b0a ho\u1ea1t \u0111\u1ed9ng.')
        with self.connection(True) as db:
            self._require(db,plant,5,True)
            db.execute('INSERT INTO grants VALUES(?,?,?,?) ON CONFLICT(username,plant,domain) DO UPDATE SET can_write=excluded.can_write',(username,plant,domain,int(write)))
            self._audit(db,plant,'GRANT',{'username':username,'domain':domain,'write':write})

    def revoke(self,plant,username,domain):
        self._admin()
        with self.connection(True) as db:
            self._require(db,plant,5,True)
            db.execute('DELETE FROM grants WHERE plant=? AND username=? AND domain=?',(plant,username,int(domain)))
            self._audit(db,plant,'REVOKE',{'username':username,'domain':int(domain)})

    def list_grants(self,plant):
        self._admin()
        with self.connection() as db:
            self._require(db,plant,5)
            return [dict(r) for r in db.execute('SELECT username,domain,can_write FROM grants WHERE plant=? ORDER BY username,domain',(plant,))]

    def _rows(self,db,plant,kind):
        rows=db.execute('SELECT code,data,rev,updated,actor FROM records WHERE plant=? AND kind=? ORDER BY code LIMIT ?',(plant,kind,MAX_RECORDS+1)).fetchall()
        if len(rows)>MAX_RECORDS:raise FactoryError('V\u01b0\u1ee3t gi\u1edbi h\u1ea1n x\u1eed l\u00fd c\u1ee5c b\u1ed9; c\u1ea7n CSDL m\u00e1y ch\u1ee7.')
        return [dict(code=r['code'],**json.loads(r['data']),_rev=r['rev'],_updated=r['updated'],_actor=r['actor']) for r in rows]

    def _get(self,db,plant,kind,code):
        r=db.execute('SELECT * FROM records WHERE plant=? AND kind=? AND code=?',(plant,kind,code)).fetchone()
        if not r: raise FactoryError('Kh\u00f4ng t\u00ecm th\u1ea5y '+kind+': '+str(code))
        return json.loads(r['data']),r['rev']

    def _write(self,db,plant,kind,code,data,rev):
        if rev==0:
            try:db.execute('INSERT INTO records VALUES(?,?,?,?,?,?,?)',(plant,kind,code,packed(data),1,now(),self.session.username))
            except sqlite3.IntegrityError:raise Conflict('M\u00e3 \u0111\u00e3 t\u1ed3n t\u1ea1i: '+code)
        else:
            n=db.execute('UPDATE records SET data=?,rev=rev+1,updated=?,actor=? WHERE plant=? AND kind=? AND code=? AND rev=?',(packed(data),now(),self.session.username,plant,kind,code,rev)).rowcount
            if n!=1:raise Conflict('D\u1eef li\u1ec7u \u0111\u00e3 thay \u0111\u1ed5i. T\u1ea3i l\u1ea1i tr\u01b0\u1edbc khi l\u01b0u.')
        return rev+1

    def list_records(self,plant,kind,search='',page=0,limit=100):
        if kind not in ENTITIES:raise FactoryError('Ph\u00e2n h\u1ec7 kh\u00f4ng h\u1ee3p l\u1ec7.')
        page=int(page);limit=int(limit)
        if page<0 or not 1<=limit<=500:raise FactoryError('Ph\u00e2n trang kh\u00f4ng h\u1ee3p l\u1ec7.')
        search=text(search,100).replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        with self.connection() as db:
            self._require(db,plant,ENTITIES[kind]['group'])
            where="plant=? AND kind=? AND (code LIKE ? ESCAPE '\\' OR data LIKE ? ESCAPE '\\')"
            args=(plant,kind,'%'+search+'%','%'+search+'%')
            total=db.execute('SELECT COUNT(*) FROM records WHERE '+where,args).fetchone()[0]
            rows=db.execute('SELECT code,data,rev,updated,actor FROM records WHERE '+where+' ORDER BY updated DESC,code LIMIT ? OFFSET ?',args+(limit,page*limit)).fetchall()
            return {'total':total,'rows':[dict(code=r['code'],**json.loads(r['data']),_rev=r['rev'],_updated=r['updated'],_actor=r['actor']) for r in rows]}

    def save(self,plant,kind,code,values,expected_rev=0):
        data=clean_input(kind,values);code=ident(code)
        if isinstance(expected_rev,bool) or int(expected_rev)!=expected_rev or expected_rev<0:raise FactoryError('Revision kh\u00f4ng h\u1ee3p l\u1ec7.')
        with self.connection(True) as db:
            self._require(db,plant,ENTITIES[kind]['group'],True,ENTITIES[kind]['admin'])
            return self._save(db,plant,kind,code,data,expected_rev)

    def _save(self,db,plant,kind,code,data,rev):
        old=None
        if rev:
            if ENTITIES[kind]['immutable']:raise FactoryError('Ch\u1ee9ng t\u1eeb \u0111\u00e3 ghi s\u1ed5: kh\u00f4ng s\u1eeda tr\u1ef1c ti\u1ebfp.')
            old,actual=self._get(db,plant,kind,code)
            if actual!=rev:raise Conflict('D\u1eef li\u1ec7u \u0111\u00e3 \u0111\u01b0\u1ee3c ng\u01b0\u1eddi kh\u00e1c thay \u0111\u1ed5i.')
        for f in ENTITIES[kind]['fields']:
            if f.ref and data[f.key]:self._get(db,plant,f.ref,data[f.key])
        self._validate(db,plant,kind,code,data,old)
        if kind=='orders':
            data['good_qty']=old.get('good_qty','0') if old else '0'
            if old and old.get('bom_snapshot'):data['bom_snapshot']=old['bom_snapshot']
            if data['state']=='RELEASED' and not data.get('bom_snapshot'):
                data['bom_snapshot']=self._leaf_bom(db,plant,data['product'],D(data['quantity']))
        if kind=='lots':data['initial_quantity']=data['quantity']
        if kind=='counts':
            data['snapshot_at']=now()
            lot,_=self._get(db,plant,'lots',data['lot']);data['book_quantity']=lot['quantity']
        newrev=self._write(db,plant,kind,code,data,rev)
        if kind=='readings':
            sensor,_=self._get(db,plant,'sensors',data['sensor'])
            if D(data['value'])<D(sensor['low']) or D(data['value'])>D(sensor['high']):
                incident={'title':'Threshold '+data['sensor'],'severity':'WARNING','state':'OPEN','owner':'','notes':'Sample '+code+' = '+data['value']+' '+sensor['unit']}
                self._write(db,plant,'incidents','AUTO-'+uuid.uuid4().hex[:20],incident,0)
                self._audit(db,plant,'THRESHOLD_ALERT',{'sample':code,'sensor':data['sensor']})
        if kind=='inspections' and D(data['rejected'])>0:
            lot,lr=self._get(db,plant,'lots',data['lot']);lot['quality']='BLOCKED'
            self._write(db,plant,'lots',data['lot'],lot,lr)
            self._audit(db,plant,'QUARANTINE',{'lot':data['lot'],'inspection':code})
        self._audit(db,plant,'CREATE' if not rev else 'UPDATE',{'kind':kind,'code':code,'before':old,'after':data})
        return newrev

    def _validate(self,db,plant,kind,code,d,old):
        if kind=='assets':
            rows=self._rows(db,plant,kind)
            if d['ip'] and any(x['code']!=code and x['ip']==d['ip'] for x in rows):raise Conflict('IP \u0111\u00e3 c\u00f3 trong s\u1ed5 thi\u1ebft b\u1ecb nh\u00e0 m\u00e1y.')
            parents={r['code']:r['parent'] for r in rows};parents[code]=d['parent'];seen={code};p=d['parent']
            while p:
                if p in seen:raise FactoryError('Li\u00ean k\u1ebft thi\u1ebft b\u1ecb t\u1ea1o v\u00f2ng l\u1eb7p.')
                seen.add(p);p=parents.get(p,'')
        if kind=='sensors' and D(d['low'])>=D(d['high']):raise FactoryError('Ng\u01b0\u1ee1ng d\u01b0\u1edbi ph\u1ea3i nh\u1ecf h\u01a1n ng\u01b0\u1ee1ng tr\u00ean.')
        if kind=='readings' and dt(d['at'])>datetime.now(UTC)+timedelta(minutes=5):raise FactoryError('M\u1eabu \u0111o n\u1eb1m trong t\u01b0\u01a1ng lai (>5 ph\u00fat).')
        if kind=='lots' and d['received']>self._local_date(db,plant):raise FactoryError('Ngay nhap lo khong duoc nam trong tuong lai; dung hang dang ve.')
        if kind=='lots' and d['expiry'] and d['expiry']<d['received']:raise FactoryError('H\u1ea1n d\u00f9ng tr\u01b0\u1edbc ng\u00e0y nh\u1eadp.')
        if kind in ('docks','maintenance','shifts','energy'):
            if dt(d['end'])<=dt(d['start']):raise FactoryError('K\u1ebft th\u00fac ph\u1ea3i sau b\u1eaft \u0111\u1ea7u.')
        if kind in ('docks','shifts','energy'):
            for r in self._rows(db,plant,kind):
                same=(r['dock']==d['dock'] or r['vehicle']==d['vehicle']) if kind=='docks' else ((r['staff']==d['staff'] or r['asset']==d['asset']) if kind=='shifts' else r['asset']==d['asset'])
                if r['code']!=code and same and overlap(dt(d['start']),dt(d['end']),dt(r['start']),dt(r['end'])):raise Conflict('Kho\u1ea3ng th\u1eddi gian b\u1ecb tr\u00f9ng l\u1ecbch.')
        if kind=='bom':
            parent,_=self._get(db,plant,'materials',d['parent'])
            if parent['type']!='MAKE':raise FactoryError('M\u00e3 cha BOM ph\u1ea3i l\u00e0 MAKE.')
            rows=[x for x in self._rows(db,plant,'bom') if x['code']!=code]
            if any(x['parent']==d['parent'] and x['component']==d['component'] for x in rows):raise Conflict('C\u1eb7p cha / linh ki\u1ec7n \u0111\u00e3 c\u00f3 trong BOM.')
            self._graph(rows+[d])
        if kind=='materials' and old:
            if d['unit']!=old['unit'] and any(x['material']==code for x in self._rows(db,plant,'lots')):raise FactoryError('Kh\u00f4ng \u0111\u1ed5i \u0111\u01a1n v\u1ecb khi \u0111\u00e3 c\u00f3 l\u00f4; c\u1ea7n quy \u0111\u1ed5i c\u00f3 ki\u1ec3m so\u00e1t.')
            if d['type']=='BUY' and any(x['parent']==code for x in self._rows(db,plant,'bom')):raise FactoryError('V\u1eadt t\u01b0 cha BOM ph\u1ea3i gi\u1eef lo\u1ea1i MAKE.')
        if kind=='orders':
            if old and d['state']=='CANCELLED' and old['state']!='CANCELLED':
                if any(x['payload']['order']==code for x in self._issues(db,plant)):
                    raise FactoryError('Hoan tra vat tu da cap truoc khi huy lenh.')
            if not old and d['state']!='DRAFT':raise FactoryError('L\u1ec7nh m\u1edbi ph\u1ea3i \u1edf tr\u1ea1ng th\u00e1i DRAFT.')
            if old:
                allowed={'DRAFT':{'DRAFT','RELEASED','CANCELLED'},'RELEASED':{'RELEASED','HOLD','CLOSED'},'HOLD':{'HOLD','RELEASED','CANCELLED'},'CLOSED':{'CLOSED'},'CANCELLED':{'CANCELLED'}}
                if d['state'] not in allowed[old['state']]:raise FactoryError('Chuy\u1ec3n tr\u1ea1ng th\u00e1i l\u1ec7nh kh\u00f4ng h\u1ee3p l\u1ec7.')
                if old['state'] in ('CLOSED','CANCELLED') and any(d[k]!=old[k] for k in d):raise FactoryError('L\u1ec7nh \u0111\u00e3 \u0111\u00f3ng: kh\u00f4ng \u0111\u01b0\u1ee3c thay \u0111\u1ed5i.')
                if old['state']!='DRAFT' and (d['product']!=old['product'] or d['quantity']!=old['quantity']):raise FactoryError('L\u1ec7nh \u0111\u00e3 ph\u00e1t h\u00e0nh: kh\u00f4ng \u0111\u1ed5i s\u1ea3n ph\u1ea9m / s\u1ed1 l\u01b0\u1ee3ng.')
                if d['state']=='CLOSED' and D(old.get('good_qty','0'))<D(d['quantity']):raise FactoryError('Ch\u01b0a \u0111\u1ee7 th\u00e0nh ph\u1ea9m \u0111\u1ec3 \u0111\u00f3ng l\u1ec7nh.')
        if kind=='oee':
            if D(d['run_min'])>D(d['planned_min']) or D(d['good'])>D(d['total']):raise FactoryError('Th\u1eddi gian / s\u1ea3n l\u01b0\u1ee3ng OEE kh\u00f4ng h\u1ee3p l\u1ec7.')
            if not D(d['run_min']) and D(d['total']):raise FactoryError('C\u00f3 s\u1ea3n l\u01b0\u1ee3ng nh\u01b0ng th\u1eddi gian ch\u1ea1y b\u1eb1ng 0.')
        if kind=='inspections':
            lot,_=self._get(db,plant,'lots',d['lot'])
            if D(d['sampled'])>D(lot.get('initial_quantity',lot['quantity'])):raise FactoryError('Co mau kiem vuot so luong lo ban dau.')
            if D(d['rejected'])>D(d['sampled']):raise FactoryError('S\u1ed1 l\u1ed7i v\u01b0\u1ee3t s\u1ed1 ki\u1ec3m.')
            if D(d['rejected']) and not d['reason']:raise FactoryError('C\u1ea7n ghi r\u00f5 lo\u1ea1i l\u1ed7i.')
        if kind=='capa':
            if not old and d['state']!='OPEN':raise FactoryError('CAPA m\u1edbi ph\u1ea3i l\u00e0 OPEN.')
            if old:
                allowed={'OPEN':('OPEN','IN_PROGRESS'),'IN_PROGRESS':('IN_PROGRESS','VERIFY'),'VERIFY':('VERIFY','IN_PROGRESS','CLOSED'),'CLOSED':('CLOSED',)}
                if d['state'] not in allowed[old['state']]:raise FactoryError('Chuy\u1ec3n tr\u1ea1ng th\u00e1i CAPA kh\u00f4ng h\u1ee3p l\u1ec7.')
                if old['state']=='CLOSED' and d!=old:raise FactoryError('CAPA \u0111\u00e3 \u0111\u00f3ng kh\u00f4ng \u0111\u01b0\u1ee3c s\u1eeda.')
            if d['state'] in ('VERIFY','CLOSED') and (not d['cause'] or not d['action']):raise FactoryError('C\u1ea7n nguy\u00ean nh\u00e2n v\u00e0 h\u00e0nh \u0111\u1ed9ng.')
            if d['state']=='CLOSED' and not d['verification']:raise FactoryError('Thi\u1ebfu b\u1eb1ng ch\u1ee9ng x\u00e1c minh CAPA.')
        if kind=='calibrations' and d['due']<d['calibrated']:raise FactoryError('H\u1ea1n hi\u1ec7u chu\u1ea9n kh\u00f4ng h\u1ee3p l\u1ec7.')
        if kind=='skills' and d['valid_to']<d['valid_from']:raise FactoryError('Kho\u1ea3ng hi\u1ec7u l\u1ef1c ch\u1ee9ng ch\u1ec9 kh\u00f4ng h\u1ee3p l\u1ec7.')
        if kind=='shifts':
            staff,_=self._get(db,plant,'staff',d['staff']);asset,_=self._get(db,plant,'assets',d['asset'])
            if staff['active']!='YES':raise FactoryError('Nh\u00e2n s\u1ef1 kh\u00f4ng ho\u1ea1t \u0111\u1ed9ng.')
            if asset['state']=='MAINTENANCE':raise FactoryError('M\u00e1y \u0111ang b\u1ea3o tr\u00ec.')
            if any(x['asset']==d['asset'] and overlap(dt(d['start']),dt(d['end']),dt(x['start']),dt(x['end'])) for x in self._rows(db,plant,'maintenance')):raise FactoryError('Ca tr\u00f9ng l\u1ecbch b\u1ea3o tr\u00ec.')
            if asset['skill']:
                a=self._local_date(db,plant,d['start']);b=self._local_date(db,plant,d['end'])
                if not any(s['staff']==d['staff'] and s['skill']==asset['skill'] and s['valid_from']<=a and s['valid_to']>=b for s in self._rows(db,plant,'skills')):raise FactoryError('Thi\u1ebfu ch\u1ee9ng ch\u1ec9 c\u00f2n hi\u1ec7u l\u1ef1c cho to\u00e0n b\u1ed9 ca.')
        if kind=='energy' and d['factor'] and (not d['factor_source'] or not d['factor_date']):raise FactoryError('H\u1ec7 s\u1ed1 CO2e c\u1ea7n ngu\u1ed3n v\u00e0 ng\u00e0y hi\u1ec7u l\u1ef1c.')
        if kind=='incidents' and d['state']=='RESOLVED' and not d['notes']:raise FactoryError('C\u1ea7n ghi bi\u1ec7n ph\u00e1p x\u1eed l\u00fd tr\u01b0\u1edbc khi \u0111\u00f3ng s\u1ef1 c\u1ed1.')

    @staticmethod
    def _graph(rows):
        graph={}
        for r in rows:graph.setdefault(r['parent'],[]).append((r['component'],D(r['per'])))
        state={};height={};post=[]
        def visit(node):
            if state.get(node)==1:raise FactoryError('BOM c\u00f3 v\u00f2ng l\u1eb7p.')
            if state.get(node)==2:return height[node]
            state[node]=1;h=0
            for child,_ in graph.get(node,[]):h=max(h,1+visit(child))
            if h>10:raise FactoryError('BOM v\u01b0\u1ee3t 10 c\u1ea5p; kh\u00f4ng t\u1ef1 b\u1ecf qua linh ki\u1ec7n.')
            state[node]=2;height[node]=h;post.append(node);return h
        for n in graph:visit(n)
        return graph,list(reversed(post))

    def _leaf_bom(self,db,plant,product,quantity):
        graph,_=self._graph(self._rows(db,plant,'bom'))
        materials={x['code']:x for x in self._rows(db,plant,'materials')}
        result={}
        def expand(item,qty,depth=0):
            if depth>10:raise FactoryError('BOM qu\u00e1 10 c\u1ea5p.')
            mat=materials.get(item)
            if mat is None:raise FactoryError('BOM tham chi\u1ebfu v\u1eadt t\u01b0 kh\u00f4ng t\u1ed3n t\u1ea1i.')
            children=graph.get(item,[])
            if mat['type']=='MAKE' and not children:raise FactoryError('Thi\u1ebfu BOM cho '+item)
            if children:
                for child,per in children:expand(child,qty*per,depth+1)
            else:result[item]=result.get(item,D(0))+qty
        expand(product,quantity)
        return {k:dec(number(v)) for k,v in result.items()}

    def _prior_post(self,db,plant,request,action,payload):
        r=db.execute('SELECT action,payload,result FROM postings WHERE plant=? AND request_id=?',(plant,request)).fetchone()
        if r:
            if r['action']!=action or r['payload']!=packed(payload):raise Conflict('M\u00e3 giao d\u1ecbch \u0111\u00e3 d\u00f9ng v\u1edbi n\u1ed9i dung kh\u00e1c.')
            return json.loads(r['result'])
        return None

    def _post(self,db,plant,request,action,payload,result):
        db.execute('INSERT INTO postings VALUES(?,?,?,?,?,?,?)',(plant,request,action,packed(payload),packed(result),now(),self.session.username))
        self._audit(db,plant,action,{'request':request,'payload':payload,'result':result})

    def lot_quality(self,plant,lot,quality,reason):
        if quality not in ('HOLD','RELEASED','BLOCKED') or not text(reason):raise FactoryError('C\u1ea7n tr\u1ea1ng th\u00e1i v\u00e0 l\u00fd do.')
        with self.connection(True) as db:
            self._require(db,plant,8,True)
            data,rev=self._get(db,plant,'lots',ident(lot));before=data['quality'];data['quality']=quality
            self._write(db,plant,'lots',lot,data,rev)
            self._audit(db,plant,'LOT_QUALITY',{'lot':lot,'before':before,'after':quality,'reason':text(reason)})
        return quality

    def issue(self,plant,request,order,material,quantity,on_date=None):
        request=ident(request);order=ident(order);material=ident(material);q=number(quantity,positive=True)
        with self.connection(True) as db:
            self._require(db,plant,3,True)
            today=self._local_date(db,plant)
            on_date=iso_date(on_date or today)
            if on_date!=today:raise FactoryError('Chi ghi so xuat kho theo ngay hien tai cua nha may.')
            payload={'order':order,'material':material,'quantity':dec(q),'date':on_date}
            prior=self._prior_post(db,plant,request,'ISSUE',payload)
            if prior is not None:return prior
            job,_=self._get(db,plant,'orders',order)
            if job['state']!='RELEASED':raise FactoryError('Ch\u1ec9 xu\u1ea5t v\u1eadt t\u01b0 cho l\u1ec7nh RELEASED.')
            bom=job.get('bom_snapshot')
            if not bom:raise FactoryError('L\u1ec7nh ch\u01b0a c\u00f3 BOM ch\u1ed1t khi ph\u00e1t h\u00e0nh.')
            already=D(0)
            for p in self._issues(db,plant):
                x=p['payload']
                if x['order']==order and x['material']==material:already+=D(x['quantity'])
            if material not in bom or already+q>D(bom[material]):raise FactoryError('V\u01b0\u1ee3t \u0111\u1ecbnh m\u1ee9c BOM \u0111\u00e3 ch\u1ed1t ho\u1eb7c sai v\u1eadt t\u01b0.')
            lots=[x for x in self._rows(db,plant,'lots') if x['material']==material and x['quality']=='RELEASED' and x['received']<=on_date and (not x['expiry'] or x['expiry']>on_date) and D(x['quantity'])>0]
            lots.sort(key=lambda x:(x['expiry'] or '9999-12-31',x['received'],x['code']))
            if sum((D(x['quantity']) for x in lots),D(0))<q:raise FactoryError('Thi\u1ebfu t\u1ed3n kh\u1ea3 d\u1ee5ng (lo\u1ea1i l\u00f4 h\u1ebft h\u1ea1n / HOLD / BLOCKED).')
            remain=q;allocations=[]
            for lot in lots:
                used=min(remain,D(lot['quantity']))
                if used<=0:continue
                data,rev=self._get(db,plant,'lots',lot['code']);data['quantity']=dec(D(data['quantity'])-used)
                self._write(db,plant,'lots',lot['code'],data,rev)
                allocations.append({'lot':lot['code'],'quantity':dec(used)});remain-=used
                if remain==0:break
            result={'order':order,'material':material,'quantity':dec(q),'allocations':allocations}
            self._post(db,plant,request,'ISSUE',payload,result)
            return result

    def return_issue(self,plant,request,issue_request,reason):
        request=ident(request);issue_request=ident(issue_request);reason=text(reason)
        if not reason:raise FactoryError('Can ly do hoan tra.')
        payload={'issue_request':issue_request,'reason':reason}
        with self.connection(True) as db:
            self._require(db,plant,3,True)
            prior=self._prior_post(db,plant,request,'RETURN',payload)
            if prior is not None:return prior
            issue=next((x for x in self._issues(db,plant) if x['request']==issue_request),None)
            if issue is None:raise FactoryError('Phieu xuat khong ton tai hoac da hoan tra.')
            order=issue['payload']['order']
            for r in db.execute("SELECT payload FROM postings WHERE plant=? AND action='OUTPUT'",(plant,)):
                if json.loads(r[0])['order']==order:raise FactoryError('Lenh da co thanh pham; can quy trinh hoan tra WIP rieng.')
            for item in issue['result']['allocations']:
                lot,rev=self._get(db,plant,'lots',item['lot']);lot['quantity']=dec(D(lot['quantity'])+D(item['quantity']))
                self._write(db,plant,'lots',item['lot'],lot,rev)
            result={'order':order,'returned':issue['result']['allocations']}
            self._post(db,plant,request,'RETURN',payload,result)
            return result

    def output(self,plant,request,order,good,scrap,lot,operator=''):
        request=ident(request);order=ident(order);lot=ident(lot);good=number(good,positive=True);scrap=number(scrap);operator=text(operator,64)
        payload={'order':order,'good':dec(good),'scrap':dec(scrap),'lot':lot,'operator':operator}
        with self.connection(True) as db:
            self._require(db,plant,4,True)
            prior=self._prior_post(db,plant,request,'OUTPUT',payload)
            if prior is not None:return prior
            job,rev=self._get(db,plant,'orders',order)
            if job['state']!='RELEASED':raise FactoryError('L\u1ec7nh ch\u01b0a RELEASED ho\u1eb7c \u0111\u00e3 \u0111\u00f3ng.')
            new=D(job.get('good_qty','0'))+good
            if new>D(job['quantity']):raise FactoryError('Th\u00e0nh ph\u1ea9m v\u01b0\u1ee3t k\u1ebf ho\u1ea1ch.')
            if operator:self._get(db,plant,'staff',operator)
            # Traceability requires all declared input materials to have been issued.
            issued={}
            for r in self._issues(db,plant):
                p=r['payload']
                if p['order']==order:issued[p['material']]=issued.get(p['material'],D(0))+D(p['quantity'])
            for material,required in job.get('bom_snapshot',{}).items():
                if issued.get(material,D(0)) < D(required)*new/D(job['quantity']):raise FactoryError('Ch\u01b0a c\u1ea5p \u0111\u1ee7 v\u1eadt t\u01b0 cho s\u1ea3n l\u01b0\u1ee3ng n\u00e0y.')
            lotdata={'material':job['product'],'quantity':dec(good),'received':self._local_date(db,plant),'initial_quantity':dec(good),'expiry':'','quality':'HOLD','location':'FG','owner':'','source_order':order}
            self._write(db,plant,'lots',lot,lotdata,0)
            job['good_qty']=dec(new);self._write(db,plant,'orders',order,job,rev)
            result=dict(payload,at=now(),quality='HOLD')
            self._post(db,plant,request,'OUTPUT',payload,result)
            return result

    def mrp(self,plant,product,quantity,need_date):
        """Scenario netting at ONE need date; no automatic demand import from ERP."""
        product=ident(product);qty=number(quantity,positive=True);need_date=iso_date(need_date)
        with self.connection() as db:
            self._require(db,plant,4)
            materials={x['code']:x for x in self._rows(db,plant,'materials')}
            if product not in materials:raise FactoryError('Kh\u00f4ng c\u00f3 s\u1ea3n ph\u1ea9m.')
            graph,topo=self._graph(self._rows(db,plant,'bom'))
            if product not in topo:topo.insert(0,product)
            stock={};incoming={}
            for r in self._rows(db,plant,'lots'):
                if r['quality']=='RELEASED' and r['received']<=need_date and (not r['expiry'] or r['expiry']>need_date):stock[r['material']]=stock.get(r['material'],D(0))+D(r['quantity'])
            for r in self._rows(db,plant,'inbound'):
                if r['status']=='OPEN' and r['eta']<=need_date:incoming[r['material']]=incoming.get(r['material'],D(0))+D(r['quantity'])
            gross={product:qty};rows=[]
            for code in topo:
                if code not in gross:continue
                mat=materials[code];required=gross[code];safety=D(mat['safety']);onhand=stock.get(code,D(0));inbound=incoming.get(code,D(0))
                net=max(D(0),required+safety-onhand-inbound)
                rows.append({'material':code,'type':mat['type'],'unit':mat['unit'],'gross':dec(required),'safety':dec(safety),'onhand':dec(onhand),'inbound_by_date':dec(inbound),'net':dec(net),'need_date':need_date})
                if mat['type']=='MAKE' and net:
                    if not graph.get(code):raise FactoryError('Thi\u1ebfu BOM cho '+code+'; kh\u00f4ng tr\u1ea3 k\u1ebft qu\u1ea3 thi\u1ebfu linh ki\u1ec7n.')
                    for child,per in graph[code]:gross[child]=gross.get(child,D(0))+net*per
            return rows

    def plan(self,plant,asset,start):
        """Single selected machine; deterministic draft, no machine control."""
        asset=ident(asset);start=stamp(start)
        with self.connection() as db:
            self._require(db,plant,4)
            machine,_=self._get(db,plant,'assets',asset)
            rate=D(machine['capacity'])
            if machine['type']!='MACHINE' or machine['state']=='MAINTENANCE' or rate<=0:raise FactoryError('M\u00e1y kh\u00f4ng kh\u1ea3 d\u1ee5ng ho\u1eb7c ch\u01b0a c\u00f3 c\u00f4ng su\u1ea5t.')
            blocks=sorted([(dt(x['start']),dt(x['end'])) for x in self._rows(db,plant,'maintenance') if x['asset']==asset])
            jobs=[x for x in self._rows(db,plant,'orders') if x['state'] in ('DRAFT','RELEASED') and D(x['quantity'])>D(x.get('good_qty','0'))]
            jobs.sort(key=lambda x:(x['due'],-int(x['priority']),x['code']))
            current=dt(start);rows=[]
            for job in jobs:
                seconds=((D(job['quantity'])-D(job.get('good_qty','0')))*3600/rate).to_integral_value(rounding=ROUND_CEILING)
                if seconds>D('31536000'):raise FactoryError('Th\u1eddi l\u01b0\u1ee3ng v\u01b0\u1ee3t m\u1ed9t n\u0103m; ki\u1ec3m tra c\u00f4ng su\u1ea5t.')
                duration=timedelta(seconds=int(seconds));shifted=False
                for a,b in blocks:
                    if overlap(current,current+duration,a,b):current=b;shifted=True
                end=current+duration
                rows.append({'order':job['code'],'asset':asset,'start_utc':current.isoformat(),'finish_utc':end.isoformat(),'due':job['due'],'late':self._local_date(db,plant,end.isoformat())>job['due'],'maintenance_shifted':shifted,'state':'DRAFT_ONLY'})
                current=end
            return rows

    def allocation(self,quantity):
        self._admin();quantity=number(quantity,positive=True)
        rows=self.plants();total=sum((D(x['capacity']) for x in rows),D(0))
        if total==0:raise FactoryError('Ch\u01b0a khai b\u00e1o c\u00f4ng su\u1ea5t c\u00e1c nh\u00e0 m\u00e1y.')
        remaining=quantity;result=[];eligible=[r for r in rows if D(r['capacity'])>0]
        for i,r in enumerate(eligible):
            q=remaining if i==len(eligible)-1 else (quantity*D(r['capacity'])/total).quantize(D('0.000001'),rounding=ROUND_FLOOR)
            remaining-=q;result.append({'plant':r['code'],'capacity_weight':r['capacity'],'suggested_qty':dec(q),'state':'PROPOSAL_ONLY'})
        return result

    def trace(self,plant,lot):
        lot=ident(lot)
        with self.connection() as db:
            self._require(db,plant,8);self._get(db,plant,'lots',lot)
            issues=[];outputs=[]
            valid_issues={x['request'] for x in self._issues(db,plant)}
            for r in db.execute("SELECT request_id,action,payload,result,created,actor FROM postings WHERE plant=? AND action IN ('ISSUE','OUTPUT')",(plant,)):
                if r['action']=='ISSUE' and r['request_id'] not in valid_issues:continue
                p=json.loads(r['payload']);p.update(json.loads(r['result']));p['created']=r['created'];p['actor']=r['actor']
                (issues if r['action']=='ISSUE' else outputs).append(p)
            # Reachability across multi-stage orders (not just one direct hop).
            lots={lot};orders=set();changed=True
            while changed:
                before=(len(lots),len(orders))
                for i in issues:
                    consumed={x['lot'] for x in i['allocations']}
                    if consumed & lots or i['order'] in orders:orders.add(i['order']);lots.update(consumed)
                for o in outputs:
                    if o['lot'] in lots or o['order'] in orders:orders.add(o['order']);lots.add(o['lot'])
                changed=before!=(len(lots),len(orders))
            rows=[]
            for i in issues:
                if i['order'] in orders:
                    for a in i['allocations']:rows.append({'direction':'INPUT_LOT -> ORDER','lot':a['lot'],'order':i['order'],'quantity':a['quantity'],'at':i['created']})
            for o in outputs:
                if o['order'] in orders:rows.append({'direction':'ORDER -> OUTPUT_LOT','lot':o['lot'],'order':o['order'],'quantity':o['good'],'at':o['created']})
            return rows

    def report(self,plant,kind,**options):
        domain={'stock':3,'reconcile':3,'abc':3,'oee':4,'outputs':4,'sensors':2,'risks':1,'quality':8,'expiry':8,'energy_report':10,'topology':7,'audit':5}.get(kind)
        if domain is None:raise FactoryError('B\u00e1o c\u00e1o kh\u00f4ng h\u1ee3p l\u1ec7.')
        with self.connection() as db:
            self._require(db,plant,domain)
            if kind=='stock':return self._stock(db,plant)
            if kind=='reconcile':
                return [{'count':x['code'],'lot':x['lot'],'counted':x['counted'],'book_at_count':x['book_quantity'],'difference':dec(D(x['counted'])-D(x['book_quantity'])),'counted_at':x['at'],'snapshot_at':x['snapshot_at']} for x in self._rows(db,plant,'counts')]
            if kind=='oee':
                rows=[]
                for x in self._rows(db,plant,'oee'):
                    a=D(x['run_min'])/D(x['planned_min']);p=D(x['cycle_sec'])*D(x['total'])/(D(x['run_min'])*60) if D(x['run_min']) else D(0);q=D(x['good'])/D(x['total']) if D(x['total']) else D(0)
                    rows.append({'shift':x['code'],'asset':x['asset'],'date':x['date'],'availability_pct':dec((a*100).quantize(D('.01'))),'performance_pct':dec((p*100).quantize(D('.01'))),'quality_pct':dec((q*100).quantize(D('.01'))),'oee_pct':dec((a*p*q*100).quantize(D('.01'))),'warning':'CHECK_CYCLE_TIME' if p>1 else ''})
                return rows
            if kind=='outputs':
                return [dict(request=r['request_id'],**json.loads(r['result'])) for r in db.execute("SELECT request_id,result FROM postings WHERE plant=? AND action='OUTPUT' ORDER BY created DESC LIMIT 20000",(plant,))]
            if kind=='sensors':
                readings=self._rows(db,plant,'readings');rows=[]
                for s in self._rows(db,plant,'sensors'):
                    samples=[r for r in readings if r['sensor']==s['code']];latest=max(samples,key=lambda r:r['at']) if samples else None
                    status='NO_DATA'
                    if latest:
                        status='STALE' if (datetime.now(UTC)-dt(latest['at'])).total_seconds()>float(D(s['stale_minutes'])*60) else ('ALERT' if D(latest['value'])<D(s['low']) or D(latest['value'])>D(s['high']) else 'IN_RANGE')
                    rows.append({'sensor':s['code'],'asset':s['asset'],'value':latest['value'] if latest else '', 'unit':s['unit'],'at':latest['at'] if latest else '', 'status':status,'source':'MANUAL_OR_CSV'})
                return rows
            if kind=='risks':
                rows=[{'type':'SUPPLIER','code':s['code'],'risk':'HIGH','reason':'Entered risk grade'} for s in self._rows(db,plant,'suppliers') if s['risk']=='HIGH']
                rows += [{'type':'SHIPMENT','code':s['code'],'risk':'LATE','reason':s['due']} for s in self._rows(db,plant,'shipments') if s['status'] not in ('DELIVERED','CANCELLED') and s['due']<self._local_date(db,plant)]
                return rows
            if kind=='quality':
                totals={}
                for x in self._rows(db,plant,'inspections'):
                    key=(x['stage'],x['reason'] or 'NO_DEFECT');agg=totals.setdefault(key,[D(0),D(0)]);agg[0]+=D(x['sampled']);agg[1]+=D(x['rejected'])
                return [{'stage':k[0],'reason':k[1],'sampled':dec(v[0]),'rejected':dec(v[1]),'defect_pct':dec((v[1]/v[0]*100).quantize(D('.01')))} for k,v in totals.items()]
            if kind=='expiry':
                today=self._local_date(db,plant);rows=[]
                for entity,field in (('calibrations','due'),('skills','valid_to'),('licenses','expires'),('assets','maintenance_due')):
                    if not self.can(plant,ENTITIES[entity]['group']):continue
                    candidates=self._rows(db,plant,entity)
                    if entity=='calibrations':
                        latest={}
                        for r in candidates:
                            if r['asset'] not in latest or r['calibrated']>latest[r['asset']]['calibrated']:latest[r['asset']]=r
                        candidates=list(latest.values())
                    if entity=='skills':
                        valid={(r['staff'],r['skill']) for r in candidates if r['valid_from']<=today<=r['valid_to']}
                        candidates=[r for r in candidates if (r['staff'],r['skill']) not in valid]
                    for r in candidates:
                        if r[field] and r[field]<today:rows.append({'kind':entity,'code':r['code'],'due':r[field],'status':'OVERDUE_RECORD'})
                return rows
            if kind=='energy_report':
                threshold=number(options.get('idle_threshold','0'))
                rows=[]
                for r in self._rows(db,plant,'energy'):
                    kwh=D(r['kwh']);factor=D(r['factor']) if r['factor'] else None
                    rows.append({'record':r['code'],'asset':r['asset'],'kwh':r['kwh'],'cost':dec(kwh*D(r['tariff'])),'co2e_kg':dec(kwh*factor) if factor is not None else 'UNKNOWN','factor_source':r['factor_source'],'factor_date':r['factor_date'],'idle_alert':r['state']=='IDLE' and kwh>threshold,'start':r['start'],'end':r['end']})
                return rows
            if kind=='topology':return [{'asset':r['code'],'parent':r['parent'],'type':r['type'],'ip':r['ip'],'state':r['state'],'source':'MANUALLY_DECLARED'} for r in self._rows(db,plant,'assets')]
            if kind=='audit':
                if self.session.role not in ('it_admin','auditor'):raise AccessDenied('Audit can quyen quan tri hoac kiem toan.')
                return [dict(x) for x in db.execute('SELECT id,at,actor,action,detail FROM audit WHERE plant=? ORDER BY id DESC LIMIT 500',(plant,))]
            if kind=='abc':
                qty={}
                for r in self._issues(db,plant):
                    p=r['payload'];qty[p['material']]=qty.get(p['material'],D(0))+D(p['quantity'])
                # Quantity ranking is separated by unit; pcs and kg are never added together.
                mats={x['code']:x for x in self._rows(db,plant,'materials')};units={}
                for k,v in qty.items():units.setdefault(mats[k]['unit'],[]).append((k,v))
                result=[]
                for unit,items in units.items():
                    total=sum((v for _,v in items),D(0));cum=D(0)
                    for k,v in sorted(items,key=lambda x:-x[1]):
                        rank='A' if cum/total<D('.8') else ('B' if cum/total<D('.95') else 'C');cum+=v
                        result.append({'material':k,'unit':unit,'issued':dec(v),'class':rank,'cumulative_pct':dec((cum/total*100).quantize(D('.01')))})
                return result

    def _stock(self,db,plant):
        materials=self._rows(db,plant,'materials');lots=self._rows(db,plant,'lots');today=self._local_date(db,plant);rows=[]
        for m in materials:
            items=[l for l in lots if l['material']==m['code']];physical=sum((D(l['quantity']) for l in items),D(0))
            available=sum((D(l['quantity']) for l in items if l['quality']=='RELEASED' and l['received']<=today and (not l['expiry'] or l['expiry']>today)),D(0))
            rows.append({'material':m['code'],'unit':m['unit'],'physical':dec(physical),'available':dec(available),'safety':m['safety'],'status':'BELOW_SAFETY' if available<D(m['safety']) else 'OK'})
        return rows

    def overview(self,plant):
        result={'plant':plant,'as_of':now(),'source':'LOCAL_RECORDS'}
        with self.connection() as db:
            self._session()
            if not any(self.can(plant,g) for g in range(1,11)):raise AccessDenied('Kh\u00f4ng c\u00f3 quy\u1ec1n xem nh\u00e0 m\u00e1y.')
            for name,kind,domain in [('assets','assets',7),('orders','orders',4),('incidents','incidents',6),('lots','lots',3),('capa','capa',8)]:
                if self.can(plant,domain):
                    rows=self._rows(db,plant,kind)
                    if kind=='incidents':rows=[r for r in rows if r['state']!='RESOLVED']
                    result[name]=len(rows)
                else:result[name]=None
            if self.can(plant,3):result['shortages']=sum(1 for x in self._stock(db,plant) if x['status']=='BELOW_SAFETY')
            else:result['shortages']=None
        return result

    def preferences(self,values=None):
        self._session()
        with self.connection(values is not None) as db:
            if values is not None:
                if set(values)-{'plant','group'}:raise FactoryError('Thi\u1ebft l\u1eadp kh\u00f4ng h\u1ee3p l\u1ec7.')
                group=int(values.get('group',1))
                if group not in range(1,11):raise FactoryError('Nh\u00f3m kh\u00f4ng h\u1ee3p l\u1ec7.')
                plant=ident(values['plant']);self._require(db,plant,group)
                data={'plant':plant,'group':group}
                db.execute('INSERT INTO preferences VALUES(?,?) ON CONFLICT(username) DO UPDATE SET data=excluded.data',(self.session.username,packed(data)))
                self._audit(db,plant,'PREFERENCE',data)
            r=db.execute('SELECT data FROM preferences WHERE username=?',(self.session.username,)).fetchone()
            return json.loads(r[0]) if r else {}

    def import_csv(self,plant,kind,path):
        if kind not in ENTITIES:raise FactoryError('Lo\u1ea1i d\u1eef li\u1ec7u kh\u00f4ng h\u1ee3p l\u1ec7.')
        path=Path(path)
        if path.stat().st_size>5*1024*1024:raise FactoryError('CSV t\u1ed1i \u0111a 5 MB / 2000 d\u00f2ng.')
        expected={'code'}|{f.key for f in ENTITIES[kind]['fields']};rows=[];ids=set()
        with path.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)) or set(reader.fieldnames)!=expected:raise FactoryError('C\u1ed9t CSV kh\u00f4ng \u0111\u00fang m\u1eabu. T\u1ea3i m\u1eabu t\u1eeb giao di\u1ec7n.')
            for i,row in enumerate(reader,2):
                if len(rows)>=2000 or None in row or any(v is None for v in row.values()):raise FactoryError('CSV qu\u00e1 l\u1edbn / thi\u1ebfu ho\u1eb7c th\u1eeba c\u1ed9t.')
                code=ident(row.pop('code'))
                if code in ids:raise Conflict('Tr\u00f9ng m\u00e3 trong CSV: '+code)
                ids.add(code)
                try:rows.append((code,clean_input(kind,row)))
                except FactoryError as e:raise FactoryError('D\u00f2ng '+str(i)+': '+str(e))
        with self.connection(True) as db:
            self._require(db,plant,ENTITIES[kind]['group'],True,ENTITIES[kind]['admin'])
            for code,data in rows:self._save(db,plant,kind,code,data,0)
            self._audit(db,plant,'IMPORT_CSV',{'kind':kind,'rows':len(rows)})
        return len(rows)

    def export_records(self,plant,kind,path):
        if kind not in ENTITIES:raise FactoryError('Ph\u00e2n h\u1ec7 kh\u00f4ng h\u1ee3p l\u1ec7.')
        with self.connection() as db:
            self._require(db,plant,ENTITIES[kind]['group']);rows=self._rows(db,plant,kind)
        fields=['code']+[f.key for f in ENTITIES[kind]['fields']]
        self.write_csv(path,[{k:r.get(k,'') for k in fields} for r in rows],fields)
        with self.connection(True) as db:self._audit(db,plant,'EXPORT_CSV',{'kind':kind,'rows':len(rows)})
        return len(rows)

    def export_result(self,plant,domain,path,rows,fields=None):
        with self.connection() as db:self._require(db,plant,domain)
        self.write_csv(path,rows,fields)
        with self.connection(True) as db:self._audit(db,plant,'EXPORT_RESULT',{'domain':domain,'rows':len(rows)})
        return len(rows)

    @staticmethod
    def write_csv(path,rows,fields=None):
        fields=fields or (list(rows[0]) if rows else ['status'])
        created=False
        try:
            with open(path,'x',encoding='utf-8-sig',newline='') as f:
                created=True;w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
                for row in rows:w.writerow({k:csv_safe(row.get(k,'')) for k in fields})
                f.flush();os.fsync(f.fileno())
        except BaseException:
            if created:Path(path).unlink(missing_ok=True)
            raise

    def executive_html(self,plant,path):
        self._admin();summary=self.overview(plant);stock=self.report(plant,'stock');oee=self.report(plant,'oee')
        def table(rows):
            if not rows:return '<p>No records.</p>'
            cols=list(rows[0]);head=''.join('<th>'+html.escape(x)+'</th>' for x in cols)
            body=''.join('<tr>'+''.join('<td>'+html.escape(str(r.get(c,'')))+'</td>' for c in cols)+'</tr>' for r in rows)
            return '<table><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table>'
        page='<!doctype html><html lang="vi"><meta charset="utf-8"><title>Factory Report</title><style>body{font:15px system-ui;background:#0f172a;color:#e2e8f0;padding:40px}table{border-collapse:collapse;width:100%;margin:18px 0}td,th{padding:10px;border:1px solid #334155;text-align:left}h1{color:#38bdf8}</style><h1>Alibaba Operations Center</h1><p>LOCAL SNAPSHOT - not a live PLC/ERP report. Values reflect entered records only.</p>'+table([summary])+'<h2>Stock</h2>'+table(stock)+'<h2>OEE</h2>'+table(oee)+'</html>'
        with open(path,'x',encoding='utf-8') as f:f.write(page)
        with self.connection(True) as db:self._audit(db,plant,'EXPORT_HTML',{'stock_rows':len(stock),'oee_rows':len(oee)})
        return path

    def verify_audit(self):
        self._admin();prev='0'*64;count=0
        with self.connection() as db:
            for r in db.execute('SELECT * FROM audit ORDER BY id'):
                digest=hashlib.sha256(packed([prev,r['at'],r['actor'],r['plant'],r['action'],r['detail']]).encode()).hexdigest()
                if r['prev']!=prev or digest!=r['digest']:return {'ok':False,'first_bad_id':r['id'],'checked':count}
                count+=1;prev=r['digest']
        return {'ok':True,'checked':count,'head':prev,'limitation':'Not externally anchored; local OS administrator can rewrite the chain.'}

    def backup(self,path):
        self._admin();path=Path(path)
        if path.resolve()==self.path.resolve():raise FactoryError('Kh\u00f4ng ghi \u0111\u00e8 CSDL.')
        with tempfile.TemporaryDirectory(prefix='aoc-snapshot-') as temp:
            snap=Path(temp)/'factory.sqlite3'
            source=sqlite3.connect(self.path);target=sqlite3.connect(snap)
            try:
                source.backup(target)
                if target.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise FactoryError('Snapshot kh\u00f4ng to\u00e0n v\u1eb9n.')
            finally:target.close();source.close()
            manifest={'schema':SCHEMA_VERSION,'created':now(),'scope':'SMART_FACTORY_ONLY_NOT_ACCOUNTS_OR_LEGACY_MAIL','encrypted':False,'sha256':self._hash(snap)}
            created=False
            try:
                with open(path,'xb') as stream:
                    created=True
                    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as z:
                        z.write(snap,'factory.sqlite3');z.writestr('manifest.json',packed(manifest))
                    stream.flush();os.fsync(stream.fileno())
                self.verify_backup(path)
            except BaseException:
                if created:path.unlink(missing_ok=True)
                raise
            with self.connection(True) as db:self._audit(db,'','BACKUP',{'sha256':manifest['sha256'],'encrypted':False})
            return manifest

    @staticmethod
    def _hash(path):
        h=hashlib.sha256()
        with open(path,'rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        return h.hexdigest()

    def verify_backup(self,path,restore_path=None):
        self._admin()
        if restore_path and Path(restore_path).resolve()==self.path.resolve():raise FactoryError('Ch\u1ec9 ph\u1ee5c h\u1ed3i ra t\u1ec7p M\u1edaI; kh\u00f4ng thay CSDL \u0111ang ch\u1ea1y.')
        with zipfile.ZipFile(path) as z, tempfile.TemporaryDirectory(prefix='aoc-verify-') as temp:
            if z.namelist()!=['factory.sqlite3','manifest.json']:raise FactoryError('G\u00f3i sao l\u01b0u kh\u00f4ng \u0111\u00fang c\u1ea5u tr\u00fac.')
            if z.getinfo('manifest.json').file_size>65536 or z.getinfo('factory.sqlite3').file_size>512*1024*1024:raise FactoryError('G\u00f3i sao l\u01b0u v\u01b0\u1ee3t gi\u1edbi h\u1ea1n 512 MB.')
            manifest=json.loads(z.read('manifest.json'))
            if not isinstance(manifest,dict) or manifest.get('schema')!=SCHEMA_VERSION:raise FactoryError('Schema kh\u00f4ng t\u01b0\u01a1ng th\u00edch.')
            dest=Path(temp)/'factory.sqlite3';size=0
            with z.open('factory.sqlite3') as src,dest.open('wb') as out:
                for block in iter(lambda:src.read(1024*1024),b''):
                    size+=len(block)
                    if size>512*1024*1024:raise FactoryError('Snapshot qu\u00e1 l\u1edbn.')
                    out.write(block)
            if self._hash(dest)!=manifest.get('sha256'):raise FactoryError('Checksum kh\u00f4ng kh\u1edbp.')
            db=sqlite3.connect(dest)
            try:
                db.execute('PRAGMA trusted_schema=OFF');db.execute('PRAGMA query_only=ON')
                if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise FactoryError('CSDL h\u1ecfng.')
                if db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]!=str(SCHEMA_VERSION):raise FactoryError('Schema snapshot kh\u00f4ng kh\u1edbp.')
            finally:db.close()
            if restore_path:
                created=False
                try:
                    with open(restore_path,'xb') as out,dest.open('rb') as src:
                        created=True
                        for b in iter(lambda:src.read(1024*1024),b''):out.write(b)
                        out.flush();os.fsync(out.fileno())
                except BaseException:
                    if created:Path(restore_path).unlink(missing_ok=True)
                    raise
            return {'ok':True,'schema':SCHEMA_VERSION,'encrypted':False,'bytes':size,'restored_copy':str(restore_path or '')}


def cost_estimate(quantity,material,labor,energy,overhead):
    q=number(quantity,positive=True);parts=[number(v) for v in (material,labor,energy,overhead)];total=sum(parts,D(0))
    return {'quantity':dec(q),'total_cost':dec(total),'unit_cost':dec((total/q).quantize(D('.000001'))),'scope':'Entered costs for the whole lot; all amounts use one currency.'}

def what_if(quantity,regular,overtime,outsourced):
    q=number(quantity,positive=True)
    return [{'scenario':name,'unit_cost':dec(number(rate)),'quantity':dec(q),'total':dec(q*number(rate)),'scope':'Entered unit costs only; no transport/capacity optimizer.'} for name,rate in [('REGULAR',regular),('OVERTIME',overtime),('SUBCONTRACT',outsourced)]]

def roi_estimate(capex,annual_savings):
    capex=number(capex,positive=True);savings=number(annual_savings,signed=True)
    return {'capex':dec(capex),'annual_net_savings':dec(savings),'annual_return_pct':dec((savings/capex*100).quantize(D('.01'))),'simple_payback_years':dec((capex/savings).quantize(D('.01'))) if savings>0 else 'NO_POSITIVE_PAYBACK','scope':'Undiscounted entered-input estimate; not investment advice.'}
