import os
import sys
import re
from datetime import datetime,timedelta
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
        self.zmin_refs = None
        self.zmax_refs = None
        self.zstp_refs = None
        self.zmin_nrefs = None
        self.zmax_nrefs = None
        self.zstp_nrefs = None
        self.zmin_inds = None
        self.zmax_inds = None
        self.zstp_inds = None
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
        wrk_dir = os.path.join(self.s2_data,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))
        iflag = self.list_labels['oflag'].index('mask')
        flag_parcel = self.values['oflag'][iflag]
        flag_studyarea = self.values['oflag'][iflag]

        # Check Indices
        indices_fnams = []
        indices_dstrs = []
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.values['indices_dir'],ystr)
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
            raise IOError('No indices data for process.')

        # Select nearest pixels
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(wrk_dir,ystr)
            inds_npz = os.path.join(dnam,'nearest_inds.npz')
            iflag = self.list_labels['oflag'].index('index')
            if os.path.exists(inds_npz) and self.values['oflag'][iflag]:
                os.remove(inds_npz)
            if not os.path.exists(inds_npz):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                d2 = datetime(year,1,1)-timedelta(days=1)
                d1 = d2-timedelta(days=self.values['stat_period'])
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'atcor_select_reference.py'))
                command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                command += ' --inpdir "{}"'.format(self.values['geocor_dir'])
                command += ' --out_fnam "{}"'.format(inds_npz)
                for band,flag in zip(self.list_labels['ref_band'],self.values['ref_band']):
                    if flag:
                        command += ' --ref_band {}'.format(band.strip())
                command += ' --data_tmin {:%Y%m%d}'.format(d1)
                command += ' --data_tmax {:%Y%m%d}'.format(d2)
                command += ' --nmin {}'.format(self.values['stat_nmin'])
                command += ' --rthr {}'.format(self.values['ref_thr'])
                command += ' --n_nearest {}'.format(self.values['n_ref'])
                command += ' --use_index'
                self.run_command(command,message='<<< Select nearest pixels for {} >>>'.format(ystr))

        # Calculate stats
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(wrk_dir,ystr)
            stat_tif = os.path.join(dnam,'atcor_stat.tif')
            bnam,enam = os.path.splitext(stat_tif)
            stat_pdf = bnam+'.pdf'
            iflag = self.list_labels['oflag'].index('stats')
            if os.path.exists(stat_tif) and self.values['oflag'][iflag]:
                os.remove(stat_tif)
            if not os.path.exists(stat_tif):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                # Make mask
                mask_studyarea = self.values['mask_studyarea']
                if os.path.exists(mask_studyarea) and flag_studyarea:
                    os.remove(mask_studyarea)
                if not os.path.exists(mask_studyarea):
                    mask_dnam = os.path.dirname(mask_studyarea)
                    if not os.path.exists(mask_dnam):
                        os.makedirs(mask_dnam)
                    if not os.path.isdir(mask_dnam):
                        raise IOError('Error, no such folder >>> {}'.format(mask_dnam))
                    list_labels = [s.split()[0] for s in self.list_labels['p1_studyarea']]
                    x0 = self.values['p1_studyarea'][list_labels.index('X0')]
                    y0 = self.values['p1_studyarea'][list_labels.index('Y0')]
                    lmin = self.values['p1_studyarea'][list_labels.index('Lmin')]
                    lmax = self.values['p1_studyarea'][list_labels.index('Lmax')]
                    lstp = self.values['p1_studyarea'][list_labels.index('Lstp')]
                    buff = self.values['p1_studyarea'][list_labels.index('Buffer')]
                    list_labels = [s.split()[0] for s in self.list_labels['p2_studyarea']]
                    dmax = self.values['p2_studyarea'][list_labels.index('Dmax')]
                    athr = self.values['p2_studyarea'][list_labels.index('Athr')]
                    command = self.python_path
                    command += ' "{}"'.format(os.path.join(self.scr_dir,'trace_outline.py'))
                    command += ' --src_geotiff "{}"'.format(fnam)
                    command += ' --dst_geotiff "{}"'.format(mask_studyarea)
                    command += ' --buffer="{}"'.format(buff)
                    if not np.isnan(x0) and not np.isnan(y0):
                        command += ' --x0 {}'.format(x0)
                        command += ' --y0 {}'.format(y0)
                    command += ' --lmin {}'.format(lmin)
                    command += ' --lmax {}'.format(lmax)
                    command += ' --lmstp{}'.format(lstp)
                    command += ' --dmax {}'.format(dmax)
                    if not np.isnan(athr):
                        command += ' --athr {}'.format(athr)
                        command += ' --fcc'
                    self.run_command(command,message='<<< Make mask >>>')
                if not os.path.exists(mask_studyarea):
                    raise ValueError('Error, no such file >>> {}'.format(mask_studyarea))
                else:
                    flag_studyarea = False
                # Stats
                d2 = datetime(year,1,1)-timedelta(days=1)
                d1 = d2-timedelta(days=self.values['stat_period'])
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'atcor_calc_stat.py'))
                command += ' --inpdir "{}"'.format(self.values['indices_dir'])
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
                        raise IOError('No indices data to calculate stats for {}'.format(ystr))
                    else:
                        self.run_command(command,message='<<< Calculate stats for {} >>>'.format(ystr))
                else:
                    self.print_message('No parameters to be corrected for {}.'.format(ystr),print_time=False)

        # Calculate correction factor
        for fnam,dstr in zip(indices_fnams,indices_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(wrk_dir,ystr)
            inds_npz = os.path.join(dnam,'nearest_inds.npz')
            stat_tif = os.path.join(dnam,'atcor_stat.tif')
            fact_npz = os.path.join(dnam,'{}_factor.npz'.format(dstr))
            fact_pdf = os.path.join(dnam,'{}_factor.pdf'.format(dstr))
            iflag = self.list_labels['oflag'].index('factor')
            if os.path.exists(fact_npz) and self.values['oflag'][iflag]:
                os.remove(fact_npz)
            if not os.path.exists(fact_npz):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_atcor_fit.py'))
                command += ' --src_geotiff "{}"'.format(fnam)
                command += ' --inds_fnam "{}"'.format(inds_npz)
                command += ' --stat_fnam "{}"'.format(stat_tif)
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
                command += ' --ax1_title "{}"'.format(dstr)
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
            dnam = os.path.join(wrk_dir,ystr)
            fact_npz = os.path.join(dnam,'{}_factor.npz'.format(dstr))
            atcor_npz = os.path.join(dnam,'{}_atcor.npz'.format(dstr))
            atcor_shp = os.path.join(dnam,'{}_atcor.shp'.format(dstr))
            atcor_pdf = os.path.join(dnam,'{}_atcor.pdf'.format(dstr))
            iflag = self.list_labels['oflag'].index('atcor')
            if os.path.exists(atcor_npz) and self.values['oflag'][iflag]:
                os.remove(atcor_npz)
            if self.values['csv_flag']:
                atcor_csv = os.path.join(dnam,'{}_atcor.csv'.format(dstr))
                if os.path.exists(atcor_csv):
                    if self.values['oflag'][iflag]:
                        os.remove(atcor_csv)
                elif os.path.exists(atcor_npz):
                    os.remove(atcor_npz)
            if not os.path.exists(atcor_npz):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                # Make mask
                mask_parcel = self.values['mask_parcel']
                if os.path.exists(mask_parcel) and flag_parcel:
                    os.remove(mask_parcel)
                if not os.path.exists(mask_parcel):
                    mask_dnam = os.path.dirname(mask_parcel)
                    if not os.path.exists(mask_dnam):
                        os.makedirs(mask_dnam)
                    if not os.path.isdir(mask_dnam):
                        raise IOError('Error, no such folder >>> {}'.format(mask_dnam))
                    command = self.python_path
                    command += ' "{}"'.format(os.path.join(self.scr_dir,'make_mask.py'))
                    command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                    command += ' --src_geotiff "{}"'.format(fnam)
                    command += ' --dst_geotiff "{}"'.format(mask_parcel)
                    if abs(self.values['buffer_parcel']) < 1.0e-6:
                        command += ' --buffer 0.0'
                    else:
                        command += ' --buffer="{}"'.format(-abs(self.values['buffer_parcel']))
                    command += ' --use_index'
                    self.run_command(command,message='<<< Make mask >>>')
                if not os.path.exists(mask_parcel):
                    raise ValueError('Error, no such file >>> {}'.format(mask_parcel))
                else:
                    flag_parcel = False
                # Correct
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_atcor_correct.py'))
                command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                command += ' --mask_geotiff "{}"'.format(mask_parcel)
                command += ' --src_geotiff "{}"'.format(fnam)
                command += ' --parcel_fnam "{}"'.format(data_npz)
                command += ' --atcor_fnam "{}"'.format(fact_npz)
                command += ' --out_fnam "{}"'.format(atcor_npz)
                command += ' --out_shp "{}"'.format(atcor_shp)
                if self.values['csv_flag']:
                    command += ' --out_csv "{}"'.format(atcor_csv)
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
                for value,flag in zip(self.zmin_refs,self.values['out_refs']):
                    if flag:
                        command += ' --ax1_zmin="{}"'.format(value)
                for value,flag in zip(self.zmin_nrefs,self.values['out_nrefs']):
                    if flag:
                        command += ' --ax1_zmin="{}"'.format(value)
                for value,flag in zip(self.zmin_inds,self.values['out_inds']):
                    if flag:
                        command += ' --ax1_zmin="{}"'.format(value)
                for value,flag in zip(self.zmax_refs,self.values['out_refs']):
                    if flag:
                        command += ' --ax1_zmax="{}"'.format(value)
                for value,flag in zip(self.zmax_nrefs,self.values['out_nrefs']):
                    if flag:
                        command += ' --ax1_zmax="{}"'.format(value)
                for value,flag in zip(self.zmax_inds,self.values['out_inds']):
                    if flag:
                        command += ' --ax1_zmax="{}"'.format(value)
                for value,flag in zip(self.zstp_refs,self.values['out_refs']):
                    if flag:
                        command += ' --ax1_zstp="{}"'.format(value)
                for value,flag in zip(self.zstp_nrefs,self.values['out_nrefs']):
                    if flag:
                        command += ' --ax1_zstp="{}"'.format(value)
                for value,flag in zip(self.zstp_inds,self.values['out_inds']):
                    if flag:
                        command += ' --ax1_zstp="{}"'.format(value)
                command += ' --ax1_title "{}"'.format(dstr)
                command += ' --use_index'
                command += ' --debug'
                command += ' --batch'
                if atcor_flag:
                    self.run_command(command,message='<<< Atmospheric correction for {} >>>'.format(dstr))

        # Finish process
        super().finish()
        return
