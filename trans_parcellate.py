#!/usr/bin/env python
import os
import re
import shutil
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
import shapefile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_pdf import PdfPages
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
PARAMS = ['trans_d','trans_s','trans_n','bsc_min','post_avg','post_min','post_max','risetime',
'p1_2','p2_2','p3_2','p4_2','p5_2','p6_2','p7_2','p8_2']

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-M','--mask_geotiff',default=None,help='Mask GeoTIFF name (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-o','--out_shp',default=None,help='Output Shapefile name (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-n','--remove_nan',default=False,action='store_true',help='Remove nan for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.ax1_zmin is not None:
    while len(args.ax1_zmin) < len(PARAMS):
        args.ax1_zmin.append(args.ax1_zmin[-1])
    ax1_zmin = {}
    for i,param in enumerate(PARAMS):
        ax1_zmin[param] = args.ax1_zmin[i]
if args.ax1_zmax is not None:
    while len(args.ax1_zmax) < len(PARAMS):
        args.ax1_zmax.append(args.ax1_zmax[-1])
    ax1_zmax = {}
    for i,param in enumerate(PARAMS):
        ax1_zmax[param] = args.ax1_zmax[i]
if args.ax1_zstp is not None:
    while len(args.ax1_zstp) < len(PARAMS):
        args.ax1_zstp.append(args.ax1_zstp[-1])
    ax1_zstp = {}
    for i,param in enumerate(PARAMS):
        ax1_zstp[param] = args.ax1_zstp[i]
if args.out_csv is None or args.out_shp is None or args.fignam is None:
    bnam,enam = os.path.splitext(args.src_geotiff)
    if args.out_csv is None:
        args.out_csv = bnam+'_parcel.csv'
    if args.out_shp is None:
        args.out_shp = bnam+'_parcel.shp'
    if args.fignam is None:
        args.fignam = bnam+'_parcel.pdf'

# Read Source GeoTIFF
ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
ngrd = src_nx*src_ny
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
if src_trans[2] != 0.0 or src_trans[4] != 0.0:
    raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().astype(np.float64).reshape(src_nb,ngrd)
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
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
ds = gdal.Open(args.mask_geotiff)
mask_nx = ds.RasterXSize
mask_ny = ds.RasterYSize
mask_nb = ds.RasterCount
if mask_nb != 1:
    raise ValueError('Error, mask_nb={} >>> {}'.format(mask_nb,args.mask_geotiff))
mask_shape = (mask_ny,mask_nx)
if mask_shape != src_shape:
    raise ValueError('Error, mask_shape={}, src_shape={} >>> {}'.format(mask_shape,src_shape,args.mask_geotiff))
mask_data = ds.ReadAsArray().reshape(ngrd)
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

# Get OBJECTID
object_ids = np.unique(mask_data[mask_data != mask_nodata])
ndat = object_ids.size
object_inds = []
indp = np.arange(ngrd)
for object_id in object_ids:
    cnd = (mask_data == object_id)
    object_inds.append(indp[cnd])
object_inds = np.array(object_inds,dtype='object')
out_data = np.full((ndat,src_nb),np.nan)

# Read Shapefile
r = shapefile.Reader(args.shp_fnam)
nobject = len(r)

# Calculate weighted mean values
for iband,param in enumerate(PARAMS):
    data = src_data[iband]
    out_data[:,iband] = [np.nanmean(data[inds]) for inds in object_inds]

if args.use_index:
    all_ids = np.arange(nobject)+1
    if np.array_equal(object_ids,all_ids):
        all_data = out_data
    else:
        if (object_ids[0] < 1) or (object_ids[-1] > nobject):
            raise ValueError('Error, object_ids[0]={}, object_ids[-1]={}, nobject={} >>> {}'.format(object_ids[0],object_ids[-1],nobject,args.mask_geotiff))
        indx = object_ids-1
        all_data = np.full((nobject,src_nb),np.nan)
        all_data[indx] = out_data
else:
    all_ids = []
    for rec in r.iterRecords():
        all_ids.append(rec.OBJECTID)
    if np.array_equal(object_ids,np.array(all_ids)):
        all_data = out_data
    else:
        try:
            indx = np.array([all_ids.index(object_id) for object_id in object_ids])
        except Exception:
            raise ValueError('Error in finding OBJECTID in {}'.format(args.shp_fnam))
        all_data = np.full((nobject,src_nb),np.nan)
        all_data[indx] = out_data

if args.debug:
    dst_nx = src_nx
    dst_ny = src_ny
    dst_nb = len(PARAMS)
    dst_shape = (dst_ny,dst_nx)
    dst_data = np.full((dst_nb,ngrd),np.nan)
    dst_band = PARAMS
    for i,inds in enumerate(object_inds):
        dst_data[:,inds] = out_data[i,:].reshape(-1,1)
    dst_data = dst_data.reshape((dst_nb,dst_ny,dst_nx))

# Output CSV
with open(args.out_csv,'w') as fp:
    fp.write('{:>8s}'.format('OBJECTID'))
    for param in PARAMS:
        fp.write(', {:>13s}'.format(param))
    fp.write('\n')
    for iobj,object_id in enumerate(all_ids):
        fp.write('{:8d}'.format(object_id))
        for iband,param in enumerate(PARAMS):
            fp.write(', {:>13.6e}'.format(all_data[iobj,iband]))
        fp.write('\n')

# Output Shapefile
w = shapefile.Writer(args.out_shp)
w.shapeType = shapefile.POLYGON
w.fields = r.fields[1:] # skip first deletion field
for param in PARAMS:
    w.field(param,'F',13,6)
for iobj,shaperec in enumerate(r.iterShapeRecords()):
    rec = shaperec.record
    shp = shaperec.shape
    rec.extend(list(all_data[iobj]))
    w.shape(shp)
    w.record(*rec)
w.close()
shutil.copy2(os.path.splitext(args.shp_fnam)[0]+'.prj',os.path.splitext(args.out_shp)[0]+'.prj')

# For debug
if args.debug:
    if args.shp_fnam is not None:
        r = shapefile.Reader(args.out_shp)
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.80)
    pdf = PdfPages(args.fignam)
    for iband,param in enumerate(PARAMS):
        data = dst_data[iband]
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.shp_fnam is not None:
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
                z = getattr(rec,param)
                if not np.isnan(z):
                    ax1.add_patch(plt.Polygon(shp.points,edgecolor='none',facecolor=cm.jet((z-zmin)/zdif),linewidth=0.02))
            im = ax1.imshow(np.arange(4).reshape(2,2),extent=(-2,-1,-2,-1),vmin=zmin,vmax=zmax,cmap=cm.jet)
        else:
            if args.ax1_zmin is not None and args.ax1_zmax is not None and not np.isnan(ax1_zmin[param]) and not np.isnan(ax1_zmax[param]):
                im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],vmax=ax1_zmax[param],cmap=cm.jet,interpolation='none')
            elif args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
                im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmin=ax1_zmin[param],cmap=cm.jet,interpolation='none')
            elif args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
                im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),vmax=ax1_zmax[param],cmap=cm.jet,interpolation='none')
            else:
                im = ax1.imshow(data,extent=(src_xmin,src_xmax,src_ymin,src_ymax),cmap=cm.jet,interpolation='none')
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
        if args.remove_nan:
            src_indy,src_indx = np.indices(src_shape)
            src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
            src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
            cnd = ~np.isnan(data)
            if cnd.sum() < 1:
                fig_xmin = src_xmin
                fig_xmax = src_xmax
                fig_ymin = src_ymin
                fig_ymax = src_ymax
            else:
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
            ax1.set_title(args.ax1_title)
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    pdf.close()
