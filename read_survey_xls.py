#!/usr/bin/env python
import os
import sys
import re
import numpy as np
import pandas as pd
from datetime import datetime
from matplotlib.dates import date2num,num2date
try:
    import gdal
except Exception:
    from osgeo import gdal
import pyproj
from subprocess import call
from io import StringIO
from argparse import ArgumentParser,RawTextHelpFormatter

# Defaults
SHEET = 1
RMAX = 10.0 # m
NMIN = 0.5
EPSG = 32748 # UTM zone 48S

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_fnam',default=None,help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('-S','--sheet',default=SHEET,type=int,help='Sheet number from 1 (%(default)s)')
parser.add_argument('-r','--ref_fnam',default=None,help='CSV file for reference coordinates (%(default)s)')
parser.add_argument('-R','--rmax',default=RMAX,type=float,help='Maximum distance from reference in m (%(default)s)')
parser.add_argument('-n','--nmin',default=NMIN,type=float,help='Minimum ratio of points near the reference (%(default)s)')
parser.add_argument('-E','--epsg',default=EPSG,help='Output EPSG (%(default)s)')
parser.add_argument('-g','--geocor_fnam',default=None,help='GCP file name for geometric correction (%(default)s)')
parser.add_argument('-G','--geocor_geotiff',default=None,help='GeoTIFF name for geometric correction (%(default)s)')
parser.add_argument('-N','--geocor_npoly',default=None,type=int,help='Order of polynomial for geometric correction between 1 and 3 (selected based on the number of GCPs)')
parser.add_argument('-o','--optfile',default=None,help='Option file name for ogr2ogr (%(default)s)')
args = parser.parse_args()

def get_item(data,row,ncol):
    for j in range(ncol):
        v = data.iloc[row,j]
        if not isinstance(v,str):
            continue
        m = re.search(':(.*)',v)
        if m:
            return m.group(1).strip()
    return None

def read_gps(s):
    #'S 06°50\'31.62"  E 107°16\'41.50"'
    m = re.search('([nNsS])\s*(\d+)\s*°\s*(\d+)\s*\'\s*([\d\., ]+)\s*\"\s*([eEwW])\s*(\d+)\s*°\s*(\d+)\s*\'\s*([\d\., ]+)',s)
    if not m:
        raise ValueError('Error, cannot read GPS coordinates >>> {}'.format(s))
    lat = float(m.group(2))+float(m.group(3))/60.0+float(m.group(4).strip().replace(' ','.').replace(',','.'))/3600.0
    if m.group(1).upper() == 'S':
        lat *= -1
    lon = float(m.group(6))+float(m.group(7))/60.0+float(m.group(8).strip().replace(' ','.').replace(',','.'))/3600.0
    if m.group(5).upper() == 'W':
        lon *= -1
    return lon,lat

def read_month(s):
    s_low = s.lower()
    if s_low[:2] == 'ja':
        return 1
    elif s_low[:1] == 'f':
        return 2
    elif s_low[:3] == 'mar' or s_low[:1] == 'b':
        return 3
    elif s_low[:2] == 'ap':
        return 4
    elif s_low[:3] == 'may' or s_low[:2] == 'me':
        return 5
    elif s_low[:3] == 'jun':
        return 6
    elif s_low[:3] == 'jul':
        return 7
    elif s_low[:2] == 'au' or s_low[:2] == 'ag':
        return 8
    elif s_low[:1] == 's':
        return 9
    elif s_low[:1] == 'o':
        return 10
    elif s_low[:1] == 'n':
        return 11
    elif s_low[:1] == 'd':
        return 12
    else:
        raise ValueError('Error, cannot read month >>> {}'.format(s))

#if False:
if int(pyproj.__version__[0]) > 1:
    def transform_wgs84_to_utm(longitude,latitude):
        return pyproj.Transformer.from_crs('epsg:4326','epsg:{}'.format(args.epsg),always_xy=True).transform(longitude,latitude)
else:
    def transform_wgs84_to_utm(longitude,latitude):
        inProj = pyproj.Proj(init='epsg:4326')
        outProj = pyproj.Proj(init='epsg:{}'.format(args.epsg))
        return pyproj.transform(inProj,outProj,longitude,latitude)

xl = pd.ExcelFile(args.inp_fnam)
if args.sheet > 1:
    sheets = xl.sheet_names
    if len(sheets) < args.sheet:
        raise ValueError('Error, len(sheets)={}, args.sheet={}'.format(len(sheets),args.sheet))
    df = pd.read_excel(xl,header=None,sheet_name=args.sheet-1)
else:
    df = pd.read_excel(xl,header=None)
ny,nx = df.shape

location = None
date = None
trans_date = None
variety = None
village = None
for i in range(ny):
    line = ''
    for j in range(nx):
        v = df.iloc[i,j]
        if isinstance(v,str):
            line += v
        elif len(line) > 0 and line[-1] != ',':
            line += ','
    if location is None and re.search('Location.*:',line):
        v = get_item(df,i,nx)
        if v is not None:
            location = v.replace(' ','')
    elif date is None and re.search('Time Observation.*:',line):
        v = get_item(df,i,nx)
        if v is not None:
            date = v
    elif trans_date is None and re.search('Plant Date.*:',line):
        v = get_item(df,i,nx)
        if v is not None:
            trans_date = v
    elif variety is None and re.search('Variety.*:',line):
        v = get_item(df,i,nx)
        if v is not None:
            variety = v
    elif village is None and re.search('Village.*:',line):
        v = get_item(df,i,nx)
        if v is not None:
            village = v
if location is None:
    raise ValueError('Error, failed in finding location.')
if date is None:
    raise ValueError('Error, failed in finding date.')
# 04.01.2022 or 04,01,2022
m = re.search('(\d+)\s*[,\.]\s*(\d+)\s*[,\.]\s*(\d+)',date)
if m:
    dtim = datetime.strptime(m.group(1)+'.'+m.group(2)+'.'+m.group(3),'%d.%m.%Y')
else:
    # 26 Desember 2021
    m = re.search('(\d+)\s*(\D+)\s*(\d+)',date)
    if m:
        dtim = datetime(int(m.group(3)),read_month(m.group(2)),int(m.group(1)))
    else:
        raise ValueError('Error, failed in reading Time Observation >>> {}'.format(date))
if args.out_fnam is None:
    args.out_fnam = '{}_{:%Y-%m-%d}_blb.csv'.format(location,dtim)

row_number_str = None
col_number_1 = 0
for i in range(ny-1):
    v1 = df.iloc[i,col_number_1]
    v2 = df.iloc[i+1,col_number_1]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'Bunch' and v2 == 'Number':
            row_number_str = i+2
            break
if row_number_str is None:
    raise ValueError('Error, failed in finding row_number_str.')

col_number_2 = None
for j in range(col_number_1+1,nx-1):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'Bunch' and v2 == 'Number':
            col_number_2 = j
            break
if col_number_2 is None:
    raise ValueError('Error, failed in finding col_number_2.')

row_number_end = None
for i in range(row_number_str+1,ny):
    v = df.iloc[i,col_number_1]
    if isinstance(v,str):
        v = v.strip()
        if v == 'Total':
            row_number_end = i
            break
if row_number_end is None:
    raise ValueError('Error, failed in finding row_number_end.')

v = df.iloc[row_number_end,col_number_2]
if not isinstance(v,str) or v.strip() != 'Total':
    raise ValueError('Error, failed in finding row_number_end >>> {}'.format(v))

col_gps_bunch = None
for j in range(1,col_number_2):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,float):
        v1 = v1.strip()
        if v1 == 'GPS' and np.isnan(v2):
            col_gps_bunch = j
            break
if col_gps_bunch is None:
    raise ValueError('Error, failed in finding col_gps_bunch.')

col_plot_1 = None
for j in range(1,col_number_2):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'Plot' and v2 == 'Paddy':
            col_plot_1 = j
            break
if col_plot_1 is None:
    raise ValueError('Error, failed in finding col_plot_1.')
col_tiller_bunch = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if 'number' in v1.lower() and v2 == 'tillers':
            col_tiller_bunch = j
            break
if col_tiller_bunch is None:
    raise ValueError('Error, failed in finding col_tiller_bunch.')
col_blb_bunch = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if 'damage' in v1.lower() and v2 == 'BLB':
            col_blb_bunch = j
            break
if col_blb_bunch is None:
    raise ValueError('Error, failed in finding col_blb_bunch.')

col_blast_bunch = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,float) and isinstance(v2,str):
        v2 = v2.strip()
        if np.isnan(v1) and v2 == 'Blast':
            col_blast_bunch = j
            break
if col_blast_bunch is None:
    raise ValueError('Error, failed in finding col_blast_bunch.')

col_borer_bunch = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if 'damage' in v1.lower() and v2 == 'Stem Borer':
            col_borer_bunch = j
            break
if col_borer_bunch is None:
    raise ValueError('Error, failed in finding col_borer_bunch.')

col_rat_bunch = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,float) and isinstance(v2,str):
        v2 = v2.strip()
        if np.isnan(v1) and v2 == 'Rats':
            col_rat_bunch = j
            break
if col_rat_bunch is None:
    raise ValueError('Error, failed in finding col_rat_bunch.')

col_hopper_bunch = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if 'brown' in v1.lower() and v2 == 'Hopper':
            col_hopper_bunch = j
            break
if col_hopper_bunch is None:
    raise ValueError('Error, failed in finding col_hopper_bunch.')

col_plot_2 = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,float):
        v1 = v1.strip()
        if v1 == 'Plot Paddy' and np.isnan(v2):
            col_plot_2 = j
            break
if col_plot_2 is None:
    raise ValueError('Error, failed in finding col_plot_2.')

col_gps_paddy = None
for j in range(col_number_2+1,nx):
    v1 = df.iloc[row_number_str-2,j]
    v2 = df.iloc[row_number_str-1,j]
    if isinstance(v1,str) and isinstance(v2,str):
        v1 = v1.strip()
        v2 = v2.strip()
        if v1 == 'GPS' and v2 == 'Plot Paddy':
            col_gps_paddy = j
            break
if col_gps_paddy is None:
    raise ValueError('Error, failed in finding col_gps_paddy.')

number_bunch = []
plot_bunch = []
lon_bunch = []
lat_bunch = []
tiller_bunch = []
blb_bunch = []
blast_bunch = []
borer_bunch = []
rat_bunch = []
hopper_bunch = []
lon_plot = {}
lat_plot = {}
plot = None
for i in range(row_number_str,row_number_end):
    v1 = df.iloc[i,col_plot_1]
    v2 = df.iloc[i,col_plot_2]
    if not np.isnan(v1):
        if v1 != v2:
            raise ValueError('Error, different plot number, v1={}, v2={}'.format(v1,v2))
        plot = v1
    number_bunch.append(df.iloc[i,col_number_1])
    plot_bunch.append(plot)
    lon,lat = read_gps(df.iloc[i,col_gps_bunch])
    lon_bunch.append(lon)
    lat_bunch.append(lat)
    tiller_bunch.append(df.iloc[i,col_tiller_bunch])
    blb = df.iloc[i,col_blb_bunch]
    if np.isnan(blb):
        blb = 0
    blb_bunch.append(blb)
    blast = df.iloc[i,col_blast_bunch]
    if np.isnan(blast):
        blast = 0
    blast_bunch.append(blast)
    borer = df.iloc[i,col_borer_bunch]
    if np.isnan(borer):
        borer = 0
    borer_bunch.append(borer)
    rat = df.iloc[i,col_rat_bunch]
    if np.isnan(rat):
        rat = 0
    rat_bunch.append(rat)
    hopper = df.iloc[i,col_hopper_bunch]
    if np.isnan(hopper):
        hopper = 0
    hopper_bunch.append(hopper)
    if not plot in lon_plot:
        lon_plot[plot] = []
        lat_plot[plot] = []
    try:
        lon,lat = read_gps(df.iloc[i,col_gps_paddy])
        lon_plot[plot].append(lon)
        lat_plot[plot].append(lat)
    except Exception:
        continue
x_bunch,y_bunch = transform_wgs84_to_utm(lon_bunch,lat_bunch)
if len(lon_plot) < 1 or len(lon_plot) != len(lat_plot):
    raise ValueError('Error, len(lon_plot)={}, len(lat_plot)={}'.format(len(lon_plot),len(lat_plot)))
plots = np.unique(plot_bunch)
x_plot = {}
y_plot = {}
for plot in plots:
    if len(lon_plot[plot]) < 1 or len(lon_plot[plot]) != len(lat_plot[plot]):
        raise ValueError('Error, len(lon_plot[{}])={}, len(lat_plot[{}])={}'.format(plot,len(lon_plot[plot]),plot,len(lat_plot[plot])))
    x,y = transform_wgs84_to_utm(lon_plot[plot],lat_plot[plot])
    x_plot[plot] = x
    y_plot[plot] = y
plant_plot = {}
for plot in plots:
    # Plot 1. 04.01.2022 or 04,01,2022
    m = re.search('Plot\s*{}[\D]+(\d+)\s*[,\.]\s*(\d+)\s*[,\.]\s*(\d+)'.format(plot),trans_date)
    if m:
        plant_plot[plot] = datetime.strptime(m.group(1)+'.'+m.group(2)+'.'+m.group(3),'%d.%m.%Y')
        continue
    # 04.01.2022 or 04,01,2022
    m = re.search('(\d+)\s*[,\.]\s*(\d+)\s*[,\.]\s*(\d+)',trans_date)
    if m:
        plant_plot[plot] = datetime.strptime(m.group(1)+'.'+m.group(2)+'.'+m.group(3),'%d.%m.%Y')
        continue
    # 26 Desember 2021
    m = re.search('(\d+)\s*(\D+)\s*(\d+)',trans_date)
    if m:
        plant_plot[plot] = datetime(int(m.group(3)),read_month(m.group(2)),int(m.group(1)))
        continue
    raise ValueError('Error, failed in finding Plant Date for Plot{} >>> {}'.format(plot,trans_date))
plant_bunch = [plant_plot[plot] for plot in plot_bunch]

geocor_flag = False
if args.geocor_fnam is not None:
    src_xi = []
    src_yi = []
    src_xp = []
    src_yp = []
    with open(args.geocor_fnam,'r') as fp:
        for line in fp:
            #660.5    120.5 751655.112266 9243156.957321  -0.009634  -0.003979    2.10494      0.824779      0.016902   3555      0.789201   1440
            #720.5    120.5 751667.515378 9243156.775077   0.393478  -0.186223    2.37634      0.832486      0.014921   5446      0.797028   1845
            m = re.search('^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+',line)
            if not m:
                raise ValueError('Error in reading '+args.geocor_fnam)
            src_xi.append(float(m.group(1)))
            src_yi.append(float(m.group(2)))
            src_xp.append(float(m.group(3)))
            src_yp.append(float(m.group(4)))
    src_xi = np.array(src_xi)
    src_yi = np.array(src_yi)
    src_xp = np.array(src_xp)
    src_yp = np.array(src_yp)
    if args.geocor_geotiff is not None:
        ds = gdal.Open(args.geocor_geotiff)
        src_trans = ds.GetGeoTransform()
        if src_trans[2] != 0.0 or src_trans[4] != 0.0:
            raise ValueError('Error, src_trans={}'.format(src_trans))
        src_xmin = src_trans[0]
        src_xstp = src_trans[1]
        src_ymax = src_trans[3]
        src_ystp = src_trans[5]
        ds = None
        dst_xi = src_xmin+src_xstp*src_xi
        dst_yi = src_ymax+src_ystp*src_yi
    else:
        dst_xi = src_xi
        dst_yi = src_yi
    bnam,enam = os.path.splitext(args.out_fnam)
    tmp_fnam = bnam+'_tmp'+enam
    command = 'ogr2ogr'
    command += ' -f CSV'
    command += ' -s_srs EPSG:{}'.format(args.epsg)
    command += ' -t_srs EPSG:{}'.format(args.epsg)
    #command += ' -overwrite'
    command += ' -oo X_POSSIBLE_NAMES=Easting'
    command += ' -oo Y_POSSIBLE_NAMES=Northing'
    command += ' -lco GEOMETRY=AS_XY'
    command += ' -lco STRING_QUOTING=IF_NEEDED'
    if args.geocor_npoly is not None:
        command += ' -order {}'.format(args.geocor_npoly)
    line = ''
    for xi,yi,xp,yp in zip(dst_xi,dst_yi,src_xp,src_yp):
        line += ' -gcp {:22.15e} {:22.15e} {:22.15e} {:22.15e}'.format(xi,yi,xp,yp)
    if args.optfile is not None:
        with open(args.optfile,'w') as fp:
            fp.write(line)
        command += ' --optfile {}'.format(args.optfile)
    else:
        command += line
    command += ' {}'.format(tmp_fnam)
    command += ' {}'.format(args.out_fnam)
    #command += ' 2>err'
    if os.path.exists(tmp_fnam):
        os.remove(tmp_fnam)
    with open(args.out_fnam,'w') as fp:
        fp.write('Easting, Northing\n')
        for i in range(len(plot_bunch)):
            fp.write('{:12.4f}, {:13.4f}\n'.format(x_bunch[i],y_bunch[i]))
    call(command,shell=True)
    if args.optfile is not None:
        if os.path.exists(args.optfile):
            os.remove(args.optfile)
    df = pd.read_csv(tmp_fnam)
    x = list(df['X'])
    y = list(df['Y'])
    if (len(x) != len(x_bunch)) or (len(y) != len(y_bunch)):
        raise ValueError('Error, len(x)={}, len(x_bunch)={}, len(y)={}, len(y_bunch)={}'.format(len(x),len(x_bunch),len(y),len(y_bunch)))
    x_bunch = x
    y_bunch = y
    if os.path.exists(tmp_fnam):
        os.remove(tmp_fnam)
    geocor_flag = True

identify_flag = False
if args.ref_fnam is not None:
    df = pd.read_csv(args.ref_fnam,comment='#')
    df.columns = df.columns.str.strip()
    if not 'EastingI' in df.columns or not 'NorthingI' in df.columns:
        raise ValueError('Error, identified coordinates not found >>> {}'.format(args.ref_fnam))
    loc_ref = df['Location'].astype(str).str.strip().str.lower().values
    number_ref = df['BunchNumber'].astype(int).values
    plot_ref = df['PlotPaddy'].astype(int).values
    x_ref = df['EastingI'].astype(float).values
    y_ref = df['NorthingI'].astype(float).values
    plant_ref = pd.to_datetime(df['PlantDate']).dt.to_pydatetime()
    if not np.all(loc_ref == location.lower()):
        raise ValueError('Error, different Location >>> {}'.format(args.ref_fnam))
    elif not np.array_equal(number_ref,number_bunch):
        raise ValueError('Error, different BunchNumber >>> {}'.format(args.ref_fnam))
    elif not np.array_equal(plot_ref,plot_bunch):
        raise ValueError('Error, different PlotPaddy >>> {}'.format(args.ref_fnam))
    elif not np.array_equal(plant_ref,plant_bunch):
        raise ValueError('Error, different PlantDate >>> {}'.format(args.ref_fnam))
    r = np.sqrt(np.square(x_ref-np.array(x_bunch))+np.square(y_ref-np.array(y_bunch)))
    cnd = (r < args.rmax)
    rcnd = r[cnd]
    if rcnd.size < r.size*args.nmin:
        raise ValueError('Error, too few points near reference >>> {}'.format(rcnd.size))
    x_bunch = list(x_ref)
    y_bunch = list(y_ref)
    identify_flag = True

with open(args.out_fnam,'w') as fp:
    fp.write('# Location: {}\n'.format(location))
    fp.write('# Village: {}\n'.format(village))
    for plot in plots:
        fp.write('# Plot{}:'.format(plot))
        for i in range(len(x_plot[plot])):
            fp.write(' {:12.4f} {:13.4f}'.format(x_plot[plot][i],y_plot[plot][i]))
        fp.write('\n')
    fp.write('# Variety: {}\n'.format(variety))
    fp.write('# Date: {:%Y-%m-%d}\n'.format(dtim))
    fp.write('#------------------------\n')
    if identify_flag:
        fp.write('Location, BunchNumber, PlotPaddy, EastingI, NorthingI, PlantDate, Age, Tiller, BLB, Blast, Borer, Rat, Hopper, Drought\n')
    elif geocor_flag:
        fp.write('Location, BunchNumber, PlotPaddy, EastingG, NorthingG, PlantDate, Age, Tiller, BLB, Blast, Borer, Rat, Hopper, Drought\n')
    else:
        fp.write('Location, BunchNumber, PlotPaddy, EastingO, NorthingO, PlantDate, Age, Tiller, BLB, Blast, Borer, Rat, Hopper, Drought\n')
    for i in range(len(plot_bunch)):
        fp.write('{:>13s}, {:3d}, {:3d}, {:12.4f}, {:13.4f}, {:10s}, {:5.0f}, {:3d}, {:3d}, {:3d}, {:3d}, {:3d}, {:3d}, {:3d}\n'.format(
                 location,number_bunch[i],plot_bunch[i],x_bunch[i],y_bunch[i],plant_bunch[i].strftime('%Y-%m-%d'),date2num(dtim)-date2num(plant_bunch[i]),
                 tiller_bunch[i],blb_bunch[i],blast_bunch[i],borer_bunch[i],rat_bunch[i],hopper_bunch[i],0))
