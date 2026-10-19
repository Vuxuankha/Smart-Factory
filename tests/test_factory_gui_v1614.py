import os
import tempfile
import threading
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch
from app import Application
from auth_local import AuthStore
from factory_ui import FormDialog
from factory_schema import ENTITIES,F

PASS='GuiTestFactory2026!'
@unittest.skipUnless(os.environ.get('DISPLAY'),'Needs DISPLAY / Xvfb')
class FactoryUITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)
        self.auth=AuthStore(self.path/'accounts.sqlite3');self.auth.register('admin',PASS);self.user=self.auth.authenticate('admin',PASS)
        self.root=tk.Tk();self.root.withdraw();self.errors=[];self.root.report_callback_exception=lambda *args:self.errors.append(args)
        self.app=Application(self.root,self.user,self.auth)
        self.w=self.app.open_factory();self.root.update()
    def tearDown(self):
        self.root.destroy();self.tmp.cleanup()
        self.assertEqual(self.errors,[],'Tk callbacks must not fail')
    def plant(self):
        self.w.service.add_plant('P1','Test');self.w.plant_var.set('P1');self.w.refresh()
    def spin(self,seconds=2):
        end=time.time()+seconds
        while time.time()<end:
            self.root.update();time.sleep(.01)
            if not self.w._busy:break
    def test_factory_window_open(self):self.assertTrue(self.w.win.winfo_exists())
    def test_one_window_reused(self):self.assertIs(self.app.open_factory(4),self.w)
    def test_ten_group_navigation(self):
        for g in range(1,11):self.w.select_group(g);self.root.update();self.assertEqual(self.w.group,g)
    def test_each_group_has_ten_scope_items(self):
        for g in range(1,11):self.w.select_group(g);self.assertEqual(len(self.w.scope_tree.get_children()),10)
    def test_scope_integration_button_disabled(self):
        self.w.select_group(2);self.w.scope_tree.selection_set('11');self.w.scope_detail();self.assertEqual(str(self.w.scope_open['state']),'disabled')
    def test_all_groups_do_not_prompt_mail_password(self):
        with patch('app.simpledialog.askstring') as ask:
            for g in range(1,11):self.w.select_group(g);self.root.update()
            ask.assert_not_called()
    def test_worker_result_reaches_ui_thread(self):
        main=threading.get_ident();seen=[]
        self.w.run_task(lambda:threading.get_ident(),lambda result:seen.append((result,threading.get_ident())))
        self.spin();self.assertNotEqual(seen[0][0],main);self.assertEqual(seen[0][1],main)
    def test_duplicate_job_not_launched(self):
        gate=threading.Event();calls=[]
        self.assertTrue(self.w.run_task(lambda:gate.wait(1)))
        self.assertFalse(self.w.run_task(lambda:calls.append('duplicate')));gate.set();self.spin();self.assertEqual(calls,[])
    def test_close_during_job_is_prevented(self):
        gate=threading.Event();self.w.run_task(lambda:gate.wait(1))
        with patch('factory_ui.messagebox.showwarning') as msg:self.w.close();self.assertTrue(self.w.win.winfo_exists());msg.assert_called_once()
        gate.set();self.spin()
    def test_logout_during_job_is_prevented(self):
        gate=threading.Event();self.w.run_task(lambda:gate.wait(1))
        with patch('app.messagebox.showinfo') as msg:self.app.logout();self.assertIsNotNone(self.app.session);msg.assert_called_once()
        gate.set();self.spin()
    def test_poll_cancelled_on_destroy(self):
        self.w.close();self.root.update();self.assertTrue(self.w._closed);self.assertIsNone(self.w._poll_id)
    def test_new_form_is_real_input(self):
        self.plant();self.w.select_group(3);self.w.entity_var.set(ENTITIES['materials']['label'])
        d=FormDialog(self.w,'Test',[F('code','Code'),F('name','Name')],lambda v:self.w.service.save('P1','materials',v['code'],{'name':v['name']}))
        d.vars['code'].set('RM');d.vars['name'].set('Material');d.save();self.spin()
        self.assertEqual(self.w.service.list_records('P1','materials')['total'],1)
    def test_form_required_fields_no_job(self):
        d=FormDialog(self.w,'Test',[F('code','Code')],lambda v:None);d.save();self.assertFalse(self.w._busy);self.assertTrue(d.error_var.get());d.win.destroy()
    def test_form_invalid_backend_data_can_retry(self):
        self.plant();d=FormDialog(self.w,'Test',[F('qty','Qty')],lambda v:self.w.service.save('P1','materials','RM',{'name':'R','safety':v['qty']}));d.vars['qty'].set('-1')
        with patch('factory_ui.messagebox.showwarning'):d.save();self.spin()
        self.assertTrue(d.win.winfo_exists());self.assertEqual(str(d.save_button['state']),'normal');d.win.destroy()
    def test_posted_lot_edit_is_disabled(self):
        self.plant();self.w.select_group(3);self.w.entity_var.set(ENTITIES['lots']['label']);self.w.refresh_data();self.assertEqual(str(self.w.edit_button['state']),'disabled')
    def test_empty_state_visible(self):
        self.assertTrue(self.w.empty_label.cget('text'));self.assertEqual(self.w.metrics['orders'].value.get(),'\u2014')
    def test_table_and_search(self):
        self.plant();self.w.service.save('P1','materials','RM',{'name':'Steel'});self.w.select_group(3);self.w.search_var.set('Steel');self.w.refresh_data();self.assertEqual(len(self.w.tree.get_children()),1)
    def test_saved_group_reopened(self):
        self.plant();self.w.select_group(8);self.w.save_preference();self.w.close();self.w=self.app.open_factory();self.root.update();self.assertEqual(self.w.group,8)
    def test_dashboard_real_counts(self):
        self.plant();self.w.service.save('P1','materials','RM',{'name':'R'});self.w.refresh();self.assertEqual(self.w.metrics['orders'].value.get(),'0')
    def test_no_fake_oee_when_empty(self):
        self.plant();self.w.select_group(6);self.root.update();self.assertEqual(self.w.chart_data,([],[]))
    def test_entrypoints_include_factory_nav(self):self.assertTrue(any('Smart Factory' in name for _,name in self.app.sidebar_items))
    def test_no_regression_mail_mode(self):
        self.app.account.set('test@example.org');self.app.mode.set('admin');self.app.switch_mode();self.app.mode.set('employee');self.app.switch_mode();self.assertEqual(self.app.account.get(),'test@example.org')
    def test_all_record_forms_open_without_mail(self):
        self.plant()
        with patch('app.simpledialog.askstring') as ask:
            for kind,e in ENTITIES.items():
                d=FormDialog(self.w,e['label'],e['fields'],lambda v:None,refs=True);self.root.update();self.assertEqual(len(d.vars),len(e['fields']));d.win.destroy()
            ask.assert_not_called()
    def test_no_mail_prompt_stock_report(self):
        self.plant()
        with patch('app.simpledialog.askstring') as ask:self.w.show_report('stock');self.spin();ask.assert_not_called()
    def test_window_resizes(self):
        self.w.win.geometry('1100x680');self.w.select_group(4);self.root.update();self.assertTrue(self.w.tree.winfo_exists());self.assertGreater(self.w.tree.winfo_width(),100)

    def test_form_cannot_close_during_committed_job(self):
        gate=threading.Event();d=FormDialog(self.w,'Test',[F('code','Code')],lambda v:gate.wait(2));d.vars['code'].set('X');d.save()
        d.close();self.assertTrue(d.win.winfo_exists());self.assertEqual(str(d.cancel_button['state']),'disabled')
        gate.set();self.spin();self.assertFalse(d.win.winfo_exists())
    def test_form_ctrl_enter_cannot_duplicate_write(self):
        gate=threading.Event();seen=[]
        def work(v):gate.wait(2);seen.append(v['code'])
        d=FormDialog(self.w,'Test',[F('code','Code')],work);d.vars['code'].set('X');d.save();d.save();gate.set();self.spin();self.assertEqual(seen,['X'])
    def test_form_cancel_before_submit_has_no_write(self):
        seen=[];d=FormDialog(self.w,'Test',[F('code','Code')],lambda v:seen.append(v));d.vars['code'].set('X');d.close();self.assertEqual(seen,[])
