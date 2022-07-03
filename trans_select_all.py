#!/usr/bin/env python
import os
import sys
import re
import json
import gdal
import osr
from datetime import datetime
import numpy as np
from matplotlib.dates import date2num,num2date
from optparse import OptionParser,IndentedHelpFormatter

# Default values
TMIN = '20200216'
TMAX = '20200730'
DATDIR = '/home/naohiro/Work/SATREPS/Transplanting_date/Cihea/final/v1.4'
MASK_FNAM = '/home/naohiro/Work/SATREPS/Transplanting_date/Cihea/paddy_mask.tif'
PERIOD_NUM = 0

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('-s','--tmin',default=TMIN,help='Min date of transplanting in the format YYYYMMDD (%default)')
parser.add_option('-e','--tmax',default=TMAX,help='Max date of transplanting in the format YYYYMMDD (%default)')
parser.add_option('-D','--datdir',default=DATDIR,help='Input data directory (%default)')
parser.add_option('--mask_fnam',default=MASK_FNAM,help='Mask file name (%default)')
parser.add_option('-f','--period_fnam',default=None,help='Period file name (%default)')
parser.add_option('-i','--period_num',default=PERIOD_NUM,type='int',help='Period number from 1 to 3 (%default)')
(opts,args) = parser.parse_args()

def all_close(a,b,rtol=0.01,atol=1.0):
    dif = np.abs(a-b)
    avg = 0.5*(np.abs(a)+np.abs(b))
    cnd1 = np.all(dif < avg*rtol)
    cnd2 = np.all(dif < atol)
    if cnd1 or  cnd2:
        return True
    else:
        sys.stderr.write('{} {}\n'.format(dif/avg,dif))
        return False

if opts.period_fnam is not None:
    lines = []
    with open(opts.period_fnam,'r') as fp:
        lines = fp.readlines()
    if len(lines) < opts.period_num+1:
        raise ValueError('Error, len(lines)={}, period_num={}'.format(len(lines),opts.period_num))
    m = re.search('period{}'.format(opts.period_num)+'\s*:\s*('+'\d'*8+')\s+('+'\d'*8+')\s*$',lines[opts.period_num])
    if not m:
        raise ValueError('Error in reading period {} >>> '.format(opts.period_num)+lines[opts.period_num])
    opts.tmin = m.group(1)
    opts.tmax = m.group(2)

dmin = datetime.strptime(opts.tmin,'%Y%m%d')
dmax = datetime.strptime(opts.tmax,'%Y%m%d')
nmin = date2num(dmin)
nmax = date2num(dmax)

bsc_min_max = -13.0
post_avg_min = 0.0
offset = -9.0 # day
rthr = 0.02

ds = gdal.Open(opts.mask_fnam)
mask = ds.ReadAsArray()
mask_shape = mask.shape
ds = None

stat_fnam = 'avg_{:%Y%m%d}_{:%Y%m%d}.tif'.format(dmin,dmax)
ds = gdal.Open(stat_fnam)
dsta = ds.ReadAsArray()
if dsta[0].shape != mask_shape:
    raise ValueError('Error, dsta[0].shape={}, mask_shape={}'.format(dsta[0].shape,mask_shape))
dsta_meta = ds.GetMetadata()
ds = None
dsta_tmin = dsta_meta['tmin']
dsta_tmax = dsta_meta['tmax']
if dsta_tmin != dmin.strftime('%Y%m%d') or dsta_tmax != dmax.strftime('%Y%m%d'):
    raise ValueError('Error, dsta_tmin={}, dsta_tmax={}, dmin={:%Y%m%d}, dmax={:%Y%m%d}'.format(dsta_tmin,dsta_tmax,dmin,dmax))

gnams = []
tmins = []
tmaxs = []
dstrs = []
for d in sorted(os.listdir(opts.datdir)):
    m = re.search('^('+'\d'*8+')$',d)
    if not m:
        continue
    dstr = m.group(1)
    fnam = os.path.join(opts.datdir,d,'trans_date_cihea_{}_final.json'.format(dstr))
    gnam = os.path.join(opts.datdir,d,'trans_date_cihea_{}_final.tif'.format(dstr))
    if not os.path.exists(fnam) or not os.path.exists(gnam):
        continue
    #print(dstr)
    with open(fnam,'r') as fp:
        data_info = json.load(fp)
    #t = datetime.strptime(dstr,'%Y%m%d')
    tmin = datetime.strptime(data_info['tmin'],'%Y%m%d')
    tmax = datetime.strptime(data_info['tmax'],'%Y%m%d')
    if tmin < dmax and tmax > dmin:
        print(tmin,tmax)
        gnams.append(gnam)
        tmins.append(tmin)
        tmaxs.append(tmax)
        dstrs.append(dstr)
tmins = date2num(np.array(tmins))
tmaxs = date2num(np.array(tmaxs))
tvals = 0.5*(tmins+tmaxs)
dstrs = np.array(dstrs)

data_shape = None
data_trans = None
data_epsg = None
data = []
for gnam in gnams:
    ds = gdal.Open(gnam)
    dtmp = ds.ReadAsArray()
    if data_shape is None:
        data_shape = dtmp[0].shape
        if data_shape != mask_shape:
            raise ValueError('Error, data_shape={}, mask_shape={}'.format(data_shape,mask_shape))
    elif dtmp[0].shape != data_shape:
        raise ValueError('Error, dtmp[0].shape={}, data_shape={}'.format(dtmp[0].shape,data_shape))
    if data_trans is None:
        data_trans = ds.GetGeoTransform()
    elif ds.GetGeoTransform() != data_trans:
        raise ValueError('Error, different transform')
    prj = ds.GetProjection()
    srs = osr.SpatialReference(wkt=prj)
    estr = srs.GetAttrValue('AUTHORITY',1)
    if re.search('\D',estr):
        raise ValueError('Error in EPSG >>> '+estr)
    epsg = int(estr)
    if data_epsg is None:
        data_epsg = epsg
    elif epsg != data_epsg:
        raise ValueError('Error, epsg={}, data_epsg={}'.format(epsg,data_epsg))
    data.append(dtmp)
data = np.array(data)
ndat = len(data)
nx = data_shape[1]
ny = data_shape[0]
nb = 8*2
output_data = np.full((nb,ny,nx),np.nan)
cnd = (data[:,0,:,:] < nmin-1.0e-4) | (data[:,0,:,:] > nmax+1.0e-4)
data[:,0,:,:][cnd] = np.nan

flag = False
for iy in range(data_shape[0]):
    if iy%100 == 0:
        sys.stderr.write('{}/{}\n'.format(iy,data_shape[0]))
    for ix in range(data_shape[1]):
        #if mask[iy,ix] < 0.5:
        #    continue
        if np.isnan(dsta[0,iy,ix]) or dsta[4,iy,ix] < rthr:
            continue
        isrt = np.argsort(data[:,0,iy,ix])
        dtmp = data[isrt,:,iy,ix] # trans_d,trans_s,trans_n,bsc_min,post_avg,post_min,post_max,reserved
        ttmp = tvals[isrt]
        stmp = dstrs[isrt]
        inds = None
        i0 = 0
        while i0 < len(data):
            if not np.isnan(dtmp[i0,0]):
                inds = [[i0]]
                break
            i0 += 1
        if inds is None:
            continue
        #if i0 != 0:
        #    print(i0)
        for idat in range(i0+1,len(data)):
            if np.isnan(dtmp[idat,0]):
                continue
            elif np.abs(dtmp[idat,0]-dtmp[inds[-1][0],0]) > 2.0:
                inds.append([idat])
            else:
                """
                if not all_close(dtmp[idat,1],dtmp[inds[-1][0],1],rtol=0.1,atol=1.0):
                    sys.stderr.write('Warning, ix={:6d}, iy={:6d}, different trans_s >>> {}, {} ({}, {})\n'.format(ix,iy,dtmp[idat,1],dtmp[inds[-1][0],1],stmp[idat],stmp[inds[-1][0]]))
                if not all_close(dtmp[idat,2],dtmp[inds[-1][0],2],rtol=0.1,atol=1.0):
                    sys.stderr.write('Warning, ix={:6d}, iy={:6d}, different trans_n >>> {}, {} ({}, {})\n'.format(ix,iy,dtmp[idat,2],dtmp[inds[-1][0],2],stmp[idat],stmp[inds[-1][0]]))
                if not all_close(dtmp[idat,3],dtmp[inds[-1][0],3],rtol=0.01,atol=0.02):
                    sys.stderr.write('Warning, ix={:6d}, iy={:6d}, different bsc_min >>> {}, {} ({}, {})\n'.format(ix,iy,dtmp[idat,3],dtmp[inds[-1][0],3],stmp[idat],stmp[inds[-1][0]]))
                if not all_close(dtmp[idat,4],dtmp[inds[-1][0],4],rtol=0.01,atol=0.02):
                    sys.stderr.write('Warning, ix={:6d}, iy={:6d}, different post_avg >>> {}, {} ({}, {})\n'.format(ix,iy,dtmp[idat,4],dtmp[inds[-1][0],4],stmp[idat],stmp[inds[-1][0]]))
                if not all_close(dtmp[idat,5],dtmp[inds[-1][0],5],rtol=0.01,atol=0.02):
                    sys.stderr.write('Warning, ix={:6d}, iy={:6d}, different post_min >>> {}, {} ({}, {})\n'.format(ix,iy,dtmp[idat,5],dtmp[inds[-1][0],5],stmp[idat],stmp[inds[-1][0]]))
                if not all_close(dtmp[idat,6],dtmp[inds[-1][0],6],rtol=0.01,atol=0.02):
                    sys.stderr.write('Warning, ix={:6d}, iy={:6d}, different post_max >>> {}, {} ({}, {})\n'.format(ix,iy,dtmp[idat,6],dtmp[inds[-1][0],6],stmp[idat],stmp[inds[-1][0]]))
                """
                inds[-1].append(idat)
        tvals_d = []
        trans_d = []
        trans_s = []
        trans_n = []
        bsc_min = []
        post_avg = []
        post_min = []
        post_max = []
        risetime = []
        for ii in inds:
            d = dtmp[ii]
            t = ttmp[ii]
            trans_d_tmp = np.nanmean(d[:,0])
            dt = np.abs(t-trans_d_tmp)
            itmp = np.argmin(dt)
            if dt[itmp] > 46.5: # 1.5 months
                raise ValueError('Error, dt={}, trans_d={}, t={}'.format(dt[itmp],num2date(trans_d_tmp),num2date(t[itmp])))
            tvals_d.append(t)
            trans_d.append(d[itmp,0])
            trans_s.append(d[itmp,1])
            trans_n.append(d[itmp,2])
            bsc_min.append(d[itmp,3])
            post_avg.append(d[itmp,4])
            post_min.append(d[itmp,5])
            post_max.append(d[itmp,6])
            risetime.append(d[itmp,7])
        tvals_d = np.array(tvals_d,dtype='object')
        trans_d = np.array(trans_d)
        trans_s = np.array(trans_s)
        trans_n = np.array(trans_n)
        bsc_min = np.array(bsc_min)
        post_avg = np.array(post_avg)
        post_min = np.array(post_min)
        post_max = np.array(post_max)
        risetime = np.array(risetime)
        #cnd1 = np.abs(trans_n-trans_d) < trans_n_max
        cnd2 = bsc_min < bsc_min_max
        #cnd3 = post_min > post_min_min
        cnd4 = post_avg > post_avg_min
        #cnd5 = risetime < risetime_max
        #cnd = cnd1 & cnd2 & cnd3 & cnd4 & cnd5
        cnd = cnd2 & cnd4
        ncnd = cnd.sum()
        if ncnd < 1:
            continue
        tvals_d = tvals_d[cnd]
        trans_d = trans_d[cnd]
        trans_s = trans_s[cnd]
        trans_n = trans_n[cnd]
        bsc_min = bsc_min[cnd]
        post_avg = post_avg[cnd]
        post_min = post_min[cnd]
        post_max = post_max[cnd]
        risetime = risetime[cnd]
        dt = np.abs(trans_d-dsta[0,iy,ix])
        cnd = dt < 30.1
        ncnd = cnd.sum()
        if ncnd < 1:
            continue
        tvals_d = tvals_d[cnd]
        trans_d = trans_d[cnd]
        trans_s = trans_s[cnd]
        trans_n = trans_n[cnd]
        bsc_min = bsc_min[cnd]
        post_avg = post_avg[cnd]
        post_min = post_min[cnd]
        post_max = post_max[cnd]
        risetime = risetime[cnd]
        dt = []
        for tv in tvals_d:
            dt.append(np.nanmin(np.abs(tv-dsta[0,iy,ix])))
        dt = np.array(dt)
        isrt = np.argsort(dt)
        if ncnd > 1:
            i1 = isrt[0]
            i2 = isrt[1]
            output_data[0,iy,ix] = trans_d[i1]
            output_data[1,iy,ix] = trans_s[i1]
            output_data[2,iy,ix] = trans_n[i1]
            output_data[3,iy,ix] = bsc_min[i1]
            output_data[4,iy,ix] = post_avg[i1]
            output_data[5,iy,ix] = post_min[i1]
            output_data[6,iy,ix] = post_max[i1]
            output_data[7,iy,ix] = risetime[i1]
            output_data[8,iy,ix] = trans_d[i2]
            output_data[9,iy,ix] = trans_s[i2]
            output_data[10,iy,ix] = trans_n[i2]
            output_data[11,iy,ix] = bsc_min[i2]
            output_data[12,iy,ix] = post_avg[i2]
            output_data[13,iy,ix] = post_min[i2]
            output_data[14,iy,ix] = post_max[i2]
            output_data[15,iy,ix] = risetime[i2]
        else:
            i1 = isrt[0]
            output_data[0,iy,ix] = trans_d[0]
            output_data[1,iy,ix] = trans_s[0]
            output_data[2,iy,ix] = trans_n[0]
            output_data[3,iy,ix] = bsc_min[0]
            output_data[4,iy,ix] = post_avg[0]
            output_data[5,iy,ix] = post_min[0]
            output_data[6,iy,ix] = post_max[0]
            output_data[7,iy,ix] = risetime[0]
        #flag = True
        #if flag:
        #    break
    #if flag:
    #    break

comments = {}
comments['tmin'] = '{:%Y%m%d}'.format(dmin)
comments['tmax'] = '{:%Y%m%d}'.format(dmax)
comments['bsc_min_max'] = '{:.1f}'.format(bsc_min_max)
comments['post_avg_min'] = '{:.1f}'.format(post_avg_min)
comments['offset'] = '{:.4f}'.format(offset)
out_fnam = 'all_{:%Y%m%d}_{:%Y%m%d}.tif'.format(dmin,dmax)
drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(out_fnam,nx,ny,nb,gdal.GDT_Float32)
ds.SetGeoTransform(data_trans)
srs = osr.SpatialReference()
srs.ImportFromEPSG(data_epsg)
ds.SetProjection(srs.ExportToWkt())
ds.SetMetadata(comments)
band_name = ['trans_d','trans_s','trans_n','bsc_min','post_avg','post_min','post_max','risetime','p1_2','p2_2','p3_2','p4_2','p5_2','p6_2','p7_2','p8_2']
for i in range(nb):
    band = ds.GetRasterBand(i+1)
    band.WriteArray(output_data[i])
    band.SetDescription(band_name[i])
band.SetNoDataValue(np.nan) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
