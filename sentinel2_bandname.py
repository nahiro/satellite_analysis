#!/usr/bin/env python
import tifffile
import xml.etree.ElementTree as ET
import xmltodict
from datetime import datetime
import numpy as np
try:
    import gdal
except Exception:
    from osgeo import gdal
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
D0 = datetime(2022,1,25) # L2A product Baseline 04.00

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_fnam',default=None,help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('-d','--date',default=None,help='Data acquisition date in the format YYYYMMDD (%(default)s)')
parser.add_argument('--replace_no_data',default=False,action='store_true',help='Replace no_data (%(default)s)')
parser.add_argument('--add_offset',default=False,action='store_true',help='Add offset (%(default)s)')
args = parser.parse_args()

def get_band(metadata):
    src_band = None
    no_data = None
    d = metadata
    while True:
        if (type(d) != dict) or (not 'Dimap_Document' in d.keys()):
            break
        d = d['Dimap_Document']
        if (type(d) != dict) or (not 'Image_Interpretation' in d.keys()):
            break
        d = d['Image_Interpretation']
        if (type(d) != dict) or (not 'Spectral_Band_Info' in d.keys()):
            break
        d = d['Spectral_Band_Info']
        if type(d) != list or len(d) < 1:
            break
        src_band = []
        no_data = []
        for i in range(len(d)):
            if (type(d[i]) == dict) and ('BAND_NAME' in d[i]) and ('NO_DATA_VALUE' in d[i]):
                src_band.append(d[i]['BAND_NAME'])
                no_data.append(np.nan if d[i]['NO_DATA_VALUE'].lower() == 'nan' else eval(d[i]['NO_DATA_VALUE']))
            else:
                break
        if len(src_band) != len(d) or len(no_data) != len(d):
            src_band = None
            no_data = None
            break
        break
    return src_band,no_data

def get_offset(metadata):
    bands = None
    factor = None
    offsets = None
    d = metadata
    while True:
        if (type(d) != dict) or (not 'Dimap_Document' in d.keys()):
            break
        d = d['Dimap_Document']
        if (type(d) != dict) or (not 'Dataset_Sources' in d.keys()):
            break
        d = d['Dataset_Sources']
        if (type(d) != dict) or (not 'MDElem' in d.keys()):
            break
        d = d['MDElem']
        if (type(d) != dict) or (not 'MDElem' in d.keys()):
            break
        d = d['MDElem']
        if type(d) != list:
            break
        for i in range(len(d)):
            if (type(d[i]) == dict) and ('@name' in d[i]) and (d[i]['@name'] == 'Level-2A_User_Product'):
                d = d[i]
                break
        if (type(d) != dict) or (not 'MDElem' in d.keys()):
            break
        d = d['MDElem']
        if type(d) != list:
            break
        for i in range(len(d)):
            if (type(d[i]) == dict) and ('@name' in d[i]) and (d[i]['@name'] == 'General_Info'):
                d = d[i]
                break
        if (type(d) != dict) or (not 'MDElem' in d.keys()):
            break
        d = d['MDElem']
        if type(d) != list:
            break
        for i in range(len(d)):
            if (type(d[i]) == dict) and ('@name' in d[i]) and (d[i]['@name'] == 'Product_Image_Characteristics'):
                d = d[i]
                break
        if (type(d) != dict) or (not 'MDElem' in d.keys()):
            break
        d = d['MDElem']
        if type(d) != list:
            break
        # Read bands
        d3 = None
        for i in range(len(d)):
            if (type(d[i]) == dict) and ('@name' in d[i]) and (d[i]['@name'] == 'Spectral_Information_List'):
                d3 = d[i]
                break
        if (type(d3) != dict) or (not 'MDElem' in d3.keys()):
            break
        d3 = d3['MDElem']
        if type(d3) != list or len(d3) < 1:
            break
        bands = []
        for i in range(len(d3)):
            if (type(d3[i]) == dict) and ('@name' in d3[i]) and (d3[i]['@name'] == 'Spectral_Information') and ('MDATTR' in d3[i]):
                d4 = d3[i]['MDATTR']
                if type(d4) != list:
                    break
                band = None
                for j in range(len(d4)):
                    if (type(d4[j]) == dict) and ('@name' in d4[j]) and (d4[j]['@name'] == 'physicalBand') and ('#text' in d4[j]):
                        band = d4[j]['#text']
                        break
                if band is None:
                    break
                bands.append(band)
            else:
                break
        if len(bands) != len(d3):
            bands = None
            break
        # Read factor
        d1 = None
        for i in range(len(d)):
            if (type(d[i]) == dict) and ('@name' in d[i]) and (d[i]['@name'] == 'QUANTIFICATION_VALUES_LIST'):
                d1 = d[i]
                break
        if (type(d1) != dict) or (not 'MDATTR' in d1.keys()):
            break
        d1 = d1['MDATTR']
        if type(d1) != list:
            break
        for i in range(len(d1)):
            if (type(d1[i]) == dict) and ('@name' in d1[i]) and (d1[i]['@name'] == 'BOA_QUANTIFICATION_VALUE') and ('#text' in d1[i]):
                factor = eval(d1[i]['#text'])
                break
        if factor is None:
            break
        # Read offsets
        d2 = None
        for i in range(len(d)):
            if (type(d[i]) == dict) and ('@name' in d[i]) and (d[i]['@name'] == 'BOA_ADD_OFFSET_VALUES_LIST'):
                d2 = d[i]
                break
        if (type(d2) != dict) or (not 'MDATTR' in d2.keys()):
            break
        d2 = d2['MDATTR']
        if type(d2) != list or len(d2) != len(d3):
            break
        offsets = []
        for i in range(len(d2)):
            if (type(d2[i]) == dict) and ('@name' in d2[i]) and (d2[i]['@name'] == 'BOA_ADD_OFFSET') and ('#text' in d2[i]):
                offsets.append(eval(d2[i]['#text']))
            else:
                break
        if len(offsets) != len(d2):
            offsets = None
            break
        break
    return bands,factor,offsets

# Read BND_NAME
tif_tags = {}
with tifffile.TiffFile(args.inp_fnam) as tif:
    for tag in tif.pages[0].tags.values():
        name,value = tag.name,tag.value
        tif_tags[name] = value
if not '65000' in tif_tags:
    raise ValueError('Error in finding 65000 >>> {}'.format(args.inp_fnam))
meta = xmltodict.parse(tif_tags['65000'])
src_band,no_data = get_band(meta)
if src_band is None:
    raise ValueError('Error in finding band name >>> {}'.format(args.inp_fnam))

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
src_meta.update(tif_tags)
src_data = ds.ReadAsArray().reshape((src_nb,src_ny,src_nx))
band = ds.GetRasterBand(1)
src_dtype = band.DataType
src_nodata = band.GetNoDataValue()
ds = None

# Replace no_data
replace_no_data = False
if args.replace_no_data:
    if no_data is None:
        raise ValueError('Error, no_data={} >>> {}'.format(no_data,args.inp_fnam))
    for iband in range(src_nb):
        if not np.isnan(no_data[iband]):
            cnd = (src_data[iband] == no_data[iband])
            src_data[iband,cnd] = np.nan
    src_nodata = np.nan
    replace_no_data = True
src_meta.update({'FlagReplaceNoData':replace_no_data})

# Add offset
add_offset = False
if args.add_offset:
    bands,factor,offsets = get_offset(meta)
    if offsets is not None:
        for i in range(len(offsets)):
            band_name = bands[i]
            if not band_name in src_band:
                if band_name == 'B10':
                    continue
                else:
                    raise ValueError('Error in finding {} >>> {}'.format(band_name,args.inp_fnam))
            iband = src_band.index(band_name)
            src_data[iband] += offsets[i]
        add_offset = True
    if args.date is not None:
        dtim = datetime.strptime(args.date,'%Y%m%d')
        if dtim < D0:
            if add_offset:
                sys.stderr.write('Warning, date={}, add_offset={} >>> {}'.format(args.date,add_offset,args.inp_fnam))
                sys.stderr.flush()
        else:
            if not add_offset:
                raise ValueError('Error, date={}, add_offset={} >>> {}'.format(args.date,add_offset,args.inp_fnam))
src_meta.update({'FlagAddOffset':add_offset})

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
