#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
from matplotlib.dates import date2num,num2date,MonthLocator,DayLocator
from csaps import csaps
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
EPSILON = 1.0e-6 # a small number
PARAMS = ['trans_d','peak_d','head_d','harvest_d','assess_d']
# trans_d   : Transplanting date
# peak_d    : Heading date (peak of NDVI)
# head_d    : Heading date (between two peaks of NDVI 2nd difference)
# harvest_d : Harvesting date
# assess_d  : Assessment date

# Default values
TMIN = '20190315'
TMAX = '20190615'
TMGN = 90 # day
TSTP = 1 # day
SMOOTH = 0.02
GROW_PERIOD = 120.0 # day
ATC = 1.1
OFFSET = 10.0 # day
STHR = 0.0
DTHR1 = 10.0 # day
DTHR2 = 10.0 # day

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
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
parser.add_argument('--atc',default=ATC,type=float,help='Assessment timing coefficient (%(default)s)')
parser.add_argument('--offset',default=OFFSET,type=float,help='Offset of assessment timing (%(default)s)')
parser.add_argument('--sthr',default=STHR,type=float,help='Threshold for 1st difference at harvesting (%(default)s)')
parser.add_argument('--dthr1',default=DTHR1,type=float,help='Max difference of heading from the peak in day (%(default)s)')
parser.add_argument('--dthr2',default=DTHR2,type=float,help='Min number of days between peak and harvesting (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
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
all_data = np.full((nobject,len(PARAMS)),np.nan)

# Read Shapefile
if args.shp_fnam is not None:
    r = shapefile.Reader(args.shp_fnam)
    if len(r) != nobject:
        raise ValueError('Error, len()={}, nobject={} >>> {}'.format(len(r),nobject,args.shp_fnam))
    if args.use_index:
        all_ids = np.arange(nobject)+1
    else:
        all_ids = []
        for rec in r.iterRecords():
            all_ids.append(rec.OBJECTID)
        all_inds = np.array(all_inds)
    if not np.array_equal(all_ids,object_ids):
        raise ValueError('Error, different OBJECTID >>> {}'.format(args.shp_fnam))

# Estimate heading/harvesting/assessment dates
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(6,3.5))
    plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.70)
    pdf = PdfPages(args.fignam)
for iobj,object_id in enumerate(object_ids):
    x_trans = trans_d[iobj]
    if np.isnan(x_trans):
        continue
    cnd = (inp_ntim >= x_trans) & (inp_ntim <= x_trans+args.grow_period)
    x = inp_ntim[cnd]
    y = inp_ndvi[cnd,iobj]
    if (x.size < 5) or np.any(np.isnan(y)):
        continue
    indx = np.argmax(y)
    x_peak = x[indx] # NDVI-peak date
    y_peak = y[indx] # NDVI-peak
    y1 = np.gradient(inp_ndvi[:,iobj])
    y2 = np.gradient(csaps(inp_ntim,y1,inp_ntim,smooth=args.smooth))
    y1 = y1[cnd]
    y2 = y2[cnd]
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
    cnd = (x >= x_peak+args.dthr2)
    xc = x[cnd]
    y1c = y1[cnd]
    indx = np.argmin(y1c)
    if y1c[indx] >= args.sthr:
        x_harvest = np.nan
        y_harvest = np.nan
    else:
        x_harvest = xc[indx]
        y_harvest = y1c[indx]
    x_assess = x_head+(x_harvest-x_head)*args.atc-args.offset
    if x_assess-x_trans > args.grow_period:
        x_assess = np.nan
    all_data[iobj,0] = x_trans
    all_data[iobj,1] = x_peak
    all_data[iobj,2] = x_head
    all_data[iobj,3] = x_harvest
    all_data[iobj,4] = x_assess
    if args.debug:
        dtim = num2date(x)
        fig.clear()
        ax1 = plt.subplot(111)
        ax2 = ax1.twinx()
        ax3 = ax1.twinx()
        ax1.minorticks_on()
        ax2.minorticks_on()
        ax3.minorticks_on()
        ax2.spines['right'].set_position(('outward',60))
        ax1.plot(dtim,y,'b-',zorder=10)
        ax1.plot(x_peak,y_peak,'bo',zorder=10)
        ax2.plot(dtim,y1*1.0e2,'g-',zorder=5)
        ax2.plot(x_harvest,y_harvest*1.0e2,'go',zorder=5)
        ax3.plot(dtim,y2*1.0e3,'r-',zorder=1)
        ax1.axvline(xp_1,color='k',linestyle=':',zorder=1)
        ax1.axvline(xp_2,color='k',linestyle=':',zorder=1)
        ax1.axvline(x_head,color='r',zorder=1)
        ax1.axvline(x_assess,color='g',zorder=1)
        ax1.xaxis.set_major_locator(MonthLocator())
        ax1.xaxis.set_minor_locator(DayLocator(bymonthday=(15)))
        ax1.zorder = 10
        ax1.set_frame_on(False)
        ax1.set_ylabel('NDVI')
        ax2.set_ylabel(r'NDVI$^{\prime}$ $\times$ 10$^{2}$')
        ax3.set_ylabel(r'NDVI$^{\prime\prime}$ $\times$ 10$^{3}$')
        ax1.set_title('OBJECTID: {}'.format(object_id))
        fig.autofmt_xdate()
        if not args.batch:
            plt.savefig(pdf,format='pdf')
            plt.draw()
            plt.pause(0.1)
    #break # for debug
if args.debug:
    pdf.close()

# Output CSV
with open(args.out_csv,'w') as fp:
    fp.write('{:>8s}'.format('OBJECTID'))
    for param in PARAMS:
        fp.write(', {:>13s}'.format(param))
    fp.write('\n')
    for iobj,object_id in enumerate(object_ids):
        fp.write('{:8d}'.format(object_id))
        for iband,param in enumerate(PARAMS):
            fp.write(', {:>13.6e}'.format(all_data[iobj,iband]))
        fp.write('\n')

# Output Shapefile
if args.shp_fnam is not None and args.out_shp is not None:
    w = shapefile.Writer(args.out_shp)
    w.shapeType = shapefile.POLYGON
    w.fields = r.fields[1:] # skip first deletion field
    for param in PARAMS:
        w.field(param,'F',13,6)
    for iobj,shaperec in enumerate(r.iterShapeRecords()):
        rec = shaperec.record
        shp = shaperec.shape
        rec.extend(list(all_data[iobj]))
        w.shape(shp)
        w.record(*rec)
    w.close()
    shutil.copy2(os.path.splitext(args.shp_fnam)[0]+'.prj',os.path.splitext(args.out_shp)[0]+'.prj')
