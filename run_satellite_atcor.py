import os
import sys
import re
from datetime import datetime
try:
    import gdal
except Exception:
    from osgeo import gdal
from glob import glob
import numpy as np
from subprocess import call
from proc_satellite_class import Satellite_Process

class Atcor(Satellite_Process):

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
        d1 = datetime.strptime(self.values['stat_period'][0],self.date_fmt)
        d2 = datetime.strptime(self.values['stat_period'][1],self.date_fmt)
        data_years = np.arange(first_dtim.year,last_dtim.year+1,1)

        # Select nearest pixels
        if os.path.exists(self.values['inds_fnam']) and self.values['oflag'][2]:
            os.remove(self.values['inds_fnam'])
        if not os.path.exists(self.values['inds_fnam']):
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'atcor_select_reference.py'))
            command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'resample'))
            command += ' --out_fnam "{}"'.format(self.values['inds_fnam'])
            for band,flag in zip(self.list_labels['ref_band'],self.values['ref_band']):
                if flag:
                    command += ' --ref_band {}'.format(band.strip())
            command += ' --data_tmin {:%Y%m%d}'.format(d1)
            command += ' --data_tmax {:%Y%m%d}'.format(d2)
            command += ' --rthr {}'.format(self.values['ref_thr'])
            command += ' --n_nearest {}'.format(self.values['n_ref'])
            command += ' --use_index'
            self.run_command(command,message='<<< Select nearest pixels >>>')

        # Calculate stats
        if os.path.exists(self.values['stat_fnam']) and self.values['oflag'][1]:
            os.remove(self.values['stat_fnam'])
        if not os.path.exists(self.values['stat_fnam']):
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'atcor_calc_stat.py'))
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'indices'))
            command += ' --dst_geotiff "{}"'.format(self.values['stat_fnam'])

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
