#!/usr/bin/env python
import os
import sys
import re
import json
try:
    import gdal
except Exception:
    from osgeo import gdal
try:
    import osr
except Exception:
    from osgeo import osr
from datetime import datetime
import numpy as np
from matplotlib.dates import date2num,num2date
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')

# Default values
TMIN = '20200216'
TMAX = '20200730'
DATDIR = os.path.join(HOME,'Work','Sentinel-1_Analysis','planting')
MASK_FNAM = os.path.join(HOME,'Work','Sentinel-1_Analysis','paddy_mask.tif')
STAT_FNAM = os.path.join(HOME,'Work','Sentinel-1_Analysis','stat.tif')
BSC_MIN_MAX = -13.0 # dB
POST_AVG_MIN = 0.0 # dB
OFFSET = -9.0 # day
RTHR = 0.02

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-s','--tmin',default=TMIN,help='Min date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-D','--datdir',default=DATDIR,help='Input data directory (%(default)s)')
parser.add_argument('--mask_fnam',default=MASK_FNAM,help='Mask file name (%(default)s)')
parser.add_argument('--stat_fnam',default=STAT_FNAM,help='Stat file name (%(default)s)')
parser.add_argument('--bsc_min_max',default=BSC_MIN_MAX,type=float,help='Max bsc_min in dB (%(default)s)')
parser.add_argument('--post_avg_min',default=POST_AVG_MIN,type=float,help='Min post_avg in dB (%(default)s)')
parser.add_argument('--offset',default=OFFSET,type=float,help='Transplanting date offset in day (%(default)s)')
parser.add_argument('--rthr',default=RTHR,type=float,help='Min reference density (%(default)s)')
args = parser.parse_args()

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

dmin = datetime.strptime(args.tmin,'%Y%m%d')
dmax = datetime.strptime(args.tmax,'%Y%m%d')
nmin = date2num(dmin)
nmax = date2num(dmax)

ds = gdal.Open(args.mask_fnam)
mask_nx = ds.RasterXSize
mask_ny = ds.RasterYSize
mask_nb = ds.RasterCount
if mask_nb != 1:
    raise ValueError('Error, mask_nb={}'.format(mask_nb))
mask_shape = (mask_ny,mask_nx)
mask_data = ds.ReadAsArray().reshape(mask_shape)
ds = None

ds = gdal.Open(args.stat_fnam)
stat_nx = ds.RasterXSize
stat_ny = ds.RasterYSize
stat_nb = ds.RasterCount
stat_shape = (stat_ny,stat_nx)
if stat_shape != mask_shape:
    raise ValueError('Error, stat_shape={}, mask_shape={}'.format(stat_shape,mask_shape))
stat_meta = ds.GetMetadata()
stat_data = ds.ReadAsArray()
ds = None
stat_tmin = stat_meta['tmin']
stat_tmax = stat_meta['tmax']
if stat_tmin != dmin.strftime('%Y%m%d') or stat_tmax != dmax.strftime('%Y%m%d'):
    raise ValueError('Error, stat_tmin={}, stat_tmax={}, dmin={:%Y%m%d}, dmax={:%Y%m%d}'.format(stat_tmin,stat_tmax,dmin,dmax))

fnams = []
tmins = []
tmaxs = []
dstrs = []
for year in years:
    ystr = '{}'.format(year)
    dnam = os.path.join(args.datdir,ystr)
    if not os.path.isdir(dnam):
        continue
    for f in sorted(os.listdir(dnam)):
        m = re.search('^(\S+)_('+'\d'*8+')_final.tif$',f)
        if not m:
            continue
        bnam = m.group(1)
        dstr = m.group(2)
        fnam = os.path.join(args.datdir,dnam,f)
        gnam = os.path.join(args.datdir,dnam,'{}_{}_final.json'.format(bnam,dstr))
        if not os.path.exists(gnam):
            continue
        #print(dstr)
        with open(gnam,'r') as fp:
            data_info = json.load(fp)
        #t = datetime.strptime(dstr,'%Y%m%d')
        tmin = datetime.strptime(data_info['tmin'],'%Y%m%d')
        tmax = datetime.strptime(data_info['tmax'],'%Y%m%d')
        tofs = data_info['offset']
        if np.abs(tofs-args.offset) > 1.0e-6:
            raise ValueError('Error, tofs={}, args.offset={}'.format(tofs,args.offset))
        if tmin < dmax and tmax > dmin:
            sys.stderr.write('{} {}\n'.format(tmin,tmax))
            fnams.append(fnam)
            tmins.append(tmin)
            tmaxs.append(tmax)
            dstrs.append(dstr)
tmins = date2num(np.array(tmins))
tmaxs = date2num(np.array(tmaxs))
tvals = 0.5*(tmins+tmaxs)
dstrs = np.array(dstrs)

src_nx = None
src_ny = None
src_nb = None
src_shape = None
src_prj = None
src_trans = None
src_data = []
for fnam in fnams:
    ds = gdal.Open(fnam)
    tmp_nx = ds.RasterXSize
    tmp_ny = ds.RasterYSize
    tmp_nb = ds.RasterCount
    tmp_shape = (tmp_ny,tmp_nx)
    tmp_prj = ds.GetProjection()
    tmp_trans = ds.GetGeoTransform()
    tmp_data = ds.ReadAsArray()
    if src_shape is None:
        src_shape = tmp_shape
        if src_shape != mask_shape:
            raise ValueError('Error, src_shape={}, mask_shape={}'.format(src_shape,mask_shape))
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
    src_data.append(tmp_data)
src_data = np.array(src_data)
cnd = (src_data[:,0,:,:] < nmin-1.0e-4) | (src_data[:,0,:,:] > nmax+1.0e-4)
src_data[:,0,:,:][cnd] = np.nan

dst_nx = src_nx
dst_ny = src_ny
dst_nb = 8*2
dst_prj = src_prj
dst_trans = src_trans
dst_meta = {}
dst_meta['tmin'] = '{:%Y%m%d}'.format(dmin)
dst_meta['tmax'] = '{:%Y%m%d}'.format(dmax)
dst_meta['bsc_min_max'] = '{:.1f}'.format(bsc_min_max)
dst_meta['post_avg_min'] = '{:.1f}'.format(post_avg_min)
dst_meta['offset'] = '{:.4f}'.format(offset)
dst_data = np.full((dst_nb,dst_ny,dst_nx),np.nan)
dst_band = ['trans_d','trans_s','trans_n','bsc_min','post_avg','post_min','post_max','risetime','p1_2','p2_2','p3_2','p4_2','p5_2','p6_2','p7_2','p8_2']

flag = False
for iy in range(src_ny):
    #if iy%100 == 0:
    #    sys.stderr.write('{}/{}\n'.format(iy,src_ny))
    for ix in range(src_nx):
        #if mask[iy,ix] < 0.5:
        #    continue
        if np.isnan(dsta[0,iy,ix]) or dsta[4,iy,ix] < rthr:
            continue
        isrt = np.argsort(data[:,0,iy,ix])
        dtmp = src_data[isrt,:,iy,ix] # trans_d,trans_s,trans_n,bsc_min,post_avg,post_min,post_max,reserved
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
            dst_data[0,iy,ix] = trans_d[i1]
            dst_data[1,iy,ix] = trans_s[i1]
            dst_data[2,iy,ix] = trans_n[i1]
            dst_data[3,iy,ix] = bsc_min[i1]
            dst_data[4,iy,ix] = post_avg[i1]
            dst_data[5,iy,ix] = post_min[i1]
            dst_data[6,iy,ix] = post_max[i1]
            dst_data[7,iy,ix] = risetime[i1]
            dst_data[8,iy,ix] = trans_d[i2]
            dst_data[9,iy,ix] = trans_s[i2]
            dst_data[10,iy,ix] = trans_n[i2]
            dst_data[11,iy,ix] = bsc_min[i2]
            dst_data[12,iy,ix] = post_avg[i2]
            dst_data[13,iy,ix] = post_min[i2]
            dst_data[14,iy,ix] = post_max[i2]
            dst_data[15,iy,ix] = risetime[i2]
        else:
            i1 = isrt[0]
            dst_data[0,iy,ix] = trans_d[0]
            dst_data[1,iy,ix] = trans_s[0]
            dst_data[2,iy,ix] = trans_n[0]
            dst_data[3,iy,ix] = bsc_min[0]
            dst_data[4,iy,ix] = post_avg[0]
            dst_data[5,iy,ix] = post_min[0]
            dst_data[6,iy,ix] = post_max[0]
            dst_data[7,iy,ix] = risetime[0]
        #flag = True
        #if flag:
        #    break
    #if flag:
    #    break

drv = gdal.GetDriverByName('GTiff')
ds = drv.Create(args.dst_fnam,dst_nx,dst_ny,dst_nb,gdal.GDT_Float32)
ds.SetProjection(dst_prj)
ds.SetGeoTransform(dst_trans)
ds.SetMetadata(dst_meta)
for i in range(dst_nb):
    band = ds.GetRasterBand(i+1)
    band.WriteArray(dst_data[i])
    band.SetDescription(dst_band[i])
band.SetNoDataValue(dst_nodata) # The TIFFTAG_GDAL_NODATA only support one value per dataset
ds.FlushCache()
ds = None # close dataset
