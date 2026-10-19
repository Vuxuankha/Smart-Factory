"""Opt-in synthetic fixture for tests/previews. Not loaded by application startup.
Call seed_demo only in a separate test database after administrator login.
"""
from datetime import datetime, timezone

def seed_demo(service,plant='DEMO-N01'):
    service.add_plant(plant,'DEMO - Nha may thu nghiem (khong phai so lieu that)',capacity='600')
    def save(kind,code,**data):return service.save(plant,kind,code,data)
    def update(kind,code,**changes):
        from factory_schema import ENTITIES
        row=next(r for r in service.list_records(plant,kind,limit=500)['rows'] if r['code']==code)
        data={f.key:row[f.key] for f in ENTITIES[kind]['fields']};data.update(changes)
        return service.save(plant,kind,code,data,row['_rev'])
    save('suppliers','SUP-001',name='DEMO Supplier A',risk='LOW')
    save('suppliers','SUP-002',name='DEMO Subcontract B',risk='HIGH')
    save('shipments','SHIP-01',supplier='SUP-002',reference='DEMO-PO-2026',due='2026-10-01',status='IN_TRANSIT')
    save('assets','RTR-01',name='DEMO Router',type='ROUTER',state='UNKNOWN',ip='192.0.2.1',location='DEMO IT')
    save('assets','SW-01',name='DEMO Core Switch',type='SWITCH',state='UNKNOWN',parent='RTR-01',ip='192.0.2.2',location='DEMO IT')
    save('assets','CAM-01',name='DEMO Camera',type='CAMERA',state='UNKNOWN',parent='SW-01',ip='192.0.2.10',location='DEMO WH')
    save('assets','NAS-01',name='DEMO NAS',type='NAS',state='UNKNOWN',parent='SW-01',ip='192.0.2.20',location='DEMO IT')
    save('assets','PRESS-01',name='DEMO Press Line A',type='MACHINE',state='RUN',parent='SW-01',capacity='120',skill='PRESS',location='DEMO Line A')
    save('assets','CNC-02',name='DEMO CNC Line B',type='MACHINE',state='IDLE',parent='SW-01',capacity='80',location='DEMO Line B')
    save('sensors','TEMP-01',asset='PRESS-01',unit='degC',low='15',high='70')
    save('readings','READ-001',sensor='TEMP-01',value='76',at=datetime.now(timezone.utc).isoformat())
    for code,name,kind,unit,safety in [('FG-100','DEMO Assembly A','MAKE','pcs','0'),('SUB-10','DEMO Subassembly','MAKE','pcs','0'),('RM-STEEL','DEMO Steel blanks','BUY','pcs','100'),('RM-BOLT','DEMO Bolts M6','BUY','pcs','200'),('RM-SEAL','DEMO Sealing ring','BUY','pcs','50')]:
        save('materials',code,name=name,type=kind,unit=unit,safety=safety)
    for code,parent,component,per in [('B-01','FG-100','SUB-10','1'),('B-02','SUB-10','RM-STEEL','2'),('B-03','FG-100','RM-BOLT','4')]:save('bom',code,parent=parent,component=component,per=per)
    lots=[('LOT-ST-01','RM-STEEL','500','2099-12-31','RELEASED'),('LOT-ST-02','RM-STEEL','100','2098-12-31','HOLD'),('LOT-BT-01','RM-BOLT','500','2099-12-31','RELEASED'),('LOT-SL-01','RM-SEAL','20','2099-12-31','RELEASED'),('LOT-SL-OLD','RM-SEAL','80','2020-12-31','BLOCKED')]
    for code,material,qty,expiry,quality in lots:save('lots',code,material=material,quantity=qty,received='2020-01-01',expiry=expiry,quality=quality,location='DEMO WH-A')
    save('inbound','PO-IN-01',material='RM-SEAL',quantity='60',eta='2099-01-01')
    for i,qty in [(1,'50'),(2,'120'),(3,'80')]:save('orders',f'MO-00{i}',product='FG-100',quantity=qty,due='2099-01-01',priority=str(i))
    update('orders','MO-001',state='RELEASED')
    service.issue(plant,'DEMO-ISS-01','MO-001','RM-STEEL','100')
    service.issue(plant,'DEMO-ISS-02','MO-001','RM-BOLT','200')
    save('staff','OP-01',name='DEMO Operator A',team='DEMO Press')
    save('staff','OP-02',name='DEMO Operator B',team='DEMO Press')
    save('skills','CERT-01',staff='OP-01',skill='PRESS',valid_from='2020-01-01',valid_to='2099-12-31',certificate='DEMO-CERT-NOT-REAL')
    save('shifts','SHIFT-01',staff='OP-01',asset='PRESS-01',start='2098-10-19T08:00+07:00',end='2098-10-19T16:00+07:00')
    save('handovers','HAND-01',asset='PRESS-01',at='2026-10-19T16:00+07:00',outgoing='OP-01',incoming='OP-02',notes='DEMO - check tooling before next shift')
    service.output(plant,'DEMO-OUT-01','MO-001','25','2','FG-LOT-001','OP-01')
    save('oee','OEE-SHIFT-01',asset='PRESS-01',date='2026-10-19',planned_min='480',run_min='420',cycle_sec='30',total='800',good='760')
    save('oee','OEE-SHIFT-02',asset='CNC-02',date='2026-10-19',planned_min='480',run_min='400',cycle_sec='45',total='480',good='470')
    save('maintenance','PM-001',asset='PRESS-01',start='2098-10-20T08:00+07:00',end='2098-10-20T10:00+07:00',reason='DEMO preventive maintenance')
    save('inspections','IQC-01',stage='IQC',lot='LOT-ST-01',sampled='20',rejected='0',date='2026-10-19')
    save('inspections','OQC-01',stage='OQC',lot='FG-LOT-001',sampled='10',rejected='1',reason='DEMO scratch',date='2026-10-19')
    save('capa','CAPA-001',title='DEMO surface scratch',owner='DEMO QA',due='2099-01-01')
    save('calibrations','CAL-001',asset='PRESS-01',calibrated='2026-01-01',due='2026-10-01',certificate='DEMO-ONLY',result='PASS')
    save('sops','SOP-01',title='DEMO Incoming inspection',revision='A',reference='DEMO reference only',effective='2026-01-01',owner='DEMO QA')
    save('counts','COUNT-01',lot='LOT-ST-01',counted='395',at=datetime.now(timezone.utc).isoformat())
    save('docks','DOCK-01',dock='DEMO-D1',vehicle='DEMO-TRUCK',start='2098-10-20T08:00+07:00',end='2098-10-20T09:00+07:00')
    save('training','TRAIN-01',staff='OP-01',course='DEMO PPE briefing',date='2026-10-19',result='PASS')
    save('ppe','PPE-01',staff='OP-01',item='DEMO safety gloves',quantity='2',date='2026-10-19')
    save('licenses','LIC-01',asset='NAS-01',software='DEMO asset register',seats='1',expires='2099-01-01',reference='DEMO-NO-KEY')
    save('energy','METER-01',asset='PRESS-01',start='2026-10-19T08:00+07:00',end='2026-10-19T12:00+07:00',kwh='88.5',tariff='2000',state='RUN')
    return plant
