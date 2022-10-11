#!/usr/bin/env python
import os
import re
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
PARAMS = ['plant_d','peak_d','head_d','assess_d','harvest_d']
# plant_d   : Planting date
# peak_d    : Heading date (peak of NDVI)
# head_d    : Heading date (between two peaks of NDVI 2nd difference)
# assess_d  : Assessment date
# harvest_d : Harvesting date

# Default values
PARAM = ['plant_d','peak_d','head_d','assess_d','harvest_d']

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.param is None:
    args.param = PARAM
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if args.ax1_zmin is not None:
    while len(args.ax1_zmin) < len(args.param):
        args.ax1_zmin.append(args.ax1_zmin[-1])
    ax1_zmin = {}
    for i,param in enumerate(args.param):
        ax1_zmin[param] = args.ax1_zmin[i]
if args.ax1_zmax is not None:
    while len(args.ax1_zmax) < len(args.param):
        args.ax1_zmax.append(args.ax1_zmax[-1])
    ax1_zmax = {}
    for i,param in enumerate(args.param):
        ax1_zmax[param] = args.ax1_zmax[i]
if args.ax1_zstp is not None:
    while len(args.ax1_zstp) < len(args.param):
        args.ax1_zstp.append(args.ax1_zstp[-1])
    ax1_zstp = {}
    for i,param in enumerate(args.param):
        ax1_zstp[param] = args.ax1_zstp[i]
if args.fignam is None:
    bnam,enam = os.path.splitext(os.path.basename(args.shp_fnam))
    if args.fignam is None:
        args.fignam = bnam+'_phenology.pdf'

indices = gpd.read_file(args.shp_fnam)
if not args.batch:
    plt.interactive(True)
fig = plt.figure(1,facecolor='w',figsize=(5,5))
plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.80)
pdf = PdfPages(args.fignam)
for iband,param in enumerate(args.param):
    data = indices[param]
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
    indices.plot(column=param,ax=ax1,vmin=zmin,vmax=zmax,cmap=cm.jet)
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
    ax2.yaxis.set_label_coords(5.5,0.5)
    fig_xmin,fig_ymin,fig_xmax,fig_ymax = indices.total_bounds
    ax1.set_xlim(fig_xmin,fig_xmax)
    ax1.set_ylim(fig_ymin,fig_ymax)
    if args.ax1_title is not None:
        ax1.set_title(args.ax1_title)
    plt.savefig(pdf,format='pdf')
    if not args.batch:
        plt.draw()
        plt.pause(0.1)
pdf.close()
