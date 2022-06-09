import numpy as np
from run_formula import Formula

proc_formula = Formula()
proc_formula.proc_name = 'formula'
proc_formula.proc_title = 'Make Formula'
proc_formula.pnams.append('inp_fnams')
proc_formula.pnams.append('assess_day')
proc_formula.pnams.append('age_range')
proc_formula.pnams.append('n_x')
proc_formula.pnams.append('x_params')
proc_formula.pnams.append('q_params')
proc_formula.pnams.append('y_params')
proc_formula.pnams.append('score_max')
proc_formula.pnams.append('score_step')
proc_formula.pnams.append('ythr')
proc_formula.pnams.append('yfac1')
proc_formula.pnams.append('yfac2')
proc_formula.pnams.append('yfac3')
proc_formula.pnams.append('yfac4')
proc_formula.pnams.append('yfac5')
proc_formula.pnams.append('yfac6')
proc_formula.pnams.append('mean_fitting')
proc_formula.pnams.append('criteria')
proc_formula.pnams.append('n_multi')
proc_formula.pnams.append('vif_max')
proc_formula.pnams.append('n_cros')
proc_formula.pnams.append('n_formula')
proc_formula.params['inp_fnams'] = 'Input Files'
proc_formula.params['assess_day'] = 'Assessment Timing Estimation'
proc_formula.params['age_range'] = 'Age Range (day)'
proc_formula.params['n_x'] = 'Explanatory Variable Number'
proc_formula.params['x_params'] = 'Explanatory Variable Candidate'
proc_formula.params['q_params'] = 'Parameter for Plot-mean'
proc_formula.params['y_params'] = 'Objective Variable'
proc_formula.params['score_max'] = 'Max Input Score'
proc_formula.params['score_step'] = 'Score Step for Score-mean'
proc_formula.params['ythr'] = 'Threshold for Training Data'
proc_formula.params['yfac1'] = 'Conversion Factor for BLB'
proc_formula.params['yfac2'] = 'Conversion Factor for Blast'
proc_formula.params['yfac3'] = 'Conversion Factor for Borer'
proc_formula.params['yfac4'] = 'Conversion Factor for Rat'
proc_formula.params['yfac5'] = 'Conversion Factor for Hopper'
proc_formula.params['yfac6'] = 'Conversion Factor for Drought'
proc_formula.params['mean_fitting'] = 'Score-mean Fitting'
proc_formula.params['criteria'] = 'Selection Criteria'
proc_formula.params['n_multi'] = 'Min Multicollinearity Number'
proc_formula.params['vif_max'] = 'Max Variance Inflation Factor'
proc_formula.params['n_cros'] = 'Cross Validation Number'
proc_formula.params['n_formula'] = 'Max Formula Number'
proc_formula.param_types['inp_fnams'] = 'string'
proc_formula.param_types['assess_day'] = 'string_select'
proc_formula.param_types['age_range'] = 'float_list'
proc_formula.param_types['n_x'] = 'int_select_list'
proc_formula.param_types['x_params'] = 'boolean_list'
proc_formula.param_types['q_params'] = 'boolean_list'
proc_formula.param_types['y_params'] = 'boolean_list'
proc_formula.param_types['score_max'] = 'int_list'
proc_formula.param_types['score_step'] = 'float_list'
proc_formula.param_types['ythr'] = 'float_list'
proc_formula.param_types['yfac1'] = 'float_list'
proc_formula.param_types['yfac2'] = 'float_list'
proc_formula.param_types['yfac3'] = 'float_list'
proc_formula.param_types['yfac4'] = 'float_list'
proc_formula.param_types['yfac5'] = 'float_list'
proc_formula.param_types['yfac6'] = 'float_list'
proc_formula.param_types['mean_fitting'] = 'boolean'
proc_formula.param_types['criteria'] = 'string_select'
proc_formula.param_types['n_multi'] = 'int'
proc_formula.param_types['vif_max'] = 'float'
proc_formula.param_types['n_cros'] = 'int'
proc_formula.param_types['n_formula'] = 'int'
#proc_formula.param_range['n_x'] = (1,14)
proc_formula.param_range['age_range'] = (-1000.0,1000.0)
proc_formula.param_range['score_max'] = (1,65535)
proc_formula.param_range['score_step'] = (0.0,1.0e50)
proc_formula.param_range['ythr'] = (0.0,1.0e3)
proc_formula.param_range['yfac1'] = (0.0,1.0e5)
proc_formula.param_range['yfac2'] = (0.0,1.0e5)
proc_formula.param_range['yfac3'] = (0.0,1.0e5)
proc_formula.param_range['yfac4'] = (0.0,1.0e5)
proc_formula.param_range['yfac5'] = (0.0,1.0e5)
proc_formula.param_range['yfac6'] = (0.0,1.0e5)
proc_formula.param_range['n_multi'] = (1,1000)
proc_formula.param_range['vif_max'] = (0.0,1.0e5)
proc_formula.param_range['n_cros'] = (2,1000)
proc_formula.param_range['n_formula'] = (1,1000)
proc_formula.defaults['inp_fnams'] = 'input.csv'
proc_formula.defaults['assess_day'] = 'Assessment Timing Coefficient'
proc_formula.defaults['age_range'] = [-100.0,150.0]
proc_formula.defaults['n_x'] = [1,2]
proc_formula.defaults['x_params'] = [False,False,False,False,False,True,True,True,True,True,True,True,False,True]
proc_formula.defaults['q_params'] = [True,True,True,True]
proc_formula.defaults['y_params'] = [True,False,False,False,False,False]
proc_formula.defaults['score_max'] = [9,9,1,1,1,9]
proc_formula.defaults['score_step'] = [2.0,2.0,0.2,0.2,0.2,2.0]
proc_formula.defaults['ythr'] = [0.2,0.2,0.2,0.2,0.2,0.2]
proc_formula.defaults['yfac1'] = [1.0,np.nan,np.nan,np.nan,np.nan,np.nan]
proc_formula.defaults['yfac2'] = [np.nan,1.0,np.nan,np.nan,np.nan,np.nan]
proc_formula.defaults['yfac3'] = [np.nan,np.nan,1.0,np.nan,np.nan,np.nan]
proc_formula.defaults['yfac4'] = [np.nan,np.nan,np.nan,1.0,np.nan,np.nan]
proc_formula.defaults['yfac5'] = [np.nan,np.nan,np.nan,np.nan,1.0,np.nan]
proc_formula.defaults['yfac6'] = [np.nan,np.nan,np.nan,np.nan,np.nan,1.0]
proc_formula.defaults['mean_fitting'] = False
proc_formula.defaults['criteria'] = 'RMSE_test'
proc_formula.defaults['n_multi'] = 1
proc_formula.defaults['vif_max'] = 5.0
proc_formula.defaults['n_cros'] = 5
proc_formula.defaults['n_formula'] = 3
proc_formula.list_sizes['assess_day'] = 2
proc_formula.list_sizes['age_range'] = 2
proc_formula.list_sizes['n_x'] = 2
proc_formula.list_sizes['x_params'] = 14
proc_formula.list_sizes['q_params'] = 4
proc_formula.list_sizes['y_params'] = 6
proc_formula.list_sizes['score_max'] = 6
proc_formula.list_sizes['score_step'] = 6
proc_formula.list_sizes['ythr'] = 6
proc_formula.list_sizes['yfac1'] = 6
proc_formula.list_sizes['yfac2'] = 6
proc_formula.list_sizes['yfac3'] = 6
proc_formula.list_sizes['yfac4'] = 6
proc_formula.list_sizes['yfac5'] = 6
proc_formula.list_sizes['yfac6'] = 6
proc_formula.list_sizes['criteria'] = 7
proc_formula.list_labels['assess_day'] = ['Assessment Timing Coefficient','Age Range']
proc_formula.list_labels['age_range'] = ['Min :',' Max :']
proc_formula.list_labels['n_x'] = [('Min :',[1,2,3,4,5,6,7,8,9,10,11,12,13,14]),(' Max :',[1,2,3,4,5,6,7,8,9,10,11,12,13,14])]
proc_formula.list_labels['x_params'] = ['b','g','r','e','n','Nb','Ng','Nr','Ne','Nn','NDVI','GNDVI','RGI','NRGI']
proc_formula.list_labels['q_params'] = ['Location','PlotPaddy','PlantDate','Age']
proc_formula.list_labels['y_params'] = ['BLB','Blast','Borer','Rat','Hopper','Drought']
proc_formula.list_labels['score_max'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_formula.list_labels['score_step'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_formula.list_labels['ythr'] = ['BLB :',' Blast :',' Borer :',' Rat :',' Hopper :',' Drought :']
proc_formula.list_labels['yfac1'] = ['','','','','','']
proc_formula.list_labels['yfac2'] = ['','','','','','']
proc_formula.list_labels['yfac3'] = ['','','','','','']
proc_formula.list_labels['yfac4'] = ['','','','','','']
proc_formula.list_labels['yfac5'] = ['','','','','','']
proc_formula.list_labels['yfac6'] = ['','','','','','']
proc_formula.list_labels['criteria'] = ['RMSE_test','R2_test','AIC_test','RMSE_train','R2_train','AIC_train','BIC_train']
proc_formula.input_types['inp_fnams'] = 'ask_files'
proc_formula.input_types['assess_day'] = 'string_select'
proc_formula.input_types['age_range'] = 'float_list'
proc_formula.input_types['n_x'] = 'int_select_list'
proc_formula.input_types['x_params'] = 'boolean_list'
proc_formula.input_types['q_params'] = 'boolean_list'
proc_formula.input_types['y_params'] = 'boolean_list'
proc_formula.input_types['score_max'] = 'int_list'
proc_formula.input_types['score_step'] = 'float_list'
proc_formula.input_types['ythr'] = 'float_list'
proc_formula.input_types['yfac1'] = 'float_list'
proc_formula.input_types['yfac2'] = 'float_list'
proc_formula.input_types['yfac3'] = 'float_list'
proc_formula.input_types['yfac4'] = 'float_list'
proc_formula.input_types['yfac5'] = 'float_list'
proc_formula.input_types['yfac6'] = 'float_list'
proc_formula.input_types['mean_fitting'] = 'boolean'
proc_formula.input_types['criteria'] = 'string_select'
proc_formula.input_types['n_multi'] = 'box'
proc_formula.input_types['vif_max'] = 'box'
proc_formula.input_types['n_cros'] = 'box'
proc_formula.input_types['n_formula'] = 'box'
#proc_formula.flag_fill['x_params'] = True
#proc_formula.flag_fill['q_params'] = True
#proc_formula.flag_fill['y_params'] = True
for pnam in proc_formula.pnams:
    proc_formula.values[pnam] = proc_formula.defaults[pnam]
proc_formula.left_frame_width = 200
proc_formula.middle_left_frame_width = 1000
