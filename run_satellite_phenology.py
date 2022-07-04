import os
import sys
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
        data_years = np.arange(first_dtim.year,last_dtim.year+1,1)
        if not os.path.exists(self.s2_analysis):
            os.makedirs(self.s2_analysis)
        if not os.path.isdir(self.s2_analysis):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_analysis))

        mask_fnam = os.path.join(self.s1_analysis,'paddy_mask.tif')
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_reference.py'))
        command += ' --datdir "{}"'.format(os.path.join(self.s1_analysis,'planting'))
        command += ' --mask_fnam "{}"'.format(mask_fnam)
        command += ' --tmin {:%Y%m%d}'.format(start_dtim)
        command += ' --tmax {:%Y%m%d}'.format(end_dtim)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
