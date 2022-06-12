import numpy as np
from run_interp import Interp

proc_interp = Interp()
proc_interp.proc_name = 'interp'
proc_interp.proc_title = 'Interpolate Time-series Data'
proc_interp.pnams.append('gis_fnam')
proc_interp.pnams.append('calib_params')
proc_interp.pnams.append('cflag_sc')
proc_interp.pnams.append('cflag_red')
proc_interp.pnams.append('cflag_ndvi')
proc_interp.pnams.append('p_smooth')
proc_interp.params['gis_fnam'] = 'Polygon File'
proc_interp.params['calib_params'] = 'Calibrate Parameter'
proc_interp.params['cflag_sc'] = 'Cloud Removal by SC'
proc_interp.params['cflag_red'] = 'Cloud Removal by Red'
proc_interp.params['cflag_ndvi'] = 'Cloud Removal by NDVI'
proc_interp.params['p_smooth'] = 'Smoothing Parameter'
proc_interp.param_types['gis_fnam'] = 'string'
proc_interp.param_types['calib_params'] = 'boolean_list'
proc_interp.param_types['cflag_sc'] = 'boolean_list'
proc_interp.param_types['cflag_red'] = 'boolean_list'
proc_interp.param_types['cflag_ndvi'] = 'boolean_list'
proc_interp.param_types['p_smooth'] = 'float'
proc_interp.param_range['p_smooth'] = (0.0,1.0)
proc_interp.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_interp.defaults['calib_params'] = [False,False,False,False,False,False,False,False,False,False,False,False,False,False]
proc_interp.defaults['cflag_sc'] = '[True,True,True,True,True,True,True,True,True,True,True,True,True,True]'
proc_interp.defaults['cflag_red'] = '[False,False,False,False,False,False,False,False,False,False,False,False,False,False]'
proc_interp.defaults['cflag_ndvi'] = '[False,False,False,False,False,False,False,False,False,False,False,False,False,False]'
proc_interp.defaults['p_smooth'] = 2.0e-3
proc_interp.list_sizes['calib_params'] = 14
proc_interp.list_sizes['cflag_sc'] = 14 
proc_interp.list_sizes['cflag_red'] = 14 
proc_interp.list_sizes['cflag_ndvi'] = 14 
proc_interp.list_labels['calib_params'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
proc_interp.list_labels['cflag_sc'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
proc_interp.list_labels['cflag_red'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
proc_interp.list_labels['cflag_ndvi'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
#proc_interp.list_labels['cflag_sc'] = ['SC Flag','Time-series Smoothong']
proc_interp.input_types['gis_fnam'] = 'ask_file'
proc_interp.input_types['calib_params'] = 'boolean_list'
proc_interp.input_types['cflag_sc'] = 'boolean_list'
proc_interp.input_types['cflag_red'] = 'boolean_list'
proc_interp.input_types['cflag_ndvi'] = 'boolean_list'
proc_interp.input_types['p_smooth'] = 'box'
for pnam in proc_interp.pnams:
    proc_interp.values[pnam] = proc_interp.defaults[pnam]
proc_interp.middle_left_frame_width = 1000
