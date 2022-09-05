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
PARAMS = ['Sb','Sg','Sr','Se1','Se2','Se3','Sn1','Sn2','Ss1','Ss2',
          'Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2',
          'NDVI','GNDVI','RGI','NRGI']
S2_PARAM = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
BAND_NAME = {'b':'Blue','g':'Green','r':'Red','e1':'RedEdge1','e2':'RedEdge2','e3':'RedEdge3','n1':'NIR1','n2':'NIR2','s1':'SWIR1','s2':'SWIR2'}
NORM_BAND = ['b','g','r','e1','e2','e3','n1']

# Default values
PARAM = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','NDVI','GNDVI','NRGI']
CR_BAND = 'r'
VTHR = [
'Sb:0.02','Sg:0.02','Sr:0.02','Se1:0.02','Se2:0.02','Se3:0.02','Sn1:0.02','Sn2:0.02','Ss1:0.02','Ss2:0.02',
'Nb:0.05','Ng:0.05','Nr:0.05','Ne1:0.05','Ne2:0.05','Ne3:0.05','Nn1:0.05','Nn2:0.05','Ns1:0.05','Ns2:0.05',
'NDVI:0.1','GNDVI:0.1','RGI:0.1','NRGI:0.1']
RTHR = 1.0
MTHR = 2.0
CTHR = 0.35
INDS_FNAM = 'nearest_inds.npy'
NFIG = 1000

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-C','--cr_band',default=CR_BAND,help='Wavelength band for cloud removal (%(default)s)')
parser.add_argument('-c','--cthr',default=CTHR,type=float,help='Threshold for cloud removal (%(default)s)')
parser.add_argument('-v','--vthr',default=None,type=float,help='Absolute threshold to remove outliers ({})'.format(VTHR))
parser.add_argument('-R','--rthr',default=RTHR,type=float,help='Relative threshold for 2-step outlier removal (%(default)s)')
parser.add_argument('--mthr',default=MTHR,type=float,help='Multiplying factor of vthr for 2-step outlier removal (%(default)s)')
parser.add_argument('-x','--ax1_xmin',default=None,type=float,action='append',help='Axis1 X min for debug (%(default)s)')
parser.add_argument('-X','--ax1_xmax',default=None,type=float,action='append',help='Axis1 X max for debug (%(default)s)')
parser.add_argument('-y','--ax1_ymin',default=None,type=float,action='append',help='Axis1 Y min for debug (%(default)s)')
parser.add_argument('-Y','--ax1_ymax',default=None,type=float,action='append',help='Axis1 Y max for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--mask_fnam',default=None,help='Mask file name (%(default)s)')
parser.add_argument('--stat_fnam',default=None,help='Statistic file name (%(default)s)')
parser.add_argument('--inds_fnam',default=INDS_FNAM,help='Index file name (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('--nfig',default=NFIG,type=int,help='Max number of figure for debug (%(default)s)')
parser.add_argument('-o','--out_fnam',default=None,help='Output NPZ name (%(default)s)')
parser.add_argument('--outlier_remove2',default=False,action='store_true',help='2-step outlier removal mode (%(default)s)')
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
if args.vthr is None:
    args.vthr = VTHR
vthr = {}
for s in args.vthr:
    m = re.search('\s*(\S+)\s*:\s*(\S+)\s*',s)
    if not m:
        raise ValueError('Error, invalid threshold to remove outliers >>> {}'.format(s))
    param = m.group(1)
    value = float(m.group(2))
    if not param in PARAMS:
        raise ValueError('Error, unknown objective variable for vthr ({}) >>> {}'.format(param,s))
    if not np.isnan(value):
        vthr[param] = value
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
src_nb = ds.RasterCount
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_data = ds.ReadAsArray() # NBAND,NY,NX
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
src_meta = ds.GetMetadata()
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp
ds = None
if src_nodata is not None and not np.isnan(src_nodata):
    src_data[src_data == src_nodata] = np.nan
param = 'S'+args.cr_band
if not param in src_band:
    raise ValueError('Error in finding {} >>> {}'.format(param,args.src_geotiff))
cr_data = src_data[src_band.index(param)].copy() # NY,NX
if not 'norm_band' in src_meta:
    sys.stderr.write('Warning, failed in finding {} in metadata >>> {}\n'.format('norm_band',args.src_geotiff))
    sys.stderr.flush()
    norm_band = NORM_BAND
else:
    norm_band = [s.strip() for s in src_meta['norm_band'].split(',')]
all_data = []
for param in args.param:
    iband = src_band.index(param)
    all_data.append(src_data[iband])
all_data = np.array(all_data)

cnd = (np.isnan(cr_data)) | (cr_data > args.cthr)
all_data[:,cnd] = np.nan

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
    all_data[:,cnd] = np.nan

# Read Statistic GeoTIFF
ds = gdal.Open(args.stat_fnam)
stat_nx = ds.RasterXSize
stat_ny = ds.RasterYSize
stat_nb = ds.RasterCount
stat_shape = (stat_ny,stat_nx)
if stat_shape != src_shape:
    raise ValueError('Error, stat_shape={}, src_shape={} >>> {}'.format(stat_shape,src_shape,args.stat_fnam))
stat_band = []
for iband in range(stat_nb):
    band = ds.GetRasterBand(iband+1)
    stat_band.append(band.GetDescription())
stat_data = ds.ReadAsArray().reshape(stat_nb,stat_ny,stat_nx)
ds = None
for param in args.param:
    if not param in stat_band:
        raise ValueError('Error in finding {} >>> {}'.format(param,args.stat_fnam))

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
    data_x_all = all_data[iband].flatten()
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
        data_x = data_x_all[indx]
        data_y = data_y_all[indx]
        data_b = data_b_all[indx]
        if args.outlier_remove2:
            cnd1 = (~np.isnan(data_x)) & (np.abs(data_x-data_y) < (np.abs(data_y)*args.rthr).clip(min=vthr[param]*args.mthr))
        else:
            cnd1 = ~np.isnan(data_x)
        xcnd = data_x[cnd1]
        ycnd = data_y[cnd1]
        bcnd = data_b[cnd1]
        if xcnd.size < 2:
            result = [np.nan,np.nan]
            calc_y = np.array([])
            r_value = np.nan
            cr_value = np.nan
            cr_error = np.nan
            rms_value = np.nan
            flag = False
        else:
            result = np.polyfit(xcnd,ycnd,1)
            calc_y = xcnd*result[0]+result[1]
            cnd2 = np.abs(calc_y-ycnd) < vthr[param]
            xcnd2 = xcnd[cnd2]
            ycnd2 = ycnd[cnd2]
            bcnd2 = bcnd[cnd2]
            if (xcnd2.size == cnd2.size) or (xcnd2.size < 2):
                r_value = np.corrcoef(xcnd,ycnd)[0,1]
                cr_value = np.nanmean(bcnd)
                cr_error = np.nanstd(bcnd)
                rms_value = np.sqrt(np.square(calc_y-ycnd).sum()/calc_y.size)
                flag = False
            else:
                result = np.polyfit(xcnd2,ycnd2,1)
                calc_y = xcnd2*result[0]+result[1]
                r_value = np.corrcoef(xcnd2,ycnd2)[0,1]
                cr_value = np.nanmean(bcnd2)
                cr_error = np.nanstd(bcnd2)
                rms_value = np.sqrt(np.square(calc_y-ycnd2).sum()/calc_y.size)
                flag = True
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
            if xcnd.size != cnd1.size:
                ax1.plot(data_x,data_y,'k.')
            if flag:
                ax1.plot(xcnd,ycnd,'.',color='#888888')
                ax1.plot(xcnd2,ycnd2,'b.')
            else:
                ax1.plot(xcnd,ycnd,'b.')
            ax1.plot(xfit,np.polyval(result,xfit),'k:')
            if args.ax1_xmin is None or args.ax1_ymin is None:
                if flag:
                    xmin = min(np.nanmin(xcnd),np.nanmin(xcnd2))
                    ymin = min(np.nanmin(ycnd),np.nanmin(ycnd2))
                else:
                    xmin = np.nanmin(xcnd)
                    ymin = np.nanmin(ycnd)
            if args.ax1_xmax is None or args.ax1_ymax is None:
                if flag:
                    xmax = max(np.nanmax(xcnd),np.nanmax(xcnd2))
                    ymax = max(np.nanmax(ycnd),np.nanmax(ycnd2))
                else:
                    xmax = np.nanmax(xcnd)
                    ymax = np.nanmax(ycnd)
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
np.savez(args.out_fnam,params=args.param,number=number_array,corcoef=corcoef_array,cr_mean=cr_mean_array,cr_std=cr_std_array,
         factor=factor_array,offset=offset_array,rmse=rmse_array)
