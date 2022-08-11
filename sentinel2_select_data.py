#!/usr/bin/env python
import os
import sys
import shutil
import re
from datetime import datetime,timedelta
import shapefile
import numpy as np
import pandas as pd
from matplotlib.dates import date2num,num2date
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
PARAM = 'harvest_d'
OFFSET = -10.0 # day

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-T','--tendir',default=None,help='Tentative data directory (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-o','--out_shp',default=None,help='Output Shapefile name (%(default)s)')
parser.add_argument('-P','--phenology',default=None,help='Phenology CSV name (%(default)s)')
parser.add_argument('-p','--param',default=PARAM,help='Parameter for selection (%(default)s)')
parser.add_argument('--offset',default=OFFSET,type=float,help='Offset in day (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.phenology is None or not os.path.exists(args.phenology):
    raise IOError('Error, no such file >>> {}'.format(args.phenology))
if args.out_csv is None or args.out_shp is None or args.fignam is None:
    bnam = 'assess'
    if args.out_csv is None:
        args.out_csv = bnam+'_select.csv'
    if args.out_shp is None:
        args.out_shp = bnam+'_select.shp'
    if args.fignam is None:
        args.fignam = bnam+'_select.pdf'

# Read phenology CSV
df = pd.read_csv(args.phenology,comment='#')
df.columns = df.columns.str.strip()
columns = df.columns.to_list()
if not 'OBJECTID' in columns:
    raise ValueError('Error in finding OBJECTID >>> {}'.format(args.phenology))
iband = columns.index('OBJECTID')
object_ids = df.iloc[:,iband].astype(int)
nobject = len(object_ids)
if not args.param in columns:
    raise ValueError('Error in finding {} >>> {}'.format(args.param,args.phenology))
iband = columns.index(args.param)
assess_d = df.iloc[:,iband].astype(float).values # Assessment date
if np.abs(args.offset) > EPSILON:
    assess_d += args.offset
cnd = np.isnan(assess_d)
assess_d = (assess_d+0.5).astype(np.int32)
assess_d[cnd] = -1
inp_ntim = np.unique(assess_d[~cnd])
inp_dtim = num2date(inp_ntim)
inp_ndat = len(inp_ntim)
if inp_ndat < 1 or nobject < 1:
    raise ValueError('Error, inp_ndat={}, nobject={}'.format(inp_ndat,nobject))

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
        all_ids = np.array(all_ids)
    if not np.array_equal(all_ids,object_ids):
        raise ValueError('Error, different OBJECTID >>> {}'.format(args.shp_fnam))

# Read indices
columns = None
inp_data = []
for d in inp_dtim:
    ystr = '{}'.format(d.year)
    dstr = '{:%Y%m%d}'.format(d)
    fnam = os.path.join(args.inpdir,ystr,'{}_interp.csv'.format(dstr))
    if not os.path.exists(fnam):
        gnam = os.path.join(args.tendir,ystr,'{}_interp.csv'.format(dstr))
        if not os.path.exists(gnam):
            raise IOError('Error, no such file >>> {}\n{}'.format(fnam,gnam))
        else:
            fnam = gnam
    df = pd.read_csv(fnam,comment='#')
    df.columns = df.columns.str.strip()
    if columns is None:
        columns = df.columns
        if columns[0].upper() != 'OBJECTID':
            raise ValueError('Error columns[0]={} (!= OBJECTID) >>> {}'.format(columns[0],fnam))
    elif not np.array_equal(df.columns,columns):
        raise ValueError('Error, different columns >>> {}'.format(fnam))
    if not np.array_equal(df.iloc[:,0].astype(int),object_ids):
        raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
    inp_data.append(df.iloc[:,1:].astype(float))
inp_data = np.array(inp_data) # (NDAT,NOBJECT)

for iobj,object_id in enumerate(object_ids):
    x_assess = assess_d[iobj]
    if x_assess < 0:
        continue
    d = num2date(x_assess+0.5)


"""
# Estimate heading/harvesting/assessment dates
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(6,3.5))
    plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.70)
    pdf = PdfPages(args.fignam)
    fig_interval = int(np.ceil(nobject/args.nfig)+0.1)
all_data = np.full((nobject,len(PARAMS)),np.nan)
for iobj,object_id in enumerate(object_ids):
    if args.debug and (iobj%fig_interval == 0):
        fig_flag = True
    else:
        fig_flag = False
    x_trans = trans_d[iobj]
    if np.isnan(x_trans):
        continue
    grow_cnd = (inp_ntim >= x_trans) & (inp_ntim <= x_trans+args.grow_period)
    x = inp_ntim[grow_cnd]
    y = inp_ndvi[grow_cnd,iobj]
    if (x.size < 5) or np.any(np.isnan(y)):
        continue
    indx = np.argmax(y)
    x_peak = x[indx] # NDVI-peak date
    y_peak = y[indx] # NDVI-peak
    if args.head is not None and not np.isnan(head_d[iobj]):
        x_head = head_d[iobj]
        if fig_flag:
            y1 = np.gradient(inp_ndvi[:,iobj])
            y2 = np.gradient(csaps(inp_ntim,y1,inp_ntim,smooth=args.smooth))
            y1 = y1[grow_cnd]
            y2 = y2[grow_cnd]
            xp_1 = np.nan
            xp_2 = np.nan
        else:
            y1 = None
    else:
        y1 = np.gradient(inp_ndvi[:,iobj])
        y2 = np.gradient(csaps(inp_ntim,y1,inp_ntim,smooth=args.smooth))
        y1 = y1[grow_cnd]
        y2 = y2[grow_cnd]
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
    if args.harvest is not None and not np.isnan(harvest_d[iobj]):
        x_harvest = harvest_d[iobj]
        if fig_flag:
            indx = np.argmin(np.abs(x-x_harvest))
            y_harvest = y1[indx]
    else:
        if y1 is None:
            y1 = np.gradient(inp_ndvi[:,iobj])
            y1 = y1[grow_cnd]
        cnd = (x >= x_peak+args.dthr2)
        xc = x[cnd]
        y1c = y1[cnd]
        indx = np.argmin(y1c)
        if y1c[indx] > args.sthr:
            x_harvest = np.nan
            y_harvest = np.nan
        else:
            x_harvest = xc[indx]
            y_harvest = y1c[indx]
    if args.assess is not None and not np.isnan(assess_d[iobj]):
        x_assess = assess_d[iobj]
    else:
        x_assess = x_head+(x_harvest-x_head)*args.atc-args.offset
        if x_assess-x_trans > args.grow_period:
            x_assess = np.nan
    all_data[iobj,0] = x_trans
    all_data[iobj,1] = x_peak
    all_data[iobj,2] = x_head
    all_data[iobj,3] = x_harvest
    all_data[iobj,4] = x_assess
    if fig_flag:
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
"""
