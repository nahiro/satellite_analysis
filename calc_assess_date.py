#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime
import numpy as np
import pandas as pd
from matplotlib.dates import date2num,num2date
from csaps import csaps
import matplotlib.pyplot as plt
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
TMIN = '20190315'
TMAX = '20190615'
TSTP = 1 # day
TMGN = 60
SMOOTH = 0.02

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-T','--tendir',default=None,help='Tentative data directory (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=float,help='Margin of input data in day (%(default)s)')
parser.add_argument('--tstp',default=TSTP,type=int,help='Time step in day (%(default)s)')
parser.add_argument('-S','--smooth',default=SMOOTH,type=float,help='Smoothing factor for 1st difference from 0 to 1 (%(default)s)')
args = parser.parse_args()
tmin = datetime.strptime(args.tmin,'%Y%m%d')
tmax = datetime.strptime(args.tmax,'%Y%m%d')
if args.data_tmin is None:
    d1 = tmin-timedelta(days=args.tmgn)
else:
    d1 = datetime.strptime(args.data_tmin,'%Y%m%d')
if args.data_tmax is None:
    d2 = tmax+timedelta(days=args.tmgn)
else:
    d2 = datetime.strptime(args.data_tmax,'%Y%m%d')

# Read data
data_years = np.arange(d1.year,d2.year+1,1)
columns = None
object_ids = None
iband = None
inp_ndvi = []
inp_dtim = []
d = d1
while d <= d2:
    ystr = '{}'.format(d.year)
    dstr = '{:%Y%m%d}'.format(d)
    fnam = os.path.join(args.inpdir,ystr,'{}_interp.csv'.format(dstr))
    if not os.path.exists(fnam):
        gnam = os.path.join(args.tendir,ystr,'{}_interp.csv'.format(dstr))
        if not os.path.exists(gnam):
            raise IOError('Error, no such file >>> {}\n{}'.format(fnam,gnam))
        else:
            fnam = gnam
    inp_dtim.append(d)
    df = pd.read_csv(fnam,comment='#')
    df.columns = df.columns.str.strip()
    if columns is None:
        columns = df.columns
        if columns[0].upper() != 'OBJECTID':
            raise ValueError('Error columns[0]={} (!= OBJECTID) >>> {}'.format(columns[0],fnam))
        if not 'NDVI' in columns:
            raise ValueError('Error in finding NDVI >>> {}'.format(fnam))
        iband = columns.to_list().index('NDVI')
    elif not np.array_equal(df.columns,columns):
        raise ValueError('Error, different columns >>> {}'.format(fnam))
    if object_ids is None:
        object_ids = df.iloc[:,0].astype(int)
    elif not np.array_equal(df.iloc[:,0].astype(int),object_ids):
        raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
    inp_ndvi.append(df.iloc[:,iband].astype(float))
    d += timedelta(days=args.tstp)
inp_ndvi = np.array(inp_ndvi) # (NDAT,NOBJECT)
inp_dtim = np.array(inp_dtim)
inp_ntim = date2num(inp_dtim)
inp_ndat = len(inp_dtim)
nobject = len(object_ids)
if inp_ndat < 5 or nobject < 1:
    raise ValueError('Error, inp_ndat={}, nobject={}'.format(inp_ndat,nobject))

for iobj,object_id in enumerate(object_ids):
    x = inp_ntim
    y = inp_ndvi[:,iobj]
    if np.isnan(y[0]):
        continue
    y1 = csaps(x,np.gradient(y),x
    ysmo = csaps(xc,yc,out_ntim,smooth=args.smooth)


"""
# Interpolate data
d1 = datetime.strptime(args.tmin,'%Y%m%d')
d2 = datetime.strptime(args.tmax,'%Y%m%d')
out_ntim = np.arange(date2num(d1),date2num(d2)+0.1*args.tstp,args.tstp)
out_dtim = num2date(out_ntim)
out_ndat = len(out_dtim)
out_nb = len(params)
out_data = np.full((out_ndat,nobject,out_nb),np.nan)
for iobj,object_id in enumerate(object_ids):
    for iband,param in enumerate(params):
        cnd = ~np.isnan(inp_ndvi[:,iobj,iband])
        xc = inp_ntim[cnd]
        yc = inp_data[cnd,iobj,iband]
        if xc.size > 4:
            ysmo = csaps(xc,yc,out_ntim,smooth=args.smooth)
            out_data[:,iobj,iband] = ysmo

# Output CSV
for idat,dtim in enumerate(out_dtim):
    dnam = os.path.join(args.dstdir,'{}'.format(dtim.year))
    if not os.path.exists(dnam):
        os.makedirs(dnam)
    if not os.path.isdir(dnam):
        raise IOError('No such folder >>> {}'.format(dnam))
    fnam = os.path.join(dnam,'{:%Y%m%d}_interp.csv'.format(dtim))
    with open(fnam,'w') as fp:
        fp.write('{:>8s}'.format('OBJECTID'))
        for param in params:
            fp.write(', {:>13s}'.format(param))
        fp.write('\n')
        for iobj,object_id in enumerate(object_ids):
            fp.write('{:8d}'.format(object_id))
            for iband,param in enumerate(params):
                fp.write(', {:>13.6e}'.format(out_data[idat,iobj,iband]))
            fp.write('\n')
"""
