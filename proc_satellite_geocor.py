import numpy as np
from run_satellite_geocor import Geocor

proc_geocor = Geocor()
proc_geocor.proc_name = 'geocor'
proc_geocor.proc_title = 'Geometric Correction'
proc_geocor.pnams.append('l2a_dir')
proc_geocor.pnams.append('search_key')
proc_geocor.pnams.append('unzip')
proc_geocor.pnams.append('ref_fnam')
proc_geocor.pnams.append('ref_bands')
proc_geocor.pnams.append('ref_factors')
proc_geocor.pnams.append('ref_range')
proc_geocor.pnams.append('trg_subset')
proc_geocor.pnams.append('trg_resample')
proc_geocor.pnams.append('trg_pixel')
proc_geocor.pnams.append('trg_bands')
proc_geocor.pnams.append('trg_factors')
proc_geocor.pnams.append('trg_flags')
proc_geocor.pnams.append('trg_range')
proc_geocor.pnams.append('init_shifts')
proc_geocor.pnams.append('part_size')
proc_geocor.pnams.append('gcp_interval')
proc_geocor.pnams.append('max_shift')
proc_geocor.pnams.append('margin')
proc_geocor.pnams.append('scan_step')
proc_geocor.pnams.append('geocor_order')
proc_geocor.pnams.append('nmin')
proc_geocor.pnams.append('cmin')
proc_geocor.pnams.append('rmax')
proc_geocor.pnams.append('emaxs')
proc_geocor.pnams.append('smooth_fact')
proc_geocor.pnams.append('smooth_dmax')
proc_geocor.pnams.append('oflag')
proc_geocor.params['l2a_dir'] = 'Sentinel-2 L2A Folder'
proc_geocor.params['search_key'] = 'Search Keyword for L2A'
proc_geocor.params['unzip'] = 'Unzip Command'
proc_geocor.params['ref_fnam'] = 'Reference Image'
proc_geocor.params['ref_bands'] = 'Reference Band'
proc_geocor.params['ref_factors'] = 'Reference Factor'
proc_geocor.params['ref_range'] = 'Reference DN Range'
proc_geocor.params['trg_subset'] = 'Target Subset Region (\u00B0)'
proc_geocor.params['trg_resample'] = 'Target Resample Region (m)'
proc_geocor.params['trg_pixel'] = 'Target Pixel Size (m)'
proc_geocor.params['trg_bands'] = 'Target Band'
proc_geocor.params['trg_factors'] = 'Target Factor'
proc_geocor.params['trg_flags'] = 'Target Flag Band'
proc_geocor.params['trg_range'] = 'Target DN Range'
proc_geocor.params['init_shifts'] = 'Initial Shift (m)'
proc_geocor.params['part_size'] = 'Partial Image Size (m)'
proc_geocor.params['gcp_interval'] = 'GCP Interval (m)'
proc_geocor.params['max_shift'] = 'Max Shift (m)'
proc_geocor.params['margin'] = 'Image Margin (m)'
proc_geocor.params['scan_step'] = 'Scan Step (pixel)'
proc_geocor.params['geocor_order'] = 'Order of Geom. Correction'
proc_geocor.params['nmin'] = 'Min GCP Number'
proc_geocor.params['cmin'] = 'Min Correlation Coefficient'
proc_geocor.params['rmax'] = 'Max Contrast Spread (m)'
proc_geocor.params['emaxs'] = 'Max GCP Error (\u03C3)'
proc_geocor.params['smooth_fact'] = 'Smoothing Factor'
proc_geocor.params['smooth_dmax'] = 'Max Diff. from Smooth (m)'
proc_geocor.params['oflag'] = 'Overwrite Flag'
proc_geocor.param_types['l2a_dir'] = 'string'
proc_geocor.param_types['search_key'] = 'string'
proc_geocor.param_types['unzip'] = 'string'
proc_geocor.param_types['ref_fnam'] = 'string'
proc_geocor.param_types['ref_bands'] = 'int_list'
proc_geocor.param_types['ref_factors'] = 'float_list'
proc_geocor.param_types['ref_range'] = 'float_list'
proc_geocor.param_types['trg_subset'] = 'float_list'
proc_geocor.param_types['trg_resample'] = 'float_list'
proc_geocor.param_types['trg_pixel'] = 'float'
proc_geocor.param_types['trg_bands'] = 'string_select_list'
proc_geocor.param_types['trg_factors'] = 'float_list'
proc_geocor.param_types['trg_flags'] = 'string_list'
proc_geocor.param_types['trg_range'] = 'float_list'
proc_geocor.param_types['init_shifts'] = 'float_list'
proc_geocor.param_types['part_size'] = 'float'
proc_geocor.param_types['gcp_interval'] = 'float'
proc_geocor.param_types['max_shift'] = 'float'
proc_geocor.param_types['margin'] = 'float'
proc_geocor.param_types['scan_step'] = 'int'
proc_geocor.param_types['geocor_order'] = 'string_select'
proc_geocor.param_types['nmin'] = 'int'
proc_geocor.param_types['cmin'] = 'float'
proc_geocor.param_types['rmax'] = 'float'
proc_geocor.param_types['emaxs'] = 'float_list'
proc_geocor.param_types['smooth_fact'] = 'float_list'
proc_geocor.param_types['smooth_dmax'] = 'float_list'
proc_geocor.param_types['oflag'] = 'boolean_list'
proc_geocor.param_range['ref_bands'] = (-10000,10000)
proc_geocor.param_range['ref_factors'] = (0,1.0)
proc_geocor.param_range['ref_range'] = (-1.0e50,1.0e50)
proc_geocor.param_range['trg_subset'] = (-360.0,360.0)
proc_geocor.param_range['trg_resample'] = (0.0,1.0e50)
proc_geocor.param_range['trg_pixel'] = (0.0,1.0e50)
proc_geocor.param_range['trg_factors'] = (0,1.0)
proc_geocor.param_range['trg_range'] = (-1.0e50,1.0e50)
proc_geocor.param_range['init_shifts'] = (-1.0e50,1.0e50)
proc_geocor.param_range['part_size'] = (0.0,1.0e50)
proc_geocor.param_range['gcp_interval'] = (0.0,1.0e50)
proc_geocor.param_range['max_shift'] = (0.0,1.0e50)
proc_geocor.param_range['margin'] = (0.0,1.0e50)
proc_geocor.param_range['scan_step'] = (1,1000000)
proc_geocor.param_range['nmin'] = (1,1000000)
proc_geocor.param_range['cmin'] = (-1.0e6,1.0e6)
proc_geocor.param_range['rmax'] = (1.0e-6,1.0e6)
proc_geocor.param_range['emaxs'] = (1.0e-6,1.0e6)
proc_geocor.param_range['smooth_fact'] = (0.0,1.0e50)
proc_geocor.param_range['smooth_dmax'] = (0.0,1.0e50)
proc_geocor.defaults['l2a_dir'] = 'L2A'
proc_geocor.defaults['search_key'] = ''
proc_geocor.defaults['unzip'] = ''
proc_geocor.defaults['ref_fnam'] = 'wv2_180629_mul.tif'
proc_geocor.defaults['ref_bands'] = [5,-1,-1]
proc_geocor.defaults['ref_factors'] = [np.nan,np.nan,np.nan]
proc_geocor.defaults['ref_range'] = [1.0e-5,np.nan]
proc_geocor.defaults['trg_subset'] = [107.201,107.367,-6.910,-6.750]
proc_geocor.defaults['trg_resample'] = [743805.0,757295.0,9235815.0,9251805.0]
proc_geocor.defaults['trg_pixel'] = 10.0
proc_geocor.defaults['trg_bands'] = ['r','-1','-1']
proc_geocor.defaults['trg_factors'] = [np.nan,np.nan,np.nan]
proc_geocor.defaults['trg_flags'] = ['quality_scene_classification','-1','-1','-1','-1']
proc_geocor.defaults['trg_range'] = [-10000.0,32767.0]
proc_geocor.defaults['init_shifts'] = [0.0,0.0]
proc_geocor.defaults['part_size'] = 1000.0
proc_geocor.defaults['gcp_interval'] = 500.0
proc_geocor.defaults['max_shift'] = 30.0
proc_geocor.defaults['margin'] = 50.0
proc_geocor.defaults['scan_step'] = 1
proc_geocor.defaults['geocor_order'] = 'Auto'
proc_geocor.defaults['nmin'] = 20
proc_geocor.defaults['cmin'] = 0.3
proc_geocor.defaults['rmax'] = 100.0
proc_geocor.defaults['emaxs'] = [3.0,2.0,2.0]
proc_geocor.defaults['smooth_fact'] = [1.0e4,1.0e4]
proc_geocor.defaults['smooth_dmax'] = [4.0,4.0]
proc_geocor.defaults['oflag'] = [False,False]
proc_geocor.list_sizes['ref_bands'] = 3
proc_geocor.list_sizes['ref_factors'] = 3
proc_geocor.list_sizes['ref_range'] = 2
proc_geocor.list_sizes['trg_subset'] = 4
proc_geocor.list_sizes['trg_resample'] = 4
proc_geocor.list_sizes['trg_bands'] = 3
proc_geocor.list_sizes['trg_factors'] = 3
proc_geocor.list_sizes['trg_flags'] = 5
proc_geocor.list_sizes['trg_range'] = 2
proc_geocor.list_sizes['init_shifts'] = 2
proc_geocor.list_sizes['geocor_order'] = 4
proc_geocor.list_sizes['emaxs'] = 3
proc_geocor.list_sizes['smooth_fact'] = 2
proc_geocor.list_sizes['smooth_dmax'] = 2
proc_geocor.list_sizes['oflag'] = 2
proc_geocor.list_labels['ref_bands'] = ['1 :',' 2 :',' 3 :']
proc_geocor.list_labels['ref_factors'] = ['1 :',' 2 :',' 3 :']
proc_geocor.list_labels['ref_range'] = ['Min :',' Max :']
proc_geocor.list_labels['trg_subset'] = ['Lon Min :',' Lon Max :',' Lat Min :',' Lat Max :']
proc_geocor.list_labels['trg_resample'] = ['East Min :',' East Max :',' North Min :',' North Max :']
proc_geocor.list_labels['trg_bands'] = [('1 :',['b','g','r','n1']),(' 2 :',['b','g','r','n1','-1']),(' 3 :',['b','g','r','n1','-1'])]
proc_geocor.list_labels['trg_factors'] = ['1 :',' 2 :',' 3 :']
proc_geocor.list_labels['trg_flags'] = ['1 :',' 2 :',' 3 :',' 4 :',' 5 :']
proc_geocor.list_labels['trg_range'] = ['Min :',' Max :']
proc_geocor.list_labels['init_shifts'] = ['Easting :',' Northing :']
proc_geocor.list_labels['geocor_order'] = ['Auto','1st','2nd','3rd']
proc_geocor.list_labels['emaxs'] = ['','','']
proc_geocor.list_labels['smooth_fact'] = ['X :',' Y :']
proc_geocor.list_labels['smooth_dmax'] = ['X :',' Y :']
proc_geocor.list_labels['oflag'] = ['subset','geocor']
proc_geocor.input_types['l2a_dir'] = 'ask_folder'
proc_geocor.input_types['search_key'] = 'box'
proc_geocor.input_types['unzip'] = 'box'
proc_geocor.input_types['ref_fnam'] = 'ask_file'
proc_geocor.input_types['ref_bands'] = 'int_list'
proc_geocor.input_types['ref_factors'] = 'float_list'
proc_geocor.input_types['ref_range'] = 'float_list'
proc_geocor.input_types['trg_subset'] = 'float_list'
proc_geocor.input_types['trg_resample'] = 'float_list'
proc_geocor.input_types['trg_pixel'] = 'box'
proc_geocor.input_types['trg_bands'] = 'string_select_list'
proc_geocor.input_types['trg_factors'] = 'float_list'
proc_geocor.input_types['trg_flags'] = 'string_list'
proc_geocor.input_types['trg_range'] = 'float_list'
proc_geocor.input_types['init_shifts'] = 'float_list'
proc_geocor.input_types['part_size'] = 'box'
proc_geocor.input_types['gcp_interval'] = 'box'
proc_geocor.input_types['max_shift'] = 'box'
proc_geocor.input_types['margin'] = 'box'
proc_geocor.input_types['scan_step'] = 'box'
proc_geocor.input_types['geocor_order'] = 'string_select'
proc_geocor.input_types['nmin'] = 'box'
proc_geocor.input_types['cmin'] = 'box'
proc_geocor.input_types['rmax'] = 'box'
proc_geocor.input_types['emaxs'] = 'float_list'
proc_geocor.input_types['smooth_fact'] = 'float_list'
proc_geocor.input_types['smooth_dmax'] = 'float_list'
proc_geocor.input_types['oflag'] = 'boolean_list'
proc_geocor.expected['ref_fnam'] = '*.tif'
proc_geocor.select_types['trg_bands'] = ['rw','rw','rw']
for pnam in proc_geocor.pnams:
    proc_geocor.values[pnam] = proc_geocor.defaults[pnam]
proc_geocor.middle_left_frame_width = 1000
