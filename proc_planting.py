from run_planting import Planting

proc_planting = Planting()
proc_planting.proc_name = 'planting'
proc_planting.proc_title = 'Estimate Planting Date'
proc_planting.pnams.append('inp_fnam')
proc_planting.params['inp_fnam'] = 'Input File'
proc_planting.param_types['inp_fnam'] = 'string'
#proc_planting.param_range['score_number'] = (1,10000)
proc_planting.defaults['inp_fnam'] = 'input.tif'
#proc_planting.list_sizes['y_params'] = 6
#proc_planting.list_labels['xmp_flag'] = ['Calibration','Orientation','Accuracy','Antenna']
proc_planting.input_types['inp_fnam'] = 'ask_file'
for pnam in proc_planting.pnams:
    proc_planting.values[pnam] = proc_planting.defaults[pnam]
proc_planting.left_frame_width = 210
proc_planting.middle_left_frame_width = 1000
