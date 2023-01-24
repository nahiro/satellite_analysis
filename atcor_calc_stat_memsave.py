#!/usr/bin/env python
import os
import sys
import re
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
from datetime import datetime
import numpy as np
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
PARAMS = ['Sb','Sg','Sr','Se1','Se2','Se3','Sn1','Sn2','Ss1','Ss2',
          'Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2',
          'NDVI','GNDVI','RGI','NRGI']
S2_PARAM = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
S2_BAND = {'b':'B2','g':'B3','r':'B4','e1':'B5','e2':'B6','e3':'B7','n1':'B8','n2':'B8A','s1':'B11','s2':'B12'}
BAND_NAME = {'b':'Blue','g':'Green','r':'Red','e1':'RedEdge1','e2':'RedEdge2','e3':'RedEdge3','n1':'NIR1','n2':'NIR2','s1':'SWIR1','s2':'SWIR2'}

# Default values
PARAM = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','NDVI','GNDVI','NRGI']
CLN_BAND = 'r'
CTHR_AVG = 0.06
CTHR_STD = 0.05
CTHR_DIF = 1.0
CLN_NMIN = 4

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-C','--cln_band',default=CLN_BAND,help='Wavelength band for clean-day select (%(default)s)')
parser.add_argument('--mask_fnam',default=None,help='Mask file name (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--cthr_avg',default=CTHR_AVG,type=float,help='Threshold of mean for clean-day select (%(default)s)')
parser.add_argument('--cthr_std',default=CTHR_STD,type=float,help='Threshold of std for clean-day select (%(default)s)')
parser.add_argument('--cthr_dif',default=CTHR_DIF,type=float,help='Threshold of deviation in sigma for clean-day select (%(default)s)')
parser.add_argument('-n','--cln_nmin',default=CLN_NMIN,type=int,help='Minimum clean-day number (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('-D','--fig_dpi',default=None,type=int,help='DPI of figure for debug (%(default)s)')
parser.add_argument('--remove_nan',default=False,action='store_true',help='Remove nan for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.param is None:
    args.param = PARAM
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if not args.cln_band in S2_PARAM:
    raise ValueError('Error, unknown band for clean-day select >>> {}'.format(args.cln_band))
if args.ax1_zmin is not None:
    while len(args.ax1_zmin) < len(args.param):
        args.ax1_zmin.append(args.ax1_zmin[-1])
if args.ax1_zmax is not None:
    while len(args.ax1_zmax) < len(args.param):
        args.ax1_zmax.append(args.ax1_zmax[-1])
if args.ax1_zstp is not None:
    while len(args.ax1_zstp) < len(args.param):
        args.ax1_zstp.append(args.ax1_zstp[-1])
d1 = datetime.strptime(args.data_tmin,'%Y%m%d')
d2 = datetime.strptime(args.data_tmax,'%Y%m%d')
data_years = np.arange(d1.year,d2.year+1,1)

# Read Source GeoTIFF
src_nx = None
src_ny = None
src_shape = None
src_prj = None
src_trans = None
cln_data = [] # Clean-day Selection Data
fnams = []
for year in data_years:
    ystr = '{}'.format(year)
    dnam = os.path.join(args.inpdir,ystr)
    if not os.path.isdir(dnam):
        continue
    for f in sorted(os.listdir(dnam)):
        m = re.search('^('+'\d'*8+')_indices\.tif$',f)
        if not m:
            continue
        dstr = m.group(1)
        d = datetime.strptime(dstr,'%Y%m%d')
        if d < d1 or d > d2:
            continue
        fnam = os.path.join(dnam,f)
        ds = gdal.Open(fnam)
        tmp_nx = ds.RasterXSize
        tmp_ny = ds.RasterYSize
        tmp_nb = ds.RasterCount
        tmp_shape = (tmp_ny,tmp_nx)
        tmp_prj = ds.GetProjection()
        tmp_trans = ds.GetGeoTransform()
        tmp_data = ds.ReadAsArray().reshape(tmp_nb,tmp_ny,tmp_nx)
        tmp_band = []
        for iband in range(tmp_nb):
            band = ds.GetRasterBand(iband+1)
            tmp_band.append(band.GetDescription())
        if src_shape is None:
            src_nx = tmp_nx
            src_ny = tmp_ny
            src_shape = tmp_shape
        elif tmp_shape != src_shape:
            raise ValueError('Error, tmp_shape={}, src_shape={}'.format(tmp_shape,src_shape))
        if src_prj is None:
            src_prj = tmp_prj
        elif tmp_prj != src_prj:
            raise ValueError('Error, tmp_prj={}, src_prj={}'.format(tmp_prj,src_prj))
        if src_trans is None:
            src_trans = tmp_trans
        elif tmp_trans != src_trans:
            raise ValueError('Error, tmp_trans={}, src_trans={}'.format(tmp_trans,src_trans))
        band = 'S'+args.cln_band
        if not band in tmp_band:
            raise ValueError('Error in finding {} >>> {}'.format(band,fnam))
        cln_indx = tmp_band.index(band)
        cln_data.append(tmp_data[cln_indx])
        fnams.append(fnam)
if len(cln_data) < 1:
    raise IOError('No indices data for process.')
cln_data = np.array(cln_data) # NTIM,NY,NX
fnams = np.array(fnams)
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp

# Read Mask GeoTIFF
ds = gdal.Open(args.mask_fnam)
mask_nx = ds.RasterXSize
mask_ny = ds.RasterYSize
mask_nb = ds.RasterCount
if mask_nb != 1:
    raise ValueError('Error, mask_nb={} >>> {}'.format(mask_nb,args.mask_fnam))
mask_shape = (mask_ny,mask_nx)
if mask_shape != src_shape:
    raise ValueError('Error, mask_shape={}, src_shape={} >>> {}'.format(mask_shape,src_shape,args.mask_fnam))
mask_data = ds.ReadAsArray()
band = ds.GetRasterBand(1)
mask_dtype = band.DataType
mask_nodata = band.GetNoDataValue()
if mask_dtype in [gdal.GDT_Int16,gdal.GDT_Int32]:
    if mask_nodata < 0.0:
        mask_nodata = -int(abs(mask_nodata)+0.5)
    else:
        mask_nodata = int(mask_nodata+0.5)
elif mask_dtype in [gdal.GDT_UInt16,gdal.GDT_UInt32]:
    mask_nodata = int(mask_nodata+0.5)
ds = None

# Select clean-day images
cnd = (mask_data > 0.5) # inside study area
cnd_data = cln_data[:,cnd]
cln_avg = np.nanmean(cnd_data,axis=1)
cln_std = np.nanstd(cnd_data,axis=1)
cnd = (cln_avg < args.cthr_avg) & (cln_std < args.cthr_std)
ncnd = cnd.sum()
if ncnd < args.cln_nmin:
    raise ValueError('Error, not enough clean-day found >>> {}'.format(ncnd))
cln_data = cln_data[cnd] # NTIM,NY,NX
fnams = fnams[cnd]
indx_all = np.arange(ncnd)

# Read clean-day images
src_nb = len(args.param)
src_band = args.param
src_data = []
for fnam in fnams:
    ds = gdal.Open(fnam)
    tmp_nx = ds.RasterXSize
    tmp_ny = ds.RasterYSize
    tmp_nb = ds.RasterCount
    tmp_shape = (tmp_ny,tmp_nx)
    tmp_prj = ds.GetProjection()
    tmp_trans = ds.GetGeoTransform()
    tmp_data = ds.ReadAsArray().reshape(tmp_nb,tmp_ny,tmp_nx)
    tmp_band = []
    for iband in range(tmp_nb):
        band = ds.GetRasterBand(iband+1)
        tmp_band.append(band.GetDescription())
    if tmp_shape != src_shape:
        raise ValueError('Error, tmp_shape={}, src_shape={}'.format(tmp_shape,src_shape))
    if tmp_prj != src_prj:
        raise ValueError('Error, tmp_prj={}, src_prj={}'.format(tmp_prj,src_prj))
    if tmp_trans != src_trans:
        raise ValueError('Error, tmp_trans={}, src_trans={}'.format(tmp_trans,src_trans))
    tmp_indx = []
    for band in src_band:
        if not band in tmp_band:
            raise ValueError('Error in finding {} >>> {}'.format(band,fnam))
        tmp_indx.append(tmp_band.index(band))
    src_data.append(tmp_data[tmp_indx])
if len(src_data) < 1:
    raise IOError('No indices data for process.')
src_data = np.array(src_data) # NTIM,NBAND,NY,NX

# Calculate stats for clean-day pixels
dst_nx = src_nx
dst_ny = src_ny
dst_nb = src_nb
dst_prj = src_prj
dst_trans = src_trans
dst_band = src_band
dst_data = np.full((dst_nb,dst_ny,dst_nx),np.nan)
dst_dtype = gdal.GDT_Float32
dst_nodata = np.nan
dst_meta = {}
dst_meta['data_tmin'] = '{:%Y%m%d}'.format(d1)
dst_meta['data_tmax'] = '{:%Y%m%d}'.format(d2)
for iy in range(src_ny):
    for ix in range(src_nx):
        src_data_tmp = src_data[:,:,iy,ix]
        cln_data_tmp = cln_data[:,iy,ix]
        indx = indx_all[np.isfinite(cln_data_tmp)]
        vc = cln_data_tmp[indx].copy()
        vm = vc.mean()
        ve = vc.std()
        cnd = (vc < vm+ve*args.cthr_dif)
        ncnd = cnd.sum()
        if (ncnd != vc.size) and (ncnd >= args.cln_nmin):
            indx = indx[cnd]
            vc = cln_data_tmp[indx].copy()
            vm = vc.mean()
            ve = vc.std()
            cnd = (vc < vm+ve*args.cthr_dif)
            ncnd = cnd.sum()
            if (ncnd != vc.size) and (ncnd >= args.cln_nmin):
                indx = indx[cnd]
                vc = cln_data_tmp[indx].copy()
                vm = vc.mean()
                ve = vc.std()
                cnd = (vc < vm+ve*args.cthr_dif)
                ncnd = cnd.sum()
                if (ncnd != vc.size) and (ncnd >= args.cln_nmin):
                    indx = indx[cnd]
        dst_data[:,iy,ix] = np.nanmean(src_data_tmp[indx],axis=0)

# Write Destination GeoTIFF
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.dst_geotiff,dst_nx,dst_ny,dst_nb,dst_dtype)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
for iband in range(dst_nb):
    band = ds.GetRasterBand(iband+1)
    band.WriteArray(dst_data[iband])
    band.SetDescription(dst_band[iband])
band.SetNoDataValue(dst_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset

# For debug
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.85)
    pdf = PdfPages(args.fignam)
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
    for i,param in enumerate(args.param):
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.fig_dpi is None:
            if args.ax1_zmin is not None and args.ax1_zmax is not None:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],vmax=args.ax1_zmax[i],cmap=cm.jet,interpolation='none')
            elif args.ax1_zmin is not None:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],cmap=cm.jet,interpolation='none')
            elif args.ax1_zmax is not None:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=args.ax1_zmax[i],cmap=cm.jet,interpolation='none')
            else:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
        else:
            if args.ax1_zmin is not None and args.ax1_zmax is not None:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],vmax=args.ax1_zmax[i],cmap=cm.jet)
            elif args.ax1_zmin is not None:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=args.ax1_zmin[i],cmap=cm.jet)
            elif args.ax1_zmax is not None:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=args.ax1_zmax[i],cmap=cm.jet)
            else:
                im = ax1.imshow(dst_data[i],extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet)
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if args.ax1_zstp is not None:
            if args.ax1_zmin is not None:
                zmin = (np.floor(args.ax1_zmin[i]/args.ax1_zstp[i])-1.0)*args.ax1_zstp[i]
            else:
                zmin = (np.floor(np.nanmin(dst_data[i])/args.ax1_zstp[i])-1.0)*args.ax1_zstp[i]
            if args.ax1_zmax is not None:
                zmax = args.ax1_zmax[i]+0.1*args.ax1_zstp[i]
            else:
                zmax = np.nanmax(dst_data[i])+0.1*args.ax1_zstp[i]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,args.ax1_zstp[i])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel(pnams[i])
        ax2.yaxis.set_label_coords(3.5,0.5)
        if args.remove_nan:
            src_indy,src_indx = np.indices(src_shape)
            src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
            src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
            cnd = ~np.isnan(dst_data[i])
            xp = src_xp[cnd]
            yp = src_yp[cnd]
            fig_xmin = xp.min()
            fig_xmax = xp.max()
            fig_ymin = yp.min()
            fig_ymax = yp.max()
        else:
            fig_xmin = src_xmin
            fig_xmax = src_xmax
            fig_ymin = src_ymin
            fig_ymax = src_ymax
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        if args.ax1_title is not None:
            ax1.set_title('{}'.format(args.ax1_title))
        if args.fig_dpi is None:
            plt.savefig(pdf,format='pdf')
        else:
            plt.savefig(pdf,dpi=args.fig_dpi,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    pdf.close()
