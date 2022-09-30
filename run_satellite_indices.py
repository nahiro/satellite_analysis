import os
import sys
import re
from datetime import datetime
import numpy as np
from proc_satellite_class import Satellite_Process

class Indices(Satellite_Process):

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

        # Check Geocor
        geocor_fnams = []
        geocor_dstrs = []
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.values['geocor_dir'],ystr)
            if not os.path.isdir(dnam):
                continue
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_geocor\.tif$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < first_dtim or d > last_dtim:
                    continue
                fnam = os.path.join(dnam,f)
                geocor_fnams.append(fnam)
                geocor_dstrs.append(dstr)
        inds = np.argsort(geocor_dstrs)#[::-1]
        geocor_fnams = [geocor_fnams[i] for i in inds]
        geocor_dstrs = [geocor_dstrs[i] for i in inds]
        if len(geocor_fnams) < 1:
            self.print_message('No geocor data for process.',print_time=False)

        # Calculate indices
        for fnam,dstr in zip(geocor_fnams,geocor_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(self.s2_data,'indices',ystr)
            gnam = os.path.join(dnam,'{}_indices.tif'.format(dstr))
            if os.path.exists(gnam) and self.values['oflag']:
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

        # Finish process
        super().finish()
        return
