from run_satellite_extract import Extract

proc_extract = Extract()
proc_extract.proc_name = 'extract'
proc_extract.proc_title = 'Extract Indices'
proc_extract.pnams.append('gis_fnam')
proc_extract.pnams.append('obs_src')
proc_extract.pnams.append('obs_fnam')
proc_extract.pnams.append('i_sheet')
proc_extract.pnams.append('epsg')
proc_extract.pnams.append('major_flag')
proc_extract.pnams.append('event_fnam')
proc_extract.pnams.append('event_dates')
proc_extract.pnams.append('data_select')
proc_extract.pnams.append('spec_date')
proc_extract.params['gis_fnam'] = 'Polygon File'
proc_extract.params['obs_src'] = 'Observation Source'
proc_extract.params['obs_fnam'] = 'Observation File'
proc_extract.params['i_sheet'] = 'Observation Sheet Number'
proc_extract.params['epsg'] = 'EPSG'
proc_extract.params['major_flag'] = 'Use Major Plot'
proc_extract.params['event_fnam'] = 'Event Date File'
proc_extract.params['event_dates'] = 'Event Dates'
proc_extract.params['data_select'] = 'Data Selection Criteria'
proc_extract.params['spec_date'] = 'Specific Date'
proc_extract.param_types['gis_fnam'] = 'string'
proc_extract.param_types['obs_src'] = 'string_select'
proc_extract.param_types['obs_fnam'] = 'string'
proc_extract.param_types['i_sheet'] = 'int'
proc_extract.param_types['epsg'] = 'int'
proc_extract.param_types['major_flag'] = 'boolean'
proc_extract.param_types['event_fnam'] = 'string'
proc_extract.param_types['event_dates'] = 'date_list'
proc_extract.param_types['data_select'] = 'string_select'
proc_extract.param_types['spec_date'] = 'date'
proc_extract.param_range['i_sheet'] = (1,100)
proc_extract.param_range['epsg'] = (1,100000)
proc_extract.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
proc_extract.defaults['obs_src'] = 'Drone Analysis'
proc_extract.defaults['obs_fnam'] = 'observation.csv'
proc_extract.defaults['i_sheet'] = 1
proc_extract.defaults['epsg'] = 32748
proc_extract.defaults['major_flag'] = False
proc_extract.defaults['event_fnam'] = 'phenology.csv'
proc_extract.defaults['event_dates'] = ['','','','']
proc_extract.defaults['data_select'] = 'Specific Interpolated Data'
proc_extract.defaults['spec_date'] = ''
proc_extract.list_sizes['obs_src'] = 2
proc_extract.list_sizes['event_dates'] = 4
proc_extract.list_sizes['data_select'] = 2
proc_extract.list_labels['obs_src'] = ['Field Data','Drone Analysis']
proc_extract.list_labels['event_dates'] = ['Planting :',' Heading :',' Assessment :',' Harvesting :']
proc_extract.list_labels['data_select'] = ['Specific Non-interpolated Data','Specific Interpolated Data']
proc_extract.input_types['gis_fnam'] = 'ask_file'
proc_extract.input_types['obs_src'] = 'string_select'
proc_extract.input_types['obs_fnam'] = 'ask_file'
proc_extract.input_types['i_sheet'] = 'box'
proc_extract.input_types['epsg'] = 'box'
proc_extract.input_types['major_flag'] = 'boolean'
proc_extract.input_types['event_fnam'] = 'ask_file'
proc_extract.input_types['event_dates'] = 'date_list'
proc_extract.input_types['data_select'] = 'string_select'
proc_extract.input_types['spec_date'] = 'date'
proc_extract.flag_check['event_fnam'] = False
proc_extract.flag_check['obs_fnam'] = False
proc_extract.depend_proc['event_fnam'] = ['phenology']
proc_extract.expected['gis_fnam'] = '*.shp'
proc_extract.expected['obs_fnam'] = '*.xls'
proc_extract.expected['event_fnam'] = 'assess.csv'
for pnam in proc_extract.pnams:
    proc_extract.values[pnam] = proc_extract.defaults[pnam]
proc_extract.middle_left_frame_width = 1000
