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

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['ref_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['ref_fnam']))
        if not os.path.exists(self.values['trg_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['trg_fnam']))
        ref_bnam,ref_enam = os.path.splitext(os.path.basename(self.values['ref_fnam']))
        trg_bnam = '{}_{}'.format(self.current_block,self.current_date)
        wrk_dir = os.path.join(self.drone_analysis,self.current_block,self.current_date,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        """
        # Geometric correction
        fnam = os.path.join(wrk_dir,'{}_resized_geocor_{}.dat'.format(trg_bnam,trials[itry]))
        if os.path.exists(fnam):
            os.remove(fnam)
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'find_gcps.py'))
        command += ' {}'.format(os.path.join(wrk_dir,'{}_resized.tif'.format(trg_bnam)))
        command += ' {}'.format(os.path.join(wrk_dir,'{}_{}_resized.tif'.format(ref_bnam,trg_bnam)))
        command += ' --ref_mask_fnam {}'.format(os.path.join(wrk_dir,'{}_{}_resized_mask.tif'.format(ref_bnam,trg_bnam)))
        command += ' --out_fnam {}'.format(fnam)
        command += ' --x0 {:.4f}'.format(xorg)
        command += ' --y0 {:.4f}'.format(yorg)
        command += ' --subset_width {}'.format(sizes[itry])
        command += ' --subset_height {}'.format(sizes[itry])
        command += ' --trg_indx_step {}'.format(steps[itry])
        command += ' --trg_indy_step {}'.format(steps[itry])
        command += ' --shift_width {}'.format(shifts[itry])
        command += ' --shift_height {}'.format(shifts[itry])
        command += ' --margin_width {}'.format(margins[itry])
        command += ' --margin_height {}'.format(margins[itry])
        command += ' --scan_indx_step {}'.format(self.values['scan_steps'][itry])
        command += ' --scan_indy_step {}'.format(self.values['scan_steps'][itry])
        command += ' --ref_band {}'.format(self.values['ref_band'])
        if self.values['trg_ndvi']:
            command += ' --trg_ndvi'
            command += ' --trg_multi_band {}'.format(self.values['trg_bands'][0])
            command += ' --trg_multi_band {}'.format(self.values['trg_bands'][1])
        else:
            command += ' --trg_band {}'.format(self.values['trg_bands'][0])
        command += ' --rthr {}'.format(self.values['boundary_cmins'][0])
        command += ' --feps 0.0001'
        if not np.isnan(self.values['trg_range'][0]):
            command += ' --trg_data_min {}'.format(self.values['trg_range'][0])
        if not np.isnan(self.values['trg_range'][1]):
            command += ' --trg_data_max {}'.format(self.values['trg_range'][1])
        if not np.isnan(self.values['ref_range'][0]):
            command += ' --ref_data_umin {}'.format(self.values['raf_range'][0])
        if not np.isnan(self.values['ref_range'][1]):
            command += ' --ref_data_umax {}'.format(self.values['ref_range'][1])
        command += ' --long'
        sys.stderr.write('\nGeometric correction ({}/{})\n'.format(itry+1,len(trials)))
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)
        sys.stderr.write('{}\n'.format(datetime.now()))
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
