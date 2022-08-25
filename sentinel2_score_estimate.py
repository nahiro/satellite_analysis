#!/usr/bin/env python
import os
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
OBJECTS = ['BLB','Blast','Borer','Rat','Hopper','Drought']
EPSILON = 1.0e-6

# Default values
Y_PARAM = ['BLB']
Y_NUMBER = [1]
SMAX = [9]
SINT = [2]
AX1_VMIN = 0.0
AX1_VMAX = 1.0

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-f','--form_fnam',default=None,help='Input formula file name (%(default)s)')
parser.add_argument('-i','--inp_shp',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-I','--inp_csv',default=None,help='Input CSV name (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-o','--out_shp',default=None,help='Output Shapefile name (%(default)s)')
parser.add_argument('-y','--y_param',default=None,action='append',help='Objective variable ({})'.format(Y_PARAM))
parser.add_argument('--y_number',default=None,type=int,action='append',help='Formula number ({})'.format(Y_NUMBER))
parser.add_argument('-M','--smax',default=None,type=int,action='append',help='Max score ({})'.format(SMAX))
parser.add_argument('-S','--sint',default=None,type=int,action='append',help='Sampling interval for digitizing score ({})'.format(SINT))
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--ax1_vmin',default=AX1_VMIN,type=float,action='append',help='Axis1 V min for debug (%(default)s)')
parser.add_argument('--ax1_vmax',default=AX1_VMAX,type=float,action='append',help='Axis1 V max for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.y_param is None:
    args.y_param = Y_PARAM
for param in args.y_param:
    if not param in OBJECTS:
        raise ValueError('Error, unknown objective variable for y_param >>> {}'.format(param))
if args.y_number is None:
    args.y_number = Y_NUMBER
while len(args.y_number) < len(args.y_param):
    args.y_number.append(args.y_number[-1])
y_number = {}
for i,param in enumerate(args.y_param):
    y_number[param] = args.y_number[i]
if args.smax is None:
    args.smax = SMAX
while len(args.smax) < len(args.y_param):
    args.smax.append(args.smax[-1])
smax = {}
for i,param in enumerate(args.y_param):
    smax[param] = args.smax[i]
if args.sint is None:
    args.sint = SINT
while len(args.sint) < len(args.y_param):
    args.sint.append(args.sint[-1])
sint = {}
for i,param in enumerate(args.y_param):
    sint[param] = args.sint[i]
if args.ax1_zmin is not None:
    while len(args.ax1_zmin) < len(args.y_param):
        args.ax1_zmin.append(args.ax1_zmin[-1])
    ax1_zmin = {}
    for i,param in enumerate(args.y_param):
        ax1_zmin[param] = args.ax1_zmin[i]
if args.ax1_zmax is not None:
    while len(args.ax1_zmax) < len(args.y_param):
        args.ax1_zmax.append(args.ax1_zmax[-1])
    ax1_zmax = {}
    for i,param in enumerate(args.y_param):
        ax1_zmax[param] = args.ax1_zmax[i]
if args.ax1_zstp is not None:
    while len(args.ax1_zstp) < len(args.y_param):
        args.ax1_zstp.append(args.ax1_zstp[-1])
    ax1_zstp = {}
    for i,param in enumerate(args.y_param):
        ax1_zstp[param] = args.ax1_zstp[i]
if args.dst_geotiff is None or args.fignam is None:
    bnam,enam = os.path.splitext(args.src_geotiff)
    if args.dst_geotiff is None:
        args.dst_geotiff = bnam+'_estimate'+enam
    if args.fignam is None:
        args.fignam = bnam+'_estimate.pdf'

# Read Shapefile
r = shapefile.Reader(args.shp_fnam)
nobject = len(r)
if args.use_index:
    object_ids = np.arange(nobject)+1
else:
    list_ids = []
    for rec in r.iterRecords():
        list_ids.append(rec.OBJECTID)
    object_ids = np.array(list_ids)

# Read indices
src_df = pd.read_csv(args.inp_csv,comment='#')
src_df.columns = src_df.columns.str.strip()
if not 'OBJECTID' in src_df.columns:
    raise ValueError('Error in finding OBJECTID >>> {}'.format(args.inp_csv))
if not np.array_equal(src_df['OBJECTID'].astype(int),object_ids):
    raise ValueError('Error, different OBJECTID >>> {}'.format(args.inp_csv))

# Read formula
form_df = pd.read_csv(args.form_fnam,comment='#')
form_df.columns = form_df.columns.str.strip()
form_df['Y'] = form_df['Y'].str.strip()
nmax = form_df['N'].max()+1
for n in range(nmax):
    p = 'P{}_param'.format(n)
    if not p in form_df.columns:
        raise ValueError('Error in finding column for {} >>> {}'.format(p,args.form_fnam))
    form_df[p] = form_df[p].str.strip()
    p = 'P{}_value'.format(n)
    if not p in form_df.columns:
        raise ValueError('Error in finding column for {} >>> {}'.format(p,args.form_fnam))
    form_df[p] = form_df[p].astype(float)

# Calculate damage intensity
out_nb = len(args.y_param)
out_data = np.full((nobject,out_nb),0.0)
for iband,y_param in enumerate(args.y_param):
    cnd = (form_df['Y'] == y_param)
    if cnd.sum() < y_number[y_param]:
        raise ValueError('Error in finding formula for {} >>> {}'.format(y_param,args.inp_fnam))
    formula = form_df[cnd].iloc[y_number[y_param]-1]
    for n in range(nmax):
        p = 'P{}_param'.format(n)
        param = formula[p]
        param_low = param.lower()
        p = 'P{}_value'.format(n)
        coef = formula[p]
        if param_low == 'none':
            continue
        elif param_low == 'const':
            out_data[:,iband] += coef
        else:
            if not param in src_df.columns:
                raise ValueError('Error in finding {} in {}'.format(param,args.inp_csv))
            out_data[:,iband] += coef*src_df[param]

# Output CSV
with open(args.out_csv,'w') as fp:
    fp.write('{:>8s}'.format('OBJECTID'))
    for param in args.y_param:
        fp.write(', {:>13s}'.format(param))
    fp.write('\n')
    for iobj,object_id in enumerate(object_ids):
        fp.write('{:8d}'.format(object_id))
        for iband,param in enumerate(args.y_param):
            fp.write(', {:>13.6e}'.format(out_data[iobj,iband]))
        fp.write('\n')

# Output Shapefile
if args.out_shp is not None:
    w = shapefile.Writer(args.out_shp)
    w.shapeType = shapefile.POLYGON
    w.fields = r.fields[1:] # skip first deletion field
    for param in args.y_param:
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
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.80)
    pdf = PdfPages(args.fignam)
    for iband,param in enumerate(args.y_param):
        data = out_data[:,iband]*100.0
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
            zmin = ax1_zmin[param]
        else:
            zmin = max(np.nanmin(data),args.ax1_vmin*100.0)
            if np.isnan(zmin):
                zmin = 0.0
        if args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
            zmax = ax1_zmax[param]
        else:
            zmax = min(np.nanmax(data),args.ax1_vmax*100.0)
            if np.isnan(zmax):
                zmax = 100.0
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
        ax2.set_ylabel('{} Intensity (%)'.format(param))
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
