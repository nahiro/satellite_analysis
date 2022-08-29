import os
import sys
from proc_satellite_class import Satellite_Process

class Estimate(Satellite_Process):

    def __init__(self):
        super().__init__()
        self.ax1_zmin = None
        self.ax1_zmax = None
        self.ax1_zstp = None
        self._freeze()

    def run(self):
        # Start process
        super().run()

        # Check files/folders
        start_dtim = datetime.strptime(self.start_date,self.date_fmt)
        end_dtim = datetime.strptime(self.end_date,self.date_fmt)
        first_dtim = datetime.strptime(self.first_date,self.date_fmt)
        last_dtim = datetime.strptime(self.last_date,self.date_fmt)
        if not os.path.exists(self.values['inp_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['inp_fnam']))
        if not os.path.exists(self.values['pm_fnam']):
            raise IOError('{}: error, no such file >>> {}'.format(self.proc_name,self.values['pm_fnam']))
        trg_bnam = '{:%Y%m%d}_{:%Y%m%d}'.format(start_dtim,end_dtim)
        wrk_dir = os.path.join(self.s2_analysis,self.proc_name)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Select data
        select_csv = os.path.join(wrk_dir,'{}_select.csv'.format(trg_bnam))
        select_shp = os.path.join(wrk_dir,'{}_select.shp'.format(trg_bnam))
        select_pdf = os.path.join(wrk_dir,'{}_select.pdf'.format(trg_bnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_select_data.py'))
        command += ' --phenology "{}"'.format()
        command += ' --out_csv "{}"'.format(select_csv)
        command += ' --out_shp "{}"'.format(select_shp)
        command += ' --fignam "{}"'.format(select_pdf)
        command += ' --use_index'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Select data >>>')

        # Estimate plot-mean
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'drone_score_estimate.py'))
        command += ' --inp_fnam "{}"'.format(self.values['pm_fnam'])
        command += ' --src_geotiff "{}"'.format(img_fnam)
        command += ' --dst_geotiff "{}"'.format(os.path.join(wrk_dir,'{}_pm_mesh.tif'.format(trg_bnam)))
        for param,flag in zip(self.list_labels['y_params'],self.values['y_params']):
            if flag:
                command += ' --y_param {}'.format(param)
                command += ' --y_number {}'.format(self.values['pm_number'])
                command += ' --smax 1'
        command += ' --fignam "{}"'.format(os.path.join(wrk_dir,'{}_pm_mesh.pdf'.format(trg_bnam)))
        for value,flag in zip(self.ax1_zmin[1],self.values['y_params']):
            if flag:
                command += ' --ax1_zmin="{}"'.format(value)
        for value,flag in zip(self.ax1_zmax[1],self.values['y_params']):
            if flag:
                command += ' --ax1_zmax="{}"'.format(value)
        for value,flag in zip(self.ax1_zstp[1],self.values['y_params']):
            if flag:
                command += ' --ax1_zstp="{}"'.format(value)
        command += ' --ax1_title "{}"'.format(trg_bnam)
        command += ' --remove_nan'
        command += ' --debug'
        command += ' --batch'
        self.run_command(command,message='<<< Estimate plot-mean >>>')

        # Finish process
        sys.stderr.write('\nFinished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
