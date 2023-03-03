#!/usr/bin/env python
import os
import sys
import numpy as np
try:
    import gdal
except Exception:
    from osgeo import gdal
try:
    import osr
except Exception:
    from osgeo import osr
try:
    from io import StringIO
except Exception:
    from StringIO import StringIO
from subprocess import check_output,call
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
SCRDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
#REF_DATA_MIN = None
REF_DATA_MIN = 1.0e-5 # for WorldView DN image
RESAMPLING = 'cubic'
RESAMPLING2 = 'near'
MINIMUM_RATIO = 0.9
MINIMUM_NUMBER = 20
REFINE_NUMBER = 10

# Read options
parser = ArgumentParser(usage='%(prog)s target_georeferenced_image reference_georeferenced_image [options]\n'
'       reference_georeferenced_image is not required if the use_gcps option is given.\n'
'       Both target_georeferenced_image and reference_georeferenced_image are not required if the use_gcps option and the trg_shapefile option are given.\n',
formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('--scrdir',default=SCRDIR,help='Script directory where find_gcps_cc.py exists (%(default)s)')
parser.add_argument('-o','--out_fnam',default=None,help='Output file name (%(default)s)')
parser.add_argument('-b','--ref_band',default=None,type=int,help='Reference band# from 1 (%(default)s)')
parser.add_argument('--ref_band_name',default=None,help='Reference band name (%(default)s)')
parser.add_argument('-B','--trg_band',default=None,type=int,help='Target band# from 1 (%(default)s)')
parser.add_argument('--trg_band_name',default=None,help='Target band name (%(default)s)')
parser.add_argument('--ref_multi_band',default=None,type=int,action='append',help='Reference multi-band number from 1 (%(default)s)')
parser.add_argument('--ref_multi_band_name',default=None,action='append',help='Reference multi-band name (%(default)s)')
parser.add_argument('--ref_multi_ratio',default=None,type=float,action='append',help='Reference multi-band ratio (%(default)s)')
parser.add_argument('--trg_multi_band',default=None,type=int,action='append',help='Target multi-band number from 1 (%(default)s)')
parser.add_argument('--trg_multi_band_name',default=None,action='append',help='Target multi-band name (%(default)s)')
parser.add_argument('--trg_multi_ratio',default=None,type=float,action='append',help='Target multi-band ratio (%(default)s)')
parser.add_argument('-x','--trg_indx_start',default=None,type=int,help='Target start x index (0)')
parser.add_argument('-X','--trg_indx_stop',default=None,type=int,help='Target stop x index (target width)')
parser.add_argument('-s','--trg_indx_step',default=None,type=int,help='Target step x index (half of subset_width)')
parser.add_argument('-y','--trg_indy_start',default=None,type=int,help='Target start y index (0)')
parser.add_argument('-Y','--trg_indy_stop',default=None,type=int,help='Target stop y index (target height)')
parser.add_argument('-S','--trg_indy_step',default=None,type=int,help='Target step y index (half of subset_height)')
parser.add_argument('-W','--subset_width',default=None,type=int,help='Subset width in target pixel (%(default)s)')
parser.add_argument('-H','--subset_height',default=None,type=int,help='Subset height in target pixel (%(default)s)')
parser.add_argument('--shift_width',default=None,type=int,help='Max shift width in target pixel (%(default)s)')
parser.add_argument('--shift_height',default=None,type=int,help='Max shift height in target pixel (%(default)s)')
parser.add_argument('--margin_width',default=None,type=int,help='Margin width in target pixel (%(default)s)')
parser.add_argument('--margin_height',default=None,type=int,help='Margin height in target pixel (%(default)s)')
parser.add_argument('--scan_indx_step',default=None,type=int,help='Scan step x index (%(default)s)')
parser.add_argument('--scan_indy_step',default=None,type=int,help='Scan step y index (%(default)s)')
parser.add_argument('--ref_data_min',default=REF_DATA_MIN,type=float,help='Minimum reference data value (%(default)s)')
parser.add_argument('--ref_data_max',default=None,type=float,help='Maximum reference data value (%(default)s)')
parser.add_argument('--trg_data_min',default=None,type=float,help='Minimum target data value (%(default)s)')
parser.add_argument('--trg_data_max',default=None,type=float,help='Maximum target data value (%(default)s)')
parser.add_argument('--ref_data_umin',default=None,type=float,help='Minimum reference data value to use (%(default)s)')
parser.add_argument('--ref_data_umax',default=None,type=float,help='Maximum reference data value to use (%(default)s)')
parser.add_argument('-I','--interp',default=None,help='Interpolation method (%(default)s)')
parser.add_argument('-r','--rthr',default=None,type=float,help='Threshold of correlation coefficient (%(default)s)')
parser.add_argument('-E','--feps',default=None,type=float,help='Step length for curve_fit (%(default)s)')
parser.add_argument('--img_fnam',default=None,help='Image file name (%(default)s)')
parser.add_argument('--scan_fnam',default=None,help='Scan file name (%(default)s)')
parser.add_argument('-g','--use_gcps',default=None,help='GCP file name to use (%(default)s)')
parser.add_argument('-G','--save_gcps',default=None,help='GCP file name to save (%(default)s)')
parser.add_argument('--optfile',default=None,help='Option file name for gdal_translate (%(default)s)')
parser.add_argument('--trg_shapefile',default=None,help='Target shapefile (%(default)s)')
parser.add_argument('-e','--trg_epsg',default=None,help='Target EPSG (guessed from target data)')
parser.add_argument('-n','--npoly',default=None,type=int,help='Order of polynomial used for warping between 1 and 3 (selected based on the number of GCPs)')
parser.add_argument('-R','--resampling',default=RESAMPLING,help='Resampling method (%(default)s)')
parser.add_argument('--resampling2',default=RESAMPLING2,help='Another resampling method (%(default)s)')
parser.add_argument('--resampling2_band',default=None,type=int,action='append',help='Target band# from 1 for another resampling method (%(default)s)')
parser.add_argument('--minimum_number',default=MINIMUM_NUMBER,type=int,help='Minimum number of GCPs to perform geometric correction (%(default)s)')
parser.add_argument('--refine_gcps',default=None,type=float,help='Tolerance to refine GCPs for polynomial interpolation (%(default)s)')
parser.add_argument('--minimum_gcps',default=None,type=int,help='Minimum number of GCPs to be left after refine_gcps (available number - discard_number or available number x minimum_ratio)')
parser.add_argument('--minimum_ratio',default=MINIMUM_RATIO,type=float,help='Minimum ratio of GCPs to be left after refine_gcps (%(default)s)')
parser.add_argument('--discard_number',default=None,type=int,help='Maximum number of GCPs to be discarded by refine_gcps (%(default)s)')
parser.add_argument('--refine_number',default=REFINE_NUMBER,type=int,help='Minimum number of GCPs to perform refine_gcps (%(default)s)')
parser.add_argument('--tr',default=None,type=float,help='Output resolution in output georeferenced units (%(default)s)')
parser.add_argument('--tps',default=False,action='store_true',help='Use thin plate spline transformer (%(default)s)')
parser.add_argument('--exp',default=False,action='store_true',help='Output in exp format (%(default)s)')
parser.add_argument('--long',default=False,action='store_true',help='Output in long format (%(default)s)')
parser.add_argument('-u','--use_edge',default=False,action='store_true',help='Use GCPs near the edge of the correction range (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
(args,rest) = parser.parse_known_args()
if args.use_gcps is None: # Both trg and ref images are required
    if len(rest) < 2:
        parser.print_help()
        sys.exit(0)
    trg_fnam = rest[0]
    ref_fnam = rest[1]
elif args.trg_shapefile is None: # Only trg image is required
    if len(rest) < 1:
        parser.print_help()
        sys.exit(0)
    trg_fnam = rest[0]
elif len(rest) >= 1: # trg image is optional
    trg_fnam = rest[0]
else: # No trg image
    trg_fnam = None

if trg_fnam is not None:
    trg_bnam = os.path.splitext(os.path.basename(trg_fnam))[0]
    tmp_fnam = trg_bnam+'_tmp.tif'
    tmp_xnam = tmp_fnam+'.aux.xml'
    if args.out_fnam is None:
        out_fnam = trg_bnam+'_geocor.tif'
    else:
        out_fnam = args.out_fnam
    if (args.trg_epsg is None) or (args.resampling2_band_name is not None):
        ds = gdal.Open(trg_fnam)
        if args.trg_epsg is None:
            prj = ds.GetProjection()
            srs = osr.SpatialReference(wkt=prj)
            args.trg_epsg = srs.GetAttrValue('AUTHORITY',1)
        if args.resampling2_band_name is not None:
            band_names = []
            for i in range(ds.RasterCount):
                band_names.append(ds.GetRasterBand(i+1).GetDescription())
            args.resampling2_band = []
            for band_name in args.resampling2_band_name:
                if not band_name in band_names:
                    raise ValueError('Error in finding {} >>> {}'.format(band_name,trg_fnam))
                indx = band_names.index(band_name)
                args.resampling2_band.append(indx+1)
        ds = None # close dataset

if args.use_gcps is not None:
    fnam = args.use_gcps
else:
    command = 'python'
    command += ' '+os.path.join(args.scrdir,'find_gcps_cc.py')
    command += ' '+trg_fnam
    command += ' '+ref_fnam
    command += ' -v'
    if args.ref_band is not None:
        command += ' --ref_band {}'.format(args.ref_band)
    if args.ref_band_name is not None:
        command += ' --ref_band_name {}'.format(args.ref_band_name)
    if args.trg_band is not None:
        command += ' --trg_band {}'.format(args.trg_band)
    if args.trg_band_name is not None:
        command += ' --trg_band_name {}'.format(args.trg_band_name)
    if args.ref_multi_band is not None:
        for band in args.ref_multi_band:
            command += ' --ref_multi_band {}'.format(band)
    if args.ref_multi_band_name is not None:
        for band in args.ref_multi_band_name:
            command += ' --ref_multi_band_name {}'.format(band)
    if args.ref_multi_ratio is not None:
        for ratio in args.ref_multi_ratio:
            command += ' --ref_multi_ratio {}'.format(ratio)
    if args.trg_multi_band is not None:
        for band in args.trg_multi_band:
            command += ' --trg_multi_band {}'.format(band)
    if args.trg_multi_band_name is not None:
        for band in args.trg_multi_band_name:
            command += ' --trg_multi_band_name {}'.format(band)
    if args.trg_multi_ratio is not None:
        for ratio in args.trg_multi_ratio:
            command += ' --trg_multi_ratio {}'.format(ratio)
    if args.trg_indx_start is not None:
        command += ' --trg_indx_start {}'.format(args.trg_indx_start)
    if args.trg_indx_stop is not None:
        command += ' --trg_indx_stop {}'.format(args.trg_indx_stop)
    if args.trg_indx_step is not None:
        command += ' --trg_indx_step {}'.format(args.trg_indx_step)
    if args.trg_indy_start is not None:
        command += ' --trg_indy_start {}'.format(args.trg_indy_start)
    if args.trg_indy_stop is not None:
        command += ' --trg_indy_stop {}'.format(args.trg_indy_stop)
    if args.trg_indy_step is not None:
        command += ' --trg_indy_step {}'.format(args.trg_indy_step)
    if args.subset_width is not None:
        command += ' --subset_width {}'.format(args.subset_width)
    if args.subset_height is not None:
        command += ' --subset_height {}'.format(args.subset_height)
    if args.shift_width is not None:
        command += ' --shift_width {}'.format(args.shift_width)
    if args.shift_height is not None:
        command += ' --shift_height {}'.format(args.shift_height)
    if args.margin_width is not None:
        command += ' --margin_width {}'.format(args.margin_width)
    if args.margin_height is not None:
        command += ' --margin_height {}'.format(args.margin_height)
    if args.scan_indx_step is not None:
        command += ' --scan_indx_step {}'.format(args.scan_indx_step)
    if args.scan_indy_step is not None:
        command += ' --scan_indy_step {}'.format(args.scan_indy_step)
    if args.ref_data_min is not None:
        command += ' --ref_data_min {}'.format(args.ref_data_min)
    if args.ref_data_max is not None:
        command += ' --ref_data_max {}'.format(args.ref_data_max)
    if args.trg_data_min is not None:
        command += ' --trg_data_min {}'.format(args.trg_data_min)
    if args.trg_data_max is not None:
        command += ' --trg_data_max {}'.format(args.trg_data_max)
    if args.ref_data_umin is not None:
        command += ' --ref_data_umin {}'.format(args.ref_data_umin)
    if args.ref_data_umax is not None:
        command += ' --ref_data_umax {}'.format(args.ref_data_umax)
    if args.interp is not None:
        command += ' --interp {}'.format(args.interp)
    if args.rthr is not None:
        command += ' --rthr {}'.format(args.rthr)
    if args.feps is not None:
        command += ' --feps {}'.format(args.feps)
    if args.img_fnam is not None:
        command += ' --img_fnam {}'.format(args.img_fnam)
    if args.scan_fnam is not None:
        command += ' --scan_fnam {}'.format(args.scan_fnam)
    if args.exp:
        command += ' --exp'
    if args.long:
        command += ' --long'
    if args.use_edge:
        command += ' --use_edge'
    if args.debug:
        command += ' --debug'
    out = check_output(command,shell=True).decode()
    fnam = StringIO(out)
    if args.save_gcps is not None:
        with open(args.save_gcps,'w') as fp:
            fp.write(out)
try:
    xi,yi,xp,yp,dx,dy,r = np.loadtxt(fnam,usecols=(0,1,2,3,4,5,6),unpack=True)
    if xi.size < args.minimum_number:
        raise ValueError('Error, not enough GCP points.')
except Exception:
    sys.exit()

if trg_fnam is not None:
    command = 'gdal_translate'
    line = ''
    for i,j,x,y in zip(xi,yi,xp,yp):
        line += ' -gcp {} {} {} {}'.format(i,j,x,y)
    if args.optfile is not None:
        with open(args.optfile,'w') as fp:
            fp.write(line)
        command += ' --optfile {}'.format(args.optfile)
    else:
        command += line
    command += ' '+trg_fnam
    command += ' '+tmp_fnam
    call(command,shell=True)
    if args.optfile is not None:
        if os.path.exists(args.optfile):
            os.remove(args.optfile)

    command = 'gdalwarp'
    command += ' -t_srs EPSG:{}'.format(args.trg_epsg)
    command += ' -overwrite'
    if args.tr is not None:
        command += ' -tr {} {}'.format(args.tr,args.tr)
        command += ' -tap'
    if args.tps:
        command += ' -tps'
    elif args.npoly is not None:
        command += ' -order {}'.format(args.npoly)
    if args.refine_gcps is not None and xi.size >= args.refine_number:
        if args.minimum_gcps is None:
            if args.discard_number is not None:
                args.minimum_gcps = xi.size-args.discard_number
            else:
                args.minimum_gcps = int(args.minimum_ratio*xi.size+0.5)
        command += ' -refine_gcps {} {}'.format(args.refine_gcps,args.minimum_gcps)
    if args.resampling2_band is not None:
        tmp2_fnam = trg_bnam+'_tmp2.tif'
        tmp2_xnam = tmp2_fnam+'.aux.xml'
        out1_fnam = trg_bnam+'_geocor1.tif'
        out2_fnam = trg_bnam+'_geocor2.tif'
        command1 = command + ' -r {}'.format(args.resampling)
        command1 += ' '+tmp_fnam
        command1 += ' '+out1_fnam
        command2 = command + ' -r {}'.format(args.resampling2)
        command2 += ' '+tmp2_fnam
        command2 += ' '+out2_fnam
        command = 'gdal_translate'
        for band_number in args.resampling2_band:
            command += ' -b {}'.format(band_number)
        command += ' '+tmp_fnam
        command += ' '+tmp2_fnam
        call(command,shell=True)
        call(command1,shell=True)
        call(command2,shell=True)
        ds1 = gdal.Open(out1_fnam)
        ds2 = gdal.Open(out2_fnam)
        drv = gdal.GetDriverByName('GTiff')
        ds = drv.CreateCopy(out_fnam,ds1,strict=0)
        for i,band_number in enumerate(args.resampling2_band):
            band = ds2.GetRasterBand(i+1)
            ds.GetRasterBand(band_number).WriteArray(band.ReadAsArray())
        ds.FlushCache()
        ds = None
        ds1 = None
        ds2 = None
        if os.path.exists(tmp2_fnam):
            os.remove(tmp2_fnam)
        if os.path.exists(tmp2_xnam):
            os.remove(tmp2_xnam)
        if os.path.exists(out1_fnam):
            os.remove(out1_fnam)
        if os.path.exists(out2_fnam):
            os.remove(out2_fnam)
    else:
        command += ' -r {}'.format(args.resampling)
        command += ' '+tmp_fnam
        command += ' '+out_fnam
        call(command,shell=True)
    if os.path.exists(tmp_fnam):
        os.remove(tmp_fnam)
    if os.path.exists(tmp_xnam):
        os.remove(tmp_xnam)

if args.trg_shapefile is not None:
    if args.out_fnam is None:
        out_shapefile = os.path.splitext(os.path.basename(args.trg_shapefile))[0]+'_geocor.shp'
    else:
        out_shapefile = args.out_fnam
    command = 'ogr2ogr'
    command += ' -t_srs EPSG:{}'.format(args.trg_epsg)
    command += ' -overwrite'
    if args.tps:
        command += ' -tps'
    elif args.npoly is not None:
        command += ' -order {}'.format(args.npoly)
    line = ''
    for i,j,x,y in zip(xi,yi,xp,yp):
        line += ' -gcp {} {} {} {}'.format(i,j,x,y)
    if args.optfile is not None:
        with open(args.optfile,'w') as fp:
            fp.write(line)
        command += ' --optfile {}'.format(args.optfile)
    else:
        command += line
    command += ' -f "ESRI Shapefile"'
    command += ' '+out_shapefile
    command += ' '+args.trg_shapefile
    call(command,shell=True)
    if args.optfile is not None:
        if os.path.exists(args.optfile):
            os.remove(args.optfile)
