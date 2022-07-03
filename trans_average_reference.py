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

# Default values
TMIN = '20200216'
TMAX = '20200730'
DATDIR = '.'
MASK_FNAM = '/home/naohiro/Work/SATREPS/Transplanting_date/Cihea/paddy_mask.tif'
PERIOD_NUM = 0

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-s','--tmin',default=TMIN,help='Min date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-D','--datdir',default=DATDIR,help='Input data directory (%(default)s)')
parser.add_argument('--mask_fnam',default=MASK_FNAM,help='Mask file name (%(default)s)')
args = parser.parse_args()

dmin = datetime.strptime(args.tmin,'%Y%m%d')
dmax = datetime.strptime(args.tmax,'%Y%m%d')

ds = gdal.Open(args.mask_fnam)
mask = ds.ReadAsArray()
mask_shape = mask.shape
ds = None

gnam = os.path.join(args.datdir,'ref_{:%Y%m%d}_{:%Y%m%d}.tif'.format(dmin,dmax))
ds = gdal.Open(gnam)
data = ds.ReadAsArray()
data_shape = data[0].shape
if data_shape != mask_shape:
    raise ValueError('Error, data_shape={}, mask_shape={}'.format(data_shape,mask_shape))
data_trans = ds.GetGeoTransform()
data_meta = ds.GetMetadata()
prj = ds.GetProjection()
srs = osr.SpatialReference(wkt=prj)
estr = srs.GetAttrValue('AUTHORITY',1)
ds = None
data_tmin = data_meta['tmin']
data_tmax = data_meta['tmax']
if data_tmin != dmin.strftime('%Y%m%d') or data_tmax != dmax.strftime('%Y%m%d'):
    raise ValueError('Error, data_tmin={}, data_tmax={}, dmin={:%Y%m%d}, dmax={:%Y%m%d}'.format(data_tmin,data_tmax,dmin,dmax))
if re.search('\D',estr):
    raise ValueError('Error in EPSG >>> '+estr)
data_epsg = int(estr)
ndat = len(data)
nx = data_shape[1]
ny = data_shape[0]
nb = 5
output_data = np.full((nb,ny,nx),np.nan)

flag = False
for iy in range(data_shape[0]):
    if iy%100 == 0:
        sys.stderr.write('{}/{}\n'.format(iy,data_shape[0]))
    for ix in range(data_shape[1]):
        #if mask[iy,ix] < 0.5:
        #    continue
        dtmp = data[0,max(iy-5,0):min(iy+6,data_shape[0]),max(ix-5,0):min(ix+6,data_shape[1])].copy()
        ntmp = (~np.isnan(dtmp)).sum()
        if ntmp < 10:
            dtmp = data[0,max(iy-10,0):min(iy+11,data_shape[0]),max(ix-10,0):min(ix+11,data_shape[1])].copy()
            ntmp = (~np.isnan(dtmp)).sum()
            if ntmp < 10:
                dtmp = data[0,max(iy-20,0):min(iy+21,data_shape[0]),max(ix-20,0):min(ix+21,data_shape[1])].copy()
                ntmp = (~np.isnan(dtmp)).sum()
                if ntmp < 10:
                    dtmp = data[0,max(iy-50,0):min(iy+51,data_shape[0]),max(ix-50,0):min(ix+51,data_shape[1])].copy()
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
        output_data[0,iy,ix] = np.nanmean(dtmp)
        output_data[1,iy,ix] = np.nanstd(dtmp)
        output_data[2,iy,ix] = float(ntmp)
        output_data[3,iy,ix] = float(dtmp.size)
        dtmp = data[0,max(iy-50,0):min(iy+51,data_shape[0]),max(ix-50,0):min(ix+51,data_shape[1])].copy()
        ntmp = (~np.isnan(dtmp)).sum()
        output_data[4,iy,ix] = float(ntmp)/dtmp.size
        #flag = True
        #if flag:
        #    break
    #if flag:
    #    break

comments = {}
comments['tmin'] = '{:%Y%m%d}'.format(dmin)
comments['tmax'] = '{:%Y%m%d}'.format(dmax)
out_fnam = 'avg_{:%Y%m%d}_{:%Y%m%d}.tif'.format(dmin,dmax)
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(out_fnam,nx,ny,nb,gdal.GDT_Float32)
ds.SetGeoTransform(data_trans)
srs = osr.SpatialReference()
srs.ImportFromEPSG(data_epsg)
ds.SetProjection(srs.ExportToWkt())
ds.SetMetadata(comments)
band_name = ['avg','std','number','area','density']
for i in range(nb):
    band = ds.GetRasterBand(i+1)
    band.WriteArray(output_data[i])
    band.SetDescription(band_name[i])
band.SetNoDataValue(np.nan) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
