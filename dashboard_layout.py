"""Three-lane operations dashboard, using only the Python standard Tk GUI."""
import tkinter as tk
from tkinter import ttk
from dashboard_widgets import PALETTE as P, ui_label, action_button, card, badge, MetricCard, Sparkline
from auth_local import ROLE_LABELS


def _make_card(parent,title,fill='x'):
    outer, inner=card(parent,title,13)
    outer.pack(fill=fill,pady=(0,10))
    return inner


def create_dashboard(app):
    root=app.root
    root.configure(bg=P['base'])
    style=ttk.Style(root)
    style.configure('OpsRadio.TRadiobutton',background=P['card'],foreground=P['white'])
    style.map('OpsRadio.TRadiobutton',background=[('active',P['card'])])
    style.configure('OpsEntry.TEntry',fieldbackground=P['card_light'],foreground=P['white'],padding=(9,8))
    style.configure('OpsCombo.TCombobox',fieldbackground=P['card_light'],foreground=P['white'],padding=(7,7))
    style.configure('OpsProgress.Horizontal.TProgressbar',background=P['green'],troughcolor=P['card_light'],thickness=10)

    app.shell=tk.Frame(root,bg=P['base'])
    app.shell.pack(fill='both',expand=True)
    app.header=tk.Frame(app.shell,bg=P['base'],height=77,padx=21,pady=11)
    app.header.pack(fill='x')
    brand=tk.Frame(app.header,bg=P['base']);brand.pack(side='left',fill='y')
    ui_label(brand,'◆  ALIBABA OPERATIONS CENTER',17,strong=True).pack(anchor='w')
    ui_label(brand,'UNIFIED MAIL  /  NETWORK  /  IT  /  PMC DASHBOARD',9,color=P['muted']).pack(anchor='w',pady=(2,0))
    app.header_status=tk.StringVar(value='● Sẵn sàng')
    ui_label(app.header,text='',color=P['muted'],size=9).pack(side='right',padx=4) if False else None
    app.identity_var=tk.StringVar(value=(f'{app.session.display_name} · {ROLE_LABELS.get(app.session.role, app.session.role)}' if app.session else 'Phiên kiểm thử'))
    action_button(app.header,'⌕  Tìm nhanh  Ctrl+K',app.open_command_palette).pack(side='right',padx=(8,0))
    action_button(app.header,'≡  Chức năng',app.show_menu_popup).pack(side='right',padx=(8,0))
    if app.session:
        action_button(app.header,'↪  Đăng xuất',app.logout).pack(side='right',padx=(8,0))
    ui_label(app.header,text='',color=P['muted'],size=9).pack(side='right',padx=4) if False else None
    tk.Label(app.header,textvariable=app.identity_var,bg=P['base'],fg=P['muted'],font=('Segoe UI',9)).pack(side='right',padx=(10,0))

    # Pack the live-console bar before expanding the main body so it stays visible.
    app.logs_card=tk.Frame(app.shell,bg=P['card'],highlightthickness=1,
                           highlightbackground=P['border'],padx=14,pady=7)
    app.logs_card.pack(side='bottom',fill='x',padx=15,pady=(0,10))

    app.body=tk.Frame(app.shell,bg=P['base'],padx=15)
    app.body.pack(fill='both',expand=True,pady=(0,5))
    app.sidebar=tk.Frame(app.body,bg=P['sidebar'],width=210,highlightbackground=P['border'],highlightthickness=1)
    app.sidebar.pack(side='left',fill='y',padx=(0,12));app.sidebar.pack_propagate(False)
    ui_label(app.sidebar,'WORKSPACES',9,color=P['muted'],bg=P['sidebar'],strong=True).pack(anchor='w',padx=15,pady=(18,12))
    app.sidebar_items=[]
    nav=[('01   Tổng quan / Sao lưu',lambda:app.focus_mail()),
         ('02   Dung lượng hộp thư',app.open_mail_quota),
         ('03   Mạng / VPN',app.open_network_manager),
         ('04   Hạ tầng CNTT',app.open_infrastructure),
         ('05   PMC sản xuất',app.open_pmc),
         ('06   Lỗi & Nhật ký',app.show_issues),
         ('07   Kiểm tra hệ thống',app.diagnose),
         ('08   Quản lý người dùng',app.manage_users),
         ('09   Smart Factory',app.open_factory)]
    for i,(name,cb) in enumerate(nav):
        if not app.can_access_nav(i):continue
        b=action_button(app.sidebar,name,cb,variant='primary' if i==0 else 'secondary',anchor='w',font=('Segoe UI',10)) if False else None
        b=tk.Button(app.sidebar,text=name,command=cb,bg=P['card_light'] if i==0 else P['sidebar'],
                    fg=P['white'] if i==0 else P['muted'],activeforeground=P['white'],
                    activebackground=P['card_light'],font=('Segoe UI',10,'bold' if i==0 else 'normal'),
                    anchor='w',relief='flat',bd=0,highlightthickness=0,padx=11,pady=11,cursor='hand2')
        b.pack(fill='x',padx=8,pady=2)
        app.sidebar_items.append((b,name))
    app.collapse_button=action_button(app.sidebar,'☰  Thu gọn menu',app.toggle_sidebar)
    app.collapse_button.pack(fill='x',padx=8,pady=(10,5))
    tk.Frame(app.sidebar,bg=P['sidebar']).pack(fill='both',expand=True)
    ui_label(app.sidebar,'V16.0.14  ·  LOCAL',8,color=P['muted'],bg=P['sidebar']).pack(anchor='w',padx=15,pady=16)

    app.quick=tk.Frame(app.body,bg=P['base'],width=255)
    app.quick.pack(side='right',fill='y',padx=(12,0));app.quick.pack_propagate(False)
    center=tk.Frame(app.body,bg=P['base'])
    center.pack(side='left',fill='both',expand=True)
    viewport=tk.Canvas(center,bg=P['base'],highlightthickness=0,bd=0)
    scroll=ttk.Scrollbar(center,orient='vertical',command=viewport.yview)
    scroll.pack(side='right',fill='y')
    viewport.pack(side='left',fill='both',expand=True)
    viewport.configure(yscrollcommand=scroll.set)
    app.main_panel=tk.Frame(viewport,bg=P['base'])
    content_id=viewport.create_window((0,0),window=app.main_panel,anchor='nw')
    app.main_panel.bind('<Configure>',lambda _:viewport.configure(scrollregion=viewport.bbox('all')))
    viewport.bind('<Configure>',lambda event:viewport.itemconfigure(content_id,width=event.width))
    def wheel(event):
        viewport.yview_scroll(-1 if event.delta>0 else 1,'units')
    def wheel_linux(direction):
        viewport.yview_scroll(direction,'units')
    def enter(_):
        viewport.bind_all('<MouseWheel>',wheel)
        viewport.bind_all('<Button-4>',lambda e:wheel_linux(-1))
        viewport.bind_all('<Button-5>',lambda e:wheel_linux(1))
    def leave(_):
        viewport.unbind_all('<MouseWheel>')
        viewport.unbind_all('<Button-4>')
        viewport.unbind_all('<Button-5>')
    viewport.bind('<Enter>',enter)
    viewport.bind('<Leave>',leave)
    app.main_viewport=viewport
    main=app.main_panel
    top=tk.Frame(main,bg=P['base']);top.pack(fill='x',pady=(0,8))
    ui_label(top,'Tổng quan vận hành',17,strong=True).pack(side='left')
    tk.Label(top,textvariable=app.header_status,bg=P['base'],fg=P['green'],font=('Segoe UI',9)).pack(side='right')

    metrics=tk.Frame(main,bg=P['base']);metrics.pack(fill='x',pady=(0,11))
    app.metric_cards={}
    for i,(key,name,accent) in enumerate((('cpu','CPU','blue'),('ram','RAM','violet'),('disk','Ổ đĩa sao lưu','green'),('backup','Trạng thái sao lưu','amber'))):
        metric=MetricCard(metrics,name,accent=accent)
        metric.pack(side='left',fill='x',expand=True,padx=(0,8) if i<3 else 0)
        app.metric_cards[key]=metric

    account=_make_card(main,'BƯỚC 1   ·   CHỌN HỘP THƯ CẦN SAO LƯU')
    mode_row=tk.Frame(account,bg=P['card']);mode_row.pack(fill='x',pady=(0,6))
    for name,key in (('Một hộp thư','employee'),('Nhiều hộp thư được ủy quyền','admin')):
        ttk.Radiobutton(mode_row,text=name,variable=app.mode,value=key,command=app.switch_mode,
                        style='OpsRadio.TRadiobutton').pack(side='left',padx=(0,20))
    app.account_area=tk.Frame(account,bg=P['card']);app.account_area.pack(fill='x')
    app.single_frame=tk.Frame(app.account_area,bg=P['card']);app.single_frame.pack(fill='x')
    ui_label(app.single_frame,'Địa chỉ email (khác với tên đăng nhập ứng dụng)',9,color=P['muted']).pack(anchor='w')
    ttk.Entry(app.single_frame,textvariable=app.account,style='OpsEntry.TEntry').pack(fill='x',pady=(4,0))
    app.multi_frame=tk.Frame(app.account_area,bg=P['card'])
    ui_label(app.multi_frame,'Mỗi dòng một hộp thư đã được cấp quyền',9,color=P['muted']).pack(anchor='w')
    app.accounts_box=tk.Text(app.multi_frame,height=3,background=P['card_light'],foreground=P['white'],
                             insertbackground=P['white'],font=('Segoe UI',10),relief='flat',padx=8,pady=6)
    app.accounts_box.pack(fill='x',pady=(4,0))
    ui_label(account,'Chỉ thao tác Email/Sao lưu mới yêu cầu mật khẩu IMAP. Mạng, IT và PMC sử dụng phiên đăng nhập ứng dụng.',
             9,color=P['muted'],wraplength=680,justify='left').pack(anchor='w',pady=(8,0))

    operations=_make_card(main,'BƯỚC 2   ·   KHỞI CHẠY VÀ THEO DÕI')
    btns=tk.Frame(operations,bg=P['card']);btns.pack(fill='x',pady=(0,9))
    app.start_button=action_button(btns,'▶   BẮT ĐẦU SAO LƯU   Ctrl+Enter',app.start,variant='primary')
    app.start_button.pack(side='left',padx=(0,8))
    app.stop_button=action_button(btns,'■   DỪNG AN TOÀN',app.request_stop,variant='danger')
    app.stop_button.configure(state='disabled');app.stop_button.pack(side='left',padx=(0,8))
    app.inspect_button=action_button(btns,'⌕   Kiểm tra IMAP',app.inspect)
    app.inspect_button.pack(side='left')
    app.progress=ttk.Progressbar(operations,mode='indeterminate',style='OpsProgress.Horizontal.TProgressbar')
    app.progress.pack(fill='x',pady=(4,6))
    ui_label(operations,'Không ước tính %/ETA nếu máy chủ chưa cung cấp tổng số email.',9,color=P['muted']).pack(anchor='w')
    tk.Label(operations,textvariable=app.stats_line,bg=P['card'],fg=P['green'],
             font=('Segoe UI',9,'bold'),anchor='w').pack(fill='x',pady=(5,0))

    storage=_make_card(main,'BƯỚC 3   ·   LƯU TRỮ VÀ CẤU HÌNH')
    folder=tk.Frame(storage,bg=P['card']);folder.pack(fill='x',pady=(0,9))
    ttk.Entry(folder,textvariable=app.destination,style='OpsEntry.TEntry').pack(side='left',fill='x',expand=True)
    action_button(folder,'📁  Chọn',app.pick).pack(side='left',padx=(6,0))
    action_button(folder,'↗  Mở',app.open_destination).pack(side='left',padx=(6,0))
    settings=tk.Frame(storage,bg=P['card']);settings.pack(fill='x')
    ui_label(settings,'Luồng',9,color=P['muted']).pack(side='left')
    ttk.Combobox(settings,textvariable=app.worker_count,values=('1','2','3','5'),width=4,state='readonly',style='OpsCombo.TCombobox').pack(side='left',padx=(5,16))
    ui_label(settings,'Giới hạn MB/s',9,color=P['muted']).pack(side='left')
    ttk.Entry(settings,textvariable=app.speed_limit,width=7,style='OpsEntry.TEntry').pack(side='left',padx=(5,12))
    ui_label(settings,'Cấu trúc',9,color=P['muted']).pack(side='left')
    ttk.Combobox(settings,textvariable=app.folder_layout,values=tuple(app.folder_layout_choices),width=26,
                 state='readonly',style='OpsCombo.TCombobox').pack(side='left',fill='x',expand=True,padx=(5,0))

    # Only actual CPU readings populate this graph. No placeholder numbers.
    trend=_make_card(main,'DIỄN BIẾN TẢI CPU · GIÁ TRỊ THỰC TẾ')
    app.cpu_graph=Sparkline(trend)
    app.cpu_graph.pack(fill='x')

    health=_make_card(app.quick,'●  SỨC KHỎE THIẾT BỊ')
    app.health_var=tk.StringVar(value='Đang đọc chỉ số thực...')
    tk.Label(health,textvariable=app.health_var,bg=P['card'],fg=P['muted'],font=('Segoe UI',10),
             wraplength=210,justify='left').pack(anchor='w')
    quick=_make_card(app.quick,'⚡  THAO TÁC 1-CLICK')
    for name,callback in [('⌕  Kiểm tra mạng/DNS',app.diagnose),
                          ('▤  Dung lượng Mail',app.open_mail_quota),
                          ('◇  Quét thiết bị LAN',lambda:app.open_infrastructure('monitor')),
                          ('⌁  IP / VPN',app.open_network_manager),
                          ('▣  Báo cáo sao lưu',app.export_usage)]:
        action_button(quick,name,callback).pack(fill='x',pady=3)
    alerts=_make_card(app.quick,'◆  TRẠNG THÁI / CẢNH BÁO')
    app.alert_var=tk.StringVar(value='Chưa ghi nhận sự cố. Số liệu sẽ cập nhật sau kiểm tra.')
    tk.Label(alerts,textvariable=app.alert_var,bg=P['card'],fg=P['muted'],
             font=('Segoe UI',9),wraplength=210,justify='left').pack(anchor='w')
    action_button(alerts,'Xem danh sách lỗi',app.show_issues).pack(fill='x',pady=(10,0))
    ui_label(app.quick,'Ctrl+K · Ctrl+L  · Ctrl+Enter',8,color=P['muted']).pack(anchor='w',padx=7,pady=5)

    bar=tk.Frame(app.logs_card,bg=P['card']);bar.pack(fill='x')
    ui_label(bar,'▤  LIVE CONSOLE  ·  LOG HỆ THỐNG',9,strong=True).pack(side='left')
    action_button(bar,'Ẩn/hiện   Ctrl+L',app.toggle_logs).pack(side='right')
    app.log_details=tk.Frame(app.logs_card,bg=P['card']);app.log_details.pack(fill='x',pady=(8,0))
    app.logs=tk.Text(app.log_details,height=6,wrap='word',state='disabled',font=('Consolas',9),
                     bg='#071120',fg=P['white'],insertbackground=P['white'],relief='flat',padx=10,pady=7)
    app.logs.pack(side='left',fill='both',expand=True)
    scrollbar=ttk.Scrollbar(app.log_details,orient='vertical',command=app.logs.yview)
    scrollbar.pack(side='right',fill='y');app.logs.configure(yscrollcommand=scrollbar.set)
    for name,col in [('error',P['red']),('success',P['green']),('info','#C7D9F4')]:
        app.logs.tag_configure(name,foreground=col)
    app.logs_open=True;app.toggle_logs()
