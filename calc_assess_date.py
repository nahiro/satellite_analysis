#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
from matplotlib.dates import date2num,num2date
from csaps import csaps
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
TMIN = '20190315'
TMAX = '20190615'
TMGN = 90 # day
TSTP = 1 # day
SMOOTH = 0.02
GROW_PERIOD = 120.0 # day
DTHR1 = 10.0 # day
DTHR2 = 24.0 # day

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-T','--tendir',default=None,help='Tentative data directory (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-o','--out_shp',default=None,help='Output Shapefile name (%(default)s)')
parser.add_argument('-P','--plant',default=None,help='Planting CSV name (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=float,help='Margin of input data in day (%(default)s)')
parser.add_argument('--tstp',default=TSTP,type=int,help='Time step in day (%(default)s)')
parser.add_argument('-S','--smooth',default=SMOOTH,type=float,help='Smoothing factor for 1st difference from 0 to 1 (%(default)s)')
parser.add_argument('--grow_period',default=GROW_PERIOD,type=float,help='Length of growing period in days (%(default)s)')
parser.add_argument('--dthr1',default=DTHR1,type=float,help='Max difference of heading from the peak in day (%(default)s)')
parser.add_argument('--dthr2',default=DTHR2,type=float,help='Min number of days between heading and harvesting (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--two_peak',default=False,action='store_true',help='Two-peak mode (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.plant is None or not os.path.exists(args.plant):
    raise IOError('Error, no such file >>> {}'.format(args.plant))
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
if args.out_csv is None or args.out_shp is None or args.fignam is None:
    bnam = 'assess_{:%Y%m%d}_{:%Y%m%d}'.format(d1,d2)
    if args.out_csv is None:
        args.out_csv = bnam+'_parcel.csv'
    if args.out_shp is None:
        args.out_shp = bnam+'_parcel.shp'
    if args.fignam is None:
        args.fignam = bnam+'_parcel.pdf'

# Read NDVI data
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

# Read planting data
df = pd.read_csv(args.plant,comment='#')
df.columns = df.columns.str.strip()
if df.columns[0].upper() != 'OBJECTID':
    raise ValueError('Error df.columns[0]={} (!= OBJECTID) >>> {}'.format(df.columns[0],args.plant))
elif not np.array_equal(df.iloc[:,0].astype(int),object_ids):
    raise ValueError('Error, different OBJECTID >>> {}'.format(args.plant))
if not 'trans_d' in df.columns:
    raise ValueError('Error in finding trans_d >>> {}'.format(args.plant))
iband = df.columns.to_list().index('trans_d')
trans_d = df.iloc[:,iband].astype(float).values # Transplanting date
head_d = np.full(nobject,np.nan) # Heading date
harvest_d = np.full(nobject,np.nan) # Harvesting date
harvest_p = np.full(nobject,-1,dtype=np.int32) # Pattern of harvesting date

if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(6,3.5))
    if args.two_peak:
        plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.70)
    else:
        plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.90)
    pdf = PdfPages(args.fignam)
for iobj,object_id in enumerate(object_ids):
    if np.isnan(trans_d[iobj]):
        continue
    cnd = (inp_ntim >= trans_d[iobj]) & (inp_ntim <= trans_d[iobj]+args.grow_period)
    x = inp_ntim[cnd]
    y = inp_ndvi[cnd,iobj]
    if (x.size < 5) or np.any(np.isnan(y)):
        continue
    indx = np.argmax(y)
    x_peak = x[indx] # NDVI-peak date
    y_peak = y[indx] # NDVI-peak
    y1 = np.gradient(y)
    if args.two_peak:
        y2 = np.gradient(csaps(x,y1,x,smooth=args.smooth))
        min_peaks,min_properties = find_peaks(-y2)
        max_peaks,max_properties = find_peaks(y2)
        if (min_peaks.size < 1) or (max_peaks.size < 1):
            xp_1 = x_peak
            xp_2 = x_peak
        else:
            x_mins = x[min_peaks] 
            cnd = (x_mins < x_peak)
            x_mins = x_mins[cnd]
            if x_mins.size < 1:
                xp_1 = x_peak
                xp_2 = x_peak
            else:
                x_min = x_mins[-1]
                x_maxs = x[max_peaks] 
                cnd = (x_maxs > x_min)
                x_maxs = x_maxs[cnd]
                if x_maxs.size < 1:
                    xp_1 = x_peak
                    xp_2 = x_peak
                else:
                    x_max = x_maxs[0]
                    xp_1 = x_min
                    xp_2 = x_max
        x_head = (xp_1+xp_2)*0.5
        if np.abs(x_head-x_peak) > args.dthr1:
            xp_1 = x_peak
            xp_2 = x_peak
            x_head = x_peak
    else:
        x_head = x_peak
    if args.debug:
        fig.clear()
        ax1 = plt.subplot(111)
        ax2 = ax1.twinx()
        ax1.plot(x,y,'b-')
        ax1.plot(x_peak,y_peak,'bo')
        ax2.plot(x,y1*1.0e2,'g-')
        if args.two_peak:
            ax3 = ax1.twinx()
            ax3.spines['right'].set_position(('outward',60))
            ax3.plot(x,y2*1.0e3,'r-')
            ax1.axvline(xp_1,color='k',linestyle=':')
            ax1.axvline(xp_2,color='k',linestyle=':')
        ax1.axvline(x_head,color='r')
        ax1.set_title('OBJECTID: {}'.format(object_id))
        if not args.batch:
            plt.savefig(pdf,format='pdf')
            plt.draw()
            plt.pause(0.1)
    break # for debug
if args.debug:
    pdf.close()

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
