#!/usr/bin/env python
import os
import sys
import re
import numpy as np
import tifffile
import xml.etree.ElementTree as ET
try:
    import gdal
except Exception:
    from osgeo import gdal
try:
    import osr
except Exception:
    from osgeo import osr
from scipy.interpolate import griddata
from argparse import ArgumentParser,RawTextHelpFormatter

# Defaults
DATDIR = os.curdir
XMIN_CIHEA = 743805.0 # Cihea, pixel center
XMAX_CIHEA = 757295.0 # Cihea, pixel center
YMIN_CIHEA = 9235815.0 # Cihea, pixel center
YMAX_CIHEA = 9251805.0 # Cihea, pixel center
XMIN_BOJONGSOANG = 790585.0 # Bojongsoang, pixel center
XMAX_BOJONGSOANG = 799555.0 # Bojongsoang, pixel center
YMIN_BOJONGSOANG = 9224425.0 # Bojongsoang, pixel center
YMAX_BOJONGSOANG = 9229335.0 # Bojongsoang, pixel center
XSTP = 10.0
YSTP = -10.0
BAND_COL = 1

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_fnam',default=None,help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('-D','--datdir',default=DATDIR,help='Output data directory (%(default)s)')
parser.add_argument('--site',default=None,help='Site name for preset coordinates (%(default)s)')
parser.add_argument('-b','--output_band',default=None,action='append',help='Output band name (%(default)s)')
parser.add_argument('--output_bmin',default=None,type=int,help='Minimum output band index (%(default)s)')
parser.add_argument('--output_bmax',default=None,type=int,help='Maximum output band index (%(default)s)')
parser.add_argument('-B','--band_fnam',default=None,help='Band file name (%(default)s)')
parser.add_argument('-x','--xmin',default=XMIN_CIHEA,type=float,help='Minimum X in m (%(default)s)')
parser.add_argument('-X','--xmax',default=XMAX_CIHEA,type=float,help='Maximum X in m (%(default)s)')
parser.add_argument('--xstp',default=XSTP,type=float,help='Step X in m (%(default)s)')
parser.add_argument('-y','--ymin',default=YMIN_CIHEA,type=float,help='Minimum Y in m (%(default)s)')
parser.add_argument('-Y','--ymax',default=YMAX_CIHEA,type=float,help='Maximum Y in m (%(default)s)')
parser.add_argument('--ystp',default=YSTP,type=float,help='Step Y in m (%(default)s)')
parser.add_argument('--band_col',default=BAND_COL,help='Band column number (%(default)s)')
parser.add_argument('--no_check_grid',default=False,action='store_true',help='Do not check grid (%(default)s)')
parser.add_argument('--read_comments',default=False,action='store_true',help='Read comments from input_file (%(default)s)')
parser.add_argument('-v','--verbose',default=False,action='store_true',help='Verbose mode (%(default)s)')
parser.add_argument('--overwrite',default=False,action='store_true',help='Overwrite mode (%(default)s)')
args = parser.parse_args()
if args.out_fnam is None:
    bnam,enam = os.path.splitext(os.path.basename(args.inp_fnam))
    args.out_fnam = os.path.join(args.datdir,bnam+'_resample'+enam)
if os.path.exists(args.out_fnam) and not args.overwrite:
    sys.stderr.write('input: {}, output: {} ... exists, skip!\n'.format(args.inp_fnam,args.out_fnam))
    sys.exit()
if args.site is not None:
    if args.site.lower() == 'cihea':
        args.xmin = XMIN_CIHEA
        args.xmax = XMAX_CIHEA
        args.ymin = YMIN_CIHEA
        args.ymax = YMAX_CIHEA
    elif args.site.lower() == 'bojongsoang':
        args.xmin = XMIN_BOJONGSOANG
        args.xmax = XMAX_BOJONGSOANG
        args.ymin = YMIN_BOJONGSOANG
        args.ymax = YMAX_BOJONGSOANG
    else:
        raise ValueError('Error, unknown site >>> '+args.site)

dst_trans = (args.xmin-0.5*args.xstp,args.xstp,0.0,args.ymax-0.5*args.ystp,0.0,args.ystp)
dst_xp,dst_yp = np.meshgrid(np.arange(args.xmin,args.xmax+0.1*args.xstp,args.xstp),np.arange(args.ymax,args.ymin+0.1*args.ystp,args.ystp))
dst_shape = dst_xp.shape
dst_ny,dst_nx = dst_shape

ds = gdal.Open(args.inp_fnam)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
src_shape = (src_ny,src_nx)
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().astype(np.float64).reshape(src_nb,src_ny,src_nx)
src_indy,src_indx = np.indices(src_shape)
src_xp = src_trans[0]+(src_indx+0.5)*src_trans[1]+(src_indy+0.5)*src_trans[2]
src_yp = src_trans[3]+(src_indx+0.5)*src_trans[4]+(src_indy+0.5)*src_trans[5]
if not args.no_check_grid:
    indx1 = np.argmin(np.abs(src_xp[0,:]-dst_xp[0,0]))
    indx2 = np.argmin(np.abs(src_xp[0,:]-dst_xp[0,-1]))+1
    indy1 = np.argmin(np.abs(src_yp[:,0]-dst_yp[0,0]))
    indy2 = np.argmin(np.abs(src_yp[:,0]-dst_yp[-1,0]))+1
    if np.array_equal(dst_xp[0,:],src_xp[0,indx1:indx2]) and np.array_equal(dst_yp[:,0],src_yp[indy1:indy2,0]):
        flag_grid = True
    else:
        flag_grid = False
else:
    flag_grid = False
# Get band name
band_name = []
if args.band_fnam is not None:
    with open(args.band_fnam,'r') as fp:
        for line in fp:
            item = line.split()
            if len(item) <= args.band_col or item[0][0]=='#':
                continue
            band_name.append(item[args.band_col])
else:
    if ds.GetRasterBand(1).GetDescription() != '':
        for i in range(src_nb):
            band = ds.GetRasterBand(i+1)
            band_name.append(band.GetDescription())
    else:
        tif_tags = {}
        with tifffile.TiffFile(args.inp_fnam) as tif:
            for tag in tif.pages[0].tags.values():
                name,value = tag.name,tag.value
                tif_tags[name] = value
        if '65000' in tif_tags:
            root = ET.fromstring(tif_tags['65000'])
            for value in root.iter('BAND_NAME'):
                band_name.append(value.text)
        else:
            for i in range(src_nb):
                band_name.append('band_{}'.format(i+1))
nband = len(band_name)
if nband != src_nb:
    raise ValueError('Error, nband={}, src_nb={}'.format(nband,src_nb))
if args.read_comments:
    comments = {}
    tif_tags = {}
    with tifffile.TiffFile(args.inp_fnam) as tif:
        for tag in tif.pages[0].tags.values():
            name,value = tag.name,tag.value
            tif_tags[name] = value
    if '65000' in tif_tags:
        root = ET.fromstring(tif_tags['65000'])
        for dataset in root.findall('Dataset_Sources'):
            for metadata in dataset.findall('MDElem'):
                if metadata.attrib['name'].lower() == 'metadata':
                    for abstract in metadata.findall('MDElem'):
                        if abstract.attrib['name'].lower() == 'abstracted_metadata':
                            for attr in abstract.findall('MDATTR'):
                                if attr.attrib['name'].lower() == 'pass':
                                    comments[attr.attrib['name']] = attr.text
        for value in root.iter('DATASET_COMMENTS'):
            for line in value.text.split('\n'):
                m = re.search('([^=]+)=([^=]+)',value.text)
                if m:
                    comments[m.group(1).strip()] = m.group(2).strip()
    src_meta.update(comments)
ds = None # close dataset

if args.output_bmin is not None:
    if args.output_bmax is not None:
        indxs = list(range(args.output_bmin,args.output_bmax+1))
    else:
        indxs = list(range(args.output_bmin,src_nb))
elif args.output_bmax is not None:
    indxs = list(range(0,args.output_bmax+1))
elif args.output_band is None:
    indxs = list(range(0,src_nb))
else:
    indxs = []
if args.output_band is not None:
    for band in args.output_band:
        indxs.append(band_name.index(band))
dst_nb = len(indxs)
if args.verbose:
    for i in indxs:
        sys.stderr.write('{}\n'.format(band_name[i]))
if flag_grid:
    sys.stderr.write('############ No need to interpolate.\n')
    dst_data = src_data[indxs,indy1:indy2,indx1:indx2]
else:
    dst_data = []
    for i in indxs:
        dst_data.append(griddata((src_xp.flatten(),src_yp.flatten()),src_data[i].flatten(),(dst_xp.flatten(),dst_yp.flatten()),method='nearest').reshape(dst_shape))
    dst_data = np.array(dst_data)
dst_meta = src_meta
dst_prj = src_prj

drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.out_fnam,dst_nx,dst_ny,dst_nb,gdal.GDT_Float32)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
for i in range(dst_nb):
    band = ds.GetRasterBand(i+1)
    band.WriteArray(dst_data[i])
    band.SetDescription(band_name[indxs[i]])
band.SetNoDataValue(np.nan) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
