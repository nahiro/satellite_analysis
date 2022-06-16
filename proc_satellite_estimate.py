from run_satellite_estimate import Estimate

proc_estimate = Estimate()
proc_estimate.proc_name = 'estimate'
proc_estimate.proc_title = 'Estimate Damage'
proc_estimate.pnams.append('gis_fnam')
proc_estimate.pnams.append('data_select')
proc_estimate.pnams.append('assess_value')
proc_estimate.pnams.append('mature_value')
proc_estimate.pnams.append('age_value')
proc_estimate.pnams.append('intens_fnam')
proc_estimate.pnams.append('intens_number')
proc_estimate.pnams.append('digitize')
proc_estimate.pnams.append('y_params')
proc_estimate.pnams.append('score_max')
proc_estimate.pnams.append('score_step')
proc_estimate.params['gis_fnam'] = 'Polygon File'
proc_estimate.params['data_select'] = 'Data Selection Criteria'
proc_estimate.params['assess_value'] = 'Days from Assessment'
proc_estimate.params['mature_value'] = 'Days from Heading'
proc_estimate.params['age_value'] = 'Days from Planting'
proc_estimate.params['intens_fnam'] = 'Plot-mean/Score-mean Formula'
proc_estimate.params['intens_number'] = 'P-m/S-m Formula Number'
proc_estimate.params['digitize'] = 'Digitize Score'
proc_estimate.params['y_params'] = 'Output Variable'
proc_estimate.params['score_max'] = 'Max Output Score'
proc_estimate.params['score_step'] = 'Score Step for Digitization'
proc_estimate.param_types['gis_fnam'] = 'string'
proc_estimate.param_types['data_select'] = 'string_select'
proc_estimate.param_types['assess_value'] = 'float'
proc_estimate.param_types['mature_value'] = 'float'
proc_estimate.param_types['age_value'] = 'float'
proc_estimate.param_types['intens_fnam'] = 'string'
proc_estimate.param_types['intens_number'] = 'int'
proc_estimate.param_types['digitize'] = 'boolean'
proc_estimate.param_types['y_params'] = 'boolean_list'
proc_estimate.param_types['score_max'] = 'int_list'
proc_estimate.param_types['score_step'] = 'int_list'
proc_estimate.param_range['assess_value'] = (-1000.0,1000.0)
proc_estimate.param_range['mature_value'] = (-1000.0,1000.0)
proc_estimate.param_range['age_value'] = (-1000.0,1000.0)
proc_estimate.param_range['intens_number'] = (1,10000)
proc_estimate.param_range['score_max'] = (1,65535)
proc_estimate.param_range['score_step'] = (1,65535)
proc_estimate.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_estimate.defaults['data_select'] = 'Days from Assessment'
proc_estimate.defaults['assess_value'] = 0.0
proc_estimate.defaults['mature_value'] = 35.0
proc_estimate.defaults['age_value'] = 95.0
proc_estimate.defaults['intens_fnam'] = 'intensity_formula.csv'
proc_estimate.defaults['intens_number'] = 1
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
proc_estimate.input_types['assess_value'] = 'box'
proc_estimate.input_types['mature_value'] = 'box'
proc_estimate.input_types['age_value'] = 'box'
proc_estimate.input_types['intens_fnam'] = 'ask_file'
proc_estimate.input_types['intens_number'] = 'box'
proc_estimate.input_types['digitize'] = 'boolean'
proc_estimate.input_types['y_params'] = 'boolean_list'
proc_estimate.input_types['score_max'] = 'int_list'
proc_estimate.input_types['score_step'] = 'int_list'
for pnam in proc_estimate.pnams:
    proc_estimate.values[pnam] = proc_estimate.defaults[pnam]
proc_estimate.left_frame_width = 210
proc_estimate.middle_left_frame_width = 1000
