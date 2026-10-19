"""Declarative input contracts for the local Smart Factory workspace.
No arbitrary table names or field names from a form reach SQL.
Quantities are Decimal strings to avoid inventory floating-point drift.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Field:
    key: str
    label: str
    type: str = 'text'
    default: str = ''
    required: bool = True
    choices: tuple = ()
    ref: str = ''

def F(key, label, kind='text', default='', required=True, choices=(), ref=''):
    return Field(key,label,kind,default,required,tuple(choices),ref)

def E(label, group, fields, immutable=False, admin=False):
    return {'label':label,'group':group,'fields':tuple(fields),'immutable':immutable,'admin':admin}

ENTITIES = {
'suppliers':E('Nh\u00e0 cung c\u1ea5p / gia c\u00f4ng',1,[F('name','T\u00ean'),F('risk','M\u1ee9c r\u1ee7i ro','choice','LOW',choices=('LOW','MEDIUM','HIGH')),F('contact','Li\u00ean h\u1ec7',required=False),F('notes','Ghi ch\u00fa',required=False)]),
'shipments':E('Theo d\u00f5i giao h\u00e0ng',1,[F('supplier','Nh\u00e0 cung c\u1ea5p',ref='suppliers'),F('reference','M\u00e3 \u0111\u01a1n / v\u1eadn \u0111\u01a1n'),F('due','H\u1ea1n giao','date'),F('status','Tr\u1ea1ng th\u00e1i','choice','PLANNED',choices=('PLANNED','IN_TRANSIT','DELIVERED','CANCELLED')),F('notes','M\u1ed1c giao nh\u1eadn',required=False)]),
'assets':E('T\u00e0i s\u1ea3n / m\u00e1y / thi\u1ebft b\u1ecb',7,[F('name','T\u00ean thi\u1ebft b\u1ecb'),F('type','Lo\u1ea1i','choice','MACHINE',choices=('MACHINE','TOOL','SERVER','SWITCH','ROUTER','CAMERA','NAS','SENSOR','OTHER')),F('location','Khu v\u1ef1c',required=False),F('state','Tr\u1ea1ng th\u00e1i khai b\u00e1o','choice','UNKNOWN',choices=('UNKNOWN','RUN','IDLE','STOP','MAINTENANCE')),F('ip','IP (t\u00f9y ch\u1ecdn)','ip',required=False),F('parent','Thi\u1ebft b\u1ecb cha',required=False,ref='assets'),F('capacity','S\u1ea3n ph\u1ea9m / gi\u1edd','decimal','0'),F('skill','K\u1ef9 n\u0103ng b\u1eaft bu\u1ed9c',required=False),F('maintenance_due','H\u1ea1n b\u1ea3o tr\u00ec','date',required=False)]),
'sensors':E('C\u1ea3m bi\u1ebfn & ng\u01b0\u1ee1ng',2,[F('asset','Thi\u1ebft b\u1ecb',ref='assets'),F('unit','\u0110\u01a1n v\u1ecb'),F('low','Ng\u01b0\u1ee1ng d\u01b0\u1edbi','signed','0'),F('high','Ng\u01b0\u1ee1ng tr\u00ean','signed','100'),F('stale_minutes','Qu\u00e1 h\u1ea1n sau (ph\u00fat)','positive','60')]),
'readings':E('M\u1eabu \u0111o c\u1ea3m bi\u1ebfn',2,[F('sensor','C\u1ea3m bi\u1ebfn',ref='sensors'),F('value','Gi\u00e1 tr\u1ecb \u0111o','signed'),F('at','Th\u1eddi gian ISO + m\u00fai gi\u1edd','datetime')],immutable=True),
'materials':E('Danh m\u1ee5c v\u1eadt t\u01b0 / s\u1ea3n ph\u1ea9m',3,[F('name','T\u00ean v\u1eadt t\u01b0'),F('unit','\u0110\u01a1n v\u1ecb','text','pcs'),F('type','Ngu\u1ed3n cung','choice','BUY',choices=('BUY','MAKE')),F('safety','T\u1ed3n an to\u00e0n','decimal','0')]),
'lots':E('L\u00f4 h\u00e0ng / FIFO / FEFO',3,[F('material','V\u1eadt t\u01b0',ref='materials'),F('quantity','S\u1ed1 l\u01b0\u1ee3ng nh\u1eadp','decimal'),F('received','Ng\u00e0y nh\u1eadp','date'),F('expiry','H\u1ea1n d\u00f9ng','date',required=False),F('quality','Tr\u1ea1ng th\u00e1i ch\u1ea5t l\u01b0\u1ee3ng','choice','HOLD',choices=('HOLD','RELEASED','BLOCKED')),F('location','V\u1ecb tr\u00ed kho',default='MAIN'),F('owner','Ch\u1ee7 h\u00e0ng k\u00fd g\u1eedi',required=False)],immutable=True),
'inbound':E('H\u00e0ng \u0111ang v\u1ec1 (k\u1ebf ho\u1ea1ch)',3,[F('material','V\u1eadt t\u01b0',ref='materials'),F('quantity','S\u1ed1 l\u01b0\u1ee3ng','positive'),F('eta','D\u1ef1 ki\u1ebfn \u0111\u1ebfn','date'),F('status','Tr\u1ea1ng th\u00e1i','choice','OPEN',choices=('OPEN','RECEIVED','CANCELLED'))]),
'counts':E('Phi\u1ebfu ki\u1ec3m k\u00ea',3,[F('lot','M\u00e3 l\u00f4',ref='lots'),F('counted','S\u1ed1 l\u01b0\u1ee3ng \u0111\u1ebfm','decimal'),F('at','Th\u1eddi \u0111i\u1ec3m \u0111\u1ebfm','datetime')],immutable=True),
'docks':E('L\u1ecbch c\u1eeda kho / b\u1ebfn b\u00e3i',3,[F('dock','C\u1eeda / b\u1ebfn'),F('vehicle','Bi\u1ec3n s\u1ed1 / xe'),F('start','B\u1eaft \u0111\u1ea7u (ISO + m\u00fai gi\u1edd)','datetime'),F('end','K\u1ebft th\u00fac','datetime')]),
'bom':E('BOM \u0111a c\u1ea5p',4,[F('parent','M\u00e3 cha (MAKE)',ref='materials'),F('component','Linh ki\u1ec7n',ref='materials'),F('per','\u0110\u1ecbnh m\u1ee9c / 1 s\u1ea3n ph\u1ea9m','positive')]),
'orders':E('L\u1ec7nh s\u1ea3n xu\u1ea5t \u0111i\u1ec7n t\u1eed',4,[F('product','Th\u00e0nh ph\u1ea9m',ref='materials'),F('quantity','S\u1ed1 l\u01b0\u1ee3ng','positive'),F('due','H\u1ea1n giao','date'),F('priority','\u01afu ti\u00ean (5 cao nh\u1ea5t)','choice','1',choices=('1','2','3','4','5')),F('state','Tr\u1ea1ng th\u00e1i','choice','DRAFT',choices=('DRAFT','RELEASED','HOLD','CLOSED','CANCELLED'))]),
'maintenance':E('L\u1ecbch b\u1ea3o tr\u00ec',4,[F('asset','Thi\u1ebft b\u1ecb',ref='assets'),F('start','B\u1eaft \u0111\u1ea7u (ISO + m\u00fai gi\u1edd)','datetime'),F('end','K\u1ebft th\u00fac','datetime'),F('reason','N\u1ed9i dung')]),
'oee':E('Nh\u1eadt k\u00fd ca / OEE',4,[F('asset','M\u00e1y',ref='assets'),F('date','Ng\u00e0y','date'),F('planned_min','Th\u1eddi gian k\u1ebf ho\u1ea1ch (ph\u00fat)','positive','480'),F('run_min','Th\u1eddi gian ch\u1ea1y (ph\u00fat)','decimal'),F('cycle_sec','Chu k\u1ef3 l\u00fd t\u01b0\u1edfng (gi\u00e2y)','positive'),F('total','T\u1ed5ng s\u1ea3n l\u01b0\u1ee3ng','integer'),F('good','S\u1ea3n l\u01b0\u1ee3ng \u0111\u1ea1t','integer')],immutable=True),
'incidents':E('S\u1ef1 c\u1ed1 & theo d\u00f5i x\u1eed l\u00fd',6,[F('title','S\u1ef1 c\u1ed1'),F('severity','M\u1ee9c \u0111\u1ed9','choice','WARNING',choices=('INFO','WARNING','CRITICAL')),F('state','Tr\u1ea1ng th\u00e1i','choice','OPEN',choices=('OPEN','ACKNOWLEDGED','RESOLVED')),F('owner','Ng\u01b0\u1eddi x\u1eed l\u00fd',required=False),F('notes','Nguy\u00ean nh\u00e2n / bi\u1ec7n ph\u00e1p',required=False)]),
'licenses':E('B\u1ea3n quy\u1ec1n ph\u1ea7n m\u1ec1m',7,[F('asset','M\u00e1y / thi\u1ebft b\u1ecb',ref='assets'),F('software','Ph\u1ea7n m\u1ec1m'),F('seats','S\u1ed1 l\u01b0\u1ee3ng','integer','1'),F('expires','H\u1ea1n b\u1ea3n quy\u1ec1n','date',required=False),F('reference','M\u00e3 h\u1ee3p \u0111\u1ed3ng (kh\u00f4ng l\u01b0u license key)',required=False)],admin=True),
'inspections':E('Ki\u1ec3m tra IQC / PQC / OQC',8,[F('stage','C\u00f4ng \u0111o\u1ea1n','choice','IQC',choices=('IQC','PQC','OQC')),F('lot','L\u00f4 ki\u1ec3m tra',ref='lots'),F('sampled','S\u1ed1 l\u01b0\u1ee3ng ki\u1ec3m','positive'),F('rejected','S\u1ed1 l\u01b0\u1ee3ng l\u1ed7i','decimal','0'),F('reason','Lo\u1ea1i l\u1ed7i / nguy\u00ean nh\u00e2n',required=False),F('date','Ng\u00e0y ki\u1ec3m','date')],immutable=True),
'capa':E('CAPA - kh\u1eafc ph\u1ee5c / ph\u00f2ng ng\u1eeba',8,[F('title','V\u1ea5n \u0111\u1ec1'),F('owner','Ng\u01b0\u1eddi ph\u1ee5 tr\u00e1ch'),F('due','H\u1ea1n x\u1eed l\u00fd','date'),F('state','Tr\u1ea1ng th\u00e1i','choice','OPEN',choices=('OPEN','IN_PROGRESS','VERIFY','CLOSED')),F('cause','Nguy\u00ean nh\u00e2n g\u1ed1c',required=False),F('action','H\u00e0nh \u0111\u1ed9ng',required=False),F('verification','B\u1eb1ng ch\u1ee9ng x\u00e1c minh',required=False)]),
'calibrations':E('Ki\u1ec3m \u0111\u1ecbnh / hi\u1ec7u chu\u1ea9n',8,[F('asset','Thi\u1ebft b\u1ecb',ref='assets'),F('calibrated','Ng\u00e0y hi\u1ec7u chu\u1ea9n','date'),F('due','H\u1ea1n hi\u1ec7u chu\u1ea9n','date'),F('certificate','M\u00e3 ch\u1ee9ng th\u01b0'),F('result','K\u1ebft qu\u1ea3','choice','PASS',choices=('PASS','FAIL'))],immutable=True),
'sops':E('SOP / t\u00e0i li\u1ec7u k\u1ef9 thu\u1eadt',8,[F('title','Ti\u00eau \u0111\u1ec1'),F('revision','Phi\u00ean b\u1ea3n'),F('reference','Tham chi\u1ebfu t\u00e0i li\u1ec7u'),F('effective','Ng\u00e0y hi\u1ec7u l\u1ef1c','date'),F('owner','Ng\u01b0\u1eddi ki\u1ec3m so\u00e1t')]),
'staff':E('H\u1ed3 s\u01a1 nh\u00e2n s\u1ef1 t\u1ed1i thi\u1ec3u',9,[F('name','H\u1ecd t\u00ean'),F('team','T\u1ed5 / b\u1ed9 ph\u1eadn'),F('active','\u0110ang l\u00e0m vi\u1ec7c','choice','YES',choices=('YES','NO'))],admin=True),
'skills':E('Ma tr\u1eadn k\u1ef9 n\u0103ng & ch\u1ee9ng ch\u1ec9',9,[F('staff','Nh\u00e2n s\u1ef1',ref='staff'),F('skill','M\u00e3 k\u1ef9 n\u0103ng'),F('valid_from','C\u00f3 hi\u1ec7u l\u1ef1c t\u1eeb','date'),F('valid_to','H\u1ebft h\u1ea1n','date'),F('certificate','M\u00e3 ch\u1ee9ng ch\u1ec9')],admin=True),
'shifts':E('Ph\u00e2n ca & ki\u1ec3m tra k\u1ef9 n\u0103ng',9,[F('staff','Nh\u00e2n s\u1ef1',ref='staff'),F('asset','M\u00e1y',ref='assets'),F('start','B\u1eaft \u0111\u1ea7u (ISO + m\u00fai gi\u1edd)','datetime'),F('end','K\u1ebft th\u00fac','datetime')],admin=True),
'handovers':E('Nh\u1eadt k\u00fd b\u00e0n giao ca',9,[F('asset','M\u00e1y',ref='assets'),F('at','Th\u1eddi \u0111i\u1ec3m b\u00e0n giao','datetime'),F('outgoing','Ng\u01b0\u1eddi b\u00e0n giao',ref='staff'),F('incoming','Ng\u01b0\u1eddi nh\u1eadn',ref='staff'),F('notes','N\u1ed9i dung b\u00e0n giao')],immutable=True),
'TRAINING_PLACEHOLDER':None,
'ppe':E('C\u1ea5p ph\u00e1t b\u1ea3o h\u1ed9 lao \u0111\u1ed9ng',9,[F('staff','Nh\u00e2n s\u1ef1',ref='staff'),F('item','V\u1eadt d\u1ee5ng'),F('quantity','S\u1ed1 l\u01b0\u1ee3ng','positive'),F('date','Ng\u00e0y c\u1ea5p','date')],immutable=True),
'energy':E('N\u0103ng l\u01b0\u1ee3ng & \u01b0\u1edbc t\u00ednh CO2e',10,[F('asset','M\u00e1y / c\u00f4ng t\u01a1',ref='assets'),F('start','\u0110\u1ea7u k\u1ef3 (ISO + m\u00fai gi\u1edd)','datetime'),F('end','Cu\u1ed1i k\u1ef3','datetime'),F('kwh','\u0110i\u1ec7n TI\u00caU TH\u1ee4 trong k\u1ef3 (kWh)','decimal'),F('state','Tr\u1ea1ng th\u00e1i','choice','RUN',choices=('RUN','IDLE')),F('tariff','\u0110\u01a1n gi\u00e1 / kWh','decimal','0'),F('factor','H\u1ec7 s\u1ed1 kgCO2e/kWh','decimal',required=False),F('factor_source','Ngu\u1ed3n h\u1ec7 s\u1ed1',required=False),F('factor_date','Ng\u00e0y hi\u1ec7u l\u1ef1c h\u1ec7 s\u1ed1','date',required=False)],immutable=True,admin=True),
}
ENTITIES.pop('TRAINING_PLACEHOLDER')
ENTITIES['training']=E('\u0110\u00e0o t\u1ea1o & \u0111\u00e1nh gi\u00e1',9,[F('staff','Nh\u00e2n s\u1ef1',ref='staff'),F('course','Kh\u00f3a \u0111\u00e0o t\u1ea1o'),F('date','Ng\u00e0y','date'),F('result','K\u1ebft qu\u1ea3','choice','PENDING',choices=('PENDING','PASS','FAIL'))],immutable=True,admin=True)
GROUP_ENTITIES={g:tuple(k for k,v in ENTITIES.items() if v['group']==g) for g in range(1,11)}
# Show common dependencies where they are needed, but retain the same underlying record.
GROUP_ENTITIES[2]=('assets','sensors','readings')
GROUP_ENTITIES[4]=('orders','bom','maintenance','oee','assets','materials')
GROUP_ENTITIES[9]=('staff','skills','shifts','handovers','training','ppe')
