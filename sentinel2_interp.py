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
TSTP = 1.0 # day
SMOOTH = 0.002

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--inp_list',default=None,help='Input file list (%(default)s)')
parser.add_argument('-I','--inp_fnam',default=None,action='append',help='Input file name (%(default)s)')
parser.add_argument('-D','--dstdir',default=None,help='Destination directory (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tstp',default=TSTP,type=float,help='Time step in day (%(default)s)')
parser.add_argument('-S','--smooth',default=SMOOTH,type=float,help='Smoothing factor from 0 to 1 (%(default)s)')
args = parser.parse_args()
if args.inp_list is None and args.inp_fnam is None:
    raise ValueError('Error, args.inp_list={}, args.inp_fnam={}'.format(args.inp_list,args.inp_fnam))
if args.inp_list is not None:
    fnams = []
    with open(args.inp_list,'r') as fp:
        for line in fp:
            fnam = line.strip()
            if (len(fnam) < 1) or (fnam[0] == '#'):
                continue
            fnams.append(fnam)
else:
    fnams = args.inp_fnam

# Read data
columns = None
object_ids = None
inp_data = []
inp_dtim = []
for fnam in fnams:
    f = os.path.basename(fnam)
    m = re.search('^('+'\d'*8+')_parcel\.csv$',f)
    if not m:
        raise ValueError('Error in file name >>> {}'.format(f))
    dstr = m.group(1)
    d = datetime.strptime(dstr,'%Y%m%d')
    inp_dtim.append(d)
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
    inp_data.append(df.iloc[:,1:].astype(float))
inp_data = np.array(inp_data) # (NDAT,NOBJECT,NBAND)
inp_dtim = np.array(inp_dtim)
inp_ntim = date2num(inp_dtim)
inp_ndat = len(inp_dtim)
nobject = len(object_ids)
params = columns[1:]

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
        cnd = ~np.isnan(inp_data[:,iobj,iband])
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
