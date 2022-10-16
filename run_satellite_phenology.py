import os
import sys
from datetime import datetime,timedelta
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
        finish_dtim = end_dtim+timedelta(days=self.values['assess_dthrs'][0])
        first_dtim = datetime.strptime(self.first_date,self.date_fmt)
        last_dtim = datetime.strptime(self.last_date,self.date_fmt)
        pref_dtim = datetime.strptime(self.values['trans_pref'],self.date_fmt)
        trg_bnam = '{:%Y%m%d}_{:%Y%m%d}'.format(start_dtim,end_dtim)
        wrk_dir = os.path.join(self.s2_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))
        mask_paddy = self.values['mask_paddy']
        if not os.path.exists(mask_paddy):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,mask_paddy))
        mask_parcel = self.values['mask_parcel']
        if not os.path.exists(mask_parcel):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,mask_parcel))

        # Select reference for planting
        planting_ref = os.path.join(self.s1_analysis,'planting','{}_planting_ref.tif'.format(trg_bnam))
        dnam = os.path.dirname(planting_ref)
        if not os.path.exists(dnam):
            os.makedirs(dnam)
        if not os.path.isdir(dnam):
            raise IOError('Error, no such folder >>> {}'.format(dnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_reference.py'))
        command += ' --datdir "{}"'.format(os.path.join(self.s1_data,'planting'))
        command += ' --dst_fnam "{}"'.format(planting_ref)
        command += ' --mask_fnam "{}"'.format(mask_paddy)
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

        # Calculate average for planting
        planting_avg = os.path.join(self.s1_analysis,'planting','{}_planting_avg.tif'.format(trg_bnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_average_reference.py'))
        command += ' --ref_fnam "{}"'.format(planting_ref)
        command += ' --dst_fnam "{}"'.format(planting_avg)
        command += ' --tmin {:%Y%m%d}'.format(start_dtim)
        command += ' --tmax {:%Y%m%d}'.format(end_dtim)
        self.run_command(command,message='<<< Calculate average for planting >>>')

        # Select planting
        planting_sel = os.path.join(self.s1_analysis,'planting','{}_planting.tif'.format(trg_bnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_all.py'))
        command += ' --datdir "{}"'.format(os.path.join(self.s1_data,'planting'))
        command += ' --stat_fnam "{}"'.format(planting_avg)
        command += ' --dst_fnam "{}"'.format(planting_sel)
        command += ' --mask_fnam "{}"'.format(mask_paddy)
        command += ' --tmin {:%Y%m%d}'.format(start_dtim)
        command += ' --tmax {:%Y%m%d}'.format(end_dtim)
        #command += ' --tref {:%Y%m%d}'.format(pref_dtim)
        if not np.isnan(self.values['trans_thr4'][0]):
            command += ' --trans_n_max {}'.format(self.values['trans_thr4'][0])
        if not np.isnan(self.values['trans_thr2'][0]):
            command += ' --bsc_min_max {}'.format(self.values['trans_thr2'][0])
        if not np.isnan(self.values['trans_thr2'][2]):
            command += ' --post_min_min {}'.format(self.values['trans_thr2'][2])
        if not np.isnan(self.values['trans_thr2'][3]):
            command += ' --post_avg_min {}'.format(self.values['trans_thr2'][3])
        if not np.isnan(self.values['trans_thr4'][1]):
            command += ' --risetime_max {}'.format(self.values['trans_thr4'][1])
        self.run_command(command,message='<<< Select planting >>>')

        # Parcellate planting
        planting_csv = os.path.join(self.s1_analysis,'planting','{}_planting.csv'.format(trg_bnam))
        planting_shp = os.path.join(self.s1_analysis,'planting','{}_planting.shp'.format(trg_bnam))
        planting_pdf = os.path.join(self.s1_analysis,'planting','{}_planting.pdf'.format(trg_bnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_parcellate.py'))
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --src_geotiff "{}"'.format(planting_sel)
        command += ' --mask_geotiff "{}"'.format(mask_parcel)
        command += ' --out_csv "{}"'.format(planting_csv)
        command += ' --out_shp "{}"'.format(planting_shp)
        command += ' --fignam "{}"'.format(planting_pdf)
        command += ' --ax1_title "Planting Date ({:%Y%m%d} - {:%Y%m%d})"'.format(start_dtim,end_dtim)
        command += ' --use_index'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Parcellate planting >>>')

        # Calculate assessment date
        assess_csv = os.path.join(wrk_dir,'{}_assess.csv'.format(trg_bnam))
        assess_shp = os.path.join(wrk_dir,'{}_assess.shp'.format(trg_bnam))
        assess_pdf = os.path.join(wrk_dir,'{}_assess.pdf'.format(trg_bnam))
        dnam = os.path.dirname(assess_csv)
        if not os.path.exists(dnam):
            os.makedirs(dnam)
        if not os.path.isdir(dnam):
            raise IOError('Error, no such folder >>> {}'.format(dnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'calc_assess_date.py'))
        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
        command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'interp'))
        command += ' --tendir "{}"'.format(os.path.join(self.s2_data,'tentative_interp'))
        command += ' --plant "{}"'.format(planting_csv)
        if self.values['head_fnam'] != '':
            command += ' --head "{}"'.format(self.values['head_fnam'])
        if self.values['harvest_fnam'] != '':
            command += ' --harvest "{}"'.format(self.values['harvest_fnam'])
        if self.values['assess_fnam'] != '':
            command += ' --assess "{}"'.format(self.values['assess_fnam'])
        command += ' --out_csv "{}"'.format(assess_csv)
        command += ' --out_shp "{}"'.format(assess_shp)
        command += ' --fignam "{}"'.format(assess_pdf)
        command += ' --smooth "{}"'.format(self.values['y1_smooth'])
        command += ' --atc {}'.format(self.values['atc_params'][0]*1.0e-2)
        command += ' --offset {}'.format(self.values['atc_params'][1])
        command += ' --sthr {}'.format(self.values['y1_thr'])
        command += ' --tmin {:%Y%m%d}'.format(start_dtim)
        command += ' --tmax {:%Y%m%d}'.format(finish_dtim)
        command += ' --data_tmin {:%Y%m%d}'.format(first_dtim)
        command += ' --data_tmax {:%Y%m%d}'.format(last_dtim)
        command += ' --grow_period {}'.format(self.values['assess_dthrs'][0])
        command += ' --dthr1 {}'.format(self.values['assess_dthrs'][1])
        command += ' --dthr2 {}'.format(self.values['assess_dthrs'][2])
        command += ' --use_index'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Calculate assessment date >>>')
        if os.path.exists(assess_shp):
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'draw_phenology.py'))
            command += ' --shp_fnam "{}"'.format(assess_shp)
            command += ' --fignam "{}"'.format(os.path.join(dnam,'{}_phenology.pdf'.format(trg_bnam)))
            command += ' --use_index'
            command += ' --batch'
            self.run_command(command,message='<<< Draw figure for {} >>>'.format(trg_bnam))

        # Finish process
        super().finish()
        return
