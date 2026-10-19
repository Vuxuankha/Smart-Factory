"""Consistent dark styling for operations dashboard and secondary workspaces."""
import tkinter as tk
from tkinter import ttk

NAVY = '#0B1220'
BLUE = '#3B82F6'
INK = '#E5F0FF'
MUTED = '#9CB0C9'
BG = '#0F172A'
WHITE = '#17253B'
BORDER = '#2D405B'
GREEN = '#10B981'


def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass
    root.configure(background=BG)
    style.configure('.',font=('Segoe UI',10),background=BG,foreground=INK)
    style.configure('TFrame',background=BG)
    style.configure('Card.TFrame',background=WHITE)
    style.configure('Sidebar.TFrame',background=NAVY)
    style.configure('TLabel',background=BG,foreground=INK)
    style.configure('Card.TLabel',background=WHITE,foreground=INK)
    style.configure('Muted.TLabel',background=WHITE,foreground=MUTED)
    style.configure('Title.TLabel',font=('Segoe UI',20,'bold'),foreground=INK,background=BG)
    style.configure('Section.TLabel',font=('Segoe UI',11,'bold'),background=WHITE,foreground=INK)
    style.configure('Sidebar.TLabel',font=('Segoe UI',11),background=NAVY,foreground=INK)
    style.configure('SidebarSmall.TLabel',font=('Segoe UI',9),background=NAVY,foreground=MUTED)
    style.configure('TButton',font=('Segoe UI',10),padding=(11,8),borderwidth=0,
                    relief='flat',background='#203552',foreground=INK)
    style.map('TButton',background=[('active','#304F79'),('disabled','#192337')],foreground=[('disabled','#7188A4')])
    style.configure('Primary.TButton',background=BLUE,foreground='white',font=('Segoe UI',10,'bold'),padding=(14,10))
    style.map('Primary.TButton',background=[('active','#2563EB'),('disabled','#1D3854')])
    style.configure('Danger.TButton',background='#633142',foreground='white')
    style.map('Danger.TButton',background=[('active','#A44556')])
    style.configure('Nav.TButton',background=NAVY,foreground=INK,relief='flat',padding=(14,11),anchor='w')
    style.configure('TEntry',padding=7,fieldbackground='#223751',foreground=INK,insertcolor=INK)
    style.configure('TCombobox',padding=6,fieldbackground='#223751',foreground=INK,arrowcolor=INK)
    style.map('TCombobox',fieldbackground=[('readonly','#223751')],foreground=[('readonly',INK)])
    style.configure('TRadiobutton',background=WHITE,foreground=INK)
    style.configure('TLabelframe',background=BG,foreground=INK,bordercolor=BORDER,borderwidth=1,relief='solid')
    style.configure('TLabelframe.Label',background=BG,foreground=INK,font=('Segoe UI',10,'bold'))
    style.configure('TNotebook',background=BG,borderwidth=0)
    style.configure('TNotebook.Tab',background='#1A2B44',foreground='#BDCEE6',padding=(11,8))
    style.map('TNotebook.Tab',background=[('selected','#2C4670'),('active','#274063')],foreground=[('selected','white')])
    style.configure('Treeview',background='#14243C',fieldbackground='#14243C',foreground=INK,rowheight=27,borderwidth=0)
    style.map('Treeview',background=[('selected','#265A9E')],foreground=[('selected','white')])
    style.configure('Treeview.Heading',background='#244161',foreground='#F2F7FF',font=('Segoe UI',9,'bold'),relief='flat',padding=7)
    style.map('Treeview.Heading',background=[('active','#365A87')])
    style.configure('Vertical.TScrollbar', background='#28405F', troughcolor='#101B2B',
                    arrowcolor='#B7CAE5', bordercolor='#22334C', relief='flat')
    style.map('Vertical.TScrollbar',background=[('active','#40648F')])
    style.configure('Horizontal.TProgressbar',background=BLUE,troughcolor='#1C3047',thickness=9)
    return style


def decorate_dialog(win,title,subtitle=''):
    win.configure(background=BG)
    win.minsize(760,540)
    header=ttk.Frame(win,padding=(18,15))
    header.pack(fill='x')
    ttk.Label(header,text=title,style='Title.TLabel').pack(anchor='w')
    if subtitle:
        ttk.Label(header,text=subtitle,foreground=MUTED).pack(anchor='w',pady=(2,0))
    return header
