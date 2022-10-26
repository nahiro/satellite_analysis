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
BAND_NAME = {'Sb':'Blue','Sg':'Green','Sr':'Red','Se1':'RedEdge1','Se2':'RedEdge2','Se3':'RedEdge3','Sn1':'NIR1','Sn2':'NIR2','Ss1':'SWIR1','Ss2':'SWIR2',
             'Nb':'Normalized Blue','Ng':'Normalized Green','Nr':'Normalized Red','Ne1':'Normalized RedEdge1','Ne2':'Normalized RedEdge2','Ne3':'Normalized RedEdge3',
             'Nn1':'Normalized NIR1','Nn2':'Normalized NIR2','Ns1':'Normalized SWIR1','Ns2':'Normalized SWIR2',
             'NDVI':'NDVI','GNDVI':'GNDVI','RGI':'RGI','NRGI':'NRGI'}

# Default values
DATA_TMIN = '20190315'
DATA_TMAX = '20190615'
TMGN = 90 # day
TSTP = 1 # day
SMOOTH = 0.002
NFIG = 1000
RTHR = 0.5
ETHR = 3.0

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-D','--dstdir',default=None,help='Destination directory (%(default)s)')
parser.add_argument('-T','--tendir',default=None,help='Tentative data directory (%(default)s)')
parser.add_argument('--data_tmin',default=DATA_TMIN,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=DATA_TMAX,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=float,help='Margin of input data in day (%(default)s)')
parser.add_argument('--tstp',default=TSTP,type=int,help='Time step in day (%(default)s)')
parser.add_argument('-S','--smooth',default=SMOOTH,type=float,help='Smoothing factor from 0 to 1 (%(default)s)')
parser.add_argument('-R','--rthr',default=RTHR,type=float,help='R threshold (%(default)s)')
parser.add_argument('-E','--ethr',default=ETHR,type=float,help='Max error in sigma for cloud removal (%(default)s)')
parser.add_argument('--out_csv',default=False,action='store_true',help='Output CSV (%(default)s)')
parser.add_argument('--overwrite',default=False,action='store_true',help='Overwrite mode (%(default)s)')
parser.add_argument('--tentative_overwrite',default=False,action='store_true',help='Overwrite tentative data (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--nfig',default=NFIG,type=int,help='Max number of figure for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.fignam is None:
    args.fignam = 'test.pdf'
d1 = datetime.strptime(args.data_tmin,'%Y%m%d')
d2 = datetime.strptime(args.data_tmax,'%Y%m%d')

# Read data
data_years = np.arange(d1.year,d2.year+1,1)
params = None
atcor_params = None
object_ids = None
inp_dtim = []
inp_data = []
inp_rval = []
for year in data_years:
    ystr = '{}'.format(year)
    dnam = os.path.join(args.inpdir,ystr)
    if not os.path.isdir(dnam):
        continue
    for f in sorted(os.listdir(dnam)):
        m = re.search('^('+'\d'*8+')_atcor\.npz$',f)
        if not m:
            continue
        dstr = m.group(1)
        d = datetime.strptime(dstr,'%Y%m%d')
        if d < d1 or d > d2:
            continue
        fnam = os.path.join(dnam,f)
        gnam = os.path.join(dnam,'{}_factor.npz'.format(dstr))
        if not os.path.exists(gnam):
            sys.stderr.write('Warning, no such file >>> {}'.format(gnam))
            sys.stderr.flush()
            continue
        data = np.load(fnam)
        if object_ids is None:
            object_ids = data['object_ids']
            params = data['params']
            atcor_params = data['atcor_params']
        elif not np.array_equal(data['object_ids'],object_ids):
            raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
        elif not np.array_equal(data['params'],params):
            raise ValueError('Error, different parameter >>> {}'.format(fnam))
        elif not np.array_equal(data['atcor_params'],atcor_params):
            raise ValueError('Error, different atcor parameter >>> {}'.format(fnam))
        data2 = np.load(gnam)
        if not np.array_equal(data2['object_ids'],object_ids):
            raise ValueError('Error, different OBJECTID >>> {}'.format(gnam))
        inp_data.append(data['data'])
        inp_rval.append(data2['corcoef'].swapaxes(0,1))
        inp_dtim.append(d)
inp_dtim = np.array(inp_dtim)
inp_ntim = date2num(inp_dtim)
inp_data = np.array(inp_data) # (NDAT,NOBJECT,NBAND)
inp_rval = np.array(inp_rval) # (NDAT,NOBJECT,NBAND)
inp_ndat = len(inp_dtim)
nobject = len(object_ids)
if inp_ndat < 5 or nobject < 1:
    raise ValueError('Error, inp_ndat={}, nobject={}'.format(inp_ndat,nobject))
tmin = inp_dtim.min()+timedelta(days=args.tmgn)
tmax = inp_dtim.max()-timedelta(days=args.tmgn)

# Make output time list
out_dtim = []
d = d1
while d <= d2:
    out_dtim.append(d)
    d += timedelta(days=args.tstp)
out_dtim = np.array(out_dtim)
out_ntim = date2num(out_dtim)

# Make output file list
out_indx_npz = []
out_fnam_npz = []
for idat,dtim in enumerate(out_dtim):
    if dtim < tmin or dtim > tmax:
        dnam = os.path.join(args.tendir,'{}'.format(dtim.year))
        fnam = os.path.join(dnam,'{:%Y%m%d}_interp.npz'.format(dtim))
        if os.path.exists(fnam) and args.tentative_overwrite:
            os.remove(fnam)
    else:
        dnam = os.path.join(args.dstdir,'{}'.format(dtim.year))
        fnam = os.path.join(dnam,'{:%Y%m%d}_interp.npz'.format(dtim))
        if os.path.exists(fnam) and args.overwrite:
            os.remove(fnam)
    if os.path.exists(fnam):
        continue
    if not os.path.exists(dnam):
        os.makedirs(dnam)
    if not os.path.isdir(dnam):
        raise IOError('No such folder >>> {}'.format(dnam))
    out_indx_npz.append(idat)
    out_fnam_npz.append(fnam)
if args.out_csv:
    out_indx_csv = []
    out_fnam_csv = []
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
        out_indx_csv.append(idat)
        out_fnam_csv.append(fnam)
    if len(out_indx_npz) < 1 and len(out_indx_csv) < 1:
        sys.stderr.write('No need to interpolate data.\n')
        sys.stderr.flush()
        sys.exit()
else:
    if len(out_indx_npz) < 1:
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
            if param in atcor_params:
                rc = inp_rval[cnd,iobj,iband]
                cnd2 = (~np.isnan(rc)) & (rc > args.rthr)
                xc2 = xc[cnd2]
                yc2 = yc[cnd2]
                if xc2.size > 4:
                    yt = csaps(xc2,yc2,xc,smooth=args.smooth)
                    yd = yc-yt
                    ye = np.std(yd[cnd2])
                    cnd = np.abs(yd) < ye*args.ethr
                else:
                    x1 = np.gradient(xc)
                    y1 = np.gradient(yc)/x1
                    y2 = np.gradient(y1)/x1
                    ye = np.std(y2)
                    cnd = np.abs(y2) < ye*args.ethr
            else:
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
                ax1.minorticks_on()
                ax1.tick_params('x',length=8,which='major')
                ax1.plot(xc,yc,'b-')
                ax1.plot(xc[~cnd],yc[~cnd],'kx')
                ax1.plot(out_dtim,ys,'r-')
                xmin = xc.min()
                xmax = xc.max()
                xdif = xmax-xmin
                ymin = yc.min()
                ymax = yc.max()
                ydif = ymax-ymin
                if xdif < 365.0:
                    ax1.xaxis.set_major_locator(MonthLocator())
                    ax1.xaxis.set_minor_locator(DayLocator(bymonthday=[16]))
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                elif xdif < 547.0:
                    ax1.xaxis.set_major_locator(MonthLocator(bymonth=[1,4,7,10]))
                    ax1.xaxis.set_minor_locator(MonthLocator())
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                else:
                    ax1.xaxis.set_major_locator(MonthLocator(bymonth=[1,7]))
                    ax1.xaxis.set_minor_locator(MonthLocator())
                    ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                ax1.set_xlim(xmin,xmax)
                ax1.set_ylim(ymin-0.1*ydif,ymax+0.1*ydif)
                ax1.set_ylabel('{}'.format(BAND_NAME[param]))
                if args.ax1_title is not None:
                    ax1.set_title('{} (OBJECTID={})'.format(args.ax1_title,object_id))
                else:
                    ax1.set_title('OBJECTID={}'.format(object_id))
                ax1.yaxis.set_label_coords(-0.12,0.5)
                fig.autofmt_xdate()
                plt.savefig(pdf,format='pdf')
                if not args.batch:
                    plt.draw()
                    plt.pause(0.1)
if args.debug:
    pdf.close()

# Output data
for idat,fnam in zip(out_indx_npz,out_fnam_npz):
    np.savez(fnam,
    params=params,
    atcor_params=atcor_params,
    object_ids=object_ids,
    data=out_data[idat])

# Output CSV
if args.out_csv:
    for idat,fnam in zip(out_indx_csv,out_fnam_csv):
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
