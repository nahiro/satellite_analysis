import os
import sys
import re
from datetime import datetime,timedelta
from glob import glob
import numpy as np
import pandas as pd
from proc_satellite_class import Satellite_Process

class Download(Satellite_Process):

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
        d1 = start_dtim+timedelta(days=60)
        d2 = end_dtim+timedelta(days=240)
        l2a_dir = os.path.join(self.s2_data)
        if not os.path.exists(l2a_dir):
            os.makedirs(l2a_dir)
        if not os.path.isdir(l2a_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,l2a_dir))

        # Download Planting data
        itarg = 0
        if self.values['dflag'][itarg]:
            data_years = np.arange(d1.year,d2.year+1,1)
            for year in data_years:
                ystr = '{}'.format(year)
                # Make file list
                tmp_fnam = self.mktemp(suffix='.csv')
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'google_drive_query.py'))
                command += ' --drvdir {}'.format(self.values['drv_dir'])
                command += ' --srcdir {}'.format('{}/{}'.format(self.values['trans_path'],year))
                command += ' --out_csv {}'.format(tmp_fnam)
                command += ' --max_layer 1'
                try:
                    self.run_command(command,message='<<< Make Planting data list ({}) >>>'.format(ystr))
                except Exception:
                    if os.path.exists(tmp_fnam):
                        os.remove(tmp_fnam)
                    continue
                df = pd.read_csv(tmp_fnam,comment='#')
                if os.path.exists(tmp_fnam):
                    os.remove(tmp_fnam)
                df.columns = df.columns.str.strip()
                inds = []
                for index,row in df.iterrows():
                    #fileName,nLayer,fileSize,modifiedDate,fileId,md5Checksum
                    src_fnam = row['fileName'].split('/')[-1]
                    m = re.search('_('+'\d'*8+')_final.tif$',src_fnam)
                    if not m:
                        m = re.search('_('+'\d'*8+')_final.json$',src_fnam)
                        if not m:
                            continue
                    dstr = m.group(1)
                    d = datetime.strptime(dstr,'%Y%m%d')
                    if d < d1 or d > d2:
                        continue
                    df.loc[index,'fileName'] = src_fnam
                    df.loc[index,'nLayer'] = 0
                    inds.append(index)
                if len(inds) < 1:
                    continue
                tmp_fnam = self.mktemp(suffix='.csv')
                df.loc[inds].to_csv(tmp_fnam,index=False)
                # Download Data
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'google_drive_download_file.py'))
                command += ' --drvdir {}'.format(self.values['drv_dir'])
                command += ' --inp_list {}'.format(tmp_fnam)
                command += ' --dstdir {}'.format(os.path.join(self.s1_analysis,'planting',ystr))
                command += ' --verbose'
                if self.values['oflag'][itarg]:
                    command += ' --overwrite'
                self.run_command(command,message='<<< Download Planting data ({}) >>>'.format(ystr))
                if os.path.exists(tmp_fnam):
                    os.remove(tmp_fnam)
        """

        # Download Sentinel-2 L2A
        itarg = 1
        if args.dflag[itarg]:
            sys.stderr.write('\nDownload Sentinel-2 L2A\n')
            sys.stderr.flush()
            keys = []
            for key in [s.strip() for s in self.values['search_key'].split(',')]:
                if key:
                    keys.append(key)
            if len(keys) < 1:
                keys = None
            data_years = np.arange(first_dtim.year,last_dtim.year+1,1)
            for year in data_years:
                ystr = '{}'.format(year)
                # Make file list
                if os.path.exists(tmp_fnam):
                    os.remove(tmp_fnam)
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'google_drive_query.py'))
                command += ' --drvdir {}'.format(self.values['drv_dir'])
                command += ' --srcdir {}'.format('{}/{}'.format(self.values['l2a_path'],year))
                command += ' --out_csv {}'.format(tmp_fnam)
                command += ' --max_layer 0'
                try:
                    self.run_command(command,message='<<< Make Sentinel-2 L2A list ({}) >>>'.format(ystr))
                except Exception:
                    continue
                df = pd.read_csv(tmp_fnam,comment='#')
                df.columns = df.columns.str.strip()
                inds = []
                for index,row in df.iterrows():
                    #fileName,nLayer,fileSize,modifiedDate,fileId,md5Checksum
                    src_fnam = row['fileName']
                    m = re.search('^S2[AB]_MSIL2A_('+'\d'*8+')T\S+\.zip$',src_fnam)
                    if not m:
                        continue
                    dstr = m.group(1)
                    d = datetime.strptime(dstr,'%Y%m%d')
                    if d < first_dtim or d > last_dtim:
                        continue
                    if keys is not None:
                        flag = False
                        for key in keys:
                            if not key in src_fnam:
                                flag = True
                                break
                        if flag:
                            continue
                    inds.append(index)
                if len(inds) < 1:
                    continue
                df.loc[inds].to_csv(tmp_fnam,index=False)
                # Download Data
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'google_drive_download_file.py'))
                command += ' --drvdir {}'.format(self.values['drv_dir'])
                command += ' --inp_list {}'.format(tmp_fnam)
                command += ' --dstdir {}'.format(os.path.join(self.s2_data,ystr))
                command += ' --verbose'
                if self.values['oflag'][itarg]:
                    command += ' --overwrite'
                self.run_command(command,message='<<< Download Sentinel-2 L2A ({}) >>>'.format(ystr))
        """

        #if os.path.exists(tmp_fnam):
        #    os.remove(tmp_fnam)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
