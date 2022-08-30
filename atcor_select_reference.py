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


ntim = np.load('ntim.npy')
b2 = np.load('band2.npy')
b3 = np.load('band3.npy')
b4 = np.load('band4.npy')
b8 = np.load('band8.npy')
scl = np.load('scl.npy')
#cnd = (scl < 3.9) | (scl > 7.1)
cnd = (scl < 1.9) | ((scl > 2.1) & (scl < 3.9)) | (scl > 7.1)
b2[cnd] = np.nan
b3[cnd] = np.nan
b4[cnd] = np.nan
b8[cnd] = np.nan
b2_std = np.nanstd(b2.astype(np.float64),axis=0)
b3_std = np.nanstd(b3.astype(np.float64),axis=0)
b4_std = np.nanstd(b4.astype(np.float64),axis=0)
b8_std = np.nanstd(b8.astype(np.float64),axis=0)

c2 = (b2_std < 0.035)# | (b2_std < 0.20*b2_mean)
c3 = (b3_std < 0.035)# | (b3_std < 0.20*b3_mean)
c4 = (b4_std < 0.035)# | (b4_std < 0.20*b4_mean)
c8 = (b8_std < 0.035)# | (b8_std < 0.20*b8_mean)
cnd = c2 & c3 & c4 & c8
inds = np.indices([cnd.size]).reshape(cnd.shape)
np.save('inds_selected.npy',inds[cnd])


n_nearest = 1000

sid,xc,yc,ndat,leng,area = np.loadtxt('get_center.dat',unpack=True)
sid = (sid+0.1).astype(np.int64)
ndat = (ndat+0.1).astype(np.int64)
sid_indx = np.arange(sid.size)

inds = np.load('inds_selected.npy')

ds = gdal.Open('/home/naohiro/Work/Sentinel-2/L2A/Cihea/resample/20210916_geocor_resample.tif')
data = ds.ReadAsArray()
data_trans = ds.GetGeoTransform()
data_shape = data[0].shape
ds = None
indy,indx = np.indices(data_shape)
xp = data_trans[0]+(indx+0.5)*data_trans[1]+(indy+0.5)*data_trans[2]
yp = data_trans[3]+(indx+0.5)*data_trans[4]+(indy+0.5)*data_trans[5]

xq = xp.flatten()[inds]
yq = yp.flatten()[inds]

inds_array = []
leng_array = []
for n in range(sid.size):
    l2 = np.square(xq-xc[n])+np.square(yq-yc[n])
    indx = np.argsort(l2)
    inds_temp = inds[indx[:n_nearest]]
    leng_temp = np.sqrt(l2[indx[:n_nearest]])
    inds_array.append(inds_temp)
    leng_array.append(leng_temp)
inds_array = np.array(inds_array)
leng_array = np.array(leng_array)
np.save('nearest_inds.npy',inds_array)
np.save('nearest_leng.npy',leng_array)
