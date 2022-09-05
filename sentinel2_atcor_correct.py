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
parser.add_argument('-i','--parcel_fnam',default=None,help='Parcel file name (%(default)s)')
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
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

cal_band = []
for param in args.param:
    if not param in org_band:
        cal_band.append(param)
    else:
        iband = obs_band.index(param)
        if cflag_sc[iband]: # cloud removal by SC
            cal_band.append(param)
        elif not cflag_ref[iband]: # cloud removal by reflectance
            cal_band.append(param)

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
