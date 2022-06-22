import numpy as np
from run_satellite_download import Download

proc_download = Download()
proc_download.proc_name = 'download'
proc_download.proc_title = 'Download Data'
proc_download.pnams.append('drv_dir')
proc_download.pnams.append('trans_path')
proc_download.pnams.append('l2a_path')
proc_download.pnams.append('geocor_path')
proc_download.pnams.append('parcel_path')
proc_download.pnams.append('atcor_path')
proc_download.pnams.append('search_key')
proc_download.pnams.append('dflag')
proc_download.pnams.append('oflag')
proc_download.params['drv_dir'] = 'Google Drive Folder'
proc_download.params['trans_path'] = 'Planting Data on GD'
proc_download.params['l2a_path'] = 'Sentinel-2 L2A on GD'
proc_download.params['geocor_path'] = 'Sentinel-2 geocor on GD'
proc_download.params['parcel_path'] = 'Sentinel-2 parcel on GD'
proc_download.params['atcor_path'] = 'Sentinel-2 atcor on GD'
proc_download.params['search_key'] = 'Keyword for Sentinel-2 L2A'
proc_download.params['dflag'] = 'Download Flag'
proc_download.params['oflag'] = 'Overwrite Flag'
proc_download.param_types['drv_dir'] = 'string'
proc_download.param_types['trans_path'] = 'string'
proc_download.param_types['l2a_path'] = 'string'
proc_download.param_types['geocor_path'] = 'string'
proc_download.param_types['parcel_path'] = 'string'
proc_download.param_types['atcor_path'] = 'string'
proc_download.param_types['search_key'] = 'string'
proc_download.param_types['dflag'] = 'boolean_list'
proc_download.param_types['oflag'] = 'boolean_list'
proc_download.defaults['drv_dir'] = 'GoogleDrive'
proc_download.defaults['trans_path'] = '/Spatial-Information/Transplanting_date/Cihea/final/v1.4'
proc_download.defaults['l2a_path'] = '/Spatial-Information/Sentinel-2/L2A/Cihea'
proc_download.defaults['geocor_path'] = '/Spatial-Information/Sentinel-2/geocor/Cihea'
proc_download.defaults['parcel_path'] = '/Spatial-Information/Sentinel-2/parcel/Cihea'
proc_download.defaults['atcor_path'] = '/Spatial-Information/Sentinel-2/atcor/Cihea'
proc_download.defaults['search_key'] = ''
proc_download.defaults['dflag'] = [True,True,True,True,True]
proc_download.defaults['oflag'] = [False,False,False,False,False]
proc_download.list_sizes['dflag'] = 5
proc_download.list_sizes['oflag'] = 5
proc_download.list_labels['dflag'] = ['Planting Data','Sentinel-2 L2A','Sentinel-2 geocor','Sentinel-2 parcel','Sentinel-2 atcor']
proc_download.list_labels['oflag'] = ['Planting Data','Sentinel-2 L2A','Sentinel-2 geocor','Sentinel-2 parcel','Sentinel-2 atcor']
proc_download.input_types['drv_dir'] = 'ask_folder'
proc_download.input_types['trans_path'] = 'box'
proc_download.input_types['l2a_path'] = 'box'
proc_download.input_types['geocor_path'] = 'box'
proc_download.input_types['parcel_path'] = 'box'
proc_download.input_types['atcor_path'] = 'box'
proc_download.input_types['search_key'] = 'box'
proc_download.input_types['dflag'] = 'boolean_list'
proc_download.input_types['oflag'] = 'boolean_list'
for pnam in proc_download.pnams:
    proc_download.values[pnam] = proc_download.defaults[pnam]
proc_download.middle_left_frame_width = 1000
