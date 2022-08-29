import os
import sys
from proc_satellite_class import Satellite_Process

class Extract(Satellite_Process):

    def __init__(self):
        super().__init__()
        #self.ax1_zmin = None
        #self.ax1_zmax = None
        #self.ax1_zstp = None
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['gis_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gis_fnam']))
        if not os.path.exists(self.values['gps_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gps_fnam']))
        if not os.path.exists(self.values['event_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['event_fnam']))
        if not os.path.exists(self.s2_analysis):
            os.makedirs(self.s2_analysis)
        if not os.path.isdir(self.s2_analysis):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_analysis))

        # Extract indices
        extract_csv = os.path.join(self.s2_analysis,'extract','{:%Y%m%d}_{:%Y%m%d}_extract.csv'.format(start_dtim,end_dtim))
        extract_pdf = os.path.join(self.s2_analysis,'extract','{:%Y%m%d}_{:%Y%m%d}_extract.pdf'.format(start_dtim,end_dtim))
        dnam = os.path.dirname(extract_csv)
        if not os.path.exists(dnam):
            os.makedirs(dnam)
        if not os.path.isdir(dnam):
            raise IOError('Error, no such folder >>> {}'.format(dnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_extract_values.py'))
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --obs_fnam "{}"'.format(self.values['gps_fnam'])
        command += ' --phenology "{}"'.format(self.values['event_fnam'])
        command += ' --tobs {}'.format(self.obs_date)
        command += ' --inpdir "{}"'.format(os.path.join(self.s2_analysis,'interp'))
        command += ' --tendir "{}"'.format(os.path.join(self.s2_analysis,'tentative_interp'))
        command += ' --out_csv "{}"'.format(extract_csv)
        command += ' --fignam "{}"'.format(extract_pdf)
        #command += ' --ax1_zmin="{}"'.format(self.ax1_zmin)
        #command += ' --ax1_zmax="{}"'.format(self.ax1_zmax)
        #command += ' --ax1_zstp="{}"'.format(self.ax1_zstp)
        #command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --use_index'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Extract indices >>>')

        # Finish process
        sys.stderr.write('\nFinished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
