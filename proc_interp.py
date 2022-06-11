import numpy as np
from run_interp import Interp

proc_interp = Interp()
proc_interp.proc_name = 'interp'
proc_interp.proc_title = 'Interpolate Time-series Data'
proc_interp.pnams.append('gis_fnam')
proc_interp.params['gis_fnam'] = 'Polygon File'
proc_interp.param_types['gis_fnam'] = 'string'
proc_interp.param_range['ref_bands'] = (-10000,10000)
#proc_interp.param_range['ref_factors'] = (0,1.0)
proc_interp.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
#proc_interp.list_sizes['ref_bands'] = 3
#proc_interp.list_labels['ref_bands'] = ['','','']
proc_interp.input_types['gis_fnam'] = 'ask_file'
for pnam in proc_interp.pnams:
    proc_interp.values[pnam] = proc_interp.defaults[pnam]
proc_interp.middle_left_frame_width = 1000
