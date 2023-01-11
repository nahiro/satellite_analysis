import os
import sys
import shutil
import re
from datetime import datetime
import zipfile
try:
    import gdal
except Exception:
    from osgeo import gdal
from glob import glob
import numpy as np
from proc_satellite_class import Satellite_Process

def calc_mean(x,y,emax=2.0,nrpt=10,nmin=1,selected=None):
    if selected is not None:
        indx = selected.copy()
    else:
        indx = np.where(np.isfinite(x+y))[0]
    for n in range(nrpt):
        x_selected = x[indx]
        y_selected = y[indx]
        i_selected = indx.copy()
        x_center = x_selected.mean()
        y_center = y_selected.mean()
        r_selected = np.sqrt(np.square(x_selected-x_center)+np.square(y_selected-y_center))
        rmse = np.sqrt(np.mean(np.square(x_selected-x_center)+np.square(y_selected-y_center)))
        cnd = (r_selected < rmse*emax)
        indx = indx[cnd]
        if (indx.size == x_selected.size) or (indx.size < nmin):
            break
    return x_center,y_center,rmse,x_selected.size,i_selected

class Geocor(Satellite_Process):

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
        data_years = np.arange(first_dtim.year,last_dtim.year+1,1)
        wrk_dir = os.path.join(self.s2_data,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))
        if not os.path.exists(self.values['ref_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['ref_fnam']))

        # Check Sentinel-2 L2A
        l2a_fnams = []
        l2a_dstrs = []
        l2a_sizes = []
        keys = []
        for key in [s.strip() for s in self.values['search_key'].split(',')]:
            if key:
                keys.append(key)
        if len(keys) < 1:
            keys = None
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.values['l2a_dir'],ystr)
            if not os.path.isdir(dnam):
                continue
            for f in sorted(os.listdir(dnam)):
                m = re.search('^S2[AB]_MSIL2A_('+'\d'*8+')T\S+\.zip$',f)
                if not m:
                    m = re.search('^S2[AB]_MSIL2A_('+'\d'*8+')T\S+\.SAFE$',f)
                    if not m:
                        continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < first_dtim or d > last_dtim:
                    continue
                if keys is not None:
                    flag = False
                    for key in keys:
                        if not key in f:
                            flag = True
                            break
                    if flag:
                        continue
                fnam = os.path.join(dnam,f)
                l2a_fnams.append(fnam)
                l2a_dstrs.append(dstr)
                l2a_sizes.append(os.path.getsize(fnam))
        if len(l2a_dstrs) < 1:
            self.print_message('No L2A data for process.',print_time=False)
        iflag = self.list_labels['oflag'].index('subset')
        if not self.values['oflag'][iflag]:
            for year in data_years:
                ystr = '{}'.format(year)
                dnam = os.path.join(wrk_dir,ystr)
                if not os.path.isdir(dnam):
                    continue
                for f in sorted(os.listdir(dnam)):
                    m = re.search('^('+'\d'*8+')_subset\.tif$',f)
                    if not m:
                        continue
                    dstr = m.group(1)
                    d = datetime.strptime(dstr,'%Y%m%d')
                    if d < first_dtim or d > last_dtim:
                        continue
                    if not dstr in l2a_dstrs:
                        l2a_fnams.append(None)
                        l2a_dstrs.append(dstr)
                        l2a_sizes.append(0)
        inds = np.argsort(l2a_dstrs)#[::-1]
        l2a_fnams = [l2a_fnams[i] for i in inds]
        l2a_dstrs = [l2a_dstrs[i] for i in inds]
        l2a_sizes = [l2a_sizes[i] for i in inds]
        # Delete duplicates
        dup = [dstr for dstr in set(l2a_dstrs) if l2a_dstrs.count(dstr) > 1]
        for dstr in dup:
            inds = np.array([i for i,d in enumerate(l2a_dstrs) if d == dstr])
            fs = [l2a_fnams[j] for j in inds[np.argsort([l2a_sizes[i] for i in inds])[-2::-1]]]
            for fnam in fs:
                i = l2a_fnams.index(fnam)
                del l2a_fnams[i]
                del l2a_dstrs[i]
                del l2a_sizes[i]

        # Subset
        subset_fnams = []
        subset_dstrs = []
        for fnam,dstr in zip(l2a_fnams,l2a_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(wrk_dir,ystr)
            gnam = os.path.join(dnam,'{}_subset.tif'.format(dstr))
            tmp_gnam = os.path.join(dnam,'{}_subset_tmp.tif'.format(dstr))
            iflag = self.list_labels['oflag'].index('subset')
            if self.values['oflag'][iflag]:
                if os.path.exists(gnam):
                    os.remove(gnam)
                if os.path.exists(tmp_gnam):
                    os.remove(tmp_gnam)
            if not os.path.exists(gnam):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                unzip_flag = False
                rnam = os.path.splitext(fnam)[0]+'.SAFE'
                if not os.path.exists(rnam):
                    try:
                        with zipfile.ZipFile(fnam,'r') as z:
                            for d in z.namelist():
                                dnam = os.path.dirname(d)
                                if re.search('\.SAFE$',dnam):
                                    if os.path.basename(rnam) != dnam:
                                        raise ValueError('Error, rnam={}, dnam={}'.format(rnam,dnam))
                                    break
                            z.extractall(os.path.dirname(fnam))
                        unzip_flag = True
                    except Exception as e:
                        sys.stderr.write(str(e)+'\n')
                        sys.stderr.flush()
                        continue
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'sentinel2_subset.py'))
                command += ' --inp_fnam "{}"'.format(rnam)
                command += ' --out_fnam "{}"'.format(tmp_gnam)
                command += ' --polygon "POLYGON(({} {},{} {},{} {},{} {},{} {}))"'.format(self.values['trg_subset'][0],self.values['trg_subset'][2],
                                                                                          self.values['trg_subset'][1],self.values['trg_subset'][2],
                                                                                          self.values['trg_subset'][1],self.values['trg_subset'][3],
                                                                                          self.values['trg_subset'][0],self.values['trg_subset'][3],
                                                                                          self.values['trg_subset'][0],self.values['trg_subset'][2])
                command += ' --resolution {}'.format(int(self.values['trg_pixel']+0.5))
                command += ' --geotiff'
                self.run_command(command,message='<<< Subset for {} >>>'.format(dstr))
                if unzip_flag:
                    shutil.rmtree(rnam)
                # Remove cache
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'remove_snap_cache.py'))
                self.run_command(command,print_command=False,print_time=False)
                # Append bandname
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'sentinel2_bandname.py'))
                command += ' --inp_fnam "{}"'.format(tmp_gnam)
                command += ' --out_fnam "{}"'.format(gnam)
                self.run_command(command,message='<<< Append bandname for {} >>>'.format(dstr))
            if os.path.exists(tmp_gnam):
                os.remove(tmp_gnam)
            if os.path.exists(gnam):
                subset_fnams.append(gnam)
                subset_dstrs.append(dstr)
        if len(subset_dstrs) < 1:
            self.print_message('No subset data for process.',print_time=False)
        iflag = self.list_labels['oflag'].index('geocor')
        if not self.values['oflag'][iflag]:
            for year in data_years:
                ystr = '{}'.format(year)
                dnam = os.path.join(wrk_dir,ystr)
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
                    if not dstr in subset_dstrs:
                        subset_fnams.append(None)
                        subset_dstrs.append(dstr)
        inds = np.argsort(subset_dstrs)#[::-1]
        subset_fnams = [subset_fnams[i] for i in inds]
        subset_dstrs = [subset_dstrs[i] for i in inds]

        # Geometric correction
        orders = {'1st':1,'2nd':2,'3rd':3}
        for fnam,dstr in zip(subset_fnams,subset_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            ystr = '{}'.format(d.year)
            dnam = os.path.join(wrk_dir,ystr)
            gnam = os.path.join(dnam,'{}_geocor.tif'.format(dstr))
            tmp_gnam = os.path.join(dnam,'{}_geocor_tmp.tif'.format(dstr))
            dat_fnam = os.path.join(dnam,'{}_geocor.dat'.format(dstr))
            iflag = self.list_labels['oflag'].index('geocor')
            if self.values['oflag'][iflag]:
                if os.path.exists(gnam):
                    os.remove(gnam)
                if os.path.exists(tmp_gnam):
                    os.remove(tmp_gnam)
                if os.path.exists(dat_fnam):
                    os.remove(dat_fnam)
            if not os.path.exists(dat_fnam):
                if not os.path.exists(dnam):
                    os.makedirs(dnam)
                if not os.path.isdir(dnam):
                    raise IOError('Error, no such folder >>> {}'.format(dnam))
                se1_fnam = os.path.join(dnam,'{}_geocor_selected1.dat'.format(dstr))
                se2_fnam = os.path.join(dnam,'{}_geocor_selected2.dat'.format(dstr))
                tmp_fnam = os.path.join(dnam,'{}_geocor_temp.dat'.format(dstr))
                ds = gdal.Open(fnam)
                trg_trans = ds.GetGeoTransform()
                ds = None
                trg_xstp = trg_trans[1]
                trg_pixel_size = abs(trg_xstp)
                size = np.int64(self.values['part_size']/trg_pixel_size+0.5)
                step = np.int64(self.values['gcp_interval']/trg_pixel_size+0.5)
                shift = np.int64(self.values['max_shift']/trg_pixel_size+0.5)
                margin = np.int64(self.values['margin']/trg_pixel_size+0.5)
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'find_gcps_cc.py'))
                command += ' "{}"'.format(fnam)
                command += ' "{}"'.format(self.values['ref_fnam'])
                command += ' --out_fnam "{}"'.format(dat_fnam)
                command += ' --x0 {:.4f}'.format(self.values['init_shifts'][0])
                command += ' --y0 {:.4f}'.format(self.values['init_shifts'][1])
                command += ' --subset_width {}'.format(size)
                command += ' --subset_height {}'.format(size)
                command += ' --trg_indx_step {}'.format(step)
                command += ' --trg_indy_step {}'.format(step)
                command += ' --shift_width {}'.format(shift)
                command += ' --shift_height {}'.format(shift)
                command += ' --margin_width {}'.format(margin)
                command += ' --margin_height {}'.format(margin)
                command += ' --scan_indx_step {}'.format(self.values['scan_step'])
                command += ' --scan_indy_step {}'.format(self.values['scan_step'])
                if self.values['ref_bands'][0] < 0: # panchromatic
                    command += ' --ref_band -1'
                elif self.values['ref_bands'][1] < 0: # single band
                    command += ' --ref_band {}'.format(self.values['ref_bands'][0])
                elif self.values['ref_bands'][2] < 0: # dual band
                    command += ' --ref_multi_band {}'.format(self.values['ref_bands'][0])
                    command += ' --ref_multi_band {}'.format(self.values['ref_bands'][1])
                    command += ' --ref_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['ref_factors'][0]) else self.values['ref_factors'][0])
                    command += ' --ref_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['ref_factors'][1]) else self.values['ref_factors'][1])
                else: # triple band
                    command += ' --ref_multi_band {}'.format(self.values['ref_bands'][0])
                    command += ' --ref_multi_band {}'.format(self.values['ref_bands'][1])
                    command += ' --ref_multi_band {}'.format(self.values['ref_bands'][2])
                    command += ' --ref_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['ref_factors'][0]) else self.values['ref_factors'][0])
                    command += ' --ref_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['ref_factors'][1]) else self.values['ref_factors'][1])
                    command += ' --ref_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['ref_factors'][2]) else self.values['ref_factors'][2])
                if self.values['trg_bands'][0] < 0: # panchromatic
                    command += ' --trg_band -1'
                elif self.values['trg_bands'][1] < 0: # single band
                    command += ' --trg_band {}'.format(self.values['trg_bands'][0])
                elif self.values['trg_bands'][2] < 0: # dual band
                    command += ' --trg_multi_band {}'.format(self.values['trg_bands'][0])
                    command += ' --trg_multi_band {}'.format(self.values['trg_bands'][1])
                    command += ' --trg_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['trg_factors'][0]) else self.values['trg_factors'][0])
                    command += ' --trg_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['trg_factors'][1]) else self.values['trg_factors'][1])
                else: # triple band
                    command += ' --trg_multi_band {}'.format(self.values['trg_bands'][0])
                    command += ' --trg_multi_band {}'.format(self.values['trg_bands'][1])
                    command += ' --trg_multi_band {}'.format(self.values['trg_bands'][2])
                    command += ' --trg_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['trg_factors'][0]) else self.values['trg_factors'][0])
                    command += ' --trg_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['trg_factors'][1]) else self.values['trg_factors'][1])
                    command += ' --trg_multi_ratio="{}"'.format(1.0 if np.isnan(self.values['trg_factors'][2]) else self.values['trg_factors'][2])
                if not np.isnan(self.values['ref_range'][0]):
                    command += ' --ref_data_min="{}"'.format(self.values['ref_range'][0])
                if not np.isnan(self.values['ref_range'][1]):
                    command += ' --ref_data_max="{}"'.format(self.values['ref_range'][1])
                if not np.isnan(self.values['trg_range'][0]):
                    command += ' --trg_data_min="{}"'.format(self.values['trg_range'][0])
                if not np.isnan(self.values['trg_range'][1]):
                    command += ' --trg_data_max="{}"'.format(self.values['trg_range'][1])
                command += ' --rthr {}'.format(self.values['cmin'])
                command += ' --feps 0.01'
                command += ' --exp'
                command += ' --out_empty'
                try:
                    self.run_command(command,message='<<< Find GCPs for {} >>>'.format(dstr))
                except Exception:
                    continue
                if not os.path.exists(dat_fnam):
                    self.print_message('No GCPs found.',print_time=False)
                    continue
                elif os.path.getsize(dat_fnam) < 1:
                    self.print_message('No GCPs found.',print_time=False)
                    continue
                x,y,r,r90 = np.loadtxt(dat_fnam,usecols=(4,5,6,7),unpack=True)
                if not np.iterable(x):
                    self.print_message('Not enough GCPs were found >>> {}'.format(x.size),print_time=False)
                    continue
                indx0 = np.arange(r.size)[(r90<self.values['rmax'])]
                x_diff1,y_diff1,e1,n1,indx1 = calc_mean(x,y,emax=self.values['emaxs'][0],selected=indx0)
                x_diff2,y_diff2,e2,n2,indx2 = calc_mean(x,y,emax=self.values['emaxs'][1],selected=indx1)
                x_diff3,y_diff3,e3,n3,indx3 = calc_mean(x,y,emax=self.values['emaxs'][2],selected=indx2)
                if indx3.size < self.values['nmin']:
                    self.print_message('Not enough GCPs were found >>> {}'.format(indx3.size),print_time=False)
                    continue
                with open(dat_fnam,'r') as fp:
                    lines = fp.readlines()
                with open(se1_fnam,'w') as fp:
                    for i,line in enumerate(lines):
                        if i in indx3:
                            fp.write(line)
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'select_gcps.py'))
                command += ' --inp_fnam "{}"'.format(se1_fnam)
                command += ' --out_fnam "{}"'.format(se2_fnam)
                command += ' --trg_indx_step {}'.format(step)
                command += ' --trg_indy_step {}'.format(step)
                command += ' --smooth_x="{}"'.format(self.values['smooth_fact'][0])
                command += ' --smooth_y="{}"'.format(self.values['smooth_fact'][1])
                command += ' --xthr {}'.format(self.values['smooth_dmax'][0])
                command += ' --ythr {}'.format(self.values['smooth_dmax'][1])
                command += ' --replace'
                command += ' --exp'
                try:
                    self.run_command(command,message='<<< Select GCPs for {} >>>'.format(dstr))
                except Exception:
                    continue
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'auto_geocor_cc.py'))
                command += ' "{}"'.format(fnam)
                command += ' "{}"'.format(self.values['ref_fnam'])
                command += ' --out_fnam "{}"'.format(tmp_gnam)
                command += ' --scrdir "{}"'.format(self.scr_dir)
                command += ' --use_gcps "{}"'.format(se2_fnam) # use
                command += ' --tr {}'.format(self.values['trg_pixel'])
                if self.values['geocor_order'] != 'Auto':
                    command += ' --npoly {}'.format(orders[self.values['geocor_order']])
                for band in self.values['trg_flags']:
                    if band > 0:
                        command += ' --resampling2_band {}'.format(band)
                command += ' --minimum_number {}'.format(self.values['nmin'])
                command += ' --optfile "{}"'.format(tmp_fnam)
                try:
                    self.run_command(command,message='<<< Geometric Correction for {} >>>'.format(dstr))
                except Exception:
                    continue
                # Resample
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel_resample.py'))
                command += ' --inp_fnam "{}"'.format(tmp_gnam)
                command += ' --out_fnam "{}"'.format(gnam)
                command += ' --xmin {}'.format(self.values['trg_resample'][0])
                command += ' --xmax {}'.format(self.values['trg_resample'][1])
                command += ' --ymin {}'.format(self.values['trg_resample'][2])
                command += ' --ymax {}'.format(self.values['trg_resample'][3])
                command += ' --read_comments'
                self.run_command(command,message='<<< Resampling for {} >>>'.format(dstr))
                # Draw figure
                if os.path.exists(gnam):
                    command = self.python_path
                    command += ' "{}"'.format(os.path.join(self.scr_dir,'draw_geocor.py'))
                    command += ' --img_fnam "{}"'.format(gnam)
                    command += ' --fignam "{}"'.format(os.path.join(dnam,'{}_geocor.pdf'.format(dstr)))
                    command += ' --ax1_title "{}"'.format(dstr)
                    command += ' --batch'
                    self.run_command(command,message='<<< Draw figure for {} >>>'.format(dstr))
            #if os.path.exists(se2_fnam):
            #    os.rename(se2_fnam,dat_fnam)
            if os.path.exists(tmp_gnam):
                os.remove(tmp_gnam)

        # Finish process
        super().finish()
        return
