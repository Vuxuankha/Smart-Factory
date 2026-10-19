"""Local, approval-gated PMC planning engine. No ERP writes or email side effects."""
import csv
import io
import json
import math
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, product TEXT NOT NULL, qty REAL NOT NULL CHECK(qty>0), due TEXT NOT NULL, priority INTEGER NOT NULL DEFAULT 1, customer TEXT NOT NULL DEFAULT '', produced REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS bom(product TEXT NOT NULL, material TEXT NOT NULL, per_unit REAL NOT NULL CHECK(per_unit>0), PRIMARY KEY(product,material));
CREATE TABLE IF NOT EXISTS stock(material TEXT PRIMARY KEY, onhand REAL NOT NULL DEFAULT 0, inbound REAL NOT NULL DEFAULT 0, counted REAL);
CREATE TABLE IF NOT EXISTS centers(name TEXT PRIMARY KEY, units_per_day REAL NOT NULL CHECK(units_per_day>0), enabled INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS schedule(order_id TEXT PRIMARY KEY, center TEXT NOT NULL, start TEXT NOT NULL, finish TEXT NOT NULL, days INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, order_id TEXT NOT NULL UNIQUE, state TEXT NOT NULL DEFAULT 'DRAFT', qr_payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY AUTOINCREMENT, material TEXT NOT NULL, qty REAL NOT NULL, need_by TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'DRAFT');
CREATE TABLE IF NOT EXISTS movements(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, material TEXT NOT NULL, qty REAL NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scrap(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL, material TEXT NOT NULL, actual_qty REAL NOT NULL, good_qty REAL NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, note TEXT NOT NULL, created TEXT NOT NULL);
'''

def csv_safe(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value

def today(): return datetime.now().date().isoformat()
def positive(v):
    v=float(v)
    if not math.isfinite(v) or v<=0: raise ValueError('Số lượng/công suất phải > 0 và hữu hạn')
    return v

def nonnegative(v):
    v=float(v)
    if not math.isfinite(v) or v<0: raise ValueError('Giá trị phải >= 0 và hữu hạn')
    return v

def date(v):
    return datetime.strptime(str(v), '%Y-%m-%d').date().isoformat()

class PMC:
    def __init__(self, dbfile):
        self.dbfile=str(dbfile)
        Path(self.dbfile).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db: db.executescript(SCHEMA)
    @contextmanager
    def connection(self):
        db=sqlite3.connect(self.dbfile, timeout=10)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()
    def query(self, sql, args=()):
        with self.connection() as db: return [dict(r) for r in db.execute(sql,args)]
    def event(self, db, kind, note): db.execute('INSERT INTO events(kind,note,created) VALUES(?,?,?)',(kind,str(note)[:1000],today()))
    def order(self, oid, product, qty, due, priority=1, customer=''):
        if not str(oid).strip() or not str(product).strip(): raise ValueError('Thiếu mã đơn hoặc mã hàng')
        qty=positive(qty);due=date(due);priority=int(priority)
        if priority not in (1,2,3,4,5): raise ValueError('Ưu tiên 1-5')
        with self.connection() as db:
            db.execute('INSERT INTO orders(id,product,qty,due,priority,customer) VALUES(?,?,?,?,?,?)',(oid.strip(),product.strip(),qty,due,priority,customer.strip()))
            self.event(db,'ORDER',oid)
    def set_bom(self, product, material, per_unit):
        if not product.strip() or not material.strip(): raise ValueError('Thiếu mã thành phẩm/vật tư')
        with self.connection() as db: db.execute('INSERT INTO bom VALUES(?,?,?) ON CONFLICT(product,material) DO UPDATE SET per_unit=excluded.per_unit',(product.strip(),material.strip(),positive(per_unit)))
    def set_stock(self, material, onhand, inbound=0, counted=None):
        if not material.strip(): raise ValueError('Thiếu mã vật tư')
        with self.connection() as db:
            db.execute('INSERT INTO stock(material,onhand,inbound,counted) VALUES(?,?,?,?) ON CONFLICT(material) DO UPDATE SET onhand=excluded.onhand,inbound=excluded.inbound,counted=excluded.counted',(material.strip(),nonnegative(onhand),nonnegative(inbound),None if counted in (None,'') else nonnegative(counted)))
    def center(self, name, units_day, enabled=True):
        if not name.strip(): raise ValueError('Thiếu tên chuyền')
        with self.connection() as db: db.execute('INSERT INTO centers VALUES(?,?,?) ON CONFLICT(name) DO UPDATE SET units_per_day=excluded.units_per_day,enabled=excluded.enabled',(name.strip(),positive(units_day),int(enabled)))
    def orders(self):return self.query('SELECT * FROM orders ORDER BY due, priority DESC, id')
    def demand(self):
        return self.query('''SELECT b.material, SUM((o.qty-o.produced)*b.per_unit) AS required, MIN(o.due) AS need_by
                             FROM orders o JOIN bom b ON o.product=b.product WHERE o.qty>o.produced GROUP BY b.material ORDER BY b.material''')
    def mrp(self):
        supplies={s['material']:s for s in self.query('SELECT * FROM stock')}
        result=[]
        for d in self.demand():
            s=supplies.get(d['material'],{})
            onhand=s.get('onhand',0); inbound=s.get('inbound',0)
            result.append({**d,'onhand':onhand,'inbound':inbound,'shortage':round(max(0,d['required']-onhand-inbound),6)})
        return result
    def shortages(self):return [r for r in self.mrp() if r['shortage']>0]
    def missing_bom(self):
        return self.query('SELECT DISTINCT o.product FROM orders o LEFT JOIN bom b ON b.product=o.product WHERE b.product IS NULL')
    def plan(self, start=None, persist=False):
        start=date(start or today())
        centers=self.query('SELECT * FROM centers WHERE enabled=1 ORDER BY name')
        if not centers: raise ValueError('Chưa khai báo chuyền sản xuất')
        next_free={c['name']:datetime.strptime(start,'%Y-%m-%d').date() for c in centers}
        rows=[]
        for order in self.orders():
            remaining=order['qty']-order['produced']
            if remaining<=0:continue
            options=[]
            for c in centers:
                days=math.ceil(remaining/c['units_per_day'])
                st=next_free[c['name']];end=st+timedelta(days=days-1)
                options.append((end,st,c['name'],days))
            end,st,center,days=min(options)
            next_free[center]=end+timedelta(days=1)
            rows.append({'order_id':order['id'],'center':center,'start':str(st),'finish':str(end),'days':days,'late':str(end)>order['due']})
        if persist:
            with self.connection() as db:
                db.execute('DELETE FROM schedule')
                for r in rows: db.execute('INSERT INTO schedule VALUES(?,?,?,?,?)',(r['order_id'],r['center'],r['start'],r['finish'],r['days']))
                self.event(db,'PLAN','Replanned '+str(len(rows))+' orders')
        return rows
    def work_orders(self, approve=False):
        rows=self.query('SELECT * FROM schedule ORDER BY start,order_id')
        if approve:
            with self.connection() as db:
                for r in rows:
                    oid='WO-'+r['order_id']
                    db.execute('INSERT OR IGNORE INTO jobs(id,order_id,state,qr_payload) VALUES(?,?,?,?)',(oid,r['order_id'],'DRAFT',json.dumps({'work_order':oid,'order':r['order_id']},ensure_ascii=False)))
                self.event(db,'WORK_ORDERS','Generated DRAFT jobs')
        return [{'id':'WO-'+r['order_id'],'order':r['order_id'],'center':r['center'],'start':r['start']} for r in rows]
    def create_pr(self):
        shortage=self.shortages()
        with self.connection() as db:
            for r in shortage:
                # DRAFTs are refreshed, not duplicated on every run.
                db.execute("DELETE FROM requests WHERE material=? AND status='DRAFT'",(r['material'],))
                db.execute('INSERT INTO requests(material,qty,need_by) VALUES(?,?,?)',(r['material'],r['shortage'],r['need_by']))
            self.event(db,'PR',f'{len(shortage)} draft requisitions')
        return shortage
    def issue(self, oid, material, qty):
        qty=positive(qty)
        with self.connection() as db:
            if not db.execute('SELECT 1 FROM orders WHERE id=?',(oid,)).fetchone():raise ValueError('Không có đơn hàng')
            cur=db.execute('UPDATE stock SET onhand=onhand-? WHERE material=? AND onhand>=?',(qty,material,qty))
            if not cur.rowcount:raise ValueError('Không đủ tồn kho hoặc không có mã vật tư')
            db.execute('INSERT INTO movements(order_id,material,qty,created) VALUES(?,?,?,?)',(oid,material,qty,today()))
            self.event(db,'ISSUE',f'{oid} {material} {qty}')
    def produce(self, oid, good_qty):
        good_qty=positive(good_qty)
        with self.connection() as db:
            cur=db.execute('UPDATE orders SET produced=produced+? WHERE id=? AND produced+?<=qty',(good_qty,oid,good_qty))
            if not cur.rowcount:raise ValueError('Sản lượng vượt kế hoạch hoặc mã đơn không hợp lệ')
            self.event(db,'PRODUCE',f'{oid} {good_qty}')
    def scrap(self, oid, material, actual_qty, good_qty):
        actual_qty=nonnegative(actual_qty);good_qty=nonnegative(good_qty)
        if not self.query('SELECT id FROM orders WHERE id=?',(oid,)):raise ValueError('Mã đơn không hợp lệ')
        with self.connection() as db:db.execute('INSERT INTO scrap(order_id,material,actual_qty,good_qty,created) VALUES(?,?,?,?,?)',(oid,material,actual_qty,good_qty,today()))
    def scrap_report(self):
        rows=self.query('''SELECT s.order_id,s.material,s.actual_qty,s.good_qty,b.per_unit,
                  ROUND(s.actual_qty-s.good_qty*b.per_unit,4) AS variance
                  FROM scrap s JOIN orders o ON o.id=s.order_id JOIN bom b ON b.product=o.product AND b.material=s.material ORDER BY s.id DESC''')
        for r in rows:r['loss_percent']=round(max(0,r['variance'])/(r['good_qty']*r['per_unit'])*100,2) if r['good_qty'] else None
        return rows
    def reconcile(self):return self.query('SELECT material,onhand,counted,ROUND(counted-onhand,5) AS difference FROM stock WHERE counted IS NOT NULL AND ABS(counted-onhand)>0.000001')
    def dashboard(self):
        rows=self.query('SELECT COUNT(*) AS total,COALESCE(SUM(qty),0) AS planned,COALESCE(SUM(produced),0) AS produced FROM orders')
        r=rows[0];r['completion_pct']=round(100*r['produced']/r['planned'],2) if r['planned'] else 0
        r['shortage_items']=len(self.shortages());r['inventory_mismatches']=len(self.reconcile())
        r['late_orders']=sum(1 for p in self.plan() if p['late']) if self.query('SELECT 1 FROM centers LIMIT 1') else None
        return r
    def report_csv(self, target, section='mrp'):
        data={'orders':self.orders,'mrp':self.mrp,'shortages':self.shortages,'reconcile':self.reconcile,'scrap':self.scrap_report,'schedule':lambda:self.query('SELECT * FROM schedule')}.get(section)
        if data is None:raise ValueError('Không hỗ trợ báo cáo này')
        rows=data()
        # Exclusive creation avoids silently destroying a previous report.
        with open(target,'x',newline='',encoding='utf-8-sig') as f:
            if rows:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
                for row in rows:
                    w.writerow({k: csv_safe(v) for k,v in row.items()})
        return len(rows)
    def import_csv(self, filepath, table):
        methods={'orders':lambda r:self.order(r['id'],r['product'],r['qty'],r['due'],r.get('priority',1),r.get('customer','')),
                 'bom':lambda r:self.set_bom(r['product'],r['material'],r['per_unit']),
                 'stock':lambda r:self.set_stock(r['material'],r['onhand'],r.get('inbound',0),r.get('counted')),
                 'centers':lambda r:self.center(r['name'],r['units_per_day'])}
        if table not in methods:raise ValueError('Loại dữ liệu không hợp lệ')
        # Validate required CSV fields before applying records. Valid rows are imported sequentially.
        with open(filepath,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
        if len(rows)>100000:raise ValueError('CSV quá lớn')
        for r in rows:
            for key in {'orders':['id','product','qty','due'],'bom':['product','material','per_unit'],'stock':['material','onhand'],'centers':['name','units_per_day']}[table]:
                if not r.get(key):raise ValueError('Thiếu cột hoặc dữ liệu: '+key)
        # Validate every record before any mutation (including duplicates within file).
        existing = set()
        keys = {'orders':'id','bom':None,'stock':'material','centers':'name'}
        for row in rows:
            if table == 'orders':
                positive(row['qty']); date(row['due'])
                priority = int(row.get('priority') or 1)
                if priority not in range(1, 6): raise ValueError('Ưu tiên 1-5')
            elif table == 'bom': positive(row['per_unit'])
            elif table == 'stock':
                nonnegative(row['onhand']); nonnegative(row.get('inbound') or 0)
                if row.get('counted') not in (None, ''): nonnegative(row['counted'])
            elif table == 'centers': positive(row['units_per_day'])
            key = (row.get('product'), row.get('material')) if table == 'bom' else row.get(keys[table])
            if key in existing:
                raise ValueError('Mã trùng trong file CSV: ' + str(key))
            existing.add(key)
        # Existing per-record transaction behavior remains; invalid content never starts an import.
        for row in rows: methods[table](row)
        return len(rows)
