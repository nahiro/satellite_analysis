import numpy as np
from run_atcor import Atcor

proc_atcor = Atcor()
proc_atcor.proc_name = 'atcor'
proc_atcor.proc_title = 'Atmonspheric Correction'
proc_atcor.pnams.append('gis_fnam')
proc_atcor.pnams.append('mask_fnam')
proc_atcor.pnams.append('stat_fnam')
proc_atcor.pnams.append('inds_fnam')
proc_atcor.pnams.append('calib_refs')
proc_atcor.pnams.append('calib_nrefs')
proc_atcor.pnams.append('calib_inds')
proc_atcor.pnams.append('stat_period')
proc_atcor.pnams.append('n_ref')
proc_atcor.params['gis_fnam'] = 'Polygon File'
proc_atcor.params['mask_fnam'] = 'Mask File'
proc_atcor.params['stat_fnam'] = 'Stats File'
proc_atcor.params['inds_fnam'] = 'Index File'
proc_atcor.params['calib_refs'] = 'Calibrate Reflectance'
proc_atcor.params['calib_nrefs'] = 'Calibrate Norm. Reflectance'
proc_atcor.params['calib_inds'] = 'Calibrate Index'
proc_atcor.params['stat_period'] = 'Stats Calculation Period'
proc_atcor.params['n_ref'] = 'Reference Number'
###########proc_atcor.params['calib_band'] = 'Band for Calibration'
###########proc_atcor.params['calib_thr'] = 'Thres. for Calibration'
proc_atcor.param_types['gis_fnam'] = 'string'
proc_atcor.param_types['mask_fnam'] = 'string'
proc_atcor.param_types['stat_fnam'] = 'string'
proc_atcor.param_types['inds_fnam'] = 'string'
proc_atcor.param_types['calib_refs'] = 'boolean_list'
proc_atcor.param_types['calib_nrefs'] = 'boolean_list'
proc_atcor.param_types['calib_inds'] = 'boolean_list'
proc_atcor.param_types['stat_period'] = 'date_list'
proc_atcor.param_types['n_ref'] = 'int'
proc_atcor.param_range['n_ref'] = (10,1000000)
proc_atcor.param_range['p_smooth'] = (0.0,1.0)
proc_atcor.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_atcor.defaults['mask_fnam'] = 'mask.tif'
proc_atcor.defaults['stat_fnam'] = 'stat.npz'
proc_atcor.defaults['inds_fnam'] = 'inds.npy'
proc_atcor.defaults['calib_refs'] = [False,False,False,False,False,False,False,False,False,False]
proc_atcor.defaults['calib_nrefs'] = [False,False,False,False,False,False,False,False,False,False]
proc_atcor.defaults['calib_inds'] = [False,False,False,False]
proc_atcor.defaults['stat_period'] = ['','']
proc_atcor.defaults['n_ref'] = 1000
proc_atcor.list_sizes['calib_refs'] = 10
proc_atcor.list_sizes['calib_nrefs'] = 10
proc_atcor.list_sizes['calib_inds'] = 4
proc_atcor.list_sizes['stat_period'] = 2
proc_atcor.list_labels['calib_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.list_labels['calib_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_atcor.list_labels['calib_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_atcor.list_labels['stat_period'] = ['Start :',' End :']
proc_atcor.input_types['gis_fnam'] = 'ask_file'
proc_atcor.input_types['mask_fnam'] = 'ask_file'
proc_atcor.input_types['stat_fnam'] = 'ask_file'
proc_atcor.input_types['inds_fnam'] = 'ask_file'
proc_atcor.input_types['calib_refs'] = 'boolean_list'
proc_atcor.input_types['calib_nrefs'] = 'boolean_list'
proc_atcor.input_types['calib_inds'] = 'boolean_list'
proc_atcor.input_types['stat_period'] = 'date_list'
proc_atcor.input_types['n_ref'] = 'box'
proc_atcor.flag_check['mask_fnam'] = False
proc_atcor.flag_check['stat_fnam'] = False
proc_atcor.flag_check['inds_fnam'] = False
for pnam in proc_atcor.pnams:
    proc_atcor.values[pnam] = proc_atcor.defaults[pnam]
proc_atcor.middle_left_frame_width = 1000
