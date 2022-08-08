import numpy as np
from run_satellite_interp import Interp

proc_interp = Interp()
proc_interp.proc_name = 'interp'
proc_interp.proc_title = 'Interpolate Data'
proc_interp.pnams.append('smooth1_flag')
proc_interp.pnams.append('smooth2_flag')
proc_interp.pnams.append('cflag_ref')
proc_interp.pnams.append('cflag_ind')
proc_interp.pnams.append('cflag_thr')
proc_interp.pnams.append('cflag_period')
proc_interp.pnams.append('cflag_smooth')
proc_interp.pnams.append('p_smooth')
proc_interp.pnams.append('atcor_flag')
proc_interp.pnams.append('oflag')
proc_interp.params['smooth1_flag'] = 'Cloud Rem. by Smoothing Refl.'
proc_interp.params['smooth2_flag'] = 'Cloud Rem. by Smoothing Index'
proc_interp.params['cflag_ref'] = 'Reflectance for Cloud Rem.'
proc_interp.params['cflag_ind'] = 'Index for Cloud Removal'
proc_interp.params['cflag_thr'] = 'Thres. for Cloud Removal'
proc_interp.params['cflag_period'] = 'Period for Cloud Removal'
proc_interp.params['cflag_smooth'] = 'Smoothing for Cloud Removal'
proc_interp.params['p_smooth'] = 'Smoothing Parameter'
proc_interp.params['atcor_flag'] = 'Atmospheric Correction'
proc_interp.params['oflag'] = 'Overwrite Flag'
proc_interp.param_types['smooth1_flag'] = 'boolean_list'
proc_interp.param_types['smooth2_flag'] = 'boolean_list'
proc_interp.param_types['cflag_ref'] = 'string_select'
proc_interp.param_types['cflag_ind'] = 'string_select'
proc_interp.param_types['cflag_thr'] = 'float_list'
proc_interp.param_types['cflag_period'] = 'date_list'
proc_interp.param_types['cflag_smooth'] = 'float'
proc_interp.param_types['p_smooth'] = 'float'
proc_interp.param_types['atcor_flag'] = 'boolean'
proc_interp.param_types['oflag'] = 'boolean_list'
proc_interp.param_range['cflag_thr'] = (0.0,10.0)
proc_interp.param_range['cflag_smooth'] = (0.0,1.0)
proc_interp.param_range['p_smooth'] = (0.0,1.0)
proc_interp.defaults['smooth1_flag'] = [False,False,False]
proc_interp.defaults['smooth2_flag'] = [False,False,False]
proc_interp.defaults['cflag_ref'] = 'b'
proc_interp.defaults['cflag_ind'] = 'NDVI'
proc_interp.defaults['cflag_thr'] = [0.06,0.1,0.06,0.1]
proc_interp.defaults['cflag_period'] = ['','']
proc_interp.defaults['cflag_smooth'] = 5.0e-3
proc_interp.defaults['p_smooth'] = 2.0e-3
proc_interp.defaults['atcor_flag'] = False
proc_interp.defaults['oflag'] = [False,True,False,True]
proc_interp.list_sizes['smooth1_flag'] = 3
proc_interp.list_sizes['smooth2_flag'] = 3
proc_interp.list_sizes['cflag_ref'] = 10
proc_interp.list_sizes['cflag_ind'] = 14
proc_interp.list_sizes['cflag_thr'] = 4
proc_interp.list_sizes['cflag_period'] = 2
proc_interp.list_sizes['oflag'] = 4
proc_interp.list_labels['smooth1_flag'] = ['Reflectance','Norm. Reflectance','Index']
proc_interp.list_labels['smooth2_flag'] = ['Reflectance','Norm. Reflectance','Index']
proc_interp.list_labels['cflag_ref'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_interp.list_labels['cflag_ind'] = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','Ns1','Ns2','NDVI','GNDVI','RGI','NRGI']
proc_interp.list_labels['cflag_thr'] = ['Reflectance :','',' Index :','']
proc_interp.list_labels['cflag_period'] = ['Start :',' End :']
proc_interp.list_labels['oflag'] = ['cflag','tentative cflag','interp','tentative interp']
proc_interp.input_types['smooth1_flag'] = 'boolean_list'
proc_interp.input_types['smooth2_flag'] = 'boolean_list'
proc_interp.input_types['cflag_ref'] = 'string_select'
proc_interp.input_types['cflag_ind'] = 'string_select'
proc_interp.input_types['cflag_thr'] = 'float_list'
proc_interp.input_types['cflag_period'] = 'date_list'
proc_interp.input_types['cflag_smooth'] = 'box'
proc_interp.input_types['p_smooth'] = 'box'
proc_interp.input_types['atcor_flag'] = 'boolean'
proc_interp.input_types['oflag'] = 'boolean_list'
for pnam in proc_interp.pnams:
    proc_interp.values[pnam] = proc_interp.defaults[pnam]
proc_interp.left_frame_width = 210
proc_interp.middle_left_frame_width = 1000
