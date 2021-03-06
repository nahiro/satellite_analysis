import os
import sys
import numpy as np
from subprocess import call
from proc_satellite_class import Satellite_Process

class Formula(Satellite_Process):

    def __init__(self):
        super().__init__()
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files
        fnams = []
        for line in self.values['inp_fnams'].splitlines():
            fnam = line.strip()
            if (len(fnam) < 1) or (fnam[0] == '#'):
                continue
            if not os.path.exists(fnam):
                raise IOError('{}: error, no such file >>> "{}"'.format(self.proc_name,fnam))
            fnams.append(fnam)
        trg_bnam = '{}_{}'.format(self.obs_block,self.obs_date)
        wrk_dir = os.path.join(self.drone_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Make score formula
        tmp_fnam = os.path.join(wrk_dir,'temp.dat')
        with open(tmp_fnam,'w') as fp:
            fp.write('\n'.join(fnams))
        x_params = [(('S'+param) if param.islower() else param) for param in self.list_labels['x_params']]
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_fit.py'))
        command += ' --inp_list {}'.format(tmp_fnam)
        command += ' --out_fnam {}'.format(os.path.join(wrk_dir,'{}_score_formula.csv'.format(trg_bnam)))
        for param,flag in zip(x_params,self.values['x_params']):
            if flag:
                command += ' --x_param {}'.format(param)
        for param,flag in zip(self.list_labels['q_params'],self.values['q_params']):
            if flag:
                command += ' --q_param {}'.format(param)
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
        for param,value in zip(self.list_labels['y_params'],self.values['ythr']):
            if not np.isnan(value):
                command += ' --y_threshold "{}:{}"'.format(param,value)
        for param,value in zip(self.list_labels['y_params'],self.values['score_max']):
            if not np.isnan(value) and (np.abs(value-1.0) > 1.0e-6):
                command += ' --y_max "{}:{}"'.format(param,value)
        for param,value in zip(self.list_labels['y_params'],self.values['score_step']):
            if not np.isnan(value):
                command += ' --y_int "{}:{}"'.format(param,value)
        for y_param,label in zip(self.list_labels['y_params'],['yfac{}'.format(i+1) for i in range(len(self.list_labels['y_params']))]):
            for param,value in zip(self.list_labels['y_params'],self.values[label]):
                if not np.isnan(value):
                    command += ' --y_factor "{}:{}:{}"'.format(y_param,param,value)
        command += ' --vmax {}'.format(self.values['vif_max'])
        command += ' --nx_min {}'.format(self.values['n_x'][0])
        command += ' --nx_max {}'.format(self.values['n_x'][1])
        command += ' --ncheck_min {}'.format(self.values['n_multi'])
        command += ' --nmodel_max {}'.format(self.values['n_formula'])
        command += ' --criteria {}'.format(self.values['criteria'])
        command += ' --n_cross {}'.format(self.values['n_cros'])
        command += ' --amin {}'.format(self.values['age_range'][0])
        command += ' --amax {}'.format(self.values['age_range'][1])
        if self.values['mean_fitting']:
            command += ' --mean_fitting'
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_score_formula.pdf'.format(trg_bnam)))
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nMake score formula\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Make intensity formula
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_fit.py'))
        command += ' --inp_list {}'.format(tmp_fnam)
        command += ' --out_fnam {}'.format(os.path.join(wrk_dir,'{}_intensity_formula.csv'.format(trg_bnam)))
        for param,flag in zip(x_params,self.values['x_params']):
            if flag:
                command += ' --x_param {}'.format(param)
        for param,flag in zip(self.list_labels['q_params'],self.values['q_params']):
            if flag:
                command += ' --q_param {}'.format(param)
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
        for param,value in zip(self.list_labels['y_params'],self.values['ythr']):
            if not np.isnan(value):
                command += ' --y_threshold "{}:{}"'.format(param,value)
        for param,value in zip(self.list_labels['y_params'],self.values['score_max']):
            if not np.isnan(value) and (np.abs(value-1.0) > 1.0e-6):
                command += ' --y_max "{}:{}"'.format(param,value)
        for param,value in zip(self.list_labels['y_params'],self.values['score_step']):
            if not np.isnan(value):
                command += ' --y_int "{}:{}"'.format(param,value)
        for y_param,label in zip(self.list_labels['y_params'],['yfac{}'.format(i+1) for i in range(len(self.list_labels['y_params']))]):
            for param,value in zip(self.list_labels['y_params'],self.values[label]):
                if not np.isnan(value):
                    command += ' --y_factor "{}:{}:{}"'.format(y_param,param,value)
        command += ' --vmax {}'.format(self.values['vif_max'])
        command += ' --nx_min {}'.format(self.values['n_x'][0])
        command += ' --nx_max {}'.format(self.values['n_x'][1])
        command += ' --ncheck_min {}'.format(self.values['n_multi'])
        command += ' --nmodel_max {}'.format(self.values['n_formula'])
        command += ' --criteria {}'.format(self.values['criteria'])
        command += ' --n_cross {}'.format(self.values['n_cros'])
        command += ' --amin {}'.format(self.values['age_range'][0])
        command += ' --amax {}'.format(self.values['age_range'][1])
        command += ' --use_average'
        if self.values['mean_fitting']:
            command += ' --mean_fitting'
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_intensity_formula.pdf'.format(trg_bnam)))
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nMake intensity formula\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)
        if os.path.exists(tmp_fnam):
            os.remove(tmp_fnam)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
