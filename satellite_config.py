import os
import sys
import numpy as np
from datetime import datetime,timedelta
import configparser
from proc_satellite_download import proc_download
from proc_satellite_geocor import proc_geocor
from proc_satellite_indices import proc_indices
from proc_satellite_parcel import proc_parcel
from proc_satellite_atcor import proc_atcor
from proc_satellite_interp import proc_interp
from proc_satellite_phenology import proc_phenology
from proc_satellite_extract import proc_extract
from proc_satellite_formula import proc_formula
from proc_satellite_estimate import proc_estimate

# Set folder&file names
HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')
top_dir = os.path.join(HOME,'Work')
if not os.path.isdir(top_dir):
    top_dir = os.path.join(HOME,'Documents')
python_path = sys.executable
scr_dir = os.path.join(HOME,'SatelliteTool')
netrc_fnam = os.path.join(HOME,'.netrc')
cnf_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
now_dtim = datetime.now()
main_start_date = (now_dtim-timedelta(days=300)).strftime('%Y-%m%b-%d')
main_end_date = (now_dtim-timedelta(days=210)).strftime('%Y-%m%b-%d')
main_field_data = os.path.join(top_dir,'Field_Data','Current')
main_drone_analysis = os.path.join(top_dir,'Drone_Analysis','Current')
main_s1_data = os.path.join(top_dir,'Sentinel-1_Data')
main_s1_analysis = os.path.join(top_dir,'Sentinel-1_Analysis','Current')
main_s2_data = os.path.join(top_dir,'Sentinel-2_Data')
main_s2_analysis = os.path.join(top_dir,'Sentinel-2_Analysis','Current')
main_browse_image = os.path.join(cnf_dir,'browse.png')
if not os.path.exists(main_browse_image):
    main_browse_image = os.path.join(HOME,'Pictures','browse.png')
gis_fnam = os.path.join(top_dir,'Shapefile','All_area_polygon_20210914','All_area_polygon_20210914.shp')
ref_fnam = os.path.join(top_dir,'WorldView','wv2_180629_mul.tif')
mask_parcel = os.path.join(main_s2_data,'parcel_mask.tif')
mask_studyarea = os.path.join(main_s2_data,'studyarea_mask.tif')
mask_paddy = os.path.join(main_s1_data,'paddy_mask.tif')

# Set defaults
config_defaults = dict(os.environ)
config_defaults.update({
#----------- main -----------
'main.blocks'                         : ['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15'],
'main.date_format'                    : 'yyyy-mm&mmm-dd',
'main.start_date'                     : main_start_date,
'main.end_date'                       : main_end_date,
'main.first_date'                     : '',
'main.last_date'                      : '',
'main.obs_block'                      : '',
'main.obs_date'                       : '',
'main.field_data'                     : main_field_data,
'main.drone_analysis'                 : main_drone_analysis,
'main.s1_data'                        : main_s1_data,
'main.s1_analysis'                    : main_s1_analysis,
'main.s2_data'                        : main_s2_data,
'main.s2_analysis'                    : main_s2_analysis,
'main.browse_image'                   : main_browse_image,
'main.download'                       : True,
'main.geocor'                         : True,
'main.indices'                        : True,
'main.parcel'                         : True,
'main.atcor'                          : False,
'main.interp'                         : True,
'main.phenology'                      : True,
'main.extract'                        : False,
'main.formula'                        : False,
'main.estimate'                       : True,
'main.no_gui'                         : False,
'main.window_width'                   : 650,
'main.top_frame_height'               : 275,
'main.left_frame_width'               : 30,
'main.right_frame_width'              : 100,
'main.left_cnv_height'                : 21,
'main.right_cnv_height'               : 21,
'main.center_btn_width'               : 20,
#----------- download -----------
'download.server'                     : 'satreps-nas',
'download.port'                       : 443,
'download.netrc_fnam'                 : netrc_fnam,
'download.trans_path'                 : '/SATREPS/ipb/User/1_Spatial-information/Transplanting_date/Cihea/final/v1.4',
'download.l2a_path'                   : '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/L2A',
'download.geocor_path'                : '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/geocor',
'download.indices_path'               : '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/indices',
'download.parcel_path'                : '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/parcel',
'download.atcor_path'                 : '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/atcor',
'download.interp_path'                : '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/interp',
'download.tentative_path'             : '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/tentative_interp',
'download.search_key'                 : '',
'download.dflag'                      : [True,True,True,True,True,True,True,True],
'download.oflag'                      : [False,False,False,False,False,False,False,False],
'download.python_path'                : python_path,
'download.scr_dir'                    : scr_dir,
'download.middle_left_frame_width'    : 1000,
#----------- geocor -----------
'geocor.l2a_dir'                      : os.path.join(main_s2_data,'L2A'),
'geocor.search_key'                   : '',
'geocor.ref_fnam'                     : ref_fnam,
'geocor.ref_bands'                    : [5,-1,-1],
'geocor.ref_factors'                  : [np.nan,np.nan,np.nan],
'geocor.ref_range'                    : [1.0e-5,np.nan],
'geocor.trg_subset'                   : [107.201,107.367,-6.910,-6.750],
'geocor.trg_resample'                 : [743805.0,757295.0,9235815.0,9251805.0],
'geocor.trg_bands'                    : [4,-1,-1],
'geocor.trg_factors'                  : [np.nan,np.nan,np.nan],
'geocor.trg_flags'                    : [17,-1,-1,-1,-1],
'geocor.trg_pixel'                    : 10.0,
'geocor.trg_range'                    : [np.nan,np.nan],
'geocor.init_shifts'                  : [0.0,0.0],
'geocor.part_size'                    : 1000.0,
'geocor.gcp_interval'                 : 500.0,
'geocor.max_shift'                    : 30.0,
'geocor.margin'                       : 50.0,
'geocor.scan_step'                    : 1,
'geocor.geocor_order'                 : 'Auto',
'geocor.nmin'                         : 20,
'geocor.cmin'                         : 0.3,
'geocor.rmax'                         : 100.0,
'geocor.emaxs'                        : [3.0,2.0,2.0],
'geocor.smooth_fact'                  : [1.0e4,1.0e4],
'geocor.smooth_dmax'                  : [4.0,4.0],
'geocor.oflag'                        : [False,False],
'geocor.python_path'                  : python_path,
'geocor.scr_dir'                      : scr_dir,
'geocor.middle_left_frame_width'      : 1000,
#----------- indices -----------
'indices.geocor_dir'                  : os.path.join(main_s2_data,'geocor'),
'indices.out_refs'                    : [True,True,True,True,True,True,True,True,True,True],
'indices.norm_bands'                  : [True,True,True,True,True,True,True,False,False,False],
'indices.out_nrefs'                   : [True,True,True,True,True,True,True,True,True,True],
'indices.rgi_red_band'                : 'e1',
'indices.out_inds'                    : [True,True,True,True],
'indices.oflag'                       : False,
'indices.zmin_refs'                   : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
'indices.zmin_nrefs'                  : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
'indices.zmin_inds'                   : [-0.2,-0.2,0.0,0.0],
'indices.zmax_refs'                   : [0.3,0.3,0.3,0.5,0.5,0.6,0.6,0.6,0.6,0.6],
'indices.zmax_nrefs'                  : [1.2,1.2,1.2,2.0,2.0,2.5,2.5,2.5,2.5,2.5],
'indices.zmax_inds'                   : [1.0,1.0,0.1,1.2],
'indices.zstp_refs'                   : [0.05,0.05,0.05,0.1,0.1,0.1,0.1,0.1,0.1,0.1],
'indices.zstp_nrefs'                  : [0.2,0.2,0.2,0.5,0.5,0.5,0.5,0.5,0.5,0.5],
'indices.zstp_inds'                   : [0.2,0.2,0.02,0.2],
'indices.python_path'                 : python_path,
'indices.scr_dir'                     : scr_dir,
'indices.middle_left_frame_width'     : 1000,
#----------- parcel -----------
'parcel.geocor_dir'                   : os.path.join(main_s2_data,'geocor'),
'parcel.indices_dir'                  : os.path.join(main_s2_data,'indices'),
'parcel.gis_fnam'                     : gis_fnam,
'parcel.mask_parcel'                  : mask_parcel,
'parcel.out_refs'                     : [True,True,True,True,True,True,True,True,True,True],
'parcel.cr_sc_refs'                   : [True,True,True,True,True,True,True,True,True,True],
'parcel.cr_ref_refs'                  : [True,True,True,True,True,True,True,True,True,True],
'parcel.out_nrefs'                    : [True,True,True,True,True,True,True,True,True,True],
'parcel.cr_sc_nrefs'                  : [True,True,True,True,True,True,True,True,True,True],
'parcel.cr_ref_nrefs'                 : [True,True,True,True,True,True,True,True,True,True],
'parcel.out_inds'                     : [True,True,True,True],
'parcel.cr_sc_inds'                   : [True,True,True,True],
'parcel.cr_ref_inds'                  : [True,True,True,True],
'parcel.cloud_band'                   : 'r',
'parcel.cloud_thr'                    : 0.35,
'parcel.buffer'                       : 0.0,
'parcel.csv_flag'                     : True,
'parcel.oflag'                        : False,
'parcel.zmin_refs'                    : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
'parcel.zmin_nrefs'                   : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
'parcel.zmin_inds'                    : [-0.2,-0.2,0.0,0.0],
'parcel.zmax_refs'                    : [0.3,0.3,0.3,0.5,0.5,0.6,0.6,0.6,0.6,0.6],
'parcel.zmax_nrefs'                   : [1.2,1.2,1.2,2.0,2.0,2.5,2.5,2.5,2.5,2.5],
'parcel.zmax_inds'                    : [1.0,1.0,0.1,1.2],
'parcel.zstp_refs'                    : [0.05,0.05,0.05,0.1,0.1,0.1,0.1,0.1,0.1,0.1],
'parcel.zstp_nrefs'                   : [0.2,0.2,0.2,0.5,0.5,0.5,0.5,0.5,0.5,0.5],
'parcel.zstp_inds'                    : [0.2,0.2,0.02,0.2],
'parcel.python_path'                  : python_path,
'parcel.scr_dir'                      : scr_dir,
'parcel.middle_left_frame_width'      : 1000,
#----------- atcor -----------
'atcor.geocor_dir'                    : os.path.join(main_s2_data,'geocor'),
'atcor.indices_dir'                   : os.path.join(main_s2_data,'indices'),
'atcor.gis_fnam'                      : gis_fnam,
'atcor.mask_parcel'                   : mask_parcel,
'atcor.mask_studyarea'                : mask_studyarea,
'atcor.out_refs'                      : [True,True,True,True,True,True,True,True,True,True],
'atcor.atcor_refs'                    : [True,True,True,True,True,True,True,True,True,True],
'atcor.out_nrefs'                     : [True,True,True,True,True,True,True,True,True,True],
'atcor.atcor_nrefs'                   : [True,True,True,True,True,True,True,True,True,True],
'atcor.out_inds'                      : [True,True,True,True],
'atcor.atcor_inds'                    : [True,True,True,True],
'atcor.stat_period'                   : 730,
'atcor.stat_nmin'                     : 10,
'atcor.n_ref'                         : 1000,
'atcor.ref_band'                      : [True,True,True,False,False,False,True,False,False,False],
'atcor.ref_thr'                       : 0.035,
'atcor.clean_nmin'                    : 4,
'atcor.clean_band'                    : 'r',
'atcor.clean_thr'                     : [0.06,0.05,1.0],
'atcor.cloud_band'                    : 'r',
'atcor.cloud_thr'                     : 0.35,
'atcor.nstp'                          : 10,
'atcor.rel_thr'                       : 2.0,
'atcor.fit_thr'                       : 0.3,
'atcor.csv_flag'                      : True,
'atcor.oflag'                         : [False,False,False,False,False],
'atcor.zmin_refs'                     : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
'atcor.zmin_nrefs'                    : [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
'atcor.zmin_inds'                     : [-0.2,-0.2,0.0,0.0],
'atcor.zmax_refs'                     : [0.3,0.3,0.3,0.5,0.5,0.6,0.6,0.6,0.6,0.6],
'atcor.zmax_nrefs'                    : [1.2,1.2,1.2,2.0,2.0,2.5,2.5,2.5,2.5,2.5],
'atcor.zmax_inds'                     : [1.0,1.0,0.1,1.2],
'atcor.zstp_refs'                     : [0.05,0.05,0.05,0.1,0.1,0.1,0.1,0.1,0.1,0.1],
'atcor.zstp_nrefs'                    : [0.2,0.2,0.2,0.5,0.5,0.5,0.5,0.5,0.5,0.5],
'atcor.zstp_inds'                     : [0.2,0.2,0.02,0.2],
'atcor.python_path'                   : python_path,
'atcor.scr_dir'                       : scr_dir,
'atcor.middle_left_frame_width'       : 1000,
#----------- interp -----------
'interp.cflag_thr'                    : 3.0,
'interp.p_smooth'                     : 2.0e-3,
'interp.atcor_flag'                   : True,
'interp.csv_flag'                     : True,
'interp.oflag'                        : [False,True],
'interp.python_path'                  : python_path,
'interp.scr_dir'                      : scr_dir,
'interp.middle_left_frame_width'      : 1000,
#----------- phenology -----------
'phenology.gis_fnam'                  : gis_fnam,
'phenology.mask_parcel'               : mask_parcel,
'phenology.mask_paddy'                : mask_paddy,
'phenology.trans_fnam'                : '',
'phenology.head_fnam'                 : '',
'phenology.harvest_fnam'              : '',
'phenology.assess_fnam'               : '',
'phenology.trans_select'              : 'Around Probable Planting',
'phenology.trans_indicator'           : '\u03C3 Min',
'phenology.trans_pref'                : '',
'phenology.trans_thr1'                : [-18.0,np.nan,-0.6,2.2,np.nan],
'phenology.trans_thr2'                : [-13.0,np.nan,np.nan,0.0,np.nan],
'phenology.trans_thr3'                : [4.0,30.0],
'phenology.trans_thr4'                : [np.nan,np.nan],
'phenology.trans_thr5'                : [2.0,30.0],
'phenology.atc_params'                : [100.0,10.0],
'phenology.assess_dthrs'              : [120,10,10],
'phenology.y1_smooth'                 : 0.02,
'phenology.y1_thr'                    : 0.0,
'phenology.python_path'               : python_path,
'phenology.scr_dir'                   : scr_dir,
'phenology.middle_left_frame_width'   : 1000,
#----------- extract -----------
'extract.gis_fnam'                    : gis_fnam,
'extract.obs_src'                     : 'Field Data',
'extract.obs_fnam'                    : os.path.join(main_field_data,'observation.csv'),
'extract.i_sheet'                     : 1,
'extract.epsg'                        : 32748,
'extract.major_flag'                  : True,
'extract.data_select'                 : 'Specific Interpolated Data',
'extract.spec_date'                   : '',
'extract.atcor_flag'                  : True,
'extract.event_fnam'                  : os.path.join(main_s2_analysis,'phenology','phenology.csv'),
'extract.event_dates'                 : ['','','','',''],
'extract.event_flag'                  : False,
'extract.python_path'                 : python_path,
'extract.scr_dir'                     : scr_dir,
'extract.middle_left_frame_width'     : 1000,
#----------- formula -----------
'formula.inp_fnams'                   : os.path.join(main_s2_analysis,'extract','extract.csv'),
'formula.data_select'                 : 'Days from Assessment',
'formula.harvest_range'               : [-100.0,100.0],
'formula.assess_range'                : [-15.0,15.0],
'formula.head_range'                  : [20.0,50.0],
'formula.peak_range'                  : [20.0,50.0],
'formula.plant_range'                 : [80.0,110.0],
'formula.age_range'                   : [80.0,110.0],
'formula.n_x'                         : [1,2],
'formula.x1_params'                   : [False,False,False,False,False,False,False,False,False,False],
'formula.x2_params'                   : [False,False,True,False,False,False,True,False,False,False],
'formula.x3_params'                   : [True,True,False,True],
'formula.y_params'                    : [True,False,False,False,False,False],
'formula.score_max'                   : [9,9,1,1,1,9],
'formula.score_step'                  : [2.0,2.0,0.2,0.2,0.2,2.0],
'formula.ythr'                        : [0.2,1.0,1.0,1.0,1.0,1.0],
'formula.yfac1'                       : [1.0,np.nan,np.nan,np.nan,np.nan,np.nan],
'formula.yfac2'                       : [np.nan,1.0,np.nan,np.nan,np.nan,np.nan],
'formula.yfac3'                       : [np.nan,np.nan,1.0,np.nan,np.nan,np.nan],
'formula.yfac4'                       : [np.nan,np.nan,np.nan,1.0,np.nan,np.nan],
'formula.yfac5'                       : [np.nan,np.nan,np.nan,np.nan,1.0,np.nan],
'formula.yfac6'                       : [np.nan,np.nan,np.nan,np.nan,np.nan,1.0],
'formula.mean_fitting'                : True,
'formula.criteria'                    : 'RMSE_train',
'formula.n_multi'                     : 1,
'formula.vif_max'                     : 5.0,
'formula.n_cros'                      : 5,
'formula.n_formula'                   : 3,
'formula.python_path'                 : python_path,
'formula.scr_dir'                     : scr_dir,
'formula.middle_left_frame_width'     : 1000,
#----------- estimate -----------
'estimate.gis_fnam'                   : gis_fnam,
'estimate.event_fnam'                 : os.path.join(main_s2_analysis,'phenology','phenology.csv'),
'estimate.data_select'                : 'Days from Assessment',
'estimate.harvest_value'              : -10.0,
'estimate.assess_value'               : 0.0,
'estimate.head_value'                 : 35.0,
'estimate.peak_value'                 : 35.0,
'estimate.plant_value'                : 95.0,
'estimate.age_value'                  : 95.0,
'estimate.spec_date'                  : '',
'estimate.atcor_flag'                 : True,
'estimate.pm_fnam'                    : os.path.join(main_s2_analysis,'formula','pm_formula_age_90_110.csv'),
'estimate.pm_number'                  : 1,
'estimate.y_params'                   : [True,False,False,False,False,False],
'estimate.ax1_zmin'                   : [0.0,0.0,0.0,0.0,0.0,0.0],
'estimate.ax1_zmax'                   : [100.0,100.0,100.0,100.0,100.0,100.0],
'estimate.ax1_zstp'                   : [20.0,20.0,20.0,20.0,20.0,20.0],
'estimate.python_path'                : python_path,
'estimate.scr_dir'                    : scr_dir,
'estimate.middle_left_frame_width'    : 1000,
})
config = configparser.ConfigParser(config_defaults)

# Read configuration
if (len(sys.argv) > 1) and os.path.exists(sys.argv[1]):
    fnam = sys.argv[1]
    config.read(fnam,encoding='utf-8')
else:
    fnam = os.path.join(cnf_dir,'satellite_config.ini')
    if os.path.exists(fnam):
        config.read(fnam,encoding='utf-8')

# Configure parameters
#----------- main -----------
if not 'main' in config:
    config['main'] = {}
blocks = eval(config['main'].get('main.blocks'))
date_format = config['main'].get('main.date_format')
date_fmt = date_format.replace('yyyy','%Y').replace('yy','%y').replace('mmm','%b').replace('mm','%m').replace('dd','%d').replace('&','')
start_date = config['main'].get('main.start_date')
end_date = config['main'].get('main.end_date')
first_date = config['main'].get('main.first_date')
if first_date == '':
    start_dtim = datetime.strptime(start_date,date_fmt)
    first_date = (start_dtim-timedelta(days=90)).strftime(date_fmt)
last_date = config['main'].get('main.last_date')
if last_date == '':
    end_dtim = datetime.strptime(end_date,date_fmt)
    last_dtim = end_dtim+timedelta(days=210)
    if last_dtim > now_dtim:
        last_dtim = now_dtim
    last_date = last_dtim.strftime(date_fmt)
obs_block = config['main'].get('main.obs_block')
obs_date = config['main'].get('main.obs_date')
field_data = os.path.normpath(config['main'].get('main.field_data'))
drone_analysis = os.path.normpath(config['main'].get('main.drone_analysis'))
s1_data = os.path.normpath(config['main'].get('main.s1_data'))
s1_analysis = os.path.normpath(config['main'].get('main.s1_analysis'))
s2_data = os.path.normpath(config['main'].get('main.s2_data'))
s2_analysis = os.path.normpath(config['main'].get('main.s2_analysis'))
browse_image = os.path.normpath(config['main'].get('main.browse_image'))
no_gui = config['main'].getboolean('main.no_gui')
window_width = config['main'].getint('main.window_width')
top_frame_height = config['main'].getint('main.top_frame_height')
left_frame_width = config['main'].getint('main.left_frame_width')
right_frame_width = config['main'].getint('main.right_frame_width')
left_cnv_height = config['main'].getint('main.left_cnv_height')
right_cnv_height = config['main'].getint('main.right_cnv_height')
center_btn_width = config['main'].getint('main.center_btn_width')
#----------- subprocess -----------
pnams = []
pnams.append('download')
pnams.append('geocor')
pnams.append('indices')
pnams.append('parcel')
pnams.append('atcor')
pnams.append('interp')
pnams.append('phenology')
pnams.append('extract')
pnams.append('formula')
pnams.append('estimate')
modules = {}
titles = {}
defaults = {}
for proc in pnams:
    modules[proc] = eval('proc_{}'.format(proc))
    titles[proc] = modules[proc].proc_title
    defaults[proc] = config['main'].getboolean('main.{}'.format(proc))
    if not proc in config:
        config[proc] = {}
    for pnam in modules[proc].pnams:
        if modules[proc].input_types[pnam] in ['ask_file','ask_folder']:
            modules[proc].flag_fix[pnam] = False
            fnam = config[proc].get('{}.{}'.format(proc,pnam)).strip()
            if len(fnam) < 1:
                modules[proc].values[pnam] = fnam
            else:
                if fnam[0] == '!':
                    modules[proc].flag_fix[pnam] = True
                    fnam = fnam[1:]
                modules[proc].values[pnam] = os.path.normpath(fnam)
        elif modules[proc].input_types[pnam] in ['ask_files','ask_folders']:
            lines = config[proc].get('{}.{}'.format(proc,pnam)).strip()
            if len(lines) < 1:
                modules[proc].values[pnam] = lines
            else:
                fnams = []
                for line in lines.splitlines():
                    if len(line) < 1:
                        continue
                    fnams.append(os.path.normpath(line))
                modules[proc].values[pnam] = '\n'.join(fnams)
        elif modules[proc].param_types[pnam] in ['string','string_select']:
            modules[proc].values[pnam] = config[proc].get('{}.{}'.format(proc,pnam))
        elif modules[proc].param_types[pnam] in ['int','int_select']:
            modules[proc].values[pnam] = config[proc].getint('{}.{}'.format(proc,pnam))
        elif modules[proc].param_types[pnam] in ['float','float_select']:
            modules[proc].values[pnam] = config[proc].getfloat('{}.{}'.format(proc,pnam))
        elif modules[proc].param_types[pnam] in ['boolean','boolean_select']:
            modules[proc].values[pnam] = config[proc].getboolean('{}.{}'.format(proc,pnam))
        elif modules[proc].param_types[pnam] in ['float_list','float_select_list']:
            modules[proc].values[pnam] = eval(config[proc].get('{}.{}'.format(proc,pnam)).lower().replace('nan','np.nan'))
        else:
            v = config[proc].get('{}.{}'.format(proc,pnam))
            if v is None:
                raise ValueError('Errror, no such parameter >>> {}.{}'.format(proc,pnam))
            elif len(v) < 1:
                modules[proc].values[pnam] = v
            else:
                modules[proc].values[pnam] = eval(v)
    modules[proc].python_path = config[proc].get('{}.python_path'.format(proc))
    modules[proc].scr_dir = config[proc].get('{}.scr_dir'.format(proc))
    modules[proc].date_fmt = date_fmt
    modules[proc].start_date = start_date
    modules[proc].end_date = end_date
    modules[proc].first_date = first_date
    modules[proc].last_date = last_date
    modules[proc].obs_block = obs_block
    modules[proc].obs_date = obs_date
    modules[proc].field_data = field_data
    modules[proc].drone_analysis = drone_analysis
    modules[proc].s1_data = s1_data
    modules[proc].s1_analysis = s1_analysis
    modules[proc].s2_data = s2_data
    modules[proc].s2_analysis = s2_analysis
    modules[proc].browse_image = browse_image
    for pnam in ['ax1_zmin','ax1_zmax','ax1_zstp','fig_dpi',
                 'zmin_refs','zmin_nrefs','zmin_inds',
                 'zmax_refs','zmax_nrefs','zmax_inds',
                 'zstp_refs','zstp_nrefs','zstp_inds']:
        if hasattr(modules[proc],pnam):
            value = config[proc].get('{}.{}'.format(proc,pnam))
            if value is not None:
                setattr(modules[proc],pnam,eval(value.lower().replace('nan','np.nan')))
    modules[proc].middle_left_frame_width = config[proc].getint('{}.middle_left_frame_width'.format(proc))
