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

# Constants
PARAMS = ['Sb','Sg','Sr','Se1','Se2','Se3','Sn1','Sn2','Ss1','Ss2',
          'Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2',
          'NDVI','GNDVI','RGI','NRGI']

# Default values
TMIN = '20190315'
TMAX = '20190615'
TMGN = 90 # day
TSTP = 1 # day
SMOOTH = 0.002

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-D','--dstdir',default=None,help='Destination directory (%(default)s)')
parser.add_argument('-T','--tendir',default=None,help='Tentative data directory (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=float,help='Margin of input data in day (%(default)s)')
parser.add_argument('--tstp',default=TSTP,type=int,help='Time step in day (%(default)s)')
parser.add_argument('-S','--smooth',default=SMOOTH,type=float,help='Smoothing factor from 0 to 1 (%(default)s)')
parser.add_argument('--overwrite',default=False,action='store_true',help='Overwrite mode (%(default)s)')
parser.add_argument('--tentative_overwrite',default=False,action='store_true',help='Overwrite tentative data (%(default)s)')
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
inp_dtim = []
inp_data = []
for year in data_years:
    ystr = '{}'.format(year)
    dnam = os.path.join(args.inpdir,ystr)
    if not os.path.isdir(dnam):
        continue
    for f in sorted(os.listdir(dnam)):
        m = re.search('^('+'\d'*8+')_parcel\.csv$',f)
        if not m:
            continue
        dstr = m.group(1)
        d = datetime.strptime(dstr,'%Y%m%d')
        if d < d1 or d > d2:
            continue
        fnam = os.path.join(dnam,f)
        df = pd.read_csv(fnam,comment='#')
        df.columns = df.columns.str.strip()
        if columns is None:
            columns = df.columns
            if columns[0].upper() != 'OBJECTID':
                raise ValueError('Error columns[0]={} (!= OBJECTID) >>> {}'.format(columns[0],fnam))
        elif not np.array_equal(df.columns,columns):
            raise ValueError('Error, different columns >>> {}'.format(fnam))
        if object_ids is None:
            object_ids = df.iloc[:,0].astype(int)
        elif not np.array_equal(df.iloc[:,0].astype(int),object_ids):
            raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
        inp_dtim.append(d)
        inp_data.append(df.iloc[:,1:].astype(float))
inp_dtim = np.array(inp_dtim)
inp_ntim = date2num(inp_dtim)
inp_data = np.array(inp_data) # (NDAT,NOBJECT,NBAND)
inp_ndat = len(inp_dtim)
nobject = len(object_ids)
params = columns[1:]
if inp_ndat < 5 or nobject < 1:
    raise ValueError('Error, inp_ndat={}, nobject={}'.format(inp_ndat,nobject))

# Interpolate data
out_dtim = []
d = d1
while d <= d2:
    out_dtim.append(d)
    d += timedelta(days=args.tstp)
out_dtim = np.array(out_dtim)
out_ntim = date2num(out_dtim)
out_ndat = len(out_dtim)
out_nb = len(params)
out_data = np.full((out_ndat,nobject,out_nb),np.nan)
for iobj,object_id in enumerate(object_ids):
    for iband,param in enumerate(params):
        cnd = ~np.isnan(inp_data[:,iobj,iband])
        xc = inp_ntim[cnd]
        yc = inp_data[cnd,iobj,iband]
        if xc.size > 4:
            ys = csaps(xc,yc,out_ntim,smooth=args.smooth)
            out_data[:,iobj,iband] = ys

# Output CSV
for idat,dtim in enumerate(out_dtim):
    if dtim < tmin or dtim > tmax:
        dnam = os.path.join(args.tendir,'{}'.format(dtim.year))
        fnam = os.path.join(dnam,'{:%Y%m%d}_interp.csv'.format(dtim))
        if os.path.exists(fnam) and args.tentative_overwrite:
            os.remove(fnam)
    else:
        dnam = os.path.join(args.dstdir,'{}'.format(dtim.year))
        fnam = os.path.join(dnam,'{:%Y%m%d}_interp.csv'.format(dtim))
        if os.path.exists(fnam) and args.overwrite:
            os.remove(fnam)
    if os.path.exists(fnam):
        continue
    if not os.path.exists(dnam):
        os.makedirs(dnam)
    if not os.path.isdir(dnam):
        raise IOError('No such folder >>> {}'.format(dnam))
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
