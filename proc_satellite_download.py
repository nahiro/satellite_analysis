import numpy as np
from run_satellite_download import Download

proc_download = Download()
proc_download.proc_name = 'download'
proc_download.proc_title = 'Download Data'
proc_download.pnams.append('drv_dir')
proc_download.pnams.append('trans_path')
proc_download.pnams.append('s2_path')
proc_download.pnams.append('dflag1')
proc_download.pnams.append('dflag2')
proc_download.pnams.append('dflag3')
proc_download.pnams.append('dflag4')
proc_download.pnams.append('dflag5')
proc_download.params['drv_dir'] = 'Google Drive Folder'
proc_download.params['trans_path'] = 'Planting Folder on GD'
proc_download.params['s2_path'] = 'Sentinel-2 Folder on GD'
proc_download.params['dflag1'] = 'Download Planting'
proc_download.params['dflag2'] = 'Download S2 L2A'
proc_download.params['dflag3'] = 'Download S2 aft. Geometric Correction '
proc_download.params['dflag4'] = 'Download S2 aft. Parcellate'
proc_download.params['dflag5'] = 'Download S2 aft. Atmospheric Correction'
proc_download.param_types['drv_dir'] = 'string'
proc_download.param_types['trans_path'] = 'string'
proc_download.param_types['s2_path'] = 'string'
proc_download.param_types['dflag1'] = 'boolean'
proc_download.param_types['dflag2'] = 'boolean'
proc_download.param_types['dflag3'] = 'boolean'
proc_download.param_types['dflag4'] = 'boolean'
proc_download.param_types['dflag5'] = 'boolean'
#proc_download.param_range['p_smooth'] = (0.0,1.0)
proc_download.defaults['drv_dir'] = 'GoogleDrive'
proc_download.defaults['trans_path'] = '/Spatial-information/Transplanting_date/Cihea/final/v1.4'
proc_download.defaults['s2_path'] = '/Spatial-information/Sentinel-2/L2A/Cihea'
proc_download.defaults['dflag1'] = True
proc_download.defaults['dflag2'] = True
proc_download.defaults['dflag3'] = True
proc_download.defaults['dflag4'] = True
proc_download.defaults['dflag5'] = True
#proc_download.list_labels['calib_params'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
proc_download.input_types['drv_dir'] = 'ask_folder'
proc_download.input_types['trans_path'] = 'box'
proc_download.input_types['s2_path'] = 'box'
proc_download.input_types['dflag1'] = 'boolean'
proc_download.input_types['dflag2'] = 'boolean'
proc_download.input_types['dflag3'] = 'boolean'
proc_download.input_types['dflag4'] = 'boolean'
proc_download.input_types['dflag5'] = 'boolean'
for pnam in proc_download.pnams:
    proc_download.values[pnam] = proc_download.defaults[pnam]
proc_download.left_frame_width = 250
proc_download.middle_left_frame_width = 1000
