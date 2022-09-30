import os
import sys
import re
from datetime import datetime,timedelta
import numpy as np
from proc_satellite_class import Satellite_Process

class Interp(Satellite_Process):

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
        trg_bnam = '{:%Y%m%d}_{:%Y%m%d}'.format(first_dtim,last_dtim)
        if not os.path.exists(self.s2_data):
            os.makedirs(self.s2_data)
        if not os.path.isdir(self.s2_data):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_data))

        # Interpolate data
        ystr = '{:%Y}'.format(first_dtim)
        dnam = os.path.join(self.s2_data,'interp',ystr)
        if not os.path.exists(dnam):
            os.makedirs(dnam)
        if not os.path.isdir(dnam):
            raise IOError('Error, no such folder >>> {}'.format(dnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_interp.py'))
        if self.values['atcor_flag']:
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'atcor'))
            command += ' --atcor'
        else:
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'parcel'))
        command += ' --dstdir "{}"'.format(os.path.join(self.s2_data,'interp'))
        command += ' --tendir "{}"'.format(os.path.join(self.s2_data,'tentative_interp'))
        command += ' --data_tmin {:%Y%m%d}'.format(first_dtim)
        command += ' --data_tmax {:%Y%m%d}'.format(last_dtim)
        command += ' --tstp 1'
        command += ' --smooth="{}"'.format(self.values['p_smooth'])
        command += ' --ethr {}'.format(self.values['cflag_thr'])
        if self.values['csv_flag']:
            command += ' --out_csv'
        if self.values['oflag'][0]:
            command += ' --overwrite'
        if self.values['oflag'][1]:
            command += ' --tentative_overwrite'
        command += ' --fignam "{}"'.format(os.path.join(dnam,'{}_interp.pdf'.format(trg_bnam)))
        command += ' --nfig 10'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Interpolate data between {:%Y-%m-%d} - {:%Y-%m-%d} >>>'.format(first_dtim,last_dtim))

        # Finish process
        super().finish()
        return
