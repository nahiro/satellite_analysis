#!/usr/bin/env python
import os
import sys
try:
    import gdal
except Exception:
    from osgeo import gdal
try:
    import osr
except Exception:
    from osgeo import osr
from skimage.measure import points_in_poly
import shapefile
from shapely.geometry import Polygon
import numpy as np
from scipy.interpolate import griddata
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
BUFFER = -1.5 # m
NODATA_VALUE = -1

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-s','--shp_fnam',default=None,help='Shape file name (%(default)s)')
parser.add_argument('-b','--buffer',default=BUFFER,type=float,help='Buffer distance (%(default)s)')
parser.add_argument('-n','--nodata_value',default=NODATA_VALUE,type=int,help='No-data value (%(default)s)')
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('--select_inside',default=False,action='store_true',help='Select inside pixels (%(default)s)')
parser.add_argument('--select_outside',default=False,action='store_true',help='Select outside pixels (%(default)s)')
args = parser.parse_args()
if args.dst_geotiff is None:
    bnam,enam = os.path.splitext(os.path.basename(args.src_geotiff))
    args.dst_geotiff = bnam+'_mask'+enam

ds = gdal.Open(args.src_geotiff)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().astype(np.float64).reshape(src_nb,src_ny,src_nx)
src_band = []
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    src_band.append(band.GetDescription())
src_nodata = band.GetNoDataValue()
src_xmin = src_trans[0]
src_xstp = src_trans[1]
src_xmax = src_xmin+src_nx*src_xstp
src_ymax = src_trans[3]
src_ystp = src_trans[5]
src_ymin = src_ymax+src_ny*src_ystp
src_indy,src_indx = np.indices(src_shape)
src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
src_points = np.hstack((src_xp.reshape(-1,1),src_yp.reshape(-1,1)))
ds = None

dst_nx = src_nx
dst_ny = src_ny
dst_nb = 1
dst_shape = (dst_ny,dst_nx)
dst_prj = src_prj
dst_trans = src_trans
dst_meta = src_meta
dst_data = np.full(dst_shape,fill_value=args.nodata_value,dtype=np.int32)
dst_band = 'mask'
dst_nodata = args.nodata_value

r = shapefile.Reader(args.shp_fnam)
for ii,shaperec in enumerate(r.iterShapeRecords()):
    rec = shaperec.record
    shp = shaperec.shape
    if args.use_index:
        object_id = ii+1
    else:
        object_id = rec.OBJECTID
    if len(shp.points) < 1:
        sys.stderr.write('Warning, len(shp.points)={}, ii={}\n'.format(len(shp.points),ii))
        continue
    poly_buffer = Polygon(shp.points).buffer(args.buffer)
    if poly_buffer.area <= 0.0:
        continue
    xmin_buffer,ymin_buffer,xmax_buffer,ymax_buffer = poly_buffer.bounds
    if (xmin_buffer > src_xmax) or (xmax_buffer < src_xmin) or (ymin_buffer > src_ymax) or (ymax_buffer < src_ymin):
        continue
    flags = np.full(dst_shape,False)
    if poly_buffer.type == 'MultiPolygon':
        for p in poly_buffer.geoms:
            path_search = np.array(p.exterior.coords.xy).swapaxes(0,1)
            flags |= points_in_poly(src_points,path_search).reshape(dst_shape)
    else:
        path_search = np.array(poly_buffer.exterior.coords.xy).swapaxes(0,1)
        flags = points_in_poly(src_points,path_search).reshape(dst_shape)
    dst_data[flags] = object_id

if args.select_inside:
    mask = np.full(dst_shape,fill_value=1,dtype=np.int32)
    cnd = (dst_data < 0.5)
    mask[cnd] = dst_nodata
    dst_data = mask
elif args.select_outside:
    mask = np.full(dst_shape,fill_value=1,dtype=np.int32)
    cnd = (dst_data > -0.5)
    mask[cnd] = dst_nodata
    dst_data = mask

drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.dst_geotiff,dst_nx,dst_ny,dst_nb,gdal.GDT_Int32)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
band = ds.GetRasterBand(1)
band.WriteArray(dst_data)
band.SetDescription(dst_band)
band.SetNoDataValue(dst_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
