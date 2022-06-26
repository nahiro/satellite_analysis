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
from subprocess import call
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
        wrk_dir = os.path.join(self.s2_analysis)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))
        if not os.path.exists(self.values['ref_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['ref_fnam']))
        ref_bnam,ref_enam = os.path.splitext(os.path.basename(self.values['ref_fnam']))

        # Check Sentinel-2 L2A
        l2a_fnams = []
        l2a_dstrs = []
        l2a_sizes = []
        for year in data_years:
            dnam = os.path.join(self.s2_data,'{}'.format(year))
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
                fnam = os.path.join(dnam,f)
                l2a_fnams.append(fnam)
                l2a_dstrs.append(dstr)
                l2a_sizes.append(os.path.getsize(fnam))
        if len(l2a_dstrs) < 1:
            return
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
        subset_dstrs = []
        for fnam,dstr in zip(l2a_fnams,l2a_dstrs):
            d = datetime.strptime(dstr,'%Y%m%d')
            dnam = os.path.join(self.s2_analysis,'subset','{}'.format(d.year))
            gnam = os.path.join(dnam,'{}_subset.tif'.format(dstr))
            if os.path.exists(gnam) and self.values['oflag'][0]:
                os.remove(gnam)
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
                command += ' '+rnam
                command += ' --output_fnam "{}"'.format(gnam)
                command += ' --polygon "POLYGON(({} {},{} {},{} {},{} {},{} {}))"'.format(self.values['trg_subset'][0],self.values['trg_subset'][2],
                                                                                          self.values['trg_subset'][1],self.values['trg_subset'][2],
                                                                                          self.values['trg_subset'][1],self.values['trg_subset'][3],
                                                                                          self.values['trg_subset'][0],self.values['trg_subset'][3],
                                                                                          self.values['trg_subset'][0],self.values['trg_subset'][2])
                command += ' --resolution {}'.format(int(self.values['trg_pixel']+0.5))
                command += ' --geotiff'
                call(command,shell=True)
                if unzip_flag:
                    shutil.rmtree(rnam)
                # Remove cache
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'remove_snap_cache.py'))
                call(command,shell=True)
            if os.path.exists(gnam):
                subset_dstrs.append(dstr)

        # Geocor
        geocor_dstrs = []
        for dstr in subset_dstrs:
            d = datetime.strptime(dstr,'%Y%m%d')
            dnam = os.path.join(self.s2_analysis,'geocor','{}'.format(d.year))
            gnam = os.path.join(dnam,'{}_geocor.tif'.format(dstr))
            dat_fnam = os.path.join(dnam,'{}_geocor.dat'.format(dstr))
            if self.values['oflag'][1]:
                if os.path.exists(gnam):
                    os.remove(gnam)
                if os.path.exists(dat_fnam):
                    os.remove(dat_fnam)
            if not os.path.exists(dat_fnam):
                fnam = os.path.join(self.s2_analysis,'subset','{}'.format(d.year),'{}_subset.tif'.format(dstr))
                sel_fnam = os.path.join(dnam,'{}_geocor_selected.dat'.format(dstr))
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
                ret = call(command,shell=True)
                if ret != 0:
                    continue
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'select_gcps.py'))
                command += ' "{}"'.format(dat_fnam)
                command += ' --datdir "{}"'.format(os.path.dirname(dat_fnam))
                command += ' --replace'
                command += ' --exp'
                ret = call(command,shell=True)
                if ret != 0:
                    continue
                command = self.python_path
                command += ' "{}"'.format(os.path.join(self.scr_dir,'auto_geocor_cc.py'))
                command += ' "{}"'.format(fnam)
                command += ' "{}"'.format(self.values['ref_fnam'])
                command += ' --out_fnam "{}"'.format(gnam)
                command += ' --ref_band 4' # Red band
                command += ' --trg_band 3' # Red band
                command += ' --tr 10.0'
                command += ' --use_gcps "{}"'.format(sel_fnam) # use
                command += ' --resampling2_band 16'
                try:
                    call(command,shell=True)
                except Exception:
                    continue
            #if os.path.exists(sel_fnam):
            #    os.rename(sel_fnam,dat_fnam)
            if os.path.exists(gnam):
                geocor_dstrs.append(dstr)


        """
        # Geometric correction


        #---------
        x,y,r,ni,nb,r90 = np.loadtxt(fnam,usecols=(4,5,6,9,11,12),unpack=True)
        indx0 = np.arange(r.size)[(r>self.values['boundary_cmins'][1]) & (nb>nb.max()*self.values['boundary_nmin']) & (r90<self.values['boundary_rmax'])]
        x_diff1,y_diff1,e1,n1,indx1 = calc_mean(x,y,emax=self.values['boundary_emaxs'][0],selected=indx0)
        x_diff2,y_diff2,e2,n2,indx2 = calc_mean(x,y,emax=self.values['boundary_emaxs'][1],selected=indx1)
        x_diff3,y_diff3,e3,n3,indx3 = calc_mean(x,y,emax=self.values['boundary_emaxs'][2],selected=indx2)
        with open(shift_dat,'a') as fp:
            fp.write('{} {:8.4f} {:8.4f} {:7.4f} {:7.4f} {:7.4f} {:3d} {:3d} {:3d}\n'.format(trials[itry],x_diff3,y_diff3,e1,e2,e3,n1,n2,n3))
        xorg = x_diff3
        yorg = y_diff3
        #---------

            command = self.python_path
            command += ' {}'.format(os.path.join(self.scr_dir,'auto_geocor.py'))
            command += ' {}'.format(os.path.join(wrk_dir,'{}_resized.tif'.format(trg_bnam)))
            command += ' --out_fnam {}'.format(os.path.join(wrk_dir,'{}_resized_geocor_{}.tif'.format(trg_bnam,orders[order])))
            command += ' --scrdir {}'.format(self.scr_dir)
            command += ' --use_gcps {}'.format(gnam) # use
            command += ' --optfile {}'.format(os.path.join(wrk_dir,'temp.dat'))
            command += ' --npoly {}'.format(order)
            command += ' --refine_gcps 0.1'
            command += ' --minimum_number 3'
            sys.stderr.write(command+'\n')
            sys.stderr.flush()
            call(command,shell=True)
            figure_orders.append(order)
        if len(figure_orders) > 0:
            command = self.python_path
            command += ' {}'.format(os.path.join(self.scr_dir,'draw_resized_geocor.py'))
            command += ' --shp_fnam {}'.format(self.values['gis_fnam'])
            command += ' --img_fnam {}'.format(os.path.join(wrk_dir,'{}_resized_geocor.tif'.format(trg_bnam)))
            for order in figure_orders:
                command += ' --order {}'.format(order)
            command += ' --title {}'.format(trg_bnam)
            command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_resized.pdf'.format(trg_bnam)))
            command += ' --batch'
            call(command,shell=True)
        """

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
