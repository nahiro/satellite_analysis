import os
import sys
from datetime import datetime
import numpy as np
from subprocess import call
from proc_satellite_class import Satellite_Process

class Phenology(Satellite_Process):

    def __init__(self):
        super().__init__()
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files/folders
        start_dtim = datetime.strptime(self.start_date,self.date_fmt)
        end_dtim = datetime.strptime(self.end_date,self.date_fmt)
        first_dtim = datetime.strptime(self.first_date,self.date_fmt)
        last_dtim = datetime.strptime(self.last_date,self.date_fmt)
        pref_dtim = datetime.strptime(self.values['trans_pref'],self.date_fmt)
        data_years = np.arange(first_dtim.year,last_dtim.year+1,1)
        if not os.path.exists(self.s2_analysis):
            os.makedirs(self.s2_analysis)
        if not os.path.isdir(self.s2_analysis):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_analysis))
        mask_fnam = os.path.join(self.s1_analysis,'paddy_mask.tif')
        if not os.path.exists(mask_fnam):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,mask_fnam))

        # Select reference
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_reference.py'))
        command += ' --datdir "{}"'.format(os.path.join(self.s1_analysis,'planting'))
        command += ' --dst_fnam "{}"'.format(os.path.join(self.s1_analysis,'planting','ref_{:%Y%m%d}_{:%Y%m%d}.tif'.format(start_dtim,end_dtim)))
        command += ' --mask_fnam "{}"'.format(mask_fnam)
        command += ' --tmin {:%Y%m%d}'.format(start_dtim)
        command += ' --tmax {:%Y%m%d}'.format(end_dtim)
        command += ' --tref {:%Y%m%d}'.format(pref_dtim)
        if not np.isnan(self.values['trans_thr3'][0]):
            command += ' --trans_n_max {}'.format(self.values['trans_thr3'][0])
        if not np.isnan(self.values['trans_thr1'][0]):
            command += ' --bsc_min_max {}'.format(self.values['trans_thr1'][0])
        if not np.isnan(self.values['trans_thr1'][2]):
            command += ' --post_min_min {}'.format(self.values['trans_thr1'][2])
        if not np.isnan(self.values['trans_thr1'][3]):
            command += ' --post_avg_min {}'.format(self.values['trans_thr1'][3])
        if not np.isnan(self.values['trans_thr3'][1]):
            command += ' --risetime_max {}'.format(self.values['trans_thr3'][1])
        self.run_command(command,message='<<< Select reference for planting >>>')

        # Calculate average
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_average_reference.py'))
        command += ' --ref_fnam "{}"'.format(os.path.join(self.s1_analysis,'planting','ref_{:%Y%m%d}_{:%Y%m%d}.tif'.format(start_dtim,end_dtim)))
        command += ' --dst_fnam "{}"'.format(os.path.join(self.s1_analysis,'planting','avg_{:%Y%m%d}_{:%Y%m%d}.tif'.format(start_dtim,end_dtim)))
        command += ' --tmin {:%Y%m%d}'.format(start_dtim)
        command += ' --tmax {:%Y%m%d}'.format(end_dtim)
        self.run_command(command,message='<<< Calculate average for planting >>>')

        # Select planting
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_all.py'))
        command += ' --datdir "{}"'.format(os.path.join(self.s1_analysis,'planting'))
        command += ' --stat_fnam "{}"'.format(os.path.join(self.s1_analysis,'planting','avg_{:%Y%m%d}_{:%Y%m%d}.tif'.format(start_dtim,end_dtim)))
        command += ' --dst_fnam "{}"'.format(os.path.join(self.s1_analysis,'planting','planting_{:%Y%m%d}_{:%Y%m%d}.tif'.format(start_dtim,end_dtim)))
        command += ' --mask_fnam "{}"'.format(mask_fnam)
        command += ' --tmin {:%Y%m%d}'.format(start_dtim)
        command += ' --tmax {:%Y%m%d}'.format(end_dtim)
        #command += ' --tref {:%Y%m%d}'.format(pref_dtim)
        #if not np.isnan(self.values['trans_thr3'][0]):
        #    command += ' --trans_n_max {}'.format(self.values['trans_thr3'][0])
        if not np.isnan(self.values['trans_thr1'][0]):
            command += ' --bsc_min_max {}'.format(self.values['trans_thr1'][0])
        #if not np.isnan(self.values['trans_thr1'][2]):
        #    command += ' --post_min_min {}'.format(self.values['trans_thr1'][2])
        if not np.isnan(self.values['trans_thr1'][3]):
            command += ' --post_avg_min {}'.format(self.values['trans_thr1'][3])
        #if not np.isnan(self.values['trans_thr3'][1]):
        #    command += ' --risetime_max {}'.format(self.values['trans_thr3'][1])
        self.run_command(command,message='<<< Select planting >>>')

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
