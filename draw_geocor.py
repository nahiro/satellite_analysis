import os
import re
import zlib # to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
from glob import glob
import numpy as np
import shapefile
from shapely.geometry import shape
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
S2_BAND = {'b':'B2','g':'B3','r':'B4','e1':'B5','e2':'B6','e3':'B7','n1':'B8','n2':'B8A','s1':'B11','s2':'B12'}
SC_BAND = 'quality_scene_classification'

# Default values
FACT = 1.5
GAMMA = 2.2
FIGNAM = 'geocor.pdf'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-f','--img_fnam',default=None,help='Image file name (%(default)s)')
parser.add_argument('-s','--shp_fnam',default=None,help='Shape file name (%(default)s)')
parser.add_argument('-F','--fignam',default=FIGNAM,help='Output figure name (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title (%(default)s)')
parser.add_argument('-S','--fact',default=FACT,type=float,help='Scale factor of output figure for debug (%(default)s)')
parser.add_argument('-G','--gamma',default=GAMMA,type=float,help='Gamma factor of output figure for debug (%(default)s)')
parser.add_argument('-D','--fig_dpi',default=None,type=int,help='DPI of figure for debug (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()

if not args.batch:
    plt.interactive(True)
fig = plt.figure(1,facecolor='w',figsize=(5,5))
plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.95)
pdf = PdfPages(args.fignam)

ds = gdal.Open(args.img_fnam)
src_nb = ds.RasterCount
src_trans = ds.GetGeoTransform()
src_shape = (ds.RasterYSize,ds.RasterXSize)
src_band = []
for i in range(src_nb):
    band = ds.GetRasterBand(i+1)
    src_band.append(band.GetDescription())
src_data = ds.ReadAsArray()
ds = None
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_xstp*src_shape[1]
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ystp*src_shape[0]
for band in ['b','g','r']:
    band_name = S2_BAND[band]
    if not band_name in src_band:
        raise ValueError('Error in finding {} >>> {}'.format(band_name,args.img_fnam))
b_indx = src_band.index(S2_BAND['b'])
g_indx = src_band.index(S2_BAND['g'])
r_indx = src_band.index(S2_BAND['r'])
scl_indx = src_band.index(SC_BAND)
b = src_data[b_indx].astype(np.float32)
g = src_data[g_indx].astype(np.float32)
r = src_data[r_indx].astype(np.float32)
scl = src_data[scl_indx].astype(np.float32)
fact = args.fact*1.0e-4
b = (b*fact).clip(0,1)
g = (g*fact).clip(0,1)
r = (r*fact).clip(0,1)
rgb = np.power(np.dstack((r,g,b)),1.0/args.gamma)
fig.clear()
axs = plt.subplot(111)
axs.xaxis.set_ticks([])
axs.yaxis.set_ticks([])
axs.imshow(rgb,extent=(src_xmin,src_xmax,src_ymin,src_ymax),origin='upper',interpolation='none')
divider = make_axes_locatable(axs)
cax = divider.append_axes('right',size='5%',pad=0.05)
cax.set_visible(False)
if args.shp_fnam is not None:
    shp = shape(shapefile.Reader(args.shp_fnam).shapes())
    axs.add_patch(plt.Polygon(shp.points,edgecolor='k',facecolor='none',linestyle='-',alpha=1.0,linewidth=0.02))
axs.set_xlim(src_xmin,src_xmax)
axs.set_ylim(src_ymin,src_ymax)
if args.ax1_title is not None:
    axs.set_title('{} (RGB)'.format(args.ax1_title))
if args.fig_dpi is None:
    plt.savefig(pdf,format='pdf')
else:
    plt.savefig(pdf,dpi=args.fig_dpi,format='pdf')
if not args.batch:
    plt.draw()
    plt.pause(0.1)

fig.clear()
axs = plt.subplot(111)
axs.xaxis.set_ticks([])
axs.yaxis.set_ticks([])
scl[scl >= 7.5] = np.nan
bounds = np.arange(0.5,7.6,1.0)
cmap = mpl.colors.ListedColormap(['red','#666666','brown','g','y','b','m'])
cmap.set_over('w')
cmap.set_under('k')
norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
im = axs.imshow(scl,extent=(src_xmin,src_xmax,src_ymin,src_ymax),origin='upper',interpolation='none',cmap=cmap,norm=norm) # scene_classification
divider = make_axes_locatable(axs)
cax = divider.append_axes('right',size='5%',pad=0.05)
cax.set_visible(False)
fig.canvas.draw()
axs2 = fig.add_axes(cax.get_position().bounds)
plt.colorbar(im,cax=axs2,extend='both',boundaries=[-10]+list(bounds)+[10],extendfrac='auto',ticks=bounds+0.5)
#axs2.set_ylabel('Label')
axs2.yaxis.set_label_coords(3.0,0.5)
axs.set_xlim(src_xmin,src_xmax)
axs.set_ylim(src_ymin,src_ymax)
if args.shp_fnam is not None:
    shp = shape(shapefile.Reader(args.shp_fnam).shapes())
    axs.add_patch(plt.Polygon(shp.points,edgecolor='k',facecolor='none',linestyle='-',alpha=1.0,linewidth=0.02))
if args.ax1_title is not None:
    axs.set_title('{} (Scene Classification)'.format(args.ax1_title))
if args.fig_dpi is None:
    plt.savefig(pdf,format='pdf')
else:
    plt.savefig(pdf,dpi=args.fig_dpi,format='pdf')
if not args.batch:
    plt.draw()
pdf.close()
