#!/usr/bin/env python
import os
import sys
import re
try:
    import gdal
except Exception:
    from osgeo import gdal
try:
    import osr
except Exception:
    from osgeo import osr
from datetime import datetime
import numpy as np
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')

# Default values
TMIN = '20200216'
TMAX = '20200730'
DATDIR = os.curdir
MASK_FNAM = os.path.join(HOME,'Work','Sentinel-1_Analysis','paddy_mask.tif')

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-r','--ref_fnam',default=None,help='Reference file name (%(default)s)')
parser.add_argument('-d','--dst_fnam',default=None,help='Destination file name (%(default)s)')
parser.add_argument('--mask_fnam',default=MASK_FNAM,help='Mask file name (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date of transplanting in the format YYYYMMDD (%(default)s)')
args = parser.parse_args()
if args.ref_fnam is None:
    raise ValueError('Error, args.ref_fnam={}'.format(args.ref_fnam))
if args.dst_fnam is None:
    raise ValueError('Error, args.dst_fnam={}'.format(args.dst_fnam))

dmin = datetime.strptime(args.tmin,'%Y%m%d')
dmax = datetime.strptime(args.tmax,'%Y%m%d')

ds = gdal.Open(args.mask_fnam)
mask_nx = ds.RasterXSize
mask_ny = ds.RasterYSize
mask_nb = ds.RasterCount
if mask_nb != 1:
    raise ValueError('Error, mask_nb={} >>> {}'.format(mask_nb,args.mask_fnam))
mask_shape = (mask_ny,mask_nx)
mask = ds.ReadAsArray().reshape(mask_shape)
ds = None

ds = gdal.Open(args.ref_fnam)
ref_nx = ds.RasterXSize
ref_ny = ds.RasterYSize
ref_nb = ds.RasterCount
ref_shape = (ref_ny,ref_nx)
ref_prj = ds.GetProjection()
ref_trans = ds.GetGeoTransform()
ref_meta = ds.GetMetadata()
ref_data = ds.ReadAsArray()
if ref_shape != mask_shape:
    raise ValueError('Error, ref_shape={}, mask_shape={}'.format(ref_shape,mask_shape))
ds = None
ref_tmin = ref_meta['tmin']
ref_tmax = ref_meta['tmax']
if ref_tmin != dmin.strftime('%Y%m%d') or ref_tmax != dmax.strftime('%Y%m%d'):
    raise ValueError('Error, ref_tmin={}, ref_tmax={}, dmin={:%Y%m%d}, dmax={:%Y%m%d}'.format(ref_tmin,ref_tmax,dmin,dmax))

dst_nx = ref_nx
dst_ny = ref_ny
dst_nb = 5
dst_shape = (dst_ny,dst_nx)
dst_prj = ref_prj
dst_trans = ref_trans
dst_meta = ref_meta
dst_data = np.full((dst_nb,dst_ny,dst_nx),np.nan)
dst_band = ['avg','std','number','area','density']
dst_nodata = np.nan

flag = False
for iy in range(ref_ny):
    #if iy%100 == 0:
    #    sys.stderr.write('{}/{}\n'.format(iy,ref_ny))
    for ix in range(ref_nx):
        #if mask[iy,ix] < 0.5:
        #    continue
        dtmp = ref_data[0,max(iy-5,0):min(iy+6,ref_ny),max(ix-5,0):min(ix+6,ref_nx)].copy()
        ntmp = (~np.isnan(dtmp)).sum()
        if ntmp < 10:
            dtmp = ref_data[0,max(iy-10,0):min(iy+11,ref_ny),max(ix-10,0):min(ix+11,ref_nx)].copy()
            ntmp = (~np.isnan(dtmp)).sum()
            if ntmp < 10:
                dtmp = ref_data[0,max(iy-20,0):min(iy+21,ref_ny),max(ix-20,0):min(ix+21,ref_nx)].copy()
                ntmp = (~np.isnan(dtmp)).sum()
                if ntmp < 10:
                    dtmp = ref_data[0,max(iy-50,0):min(iy+51,ref_ny),max(ix-50,0):min(ix+51,ref_nx)].copy()
                    ntmp = (~np.isnan(dtmp)).sum()
                    if ntmp < 10:
                        continue
        davg = np.nanmean(dtmp)
        dstd = np.nanstd(dtmp)
        cnd = np.abs(dtmp-davg) > dstd*3.0
        dtmp[cnd] = np.nan
        davg = np.nanmean(dtmp)
        dstd = np.nanstd(dtmp)
        cnd = np.abs(dtmp-davg) > dstd*3.0
        dtmp[cnd] = np.nan
        ntmp = (~np.isnan(dtmp)).sum()
        dst_data[0,iy,ix] = np.nanmean(dtmp)
        dst_data[1,iy,ix] = np.nanstd(dtmp)
        dst_data[2,iy,ix] = float(ntmp)
        dst_data[3,iy,ix] = float(dtmp.size)
        dtmp = ref_data[0,max(iy-50,0):min(iy+51,ref_ny),max(ix-50,0):min(ix+51,ref_nx)].copy()
        ntmp = (~np.isnan(dtmp)).sum()
        dst_data[4,iy,ix] = float(ntmp)/dtmp.size
        #flag = True
        #if flag:
        #    break
    #if flag:
    #    break

drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.dst_fnam,dst_nx,dst_ny,dst_nb,gdal.GDT_Float32)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
for i in range(dst_nb):
    band = ds.GetRasterBand(i+1)
    band.WriteArray(dst_data[i])
    band.SetDescription(dst_band[i])
band.SetNoDataValue(dst_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
