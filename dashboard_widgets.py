"""Reusable clean dark dashboard components without external GUI dependencies."""
import tkinter as tk
from collections import deque

PALETTE = {
    'base':'#0B1220', 'sidebar':'#0D1728', 'card':'#152238', 'card_light':'#1B2C45',
    'border':'#283B54','white':'#F2F7FF','muted':'#98ABC7',
    'blue':'#3B82F6','blue_hover':'#2563EB', 'green':'#10B981',
    'amber':'#F59E0B','red':'#F87171','violet':'#A78BFA',
}


def ui_label(parent, text='', size=10, color=None, strong=False, bg=None, **kwargs):
    return tk.Label(parent,text=text,fg=color or PALETTE['white'],
                    bg=bg or parent.cget('bg'),font=('Segoe UI',size,'bold' if strong else 'normal'),
                    anchor='w',**kwargs)


def action_button(parent, text, command, variant='secondary', **kwargs):
    colors = {'primary':(PALETTE['blue'],PALETTE['blue_hover']),
              'secondary':(PALETTE['card_light'],'#2A4264'),
              'danger':('#5A2638','#84344D'),
              'success':('#087E64','#0A9474')}
    bg,hover = colors[variant]
    b=tk.Button(parent,text=text,command=command,bg=bg,fg=PALETTE['white'],
                activebackground=hover,activeforeground=PALETTE['white'],
                font=('Segoe UI',10,'bold' if variant!='secondary' else 'normal'),
                relief='flat',bd=0,highlightthickness=0,padx=14,pady=10,cursor='hand2',**kwargs)
    b.bind('<Enter>',lambda e:b.configure(bg=hover))
    b.bind('<Leave>',lambda e:b.configure(bg=bg))
    return b


def card(parent,title=None,padding=14):
    outer=tk.Frame(parent,bg=PALETTE['border'],padx=1,pady=1)
    inside=tk.Frame(outer,bg=PALETTE['card'],padx=padding,pady=padding)
    inside.pack(fill='both',expand=True)
    if title:
        ui_label(inside,title,size=10,strong=True).pack(anchor='w',pady=(0,11))
    return outer,inside


def badge(parent,text,color='green'):
    frame=tk.Frame(parent,bg=PALETTE['card_light'],padx=8,pady=4)
    dot=tk.Canvas(frame,width=9,height=9,background=PALETTE['card_light'],highlightthickness=0)
    dot.create_oval(1,1,8,8,fill=PALETTE.get(color,color),outline='')
    dot.pack(side='left',padx=(0,5))
    ui_label(frame,text,8,color=PALETTE['muted'],bg=PALETTE['card_light']).pack(side='left')
    return frame


class MetricCard(tk.Frame):
    def __init__(self,parent,label,accent='blue'):
        super().__init__(parent,bg=PALETTE['border'],padx=1,pady=1)
        inner=tk.Frame(self,bg=PALETTE['card'],padx=15,pady=13)
        inner.pack(fill='both',expand=True)
        ui_label(inner,label,9,color=PALETTE['muted']).pack(anchor='w')
        self.value=tk.StringVar(value='—')
        tk.Label(inner,textvariable=self.value,fg=PALETTE.get(accent,accent),bg=PALETTE['card'],
                 font=('Segoe UI',21,'bold'),anchor='w').pack(anchor='w',pady=(7,2))
        self.subtitle=tk.StringVar(value='Chưa đo')
        tk.Label(inner,textvariable=self.subtitle,fg=PALETTE['muted'],bg=PALETTE['card'],
                 font=('Segoe UI',8),anchor='w').pack(anchor='w')

    def update_value(self,value,note=''):
        self.value.set(value)
        self.subtitle.set(note)


class Sparkline(tk.Canvas):
    """Real system readings only; never interpolate invented sample data."""
    def __init__(self,parent,color='#3B82F6'):
        super().__init__(parent,background=PALETTE['card'],height=115,highlightthickness=0)
        self.points=deque(maxlen=45)
        self.linecolor=color
        self.bind('<Configure>',lambda event:self.redraw())
    def push(self,value):
        if 0 <= float(value) <= 100:
            self.points.append(float(value));self.redraw()
    def redraw(self):
        self.delete('all')
        w,h=max(self.winfo_width(),50),max(self.winfo_height(),40)
        for pct in (0.25,0.5,0.75):
            y=int(h*pct)
            self.create_line(0,y,w,y,fill=PALETTE['border'],dash=(2,6))
        if len(self.points)<2:
            self.create_text(12,h//2,anchor='w',text='Đang thu thập số liệu thực tế...',
                             fill=PALETTE['muted'],font=('Segoe UI',9))
            return
        xy=[]
        for i,v in enumerate(self.points):
            xy.extend((12 + (w-24)*i/(max(len(self.points)-1,1)),h-14-(h-26)*v/100))
        self.create_line(*xy,fill=self.linecolor,width=2,smooth=True)
        self.create_oval(xy[-2]-3,xy[-1]-3,xy[-2]+3,xy[-1]+3,fill=self.linecolor,outline='')
