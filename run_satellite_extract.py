import os
import sys
from datetime import datetime,timedelta
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

        # Check files/folders
        start_dtim = datetime.strptime(self.start_date,self.date_fmt)
        end_dtim = datetime.strptime(self.end_date,self.date_fmt)
        first_dtim = datetime.strptime(self.first_date,self.date_fmt)
        last_dtim = datetime.strptime(self.last_date,self.date_fmt)
        obs_dtim = datetime.strptime(self.obs_date,self.date_fmt)
        if not os.path.exists(self.values['gis_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gis_fnam']))
        if not os.path.exists(self.values['gps_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gps_fnam']))
        if not os.path.exists(self.values['event_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['event_fnam']))
        wrk_dir = os.path.join(self.s2_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))



        # Read data
        if 'Field' in self.values['obs_src']:
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'read_survey_xls.py'))
            command += ' --inp_fnam "{}"'.format(self.values['obs_fnam'])
            command += ' --sheet {}'.format(self.values['i_sheet'])
            command += ' --ref_fnam "{}"'.format(self.values['gps_fnam'])
            command += ' --epsg {}'.format(self.values['epsg'])
            command += ' --out_fnam "{}"'.format(os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam)))
            self.run_command(command,message='<<< Read observation data >>>')




        # Extract indices
        extract_csv = os.path.join(wrk_dir,'{:%Y%m%d}_{:%Y%m%d}_extract.csv'.format(start_dtim,end_dtim))
        extract_pdf = os.path.join(wrk_dir,'{:%Y%m%d}_{:%Y%m%d}_extract.pdf'.format(start_dtim,end_dtim))
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
        command += ' --tobs {:%Y%m%d}'.format(obs_dtim)
        if self.values['event_dates'][0] != '':
            dtim = datetime.strptime(self.values['event_dates'][0],date_fmt)
            command += ' --plant {:%Y%m%d}'.format(dtim)
        if self.values['event_dates'][1] != '':
            dtim = datetime.strptime(self.values['event_dates'][1],date_fmt)
            command += ' --head {:%Y%m%d}'.format(dtim)
        if self.values['event_dates'][2] != '':
            dtim = datetime.strptime(self.values['event_dates'][2],date_fmt)
            command += ' --assess {:%Y%m%d}'.format(dtim)
        if self.values['event_dates'][3] != '':
            dtim = datetime.strptime(self.values['event_dates'][3],date_fmt)
            command += ' --harvest {:%Y%m%d}'.format(dtim)
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
