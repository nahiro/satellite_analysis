import numpy as np
from run_satellite_atcor import Atcor

proc_atcor = Atcor()
proc_atcor.proc_name = 'atcor'
proc_atcor.proc_title = 'Atmonspheric Correction'
proc_atcor.pnams.append('gis_fnam')
proc_atcor.pnams.append('mask_studyarea')
proc_atcor.pnams.append('mask_parcel')
proc_atcor.pnams.append('stat_fnam')
proc_atcor.pnams.append('inds_fnam')
proc_atcor.pnams.append('out_refs')
proc_atcor.pnams.append('atcor_refs')
proc_atcor.pnams.append('out_nrefs')
proc_atcor.pnams.append('atcor_nrefs')
proc_atcor.pnams.append('out_inds')
proc_atcor.pnams.append('atcor_inds')
proc_atcor.pnams.append('stat_period')
proc_atcor.pnams.append('n_ref')
proc_atcor.pnams.append('ref_band')
proc_atcor.pnams.append('ref_thr')
proc_atcor.pnams.append('clean_nmin')
proc_atcor.pnams.append('clean_band')
proc_atcor.pnams.append('clean_thr')
proc_atcor.pnams.append('cloud_flag')
proc_atcor.pnams.append('cr2_flag')
proc_atcor.pnams.append('cloud_band')
proc_atcor.pnams.append('cloud_thr')
proc_atcor.pnams.append('refs_thr')
proc_atcor.pnams.append('nrefs_thr')
proc_atcor.pnams.append('inds_thr')
proc_atcor.pnams.append('rel_thr')
proc_atcor.pnams.append('mul_thr')
proc_atcor.pnams.append('oflag')
proc_atcor.params['gis_fnam'] = 'Polygon File'
proc_atcor.params['mask_studyarea'] = 'Mask for Reference Select'
proc_atcor.params['mask_parcel'] = 'Mask for Parcellate'
proc_atcor.params['stat_fnam'] = 'Stats File'
proc_atcor.params['inds_fnam'] = 'Index File'
proc_atcor.params['out_refs'] = 'Output Reflectance'
proc_atcor.params['atcor_refs'] = 'Correct Reflectance'
proc_atcor.params['out_nrefs'] = 'Output Norm. Reflectance'
proc_atcor.params['atcor_nrefs'] = 'Correct Norm. Reflectance'
proc_atcor.params['out_inds'] = 'Output Index'
proc_atcor.params['atcor_inds'] = 'Correct Index'
proc_atcor.params['stat_period'] = 'Stats Calculation Period'
proc_atcor.params['n_ref'] = 'Reference Number'
proc_atcor.params['ref_band'] = 'Band for Reference Select'
proc_atcor.params['ref_thr'] = 'Thres. for Reference Select'
proc_atcor.params['clean_nmin'] = 'Min Clean-day Number'
proc_atcor.params['clean_band'] = 'Band for Clean-day Select'
proc_atcor.params['clean_thr'] = 'Thres. for Clean-day Select'
proc_atcor.params['cloud_flag'] = 'Cloud Rem. by Reflectance'
proc_atcor.params['cr2_flag'] = '2-step Cloud Removal'
proc_atcor.params['cloud_band'] = 'Band for Cloud Removal'
proc_atcor.params['cloud_thr'] = 'Thres. for Cloud Removal'
proc_atcor.params['refs_thr'] = 'Reflectance Thres. for Fit'
proc_atcor.params['nrefs_thr'] = 'Norm. Reflect. Thres. for Fit'
proc_atcor.params['inds_thr'] = 'Index Thres. for Fit'
proc_atcor.params['rel_thr'] = 'Relative Thres. for Fit'
proc_atcor.params['mul_thr'] = 'Thres. Factor for Fit'
proc_atcor.params['oflag'] = 'Overwrite Flag'
proc_atcor.param_types['gis_fnam'] = 'string'
proc_atcor.param_types['mask_studyarea'] = 'string'
proc_atcor.param_types['mask_parcel'] = 'string'
proc_atcor.param_types['stat_fnam'] = 'string'
proc_atcor.param_types['inds_fnam'] = 'string'
proc_atcor.param_types['out_refs'] = 'boolean_list'
proc_atcor.param_types['atcor_refs'] = 'boolean_list'
proc_atcor.param_types['out_nrefs'] = 'boolean_list'
proc_atcor.param_types['atcor_nrefs'] = 'boolean_list'
proc_atcor.param_types['out_inds'] = 'boolean_list'
proc_atcor.param_types['atcor_inds'] = 'boolean_list'
proc_atcor.param_types['stat_period'] = 'date_list'
proc_atcor.param_types['n_ref'] = 'int'
proc_atcor.param_types['ref_band'] = 'boolean_list'
proc_atcor.param_types['ref_thr'] = 'float'
proc_atcor.param_types['clean_nmin'] = 'int'
proc_atcor.param_types['clean_band'] = 'string_select'
proc_atcor.param_types['clean_thr'] = 'float_list'
proc_atcor.param_types['cloud_flag'] = 'boolean_list'
proc_atcor.param_types['cr2_flag'] = 'boolean'
proc_atcor.param_types['cloud_band'] = 'string_select'
proc_atcor.param_types['cloud_thr'] = 'float'
proc_atcor.param_types['refs_thr'] = 'float_list'
proc_atcor.param_types['nrefs_thr'] = 'float_list'
proc_atcor.param_types['inds_thr'] = 'float_list'
proc_atcor.param_types['rel_thr'] = 'float'
proc_atcor.param_types['mul_thr'] = 'float'
proc_atcor.param_types['oflag'] = 'boolean_list'
proc_atcor.param_range['n_ref'] = (10,1000000)
proc_atcor.param_range['ref_thr'] = (0.0,10.0)
proc_atcor.param_range['clean_thr'] = (0.0,10.0)
proc_atcor.param_range['clean_nmin'] = (1,10000)
proc_atcor.param_range['cloud_thr'] = (0.0,10.0)
proc_atcor.param_range['refs_thr'] = (0.0,10.0)
proc_atcor.param_range['nrefs_thr'] = (0.0,10.0)
proc_atcor.param_range['inds_thr'] = (0.0,10.0)
proc_atcor.param_range['rel_thr'] = (0.0,10.0)
proc_atcor.param_range['mul_thr'] = (0.0,10.0)
proc_atcor.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_atcor.defaults['mask_studyarea'] = 'studyarea_mask.tif'
proc_atcor.defaults['mask_parcel'] = 'parcel_mask.tif'
proc_atcor.defaults['stat_fnam'] = 'atcor_stat.tif'
proc_atcor.defaults['inds_fnam'] = 'nearest_inds.npz'
proc_atcor.defaults['out_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_atcor.defaults['atcor_refs'] = [False,False,False,False,False,False,False,False,False,False]
proc_atcor.defaults['out_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_atcor.defaults['atcor_nrefs'] = [True,True,True,True,True,True,True,False,False,False]
proc_atcor.defaults['out_inds'] = [True,True,True,True]
proc_atcor.defaults['atcor_inds'] = [True,True,False,True]
proc_atcor.defaults['stat_period'] = ['','']
proc_atcor.defaults['n_ref'] = 1000
proc_atcor.defaults['ref_band'] = [True,True,True,False,False,False,True,False,False,False]
proc_atcor.defaults['ref_thr'] = 0.035
proc_atcor.defaults['clean_nmin'] = 4
proc_atcor.defaults['clean_band'] = 'r'
proc_atcor.defaults['clean_thr'] = [0.06,0.05,1.0]
proc_atcor.defaults['cloud_flag'] = [True,True,True]
proc_atcor.defaults['cr2_flag'] = False
proc_atcor.defaults['cloud_band'] = 'r'
proc_atcor.defaults['cloud_thr'] = 0.35
proc_atcor.defaults['refs_thr'] = [0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02,0.02]
proc_atcor.defaults['nrefs_thr'] = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
proc_atcor.defaults['inds_thr'] = [0.1,0.1,0.1,0.1]
proc_atcor.defaults['rel_thr'] = 1.0
proc_atcor.defaults['mul_thr'] = 2.0
proc_atcor.defaults['oflag'] = [False,False,False,False,False]
proc_atcor.list_sizes['out_refs'] = 10
proc_atcor.list_sizes['atcor_refs'] = 10
proc_atcor.list_sizes['out_nrefs'] = 10
proc_atcor.list_sizes['atcor_nrefs'] = 10
proc_atcor.list_sizes['out_inds'] = 4
proc_atcor.list_sizes['atcor_inds'] = 4
proc_atcor.list_sizes['stat_period'] = 2
proc_atcor.list_sizes['ref_band'] = 10
proc_atcor.list_sizes['clean_band'] = 10
proc_atcor.list_sizes['clean_thr'] = 3
proc_atcor.list_sizes['cloud_flag'] = 3
proc_atcor.list_sizes['cloud_band'] = 10
proc_atcor.list_sizes['refs_thr'] = 10
proc_atcor.list_sizes['nrefs_thr'] = 10
proc_atcor.list_sizes['inds_thr'] = 4
proc_atcor.list_sizes['oflag'] = 5
proc_atcor.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.list_labels['atcor_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.list_labels['out_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_atcor.list_labels['atcor_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_atcor.list_labels['out_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_atcor.list_labels['atcor_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_atcor.list_labels['stat_period'] = ['Start :',' End :']
proc_atcor.list_labels['ref_band'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.list_labels['clean_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_atcor.list_labels['clean_thr'] = ['Mean :',' Std :',' Deviation :']
proc_atcor.list_labels['cloud_flag'] = ['Reflectance','Norm. Reflectance','Index']
proc_atcor.list_labels['cloud_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
#proc_atcor.list_labels['refs_thr'] = [' b :','  g :','  r :','  e1 :','  e2 :','  e3 :','  n1 :','  n2 :','  s1 :','  s2 :']
proc_atcor.list_labels['refs_thr'] = ['   b :','    g :','    r :','    e1 :','    e2 :','    e3 :','    n1 :','    n2 :','    s1 :','    s2 :']
proc_atcor.list_labels['nrefs_thr'] = ['Nb :',' Ng :',' Nr :',' Ne1 :',' Ne2 :',' Ne3 :',' Nn1 :',' Nn2 :',' Ns1 :',' Ns2 :']
proc_atcor.list_labels['inds_thr'] = ['NDVI :',' GNDVI :',' RGI :',' NRGI :']
proc_atcor.list_labels['oflag'] = ['mask','stats','index','factor','atcor']
proc_atcor.input_types['gis_fnam'] = 'ask_file'
proc_atcor.input_types['mask_studyarea'] = 'ask_file'
proc_atcor.input_types['mask_parcel'] = 'ask_file'
proc_atcor.input_types['stat_fnam'] = 'ask_file'
proc_atcor.input_types['inds_fnam'] = 'ask_file'
proc_atcor.input_types['out_refs'] = 'boolean_list'
proc_atcor.input_types['atcor_refs'] = 'boolean_list'
proc_atcor.input_types['out_nrefs'] = 'boolean_list'
proc_atcor.input_types['atcor_nrefs'] = 'boolean_list'
proc_atcor.input_types['out_inds'] = 'boolean_list'
proc_atcor.input_types['atcor_inds'] = 'boolean_list'
proc_atcor.input_types['stat_period'] = 'date_list'
proc_atcor.input_types['n_ref'] = 'box'
proc_atcor.input_types['ref_band'] = 'boolean_list'
proc_atcor.input_types['ref_thr'] = 'box'
proc_atcor.input_types['clean_nmin'] = 'box'
proc_atcor.input_types['clean_band'] = 'string_select'
proc_atcor.input_types['clean_thr'] = 'float_list'
proc_atcor.input_types['cloud_flag'] = 'boolean_list'
proc_atcor.input_types['cr2_flag'] = 'boolean'
proc_atcor.input_types['cloud_band'] = 'string_select'
proc_atcor.input_types['cloud_thr'] = 'box'
proc_atcor.input_types['refs_thr'] = 'float_list'
proc_atcor.input_types['nrefs_thr'] = 'float_list'
proc_atcor.input_types['inds_thr'] = 'float_list'
proc_atcor.input_types['rel_thr'] = 'box'
proc_atcor.input_types['mul_thr'] = 'box'
proc_atcor.input_types['oflag'] = 'boolean_list'
proc_atcor.flag_check['mask_studyarea'] = False
proc_atcor.flag_check['stat_fnam'] = False
proc_atcor.flag_check['inds_fnam'] = False
proc_atcor.expected['gis_fnam'] = '*.shp'
proc_atcor.expected['mask_studyarea'] = '*.tif'
proc_atcor.expected['mask_parcel'] = '*.tif'
proc_atcor.expected['stat_fnam'] = '*.tif'
proc_atcor.expected['inds_fnam'] = '*.npz'
for pnam in proc_atcor.pnams:
    proc_atcor.values[pnam] = proc_atcor.defaults[pnam]
proc_atcor.middle_left_frame_width = 1000
