#!/usr/bin/env python
import os
import psutil
mem_size = int(psutil.virtual_memory().available*0.8e-6)
topdir = os.getcwd()
options = '-Xmx{}m'.format(mem_size) # Save memory for JAVA
options += ' -Djava.io.tmpdir='+topdir # Temporary directory
os.environ['_JAVA_OPTIONS'] = options
if os.name == 'nt':
    os.system('set _JAVA_OPTIONS="{}"'.format(options))
else:
    os.system('export _JAVA_OPTIONS="{}"'.format(options))
import sys
import re
from snappy import Product,ProductIO,ProductUtils,GPF,HashMap,WKTReader,jpy
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
DATDIR = os.curdir
SITE = 'Cihea'
POLYGON_CIHEA = 'POLYGON((107.201 -6.910,107.367 -6.910,107.367 -6.750,107.201 -6.750,107.201 -6.910))' # Cihea
POLYGON_BOJONGSOANG = 'POLYGON((107.54 -7.04,107.75 -7.04,107.75 -6.95,107.54 -6.95,107.54 -7.04))' # Bojongsoang
RESOLUTION = 10 # m

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_fnam',default=None,help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('-D','--datdir',default=DATDIR,help='Output data directory (%(default)s)')
parser.add_argument('--site',default=SITE,help='Site name for preset coordinates (%(default)s)')
parser.add_argument('--polygon',default=None,help='Polygon of ROI in WKT format (%(default)s)')
parser.add_argument('-r','--resolution',default=RESOLUTION,type=int,help='Spatial resolution in m (%(default)s)')
parser.add_argument('-G','--geotiff',default=False,action='store_true',help='GeoTiff mode (%(default)s)')
args = parser.parse_args()
safe_flag = False
m = re.search('^[^_]+_[^_]+_([^_]+)_.*.zip$',os.path.basename(args.inp_fnam))
if not m:
    m = re.search('^[^_]+_[^_]+_([^_]+)_.*.SAFE$',os.path.basename(args.inp_fnam))
    if not m:
        raise ValueError('Error in file name >>> '+args.inp_fnam)
    safe_flag = True
dstr = m.group(1)[:8]
if args.out_fnam is None:
    if args.geotiff:
        args.out_fnam = os.path.join(args.datdir,'{}.tif'.format(dstr))
    else:
        args.out_fnam = os.path.join(args.datdir,'{}.dim'.format(dstr))
if os.path.exists(args.out_fnam):
    sys.exit()

if args.site is not None:
    if args.site.lower() == 'cihea':
        args.polygon = POLYGON_CIHEA
    elif args.site.lower() == 'bojongsoang':
        args.polygon = POLYGON_BOJONGSOANG
    else:
        raise ValueError('Error, unknown site >>> '+args.site)

# Get snappy Operators
GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
# Read original product
if safe_flag:
    data = ProductIO.readProduct(os.path.join(args.inp_fnam,'MTD_MSIL2A.xml'))
else:
    data = ProductIO.readProduct(args.inp_fnam)
# Resample (ResamplingOp.java)
params = HashMap()
params.put('sourceProduct',data)
params.put('upsampling','Bilinear')
params.put('downsampling','Mean')
params.put('targetResolution',args.resolution)
data_tmp = GPF.createProduct('Resample',params,data)
data = data_tmp
# Subset (SubsetOp.java)
wkt = args.polygon
geom = WKTReader().read(wkt)
params = HashMap()
params.put('copyMetadata',True)
params.put('geoRegion',geom)
data_tmp = GPF.createProduct('Subset',params,data)
data = data_tmp
if args.geotiff:
    ProductIO.writeProduct(data,args.out_fnam,'GeoTiff')
else:
    ProductIO.writeProduct(data,args.out_fnam,'BEAM-DIMAP')
