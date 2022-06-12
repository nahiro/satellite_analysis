import numpy as np
from run_download import Download

proc_download = Download()
proc_download.proc_name = 'download'
proc_download.proc_title = 'Download Data'
proc_download.pnams.append('gis_fnam')
proc_download.params['gis_fnam'] = 'Polygon File'
proc_download.param_types['gis_fnam'] = 'string'
#proc_download.param_range['p_smooth'] = (0.0,1.0)
proc_download.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
#proc_download.list_sizes['calib_params'] = 14
#proc_download.list_labels['calib_params'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
proc_download.input_types['gis_fnam'] = 'ask_file'
for pnam in proc_download.pnams:
    proc_download.values[pnam] = proc_download.defaults[pnam]
proc_download.middle_left_frame_width = 1000
