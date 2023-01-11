#!/usr/bin/env python
import os
import sys
import re
import json
import geopandas as gpd
import xmltodict
from glob import glob
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.dates import date2num,num2date,YearLocator,MonthLocator,DayLocator,DateFormatter
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1 import make_axes_locatable
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
PARAMS = ['trans_d#','bsc_min#','fp_offs#','post_s#','fpi_#']
PARAM_NAMES = {'trans_d':'Estimated transplanting date (MM/DD)','bsc_min':'Signal at transplanting (dB)','post_s':'Signal after transplanting (dB)','fpi':'Fishpond Index at transplanting'}
PARAM_MINS = {'trans_d':np.nan,'bsc_min':-25.0,'post_s':0.0,'fpi':0.0}
PARAM_MAXS = {'trans_d':np.nan,'bsc_min':-10.0,'post_s':5.0,'fpi':1.0}
OUT_PARAMS = ['OBJECTID','Shape_Leng','Shape_Area','geometry']

# Default values
TMIN = '20200216'
TMAX = '20200730'
DATDIR = os.path.join(HOME,'Work','SATREPS','Transplanting_date','Bojongsoang','final','v1.0')
BSC_MIN_MAX = -13.0 # dB
POST_S_MIN = 0.0 # dB
DET_NMIN = 1
REF_RMAX = 500.0 # m
REF_NMAX = 10
REF_DMAX = 30.1 # day
OFFSET = 0.0 # day
REF_NCAN = 1
INP_NCAN = 1

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-R','--ref_fnam',default=None,help='Reference file name (%(default)s)')
parser.add_argument('-D','--datdir',default=DATDIR,help='Input data directory (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-o','--out_shp',default=None,help='Output Shapefile name (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('--bsc_min_max',default=BSC_MIN_MAX,type=float,help='Max bsc_min in dB (%(default)s)')
parser.add_argument('--post_s_min',default=POST_S_MIN,type=float,help='Min post_s in dB (%(default)s)')
parser.add_argument('--det_nmin',default=DET_NMIN,type=int,help='Min number of detections (%(default)s)')
parser.add_argument('--ref_rmax',default=REF_RMAX,type=float,help='Maximum distance from reference in m (%(default)s)')
parser.add_argument('--ref_nmax',default=REF_NMAX,type=int,help='Maximum number of reference (%(default)s)')
parser.add_argument('--ref_dmax',default=REF_DMAX,type=float,help='Maximum difference from reference in day (%(default)s)')
parser.add_argument('--offset',default=OFFSET,type=float,help='Transplanting date offset in day (%(default)s)')
parser.add_argument('--ref_ncan',default=REF_NCAN,type=int,help='Candidate number of reference between 1 and 2, or 0 (%(default)s)')
parser.add_argument('-N','--inp_ncan',default=INP_NCAN,type=int,help='Candidate number of input between 1 and 3 (%(default)s)')
parser.add_argument('-F','--fignam',default=None,help='Output figure name for debug (%(default)s)')
parser.add_argument('-t','--fig_title',default=None,help='Figure title for debug (%(default)s)')
parser.add_argument('--sort_difference',default=False,action='store_true',help='Sort by difference between candidate and references (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
parser.add_argument('-b','--batch',default=False,action='store_true',help='Batch mode (%(default)s)')
args = parser.parse_args()
if args.ref_fnam is None:
    raise ValueError('Error, args.ref_fnam={}'.format(args.ref_fnam))

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

# Read reference
data = gpd.read_file(args.ref_fnam)
columns = data.columns.str.strip()
for param in OUT_PARAMS:
    if not param in columns:
        raise ValueError('Error in finding {} >>> {}'.format(param,args.ref_fnam))
out_data = data[OUT_PARAMS].copy()
nobject = len(data)
if args.use_index:
    object_ids = np.arange(nobject)+1
else:
    object_ids = data['OBJECTID'].to_numpy()
center_x = np.array(data.centroid.x)
center_y = np.array(data.centroid.y)
if args.ref_ncan == 2:
    ref_data = data['p1_2']
else:
    ref_data = np.array(data['trans_d'])
cnd = (ref_data > nmin-1.0e-4) & (ref_data < nmax+1.0e-4)
sel_data = ref_data[cnd]
sel_x = center_x[cnd]
sel_y = center_y[cnd]
if args.ref_ncan == 0:
    ref_data = data['p1_2']
    cnd = (ref_data > nmin-1.0e-4) & (ref_data < nmax+1.0e-4)
    sel_data = np.append(sel_data,ref_data[cnd])
    sel_x = np.append(sel_x,center_x[cnd])
    sel_y = np.append(sel_y,center_y[cnd])

# Read all
tmins = []
tmaxs = []
dstrs = []
src_data = []
params = [param.replace('#','{}'.format(args.inp_ncan)) for param in PARAMS]
nband = len(params)
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
    f = os.path.basename(fnams[0])
    m = re.search('^planting_\D+_(\d\d\d\d\d\d\d\d)_(\d\d\d\d\d\d\d\d)_\d\d\d\d\d\d\d\d_(\d\d\d\d\d\d\d\d)_\D+\.shp$',f)
    if not m:
        raise ValueError('Error in file name >>> {}'.format(fnams[0]))
    t1 = datetime.strptime(m.group(1),'%Y%m%d')
    t2 = datetime.strptime(m.group(2),'%Y%m%d')
    if m.group(3) != dstr:
        raise ValueError('Error in file name, dstr={} >>> {}'.format(dstr,fnams[0]))
    #print(dstr)
    data = gpd.read_file(fnams[0])
    with open(gnams[0],'r') as fp:
        data_info = json.load(fp)
    if len(data) != nobject:
        raise ValueError('Error, len(data)={}, nobject={} >>> {}'.format(len(data),nobject,fnams[0]))
    columns = data.columns.str.strip()
    for param in params:
        if not param in columns:
            raise ValueError('Error in finding {} >>> {}'.format(param,fnams[0]))
    #t = datetime.strptime(dstr,'%Y%m%d')
    tmin = datetime.strptime(data_info['tmin'],'%Y%m%d')
    tmax = datetime.strptime(data_info['tmax'],'%Y%m%d')
    tofs = data_info['offset']
    if tmin != t1 or tmax != t2:
        raise ValueError('Error, tmin={:%Y%m%d}, tmax={:%Y%m%d}, t1={:%Y%m%d}, t2={:%Y%m%d} >>> {}'.format(tmin,tmax,t1,t2,fnams[0]))
    elif np.abs(tofs-args.offset) > 1.0e-6:
        raise ValueError('Error, tofs={}, args.offset={} >>> {}'.format(tofs,args.offset,fnams[0]))
    if tmin < dmax and tmax > dmin:
        sys.stderr.write('{} : {:%Y%m%d} -- {:%Y%m%d}\n'.format(dstr,tmin,tmax))
        tmins.append(tmin)
        tmaxs.append(tmax)
        dstrs.append(dstr)
        src_data.append(data[params].to_numpy())
tmins = date2num(np.array(tmins)) # tmins[ndat]
tmaxs = date2num(np.array(tmaxs)) # tmaxs[ndat]
tvals = 0.5*(tmins+tmaxs) # tvals[ndat]
dstrs = np.array(dstrs) # dstrs[ndat]
src_data = np.array(src_data) # src_data[ndat][nobject][nband]
cnd = (src_data[:,:,0] < nmin-1.0e-4) | (src_data[:,:,0] > nmax+1.0e-4)
src_data[:,:,0][cnd] = np.nan
ndat = len(src_data)

dst_meta = {}
dst_meta['tmin'] = '{:%Y%m%d}'.format(dmin)
dst_meta['tmax'] = '{:%Y%m%d}'.format(dmax)
dst_meta['bsc_min_max'] = '{:.1f}'.format(args.bsc_min_max)
dst_meta['post_s_min'] = '{:.1f}'.format(args.post_s_min)
dst_meta['det_nmin'] = '{}'.format(args.det_nmin)
dst_meta['ref_rmax'] = '{}'.format(args.ref_rmax)
dst_meta['ref_nmax'] = '{}'.format(args.ref_nmax)
dst_meta['ref_dmax'] = '{}'.format(args.ref_dmax)
dst_meta['offset'] = '{:.4f}'.format(args.offset)
dst_meta['sort'] = '{}'.format('difference' if args.sort_difference else 'distance')
dst_band = [param.replace('_#','').replace('#','') for param in PARAMS]+['p{}_2'.format(i+1) for i in range(len(PARAMS))]
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
    # Group candidates
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
    # Remove bad candidates
    cnd1 = (bsc_min < args.bsc_min_max)
    cnd2 = (post_s > args.post_s_min)
    cnd = cnd1 & cnd2
    ncnd = cnd.sum()
    if ncnd < 1:
        continue
    trans_d = trans_d[cnd]
    bsc_min = bsc_min[cnd]
    fp_offs = fp_offs[cnd]
    post_s = post_s[cnd]
    fpi = fpi[cnd]
    # Select candidates close to the reference
    rval2 = np.square(sel_x-center_x[iobj])+np.square(sel_y-center_y[iobj])
    cnd = (rval2 < np.square(args.ref_rmax))
    rcnd = np.sqrt(rval2[cnd])
    indx = np.argsort(rcnd)[:min(args.ref_nmax,rcnd.size)]
    rval = rcnd[indx] # distance between target and references
    cnd_data = (sel_data[cnd])[indx] # trans_d of references
    plot_number = []
    plot_dval = []
    plot_rval = []
    for d in trans_d:
        dval = np.abs(cnd_data-d) # difference between candidate and references
        cnd = (dval < args.ref_dmax)
        dcnd = dval[cnd]
        rcnd = rval[cnd]
        plot_number.append(dcnd.size)
        plot_dval.append(dcnd.sum() if dcnd.size > 0 else np.nan)
        plot_rval.append(rcnd.sum() if dcnd.size > 0 else np.nan)
    plot_number = np.array(plot_number)
    plot_dval = np.array(plot_dval)
    plot_rval = np.array(plot_rval)
    cnd = (plot_number > 0)
    ncnd = cnd.sum()
    if ncnd < 1:
        continue
    trans_d = trans_d[cnd]
    bsc_min = bsc_min[cnd]
    fp_offs = fp_offs[cnd]
    post_s = post_s[cnd]
    fpi = fpi[cnd]
    plot_number = plot_number[cnd]
    plot_dval = plot_dval[cnd]
    plot_rval = plot_rval[cnd]
    if ncnd > 1:
        cnd = (plot_number == plot_number.max())
        ncnd = cnd.sum()
        if ncnd > 1:
            trans_d = trans_d[cnd]
            bsc_min = bsc_min[cnd]
            fp_offs = fp_offs[cnd]
            post_s = post_s[cnd]
            fpi = fpi[cnd]
            plot_number = plot_number[cnd]
            plot_dval = plot_dval[cnd]
            plot_rval = plot_rval[cnd]
            if args.sort_difference:
                indx = np.argsort(plot_dval)
            else:
                indx = np.argsort(plot_rval)
        else:
            indx = np.argsort(plot_number)[::-1]
        i1 = indx[0]
        i2 = indx[1]
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
for i,param in enumerate(dst_band):
    out_data[param] = dst_data[i]

# Output CSV
if args.out_csv is not None:
    with open(args.out_csv,'w') as fp:
        fp.write('{:>8s}'.format('OBJECTID'))
        for param in dst_band:
            fp.write(', {:>13s}'.format(param))
        fp.write('\n')
        for iobj,object_id in enumerate(object_ids):
            fp.write('{:8d}'.format(object_id))
            for param in dst_band:
                fp.write(', {:>13.6e}'.format(out_data[param][iobj]))
            fp.write('\n')

# Output Shapefile
if args.out_shp is not None:
    out_data.to_file(args.out_shp)
    with open('{}.xml'.format(args.out_shp),'w') as fp:
        dst_meta.update({'@xml:lang':'en'})
        fp.write(xmltodict.unparse({'metadata':dst_meta},pretty=True))

if args.debug:
    if not args.batch:
        plt.interactive(True)
    fig = plt.figure(1,facecolor='w',figsize=(7.6,6.0))
    plt.subplots_adjust(top=0.95,bottom=0.06,left=0.030,right=0.96,wspace=0.12,hspace=0.15)
    pdf = PdfPages(args.fignam)
    fig_xmin,fig_ymin,fig_xmax,fig_ymax = out_data.total_bounds
    for ncan in range(2):
        fig.clear()
        # trans_d
        if ncan == 1:
            param = 'p1_2'
        else:
            param = 'trans_d'
        pnam = 'trans_d'
        ax1 = plt.subplot(221)
        ax1.set_xticks([])
        ax1.set_yticks([])
        out_data.plot(column=param,ax=ax1,vmin=nmin,vmax=nmax,cmap=cm.jet)
        im = ax1.imshow(np.arange(4).reshape(2,2),extent=(-2,-1,-2,-1),vmin=nmin,vmax=nmax,cmap=cm.jet)
        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('bottom',size='10%',pad=0.02)
        ax12 = plt.colorbar(im,cax=cax,orientation='horizontal').ax
        ax12.minorticks_on()
        ax12.xaxis.set_major_locator(MonthLocator(bymonth=[1,4,7,10]))
        ax12.xaxis.set_minor_locator(MonthLocator())
        ax12.xaxis.set_major_formatter(DateFormatter('%m/%d'))
        for l in ax12.xaxis.get_ticklabels():
            l.set_rotation(30)
        ax12.set_xlabel('{}'.format(PARAM_NAMES[pnam]))
        ax12.xaxis.set_label_coords(0.5,-3.2)
        ax1.set_xlim(fig_xmin,fig_xmax)
        ax1.set_ylim(fig_ymin,fig_ymax)
        # bsc_min
        if ncan == 1:
            param = 'p2_2'
        else:
            param = 'bsc_min'
        pnam = 'bsc_min'
        ax2 = plt.subplot(222)
        ax2.set_xticks([])
        ax2.set_yticks([])
        out_data.plot(column=param,ax=ax2,vmin=PARAM_MINS[pnam],vmax=PARAM_MAXS[pnam],cmap=cm.jet)
        im = ax2.imshow(np.arange(4).reshape(2,2),extent=(-2,-1,-2,-1),vmin=PARAM_MINS[pnam],vmax=PARAM_MAXS[pnam],cmap=cm.jet)
        divider = make_axes_locatable(ax2)
        cax = divider.append_axes('bottom',size='10%',pad=0.02)
        ax22 = plt.colorbar(im,cax=cax,orientation='horizontal').ax
        ax22.minorticks_on()
        ax22.xaxis.set_major_locator(plt.MultipleLocator(5.0))
        ax22.set_xlabel('{}'.format(PARAM_NAMES[pnam]))
        ax22.xaxis.set_label_coords(0.5,-3.2)
        ax2.set_xlim(fig_xmin,fig_xmax)
        ax2.set_ylim(fig_ymin,fig_ymax)
        # post_s
        if ncan == 1:
            param = 'p4_2'
        else:
            param = 'post_s'
        pnam = 'post_s'
        ax3 = plt.subplot(223)
        ax3.set_xticks([])
        ax3.set_yticks([])
        out_data.plot(column=param,ax=ax3,vmin=PARAM_MINS[pnam],vmax=PARAM_MAXS[pnam],cmap=cm.jet)
        im = ax3.imshow(np.arange(4).reshape(2,2),extent=(-2,-1,-2,-1),vmin=PARAM_MINS[pnam],vmax=PARAM_MAXS[pnam],cmap=cm.jet)
        divider = make_axes_locatable(ax3)
        cax = divider.append_axes('bottom',size='10%',pad=0.02)
        ax32 = plt.colorbar(im,cax=cax,orientation='horizontal').ax
        ax32.minorticks_on()
        ax32.set_xlabel('{}'.format(PARAM_NAMES[pnam]))
        ax32.xaxis.set_label_coords(0.5,-2.2)
        ax3.set_xlim(fig_xmin,fig_xmax)
        ax3.set_ylim(fig_ymin,fig_ymax)
        # fpi
        if ncan == 1:
            param = 'p5_2'
        else:
            param = 'fpi'
        pnam = 'fpi'
        ax4 = plt.subplot(224)
        ax4.set_xticks([])
        ax4.set_yticks([])
        out_data.plot(column=param,ax=ax4,vmin=PARAM_MINS[pnam],vmax=PARAM_MAXS[pnam],cmap=cm.jet)
        im = ax4.imshow(np.arange(4).reshape(2,2),extent=(-2,-1,-2,-1),vmin=PARAM_MINS[pnam],vmax=PARAM_MAXS[pnam],cmap=cm.jet)
        divider = make_axes_locatable(ax4)
        cax = divider.append_axes('bottom',size='10%',pad=0.02)
        ax42 = plt.colorbar(im,cax=cax,orientation='horizontal').ax
        ax42.minorticks_on()
        ax42.set_xlabel('{}'.format(PARAM_NAMES[pnam]))
        ax42.xaxis.set_label_coords(0.5,-2.2)
        ax4.set_xlim(fig_xmin,fig_xmax)
        ax4.set_ylim(fig_ymin,fig_ymax)
        if args.fig_title is not None:
            plt.suptitle('#{}, {}'.format(ncan+1,args.fig_title))
        else:
            plt.suptitle('#{}'.format(ncan+1))
        plt.savefig(pdf,format='pdf')
        if not args.batch:
            plt.draw()
            plt.pause(0.1)
    pdf.close()
