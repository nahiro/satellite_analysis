#!/usr/bin/env python
import os
import re
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.offsetbox import AnchoredText
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
EPSILON = 1.0e-5
PARAMS = ['Sb','Sg','Sr','Se1','Se2','Se3','Sn1','Sn2','Ss1','Ss2',
          'Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2',
          'NDVI','GNDVI','RGI','NRGI']
S2_PARAM = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
BAND_NAME = {'b':'Blue','g':'Green','r':'Red','e1':'RedEdge1','e2':'RedEdge2','e3':'RedEdge3','n1':'NIR1','n2':'NIR2','s1':'SWIR1','s2':'SWIR2'}
NORM_BAND = ['b','g','r','e1','e2','e3','n1']

# Default values
PARAM = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','NDVI','GNDVI','NRGI']
CR_BAND = 'r'
CTHR = 0.35
NSTP = 10
ETHR = 2.0
INDS_FNAM = 'nearest_inds.npz'
NFIG = 1000

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-C','--cr_band',default=CR_BAND,help='Wavelength band for cloud removal (%(default)s)')
parser.add_argument('-c','--cthr',default=CTHR,type=float,help='Threshold for cloud removal (%(default)s)')
parser.add_argument('-n','--nstp',default=NSTP,type=int,help='Number of steps for fitting (%(default)s)')
parser.add_argument('-E','--ethr',default=ETHR,type=float,help='Max error in sigma for fitting (%(default)s)')
parser.add_argument('-x','--ax1_xmin',default=None,type=float,action='append',help='Axis1 X min for debug (%(default)s)')
parser.add_argument('-X','--ax1_xmax',default=None,type=float,action='append',help='Axis1 X max for debug (%(default)s)')
parser.add_argument('-y','--ax1_ymin',default=None,type=float,action='append',help='Axis1 Y min for debug (%(default)s)')
parser.add_argument('-Y','--ax1_ymax',default=None,type=float,action='append',help='Axis1 Y max for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--mask_fnam',default=None,help='Mask file name (%(default)s)')
parser.add_argument('--stat_fnam',default=None,help='Statistic file name (%(default)s)')
parser.add_argument('--inds_fnam',default=INDS_FNAM,help='Index file name (%(default)s)')
parser.add_argument('-o','--out_fnam',default=None,help='Output NPZ name (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--nfig',default=NFIG,type=int,help='Max number of figure for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.param is None:
    args.param = PARAM
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if not args.cr_band in S2_PARAM:
    raise ValueError('Error, unknown band for cloud removal >>> {}'.format(args.cr_band))
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
bnam,enam = os.path.splitext(os.path.basename(args.src_geotiff))
if args.out_fnam is None or args.fignam is None:
    if args.out_fnam is None:
        args.out_fnam = '{}_atcor_fit.npz'.format(bnam)
    if args.fignam is None:
        args.fignam = '{}_atcor_fit.pdf'.format(bnam)

# Read Source GeoTIFF
ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = len(args.param)
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
src_band = args.param
tmp_nb = ds.RasterCount
tmp_band = []
for iband in range(tmp_nb):
    band = ds.GetRasterBand(iband+1)
    tmp_band.append(band.GetDescription())
src_data = []
for param in src_band:
    if not param in tmp_band:
        raise ValueError('Error in finding {} in {}'.format(param,args.src_geotiff))
    iband = tmp_band.index(param)
    band = ds.GetRasterBand(iband+1)
    src_data.append(band.ReadAsArray())
src_data = np.array(src_data) # NBAND,NY,NX
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
src_meta = ds.GetMetadata()
param = 'S'+args.cr_band
if not param in tmp_band:
    raise ValueError('Error in finding {} in {}'.format(param,args.src_geotiff))
iband = tmp_band.index(param)
band = ds.GetRasterBand(iband+1)
cr_data = band.ReadAsArray() # NY,NX
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp
ds = None
if src_nodata is not None and not np.isnan(src_nodata):
    src_data[src_data == src_nodata] = np.nan
cnd = (np.isnan(cr_data)) | (cr_data > args.cthr)
src_data[:,cnd] = np.nan
if not 'norm_band' in src_meta:
    sys.stderr.write('Warning, failed in finding {} in metadata >>> {}\n'.format('norm_band',args.src_geotiff))
    sys.stderr.flush()
    norm_band = NORM_BAND
else:
    norm_band = [s.strip() for s in src_meta['norm_band'].split(',')]

# Read Mask GeoTIFF
if args.mask_fnam is not None:
    ds = gdal.Open(args.mask_fnam)
    mask_nx = ds.RasterXSize
    mask_ny = ds.RasterYSize
    mask_nb = ds.RasterCount
    if mask_nb != 1:
        raise ValueError('Error, mask_nb={} >>> {}'.format(mask_nb,args.mask_fnam))
    mask_shape = (mask_ny,mask_nx)
    if mask_shape != src_shape:
        raise ValueError('Error, mask_shape={}, src_shape={} >>> {}'.format(mask_shape,src_shape,args.mask_fnam))
    mask_data = ds.ReadAsArray().reshape(mask_ny,mask_nx)
    ds = None
    cnd = (mask_data < 0.5)
    src_data[:,cnd] = np.nan

# Read Statistic GeoTIFF
ds = gdal.Open(args.stat_fnam)
stat_nx = ds.RasterXSize
stat_ny = ds.RasterYSize
stat_nb = len(args.param)
stat_shape = (stat_ny,stat_nx)
if stat_shape != src_shape:
    raise ValueError('Error, stat_shape={}, src_shape={} >>> {}'.format(stat_shape,src_shape,args.stat_fnam))
stat_band = args.param
tmp_nb = ds.RasterCount
tmp_band = []
for iband in range(tmp_nb):
    band = ds.GetRasterBand(iband+1)
    tmp_band.append(band.GetDescription())
stat_data = []
for param in stat_band:
    if not param in tmp_band:
        raise ValueError('Error in finding {} in {}'.format(param,args.src_geotiff))
    iband = tmp_band.index(param)
    band = ds.GetRasterBand(iband+1)
    stat_data.append(band.ReadAsArray())
stat_data = np.array(stat_data) # NBAND,NY,NX
ds = None

# Read Index
data = np.load(args.inds_fnam)
nearest_inds = data['inds']
object_ids = data['object_ids']
nobject = len(object_ids)

# Calculate correction factor
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(6,6))
    plt.subplots_adjust(top=0.85,bottom=0.20,left=0.15,right=0.90)
    pdf = PdfPages(args.fignam)
    xfit = np.arange(-1.0,float(len(norm_band))+0.001,0.01)
    fig_interval = int(np.ceil(nobject/args.nfig)+0.1)
    pnams = []
    for param in args.param:
        if param in ['NDVI','GNDVI','RGI','NRGI']:
            pnams.append(param)
        elif param[0] == 'S':
            if len(param) in [2,3]:
                band = param[1:]
                pnams.append('{}'.format(BAND_NAME[band]))
            else:
                raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
        elif param[0] == 'N':
            if len(param) in [2,3]:
                band = param[1:]
                pnams.append('Normalized {}'.format(BAND_NAME[band]))
            else:
                raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
        else:
            raise ValueError('Error, param={}'.format(param))
else:
    warnings.simplefilter('ignore')
number_array = []
corcoef_array = []
cr_mean_array = []
cr_std_array = []
factor_array = []
offset_array = []
rmse_array = []
for iband,param in enumerate(args.param):
    data_x_all = src_data[iband].flatten()
    data_y_all = stat_data[iband].flatten()
    data_b_all = cr_data.flatten()
    if data_x_all.shape != data_y_all.shape:
        raise ValueError('Error, data_x_all.shape={}, data_y_all.shape={}'.format(data_x_all.shape,data_y_all.shape))
    number = []
    corcoef = []
    cr_mean = []
    cr_std = []
    factor = []
    offset = []
    rmse = []
    for iobj,object_id in enumerate(object_ids):
        if args.debug and (iobj%fig_interval == 0):
            fig_flag = True
        else:
            fig_flag = False
        indx = nearest_inds[iobj]
        cnd = (~np.isnan(data_x_all[indx])) & (~np.isnan(data_y_all[indx]))
        data_x = (data_x_all[indx])[cnd]
        data_y = (data_y_all[indx])[cnd]
        data_b = (data_b_all[indx])[cnd]
        if data_x.size < 3:
            xs = np.array([])
            ys = np.array([])
            result = [np.nan,np.nan]
            calc_y = np.array([])
            r_value = np.nan
            cr_value = np.nan
            cr_error = np.nan
            rms_value = np.nan
        else:
            xs = []
            ys = []
            v1 = np.min(data_y)-EPSILON
            v2 = np.max(data_y)+EPSILON
            vstp = (v2-v1)/args.nstp
            for v in np.arange(v1+0.5*vstp,v2,vstp):
                cnd1 = (data_y >= v-0.5*vstp) & (data_y < v+0.5*vstp)
                xcnd1 = data_x[cnd1]
                ncnd1 = xcnd1.size
                if ncnd1 > 2:
                    xm = np.mean(xcnd1)
                    xe = np.sqrt(np.square(xcnd1-xm).sum()/ncnd1)
                    cnd2 = np.abs(xcnd1-xm) < xe*args.ethr
                    xcnd2 = xcnd1[cnd2]
                    ncnd2 = xcnd2.size
                    if (ncnd2 != ncnd1) and (ncnd2 > 0):
                        xm = np.mean(xcnd2)
                        xe = np.sqrt(np.square(xcnd2-xm).sum()/ncnd2)
                        cnd3 = np.abs(xcnd2-xm) < xe*args.ethr
                        xcnd3 = xcnd2[cnd3]
                        ncnd3 = xcnd3.size
                        if (ncnd3 != ncnd2) and (ncnd3 > 0):
                            ycnd1 = data_y[cnd1]
                            ycnd2 = ycnd1[cnd2]
                            ycnd3 = ycnd2[cnd3]
                            xm = np.mean(xcnd3)
                            ym = np.mean(ycnd3)
                            xs.append(xm)
                            ys.append(ym)
                        else:
                            ycnd1 = data_y[cnd1]
                            ycnd2 = ycnd1[cnd2]
                            ym = np.mean(ycnd2)
                            xs.append(xm)
                            ys.append(ym)
                    else:
                        ycnd1 = data_y[cnd1]
                        ym = np.mean(ycnd1)
                        xs.append(xm)
                        ys.append(ym)
            xs = np.array(xs)
            ys = np.array(ys)
            if xs.size < 2:
                result = [np.nan,np.nan]
                calc_y = np.array([])
                r_value = np.nan
                cr_value = np.nan
                cr_error = np.nan
                rms_value = np.nan
            else:
                result = np.polyfit(xs,ys,1)
                calc_y = data_x*result[0]+result[1]
                r_value = np.corrcoef(data_x,data_y)[0,1]
                cr_value = np.nanmean(data_b)
                cr_error = np.nanstd(data_b)
                rms_value = np.sqrt(np.square(calc_y-data_y).sum()/calc_y.size)
        number.append(calc_y.size)
        corcoef.append(r_value)
        cr_mean.append(cr_value)
        cr_std.append(cr_error)
        factor.append(result[0])
        offset.append(result[1])
        rmse.append(rms_value)
        if fig_flag:
            fig.clear()
            ax1 = plt.subplot(111,aspect='equal')
            ax1.minorticks_on()
            line = 'number: {}\n'.format(calc_y.size)
            line += 'coeff: {:7.4f}\n'.format(r_value)
            line += 'cr_band: {:6.4f}\n'.format(cr_value)
            line += 'factor: {:5.4f}\n'.format(result[0])
            line += 'offset: {:5.4f}\n'.format(result[1])
            line += 'rmse: {:5.4f}'.format(rms_value)
            at= AnchoredText(line,prop=dict(size=12),loc=2,pad=0.1,borderpad=0.8,frameon=True)
            at.patch.set_boxstyle('round')
            ax1.add_artist(at)
            ax1.plot(data_x,data_y,'b.')
            ax1.plot(xs,ys,'ro')
            ax1.plot(xfit,np.polyval(result,xfit),'k:')
            if args.ax1_xmin is None or args.ax1_ymin is None:
                if calc_y.size < 1:
                    xmin = -1.0
                    ymin = -1.0
                else:
                    xmin = np.min(data_x)
                    ymin = np.min(data_y)
            if args.ax1_xmax is None or args.ax1_ymax is None:
                if calc_y.size < 1:
                    xmax = 1.0
                    ymax = 1.0
                else:
                    xmax = np.max(data_x)
                    ymax = np.max(data_y)
            if args.ax1_xmin is not None and args.ax1_xmax is not None:
                ax1.set_xlim(args.ax1_xmin[iband],args.ax1_xmax[iband])
            elif args.ax1_xmin is not None:
                ax1.set_xlim(args.ax1_xmin[iband],max(xmax,ymax))
            elif args.ax1_xmax is not None:
                ax1.set_xlim(min(xmin,ymin),args.ax1_xmax[iband])
            else:
                ax1.set_xlim(min(xmin,ymin),max(xmax,ymax))
            if args.ax1_ymin is not None and args.ax1_ymax is not None:
                ax1.set_ylim(args.ax1_ymin[iband],args.ax1_ymax[iband])
            elif args.ax1_ymin is not None:
                ax1.set_ylim(args.ax1_ymin[iband],max(xmax,ymax))
            elif args.ax1_ymax is not None:
                ax1.set_ylim(min(xmin,ymin),args.ax1_ymax[iband])
            else:
                ax1.set_ylim(min(xmin,ymin),max(xmax,ymax))
            ax1.set_xlabel(pnams[iband]+' (target)')
            ax1.set_ylabel(pnams[iband]+' (clean-day)')
            ax1.xaxis.set_tick_params(pad=7)
            ax1.xaxis.set_label_coords(0.5,-0.14)
            ax1.yaxis.set_label_coords(-0.14,0.5)
            if args.ax1_title is not None:
                ax1.set_title('{} (OBJECTID={})'.format(args.ax1_title,object_id))
            else:
                ax1.set_title('{} (OBJECTID={})'.format(bnam,object_id))
            plt.savefig(pdf,format='pdf')
            if not args.batch:
                plt.draw()
                plt.pause(0.1)
            #break
    number_array.append(number)
    corcoef_array.append(corcoef)
    cr_mean_array.append(cr_mean)
    cr_std_array.append(cr_std)
    factor_array.append(factor)
    offset_array.append(offset)
    rmse_array.append(rmse)
if args.debug:
    pdf.close()
number_array = np.array(number_array)
corcoef_array = np.array(corcoef_array)
cr_mean_array = np.array(cr_mean_array)
cr_std_array = np.array(cr_std_array)
factor_array = np.array(factor_array)
offset_array = np.array(offset_array)
rmse_array = np.array(rmse_array)

# Output file
np.savez(args.out_fnam,
params=args.param,
object_ids=object_ids,
number=number_array,
corcoef=corcoef_array,
cr_mean=cr_mean_array,
cr_std=cr_std_array,
factor=factor_array,
offset=offset_array,
rmse=rmse_array)
