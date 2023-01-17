import os
import sys
import shutil
import json
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
        mask_parcel = self.values['mask_parcel']
        iflag = self.list_labels['oflag'].index('mask')
        flag_paddy = self.values['oflag'][iflag]
        flag_parcel = self.values['oflag'][iflag]
        list_labels = [s[0].split()[0] for s in self.list_labels['trans_source']]
        product = self.values['trans_source'][list_labels.index('Product')]
        version = self.values['trans_source'][list_labels.index('Version')]
        if version == '':
            s1_data = os.path.join(self.s1_data,product)
        else:
            s1_data = os.path.join(self.s1_data,product,version)

        if 'bojongsoang' in self.values['trans_select'].lower():
            # Select reference for planting
            dnam = os.path.join(self.s1_analysis,'planting')
            planting_ref = os.path.join(dnam,'{}_planting_ref.shp'.format(trg_bnam))
            iflag = self.list_labels['oflag'].index('plant')
            if self.values['oflag'][iflag]:
                if os.path.exists(planting_ref):
                    os.remove(planting_ref)
            if not os.path.exists(planting_ref):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                # Select
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_reference_fi.py'))
                command += ' --datdir "{}"'.format(s1_data)
                command += ' --out_shp "{}"'.format(planting_ref)
                command += ' --tmin {:%Y%m%d}'.format(start_dtim)
                command += ' --tmax {:%Y%m%d}'.format(end_dtim)
                command += ' --tref {:%Y%m%d}'.format(pref_dtim)
                if not np.isnan(self.values['trans_thr1'][0]):
                    command += ' --bsc_min_max {}'.format(self.values['trans_thr1'][0])
                if not np.isnan(self.values['trans_thr1'][3]):
                    command += ' --post_s_min {}'.format(self.values['trans_thr1'][3])
                command += ' --use_index'
                self.run_command(command,message='<<< Select reference for planting >>>')
            else:
                self.print_message('File exists >>> {}'.format(planting_ref),print_time=False)

            # Select planting
            planting_csv = os.path.join(dnam,'{}_planting.csv'.format(trg_bnam))
            planting_shp = os.path.join(dnam,'{}_planting.shp'.format(trg_bnam))
            planting_pdf = os.path.join(dnam,'{}_planting.pdf'.format(trg_bnam))
            if self.values['oflag'][iflag]:
                if os.path.exists(planting_csv):
                    os.remove(planting_csv)
                if os.path.exists(planting_shp):
                    os.remove(planting_shp)
                if os.path.exists(planting_pdf):
                    os.remove(planting_pdf)
            if not os.path.exists(planting_csv):
                # Select
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_all_fi.py'))
                command += ' --datdir "{}"'.format(s1_data)
                command += ' --ref_fnam "{}"'.format(planting_ref)
                command += ' --out_csv "{}"'.format(planting_csv)
                command += ' --out_shp "{}"'.format(planting_shp)
                command += ' --tmin {:%Y%m%d}'.format(start_dtim)
                command += ' --tmax {:%Y%m%d}'.format(end_dtim)
                if not np.isnan(self.values['trans_thr2'][0]):
                    command += ' --bsc_min_max {}'.format(self.values['trans_thr2'][0])
                if not np.isnan(self.values['trans_thr2'][3]):
                    command += ' --post_s_min {}'.format(self.values['trans_thr2'][3])
                command += ' --fignam "{}"'.format(planting_pdf)
                command += ' --fig_title "Planting Date ({:%Y%m%d} - {:%Y%m%d})"'.format(start_dtim,end_dtim)
                command += ' --use_index'
                command += ' --add_tmin'
                command += ' --add_tmax'
                command += ' --debug'
                command += ' --batch'
                self.run_command(command,message='<<< Select planting >>>')
            else:
                self.print_message('File exists >>> {}'.format(planting_csv),print_time=False)
        else:
            # Select reference for planting
            dnam = os.path.join(self.s1_analysis,'planting')
            planting_ref = os.path.join(dnam,'{}_planting_ref.tif'.format(trg_bnam))
            iflag = self.list_labels['oflag'].index('plant')
            if self.values['oflag'][iflag]:
                if os.path.exists(planting_ref):
                    os.remove(planting_ref)
            if not os.path.exists(planting_ref):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                # Make paddy mask
                if os.path.exists(mask_paddy) and flag_paddy:
                    os.remove(mask_paddy)
                if not os.path.exists(mask_paddy):
                    mask_dnam = os.path.dirname(mask_paddy)
                    if not os.path.exists(mask_dnam):
                        os.makedirs(mask_dnam)
                    if not os.path.isdir(mask_dnam):
                        raise IOError('Error, no such folder >>> {}'.format(mask_dnam))
                    if os.path.exists(mask_parcel) and not flag_parcel and (self.values['buffer_paddy'] == self.values['buffer_parcel']):
                        shutil.copy2(mask_parcel,mask_paddy)
                    else:
                        src_fnam = None
                        years = np.arange(start_dtim.year,end_dtim.year+2,1)
                        for year in years:
                            ystr = '{}'.format(year)
                            dnam = os.path.join(s1_data,ystr)
                            if not os.path.isdir(dnam):
                                continue
                            for f in sorted(os.listdir(dnam)):
                                if not re.search('_final.tif',f):
                                    continue
                                bnam = os.path.basename(f)
                                fnam = os.path.join(dnam,f)
                                gnam = os.path.join(dnam,'{}.json'.format(bnam))
                                if not os.path.exists(gnam):
                                    continue
                                with open(gnam,'r') as fp:
                                    data_info = json.load(fp)
                                tmin = datetime.strptime(data_info['tmin'],'%Y%m%d')
                                tmax = datetime.strptime(data_info['tmax'],'%Y%m%d')
                                if tmin < end_dtim and tmax > start_dtim:
                                    src_fnam = fnam
                                    break
                            if src_fnam is not None:
                                break
                        if src_fnam is None:
                            raise IOError('Error, no planting data between {:%Y%m%d} - {:%Y%m%d}'.format(start_dtim,end_dtim))
                        command = self.python_path
                        command += ' "{}"'.format(os.path.join(self.scr_dir,'make_mask.py'))
                        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                        command += ' --src_geotiff "{}"'.format(src_fnam)
                        command += ' --dst_geotiff "{}"'.format(mask_paddy)
                        if abs(self.values['buffer_paddy']) < 1.0e-6:
                            command += ' --buffer 0.0'
                        else:
                            command += ' --buffer="{}"'.format(-abs(self.values['buffer_paddy']))
                        command += ' --use_index'
                        self.run_command(command,message='<<< Make paddy mask >>>')
                if not os.path.exists(mask_paddy):
                    raise ValueError('Error, no such file >>> {}'.format(mask_paddy))
                else:
                    flag_paddy = False
                # Select
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_reference.py'))
                command += ' --datdir "{}"'.format(s1_data)
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
            else:
                self.print_message('File exists >>> {}'.format(planting_ref),print_time=False)

            # Calculate average for planting
            planting_avg = os.path.join(dnam,'{}_planting_avg.tif'.format(trg_bnam))
            if self.values['oflag'][iflag]:
                if os.path.exists(planting_avg):
                    os.remove(planting_avg)
            if not os.path.exists(planting_avg):
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_average_reference.py'))
                command += ' --ref_fnam "{}"'.format(planting_ref)
                command += ' --dst_fnam "{}"'.format(planting_avg)
                command += ' --tmin {:%Y%m%d}'.format(start_dtim)
                command += ' --tmax {:%Y%m%d}'.format(end_dtim)
                self.run_command(command,message='<<< Calculate average for planting >>>')
            else:
                self.print_message('File exists >>> {}'.format(planting_avg),print_time=False)

            # Select planting
            planting_sel = os.path.join(dnam,'{}_planting.tif'.format(trg_bnam))
            if self.values['oflag'][iflag]:
                if os.path.exists(planting_sel):
                    os.remove(planting_sel)
            if not os.path.exists(planting_sel):
                # Make paddy mask
                if os.path.exists(mask_paddy) and flag_paddy:
                    os.remove(mask_paddy)
                if not os.path.exists(mask_paddy):
                    mask_dnam = os.path.dirname(mask_paddy)
                    if not os.path.exists(mask_dnam):
                        os.makedirs(mask_dnam)
                    if not os.path.isdir(mask_dnam):
                        raise IOError('Error, no such folder >>> {}'.format(mask_dnam))
                    if os.path.exists(mask_parcel) and not flag_parcel and (self.values['buffer_paddy'] == self.values['buffer_parcel']):
                        shutil.copy2(mask_parcel,mask_paddy)
                    else:
                        command = self.python_path
                        command += ' "{}"'.format(os.path.join(self.scr_dir,'make_mask.py'))
                        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                        command += ' --src_geotiff "{}"'.format(planting_avg)
                        command += ' --dst_geotiff "{}"'.format(mask_paddy)
                        if abs(self.values['buffer_paddy']) < 1.0e-6:
                            command += ' --buffer 0.0'
                        else:
                            command += ' --buffer="{}"'.format(-abs(self.values['buffer_paddy']))
                        command += ' --use_index'
                        self.run_command(command,message='<<< Make paddy mask >>>')
                if not os.path.exists(mask_paddy):
                    raise ValueError('Error, no such file >>> {}'.format(mask_paddy))
                else:
                    flag_paddy = False
                # Select
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_select_all.py'))
                command += ' --datdir "{}"'.format(s1_data)
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
            else:
                self.print_message('File exists >>> {}'.format(planting_sel),print_time=False)

            # Parcellate planting
            planting_csv = os.path.join(dnam,'{}_planting.csv'.format(trg_bnam))
            planting_shp = os.path.join(dnam,'{}_planting.shp'.format(trg_bnam))
            planting_pdf = os.path.join(dnam,'{}_planting.pdf'.format(trg_bnam))
            if self.values['oflag'][iflag]:
                if os.path.exists(planting_csv):
                    os.remove(planting_csv)
                if os.path.exists(planting_shp):
                    os.remove(planting_shp)
                if os.path.exists(planting_pdf):
                    os.remove(planting_pdf)
            if not os.path.exists(planting_csv):
                # Make parcel mask
                if os.path.exists(mask_parcel) and flag_parcel:
                    os.remove(mask_parcel)
                if not os.path.exists(mask_parcel):
                    mask_dnam = os.path.dirname(mask_parcel)
                    if not os.path.exists(mask_dnam):
                        os.makedirs(mask_dnam)
                    if not os.path.isdir(mask_dnam):
                        raise IOError('Error, no such folder >>> {}'.format(mask_dnam))
                    if os.path.exists(mask_paddy) and not flag_paddy and (self.values['buffer_parcel'] == self.values['buffer_paddy']):
                        shutil.copy2(mask_paddy,mask_parcel)
                    else:
                        command = self.python_path
                        command += ' "{}"'.format(os.path.join(self.scr_dir,'make_mask.py'))
                        command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                        command += ' --src_geotiff "{}"'.format(planting_sel)
                        command += ' --dst_geotiff "{}"'.format(mask_parcel)
                        if abs(self.values['buffer_parcel']) < 1.0e-6:
                            command += ' --buffer 0.0'
                        else:
                            command += ' --buffer="{}"'.format(-abs(self.values['buffer_parcel']))
                        command += ' --use_index'
                        self.run_command(command,message='<<< Make parcel mask >>>')
                if not os.path.exists(mask_parcel):
                    raise ValueError('Error, no such file >>> {}'.format(mask_parcel))
                else:
                    flag_parcel = False
                # Parcellate
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'trans_parcellate.py'))
                command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                command += ' --src_geotiff "{}"'.format(planting_sel)
                command += ' --mask_geotiff "{}"'.format(mask_parcel)
                command += ' --out_csv "{}"'.format(planting_csv)
                command += ' --out_shp "{}"'.format(planting_shp)
                command += ' --fignam "{}"'.format(planting_pdf)
                command += ' --ax1_title "Planting Date ({:%Y%m%d} - {:%Y%m%d})"'.format(start_dtim,end_dtim)
                command += ' --tmin {:%Y%m%d}'.format(start_dtim)
                command += ' --tmax {:%Y%m%d}'.format(end_dtim)
                command += ' --use_index'
                command += ' --remove_nan'
                command += ' --add_tmin'
                command += ' --add_tmax'
                command += ' --debug'
                command += ' --batch'
                self.run_command(command,message='<<< Parcellate planting >>>')
            else:
                self.print_message('File exists >>> {}'.format(planting_csv),print_time=False)

        # Calculate assessment date
        assess_csv = os.path.join(wrk_dir,'{}_assess.csv'.format(trg_bnam))
        assess_shp = os.path.join(wrk_dir,'{}_assess.shp'.format(trg_bnam))
        assess_pdf = os.path.join(wrk_dir,'{}_assess.pdf'.format(trg_bnam))
        phenology_pdf = os.path.join(wrk_dir,'{}_phenology.pdf'.format(trg_bnam))
        iflag = self.list_labels['oflag'].index('assess')
        if self.values['oflag'][iflag]:
            if os.path.exists(assess_csv):
                os.remove(assess_csv)
            if os.path.exists(assess_shp):
                os.remove(assess_shp)
            if os.path.exists(assess_pdf):
                os.remove(assess_pdf)
            if os.path.exists(phenology_pdf):
                os.remove(phenology_pdf)
        if not os.path.exists(assess_csv):
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
            command += ' --atc {}'.format(self.values['atc_params'][0])
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
                command += ' --fignam "{}"'.format(phenology_pdf)
                command += ' --use_index'
                command += ' --batch'
                self.run_command(command,message='<<< Draw figure for {} >>>'.format(trg_bnam))
        else:
            self.print_message('File exists >>> {}'.format(assess_csv),print_time=False)

        # Finish process
        super().finish()
        return
