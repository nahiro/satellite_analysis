import numpy as np
from run_atcor import Atcor

proc_atcor = Atcor()
proc_atcor.proc_name = 'atcor'
proc_atcor.proc_title = 'Atmonspheric Correction'
proc_atcor.pnams.append('gis_fnam')
proc_atcor.params['gis_fnam'] = 'Polygon File'
proc_atcor.param_types['gis_fnam'] = 'string'
#proc_atcor.param_range['n_ref'] = (10,1000000)
proc_atcor.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
#proc_atcor.list_sizes['out_refs'] = 10
#proc_atcor.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_atcor.input_types['gis_fnam'] = 'ask_file'
for pnam in proc_atcor.pnams:
    proc_atcor.values[pnam] = proc_atcor.defaults[pnam]
proc_atcor.middle_left_frame_width = 1000
