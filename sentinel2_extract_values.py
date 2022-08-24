#!/usr/bin/env python
import os
import sys
import shutil
import re
from datetime import datetime,timedelta
from skimage.measure import points_in_poly
import shapefile
from shapely.geometry import Point,Polygon,shape
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

# Default values
OBS_FNAM = 'observation.csv'
NCHECK = 10
RMAX = 50.0 # m

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('--buffer',default=None,type=float,help='Buffer distance (%(default)s)')
parser.add_argument('-f','--obs_fnam',default=OBS_FNAM,help='Observation file name (%(default)s)')
parser.add_argument('-o','--tobs',default=None,help='Observation date in the format YYYYMMDD (%(default)s)')
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-T','--tendir',default=None,help='Tentative data directory (%(default)s)')
parser.add_argument('-n','--ncheck',default=NCHECK,type=int,help='Number of plots to check (%(default)s)')
parser.add_argument('-R','--rmax',default=RMAX,type=float,help='Maximum distance between bunch and plot center in m (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-H','--header_none',default=False,action='store_true',help='Read csv file with no header (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.out_csv is None or args.fignam is None:
    bnam = 'assess'
    if args.out_csv is None:
        args.out_csv = bnam+'_extract.csv'
    if args.fignam is None:
        args.fignam = bnam+'_extract.pdf'

comments = ''
header = None
loc_bunch = []
number_bunch = []
plot_bunch = []
x_bunch = []
y_bunch = []
rest_bunch = []
with open(args.obs_fnam,'r') as fp:
    #Location, BunchNumber, PlotPaddy, EastingI, NorthingI, PlantDate, Age, Tiller, BLB, Blast, Borer, Rat, Hopper, Drought
    #           15,   1,   1,  750949.8273,  9242821.0756, 2022-01-08,    55,  27,   1,   0,   5,   0,   0,   0
    for line in fp:
        if len(line) < 1:
            continue
        elif line[0] == '#':
            comments += line
            continue
        elif not args.header_none and header is None:
            header = line # skip header
            item = [s.strip() for s in header.split(',')]
            if len(item) < 6:
                raise ValueError('Error in header ({}) >>> {}'.format(args.obs_fnam,header))
            if item[0] != 'Location' or item[1] != 'BunchNumber' or item[2] != 'PlotPaddy' or item[3] != 'EastingI' or item[4] != 'NorthingI':
                raise ValueError('Error in header ({}) >>> {}'.format(args.obs_fnam,header))
            continue
        m = re.search('^([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),(.*)',line)
        if not m:
            continue
        loc_bunch.append(m.group(1).strip())
        number_bunch.append(int(m.group(2)))
        plot_bunch.append(int(m.group(3)))
        x_bunch.append(float(m.group(4)))
        y_bunch.append(float(m.group(5)))
        rest_bunch.append(m.group(6))
loc_bunch = np.array(loc_bunch)
number_bunch = np.array(number_bunch)
indx_bunch = np.arange(len(number_bunch))
plot_bunch = np.array(plot_bunch)
x_bunch = np.array(x_bunch)
y_bunch = np.array(y_bunch)
rest_bunch = np.array(rest_bunch)
plots = np.unique(plot_bunch)

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
x_center = []
y_center = []
for shp in shape(r.shapes()):
    x_center.append(shp.centroid.x)
    y_center.append(shp.centroid.y)
x_center = np.array(x_center)
y_center = np.array(y_center)

# Read indices
dtim = datetime.strptime(args.tobs,'%Y%m%d')
ystr = '{}'.format(dtim.year)
fnam = os.path.join(args.inpdir,ystr,'{}_interp.csv'.format(args.tobs))
if not os.path.exists(fnam):
    gnam = os.path.join(args.tendir,ystr,'{}_interp.csv'.format(args.tobs))
    if not os.path.exists(gnam):
        raise IOError('Error, no such file >>> {}\n{}'.format(fnam,gnam))
    else:
        fnam = gnam
df = pd.read_csv(fnam,comment='#')
df.columns = df.columns.str.strip()
columns = df.columns
if columns[0].upper() != 'OBJECTID':
    raise ValueError('Error columns[0]={} (!= OBJECTID) >>> {}'.format(columns[0],fnam))
if not np.array_equal(df.iloc[:,0].astype(int),object_ids):
    raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
inp_data = df.iloc[:,1:].astype(float).values # (NOBJECT,NBAND)
params = columns[1:]

out_data = {}
out_plot = {}
if args.debug:
    out_inds = {}
    out_weight = {}
for plot in plots:
    cnd = (plot_bunch == plot)
    indx = indx_bunch[cnd]
    ng = number_bunch[indx]
    xg = x_bunch[indx]
    yg = y_bunch[indx]
    observe_inds = []
    observe_nums = {}
    for n,x,y in zip(ng,xg,yg):
        point = np.array([[x,y]])
        r2 = np.square(x_center-x)+np.square(y_center-y)
        inds = np.argsort(r2)[:args.ncheck]
        observe_indx = None
        for indx in inds:
            shp = r.shape(indx)
            if len(shp.points) < 1:
                continue
            if args.buffer is not None:
                poly_buffer = Polygon(shp.points).buffer(args.buffer)
            else:
                poly_buffer = Polygon(shp.points)
            if poly_buffer.area <= 0.0:
                continue
            if poly_buffer.type == 'MultiPolygon':
                for p in poly_buffer.geoms:
                    path_search = np.array(p.exterior.coords.xy).swapaxes(0,1)
                    if points_in_poly(point,path_search)[0]:
                        if observe_indx is None:
                            observe_indx = indx
                        else:
                            sys.stderr.write('Warning, bunch number {} is inside multiple plots.'.format(n))
                            sys.stderr.flush()
            else:
                path_search = np.array(poly_buffer.exterior.coords.xy).swapaxes(0,1)
                if points_in_poly(point,path_search)[0]:
                    if observe_indx is None:
                        observe_indx = indx
                    else:
                        sys.stderr.write('Warning, bunch number {} is inside multiple plots.'.format(n))
                        sys.stderr.flush()
        if observe_indx is None:
            sys.stderr.write('Warning, failed in finding plot for bunch number {}.\n'.format(n))
            sys.stderr.flush()
            if np.sqrt(r2[inds[0]]) < args.rmax:
                observe_indx = inds[0]
            else:
                continue
        if observe_indx in observe_inds:
            observe_nums[observe_indx] += 1
        else:
            observe_inds.append(observe_indx)
            observe_nums[observe_indx] = 1
    observe_inds = np.array(observe_inds)
    if observe_inds.size < 1:
        raise ValueError('Error in finding correspondent plot for plot{}.'.format(plot))
    elif observe_inds.size == 1:
        observe_indx = observe_inds[0]
        out_data[plot] = inp_data[observe_indx]
        out_plot[plot] = object_ids[observe_indx]
    else:
        weight = []
        for observe_indx in observe_inds:
            weight.append(observe_nums[observe_indx])
        weight = np.array(weight).reshape(-1,1)
        cnd = ~np.isnan(inp_data[observe_inds])
        if np.all(cnd):
            out_data[plot] = np.sum(inp_data[observe_inds]*weight,axis=0)/np.sum(weight)
        else:
            out_data[plot] = np.nansum(inp_data[observe_inds]*weight,axis=0)/np.sum(np.int32(cnd)*weight,axis=0)
        out_plot[plot] = object_ids[observe_inds[np.argmax(weight)]]
    if args.debug:
        out_inds[plot] = observe_inds.copy()
        if observe_inds.size == 1:
            out_weight[plot] = None
        else:
            out_weight[plot] = weight.copy()

# Output CSV
with open(args.out_csv,'w') as fp:
    fp.write('{:>8s}'.format('OBJECTID'))
    for param in params:
        fp.write(', {:>13s}'.format(param))
    fp.write('\n')
    for plot in plots:
        object_id = out_plot[plot]
        fp.write('{:8d}'.format(object_id))
        for iband,param in enumerate(params):
            fp.write(', {:>13.6e}'.format(out_data[plot][iband]))
        fp.write('\n')

# For debug
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.80)
    pdf = PdfPages(args.fignam)
    for plot in plots:
        cnd = (plot_bunch == plot)
        indx = indx_bunch[cnd]
        lg = loc_bunch[indx]
        ng = number_bunch[indx]
        xg = x_bunch[indx]
        yg = y_bunch[indx]
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if out_inds[plot].size == 1:
            indx = out_inds[plot][0]
            shp = r.shape(indx)
            ax1.add_patch(plt.Polygon(shp.points,facecolor='none',edgecolor='k',linewidth=2.0))
            fig_xmin,fig_ymin,fig_xmax,fig_ymax = shp.bbox
        else:
            zmin = out_weight[plot].min()
            zmax = out_weight[plot].max()
            zdif = zmax-zmin
            fig_xmin = 1.0e10
            fig_xmax = -1.0e10
            fig_ymin = 1.0e10
            fig_ymax = -1.0e10
            for iobj,indx in enumerate(out_inds[plot]):
                shp = r.shape(indx)
                z = out_weight[plot][iobj]
                ax1.add_patch(plt.Polygon(shp.points,facecolor='none',edgecolor=cm.jet((z-zmin)/zdif),linewidth=2.0))
                x1,y1,x2,y2 = shp.bbox
                if x1 < fig_xmin:
                    fig_xmin = x1
                if x2 > fig_xmax:
                    fig_xmax = x2
                if y1 < fig_ymin:
                    fig_ymin = y1
                if y2 > fig_ymax:
                    fig_ymax = y2
        ax1.plot(xg,yg,'o',ms=10,mfc='none',mec='k')
        for ntmp,xtmp,ytmp in zip(ng,xg,yg):
            if np.isnan(xtmp) or np.isnan(ytmp):
                continue
            ax1.text(xtmp,ytmp,'{}'.format(ntmp))
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        if args.ax1_title is not None:
            ax1.set_title('{} (Plot{})'.format(args.ax1_title,plot))
        else:
            ax1.set_title('Location: {}, Plot: {}'.format(lg[0],plot))
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(1.1)
    pdf.close()
