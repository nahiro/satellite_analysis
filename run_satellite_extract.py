import os
import sys
from proc_satellite_class import Satellite_Process

class Extract(Satellite_Process):

    def __init__(self):
        super().__init__()
        self.ax1_zmin = None
        self.ax1_zmax = None
        self.ax1_zstp = None
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
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_extract_values.py'))
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --obs_fnam "{}"'.format(self.values['gps_fnam'])
        command += ' --phenology "{}"'.format(self.values['event_fnam'])
        command += ' --tobs {}'.format(self.obs_date)

        command += ' --obs_fnam "{}"'.format(os.path.join(s2_analysis,'extract'))
        command += ' --ext_fnam "{}"'.format(os.path.join(s2_analysis,'extract'))
        command += ' --fignam "{}"'.format(os.path.join(s2_analysis,'extract','{}_extract.pdf'.format(trg_bnam)))
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
