from run_satellite_estimate import Estimate

proc_estimate = Estimate()
proc_estimate.proc_name = 'estimate'
proc_estimate.proc_title = 'Estimate Damage'
proc_estimate.pnams.append('gis_fnam')
proc_estimate.pnams.append('event_fnam')
proc_estimate.pnams.append('data_select')
proc_estimate.pnams.append('harvest_value')
proc_estimate.pnams.append('assess_value')
proc_estimate.pnams.append('head_value')
proc_estimate.pnams.append('peak_value')
proc_estimate.pnams.append('plant_value')
proc_estimate.pnams.append('age_value')
proc_estimate.pnams.append('spec_date')
proc_estimate.pnams.append('atcor_flag')
proc_estimate.pnams.append('cloud_band')
proc_estimate.pnams.append('cloud_thr')
proc_estimate.pnams.append('pm_fnam')
proc_estimate.pnams.append('pm_number')
proc_estimate.pnams.append('y_params')
proc_estimate.params['gis_fnam'] = 'Polygon File'
proc_estimate.params['event_fnam'] = 'Event Date File'
proc_estimate.params['data_select'] = 'Data Selection Criteria'
proc_estimate.params['harvest_value'] = 'Days from Harvesting (day)'
proc_estimate.params['assess_value'] = 'Days from Assessment (day)'
proc_estimate.params['head_value'] = 'Days from Heading (day)'
proc_estimate.params['peak_value'] = 'Days from Peak (day)'
proc_estimate.params['plant_value'] = 'Days from Planting (day)'
proc_estimate.params['age_value'] = 'Age Value (day)'
proc_estimate.params['spec_date'] = 'Specific Date'
proc_estimate.params['atcor_flag'] = 'Atmospheric Correction'
proc_estimate.params['cloud_band'] = 'Band for Cloud Removal'
proc_estimate.params['cloud_thr'] = 'Thres. for Cloud Removal'
proc_estimate.params['pm_fnam'] = 'Plot-mean Formula'
proc_estimate.params['pm_number'] = 'Plot-mean Formula Number'
proc_estimate.params['y_params'] = 'Output Variable'
proc_estimate.param_types['gis_fnam'] = 'string'
proc_estimate.param_types['event_fnam'] = 'string'
proc_estimate.param_types['data_select'] = 'string_select'
proc_estimate.param_types['harvest_value'] = 'float'
proc_estimate.param_types['assess_value'] = 'float'
proc_estimate.param_types['head_value'] = 'float'
proc_estimate.param_types['peak_value'] = 'float'
proc_estimate.param_types['plant_value'] = 'float'
proc_estimate.param_types['age_value'] = 'float'
proc_estimate.param_types['spec_date'] = 'date'
proc_estimate.param_types['atcor_flag'] = 'boolean'
proc_estimate.param_types['cloud_band'] = 'string_select'
proc_estimate.param_types['cloud_thr'] = 'float_list'
proc_estimate.param_types['pm_fnam'] = 'string'
proc_estimate.param_types['pm_number'] = 'int'
proc_estimate.param_types['y_params'] = 'boolean_list'
proc_estimate.param_range['harvest_value'] = (-1000.0,1000.0)
proc_estimate.param_range['assess_value'] = (-1000.0,1000.0)
proc_estimate.param_range['head_value'] = (-1000.0,1000.0)
proc_estimate.param_range['peak_value'] = (-1000.0,1000.0)
proc_estimate.param_range['plant_value'] = (-1000.0,1000.0)
proc_estimate.param_range['age_value'] = (-1000.0,1000.0)
proc_estimate.param_range['cloud_thr'] = (0.0,1.0)
proc_estimate.param_range['pm_number'] = (1,10000)
proc_estimate.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_estimate.defaults['event_fnam'] = 'phenology.csv'
proc_estimate.defaults['data_select'] = 'Days from Assessment'
proc_estimate.defaults['harvest_value'] = -10.0
proc_estimate.defaults['assess_value'] = 0.0
proc_estimate.defaults['head_value'] = 35.0
proc_estimate.defaults['peak_value'] = 35.0
proc_estimate.defaults['plant_value'] = 95.0
proc_estimate.defaults['age_value'] = 95.0
proc_estimate.defaults['spec_date'] = ''
proc_estimate.defaults['atcor_flag'] = True
proc_estimate.defaults['cloud_band'] = 'r'
proc_estimate.defaults['cloud_thr'] = [0.35,0.8]
proc_estimate.defaults['pm_fnam'] = 'pm_formula_age_90_110.csv'
proc_estimate.defaults['pm_number'] = 1
proc_estimate.defaults['y_params'] = [True,False,False,False,False,False]
proc_estimate.list_sizes['data_select'] = 8
proc_estimate.list_sizes['cloud_band'] = 10
proc_estimate.list_sizes['cloud_thr'] = 2
proc_estimate.list_sizes['y_params'] = 6
proc_estimate.list_labels['data_select'] = ['Days from Harvesting','Days from Assessment','Days from Heading','Days from Peak','Days from Planting','Age Value','Specific Non-interpolated Data','Specific Interpolated Data']
proc_estimate.list_labels['cloud_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_estimate.list_labels['cloud_thr'] = ['Reflectance :',' Correlation :']
proc_estimate.list_labels['y_params'] = ['BLB','Blast','Borer','Rat','Hopper','Drought']
proc_estimate.input_types['gis_fnam'] = 'ask_file'
proc_estimate.input_types['event_fnam'] = 'ask_file'
proc_estimate.input_types['data_select'] = 'string_select'
proc_estimate.input_types['harvest_value'] = 'box'
proc_estimate.input_types['assess_value'] = 'box'
proc_estimate.input_types['head_value'] = 'box'
proc_estimate.input_types['peak_value'] = 'box'
proc_estimate.input_types['plant_value'] = 'box'
proc_estimate.input_types['age_value'] = 'box'
proc_estimate.input_types['spec_date'] = 'date'
proc_estimate.input_types['atcor_flag'] = 'boolean'
proc_estimate.input_types['cloud_band'] = 'string_select'
proc_estimate.input_types['cloud_thr'] = 'float_list'
proc_estimate.input_types['pm_fnam'] = 'ask_file'
proc_estimate.input_types['pm_number'] = 'box'
proc_estimate.input_types['y_params'] = 'boolean_list'
proc_estimate.flag_check['event_fnam'] = False
proc_estimate.flag_check['pm_fnam'] = False
proc_estimate.depend_proc['pm_fnam'] = ['formula']
proc_estimate.expected['gis_fnam'] = '*.shp'
proc_estimate.expected['event_fnam'] = 'assess.csv'
proc_estimate.expected['pm_fnam'] = [('pm files','pm*.csv|pm*.CSV'),'*.csv']
for pnam in proc_estimate.pnams:
    proc_estimate.values[pnam] = proc_estimate.defaults[pnam]
proc_estimate.left_frame_width = 210
proc_estimate.middle_left_frame_width = 1000
