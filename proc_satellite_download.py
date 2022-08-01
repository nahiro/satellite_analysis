import numpy as np
from run_satellite_download import Download

proc_download = Download()
proc_download.proc_name = 'download'
proc_download.proc_title = 'Download Data'
proc_download.pnams.append('server')
proc_download.pnams.append('port')
proc_download.pnams.append('netrc_dir')
proc_download.pnams.append('trans_path')
proc_download.pnams.append('l2a_path')
proc_download.pnams.append('resample_path')
proc_download.pnams.append('parcel_path')
proc_download.pnams.append('atcor_path')
proc_download.pnams.append('interp_path')
proc_download.pnams.append('search_key')
proc_download.pnams.append('dflag')
proc_download.pnams.append('oflag')
proc_download.params['server'] = 'NAS Server'
proc_download.params['port'] = 'NAS Port'
proc_download.params['netrc_dir'] = 'Netrc Folder'
proc_download.params['trans_path'] = 'Planting on NAS'
proc_download.params['l2a_path'] = 'Sentinel-2 L2A on NAS'
proc_download.params['resample_path'] = 'Sentinel-2 resample on NAS'
proc_download.params['parcel_path'] = 'Sentinel-2 parcel on NAS'
proc_download.params['atcor_path'] = 'Sentinel-2 atcor on NAS'
proc_download.params['interp_path'] = 'Sentinel-2 interp on NAS'
proc_download.params['search_key'] = 'Search Keyword for L2A'
proc_download.params['dflag'] = 'Download Flag'
proc_download.params['oflag'] = 'Overwrite Flag'
proc_download.param_types['server'] = 'string'
proc_download.param_types['port'] = 'int'
proc_download.param_types['netrc_dir'] = 'string'
proc_download.param_types['trans_path'] = 'string'
proc_download.param_types['l2a_path'] = 'string'
proc_download.param_types['resample_path'] = 'string'
proc_download.param_types['parcel_path'] = 'string'
proc_download.param_types['atcor_path'] = 'string'
proc_download.param_types['interp_path'] = 'string'
proc_download.param_types['search_key'] = 'string'
proc_download.param_types['dflag'] = 'boolean_list'
proc_download.param_types['oflag'] = 'boolean_list'
proc_download.defaults['server'] = 'satreps-nas'
proc_download.defaults['port'] = 443
proc_download.defaults['netrc_dir'] = 'Home'
proc_download.defaults['trans_path'] = '/SATREPS/ipb/User/1_Spatial-information/Transplanting_date/Cihea/final/v1.4'
proc_download.defaults['l2a_path'] = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/L2A'
proc_download.defaults['resample_path'] = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/resample'
proc_download.defaults['parcel_path'] = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/parcel'
proc_download.defaults['atcor_path'] = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/atcor'
proc_download.defaults['interp_path'] = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/interp'
proc_download.defaults['search_key'] = ''
proc_download.defaults['dflag'] = [True,True,True,True,True,True]
proc_download.defaults['oflag'] = [False,False,False,False,False,False]
proc_download.list_sizes['dflag'] = 6
proc_download.list_sizes['oflag'] = 6
proc_download.list_labels['dflag'] = ['Planting','L2A','resample','parcel','atcor','interp']
proc_download.list_labels['oflag'] = ['Planting','L2A','resample','parcel','atcor','interp']
proc_download.input_types['server'] = 'box'
proc_download.input_types['port'] = 'box'
proc_download.input_types['netrc_dir'] = 'ask_folder'
proc_download.input_types['trans_path'] = 'box'
proc_download.input_types['l2a_path'] = 'box'
proc_download.input_types['resample_path'] = 'box'
proc_download.input_types['parcel_path'] = 'box'
proc_download.input_types['atcor_path'] = 'box'
proc_download.input_types['interp_path'] = 'box'
proc_download.input_types['search_key'] = 'box'
proc_download.input_types['dflag'] = 'boolean_list'
proc_download.input_types['oflag'] = 'boolean_list'
for pnam in proc_download.pnams:
    proc_download.values[pnam] = proc_download.defaults[pnam]
proc_download.middle_left_frame_width = 1000
