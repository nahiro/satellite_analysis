import numpy as np
from run_satellite_parcel import Parcel

proc_parcel = Parcel()
proc_parcel.proc_name = 'parcel'
proc_parcel.proc_title = 'Parcellate Data'
proc_parcel.pnams.append('geocor_dir')
proc_parcel.pnams.append('indices_dir')
proc_parcel.pnams.append('gis_fnam')
proc_parcel.pnams.append('mask_parcel')
proc_parcel.pnams.append('out_refs')
proc_parcel.pnams.append('cr_sc_refs')
proc_parcel.pnams.append('cr_ref_refs')
proc_parcel.pnams.append('out_nrefs')
proc_parcel.pnams.append('cr_sc_nrefs')
proc_parcel.pnams.append('cr_ref_nrefs')
proc_parcel.pnams.append('out_inds')
proc_parcel.pnams.append('cr_sc_inds')
proc_parcel.pnams.append('cr_ref_inds')
proc_parcel.pnams.append('cloud_band')
proc_parcel.pnams.append('cloud_thr')
proc_parcel.pnams.append('buffer')
proc_parcel.pnams.append('csv_flag')
proc_parcel.pnams.append('oflag')
proc_parcel.params['geocor_dir'] = 'Geocor Folder'
proc_parcel.params['indices_dir'] = 'Indices Folder'
proc_parcel.params['gis_fnam'] = 'Polygon File'
proc_parcel.params['mask_parcel'] = 'Mask File for Parcellate'
proc_parcel.params['out_refs'] = 'Output Reflectance'
proc_parcel.params['cr_sc_refs'] = 'CR-SC Reflactance'
proc_parcel.params['cr_ref_refs'] = 'CR-Ref Reflactance'
proc_parcel.params['out_nrefs'] = 'Output Norm. Reflectance'
proc_parcel.params['cr_sc_nrefs'] = 'CR-SC Norm. Reflactance'
proc_parcel.params['cr_ref_nrefs'] = 'CR-Ref Norm. Reflactance'
proc_parcel.params['out_inds'] = 'Output Index'
proc_parcel.params['cr_sc_inds'] = 'CR-SC Index'
proc_parcel.params['cr_ref_inds'] = 'CR-Ref Index'
proc_parcel.params['cloud_band'] = 'Band for Cloud Removal'
proc_parcel.params['cloud_thr'] = 'Thres. for Cloud Removal'
proc_parcel.params['buffer'] = 'Buffer Radius (m)'
proc_parcel.params['csv_flag'] = 'Output CSV'
proc_parcel.params['oflag'] = 'Overwrite Flag'
proc_parcel.param_types['geocor_dir'] = 'string'
proc_parcel.param_types['indices_dir'] = 'string'
proc_parcel.param_types['gis_fnam'] = 'string'
proc_parcel.param_types['mask_parcel'] = 'string'
proc_parcel.param_types['out_refs'] = 'boolean_list'
proc_parcel.param_types['cr_sc_refs'] = 'boolean_list'
proc_parcel.param_types['cr_ref_refs'] = 'boolean_list'
proc_parcel.param_types['out_nrefs'] = 'boolean_list'
proc_parcel.param_types['cr_sc_nrefs'] = 'boolean_list'
proc_parcel.param_types['cr_ref_nrefs'] = 'boolean_list'
proc_parcel.param_types['out_inds'] = 'boolean_list'
proc_parcel.param_types['cr_sc_inds'] = 'boolean_list'
proc_parcel.param_types['cr_ref_inds'] = 'boolean_list'
proc_parcel.param_types['cloud_band'] = 'string_select'
proc_parcel.param_types['cloud_thr'] = 'float'
proc_parcel.param_types['buffer'] = 'float'
proc_parcel.param_types['csv_flag'] = 'boolean'
proc_parcel.param_types['oflag'] = 'boolean'
proc_parcel.param_range['cloud_thr'] = (0.0,10.0)
proc_parcel.param_range['buffer'] = (0.0,10.0e3)
proc_parcel.defaults['geocor_dir'] = 'geocor'
proc_parcel.defaults['indices_dir'] = 'indices'
proc_parcel.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_parcel.defaults['mask_parcel'] = 'parcel_mask.tif'
proc_parcel.defaults['out_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['cr_sc_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['cr_ref_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['out_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['cr_sc_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['cr_ref_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_parcel.defaults['out_inds'] = [True,True,True,True]
proc_parcel.defaults['cr_sc_inds'] = [True,True,True,True]
proc_parcel.defaults['cr_ref_inds'] = [True,True,True,True]
proc_parcel.defaults['cloud_band'] = 'r'
proc_parcel.defaults['cloud_thr'] = 0.35
proc_parcel.defaults['buffer'] = 0.0
proc_parcel.defaults['csv_flag'] = True
proc_parcel.defaults['oflag'] = False
proc_parcel.list_sizes['out_refs'] = 10
proc_parcel.list_sizes['cr_sc_refs'] = 10
proc_parcel.list_sizes['cr_ref_refs'] = 10
proc_parcel.list_sizes['out_nrefs'] = 10
proc_parcel.list_sizes['cr_sc_nrefs'] = 10
proc_parcel.list_sizes['cr_ref_nrefs'] = 10
proc_parcel.list_sizes['out_inds'] = 4
proc_parcel.list_sizes['cr_sc_inds'] = 4
proc_parcel.list_sizes['cr_ref_inds'] = 4
proc_parcel.list_sizes['cloud_band'] = 10
proc_parcel.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_parcel.list_labels['cr_sc_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_parcel.list_labels['cr_ref_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_parcel.list_labels['out_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_parcel.list_labels['cr_sc_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_parcel.list_labels['cr_ref_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_parcel.list_labels['out_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_parcel.list_labels['cr_sc_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_parcel.list_labels['cr_ref_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_parcel.list_labels['cloud_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_parcel.input_types['geocor_dir'] = 'ask_folder'
proc_parcel.input_types['indices_dir'] = 'ask_folder'
proc_parcel.input_types['gis_fnam'] = 'ask_file'
proc_parcel.input_types['mask_parcel'] = 'ask_file'
proc_parcel.input_types['out_refs'] = 'boolean_list'
proc_parcel.input_types['cr_sc_refs'] = 'boolean_list'
proc_parcel.input_types['cr_ref_refs'] = 'boolean_list'
proc_parcel.input_types['out_nrefs'] = 'boolean_list'
proc_parcel.input_types['cr_sc_nrefs'] = 'boolean_list'
proc_parcel.input_types['cr_ref_nrefs'] = 'boolean_list'
proc_parcel.input_types['out_inds'] = 'boolean_list'
proc_parcel.input_types['cr_sc_inds'] = 'boolean_list'
proc_parcel.input_types['cr_ref_inds'] = 'boolean_list'
proc_parcel.input_types['cloud_band'] = 'string_select'
proc_parcel.input_types['cloud_thr'] = 'box'
proc_parcel.input_types['buffer'] = 'box'
proc_parcel.input_types['csv_flag'] = 'boolean'
proc_parcel.input_types['oflag'] = 'boolean'
proc_parcel.flag_check['mask_parcel'] = False
proc_parcel.expected['gis_fnam'] = '*.shp'
proc_parcel.expected['mask_parcel'] = '*.tif'
for pnam in proc_parcel.pnams:
    proc_parcel.values[pnam] = proc_parcel.defaults[pnam]
proc_parcel.middle_left_frame_width = 1000
