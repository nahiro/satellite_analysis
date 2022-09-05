#!/usr/bin/env python
import os
import sys
import re
import warnings
import numpy as np
try:
    import gdal
except Exception:
    from osgeo import gdal
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
NORM_BAND = ['b','g','r','e1','e2','e3','n1']
RGI_RED_BAND = 'e1'
CR_BAND = 'r'
CTHR = 0.35
R_MIN = 0.3

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-P','--parcel_fnam',default=None,help='Parcel file name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-C','--cr_band',default=CR_BAND,help='Wavelength band for cloud removal (%(default)s)')
parser.add_argument('-c','--cthr',default=CTHR,type=float,help='Threshold for cloud removal (%(default)s)')
parser.add_argument('--r_min',default=R_MIN,type=float,help='R threshold (%(default)s)')
parser.add_argument('--param_fnam',default=None,help='Atcor parameter file name (%(default)s)')
parser.add_argument('-o','--out_fnam',default=None,help='Output NPZ name (%(default)s)')
parser.add_argument('--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
args = parser.parse_args()
if args.param is None:
    args.param = PARAM
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if not args.cr_band in S2_PARAM:
    raise ValueError('Error, unknown band for cloud removal >>> {}'.format(args.cr_band))
if not os.path.exists(args.parcel_fnam):
    raise IOError('Error, no such file >>> '+args.parcel_fnam)
if not os.path.exists(args.param_fnam):
    raise IOError('Error, no such file >>> '+args.param_fnam)
if not args.debug:
    warnings.simplefilter('ignore')

# Read parcel data
data = np.load(args.parcel_fnam)
org_band = data['params'].tolist()
org_data = data['data_org']
object_ids = data['object_ids']
cflag_sc = data['cflag_sc']
cflag_ref = data['cflag_ref']
cloud_band = str(data['cloud_band'])
cloud_thr = float(data['cloud_thr'])

cal_param = []
for param in args.param:
    if not param in org_band:
        cal_param.append(param)
    else:
        iband = org_band.index(param)
        if cflag_sc[iband]: # cloud removal by SC is applied
            cal_param.append(param)
        elif not cflag_ref[iband]: # cloud removal by reflectance is not appplied
            cal_param.append(param)
        elif cloud_band != args.cr_band:
            cal_param.append(param)
        elif not np.allclose(cloud_thr,args.cthr):
            cal_param.append(param)
if len(cal_param) > 0: # Parcellate data
    # Read Source GeoTIFF
    ds = gdal.Open(args.src_geotiff)
    src_nx = ds.RasterXSize
    src_ny = ds.RasterYSize
    src_nb = len(cal_param)
    ngrd = src_nx*src_ny
    src_shape = (src_ny,src_nx)
    src_prj = ds.GetProjection()
    src_trans = ds.GetGeoTransform()
    if src_trans[2] != 0.0 or src_trans[4] != 0.0:
        raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
    src_meta = ds.GetMetadata()
    src_band = cal_param
    tmp_nb = ds.RasterCount
    tmp_band = []
    for iband in range(tmp_nb):
        band = ds.GetRasterBand(iband+1)
        tmp_band.append(band.GetDescription())
    src_data = []
    for param in cal_param:
        if not param in tmp_band:
            raise ValueError('Error in finding {} in {}'.format(param,args.src_geotiff))
        iband = tmp_band.index(param)
        band = ds.GetRasterBand(iband+1)
        src_data.append(band.ReadAsArray().astype(np.float64).reshape(ngrd))
    src_data = np.array(src_data)
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

    # Read Resample GeoTIFF
    ds = gdal.Open(args.res_geotiff)
    res_nx = ds.RasterXSize
    res_ny = ds.RasterYSize
    res_nb = ds.RasterCount
    res_shape = (res_ny,res_nx)
    if res_shape != src_shape:
        raise ValueError('Error, res_shape={}, src_shape={} >>> {}'.format(res_shape,src_shape,args.res_geotiff))
    res_data = ds.ReadAsArray().reshape(res_nb,ngrd)
    res_band = []
    for iband in range(res_nb):
        band = ds.GetRasterBand(iband+1)
        res_band.append(band.GetDescription())
    res_nodata = band.GetNoDataValue()
    ds = None
    if True in cflag_sc.values():
        if not 'quality_scene_classification' in res_band:
            raise ValueError('Error in finding SC band in {}'.format(args.res_geotiff))
        iband = res_band.index('quality_scene_classification')
        scl = res_data[iband]
        mask_sc = ((scl < 1.9) | ((scl > 2.1) & (scl < 3.9)) | (scl > 7.1))
    else:
        mask_sc = None
    if True in cflag_ref.values():
        band = S2_BAND[args.cloud_band]
        if not band in res_band:
            raise ValueError('Error in finding {} band in {}'.format(band,args.res_geotiff))
        iband = res_band.index(band)
        v = res_data[iband]*1.0e-4
        mask_ref = (v > args.cloud_thr)
    else:
        mask_ref = None

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

    # Calculate mean indices
    for iband,param in enumerate(cal_param):
        data = src_data[iband]
        if cflag_sc[param]:
            data[mask_sc] = np.nan
        if cflag_ref[param]:
            data[mask_ref] = np.nan
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




"""
# Read atcor paramater
param = np.load(args.param_fnam)
corcoef = param['corcoef']
factor = param['factor']
offset = param['offset']
cnd = (corcoef < args.r_min)
factor[cnd] = np.nan
offset[cnd] = np.nan
npar = factor.size

ds = gdal.Open(input_fnam)
data = ds.ReadAsArray()
band_list = []
if args.band_fnam is not None:
    with open(args.band_fnam,'r') as fp:
        for line in fp:
            item = line.split()
            if len(item) <= args.band_col or item[0][0]=='#':
                continue
            band_list.append(item[args.band_col])
    if len(data) != len(band_list):
        raise ValueError('Error, len(data)={}, len(band_list)={} >>> {}'.format(len(data),len(band_list),input_fnam))
else:
    for i in range(ds.RasterCount):
        band = ds.GetRasterBand(i+1)
        band_name = band.GetDescription()
        if not band_name:
            raise ValueError('Error, faild to read band name >>> {}'.format(input_fnam))
        band_list.append(band_name)
ds = None
if args.band.upper() == 'NDVI':
    band_name = 'B4'
    if not band_name in band_list:
        raise ValueError('Error, faild to search index for {}'.format(band_name))
    band4_index = band_list.index(band_name)
    b4_img = data[band4_index].astype(np.float64).flatten()
    band_name = 'B8'
    if not band_name in band_list:
        raise ValueError('Error, faild to search index for {}'.format(band_name))
    band8_index = band_list.index(band_name)
    b8_img = data[band8_index].astype(np.float64).flatten()
    data_img = (b8_img-b4_img)/(b8_img+b4_img)
    if not args.ignore_band4:
        b4_img *= 1.0e-4
else:
    band_name = 'B{}'.format(args.band)
    if not band_name in band_list:
        raise ValueError('Error, faild to search index for {}'.format(band_name))
    band_index = band_list.index(band_name)
    data_img = data[band_index].astype(np.float64).flatten()*1.0e-4
    if not args.ignore_band4:
        if args.band == 4:
            b4_img = data_img.copy()
        else:
            band_name = 'B4'
            if not band_name in band_list:
                raise ValueError('Error, faild to search index for {}'.format(band_name))
            band4_index = band_list.index(band_name)
            b4_img = data[band4_index].astype(np.float64).flatten()*1.0e-4

object_ids = []
blocks = []
inds = []
areas = []
with open(args.area_fnam,'r') as fp:
    for line in fp:
        item = line.split()
        if len(item) < 3 or item[0] == '#':
            continue
        object_ids.append(int(item[0]))
        blocks.append(item[1])
        inds.append([])
        areas.append([])
        n = int(item[2])
        if len(item) < 5 and n != 0:
            raise ValueError('Error, len(item)={}, n={}, expected n=0.'.format(len(item),n))
        for nn in range(3,n*2+3,2):
            inds[-1].append(int(item[nn]))
            areas[-1].append(float(item[nn+1]))
        inds[-1] = np.array(inds[-1])
        areas[-1] = np.array(areas[-1])
object_ids = np.array(object_ids)
blocks = np.array(blocks)
nobject = object_ids.size
if nobject != npar:
    raise ValueError('Error, nobject={}, npar={}'.format(nobject,npar))

data_org = []
for iobj in range(nobject):
    if inds[iobj].size < 1:
        data_org.append(np.nan)
        continue
    data_value = data_img[inds[iobj]]
    data_weight = areas[iobj]
    if args.ignore_band4:
        cnd = ~np.isnan(data_value)
    else:
        data_band4 = b4_img[inds[iobj]]
        cnd = (~np.isnan(data_value)) & (~np.isnan(data_band4)) & (data_band4 < args.band4_max)
    if cnd.sum() <= 1:
        data_org.append(data_value[cnd].mean())
    else:
        data_weighted_stats = DescrStatsW(data_value[cnd],weights=data_weight[cnd],ddof=0)
        data_org.append(data_weighted_stats.mean)
data_org = np.array(data_org)
data_cor = data_org*factor+offset
np.savez(args.out_fnam,data_org=data_org,data_cor=data_cor)
"""
