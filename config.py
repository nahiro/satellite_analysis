import os
import sys
import numpy as np
import configparser
from proc_geocor import proc_geocor
from proc_interp import proc_interp
from proc_phenology import proc_phenology
from proc_extract import proc_extract
from proc_formula import proc_formula
from proc_estimate import proc_estimate

# Set folder&file names
HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')
top_dir = os.path.join(HOME,'Work')
if not os.path.isdir(top_dir):
    top_dir = os.path.join(HOME,'Documents')
python_path = sys.executable
scr_dir = os.path.join(HOME,'Script')
cnf_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
main_field_data = os.path.join(top_dir,'Field_Data')
main_drone_analysis = os.path.join(top_dir,'Drone_Analysis')
main_s1_analysis = os.path.join(top_dir,'Sentinel-1_Analysis')
main_s2_analysis = os.path.join(top_dir,'Sentinel-2_Analysis')
main_browse_image = os.path.join(cnf_dir,'browse.png')
if not os.path.exists(main_browse_image):
    main_browse_image = os.path.join(HOME,'Pictures','browse.png')
gis_fnam = os.path.join(top_dir,'Shapefile','All_area_polygon_20210914','All_area_polygon_20210914.shp')

# Set defaults
config_defaults = dict(os.environ)
config_defaults.update({
#----------- main -----------
'main.blocks'                         : ['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15'],
'main.date_format'                    : 'yyyy-mm&mmm-dd',
'main.start_date'                     : '',
'main.end_date'                       : '',
'main.current_block'                  : '',
'main.current_date'                   : '',
'main.field_data'                     : main_field_data,
'main.drone_analysis'                 : main_drone_analysis,
'main.browse_image'                   : main_browse_image,
'main.geocor'                         : False,
'main.interp'                         : True,
'main.phenology'                      : True,
'main.extract'                        : False,
'main.formula'                        : False,
'main.estimate'                       : True,
'main.window_width'                   : 650,
'main.top_frame_height'               : 169,
'main.left_frame_width'               : 30,
'main.right_frame_width'              : 100,
'main.left_cnv_height'                : 21,
'main.right_cnv_height'               : 21,
'main.center_btn_width'               : 20,
#----------- geocor -----------
'geocor.gis_fnam'                     : gis_fnam,
'geocor.ref_fnam'                     : ref_fnam,
'geocor.ref_bands'                    : [4,-1,-1],
'geocor.ref_factors',                 : [np.nan,np.nan,np.nan],
'geocor.ref_range'                    : [np.nan,np.nan],
'geocor.trg_fnam'                     : os.path.join(main_drone_analysis,'Current','orthomosaic','orthomosaic.tif'),
'geocor.trg_bands'                    : [3,-1,-1],
'geocor.trg_factors',                 : [np.nan,np.nan,np.nan],
'geocor.trg_flags'                    : [16,-1,-1,-1,-1],
'geocor.trg_range'                    : [np.nan,np.nan],
'geocor.pixel_size'                   : 10.0,
'geocor.init_shifts'                  : [0.0,0.0],
'geocor.part_size'                    : 1000.0,
'geocor.gcp_interval'                 : 500.0,
'geocor.max_shift'                    : 30.0,
'geocor.margin'                       : 50.0,
'geocor.scan_step'                    : 1,
'geocor.geocor_order'                 : 'Auto',
'geocor.nmin'                         : 20,
'geocor.cmin'                         : 0.3,
'geocor.emaxs'                        : [3.0,2.0,2.0],
'geocor.smooth_fact'                  : [1.0e4,1.0e4],
'geocor.smooth_dmax'                  : [4.0,4.0],
'geocor.python_path'                  : python_path,
'geocor.scr_dir'                      : scr_dir,
'geocor.middle_left_frame_width'      : 1000,
#----------- phenology -----------
'phenology.inp_fnam'                  : os.path.join(main_s1_analysis,'Current','indices','orthomosaic_indices.tif'),
'phenology.atc_params'                : [90.0,10.0],
'phenology.atc_ithrs'                 : [30,35],
'phenology.atc_nthrs'                 : [-0.0005,-0.0005,-0.0003],
'phenology.middle_left_frame_width'   : 1000,
#----------- extract -----------
'extract.obs_fnam'                    : os.path.join(main_field_data,'Current','observation.xls'),
'extract.i_sheet'                     : 1,
'extract.epsg'                        : 32748,
'extract.gps_fnam'                    : os.path.join(main_drone_analysis,'Current','identify','orthomosaic_identify.csv'),
'extract.event_dates'                 : ['','',''],
'extract.python_path'                 : python_path,
'extract.scr_dir'                     : scr_dir,
'extract.middle_left_frame_width'     : 1000,
#----------- formula -----------
'formula.inp_fnams'                   : os.path.join(main_s2_analysis,'Current','extract','s2_indices.csv'),
'formula.data_select'                 : 'Days from Assessment',
'formula.assess_range'                : [-5.0,5.0],
'formula.mature_range'                : [30.0,40.0],
'formula.age_range'                   : [90.0,100.0],
'formula.n_x'                         : [1,2],
'formula.x_params'                    : [False,False,False,False,False,True,True,True,True,True,True,True,False,True],
'formula.q_params'                    : [True,True,True,True],
'formula.y_params'                    : [True,False,False,False,False,False],
'formula.score_max'                   : [9,9,1,1,1,9],
'formula.score_step'                  : [2.0,2.0,0.2,0.2,0.2,2.0],
'formula.ythr'                        : [0.2,0.2,0.2,0.2,0.2,0.2],
'formula.yfac1'                       : [1.0,np.nan,np.nan,np.nan,np.nan,np.nan],
'formula.yfac2'                       : [np.nan,1.0,np.nan,np.nan,np.nan,np.nan],
'formula.yfac3'                       : [np.nan,np.nan,1.0,np.nan,np.nan,np.nan],
'formula.yfac4'                       : [np.nan,np.nan,np.nan,1.0,np.nan,np.nan],
'formula.yfac5'                       : [np.nan,np.nan,np.nan,np.nan,1.0,np.nan],
'formula.yfac6'                       : [np.nan,np.nan,np.nan,np.nan,np.nan,1.0],
'formula.mean_fitting'                : False,
'formula.criteria'                    : 'RMSE_test',
'formula.n_multi'                     : 1,
'formula.vif_max'                     : 5.0,
'formula.n_cros'                      : 5,
'formula.n_formula'                   : 3,
'formula.python_path'                 : python_path,
'formula.scr_dir'                     : scr_dir,
'formula.middle_left_frame_width'     : 1000,
#----------- estimate -----------
'estimate.data_select'                : 'Days from Assessment',
'estimate.assess_value'               : 0.0,
'estimate.mature_value'               : 35.0,
'estimate.age_value'                  : 95.0,
'estimate.intensity_fnam'             : os.path.join(main_s2_analysis,'Current','formula','intensity_formula_age_90_110.csv'),
'estimate.intensity_number'           : 1,
'estimate.digitize'                   : False,
'estimate.y_params'                   : [True,False,False,False,False,False],
'estimate.score_max'                  : [9,9,1,1,1,9],
'estimate.score_step'                 : [2,2,1,1,1,2],
'estimate.gis_fnam'                   : gis_fnam,
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
    fnam = os.path.join(cnf_dir,'config.ini')
    if os.path.exists(fnam):
        config.read(fnam,encoding='utf-8')

# Configure parameters
#----------- main -----------
if not 'main' in config:
    config['main'] = {}
blocks = eval(config['main'].get('main.blocks'))
date_format = config['main'].get('main.date_format')
start_date = config['main'].get('main.start_date')
end_date = config['main'].get('main.end_date')
current_block = config['main'].get('main.current_block')
current_date = config['main'].get('main.current_date')
field_data = os.path.normpath(config['main'].get('main.field_data'))
drone_analysis = os.path.normpath(config['main'].get('main.drone_analysis'))
s1_analysis = os.path.normpath(config['main'].get('main.s1_analysis'))
s2_analysis = os.path.normpath(config['main'].get('main.s2_analysis'))
browse_image = os.path.normpath(config['main'].get('main.browse_image'))
window_width = config['main'].getint('main.window_width')
top_frame_height = config['main'].getint('main.top_frame_height')
left_frame_width = config['main'].getint('main.left_frame_width')
right_frame_width = config['main'].getint('main.right_frame_width')
left_cnv_height = config['main'].getint('main.left_cnv_height')
right_cnv_height = config['main'].getint('main.right_cnv_height')
center_btn_width = config['main'].getint('main.center_btn_width')
#----------- subprocess -----------
pnams = []
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
            fnam = config[proc].get('{}.{}'.format(proc,pnam)).strip()
            if len(fnam) < 1:
                modules[proc].values[pnam] = fnam
            else:
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
            modules[proc].values[pnam] = eval(config[proc].get('{}.{}'.format(proc,pnam)))
    modules[proc].python_path = config[proc].get('{}.python_path'.format(proc))
    modules[proc].scr_dir = config[proc].get('{}.scr_dir'.format(proc))
    modules[proc].start_date = config['main'].get('main.start_date')
    modules[proc].end_date = config['main'].get('main.end_date')
    modules[proc].current_block = config['main'].get('main.current_block')
    modules[proc].current_date = config['main'].get('main.current_date')
    modules[proc].field_data = os.path.normpath(config['main'].get('main.field_data'))
    modules[proc].drone_analysis = os.path.normpath(config['main'].get('main.drone_analysis'))
    modules[proc].s1_analysis = os.path.normpath(config['main'].get('main.s1_analysis'))
    modules[proc].s2_analysis = os.path.normpath(config['main'].get('main.s2_analysis'))
    modules[proc].browse_image = os.path.normpath(config['main'].get('main.browse_image'))
    modules[proc].middle_left_frame_width = config[proc].getint('{}.middle_left_frame_width'.format(proc))
