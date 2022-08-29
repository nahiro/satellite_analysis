from run_satellite_extract import Extract

proc_extract = Extract()
proc_extract.proc_name = 'extract'
proc_extract.proc_title = 'Extract Indices'
proc_extract.pnams.append('gis_fnam')
proc_extract.pnams.append('gps_fnam')
proc_extract.pnams.append('event_fnam')
proc_extract.pnams.append('event_dates')
proc_extract.params['gis_fnam'] = 'Polygon File'
proc_extract.params['gps_fnam'] = 'Point File'
proc_extract.params['event_fnam'] = 'Event Date File'
proc_extract.params['event_dates'] = 'Event Dates'
proc_extract.param_types['gis_fnam'] = 'string'
proc_extract.param_types['gps_fnam'] = 'string'
proc_extract.param_types['event_fnam'] = 'string'
proc_extract.param_types['event_dates'] = 'date_list'
proc_extract.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_extract.defaults['gps_fnam'] = 'gps.csv'
proc_extract.defaults['event_fnam'] = 'phenology.csv'
proc_extract.defaults['event_dates'] = ['','','','']
proc_extract.list_sizes['event_dates'] = 4
proc_extract.list_labels['event_dates'] = ['Planting :',' Heading :',' Assessment :',' Harvesting :']
proc_extract.input_types['gis_fnam'] = 'ask_file'
proc_extract.input_types['gps_fnam'] = 'ask_file'
proc_extract.input_types['event_fnam'] = 'ask_file'
proc_extract.input_types['event_dates'] = 'date_list'
for pnam in proc_extract.pnams:
    proc_extract.values[pnam] = proc_extract.defaults[pnam]
proc_extract.middle_left_frame_width = 1000
