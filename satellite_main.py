import os
import sys
from glob import glob
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
import tkfilebrowser
from custom_calendar import CustomDateEntry
from satellite_config import *

def set_title(pnam):
    global start_date
    global end_date
    global first_date
    global last_date
    global field_data
    global drone_analysis
    global s1_data
    global s1_analysis
    global s2_data
    global s2_analysis
    if pnam is None:
        block = obs_block
        dstr = obs_date
    else:
        start_date = top_start.get()
        end_date = top_end.get()
        first_date = top_first.get()
        last_date = top_last.get()
        block = top_cmb.get()
        dstr = top_cde.get()
        field_data = top_var['field_data'].get()
        drone_analysis = top_var['drone_analysis'].get()
        s1_data = top_var['s1_data'].get()
        s1_analysis = top_var['s1_analysis'].get()
        s2_data = top_var['s2_data'].get()
        s2_analysis = top_var['s2_analysis'].get()
    for proc in pnams:
        modules[proc].start_date = start_date
        modules[proc].end_date = end_date
        modules[proc].first_date = first_date
        modules[proc].last_date = last_date
        modules[proc].obs_block = block
        modules[proc].obs_date = dstr
        modules[proc].field_data = field_data
        modules[proc].drone_analysis = drone_analysis
        modules[proc].s1_data = s1_data
        modules[proc].s1_analysis = s1_analysis
        modules[proc].s2_data = s2_data
        modules[proc].s2_analysis = s2_analysis
    now_dtim = datetime.now()
    start_dtim = datetime.strptime(start_date,date_fmt)
    end_dtim = datetime.strptime(end_date,date_fmt)
    first_dtim = datetime.strptime(first_date,date_fmt)
    last_dtim = datetime.strptime(last_date,date_fmt)
    # atcor
    proc_pnam = 'mask_fnam'
    proc_atcor.values[proc_pnam] = os.path.join(s2_analysis,'paddy_mask.tif')
    proc_pnam = 'stat_fnam'
    proc_atcor.values[proc_pnam] = os.path.join(s2_analysis,'atcor_stat.tif')
    proc_pnam = 'inds_fnam'
    proc_atcor.values[proc_pnam] = os.path.join(s2_analysis,'nearest_inds.npy')
    proc_pnam = 'stat_period'
    data_tmin = (first_dtim+relativedelta(years=-2)).strftime(date_fmt)
    data_tmax = last_dtim.strftime(date_fmt)
    proc_atcor.values[proc_pnam][0] = data_tmin
    proc_atcor.values[proc_pnam][1] = data_tmax
    if proc_atcor.center_var is not None:
        for proc_pnam in ['mask_fnam','stat_fnam','inds_fnam']:
            proc_atcor.center_var[proc_pnam].set(proc_atcor.values[proc_pnam])
        proc_pnam = 'stat_period'
        proc_atcor.center_var[proc_pnam][0].set(data_tmin)
        proc_atcor.center_var[proc_pnam][1].set(data_tmax)
    # interp
    proc_pnam = 'cflag_period'
    data_tmin = first_dtim+relativedelta(months=-6)
    data_tmax = last_dtim+relativedelta(months=6)
    if data_tmax > now_dtim:
        data_tmax = now_dtim
    data_tmin = data_tmin.strftime(date_fmt)
    data_tmax = data_tmax.strftime(date_fmt)
    proc_interp.values[proc_pnam][0] = data_tmin
    proc_interp.values[proc_pnam][1] = data_tmax
    if proc_interp.center_var is not None:
        proc_interp.center_var[proc_pnam][0].set(data_tmin)
        proc_interp.center_var[proc_pnam][1].set(data_tmax)
    # phenology
    proc_pnam = 'trans_fnam'
    proc_phenology.values[proc_pnam] = os.path.join(s1_analysis,'planting','{:%Y%m%d}_{:%Y%m%d}_planting.csv'.format(start_dtim,end_dtim))
    dt = (end_dtim-start_dtim).total_seconds()
    trans_pref = (start_dtim+timedelta(seconds=dt/2)).strftime(date_fmt)
    proc_pnam = 'trans_pref'
    proc_phenology.values[proc_pnam] = trans_pref
    if proc_phenology.center_var is not None:
        for proc_pnam in ['trans_fnam','trans_pref']:
            proc_phenology.center_var[proc_pnam].set(proc_phenology.values[proc_pnam])
    # extract
    proc_pnam = 'obs_fnam'
    if 'Field' in proc_extract.values['obs_src']:
        proc_extract.values[proc_pnam] = os.path.join(field_data,block,'Excel_File','{}_{}.xls'.format(block,dstr))
    else:
        proc_extract.values[proc_pnam] = os.path.join(drone_analysis,'extract','{}_{}_observation.csv'.format(block,dstr))
    proc_pnam = 'event_fnam'
    proc_extract.values[proc_pnam] = os.path.join(s2_analysis,'phenology','{:%Y%m%d}_{:%Y%m%d}_assess.csv'.format(start_dtim,end_dtim))
    if proc_extract.center_var is not None:
        for proc_pnam in ['obs_fnam','event_fnam']:
            proc_extract.center_var[proc_pnam].set(proc_extract.values[proc_pnam])
    # formula
    proc_pnam = 'inp_fnams'
    dnam = os.path.join(s2_analysis,'extract')
    fnams = glob(os.path.join(dnam,'*_extract.csv'))
    if len(fnams) > 0:
        proc_formula.values[proc_pnam] = '\n'.join(sorted(fnams))
    else:
        proc_formula.values[proc_pnam] = os.path.join(dnam,'{}_{}_extract.csv'.format(block,dstr))
    if proc_formula.center_var is not None:
        try:
            proc_formula.center_inp[proc_pnam].delete('1.0',tk.END)
            proc_formula.center_inp[proc_pnam].insert('1.0',proc_formula.values[proc_pnam])
        except Exception:
            pass
        proc_formula.center_var[proc_pnam].set(proc_formula.values[proc_pnam])
    # extract
    proc_pnam = 'event_fnam'
    proc_estimate.values[proc_pnam] = os.path.join(s2_analysis,'phenology','{:%Y%m%d}_{:%Y%m%d}_assess.csv'.format(start_dtim,end_dtim))
    if proc_estimate.center_var is not None:
        for proc_pnam in ['event_fnam']:
            proc_estimate.center_var[proc_pnam].set(proc_estimate.values[proc_pnam])
    if pnam is None:
        return
    # change color
    root.focus_set()
    if pnam == 'planting':
        style = ttk.Style()
        style.configure('top_start.DateEntry',foreground='black')
        style.configure('top_end.DateEntry',foreground='black')
    elif pnam == 'download':
        style = ttk.Style()
        style.configure('top_first.DateEntry',foreground='black')
        style.configure('top_last.DateEntry',foreground='black')
    elif pnam == 'observation':
        style = ttk.Style()
        style.map('top_cmb.TCombobox',
                  foreground=[('!readonly','!focus','black'),('!readonly','focus','black')],
                  selectforeground=[('!readonly','!focus','black'),('!readonly','focus','black')],)
        style.configure('top_cde.DateEntry',foreground='black')
    elif pnam in top_box:
        top_box[pnam].config(foreground='black')
    #top_err[pnam].pack(pady=(0,3),side=tk.LEFT)
    for proc in pnams:
        check_child(proc)
    return

def change_color(pnam):
    if pnam == 'start_date':
        start_dtim = datetime.strptime(top_start.get(),date_fmt)
        first_dtim = start_dtim-timedelta(days=90)
        top_first.set_date(first_dtim)
        style = ttk.Style()
        style.configure('top_start.DateEntry',foreground='red')
        style.configure('top_first.DateEntry',foreground='red')
    elif pnam == 'end_date':
        end_dtim = datetime.strptime(top_end.get(),date_fmt)
        last_dtim = end_dtim+timedelta(days=210)
        top_last.set_date(last_dtim)
        style = ttk.Style()
        style.configure('top_end.DateEntry',foreground='red')
        style.configure('top_last.DateEntry',foreground='red')
    elif pnam == 'first_date':
        style = ttk.Style()
        style.configure('top_first.DateEntry',foreground='red')
    elif pnam == 'last_date':
        style = ttk.Style()
        style.configure('top_last.DateEntry',foreground='red')
    elif pnam == 'block':
        style = ttk.Style()
        style.map('top_cmb.TCombobox',
                  foreground=[('!readonly','!focus','red'),('!readonly','focus','red')],
                  selectforeground=[('!readonly','!focus','red'),('!readonly','focus','red')],)
    elif pnam == 'date':
        style = ttk.Style()
        style.configure('top_cde.DateEntry',foreground='red')
    elif pnam in top_box:
        top_box[pnam].config(foreground='red')
    return True

def ask_folder(pnam,dnam=None):
    if dnam is None:
        dnam = eval(pnam)
    path = tkfilebrowser.askopendirname(initialdir=dnam)
    if len(path) > 0:
        top_var[pnam].set(path)
    if pnam in top_box:
        top_box[pnam].config(foreground='red')
    return

def run_all():
    for pnam in pnams:
        if center_var[pnam].get():
            modules[pnam].run()
    return

def set_child(pnam):
    modules[pnam].set(root,center_var)

def check_child(pnam):
    for p in pnams:
        if p != pnam:
            continue
        if center_var[pnam].get():
            check_values,check_errors = modules[pnam].check_all(source='value')
            err = False
            for error in check_errors.values():
                if hasattr(error,'__iter__'):
                    for e in error:
                        if e:
                            err = True
                            break
                else:
                    if error:
                        err = True
                if err:
                    break
            if err:
                right_lbl[pnam].pack(side=tk.LEFT)
            else:
                right_lbl[pnam].pack_forget()
        else:
            right_lbl[pnam].pack_forget()
    return

def exit():
    sys.exit()
    return

if no_gui:
    set_title(None)
    for pnam in pnams:
        if defaults[pnam]:
            modules[pnam].run()
    exit()
root = tk.Tk()
root.title('BLB Damage Estimation - Satellite version')
root.geometry('{}x{}'.format(window_width,305+30*len(pnams)))
top_frame = tk.Frame(root,width=10,height=top_frame_height,background=None)
middle_frame = tk.Frame(root,width=10,height=20,background=None)
bottom_frame = tk.Frame(root,width=10,height=40,background=None)
left_frame = tk.Frame(middle_frame,width=left_frame_width,height=10,background=None)
center_canvas = tk.Canvas(middle_frame,width=30,height=10,background=None)
right_frame = tk.Frame(middle_frame,width=right_frame_width,height=10,background=None)
top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.TOP)
middle_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,expand=True)
bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.BOTTOM)
left_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
center_canvas.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
right_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.RIGHT)
top_frame.pack_propagate(False)
middle_frame.pack_propagate(False)
bottom_frame.pack_propagate(False)
left_frame.pack_propagate(False)
center_canvas.pack_propagate(False)
right_frame.pack_propagate(False)

top_left_frame = tk.Frame(top_frame,width=left_frame_width,height=10,background=None)
top_center_frame = tk.Frame(top_frame,width=30,height=10,background=None)
top_right_frame = tk.Frame(top_frame,width=right_frame_width,height=10,background=None)
top_left_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
top_center_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
top_right_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.RIGHT)
top_left_frame.pack_propagate(False)
top_center_frame.pack_propagate(False)
top_right_frame.pack_propagate(False)

top_center_top_frame = tk.Frame(top_center_frame,width=30,height=10,background=None)
top_center_middle_frame = tk.Frame(top_center_frame,width=30,height=10,background=None)
top_center_bottom_frame = tk.Frame(top_center_frame,width=30,height=10,background=None)
top_center_top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)
top_center_middle_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)
top_center_bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)

top_right_top_frame = tk.Frame(top_right_frame,width=30,height=10,background=None)
top_right_middle_frame = tk.Frame(top_right_frame,width=30,height=10,background=None)
top_right_bottom_frame = tk.Frame(top_right_frame,width=30,height=10,background=None)
top_right_top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)
top_right_middle_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.TOP,expand=True)
top_right_bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.TOP)
top_right_top_frame.pack_propagate(False)
top_right_middle_frame.pack_propagate(False)

top_lbl = {}
top_btn = {}
top_err = {}
top_img = {}
top_sep = {}
top_box = {}
top_var = {}
btn_pnam = 'set'

top_center_bottom_cnv = {}
top_center_left_cnv = {}
top_center_right_cnv = {}
top_right_bottom_cnv = {}
browse_img = tk.PhotoImage(file=browse_image)
for pnam,title in zip(['planting','download','observation','field_data','drone_analysis','s1_data','s1_analysis','s2_data','s2_analysis'],
                      ['Planting Start/End','Data First/Last','Observation Block/Date',
                       'Field Data','Drone Analysis','Sentinel-1 Data','Sentinel-1 Analysis','Sentinel-2 Data','Sentinel-2 Analysis']):
    top_center_bottom_cnv[pnam] = tk.Canvas(top_center_bottom_frame,width=10,height=25)
    top_center_bottom_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,expand=True)
    top_center_left_cnv[pnam] = tk.Canvas(top_center_bottom_cnv[pnam],width=150,height=25)
    top_center_left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.LEFT)
    top_center_left_cnv[pnam].pack_propagate(False)
    top_center_right_cnv[pnam] = tk.Canvas(top_center_bottom_cnv[pnam],width=10,height=25)
    top_center_right_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.LEFT,expand=True)
    top_lbl[pnam] = tk.Label(top_center_left_cnv[pnam],text=title)
    top_lbl[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(3,3),anchor=tk.W,side=tk.LEFT,expand=False)
    top_sep[pnam] = ttk.Separator(top_center_left_cnv[pnam],orient='horizontal')
    top_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=0,fill=tk.X,side=tk.LEFT,expand=True)
    if pnam == 'planting':
        box_pnam = 'start_date'
        myfont = font.Font(root,family='',size=9,weight='normal')
        top_start = CustomDateEntry(top_center_right_cnv[pnam],width=10,date_pattern=date_format,style='top_start.DateEntry')
        if start_date != '':
            top_start.set_date(start_date)
        top_start.pack(ipadx=0,ipady=0,padx=(0,1),pady=(0,0),fill=tk.X,side=tk.LEFT,expand=True)
        top_start.config(validatecommand=eval('lambda:change_color("{}")'.format(box_pnam)),validate='focusout')
        box_pnam = 'end_date'
        top_end = CustomDateEntry(top_center_right_cnv[pnam],width=10,date_pattern=date_format,style='top_end.DateEntry')
        if end_date != '':
            top_end.set_date(end_date)
        top_end.pack(ipadx=0,ipady=0,padx=(0,1),pady=(0,0),fill=tk.X,side=tk.LEFT,expand=True)
        top_end.config(validatecommand=eval('lambda:change_color("{}")'.format(box_pnam)),validate='focusout')
    elif pnam == 'download':
        box_pnam = 'first_date'
        myfont = font.Font(root,family='',size=9,weight='normal')
        top_first = CustomDateEntry(top_center_right_cnv[pnam],width=10,date_pattern=date_format,style='top_first.DateEntry')
        if first_date != '':
            top_first.set_date(first_date)
        top_first.pack(ipadx=0,ipady=0,padx=(0,1),pady=(0,0),fill=tk.X,side=tk.LEFT,expand=True)
        top_first.config(validatecommand=eval('lambda:change_color("{}")'.format(box_pnam)),validate='focusout')
        box_pnam = 'last_date'
        top_last = CustomDateEntry(top_center_right_cnv[pnam],width=10,date_pattern=date_format,style='top_last.DateEntry')
        if last_date != '':
            top_last.set_date(last_date)
        top_last.pack(ipadx=0,ipady=0,padx=(0,1),pady=(0,0),fill=tk.X,side=tk.LEFT,expand=True)
        top_last.config(validatecommand=eval('lambda:change_color("{}")'.format(box_pnam)),validate='focusout')
    elif pnam == 'observation':
        box_pnam = 'block'
        myfont = font.Font(root,family='',size=9,weight='normal')
        #top_cmb = ttk.Combobox(top_center_right_cnv[pnam],width=10,style='top_cmb.TCombobox',font=myfont,values=['Block-'+block for block in blocks])
        top_cmb = ttk.Combobox(top_center_right_cnv[pnam],width=10,style='top_cmb.TCombobox',values=['Block-'+block for block in blocks])
        style = ttk.Style()
        style.map('top_cmb.TCombobox',
                  fieldbackground=[('!readonly','!focus','white'),('!readonly','focus','white')],
                  selectbackground=[('!readonly','!focus','white'),('!readonly','focus','white')],)
        if obs_block != '':
            top_cmb.set(obs_block)
        else:
            top_cmb.current(0)
        top_cmb.pack(ipadx=0,ipady=0,padx=(0,1),pady=(0,0),fill=tk.X,side=tk.LEFT,expand=True)
        top_cmb.config(validatecommand=eval('lambda:change_color("{}")'.format(box_pnam)),validate='focusout')
        box_pnam = 'date'
        top_cde = CustomDateEntry(top_center_right_cnv[pnam],width=10,date_pattern=date_format,style='top_cde.DateEntry')
        if obs_date != '':
            top_cde.set_date(obs_date)
        top_cde.pack(ipadx=0,ipady=0,padx=(0,1),pady=(0,0),fill=tk.X,side=tk.LEFT,expand=True)
        top_cde.config(validatecommand=eval('lambda:change_color("{}")'.format(box_pnam)),validate='focusout')
    else:
        top_var[pnam] = tk.StringVar()
        top_var[pnam].set(eval(pnam))
        top_box[pnam] = tk.Entry(top_center_right_cnv[pnam],textvariable=top_var[pnam])
        top_box[pnam].pack(ipadx=0,ipady=0,padx=(0,1),pady=(3,0),anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
        top_box[pnam].config(validatecommand=eval('lambda:change_color("{}")'.format(pnam)),validate='focusout')
        top_img[pnam] = tk.Button(top_center_right_cnv[pnam],image=browse_img,width=center_btn_width,bg='white',bd=1,command=eval('lambda:ask_folder("{}")'.format(pnam)))
        top_img[pnam].image = browse_img
        top_img[pnam].pack(ipadx=0,ipady=0,padx=(0,1),pady=0,anchor=tk.W,side=tk.LEFT)
    top_right_bottom_cnv[pnam] = tk.Canvas(top_right_bottom_frame,width=10,height=25)
    top_right_bottom_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,expand=True)
    top_btn[pnam] = tk.Button(top_right_bottom_cnv[pnam],text=btn_pnam.capitalize(),width=4,command=eval('lambda:set_title("{}")'.format(pnam)))
    top_btn[pnam].pack(padx=(1,0),pady=(0,2.2),side=tk.LEFT)
    top_err[pnam] = ttk.Label(top_right_bottom_cnv[pnam],text='ERROR',foreground='red')

bottom_lbl = {}
bottom_btn = {}
pnam = 'left'
bottom_lbl[pnam] = tk.Label(bottom_frame,text='')
bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)
pnam = 'run'
bottom_btn[pnam] = tk.Button(bottom_frame,text=pnam.capitalize(),width=8,command=run_all)
bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
pnam = 'exit'
bottom_btn[pnam] = tk.Button(bottom_frame,text=pnam.capitalize(),width=8,command=exit)
bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
pnam = 'right'
bottom_lbl[pnam] = tk.Label(bottom_frame,text='')
bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)

bgs = [None,None]
center_var = {}
center_cnv = {}
center_chk = {}
center_sep = {}
left_cnv = {}
left_btn = {}
right_cnv = {}
right_btn = {}
right_lbl = {}
for i,pnam in enumerate(pnams):
    center_var[pnam] = tk.BooleanVar()
    center_var[pnam].set(defaults[pnam])
    center_cnv[pnam] = tk.Canvas(center_canvas,background=bgs[i%2])
    center_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2),fill=tk.X,expand=True)
    center_chk[pnam] = tk.Checkbutton(center_cnv[pnam],background=bgs[i%2],variable=center_var[pnam],text=titles[pnam],command=eval('lambda:check_child("{}")'.format(pnam)))
    center_chk[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
    center_sep[pnam] = ttk.Separator(center_cnv[pnam],orient='horizontal')
    center_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=0,fill=tk.X,side=tk.LEFT,expand=True)
    left_cnv[pnam] = tk.Canvas(left_frame,width=left_frame_width,height=left_cnv_height,background=bgs[i%2])
    left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,expand=True)
    left_btn[pnam] = ttk.Button(root,text='check_{}'.format(pnam),command=eval('lambda:check_child("{}")'.format(pnam)))
    left_btn[pnam].pack_forget() # hidden
    right_cnv[pnam] = tk.Canvas(right_frame,width=right_frame_width,height=right_cnv_height,background=bgs[i%2])
    right_cnv[pnam].pack(ipadx=0,ipady=0,padx=(0,20),pady=(0,2),expand=True)
    right_cnv[pnam].pack_propagate(False)
    right_btn[pnam] = tk.Button(right_cnv[pnam],text='Set',width=4,command=eval('lambda:set_child("{}")'.format(pnam)))
    right_btn[pnam].pack(side=tk.LEFT)
    right_lbl[pnam] = ttk.Label(right_cnv[pnam],text='ERROR',foreground='red')
set_title('block')
for pnam in pnams:
    check_child(pnam)
root.mainloop()
