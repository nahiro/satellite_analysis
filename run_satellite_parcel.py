import os
import sys
import re
from datetime import datetime
import numpy as np
from proc_satellite_class import Satellite_Process

class Parcel(Satellite_Process):

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
        iflag = self.list_labels['oflag'].index('mask')
        flag_parcel = self.values['oflag'][iflag]

        # Check Indices
        indices_fnams = []
        indices_rnams = []
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
                rnam = os.path.join(self.values['geocor_dir'],ystr,'{}_geocor.tif'.format(dstr))
                if os.path.exists(rnam):
                    indices_fnams.append(fnam)
                    indices_rnams.append(rnam)
                    indices_dstrs.append(dstr)
        inds = np.argsort(indices_dstrs)#[::-1]
        indices_fnams = [indices_fnams[i] for i in inds]
        indices_rnams = [indices_rnams[i] for i in inds]
        indices_dstrs = [indices_dstrs[i] for i in inds]
        if len(indices_fnams) < 1:
            self.print_message('No indices data for process.',print_time=False)

        # Parcellate data
        for fnam,rnam,dstr in zip(indices_fnams,indices_rnams,indices_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_data,'parcel',ystr)
            data_npz = os.path.join(dnam,'{}_parcel.npz'.format(dstr))
            iflag = self.list_labels['oflag'].index('parcel')
            if os.path.exists(data_npz) and self.values['oflag'][iflag]:
                os.remove(data_npz)
            if self.values['csv_flag']:
                data_csv = os.path.join(dnam,'{}_parcel.csv'.format(dstr))
                if os.path.exists(data_csv):
                    if self.values['oflag'][iflag]:
                        os.remove(data_csv)
                elif os.path.exists(data_npz):
                    os.remove(data_npz)
            if not os.path.exists(data_npz):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                # Make mask
                mask_parcel = self.values['mask_parcel']
                if os.path.exists(mask_parcel) and flag_parcel:
                    os.remove(mask_parcel)
                    flag_parcel = False
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
                # Parcellate
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_parcellate.py'))
                command += ' --src_geotiff "{}"'.format(fnam)
                command += ' --res_geotiff "{}"'.format(rnam)
                command += ' --mask_geotiff "{}"'.format(mask_parcel)
                command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                command += ' --out_fnam "{}"'.format(data_npz)
                command += ' --out_shp "{}"'.format(os.path.join(dnam,'{}_parcel.shp'.format(dstr)))
                if self.values['csv_flag']:
                    command += ' --out_csv "{}"'.format(data_csv)
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
                command += ' --remove_nan'
                command += ' --debug'
                command += ' --batch'
                self.run_command(command,message='<<< Parcellate data for {} >>>'.format(dstr))

        # Finish process
        super().finish()
        return
