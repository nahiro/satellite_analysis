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
        spec_dtim = datetime.strptime(self.values['spec_date'],self.date_fmt)
        if not os.path.exists(self.values['gis_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gis_fnam']))
        if not os.path.exists(self.values['obs_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['obs_fnam']))
        if not os.path.exists(self.values['event_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['event_fnam']))
        trg_bnam = '{}_{}'.format(self.obs_block,self.obs_date)
        wrk_dir = os.path.join(self.s2_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Read data
        if 'Field' in self.values['obs_src']:
            obs_csv = os.path.join(wrk_dir,'{}_observation.csv'.format(trg_bnam))
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'read_survey_xls.py'))
            command += ' --inp_fnam "{}"'.format(self.values['obs_fnam'])
            command += ' --sheet {}'.format(self.values['i_sheet'])
            command += ' --epsg {}'.format(self.values['epsg'])
            command += ' --out_fnam "{}"'.format(obs_csv)
            self.run_command(command,message='<<< Read observation data >>>')
        else:
            obs_csv = self.values['obs_fnam']

        # Extract indices
        extract_csv = os.path.join(wrk_dir,'{}_extract.csv'.format(trg_bnam))
        extract_pdf = os.path.join(wrk_dir,'{}_extract.pdf'.format(trg_bnam))
        dnam = os.path.dirname(extract_csv)
        if not os.path.exists(dnam):
            os.makedirs(dnam)
        if not os.path.isdir(dnam):
            raise IOError('Error, no such folder >>> {}'.format(dnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_extract_values.py'))
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --obs_fnam "{}"'.format(obs_csv)
        if not self.values['event_flag']:
            command += ' --phenology "{}"'.format(self.values['event_fnam'])
        command += ' --tobs {:%Y%m%d}'.format(spec_dtim)
        list_labels = [s.split()[0] for s in self.list_labels['event_dates']]
        idate = list_labels.index('Planting')
        if self.values['event_dates'][idate] != '':
            dtim = datetime.strptime(self.values['event_dates'][idate],date_fmt)
            command += ' --plant {:%Y%m%d}'.format(dtim)
        idate = list_labels.index('Peak')
        if self.values['event_dates'][idate] != '':
            dtim = datetime.strptime(self.values['event_dates'][idate],date_fmt)
            command += ' --peak {:%Y%m%d}'.format(dtim)
        idate = list_labels.index('Heading')
        if self.values['event_dates'][idate] != '':
            dtim = datetime.strptime(self.values['event_dates'][idate],date_fmt)
            command += ' --head {:%Y%m%d}'.format(dtim)
        idate = list_labels.index('Assessment')
        if self.values['event_dates'][idate] != '':
            dtim = datetime.strptime(self.values['event_dates'][idate],date_fmt)
            command += ' --assess {:%Y%m%d}'.format(dtim)
        idate = list_labels.index('Harvesting')
        if self.values['event_dates'][idate] != '':
            dtim = datetime.strptime(self.values['event_dates'][idate],date_fmt)
            command += ' --harvest {:%Y%m%d}'.format(dtim)
        if 'Non-interpolated' in self.values['data_select']:
            command += ' --no_interp'
            command += ' --cr_band {}'.format(self.values['cloud_band'])
            list_labels = [s.split()[0] for s in self.list_labels['cloud_thr']]
            ithr = list_labels.index('Reflectance')
            command += ' --cthr {}'.format(self.values['cloud_thr'][ithr])
            if self.values['atcor_flag']:
                command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'atcor'))
                ithr = list_labels.index('Correlation')
                command += ' --rthr {}'.format(self.values['cloud_thr'][ithr])
            else:
                command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'parcel'))
                command += ' --no_atcor'
        else:
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'interp'))
            command += ' --tendir "{}"'.format(os.path.join(self.s2_data,'tentative_interp'))
        command += ' --out_csv "{}"'.format(extract_csv)
        command += ' --fignam "{}"'.format(extract_pdf)
        #command += ' --ax1_zmin="{}"'.format(self.ax1_zmin)
        #command += ' --ax1_zmax="{}"'.format(self.ax1_zmax)
        #command += ' --ax1_zstp="{}"'.format(self.ax1_zstp)
        #command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --use_index'
        if self.values['major_flag']:
            command += ' --use_major_plot'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Extract indices >>>')

        # Finish process
        super().finish()
        return
