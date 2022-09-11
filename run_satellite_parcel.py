import os
import sys
import re
from datetime import datetime
import numpy as np
from proc_satellite_class import Satellite_Process

class Parcel(Satellite_Process):

    def __init__(self):
        super().__init__()
        self.ax1_zmin = None
        self.ax1_zmax = None
        self.ax1_zstp = None
        self.fig_dpi = None
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
        if not os.path.exists(self.s2_data):
            os.makedirs(self.s2_data)
        if not os.path.isdir(self.s2_data):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_data))

        # Check Resample
        resample_fnams = []
        resample_dstrs = []
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.s2_data,'resample',ystr)
            if not os.path.isdir(dnam):
                continue
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_resample\.tif$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < first_dtim or d > last_dtim:
                    continue
                fnam = os.path.join(dnam,f)
                resample_fnams.append(fnam)
                resample_dstrs.append(dstr)
        inds = np.argsort(resample_dstrs)#[::-1]
        resample_fnams = [resample_fnams[i] for i in inds]
        resample_dstrs = [resample_dstrs[i] for i in inds]
        if len(resample_fnams) < 1:
            self.print_message('No resample data for process.',print_time=False)

        # Calculate indices
        indices_fnams = []
        indices_rnams = []
        indices_dstrs = []
        for fnam,dstr in zip(resample_fnams,resample_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_data,'indices',ystr)
            gnam = os.path.join(dnam,'{}_indices.tif'.format(dstr))
            if os.path.exists(gnam) and self.values['oflag'][0]:
                os.remove(gnam)
            if not os.path.exists(gnam):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_calc_indices.py'))
                command += ' --src_geotiff "{}"'.format(fnam)
                command += ' --dst_geotiff "{}"'.format(gnam)
                command += ' --fignam "{}"'.format(os.path.join(dnam,'{}_indices.pdf'.format(dstr)))
                for param,flag in zip(self.list_labels['out_refs'],self.values['out_refs']):
                    if flag:
                        command += ' --param S{}'.format(param.strip())
                for param,flag in zip(self.list_labels['out_nrefs'],self.values['out_nrefs']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                for param,flag in zip(self.list_labels['out_inds'],self.values['out_inds']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                for band,flag in zip(self.list_labels['norm_bands'],self.values['norm_bands']):
                    if flag:
                        command += ' --norm_band {}'.format(band.strip())
                command += ' --rgi_red_band {}'.format(self.values['rgi_red_band'])
                #for value,flag in zip(self.ax1_zmin,self.values['out_refs']):
                #    if flag:
                #        command += ' --ax1_zmin="{}"'.format(value)
                #for value,flag in zip(self.ax1_zmax,self.values['out_refs']):
                #    if flag:
                #        command += ' --ax1_zmax="{}"'.format(value)
                #for value,flag in zip(self.ax1_zstp,self.values['out_refs']):
                #    if flag:
                #        command += ' --ax1_zstp="{}"'.format(value)
                command += ' --ax1_title "{}"'.format(dstr)
                #command += ' --fig_dpi {}'.format(self.fig_dpi)
                command += ' --remove_nan'
                command += ' --debug'
                command += ' --batch'
                self.run_command(command,message='<<< Calculate indices for {} >>>'.format(dstr))
            if os.path.exists(gnam):
                indices_fnams.append(gnam)
                indices_rnams.append(fnam)
                indices_dstrs.append(dstr)

        # Parcellate data
        for fnam,rnam,dstr in zip(indices_fnams,indices_rnams,indices_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_data,'parcel',ystr)
            npz_fnam = os.path.join(dnam,'{}_parcel.npz'.format(dstr))
            if os.path.exists(npz_fnam) and self.values['oflag'][1]:
                os.remove(npz_fnam)
            if self['csv_flag']:
                csv_fnam = os.path.join(dnam,'{}_parcel.csv'.format(dstr))
                if os.path.exists(csv_fnam):
                    if self.values['oflag'][1]:
                        os.remove(csv_fnam)
                elif os.path.exists(npz_fnam):
                    os.remove(npz_fnam)
            if not os.path.exists(npz_fnam):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                # Make mask
                mask_fnam = self.values['mask_parcel']
                if not os.path.exists(mask_fnam):
                    command = self.python_path
                    command += ' "{}"'.format(os.path.join(self.scr_dir,'make_mask.py'))
                    command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                    command += ' --src_geotiff "{}"'.format(fnam)
                    command += ' --dst_geotiff "{}"'.format(mask_fnam)
                    if abs(self.values['buffer']) < 1.0e-6:
                        command += ' --buffer 0.0'
                    else:
                        command += ' --buffer="{}"'.format(-abs(self.values['buffer']))
                    command += ' --use_index'
                    self.run_command(command,message='<<< Make mask >>>')
                if not os.path.exists(mask_fnam):
                    raise ValueError('Error, no such file >>> {}'.format(mask_fnam))
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_parcellate.py'))
                command += ' --src_geotiff "{}"'.format(fnam)
                command += ' --res_geotiff "{}"'.format(rnam)
                command += ' --mask_geotiff "{}"'.format(mask_fnam)
                command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                command += ' --out_fnam "{}"'.format(npz_fnam)
                command += ' --out_shp "{}"'.format(os.path.join(dnam,'{}_parcel.shp'.format(dstr)))
                for param,flag in zip(self.list_labels['out_refs'],self.values['out_refs']):
                    if flag:
                        command += ' --param S{}'.format(param.strip())
                for param,flag in zip(self.list_labels['out_nrefs'],self.values['out_nrefs']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                for param,flag in zip(self.list_labels['out_inds'],self.values['out_inds']):
                    if flag:
                        command += ' --param {}'.format(param.strip())
                for param,flag,value in zip(self.list_labels['out_refs'],self.values['out_refs'],self.values['cr_sc_refs']):
                    if flag:
                        command += ' --cflag_sc "S{}:{}"'.format(param.strip(),value)
                for param,flag,value in zip(self.list_labels['out_nrefs'],self.values['out_nrefs'],self.values['cr_sc_nrefs']):
                    if flag:
                        command += ' --cflag_sc "{}:{}"'.format(param.strip(),value)
                for param,flag,value in zip(self.list_labels['out_inds'],self.values['out_inds'],self.values['cr_sc_inds']):
                    if flag:
                        command += ' --cflag_sc "{}:{}"'.format(param.strip(),value)
                for param,flag,value in zip(self.list_labels['out_refs'],self.values['out_refs'],self.values['cr_ref_refs']):
                    if flag:
                        command += ' --cflag_ref "S{}:{}"'.format(param.strip(),value)
                for param,flag,value in zip(self.list_labels['out_nrefs'],self.values['out_nrefs'],self.values['cr_ref_nrefs']):
                    if flag:
                        command += ' --cflag_ref "{}:{}"'.format(param.strip(),value)
                for param,flag,value in zip(self.list_labels['out_inds'],self.values['out_inds'],self.values['cr_ref_inds']):
                    if flag:
                        command += ' --cflag_ref "{}:{}"'.format(param.strip(),value)
                command += ' --cloud_band {}'.format(self.values['cloud_band'])
                command += ' --cloud_thr {}'.format(self.values['cloud_thr'])
                command += ' --fignam "{}"'.format(os.path.join(dnam,'{}_parcel.pdf'.format(dstr)))
                #for value,flag in zip(self.ax1_zmin[2],self.values['out_refs']):
                #    if flag:
                #        command += ' --ax1_zmin="{}"'.format(value)
                #for value,flag in zip(self.ax1_zmax[2],self.values['out_refs']):
                #    if flag:
                #        command += ' --ax1_zmax="{}"'.format(value)
                #for value,flag in zip(self.ax1_zstp[2],self.values['out_refs']):
                #    if flag:
                #        command += ' --ax1_zstp="{}"'.format(value)
                command += ' --ax1_title "{}"'.format(dstr)
                command += ' --use_index'
                command += ' --remove_nan'
                command += ' --debug'
                command += ' --batch'
                self.run_command(command,message='<<< Parcellate data for {} >>>'.format(dstr))

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
