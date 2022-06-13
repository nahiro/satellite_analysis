import numpy as np
from run_download import Download

proc_download = Download()
proc_download.proc_name = 'download'
proc_download.proc_title = 'Download Data'
proc_download.pnams.append('drv_dir')
proc_download.pnams.append('s2_path')
proc_download.pnams.append('trans_path')
proc_download.pnams.append('dflag')
proc_download.params['drv_dir'] = 'Google Drive Folder'
proc_download.params['s2_path'] = 'Sentinel-2 Data on GD'
proc_download.params['trans_path'] = 'Planting Data on GD'
proc_download.params['dflag'] = 'Download'
proc_download.param_types['drv_dir'] = 'string'
proc_download.param_types['s2_path'] = 'string'
proc_download.param_types['trans_path'] = 'string'
proc_download.param_types['dflag'] = 'boolean_list'
#proc_download.param_range['p_smooth'] = (0.0,1.0)
proc_download.defaults['drv_dir'] = 'GoogleDrive'
proc_download.defaults['s2_path'] = '/Spatial-information/Sentinel-2/L2A/Cihea'
proc_download.defaults['trans_path'] = '/Spatial-information/Transplanting_date/Cihea/final/v1.4'
proc_download.defaults['dflag'] = [True,True,True,True,True]
proc_download.list_sizes['dflag'] = 5
#proc_download.list_labels['calib_params'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
proc_download.list_labels['dflag'] = ['Planting  ','S2 L2A  ','S2 aft. Geometric Correction  ','S2 aft. Parcellate','S2 aft. Atmospheric Correction']
proc_download.input_types['drv_dir'] = 'ask_folder'
proc_download.input_types['s2_path'] = 'box'
proc_download.input_types['trans_path'] = 'box'
proc_download.input_types['dflag'] = 'boolean_list'
for pnam in proc_download.pnams:
    proc_download.values[pnam] = proc_download.defaults[pnam]
proc_download.middle_left_frame_width = 1000
