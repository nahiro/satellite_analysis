#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
from matplotlib.dates import date2num,num2date,YearLocator,MonthLocator,DayLocator,DateFormatter
from csaps import csaps
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
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
NFIG = 1000
ETHR = 3.0

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
parser.add_argument('-E','--ethr',default=ETHR,type=float,help='Max error in sigma for cloud removal (%(default)s)')
parser.add_argument('--inp_csv',default=False,action='store_true',help='Input CSV (%(default)s)')
parser.add_argument('--out_csv',default=False,action='store_true',help='Output CSV (%(default)s)')
parser.add_argument('--overwrite',default=False,action='store_true',help='Overwrite mode (%(default)s)')
parser.add_argument('--tentative_overwrite',default=False,action='store_true',help='Overwrite tentative data (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--nfig',default=NFIG,type=int,help='Max number of figure for debug (%(default)s)')
parser.add_argument('--atcor',default=False,action='store_true',help='Atcor mode (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
tmin = datetime.strptime(args.tmin,'%Y%m%d')
tmax = datetime.strptime(args.tmax,'%Y%m%d')
if args.fignam is None:
    args.fignam = 'test.pdf'
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
params = None
object_ids = None
inp_dtim = []
inp_data = []
if args.inp_csv:
    columns = None
    ext = '\.csv$'
else:
    ext = '\.npz$'
if args.atcor:
    tnam = '_atcor'
else:
    tnam = '_parcel'
for year in data_years:
    ystr = '{}'.format(year)
    dnam = os.path.join(args.inpdir,ystr)
    if not os.path.isdir(dnam):
        continue
    for f in sorted(os.listdir(dnam)):
        m = re.search('^('+'\d'*8+')'+tnam+ext,f)
        if not m:
            continue
        dstr = m.group(1)
        d = datetime.strptime(dstr,'%Y%m%d')
        if d < d1 or d > d2:
            continue
        fnam = os.path.join(dnam,f)
        if args.inp_csv:
            df = pd.read_csv(fnam,comment='#')
            df.columns = df.columns.str.strip()
            if columns is None:
                columns = df.columns
                if columns[0].upper() != 'OBJECTID':
                    raise ValueError('Error columns[0]={} (!= OBJECTID) >>> {}'.format(columns[0],fnam))
                params = columns[1:]
            elif not np.array_equal(df.columns,columns):
                raise ValueError('Error, different columns >>> {}'.format(fnam))
            if object_ids is None:
                object_ids = df.iloc[:,0].astype(int)
            elif not np.array_equal(df.iloc[:,0].astype(int),object_ids):
                raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
            inp_data.append(df.iloc[:,1:].astype(float))
        else:
            data = np.load(fnam)
            if object_ids is None:
                object_ids = data['object_ids']
                params = data['params']
            elif not np.array_equal(data['object_ids'],object_ids):
                raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
            elif not np.array_equal(data['params'],params):
                raise ValueError('Error, different parameter >>> {}'.format(fnam))
            inp_data.append(data['data'])
        inp_dtim.append(d)
inp_dtim = np.array(inp_dtim)
inp_ntim = date2num(inp_dtim)
inp_data = np.array(inp_data) # (NDAT,NOBJECT,NBAND)
inp_ndat = len(inp_dtim)
nobject = len(object_ids)
if inp_ndat < 5 or nobject < 1:
    raise ValueError('Error, inp_ndat={}, nobject={}'.format(inp_ndat,nobject))

# Make output time list
out_dtim = []
d = d1
while d <= d2:
    out_dtim.append(d)
    d += timedelta(days=args.tstp)
out_dtim = np.array(out_dtim)
out_ntim = date2num(out_dtim)

# Make output file list
out_idats = []
out_fnams = []
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
    out_idats.append(idat)
    out_fnams.append(fnam)
if len(out_idats) < 1:
    sys.stderr.write('No need to interpolate data.\n')
    sys.stderr.flush()
    sys.exit()

# Interpolate data
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(6,3.5))
    plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.90)
    pdf = PdfPages(args.fignam)
    fig_interval = int(np.ceil(nobject/args.nfig)+0.1)
out_ndat = len(out_dtim)
out_nb = len(params)
out_data = np.full((out_ndat,nobject,out_nb),np.nan)
for iobj,object_id in enumerate(object_ids):
    if args.debug and (iobj%fig_interval == 0):
        fig_flag = True
    else:
        fig_flag = False
    for iband,param in enumerate(params):
        cnd = ~np.isnan(inp_data[:,iobj,iband])
        xc = inp_ntim[cnd]
        yc = inp_data[cnd,iobj,iband]
        if xc.size > 4:
            x1 = np.gradient(xc)
            y1 = np.gradient(yc)/x1
            y2 = np.gradient(y1)/x1
            ye = np.std(y2)
            cnd = np.abs(y2) < ye*args.ethr
            ys = csaps(xc[cnd],yc[cnd],out_ntim,smooth=args.smooth)
            out_data[:,iobj,iband] = ys
            if fig_flag:
                fig.clear()
                ax1 = plt.subplot(111)
                ax1.plot(xc,yc,'b-')
                ax1.plot(xc[cnd],yc[cnd],'g-')
                ax1.plot(out_dtim,ys,'r-')
                xmin = xc.min()
                xmax = xc.max()
                xdif = xmax-xmin
                ymin = yc.min()
                ymax = yc.max()
                ydif = ymax-ymin
                if xdif < 365.0:
                    ax1.xaxis.set_major_locator(MonthLocator())
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                else:
                    ax1.xaxis.set_major_locator(MonthLocator(bymonth=[1,7]))
                    ax1.xaxis.set_minor_locator(MonthLocator())
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                ax1.set_xlim(xmin,xmax)
                ax1.set_ylim(ymin-0.1*ydif,ymax+0.1*ydif)
                ax1.set_ylabel(param)
                if args.ax1_title is not None:
                    ax1.set_title('{} (OBJECTID={})'.format(args.ax1_title,object_id))
                else:
                    ax1.set_title('OBJECTID={}'.format(object_id))
                fig.autofmt_xdate()
                plt.savefig(pdf,format='pdf')
                if not args.batch:
                    plt.draw()
                    plt.pause(0.1)
if args.debug:
    pdf.close()

# Output CSV
for idat,fnam in zip(out_idats,out_fnams):
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
