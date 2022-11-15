import os
import shutil
import re
from datetime import datetime
import tkinter as tk

def read_month(s):
    s_low = s.lower()
    if s_low[:2] == 'ja':
        return 1
    elif s_low[:1] == 'f':
        return 2
    elif s_low[:3] == 'mar' or s_low[:1] == 'b':
        return 3
    elif s_low[:2] == 'ap':
        return 4
    elif s_low[:3] == 'may' or s_low[:2] == 'me':
        return 5
    elif s_low[:3] == 'jun':
        return 6
    elif s_low[:3] == 'jul':
        return 7
    elif s_low[:2] == 'au' or s_low[:2] == 'ag':
        return 8
    elif s_low[:1] == 's':
        return 9
    elif s_low[:1] == 'o':
        return 10
    elif s_low[:1] == 'n':
        return 11
    elif s_low[:1] == 'd':
        return 12
    else:
        raise ValueError('Error, cannot read month >>> {}'.format(s))

def ask_question():
    win = tk.Tk()
    canvas = tk.Canvas(win,width=300,height=300)
    canvas.pack()
    return

def set_obs_fnam(block,dstr,field_dir,date_format='yyyy-mm&mmm-dd'):
    obs_fnam = os.path.join(field_dir,block,'Excel_File','{}_{}.xls'.format(block,dstr))
    if not os.path.isdir(field_dir):
        return -1
    date_fmt = date_format.replace('yyyy','%Y').replace('yy','%y').replace('mmm','%b').replace('mm','%m').replace('dd','%d').replace('&','')
    for f in sorted(os.listdir(field_dir)):
        obs_block = None
        obs_date = None
        try:
            # pattern 1: day[. ,-_]month[. ,-_]year[. ,-_]block.xls, ex. 26.03.2022 2a.xls
            m = re.search('^(\d+)[\s\.\-,_]+(\d+)[\s\.\-,_]+(\d+)[\s\.\-,_]+(\S.*)\.XLS',f.upper())
            if m:
                day = int(m.group(1))
                month = int(m.group(2))
                year = int(m.group(3))
                obs_block = m.group(4).strip().replace(' ','')
                obs_date = datetime(year,month,day)
            else:
                # pattern 2: cihea - block (yyyymmdd).xls, ex. CIHEA - 11 B (20220324).xls
                m = re.search('[^\-_]+[\-_]+([^(]+)\(\s*(\d+)\s*\)\s*\.XLS',f.upper())
                if m:
                    obs_block = m.group(1).strip().replace(' ','')
                    obs_date = datetime.strptime(m.group(2),'%Y%m%d')
                else:
                    # pattern 3: ex. Block-11B_2022-04Apr-04.xls
                    m = re.search('^(.*)[\s\.\-,_]+(\d\d\d\d)[\s\.\-,_]+(\d*)([A-Z]*)[\s\.\-,_]+(\d+)\s*\.XLS',f.upper())
                    if m:
                        obs_block = m.group(1).strip().replace(' ','').replace('_','-')
                        year = int(m.group(2))
                        if m.group(3) != '':
                            month = int(m.group(3))
                        elif m.group(4) != '':
                            month = read_month(m.group(4))
                        else:
                            raise ValueError('Error, failed in finding month >>> {}'.format(f))
                        day = int(m.group(5))
                        obs_date = datetime(year,month,day)
        except Exception:
            continue
        if obs_block is None or obs_date is None:
            continue
        if (obs_block == block.upper()) or ('BLOCK-'+obs_block == block.upper()):
            obs_dstr = obs_date.strftime(date_fmt)
            if obs_dstr == dstr:
                if os.path.exists(obs_fnam):
                    os.remove(obs_fnam)
                    #ask_question()
                fnam = os.path.join(field_dir,f)
                pnam = os.path.dirname(obs_fnam)
                if not os.path.exists(pnam):
                    os.makedirs(pnam)
                if not os.path.isdir(pnam):
                    raise IOError('Error, no such folder >>> {}'.format(pnam))
                shutil.move(fnam,obs_fnam)
                return 1

def set_drone_dnam(block,dstr,drone_dir,date_format='yyyy-mm&mmm-dd'):
    drone_dnam = os.path.join(drone_dir,block,dstr)
    if os.path.exists(drone_dnam):
        return 0
    elif not os.path.isdir(drone_dir):
        return -1
    date_fmt = date_format.replace('yyyy','%Y').replace('yy','%y').replace('mmm','%b').replace('mm','%m').replace('dd','%d').replace('&','')
    for d in sorted(os.listdir(drone_dir)):
        dnam = os.path.join(drone_dir,d)
        if not os.path.isdir(dnam):
            continue
        obs_block = None
        obs_date = None
        try:
            # pattern 1: day[. ,-_]month[. ,-_]year[. ,-_]block, ex. 26.03.2022 2a
            m = re.search('^(\d+)[\s\.\-,_]+(\d+)[\s\.\-,_]+(\d+)[\s\.\-,_]+(\S.*)$',d.upper())
            if m:
                day = int(m.group(1))
                month = int(m.group(2))
                year = int(m.group(3))
                obs_block = m.group(4).strip().replace(' ','')
                obs_date = datetime(year,month,day)
            else:
                # pattern 2: cihea - block (yyyymmdd), ex. CIHEA - 11 B (20220324)
                m = re.search('[^\-_]+[\-_]+([^(]+)\(\s*(\d+)\s*\)\s*$',d.upper())
                if m:
                    obs_block = m.group(1).strip().replace(' ','')
                    obs_date = datetime.strptime(m.group(2),'%Y%m%d')
                else:
                    # pattern 3: ex. Block-11B_2022-04Apr-04
                    m = re.search('^(.*)[\s\.\-,_]+(\d\d\d\d)[\s\.\-,_]+(\d*)([A-Z]*)[\s\.\-,_]+(\d+)\s*$',d.upper())
                    if m:
                        obs_block = m.group(1).strip().replace(' ','').replace('_','-')
                        year = int(m.group(2))
                        if m.group(3) != '':
                            month = int(m.group(3))
                        elif m.group(4) != '':
                            month = read_month(m.group(4))
                        else:
                            raise ValueError('Error, failed in finding month >>> {}'.format(d))
                        day = int(m.group(5))
                        obs_date = datetime(year,month,day)
        except Exception:
            continue
        if obs_block is None or obs_date is None:
            continue
        if (obs_block == block.upper()) or ('BLOCK-'+obs_block == block.upper()):
            obs_dstr = obs_date.strftime(date_fmt)
            if obs_dstr == dstr:
                pnam = os.path.dirname(drone_dnam)
                if not os.path.exists(pnam):
                    os.makedirs(pnam)
                if not os.path.isdir(pnam):
                    raise IOError('Error, no such folder >>> {}'.format(pnam))
                shutil.move(dnam,drone_dnam)
                return 1
