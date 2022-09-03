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
PARAMS = ['Sb','Sg','Sr','Se1','Se2','Se3','Sn1','Sn2','Ss1','Ss2',
          'Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2',
          'NDVI','GNDVI','RGI','NRGI']
S2_BAND = {'b':'B2','g':'B3','r':'B4','e1':'B5','e2':'B6','e3':'B7','n1':'B8','n2':'B8A','s1':'B11','s2':'B12'}

# Default values
PARAM = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','NDVI','GNDVI','NRGI']
CLN_BAND = 'r'
CTHR_AVG = 0.06
CTHR_STD = 0.05

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inpdir',default=None,help='Input directory (%(default)s)')
parser.add_argument('-O','--dst_geotiff',default=None,help='Destination GeoTIFF name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-C','--cln_band',default=CLN_BAND,help='Band for clean-day select (%(default)s)')
parser.add_argument('--mask_fnam',default=None,help='Mask file name (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--cthr_avg',default=CTHR_AVG,type=float,help='Threshold of mean for clean-day select (%(default)s)')
parser.add_argument('--cthr_std',default=CTHR_STD,type=float,help='Threshold of std for clean-day select (%(default)s)')
#parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
#parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
#parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
#parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
#parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.ref_band is None:
    args.ref_band = REF_BAND
for band in args.ref_band:
    if not band in S2_BAND:
        raise ValueError('Error, unknown band for reference select >>> {}'.format(band))
if not args.cln_band in S2_BAND:
    raise ValueError('Error, unknown band for clean-day select >>> {}'.format(args.cln_band))
cln_band = S2_BAND[args.cln_band]
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

# Read Source GeoTIFF
src_nx = None
src_ny = None
src_nb = len(args.ref_band)
src_shape = None
src_prj = None
src_trans = None
src_data = []
scl_data = [] # Scene Classification Data
cln_data = [] # Clean-day Selection Data
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
        if not cln_band in tmp_band:
            raise ValueError('Error in finding {} >>> {}'.format(cln_band,fnam))
        cln_indx = tmp_band.index(cln_band)
        src_data.append(tmp_data[tmp_indx])
        scl_data.append(tmp_data[scl_indx])
        cln_data.append(tmp_data[cln_indx])
        src_dtim.append(d)
src_data = np.array(src_data)*1.0e-4 # NTIM,NBAND,NY,NX
scl_data = np.array(scl_data) # NTIM,NY,NX
cln_data = np.array(cln_data)*1.0e-4 # NTIM,NY,NX
src_dtim = np.array(src_dtim)
src_ntim = date2num(src_dtim)
src_indy,src_indx = np.indices(src_shape)
src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]

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
src_data_selected = src_data[cnd] # NTIM,NBAND,NY,NX
cln_data_selected = cln_data[cnd] # NTIM,NY,NX
indx_all = np.arange(ncnd)

# Calculate stats for clean-day pixels
data_avg = np.full(src_shape,np.nan)
data_std = np.full(src_shape,np.nan)
for iy in range(src_ny):
    for ix in range(src_nx):
        src_data_tmp = src_data_selected[:,iy,ix]
        cln_data_tmp = cln_data_selected[:,iy,ix]
        indx = indx_all[np.isfinite(cln_data_tmp)]
        vc = cln_data_tmp[indx].copy()
        vm = vc.mean()
        ve = vc.std()
        cnd = (vc < vm+ve)
        ncnd = cnd.sum()
        if (ncnd != vc.size) and (ncnd > 4):
            indx = indx[cnd]
            vc = cln_data_tmp[indx].copy()
            vm = vc.mean()
            ve = vc.std()
            cnd = (vc < vm+ve)
            ncnd = cnd.sum()
            if (ncnd != vc.size) and (ncnd > 4):
                indx = indx[cnd]
                vc = cln_data_tmp[indx].copy()
                vm = vc.mean()
                ve = vc.std()
                cnd = (vc < vm+ve)
                ncnd = cnd.sum()
                if (ncnd != vc.size) and (ncnd > 4):
                    indx = indx[cnd]
        data_avg[iy,ix] = np.nanmean(src_data_tmp[indx],axis=0)
        data_std[iy,ix] = np.nanstd(src_data_tmp[indx],axis=0)
np.savez(args.out_stats,mean=data_avg,std=data_std)
