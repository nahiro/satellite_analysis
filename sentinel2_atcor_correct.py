#!/usr/bin/env python
import os
import re
import shutil
import warnings
import numpy as np
try:
    import gdal
except Exception:
    from osgeo import gdal
import shapefile
import numpy as np
import geopandas as gpd
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
ATCOR_PARAM = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','NDVI','GNDVI','NRGI']
NORM_BAND = ['b','g','r','e1','e2','e3','n1']
RGI_RED_BAND = 'e1'
CR_BAND = 'r'
CTHR = 0.35
R_MIN = 0.3

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-I','--src_geotiff',default=None,help='Source GeoTIFF name (%(default)s)')
parser.add_argument('-M','--mask_geotiff',default=None,help='Mask GeoTIFF name (%(default)s)')
parser.add_argument('-A','--atcor_fnam',default=None,help='Atcor parameter file name (%(default)s)')
parser.add_argument('-P','--parcel_fnam',default=None,help='Parcel file name (%(default)s)')
parser.add_argument('-p','--param',default=None,action='append',help='Output parameter ({})'.format(PARAM))
parser.add_argument('-a','--atcor_param',default=None,action='append',help='Parameters to be corrected ({})'.format(ATCOR_PARAM))
parser.add_argument('-C','--cr_band',default=CR_BAND,help='Wavelength band for cloud removal (%(default)s)')
parser.add_argument('-c','--cthr',default=CTHR,type=float,help='Threshold for cloud removal (%(default)s)')
parser.add_argument('--r_min',default=R_MIN,type=float,help='R threshold (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output NPZ name (%(default)s)')
parser.add_argument('-o','--out_shp',default=None,help='Output Shapefile name (%(default)s)')
parser.add_argument('--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-z','--ax1_zmin',default=None,type=float,action='append',help='Axis1 Z min for debug (%(default)s)')
parser.add_argument('-Z','--ax1_zmax',default=None,type=float,action='append',help='Axis1 Z max for debug (%(default)s)')
parser.add_argument('-s','--ax1_zstp',default=None,type=float,action='append',help='Axis1 Z stp for debug (%(default)s)')
parser.add_argument('-t','--ax1_title',default=None,help='Axis1 title for debug (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.param is None:
    args.param = PARAM
for param in args.param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
if args.atcor_param is None:
    args.atcor_param = ATCOR_PARAM
for param in args.atcor_param:
    if not param in PARAMS:
        raise ValueError('Error, unknown parameter >>> {}'.format(param))
    if not param in args.param:
        raise ValueError('Error, not included in output parameter >>> {}'.format(param))
if not args.cr_band in S2_PARAM:
    raise ValueError('Error, unknown band for cloud removal >>> {}'.format(args.cr_band))
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
if not os.path.exists(args.parcel_fnam):
    raise IOError('Error, no such file >>> '+args.parcel_fnam)
if not os.path.exists(args.atcor_fnam):
    raise IOError('Error, no such file >>> '+args.atcor_fnam)
if args.out_fnam is None or args.out_shp is None or args.fignam is None:
    bnam,enam = os.path.splitext(os.path.basename(args.src_geotiff))
    if args.out_fnam is None:
        args.out_fnam = bnam+'_atcor.npz'
    if args.out_shp is None:
        args.out_shp = bnam+'_atcor.shp'
    if args.fignam is None:
        args.fignam = bnam+'_atcor.pdf'
if not args.debug:
    warnings.simplefilter('ignore')

# Read Shapefile
r = shapefile.Reader(args.shp_fnam)
nobject = len(r)
if args.use_index:
    all_ids = np.arange(nobject)+1
else:
    list_ids = []
    for rec in r.iterRecords():
        list_ids.append(rec.OBJECTID)
    all_ids = np.array(list_ids)

# Read parcel data
data = np.load(args.parcel_fnam)
inp_band = data['params'].tolist()
inp_data = data['data']
norm_band = data['norm_band'].tolist()
rgi_red_band = str(data['rgi_red_band'])
if not np.array_equal(data['object_ids'],all_ids):
    raise ValueError('Error, different OBJECTID >>> {}'.format(args.parcel_fnam))
inp_cflag_sc = data['cflag_sc']
inp_cflag_ref = data['cflag_ref']
inp_cr_band = str(data['cloud_band'])
inp_cthr = float(data['cloud_thr'])
for param in args.param:
    if not param in inp_band:
        if not param in args.atcor_param:
            raise ValueError('Error in finding {} in {}'.format(param,args.parcel_fnam))

# Check parameters to be collected
cal_band = []
for param in args.atcor_param:
    if not param in inp_band:
        cal_band.append(param)
    else:
        iband = inp_band.index(param)
        if inp_cflag_sc[iband]: # cloud removal by SC is applied
            cal_band.append(param)
        elif not inp_cflag_ref[iband]: # cloud removal by reflectance is not appplied
            cal_band.append(param)
        elif inp_cr_band != args.cr_band:
            cal_band.append(param)
        elif not np.allclose(inp_cthr,args.cthr):
            cal_band.append(param)

# Parcellate data
if len(cal_band) > 0:
    cal_cflag_sc = False
    cal_cflag_ref = True
    cal_cr_band = args.cr_band
    cal_cthr = args.cthr
    # Read Source GeoTIFF
    ds = gdal.Open(args.src_geotiff)
    src_nx = ds.RasterXSize
    src_ny = ds.RasterYSize
    src_nb = len(cal_band)
    ngrd = src_nx*src_ny
    src_shape = (src_ny,src_nx)
    src_prj = ds.GetProjection()
    src_trans = ds.GetGeoTransform()
    if src_trans[2] != 0.0 or src_trans[4] != 0.0:
        raise ValueError('Error, src_trans={} >>> {}'.format(src_trans,args.src_geotiff))
    src_meta = ds.GetMetadata()
    src_band = cal_band
    tmp_nb = ds.RasterCount
    tmp_band = []
    for iband in range(tmp_nb):
        band = ds.GetRasterBand(iband+1)
        tmp_band.append(band.GetDescription())
    src_data = []
    for param in cal_band:
        if not param in tmp_band:
            raise ValueError('Error in finding {} in {}'.format(param,args.src_geotiff))
        iband = tmp_band.index(param)
        band = ds.GetRasterBand(iband+1)
        src_data.append(band.ReadAsArray().astype(np.float64).reshape(ngrd))
    src_data = np.array(src_data)
    src_dtype = band.DataType
    src_nodata = band.GetNoDataValue()
    param = 'S'+args.cr_band
    if not param in tmp_band:
        raise ValueError('Error in finding {} in {}'.format(param,args.src_geotiff))
    iband = tmp_band.index(param)
    band = ds.GetRasterBand(iband+1)
    cr_data = band.ReadAsArray().reshape(ngrd)
    src_xmin = src_trans[0]
    src_xstp = src_trans[1]
    src_xmax = src_xmin+src_nx*src_xstp
    src_ymax = src_trans[3]
    src_ystp = src_trans[5]
    src_ymin = src_ymax+src_ny*src_ystp
    ds = None
    if src_nodata is not None and not np.isnan(src_nodata):
        src_data[src_data == src_nodata] = np.nan
    mask_ref = (cr_data > args.cthr)
    if 'norm_band' in src_meta:
        if (len(src_meta['norm_band']) > 0) and (not np.array_equal(norm_band,[s.strip() for s in src_meta['norm_band'].split(',')])):
            raise ValueError('Error, different band for normalization >>> {}'.format(args.src_geotiff))
    if 'rgi_red_band' in src_meta:
        if (rgi_red_band != '') and (rgi_red_band != src_meta['rgi_red_band']):
            raise ValueError('Error, different band for RGI >>> {}'.format(args.src_geotiff))

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
    object_inds = np.array(object_inds,dtype=object)
    tmp_data = np.full((ndat,src_nb),np.nan)

    # Calculate mean indices
    for iband,param in enumerate(cal_band):
        data = src_data[iband]
        data[mask_ref] = np.nan
        tmp_data[:,iband] = [np.nanmean(data[inds]) for inds in object_inds]

    # Store data
    if args.use_index:
        if np.array_equal(object_ids,all_ids):
            cal_data = tmp_data
        else:
            if (object_ids[0] < 1) or (object_ids[-1] > nobject):
                raise ValueError('Error, object_ids[0]={}, object_ids[-1]={}, nobject={} >>> {}'.format(object_ids[0],object_ids[-1],nobject,args.mask_geotiff))
            indx = object_ids-1
            cal_data = np.full((nobject,src_nb),np.nan)
            cal_data[indx] = tmp_data
    else:
        if np.array_equal(object_ids,all_ids):
            cal_data = tmp_data
        else:
            try:
                indx = np.array([list_ids.index(object_id) for object_id in object_ids])
            except Exception:
                raise ValueError('Error in finding OBJECTID in {}'.format(args.shp_fnam))
            cal_data = np.full((nobject,src_nb),np.nan)
            cal_data[indx] = tmp_data

# Data before correction
org_nb = len(args.param)
org_band = []
org_data = np.full((nobject,org_nb),np.nan)
org_cflag_sc = []
org_cflag_ref = []
org_cr_band = []
org_cthr = []
for iband,param in enumerate(args.param):
    org_band.append(param)
    if param in cal_band:
        indx = cal_band.index(param)
        org_data[:,iband] = cal_data[:,indx]
        org_cflag_sc.append(cal_cflag_sc)
        org_cflag_ref.append(cal_cflag_ref)
        org_cr_band.append(cal_cr_band)
        org_cthr.append(cal_cthr)
    else:
        indx = inp_band.index(param)
        org_data[:,iband] = inp_data[:,indx]
        org_cflag_sc.append(inp_cflag_sc[indx])
        org_cflag_ref.append(inp_cflag_ref[indx])
        org_cr_band.append(inp_cr_band)
        org_cthr.append(inp_cthr)

# Read atcor paramater
param = np.load(args.atcor_fnam)
atcor_band = param['params'].tolist()
corcoef = param['corcoef']
factor = param['factor']
offset = param['offset']
cnd = (corcoef < args.r_min)
factor[cnd] = np.nan
offset[cnd] = np.nan
npar = factor.shape[1]
if npar != nobject:
    raise ValueError('Error, npar={}, nobject={}'.format(npar,nobject))
for param in args.atcor_param:
    if not param in atcor_band:
        raise ValueError('Error in finding {} in {}'.format(param,args.atcor_fnam))

# Atmospheric correction
cor_nb = len(args.param)
cor_data = np.full((nobject,cor_nb),np.nan)
for iband,param in enumerate(args.param):
    if param in args.atcor_param:
        indx = atcor_band.index(param)
        cor_data[:,iband] = org_data[:,iband]*factor[indx]+offset[indx]
    else:
        cor_data[:,iband] = org_data[:,iband]

# Output file
np.savez(args.out_fnam,
params=args.param,
atcor_params=args.atcor_param,
norm_band=norm_band,
rgi_red_band=rgi_red_band,
object_ids=all_ids,
data_org=org_data,
data=cor_data,
cflag_sc=org_cflag_sc,
cflag_ref=org_cflag_ref,
cloud_band=org_cr_band,
cloud_thr=org_cthr)

# Output Shapefile
w = shapefile.Writer(args.out_shp)
w.shapeType = shapefile.POLYGON
w.fields = r.fields[1:] # skip first deletion field
for param in args.param:
    w.field(param,'F',13,6)
for iobj,shaperec in enumerate(r.iterShapeRecords()):
    rec = shaperec.record
    shp = shaperec.shape
    rec.extend(list(cor_data[iobj]))
    w.shape(shp)
    w.record(*rec)
w.close()
shutil.copy2(os.path.splitext(args.shp_fnam)[0]+'.prj',os.path.splitext(args.out_shp)[0]+'.prj')

# Output CSV
if args.out_csv is not None:
    with open(args.out_csv,'w') as fp:
        fp.write('{:>8s}'.format('OBJECTID'))
        for param in args.param:
            fp.write(', {:>13s}'.format(param))
        fp.write('\n')
        for iobj,object_id in enumerate(all_ids):
            fp.write('{:8d}'.format(object_id))
            for iband,param in enumerate(args.param):
                fp.write(', {:>13.6e}'.format(cor_data[iobj,iband]))
            fp.write('\n')

# For debug
if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(5,5))
    plt.subplots_adjust(top=0.9,bottom=0.1,left=0.05,right=0.80)
    pdf = PdfPages(args.fignam)
    indices = gpd.read_file(args.out_shp)
    for iband,param in enumerate(args.param):
        fig.clear()
        ax1 = plt.subplot(111)
        ax1.set_xticks([])
        ax1.set_yticks([])
        if args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
            zmin = ax1_zmin[param]
        else:
            zmin = np.nanmin(cor_data[:,iband])
            if np.isnan(zmin):
                zmin = 0.0
        if args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
            zmax = ax1_zmax[param]
        else:
            zmax = np.nanmax(cor_data[:,iband])
            if np.isnan(zmax):
                zmax = 1.0
        zdif = zmax-zmin
        indices.plot(column=param,ax=ax1,vmin=zmin,vmax=zmax,cmap=cm.jet)
        im = ax1.imshow(np.arange(4).reshape(2,2),extent=(-2,-1,-2,-1),vmin=zmin,vmax=zmax,cmap=cm.jet)
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right',size='5%',pad=0.05)
        if args.ax1_zstp is not None and not np.isnan(ax1_zstp[param]):
            if args.ax1_zmin is not None and not np.isnan(ax1_zmin[param]):
                zmin = (np.floor(ax1_zmin[param]/ax1_zstp[param])-1.0)*ax1_zstp[param]
            else:
                zmin = (np.floor(np.nanmin(cor_data[:,iband])/ax1_zstp[param])-1.0)*ax1_zstp[param]
            if args.ax1_zmax is not None and not np.isnan(ax1_zmax[param]):
                zmax = ax1_zmax[param]+0.1*ax1_zstp[param]
            else:
                zmax = np.nanmax(cor_data[:,iband])+0.1*ax1_zstp[param]
            ax2 = plt.colorbar(im,cax=cax,ticks=np.arange(zmin,zmax,ax1_zstp[param])).ax
        else:
            ax2 = plt.colorbar(im,cax=cax).ax
        ax2.minorticks_on()
        ax2.set_ylabel('{}'.format(BAND_NAME[param]))
        ax2.yaxis.set_label_coords(5.5,0.5)
        fig_xmin,fig_ymin,fig_xmax,fig_ymax = indices.total_bounds
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        if args.ax1_title is not None:
            ax1.set_title(args.ax1_title)
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    pdf.close()
