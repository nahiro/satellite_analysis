import os
import sys
import re
from datetime import datetime
import tempfile
import random
import string
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkfilebrowser
from subprocess import call
from custom_calendar import CustomDateEntry
from proc_func import *

HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')

class Process:

    __isfrozen = False

    def __init__(self):
        self.proc_name = 'process'
        self.proc_title = 'Process Title'
        self.pnams = []
        self.params = {}
        self.param_types = {}
        self.param_range = {}
        self.defaults = {}
        self.list_sizes = {}
        self.list_labels = {}
        self.values = {}
        self.input_types = {}
        self.flag_check = {}
        self.flag_fill = {}
        self.depend_proc = {}
        self.expected = {}

        self.root_width = 1000
        self.top_frame_height = 5
        self.bottom_frame_height = 40
        self.left_frame_width = 180
        self.right_frame_width = 70
        self.middle_left_frame_width = 700
        self.left_cnv_height = 25
        self.center_cnv_height = 25
        self.right_cnv_height = 25
        self.center_btn_width = 20
        self.center_frame_width = 750
        self.text_height = 3
        self.inidir = os.path.join(HOME,'Work','Drone')
        if not os.path.isdir(self.inidir):
            self.inidir = os.path.join(HOME,'Documents')

        self.python_path = sys.executable
        self.scr_dir = os.path.join(HOME,'Script')
        self.date_format = 'yyyy-mm&mmm-dd'
        self.current_block = None
        self.current_date = None
        self.field_data = None
        self.drone_data = None
        self.drone_analysis = None
        self.browse_image = os.path.join(HOME,'Pictures','browse.png')
        self.root = None
        self.chk_btn = None
        self.left_btn = None
        self.top_frame = None
        self.middle_frame = None
        self.middle_left_canvas = None
        self.middle_left_frame = None
        self.middle_right_scr = None
        self.bottom_frame = None
        self.bottom_lbl = None
        self.bottom_btn = None
        self.left_frame = None
        self.left_cnv = None
        self.left_lbl = None
        self.left_sep = None
        self.center_frame = None
        self.center_var = None
        self.center_cnv = None
        self.center_inp = None
        self.center_lbl = None
        self.center_btn = None
        self.right_frame = None
        self.right_lbl = None
        self.right_cnv = None

    def __setattr__(self,key,value):
        if self.__isfrozen and not hasattr(self,key):
            raise TypeError('Error in setting attribute, key={}, value={} ({})'.format(key,value,self.proc_name))
        object.__setattr__(self,key,value)

    def _freeze(self):
        self.__isfrozen = True

    def ask_file(self,pnam,dnam=None):
        if dnam is None:
            if self.center_var is not None:
                fnam = self.center_var[pnam].get().strip()
                if fnam != '':
                    dnam = os.path.dirname(fnam)
                else:
                    dnam = self.inidir
            else:
                dnam = self.inidir
        if pnam in self.expected:
            if isinstance(self.expected[pnam],str):
                es = [self.expected[pnam]]
            else:
                es = self.expected[pnam]
            fs = []
            flag_all = False
            for e in es:
                if isinstance(e,str):
                    bnam,enam = os.path.splitext(e)
                    enam = enam.replace('.','')
                    if bnam == '*' and enam == '*':
                        pass
                    elif bnam == '*':
                        fs.append(('{} files'.format(enam),'*.{}|*.{}'.format(enam.lower(),enam.upper())))
                        flag_all = True
                    elif enam == '*':
                        fs.append(('{} files'.format(bnam),'*{}.*'.format(bnam)))
                        flag_all = True
                    else:
                        fs.extend([('{}.{}'.format(bnam,enam),'*{}.{}|*{}.{}'.format(bnam,enam.lower(),bnam,enam.upper())),
                                   ('{} files'.format(bnam),'*{}.*'.format(bnam)),
                                   ('{} files'.format(enam),'*.{}|*.{}'.format(enam.lower(),enam.upper()))])
                        flag_all = True
                else:
                    fs.append(e)
            if flag_all:
                fs.append(('all files','*.*'))
            if len(fs) < 1:
                fs = None
            else:
                fs = tuple(fs)
        else:
            fs = None
        if fs is None:
            path = tkfilebrowser.askopenfilename(initialdir=dnam)
        else:
            path = tkfilebrowser.askopenfilename(initialdir=dnam,filetypes=fs)
        if len(path) > 0:
            self.center_var[pnam].set(path)
        return

    def ask_files(self,pnam,dnam=None):
        if dnam is None:
            if self.center_var is not None:
                lines = self.center_var[pnam].get().strip().splitlines()
                fnams = []
                for line in lines:
                    fnam = line.strip()
                    if (len(fnam) < 1) or (fnam[0] == '#'):
                        continue
                    fnams.append(fnam)
                if len(fnams) > 0:
                    dnam = os.path.dirname(fnams[-1])
                else:
                    dnam = self.inidir
            else:
                dnam = self.inidir
        if pnam in self.expected:
            if isinstance(self.expected[pnam],str):
                es = [self.expected[pnam]]
            else:
                es = self.expected[pnam]
            fs = []
            flag_all = False
            for e in es:
                if isinstance(e,str):
                    bnam,enam = os.path.splitext(e)
                    enam = enam.replace('.','')
                    if bnam == '*' and enam == '*':
                        pass
                    elif bnam == '*':
                        fs.append(('{} files'.format(enam),'*.{}|*.{}'.format(enam.lower(),enam.upper())))
                        flag_all = True
                    elif enam == '*':
                        fs.append(('{} files'.format(bnam),'*{}.*'.format(bnam)))
                        flag_all = True
                    else:
                        fs.extend([('{}.{}'.format(bnam,enam),'*{}.{}|*{}.{}'.format(bnam,enam.lower(),bnam,enam.upper())),
                                   ('{} files'.format(bnam),'*{}.*'.format(bnam)),
                                   ('{} files'.format(enam),'*.{}|*.{}'.format(enam.lower(),enam.upper()))])
                        flag_all = True
                else:
                    fs.append(e)
            if flag_all:
                fs.append(('all files','*.*'))
            if len(fs) < 1:
                fs = None
            else:
                fs = tuple(fs)
        else:
            fs = None
        if fs is None:
            files = list(tkfilebrowser.askopenfilenames(initialdir=dnam))
        else:
            files = list(tkfilebrowser.askopenfilenames(initialdir=dnam,filetypes=fs))
        if len(files) > 0:
            lines = self.center_inp[pnam].get('1.0',tk.END)
            if (len(lines) > 1) and (lines[-2] != '\n'):
                path = '\n'+'\n'.join(files)+'\n'
            else:
                path = '\n'.join(files)+'\n'
            self.center_inp[pnam].insert(tk.END,path)
            lines = self.center_inp[pnam].get('1.0',tk.END)
            if self.check_err(pnam,lines):
                self.center_var[pnam].set(lines)
        return

    def ask_folder(self,pnam,dnam=None):
        if dnam is None:
            if self.center_var is not None:
                fnam = self.center_var[pnam].get().strip()
                if fnam != '':
                    dnam = os.path.dirname(fnam)
                else:
                    dnam = self.inidir
            else:
                dnam = self.inidir
        path = tkfilebrowser.askopendirname(initialdir=dnam)
        if len(path) > 0:
            self.center_var[pnam].set(path)
        return

    def ask_folders(self,pnam,dnam=None):
        if dnam is None:
            if self.center_var is not None:
                lines = self.center_var[pnam].get().strip().splitlines()
                fnams = []
                for line in lines:
                    fnam = line.strip()
                    if (len(fnam) < 1) or (fnam[0] == '#'):
                        continue
                    fnams.append(fnam)
                if len(fnams) > 0:
                    dnam = os.path.dirname(fnams[-1])
                else:
                    dnam = self.inidir
            else:
                dnam = self.inidir
        dirs = list(tkfilebrowser.askopendirnames(initialdir=dnam))
        if len(dirs) > 0:
            lines = self.center_inp[pnam].get('1.0',tk.END)
            if (len(lines) > 1) and (lines[-2] != '\n'):
                path = '\n'+'\n'.join(dirs)+'\n'
            else:
                path = '\n'.join(dirs)+'\n'
            self.center_inp[pnam].insert(tk.END,path)
            lines = self.center_inp[pnam].get('1.0',tk.END)
            if self.check_err(pnam,lines):
                self.center_var[pnam].set(lines)
        return

    def mktemp(self,suffix='',prefix=''):
        dnam = tempfile.gettempdir()
        string_seed = string.digits + string.ascii_lowercase + string.ascii_uppercase
        random_string = ''.join(random.choices(string_seed,k=8))
        return os.path.join(dnam,'{}{}_{}{}'.format(prefix,self.proc_name,random_string,suffix))

    def on_mousewheel(self,event):
        if self.root is not None and self.root.winfo_exists():
            self.middle_left_canvas.yview_scroll(-1*(event.delta//20),'units')

    def on_frame_configure(self,event):
        self.root_width = self.root.winfo_width()
        self.center_frame_width = self.root_width-(self.left_frame_width+self.right_frame_width)
        self.middle_left_frame.config(width=self.root_width)
        for pnam in self.pnams:
            self.center_cnv[pnam].config(width=self.center_frame_width)
        return

    def reset(self):
        for pnam in self.pnams:
            if '_list' in self.param_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    if self.values[pnam][j] is not None:
                        self.center_var[pnam][j].set(self.values[pnam][j])
            elif self.input_types[pnam] in ['ask_files','ask_folders']:
                if self.values[pnam] is not None:
                    self.center_inp[pnam].delete('1.0',tk.END)
                    self.center_inp[pnam].insert('1.0',self.values[pnam])
                    self.center_var[pnam].set(self.values[pnam])
            else:
                if self.values[pnam] is not None:
                    self.center_var[pnam].set(self.values[pnam])
        return

    def exit(self):
        self.root.destroy()
        return

    def run(self):
        sys.stderr.write('Running process {}.\n'.format(self.proc_name))
        sys.stderr.flush()
        return

    def run_command(self,command,message=None,print_command=True,print_time=True):
        if message is not None:
            sys.stderr.write('\n'+message+'\n')
            sys.stderr.flush()
        if print_command:
            sys.stderr.write('\n'+command+'\n')
            sys.stderr.flush()
        if print_time:
            t1 = datetime.now()
            sys.stderr.write('\nStart: {}\n'.format(t1))
            sys.stderr.flush()
        ret = call(command,shell=True)
        if print_time:
            t2 = datetime.now()
            sys.stderr.write('\nEnd: {} ({})\n'.format(t2,t2-t1))
            sys.stderr.flush()
        if ret != 0:
            sys.stderr.write('\nTerminated process {}.\n'.format(self.proc_name))
            sys.stderr.write('\n')
            sys.stderr.flush()
            raise ValueError('ERROR')
        return ret

    def print_message(self,message,print_time=True):
        if message is not None:
            sys.stderr.write('\n'+message+'\n')
            sys.stderr.flush()
        if print_time:
            t1 = datetime.now()
            sys.stderr.write('\n{}\n'.format(t1))
            sys.stderr.flush()
        return

    def modify(self):
        check_values,check_errors = self.check_all(source='input')
        err = False
        for pnam in self.pnams:
            if '_list' in self.param_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    value = check_values[pnam][j]
                    error = check_errors[pnam][j]
                    if error:
                        err = True
                    else:
                        self.center_var[pnam][j].set(value)
                        self.values[pnam][j] = value
            else:
                value = check_values[pnam]
                error = check_errors[pnam]
                if error:
                    err = True
                else:
                    self.center_var[pnam].set(value)
                    self.values[pnam] = value
        if not err:
            self.left_btn.invoke()
            self.root.destroy()
        return

    def get_input(self,pnam,indx=None):
        if self.param_types[pnam] == 'boolean':
            return self.center_var[pnam].get()
        elif self.param_types[pnam] == 'boolean_list':
            return self.center_var[pnam][indx].get()
        elif self.input_types[pnam] in ['ask_files','ask_folders']:
            if indx is not None:
                return self.center_inp[pnam][indx].get(1.0,tk.END)
            else:
                return self.center_inp[pnam].get(1.0,tk.END)
        else:
            if indx is not None:
                return self.center_inp[pnam][indx].get()
            else:
                return self.center_inp[pnam].get()

    def get_value(self,pnam,indx=None):
        if indx is not None:
            return self.values[pnam][indx]
        else:
            return self.values[pnam]

    def check_par(self,pnam,t):
        if ((pnam in self.flag_check) and (not self.flag_check[pnam]) and
            (not self.input_types[pnam] in ['ask_file','ask_files','ask_folder','ask_folders'])):
            return True
        elif self.input_types[pnam] == 'box':
            if self.param_types[pnam] == 'string':
                return True
            elif self.param_types[pnam] == 'int':
                return check_int(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
            elif self.param_types[pnam] == 'float':
                return check_float(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
        elif self.input_types[pnam] == 'ask_file':
            return check_file(self.params[pnam],t,quiet=((pnam in self.flag_check) and (not self.flag_check[pnam])))
        elif self.input_types[pnam] == 'ask_files':
            return check_files(self.params[pnam],t,quiet=((pnam in self.flag_check) and (not self.flag_check[pnam])))
        elif self.input_types[pnam] == 'ask_folder':
            return check_folder(self.params[pnam],t,quiet=((pnam in self.flag_check) and (not self.flag_check[pnam])))
        elif self.input_types[pnam] == 'ask_folders':
            return check_folders(self.params[pnam],t,quiet=((pnam in self.flag_check) and (not self.flag_check[pnam])))
        elif self.input_types[pnam] in ['date','date_list']:
            return True
        elif self.input_types[pnam] in ['boolean','boolean_list']:
            return True
        elif 'int_list' in self.input_types[pnam]:
            return check_int(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
        elif 'float_list' in self.input_types[pnam]:
            return check_float(self.params[pnam],t,self.param_range[pnam][0],self.param_range[pnam][1])
        elif '_select' in self.input_types[pnam]:
            return True
        elif '_select_list' in self.input_types[pnam]:
            return True
        else:
            raise ValueError('Error, unsupported input type ({}) >>> {}'.format(pnam,self.input_types[pnam]))

    def check_err(self,pnam,t):
        ret = self.check_par(pnam,t)
        if self.right_lbl[pnam] is not None:
            if ret:
                if self.input_types[pnam] in ['ask_file','ask_files','ask_folder','ask_folders']:
                    self.right_lbl[pnam].config(text='\U00002B55',foreground='green')
                    if self.input_types[pnam] in ['ask_files','ask_folders']:
                        self.right_lbl[pnam].pack(anchor=tk.N,side=tk.LEFT)
                    else:
                        self.right_lbl[pnam].pack(side=tk.LEFT)
                else:
                    self.right_lbl[pnam].pack_forget()
            else:
                if self.input_types[pnam] in ['ask_file','ask_files','ask_folder','ask_folders']:
                    if (pnam in self.flag_check) and (not self.flag_check[pnam]):
                        if pnam in self.depend_proc:
                            flag = False
                            for proc in self.depend_proc[pnam]:
                                if not self.chk_btn[proc].get():
                                    flag = True
                                    break
                            if flag:
                                self.right_lbl[pnam].config(text='ERROR',foreground='red')
                            else:
                                self.right_lbl[pnam].config(text='\U0000274C',foreground='red')
                                ret = True
                        else:
                            self.right_lbl[pnam].config(text='\U0000274C',foreground='red')
                            ret = True
                    else:
                        self.right_lbl[pnam].config(text='ERROR',foreground='red')
                    if self.input_types[pnam] in ['ask_files','ask_folders']:
                        self.right_lbl[pnam].pack(anchor=tk.N,side=tk.LEFT)
                    else:
                        self.right_lbl[pnam].pack(side=tk.LEFT)
                else:
                    self.right_lbl[pnam].pack(side=tk.LEFT)
        return ret

    def check_all(self,source='input'):
        if source == 'input':
            get = self.get_input
        elif source == 'value':
            get = self.get_value
        else:
            raise ValueError('Error, source={}'.format(source))
        check_values = {}
        check_errors = {}
        for pnam in self.pnams:
            if '_list' in self.param_types[pnam]:
                check_values[pnam] = []
                check_errors[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    check_values[pnam].append(None)
                    check_errors[pnam].append(True)
                try:
                    for j in range(self.list_sizes[pnam]):
                        t = get(pnam,j)
                        ret = self.check_par(pnam,t)
                        if ret: # Use values or center_var to skip type conversion
                            if self.center_var is None:
                                check_values[pnam][j] = self.values[pnam][j]
                            else:
                                check_values[pnam][j] = self.center_var[pnam][j].get()
                        else:
                            raise ValueError('ERROR')
                        check_errors[pnam][j] = False
                except Exception as e:
                    sys.stderr.write(str(e)+'\n')
            else:
                check_values[pnam] = None
                check_errors[pnam] = True
                try:
                    t = get(pnam)
                    ret = self.check_par(pnam,t)
                    if ret: # Use values or center_var to skip type conversion
                        if self.param_types[pnam] in ['string']: # center_var maybe None in case ask_files/ask_folders
                            check_values[pnam] = t
                        elif self.center_var is None:
                            check_values[pnam] = self.values[pnam]
                        else:
                            check_values[pnam] = self.center_var[pnam].get()
                    else:
                        raise ValueError('ERROR')
                    check_errors[pnam] = False
                except Exception as e:
                    if (pnam in self.flag_check) and (not self.flag_check[pnam]):
                        if self.param_types[pnam] in ['string']: # center_var maybe None in case ask_files/ask_folders
                            check_values[pnam] = t
                        elif self.center_var is None:
                            check_values[pnam] = self.values[pnam]
                        else:
                            check_values[pnam] = self.center_var[pnam].get()
                    else:
                        sys.stderr.write(str(e)+'\n')
        if source == 'input':
            for pnam in self.pnams:
                if not pnam in check_errors or not pnam in self.right_lbl:
                    continue
                if '_list' in self.param_types[pnam]:
                    if True in check_errors[pnam]:
                        self.right_lbl[pnam].pack(side=tk.LEFT)
                    else:
                        self.right_lbl[pnam].pack_forget()
                else:
                    if check_errors[pnam]:
                        if self.input_types[pnam] in ['ask_file','ask_files','ask_folder','ask_folders']:
                            if (pnam in self.flag_check) and (not self.flag_check[pnam]):
                                if pnam in self.depend_proc:
                                    flag = False
                                    for proc in self.depend_proc[pnam]:
                                        if not self.chk_btn[proc].get():
                                            flag = True
                                            break
                                    if flag:
                                        self.right_lbl[pnam].config(text='ERROR',foreground='red')
                                    else:
                                        self.right_lbl[pnam].config(text='\U0000274C',foreground='red')
                                        check_errors[pnam] = False
                                else:
                                    self.right_lbl[pnam].config(text='\U0000274C',foreground='red')
                                    check_errors[pnam] = False
                            else:
                                self.right_lbl[pnam].config(text='ERROR',foreground='red')
                            if self.input_types[pnam] in ['ask_files','ask_folders']:
                                self.right_lbl[pnam].pack(anchor=tk.N,side=tk.LEFT)
                            else:
                                self.right_lbl[pnam].pack(side=tk.LEFT)
                        else:
                            self.right_lbl[pnam].pack(side=tk.LEFT)
                    else:
                        if self.input_types[pnam] in ['ask_file','ask_files','ask_folder','ask_folders']:
                            self.right_lbl[pnam].config(text='\U00002B55',foreground='green')
                            if self.input_types[pnam] in ['ask_files','ask_folders']:
                                self.right_lbl[pnam].pack(anchor=tk.N,side=tk.LEFT)
                            else:
                                self.right_lbl[pnam].pack(side=tk.LEFT)
                        else:
                            self.right_lbl[pnam].pack_forget()
        else:
            for pnam in self.pnams:
                if self.input_types[pnam] in ['ask_file','ask_files','ask_folder','ask_folders']:
                    if (pnam in self.flag_check) and (not self.flag_check[pnam]):
                        if (pnam in self.depend_proc) and (self.chk_btn is not None):
                            flag = False
                            for proc in self.depend_proc[pnam]:
                                if not self.chk_btn[proc].get():
                                    flag = True
                                    break
                            if flag:
                                pass
                            else:
                                check_errors[pnam] = False
                        else:
                            check_errors[pnam] = False
        return check_values,check_errors

    def print_message(self,message):
        sys.stderr.write('\n')
        if isinstance(message,str):
            sys.stderr.write('{}\n'.format(message))
        else:
            for line in message:
                sys.stderr.write('{}\n'.format(line))
        sys.stderr.flush()
        return

    def print_time(self,message=None):
        sys.stderr.write('\n')
        if message is not None:
            if isinstance(message,str):
                sys.stderr.write('{}\n'.format(message))
            else:
                for line in message:
                    sys.stderr.write('{}\n'.format(line))
        sys.stderr.write('{}\n'.format(datetime.now()))
        sys.stderr.flush()
        return

    def set(self,parent,chk_btn):
        if self.root is not None and self.root.winfo_exists():
            return
        for x in parent.winfo_children():
            if isinstance(x,ttk.Button) and x['text'] == 'check_{}'.format(self.proc_name):
                self.left_btn = x
        self.chk_btn = chk_btn
        self.root = tk.Toplevel(parent)
        self.root.title(self.proc_title)
        self.root.geometry('{}x{}'.format(self.middle_left_frame_width,
                                          self.top_frame_height
                                          +self.bottom_frame_height+len(self.pnams)*(self.center_cnv_height+2)
                                          +list(self.input_types.values()).count('ask_files')*(self.center_cnv_height*(self.text_height-1))
                                          +list(self.input_types.values()).count('ask_folders')*(self.center_cnv_height*(self.text_height-1))))
        self.top_frame = tk.Frame(self.root,width=10,height=self.top_frame_height,background=None)
        self.middle_frame = tk.Frame(self.root,width=10,height=20,background=None)
        self.bottom_frame = tk.Frame(self.root,width=10,height=self.bottom_frame_height,background=None)
        self.middle_left_canvas = tk.Canvas(self.middle_frame,width=30,height=10,scrollregion=(0,0,
                                            self.middle_left_frame_width,
                                            self.top_frame_height+self.bottom_frame_height+len(self.pnams)*(self.center_cnv_height+2)),
                                            background=None)
        self.middle_left_canvas.bind_all('<MouseWheel>',self.on_mousewheel)
        self.middle_right_scr = tk.Scrollbar(self.middle_frame,orient=tk.VERTICAL,command=self.middle_left_canvas.yview)
        self.top_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.TOP)
        self.middle_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,expand=True)
        self.bottom_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.X,side=tk.BOTTOM)
        self.middle_left_canvas.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
        self.middle_right_scr.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
        self.top_frame.pack_propagate(False)
        self.middle_frame.pack_propagate(False)
        self.bottom_frame.pack_propagate(False)
        self.middle_left_canvas.pack_propagate(False)

        self.middle_left_frame = tk.Frame(self.middle_left_canvas,background=None)
        self.middle_left_canvas.create_window(0,0,window=self.middle_left_frame,anchor=tk.NW)
        self.middle_left_canvas.config(yscrollcommand=self.middle_right_scr.set)

        self.left_frame = tk.Frame(self.middle_left_frame,width=self.left_frame_width,height=10,background=None)
        self.left_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.LEFT)
        self.center_frame = tk.Frame(self.middle_left_frame,width=30,height=10,background=None)
        self.center_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.BOTH,side=tk.LEFT,expand=True)
        self.right_frame = tk.Frame(self.middle_left_frame,width=self.right_frame_width,height=10,background=None)
        self.right_frame.pack(ipadx=0,ipady=0,padx=0,pady=0,fill=tk.Y,side=tk.RIGHT)
        self.middle_left_frame.pack_propagate(False)
        self.left_frame.pack_propagate(False)
        self.right_frame.pack_propagate(False)
        self.middle_left_frame.config(width=self.middle_left_frame_width,height=8000)

        self.bottom_lbl = {}
        self.bottom_btn = {}
        pnam = 'left'
        self.bottom_lbl[pnam] = tk.Label(self.bottom_frame,text='')
        self.bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)
        pnam = 'set'
        self.bottom_btn[pnam] = tk.Button(self.bottom_frame,text=pnam.capitalize(),width=8,command=self.modify)
        self.bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
        pnam = 'reset'
        self.bottom_btn[pnam] = tk.Button(self.bottom_frame,text=pnam.capitalize(),width=8,command=self.reset)
        self.bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
        pnam = 'cancel'
        self.bottom_btn[pnam] = tk.Button(self.bottom_frame,text=pnam.capitalize(),width=8,command=self.exit)
        self.bottom_btn[pnam].pack(padx=10,side=tk.LEFT)
        pnam = 'right'
        self.bottom_lbl[pnam] = tk.Label(self.bottom_frame,text='')
        self.bottom_lbl[pnam].pack(fill=tk.X,side=tk.LEFT,expand=True)

        browse_img = tk.PhotoImage(file=self.browse_image)
        bgs = [None,None]
        self.center_var = {}
        self.center_cnv = {}
        self.center_inp = {}
        self.center_lbl = {}
        self.center_btn = {}
        self.left_cnv = {}
        self.left_lbl = {}
        self.left_sep = {}
        self.right_cnv = {}
        self.right_lbl = {}
        self.center_frame.update()
        self.center_frame_width = self.root.winfo_width()-(self.left_frame_width+self.right_frame_width)
        for i,pnam in enumerate(self.pnams):
            if self.param_types[pnam] == 'string':
                self.center_var[pnam] = tk.StringVar()
            elif self.param_types[pnam] == 'int':
                self.center_var[pnam] = tk.IntVar()
            elif self.param_types[pnam] == 'float':
                self.center_var[pnam] = tk.DoubleVar()
            elif self.param_types[pnam] == 'boolean':
                self.center_var[pnam] = tk.BooleanVar()
            elif self.param_types[pnam] == 'date':
                self.center_var[pnam] = tk.StringVar()
            elif self.param_types[pnam] == 'string_select':
                self.center_var[pnam] = tk.StringVar()
            elif self.param_types[pnam] == 'int_select':
                self.center_var[pnam] = tk.IntVar()
            elif self.param_types[pnam] == 'float_select':
                self.center_var[pnam] = tk.DoubleVar()
            elif self.param_types[pnam] == 'string_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.StringVar())
            elif self.param_types[pnam] == 'int_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.IntVar())
            elif self.param_types[pnam] == 'float_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.DoubleVar())
            elif self.param_types[pnam] == 'boolean_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.BooleanVar())
            elif self.param_types[pnam] == 'date_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.StringVar())
            elif self.param_types[pnam] == 'string_select_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.StringVar())
            elif self.param_types[pnam] == 'int_select_list':
                self.center_var[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_var[pnam].append(tk.IntVar())
            else:
                raise ValueError('Error, unsupported parameter type ({}) >>> {}'.format(pnam,self.param_types[pnam]))
            if '_list' in self.input_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    if self.values[pnam][j] is not None:
                        self.center_var[pnam][j].set(self.values[pnam][j])
            else:
                if self.values[pnam] is not None:
                    self.center_var[pnam].set(self.values[pnam])
            if self.input_types[pnam] in ['ask_files','ask_folders']:
                self.center_cnv[pnam] = tk.Canvas(self.center_frame,width=self.center_frame_width,height=self.center_cnv_height*self.text_height,background=bgs[i%2],highlightthickness=0)
            else:
                self.center_cnv[pnam] = tk.Canvas(self.center_frame,width=self.center_frame_width,height=self.center_cnv_height,background=bgs[i%2],highlightthickness=0)
            self.center_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2))
            self.center_cnv[pnam].pack_propagate(False)
            if self.input_types[pnam] == 'box':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            elif self.input_types[pnam] == 'ask_file':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_file("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'ask_files':
                self.center_inp[pnam] = tk.Text(self.center_cnv[pnam],background=bgs[i%2],width=1)
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_inp[pnam].insert('1.0',self.center_var[pnam].get())
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_files("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.N,side=tk.LEFT)
            elif self.input_types[pnam] == 'ask_folder':
                self.center_inp[pnam] = tk.Entry(self.center_cnv[pnam],background=bgs[i%2],textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_folder("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'ask_folders':
                self.center_inp[pnam] = tk.Text(self.center_cnv[pnam],background=bgs[i%2],width=1)
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_inp[pnam].insert('1.0',self.center_var[pnam].get())
                self.center_btn[pnam] = tk.Button(self.center_cnv[pnam],image=browse_img,width=self.center_btn_width,bg='white',bd=1,command=eval('lambda self=self:self.ask_folders("{}")'.format(pnam)))
                self.center_btn[pnam].image = browse_img
                self.center_btn[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.N,side=tk.LEFT)
            elif self.input_types[pnam] == 'date':
                self.center_inp[pnam] = CustomDateEntry(self.center_cnv[pnam],width=10,date_pattern=self.date_format,textvariable=self.center_var[pnam])
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                self.center_inp[pnam].delete(0,tk.END)
                if self.values[pnam] != '':
                    self.center_inp[pnam].insert(0,self.values[pnam])
            elif self.input_types[pnam] == 'date_list':
                self.center_inp[pnam] = []
                self.center_lbl[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    if self.list_labels[pnam][j] != '':
                        self.center_lbl[pnam].append(ttk.Label(self.center_cnv[pnam],text=self.list_labels[pnam][j]))
                        self.center_lbl[pnam][-1].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
                    self.center_inp[pnam].append(CustomDateEntry(self.center_cnv[pnam],width=1,date_pattern=self.date_format,textvariable=self.center_var[pnam][j]))
                    self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                    self.center_inp[pnam][j].delete(0,tk.END)
                    if self.values[pnam][j] != '':
                        self.center_inp[pnam][j].insert(0,self.values[pnam][j])
            elif self.input_types[pnam] == 'boolean':
                if pnam in self.list_labels:
                    self.center_inp[pnam] = tk.Checkbutton(self.center_cnv[pnam],background=bgs[i%2],variable=self.center_var[pnam],text=self.list_labels[pnam][0])
                else:
                    self.center_inp[pnam] = tk.Checkbutton(self.center_cnv[pnam],background=bgs[i%2],variable=self.center_var[pnam])
                if pnam in self.flag_fill and self.flag_fill[pnam]:
                    self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                else:
                    self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif self.input_types[pnam] == 'boolean_list':
                self.center_inp[pnam] = []
                self.center_lbl[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    self.center_inp[pnam].append(tk.Checkbutton(self.center_cnv[pnam],background=bgs[i%2],variable=self.center_var[pnam][j],text=self.list_labels[pnam][j]))
                    if pnam in self.flag_fill and self.flag_fill[pnam]:
                        self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
                    else:
                        self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
            elif '_select_list' in self.input_types[pnam]:
                self.center_inp[pnam] = []
                self.center_lbl[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    if self.list_labels[pnam][j] != '':
                        self.center_lbl[pnam].append(ttk.Label(self.center_cnv[pnam],text=self.list_labels[pnam][j][0]))
                        self.center_lbl[pnam][-1].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
                    self.center_inp[pnam].append(ttk.Combobox(self.center_cnv[pnam],width=1,background=bgs[i%2],values=self.list_labels[pnam][j][1],state='readonly',textvariable=self.center_var[pnam][j]))
                    self.center_inp[pnam][j].current(self.list_labels[pnam][j][1].index(self.values[pnam][j]))
                    self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            elif '_list' in self.input_types[pnam]:
                self.center_inp[pnam] = []
                self.center_lbl[pnam] = []
                for j in range(self.list_sizes[pnam]):
                    if self.list_labels[pnam][j] != '':
                        self.center_lbl[pnam].append(ttk.Label(self.center_cnv[pnam],text=self.list_labels[pnam][j]))
                        self.center_lbl[pnam][-1].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,side=tk.LEFT)
                    self.center_inp[pnam].append(tk.Entry(self.center_cnv[pnam],width=1,background=bgs[i%2],textvariable=self.center_var[pnam][j]))
                    self.center_inp[pnam][j].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            elif '_select' in self.input_types[pnam]:
                self.center_inp[pnam] = ttk.Combobox(self.center_cnv[pnam],background=bgs[i%2],values=self.list_labels[pnam],state='readonly',textvariable=self.center_var[pnam])
                if re.search(r'\\u',self.values[pnam]):
                    v = re.sub(r'\\u(\S\S\S\S)',lambda m:chr(int('0x'+m.group(1),16)),self.values[pnam])
                else:
                    v = self.values[pnam]
                if re.search(r'\\U',v):
                    v = re.sub(r'\\U(\S\S\S\S\S\S\S\S)',lambda m:chr(int('0x'+m.group(1),16)),v)
                else:
                    v = self.values[pnam]
                if v in self.center_inp[pnam]['values']:
                    self.center_inp[pnam].current(self.list_labels[pnam].index(v))
                else:
                    self.center_inp[pnam].current(self.list_labels[pnam].index(self.values[pnam]))
                self.center_inp[pnam].pack(ipadx=0,ipady=0,padx=0,pady=0,anchor=tk.W,fill=tk.X,side=tk.LEFT,expand=True)
            else:
                raise ValueError('Error, unsupported input type ({}) >>> {}'.format(pnam,self.input_types[pnam]))
            if self.input_types[pnam] in ['ask_files','ask_folders']:
                self.left_cnv[pnam] = tk.Canvas(self.left_frame,width=self.left_frame_width,height=self.left_cnv_height*self.text_height,background=bgs[i%2],highlightthickness=0)
            else:
                self.left_cnv[pnam] = tk.Canvas(self.left_frame,width=self.left_frame_width,height=self.left_cnv_height,background=bgs[i%2],highlightthickness=0)
            self.left_cnv[pnam].pack(ipadx=0,ipady=0,padx=0,pady=(0,2))
            self.left_lbl[pnam] = ttk.Label(self.left_cnv[pnam],text=self.params[pnam])
            if self.input_types[pnam] in ['ask_files','ask_folders']:
                self.left_lbl[pnam].pack(ipadx=0,ipady=0,padx=(20,2),pady=0,anchor=tk.N,side=tk.LEFT)
            else:
                self.left_lbl[pnam].pack(ipadx=0,ipady=0,padx=(20,2),pady=0,side=tk.LEFT)
            self.left_sep[pnam] = ttk.Separator(self.left_cnv[pnam],orient='horizontal')
            if self.input_types[pnam] in ['ask_files','ask_folders']:
                self.left_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=(self.left_cnv_height*0.4,0),anchor=tk.N,fill=tk.X,side=tk.LEFT,expand=True)
            else:
                self.left_sep[pnam].pack(ipadx=0,ipady=0,padx=(0,2),pady=(self.left_cnv_height*0.1,0),fill=tk.X,side=tk.LEFT,expand=True)
            self.left_cnv[pnam].pack_propagate(False)
            if self.input_types[pnam] in ['ask_files','ask_folders']:
                self.right_cnv[pnam] = tk.Canvas(self.right_frame,width=self.right_frame_width,height=self.right_cnv_height*self.text_height,background=bgs[i%2],highlightthickness=0)
            else:
                self.right_cnv[pnam] = tk.Canvas(self.right_frame,width=self.right_frame_width,height=self.right_cnv_height,background=bgs[i%2],highlightthickness=0)
            self.right_cnv[pnam].pack(ipadx=0,ipady=0,padx=(0,20),pady=(0,2))
            self.right_cnv[pnam].pack_propagate(False)
            self.right_lbl[pnam] = ttk.Label(self.right_cnv[pnam],text='ERROR',foreground='red')
        for pnam in self.pnams:
            if self.input_types[pnam] in ['date','date_list']:
                pass
            elif self.input_types[pnam] in ['boolean','boolean_list']:
                pass
            elif self.input_types[pnam] in ['ask_files','ask_folders']:
                pass
            elif '_select' in self.param_types[pnam]:
                pass
            elif '_list' in self.param_types[pnam]:
                for j in range(self.list_sizes[pnam]):
                    vcmd = (self.center_inp[pnam][j].register(eval('lambda x,self=self:self.check_err("{}",x)'.format(pnam))),'%P')
                    self.center_inp[pnam][j].config(validatecommand=vcmd,validate='focusout')
            else:
                vcmd = (self.center_inp[pnam].register(eval('lambda x,self=self:self.check_err("{}",x)'.format(pnam))),'%P')
                self.center_inp[pnam].config(validatecommand=vcmd,validate='focusout')
        self.check_all(source='input')
        self.root.bind('<Configure>',self.on_frame_configure)
