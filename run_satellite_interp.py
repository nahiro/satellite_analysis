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
        d1 = start_dtim
        d2 = end_dtim+timedelta(days=120)
        if not os.path.exists(self.s2_analysis):
            os.makedirs(self.s2_analysis)
        if not os.path.isdir(self.s2_analysis):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_analysis))

        # Interpolate data
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_interp.py'))
        command += ' --inpdir "{}"'.format(os.path.join(self.s2_analysis,'parcel'))
        command += ' --dstdir "{}"'.format(os.path.join(self.s2_analysis,'interp'))
        command += ' --tendir "{}"'.format(os.path.join(self.s2_analysis,'tentative_interp'))
        command += ' --tmin {:%Y%m%d}'.format(d1)
        command += ' --tmax {:%Y%m%d}'.format(d2)
        command += ' --data_tmin {:%Y%m%d}'.format(first_dtim)
        command += ' --data_tmax {:%Y%m%d}'.format(last_dtim)
        command += ' --tstp 1'
        command += ' --smooth="{}"'.format(self.values['p_smooth'])
        if self.values['oflag'][2]:
            command += ' --overwrite'
        if self.values['oflag'][3]:
            command += ' --tentative_overwrite'
        self.run_command(command,message='<<< Interpolate data between {:%Y-%m-%d} - {:%Y-%m-%d} >>>'.format(first_dtim,last_dtim))

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
