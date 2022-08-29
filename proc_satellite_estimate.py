from run_satellite_estimate import Estimate

proc_estimate = Estimate()
proc_estimate.proc_name = 'estimate'
proc_estimate.proc_title = 'Estimate Damage'
proc_estimate.pnams.append('gis_fnam')
proc_estimate.pnams.append('data_select')
proc_estimate.pnams.append('harvest_value')
proc_estimate.pnams.append('assess_value')
proc_estimate.pnams.append('head_value')
proc_estimate.pnams.append('peak_value')
proc_estimate.pnams.append('plant_value')
proc_estimate.pnams.append('age_value')
proc_estimate.pnams.append('pm_fnam')
proc_estimate.pnams.append('pm_number')
proc_estimate.pnams.append('digitize')
proc_estimate.pnams.append('y_params')
proc_estimate.pnams.append('score_max')
proc_estimate.pnams.append('score_step')
proc_estimate.params['gis_fnam'] = 'Polygon File'
proc_estimate.params['data_select'] = 'Data Selection Criteria'
proc_estimate.params['harvest_value'] = 'Days from Harvesting (day)'
proc_estimate.params['assess_value'] = 'Days from Assessment (day)'
proc_estimate.params['head_value'] = 'Days from Heading (day)'
proc_estimate.params['peak_value'] = 'Days from Peak (day)'
proc_estimate.params['plant_value'] = 'Days from Planting (day)'
proc_estimate.params['age_value'] = 'Age Value (day)'
proc_estimate.params['pm_fnam'] = 'Plot-mean Formula'
proc_estimate.params['pm_number'] = 'Plot-mean Formula Number'
proc_estimate.params['digitize'] = 'Digitize Score'
proc_estimate.params['y_params'] = 'Output Variable'
proc_estimate.params['score_max'] = 'Max Output Score'
proc_estimate.params['score_step'] = 'Score Step for Digitization'
proc_estimate.param_types['gis_fnam'] = 'string'
proc_estimate.param_types['data_select'] = 'string_select'
proc_estimate.param_types['harvest_value'] = 'float'
proc_estimate.param_types['assess_value'] = 'float'
proc_estimate.param_types['head_value'] = 'float'
proc_estimate.param_types['peak_value'] = 'float'
proc_estimate.param_types['plant_value'] = 'float'
proc_estimate.param_types['age_value'] = 'float'
proc_estimate.param_types['pm_fnam'] = 'string'
proc_estimate.param_types['pm_number'] = 'int'
proc_estimate.param_types['digitize'] = 'boolean'
proc_estimate.param_types['y_params'] = 'boolean_list'
proc_estimate.param_types['score_max'] = 'int_list'
proc_estimate.param_types['score_step'] = 'int_list'
proc_estimate.param_range['harvest_value'] = (-1000.0,1000.0)
proc_estimate.param_range['assess_value'] = (-1000.0,1000.0)
proc_estimate.param_range['head_value'] = (-1000.0,1000.0)
proc_estimate.param_range['peak_value'] = (-1000.0,1000.0)
proc_estimate.param_range['plant_value'] = (-1000.0,1000.0)
proc_estimate.param_range['age_value'] = (-1000.0,1000.0)
proc_estimate.param_range['pm_number'] = (1,10000)
proc_estimate.param_range['score_max'] = (1,65535)
proc_estimate.param_range['score_step'] = (1,65535)
proc_estimate.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_estimate.defaults['data_select'] = 'Days from Assessment'
proc_estimate.defaults['harvest_value'] = -10.0
proc_estimate.defaults['assess_value'] = 0.0
proc_estimate.defaults['head_value'] = 35.0
proc_estimate.defaults['peak_value'] = 35.0
proc_estimate.defaults['plant_value'] = 95.0
proc_estimate.defaults['age_value'] = 95.0
proc_estimate.defaults['pm_fnam'] = 'pm_formula_age_90_110.csv'
proc_estimate.defaults['pm_number'] = 1
proc_estimate.defaults['digitize'] = False
proc_estimate.defaults['y_params'] = [True,False,False,False,False,False]
proc_estimate.defaults['score_max'] = [9,9,1,1,1,9]
proc_estimate.defaults['score_step'] = [2,2,1,1,1,2]
proc_estimate.list_sizes['data_select'] = 3
proc_estimate.list_sizes['y_params'] = 6
proc_estimate.list_sizes['score_max'] = 6
proc_estimate.list_sizes['score_step'] = 6
proc_estimate.list_labels['data_select'] = ['Days from Assessment','Days from Heading','Days from Planting']
proc_estimate.list_labels['y_params'] = ['BLB','Blast','Borer','Rat','Hopper','Drought']
proc_estimate.list_labels['score_max'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_estimate.list_labels['score_step'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_estimate.input_types['gis_fnam'] = 'ask_file'
proc_estimate.input_types['data_select'] = 'string_select'
proc_estimate.input_types['harvest_value'] = 'box'
proc_estimate.input_types['assess_value'] = 'box'
proc_estimate.input_types['head_value'] = 'box'
proc_estimate.input_types['peak_value'] = 'box'
proc_estimate.input_types['plant_value'] = 'box'
proc_estimate.input_types['age_value'] = 'box'
proc_estimate.input_types['pm_fnam'] = 'ask_file'
proc_estimate.input_types['pm_number'] = 'box'
proc_estimate.input_types['digitize'] = 'boolean'
proc_estimate.input_types['y_params'] = 'boolean_list'
proc_estimate.input_types['score_max'] = 'int_list'
proc_estimate.input_types['score_step'] = 'int_list'
for pnam in proc_estimate.pnams:
    proc_estimate.values[pnam] = proc_estimate.defaults[pnam]
proc_estimate.left_frame_width = 210
proc_estimate.middle_left_frame_width = 1000
