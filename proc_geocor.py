import numpy as np
from run_geocor import Geocor

proc_geocor = Geocor()
proc_geocor.proc_name = 'geocor'
proc_geocor.proc_title = 'Geometric Correction'
proc_geocor.pnams.append('gis_fnam')
proc_geocor.pnams.append('ref_fnam')
proc_geocor.pnams.append('ref_bands')
proc_geocor.pnams.append('ref_factors')
proc_geocor.pnams.append('ref_range')
proc_geocor.pnams.append('trg_fnam')
proc_geocor.pnams.append('trg_bands')
proc_geocor.pnams.append('trg_factors')
proc_geocor.pnams.append('trg_flags')
proc_geocor.pnams.append('trg_pixel')
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
proc_geocor.pnams.append('emaxs')
proc_geocor.pnams.append('smooth_fact')
proc_geocor.pnams.append('smooth_dmax')
proc_geocor.params['gis_fnam'] = 'Polygon File'
proc_geocor.params['ref_fnam'] = 'Reference Image'
proc_geocor.params['ref_bands'] = 'Reference Band'
proc_geocor.params['ref_factors'] = 'Reference Factor'
proc_geocor.params['ref_range'] = 'Reference DN Range'
proc_geocor.params['trg_fnam'] = 'Target Image'
proc_geocor.params['trg_bands'] = 'Target Band'
proc_geocor.params['trg_factors'] = 'Target Factor'
proc_geocor.params['trg_flags'] = 'Target Flag Band'
proc_geocor.params['trg_pixel'] = 'Target Pixel Size (m)'
proc_geocor.params['trg_range'] = 'Target DN Range'
proc_geocor.params['init_shifts'] = 'Initial Shift (m)'
proc_geocor.params['part_size'] = 'Partial Image Size (m)'
proc_geocor.params['gcp_interval'] = 'GCP Interval (m)'
proc_geocor.params['max_shift'] = 'Max Shift (m)'
proc_geocor.params['margin'] = 'Image Margin (m)'
proc_geocor.params['scan_step'] = 'Scan Step (pixel)'
proc_geocor.params['geocor_order'] = 'Full-size Image Output'
proc_geocor.params['nmin'] = 'Min Boundary Ratio'
proc_geocor.params['cmin'] = 'Min Correlation Coefficient'
proc_geocor.params['emaxs'] = 'Max GCP Error (\u03C3)'
proc_geocor.params['smooth_fact'] = 'Smoothing Factor'
proc_geocor.params['smooth_dmax'] = 'Max Diff. from Smooth (m)'
proc_geocor.param_types['gis_fnam'] = 'string'
proc_geocor.param_types['ref_fnam'] = 'string'
proc_geocor.param_types['ref_bands'] = 'int_list'
proc_geocor.param_types['ref_factors'] = 'float_list'
proc_geocor.param_types['ref_range'] = 'float_list'
proc_geocor.param_types['trg_fnam'] = 'string'
proc_geocor.param_types['trg_bands'] = 'int_list'
proc_geocor.param_types['trg_factors'] = 'float_list'
proc_geocor.param_types['trg_flags'] = 'int_list'
proc_geocor.param_types['trg_pixel'] = 'float'
proc_geocor.param_types['trg_range'] = 'float_list'
proc_geocor.param_types['init_shifts'] = 'float_list'
proc_geocor.param_types['part_size'] = 'float'
proc_geocor.param_types['gcp_interval'] = 'float'
proc_geocor.param_types['max_shift'] = 'float'
proc_geocor.param_types['margin'] = 'float'
proc_geocor.param_types['scan_step'] = 'int'
proc_geocor.param_types['geocor_order'] = 'string_select'
proc_geocor.param_types['nmin'] = 'float'
proc_geocor.param_types['cmin'] = 'float'
proc_geocor.param_types['emaxs'] = 'float_list'
proc_geocor.param_types['smooth_fact'] = 'float_list'
proc_geocor.param_types['smooth_dmax'] = 'float_list'
proc_geocor.param_range['ref_bands'] = (-10000,10000)
proc_geocor.param_range['ref_factors'] = (0,1.0)
proc_geocor.param_range['ref_range'] = (-1.0e50,1.0e50)
proc_geocor.param_range['trg_bands'] = (-10000,10000)
proc_geocor.param_range['trg_factors'] = (0,1.0)
proc_geocor.param_range['trg_flags'] = (-10000,10000)
proc_geocor.param_range['trg_pixel'] = (0.0,1.0e50)
proc_geocor.param_range['trg_range'] = (-1.0e50,1.0e50)
proc_geocor.param_range['init_shifts'] = (-1.0e50,1.0e50)
proc_geocor.param_range['part_size'] = (0.0,1.0e50)
proc_geocor.param_range['gcp_interval'] = (0.0,1.0e50)
proc_geocor.param_range['max_shift'] = (0.0,1.0e50)
proc_geocor.param_range['margin'] = (0.0,1.0e50)
proc_geocor.param_range['scan_step'] = (1,1000000)
proc_geocor.param_range['nmin'] = (1.0e-6,1.0)
proc_geocor.param_range['cmin'] = (-1.0e6,1.0e6)
proc_geocor.param_range['emaxs'] = (1.0e-6,1.0e6)
proc_geocor.param_range['smooth_fact'] = (0.0,1.0e50)
proc_geocor.param_range['smooth_dmax'] = (0.0,1.0e50)
proc_geocor.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_geocor.defaults['ref_fnam'] = 'wv2_180629_pan.tif'
proc_geocor.defaults['ref_bands'] = [1,-1,-1]
proc_geocor.defaults['ref_factors'] = [np.nan,np.nan,np.nan]
proc_geocor.defaults['ref_range'] = [np.nan,np.nan]
proc_geocor.defaults['trg_fnam'] = 'test.tif'
proc_geocor.defaults['trg_bands'] = [2,-1,-1]
proc_geocor.defaults['trg_factors'] = [np.nan,np.nan,np.nan]
proc_geocor.defaults['trg_flags'] = [16,-1,-1,-1,-1]
proc_geocor.defaults['trg_pixel'] = 10.0
proc_geocor.defaults['trg_range'] = [-10000.0,32767.0]
proc_geocor.defaults['init_shifts'] = [0.0,0.0]
proc_geocor.defaults['part_size'] = [50.0,50.0,25.0,25.0,15.0]
proc_geocor.defaults['gcp_interval'] = [25.0,25.0,12.5,12.5,7.5]
proc_geocor.defaults['max_shift'] = [8.0,5.0,2.5,1.5,1.5]
proc_geocor.defaults['margin'] = [12.0,7.5,3.75,2.25,2.25]
proc_geocor.defaults['scan_step'] = [2,2,1,1,1]
proc_geocor.defaults['geocor_order'] = '2nd'
proc_geocor.defaults['nmin'] = 0.1
proc_geocor.defaults['cmin'] = 0.3
proc_geocor.defaults['emaxs'] = [3.0,2.0,1.5]
proc_geocor.defaults['smooth_fact'] = [1.0e4,1.0e4]
proc_geocor.defaults['smooth_dmax'] = [4.0,4.0]
proc_geocor.list_sizes['ref_bands'] = 3
proc_geocor.list_sizes['ref_factors'] = 3
proc_geocor.list_sizes['ref_range'] = 2
proc_geocor.list_sizes['trg_bands'] = 3
proc_geocor.list_sizes['trg_factors'] = 3
proc_geocor.list_sizes['trg_flags'] = 5
proc_geocor.list_sizes['trg_range'] = 2
proc_geocor.list_sizes['init_shifts'] = 2
proc_geocor.list_sizes['part_size'] = 5
proc_geocor.list_sizes['gcp_interval'] = 5
proc_geocor.list_sizes['max_shift'] = 5
proc_geocor.list_sizes['margin'] = 5
proc_geocor.list_sizes['scan_step'] = 5
proc_geocor.list_sizes['geocor_order'] = 4
proc_geocor.list_sizes['emaxs'] = 3
proc_geocor.list_sizes['smooth_fact'] = 2
proc_geocor.list_sizes['smooth_dmax'] = 2
proc_geocor.list_labels['ref_bands'] = ['','','']
proc_geocor.list_labels['ref_factors'] = ['','','']
proc_geocor.list_labels['ref_range'] = ['Min :',' Max :']
proc_geocor.list_labels['trg_bands'] = ['','','']
proc_geocor.list_labels['trg_factors'] = ['','','']
proc_geocor.list_labels['trg_flags'] = ['','','','','']
proc_geocor.list_labels['trg_range'] = ['Min :',' Max :']
proc_geocor.list_labels['init_shifts'] = ['Easting :',' Northing :']
proc_geocor.list_labels['part_size'] = ['','','','','']
proc_geocor.list_labels['gcp_interval'] = ['','','','','']
proc_geocor.list_labels['max_shift'] = ['','','','','']
proc_geocor.list_labels['margin'] = ['','','','','']
proc_geocor.list_labels['scan_step'] = ['','','','','']
proc_geocor.list_labels['geocor_order'] = ['0th','1st','2nd','3rd']
proc_geocor.list_labels['emaxs'] = ['','','']
proc_geocor.list_labels['smooth_fact'] = ['X :',' Y :']
proc_geocor.list_labels['smooth_dmax'] = ['X :',' Y :']
proc_geocor.input_types['gis_fnam'] = 'ask_file'
proc_geocor.input_types['ref_fnam'] = 'ask_file'
proc_geocor.input_types['ref_bands'] = 'int_list'
proc_geocor.input_types['ref_factors'] = 'float_list'
proc_geocor.input_types['ref_range'] = 'float_list'
proc_geocor.input_types['trg_fnam'] = 'ask_file'
proc_geocor.input_types['trg_bands'] = 'int_list'
proc_geocor.input_types['trg_factors'] = 'float_list'
proc_geocor.input_types['trg_flags'] = 'int_list'
proc_geocor.input_types['trg_pixel'] = 'box'
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
proc_geocor.input_types['emaxs'] = 'float_list'
proc_geocor.input_types['smooth_fact'] = 'float_list'
proc_geocor.input_types['smooth_dmax'] = 'float_list'
proc_geocor.flag_check['trg_fnam'] = False
for pnam in proc_geocor.pnams:
    proc_geocor.values[pnam] = proc_geocor.defaults[pnam]
proc_geocor.middle_left_frame_width = 1000
