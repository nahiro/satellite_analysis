import numpy as np
from run_satellite_download import Download

proc_download = Download()
proc_download.proc_name = 'download'
proc_download.proc_title = 'Download Data'
proc_download.pnams.append('drv_dir')
proc_download.pnams.append('trans_path')
proc_download.pnams.append('s2_path')
proc_download.pnams.append('search_key')
proc_download.pnams.append('dflag1')
proc_download.pnams.append('dflag2')
proc_download.pnams.append('dflag3')
proc_download.pnams.append('dflag4')
proc_download.pnams.append('dflag5')
proc_download.params['drv_dir'] = 'Google Drive Folder'
proc_download.params['trans_path'] = 'Planting Folder on GD'
proc_download.params['s2_path'] = 'Sentinel-2 Folder on GD'
proc_download.params['search_key'] = 'Keyword for Sentinel-2 Data'
proc_download.params['dflag1'] = 'Download'
proc_download.params['dflag2'] = 'Download'
proc_download.params['dflag3'] = 'Download'
proc_download.params['dflag4'] = 'Download'
proc_download.params['dflag5'] = 'Download'
proc_download.param_types['drv_dir'] = 'string'
proc_download.param_types['trans_path'] = 'string'
proc_download.param_types['s2_path'] = 'string'
proc_download.param_types['search_key'] = 'string'
proc_download.param_types['dflag1'] = 'boolean'
proc_download.param_types['dflag2'] = 'boolean'
proc_download.param_types['dflag3'] = 'boolean'
proc_download.param_types['dflag4'] = 'boolean'
proc_download.param_types['dflag5'] = 'boolean'
proc_download.defaults['drv_dir'] = 'GoogleDrive'
proc_download.defaults['trans_path'] = '/Spatial-Information/Transplanting_date/Cihea/final/v1.4'
proc_download.defaults['s2_path'] = '/Spatial-Information/Sentinel-2/L2A/Cihea'
proc_download.defaults['search_key'] = ''
proc_download.defaults['dflag1'] = True
proc_download.defaults['dflag2'] = True
proc_download.defaults['dflag3'] = True
proc_download.defaults['dflag4'] = True
proc_download.defaults['dflag5'] = True
proc_download.list_sizes['dflag1'] = 1
proc_download.list_sizes['dflag2'] = 1
proc_download.list_sizes['dflag3'] = 1
proc_download.list_sizes['dflag4'] = 1
proc_download.list_sizes['dflag5'] = 1
proc_download.list_labels['dflag1'] = ['Planting Data']
proc_download.list_labels['dflag2'] = ['Sentinel-2 L2A']
proc_download.list_labels['dflag3'] = ['Sentinel-2 Data after Geometric Correction']
proc_download.list_labels['dflag4'] = ['Sentinel-2 Data after Parcellate']
proc_download.list_labels['dflag5'] = ['Sentinel-2 Data after Atmospheric Correction']
proc_download.input_types['drv_dir'] = 'ask_folder'
proc_download.input_types['trans_path'] = 'box'
proc_download.input_types['s2_path'] = 'box'
proc_download.input_types['search_key'] = 'box'
proc_download.input_types['dflag1'] = 'boolean'
proc_download.input_types['dflag2'] = 'boolean'
proc_download.input_types['dflag3'] = 'boolean'
proc_download.input_types['dflag4'] = 'boolean'
proc_download.input_types['dflag5'] = 'boolean'
for pnam in proc_download.pnams:
    proc_download.values[pnam] = proc_download.defaults[pnam]
proc_download.middle_left_frame_width = 1000
