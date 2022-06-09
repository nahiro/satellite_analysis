import os
import sys
import numpy as np
import configparser
from proc_orthomosaic import proc_orthomosaic
from proc_geocor import proc_geocor
from proc_indices import proc_indices
from proc_identify import proc_identify
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
main_drone_data = os.path.join(top_dir,'Drone_Data')
main_drone_analysis = os.path.join(top_dir,'Drone_Analysis')
main_browse_image = os.path.join(cnf_dir,'browse.png')
if not os.path.exists(main_browse_image):
    main_browse_image = os.path.join(HOME,'Pictures','browse.png')
gis_fnam = os.path.join(top_dir,'Shapefile','All_area_polygon_20210914','All_area_polygon_20210914.shp')
ref_fnam = os.path.join(top_dir,'WorldView','wv2_180629_pan.tif')

# Set defaults
config_defaults = dict(os.environ)
config_defaults.update({
#----------- main -----------
'main.blocks'                         : ['1A','1B','2A','2B','3A','3B','4A','4B','5','6','7A','7B','8A','8B','9A','9B','10A','10B','11A','11B','12','13','14A','14B','15'],
'main.date_format'                    : 'yyyy-mm&mmm-dd',
'main.current_block'                  : '',
'main.current_date'                   : '',
'main.field_data'                     : main_field_data,
'main.drone_data'                     : main_drone_data,
'main.drone_analysis'                 : main_drone_analysis,
'main.browse_image'                   : main_browse_image,
'main.orthomosaic'                    : True,
'main.geocor'                         : True,
'main.indices'                        : True,
'main.identify'                       : False,
'main.extract'                        : False,
'main.formula'                        : False,
'main.estimate'                       : True,
'main.window_width'                   : 600,
'main.top_frame_height'               : 120,
'main.left_frame_width'               : 30,
'main.right_frame_width'              : 100,
'main.left_cnv_height'                : 21,
'main.right_cnv_height'               : 21,
'main.center_btn_width'               : 20,
#----------- orthomosaic -----------
'orthomosaic.metashape_path'          : os.path.join(os.environ.get('PROGRAMFILES'),'Agisoft','Metashape Pro','metashape.exe'),
'orthomosaic.inpdirs'                 : os.path.join(main_drone_data,'Current'),
'orthomosaic.qmin'                    : 0.5,
'orthomosaic.xmp_flag'                : [True,True,True,True],
'orthomosaic.calib_flag'              : [False,True],
'orthomosaic.panel_fnam'              : '',
'orthomosaic.align_level'             : 'High',
'orthomosaic.preselect'               : [True,True],
'orthomosaic.point_limit'             : [40000,4000],
'orthomosaic.cam_flags'               : [False,False],
'orthomosaic.optimize_flag'           : True,
'orthomosaic.cam_params'              : [True,True,True,True,False,True,True,True,True,False,False,True],
'orthomosaic.depth_map'               : ['Medium','Aggressive'],
'orthomosaic.epsg'                    : 32748,
'orthomosaic.pixel_size'              : 0.025,
'orthomosaic.output_type'             : 'Float32',
'orthomosaic.python_path'             : python_path,
'orthomosaic.scr_dir'                 : scr_dir,
'orthomosaic.middle_left_frame_width' : 1000,
#----------- geocor -----------
'geocor.gis_fnam'                     : gis_fnam,
'geocor.ref_fnam'                     : ref_fnam,
'geocor.ref_band'                     : -1,
'geocor.ref_pixel'                    : 0.2,
'geocor.ref_margin'                   : 10.0,
'geocor.ref_range'                    : [np.nan,np.nan],
'geocor.trg_fnam'                     : os.path.join(main_drone_analysis,'Current','orthomosaic','orthomosaic.tif'),
'geocor.trg_bands'                    : [2,4],
'geocor.trg_ndvi'                     : True,
'geocor.trg_binning'                  : 0.2,
'geocor.trg_range'                    : [-10000.0,32767.0],
'geocor.init_shifts'                  : [0.0,0.0],
'geocor.part_sizes'                   : [50.0,50.0,25.0,25.0,15.0],
'geocor.gcp_intervals'                : [25.0,25.0,12.5,12.5,7.5],
'geocor.max_shifts'                   : [8.0,5.0,2.5,1.5,1.5],
'geocor.margins'                      : [12.0,7.5,3.75,2.25,2.25],
'geocor.scan_steps'                   : [2,2,1,1,1],
'geocor.resized_flags'                : [True,True,True,True],
'geocor.geocor_order'                 : '2nd',
'geocor.boundary_width'               : 0.6,
'geocor.boundary_nmin'                : 0.1,
'geocor.boundary_cmins'               : [0.01,1.3],
'geocor.boundary_rmax'                : 1.0,
'geocor.boundary_emaxs'               : [3.0,2.0,1.5],
'geocor.python_path'                  : python_path,
'geocor.scr_dir'                      : scr_dir,
'geocor.middle_left_frame_width'      : 1000,
#----------- indices -----------
'indices.inp_fnam'                    : os.path.join(main_drone_analysis,'Current','geocor','orthomosaic_geocor_np2.tif'),
'indices.out_params'                  : [False,False,False,False,False,True,True,True,True,True,True,True,False,True],
'indices.norm_bands'                  : [True,True,True,True,True],
'indices.rgi_red_band'                : 'e',
'indices.data_range'                  : [np.nan,np.nan],
'indices.python_path'                 : python_path,
'indices.scr_dir'                     : scr_dir,
'indices.middle_left_frame_width'     : 1000,
#----------- identify -----------
'identify.inp_fnam'                   : os.path.join(main_drone_analysis,'Current','geocor','orthomosaic_geocor_np2.tif'),
'identify.gcp_fnam'                   : os.path.join(main_drone_analysis,'Current','geocor','orthomosaic_resized_geocor_utm2utm.dat'),
'identify.geocor_order'               : '2nd',
'identify.epsg'                       : 32748,
'identify.obs_fnam'                   : os.path.join(main_field_data,'Current','observation.xls'),
'identify.i_sheet'                    : 1,
'identify.buffer'                     : 5.0,
'identify.bunch_nmin'                 : 5,
'identify.bunch_rmax'                 : 10.0,
'identify.bunch_emax'                 : 2.0,
'identify.point_nmin'                 : 5,
'identify.point_rmax'                 : 1.0,
'identify.point_dmax'                 : [1.0,0.5],
'identify.point_area'                 : [0.015,0.105,0.05],
'identify.criteria'                   : 'Distance from Line',
'identify.rr_param'                   : ['Lrg','S/N'],
'identify.rthr'                       : [0.0,1.0,0.01],
'identify.sthr'                       : 1.0,
'identify.data_range'                 : [np.nan,np.nan],
'identify.neighbor_size'              : [0.78,0.95],
'identify.python_path'                : python_path,
'identify.scr_dir'                    : scr_dir,
'identify.middle_left_frame_width'    : 1000,
#----------- extract -----------
'extract.inp_fnam'                    : os.path.join(main_drone_analysis,'Current','indices','orthomosaic_indices.tif'),
'extract.obs_fnam'                    : os.path.join(main_field_data,'Current','observation.xls'),
'extract.i_sheet'                     : 1,
'extract.epsg'                        : 32748,
'extract.gps_fnam'                    : os.path.join(main_drone_analysis,'Current','identify','orthomosaic_identify.csv'),
'extract.region_size'                 : [0.2,0.5],
'extract.python_path'                 : python_path,
'extract.scr_dir'                     : scr_dir,
'extract.middle_left_frame_width'     : 1000,
#----------- formula -----------
'formula.inp_fnams'                   : os.path.join(main_drone_analysis,'Current','extract','orthomosaic_indices.csv'),
'formula.age_range'                   : [-100.0,150.0],
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
'estimate.inp_fnam'                   : os.path.join(main_drone_analysis,'Current','indices','orthomosaic_indices.tif'),
'estimate.score_fnam'                 : os.path.join(main_drone_analysis,'Current','formula','score_formula_age_90_110.csv'),
'estimate.score_number'               : 1,
'estimate.intensity_fnam'             : os.path.join(main_drone_analysis,'Current','formula','intensity_formula_age_90_110.csv'),
'estimate.intensity_number'           : 1,
'estimate.digitize'                   : True,
'estimate.y_params'                   : [True,False,False,False,False,False],
'estimate.score_max'                  : [9,9,1,1,1,9],
'estimate.score_step'                 : [2,2,1,1,1,2],
'estimate.gis_fnam'                   : gis_fnam,
'estimate.buffer'                     : 1.0,
'estimate.region_size'                : 1.0,
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
current_block = config['main'].get('main.current_block')
current_date = config['main'].get('main.current_date')
field_data = os.path.normpath(config['main'].get('main.field_data'))
drone_data = os.path.normpath( config['main'].get('main.drone_data'))
drone_analysis = os.path.normpath(config['main'].get('main.drone_analysis'))
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
pnams.append('orthomosaic')
pnams.append('geocor')
pnams.append('indices')
pnams.append('identify')
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
    modules[proc].current_block = config['main'].get('main.current_block')
    modules[proc].current_date = config['main'].get('main.current_date')
    modules[proc].field_data = os.path.normpath(config['main'].get('main.field_data'))
    modules[proc].drone_data =  os.path.normpath(config['main'].get('main.drone_data'))
    modules[proc].drone_analysis = os.path.normpath(config['main'].get('main.drone_analysis'))
    modules[proc].browse_image = os.path.normpath(config['main'].get('main.browse_image'))
    modules[proc].middle_left_frame_width = config[proc].getint('{}.middle_left_frame_width'.format(proc))
