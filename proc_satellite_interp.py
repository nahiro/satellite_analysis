import numpy as np
from run_satellite_interp import Interp

proc_interp = Interp()
proc_interp.proc_name = 'interp'
proc_interp.proc_title = 'Interpolate Data'
proc_interp.pnams.append('tmgn')
proc_interp.pnams.append('cflag_thr')
proc_interp.pnams.append('p_smooth')
proc_interp.pnams.append('atcor_flag')
proc_interp.pnams.append('csv_flag')
proc_interp.pnams.append('oflag')
proc_interp.params['tmgn'] = 'Tentative Period (day)'
proc_interp.params['cflag_thr'] = 'Thres. for Cloud Removal'
proc_interp.params['p_smooth'] = 'Smoothing Parameter'
proc_interp.params['atcor_flag'] = 'Atmospheric Correction'
proc_interp.params['csv_flag'] = 'Output CSV'
proc_interp.params['oflag'] = 'Overwrite Flag'
proc_interp.param_types['tmgn'] = 'int'
proc_interp.param_types['cflag_thr'] = 'float'
proc_interp.param_types['p_smooth'] = 'float'
proc_interp.param_types['atcor_flag'] = 'boolean'
proc_interp.param_types['csv_flag'] = 'boolean'
proc_interp.param_types['oflag'] = 'boolean_list'
proc_interp.param_range['tmgn'] = (0,10000)
proc_interp.param_range['cflag_thr'] = (0.0,100.0)
proc_interp.param_range['p_smooth'] = (0.0,1.0)
proc_interp.defaults['tmgn'] = 90
proc_interp.defaults['cflag_thr'] = 3.0
proc_interp.defaults['p_smooth'] = 2.0e-3
proc_interp.defaults['atcor_flag'] = True
proc_interp.defaults['csv_flag'] = True
proc_interp.defaults['oflag'] = [False,True]
proc_interp.list_sizes['oflag'] = 2
proc_interp.list_labels['oflag'] = ['interp','tentative interp']
proc_interp.input_types['tmgn'] = 'box'
proc_interp.input_types['cflag_thr'] = 'box'
proc_interp.input_types['p_smooth'] = 'box'
proc_interp.input_types['atcor_flag'] = 'boolean'
proc_interp.input_types['csv_flag'] = 'boolean'
proc_interp.input_types['oflag'] = 'boolean_list'
for pnam in proc_interp.pnams:
    proc_interp.values[pnam] = proc_interp.defaults[pnam]
proc_interp.left_frame_width = 210
proc_interp.middle_left_frame_width = 1000
