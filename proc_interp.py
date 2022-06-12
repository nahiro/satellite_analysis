import numpy as np
from run_interp import Interp

proc_interp = Interp()
proc_interp.proc_name = 'interp'
proc_interp.proc_title = 'Interpolate Time-series Data'
proc_interp.pnams.append('gis_fnam')
proc_interp.pnams.append('out_refs')
proc_interp.pnams.append('calib_refs')
proc_interp.pnams.append('norm_bands')
proc_interp.pnams.append('out_nrefs')
proc_interp.pnams.append('calib_nrefs')
proc_interp.pnams.append('rgi_red_band')
proc_interp.pnams.append('out_inds')
proc_interp.pnams.append('calib_inds')
proc_interp.pnams.append('cflag')
proc_interp.pnams.append('cflag_ref')
proc_interp.pnams.append('cflag_ind')
proc_interp.pnams.append('cflag_thr')
proc_interp.pnams.append('p_smooth')
proc_interp.params['gis_fnam'] = 'Polygon File'
proc_interp.params['out_refs'] = 'Output Reflectance'
proc_interp.params['calib_refs'] = 'Calibrate Reflectance'
proc_interp.params['norm_bands'] = 'Bands for Normalization'
proc_interp.params['out_nrefs'] = 'Output Normalized Ref.'
proc_interp.params['calib_nrefs'] = 'Calibrate Normalized Ref.'
proc_interp.params['rgi_red_band'] = 'Band for RGI'
proc_interp.params['out_inds'] = 'Output Index'
proc_interp.params['calib_inds'] = 'Calibrate Index'
proc_interp.params['cflag'] = 'Cloud Removal Source'
proc_interp.params['cflag_ref'] = 'Reflectance for Cloud Rem.'
proc_interp.params['cflag_ind'] = 'Index for Cloud Removal'
proc_interp.params['cflag_thr'] = 'Thres. for Cloud Removal'
proc_interp.params['p_smooth'] = 'Smoothing Parameter'
proc_interp.param_types['gis_fnam'] = 'string'
proc_interp.param_types['out_refs'] = 'boolean_list'
proc_interp.param_types['calib_refs'] = 'boolean_list'
proc_interp.param_types['norm_bands'] = 'boolean_list'
proc_interp.param_types['out_nrefs'] = 'boolean_list'
proc_interp.param_types['calib_nrefs'] = 'boolean_list'
proc_interp.param_types['rgi_red_band'] = 'string'
proc_interp.param_types['out_inds'] = 'boolean_list'
proc_interp.param_types['calib_inds'] = 'boolean_list'
proc_interp.param_types['cflag'] = 'boolean_list'
proc_interp.param_types['cflag_ref'] = 'string_select'
proc_interp.param_types['cflag_ind'] = 'string_select'
proc_interp.param_types['cflag_thr'] = 'float_list'
proc_interp.param_types['p_smooth'] = 'float'
proc_interp.param_range['cflag_thr'] = (0.0,10.0)
proc_interp.param_range['p_smooth'] = (0.0,1.0)
proc_interp.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_interp.defaults['out_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_interp.defaults['calib_refs'] = [False,False,False,False,False,False,False,False,False,False]
proc_interp.defaults['norm_bands'] = [True,True,True,True,True,True,True,True,False,False]
proc_interp.defaults['out_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_interp.defaults['calib_nrefs'] = [False,False,False,False,False,False,False,False,False,False]
proc_interp.defaults['rgi_red_band'] = 'e1'
proc_interp.defaults['out_inds'] = [True,True,True,True]
proc_interp.defaults['calib_inds'] = [False,False,False,False]
proc_interp.defaults['cflag'] = [True,False,False]
proc_interp.defaults['cflag_ref'] = 'b'
proc_interp.defaults['cflag_ind'] = 'NDVI'
proc_interp.defaults['cflag_thr'] = [0.01,0.01]
proc_interp.defaults['p_smooth'] = 2.0e-3
proc_interp.list_sizes['out_refs'] = 10
proc_interp.list_sizes['calib_refs'] = 10
proc_interp.list_sizes['norm_bands'] = 10
proc_interp.list_sizes['out_nrefs'] = 10
proc_interp.list_sizes['calib_nrefs'] = 10
proc_interp.list_sizes['rgi_red_band'] = 10
proc_interp.list_sizes['out_inds'] = 4
proc_interp.list_sizes['calib_inds'] = 4
proc_interp.list_sizes['cflag'] = 3
proc_interp.list_sizes['cflag_ref'] = 8
proc_interp.list_sizes['cflag_ind'] = 12
proc_interp.list_sizes['cflag_thr'] = 2
proc_interp.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2  ']
proc_interp.list_labels['calib_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2  ']
proc_interp.list_labels['norm_bands'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2  ']
proc_interp.list_labels['out_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2  ']
proc_interp.list_labels['calib_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2  ']
proc_interp.list_labels['rgi_red_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_interp.list_labels['out_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_interp.list_labels['calib_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_interp.list_labels['cflag'] = ['SC Flag','Reflactance','Index']
proc_interp.list_labels['cflag_ref'] = ['b','g','r','e1','e2','e3','n1','n2']
proc_interp.list_labels['cflag_ind'] = ['Nb','Ng','Nr','Ne1','Ne2','Ne3','Nn1','Nn2','NDVI','GNDVI','RGI','NRGI']
proc_interp.list_labels['cflag_thr'] = ['Reflectance :',' Index :']
#proc_interp.list_labels['cflag'] = ['SC Flag','Time-series Smoothong']
proc_interp.input_types['gis_fnam'] = 'ask_file'
proc_interp.input_types['out_refs'] = 'boolean_list'
proc_interp.input_types['calib_refs'] = 'boolean_list'
proc_interp.input_types['norm_bands'] = 'boolean_list'
proc_interp.input_types['out_nrefs'] = 'boolean_list'
proc_interp.input_types['calib_nrefs'] = 'boolean_list'
proc_interp.input_types['rgi_red_band'] = 'string_select'
proc_interp.input_types['out_inds'] = 'boolean_list'
proc_interp.input_types['calib_inds'] = 'boolean_list'
proc_interp.input_types['cflag'] = 'boolean_list'
proc_interp.input_types['cflag_ref'] = 'string_select'
proc_interp.input_types['cflag_ind'] = 'string_select'
proc_interp.input_types['cflag_thr'] = 'float_list'
proc_interp.input_types['p_smooth'] = 'box'
for pnam in proc_interp.pnams:
    proc_interp.values[pnam] = proc_interp.defaults[pnam]
proc_interp.middle_left_frame_width = 1000
