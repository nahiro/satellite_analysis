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

class Interp(Satellite_Process):

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
        d1 = start_dtim
        d2 = end_dtim+timedelta(days=120)
        data_years = np.arange(first_dtim.year,last_dtim.year+1,1)
        if not os.path.exists(self.s2_analysis):
            os.makedirs(self.s2_analysis)
        if not os.path.isdir(self.s2_analysis):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_analysis))

        # Check Parcel
        parcel_fnams = []
        parcel_dstrs = []
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.s2_analysis,'parcel',ystr)
            if not os.path.isdir(dnam):
                continue
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_parcel\.csv$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < first_dtim or d > last_dtim:
                    continue
                fnam = os.path.join(dnam,f)
                parcel_fnams.append(fnam)
                parcel_dstrs.append(dstr)
        inds = np.argsort(parcel_dstrs)#[::-1]
        parcel_fnams = [parcel_fnams[i] for i in inds]
        parcel_dstrs = [parcel_dstrs[i] for i in inds]
        if len(parcel_fnams) < 1:
            self.print_message('No parcel data for process.',print_time=False)

        # Make file list
        tmp_fnam = self.mktemp(suffix='.txt')
        with open(tmp_fnam,'w') as fp:
            fp.write('\n'.join(parcel_fnams)+'\n')

        # Interpolate data
        for year in data_years:
            ystr = '{}'.format(year)
            dnam = os.path.join(self.s2_analysis,'interp',ystr)
            if not os.path.exists(dnam):
                os.makedirs(dnam)
            if not os.path.isdir(dnam):
                raise IOError('Error, no such folder >>> {}'.format(dnam))
        command = self.python_path
        command += ' "{}"'.format(os.path.join(self.scr_dir,'sentinel2_interp.py'))
        command += ' --inp_list "{}"'.format(tmp_fnam)
        command += ' --dstdir "{}"'.format(os.path.join(self.s2_analysis,'interp'))
        command += ' --tmin {:%Y-%m-%d}'.format(d1)
        command += ' --tmax {:%Y-%m-%d}'.format(d2)
        command += ' --tstp 1.0'
        self.run_command(command,message='<<< Interpolate data between {:%Y-%m-%d} - {:%Y-%m-%d} >>>'.format(dstr,d1,d2))

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
