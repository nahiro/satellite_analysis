#!/usr/bin/env python
import os
import sys
import re
import json
import geopandas as gpd
from glob import glob
from datetime import datetime
import numpy as np
from matplotlib.dates import date2num,num2date
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
DST_PARAMS = ['OBJECTID','Shape_Leng','Shape_Area','geometry']

# Default values
TMIN = '20200216'
TMAX = '20200730'
TREF = '20200501'
DATDIR = os.path.join(HOME,'Work','SATREPS','Transplanting_date','Bojongsoang','final','v1.0')
BSC_MIN_MAX = -18.0 # dB
POST_S_MIN = 2.2 # dB
DET_NMIN = 3
OFFSET = 0.0 # day

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-D','--datdir',default=DATDIR,help='Input data directory (%(default)s)')
parser.add_argument('-O','--dst_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tref',default=TREF,help='Reference date in the format YYYYMMDD (%(default)s)')
parser.add_argument('--bsc_min_max',default=BSC_MIN_MAX,type=float,help='Max bsc_min in dB (%(default)s)')
parser.add_argument('--post_s_min',default=POST_S_MIN,type=float,help='Min post_s in dB (%(default)s)')
parser.add_argument('--det_nmin',default=DET_NMIN,type=int,help='Min number of detections (%(default)s)')
parser.add_argument('--offset',default=OFFSET,type=float,help='Transplanting date offset in day (%(default)s)')
args = parser.parse_args()
if args.dst_fnam is None:
    raise ValueError('Error, args.dst_fnam={}'.format(args.dst_fnam))

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
dref = datetime.strptime(args.tref,'%Y%m%d')
nmin = date2num(dmin)
nmax = date2num(dmax)
trans_ref = date2num(dref)
years = np.arange(dmin.year,dmax.year+2,1)

tmins = []
tmaxs = []
dstrs = []
src_data = []
nobject = None
params = ['trans_d1','bsc_min1','fp_offs1','post_s1','fpi_1']
for d in sorted(os.listdir(args.datdir)):
    dnam = os.path.join(args.datdir,d)
    if not os.path.isdir(dnam):
        continue
    m = re.search('^('+'\d'*8+')$',d)
    if not m:
        continue
    dstr = m.group(1)
    fnams = glob(os.path.join(dnam,'*_{}_*.shp'.format(dstr)))
    gnams = glob(os.path.join(dnam,'*_{}_*.json'.format(dstr)))
    if len(fnams) < 1 or len(gnams) < 1:
        continue
    if len(fnams) != 1 or len(gnams) != 1:
        raise ValueError('Error, len(fnams)={}, len(gnams)={} >>> {}'.format(len(fnams),len(gnams),dstr))
    #print(dstr)
    data = gpd.read_file(fnams[0])
    with open(gnams[0],'r') as fp:
        data_info = json.load(fp)
    if nobject is None:
        nobject = len(data)
    elif len(data) != nobject:
        raise ValueError('Error, len(data)={}, nobject={} >>> {}'.format(len(data),nobject,fnams[0]))
    columns = data.columns.str.strip()
    for param in params:
        if not param in columns:
            raise ValueError('Error in finding {} >>> {}'.format(param,fnams[0]))
    #t = datetime.strptime(dstr,'%Y%m%d')
    tmin = datetime.strptime(data_info['tmin'],'%Y%m%d')
    tmax = datetime.strptime(data_info['tmax'],'%Y%m%d')
    tofs = data_info['offset']
    if np.abs(tofs-args.offset) > 1.0e-6:
        raise ValueError('Error, tofs={}, args.offset={}'.format(tofs,args.offset))
    if tmin < dmax and tmax > dmin:
        sys.stderr.write('{} : {:%Y%m%d} -- {:%Y%m%d}\n'.format(dstr,tmin,tmax))
        tmins.append(tmin)
        tmaxs.append(tmax)
        dstrs.append(dstr)
        src_data.append(data[params].to_numpy())
tmins = date2num(np.array(tmins))
tmaxs = date2num(np.array(tmaxs))
tvals = 0.5*(tmins+tmaxs)
dstrs = np.array(dstrs)
src_data = np.array(src_data)
cnd = (src_data[:,:,0] < nmin-1.0e-4) | (src_data[:,:,0] > nmax+1.0e-4)
src_data[:,:,0][cnd] = np.nan
ndat = len(src_data)

dst_meta = {}
dst_meta['tmin'] = '{:%Y%m%d}'.format(dmin)
dst_meta['tmax'] = '{:%Y%m%d}'.format(dmax)
dst_meta['tref'] = '{:%Y%m%d}'.format(dref)
dst_meta['bsc_min_max'] = '{:.1f}'.format(args.bsc_min_max)
dst_meta['post_s_min'] = '{:.1f}'.format(args.post_s_min)
dst_meta['offset'] = '{:.4f}'.format(args.offset)
dst_band = ['trans_d','bsc_min','fp_offs','post_s','fpi','p1_2','p2_2','p3_2','p4_2','p5_2']
dst_data = np.full((len(dst_band),nobject),np.nan)

#flag = False
for iobj in range(nobject):
    #if iobj%100 == 0:
    #    sys.stderr.write('{}/{}\n'.format(iobj,nobject))
    isrt = np.argsort(src_data[:,iobj,0])
    dtmp = src_data[isrt,iobj,:] # trans_d,bsc_min,fp_offs,post_s,fpi
    ttmp = tvals[isrt]
    stmp = dstrs[isrt]
    inds = None
    i0 = 0
    while i0 < ndat:
        if not np.isnan(dtmp[i0,0]):
            inds = [[i0]]
            break
        i0 += 1
    if inds is None:
        continue
    #if i0 != 0:
    #    print(i0)
    for idat in range(i0+1,ndat):
        if np.isnan(dtmp[idat,0]):
            continue
        elif np.abs(dtmp[idat,0]-dtmp[inds[-1][0],0]) > 2.0:
            inds.append([idat])
        else:
            if not all_close(dtmp[idat,1],dtmp[inds[-1][0],1],rtol=0.01,atol=0.02):
                sys.stderr.write('Warning, iobj={:6d}, different bsc_min >>> {}, {} ({}, {})\n'.format(iobj,dtmp[idat,1],dtmp[inds[-1][0],1],stmp[idat],stmp[inds[-1][0]]))
            #if not all_close(dtmp[idat,2],dtmp[inds[-1][0],2],rtol=0.1,atol=5.0):
            #    sys.stderr.write('Warning, iobj={:6d}, different fp_offs >>> {}, {} ({}, {})\n'.format(iobj,dtmp[idat,2],dtmp[inds[-1][0],2],stmp[idat],stmp[inds[-1][0]]))
            #if not all_close(dtmp[idat,3],dtmp[inds[-1][0],3],rtol=0.2,atol=1.0):
            #    sys.stderr.write('Warning, iobj={:6d}, different post_s >>> {}, {} ({}, {})\n'.format(iobj,dtmp[idat,3],dtmp[inds[-1][0],3],stmp[idat],stmp[inds[-1][0]]))
            #if not all_close(dtmp[idat,4],dtmp[inds[-1][0],4],rtol=0.3,atol=0.3):
            #    sys.stderr.write('Warning, iobj={:6d}, different fpi >>> {}, {} ({}, {})\n'.format(iobj,dtmp[idat,4],dtmp[inds[-1][0],4],stmp[idat],stmp[inds[-1][0]]))
            inds[-1].append(idat)
    trans_d = []
    bsc_min = []
    fp_offs = []
    post_s = []
    fpi = []
    for ii in inds:
        if len(ii) < args.det_nmin:
            continue
        d = dtmp[ii]
        t = ttmp[ii]
        trans_d_tmp = np.nanmean(d[:,0])
        dt = np.abs(t-trans_d_tmp)
        itmp = np.argmin(dt)
        if dt[itmp] > 46.5: # 1.5 months
            raise ValueError('Error, dt={}, trans_d={}, t={}'.format(dt[itmp],num2date(trans_d_tmp),num2date(t[itmp])))
        trans_d.append(d[itmp,0])
        bsc_min.append(d[itmp,1])
        fp_offs.append(d[itmp,2])
        post_s.append(d[itmp,3])
        fpi.append(d[itmp,4])
    trans_d = np.array(trans_d)
    bsc_min = np.array(bsc_min)
    fp_offs = np.array(fp_offs)
    post_s = np.array(post_s)
    fpi = np.array(fpi)
    cnd1 = bsc_min < args.bsc_min_max
    cnd2 = post_s > args.post_s_min
    cnd = cnd1 & cnd2
    ncnd = cnd.sum()
    if ncnd < 1:
        continue
    trans_d = trans_d[cnd]
    bsc_min = bsc_min[cnd]
    fp_offs = fp_offs[cnd]
    post_s = post_s[cnd]
    fpi = fpi[cnd]
    while ncnd > 2:
        ind_max = np.argmax(np.abs(trans_d-trans_ref))
        #if ncnd == 3:
        #    sys.stderr.write('Warning, iobj={:6d}, delete index {} >>> {:%Y%m%d}, {:%Y%m%d}, {:%Y%m%d}\n'.format(iobj,ind_max,num2date(trans_d[0]),num2date(trans_d[1]),num2date(trans_d[2])))
        #else:
        #    sys.stderr.write('Warning, iobj={:6d}, delete index {} >>> {:%Y%m%d}\n'.format(iobj,ind_max,num2date(trans_d[ind_max])))
        trans_d = np.delete(trans_d,ind_max)
        bsc_min = np.delete(bsc_min,ind_max)
        fp_offs = np.delete(fp_offs,ind_max)
        post_s = np.delete(post_s,ind_max)
        fpi = np.delete(fpi,ind_max)
        ncnd = trans_d.size
    if ncnd > 1:
        if np.abs(trans_d[1]-trans_ref) < np.abs(trans_d[0]-trans_ref):
            i1 = 1
            i2 = 0
        else:
            i1 = 0
            i2 = 1
        dst_data[0,iobj] = trans_d[i1]
        dst_data[1,iobj] = bsc_min[i1]
        dst_data[2,iobj] = fp_offs[i1]
        dst_data[3,iobj] = post_s[i1]
        dst_data[4,iobj] = fpi[i1]
        dst_data[5,iobj] = trans_d[i2]
        dst_data[6,iobj] = bsc_min[i2]
        dst_data[7,iobj] = fp_offs[i2]
        dst_data[8,iobj] = post_s[i2]
        dst_data[9,iobj] = fpi[i2]
    else:
        dst_data[0,iobj] = trans_d[0]
        dst_data[1,iobj] = bsc_min[0]
        dst_data[2,iobj] = fp_offs[0]
        dst_data[3,iobj] = post_s[0]
        dst_data[4,iobj] = fpi[0]
    #flag = True
    #if flag:
    #    break

out_data = data[DST_PARAMS].copy()
for i,param in enumerate(params):
    out_data[param] = dst_data[i]
out_data.to_file(args.dst_fnam)
"""
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
"""
