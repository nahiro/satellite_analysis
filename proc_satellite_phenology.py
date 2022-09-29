import numpy as np
from run_satellite_phenology import Phenology

proc_phenology = Phenology()
proc_phenology.proc_name = 'phenology'
proc_phenology.proc_title = 'Estimate Event Dates'
proc_phenology.pnams.append('gis_fnam')
proc_phenology.pnams.append('mask_paddy')
proc_phenology.pnams.append('mask_parcel')
proc_phenology.pnams.append('trans_fnam')
proc_phenology.pnams.append('head_fnam')
proc_phenology.pnams.append('harvest_fnam')
proc_phenology.pnams.append('assess_fnam')
proc_phenology.pnams.append('trans_select')
proc_phenology.pnams.append('trans_indicator')
proc_phenology.pnams.append('trans_pref')
proc_phenology.pnams.append('trans_thr1')
proc_phenology.pnams.append('trans_thr2')
proc_phenology.pnams.append('trans_thr3')
proc_phenology.pnams.append('trans_thr4')
proc_phenology.pnams.append('trans_thr5')
proc_phenology.pnams.append('atc_params')
proc_phenology.pnams.append('assess_dthrs')
proc_phenology.pnams.append('y1_smooth')
proc_phenology.pnams.append('y1_thr')
proc_phenology.params['gis_fnam'] = 'Polygon File'
proc_phenology.params['mask_paddy'] = 'Mask File for Paddy Selection'
proc_phenology.params['mask_parcel'] = 'Mask File for Parcellate'
proc_phenology.params['trans_fnam'] = 'Planting Date File'
proc_phenology.params['head_fnam'] = 'Heading Date File'
proc_phenology.params['harvest_fnam'] = 'Harvesting Date File'
proc_phenology.params['assess_fnam'] = 'Assessment Date File'
proc_phenology.params['trans_select'] = 'Planting Date Selection'
proc_phenology.params['trans_indicator'] = 'Probable Planting Indicator'
proc_phenology.params['trans_pref'] = 'Preferable Planting Date'
proc_phenology.params['trans_thr1'] = '\u03C3 Thres. for Prob. Planting (dB)'
proc_phenology.params['trans_thr2'] = '\u03C3 Thres. for Improb. Planting (dB)'
proc_phenology.params['trans_thr3'] = 'T Thres. for Prob. Planting (day)'
proc_phenology.params['trans_thr4'] = 'T Thres. for Improb. Planting (day)'
proc_phenology.params['trans_thr5'] = 'Other Threshold for Planting'
proc_phenology.params['atc_params'] = 'Parameter for Assessment'
proc_phenology.params['assess_dthrs'] = 'Date Interval for Assessment (day)'
proc_phenology.params['y1_smooth'] = 'Smoothing for Assessment'
proc_phenology.params['y1_thr'] = 'Threshold for Assessment'
proc_phenology.param_types['gis_fnam'] = 'string'
proc_phenology.param_types['mask_paddy'] = 'string'
proc_phenology.param_types['mask_parcel'] = 'string'
proc_phenology.param_types['trans_fnam'] = 'string'
proc_phenology.param_types['head_fnam'] = 'string'
proc_phenology.param_types['harvest_fnam'] = 'string'
proc_phenology.param_types['assess_fnam'] = 'string'
proc_phenology.param_types['trans_select'] = 'string'
proc_phenology.param_types['trans_indicator'] = 'string'
proc_phenology.param_types['trans_pref'] = 'date'
proc_phenology.param_types['trans_thr1'] = 'float_list'
proc_phenology.param_types['trans_thr2'] = 'float_list'
proc_phenology.param_types['trans_thr3'] = 'float_list'
proc_phenology.param_types['trans_thr4'] = 'float_list'
proc_phenology.param_types['trans_thr5'] = 'float_list'
proc_phenology.param_types['atc_params'] = 'float_list'
proc_phenology.param_types['assess_dthrs'] = 'int_list'
proc_phenology.param_types['y1_smooth'] = 'float'
proc_phenology.param_types['y1_thr'] = 'float'
proc_phenology.param_range['trans_thr1'] = (-1.0e3,1.0e3)
proc_phenology.param_range['trans_thr2'] = (-1.0e3,1.0e3)
proc_phenology.param_range['trans_thr3'] = (-1.0e3,1.0e3)
proc_phenology.param_range['trans_thr4'] = (-1.0e3,1.0e3)
proc_phenology.param_range['trans_thr5'] = (-1.0e3,1.0e3)
proc_phenology.param_range['atc_params'] = (-1000.0,1000.0)
proc_phenology.param_range['assess_dthrs'] = (0,1000)
proc_phenology.param_range['y1_smooth'] = (0.0,1.0)
proc_phenology.param_range['y1_thr'] = (-1.0,1.0)
proc_phenology.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_phenology.defaults['mask_paddy'] = 'paddy_mask.tif'
proc_phenology.defaults['mask_parcel'] = 'parcel_mask.tif'
proc_phenology.defaults['trans_fnam'] = ''
proc_phenology.defaults['head_fnam'] = ''
proc_phenology.defaults['harvest_fnam'] = ''
proc_phenology.defaults['assess_fnam'] = ''
proc_phenology.defaults['trans_select'] = 'Around Probable Planting'
proc_phenology.defaults['trans_indicator'] = '\u03C3 Min'
proc_phenology.defaults['trans_pref'] = ''
proc_phenology.defaults['trans_thr1'] = [-18.0,np.nan,-0.6,2.2,np.nan]
proc_phenology.defaults['trans_thr2'] = [-13.0,np.nan,np.nan,0.0,np.nan]
proc_phenology.defaults['trans_thr3'] = [4.0,30.0]
proc_phenology.defaults['trans_thr4'] = [np.nan,np.nan]
proc_phenology.defaults['trans_thr5'] = [2.0,30.0]
proc_phenology.defaults['atc_params'] = [100.0,10.0]
proc_phenology.defaults['assess_dthrs'] = [120,10,10]
proc_phenology.defaults['y1_smooth'] = 0.02
proc_phenology.defaults['y1_thr'] = 0.0
proc_phenology.list_sizes['trans_select'] = 2
proc_phenology.list_sizes['trans_indicator'] = 4
proc_phenology.list_sizes['trans_thr1'] = 5
proc_phenology.list_sizes['trans_thr2'] = 5
proc_phenology.list_sizes['trans_thr3'] = 2
proc_phenology.list_sizes['trans_thr4'] = 2
proc_phenology.list_sizes['trans_thr5'] = 2
proc_phenology.list_sizes['atc_params'] = 2
proc_phenology.list_sizes['assess_dthrs'] = 3
proc_phenology.list_labels['trans_select'] = ['Around Probable Planting','Probable Planting Indicator']
proc_phenology.list_labels['trans_indicator'] = ['\u03C3 Min','\u03C3 Sig','\U0001D6E5\u03C3 Avg','\U0001D6E5\u03C3 Max']
proc_phenology.list_labels['trans_thr1'] = ['Min :',' Sig :',' \U0001D6E5 Min :',' \U0001D6E5 Avg :',' \U0001D6E5 Max :']
proc_phenology.list_labels['trans_thr2'] = ['Min :',' Sig :',' \U0001D6E5 Min :',' \U0001D6E5 Avg :',' \U0001D6E5 Max :']
proc_phenology.list_labels['trans_thr3'] = ['Diff :',' Rise :']
proc_phenology.list_labels['trans_thr4'] = ['Diff :',' Rise :']
proc_phenology.list_labels['trans_thr5'] = ['Ratio (%) :',' Differ (day) :']
proc_phenology.list_labels['atc_params'] = ['Ratio (%) :',' Offset (day) :']
proc_phenology.list_labels['assess_dthrs'] = ['Planting - Harvesting (Max) :',' Heading - Peak (Max) :',' Peak - Harvesting (Min) :']
proc_phenology.input_types['gis_fnam'] = 'ask_file'
proc_phenology.input_types['mask_paddy'] = 'ask_file'
proc_phenology.input_types['mask_parcel'] = 'ask_file'
proc_phenology.input_types['trans_fnam'] = 'ask_file'
proc_phenology.input_types['head_fnam'] = 'ask_file'
proc_phenology.input_types['harvest_fnam'] = 'ask_file'
proc_phenology.input_types['assess_fnam'] = 'ask_file'
proc_phenology.input_types['trans_select'] = 'string_select'
proc_phenology.input_types['trans_indicator'] = 'string_select'
proc_phenology.input_types['trans_pref'] = 'date'
proc_phenology.input_types['trans_thr1'] = 'float_list'
proc_phenology.input_types['trans_thr2'] = 'float_list'
proc_phenology.input_types['trans_thr3'] = 'float_list'
proc_phenology.input_types['trans_thr4'] = 'float_list'
proc_phenology.input_types['trans_thr5'] = 'float_list'
proc_phenology.input_types['atc_params'] = 'float_list'
proc_phenology.input_types['assess_dthrs'] = 'int_list'
proc_phenology.input_types['y1_smooth'] = 'box'
proc_phenology.input_types['y1_thr'] = 'box'
proc_phenology.flag_check['mask_parcel'] = False
proc_phenology.flag_check['trans_fnam'] = False
proc_phenology.flag_check['head_fnam'] = False
proc_phenology.flag_check['harvest_fnam'] = False
proc_phenology.flag_check['assess_fnam'] = False
proc_phenology.expected['gis_fnam'] = '*.shp'
proc_phenology.expected['mask_paddy'] = '*.tif'
proc_phenology.expected['mask_parcel'] = '*.tif'
proc_phenology.expected['trans_fnam'] = 'planting.csv'
for pnam in proc_phenology.pnams:
    proc_phenology.values[pnam] = proc_phenology.defaults[pnam]
proc_phenology.left_frame_width = 210
proc_phenology.middle_left_frame_width = 1000
