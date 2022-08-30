from run_satellite_extract import Extract

proc_extract = Extract()
proc_extract.proc_name = 'extract'
proc_extract.proc_title = 'Extract Indices'
proc_extract.pnams.append('gis_fnam')
proc_extract.pnams.append('obs_src')
proc_extract.pnams.append('obs_fnam')
proc_extract.pnams.append('event_fnam')
proc_extract.pnams.append('event_dates')
proc_extract.params['gis_fnam'] = 'Polygon File'
proc_extract.params['obs_src'] = 'Observation Source'
proc_extract.params['obs_fnam'] = 'Observation File'
proc_extract.params['event_fnam'] = 'Event Date File'
proc_extract.params['event_dates'] = 'Event Dates'
proc_extract.param_types['gis_fnam'] = 'string'
proc_extract.param_types['obs_src'] = 'string_select'
proc_extract.param_types['obs_fnam'] = 'string'
proc_extract.param_types['event_fnam'] = 'string'
proc_extract.param_types['event_dates'] = 'date_list'
proc_extract.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_extract.defaults['obs_src'] = 'Drone Analysis'
proc_extract.defaults['obs_fnam'] = 'observation.csv'
proc_extract.defaults['event_fnam'] = 'phenology.csv'
proc_extract.defaults['event_dates'] = ['','','','']
proc_extract.list_sizes['obs_src'] = 2
proc_extract.list_sizes['event_dates'] = 4
proc_extract.list_labels['obs_src'] = ['Field Data','Drone Analysis']
proc_extract.list_labels['event_dates'] = ['Planting :',' Heading :',' Assessment :',' Harvesting :']
proc_extract.input_types['gis_fnam'] = 'ask_file'
proc_extract.input_types['obs_src'] = 'string_select'
proc_extract.input_types['obs_fnam'] = 'ask_file'
proc_extract.input_types['event_fnam'] = 'ask_file'
proc_extract.input_types['event_dates'] = 'date_list'
for pnam in proc_extract.pnams:
    proc_extract.values[pnam] = proc_extract.defaults[pnam]
proc_extract.middle_left_frame_width = 1000
