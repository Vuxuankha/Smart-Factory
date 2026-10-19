"""PMC workstation: PP, MC, reports; operations stay local and reviewable."""
import json
import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from industrial_theme import apply_theme, BG, WHITE, MUTED
from pmc_manager import PMC, today
from pmc_advanced import PMCAdvanced

class PMCWindow:
    def __init__(self, root, section=None, guard=None):
        self.win=tk.Toplevel(root);self.win.configure(bg=BG);self.win.title('PMC | Kế hoạch sản xuất & quản lý vật tư');self.win.geometry('1180x790');self.win.minsize(900,640)
        self.guard=guard or (lambda:True)
        db=Path(os.environ.get('LOCALAPPDATA') or Path.home()/'.local'/'share')/'AlibabaMailIT'/'pmc.sqlite3'
        self.core=PMC(db)
        self.advanced=PMCAdvanced(db)
        ttk.Label(self.win,text='PMC – dữ liệu cục bộ, không tự ghi ERP. Lệnh sản xuất và PR chỉ ở trạng thái DRAFT.',wraplength=960).pack(anchor='w',padx=12,pady=7)
        notebook=ttk.Notebook(self.win);notebook.pack(fill='both',expand=True,padx=9)
        self.tabs={}
        groups=[('orders','PP 1. Đơn hàng'),('capacity','PP 2. Công suất'),('schedule','PP 3/5. Lịch & điều độ'),('work','PP 4. Lệnh SX'),('bom','MC 6. BOM'),('mrp','MC 7/8. MRP & thiếu'),('pr','MC 9. Mua hàng'),('issue','MC 10. Xuất kho'),('scrap','MC 11. Phế liệu'),('dashboard','BC 12. Tiến độ'),('reconcile','BC 13. Đối soát'),('report','BC 14. Báo cáo'),('lots','MC 14. Lô/FIFO'),('safety','MC 15. Tồn an toàn'),('kits','MC 13. Kitting'),('maintenance','PP 7. Bảo trì'),('subcontract','KT 17. Gia công'),('matching','BC 24. 3-Way'),('delay','BC 22. Trễ hạn'),('eco','KT 16. ECO'),('audit','BC 30. Nhật ký')]
        for code,name in groups:
            f=ttk.Frame(notebook,padding=12);notebook.add(f,text=name);self.tabs[code]=f
        # Quick navigation works even when ttk.Notebook tabs do not fit the screen.
        nav=ttk.Frame(self.win);nav.pack(fill='x',padx=10,pady=5)
        ttk.Label(nav,text='Chọn chức năng:').pack(side='left')
        self.section_names=[name for _,name in groups]
        self.section_choice=tk.StringVar()
        picker=ttk.Combobox(nav,textvariable=self.section_choice,values=self.section_names,state='readonly',width=48)
        picker.pack(side='left',padx=8,fill='x',expand=True)
        self.notebook=notebook
        def select_section(event=None):
            idx=picker.current()
            if idx>=0:notebook.select(idx)
        picker.bind('<<ComboboxSelected>>',select_section)
        def update_picker(event=None):
            self.section_choice.set(self.section_names[notebook.index(notebook.select())])
        notebook.bind('<<NotebookTabChanged>>',update_picker)
        self.out=tk.Text(self.win,height=9,wrap='word',font=('Consolas',10),bg='#102033',fg='#D7E6F5',relief='flat',padx=12,pady=10);self.out.pack(fill='x',padx=10,pady=8)
        self.build()
        if section in self.tabs:notebook.select(self.tabs[section])
        self.section_choice.set(self.section_names[notebook.index(notebook.select())])
    def field(self,f,label,default=''):
        r=ttk.Frame(f);r.pack(fill='x',pady=4)
        ttk.Label(r,text=label,width=26).pack(side='left')
        v=tk.StringVar(value=default);ttk.Entry(r,textvariable=v,width=45).pack(side='left',fill='x',expand=True)
        return v
    def show(self,value):
        if not self.win.winfo_exists():return
        data=json.dumps(value,ensure_ascii=False,indent=2,default=str) if not isinstance(value,str) else value
        self.out.delete('1.0','end');self.out.insert('end',data[:25000]);self.out.see('1.0')
    def button(self,f,label,fn,confirm=None):
        def click():
            if confirm and not messagebox.askyesno('Xác nhận',confirm,parent=self.win):
                return
            # Tkinter StringVar.get() and widgets must only be accessed from
            # the GUI thread. Execute the local database operation here.
            self.button_action(fn)
        ttk.Button(f,text=label,command=click).pack(anchor='w',pady=5)
    def note(self,f,text):ttk.Label(f,text=text,wraplength=880).pack(anchor='w',pady=6)
    def import_button(self,f,kind):
        def choose():
            path=filedialog.askopenfilename(parent=self.win,filetypes=[('CSV','*.csv')]);
            if path:self.button_action(lambda:f'Đã nhập {self.core.import_csv(path,kind)} dòng')
        ttk.Button(f,text='Nhập CSV '+kind,command=choose).pack(anchor='w',pady=4)
    def button_action(self,fn):
        if not self.guard():return
        try:self.show(fn())
        except Exception as e:self.show(f'LỖI: {type(e).__name__}: {e}')
    def build(self):
        f=self.tabs['orders'];self.note(f,'Ưu tiên 1–5 (5 là cao nhất). Ngày theo YYYY-MM-DD. Có thể nhập đơn qua CSV.')
        oid=self.field(f,'Mã SO');product=self.field(f,'Mã thành phẩm');q=self.field(f,'Số lượng');due=self.field(f,'Hạn giao',today());prio=self.field(f,'Ưu tiên','1');customer=self.field(f,'Khách hàng')
        self.button(f,'Thêm đơn hàng',lambda:self.core.order(oid.get(),product.get(),q.get(),due.get(),prio.get(),customer.get()) or 'Đã lưu')
        self.button(f,'Danh sách ưu tiên đơn hàng',self.core.orders);self.import_button(f,'orders')
        f=self.tabs['capacity'];name=self.field(f,'Tên máy / chuyền');rate=self.field(f,'Năng lực sản phẩm/ngày')
        self.button(f,'Lưu năng lực',lambda:self.core.center(name.get(),rate.get()) or 'Đã lưu');self.button(f,'Danh sách năng lực',lambda:self.core.query('SELECT * FROM centers'));self.import_button(f,'centers')
        f=self.tabs['schedule'];start=self.field(f,'Ngày bắt đầu',today());self.note(f,'Lịch tham chiếu: xếp theo hạn giao, ưu tiên, 1 đơn/1 chuyền; chưa tính ca, khuôn, chuyển đổi mã hay lịch nghỉ.')
        self.button(f,'Xem trước Gantt dạng bảng',lambda:self.core.plan(start.get()))
        self.button(f,'Lưu lịch vào cơ sở dữ liệu',lambda:self.core.plan(start.get(),True),'Ghi đè lịch PMC hiện có bằng phương án mới?')
        self.button(f,'Xem lịch đã lưu',lambda:self.core.query('SELECT * FROM schedule ORDER BY start'))
        f=self.tabs['work'];self.note(f,'Lệnh sản xuất ở trạng thái nháp; QR payload là dữ liệu JSON để phần mềm in mã xử lý.')
        self.button(f,'Xem trước lệnh sản xuất',self.core.work_orders)
        self.button(f,'Tạo các lệnh DRAFT',lambda:self.core.work_orders(True),'Tạo bản nháp lệnh sản xuất cho lịch hiện tại?')
        self.button(f,'Xem các lệnh DRAFT',lambda:self.core.query('SELECT * FROM jobs'))
        f=self.tabs['bom'];p=self.field(f,'Mã thành phẩm');m=self.field(f,'Mã vật tư');per=self.field(f,'Định mức/1 sản phẩm')
        self.button(f,'Lưu BOM',lambda:self.core.set_bom(p.get(),m.get(),per.get()) or 'Đã lưu')
        self.button(f,'Bóc tách nhu cầu BOM',self.core.demand);self.button(f,'Thành phẩm thiếu BOM',self.core.missing_bom);self.import_button(f,'bom')
        f=self.tabs['mrp'];m=self.field(f,'Mã vật tư');on=self.field(f,'Tồn thực tế','0');incoming=self.field(f,'Hàng đang về','0')
        self.button(f,'Cập nhật tồn và PO đang về',lambda:self.core.set_stock(m.get(),on.get(),incoming.get()) or 'Đã lưu')
        self.button(f,'Chạy MRP ròng',self.core.mrp);self.button(f,'Cảnh báo vật tư thiếu',self.core.shortages);self.import_button(f,'stock')
        f=self.tabs['pr'];self.note(f,'Chỉ tạo yêu cầu mua nháp (DRAFT). Không gửi nhà cung cấp, không phê duyệt và không ghi ERP.')
        self.button(f,'Xem PR đề xuất',self.core.shortages)
        self.button(f,'Tạo / làm mới PR nháp',self.core.create_pr,'Làm mới các PR ở trạng thái DRAFT theo MRP?')
        self.button(f,'Xem PR',lambda:self.core.query('SELECT * FROM requests ORDER BY id DESC'))
        f=self.tabs['issue'];oid=self.field(f,'Mã đơn');m=self.field(f,'Mã vật tư');q=self.field(f,'Lượng xuất')
        self.note(f,'Chỉ trừ tồn trong cơ sở dữ liệu PMC cục bộ; không tác động kho/ERP thực.')
        self.button(f,'Xác nhận xuất vật tư',lambda:self.core.issue(oid.get(),m.get(),q.get()) or 'Đã trừ kho PMC','Xác nhận ghi nhận xuất kho trong hệ thống PMC cục bộ?')
        self.button(f,'Lịch sử xuất kho',lambda:self.core.query('SELECT * FROM movements ORDER BY id DESC LIMIT 200'))
        f=self.tabs['scrap'];oid=self.field(f,'Mã đơn');m=self.field(f,'Mã vật tư');actual=self.field(f,'Lượng tiêu hao thực tế');good=self.field(f,'Số thành phẩm tốt')
        self.button(f,'Ghi nhận hao hụt',lambda:self.core.scrap(oid.get(),m.get(),actual.get(),good.get()) or 'Đã ghi')
        self.button(f,'Tính chênh lệch so với BOM',self.core.scrap_report)
        f=self.tabs['dashboard'];oid=self.field(f,'Mã đơn hoàn thành');q=self.field(f,'Số thành phẩm tốt')
        self.button(f,'Ghi nhận sản lượng',lambda:self.core.produce(oid.get(),q.get()) or 'Đã ghi sản lượng','Cộng sản lượng thực hiện vào mã đơn này?')
        self.button(f,'Làm mới KPI tiến độ',self.core.dashboard)
        f=self.tabs['reconcile'];m=self.field(f,'Mã vật tư');book=self.field(f,'Tồn trên hệ thống');actual=self.field(f,'Số kiểm kê thực tế');incoming=self.field(f,'Hàng PO đang về','0')
        self.button(f,'Ghi nhận số kiểm kê',lambda:self.core.set_stock(m.get(),book.get(),incoming.get(),actual.get()) or 'Đã ghi')
        self.button(f,'Xem danh sách chênh lệch',self.core.reconcile)
        f=self.tabs['report'];self.note(f,'Xuất báo cáo CSV UTF-8 có BOM (Excel mở đúng tiếng Việt). Gửi theo lịch cần SMTP được cấu hình riêng.')
        kind=self.field(f,'Loại báo cáo','mrp')
        self.note(f,'Các loại: orders, mrp, shortages, reconcile, scrap, schedule')
        def export():
            path=filedialog.asksaveasfilename(parent=self.win,defaultextension='.csv',filetypes=[('CSV','*.csv')]);
            if path:self.button_action(lambda:f'Đã xuất {self.core.report_csv(path,kind.get())} dòng tới {path}')
        ttk.Button(f,text='Xuất CSV',command=export).pack(anchor='w',pady=5)
        self.button(f,'Tổng hợp tình hình',self.core.dashboard)
        f=self.tabs['lots'];a=self.field(f,'Mã lô');b=self.field(f,'Mã vật tư');c=self.field(f,'Số lượng');d=self.field(f,'Ngày nhập',today());e=self.field(f,'Hạn dùng (nếu có)')
        self.button(f,'Thêm lô',lambda:self.advanced.lot(a.get(),b.get(),c.get(),d.get(),e.get()) or 'Đã thêm lô')
        x=self.field(f,'Số lượng cần lấy');self.button(f,'Gợi ý xuất lô FEFO/FIFO',lambda:self.advanced.picking_suggestion(b.get(),x.get()))
        self.button(f,'Cảnh báo hết hạn trong 30 ngày',self.advanced.expiring)
        f=self.tabs['safety'];avg=self.field(f,'Nhu cầu trung bình/ngày');lead=self.field(f,'Lead time (ngày)');std=self.field(f,'Độ lệch chuẩn nhu cầu/ngày','0')
        self.button(f,'Tính tồn kho an toàn',lambda:self.advanced.safety_stock(avg.get(),lead.get(),std.get()))
        f=self.tabs['kits'];oid=self.field(f,'Mã đơn');mat=self.field(f,'Mã vật tư');qty=self.field(f,'Lượng phân bổ')
        self.button(f,'Phân bổ bộ vật tư',lambda:self.advanced.allocate_kit(oid.get(),mat.get(),qty.get()) or 'Đã ghi phân bổ','Lưu phân bổ vật tư cục bộ?')
        self.button(f,'Danh sách kitting',lambda:self.core.query('SELECT * FROM pmc_kits'))
        f=self.tabs['maintenance'];c=self.field(f,'Tên chuyền/máy');st=self.field(f,'Ngày bắt đầu',today());en=self.field(f,'Ngày kết thúc',today());r=self.field(f,'Lý do')
        self.button(f,'Đăng ký lịch bảo trì',lambda:self.advanced.maintenance(c.get(),st.get(),en.get(),r.get()) or 'Đã lưu')
        self.button(f,'Kiểm tra xung đột lịch đã lưu',self.advanced.maintenance_conflicts)
        f=self.tabs['subcontract'];i=self.field(f,'Mã gia công');oid=self.field(f,'Mã đơn');v=self.field(f,'Nhà gia công');q=self.field(f,'Số lượng');d=self.field(f,'Hạn giao',today())
        self.button(f,'Lưu gia công ngoài',lambda:self.advanced.subcontract(i.get(),oid.get(),v.get(),q.get(),d.get()) or 'Đã lưu')
        self.button(f,'Xem gia công quá hạn',self.advanced.late_subcontracts)
        f=self.tabs['matching'];kind=self.field(f,'Loại chứng từ (PO/GR/INV)','PO');i=self.field(f,'Mã chứng từ');po=self.field(f,'Mã PO (cho GR/INV)');mat=self.field(f,'Mã vật tư (cho PO)');q=self.field(f,'Số lượng');cost=self.field(f,'Đơn giá (cho PO/INV)','0')
        def save_doc():
            typ=kind.get().strip().upper()
            if typ=='PO':self.advanced.record_po(i.get(),mat.get(),q.get(),cost.get())
            elif typ=='GR':self.advanced.record_receipt(i.get(),po.get(),q.get())
            elif typ=='INV':self.advanced.record_invoice(i.get(),po.get(),q.get(),cost.get())
            else:raise ValueError('Chỉ nhập PO, GR hoặc INV')
            return 'Đã ghi nhận chứng từ PMC (không cập nhật ERP)'
        self.button(f,'Lưu chứng từ',save_doc,'Xác nhận thêm chứng từ cục bộ?')
        self.button(f,'Đối chiếu PO - GR - INV',self.advanced.matching)
        f=self.tabs['delay'];oid=self.field(f,'Mã đơn');cause=self.field(f,'Nguyên nhân MATERIAL/MACHINE/QUALITY/STAFF/OTHER','MATERIAL');note=self.field(f,'Ghi chú')
        self.button(f,'Ghi nhận nguyên nhân',lambda:self.advanced.delay(oid.get(),cause.get(),note.get()) or 'Đã ghi')
        self.button(f,'Thống kê nguyên nhân trễ',self.advanced.delay_summary)
        f=self.tabs['eco'];p=self.field(f,'Mã thành phẩm');old=self.field(f,'BOM phiên bản cũ');new=self.field(f,'BOM phiên bản mới');note=self.field(f,'Mô tả thay đổi')
        self.note(f,'Chỉ đánh dấu các đơn chịu ảnh hưởng để xét duyệt thủ công. Không dừng chuyền hoặc sửa BOM.')
        self.button(f,'Đánh giá ảnh hưởng ECO',lambda:self.advanced.eco(p.get(),old.get(),new.get(),note.get()),'Ghi nhận ECO để rà soát?')
        f=self.tabs['audit'];self.note(f,'Nhật ký các tác vụ mới trong mô-đun PMC nâng cao. Chưa phải nhật ký bất biến hay định danh người dùng doanh nghiệp.')
        self.button(f,'Xem nhật ký gần nhất',self.advanced.audit_log)

