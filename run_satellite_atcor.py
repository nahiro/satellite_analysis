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
        wrk_dir = os.path.join(self.s2_data,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))
        mask_studyarea = self.values['mask_studyarea']
        if not os.path.exists(mask_studyarea):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,mask_studyarea))
        mask_parcel = self.values['mask_parcel']
        if not os.path.exists(mask_parcel):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,mask_parcel))

        # Select nearest pixels
        inds_npz = self.values['inds_fnam']
        if os.path.exists(inds_npz) and self.values['oflag'][2]:
            os.remove(inds_npz)
        if not os.path.exists(inds_npz):
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'atcor_select_reference.py'))
            command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'resample'))
            command += ' --out_fnam "{}"'.format(inds_npz)
            for band,flag in zip(self.list_labels['ref_band'],self.values['ref_band']):
                if flag:
                    command += ' --ref_band {}'.format(band.strip())
            command += ' --data_tmin {:%Y%m%d}'.format(d1)
            command += ' --data_tmax {:%Y%m%d}'.format(d2)
            command += ' --rthr {}'.format(self.values['ref_thr'])
            command += ' --n_nearest {}'.format(self.values['n_ref'])
            command += ' --use_index'
            self.run_command(command,message='<<< Select nearest pixels >>>')

        # Check Indices
        indices_fnams = []
        indices_dstrs = []
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.s2_data,'indices',ystr)
            if not os.path.isdir(dnam):
                continue
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_indices\.tif$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < first_dtim or d > last_dtim:
                    continue
                fnam = os.path.join(dnam,f)
                indices_fnams.append(fnam)
                indices_dstrs.append(dstr)
        inds = np.argsort(indices_dstrs)#[::-1]
        indices_fnams = [indices_fnams[i] for i in inds]
        indices_dstrs = [indices_dstrs[i] for i in inds]
        if len(indices_fnams) < 1:
            self.print_message('No indices data for process.',print_time=False)

        # Calculate stats
        stat_tif = self.values['stat_fnam']
        bnam,enam = os.path.splitext(stat_tif)
        stat_pdf = bnam+'.pdf'
        if os.path.exists(stat_tif) and self.values['oflag'][1]:
            os.remove(stat_tif)
        if not os.path.exists(stat_tif):
            command = self.python_path
            command += ' "{}"'.format(os.path.join(self.scr_dir,'atcor_calc_stat.py'))
            command += ' --inpdir "{}"'.format(os.path.join(self.s2_data,'indices'))
            command += ' --mask_fnam "{}"'.format(mask_studyarea)
            command += ' --dst_geotiff "{}"'.format(stat_tif)
            atcor_flag = False
            for param,flag in zip(self.list_labels['atcor_refs'],self.values['atcor_refs']):
                if flag:
                    command += ' --param S{}'.format(param.strip())
                    atcor_flag = True
            for param,flag in zip(self.list_labels['atcor_nrefs'],self.values['atcor_nrefs']):
                if flag:
                    command += ' --param {}'.format(param.strip())
                    atcor_flag = True
            for param,flag in zip(self.list_labels['atcor_inds'],self.values['atcor_inds']):
                if flag:
                    command += ' --param {}'.format(param.strip())
                    atcor_flag = True
            command += ' --cln_band {}'.format(self.values['clean_band'])
            command += ' --data_tmin {:%Y%m%d}'.format(d1)
            command += ' --data_tmax {:%Y%m%d}'.format(d2)
            command += ' --cthr_avg {}'.format(self.values['clean_thr'][0])
            command += ' --cthr_std {}'.format(self.values['clean_thr'][1])
            command += ' --cthr_dif {}'.format(self.values['clean_thr'][2])
            command += ' --cln_nmin {}'.format(self.values['clean_nmin'])
            command += ' --fignam "{}"'.format(stat_pdf)
            command += ' --debug'
            command += ' --batch'
            if atcor_flag:
                if len(indices_fnams) < 1:
                    raise IOError('No indices data')
                else:
                    self.run_command(command,message='<<< Calculate stats >>>')
            else:
                self.print_message('No parameters to be corrected.',print_time=False)

        # Calculate correction factor
        for fnam,dstr in zip(indices_fnams,indices_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_data,'atcor',ystr)
            fact_npz = os.path.join(dnam,'{}_factor.npz'.format(dstr))
            fact_pdf = os.path.join(dnam,'{}_factor.pdf'.format(dstr))
            if os.path.exists(fact_npz) and self.values['oflag'][3]:
                os.remove(fact_npz)
            if not os.path.exists(fact_npz):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_atcor_fit.py'))
                command += ' --src_geotiff "{}"'.format(fnam)
                command += ' --stat_fnam "{}"'.format(stat_tif)
                command += ' --inds_fnam "{}"'.format(inds_npz)
                command += ' --out_fnam "{}"'.format(fact_npz)
                atcor_flag = False
                for param,flag in zip(self.list_labels['atcor_refs'],self.values['atcor_refs']):
                    if flag:
                        command += ' --param S{}'.format(param.strip())
                        atcor_flag = True
                for param,flag in zip(self.list_labels['atcor_nrefs'],self.values['atcor_nrefs']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                        atcor_flag = True
                for param,flag in zip(self.list_labels['atcor_inds'],self.values['atcor_inds']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                        atcor_flag = True
                command += ' --cr_band {}'.format(self.values['cloud_band'])
                command += ' --cthr {}'.format(self.values['cloud_thr'])
                command += ' --nstp {}'.format(self.values['nstp'])
                command += ' --ethr {}'.format(self.values['rel_thr'])
                command += ' --fignam "{}"'.format(fact_pdf)
                command += ' --nfig 10'
                command += ' --debug'
                command += ' --batch'
                if atcor_flag:
                    self.run_command(command,message='<<< Calculate correction factor for {} >>>'.format(dstr))

        # Atmospheric correction
        for fnam,dstr in zip(indices_fnams,indices_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_data,'parcel',ystr)
            data_npz = os.path.join(dnam,'{}_parcel.npz'.format(dstr))
            if not os.path.exists(data_npz):
                raise ValueError('Error, no such file >>> {}'.format(data_npz))
            dnam = os.path.join(self.s2_data,'atcor',ystr)
            fact_npz = os.path.join(dnam,'{}_factor.npz'.format(dstr))
            atcor_npz = os.path.join(dnam,'{}_atcor.npz'.format(dstr))
            atcor_shp = os.path.join(dnam,'{}_atcor.shp'.format(dstr))
            atcor_pdf = os.path.join(dnam,'{}_atcor.pdf'.format(dstr))
            if os.path.exists(atcor_npz) and self.values['oflag'][4]:
                os.remove(atcor_npz)
            if not os.path.exists(atcor_npz):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_atcor_correct.py'))
                command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                command += ' --mask_geotiff "{}"'.format(mask_parcel)
                command += ' --src_geotiff "{}"'.format(fnam)
                command += ' --parcel_fnam "{}"'.format(data_npz)
                command += ' --atcor_fnam "{}"'.format(fact_npz)
                command += ' --out_fnam "{}"'.format(atcor_npz)
                command += ' --out_shp "{}"'.format(atcor_shp)
                for param,flag in zip(self.list_labels['out_refs'],self.values['out_refs']):
                    if flag:
                        command += ' --param S{}'.format(param.strip())
                for param,flag in zip(self.list_labels['out_nrefs'],self.values['out_nrefs']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                for param,flag in zip(self.list_labels['out_inds'],self.values['out_inds']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                atcor_flag = False
                for param,flag in zip(self.list_labels['atcor_refs'],self.values['atcor_refs']):
                    if flag:
                        command += ' --atcor_param S{}'.format(param.strip())
                        atcor_flag = True
                for param,flag in zip(self.list_labels['atcor_nrefs'],self.values['atcor_nrefs']):
                    if flag:
                        command += ' --atcor_param {}'.format(param.strip())
                        atcor_flag = True
                for param,flag in zip(self.list_labels['atcor_inds'],self.values['atcor_inds']):
                    if flag:
                        command += ' --atcor_param {}'.format(param.strip())
                        atcor_flag = True
                command += ' --cr_band {}'.format(self.values['cloud_band'])
                command += ' --cthr {}'.format(self.values['cloud_thr'])
                command += ' --r_min {}'.format(self.values['fit_thr'])
                command += ' --fignam "{}"'.format(atcor_pdf)
                command += ' --use_index'
                command += ' --debug'
                command += ' --batch'
                if atcor_flag:
                    self.run_command(command,message='<<< Atmospheric correction for {} >>>'.format(dstr))

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
