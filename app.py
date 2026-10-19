"""Windows GUI for Alibaba Mail backup. IMAP logic lives in mail_backend."""
import csv
import sqlite3
import imaplib
import json
import logging
import math
import os
import queue
import shutil
import socket
import ssl
import sys
import threading
import time
import traceback
from logging.handlers import RotatingFileHandler
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog, simpledialog, messagebox

import kiem_tra
import network_manager as network
from infra_ui import InfraWindow
from pmc_ui import PMCWindow
from quota_ui import QuotaWindow
from usage_stats import UsageDB, export_reports, storage_usage
from mail_backend import *
from issue_journal import IssueJournal, FIELDS
from industrial_theme import apply_theme, NAVY, BG, WHITE, MUTED, BLUE
from auth_local import AuthStore, Session, ROLE_LABELS
from auth_ui import AuthDialog, show_manage_users, change_password_dialog
from dashboard_layout import create_dashboard
from factory_ui import FactoryWindow
from factory_catalog import GROUPS

class Application:
    def __init__(self, root, session=None, auth_store=None):
        self.root = root
        self.session = session
        self.auth_store = auth_store
        self._after_jobs = set()
        self._closing = False
        self._infra_window = None
        self._pmc_window = None
        self._network_window = None
        self._factory_window = None
        self.diagnosing = False
        self.issues = []
        self.issue_window = None
        self.issue_tree = None
        self.issue_report = None
        self.issue_path = None
        self.issues_preview_count = 0
        self.close_requested = False
        self._logger = None
        self._log_handler = None
        self._secrets = []
        self._preview_lock = threading.Lock()
        root.title('Alibaba Operations Center V16.0.14 • Industrial Dashboard')
        screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f'{min(1490,max(900,screen_w-80))}x{min(940,max(650,screen_h-105))}')
        root.minsize(min(1120,screen_w),min(680,screen_h))
        apply_theme(root)
        root.protocol('WM_DELETE_WINDOW', self.on_close)
        root.bind('<Destroy>', self._on_widget_destroy, add='+')
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.active = False
        self.mode = tk.StringVar(value='employee')
        self.account = tk.StringVar()
        self.destination = tk.StringVar(value=str(Path.home() / 'Documents' / 'SaoLuuAlibabaMail'))
        self.speed_limit = tk.StringVar(value='0')
        self.worker_count = tk.StringVar(value='3')
        self.folder_layout = tk.StringVar(value='Theo nam > thang > hop thu > nguoi gui/nhan (V16)')
        self.folder_layout_choices = {
            'Theo nam > thang > hop thu > nguoi gui/nhan (V16)': 'year_month_mailbox_contact',
            'Theo nam > hop thu > nguoi gui/nhan (V15)': 'year_mailbox_contact',
            'Theo ngay: ngay - nguoi gui - nguoi nhan': 'date_people',
            'Theo nguoi gui - nguoi nhan - ngay': 'people_date',
            'Kieu V13: ngay - tieu de - nguoi gui': 'legacy',
        }
        self.stats_line = tk.StringVar(value='Chua co luot sao luu')
        self.build()
        self.build_menu()
        self.bind_shortcuts()
        self._schedule(1800, self.refresh_health)
        self._schedule(100, self.process_events)

    def build(self):
        create_dashboard(self)
        if self.session and not self.session.allows('mail'):
            for button in (self.start_button, self.inspect_button):
                button.configure(state='disabled')
            self.stats_line.set('Chế độ xem: tài khoản không có quyền sao lưu Email.')

    def _schedule(self, millis, callback):
        if self._closing:
            return None
        job_id = [None]
        def fire():
            self._after_jobs.discard(job_id[0])
            if not self._closing and self.root.winfo_exists():
                callback()
        try:
            job_id[0] = self.root.after(millis, fire)
            self._after_jobs.add(job_id[0])
            return job_id[0]
        except tk.TclError:
            return None

    def _cancel_scheduled(self):
        self._closing = True
        for job in tuple(self._after_jobs):
            try: self.root.after_cancel(job)
            except tk.TclError: pass
        self._after_jobs.clear()

    def _on_widget_destroy(self, event):
        if event.widget is self.root:
            self._cancel_scheduled()

    def _permit(self, feature):
        if self.session is not None and self.auth_store is not None:
            if not self.auth_store.session_current(self.session):
                messagebox.showwarning('Phiên đăng nhập hết hiệu lực',
                    'Tài khoản đã bị khóa hoặc quyền đã thay đổi. Hãy đăng xuất và đăng nhập lại.',parent=self.root)
                return False
        if self.session is None or self.session.allows(feature):
            return True
        messagebox.showwarning('Phân quyền',
            'Tài khoản ứng dụng của bạn không có quyền sử dụng chức năng này.',parent=self.root)
        return False

    def can_access_nav(self, index):
        if self.session is None:
            return True
        features=('mail','mail','network','infra','pmc','reports','system_check','users','factory')
        return self.session.allows(features[index])

    def focus_mail(self):
        if not self._permit('mail'):
            return
        self.main_panel.focus_set()

    def manage_users(self):
        if self._permit('users') and self.auth_store is not None:
            return show_manage_users(self.root,self.auth_store,self.session)

    def change_application_password(self):
        if self.auth_store is not None and self.session is not None:
            change_password_dialog(self.root,self.auth_store,self.session)

    def logout(self):
        if self._factory_busy():
            messagebox.showinfo('Smart Factory','Cho tac vu Smart Factory hoan thanh truoc khi dang xuat.',parent=self.root)
            return
        if self.active or self.diagnosing:
            messagebox.showinfo('Tác vụ đang chạy',
                'Hãy dừng an toàn và chờ tác vụ hoàn thành trước khi đăng xuất.',parent=self.root)
            return
        if self.auth_store is None:
            return
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel):
                child.destroy()
        self._cancel_scheduled()
        self._stop_file_logging()
        self._secrets.clear()
        self.shell.destroy()
        self.root.config(menu='')
        self.root.withdraw()
        self.session=None
        def on_success(session):
            self.root.deiconify()
            Application(self.root,session=session,auth_store=self.auth_store)
        AuthDialog(self.root,self.auth_store,on_success)

    def bind_shortcuts(self):
        self.root.bind('<Control-Return>',lambda e:self.start())
        self.root.bind('<Control-Shift-s>',lambda e:self.request_stop() if self.active else None)
        self.root.bind('<Control-l>',lambda e:self.toggle_logs())
        self.root.bind('<Control-k>',lambda e:self.open_command_palette())
        self.root.bind('<Control-grave>',lambda e:self.toggle_logs())

    def open_command_palette(self):
        dialog=tk.Toplevel(self.root)
        dialog.title('Tìm nhanh chức năng')
        dialog.geometry('460x380')
        dialog.transient(self.root)
        query=tk.StringVar()
        entry=ttk.Entry(dialog,textvariable=query)
        entry.pack(fill='x',padx=15,pady=15)
        commands=[('Smart Factory / 100 hang muc',self.open_factory),('Sao lưu email',self.start),('Kiểm tra IMAP',self.inspect),
                  ('Dung lượng hộp thư',self.open_mail_quota),('Mạng & VPN',self.open_network_manager),
                  ('Giám sát hạ tầng',self.open_infrastructure),('PMC',self.open_pmc),
                  ('Kiểm tra máy tính',self.diagnose),('Nhật ký lỗi',self.show_issues),
                  ('Xuất báo cáo',self.export_usage),('Quản lý người dùng',self.manage_users)]
        listbox=tk.Listbox(dialog,font=('Segoe UI',11),height=12)
        listbox.pack(fill='both',expand=True,padx=15,pady=(0,15))
        visible=[]
        def update(*_):
            visible[:]=[(name,action) for name,action in commands if query.get().casefold() in name.casefold() and self._command_permitted(name)]
            listbox.delete(0,'end')
            for name,_ in visible:listbox.insert('end',name)
            if visible:listbox.selection_set(0)
        def execute(_=None):
            picked=listbox.curselection()
            if picked and picked[0]<len(visible):
                cb=visible[picked[0]][1]
                dialog.destroy()
                cb()
        query.trace_add('write',update)
        entry.bind('<Return>',execute)
        listbox.bind('<Double-Button-1>',execute)
        listbox.bind('<Return>',execute)
        dialog.bind('<Escape>',lambda _:dialog.destroy())
        update()
        entry.focus_set()

    def refresh_health(self):
        if self._closing:
            return
        cpu=None;ram=None
        try:
            target = self.destination.get().strip()
            path=Path(target) if target and Path(target).exists() else Path.home()
            disk=shutil.disk_usage(path)
            free=disk.free/1024**3
            used_pct=100*(disk.total-disk.free)/disk.total if disk.total else 0
            try:
                import psutil
                cpu=psutil.cpu_percent(interval=None)
                ram=psutil.virtual_memory().percent
                cpu_label=f'{cpu:.0f}%';ram_label=f'{ram:.0f}%'
            except (ImportError, OSError):
                cpu_label=ram_label='N/A'
            self.health_var.set(f'CPU        {cpu_label}\nRAM        {ram_label}\nỔ đĩa       {free:.1f} GB trống\nĐã dùng    {used_pct:.0f}%')
            self.metric_cards['cpu'].update_value(cpu_label, 'Theo dõi máy hiện tại')
            self.metric_cards['ram'].update_value(ram_label,'Dung lượng sử dụng')
            self.metric_cards['disk'].update_value(f'{free:.1f} GB',f'Còn trống · {used_pct:.0f}% đã dùng')
            self.metric_cards['backup'].update_value('ĐANG CHẠY' if self.active else 'SẴN SÀNG',
                                                      'Đang xử lý tác vụ' if self.active else 'Không có tác vụ sao lưu')
            if cpu is not None:self.cpu_graph.push(cpu)
            if used_pct>=95:
                self.alert_var.set('NGUY HIỂM: Ổ đĩa đã sử dụng ít nhất 95%. Kiểm tra nơi lưu trước khi sao lưu.')
            elif used_pct>=85:
                self.alert_var.set('CẢNH BÁO: Ổ đĩa đã dùng ít nhất 85%. Nên kiểm tra dung lượng trống.')
            else:
                self.alert_var.set('Ổ đĩa còn đủ không gian theo ngưỡng 85%. Trạng thái IMAP cần kiểm tra riêng.')
        except (OSError,ValueError) as exc:
            self.health_var.set('Không thể đọc dữ liệu ổ đĩa: '+str(exc))
            self.alert_var.set('Không thể đọc sức khỏe hệ thống.')
        self._schedule(7000,self.refresh_health)

    def build_menu(self):
        """Group all existing and optional operations in a conventional menu bar."""
        bar = tk.Menu(self.root)
        mail = tk.Menu(bar, tearoff=False)
        mail.add_command(label='Bat dau sao luu', command=self.start)
        mail.add_command(label='Dung sao luu', command=self.request_stop)
        mail.add_separator()
        mail.add_command(label='Kiem tra IMAP', command=self.inspect)
        mail.add_command(label='Dung luong hop thu (IMAP QUOTA)', command=self.open_mail_quota)
        mail.add_command(label='Chon thu muc sao luu', command=self.pick)
        mail.add_command(label='Mo noi luu', command=self.open_destination)
        mail.add_command(label='Xuat bao cao su dung', command=self.export_usage)
        mail.add_command(label='Danh sach loi', command=self.show_issues)
        bar.add_cascade(label='Email / Sao luu', menu=mail)
        net = tk.Menu(bar, tearoff=False)
        net.add_command(label='Quan ly LAN / IP / VPN', command=self.open_network_manager)
        net.add_command(label='IPAM / DHCP (so dang ky)', command=lambda: self.open_infrastructure('ipam'))
        bar.add_cascade(label='Mang', menu=net)
        infra = tk.Menu(bar, tearoff=False)
        for label, section in (('1. Giam sat thiet bi', 'monitor'), ('2. Canh bao su co', 'alert'), ('3. Sao luu ha tang', 'backup'),
                               ('4. AD / LDAP', 'ad'), ('5. IPAM', 'ipam'), ('6. Bao tri', 'maintenance'), ('7. IT Helpdesk', 'ticket')):
            infra.add_command(label=label, command=lambda tab=section: self.open_infrastructure(tab))
        bar.add_cascade(label='Ha tang CNTT', menu=infra)
        pmc = tk.Menu(bar, tearoff=False)
        for title, sections in (
            ('I. PP - Lap ke hoach san xuat', [('1. Don hang & uu tien','orders'),('2. Can doi cong suat','capacity'),('3/5. Lich san xuat & dieu do','schedule'),('4. Lenh san xuat','work'),('7. Bao tri thiet bi','maintenance')]),
            ('II. MC - Quan ly nguyen vat lieu', [('6. Dinh muc BOM','bom'),('7/8. MRP & canh bao thieu','mrp'),('9. Phieu de nghi mua PR','pr'),('10. Xuat kho vat tu','issue'),('11. Phe lieu & hao hut','scrap'),('13. Cap bo vat tu','kits'),('14. Lo/FIFO-FEFO','lots'),('15. Ton an toan','safety')]),
            ('III. Bao cao & doi soat', [('12. Dashboard tien do','dashboard'),('13. Doi soat ton kho','reconcile'),('14. Xuat bao cao','report'),('22. Nguyen nhan tre','delay'),('24. Doi chieu PO-GR-INV','matching'),('30. Nhat ky','audit')]),
            ('IV. Ky thuat & gia cong', [('16. ECO','eco'),('17. Gia cong ngoai','subcontract')])):
            submenu=tk.Menu(pmc, tearoff=False)
            for label,section in sections:
                submenu.add_command(label=label, command=lambda tab=section:self.open_pmc(tab))
            pmc.add_cascade(label=title,menu=submenu)
        bar.add_cascade(label='PMC',menu=pmc)
        factory_menu = tk.Menu(bar, tearoff=False)
        factory_menu.add_command(label='Smart Factory - Tong quan',command=self.open_factory)
        for number, label, _ in GROUPS:
            factory_menu.add_command(label=label,command=lambda g=number:self.open_factory(g))
        bar.add_cascade(label='Smart Factory',menu=factory_menu)
        helpmenu = tk.Menu(bar, tearoff=False)
        helpmenu.add_command(label='Kiểm tra mạng/máy (không cần mật khẩu mail)', command=self.diagnose)
        if self.auth_store is not None:
            helpmenu.add_command(label='Đổi mật khẩu ứng dụng',command=self.change_application_password)
            if self.session and self.session.allows('users'):
                helpmenu.add_command(label='Duyệt và phân quyền tài khoản',command=self.manage_users)
            helpmenu.add_command(label='Đăng xuất',command=self.logout)
        bar.add_cascade(label='Cong cu', menu=helpmenu)
        self.menubar=bar  # Accessible through the dark-header menu instead of a gray native menubar.

    def show_menu_popup(self):
        if not hasattr(self,'menubar'):return
        try:
            self.menubar.tk_popup(self.root.winfo_pointerx(),self.root.winfo_pointery())
        finally:
            self.menubar.grab_release()

    def toggle_logs(self):
        if self.logs_open:
            self.log_details.pack_forget()
        else:
            self.log_details.pack(fill='x',pady=(5,0))
        self.logs_open=not self.logs_open

    def toggle_sidebar(self):
        compact=int(self.sidebar.cget('width'))>100
        self.sidebar.configure(width=65 if compact else 210)
        for button,title in self.sidebar_items:
            button.configure(text=title[:2] if compact else title)
        self.collapse_button.configure(text='☰' if compact else '☰  Thu gọn menu')

    def _command_permitted(self,name):
        keyword=name.casefold()
        if 'quản lý người dùng' in keyword: return self.session is None or self.session.allows('users')
        if 'mạng' in keyword or 'hạ tầng' in keyword: return self.session is None or self.session.allows('network')
        if 'pmc' in keyword: return self.session is None or self.session.allows('pmc')
        if 'sao lưu' in keyword or 'imap' in keyword or 'hộp thư' in keyword:
            return self.session is None or self.session.allows('mail')
        return True

    def open_factory(self, group=0):
        if not self._permit('factory'): return None
        if self.session is None or self.auth_store is None:
            messagebox.showwarning('Smart Factory', 'Dang nhap tai khoan ung dung truoc khi mo Smart Factory.', parent=self.root)
            return None
        try:
            if self._factory_window and self._factory_window.win.winfo_exists():
                if group:self._factory_window.select_group(group)
                self._factory_window.win.lift()
                return self._factory_window
            self._factory_window=FactoryWindow(self,group)
            return self._factory_window
        except Exception as exc:
            messagebox.showerror('Smart Factory',str(exc),parent=self.root)
            return None

    def _factory_busy(self):
        return bool(self._factory_window and not self._factory_window._closed and self._factory_window._busy)

    def open_mail_quota(self):
        if self._permit('mail'):
            QuotaWindow(self.root)

    def open_pmc(self, section=None):
        if not self._permit('pmc'): return None
        if self._pmc_window and self._pmc_window.win.winfo_exists():
            if section in self._pmc_window.tabs:
                self._pmc_window.notebook.select(self._pmc_window.tabs[section])
            self._pmc_window.win.lift();self._pmc_window.win.focus_set()
            return self._pmc_window
        self._pmc_window=PMCWindow(self.root,section,guard=lambda:self._permit('pmc'))
        return self._pmc_window

    def open_infrastructure(self, section=None):
        if not self._permit('infra'): return None
        if self._infra_window and self._infra_window.win.winfo_exists():
            if section in self._infra_window.tabs:
                self._infra_window.notebook.select(self._infra_window.tabs[section])
            self._infra_window.win.lift();self._infra_window.win.focus_set()
            return self._infra_window
        self._infra_window=InfraWindow(self.root,section,guard=lambda:self._permit('infra'))
        return self._infra_window

    def open_network_manager(self):
        """Separate network dialog; no mailbox login should be needed."""
        if not self._permit('network'): return None
        if self._network_window and self._network_window.winfo_exists():
            self._network_window.lift();self._network_window.focus_set();return self._network_window
        win = tk.Toplevel(self.root)
        self._network_window=win
        win.title('Quan ly mang LAN va VPN - Windows')
        win.geometry('730x660')
        win.minsize(600, 520)
        panel = ttk.Frame(win, padding=14)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='Doi IP co the lam mat ket noi va gian doan sao luu. Can Windows Administrator de doi IP LAN.', wraplength=690, foreground='#9a4300').pack(anchor='w', pady=5)
        status = tk.StringVar(value='Chua doc trang thai mang')
        ttk.Label(panel, textvariable=status, wraplength=670).pack(anchor='w', pady=4)
        view = tk.Text(panel, height=9, wrap='word')
        view.pack(fill='both', expand=True, pady=5)
        view.configure(state='disabled')
        def show(text):
            view.configure(state='normal')
            view.delete('1.0', 'end')
            view.insert('1.0', text)
            view.configure(state='disabled')
        def run_async(task, success):
            if not self._permit('network'):return
            if self.active:
                messagebox.showwarning('Dang sao luu', 'Hay dung sao luu truoc khi doi IP hoac VPN.', parent=win)
                return
            status.set('Dang thuc hien...')
            def worker():
                try:
                    result = task()
                except Exception as exc:
                    error = str(exc)
                    self.events.put(('ui_callback', lambda: (status.set('Thất bại: ' + error), messagebox.showerror('Lỗi mạng', error, parent=win)) if win.winfo_exists() else None))
                else:
                    self.events.put(('ui_callback', lambda: (status.set(success), show(str(result))) if win.winfo_exists() else None))
            threading.Thread(target=worker, daemon=True).start()
        options = ttk.LabelFrame(panel, text='IP noi bo - LAN / Wi-Fi', padding=8)
        options.pack(fill='x', pady=7)
        adapter = tk.StringVar()
        ip = tk.StringVar()
        mask = tk.StringVar(value='255.255.255.0')
        gateway = tk.StringVar()
        dns = tk.StringVar()
        top = ttk.Frame(options)
        top.pack(fill='x')
        ttk.Label(top, text='Card mang:').pack(side='left')
        adapter_box = ttk.Combobox(top, textvariable=adapter, state='readonly', width=36)
        adapter_box.pack(side='left', padx=8)
        def refresh_adapters():
            def action():
                return network.adapter_names()
            def worker():
                try: names = action()
                except Exception as exc:
                    self.events.put(('ui_callback', lambda e=str(exc): status.set(e) if win.winfo_exists() else None))
                    return
                def update():
                    if not win.winfo_exists(): return
                    adapter_box['values'] = names
                    if names: adapter.set(names[0])
                    status.set('Da doc danh sach card mang')
                self.events.put(('ui_callback', lambda: update() if win.winfo_exists() else None))
            threading.Thread(target=worker, daemon=True).start()
        ttk.Button(top, text='Tai danh sach', command=refresh_adapters).pack(side='left')
        for title, variable in [('IP tinh', ip), ('Subnet mask', mask), ('Gateway', gateway), ('DNS (tuy chon)', dns)]:
            line = ttk.Frame(options)
            line.pack(fill='x', pady=2)
            ttk.Label(line, text=title + ':', width=19).pack(side='left')
            ttk.Entry(line, textvariable=variable, width=28).pack(side='left', fill='x', expand=True)
        lan_buttons = ttk.Frame(options)
        lan_buttons.pack(fill='x', pady=6)
        def apply_static():
            if not self._permit('network'):return
            if self.active: return messagebox.showwarning('Dang sao luu', 'Dung sao luu truoc.', parent=win)
            try: values = network.validate_static(ip.get(), mask.get(), gateway.get(), dns.get())
            except network.NetworkError as exc: return messagebox.showerror('Gia tri khong hop le', str(exc), parent=win)
            if messagebox.askyesno('Xac nhan doi IP', 'Thay doi IP tinh cho ' + adapter.get() + '? Ket noi mang co the bi ngat. Tiep tuc?', parent=win):
                run_async(lambda: network.set_static(adapter.get(), *values), 'Da ap dung IP tinh')
        def apply_dhcp():
            if not self._permit('network'):return
            if self.active: return messagebox.showwarning('Dang sao luu', 'Dung sao luu truoc.', parent=win)
            if messagebox.askyesno('Xac nhan DHCP', 'Chuyen ' + adapter.get() + ' ve DHCP (IP va DNS tu dong)?', parent=win):
                run_async(lambda: network.set_dhcp(adapter.get()), 'Da chuyen DHCP')
        ttk.Button(lan_buttons, text='Ap dung IP tinh', command=apply_static).pack(side='left', padx=3)
        ttk.Button(lan_buttons, text='Chuyen ve DHCP', command=apply_dhcp).pack(side='left', padx=3)
        vpn_frame = ttk.LabelFrame(panel, text='IP cong cong - VPN da cau hinh tren Windows', padding=8)
        vpn_frame.pack(fill='x', pady=6)
        ttk.Label(vpn_frame, text='Can tao ket noi VPN trong Windows truoc; VPN co the doi IP cong cong neu luu luong di qua VPN.', wraplength=670).pack(anchor='w')
        vp = tk.StringVar()
        vpn_select = ttk.Combobox(vpn_frame, textvariable=vp, width=37, state='readonly')
        vpn_select.pack(side='left', pady=6)
        def refresh_vpn():
            def worker():
                try: names = network.vpn_profiles()
                except Exception as exc:
                    self.events.put(('ui_callback', lambda e=str(exc): status.set(e) if win.winfo_exists() else None))
                    return
                def update():
                    if not win.winfo_exists(): return
                    vpn_select['values'] = names
                    if names: vp.set(names[0])
                    status.set('Da tai danh sach VPN')
                self.events.put(('ui_callback', lambda: update() if win.winfo_exists() else None))
            threading.Thread(target=worker, daemon=True).start()
        ttk.Button(vpn_frame, text='Tai VPN', command=refresh_vpn).pack(side='left', padx=3)
        def vpn_action(connect):
            if not self._permit('network'):return
            if self.active: return messagebox.showwarning('Dang sao luu', 'Dung sao luu truoc.', parent=win)
            if not vp.get(): return messagebox.showwarning('Chon VPN', 'Chon ket noi VPN da co.', parent=win)
            action = 'ket noi' if connect else 'ngat ket noi'
            if messagebox.askyesno('Xac nhan', 'Ban muon ' + action + ' VPN ' + vp.get() + '?', parent=win):
                func = network.connect_vpn if connect else network.disconnect_vpn
                run_async(lambda: func(vp.get()), 'Hoan tat ' + action + ' VPN. Hay kiem tra IP cong cong.')
        vp_buttons = ttk.Frame(panel)
        vp_buttons.pack(fill='x')
        ttk.Button(vp_buttons, text='Ket noi VPN', command=lambda: vpn_action(True)).pack(side='left', padx=3)
        ttk.Button(vp_buttons, text='Ngat VPN', command=lambda: vpn_action(False)).pack(side='left', padx=3)
        ttk.Button(vp_buttons, text='Xem IP cong cong', command=lambda: run_async(network.public_ip, 'IP cong cong hien tai')).pack(side='left', padx=3)
        ttk.Button(vp_buttons, text='Xem cau hinh LAN', command=lambda: run_async(network.network_snapshot, 'Cau hinh LAN hien tai')).pack(side='left', padx=3)
        refresh_adapters()
        refresh_vpn()

    def show_issues(self):
        if not (self.session is None or self.session.allows('mail') or self.session.allows('reports')):
            self._permit('mail');return
        if self.issue_window is not None and self.issue_window.winfo_exists():
            self.issue_window.lift()
            return
        window = tk.Toplevel(self.root)
        window.title('Danh sach email loi, bo qua, can tai lai')
        window.geometry('1100x520')
        self.issue_window = window
        ttk.Label(window, text='Bang hien thi toi da 3000 dong; CSV luu day du thu da luu / da xac minh / loi; co cot nguoi gui va nguoi nhan.', wraplength=1040).pack(anchor='w', padx=10, pady=8)
        frame = ttk.Frame(window)
        frame.pack(fill='both', expand=True, padx=10)
        columns = ('time', 'account', 'status', 'folder', 'uid', 'sender', 'recipients', 'subject', 'reason', 'path')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        widths = {'time':140, 'account':160, 'status':170, 'folder':110, 'uid':65,
                  'sender':200, 'recipients':240, 'subject':180, 'reason':215, 'path':300}
        for c in columns:
            tree.heading(c, text={'sender':'NGƯỜI GỬI','recipients':'NGƯỜI NHẬN'}.get(c, c.upper()))
            tree.column(c, width=widths[c], stretch=False)
        sy = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        sx = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky='nsew')
        sy.grid(row=0, column=1, sticky='ns')
        sx.grid(row=1, column=0, sticky='ew')
        self.issue_tree = tree
        for item in self.issues:
            self._insert_issue(item)
        buttons = ttk.Frame(window)
        buttons.pack(fill='x', padx=10, pady=8)
        ttk.Button(buttons, text='XUAT CSV DANH SACH', command=self.export_issues).pack(side='left')
        ttk.Button(buttons, text='MO CSV DA SAP XEP GUI / NHAN',
                   command=self.open_sorted_people).pack(side='left', padx=12)
        def close():
            self.issue_tree = None
            self.issue_window = None
            window.destroy()
        window.protocol('WM_DELETE_WINDOW', close)

    def _insert_issue(self, item):
        if self.issue_tree is not None and self.issue_tree.winfo_exists():
            keys = ('time', 'account', 'status', 'folder', 'uid', 'sender', 'recipients', 'subject', 'reason', 'path')
            self.issue_tree.insert('', 'end', values=[item.get(k, '') for k in keys])

    def open_sorted_people(self):
        destination = Path(self.destination.get().strip()) / '_BAO_CAO_LOI'
        path = destination / 'email_sap_xep_nguoi_gui_nguoi_nhan.csv'
        if not path.is_file():
            messagebox.showinfo('Bang sap xep', 'Chua co CSV. Hay sao luu mot luot truoc.')
            return
        try:
            os.startfile(str(path))
        except (OSError, AttributeError) as exc:
            messagebox.showerror('Khong mo duoc', str(exc))

    def export_issues_silent(self):
        if self.issue_path and self.issue_path.is_file():
            self.log('Danh sach email day du (CSV): ' + str(self.issue_path))

    def export_issues(self):
        if self.issue_path is None or not self.issue_path.is_file():
            messagebox.showinfo('Danh sach', 'Chua co bao cao cua luot sao luu.')
            return
        try:
            suggested = 'danh_sach_email_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
            path = filedialog.asksaveasfilename(title='Xuat danh sach email',
                                                defaultextension='.csv', initialfile=suggested,
                                                filetypes=[('CSV (Excel)', '*.csv')])
            if path:
                with open(self.issue_path,'rb') as source, open(path,'xb') as target:
                    shutil.copyfileobj(source,target)
                self.log('DA XUAT TOAN BO DANH SACH: ' + path)
        except FileExistsError:
            messagebox.showwarning('Tệp đã tồn tại','Hãy chọn tên mới để không ghi đè báo cáo cũ.')
        except Exception as exc:
            messagebox.showerror('Loi xuat CSV', str(exc))

    def switch_mode(self):
        # Both modes are contained in one stable placeholder. Do not use
        # pack(before=...) with an already forgotten widget.
        if self.mode.get() == 'admin':
            self.single_frame.pack_forget()
            self.multi_frame.pack(fill='x')
            if not self.accounts_box.get('1.0', 'end').strip() and self.account.get().strip():
                self.accounts_box.insert('1.0', self.account.get().strip() + '\n')
        else:
            self.multi_frame.pack_forget()
            self.single_frame.pack(fill='x')

    def pick(self):
        if not self._permit('mail'): return
        value = filedialog.askdirectory(title='Chon noi luu email')
        if value:
            self.destination.set(value)

    def open_destination(self):
        if not (self.session is None or self.session.allows('mail') or self.session.allows('reports')):
            self._permit('mail');return
        p = Path(self.destination.get().strip())
        if not p.is_dir():
            messagebox.showwarning('Thu muc', 'Chua co thu muc luu tai duong dan nay.')
            return
        os.startfile(str(p))

    def on_close(self):
        if self._factory_busy():
            messagebox.showinfo('Smart Factory','Cho tac vu Smart Factory hoan thanh truoc khi dong.',parent=self.root)
            return
        if not self.active:
            self._cancel_scheduled()
            self.root.destroy()
            return
        if not self.close_requested and messagebox.askyesno(
                'Dang sao luu', 'Dang xu ly email. Dung an toan sau email hien tai va dong?'):
            self.close_requested = True
            self.request_stop()
            self.log('Dang cho cac luong xu ly ket thuc an toan truoc khi dong...')

    def process_events(self):
        for _ in range(300):
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == 'log':
                self.logs.configure(state='normal')
                lower=str(value).lower()
                tag='error' if any(w in lower for w in ('lỗi','loi ','failed','error','that bai')) else ('success' if any(w in lower for w in ('thanh cong','hoan tat','success')) else 'info')
                self.logs.insert('end', f'[{datetime.now():%H:%M:%S}] {value}\n', tag)
                if int(self.logs.index('end-1c').split('.')[0]) > 5000:
                    self.logs.delete('1.0', '1001.0')
                self.logs.see('end')
                self.logs.configure(state='disabled')
            elif kind == 'issue':
                if len(self.issues) < 3000:
                    self.issues.append(value)
                    self._insert_issue(value)
            elif kind == 'export_issues_auto':
                if self.issues:
                    self.export_issues_silent()
            elif kind == 'stat':
                self.stats_line.set(value)
                self.header_status.set('● Đang xử lý')
            elif kind == 'diagnose_done':
                self.diagnosing=False
                self.start_button.configure(state='normal' if self.session is None or self.session.allows('mail') else 'disabled')
                self.inspect_button.configure(state='normal' if self.session is None or self.session.allows('mail') else 'disabled')
                self.header_status.set('● Sẵn sàng')
            elif kind == 'ui_callback':
                if not self._closing:
                    try: value()
                    except tk.TclError: pass
            elif kind == 'done':
                self.active = False
                self.start_button.configure(state='normal')
                self.inspect_button.configure(state='normal')
                self.stop_button.configure(state='disabled')
                self.progress.stop()
                self.header_status.set('● Sẵn sàng')
                if self.close_requested:
                    self.root.destroy()
                    return
        if not self._closing and self.root.winfo_exists():
            self._schedule(100, self.process_events)

    def _start_file_logging(self, destination):
        self._stop_file_logging()
        try:
            folder = Path(destination) / '_NHAT_KY'
            folder.mkdir(parents=True, exist_ok=True)
            logger = logging.getLogger('alibaba_backup_user_' + str(id(self)))
            logger.setLevel(logging.INFO)
            logger.propagate = False
            handler = RotatingFileHandler(folder / 'sao_luu_v16.log',
                                          maxBytes=3 * 1024 * 1024,
                                          backupCount=4, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(handler)
            self._logger, self._log_handler = logger, handler
        except OSError as exc:
            self.events.put(('log', 'CANH BAO: khong ghi duoc nhat ky file: ' + str(exc)))

    def _stop_file_logging(self):
        if self._logger and self._log_handler:
            self._log_handler.flush()
            self._logger.removeHandler(self._log_handler)
            self._log_handler.close()
        self._logger = None
        self._log_handler = None

    def log(self, line):
        line = str(line)
        for secret in tuple(self._secrets):
            if secret:
                line = line.replace(secret, '[REDACTED]')
        if self._logger:
            self._logger.info('%s', line.replace('\r', ' ').replace('\n', ' | '))
        self.events.put(('log', line))

    def request_stop(self):
        if not self.active:
            return
        self.stop.set()
        self.log('Đã yêu cầu dừng an toàn sau email đang xử lý.')

    def inspect(self):
        if self._permit('mail'): self.launch('inspect')

    def start(self):
        if self._permit('mail'): self.launch('backup')

    def export_usage(self):
        if self.session is not None and not (self.session.allows('mail') or self.session.allows('reports')):
            self._permit('mail')
            return
        try:
            output = export_reports(self.destination.get().strip())
            self.log('Da xuat bao cao: ' + str(output))
            messagebox.showinfo('Bao cao', 'Da xuat CSV va XLSX vao:\n' + str(output))
        except Exception as exc:
            messagebox.showerror('Khong xuat duoc', str(exc))

    def diagnose(self):
        """Read-only local DNS/TCP/disk check; NEVER request an IMAP password."""
        if not self._permit('system_check'):
            return
        if self.active or self.diagnosing:
            messagebox.showinfo('Đang bận', 'Hãy đợi tác vụ hiện tại kết thúc.',parent=self.root)
            return
        self.diagnosing=True
        self.start_button.configure(state='disabled')
        self.inspect_button.configure(state='disabled')
        self.header_status.set('● Kiểm tra mạng')
        self.stop.clear()
        # Snapshot all Tkinter state on the UI thread before starting a worker.
        selected_folder=self.destination.get().strip() or str(Path.home())
        self.log('=== KIỂM TRA MẠNG & MÁY TÍNH (KHÔNG CẦN TÀI KHOẢN MAIL) ===')
        threading.Thread(target=self._diagnostic_worker,args=(selected_folder,),
                         daemon=True,name='SystemHealthCheck').start()

    def _diagnostic_worker(self, selected_folder):
        try:
            folder=Path(selected_folder).expanduser()
            path=folder if folder.exists() else Path.home()
            d=shutil.disk_usage(path)
            self.log(f'Ổ đĩa {path}: còn trống {d.free/1073741824:.2f} GB')
            self.log('Đường dẫn sao lưu: '+str(folder))
            for host,port in ((SERVER,PORT),):
                if self.stop.is_set():break
                try:
                    addresses=socket.getaddrinfo(host,port,type=socket.SOCK_STREAM)
                    unique=sorted(set(item[4][0] for item in addresses))
                    self.log(f'DNS {host}: '+', '.join(unique[:5]))
                    with socket.create_connection((host,port),timeout=6):
                        self.log(f'Kết nối TCP {host}:{port}: THÀNH CÔNG (chưa xác thực IMAP)')
                except (OSError,socket.gaierror) as exc:
                    self.log(f'Lỗi kiểm tra mạng {host}:{port}: {type(exc).__name__}')
        except Exception as exc:
            self.log(f'Kiểm tra máy lỗi: {type(exc).__name__}')
        finally:
            self.events.put(('diagnose_done',None))

    @staticmethod
    def valid_mailbox_identifier(mailbox):
        if not isinstance(mailbox,str) or not (3<=len(mailbox)<=254):
            return False
        if mailbox.count('@')!=1 or any(ch.isspace() or ord(ch)<32 for ch in mailbox):
            return False
        local,domain=mailbox.rsplit('@',1)
        return bool(local and domain and not local.startswith('.') and not domain.startswith('.'))

    def launch(self, task):
        if self.active or self.diagnosing:
            return
        dest = self.destination.get().strip()
        if not dest:
            messagebox.showerror('Thieu thu muc', 'Vui long chon thu muc luu.')
            return
        if self.mode.get() == 'employee':
            accounts = [self.account.get().strip()]
        else:
            accounts = list(dict.fromkeys(line.strip() for line in self.accounts_box.get('1.0', 'end').splitlines() if line.strip()))
        if not accounts or any(not self.valid_mailbox_identifier(a) for a in accounts):
            messagebox.showerror('Tai khoan', 'Nhap dia chi email hop le, moi dong mot tai khoan.')
            return
        try:
            speed = float(self.speed_limit.get().strip().replace(',', '.'))
            if not (math.isfinite(speed) and 0 <= speed <= 10000): raise ValueError()
        except ValueError:
            messagebox.showerror('Toc do', 'Nhap MB/s la so tu 0 den 10000.')
            return
        try:
            workers = int(self.worker_count.get())
            if workers not in (1, 2, 3, 5):
                raise ValueError()
        except ValueError:
            messagebox.showerror('So luong', 'Chi ho tro 1, 2, 3 hoac 5 luong.')
            return
        layout = self.folder_layout_choices.get(self.folder_layout.get(), 'year_month_mailbox_contact')
        # Ask interactively for each password before starting; NEVER save to disk.
        credentials = []
        for account in accounts:
            password = simpledialog.askstring('Xác thực IMAP - riêng với tài khoản ứng dụng', 'Nhập mật khẩu EMAIL hoặc app password IMAP cho hộp thư:\n' + account, show='*', parent=self.root)
            if not password:
                self.log('Da huy: chua nhap du mat khau.')
                return
            credentials.append((account, password))
        self.issues.clear()
        self.issue_path = None
        self.issues_preview_count = 0
        if self.issue_tree is not None and self.issue_tree.winfo_exists():
            for node in self.issue_tree.get_children():
                self.issue_tree.delete(node)
        self.stop.clear()
        self._secrets = [password for _, password in credentials]
        self._start_file_logging(dest)
        self.active = True
        self.start_button.configure(state='disabled')
        self.inspect_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        self.progress.start(10)
        self.header_status.set('●  Đang sao lưu / kiểm tra IMAP')
        threading.Thread(target=self.run_jobs, args=(credentials, dest, task, speed, workers, layout), daemon=True).start()

    def run_jobs(self, credentials, dest, task, speed, workers, layout):
        try:
            with exclusive_backup_lock(dest):
                self._run_jobs_locked(credentials, dest, task, speed, workers, layout)
        except Exception as exc:
            self.log('LOI KHOA SAO LUU: ' + str(exc))
        finally:
            credentials.clear()
            self._secrets.clear()
            self._stop_file_logging()
            self.events.put(('done', None))

    def _run_jobs_locked(self, credentials, dest, task, speed, workers, layout):
        try:
            db = UsageDB(dest)
            with IssueJournal(dest) as journal:
                self.issue_path = journal.path
                self._run_accounts(credentials, dest, task, speed, workers, db, journal, layout)
            self.log('CSV ket qua toan bo: ' + str(self.issue_path))
            if journal.sort_error:
                self.log('CANH BAO khong tao duoc CSV sap xep: ' + journal.sort_error)
            elif journal.sorted_path.is_file():
                self.log('CSV sap xep theo nguoi gui / nguoi nhan: ' + str(journal.sorted_path))
        finally:
            pass

    def _run_accounts(self, credentials, dest, task, speed, workers, db, journal, layout):
        try:
            for account, password in credentials:
                if self.stop.is_set():
                    break
                try:
                    if task == 'inspect':
                        kiem_tra.inspect_account(account, password, dest, self.log, self.stop)
                    else:
                        session = db.start(account)
                        start_clock = time.monotonic()
                        live_lock = threading.Lock()
                        live = {'saved':0, 'skipped':0, 'error':0, 'bytes':0}
                        last_ui = [0.0]
                        def on_message(kind, nbytes):
                            with live_lock:
                                live[kind] += 1
                                live['bytes'] += nbytes
                                elapsed = max(time.monotonic()-start_clock, .001)
                                rate = live['bytes'] / elapsed / (1024*1024)
                                line = f'{account}: {live["saved"]} moi | {live["skipped"]} bo qua | {live["bytes"]/1048576:.2f} MB | TB {rate:.2f} MB/s | {workers} luong'
                            with live_lock:
                                now = time.monotonic()
                                emit = now - last_ui[0] >= 0.2
                                if emit:
                                    last_ui[0] = now
                            if emit:
                                self.events.put(('stat', line))
                        try:
                            def on_issue(item):
                                journal.add(item)
                                # Keep GUI memory bounded, journal retains every row.
                                with self._preview_lock:
                                    show = self.issues_preview_count < 3000
                                    if show:
                                        self.issues_preview_count += 1
                                if show:
                                    self.events.put(('issue', item))
                            totals = backup_parallel(account, password, dest, self.log, self.stop, on_message, speed,
                                                     on_issue, workers, layout=layout)
                            status = 'stopped' if self.stop.is_set() else ('partial_errors' if totals['errors'] else 'completed')
                            db.finish(session, totals, status, storage_usage(dest, account))
                        except Exception:
                            db.finish(session, {'saved':live['saved'],'skipped':live['skipped'],'errors':live['error']+1,'bytes':live['bytes']}, 'failed', storage_usage(dest, account))
                            raise
                        elapsed = max(time.monotonic()-start_clock, .001)
                        self.log(f'Thong ke: {totals["bytes"]/1048576:.2f} MB tai | {elapsed:.1f}s | {totals["bytes"]/elapsed/1048576:.2f} MB/s trung binh')
                        self.log(f'XONG {account}: tong UID={totals["expected"]}, luu moi={totals["saved"]}, bo qua da xac minh={totals["skipped"]}, loi={totals["errors"]}')
                        if totals['errors']:
                            self.log('CANH BAO: CON EMAIL LOI. KHONG XEM LA BAN SAO LUU DAY DU.')
                except Exception as exc:
                    self.log(f'LOI {account}: {type(exc).__name__}: {exc}')
                    self.log('Kiem tra ket noi, quyen truy cap va bao cao loi; chi tiet ky thuat duoc an de bao ve thong tin dang nhap.')
            self.log('DA DUNG THEO YEU CAU; CHUA THE XAC NHAN DAY DU.' if self.stop.is_set() else 'KET THUC CAC TAC VU. KIEM TRA CANH BAO VA BAO CAO LOI.')
            self.events.put(('export_issues_auto', None))
        finally:
            pass


def portable_self_test():
    """No network or email access: verify Python runtime and local I/O."""
    import tempfile
    import hashlib
    from issue_journal import IssueJournal
    result = 'ERROR'
    notes = []
    try:
        with tempfile.TemporaryDirectory(prefix='alibaba_v14_') as td:
            path = Path(td) / 'bao cao 中文.txt'
            safe_write(path, b'ALIBABA_V14_OK')
            assert file_digest(path) == hashlib.sha256(b'ALIBABA_V14_OK').hexdigest()
            with IssueJournal(td) as journal:
                journal.add({'uid': '1', 'status': 'SELFTEST'})
            assert journal.path.is_file()
        notes.append('Local file I/O, SHA-256, SQLite/export components imported')
        from auth_local import AuthStore
        with tempfile.TemporaryDirectory(prefix='aoc_auth_') as temp_auth:
            users=AuthStore(Path(temp_auth)/'users.sqlite3')
            users.register('bootstrap_admin','ExampleTestPassword2026!')
            assert users.authenticate('bootstrap_admin','ExampleTestPassword2026!').role=='it_admin'
            assert not users.first_run()
            from factory_core import Factory
            from factory_catalog import FEATURES
            factory=Factory(Path(temp_auth)/'factory.sqlite3',users,users.authenticate('bootstrap_admin','ExampleTestPassword2026!'))
            factory.add_plant('SELFTEST','Isolated self-test')
            factory.save('SELFTEST','materials','RM',{'name':'Self-test material'})
            assert factory.list_records('SELFTEST','materials')['total']==1
            assert len(FEATURES)==100
            assert factory.verify_audit()['ok']
        notes.append('Smart Factory schema, local I/O, audit and 100-feature catalog: OK')
        notes.append('Local authentication, scrypt and SQLite: OK')
        result='OK'
    except Exception as exc:
        notes.append(type(exc).__name__ + ': ' + str(exc))
    try:
        out = Path(tempfile.gettempdir()) / 'AlibabaOperationsCenter_V16_0_14_selftest.txt'
        out.write_text('V16.0.14 SELF TEST: ' + result + '\n' + '\n'.join(notes) + '\n', encoding='utf-8')
    except Exception:
        pass
    return 0 if result == 'OK' else 1


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        sys.exit(portable_self_test())
    window = tk.Tk()
    window.withdraw()
    try:
        store=AuthStore()
    except (OSError,sqlite3.Error) as exc:
        messagebox.showerror('Không thể mở hệ thống tài khoản',str(exc),parent=window)
        sys.exit(1)
    def logged_in(session):
        window.deiconify()
        Application(window,session=session,auth_store=store)
    AuthDialog(window,store,logged_in)
    window.mainloop()
