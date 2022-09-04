#!/usr/bin/env python
import os
import sys
import re
import warnings
try:
    import gdal
except Exception:
    from osgeo import gdal
from datetime import datetime
import numpy as np
from matplotlib.dates import date2num,num2date
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.offsetbox import AnchoredText
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
BAND = '4'
RTHR = 1.0
MTHR = 2.0
BAND4_MAX = 0.35
INDS_FNAM = 'nearest_inds.npy'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-N','--norm_band',default=None,action='append',help='Wavelength band for normalization ({})'.format(NORM_BAND))
parser.add_argument('-r','--rgi_red_band',default=RGI_RED_BAND,help='Wavelength band for RGI (%(default)s)')
parser.add_argument('-b','--band',default=BAND,help='Target band (%(default)s)')
parser.add_argument('-v','--vthr',default=None,type=float,help='Absolute threshold to remove outliers (%(default)s)')
parser.add_argument('-r','--rthr',default=RTHR,type=float,help='Relative threshold for 2-step outlier removal (%(default)s)')
parser.add_argument('--mthr',default=MTHR,type=float,help='Multiplying factor of vthr for 2-step outlier removal (%(default)s)')
parser.add_argument('--band4_max',default=BAND4_MAX,type=float,help='Band4 threshold (%(default)s)')
parser.add_argument('-x','--ax1_xmin',default=None,type=float,action='append',help='Axis1 X min for debug (%(default)s)')
parser.add_argument('-X','--ax1_xmax',default=None,type=float,action='append',help='Axis1 X max for debug (%(default)s)')
parser.add_argument('-y','--ax1_ymin',default=None,type=float,action='append',help='Axis1 Y min for debug (%(default)s)')
parser.add_argument('-Y','--ax1_ymax',default=None,type=float,action='append',help='Axis1 Y max for debug (%(default)s)')
parser.add_argument('--mask_fnam',default=None,help='Mask file name (%(default)s)')
parser.add_argument('--stat_fnam',default=None,help='Statistic file name (%(default)s)')
parser.add_argument('--inds_fnam',default=INDS_FNAM,help='Index file name (%(default)s)')
parser.add_argument('-F','--fig_fnam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--nfig',default=NFIG,type=int,help='Max number of figure for debug (%(default)s)')
parser.add_argument('-o','--out_fnam',default=None,help='Output NPZ name (%(default)s)')
parser.add_argument('--ignore_band4',default=False,action='store_true',help='Ignore exceeding the band4 threshold (%(default)s)')
parser.add_argument('--outlier_remove2',default=False,action='store_true',help='2-step outlier removal mode (%(default)s)')
parser.add_argument('--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
args = parser.parse_args()
if args.ax1_xmin is not None:
    while len(args.ax1_xmin) < len(args.param):
        args.ax1_xmin.append(args.ax1_xmin[-1])
if args.ax1_xmax is not None:
    while len(args.ax1_xmax) < len(args.param):
        args.ax1_xmax.append(args.ax1_xmax[-1])
if args.ax1_ymin is None:
    args.ax1_ymin = args.ax1_xmin
else:
    while len(args.ax1_ymin) < len(args.param):
        args.ax1_ymin.append(args.ax1_ymin[-1])
if args.ax1_ymax is None:
    args.ax1_ymax = args.ax1_xmax
else:
    while len(args.ax1_ymax) < len(args.param):
        args.ax1_ymax.append(args.ax1_ymax[-1])
if args.out_fnam is None or args.fig_fnam is None:
    bnam,enam = os.path.splitext(args.src_geotiff)
    if args.out_fnam is None:
        args.out_fnam = '{}_atcor_fit.npz'.format(bnam)
    if args.fig_fnam is None:
        args.fig_fnam = '{}_atcor_fit.pdf'.format(bnam)

# Read Source GeoTIFF
ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = len(band_list)
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
src_meta = ds.GetMetadata()
src_data = []
src_band = []
for band in band_list:
    bnam = band_dict[band]
    if not bnam in band_name:
        raise ValueError('Error, {} is not in the band name list.'.format(bnam))
    iband = band_name.index(bnam)
    b = ds.GetRasterBand(iband+1)
    src_data.append(b.ReadAsArray().astype(np.float64).reshape(src_ny,src_nx))
    src_band.append(b.GetDescription())
src_data = np.array(src_data)
src_dtype = b.DataType
src_nodata = b.GetNoDataValue()
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp
ds = None
if src_nodata is not None and not np.isnan(src_nodata):
    src_data[src_data == src_nodata] = np.nan

# Read Mask GeoTIFF
if args.mask_geotiff is not None:
    ds = gdal.Open(args.mask_geotiff)
    mask_nx = ds.RasterXSize
    mask_ny = ds.RasterYSize
    mask_nb = ds.RasterCount
    if mask_nb != 1:
        raise ValueError('Error, mask_nb={} >>> {}'.format(mask_nb,args.mask_geotiff))
    mask_shape = (mask_ny,mask_nx)
    if mask_shape != src_shape:
        raise ValueError('Error, mask_shape={}, src_shape={} >>> {}'.format(mask_shape,src_shape,args.mask_geotiff))
    mask_data = ds.ReadAsArray().reshape(mask_ny,mask_nx)
    ds = None
    src_data[:,mask_data < 0.5] = np.nan

stat = np.load(args.stat_fnam)
data_y_all = stat['mean'].flatten()
nearest_inds = np.load(args.inds_fnam)
nobject = len(nearest_inds)

data_x_all = data_img.flatten()
data_b_all = b4_img.flatten()
if data_x_all.shape != data_y_all.shape:
    raise ValueError('Error, data_x_all.shape={}, data_y_all.shape={}'.format(data_x_all.shape,data_y_all.shape))

if args.debug:
    #plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(6,5))
    plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.90)
    pdf = PdfPages(args.fig_fnam)
    xfit = np.arange(-1.0,1.001,0.01)
else:
    warnings.simplefilter('ignore')

number = []
corcoef = []
b4_mean = []
b4_std = []
factor = []
offset = []
rmse = []
for i in range(nobject):
    if args.debug and (i%500 == 0):
        sys.stderr.write('{}\n'.format(i))
    object_id = i+1
    indx = nearest_inds[i]
    data_x = data_x_all[indx]
    data_y = data_y_all[indx]
    data_b = data_b_all[indx]
    if args.outlier_remove2:
        cnd1 = (~np.isnan(data_x)) & (np.abs(data_x-data_y) < (np.abs(data_y)*args.rthr).clip(min=args.vthr*args.mthr))
    else:
        cnd1 = ~np.isnan(data_x)
    if not args.ignore_band4:
        cnd1 &= ((~np.isnan(data_b)) & (data_b < args.band4_max))
    xcnd = data_x[cnd1]
    ycnd = data_y[cnd1]
    bcnd = data_b[cnd1]
    if xcnd.size < 2:
        result = [np.nan,np.nan]
        calc_y = np.array([])
        r_value = np.nan
        b4_value = np.nan
        b4_error = np.nan
        rms_value = np.nan
        flag = False
    else:
        result = np.polyfit(xcnd,ycnd,1)
        calc_y = xcnd*result[0]+result[1]
        cnd2 = np.abs(calc_y-ycnd) < args.vthr
        xcnd2 = xcnd[cnd2]
        ycnd2 = ycnd[cnd2]
        bcnd2 = bcnd[cnd2]
        if (xcnd2.size == cnd2.size) or (xcnd2.size < 2):
            r_value = np.corrcoef(xcnd,ycnd)[0,1]
            b4_value = np.nanmean(bcnd)
            b4_error = np.nanstd(bcnd)
            rms_value = np.sqrt(np.square(calc_y-ycnd).sum()/calc_y.size)
            flag = False
        else:
            result = np.polyfit(xcnd2,ycnd2,1)
            calc_y = xcnd2*result[0]+result[1]
            r_value = np.corrcoef(xcnd2,ycnd2)[0,1]
            b4_value = np.nanmean(bcnd2)
            b4_error = np.nanstd(bcnd2)
            rms_value = np.sqrt(np.square(calc_y-ycnd2).sum()/calc_y.size)
            flag = True
    number.append(calc_y.size)
    corcoef.append(r_value)
    b4_mean.append(b4_value)
    b4_std.append(b4_error)
    factor.append(result[0])
    offset.append(result[1])
    rmse.append(rms_value)
    if args.debug:
        fig.clear()
        ax1 = plt.subplot(111)#,aspect='equal')
        ax1.minorticks_on()
        ax1.grid(True)
        line = 'number: {}\n'.format(calc_y.size)
        line += 'coeff: {:7.4f}\n'.format(r_value)
        line += 'band4: {:6.4f}\n'.format(b4_value)
        line += 'factor: {:5.4f}\n'.format(result[0])
        line += 'offset: {:5.4f}\n'.format(result[1])
        line += 'rmse: {:5.4f}'.format(rms_value)
        at= AnchoredText(line,prop=dict(size=12),loc=2,pad=0.1,borderpad=0.8,frameon=True)
        at.patch.set_boxstyle('round')
        ax1.add_artist(at)
        if xcnd.size != cnd1.size:
            ax1.plot(data_x,data_y,'k.')
        if flag:
            ax1.plot(xcnd,ycnd,'.',color='#888888')
            ax1.plot(xcnd2,ycnd2,'b.')
        else:
            ax1.plot(xcnd,ycnd,'b.')
        ax1.plot(xfit,np.polyval(result,xfit),'k:')
        ax1.set_xlim(args.ax1_xmin,args.ax1_xmax)
        ax1.set_ylim(args.ax1_ymin,args.ax1_ymax)
        ax1.set_xlabel(band_u)
        ax1.set_ylabel(band_u+' mean')
        ax1.xaxis.set_tick_params(pad=7)
        ax1.xaxis.set_label_coords(0.5,-0.14)
        ax1.yaxis.set_label_coords(-0.15,0.5)
        ax2.yaxis.set_label_coords(5.0,0.5)
        ax1.set_title('{} (OBJECTID={})'.format(dstr,object_id))
        plt.savefig(pdf,format='pdf')
        #plt.draw()
        #plt.pause(0.1)
        #break
if args.debug:
    pdf.close()
number = np.array(number)
corcoef = np.array(corcoef)
b4_mean = np.array(b4_mean)
b4_std = np.array(b4_std)
factor = np.array(factor)
offset = np.array(offset)
rmse = np.array(rmse)
np.savez(args.out_fnam,number=number,corcoef=corcoef,b4_mean=b4_mean,b4_std=b4_std,factor=factor,offset=offset,rmse=rmse)
