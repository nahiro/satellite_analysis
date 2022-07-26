import os
import sys
try:
    import gdal
except Exception:
    from osgeo import gdal
from subprocess import call
from proc_satellite_class import Satellite_Process

class Estimate(Satellite_Process):

    def __init__(self):
        super().__init__()
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files
        if not os.path.exists(self.values['inp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['inp_fnam']))
        if not os.path.exists(self.values['score_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['score_fnam']))
        if not os.path.exists(self.values['intensity_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['intensity_fnam']))
        trg_bnam = '{}_{}'.format(self.obs_block,self.obs_date)
        etc_dir = os.path.join(self.drone_analysis,self.obs_block,self.obs_date,self.proc_name)
        wrk_dir = os.path.join(self.drone_analysis,self.proc_name)
        if not os.path.exists(etc_dir):
            os.makedirs(etc_dir)
        if not os.path.isdir(etc_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,etc_dir))
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Make mask
        mask_fnam = os.path.join(etc_dir,'{}_mask.tif'.format(trg_bnam))
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'make_mask.py'))
        command += ' --shp_fnam {}'.format(self.values['gis_fnam'])
        command += ' --src_geotiff {}'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff {}'.format(mask_fnam)
        command += ' --buffer="{}"'.format(-abs(self.values['buffer']))
        command += ' --use_index'
        sys.stderr.write('\nMake mask\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Make rebinned image
        img_fnam = os.path.join(etc_dir,'{}_resized.tif'.format(trg_bnam))
        ds = gdal.Open(self.values['inp_fnam'])
        inp_trans = ds.GetGeoTransform()
        inp_shape = (ds.RasterYSize,ds.RasterXSize)
        ds = None
        inp_xmin = inp_trans[0]
        inp_xstp = inp_trans[1]
        inp_xmax = inp_xmin+inp_xstp*inp_shape[1]
        inp_ymax = inp_trans[3]
        inp_ystp = inp_trans[5]
        inp_ymin = inp_ymax+inp_ystp*inp_shape[0]
        istp = int(abs(self.values['region_size']/inp_xstp)+0.5)
        jstp = int(abs(self.values['region_size']/inp_ystp)+0.5)
        if istp != jstp:
            raise ValueError('{}: error, istp={}, jstp={}'.format(self.proc_name,istp,jstp))
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'rebin_gtiff.py'))
        command += ' --istp {}'.format(istp)
        command += ' --jstp {}'.format(jstp)
        command += ' --src_geotiff {}'.format(self.values['inp_fnam'])
        command += ' --dst_geotiff {}'.format(img_fnam)
        command += ' --mask_geotiff {}'.format(mask_fnam)
        command += ' --rmax 0.1'
        sys.stderr.write('\nRebin image\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Make parcel image
        mask_resized_fnam = os.path.join(etc_dir,'{}_mask_resized.tif'.format(trg_bnam))
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'rebin_mask.py'))
        command += ' --istp {}'.format(istp)
        command += ' --jstp {}'.format(jstp)
        command += ' --src_geotiff {}'.format(mask_fnam)
        command += ' --dst_geotiff {}'.format(mask_resized_fnam)
        command += ' --rmax 0.1'
        sys.stderr.write('\nMake parcel image\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Estimate score
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_estimate.py'))
        command += ' --inp_fnam {}'.format(self.values['score_fnam'])
        command += ' --src_geotiff {}'.format(img_fnam)
        command += ' --dst_geotiff {}'.format(os.path.join(etc_dir,'{}_score.tif'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['score_number'])
        for param,flag,value in zip(self.list_labels['y_params'],self.values['y_params'],self.values['score_max']):
            if flag:
                command += ' --smax {}'.format(value)
        for param,flag,value in zip(self.list_labels['y_params'],self.values['y_params'],self.values['score_step']):
            if flag:
                command += ' --sint {}'.format(value)
        if self.values['digitize']:
            command += ' --digitize'
        command += ' --fignam {}'.format(os.path.join(etc_dir,'{}_score.pdf'.format(trg_bnam)))
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nEstimate score\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Estimate intensity
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_score_estimate.py'))
        command += ' --inp_fnam {}'.format(self.values['intensity_fnam'])
        command += ' --src_geotiff {}'.format(img_fnam)
        command += ' --dst_geotiff {}'.format(os.path.join(etc_dir,'{}_intensity.tif'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['intensity_number'])
                command += ' --smax 1'
        command += ' --fignam {}'.format(os.path.join(etc_dir,'{}_intensity.pdf'.format(trg_bnam)))
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nEstimate intensity\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Calculate damage intensity of plot from score
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_damage_calculate.py'))
        command += ' --src_geotiff {}'.format(os.path.join(etc_dir,'{}_score.tif'.format(trg_bnam)))
        command += ' --mask_geotiff {}'.format(mask_resized_fnam)
        command += ' --shp_fnam {}'.format(self.values['gis_fnam'])
        command += ' --out_csv {}'.format(os.path.join(wrk_dir,'{}_damage_score.csv'.format(trg_bnam)))
        command += ' --out_shp {}'.format(os.path.join(etc_dir,'{}_damage_score.shp'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
        for param,flag,value in zip(self.list_labels['y_params'],self.values['y_params'],self.values['score_max']):
            if flag:
                command += ' --smax {}'.format(value)
        command += ' --rmax 0.01'
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_damage_score.pdf'.format(trg_bnam)))
        command += ' --use_index'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nEstimate intensity of plot from score\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Calculate damage intensity of plot from intensity
        command = self.python_path
        command += ' {}'.format(os.path.join(self.scr_dir,'drone_damage_calculate.py'))
        command += ' --src_geotiff {}'.format(os.path.join(etc_dir,'{}_intensity.tif'.format(trg_bnam)))
        command += ' --mask_geotiff {}'.format(mask_resized_fnam)
        command += ' --shp_fnam {}'.format(self.values['gis_fnam'])
        command += ' --out_csv {}'.format(os.path.join(wrk_dir,'{}_damage_intensity.csv'.format(trg_bnam)))
        command += ' --out_shp {}'.format(os.path.join(etc_dir,'{}_damage_intensity.shp'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --smax 1'
        command += ' --rmax 0.01'
        command += ' --fignam {}'.format(os.path.join(wrk_dir,'{}_damage_intensity.pdf'.format(trg_bnam)))
        command += ' --use_index'
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        sys.stderr.write('\nEstimate intensity of plot from intensity\n')
        sys.stderr.write(command+'\n')
        sys.stderr.flush()
        call(command,shell=True)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
