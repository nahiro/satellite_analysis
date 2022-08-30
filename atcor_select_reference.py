#!/usr/bin/env python
import os
import sys
import re
import zlib # import zlib before gdal to prevent segmentation fault when saving pdf
try:
    import gdal
except Exception:
    from osgeo import gdal
from datetime import datetime
from matplotlib.dates import date2num
import numpy as np
from argparse import ArgumentParser,RawTextHelpFormatter

bands = ['B2','B3','B4','B8','quality_scene_classification']

band_fnam = '/home/naohiro/Source/sentinel/band_names.txt'
band_list = []
with open(band_fnam,'r') as fp:
    for line in fp:
        item = line.split()
        if len(item) != 2:
            raise ValueError('Error, len(item)={}'.format(len(item)))
        band_list.append(item[1])
band_index = [band_list.index(band) for band in bands]

ntim_array = []
b2_array = []
b3_array = []
b4_array = []
b8_array = []
scl_array = []
data_shape = None
datdir = '/home/naohiro/Work/Sentinel-2/L2A/Cihea/resample'
for f in sorted(os.listdir(datdir)):
    m = re.search('(\d+)_geocor_resample.tif',f)
    if not m:
        continue
    dstr = m.group(1)
    print(dstr)
    ntim_array.append(date2num(datetime.strptime(dstr,'%Y%m%d')))
    ds = gdal.Open(os.path.join(datdir,f))
    data = ds.ReadAsArray()
    if len(data) != len(band_list):
        raise ValueError('Error, len(data)={}, len(band_list)={} >>> {}'.format(len(data),len(band_list),f))
    if data_shape is None:
        data_shape = data[0].shape
    elif data[0].shape != data_shape:
        raise ValueError('Error, data_shape={}, data.shape={} >>> {}'.format(data_shape,data.shape,f))
    ds = None
    b2_array.append(data[band_index[0]]*1.0e-4)
    b3_array.append(data[band_index[1]]*1.0e-4)
    b4_array.append(data[band_index[2]]*1.0e-4)
    b8_array.append(data[band_index[3]]*1.0e-4)
    scl_array.append(data[band_index[4]])
    #break
ntim_array = np.array(ntim_array)
b2_array = np.array(b2_array)
b3_array = np.array(b3_array)
b4_array = np.array(b4_array)
b8_array = np.array(b8_array)
scl_array = np.array(scl_array)
np.save('ntim.npy',ntim_array)
np.save('band2.npy',b2_array)
np.save('band3.npy',b3_array)
np.save('band4.npy',b4_array)
np.save('band8.npy',b8_array)
np.save('scl.npy',scl_array)
