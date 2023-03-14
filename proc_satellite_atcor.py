import numpy as np
from run_satellite_atcor import Atcor

proc_atcor = Atcor()
proc_atcor.proc_name = 'atcor'
proc_atcor.proc_title = 'Atmonspheric Correction'
proc_atcor.pnams.append('geocor_dir')
proc_atcor.pnams.append('indices_dir')
proc_atcor.pnams.append('gis_fnam')
proc_atcor.pnams.append('mask_parcel')
proc_atcor.pnams.append('mask_studyarea')
proc_atcor.pnams.append('buffer_parcel')
proc_atcor.pnams.append('p1_studyarea')
proc_atcor.pnams.append('p2_studyarea')
proc_atcor.pnams.append('out_refs')
proc_atcor.pnams.append('atcor_refs')
proc_atcor.pnams.append('out_nrefs')
proc_atcor.pnams.append('atcor_nrefs')
proc_atcor.pnams.append('out_inds')
proc_atcor.pnams.append('atcor_inds')
proc_atcor.pnams.append('stat_period')
proc_atcor.pnams.append('stat_nmin')
proc_atcor.pnams.append('n_ref')
proc_atcor.pnams.append('ref_band')
proc_atcor.pnams.append('ref_thr')
proc_atcor.pnams.append('clean_nmin')
proc_atcor.pnams.append('clean_band')
proc_atcor.pnams.append('clean_thr')
proc_atcor.pnams.append('cloud_band')
proc_atcor.pnams.append('cloud_thr')
proc_atcor.pnams.append('nstp')
proc_atcor.pnams.append('rel_thr')
proc_atcor.pnams.append('fit_thr')
proc_atcor.pnams.append('csv_flag')
proc_atcor.pnams.append('oflag')
proc_atcor.params['geocor_dir'] = 'Geocor Folder'
proc_atcor.params['indices_dir'] = 'Indices Folder'
proc_atcor.params['gis_fnam'] = 'Polygon File'
proc_atcor.params['mask_parcel'] = 'Mask File for Parcellate'
proc_atcor.params['mask_studyarea'] = 'Mask File for Reference Select'
proc_atcor.params['buffer_parcel'] = 'Buffer for Parcel Mask (m)'
proc_atcor.params['p1_studyarea'] = 'Param. for Studyarea Mask (m)'
proc_atcor.params['p2_studyarea'] = 'Param. for Studyarea Mask'
proc_atcor.params['out_refs'] = 'Output Reflectance'
proc_atcor.params['atcor_refs'] = 'Correct Reflectance'
proc_atcor.params['out_nrefs'] = 'Output Norm. Reflectance'
proc_atcor.params['atcor_nrefs'] = 'Correct Norm. Reflectance'
proc_atcor.params['out_inds'] = 'Output Index'
proc_atcor.params['atcor_inds'] = 'Correct Index'
proc_atcor.params['stat_period'] = 'Stats Period (day)'
proc_atcor.params['stat_nmin'] = 'Min Stats-data Number'
proc_atcor.params['n_ref'] = 'Reference Point Number'
proc_atcor.params['ref_band'] = 'Band for Reference Select'
proc_atcor.params['ref_thr'] = 'Thres. for Reference Select'
proc_atcor.params['clean_nmin'] = 'Min Clean-day Number'
proc_atcor.params['clean_band'] = 'Band for Clean-day Select'
proc_atcor.params['clean_thr'] = 'Thres. for Clean-day Select'
proc_atcor.params['cloud_band'] = 'Band for Cloud Removal'
proc_atcor.params['cloud_thr'] = 'Thres. for Cloud Removal'
proc_atcor.params['nstp'] = 'Step Number for Fit'
proc_atcor.params['rel_thr'] = 'Max Deviation for Fit'
proc_atcor.params['fit_thr'] = 'Min Correlation for Fit'
proc_atcor.params['csv_flag'] = 'Output CSV'
proc_atcor.params['oflag'] = 'Overwrite Flag'
proc_atcor.param_types['geocor_dir'] = 'string'
proc_atcor.param_types['indices_dir'] = 'string'
proc_atcor.param_types['gis_fnam'] = 'string'
proc_atcor.param_types['mask_parcel'] = 'string'
proc_atcor.param_types['mask_studyarea'] = 'string'
proc_atcor.param_types['buffer_parcel'] = 'float'
proc_atcor.param_types['p1_studyarea'] = 'float_list'
proc_atcor.param_types['p2_studyarea'] = 'float_list'
proc_atcor.param_types['out_refs'] = 'boolean_list'
proc_atcor.param_types['atcor_refs'] = 'boolean_list'
proc_atcor.param_types['out_nrefs'] = 'boolean_list'
proc_atcor.param_types['atcor_nrefs'] = 'boolean_list'
proc_atcor.param_types['out_inds'] = 'boolean_list'
proc_atcor.param_types['atcor_inds'] = 'boolean_list'
proc_atcor.param_types['stat_period'] = 'int'
proc_atcor.param_types['stat_nmin'] = 'int'
proc_atcor.param_types['n_ref'] = 'int'
proc_atcor.param_types['ref_band'] = 'boolean_list'
proc_atcor.param_types['ref_thr'] = 'float'
proc_atcor.param_types['clean_nmin'] = 'int'
proc_atcor.param_types['clean_band'] = 'string_select'
proc_atcor.param_types['clean_thr'] = 'float_list'
proc_atcor.param_types['cloud_band'] = 'string_select'
proc_atcor.param_types['cloud_thr'] = 'float'
proc_atcor.param_types['nstp'] = 'int'
proc_atcor.param_types['rel_thr'] = 'float'
proc_atcor.param_types['fit_thr'] = 'float'
proc_atcor.param_types['csv_flag'] = 'boolean'
proc_atcor.param_types['oflag'] = 'boolean_list'
proc_atcor.param_range['buffer_parcel'] = (0.0,10.0e3)
proc_atcor.param_range['p1_studyarea'] = (0.0,10.0e3)
proc_atcor.param_range['p2_studyarea'] = (0.0,180.0)
proc_atcor.param_range['stat_period'] = (10,1000000)
proc_atcor.param_range['stat_nmin'] = (1,1000000)
proc_atcor.param_range['n_ref'] = (10,1000000)
proc_atcor.param_range['ref_thr'] = (0.0,10.0)
proc_atcor.param_range['clean_thr'] = (0.0,10.0)
proc_atcor.param_range['clean_nmin'] = (1,10000)
proc_atcor.param_range['cloud_thr'] = (0.0,10.0)
proc_atcor.param_range['nstp'] = (2,10000)
proc_atcor.param_range['rel_thr'] = (0.0,10.0)
proc_atcor.param_range['fit_thr'] = (0.0,10.0)
proc_atcor.defaults['geocor_dir'] = 'geocor'
proc_atcor.defaults['indices_dir'] = 'indices'
proc_atcor.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_atcor.defaults['mask_parcel'] = 'parcel_mask.tif'
proc_atcor.defaults['mask_studyarea'] = 'studyarea_mask.tif'
proc_atcor.defaults['buffer_parcel'] = 0.0
proc_atcor.defaults['p1_studyarea'] = [np.nan,np.nan,300.0,600.0,100.0,0.1]
proc_atcor.defaults['p2_studyarea'] = [4.0,15.0]
proc_atcor.defaults['out_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_atcor.defaults['atcor_refs'] = [True,True,True,True,True,True,True,True,True,True]
proc_atcor.defaults['out_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_atcor.defaults['atcor_nrefs'] = [True,True,True,True,True,True,True,True,True,True]
proc_atcor.defaults['out_inds'] = [True,True,True,True]
proc_atcor.defaults['atcor_inds'] = [True,True,True,True]
proc_atcor.defaults['stat_period'] = 730
proc_atcor.defaults['stat_nmin'] = 10
proc_atcor.defaults['n_ref'] = 1000
proc_atcor.defaults['ref_band'] = [True,True,True,False,False,False,True,False,False,False]
proc_atcor.defaults['ref_thr'] = 0.035
proc_atcor.defaults['clean_nmin'] = 4
proc_atcor.defaults['clean_band'] = 'r'
proc_atcor.defaults['clean_thr'] = [0.06,0.05,1.0]
proc_atcor.defaults['cloud_band'] = 'r'
proc_atcor.defaults['cloud_thr'] = 0.35
proc_atcor.defaults['nstp'] = 10
proc_atcor.defaults['rel_thr'] = 2.0
proc_atcor.defaults['fit_thr'] = 0.3
proc_atcor.defaults['csv_flag'] = True
proc_atcor.defaults['oflag'] = [False,False,False,False,False]
proc_atcor.list_sizes['p1_studyarea'] = 6
proc_atcor.list_sizes['p2_studyarea'] = 2
proc_atcor.list_sizes['out_refs'] = 10
proc_atcor.list_sizes['atcor_refs'] = 10
proc_atcor.list_sizes['out_nrefs'] = 10
proc_atcor.list_sizes['atcor_nrefs'] = 10
proc_atcor.list_sizes['out_inds'] = 4
proc_atcor.list_sizes['atcor_inds'] = 4
proc_atcor.list_sizes['ref_band'] = 10
proc_atcor.list_sizes['clean_band'] = 10
proc_atcor.list_sizes['clean_thr'] = 3
proc_atcor.list_sizes['cloud_band'] = 10
proc_atcor.list_sizes['oflag'] = 5
proc_atcor.list_labels['p1_studyarea'] = ['X0 :',' Y0 :',' Lmin :',' Lmax :',' Lstp :',' Buffer :']
proc_atcor.list_labels['p2_studyarea'] = ['Dmax :',' Athr (deg) :']
proc_atcor.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.list_labels['atcor_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.list_labels['out_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_atcor.list_labels['atcor_nrefs'] = ['Nb  ','Ng  ','Nr  ','Ne1  ','Ne2  ','Ne3  ','Nn1  ','Nn2  ','Ns1  ','Ns2']
proc_atcor.list_labels['out_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_atcor.list_labels['atcor_inds'] = ['NDVI  ','GNDVI  ','RGI  ','NRGI  ']
proc_atcor.list_labels['ref_band'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.list_labels['clean_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_atcor.list_labels['clean_thr'] = ['Mean :',' Std :',' Deviation :']
proc_atcor.list_labels['cloud_band'] = ['b','g','r','e1','e2','e3','n1','n2','s1','s2']
proc_atcor.list_labels['oflag'] = ['mask','stats','index','factor','atcor']
proc_atcor.input_types['geocor_dir'] = 'ask_folder'
proc_atcor.input_types['indices_dir'] = 'ask_folder'
proc_atcor.input_types['gis_fnam'] = 'ask_file'
proc_atcor.input_types['mask_parcel'] = 'ask_file'
proc_atcor.input_types['mask_studyarea'] = 'ask_file'
proc_atcor.input_types['buffer_parcel'] = 'box'
proc_atcor.input_types['p1_studyarea'] = 'float_list'
proc_atcor.input_types['p2_studyarea'] = 'float_list'
proc_atcor.input_types['out_refs'] = 'boolean_list'
proc_atcor.input_types['atcor_refs'] = 'boolean_list'
proc_atcor.input_types['out_nrefs'] = 'boolean_list'
proc_atcor.input_types['atcor_nrefs'] = 'boolean_list'
proc_atcor.input_types['out_inds'] = 'boolean_list'
proc_atcor.input_types['atcor_inds'] = 'boolean_list'
proc_atcor.input_types['stat_period'] = 'box'
proc_atcor.input_types['stat_nmin'] = 'box'
proc_atcor.input_types['n_ref'] = 'box'
proc_atcor.input_types['ref_band'] = 'boolean_list'
proc_atcor.input_types['ref_thr'] = 'box'
proc_atcor.input_types['clean_nmin'] = 'box'
proc_atcor.input_types['clean_band'] = 'string_select'
proc_atcor.input_types['clean_thr'] = 'float_list'
proc_atcor.input_types['cloud_band'] = 'string_select'
proc_atcor.input_types['cloud_thr'] = 'box'
proc_atcor.input_types['nstp'] = 'box'
proc_atcor.input_types['rel_thr'] = 'box'
proc_atcor.input_types['fit_thr'] = 'box'
proc_atcor.input_types['csv_flag'] = 'boolean'
proc_atcor.input_types['oflag'] = 'boolean_list'
proc_atcor.flag_check['mask_parcel'] = False
proc_atcor.flag_check['mask_studyarea'] = False
proc_atcor.expected['gis_fnam'] = '*.shp'
proc_atcor.expected['mask_parcel'] = '*.tif'
proc_atcor.expected['mask_studyarea'] = '*.tif'
for pnam in proc_atcor.pnams:
    proc_atcor.values[pnam] = proc_atcor.defaults[pnam]
proc_atcor.left_frame_width = 210
proc_atcor.middle_left_frame_width = 1000
