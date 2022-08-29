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
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
EPSILON = 1.0e-6 # a small number
PARAMS = ['trans_d','peak_d','head_d','assess_d','harvest_d']
# trans_d   : Transplanting date
# peak_d    : Heading date (peak of NDVI)
# head_d    : Heading date (between two peaks of NDVI 2nd difference)
# assess_d  : Assessment date
# harvest_d : Harvesting date

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
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter for selection >>> {}'.format(param))
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
inp_ntim = np.unique(assess_d[~cnd]).tolist()
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
params = columns[1:]
inp_data = np.array(inp_data) # (NDAT,NOBJECT)

out_nb = len(params)
out_data = np.full((nobject,out_nb),np.nan)
for iobj,object_id in enumerate(object_ids):
    x_assess = assess_d[iobj]
    if x_assess < 0:
        continue
    indx = inp_ntim.index(x_assess)
    out_data[iobj] = inp_data[indx,iobj]

# Output CSV
with open(args.out_csv,'w') as fp:
    fp.write('{:>8s}'.format('OBJECTID'))
    for param in params:
        fp.write(', {:>13s}'.format(param))
    fp.write('\n')
    for iobj,object_id in enumerate(object_ids):
        fp.write('{:8d}'.format(object_id))
        for iband,param in enumerate(params):
            fp.write(', {:>13.6e}'.format(out_data[iobj,iband]))
        fp.write('\n')

# Output Shapefile
if args.shp_fnam is not None and args.out_shp is not None:
    w = shapefile.Writer(args.out_shp)
    w.shapeType = shapefile.POLYGON
    w.fields = r.fields[1:] # skip first deletion field
    for param in params:
        w.field(param,'F',13,6)
    for iobj,shaperec in enumerate(r.iterShapeRecords()):
        rec = shaperec.record
        shp = shaperec.shape
        rec.extend(list(out_data[iobj]))
        w.shape(shp)
        w.record(*rec)
    w.close()
    shutil.copy2(os.path.splitext(args.shp_fnam)[0]+'.prj',os.path.splitext(args.out_shp)[0]+'.prj')

# For debug
if args.shp_fnam is not None and args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.80)
    pdf = PdfPages(args.fignam)
    for iband,param in enumerate(params):
        data = out_data[:,iband]
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
            zmin = ax1_zmin[param]
        else:
            zmin = np.nanmin(data)
            if np.isnan(zmin):
                zmin = 0.0
        if args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
            zmax = ax1_zmax[param]
        else:
            zmax = np.nanmax(data)
            if np.isnan(zmax):
                zmax = 1.0
        zdif = zmax-zmin
        for iobj,shaperec in enumerate(r.iterShapeRecords()):
            rec = shaperec.record
            shp = shaperec.shape
            z = data[iobj]
            if not np.isnan(z):
                ax1.add_patch(plt.Polygon(shp.points,edgecolor='none',facecolor=cm.jet((z-zmin)/zdif),linewidth=0.02))
        im = ax1.imshow(np.arange(4).reshape(2,2),extent=(-2,-1,-2,-1),vmin=zmin,vmax=zmax,cmap=cm.jet)
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if args.ax1_zstp is not None and not np.isnan(ax1_zstp[param]):
            if args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
                zmin = (np.floor(ax1_zmin[param]/ax1_zstp[param])-1.0)*ax1_zstp[param]
            else:
                zmin = (np.floor(np.nanmin(data)/ax1_zstp[param])-1.0)*ax1_zstp[param]
            if args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
                zmax = ax1_zmax[param]+0.1*ax1_zstp[param]
            else:
                zmax = np.nanmax(data)+0.1*ax1_zstp[param]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,ax1_zstp[param])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel('{}'.format(param))
        ax2.yaxis.set_label_coords(4.5,0.5)
        fig_xmin,fig_ymin,fig_xmax,fig_ymax = r.bbox
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        if args.ax1_title is not None:
            ax1.set_title(args.ax1_title)
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    pdf.close()
