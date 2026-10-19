import csv
import json
import sqlite3
import tempfile
import unittest
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch
from auth_local import AuthStore
from factory_core import (Factory, FactoryError, AccessDenied, Conflict, number, ident, iso_date, stamp, cost_estimate, what_if, roi_estimate, D)
from factory_schema import ENTITIES
from factory_catalog import FEATURES, GROUPS

PASS='TestFactoryOnly2026!'
class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.auth=AuthStore(self.root/'auth.sqlite3');self.auth.register('admin',PASS);self.admin=self.auth.authenticate('admin',PASS)
        self.f=Factory(self.root/'factory.sqlite3',self.auth,self.admin);self.f.add_plant('P1','Factory 1',capacity='100')
    def tearDown(self):self.tmp.cleanup()
    def employee(self,role='employee'):
        self.auth.register('worker',PASS);self.auth.approve(self.admin,'worker',role);s=self.auth.authenticate('worker',PASS)
        return Factory(self.f.path,self.auth,s)
    def save(self,kind,code,**data):return self.f.save('P1',kind,code,data)
    def row(self,kind,code):return next(r for r in self.f.list_records('P1',kind,limit=500)['rows'] if r['code']==code)
    def update(self,kind,code,**changes):
        r=self.row(kind,code);data={f.key:r[f.key] for f in ENTITIES[kind]['fields']};data.update(changes);return self.f.save('P1',kind,code,data,r['_rev'])
    def mat(self,code='RM',kind='BUY',safety='0'):self.save('materials',code,name=code,unit='pcs',type=kind,safety=safety)
    def lot(self,code='L1',qty='100',expiry='2099-01-01',quality='RELEASED',material='RM'):
        self.save('lots',code,material=material,quantity=qty,received='2020-01-01',expiry=expiry,quality=quality,location='A')
    def asset(self,code='M1',**kw):
        data=dict(name=code,type='MACHINE',capacity='10',state='IDLE');data.update(kw);self.save('assets',code,**data)
    def production(self,qty='10',stock='100',per='2'):
        self.mat();self.mat('FG','MAKE');self.save('bom','B1',parent='FG',component='RM',per=per);self.lot(qty=stock)
        self.save('orders','MO1',product='FG',quantity=qty,due='2099-01-01');self.update('orders','MO1',state='RELEASED')
    def sensor(self):
        self.asset();self.save('sensors','TEMP',asset='M1',unit='C',low='10',high='30',stale_minutes='10')
    def test_registry_preserves_exact_100_numbers(self):self.assertEqual([x['id'] for x in FEATURES],list(range(1,101)))
    def test_registry_ten_groups_ten_each(self):
        self.assertEqual(len(GROUPS),10)
        for g in range(1,11):self.assertEqual(sum(f['group']==g for f in FEATURES),10)
    def test_integrations_no_executable_route(self):
        for f in FEATURES:
            if f['status']=='integration_required':self.assertIsNone(f['route'])
    def test_no_factory_session_bypass(self):
        with self.assertRaises(AccessDenied):Factory(self.root/'bad.db',None,None)
    def test_no_mail_secrets_in_schema(self):
        for e in ENTITIES.values():self.assertFalse({'password','mail_password','token'} & {f.key for f in e['fields']})
    def test_employee_defaults_deny(self):
        e=self.employee();self.assertEqual(e.plants(),[])
        with self.assertRaises(AccessDenied):e.list_records('P1','materials')
    def test_read_grant_does_not_allow_write(self):
        e=self.employee();self.f.grant('P1','worker',3)
        self.assertEqual(e.list_records('P1','materials')['total'],0)
        with self.assertRaises(AccessDenied):e.save('P1','materials','X',{'name':'Test'})
    def test_write_grant_is_scoped(self):
        e=self.employee();self.f.grant('P1','worker',3,True);e.save('P1','materials','X',{'name':'Test'})
        with self.assertRaises(AccessDenied):e.list_records('P1','orders')
    def test_revoked_grant_immediate(self):
        e=self.employee();self.f.grant('P1','worker',3,True);self.f.revoke('P1','worker',3)
        with self.assertRaises(AccessDenied):e.list_records('P1','materials')
    def test_deactivated_session_rejected(self):
        e=self.employee();self.auth.deactivate(self.admin,'worker')
        with self.assertRaises(AccessDenied):e.plants()
    def test_auditor_read_only(self):
        e=self.employee('auditor');self.assertEqual(len(e.plants()),1)
        with self.assertRaises(AccessDenied):e.add_plant('P2','Test')
        with self.assertRaises(AccessDenied):e.save('P1','materials','X',{'name':'X'})
    def test_employee_cannot_grant(self):
        e=self.employee()
        with self.assertRaises(AccessDenied):e.grant('P1','worker',3,True)
    def test_inactive_user_cannot_receive_grant(self):
        self.auth.register('pending',PASS)
        with self.assertRaises(FactoryError):self.f.grant('P1','pending',3)
    def test_domain_range(self):
        self.employee()
        with self.assertRaises(FactoryError):self.f.grant('P1','worker',11)
    def test_personnel_master_admin_only(self):
        e=self.employee();self.f.grant('P1','worker',9,True)
        with self.assertRaises(AccessDenied):e.save('P1','staff','OP',{'name':'Operator','team':'A'})
    def test_employee_cannot_read_all_audit(self):
        e=self.employee();self.f.grant('P1','worker',5)
        with self.assertRaises(AccessDenied):e.report('P1','audit')
    def test_plant_data_isolation(self):
        self.mat();self.f.add_plant('P2','Two');self.assertEqual(self.f.list_records('P2','materials')['total'],0)
    def test_foreign_reference_is_same_plant(self):
        self.mat();self.f.add_plant('P2','Two')
        with self.assertRaises(FactoryError):self.f.save('P2','lots','X',{'material':'RM','quantity':'1','received':'2020-01-01'})
    def test_unknown_fields_rejected(self):
        with self.assertRaises(FactoryError):self.save('materials','X',name='X',admin=True)
    def test_path_like_identifiers_rejected(self):
        for x in ['../P1',';DROP TABLE records','a\nB','']:
            with self.assertRaises(FactoryError):ident(x)
    def test_nonfinite_and_extreme_numbers(self):
        for x in ['NaN','Infinity','-1','1e99','1e-8']:
            with self.assertRaises(FactoryError):number(x)
    def test_zero_not_positive(self):
        with self.assertRaises(FactoryError):number(0,positive=True)
    def test_date_requires_iso(self):
        for x in ['19/10/2026','2026-02-30']:
            with self.assertRaises(FactoryError):iso_date(x)
    def test_timestamps_require_timezone(self):
        with self.assertRaises(FactoryError):stamp('2026-10-19T08:00:00')
        self.assertEqual(stamp('2026-10-19T08:00:00+07:00'),'2026-10-19T01:00:00+00:00')
    def test_duplicate_code_no_overwrite(self):
        self.mat()
        with self.assertRaises(Conflict):self.mat()
    def test_optimistic_revision(self):
        self.mat();self.update('materials','RM',name='New')
        with self.assertRaises(Conflict):self.f.save('P1','materials','RM',{'name':'Old'},1)
    def test_mutation_and_audit_rollback_together(self):
        with patch.object(self.f,'_audit',side_effect=RuntimeError('test')):
            with self.assertRaises(RuntimeError):self.mat()
        self.assertEqual(self.f.list_records('P1','materials')['total'],0)
    def test_search_sql_injection_literal(self):
        self.mat();self.assertEqual(self.f.list_records('P1','materials',"' OR 1=1 --")['total'],0)
    def test_search_wildcard_escaped(self):
        self.mat();self.assertEqual(self.f.list_records('P1','materials','%')['total'],0)
    def test_pagination_bounded(self):
        for i in range(4):self.mat('R'+str(i))
        self.assertEqual(len(self.f.list_records('P1','materials',page=1,limit=2)['rows']),2)
        with self.assertRaises(FactoryError):self.f.list_records('P1','materials',limit=501)
    def test_bom_cycle_rejected(self):
        self.mat('A','MAKE');self.mat('B','MAKE');self.save('bom','AB',parent='A',component='B',per='1')
        with self.assertRaises(FactoryError):self.save('bom','BA',parent='B',component='A',per='1')
    def test_bom_duplicate_edge_rejected(self):
        self.production()
        with self.assertRaises(Conflict):self.save('bom','B2',parent='FG',component='RM',per='3')
    def test_bom_ten_levels_and_eleven_rejected(self):
        for i in range(12):self.mat('N'+str(i),'MAKE' if i<11 else 'BUY')
        for i in range(10):self.save('bom','B'+str(i),parent='N'+str(i),component='N'+str(i+1),per='1')
        with self.assertRaises(FactoryError):self.save('bom','B10',parent='N10',component='N11',per='1')
    def test_mrp_multilevel_and_inbound_cutoff(self):
        for k,t in [('FG','MAKE'),('SUB','MAKE'),('RM','BUY')]:self.mat(k,t)
        self.save('bom','B1',parent='FG',component='SUB',per='2');self.save('bom','B2',parent='SUB',component='RM',per='3')
        self.save('inbound','PO1',material='RM',quantity='5',eta='2026-10-19');self.save('inbound','PO2',material='RM',quantity='99',eta='2027-01-01')
        r={x['material']:x for x in self.f.mrp('P1','FG',10,'2026-10-20')}
        self.assertEqual(r['RM']['gross'],'60');self.assertEqual(r['RM']['net'],'55')
    def test_mrp_shared_component_no_double_stock(self):
        for k,t in [('FG','MAKE'),('A','MAKE'),('B','MAKE'),('RM','BUY')]:self.mat(k,t)
        for code,p,c in [('FA','FG','A'),('FB','FG','B'),('AR','A','RM'),('BR','B','RM')]:self.save('bom',code,parent=p,component=c,per='1')
        self.lot(qty='5')
        r={x['material']:x for x in self.f.mrp('P1','FG',10,'2026-10-20')};self.assertEqual(r['RM']['net'],'15')
    def test_mrp_nets_intermediate_stock(self):
        for k,t in [('FG','MAKE'),('SUB','MAKE'),('RM','BUY')]:self.mat(k,t)
        self.save('bom','B1',parent='FG',component='SUB',per='2');self.save('bom','B2',parent='SUB',component='RM',per='3');self.lot(material='SUB',qty='5')
        r={x['material']:x for x in self.f.mrp('P1','FG',10,'2026-10-20')};self.assertEqual(r['RM']['gross'],'45')
    def test_mrp_missing_bom_is_not_silently_ignored(self):
        self.mat('FG','MAKE')
        with self.assertRaises(FactoryError):self.f.mrp('P1','FG',1,'2026-10-20')
    def test_safety_shortage(self):
        self.mat(safety='10');self.lot(qty='5');self.assertEqual(self.f.report('P1','stock')[0]['status'],'BELOW_SAFETY')
    def test_future_receipt_rejected(self):
        self.mat()
        with self.assertRaises(FactoryError):self.save('lots','F',material='RM',quantity='1',received='2099-01-01')
    def test_issue_requires_released_order(self):
        self.production();self.update('orders','MO1',state='HOLD')
        with self.assertRaises(FactoryError):self.f.issue('P1','I1','MO1','RM',1)
    def test_issue_fefo_earliest_expiry_first(self):
        self.production(stock='10');self.lot('EARLY',qty='10',expiry='2098-01-01')
        r=self.f.issue('P1','I1','MO1','RM','15');self.assertEqual(r['allocations'][0]['lot'],'EARLY');self.assertEqual(self.row('lots','L1')['quantity'],'5')
    def test_expired_blocked_lots_not_issued(self):
        self.production(stock='0');self.lot('EX',expiry='2021-01-01');self.lot('BLOCK',quality='BLOCKED')
        with self.assertRaises(FactoryError):self.f.issue('P1','I1','MO1','RM','1')
    def test_posting_cannot_backdate_to_bypass_expiry(self):
        self.production()
        with self.assertRaises(FactoryError):self.f.issue('P1','I1','MO1','RM',1,'2020-01-01')
    def test_issue_cumulative_bom_limit(self):
        self.production();self.f.issue('P1','I1','MO1','RM',15)
        with self.assertRaises(FactoryError):self.f.issue('P1','I2','MO1','RM',6)
    def test_issue_snapshot_not_changed_by_later_bom(self):
        self.production();self.update('bom','B1',per='5')
        with self.assertRaises(FactoryError):self.f.issue('P1','I1','MO1','RM',21)
    def test_issue_idempotent_same_request(self):
        self.production();a=self.f.issue('P1','I1','MO1','RM',10);b=self.f.issue('P1','I1','MO1','RM',10)
        self.assertEqual(a,b);self.assertEqual(self.row('lots','L1')['quantity'],'90')
    def test_reused_request_with_different_payload_rejected(self):
        self.production();self.f.issue('P1','I1','MO1','RM',10)
        with self.assertRaises(Conflict):self.f.issue('P1','I1','MO1','RM',11)
    def test_concurrent_stock_issues_do_not_overspend(self):
        self.production(stock='10')
        def go(i):
            try:self.f.issue('P1','I'+str(i),'MO1','RM',7);return True
            except FactoryError:return False
        with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(go,[1,2]))
        self.assertEqual(sum(result),1);self.assertEqual(self.row('lots','L1')['quantity'],'3')
    def test_posted_lot_cannot_edit_quantity(self):
        self.production()
        with self.assertRaises(FactoryError):self.update('lots','L1',quantity='999')
    def test_output_requires_issued_inputs(self):
        self.production()
        with self.assertRaises(FactoryError):self.f.output('P1','O1','MO1',1,0,'FG1')
    def test_output_and_two_way_trace(self):
        self.production();self.f.issue('P1','I1','MO1','RM',20);self.f.output('P1','O1','MO1',10,0,'FG1')
        self.assertEqual(self.row('lots','FG1')['quality'],'HOLD');self.assertEqual(self.f.trace('P1','L1'),self.f.trace('P1','FG1'))
    def test_output_repeated_not_duplicated(self):
        self.production();self.f.issue('P1','I1','MO1','RM',20);self.f.output('P1','O1','MO1',10,0,'FG1');self.f.output('P1','O1','MO1',10,0,'FG1')
        self.assertEqual(self.row('orders','MO1')['good_qty'],'10')
    def test_order_cannot_close_incomplete(self):
        self.production()
        with self.assertRaises(FactoryError):self.update('orders','MO1',state='CLOSED')
    def test_closed_order_cannot_change(self):
        self.production();self.f.issue('P1','I1','MO1','RM',20);self.f.output('P1','O1','MO1',10,0,'FG1');self.update('orders','MO1',state='CLOSED')
        with self.assertRaises(FactoryError):self.update('orders','MO1',state='RELEASED')
    def test_return_issue_exactly_once(self):
        self.production();self.f.issue('P1','I1','MO1','RM',20);self.f.return_issue('P1','R1','I1','Mistake');self.f.return_issue('P1','R1','I1','Mistake')
        self.assertEqual(self.row('lots','L1')['quantity'],'100')
        with self.assertRaises(FactoryError):self.f.return_issue('P1','R2','I1','Again')
    def test_return_after_output_rejected(self):
        self.production();self.f.issue('P1','I1','MO1','RM',20);self.f.output('P1','O1','MO1',1,0,'FG1')
        with self.assertRaises(FactoryError):self.f.return_issue('P1','R1','I1','Wrong')
    def test_cancel_requires_return(self):
        self.production();self.f.issue('P1','I1','MO1','RM',20);self.update('orders','MO1',state='HOLD')
        with self.assertRaises(FactoryError):self.update('orders','MO1',state='CANCELLED')
        self.f.return_issue('P1','R1','I1','Cancel');self.update('orders','MO1',state='CANCELLED')
    def test_abc_excludes_reversed_issue(self):
        self.production();self.f.issue('P1','I1','MO1','RM',20);self.f.return_issue('P1','R1','I1','Cancel');self.assertEqual(self.f.report('P1','abc'),[])
    def test_count_snapshot_is_not_later_stock(self):
        self.production();self.save('counts','C1',lot='L1',counted='99',at=datetime.now(timezone.utc).isoformat());self.f.issue('P1','I1','MO1','RM',10)
        r=self.f.report('P1','reconcile')[0];self.assertEqual(r['difference'],'-1');self.assertIn('snapshot_at',r)
    def test_oee_correct_formula(self):
        self.asset();self.save('oee','S1',asset='M1',date='2026-10-19',planned_min='480',run_min='420',cycle_sec='60',total='400',good='380')
        r=self.f.report('P1','oee')[0];self.assertEqual(r['oee_pct'],'79.17')
    def test_oee_invalid_good_rejected(self):
        self.asset()
        with self.assertRaises(FactoryError):self.save('oee','S1',asset='M1',date='2026-10-19',planned_min='480',run_min='420',cycle_sec='60',total='10',good='11')
    def test_oee_impossible_cycle_is_visible(self):
        self.asset();self.save('oee','S1',asset='M1',date='2026-10-19',planned_min='10',run_min='10',cycle_sec='60',total='100',good='100');self.assertEqual(self.f.report('P1','oee')[0]['warning'],'CHECK_CYCLE_TIME')
    def test_maintenance_moves_draft_plan(self):
        self.production();self.asset();self.save('maintenance','B1',asset='M1',start='2026-10-20T08:00+07:00',end='2026-10-20T09:00+07:00',reason='Check')
        r=self.f.plan('P1','M1','2026-10-20T08:00+07:00')[0];self.assertEqual(r['start_utc'],'2026-10-20T02:00:00+00:00');self.assertTrue(r['maintenance_shifted'])
    def test_unavailable_machine_not_scheduled(self):
        self.asset(state='MAINTENANCE')
        with self.assertRaises(FactoryError):self.f.plan('P1','M1','2026-10-20T08:00+07:00')
    def test_allocation_preserves_small_quantity(self):
        self.f.add_plant('P2','Two',capacity='100');self.f.add_plant('P3','Three',capacity='100')
        rows=self.f.allocation('0.000001');self.assertEqual(sum(D(x['suggested_qty']) for x in rows),D('0.000001'));self.assertTrue(all(D(x['suggested_qty'])>=0 for x in rows))
    def test_duplicate_ip_same_plant(self):
        self.asset(ip='192.168.11.10')
        with self.assertRaises(Conflict):self.asset('M2',ip='192.168.11.10')
    def test_topology_parent_cycle_rejected(self):
        self.asset();self.asset('M2',parent='M1')
        with self.assertRaises(FactoryError):self.update('assets','M1',parent='M2')
    def test_sensor_threshold_creates_incident(self):
        self.sensor();self.save('readings','R1',sensor='TEMP',value='35',at=datetime.now(timezone.utc).isoformat())
        self.assertEqual(self.f.list_records('P1','incidents')['total'],1);self.assertEqual(self.f.report('P1','sensors')[0]['status'],'ALERT')
    def test_sensor_without_samples_not_online(self):
        self.sensor();self.assertEqual(self.f.report('P1','sensors')[0]['status'],'NO_DATA')
    def test_stale_sensor_not_healthy(self):
        self.sensor();self.save('readings','R1',sensor='TEMP',value='20',at='2020-01-01T00:00+00:00');self.assertEqual(self.f.report('P1','sensors')[0]['status'],'STALE')
    def test_sensor_range_rejects_swapped_threshold(self):
        self.asset()
        with self.assertRaises(FactoryError):self.save('sensors','S',asset='M1',unit='C',low='50',high='20')
    def test_failed_iqc_quarantines_lot(self):
        self.production();self.save('inspections','QC',stage='IQC',lot='L1',sampled='10',rejected='1',reason='Crack',date='2026-10-19');self.assertEqual(self.row('lots','L1')['quality'],'BLOCKED')
    def test_quality_release_needs_reason(self):
        self.production()
        with self.assertRaises(FactoryError):self.f.lot_quality('P1','L1','RELEASED','')
    def test_capa_requires_verified_lifecycle(self):
        self.save('capa','C1',title='Crack',owner='QA',due='2099-01-01')
        with self.assertRaises(FactoryError):self.update('capa','C1',state='CLOSED')
        self.update('capa','C1',state='IN_PROGRESS',cause='Tool',action='Repair');self.update('capa','C1',state='VERIFY')
        with self.assertRaises(FactoryError):self.update('capa','C1',state='CLOSED')
        self.update('capa','C1',state='CLOSED',verification='Inspection PASS')
    def test_shift_requires_valid_skill(self):
        self.asset(skill='PRESS');self.save('staff','OP',name='Operator',team='A')
        with self.assertRaises(FactoryError):self.save('shifts','S1',asset='M1',staff='OP',start='2026-10-20T08:00+07:00',end='2026-10-20T16:00+07:00')
    def test_shift_checks_certificate_through_local_midnight(self):
        self.asset(skill='PRESS');self.save('staff','OP',name='Operator',team='A');self.save('skills','K',staff='OP',skill='PRESS',valid_from='2026-01-01',valid_to='2026-10-20',certificate='Cert')
        with self.assertRaises(FactoryError):self.save('shifts','S1',asset='M1',staff='OP',start='2026-10-20T23:00+07:00',end='2026-10-21T02:00+07:00')
    def test_shifts_prevent_staff_overlap(self):
        self.asset();self.asset('M2');self.save('staff','OP',name='Operator',team='A');self.save('shifts','S1',asset='M1',staff='OP',start='2026-10-20T08:00+07:00',end='2026-10-20T16:00+07:00')
        with self.assertRaises(Conflict):self.save('shifts','S2',asset='M2',staff='OP',start='2026-10-20T10:00+07:00',end='2026-10-20T18:00+07:00')
    def test_energy_unknown_factor_not_zero_carbon(self):
        self.asset();self.save('energy','E1',asset='M1',start='2026-10-20T08:00+07:00',end='2026-10-20T09:00+07:00',kwh='10',tariff='2000')
        r=self.f.report('P1','energy_report')[0];self.assertEqual(r['co2e_kg'],'UNKNOWN');self.assertEqual(r['cost'],'20000')
    def test_carbon_factor_needs_provenance(self):
        self.asset()
        with self.assertRaises(FactoryError):self.save('energy','E1',asset='M1',start='2026-10-20T08:00+07:00',end='2026-10-20T09:00+07:00',kwh='10',factor='.5')
    def test_energy_intervals_cannot_double_count(self):
        self.asset();self.save('energy','E1',asset='M1',start='2026-10-20T08:00+07:00',end='2026-10-20T09:00+07:00',kwh='10')
        with self.assertRaises(Conflict):self.save('energy','E2',asset='M1',start='2026-10-20T08:30+07:00',end='2026-10-20T09:30+07:00',kwh='10')
    def test_cost_calculations(self):
        self.assertEqual(cost_estimate(10,100,20,30,50)['unit_cost'],'20');self.assertEqual(roi_estimate(100,0)['simple_payback_years'],'NO_POSITIVE_PAYBACK');self.assertEqual(len(what_if(10,1,2,3)),3)
    def test_preferences_persist_per_account(self):
        self.f.preferences({'plant':'P1','group':4});self.assertEqual(self.f.preferences()['group'],4)
        e=self.employee();self.assertEqual(e.preferences(),{})
    def test_csv_atomic_import_rolls_back_all(self):
        path=self.root/'in.csv';path.write_text('code,name,unit,type,safety\nA,Valid,pcs,BUY,0\nB,Bad,pcs,BUY,-1\n')
        with self.assertRaises(FactoryError):self.f.import_csv('P1','materials',path)
        self.assertEqual(self.f.list_records('P1','materials')['total'],0)
    def test_csv_duplicate_rolls_back_prior_rows(self):
        self.mat('EXIST');path=self.root/'in.csv';path.write_text('code,name,unit,type,safety\nNEW,Valid,pcs,BUY,0\nEXIST,Dup,pcs,BUY,0\n')
        with self.assertRaises(Conflict):self.f.import_csv('P1','materials',path)
        self.assertEqual(self.f.list_records('P1','materials')['total'],1)
    def test_csv_formula_injection_and_utf8_bom(self):
        self.save('materials','X',name='=HYPERLINK("test")');path=self.root/'export.csv';self.f.export_records('P1','materials',path)
        self.assertTrue(path.read_bytes().startswith(b'\xef\xbb\xbf'));self.assertIn("'=HYPERLINK",path.read_text(encoding='utf-8-sig'))
    def test_export_never_overwrites_file(self):
        path=self.root/'existing.csv';path.write_text('KEEP')
        with self.assertRaises(FileExistsError):self.f.export_records('P1','materials',path)
        self.assertEqual(path.read_text(),'KEEP')
    def test_audit_chain_detects_edit(self):
        self.mat();self.assertTrue(self.f.verify_audit()['ok'])
        with sqlite3.connect(self.f.path) as db:db.execute("UPDATE audit SET detail='changed' WHERE id=1")
        self.assertFalse(self.f.verify_audit()['ok'])
    def test_backup_verified_and_restored_to_new_file(self):
        self.mat();path=self.root/'backup.zip';self.f.backup(path);target=self.root/'recovered.sqlite3';self.assertTrue(self.f.verify_backup(path,target)['ok'])
        with sqlite3.connect(target) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM records').fetchone()[0],1)
    def test_recovery_never_overwrites_current_db(self):
        path=self.root/'b.zip';self.f.backup(path)
        with self.assertRaises(FactoryError):self.f.verify_backup(path,self.f.path)
    def test_backup_rejects_checksum_tampering(self):
        path=self.root/'b.zip';self.f.backup(path)
        with zipfile.ZipFile(path) as z:blob=z.read('factory.sqlite3');manifest=json.loads(z.read('manifest.json'))
        manifest['sha256']='0'*64
        bad=self.root/'bad.zip'
        with zipfile.ZipFile(bad,'w') as z:z.writestr('factory.sqlite3',blob);z.writestr('manifest.json',json.dumps(manifest))
        with self.assertRaises(FactoryError):self.f.verify_backup(bad)
    def test_backup_rejects_path_traversal(self):
        path=self.root/'evil.zip'
        with zipfile.ZipFile(path,'w') as z:z.writestr('../owned','evil')
        with self.assertRaises(FactoryError):self.f.verify_backup(path)
        self.assertFalse((self.root.parent/'owned').exists())
    def test_future_schema_is_not_downgraded(self):
        with sqlite3.connect(self.f.path) as db:db.execute("UPDATE meta SET value='99' WHERE key='schema_version'")
        with self.assertRaises(FactoryError):Factory(self.f.path,self.auth,self.admin)
    def test_local_date_uses_plant_offset(self):
        with self.f.connection() as db:self.assertEqual(self.f._local_date(db,'P1','2026-10-20T18:00:00+00:00'),'2026-10-21')

    def test_update_plant_capacity_without_losing_records(self):
        self.mat();self.f.update_plant('P1','Renamed','VND','230',420)
        p=self.f.plants()[0];self.assertEqual(p['capacity'],'230');self.assertEqual(p['name'],'Renamed')
        self.assertEqual(self.f.list_records('P1','materials')['total'],1)
    def test_plant_currency_and_timezone_lock_after_data(self):
        self.mat()
        for currency,offset in [('USD',420),('VND',0)]:
            with self.assertRaises(FactoryError):self.f.update_plant('P1','One',currency,'100',offset)
        self.assertEqual(self.f.plants()[0]['currency'],'VND')
    def test_empty_plant_timezone_change(self):
        self.f.update_plant('P1','One','USD','100',-300)
        self.assertEqual(self.f.plants()[0]['utc_offset'],-300)
    def test_fractional_timezone_rejected(self):
        for off in ['420.5',420.5,-721,841]:
            with self.assertRaises(FactoryError):self.f.add_plant('Bad','Bad','VND',100,off)
    def test_employee_cannot_update_plant(self):
        e=self.employee();self.f.grant('P1','worker',1,True)
        with self.assertRaises(AccessDenied):e.update_plant('P1','Wrong','VND',1,420)
