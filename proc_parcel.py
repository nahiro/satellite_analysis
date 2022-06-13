import numpy as np
from run_parcel import Parcel

proc_parcel = Parcel()
proc_parcel.proc_name = 'parcel'
proc_parcel.proc_title = 'Parcellate Data'
proc_parcel.pnams.append('gis_fnam')
proc_parcel.params['gis_fnam'] = 'Polygon File'
proc_parcel.param_types['gis_fnam'] = 'string'
#proc_parcel.param_range['n_ref'] = (10,1000000)
proc_parcel.defaults['gis_fnam'] = 'All_area_polygon_20210914.shp'
#proc_parcel.list_sizes['out_refs'] = 10
#proc_parcel.list_labels['out_refs'] = ['b  ','g  ','r  ','e1  ','e2  ','e3  ','n1  ','n2  ','s1  ','s2']
proc_parcel.input_types['gis_fnam'] = 'ask_file'
for pnam in proc_parcel.pnams:
    proc_parcel.values[pnam] = proc_parcel.defaults[pnam]
proc_parcel.middle_left_frame_width = 1000
