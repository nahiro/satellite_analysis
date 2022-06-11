from run_phenology import Phenology

proc_phenology = Phenology()
proc_phenology.proc_name = 'phenology'
proc_phenology.proc_title = 'Estimate Event Dates'
proc_phenology.pnams.append('trans_select')
proc_phenology.pnams.append('atc_params')
proc_phenology.pnams.append('atc_ithrs')
proc_phenology.pnams.append('atc_nthrs')
proc_phenology.params['trans_select'] = 'Planting Date Selection'
proc_phenology.params['atc_params'] = 'Parameter for ATC'
proc_phenology.params['atc_ithrs'] = 'Id Threshold for ATC'
proc_phenology.params['atc_nthrs'] = '\u03B4NDVI Threshold for ATC'
proc_phenology.param_types['trans_select'] = 'string'
proc_phenology.param_types['atc_params'] = 'float_list'
proc_phenology.param_types['atc_ithrs'] = 'int_list'
proc_phenology.param_types['atc_nthrs'] = 'float_list'
proc_phenology.param_range['atc_params'] = (-1000.0,1000.0)
proc_phenology.param_range['atc_ithrs'] = (0,1000)
proc_phenology.param_range['atc_nthrs'] = (-1.0,1.0)
proc_phenology.defaults['trans_select'] = 'Around Plausible Planting Date'
proc_phenology.defaults['atc_params'] = [90.0,10.0]
proc_phenology.defaults['atc_ithrs'] = [30,35]
proc_phenology.defaults['atc_nthrs'] = [-0.0005,-0.0005,-0.0003]
proc_phenology.list_sizes['trans_select'] = 2
proc_phenology.list_sizes['atc_params'] = 2
proc_phenology.list_sizes['atc_ithrs'] = 2
proc_phenology.list_sizes['atc_nthrs'] = 3
proc_phenology.list_labels['trans_select'] = ['Around Plausible Planting Date','Large Planting Date Indicator']
proc_phenology.list_labels['atc_params'] = ['Ratio (%) :',' Offset (day) :']
proc_phenology.list_labels['atc_ithrs'] = ['T1 :',' T2 :']
proc_phenology.list_labels['atc_nthrs'] = ['T1 :',' T2 :',' T3 :']
proc_phenology.input_types['trans_select'] = 'string_select'
proc_phenology.input_types['atc_params'] = 'float_list'
proc_phenology.input_types['atc_ithrs'] = 'int_list'
proc_phenology.input_types['atc_nthrs'] = 'float_list'
for pnam in proc_phenology.pnams:
    proc_phenology.values[pnam] = proc_phenology.defaults[pnam]
proc_phenology.left_frame_width = 210
proc_phenology.middle_left_frame_width = 1000
