"""Login, registration and IT admin user management. Mail auth is separate."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from auth_local import AuthError, ROLE_LABELS

C = {'bg':'#0B1220','panel':'#141F32','panel2':'#1A2940','line':'#2D405B',
     'text':'#EDF4FF','muted':'#9CB0C9','blue':'#3B82F6','green':'#10B981','red':'#FB7185'}


def text_label(parent, label, size=10, bold=False, color=None, bg=None):
    return tk.Label(parent,text=label,font=('Segoe UI',size,'bold' if bold else 'normal'),
                    fg=color or C['text'],bg=bg or C['panel'],anchor='w')


def field(parent, label, secret=False):
    text_label(parent,label,9,color=C['muted']).pack(anchor='w',pady=(12,4))
    e=tk.Entry(parent,font=('Segoe UI',11),bg='#253750',fg=C['text'],
               insertbackground=C['text'],relief='flat',highlightthickness=1,
               highlightbackground=C['line'],highlightcolor=C['blue'],show='•' if secret else '')
    e.pack(fill='x',ipady=9)
    return e


def button(parent, label, action, primary=False):
    bg = C['blue'] if primary else C['panel2']
    b=tk.Button(parent,text=label,command=action,fg=C['text'],bg=bg,
                activebackground='#1D4ED8' if primary else '#253D5E',activeforeground='white',
                relief='flat',bd=0,font=('Segoe UI',10,'bold' if primary else 'normal'),
                cursor='hand2',padx=12,pady=10)
    return b


class AuthDialog:
    """Separates the local operations identity from per-mailbox IMAP credentials."""
    def __init__(self, root, store, on_success):
        self.root, self.store, self.on_success = root, store, on_success
        self.win=tk.Toplevel(root,bg=C['bg'])
        self.win.title('Alibaba Operations Center • Đăng nhập ứng dụng')
        self.win.geometry('570x680')
        self.win.minsize(510,620)
        self.win.protocol('WM_DELETE_WINDOW',self.root.destroy)
        self.win.bind('<Escape>',lambda _:self.root.destroy())
        self.form='register' if store.first_run() else 'login'
        self.draw()

    def draw(self):
        for w in self.win.winfo_children():w.destroy()
        base=tk.Frame(self.win,bg=C['bg'],padx=46,pady=20)
        base.pack(fill='both',expand=True)
        tk.Label(base,text='◆  ALIBABA',fg=C['blue'],bg=C['bg'],font=('Segoe UI',19,'bold')).pack(anchor='w',pady=(2,0))
        tk.Label(base,text='OPERATIONS CENTER  ·  SECURE WORKSPACE',fg=C['muted'],bg=C['bg'],font=('Segoe UI',9)).pack(anchor='w',pady=(0,19))
        card=tk.Frame(base,bg=C['panel'],padx=27,pady=18,highlightthickness=1,highlightbackground=C['line'])
        card.pack(fill='x')
        register=self.form=='register'
        heading='Tạo tài khoản quản trị đầu tiên' if (register and self.store.first_run()) else ('Đăng ký tài khoản nhân viên' if register else 'Đăng nhập ứng dụng')
        text_label(card,heading,15,True).pack(anchor='w')
        desc='Tài khoản ứng dụng độc lập với email Alibaba Mail. Không nhập mật khẩu email tại đây.'
        tk.Label(card,text=desc,fg=C['muted'],bg=C['panel'],wraplength=360,justify='left',font=('Segoe UI',9)).pack(anchor='w',pady=(6,5))
        self.username=field(card,'Tên đăng nhập')
        if register:self.fullname=field(card,'Họ tên hiển thị')
        self.password=field(card,'Mật khẩu ứng dụng (ít nhất 12 ký tự)',True)
        if register:self.confirm=field(card,'Xác nhận mật khẩu',True)
        self.notice=tk.Label(card,text='',fg=C['red'],bg=C['panel'],wraplength=370,justify='left')
        self.notice.pack(anchor='w',pady=(9,0))
        button(card,'TẠO TÀI KHOẢN' if register else 'ĐĂNG NHẬP',self.submit,True).pack(fill='x',pady=(12,5))
        if not (register and self.store.first_run()):
            button(card,'Đã có tài khoản? Đăng nhập' if register else 'Đăng ký tài khoản mới',self.toggle).pack(fill='x',pady=(2,4))
        note='Lần đầu: tạo 01 tài khoản quản trị IT. Các tài khoản đăng ký sau cần quản trị viên phê duyệt.'
        tk.Label(base,text=note,fg=C['muted'],bg=C['bg'],font=('Segoe UI',9),wraplength=450,justify='left').pack(anchor='w',pady=15)
        self.username.focus_set()
        self.win.bind('<Return>',lambda _:self.submit())

    def toggle(self):
        self.form='login' if self.form=='register' else 'register'
        self.draw()

    def submit(self):
        username=self.username.get()
        password=self.password.get()
        try:
            if self.form=='register':
                if password!=self.confirm.get():
                    raise AuthError('Hai lần nhập mật khẩu chưa trùng nhau.')
                result=self.store.register(username,password,self.fullname.get())
                if result=='admin_created':
                    session=self.store.authenticate(username,password)
                    self.win.destroy();self.on_success(session);return
                messagebox.showinfo('Đăng ký thành công','Tài khoản đã gửi yêu cầu. Quản trị viên IT cần phê duyệt trước khi đăng nhập.',parent=self.win)
                self.form='login';self.draw();return
            session=self.store.authenticate(username,password)
        except (AuthError,ValueError) as exc:
            self.password.delete(0,'end')
            self.notice.configure(text=str(exc))
            return
        self.win.destroy()
        self.on_success(session)


def show_manage_users(parent, auth_store, session):
    """Only an already authenticated IT admin can grant roles or disable users."""
    if not session or not session.allows('users'):
        messagebox.showerror('Phân quyền','Chỉ quản trị viên IT được quản lý người dùng.',parent=parent)
        return None
    win=tk.Toplevel(parent,bg=C['bg'])
    win.title('Quản lý tài khoản ứng dụng • RBAC')
    win.geometry('810x540');win.minsize(650,440)
    outer=tk.Frame(win,bg=C['bg'],padx=22,pady=18);outer.pack(fill='both',expand=True)
    tk.Label(outer,text='QUẢN LÝ NGƯỜI DÙNG',font=('Segoe UI',17,'bold'),bg=C['bg'],fg=C['text']).pack(anchor='w')
    tk.Label(outer,text='Đăng ký mới ở trạng thái chờ duyệt. Vai trò không thay thế quyền Windows hoặc quyền máy chủ.',bg=C['bg'],fg=C['muted']).pack(anchor='w',pady=(4,12))
    cols=('username','display_name','role','active','approved_by')
    rows=ttk.Treeview(outer,columns=cols,show='headings',selectmode='browse',height=12)
    for key,name,width in [('username','Tài khoản',135),('display_name','Họ tên',180),('role','Vai trò',115),('active','Trạng thái',90),('approved_by','Duyệt bởi',105)]:
        rows.heading(key,text=name);rows.column(key,width=width)
    rows.pack(fill='both',expand=True)
    def refresh():
        for item in rows.get_children():rows.delete(item)
        for rec in auth_store.list_users(session):
            rows.insert('','end',values=(rec['username'],rec['display_name'],ROLE_LABELS.get(rec['role'],rec['role']),
                            'Đã duyệt' if rec['active'] else 'Chờ duyệt',rec['approved_by'] or '—'))
    def selected():
        items=rows.selection()
        return rows.item(items[0],'values')[0] if items else None
    def approve(role):
        name=selected()
        if not name:return
        if not messagebox.askyesno('Xác nhận',f'Cấp vai trò {ROLE_LABELS[role]} cho {name}?',parent=win):return
        try:auth_store.approve(session,name,role);refresh()
        except (AuthError,PermissionError) as exc:messagebox.showerror('Không thể duyệt',str(exc),parent=win)
    def disable():
        name=selected()
        if not name:return
        if not messagebox.askyesno('Xác nhận',f'Vô hiệu hóa tài khoản {name}?',parent=win):return
        try:auth_store.deactivate(session,name);refresh()
        except (AuthError,PermissionError) as exc:messagebox.showerror('Không thể khóa',str(exc),parent=win)
    def show_audit():
        audit=tk.Toplevel(win,bg=C['bg'])
        audit.title('Nhật ký truy cập ứng dụng')
        audit.geometry('820x500')
        pane=tk.Frame(audit,bg=C['bg'],padx=15,pady=15)
        pane.pack(fill='both',expand=True)
        text_label(pane,'NHẬT KÝ ĐĂNG NHẬP & PHÂN QUYỀN',15,True,bg=C['bg']).pack(anchor='w',pady=(0,12))
        cols=('when_utc','actor','action','detail')
        tree=ttk.Treeview(pane,columns=cols,show='headings')
        for key,title,width in [('when_utc','Thời gian (UTC)',230),('actor','Người dùng',130),
                                ('action','Hành động',135),('detail','Chi tiết',245)]:
            tree.heading(key,text=title);tree.column(key,width=width)
        scroll=ttk.Scrollbar(pane,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side='left',fill='both',expand=True);scroll.pack(side='right',fill='y')
        for item in auth_store.audit_events(session,500):
            tree.insert('','end',values=tuple(item[k] for k in cols))

    controls=tk.Frame(outer,bg=C['bg']);controls.pack(fill='x',pady=12)
    button(controls,'Duyệt Nhân viên',lambda:approve('employee')).pack(side='left',padx=3)
    button(controls,'Duyệt Kiểm toán',lambda:approve('auditor')).pack(side='left',padx=3)
    button(controls,'Cấp Quản trị IT',lambda:approve('it_admin')).pack(side='left',padx=3)
    button(controls,'Vô hiệu hóa',disable).pack(side='left',padx=3)
    button(controls,'Nhật ký',show_audit).pack(side='left',padx=3)
    refresh()
    return win


def change_password_dialog(parent, store, session):
    old=simpledialog.askstring('Đổi mật khẩu','Mật khẩu ứng dụng hiện tại:',show='*',parent=parent)
    if old is None:return
    new=simpledialog.askstring('Đổi mật khẩu','Mật khẩu mới (ít nhất 12 ký tự):',show='*',parent=parent)
    if new is None:return
    check=simpledialog.askstring('Đổi mật khẩu','Nhập lại mật khẩu mới:',show='*',parent=parent)
    if check is None:return
    if new!=check:
        messagebox.showerror('Đổi mật khẩu','Hai lần nhập mật khẩu chưa trùng.',parent=parent);return
    try:store.change_password(session,old,new)
    except (AuthError,ValueError) as exc:messagebox.showerror('Đổi mật khẩu',str(exc),parent=parent)
    else:messagebox.showinfo('Đổi mật khẩu','Đã cập nhật mật khẩu ứng dụng.',parent=parent)
