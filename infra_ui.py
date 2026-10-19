"""Tkinter workbench for opt-in, locally scoped infrastructure operations."""
import tkinter as tk
import threading
import queue
import csv
from pathlib import Path
import lan_discovery as discovery
from tkinter import ttk, filedialog, messagebox
from industrial_theme import apply_theme, BG, WHITE, MUTED
import infra_manager as core

class InfraWindow:
    def __init__(self,parent,section=None,guard=None):
        self.win=tk.Toplevel(parent);self.win.configure(bg=BG); self.win.title('IT Infrastructure · Operations Center');self.win.geometry('1160x790');self.win.minsize(920,640)
        self.store=core.Store()
        self.guard=guard or (lambda:True)
        self.scan_events=queue.Queue()
        self.scan_cancel=threading.Event()
        self.scan_running=False
        intro=ttk.Label(self.win,text='IT Infrastructure | Các thao tác thay đổi cần xác nhận và quyền phù hợp. Không tự vận hành thiết bị doanh nghiệp.',wraplength=850)
        intro.pack(anchor='w',padx=12,pady=8)
        tabs=ttk.Notebook(self.win);self.notebook=tabs;tabs.pack(fill='both',expand=True,padx=10,pady=6)
        self.output=tk.Text(self.win,height=7,wrap='word',font=('Consolas',10),bg='#102033',fg='#D7E6F5',relief='flat',padx=12,pady=10);self.output.pack(fill='x',padx=10,pady=5)
        self.tabs={}
        for key,name in [('monitor','1. Giám sát'),('alert','2. Cảnh báo'),('backup','3. Sao lưu'),('ad','4. AD/LDAP'),('ipam','5. IPAM/DHCP'),('maintenance','6. Bảo trì'),('ticket','7. Helpdesk')]:
            f=ttk.Frame(tabs,padding=14);tabs.add(f,text=name);self.tabs[key]=f
        self.build_monitor();self.build_alert();self.build_backup();self.build_ad();self.build_ipam();self.build_maintenance();self.build_ticket()
        if section in self.tabs: tabs.select(self.tabs[section])
        self._scan_after = None
        self.win.bind('<Destroy>',self._on_destroy,add='+')
        self._scan_after = self.win.after(100, self.drain_scan_events)

    def _on_destroy(self,event):
        if event.widget is self.win:
            self.scan_cancel.set()
            if self._scan_after is not None:
                try:self.win.after_cancel(self._scan_after)
                except tk.TclError:pass
                self._scan_after=None

    def say(self,value):
        if not self.win.winfo_exists():return
        self.output.insert('end',str(value)+'\n')
        # Avoid unbounded Text widget growth during prolonged monitoring.
        if int(self.output.index('end-1c').split('.')[0])>2500:
            self.output.delete('1.0','1000.0')
        self.output.see('end')
    def run(self,fn,confirm=None):
        if not self.guard():return
        if confirm and not messagebox.askyesno('Xác nhận thao tác',confirm,parent=self.win):
            return
        try:
            self.say(fn())
        except Exception as exc:
            self.say(f'LỖI: {type(exc).__name__}: {exc}')
    def field(self,parent,label,default='',width=35):
        row=ttk.Frame(parent);row.pack(fill='x',pady=3)
        ttk.Label(row,text=label,width=24).pack(side='left')
        var=tk.StringVar(value=default);ttk.Entry(row,textvariable=var,width=width).pack(side='left',fill='x',expand=True)
        return var
    def button(self,parent,label,action,confirm=None):
        ttk.Button(parent,text=label,command=lambda:self.run(action,confirm)).pack(anchor='w',pady=6)
    def drain_scan_events(self):
        try:
            while True:
                event, value = self.scan_events.get_nowait()
                if event == 'progress':
                    done, total, count = value
                    self.scan_status.set(f'Đã kiểm tra {done}/{total} IP | Tìm thấy {count} thiết bị phản hồi')
                elif event == 'done':
                    self.scan_running=False
                    self.scan_results=value
                    self.scan_status.set(('Đã hủy lượt quét.' if self.scan_cancel.is_set() else f'Hoàn tất: {len(value)} địa chỉ phản hồi. Thiết bị chặn ping/TCP có thể không xuất hiện.'))
                    for row in self.scan_tree.get_children(): self.scan_tree.delete(row)
                    for device in value:
                        via=('Ping' if device['ping'] else 'TCP')
                        self.scan_tree.insert('', 'end', values=(device['ip'], device['mac'] or 'Chưa xác định',
                            ', '.join(map(str,device['open_ports'])) or '-', via))
                    self.say(self.scan_status.get())
                elif event == 'error':
                    self.scan_running=False
                    self.scan_status.set('Quét lỗi: '+str(value))
                    self.say(self.scan_status.get())
        except queue.Empty:
            pass
        try:
            if self.win.winfo_exists():
                self._scan_after=self.win.after(100, self.drain_scan_events)
        except tk.TclError:
            pass

    def start_lan_scan(self):
        if not self.guard():return
        if self.scan_running:
            self.say('Một lượt quét đang chạy.'); return
        try:
            cidr=str(self.scan_cidr.get()).strip()
            discovery.validate_network(cidr)
        except (ValueError, TypeError) as exc:
            messagebox.showerror('Dải mạng không hợp lệ',str(exc),parent=self.win);return
        if not messagebox.askyesno('Xác nhận quét LAN',
                f'Chỉ quét {cidr} trên mạng nội bộ do bạn quản lý/được phép kiểm tra.\n'
                'Thời gian có thể từ vài giây đến hơn một phút. Tiếp tục?',parent=self.win):
            return
        self.scan_cancel.clear()
        self.scan_running=True
        self.scan_results=[]
        self.scan_status.set('Đang quét...')
        def worker():
            try:
                rows=discovery.scan_network(cidr, cancel=self.scan_cancel,
                      progress=lambda d,t,c:self.scan_events.put(('progress',(d,t,c))))
                self.scan_events.put(('done',rows))
            except Exception as exc:
                self.scan_events.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True,name='LANDiscovery').start()

    def export_scan_csv(self):
        if not self.guard():return
        data=getattr(self,'scan_results',[])
        if not data:
            self.say('Chưa có kết quả quét để xuất.');return
        dest=filedialog.asksaveasfilename(parent=self.win,defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if dest:
            try:
                fh=open(dest,'x',newline='',encoding='utf-8-sig')
            except FileExistsError:
                self.say('Tệp báo cáo đã tồn tại, hãy chọn tên khác.');return
            with fh:
                writer=csv.DictWriter(fh,fieldnames=['ip','mac','ping','open_ports','latency_ms'])
                writer.writeheader()
                for row in data:
                    writer.writerow({key: (','.join(map(str,row['open_ports'])) if key == 'open_ports' else row.get(key,'')) for key in writer.fieldnames})
            self.say(f'Đã xuất {len(data)} thiết bị vào {Path(dest).name}')

    def build_monitor(self):
        f=self.tabs['monitor']
        ttk.Label(f,text='TÌM THIẾT BỊ TRONG LAN • Ping + các cổng TCP phổ biến. Chỉ quét dải mạng được phép.',wraplength=800).pack(anchor='w',pady=(0,8))
        self.scan_cidr=self.field(f,'Dải LAN (CIDR)',discovery.suggest_local_subnet())
        row=ttk.Frame(f);row.pack(fill='x',pady=3)
        ttk.Button(row,text='🔍 Quét thiết bị LAN',command=self.start_lan_scan).pack(side='left',padx=(0,8))
        ttk.Button(row,text='Dừng quét',command=self.scan_cancel.set).pack(side='left',padx=(0,8))
        ttk.Button(row,text='Xuất CSV',command=self.export_scan_csv).pack(side='left')
        self.scan_status=tk.StringVar(value='Chưa quét. Kiểm tra dải IP và bấm Quét thiết bị LAN.')
        ttk.Label(f,textvariable=self.scan_status,wraplength=830).pack(anchor='w',pady=5)
        frame=ttk.Frame(f);frame.pack(fill='both',expand=True,pady=4)
        self.scan_tree=ttk.Treeview(frame,columns=('ip','mac','ports','method'),show='headings',height=9)
        for key,label,width in [('ip','Địa chỉ IP',140),('mac','MAC (nếu có)',165),('ports','Cổng phản hồi',220),('method','Phát hiện bởi',120)]:
            self.scan_tree.heading(key,text=label);self.scan_tree.column(key,width=width,anchor='w')
        self.scan_tree.pack(side='left',fill='both',expand=True)
        scan_scroll=ttk.Scrollbar(frame,orient='vertical',command=self.scan_tree.yview)
        scan_scroll.pack(side='right',fill='y')
        self.scan_tree.configure(yscrollcommand=scan_scroll.set)
        ttk.Separator(f).pack(fill='x',pady=8)
        ttk.Label(f,text='GIÁM SÁT THIẾT BỊ ĐÃ LƯU (TCP): thêm IP cụ thể để theo dõi; cổng đóng không có nghĩa thiết bị mất mạng.').pack(anchor='w')
        name=self.field(f,'Tên thiết bị');host=self.field(f,'IP/hostname');kind=self.field(f,'Loại (switch/NAS/camera)');port=self.field(f,'Cổng TCP','443');site=self.field(f,'Vị trí')
        self.button(f,'Thêm thiết bị vào sổ',lambda:self.store.add_asset(name.get(),host.get(),kind.get(),int(port.get()),site.get()))
        self.button(f,'Kiểm tra thiết bị đã lưu (TCP)',lambda:'\n'.join(f"{a['name']} [{a['host']}]: {a['status']} / cổng {a['port']}" for a in self.store.check_assets()) or 'Chưa lưu thiết bị')
        self.button(f,'Xem danh sách đã lưu',lambda:'\n'.join(f"{a['name']} | {a['host']}:{a['port']} | {a['kind']}" for a in self.store.assets()) or 'Chưa có thiết bị')
    def build_alert(self):
        f=self.tabs['alert'];ttk.Label(f,text='Cảnh báo thử nghiệm: hiển thị thiết bị DOWN; chưa tự động gửi Telegram/Zalo/Email do chưa có API và quyền truy cập.',wraplength=820).pack(anchor='w')
        self.button(f,'Kiểm tra và tổng hợp cảnh báo',lambda:'\n'.join(f"CẢNH BÁO: {a['name']} ({a['host']}) không kết nối" for a in self.store.check_assets() if a['status']=='DOWN') or 'Không có thiết bị DOWN được ghi nhận')
        ttk.Label(f,text='Giám sát định kỳ và thông báo đa kênh cần được cấu hình riêng; không bật ngầm khi mở ứng dụng.',wraplength=820).pack(anchor='w',pady=10)
    def build_backup(self):
        f=self.tabs['backup'];ttk.Label(f,text='Sao lưu thư mục cục bộ, tạo SHA-256 manifest và kiểm tra. Chưa có tích hợp ERP/SQL Server/NAS/Cloud trực tiếp.',wraplength=830).pack(anchor='w')
        src=self.field(f,'Thư mục nguồn');dest=self.field(f,'Thư mục đích mới')
        self.button(f,'Sao lưu ngay',lambda:f"Sao lưu {core.backup_folder(src.get(),dest.get())} tệp thành công",'Tạo một bản sao lưu mới? Đích chưa được tồn tại và thao tác có thể tốn nhiều dung lượng.')
        check=self.field(f,'Thư mục bản sao cần kiểm');self.button(f,'Xác minh toàn vẹn SHA-256',lambda:(lambda count,errs:f'{count} tệp, {len(errs)} sai lệch: {errs[:10]}')(*core.verify_backup(check.get())))
    def build_ad(self):
        f=self.tabs['ad'];ttk.Label(f,text='Chỉ tạo bản nháp PowerShell -WhatIf, KHÔNG chạy lệnh AD hoặc tự thay đổi tài khoản.',wraplength=820).pack(anchor='w')
        user=self.field(f,'Tài khoản AD');group=self.field(f,'Nhóm AD')
        self.button(f,'Sinh lệnh cấp quyền (để duyệt)',lambda:core.draft_access_script(user.get(),group.get(),True))
        self.button(f,'Sinh lệnh thu hồi quyền (để duyệt)',lambda:core.draft_access_script(user.get(),group.get(),False))
    def build_ipam(self):
        f=self.tabs['ipam'];ttk.Label(f,text='Sổ đăng ký IP nội bộ, tránh cấp trùng trong cơ sở dữ liệu ứng dụng; KHÔNG thay đổi DHCP server hoặc QoS.',wraplength=820).pack(anchor='w')
        cidr=self.field(f,'Dải mạng IPv4 CIDR','192.168.1.0/24');owner=self.field(f,'Tên thiết bị/chủ sở hữu');reserved=self.field(f,'IP cần bỏ qua (dấu phẩy)')
        self.button(f,'Giữ chỗ IP khả dụng',lambda:self.store.allocate_ip(cidr.get(),owner.get(),reserved=[x.strip() for x in reserved.get().split(',') if x.strip()]),'Đăng ký IP mới vào sổ IPAM? Không tác động máy chủ DHCP.')
        self.button(f,'Danh sách IP đã giữ',lambda:'\n'.join(f"{r['address']} - {r['owner']}" for r in self.store.leases()) or 'Chưa cấp IP')
    def build_maintenance(self):
        f=self.tabs['maintenance'];ttk.Label(f,text='Kiểm tra trạng thái Windows Update và liệt kê file cũ. Không cài vá lỗi hoặc xóa file tự động.',wraplength=820).pack(anchor='w')
        self.button(f,'Xem Windows Update service',core.windows_update_status)
        folder=self.field(f,'Thư mục log cần xem');days=self.field(f,'Cũ hơn số ngày','30')
        self.button(f,'Xem trước tệp cũ (không xóa)',lambda:(lambda items:f'{len(items)} tệp (tối đa 1000), {sum(i[1] for i in items)} bytes\n'+'\n'.join(i[0] for i in items[:30]))(core.old_files_preview(folder.get(),int(days.get()))))
    def build_ticket(self):
        f=self.tabs['ticket'];ttk.Label(f,text='Helpdesk lưu cục bộ bằng SQLite; chưa có cổng tiếp nhận trực tuyến từ phòng ban.',wraplength=820).pack(anchor='w')
        title=self.field(f,'Tiêu đề yêu cầu');category=self.field(f,'Bộ phận/loại sự cố');requester=self.field(f,'Người yêu cầu');assignee=self.field(f,'Kỹ thuật viên')
        row=ttk.Frame(f);row.pack(anchor='w',pady=5);ttk.Label(row,text='Ưu tiên:',width=24).pack(side='left')
        priority=tk.StringVar(value='Normal');ttk.Combobox(row,textvariable=priority,values=('Low','Normal','High','Critical'),state='readonly').pack(side='left')
        self.button(f,'Tạo phiếu mới',lambda:f"Ticket #{self.store.add_ticket(title.get(),category.get(),priority.get(),requester.get(),assignee.get())}")
        self.button(f,'Xem 500 phiếu gần nhất',lambda:'\n'.join(f"#{r['id']} [{r['priority']}] {r['title']} - {r['status']} ({r['assignee']})" for r in self.store.tickets()) or 'Chưa có ticket')
        tid=self.field(f,'ID phiếu cập nhật');row=ttk.Frame(f);row.pack(anchor='w');ttk.Label(row,text='Trạng thái:',width=24).pack(side='left');status=tk.StringVar(value='In Progress');ttk.Combobox(row,textvariable=status,values=('Open','In Progress','Resolved','Closed'),state='readonly').pack(side='left')
        self.button(f,'Cập nhật phiếu',lambda:self.store.set_ticket(tid.get(),status.get(),assignee.get()))
        def export():
            file=filedialog.asksaveasfilename(parent=self.win,defaultextension='.csv',filetypes=[('CSV','*.csv')]);
            if file:self.run(lambda:f'Đã xuất {self.store.export_tickets(file)} phiếu')
        ttk.Button(f,text='Xuất CSV',command=export).pack(anchor='w',pady=5)
