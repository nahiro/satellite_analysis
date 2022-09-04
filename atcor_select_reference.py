#!/usr/bin/env python
import os
import sys
import re
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
import shapefile
from shapely.geometry import shape
from datetime import datetime
from matplotlib.dates import date2num
import numpy as np
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
S2_BAND = {'b':'B2','g':'B3','r':'B4','e1':'B5','e2':'B6','e3':'B7','n1':'B8','n2':'B8A','s1':'B11','s2':'B12'}
SC_BAND = 'quality_scene_classification'

# Default values
OUT_FNAM = 'nearest_inds.npz'
REF_BAND = ['b','g','r','n1']
RTHR = 0.035
N_NEAREST = 1000

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-O','--out_fnam',default=OUT_FNAM,help='Output index file name (%(default)s)')
parser.add_argument('-B','--ref_band',default=None,action='append',help='Band for reference select ({})'.format(REF_BAND))
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('-r','--rthr',default=RTHR,type=float,help='Threshold for reference select (%(default)s)')
parser.add_argument('-n','--n_nearest',default=N_NEAREST,type=int,help='Number of nearest indices (%(default)s)')
#parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
#parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
#parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
#parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
#parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.ref_band is None:
    args.ref_band = REF_BAND
d1 = datetime.strptime(args.data_tmin,'%Y%m%d')
d2 = datetime.strptime(args.data_tmax,'%Y%m%d')
data_years = np.arange(d1.year,d2.year+1,1)

# Read Shapefile
r = shapefile.Reader(args.shp_fnam)
nobject = len(r)
if args.use_index:
    object_ids = np.arange(nobject)+1
else:
    list_ids = []
    for rec in r.iterRecords():
        list_ids.append(rec.OBJECTID)
    object_ids = np.array(list_ids)
x_center = []
y_center = []
for shp in shape(r.shapes()).geoms:
    x_center.append(shp.centroid.x)
    y_center.append(shp.centroid.y)
x_center = np.array(x_center)
y_center = np.array(y_center)

src_nx = None
src_ny = None
src_nb = len(args.ref_band)
src_shape = None
src_prj = None
src_trans = None
src_data = []
scl_data = []
src_band = []
for band in args.ref_band:
    if not band in S2_BAND:
        raise ValueError('Error, unknown band >>> {}'.format(band))
    src_band.append(S2_BAND[band])
src_dtim = []
for year in data_years:
    ystr = '{}'.format(year)
    dnam = os.path.join(args.inpdir,ystr)
    if not os.path.isdir(dnam):
        continue
    for f in sorted(os.listdir(dnam)):
        m = re.search('^('+'\d'*8+')_resample\.tif$',f)
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
        tmp_indx = []
        for band in src_band:
            if not band in tmp_band:
                raise ValueError('Error in finding {} >>> {}'.format(band,fnam))
            tmp_indx.append(tmp_band.index(band))
        if not SC_BAND in tmp_band:
            raise ValueError('Error in finding {} >>> {}'.format(SC_BAND,fnam))
        scl_indx = tmp_band.index(SC_BAND)
        src_data.append(tmp_data[tmp_indx])
        scl_data.append(tmp_data[scl_indx])
        src_dtim.append(d)
src_data = np.array(src_data)*1.0e-4 # NTIM,NBAND,NY,NX
scl_data = np.array(scl_data) # NTIM,NY,NX
src_dtim = np.array(src_dtim)
src_ntim = date2num(src_dtim)
src_indy,src_indx = np.indices(src_shape)
src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]

cnd = np.full(src_shape,True)
scl_cnd = (scl_data < 1.9) | ((scl_data > 2.1) & (scl_data < 3.9)) | (scl_data > 7.1)
for iband in range(src_nb):
    tmp_data = src_data[:,iband,:,:].astype(np.float64)
    tmp_data[scl_cnd] = np.nan
    cnd &= (np.nanstd(tmp_data,axis=0) < args.rthr)
inds = np.indices([cnd.size]).reshape(src_shape)
inds_selected = inds[cnd]
xq = src_xp.flatten()[inds_selected]
yq = src_yp.flatten()[inds_selected]

leng_array = []
inds_array = []
for n in range(nobject):
    l2 = np.square(xq-x_center[n])+np.square(yq-y_center[n])
    indx = np.argsort(l2)
    leng_temp = np.sqrt(l2[indx[:args.n_nearest]])
    inds_temp = inds_selected[indx[:args.n_nearest]]
    leng_array.append(leng_temp)
    inds_array.append(inds_temp)
leng_array = np.array(leng_array)
inds_array = np.array(inds_array)
np.savez(args.out_fnam,object_ids=object_ids,leng=leng_array,inds=inds_array)
