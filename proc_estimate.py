from run_estimate import Estimate

proc_estimate = Estimate()
proc_estimate.proc_name = 'estimate'
proc_estimate.proc_title = 'Estimate Damage'
proc_estimate.pnams.append('intensity_fnam')
proc_estimate.pnams.append('intensity_number')
proc_estimate.pnams.append('digitize')
proc_estimate.pnams.append('y_params')
proc_estimate.pnams.append('score_max')
proc_estimate.pnams.append('score_step')
proc_estimate.pnams.append('gis_fnam')
proc_estimate.params['intensity_fnam'] = 'Plot-mean/Score-mean Formula'
proc_estimate.params['intensity_number'] = 'P-m/S-m Formula Number'
proc_estimate.params['digitize'] = 'Digitize Score'
proc_estimate.params['y_params'] = 'Output Variable'
proc_estimate.params['score_max'] = 'Max Output Score'
proc_estimate.params['score_step'] = 'Score Step for Digitization'
proc_estimate.params['gis_fnam'] = 'Polygon File'
proc_estimate.param_types['intensity_fnam'] = 'string'
proc_estimate.param_types['intensity_number'] = 'int'
proc_estimate.param_types['digitize'] = 'boolean'
proc_estimate.param_types['y_params'] = 'boolean_list'
proc_estimate.param_types['score_max'] = 'int_list'
proc_estimate.param_types['score_step'] = 'int_list'
proc_estimate.param_types['gis_fnam'] = 'string'
proc_estimate.param_range['score_number'] = (1,10000)
proc_estimate.param_range['intensity_number'] = (1,10000)
proc_estimate.param_range['score_max'] = (1,65535)
proc_estimate.param_range['score_step'] = (1,65535)
proc_estimate.defaults['intensity_fnam'] = 'intensity_formula.csv'
proc_estimate.defaults['intensity_number'] = 1
proc_estimate.defaults['digitize'] = False
proc_estimate.defaults['y_params'] = [True,False,False,False,False,False]
proc_estimate.defaults['score_max'] = [9,9,1,1,1,9]
proc_estimate.defaults['score_step'] = [2,2,1,1,1,2]
proc_estimate.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_estimate.list_sizes['y_params'] = 6
proc_estimate.list_sizes['score_max'] = 6
proc_estimate.list_sizes['score_step'] = 6
proc_estimate.list_labels['y_params'] = ['BLB','Blast','Borer','Rat','Hopper','Drought']
proc_estimate.list_labels['score_max'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_estimate.list_labels['score_step'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_estimate.input_types['intensity_fnam'] = 'ask_file'
proc_estimate.input_types['intensity_number'] = 'box'
proc_estimate.input_types['digitize'] = 'boolean'
proc_estimate.input_types['y_params'] = 'boolean_list'
proc_estimate.input_types['score_max'] = 'int_list'
proc_estimate.input_types['score_step'] = 'int_list'
proc_estimate.input_types['gis_fnam'] = 'ask_file'
for pnam in proc_estimate.pnams:
    proc_estimate.values[pnam] = proc_estimate.defaults[pnam]
proc_estimate.left_frame_width = 210
proc_estimate.middle_left_frame_width = 1000
