#!/usr/bin/env python
import tifffile
import xml.etree.ElementTree as ET
try:
    import gdal
except Exception:
    from osgeo import gdal
from argparse import ArgumentParser,RawTextHelpFormatter

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_fnam',default=None,help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output file name (%(default)s)')
args = parser.parse_args()

# Read BND_NAME
src_band = []
tif_tags = {}
with tifffile.TiffFile(args.inp_fnam) as tif:
    for tag in tif.pages[0].tags.values():
        name,value = tag.name,tag.value
        tif_tags[name] = value
if '65000' in tif_tags:
    root = ET.fromstring(tif_tags['65000'])
    for value in root.iter('BAND_NAME'):
        src_band.append(value.text)
else:
    raise ValueError('Error in finding 65000 >>> {}'.format(args.inp_fnam))

# Read GeoTIFF
ds = gdal.Open(args.inp_fnam)
src_nx = ds.RasterXSize
src_ny = ds.RasterYSize
src_nb = ds.RasterCount
if src_nb != len(src_band):
    raise ValueError('Error, src_nb={}, len(src_band)={} >>> {}'.format(src_nb,len(src_band),args.inp_fnam))
src_prj = ds.GetProjection()
src_trans = ds.GetGeoTransform()
src_meta = ds.GetMetadata()
src_data = ds.ReadAsArray().reshape((src_nb,src_ny,src_nx))
band = ds.GetRasterBand(1)
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
ds = None

# Write GeoTIFF
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.out_fnam,src_nx,src_ny,src_nb,src_dtype)
ds.SetProjection(src_prj)
ds.SetGeoTransform(src_trans)
ds.SetMetadata(src_meta)
for iband in range(src_nb):
    band = ds.GetRasterBand(iband+1)
    band.WriteArray(src_data[iband])
    band.SetDescription(src_band[iband])
if src_nodata is not None:
    band.SetNoDataValue(src_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
