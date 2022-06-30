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
        if not os.path.exists(self.s2_analysis):
            os.makedirs(self.s2_analysis)
        if not os.path.isdir(self.s2_analysis):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_analysis))

        # Check Resample
        resample_fnams = []
        resample_dstrs = []
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.s2_analysis,'resample',ystr)
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
        if len(resample_dstrs) < 1:
            return
        inds = np.argsort(resample_dstrs)#[::-1]
        resample_fnams = [resample_fnams[i] for i in inds]
        resample_dstrs = [resample_dstrs[i] for i in inds]

        # Calculate indices
        indices_fnams = []
        indices_dstrs = []
        for fnam,dstr in zip(resample_fnams,resample_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_analysis,'indices',ystr)
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
                command += ' --band_fnam "{}"'.format(self.values['band_fnam'])
                command += ' --fignam "{}"'.format(os.path.join(dnam,'{}_indices.pdf'.format(dstr)))
                for param,flag in zip(self.list_labels['out_refs'],self.values['out_refs']):
                    if flag:
                        command += ' --param S{}'.format(param)
                for param,flag in zip(self.list_labels['out_nrefs'],self.values['out_nrefs']):
                    if flag:
                        command += ' --param {}'.format(param)
                for param,flag in zip(self.list_labels['out_inds'],self.values['out_inds']):
                    if flag:
                        command += ' --param {}'.format(param)
                for band,flag in zip(self.list_labels['norm_bands'],self.values['norm_bands']):
                    if flag:
                        command += ' --norm_band {}'.format(band)
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
                indices_dstrs.append(dstr)

        # Parcellate data
        for fnam,dstr in zip(indices_fnams,indices_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_analysis,'parcel',ystr)
            gnam = os.path.join(dnam,'{}_parcel.csv'.format(dstr))
            if os.path.exists(gnam) and self.values['oflag'][1]:
                os.remove(gnam)
            if not os.path.exists(gnam):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                # Make mask
                mask_fnam = os.path.join(self.s2_analysis,'parcel_mask.tif')
                if not os.path.exists(mask_fnam):
                    command = self.python_path
                    command += ' "{}"'.format(os.path.join(self.scr_dir,'make_mask.py'))
                    command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                    command += ' --src_geotiff "{}"'.format(fnam)
                    command += ' --dst_geotiff "{}"'.format(mask_fnam)
                    command += ' --buffer="{}"'.format(-abs(self.values['buffer']))
                    command += ' --use_index'
                    self.run_command(command,message='<<< Make mask >>>')
                if not os.path.exists(mask_fnam):
                    raise ValueError('Error, no such file >>> {}'.format(mask_fnam))
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_parcellate.py'))
                command += ' --src_geotiff "{}"'.format(os.path.join(dnam,'{}_indices.tif'.format(dstr)))
                command += ' --mask_geotiff "{}"'.format(mask_fnam)
                command += ' --shp_fnam "{}"'.format(self.values['gis_fnam'])
                command += ' --out_csv "{}"'.format(gnam)
                command += ' --out_shp "{}"'.format(os.path.join(dnam,'{}_parcel.shp'.format(dstr)))
                for param,flag in zip(self.list_labels['out_refs'],self.values['out_refs']):
                    if flag:
                        command += ' --param S{}'.format(param)
                for param,flag in zip(self.list_labels['out_nrefs'],self.values['out_nrefs']):
                    if flag:
                        command += ' --param {}'.format(param)
                for param,flag in zip(self.list_labels['out_inds'],self.values['out_inds']):
                    if flag:
                        command += ' --param {}'.format(param)
                command += ' --rmax 0.01'
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
