"""Source-aligned factory workspace. Only implemented actions are executable.
All worker results return through a queue polled on the Tk thread.
"""
from __future__ import annotations
import csv
import json
import queue
import threading
import tkinter as tk
from datetime import datetime, date
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from dashboard_widgets import PALETTE as P, action_button, ui_label, MetricCard, badge
from factory_schema import ENTITIES, GROUP_ENTITIES, F
from factory_catalog import FEATURES, GROUPS
from factory_core import Factory, FactoryError, AccessDenied, cost_estimate, what_if, roi_estimate

STATUS_LABELS={'local_scope':'C\u1ee5c b\u1ed9 - xem ph\u1ea1m vi','partial':'M\u1ed9t ph\u1ea7n / ch\u01b0a t\u1ef1 \u0111\u1ed9ng','integration_required':'Ch\u01b0a t\u00edch h\u1ee3p'}
SHORT_GROUPS=['\u0110a nh\u00e0 m\u00e1y & cung \u1ee9ng','IoT & c\u1ea3m bi\u1ebfn','WMS - Kho v\u1eadn','MES / PMC - S\u1ea3n xu\u1ea5t','B\u1ea3o m\u1eadt & sao l\u01b0u','Executive & s\u1ef1 c\u1ed1','Thi\u1ebft b\u1ecb IT / OT','Ch\u1ea5t l\u01b0\u1ee3ng & truy xu\u1ea5t','Nh\u00e2n s\u1ef1 & ca l\u00e0m','Chi ph\u00ed & n\u0103ng l\u01b0\u1ee3ng']


def make_tree(parent,columns):
    frame=tk.Frame(parent,bg=P['card']);frame.pack(fill='both',expand=True)
    frame.rowconfigure(0,weight=1);frame.columnconfigure(0,weight=1)
    tree=ttk.Treeview(frame,columns=columns,show='headings',selectmode='browse',style='Factory.Treeview')
    tree.grid(row=0,column=0,sticky='nsew')
    y=ttk.Scrollbar(frame,orient='vertical',command=tree.yview);y.grid(row=0,column=1,sticky='ns')
    x=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview);x.grid(row=1,column=0,sticky='ew')
    tree.configure(yscrollcommand=y.set,xscrollcommand=x.set)
    for c in columns:tree.heading(c,text=c);tree.column(c,width=140,minwidth=70)
    return tree

class FactoryWindow:
    def __init__(self,app,group=0):
        self.app=app
        self.service=Factory(app.auth_store.path.parent/'factory.sqlite3',app.auth_store,app.session)
        self.win=tk.Toplevel(app.root);self.win.title('Alibaba Operations Center V16.0.14 | Smart Factory')
        self.win.configure(bg=P['base']);self.win.geometry(f'{min(1420,self.win.winfo_screenwidth()-40)}x{min(870,self.win.winfo_screenheight()-65)}');self.win.minsize(1000,640)
        self.win.protocol('WM_DELETE_WINDOW',self.close)
        self.win.bind('<Destroy>',self._destroyed,add='+')
        self._closed=False;self._busy=False;self._poll_id=None;self._events=queue.Queue();self.page=0;self.rows=[];self.group=1
        self.plant_var=tk.StringVar();self.entity_var=tk.StringVar();self.search_var=tk.StringVar();self.status=tk.StringVar(value='S\u1eb5n s\u00e0ng - ch\u1ec9 d\u1eef li\u1ec7u c\u1ee5c b\u1ed9')
        style=ttk.Style(self.win)
        style.configure('Factory.Treeview',borderwidth=0,relief='flat',bordercolor=P['card'],lightcolor=P['card'],darkcolor=P['card'],rowheight=27)
        style.configure('Factory.TNotebook',borderwidth=0,lightcolor=P['card'],darkcolor=P['card'],bordercolor=P['card'])
        style.configure('Factory.TNotebook.Tab',borderwidth=0,lightcolor=P['card'],darkcolor=P['card'],bordercolor=P['card'],padding=(12,8))
        self._build()
        plants=self.service.plants();self.plant_picker['values']=[p['code'] for p in plants]
        prefs=self.service.preferences()
        if plants:self.plant_var.set(prefs.get('plant') if prefs.get('plant') in self.plant_picker['values'] else plants[0]['code'])
        self.select_group(group or prefs.get('group',1))
        if not group and not prefs:self.notebook.select(self.overview_tab)
        self._poll_id=self.win.after(80,self._poll)
        self.win.bind('<Control-f>',lambda e:self.search_entry.focus_set())
        self.win.bind('<F5>',lambda e:self.refresh())
        self.win.bind('<Escape>',lambda e:self.close() if e.widget==self.win else None)

    def _build(self):
        header=tk.Frame(self.win,bg=P['sidebar'],padx=22,pady=9);header.pack(fill='x')
        brand=tk.Frame(header,bg=P['sidebar']);brand.pack(side='left')
        ui_label(brand,'\u25c8  SMART FACTORY',19,strong=True).pack(anchor='w')
        ui_label(brand,'ALIBABA OPERATIONS CENTER   /   V16.0.14',8,color=P['muted']).pack(anchor='w',pady=(3,0))
        badge(header,'LOCAL WORKSPACE','blue').pack(side='right',padx=10)
        ui_label(header,self.app.session.display_name,10,color=P['muted']).pack(side='right',padx=10)
        footer=tk.Frame(self.win,bg=P['sidebar'],padx=15,pady=8);footer.pack(side='bottom',fill='x')
        tk.Label(footer,textvariable=self.status,bg=P['sidebar'],fg=P['muted'],font=('Segoe UI',9),anchor='w').pack(fill='x')
        body=tk.Frame(self.win,bg=P['base'],padx=12,pady=12);body.pack(fill='both',expand=True)
        left=tk.Frame(body,bg=P['sidebar'],width=224);left.pack(side='left',fill='y',padx=(0,14));left.pack_propagate(False)
        ui_label(left,'10 PH\u00c2N H\u1ec6   /   100 H\u1ea0NG M\u1ee4C',9,strong=True,color=P['muted']).pack(anchor='w',padx=12,pady=(14,10))
        self.nav=[]
        for i,name in enumerate(SHORT_GROUPS,1):
            b=tk.Button(left,text=f'{i:02d}   {name}',font=('Segoe UI',10),anchor='w',bg=P['sidebar'],fg=P['muted'],activebackground=P['card_light'],activeforeground=P['white'],bd=0,highlightthickness=0,relief='flat',padx=12,pady=9,cursor='hand2',command=lambda g=i:self.select_group(g))
            b.pack(fill='x',padx=6,pady=1);self.nav.append(b)
        action_button(left,'\u2190  V\u1ec1 Email / IT / PMC',self.close).pack(side='bottom',fill='x',padx=9,pady=12)
        right=tk.Frame(body,bg=P['base']);right.pack(side='left',fill='both',expand=True)
        top=tk.Frame(right,bg=P['base']);top.pack(fill='x',pady=(0,10))
        self.heading=ui_label(top,'',16,strong=True);self.heading.pack(side='left')
        action_button(top,'+ Nh\u00e0 m\u00e1y',self.add_plant).pack(side='right',padx=(7,0))
        self.plant_picker=ttk.Combobox(top,textvariable=self.plant_var,state='readonly',width=14)
        self.plant_picker.pack(side='right');self.plant_picker.bind('<<ComboboxSelected>>',lambda e:self.refresh())
        self.metrics={};bar=tk.Frame(right,bg=P['base']);bar.pack(fill='x',pady=(0,10))
        for k,label,color in [('orders','L\u1ec6NH S\u1ea2N XU\u1ea4T','blue'),('lots','L\u00d4 TRONG KHO','violet'),('incidents','S\u1ef0 C\u1ed0 \u0110ANG M\u1ede','amber'),('shortages','D\u01af\u1edaI T\u1ed2N AN TO\u00c0N','green')]:
            card=MetricCard(bar,label,color);card.winfo_children()[0].configure(pady=7);card.pack(side='left',fill='x',expand=True,padx=(0,8));self.metrics[k]=card
        note=tk.Frame(right,bg=P['card_light'],padx=12,pady=7);note.pack(fill='x',pady=(0,9))
        ui_label(note,'D\u1eef li\u1ec7u nh\u1eadp tay / CSV. Kh\u00f4ng t\u1ef1 ghi ERP, \u0111i\u1ec1u khi\u1ec3n PLC hay g\u1eedi email.',9,color=P['muted']).pack(anchor='w')
        self.notebook=ttk.Notebook(right,style='Factory.TNotebook');self.notebook.pack(fill='both',expand=True)
        self.overview_tab=tk.Frame(self.notebook,bg=P['card'],padx=14,pady=14)
        self.notebook.add(self.overview_tab,text='Dashboard')
        self._build_overview()
        self.data_tab=tk.Frame(self.notebook,bg=P['card'],padx=12,pady=10)
        self.tools_tab=tk.Frame(self.notebook,bg=P['card'],padx=12,pady=10)
        self.scope_tab=tk.Frame(self.notebook,bg=P['card'],padx=12,pady=10)
        for frame,label in [(self.data_tab,'D\u1eef li\u1ec7u & nghi\u1ec7p v\u1ee5'),(self.tools_tab,'C\u00f4ng c\u1ee5 & b\u00e1o c\u00e1o'),(self.scope_tab,'Danh m\u1ee5c & ph\u1ea1m vi')]:self.notebook.add(frame,text=label)
        choose=tk.Frame(self.data_tab,bg=P['card']);choose.pack(fill='x',pady=(0,8))
        self.entity_picker=ttk.Combobox(choose,textvariable=self.entity_var,state='readonly',width=39);self.entity_picker.pack(side='left');self.entity_picker.bind('<<ComboboxSelected>>',lambda e:self.refresh_data())
        self.search_entry=ttk.Entry(choose,textvariable=self.search_var,width=21);self.search_entry.pack(side='right',padx=(8,0));self.search_entry.bind('<Return>',lambda e:self.refresh_data())
        ui_label(choose,'T\u00ecm m\u00e3 / n\u1ed9i dung',9,color=P['muted']).pack(side='right')
        toolbar=tk.Frame(self.data_tab,bg=P['card']);toolbar.pack(fill='x',pady=(0,8))
        self.new_button=action_button(toolbar,'+ T\u1ea1o m\u1edbi',self.edit_record,'primary');self.new_button.pack(side='left',padx=(0,6))
        self.edit_button=action_button(toolbar,'S\u1eeda',lambda:self.edit_record(True));self.edit_button.pack(side='left',padx=(0,6))
        for label,cb in [('M\u1eabu CSV',self.template),('Nh\u1eadp CSV',self.import_csv),('Xu\u1ea5t CSV',self.export_csv),('L\u00e0m m\u1edbi',self.refresh_data)]:action_button(toolbar,label,cb).pack(side='left',padx=(0,6))
        paging=tk.Frame(self.data_tab,bg=P['card']);paging.pack(side='bottom',fill='x',pady=(6,0))
        action_button(paging,'\u2039',lambda:self.turn_page(-1)).pack(side='left')
        action_button(paging,'\u203a',lambda:self.turn_page(1)).pack(side='left',padx=5)
        self.page_label=ui_label(paging,'',9,color=P['muted']);self.page_label.pack(side='left',padx=8)
        self.empty_label=ui_label(self.data_tab,'',10,color=P['amber']);self.empty_label.pack(anchor='w',pady=3)
        self.tree=make_tree(self.data_tab,['code']);self.tree.bind('<Double-Button-1>',lambda e:self.edit_record(True))
        self._build_scope()

    def _build_overview(self):
        ui_label(self.overview_tab,'PRODUCTION INSIGHTS',11,strong=True).pack(anchor='w')
        ui_label(self.overview_tab,'Chỉ hiển thị bản ghi cục bộ. Biểu đồ không là dữ liệu PLC / ERP thời gian thực.',9,color=P['muted']).pack(anchor='w',pady=(4,12))
        charts=tk.Frame(self.overview_tab,bg=P['card']);charts.pack(fill='both',expand=True)
        charts.columnconfigure(0,weight=1);charts.columnconfigure(1,weight=1);charts.rowconfigure(0,weight=1)
        self.production_chart=tk.Canvas(charts,bg=P['base'],highlightthickness=0,height=210)
        self.production_chart.grid(row=0,column=0,sticky='nsew',padx=(0,7))
        self.oee_chart=tk.Canvas(charts,bg=P['base'],highlightthickness=0,height=210)
        self.oee_chart.grid(row=0,column=1,sticky='nsew',padx=(7,0))
        self.production_chart.bind('<Configure>',lambda e:self._draw_charts())
        self.oee_chart.bind('<Configure>',lambda e:self._draw_charts())
        self.chart_data=([],[])
        ui_label(self.overview_tab,'F5: làm mới   |   Mỗi phân hệ: Dữ liệu > Công cụ > Phạm vi',9,color=P['muted']).pack(anchor='w',pady=(10,0))

    def _refresh_overview(self):
        plant=self.plant_var.get();orders=[];oee=[]
        if plant:
            try:
                if self.service.can(plant,4):
                    orders=self.service.list_records(plant,'orders',limit=8)['rows']
                    oee=self.service.report(plant,'oee')[-8:]
            except Exception:
                self.status.set('Chưa đọc được dữ liệu biểu đồ; nhấn F5 để thử lại.')
        self.chart_data=(orders,oee);self._draw_charts()

    def _draw_charts(self):
        if not hasattr(self,'chart_data'):return
        from decimal import Decimal
        orders,oee=self.chart_data
        series=[(self.production_chart,'TIẾN ĐỘ LỆNH SẢN XUẤT',[(r['code'],float(Decimal(r.get('good_qty','0'))/Decimal(r['quantity'])*100)) for r in orders],P['blue']),
                (self.oee_chart,'OEE THEO CA',[(r['shift'],float(r['oee_pct'])) for r in oee],P['green'])]
        for canvas,title,rows,color in series:
            canvas.delete('all');w=max(250,canvas.winfo_width());h=max(160,canvas.winfo_height())
            canvas.create_text(14,19,text=title,anchor='w',fill=P['white'],font=('Segoe UI',10,'bold'))
            if not rows:
                canvas.create_text(14,80,text='Chưa có dữ liệu / chưa được cấp quyền.\nNhập bản ghi để xem biểu đồ.',anchor='w',justify='left',fill=P['muted'],font=('Segoe UI',10));continue
            for i,(label,val) in enumerate(rows):
                y=48+i*max(24,min(33,(h-60)/len(rows)))
                canvas.create_text(14,y+8,text=label[:18],anchor='w',fill=P['muted'],font=('Segoe UI',9))
                canvas.create_rectangle(145,y,w-64,y+16,fill=P['card_light'],outline='')
                canvas.create_rectangle(145,y,145+(w-209)*max(0,min(100,val))/100,y+16,fill=color if val<=100 else P['amber'],outline='')
                canvas.create_text(w-12,y+8,text=f'{val:.1f}%',anchor='e',fill=P['white'],font=('Segoe UI',9))

    def _build_scope(self):
        ui_label(self.scope_tab,'Y\u00eau c\u1ea7u g\u1ed1c \u2260 ch\u1ee9ng nh\u1eadn / cam k\u1ebft \u0111\u00e3 ho\u00e0n th\u00e0nh',11,strong=True).pack(anchor='w',pady=(0,8))
        self.scope_tree=make_tree(self.scope_tab,('id','name','status'))
        for k,title,w in [('id','M\u1ee5c',50),('name','T\u00ednh n\u0103ng theo t\u1ec7p y\u00eau c\u1ea7u',390),('status','Ph\u1ea1m vi tri\u1ec3n khai',235)]:self.scope_tree.heading(k,text=title);self.scope_tree.column(k,width=w,stretch=k=='name')
        self.scope_tree.tag_configure('local_scope',foreground=P['green']);self.scope_tree.tag_configure('partial',foreground=P['amber']);self.scope_tree.tag_configure('integration_required',foreground=P['muted'])
        self.scope_tree.bind('<<TreeviewSelect>>',lambda e:self.scope_detail())
        self.scope_text=tk.Text(self.scope_tab,height=5,bg=P['base'],fg=P['white'],font=('Segoe UI',10),wrap='word',relief='flat',padx=9,pady=8)
        self.scope_text.pack(fill='x',pady=8);self.scope_text.configure(state='disabled')
        self.scope_open=action_button(self.scope_tab,'M\u1edf ph\u1ea7n \u0111\u00e3 tri\u1ec3n khai',self.open_scope_route);self.scope_open.pack(anchor='w')

    def select_group(self,group):
        if not 1<=int(group)<=10:return
        self.group=int(group);self.heading.configure(text=SHORT_GROUPS[self.group-1])
        for i,b in enumerate(self.nav,1):b.configure(bg=P['card_light'] if i==self.group else P['sidebar'],fg=P['white'] if i==self.group else P['muted'])
        keys=GROUP_ENTITIES[self.group];self.entity_picker['values']=[ENTITIES[k]['label'] for k in keys]
        self.entity_var.set(ENTITIES[keys[0]]['label'] if keys else 'Kh\u00f4ng c\u00f3 b\u1ea3ng nh\u1eadp - xem C\u00f4ng c\u1ee5')
        self.page=0;self.search_var.set('');self._build_tools()
        self.scope_tree.delete(*self.scope_tree.get_children())
        for f in FEATURES:
            if f['group']==self.group:self.scope_tree.insert('', 'end',iid=str(f['id']),values=(f['id'],f['name'],STATUS_LABELS[f['status']]),tags=(f['status'],))
        self.scope_open.configure(state='disabled')
        self.scope_text.configure(state='normal');self.scope_text.delete('1.0','end');self.scope_text.insert('1.0','Ch\u1ecdn m\u1ed9t m\u1ee5c \u0111\u1ec3 \u0111\u1ecdc y\u00eau c\u1ea7u v\u00e0 ph\u1ea1m vi th\u1ef1c t\u1ebf.');self.scope_text.configure(state='disabled')
        self.refresh()
        self.notebook.select(self.overview_tab if self.group==6 else (self.data_tab if keys else self.tools_tab))

    def current_kind(self):
        return next((k for k in GROUP_ENTITIES[self.group] if ENTITIES[k]['label']==self.entity_var.get()),None)

    def refresh(self):
        if self._closed:return
        plant=self.plant_var.get()
        if plant:
            try:
                data=self.service.overview(plant)
                for k,card in self.metrics.items():card.update_value('\u2014' if data.get(k) is None else str(data[k]),'D\u1eef li\u1ec7u l\u01b0u c\u1ee5c b\u1ed9' if data.get(k) is not None else 'Kh\u00f4ng c\u00f3 quy\u1ec1n xem')
            except Exception as e:self.status.set(str(e))
        else:
            for card in self.metrics.values():card.update_value('\u2014','Ch\u01b0a ch\u1ecdn nh\u00e0 m\u00e1y')
        self._refresh_overview()
        self.refresh_data()

    def refresh_data(self,reset=True):
        if self._closed:return
        if reset:self.page=0
        kind=self.current_kind();self.tree.delete(*self.tree.get_children());self.rows=[]
        if not self.plant_var.get():
            self.empty_label.configure(text='B\u1eaft \u0111\u1ea7u: nh\u1ea5n [+ Nh\u00e0 m\u00e1y]. Nh\u00e2n vi\u00ean c\u1ea7n \u0111\u01b0\u1ee3c qu\u1ea3n tr\u1ecb c\u1ea5p quy\u1ec1n.');self.page_label.configure(text='');return
        if not kind:
            self.empty_label.configure(text='Ch\u1ecdn tab C\u00f4ng c\u1ee5 & b\u00e1o c\u00e1o \u0111\u1ec3 thao t\u00e1c.');return
        fields=['code']+[f.key for f in ENTITIES[kind]['fields']][:7]
        self.tree.configure(columns=fields)
        labels={'code':'M\u00e3',**{f.key:f.label for f in ENTITIES[kind]['fields']}}
        if kind=='lots':labels['quantity']='T\u1ed3n l\u00f4 c\u00f2n l\u1ea1i'
        for f in fields:self.tree.heading(f,text=labels[f]);self.tree.column(f,width=150,minwidth=90,stretch=False)
        try:
            result=self.service.list_records(self.plant_var.get(),kind,self.search_var.get(),self.page)
            self.rows=result['rows'];self.total=result['total']
            for i,r in enumerate(self.rows):self.tree.insert('','end',iid=str(i),values=[r.get(k,'') for k in fields])
            self.empty_label.pack_forget()
            if not self.rows:self.empty_label.pack(anchor='w',pady=3,before=self.tree.master)
            self.empty_label.configure(text='' if self.rows else 'Ch\u01b0a c\u00f3 d\u1eef li\u1ec7u ph\u00f9 h\u1ee3p. T\u1ea1o m\u1edbi ho\u1eb7c nh\u1eadp CSV \u0111\u00fang m\u1eabu.')
            self.page_label.configure(text=f'Trang {self.page+1}   |   {len(self.rows)} / {self.total} b\u1ea3n ghi   |   100 d\u00f2ng/trang')
            write=self.service.can(self.plant_var.get(),ENTITIES[kind]['group'],True) and (not ENTITIES[kind]['admin'] or self.app.session.role=='it_admin')
            self.new_button.configure(state='normal' if write else 'disabled')
            self.edit_button.configure(state='normal' if write and not ENTITIES[kind]['immutable'] else 'disabled')
        except Exception as e:
            self.empty_label.configure(text=str(e));self.new_button.configure(state='disabled');self.edit_button.configure(state='disabled')

    def turn_page(self,direction):
        target=self.page+direction
        if target>=0 and target*100<getattr(self,'total',0):self.page=target;self.refresh_data(False)

    def _need_plant(self):
        if not self.plant_var.get():raise FactoryError('H\u00e3y t\u1ea1o / ch\u1ecdn nh\u00e0 m\u00e1y tr\u01b0\u1edbc.')
        return self.plant_var.get()

    def edit_record(self,edit=False):
        try:
            plant=self._need_plant();kind=self.current_kind()
            if not kind:return
            selected=self.tree.selection();row=self.rows[int(selected[0])] if edit and selected else None
            if edit and not row:raise FactoryError('Ch\u1ecdn m\u1ed9t d\u00f2ng c\u1ea7n s\u1eeda.')
            if edit and ENTITIES[kind]['immutable']:raise FactoryError('Ch\u1ee9ng t\u1eeb \u0111\u00e3 ghi s\u1ed5; d\u00f9ng nghi\u1ec7p v\u1ee5 hi\u1ec7u ch\u1ec9nh ri\u00eang.')
            fields=(F('code','M\u00e3 b\u1ea3n ghi (duy nh\u1ea5t)'),)+ENTITIES[kind]['fields']
            def save(values):
                code=values.pop('code')
                return self.service.save(plant,kind,code,values,row['_rev'] if row else 0)
            FormDialog(self,ENTITIES[kind]['label'],fields,save,initial=row or {},locked={'code'} if row else set(),refs=True)
        except Exception as e:self.error(e)

    def add_plant(self):
        if self.app.session.role!='it_admin':return self.error('Ch\u1ec9 qu\u1ea3n tr\u1ecb \u0111\u01b0\u1ee3c t\u1ea1o nh\u00e0 m\u00e1y.')
        def saved(code):
            self.plant_picker['values']=[x['code'] for x in self.service.plants()];self.plant_var.set(code);self.refresh()
        FormDialog(self,'Khai b\u00e1o nh\u00e0 m\u00e1y',(F('code','M\u00e3'),F('name','T\u00ean nh\u00e0 m\u00e1y'),F('currency','M\u00e3 ti\u1ec1n t\u1ec7','text','VND'),F('capacity','C\u00f4ng su\u1ea5t tham chi\u1ebfu / ng\u00e0y','decimal','0'),F('utc_offset','UTC offset (phut; Viet Nam = 420)','integer','420')),lambda v:self.service.add_plant(**v),done=saved)

    def edit_plant(self):
        try:
            plant=self._need_plant();self.service._admin()
            row=next(r for r in self.service.plants() if r['code']==plant)
        except Exception as e:return self.error(e)
        FormDialog(self,'Thiet lap nha may',[F('code','Ma nha may'),F('name','Ten nha may'),F('currency','Ma tien te'),F('capacity','Cong suat tham chieu/ngay','decimal'),F('utc_offset','UTC offset (phut, Viet Nam=420)','signed')],lambda v:self.service.update_plant(**v),initial=row,locked={'code'})

    def template(self):
        kind=self.current_kind()
        if not kind:return
        path=filedialog.asksaveasfilename(parent=self.win,initialfile=kind+'_template.csv',defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if path:
            try:self.service.write_csv(path,[],['code']+[f.key for f in ENTITIES[kind]['fields']]);self.status.set('\u0110\u00e3 t\u1ea1o m\u1eabu CSV tr\u1ed1ng; d\u00f9ng m\u1ed9t m\u00e3 m\u1edbi cho m\u1ed7i d\u00f2ng.')
            except Exception as e:self.error(e)

    def import_csv(self):
        try:plant=self._need_plant();kind=self.current_kind()
        except Exception as e:return self.error(e)
        if not kind:return
        path=filedialog.askopenfilename(parent=self.win,filetypes=[('CSV UTF-8','*.csv')])
        if path and messagebox.askyesno('Nh\u1eadp d\u1eef li\u1ec7u','Nh\u1eadp v\u00e0o '+plant+' / '+ENTITIES[kind]['label']+'? L\u1ed7i m\u1ed9t d\u00f2ng s\u1ebd h\u1ee7y to\u00e0n b\u1ed9 l\u1ea7n nh\u1eadp. Kh\u00f4ng ghi \u0111\u00e8 b\u1ea3n ghi c\u0169.',parent=self.win):
            self.run_task(lambda:self.service.import_csv(plant,kind,path),lambda n:self.status.set(f'\u0110\u00e3 nh\u1eadp {n} d\u00f2ng.'))

    def export_csv(self):
        try:plant=self._need_plant();kind=self.current_kind()
        except Exception as e:return self.error(e)
        if not kind:return
        path=filedialog.asksaveasfilename(parent=self.win,initialfile=f'{plant}_{kind}.csv',defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if path:self.run_task(lambda:self.service.export_records(plant,kind,path),lambda n:self.status.set(f'\u0110\u00e3 xu\u1ea5t {n} d\u00f2ng.'))

    def _build_tools(self):
        for w in self.tools_tab.winfo_children():w.destroy()
        self.tools={}
        cv=tk.Canvas(self.tools_tab,bg=P['card'],highlightthickness=0);cv.pack(side='left',fill='both',expand=True)
        sb=ttk.Scrollbar(self.tools_tab,orient='vertical',command=cv.yview);sb.pack(side='right',fill='y');cv.configure(yscrollcommand=sb.set)
        inner=tk.Frame(cv,bg=P['card']);wid=cv.create_window((0,0),window=inner,anchor='nw')
        inner.bind('<Configure>',lambda e:cv.configure(scrollregion=cv.bbox('all')));cv.bind('<Configure>',lambda e:cv.itemconfigure(wid,width=e.width))
        def add(route,title,note,fn):
            self.tools[route]=fn
            box=tk.Frame(inner,bg=P['card_light'],padx=12,pady=9);box.pack(fill='x',pady=(0,7))
            action_button(box,title,fn).pack(side='left',padx=(0,12))
            ui_label(box,note,9,color=P['muted'],wraplength=470,justify='left').pack(side='left',fill='x',expand=True)
        self._add_tool=add
        g=self.group
        if g==1:
            add('plant_settings','Thiet lap nha may','Doi ten / cong suat. Khoa tien te va mui gio khi da co du lieu.',self.edit_plant)
            add('allocation','\u0110\u1ec1 xu\u1ea5t ph\u00e2n b\u1ed5','Theo c\u00f4ng su\u1ea5t khai b\u00e1o; kh\u00f4ng t\u1ef1 chuy\u1ec3n \u0111\u01a1n ERP.',lambda:self.action_form('Ph\u00e2n b\u1ed5 theo tr\u1ecdng s\u1ed1',[F('quantity','T\u1ed5ng s\u1ed1 l\u01b0\u1ee3ng','positive')],lambda p,v:self.service.allocation(v['quantity'])))
            add('risks','C\u1ea3nh b\u00e1o cung \u1ee9ng','Nh\u00e0 cung c\u1ea5p r\u1ee7i ro cao v\u00e0 l\u00f4 giao h\u00e0ng tr\u1ec5 h\u1ea1n.',lambda:self.show_report('risks'))
        if g==2:add('sensors','Theo d\u00f5i ng\u01b0\u1ee1ng','D\u1eef li\u1ec7u qu\u00e1 h\u1ea1n hi\u1ec3n th\u1ecb STALE, kh\u00f4ng g\u00e1n online gi\u1ea3.',lambda:self.show_report('sensors'))
        if g==3:
            add('stock','T\u1ed3n kh\u1ea3 d\u1ee5ng','T\u00e1ch t\u1ed3n v\u1eadt l\u00fd, t\u1ed3n kh\u1ea3 d\u1ee5ng v\u00e0 m\u1ee9c an to\u00e0n.',lambda:self.show_report('stock'))
            add('issue','Xu\u1ea5t kho FEFO','Tr\u1eeb l\u00f4, kh\u00f3a l\u00f4 h\u1ebft h\u1ea1n, ki\u1ec3m tra l\u1ec7nh v\u00e0 BOM.',lambda:self.action_form('Xu\u1ea5t kho - ghi s\u1ed5 c\u1ee5c b\u1ed9',[F('request','M\u00e3 giao d\u1ecbch duy nh\u1ea5t'),F('order','L\u1ec7nh RELEASED'),F('material','M\u00e3 v\u1eadt t\u01b0'),F('quantity','S\u1ed1 l\u01b0\u1ee3ng','positive')],lambda p,v:self.service.issue(p,**v),True))
            add('return_issue','Hoan tra phieu xuat','Chi hoan tra toan bo phieu khi lenh chua co thanh pham; co nhat ky.',lambda:self.action_form('Hoan tra vat tu',[F('request','Ma giao dich moi'),F('issue_request','Ma giao dich xuat goc'),F('reason','Ly do')],lambda p,v:self.service.return_issue(p,**v),True))
            add('reconcile','\u0110\u1ed1i so\u00e1t ki\u1ec3m k\u00ea','So v\u1edbi t\u1ed3n s\u1ed5 \u0111\u00e3 ch\u1ed1t t\u1ea1i l\u00fac ghi phi\u1ebfu.',lambda:self.show_report('reconcile'))
            add('abc','Ph\u00e2n nh\u00f3m ABC','Theo l\u01b0\u1ee3ng \u0111\u00e3 xu\u1ea5t; t\u00e1ch ri\u00eang t\u1eebng \u0111\u01a1n v\u1ecb t\u00ednh.',lambda:self.show_report('abc'))
        if g==4:
            add('mrp','T\u00ednh MRP \u0111a c\u1ea5p','K\u1ecbch b\u1ea3n m\u1edbi t\u1ea1i M\u1ed8T ng\u00e0y c\u1ea7n. Kh\u00f4ng t\u1ef1 gom WIP hay \u0111\u01a1n c\u0169.',lambda:self.action_form('K\u1ecbch b\u1ea3n nhu c\u1ea7u MRP',[F('product','M\u00e3 s\u1ea3n ph\u1ea9m'),F('quantity','Nhu c\u1ea7u b\u1ed5 sung','positive'),F('need_date','Ng\u00e0y c\u1ea7n','date')],lambda p,v:self.service.mrp(p,**v)))
            add('plan','L\u1eadp l\u1ecbch nh\u00e1p','M\u1ed9t m\u00e1y \u0111\u01b0\u1ee3c ch\u1ecdn, tr\u00e1nh c\u1eeda s\u1ed5 b\u1ea3o tr\u00ec; ch\u01b0a t\u1ed1i \u01b0u APS.',lambda:self.action_form('L\u1ecbch nh\u00e1p tr\u00ean m\u1ed9t m\u00e1y',[F('asset','M\u00e3 m\u00e1y'),F('start','B\u1eaft \u0111\u1ea7u','datetime')],lambda p,v:self.service.plan(p,**v)))
            add('outputs','Ghi nh\u1eadn s\u1ea3n l\u01b0\u1ee3ng','T\u1ea1o l\u00f4 th\u00e0nh ph\u1ea9m HOLD, gi\u1eef li\u00ean k\u1ebft truy xu\u1ea5t.',lambda:self.action_form('Nh\u1eadp th\u00e0nh ph\u1ea9m',[F('request','M\u00e3 giao d\u1ecbch'),F('order','L\u1ec7nh SX'),F('good','S\u1ea3n l\u01b0\u1ee3ng \u0111\u1ea1t','positive'),F('scrap','Ph\u1ebf ph\u1ea9m','decimal','0'),F('lot','M\u00e3 l\u00f4 th\u00e0nh ph\u1ea9m M\u1edaI'),F('operator','M\u00e3 nh\u00e2n s\u1ef1',required=False)],lambda p,v:self.service.output(p,**v),True))
            add('oee','Ph\u00e2n t\u00edch OEE','Kh\u1ea3 d\u1ee5ng x Hi\u1ec7u su\u1ea5t x Ch\u1ea5t l\u01b0\u1ee3ng t\u1eeb nh\u1eadt k\u00fd ca.',lambda:self.show_report('oee'))
            add('output_report','L\u1ecbch s\u1eed s\u1ea3n l\u01b0\u1ee3ng','Ch\u1ee9ng t\u1eeb \u0111\u00e3 ghi s\u1ed5 theo th\u1eddi gian.',lambda:self.show_report('outputs'))
        if g==5:
            add('grants','C\u1ea5p quy\u1ec1n theo nh\u00e0 m\u00e1y','Qu\u1ea3n tr\u1ecb c\u1ea5p \u0111\u1ecdc/ghi theo ph\u00e2n h\u1ec7 1-10; c\u00f3 th\u1ec3 thu h\u1ed3i.',self.grant_dialog)
            add('audit','Xem Audit Trail','Nh\u1eadt k\u00fd thay \u0111\u1ed5i Smart Factory; kh\u00f4ng thay nh\u1eadt k\u00fd b\u1ea3n c\u0169.',lambda:self.show_report('audit'))
            add('verify_audit','Ki\u1ec3m tra chu\u1ed7i Audit','Hash chain c\u1ee5c b\u1ed9, kh\u00f4ng ph\u1ea3i ch\u1ee9ng nh\u1eadn ch\u1ed1ng gi\u1ea3 m\u1ea1o.',lambda:self.run_task(self.service.verify_audit,lambda r:self.show_result('Audit',r)))
            add('backup','Sao l\u01b0u CSDL','Snapshot Smart Factory + SHA-256. KH\u00d4NG m\u00e3 h\u00f3a.',self.snapshot)
            add('verify_backup','Ki\u1ec3m tra / ph\u1ee5c h\u1ed3i b\u1ea3n sao','Ph\u1ee5c h\u1ed3i ra t\u1ec7p M\u1edaI, kh\u00f4ng ghi \u0111\u00e8 CSDL \u0111ang d\u00f9ng.',self.verify_snapshot)
            add('users','T\u00e0i kho\u1ea3n \u1ee9ng d\u1ee5ng','M\u1edf qu\u1ea3n tr\u1ecb t\u00e0i kho\u1ea3n c\u0169; kh\u00f4ng h\u1ecfi m\u1eadt kh\u1ea9u mail.',self.app.manage_users)
        if g==6:add('report','Xu\u1ea5t b\u00e1o c\u00e1o qu\u1ea3n tr\u1ecb','HTML c\u1ee5c b\u1ed9, theo y\u00eau c\u1ea7u; ch\u01b0a g\u1eedi l\u00fac 08:00.',self.html_report)
        if g==7:
            add('topology','S\u01a1 \u0111\u1ed3 thi\u1ebft b\u1ecb','Li\u00ean k\u1ebft cha do ng\u01b0\u1eddi d\u00f9ng khai b\u00e1o, kh\u00f4ng suy \u0111o\u00e1n c\u1ed5ng switch.',self.topology)
            add('lan','Qu\u00e9t LAN hi\u1ec7n c\u00f3','M\u1edf c\u00f4ng c\u1ee5 LAN \u0111\u00e3 s\u1eeda l\u1ed7i CMD; ch\u1ec9 qu\u00e9t m\u1ea1ng \u0111\u01b0\u1ee3c ph\u00e9p.',lambda:self.app.open_infrastructure('monitor'))
            add('vpn','IP / VPN hi\u1ec7n c\u00f3','Kh\u00f4ng th\u1ef1c hi\u1ec7n th\u00eam l\u1ec7nh \u0111\u1ed5i m\u1ea1ng khi ch\u01b0a x\u00e1c nh\u1eadn.',self.app.open_network_manager)
        if g==8:
            add('quality','Th\u1ed1ng k\u00ea ch\u1ea5t l\u01b0\u1ee3ng','Theo IQC / PQC / OQC v\u00e0 nguy\u00ean nh\u00e2n \u0111\u00e3 ghi.',lambda:self.show_report('quality'))
            add('trace','Truy xu\u1ea5t hai chi\u1ec1u','Li\u00ean k\u1ebft l\u00f4 \u0111\u1ea7u v\u00e0o - l\u1ec7nh SX - l\u00f4 th\u00e0nh ph\u1ea9m.',lambda:self.action_form('Truy xu\u1ea5t l\u00f4',[F('lot','M\u00e3 l\u00f4')],lambda p,v:self.service.trace(p,**v)))
            add('lot_quality','Gi\u1ea3i ph\u00f3ng / c\u00e1ch ly l\u00f4','C\u1ea7n quy\u1ec1n QMS v\u00e0 ghi l\u00fd do; kh\u00f4ng b\u1ecf kh\u00f3a h\u1ebft h\u1ea1n khi xu\u1ea5t.',lambda:self.action_form('Tr\u1ea1ng th\u00e1i ch\u1ea5t l\u01b0\u1ee3ng l\u00f4',[F('lot','L\u00f4'),F('quality','Tr\u1ea1ng th\u00e1i','choice','RELEASED',choices=('RELEASED','HOLD','BLOCKED')),F('reason','L\u00fd do / b\u1eb1ng ch\u1ee9ng')],lambda p,v:self.service.lot_quality(p,**v),True))
            add('expiry','C\u1ea3nh b\u00e1o qu\u00e1 h\u1ea1n','Hi\u1ec7u chu\u1ea9n, ch\u1ee9ng ch\u1ec9, b\u1ea3n quy\u1ec1n v\u00e0 b\u1ea3o tr\u00ec.',lambda:self.show_report('expiry'))
        if g==9:add('expiry','Ch\u1ee9ng ch\u1ec9 / hi\u1ec7u chu\u1ea9n qu\u00e1 h\u1ea1n','C\u1ea7n quy\u1ec1n \u0111\u1ecdc nh\u00f3m QMS cho b\u00e1o c\u00e1o li\u00ean ph\u00e2n h\u1ec7.',lambda:self.show_report('expiry'))
        if g==10:
            add('energy_report','N\u0103ng l\u01b0\u1ee3ng & CO2e','H\u1ec7 s\u1ed1 do ng\u01b0\u1eddi d\u00f9ng cung c\u1ea5p; kh\u00f4ng c\u00f3 h\u1ec7 s\u1ed1 th\u00ec UNKNOWN.',lambda:self.action_form('B\u00e1o c\u00e1o n\u0103ng l\u01b0\u1ee3ng',[F('idle_threshold','Ng\u01b0\u1ee1ng IDLE kWh/k\u1ef3','decimal','0')],lambda p,v:self.service.report(p,'energy_report',**v)))
            add('cost','\u01af\u1edbc t\u00ednh gi\u00e1 th\u00e0nh','T\u1ed5ng chi ph\u00ed C\u1ea2 L\u00d4; c\u00f9ng \u0111\u01a1n v\u1ecb ti\u1ec1n t\u1ec7.',lambda:self.action_form('Chi ph\u00ed l\u00f4 s\u1ea3n xu\u1ea5t',[F('quantity','S\u1ed1 s\u1ea3n ph\u1ea9m','positive')]+[F(k,l,'decimal','0') for k,l in [('material','Nguy\u00ean li\u1ec7u'),('labor','Nh\u00e2n c\u00f4ng'),('energy','N\u0103ng l\u01b0\u1ee3ng'),('overhead','Kh\u1ea5u hao / chi ph\u00ed kh\u00e1c')]],lambda p,v:cost_estimate(**v)))
            add('roi','\u01af\u1edbc t\u00ednh ho\u00e0n v\u1ed1n','Kh\u00f4ng chi\u1ebft kh\u1ea5u; kh\u00f4ng ph\u1ea3i khuy\u1ebfn ngh\u1ecb \u0111\u1ea7u t\u01b0.',lambda:self.action_form('ROI / ho\u00e0n v\u1ed1n',[F('capex','V\u1ed1n \u0111\u1ea7u t\u01b0','positive'),F('annual_savings','Ti\u1ebft ki\u1ec7m r\u00f2ng/n\u0103m','signed')],lambda p,v:roi_estimate(**v)))
        if g in (4,10):add('whatif','So s\u00e1nh ph\u01b0\u01a1ng \u00e1n','\u0110\u01a1n gi\u00e1 \u0111\u1ea7u v\u00e0o: th\u01b0\u1eddng, t\u0103ng ca, gia c\u00f4ng.',lambda:self.action_form('What-if chi ph\u00ed',[F('quantity','S\u1ed1 l\u01b0\u1ee3ng','positive')]+[F(k,k,'decimal') for k in ('regular','overtime','outsourced')],lambda p,v:what_if(**v)))
        add('preferences','L\u01b0u v\u1ecb tr\u00ed l\u00e0m vi\u1ec7c','Nh\u00e0 m\u00e1y / ph\u00e2n h\u1ec7 theo t\u00e0i kho\u1ea3n tr\u00ean M\u00c1Y N\u00c0Y.',self.save_preference)

    def action_form(self,title,fields,fn,confirm=False):
        try:plant=self._need_plant()
        except Exception as e:return self.error(e)
        domain=self.group
        def submit(values):
            # Pure calculations also need the current plant/domain access.
            if not self.service.can(plant,domain):raise AccessDenied('Kh\u00f4ng c\u00f3 quy\u1ec1n ph\u00e2n h\u1ec7.')
            return fn(plant,values)
        FormDialog(self,title,fields,submit,done=lambda r:self.show_result(title,r),confirm=confirm)

    def show_report(self,kind):
        try:plant=self._need_plant()
        except Exception as e:return self.error(e)
        self.run_task(lambda:self.service.report(plant,kind),lambda r:self.show_result(kind,r))

    def show_result(self,title,result):
        rows=result if isinstance(result,list) else [result if isinstance(result,dict) else {'result':result}]
        win=tk.Toplevel(self.win);win.title(title);win.geometry('990x540');win.configure(bg=P['base'])
        ui_label(win,title,17,strong=True).pack(anchor='w',padx=15,pady=12)
        ui_label(win,f'{len(rows)} d\u00f2ng | K\u1ebft qu\u1ea3 t\u1eeb d\u1eef li\u1ec7u / \u0111\u1ea7u v\u00e0o c\u1ee5c b\u1ed9',9,color=P['muted']).pack(anchor='w',padx=15,pady=(0,10))
        columns=list(rows[0]) if rows else ['status'];tree=make_tree(win,columns)
        for r in rows[:5000]:tree.insert('','end',values=[json.dumps(r.get(c),ensure_ascii=False) if isinstance(r.get(c),(dict,list)) else r.get(c,'') for c in columns])
        if not rows:tree.insert('','end',values=['Kh\u00f4ng c\u00f3 b\u1ea3n ghi.'])
        plant=self.plant_var.get();domain=self.group
        def export():
            path=filedialog.asksaveasfilename(parent=win,defaultextension='.csv',filetypes=[('CSV','*.csv')])
            if path:
                try:
                    self.service.export_result(plant,domain,path,rows,columns)
                    self.status.set('\u0110\u00e3 xu\u1ea5t b\u00e1o c\u00e1o CSV.')
                except Exception as e:self.error(e)
        action_button(win,'Xu\u1ea5t k\u1ebft qu\u1ea3 CSV',export).pack(anchor='e',padx=15,pady=12)
        return win

    def grant_dialog(self):
        try:plant=self._need_plant();self.service._admin()
        except Exception as e:return self.error(e)
        def submit(v):
            if v['mode']=='REVOKE':self.service.revoke(plant,v['username'],v['domain'])
            else:self.service.grant(plant,v['username'],v['domain'],v['mode']=='WRITE')
            return self.service.list_grants(plant)
        FormDialog(self,'Ph\u00e2n quy\u1ec1n nh\u00e0 m\u00e1y '+plant,[F('username','T\u00e0i kho\u1ea3n \u1ee9ng d\u1ee5ng'),F('domain','Nh\u00f3m ph\u00e2n h\u1ec7','choice','1',choices=tuple(str(i) for i in range(1,11))),F('mode','Quy\u1ec1n','choice','READ',choices=('READ','WRITE','REVOKE'))],submit,done=lambda r:self.show_result('Quy\u1ec1n truy c\u1eadp',r),confirm=True)

    def snapshot(self):
        path=filedialog.asksaveasfilename(parent=self.win,initialfile='smart_factory_backup.zip',defaultextension='.zip',filetypes=[('ZIP','*.zip')])
        if path and messagebox.askyesno('Sao l\u01b0u KH\u00d4NG m\u00e3 h\u00f3a','B\u1ea3n sao ch\u1ee9a d\u1eef li\u1ec7u nh\u00e0 m\u00e1y. Ch\u1ecdn n\u01a1i l\u01b0u \u0111\u01b0\u1ee3c b\u1ea3o v\u1ec7. Ch\u1ec9 sao l\u01b0u Smart Factory, kh\u00f4ng g\u1ed3m mail / t\u00e0i kho\u1ea3n / PMC c\u0169. Ti\u1ebfp t\u1ee5c?',parent=self.win):self.run_task(lambda:self.service.backup(path),lambda r:self.show_result('Snapshot',r))

    def verify_snapshot(self):
        path=filedialog.askopenfilename(parent=self.win,filetypes=[('ZIP','*.zip')])
        if not path:return
        restore=''
        if messagebox.askyesno('Ki\u1ec3m tra snapshot','T\u1ea1o th\u00eam CSDL kh\u00f4i ph\u1ee5c v\u00e0o t\u1ec7p M\u1edaI? Ch\u1ecdn No \u0111\u1ec3 ch\u1ec9 ki\u1ec3m tra.',parent=self.win):
            restore=filedialog.asksaveasfilename(parent=self.win,initialfile='factory_recovered.sqlite3',defaultextension='.sqlite3')
            if not restore:return
        self.run_task(lambda:self.service.verify_backup(path,restore or None),lambda r:self.show_result('Ki\u1ec3m tra / ph\u1ee5c h\u1ed3i',r))

    def html_report(self):
        try:plant=self._need_plant()
        except Exception as e:return self.error(e)
        path=filedialog.asksaveasfilename(parent=self.win,initialfile=plant+'_executive.html',defaultextension='.html')
        if path:self.run_task(lambda:self.service.executive_html(plant,path),lambda r:self.status.set('\u0110\u00e3 xu\u1ea5t HTML: '+str(r)))

    def save_preference(self):
        try:self.service.preferences({'plant':self._need_plant(),'group':self.group});self.status.set('\u0110\u00e3 l\u01b0u thi\u1ebft l\u1eadp c\u1ee5c b\u1ed9 theo t\u00e0i kho\u1ea3n.')
        except Exception as e:self.error(e)

    def topology(self):
        try:plant=self._need_plant()
        except Exception as e:return self.error(e)
        def show(rows):
            win=tk.Toplevel(self.win);win.title('Topology - li\u00ean k\u1ebft KHAI B\u00c1O');win.geometry('1020x630');win.configure(bg=P['base'])
            ui_label(win,'S\u01a1 \u0111\u1ed3 theo tr\u01b0\u1eddng thi\u1ebft b\u1ecb cha. Kh\u00f4ng kh\u1eb3ng \u0111\u1ecbnh k\u1ebft n\u1ed1i v\u1eadt l\u00fd / online.',10,color=P['amber']).pack(fill='x',padx=16,pady=15)
            canvas=tk.Canvas(win,bg=P['base'],highlightthickness=0);canvas.pack(fill='both',expand=True)
            bar=ttk.Scrollbar(win,orient='vertical',command=canvas.yview);bar.pack(side='right',fill='y');canvas.configure(yscrollcommand=bar.set)
            levels={};byid={r['asset']:r for r in rows}
            def depth(key,seen=None):
                seen=seen or set()
                if key in seen:return 0
                seen.add(key);p=byid[key]['parent'];return 1+depth(p,seen) if p in byid else 0
            positions={}
            for r in rows[:500]:
                level=depth(r['asset']);index=levels.get(level,0);levels[level]=index+1;positions[r['asset']]=(35+min(level,4)*185,35+index*78)
            for r in rows[:500]:
                if r['parent'] in positions:
                    x,y=positions[r['asset']];px,py=positions[r['parent']];canvas.create_line(px+165,py+24,x,y+24,fill=P['border'],width=2)
            for r in rows[:500]:
                x,y=positions[r['asset']];canvas.create_rectangle(x,y,x+165,y+52,fill=P['card'],outline=P['blue']);canvas.create_text(x+10,y+15,anchor='w',text=r['asset'],fill=P['white'],font=('Segoe UI',10,'bold'));canvas.create_text(x+10,y+35,anchor='w',text=r['type']+' / '+r['state'],fill=P['muted'],font=('Segoe UI',8))
            if not rows:canvas.create_text(40,50,anchor='w',text='Ch\u01b0a c\u00f3 thi\u1ebft b\u1ecb.',fill=P['muted'])
            canvas.configure(scrollregion=canvas.bbox('all'))
        self.run_task(lambda:self.service.report(plant,'topology'),show)

    def scope_detail(self):
        selected=self.scope_tree.selection()
        if not selected:return
        feature=FEATURES[int(selected[0])-1]
        self.scope_text.configure(state='normal');self.scope_text.delete('1.0','end')
        self.scope_text.insert('1.0',f"{feature['id']}. {feature['name']}\nY\u00eau c\u1ea7u: {feature['requirement']}\nPh\u1ea1m vi code: {feature.get('scope_vi',feature['scope'])}")
        self.scope_text.configure(state='disabled');self.scope_open.configure(state='normal' if feature['route'] else 'disabled')

    def open_scope_route(self):
        selected=self.scope_tree.selection()
        if not selected:return
        route=FEATURES[int(selected[0])-1]['route']
        if route in GROUP_ENTITIES[self.group]:
            self.entity_var.set(ENTITIES[route]['label']);self.notebook.select(self.data_tab);self.refresh_data()
        elif route in self.tools:self.notebook.select(self.tools_tab);self.tools[route]()
        elif route=='plants':self.add_plant()
        elif route in ENTITIES:
            self.select_group(ENTITIES[route]['group']);self.entity_var.set(ENTITIES[route]['label']);self.notebook.select(self.data_tab);self.refresh_data()
        elif route in {'cost':10,'topology':7,'whatif':4}:
            group={'cost':10,'topology':7,'whatif':4}[route];self.select_group(group);self.notebook.select(self.tools_tab);self.tools[route]()
        elif route in ('overview','tests'):
            self.notebook.select(self.tools_tab);self.status.set('Xem t\u1ed5ng quan ph\u00eda tr\u00ean / TEST_REPORT_V16_0_14.md trong g\u00f3i m\u00e3 ngu\u1ed3n.')
        else:
            self.notebook.select(self.tools_tab);self.status.set('Ph\u1ea1m vi m\u1ed9t ph\u1ea7n; ch\u1ecdn c\u00f4ng c\u1ee5 t\u01b0\u01a1ng \u1ee9ng, kh\u00f4ng c\u00f3 t\u1ef1 \u0111\u1ed9ng h\u00f3a to\u00e0n b\u1ed9.')

    def run_task(self,fn,done=None,failed=None):
        if self._closed:return False
        if self._busy:self.status.set('T\u00e1c v\u1ee5 \u0111ang ch\u1ea1y. Vui l\u00f2ng ch\u1edd.');return False
        self._busy=True;self.status.set('\u0110ang x\u1eed l\u00fd...')
        def worker():
            try:self._events.put((True,fn(),done,failed))
            except Exception as e:self._events.put((False,e,done,failed))
        threading.Thread(target=worker,daemon=True,name='factory-worker').start()
        return True

    def _poll(self):
        self._poll_id=None
        if self._closed:return
        try:
            ok,value,done,failed=self._events.get_nowait();self._busy=False
            if ok:
                self.status.set('Ho\u00e0n th\u00e0nh.');self.refresh()
                if done:done(value)
            else:
                if failed:failed(value)
                self.error(value)
        except queue.Empty:pass
        except tk.TclError:pass
        finally:
            if not self._closed:self._poll_id=self.win.after(80,self._poll)

    def error(self,e):
        self.status.set(str(e)[:200]);messagebox.showwarning('Smart Factory',str(e)[:1000],parent=self.win)

    def close(self):
        if self._busy:return self.error('Ch\u1edd t\u00e1c v\u1ee5 ho\u00e0n th\u00e0nh tr\u01b0\u1edbc khi \u0111\u00f3ng.')
        self.win.destroy()

    def _destroyed(self,event):
        if event.widget is self.win:
            self._closed=True
            if self._poll_id:
                try:self.win.after_cancel(self._poll_id)
                except tk.TclError:pass
                self._poll_id=None


class FormDialog:
    def __init__(self,owner,title,fields,submit,initial=None,locked=None,refs=False,done=None,confirm=False):
        self.owner=owner;self.fields=tuple(fields);self.submit=submit;self.done=done;self.confirm=confirm;self._saving=False
        self.win=tk.Toplevel(owner.win);self.win.title(title);self.win.configure(bg=P['base']);self.win.geometry('710x620');self.win.minsize(580,420);self.win.transient(owner.win)
        ui_label(self.win,title,16,strong=True).pack(anchor='w',padx=18,pady=(15,5))
        ui_label(self.win,'* B\u1eaft bu\u1ed9c. S\u1ed1 th\u1eadp ph\u00e2n d\u00f9ng d\u1ea5u ch\u1ea5m. Th\u1eddi gian ph\u1ea3i c\u00f3 m\u00fai gi\u1edd.',9,color=P['muted']).pack(anchor='w',padx=18,pady=(0,10))
        footer=tk.Frame(self.win,bg=P['base']);footer.pack(side='bottom',fill='x',padx=18,pady=12)
        self.save_button=action_button(footer,'L\u01b0u / Th\u1ef1c hi\u1ec7n',self.save,'primary');self.save_button.pack(side='right')
        self.cancel_button=action_button(footer,'H\u1ee7y',self.close);self.cancel_button.pack(side='right',padx=8)
        self.error_var=tk.StringVar();tk.Label(footer,textvariable=self.error_var,bg=P['base'],fg=P['amber'],font=('Segoe UI',9),wraplength=320,justify='left').pack(side='left')
        area=tk.Frame(self.win,bg=P['base']);area.pack(fill='both',expand=True,padx=18)
        canvas=tk.Canvas(area,bg=P['base'],highlightthickness=0);canvas.pack(side='left',fill='both',expand=True)
        bar=ttk.Scrollbar(area,orient='vertical',command=canvas.yview);bar.pack(side='right',fill='y');canvas.configure(yscrollcommand=bar.set)
        inner=tk.Frame(canvas,bg=P['base']);wid=canvas.create_window((0,0),window=inner,anchor='nw')
        inner.bind('<Configure>',lambda e:canvas.configure(scrollregion=canvas.bbox('all')));canvas.bind('<Configure>',lambda e:canvas.itemconfigure(wid,width=e.width))
        self.vars={};self.entries={};initial=initial or {};locked=locked or set()
        for f in self.fields:
            default=f.default
            if f.type=='date' and f.required and not default:default=date.today().isoformat()
            if f.type=='datetime' and not default:default=datetime.now().astimezone().isoformat(timespec='seconds')
            v=tk.StringVar(value=initial.get(f.key,default));self.vars[f.key]=v
            row=tk.Frame(inner,bg=P['base']);row.pack(fill='x',pady=6)
            ui_label(row,f.label+(' *' if f.required else ''),9,color=P['muted']).pack(anchor='w',pady=(0,4))
            if f.choices:
                entry=ttk.Combobox(row,textvariable=v,values=f.choices,state='readonly')
            elif refs and f.ref:
                try:choices=[r['code'] for r in owner.service.list_records(owner.plant_var.get(),f.ref,limit=500)['rows']]
                except FactoryError:choices=[]
                entry=ttk.Combobox(row,textvariable=v,values=choices)
            else:entry=ttk.Entry(row,textvariable=v)
            entry.pack(fill='x');self.entries[f.key]=entry
            if f.key in locked:entry.configure(state='disabled')
        if self.entries:next(iter(self.entries.values())).focus_set()
        self.win.protocol('WM_DELETE_WINDOW',self.close)
        self.win.bind('<Control-Return>',lambda e:self.save());self.win.bind('<Escape>',lambda e:self.close())

    def close(self):
        if self._saving:
            self.error_var.set('\u0110ang ghi d\u1eef li\u1ec7u; h\u00e3y ch\u1edd x\u00e1c nh\u1eadn k\u1ebft qu\u1ea3.')
            return
        self.win.destroy()

    def save(self):
        if self._saving:return
        values={k:v.get() for k,v in self.vars.items()}
        for f in self.fields:
            if f.required and not values[f.key].strip():self.error_var.set('Thi\u1ebfu '+f.label);self.entries[f.key].focus_set();return
        if self.confirm and not messagebox.askyesno('X\u00e1c nh\u1eadn ghi d\u1eef li\u1ec7u','Thao t\u00e1c n\u00e0y thay \u0111\u1ed5i d\u1eef li\u1ec7u c\u1ee5c b\u1ed9. Ti\u1ebfp t\u1ee5c?',parent=self.win):return
        def ok(result):
            self._saving=False
            if self.win.winfo_exists():self.win.destroy()
            if self.done:self.done(result)
        def fail(e):
            self._saving=False
            if self.win.winfo_exists():
                self.save_button.configure(state='normal');self.cancel_button.configure(state='normal');self.error_var.set(str(e)[:130])
        self._saving=True;self.save_button.configure(state='disabled');self.cancel_button.configure(state='disabled')
        if not self.owner.run_task(lambda:self.submit(values),ok,fail):
            self._saving=False;self.save_button.configure(state='normal');self.cancel_button.configure(state='normal')
