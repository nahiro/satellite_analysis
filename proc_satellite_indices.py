import numpy as np
from run_satellite_indices import Indices

proc_indices = Indices()
proc_indices.proc_name = 'indices'
proc_indices.proc_title = 'Calculate Indices'
proc_indices.pnams.append('resample_dir')
proc_indices.pnams.append('out_refs')
proc_indices.pnams.append('norm_bands')
proc_indices.pnams.append('out_nrefs')
proc_indices.pnams.append('rgi_red_band')
proc_indices.pnams.append('out_inds')
proc_indices.pnams.append('oflag')
proc_indices.params['resample_dir'] = 'Resample Folder'
proc_indices.params['out_refs'] = 'Output Reflectance'
proc_indices.params['norm_bands'] = 'Bands for Normalization'
proc_indices.params['out_nrefs'] = 'Output Norm. Reflectance'
proc_indices.params['rgi_red_band'] = 'Band for RGI'
proc_indices.params['out_inds'] = 'Output Index'
proc_indices.params['oflag'] = 'Overwrite Flag'
proc_indices.param_types['resample_dir'] = 'string'
proc_indices.param_types['out_refs'] = 'boolean_list'
proc_indices.param_types['norm_bands'] = 'boolean_list'
proc_indices.param_types['out_nrefs'] = 'boolean_list'
proc_indices.param_types['rgi_red_band'] = 'string'
proc_indices.param_types['out_inds'] = 'boolean_list'
proc_indices.param_types['oflag'] = 'boolean'
proc_indices.defaults['resample_dir'] = 'resample'
proc_indices.defaults['out_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_indices.defaults['norm_bands'] = [True,True,True,True,True,True,True,False,False,False]
proc_indices.defaults['out_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_indices.defaults['rgi_red_band'] = 'e1'
proc_indices.defaults['out_inds'] = [True,True,True,True]
proc_indices.defaults['oflag'] = False
proc_indices.list_sizes['out_refs'] = 10
proc_indices.list_sizes['norm_bands'] = 10
proc_indices.list_sizes['out_nrefs'] = 10
proc_indices.list_sizes['rgi_red_band'] = 10
proc_indices.list_sizes['out_inds'] = 4
proc_indices.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_indices.list_labels['norm_bands'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_indices.list_labels['out_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_indices.list_labels['rgi_red_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_indices.list_labels['out_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_indices.input_types['resample_dir'] = 'ask_folder'
proc_indices.input_types['out_refs'] = 'boolean_list'
proc_indices.input_types['norm_bands'] = 'boolean_list'
proc_indices.input_types['out_nrefs'] = 'boolean_list'
proc_indices.input_types['rgi_red_band'] = 'string_select'
proc_indices.input_types['out_inds'] = 'boolean_list'
proc_indices.input_types['oflag'] = 'boolean'
for pnam in proc_indices.pnams:
    proc_indices.values[pnam] = proc_indices.defaults[pnam]
proc_indices.middle_left_frame_width = 1000
