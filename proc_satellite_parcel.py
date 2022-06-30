import numpy as np
from run_satellite_parcel import Parcel

proc_parcel = Parcel()
proc_parcel.proc_name = 'parcel'
proc_parcel.proc_title = 'Parcellate Data'
proc_parcel.pnams.append('gis_fnam')
proc_parcel.pnams.append('band_fnam')
proc_parcel.pnams.append('out_refs')
proc_parcel.pnams.append('norm_bands')
proc_parcel.pnams.append('out_nrefs')
proc_parcel.pnams.append('rgi_red_band')
proc_parcel.pnams.append('out_inds')
proc_parcel.pnams.append('sc_flag')
proc_parcel.pnams.append('cloud_flag')
proc_parcel.pnams.append('cloud_band')
proc_parcel.pnams.append('cloud_thr')
proc_parcel.pnams.append('buffer')
proc_parcel.pnams.append('oflag')
proc_parcel.params['gis_fnam'] = 'Polygon File'
proc_parcel.params['band_fnam'] = 'Sentinel-2 Band File'
proc_parcel.params['out_refs'] = 'Output Reflectance'
proc_parcel.params['norm_bands'] = 'Bands for Normalization'
proc_parcel.params['out_nrefs'] = 'Output Norm. Reflectance'
proc_parcel.params['rgi_red_band'] = 'Band for RGI'
proc_parcel.params['out_inds'] = 'Output Index'
proc_parcel.params['sc_flag'] = 'Cloud Rem. by SC Flag'
proc_parcel.params['cloud_flag'] = 'Cloud Rem. by Reflectance'
proc_parcel.params['cloud_band'] = 'Band for Cloud Removal'
proc_parcel.params['cloud_thr'] = 'Thres. for Cloud Removal'
proc_parcel.params['buffer'] = 'Buffer Radius (m)'
proc_parcel.params['oflag'] = 'Overwrite Flag'
proc_parcel.param_types['gis_fnam'] = 'string'
proc_parcel.param_types['band_fnam'] = 'string'
proc_parcel.param_types['out_refs'] = 'boolean_list'
proc_parcel.param_types['norm_bands'] = 'boolean_list'
proc_parcel.param_types['out_nrefs'] = 'boolean_list'
proc_parcel.param_types['rgi_red_band'] = 'string'
proc_parcel.param_types['out_inds'] = 'boolean_list'
proc_parcel.param_types['sc_flag'] = 'boolean_list'
proc_parcel.param_types['cloud_flag'] = 'boolean_list'
proc_parcel.param_types['cloud_band'] = 'string_select'
proc_parcel.param_types['cloud_thr'] = 'float'
proc_parcel.param_types['buffer'] = 'float'
proc_parcel.param_types['oflag'] = 'boolean_list'
proc_parcel.param_range['cloud_thr'] = (0.0,10.0)
proc_parcel.param_range['buffer'] = (0.0,10.0e3)
proc_parcel.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_parcel.defaults['band_fnam'] = 'band_names.txt'
proc_parcel.defaults['out_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['norm_bands'] = [True,True,True,True,True,True,True,False,False,False]
proc_parcel.defaults['out_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['rgi_red_band'] = 'e1'
proc_parcel.defaults['out_inds'] = [True,True,True,True]
proc_parcel.defaults['sc_flag'] = [True,True,True]
proc_parcel.defaults['cloud_flag'] = [True,True,True]
proc_parcel.defaults['cloud_band'] = 'r'
proc_parcel.defaults['cloud_thr'] = 0.35
proc_parcel.defaults['buffer'] = 1.0
proc_parcel.defaults['oflag'] = [False,False]
proc_parcel.list_sizes['out_refs'] = 10
proc_parcel.list_sizes['norm_bands'] = 10
proc_parcel.list_sizes['out_nrefs'] = 10
proc_parcel.list_sizes['rgi_red_band'] = 10
proc_parcel.list_sizes['out_inds'] = 4
proc_parcel.list_sizes['sc_flag'] = 3
proc_parcel.list_sizes['cloud_flag'] = 3
proc_parcel.list_sizes['cloud_band'] = 10
proc_parcel.list_sizes['oflag'] = 2
proc_parcel.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_parcel.list_labels['norm_bands'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_parcel.list_labels['out_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_parcel.list_labels['rgi_red_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_parcel.list_labels['out_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_parcel.list_labels['sc_flag'] = ['Reflectance','Norm. Reflectance','Index']
proc_parcel.list_labels['cloud_flag'] = ['Reflectance','Norm. Reflectance','Index']
proc_parcel.list_labels['cloud_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_parcel.list_labels['oflag'] = ['indices','parcel']
proc_parcel.input_types['gis_fnam'] = 'ask_file'
proc_parcel.input_types['band_fnam'] = 'ask_file'
proc_parcel.input_types['out_refs'] = 'boolean_list'
proc_parcel.input_types['norm_bands'] = 'boolean_list'
proc_parcel.input_types['out_nrefs'] = 'boolean_list'
proc_parcel.input_types['rgi_red_band'] = 'string_select'
proc_parcel.input_types['out_inds'] = 'boolean_list'
proc_parcel.input_types['sc_flag'] = 'boolean_list'
proc_parcel.input_types['cloud_flag'] = 'boolean_list'
proc_parcel.input_types['cloud_band'] = 'string_select'
proc_parcel.input_types['cloud_thr'] = 'box'
proc_parcel.input_types['buffer'] = 'box'
proc_parcel.input_types['oflag'] = 'boolean_list'
for pnam in proc_parcel.pnams:
    proc_parcel.values[pnam] = proc_parcel.defaults[pnam]
proc_parcel.middle_left_frame_width = 1000
