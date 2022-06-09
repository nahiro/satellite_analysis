from run_extract import Extract

proc_extract = Extract()
proc_extract.proc_name = 'extract'
proc_extract.proc_title = 'Extract Indices'
proc_extract.pnams.append('obs_fnam')
proc_extract.pnams.append('i_sheet')
proc_extract.pnams.append('epsg')
proc_extract.pnams.append('gps_fnam')
proc_extract.params['obs_fnam'] = 'Observation File'
proc_extract.params['i_sheet'] = 'Observation Sheet Number'
proc_extract.params['epsg'] = 'EPSG'
proc_extract.params['gps_fnam'] = 'Point File'
proc_extract.param_types['obs_fnam'] = 'string'
proc_extract.param_types['i_sheet'] = 'int'
proc_extract.param_types['epsg'] = 'int'
proc_extract.param_types['gps_fnam'] = 'string'
proc_extract.param_range['i_sheet'] = (1,100)
proc_extract.param_range['epsg'] = (1,100000)
proc_extract.defaults['obs_fnam'] = 'observation.xls'
proc_extract.defaults['i_sheet'] = 1
proc_extract.defaults['epsg'] = 32748
proc_extract.defaults['gps_fnam'] = 'gps.csv'
proc_extract.input_types['obs_fnam'] = 'ask_file'
proc_extract.input_types['i_sheet'] = 'box'
proc_extract.input_types['epsg'] = 'box'
proc_extract.input_types['gps_fnam'] = 'ask_file'
for pnam in proc_extract.pnams:
    proc_extract.values[pnam] = proc_extract.defaults[pnam]
proc_extract.middle_left_frame_width = 1000
