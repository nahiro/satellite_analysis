#!/usr/bin/env python
import os
import sys
import numpy as np
from scipy.interpolate import bisplrep,bisplev
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
XTHR = 4.0
YTHR = 4.0
TRG_INDX_STEP = 50
TRG_INDY_STEP = 50
SMOOTH = 1.0e4

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_fnam',default=None,help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('--xthr',default=XTHR,type=float,help='Max difference in X (%(default)s)')
parser.add_argument('--ythr',default=YTHR,type=float,help='Max difference in Y (%(default)s)')
parser.add_argument('-s','--trg_indx_step',default=TRG_INDX_STEP,type=int,help='Target step x index (%(default)s)')
parser.add_argument('-S','--trg_indy_step',default=TRG_INDY_STEP,type=int,help='Target step y index (%(default)s)')
parser.add_argument('--smooth_x',default=SMOOTH,type=float,help='Smoothing factor for X from 0 to 1 (%(default)s)')
parser.add_argument('--smooth_y',default=None,type=float,help='Smoothing factor for Y from 0 to 1 (%(default)s)')
parser.add_argument('-r','--replace',default=False,action='store_true',help='Replace mode (%(default)s)')
parser.add_argument('-e','--exp',default=False,action='store_true',help='Output in exp format (%(default)s)')
parser.add_argument('--long',default=False,action='store_true',help='Output in long format (%(default)s)')
parser.add_argument('-v','--verbose',default=False,action='store_true',help='Verbose mode (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
args = parser.parse_args()
if args.inp_fnam is None:
    raise ValueError('Error, args.inp_fnam={} >>> {}'.format(args.inp_fnam,sys.argv[0]))
if args.out_fnam is None:
    args.out_fnam = '{}_selected.dat'.format(os.path.splitext(args.inp_fnam)[0])
if args.smooth_y is None:
    args.smooth_y = args.smooth_x

xc,yc,xp,yp,xd,yd,rr,r90 = np.loadtxt(fnam,unpack=True)
xc_uniq = np.unique(xc)
yc_uniq = np.unique(yc)
xi = xc.astype(np.int32)
yi = yc.astype(np.int32)
xi_uniq = np.unique(xi)
yi_uniq = np.unique(yi)
xi_uniq_step = np.diff(xi_uniq).min()
yi_uniq_step = np.diff(yi_uniq).min()
xc_offset = xc_uniq[0]-xi_uniq[0]
yc_offset = yc_uniq[0]-yi_uniq[0]
if not np.all(xc_uniq[1:]-xi_uniq[1:] == xc_offset):
    raise ValueError('Error, different xc offset >>> {}'.format(fnam))
if not np.all(yc_uniq[1:]-yi_uniq[1:] == yc_offset):
    raise ValueError('Error, different yc offset >>> {}'.format(fnam))
xmin = xi.min()
xmax = xi.max()
xstp = args.trg_indx_step
if xstp != xi_uniq_step:
    sys.stderr.write('Warning, xstp={}, xi_uniq_step={} >>> {}\n'.format(xstp,xi_uniq_step,fnam))
ymin = yi.min()
ymax = yi.max()
ystp = args.trg_indy_step
if ystp != yi_uniq_step:
    sys.stderr.write('Warning, ystp={}, yi_uniq_step={} >>> {}\n'.format(ystp,yi_uniq_step,fnam))
xg,yg = np.meshgrid(np.arange(xmin,xmax+1,xstp),np.arange(ymin,ymax+1,ystp))
indx = (xi-xmin)//xstp
indy = (yi-ymin)//ystp
xc_grid = np.full(xg.shape,np.nan)
yc_grid = np.full(yg.shape,np.nan)
xp_grid = np.full(xg.shape,np.nan)
yp_grid = np.full(yg.shape,np.nan)
xd_grid = np.full(xg.shape,np.nan)
yd_grid = np.full(yg.shape,np.nan)
rr_grid = np.full(xg.shape,np.nan)
r90_grid = np.full(xg.shape,np.nan)
xc_grid[indy,indx] = xc
yc_grid[indy,indx] = yc
xp_grid[indy,indx] = xp
yp_grid[indy,indx] = yp
xd_grid[indy,indx] = xd
yd_grid[indy,indx] = yd
rr_grid[indy,indx] = rr
r90_grid[indy,indx] = r90

xs_grid = np.full(xg.shape,np.nan)
ys_grid = np.full(yg.shape,np.nan)
xs_grid[:] = bisplev(np.arange(xg.shape[0]),np.arange(xg.shape[1]),bisplrep(indy,indx,xd,s=args.smooth_x))
ys_grid[:] = bisplev(np.arange(yg.shape[0]),np.arange(yg.shape[1]),bisplrep(indy,indx,yd,s=args.smooth_y))
cnd = np.isnan(xd_grid)
xs_grid[cnd] = np.nan
cnd = np.isnan(yd_grid)
ys_grid[cnd] = np.nan

xr_grid = xd_grid-xs_grid
yr_grid = yd_grid-ys_grid

with open(args.out_fnam,'w') as fp:
    for ix,iy in zip(indx,indy):
        if (np.abs(xr_grid[iy,ix]) > args.xthr) or (np.abs(yr_grid[iy,ix]) > args.ythr):
            continue
        if args.replace:
            xp_out = xp_grid[iy,ix]-xd_grid[iy,ix]+xs_grid[iy,ix]
            yp_out = yp_grid[iy,ix]-yd_grid[iy,ix]+ys_grid[iy,ix]
            xd_out = xs_grid[iy,ix]
            yd_out = ys_grid[iy,ix]
        else:
            xp_out = xp_grid[iy,ix]
            yp_out = yp_grid[iy,ix]
            xd_out = xd_grid[iy,ix]
            yd_out = yd_grid[iy,ix]
        if args.exp:
            line = '{:8.1f} {:8.1f} {:15.8e} {:15.8e} {:15.8e} {:15.8e} {:8.3f} {:8.3f}\n'.format(xc_grid[iy,ix],yc_grid[iy,ix],xp_out,yp_out,xd_out,yd_out,rr_grid[iy,ix],r90_grid[iy,ix])
        elif args.long:
            line = '{:8.1f} {:8.1f} {:12.6f} {:12.6f} {:10.6f} {:10.6f} {:10.5f} {:10.5f}\n'.format(xc_grid[iy,ix],yc_grid[iy,ix],xp_out,yp_out,xd_out,yd_out,rr_grid[iy,ix],r90_grid[iy,ix])
        else:
            line = '{:8.1f} {:8.1f} {:8.2f} {:8.2f} {:6.2f} {:6.2f} {:8.3f} {:8.3f}\n'.format(xc_grid[iy,ix],yc_grid[iy,ix],xp_out,yp_out,xd_out,yd_out,rr_grid[iy,ix],r90_grid[iy,ix])
        fp.write(line)
        if args.verbose:
            sys.stdout.write(line)
