#!/usr/bin/env python
import os
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
import numpy as np
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
BAND_NAME = {'Sb':'Blue','Sg':'Green','Sr':'Red','Se1':'RedEdge1','Se2':'RedEdge2','Se3':'RedEdge3','Sn1':'NIR1','Sn2':'NIR2','Ss1':'SWIR1','Ss2':'SWIR2',
             'Nb':'Normalized Blue','Ng':'Normalized Green','Nr':'Normalized Red','Ne1':'Normalized RedEdge1','Ne2':'Normalized RedEdge2','Ne3':'Normalized RedEdge3',
             'Nn1':'Normalized NIR1','Nn2':'Normalized NIR2','Ns1':'Normalized SWIR1','Ns2':'Normalized SWIR2',
             'NDVI':'NDVI','GNDVI':'GNDVI','RGI':'RGI','NRGI':'NRGI'}

# Default values
PARAM = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2','NDVI','GNDVI','RGI','NRGI']
NORM_BAND = ['b','g','r','e1','e2','e3','n1']
RGI_RED_BAND = 'e1'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('-M','--mask_fnam',default=None,help='Mask GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-N','--norm_band',default=None,action='append',help='Wavelength band for normalization ({})'.format(NORM_BAND))
parser.add_argument('-r','--rgi_red_band',default=RGI_RED_BAND,help='Wavelength band for RGI (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('-D','--fig_dpi',default=None,type=int,help='DPI of figure for debug (%(default)s)')
parser.add_argument('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.param is None:
    args.param = PARAM
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if args.norm_band is None:
    args.norm_band = NORM_BAND
for band in args.norm_band:
    if not band in S2_BAND:
        raise ValueError('Error, unknown band for normalization >>> {}'.format(band))
if not args.rgi_red_band in S2_BAND:
    raise ValueError('Error, unknown band for RGI >>> {}'.format(args.rgi_red_band))
inp_band = []
for param in args.param:
    if param == 'NDVI':
        for band in ['r','n1']:
            if not band in inp_band:
                inp_band.append(band)
    elif param == 'GNDVI':
        for band in ['g','n1']:
            if not band in inp_band:
                inp_band.append(band)
    elif param in ['RGI','NRGI']:
        for band in ['g',args.rgi_red_band]:
            if not band in inp_band:
                inp_band.append(band)
    elif param[0] in ['S','N']:
        if len(param) in [2,3]:
            band = param[1:]
            if not band in inp_band:
                inp_band.append(band)
        else:
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    else:
        raise ValueError('Error, param={}'.format(param))
for band in args.norm_band:
    if not band in inp_band:
        inp_band.append(band)
inp_band = np.array(inp_band)
indx = np.argsort([S2_PARAM.index(band) for band in inp_band])
inp_band = inp_band[indx]
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
if args.src_geotiff is None:
    raise ValueError('Error, src_geotiff is not specified.')
elif args.dst_geotiff is None or args.fignam is None:
    bnam,enam = os.path.splitext(args.src_geotiff)
    if args.dst_geotiff is None:
        args.dst_geotiff = bnam+'_indices'+enam
    if args.fignam is None:
        args.fignam = bnam+'_indices.pdf'

# Read Source GeoTIFF
ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = len(inp_band)
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
src_band = [S2_BAND[band] for band in inp_band]
src_indx = {}
for band in inp_band:
    src_indx[band] = src_band.index(S2_BAND[band])
tmp_nb = ds.RasterCount
tmp_band = []
for iband in range(tmp_nb):
    band = ds.GetRasterBand(iband+1)
    tmp_band.append(band.GetDescription())
src_data = []
for band in inp_band:
    iband = tmp_band.index(S2_BAND[band])
    band = ds.GetRasterBand(iband+1)
    src_data.append(band.ReadAsArray())
src_data = np.array(src_data)*1.0e-4 # NBAND,NY,NX
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
    src_data[:,mask_data < 0.5] = np.nan

# Calculate indices
dst_nx = src_nx
dst_ny = src_ny
dst_nb = len(args.param)
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
dst_meta['norm_band'] = ','.join(args.norm_band)
dst_meta['rgi_red_band'] = args.rgi_red_band
dst_dtype = gdal.GDT_Float32
dst_nodata = np.nan
dst_band = args.param
dst_data = np.full((dst_nb,dst_ny,dst_nx),np.nan)
norm = 0.0
for band in args.norm_band:
    norm += src_data[src_indx[band]]
norm = len(args.norm_band)/norm
for iband,param in enumerate(args.param):
    if param == 'NDVI':
        red = src_data[src_indx['r']]
        nir = src_data[src_indx['n1']]
        dst_data[iband] = ((nir-red)/(nir+red))
    elif param == 'GNDVI':
        green = src_data[src_indx['g']]
        nir = src_data[src_indx['n1']]
        dst_data[iband] = ((nir-green)/(nir+green))
    elif param == 'RGI':
        green = src_data[src_indx['g']]
        red = src_data[src_indx[args.rgi_red_band]]
        dst_data[iband] = (green*red)
    elif param == 'NRGI':
        green = src_data[src_indx['g']]
        red = src_data[src_indx[args.rgi_red_band]]
        dst_data[iband] = (green*norm*red*norm)
    elif param[0] == 'S':
        if len(param) in [2,3]:
            band = param[1:]
            dst_data[iband] = src_data[src_indx[band]]
        else:
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    elif param[0] == 'N':
        if len(param) in [2,3]:
            band = param[1:]
            dst_data[iband] = src_data[src_indx[band]]*norm
        else:
            raise ValueError('Error, len(param)={} >>> {}'.format(len(param),param))
    else:
        raise ValueError('Error, param={}'.format(param))

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
    for iband,param in enumerate(args.param):
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.fig_dpi is None:
            if args.ax1_zmin is not None and args.ax1_zmax is not None and not np.isnan(ax1_zmin[param]) and not np.isnan(ax1_zmax[param]):
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],vmax=ax1_zmax[param],cmap=cm.jet,interpolation='none')
            elif args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],cmap=cm.jet,interpolation='none')
            elif args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=ax1_zmax[param],cmap=cm.jet,interpolation='none')
            else:
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
        else:
            if args.ax1_zmin is not None and args.ax1_zmax is not None and not np.isnan(ax1_zmin[param]) and not np.isnan(ax1_zmax[param]):
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],vmax=ax1_zmax[param],cmap=cm.jet)
            elif args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],cmap=cm.jet)
            elif args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=ax1_zmax[param],cmap=cm.jet)
            else:
                im = ax1.imshow(dst_data[iband],extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet)
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if args.ax1_zstp is not None and not np.isnan(ax1_zstp[param]):
            if args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
                zmin = (np.floor(ax1_zmin[param]/ax1_zstp[param])-1.0)*ax1_zstp[param]
            else:
                zmin = (np.floor(np.nanmin(dst_data[iband])/ax1_zstp[param])-1.0)*ax1_zstp[param]
            if args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
                zmax = ax1_zmax[param]+0.1*ax1_zstp[param]
            else:
                zmax = np.nanmax(dst_data[iband])+0.1*ax1_zstp[param]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,ax1_zstp[param])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel('{}'.format(BAND_NAME[param]))
        ax2.yaxis.set_label_coords(4.5,0.5)
        if args.remove_nan:
            src_indy,src_indx = np.indices(src_shape)
            src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
            src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
            cnd = ~np.isnan(dst_data[iband])
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
