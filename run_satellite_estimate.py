import os
import sys
from datetime import datetime,timedelta
from proc_satellite_class import Satellite_Process

class Estimate(Satellite_Process):

    def __init__(self):
        super().__init__()
        self.zmin_refs = None
        self.zmax_refs = None
        self.zstp_refs = None
        self.zmin_nrefs = None
        self.zmax_nrefs = None
        self.zstp_nrefs = None
        self.zmin_inds = None
        self.zmax_inds = None
        self.zstp_inds = None
        self.ax1_zmin = None
        self.ax1_zmax = None
        self.ax1_zstp = None
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files/folders
        start_dtim = datetime.strptime(self.start_date,self.date_fmt)
        end_dtim = datetime.strptime(self.end_date,self.date_fmt)
        first_dtim = datetime.strptime(self.first_date,self.date_fmt)
        last_dtim = datetime.strptime(self.last_date,self.date_fmt)
        if not os.path.exists(self.values['gis_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['gis_fnam']))
        if not os.path.exists(self.values['event_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['event_fnam']))
        if not os.path.exists(self.values['pm_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['pm_fnam']))
        trg_bnam = '{:%Y%m%d}_{:%Y%m%d}'.format(start_dtim,end_dtim)
        wrk_dir = os.path.join(self.s2_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Select data
        if 'Specific' in self.values['data_select']:
            spec_dtim = datetime.strptime(self.values['spec_date'],self.date_fmt)
            ystr = '{:%Y}'.format(spec_dtim)
            if 'Non-interpolated' in self.values['data_select']:
                if self.values['atcor_flag']:
                    spec_fnam = os.path.join(self.s2_data,'atcor',ystr,'{:%Y%m%d}_atcor.npz'.format(spec_dtim))
                    spec_gnam = os.path.join(self.s2_data,'atcor',ystr,'{:%Y%m%d}_factor.npz'.format(spec_dtim))
                else:
                    spec_fnam = os.path.join(self.s2_data,'parcel',ystr,'{:%Y%m%d}_parcel.npz'.format(spec_dtim))
            else:
                spec_fnam = os.path.join(self.s2_data,'interp',ystr,'{:%Y%m%d}_interp.npz'.format(spec_dtim))
            if not os.path.exists(spec_fnam):
                raise IOError('Error, no such file >>> {}'.format(spec_fnam))
            ax1_title = '{}: {:%Y%m%d}'.format(self.values['data_select'],spec_dtim)
        else:
            select_csv = os.path.join(wrk_dir,'{}_select.csv'.format(trg_bnam))
            select_shp = os.path.join(wrk_dir,'{}_select.shp'.format(trg_bnam))
            select_pdf = os.path.join(wrk_dir,'{}_select.pdf'.format(trg_bnam))
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_select_data.py'))
            command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
            command += ' --phenology "{}"'.format(self.values['event_fnam'])
            if 'Age' in self.values['data_select']:
                command += ' --param Age'
                command += ' --offset {}'.format(self.values['age_value'])
                ax1_title = '{}: {:.1f}'.format(self.values['data_select'],self.values['age_value'])
            elif 'Harvesting' in self.values['data_select']:
                command += ' --param harvest_d'
                command += ' --offset {}'.format(self.values['harvest_value'])
                ax1_title = '{}: {:.1f}'.format(self.values['data_select'],self.values['harvest_value'])
            elif 'Assessment' in self.values['data_select']:
                command += ' --param assess_d'
                command += ' --offset {}'.format(self.values['assess_value'])
                ax1_title = '{}: {:.1f}'.format(self.values['data_select'],self.values['assess_value'])
            elif 'Heading' in self.values['data_select']:
                command += ' --param head_d'
                command += ' --offset {}'.format(self.values['head_value'])
                ax1_title = '{}: {:.1f}'.format(self.values['data_select'],self.values['head_value'])
            elif 'Peak' in self.values['data_select']:
                command += ' --param peak_d'
                command += ' --offset {}'.format(self.values['peak_value'])
                ax1_title = '{}: {:.1f}'.format(self.values['data_select'],self.values['peak_value'])
            elif 'Planting' in self.values['data_select']:
                command += ' --param plant_d'
                command += ' --offset {}'.format(self.values['plant_value'])
                ax1_title = '{}: {:.1f}'.format(self.values['data_select'],self.values['plant_value'])
            else:
                raise ValueError('{}: error, unknown data selection >>> {}'.format(self.proc_name,self.values['data_select']))
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'interp'))
            command += ' --tendir "{}"'.format(os.path.join(self.s2_data,'tentative_interp'))
            command += ' --out_csv "{}"'.format(select_csv)
            command += ' --out_shp "{}"'.format(select_shp)
            command += ' --fignam "{}"'.format(select_pdf)
            for value in self.zmin_refs:
                command += ' --ax1_zmin="{}"'.format(value)
            for value in self.zmin_nrefs:
                command += ' --ax1_zmin="{}"'.format(value)
            for value in self.zmin_inds:
                command += ' --ax1_zmin="{}"'.format(value)
            for value in self.zmax_refs:
                command += ' --ax1_zmax="{}"'.format(value)
            for value in self.zmax_nrefs:
                command += ' --ax1_zmax="{}"'.format(value)
            for value in self.zmax_inds:
                command += ' --ax1_zmax="{}"'.format(value)
            for value in self.zstp_refs:
                command += ' --ax1_zstp="{}"'.format(value)
            for value in self.zstp_nrefs:
                command += ' --ax1_zstp="{}"'.format(value)
            for value in self.zstp_inds:
                command += ' --ax1_zstp="{}"'.format(value)
            command += ' --ax1_title "{}"'.format(ax1_title)
            command += ' --use_index'
            command += ' --debug'
            command += ' --batch'
            self.run_command(command,message='<<< Select data >>>')

        # Estimate plot-mean
        estimate_csv = os.path.join(wrk_dir,'{}_estimate.csv'.format(trg_bnam))
        estimate_shp = os.path.join(wrk_dir,'{}_estimate.shp'.format(trg_bnam))
        estimate_pdf = os.path.join(wrk_dir,'{}_estimate.pdf'.format(trg_bnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_score_estimate.py'))
        command += ' --form_fnam "{}"'.format(self.values['pm_fnam'])
        command += ' --inp_shp "{}"'.format(self.values['gis_fnam'])
        if 'Specific' in self.values['data_select']:
            command += ' --inp_fnam "{}"'.format(spec_fnam)
            if 'Non-interpolated' in self.values['data_select']:
                command += ' --cr_band {}'.format(self.values['cloud_band'])
                list_labels = [s.split()[0] for s in self.list_labels['cloud_thr']]
                ithr = list_labels.index('Reflectance')
                command += ' --cthr {}'.format(self.values['cloud_thr'][ithr])
                if self.values['atcor_flag']:
                    command += ' --fact_fnam "{}"'.format(spec_gnam)
                    ithr = list_labels.index('Correlation')
                    command += ' --rthr {}'.format(self.values['cloud_thr'][ithr])
        else:
            command += ' --inp_csv "{}"'.format(select_csv)
        command += ' --out_shp "{}"'.format(estimate_shp)
        command += ' --out_csv "{}"'.format(estimate_csv)
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['pm_number'])
        command += ' --fignam "{}"'.format(estimate_pdf)
        for value,flag in zip(self.ax1_zmin,self.values['y_params']):
            if flag:
                command += ' --ax1_zmin="{}"'.format(value)
        for value,flag in zip(self.ax1_zmax,self.values['y_params']):
            if flag:
                command += ' --ax1_zmax="{}"'.format(value)
        for value,flag in zip(self.ax1_zstp,self.values['y_params']):
            if flag:
                command += ' --ax1_zstp="{}"'.format(value)
        command += ' --ax1_title "{}"'.format(ax1_title)
        command += ' --use_index'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Estimate plot-mean >>>')

        # Finish process
        super().finish()
        return
