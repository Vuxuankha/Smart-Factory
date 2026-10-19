"""Additional PMC decision support. Local-only; no machine, supplier, or ERP writes."""
import json
import math
from datetime import date, datetime
from pmc_manager import PMC, positive, nonnegative

EXTRA_SCHEMA = '''
CREATE TABLE IF NOT EXISTS pmc_lots (id TEXT PRIMARY KEY,material TEXT NOT NULL,qty REAL NOT NULL CHECK(qty>=0),received TEXT NOT NULL,expires TEXT,location TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS pmc_maintenance (id INTEGER PRIMARY KEY AUTOINCREMENT, center TEXT NOT NULL, start TEXT NOT NULL, finish TEXT NOT NULL, reason TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pmc_subcontract (id TEXT PRIMARY KEY, order_id TEXT NOT NULL, vendor TEXT NOT NULL, quantity REAL NOT NULL, due TEXT NOT NULL, received REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS pmc_po (id TEXT PRIMARY KEY,material TEXT NOT NULL,qty REAL NOT NULL,unit_price REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS pmc_receipts (id TEXT PRIMARY KEY,po_id TEXT NOT NULL,qty REAL NOT NULL);
CREATE TABLE IF NOT EXISTS pmc_invoices (id TEXT PRIMARY KEY,po_id TEXT NOT NULL,qty REAL NOT NULL,unit_price REAL NOT NULL);
CREATE TABLE IF NOT EXISTS pmc_delay (id INTEGER PRIMARY KEY AUTOINCREMENT,order_id TEXT NOT NULL,cause TEXT NOT NULL,note TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pmc_eco (id INTEGER PRIMARY KEY AUTOINCREMENT,product TEXT NOT NULL,old_revision TEXT NOT NULL,new_revision TEXT NOT NULL,note TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pmc_audit (id INTEGER PRIMARY KEY AUTOINCREMENT,actor TEXT NOT NULL,action TEXT NOT NULL,details TEXT NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pmc_kits (order_id TEXT NOT NULL, material TEXT NOT NULL, allocated REAL NOT NULL CHECK(allocated>=0),PRIMARY KEY(order_id,material));
'''

def valid_date(value): return date.fromisoformat(str(value)).isoformat()

class PMCAdvanced:
    def __init__(self, dbfile):
        self.core=PMC(dbfile)
        with self.core.connection() as db: db.executescript(EXTRA_SCHEMA)
    def audit(self, db, action, details, actor='local_user'):
        db.execute('INSERT INTO pmc_audit(actor,action,details,created) VALUES(?,?,?,?)',
                   (str(actor)[:100],action,json.dumps(details,ensure_ascii=False),datetime.now().isoformat(timespec='seconds')))
    def lot(self, lot_id, material, qty, received, expires='', location=''):
        if not lot_id.strip() or not material.strip(): raise ValueError('Thiếu mã lô/vật tư')
        received=valid_date(received); expires=valid_date(expires) if expires else None
        if expires and expires<received:raise ValueError('Hạn dùng trước ngày nhập')
        with self.core.connection() as db:
            db.execute('INSERT INTO pmc_lots VALUES(?,?,?,?,?,?)',(lot_id.strip(),material.strip(),nonnegative(qty),received,expires,location.strip()))
            self.audit(db,'LOT_CREATED',{'lot':lot_id,'material':material})
    def picking_suggestion(self, material, qty):
        remaining=positive(qty)
        rows=self.core.query('SELECT * FROM pmc_lots WHERE material=? AND qty>0 ORDER BY CASE WHEN expires IS NULL THEN 1 ELSE 0 END,expires,received,id',(material,))
        picks=[]
        for r in rows:
            if r['expires'] and r['expires']<date.today().isoformat():continue
            take=min(remaining,r['qty'])
            if take>0:picks.append({'lot':r['id'],'qty':take,'expires':r['expires']})
            remaining-=take
            if remaining<=1e-9:break
        return {'picks':picks,'unfilled':round(remaining,6),'preview_only':True}
    def expiring(self, days=30):
        days=int(days)
        if days<0 or days>3650:raise ValueError('Ngày cảnh báo không hợp lệ')
        from datetime import timedelta
        end=(date.today()+timedelta(days=days)).isoformat()
        return self.core.query('SELECT * FROM pmc_lots WHERE expires IS NOT NULL AND expires<=? AND qty>0 ORDER BY expires',(end,))
    def safety_stock(self, avg_daily, lead_days, demand_std=0, service_factor=1.65):
        avg_daily=nonnegative(avg_daily);lead_days=nonnegative(lead_days);demand_std=nonnegative(demand_std);service_factor=nonnegative(service_factor)
        safety=service_factor*demand_std*math.sqrt(lead_days)
        return {'safety_stock':round(safety,3),'reorder_point':round(avg_daily*lead_days+safety,3),'model':'constant lead time; demand standard deviation supplied manually'}
    def maintenance(self,center,start,finish,reason):
        start=valid_date(start);finish=valid_date(finish)
        if finish<start or not center.strip(): raise ValueError('Lịch bảo trì không hợp lệ')
        with self.core.connection() as db:
            db.execute('INSERT INTO pmc_maintenance(center,start,finish,reason) VALUES(?,?,?,?)',(center,start,finish,reason))
            self.audit(db,'MAINTENANCE_ADDED',{'center':center,'start':start,'finish':finish})
    def maintenance_conflicts(self):
        return self.core.query('''SELECT s.order_id,s.center,s.start,s.finish,m.start maintenance_start,m.finish maintenance_finish
            FROM schedule s JOIN pmc_maintenance m ON s.center=m.center AND s.start<=m.finish AND m.start<=s.finish ORDER BY s.start''')
    def allocate_kit(self,order_id,material,qty):
        qty=nonnegative(qty)
        with self.core.connection() as db:
            row=db.execute('SELECT qty,produced,product FROM orders WHERE id=?',(order_id,)).fetchone()
            if not row:raise ValueError('Đơn hàng không tồn tại')
            bom=db.execute('SELECT per_unit FROM bom WHERE product=? AND material=?',(row['product'],material)).fetchone()
            if not bom:raise ValueError('Vật tư không thuộc BOM của đơn hàng')
            if qty>(row['qty']-row['produced'])*bom['per_unit']+1e-9:raise ValueError('Vượt định mức còn lại của đơn')
            db.execute('INSERT INTO pmc_kits VALUES(?,?,?) ON CONFLICT(order_id,material) DO UPDATE SET allocated=excluded.allocated',(order_id,material,qty))
            self.audit(db,'KIT_ALLOCATED',{'order_id':order_id,'material':material,'qty':qty})
    def subcontract(self,id,order_id,vendor,quantity,due):
        if not id.strip() or not vendor.strip(): raise ValueError('Thiếu nhà thầu/mã')
        if not self.core.query('SELECT id FROM orders WHERE id=?',(order_id,)):raise ValueError('Đơn không tồn tại')
        with self.core.connection() as db:
            db.execute('INSERT INTO pmc_subcontract(id,order_id,vendor,quantity,due) VALUES(?,?,?,?,?)',(id,order_id,vendor,positive(quantity),valid_date(due)))
            self.audit(db,'SUBCONTRACT_ADDED',{'id':id,'order_id':order_id})
    def late_subcontracts(self):
        return self.core.query('SELECT * FROM pmc_subcontract WHERE due<? AND received<quantity ORDER BY due',(date.today().isoformat(),))
    def record_po(self,id,material,qty,unit_price):
        if not id.strip() or not material.strip():raise ValueError('Thiếu mã PO/vật tư')
        with self.core.connection() as db:
            db.execute('INSERT INTO pmc_po VALUES(?,?,?,?)',(id,material,positive(qty),nonnegative(unit_price)))
            self.audit(db,'PO_RECORDED',{'id':id})
    def record_receipt(self,id,po_id,qty):
        self._linked('pmc_receipts',id,po_id,qty)
    def record_invoice(self,id,po_id,qty,unit_price):
        self._linked('pmc_invoices',id,po_id,qty,unit_price)
    def _linked(self,table,id,po_id,qty,unit_price=None):
        if not id.strip():raise ValueError('Thiếu mã chứng từ')
        with self.core.connection() as db:
            if not db.execute('SELECT 1 FROM pmc_po WHERE id=?',(po_id,)).fetchone():raise ValueError('PO không tồn tại')
            vals=(id,po_id,positive(qty)) if unit_price is None else (id,po_id,positive(qty),nonnegative(unit_price))
            db.execute('INSERT INTO '+table+' VALUES('+','.join('?' for _ in vals)+')',vals)
            self.audit(db,table.upper(),{'id':id,'po_id':po_id})
    def matching(self):
        return self.core.query('''SELECT p.id,p.material,p.qty po_qty,p.unit_price po_price,
          COALESCE(r.qty,0) received_qty,COALESCE(i.qty,0) invoiced_qty,
          COALESCE(i.amount,0) invoice_amount,
          CASE WHEN COALESCE(r.qty,0)>p.qty+0.000001 OR COALESCE(i.qty,0)>COALESCE(r.qty,0)+0.000001 OR ABS(COALESCE(i.amount,0)-COALESCE(i.qty,0)*p.unit_price)>0.01 THEN 'MISMATCH' ELSE 'REVIEW' END status
          FROM pmc_po p
          LEFT JOIN (SELECT po_id,SUM(qty) qty FROM pmc_receipts GROUP BY po_id) r ON r.po_id=p.id
          LEFT JOIN (SELECT po_id,SUM(qty) qty,SUM(qty*unit_price) amount FROM pmc_invoices GROUP BY po_id) i ON i.po_id=p.id''')
    def delay(self,order_id,cause,note=''):
        if cause not in ('MATERIAL','MACHINE','QUALITY','STAFF','OTHER'):raise ValueError('Nguyên nhân không hợp lệ')
        if not self.core.query('SELECT id FROM orders WHERE id=?',(order_id,)):raise ValueError('Đơn không tồn tại')
        with self.core.connection() as db:
            db.execute('INSERT INTO pmc_delay(order_id,cause,note,created) VALUES(?,?,?,?)',(order_id,cause,note,datetime.now().isoformat(timespec='seconds')))
            self.audit(db,'DELAY_LOGGED',{'order_id':order_id,'cause':cause})
    def delay_summary(self):return self.core.query('SELECT cause,COUNT(*) incidents FROM pmc_delay GROUP BY cause ORDER BY incidents DESC')
    def eco(self,product,old_revision,new_revision,note=''):
        if not all([product.strip(),old_revision.strip(),new_revision.strip()]) or old_revision==new_revision:raise ValueError('Phiên bản ECO không hợp lệ')
        affected=self.core.query('SELECT id,qty,produced FROM orders WHERE product=? AND produced<qty',(product,))
        with self.core.connection() as db:
            db.execute('INSERT INTO pmc_eco(product,old_revision,new_revision,note,created) VALUES(?,?,?,?,?)',(product,old_revision,new_revision,note,datetime.now().isoformat(timespec='seconds')))
            self.audit(db,'ECO_REVIEW',{'product':product,'affected':[r['id'] for r in affected]})
        return {'affected_orders':affected,'manual_approval_required':True,'note':'Không khóa lệnh hoặc đổi BOM tự động'}
    def audit_log(self,limit=100):
        return self.core.query('SELECT * FROM pmc_audit ORDER BY id DESC LIMIT ?', (min(max(1,int(limit)),1000),))
