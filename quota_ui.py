"""Tkinter window for read-only mailbox quota monitoring."""
import imaplib
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from mail_quota import HOST, PORT, QuotaResult, probe_quota, export_quota_csv


def fmt_bytes(number):
    if number is None:
        return '—'
    return f'{number / (1024 ** 3):.2f} GB'


class QuotaWindow:
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.title('Mailbox Storage | Alibaba Operations Center')
        self.win.geometry('1040x650')
        self.win.minsize(820, 530)
        self.results = {}
        self.running = False
        self.host = tk.StringVar(value=HOST)
        self.port = tk.StringVar(value=str(PORT))
        self.address = tk.StringVar()
        self.status = tk.StringVar(value='Chưa có kết quả. Chỉ truy vấn hộp thư bạn có quyền đăng nhập.')
        self._render()

    def _render(self):
        from industrial_theme import BG, MUTED
        self.win.configure(bg=BG)
        panel = ttk.Frame(self.win, padding=20)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='DUNG LƯỢNG HỘP THƯ', style='Title.TLabel').pack(anchor='w')
        ttk.Label(panel, text='IMAP QUOTA • Read-only • Không lưu mật khẩu • Không tự quét toàn bộ nhân viên',
                  foreground=MUTED).pack(anchor='w', pady=(0, 18))
        form = ttk.LabelFrame(panel, text=' Kiểm tra tài khoản được cấp quyền ', padding=14)
        form.pack(fill='x', pady=(0, 12))
        row = ttk.Frame(form, style='Card.TFrame')
        row.pack(fill='x')
        for label, var, width in [('IMAP Host', self.host, 29), ('Port', self.port, 7), ('Email', self.address, 32)]:
            ttk.Label(row, text=label, style='Card.TLabel').pack(side='left', padx=(8, 5))
            ttk.Entry(row, textvariable=var, width=width).pack(side='left')
        controls = ttk.Frame(form, style='Card.TFrame')
        controls.pack(fill='x', pady=(12, 0))
        self.check_btn = ttk.Button(controls, text='Kiểm tra QUOTA', style='Primary.TButton', command=self.check)
        self.check_btn.pack(side='left', padx=(0, 8))
        ttk.Button(controls, text='Xuất kết quả CSV', command=self.export).pack(side='left')
        ttk.Label(form, text='Mỗi lần kiểm tra cần đăng nhập hộp thư tương ứng. Quyền admin web không tự cho phép đọc quota qua IMAP.',
                  style='Muted.TLabel').pack(anchor='w', pady=(10, 0))
        table = ttk.Frame(panel)
        table.pack(fill='both', expand=True)
        cols = ('email', 'used', 'limit', 'free', 'percent', 'status')
        self.tree = ttk.Treeview(table, columns=cols, show='headings', height=11)
        for key, title, width in [('email','Tài khoản',260),('used','Đã dùng',125),('limit','Hạn mức',125),
                                  ('free','Còn lại',125),('percent','Sử dụng',100),('status','Trạng thái',160)]:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, stretch=(key == 'email'))
        self.tree.pack(side='left', fill='both', expand=True)
        ttk.Scrollbar(table, command=self.tree.yview).pack(side='right', fill='y')
        ttk.Label(panel, textvariable=self.status, foreground=MUTED, wraplength=900).pack(anchor='w', pady=(10, 0))
        ttk.Label(panel, text='Không có QUOTA? Hãy xuất báo cáo dung lượng từ trang quản trị Alibaba Mail để đối chiếu.',
                  foreground=MUTED).pack(anchor='w', pady=(6, 0))

    def check(self):
        if self.running:
            return
        email = self.address.get().strip()
        host = self.host.get().strip()
        try:
            port = int(self.port.get())
            if not 1 <= port <= 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror('Lỗi', 'Cổng IMAP phải là số từ 1 đến 65535.', parent=self.win)
            return
        if not email or not host:
            messagebox.showwarning('Thiếu dữ liệu', 'Nhập email và máy chủ IMAP.', parent=self.win)
            return
        password = simpledialog.askstring('Xác thực', f'Mật khẩu hoặc app password cho {email}:',
                                          show='*', parent=self.win)
        if not password:
            return
        self.running = True
        self.check_btn.configure(state='disabled')
        self.status.set('Đang kết nối IMAP an toàn...')
        def worker():
            try:
                result = probe_quota(email, password, host=host, port=port)
                error = None
            except (imaplib.IMAP4.error, OSError, ValueError, socket.timeout) as exc:
                result, error = None, type(exc).__name__ + ': ' + str(exc)
            finally:
                password_local = None  # Password is never persisted
            def finish():
                if not self.win.winfo_exists():
                    return
                self.running = False
                self.check_btn.configure(state='normal')
                if error:
                    self.status.set('Thất bại: ' + error)
                    return
                self.results[result.email] = result
                self.tree.delete(*self.tree.get_children())
                for item in self.results.values():
                    self.tree.insert('', 'end', values=(item.email, fmt_bytes(item.used_bytes), fmt_bytes(item.limit_bytes),
                                   fmt_bytes(item.free_bytes), f'{item.percent:.1f}%' if item.percent is not None else '—', item.status))
                self.status.set(f'{result.email}: {result.status}. {result.detail}')
            self.master.after(0, finish)
        threading.Thread(target=worker, daemon=True).start()

    def export(self):
        if not self.results:
            messagebox.showinfo('Chưa có dữ liệu', 'Hãy kiểm tra ít nhất một hộp thư.', parent=self.win)
            return
        path = filedialog.asksaveasfilename(parent=self.win, defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path:
            return
        try:
            export_quota_csv(path, self.results.values())
        except (OSError, ValueError) as exc:
            messagebox.showerror('Không thể xuất', str(exc), parent=self.win)
        else:
            messagebox.showinfo('Đã xuất', 'Đã lưu báo cáo CSV.', parent=self.win)
