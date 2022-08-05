#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime
import numpy as np
import pandas as pd
from matplotlib.dates import date2num,num2date
from csaps import csaps
import matplotlib.pyplot as plt
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
PARAMS = ['Sb','Sg','Sr','Se1','Se2','Se3','Sn1','Sn2','Ss1','Ss2',
          'Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2',
          'NDVI','GNDVI','RGI','NRGI']

# Default values
TMIN = '20190315'
TMAX = '20190615'
TSTP = 1.0 # day
SMOOTH = 0.01

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('--shp_fnam',default=None,help='Input Shapefile name (%(default)s)')
parser.add_argument('-i','--inp_list',default=None,help='Input file list (%(default)s)')
parser.add_argument('-I','--inp_fnam',default=None,action='append',help='Input file name (%(default)s)')
parser.add_argument('-D','--dstdir',default=None,help='Destination directory (%(default)s)')
parser.add_argument('-s','--tmin',default=TMIN,help='Min date in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tstp',default=TSTP,type=float,help='Time step in day (%(default)s)')
parser.add_argument('-S','--smooth',default=SMOOTH,type=float,help='Smoothing factor from 0 to 1 (%(default)s)')
parser.add_argument('--use_index',default=False,action='store_true',help='Use index instead of OBJECTID (%(default)s)')
args = parser.parse_args()
if args.inp_list is None and args.inp_fnam is None:
    raise ValueError('Error, args.inp_list={}, args.inp_fnam={}'.format(args.inp_list,args.inp_fnam))

# Read data
if args.inp_list is not None:
    fnams = []
    with open(args.inp_list,'r') as fp:
        for line in fp:
            fnam = line.strip()
            if (len(fnam) < 1) or (fnam[0] == '#'):
                continue
            fnams.append(fnam)
else:
    fnams = args.inp_fnam

r = shapefile.Reader(args.shp_fnam)
nobject = len(r)
if args.use_index:
    if np.array_equal(object_ids,np.arange(nobject)+1):
        all_data = out_data
    else:
        if (object_ids[0] < 1) or (object_ids[-1] > nobject):
            raise ValueError('Error, object_ids[0]={}, object_ids[-1]={}, nobject={} >>> {}'.format(object_ids[0],object_ids[-1],nobject,args.mask_geotiff))
        indx = object_ids-1
        all_data = np.full((nobject,src_nb),np.nan)
        all_data[indx] = out_data
else:
    all_ids = []
    for rec in r.iterRecords():
        all_ids.append(rec.OBJECTID)
    if np.array_equal(object_ids,np.array(all_ids)):
        all_data = out_data
    else:
        try:
            indx = np.array([all_ids.index(object_id) for object_id in object_ids])
        except Exception:
            raise ValueError('Error in finding OBJECTID {} in {}'.format(args.shp_fnam))
        all_data = np.full((nobject,src_nb),np.nan)
        all_data[indx] = out_data

params = None
object_ids = None
data = []
dtim = []
for fnam in fnams:
    f = os.path.basename(fnam)
    m = re.search('^('+'\d'*8+')_parcel\.csv$',f)
    if not m:
        raise ValueError('Error in file name >>> {}'.format(f))
    dstr = m.group(1)
    d = datetime.strptime(dstr,'%Y%m%d')
    dtim.append(d)
    df = pd.read_csv(fnam,comment='#')
    df.columns = df.columns.str.strip()
    if params is None:
        params = df.columns
        if params[0].upper() != 'OBJECTID':
            raise ValueError('Error params[0]={} (!= OBJECTID) >>> {}'.format(params[0],fnam))
    elif not np.array_equal(df.columns,params):
        raise ValueError('Error, different columns >>> {}'.format(fnam))
    if object_ids is None:
        object_ids = df.iloc[:,0].astype(int)
    elif not np.array_equal(df.iloc[:,0].astype(int),object_ids):
        raise ValueError('Error, different OBJECTID >>> {}'.format(fnam))
    data.append(df.iloc[:,1:].astype(float))
data = np.array(data).swapaxes(0,1).swapaxes(1,2)
dtim = np.array(dtim)
ntim = date2num(dtim)

#for 
