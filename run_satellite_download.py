import os
import sys
import re
from datetime import datetime
from glob import glob
import numpy as np
import pandas as pd
from subprocess import call
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
        data_years = np.arange(first_dtim.year,last_dtim.year+1,1)
        wrk_dir = os.path.join(self.s2_data)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Make file list
        tmp_fnam = os.path.join(wrk_dir,'temp.csv')
        sys.stderr.write('\nMake download list\n')
        sys.stderr.flush()
        keys = []
        for key in [s.strip() for s in self.values['search_key'].split(',')]:
            if key:
                keys.append(key)
        if len(keys) < 1:
            keys = None
        for year in data_years:
            command = self.python_path
            command += ' {}'.format(os.path.join(self.scr_dir,'google_drive_query.py'))
            command += ' --drvdir {}'.format(self.values['drv_dir'])
            command += ' --srcdir {}'.format('{}/{}'.format(self.values['s2_path'],year))
            command += ' --out_csv {}'.format(tmp_fnam)
            command += ' --max_layer 0'
            sys.stderr.write(command+'\n')
            sys.stderr.flush()
            ret = call(command,shell=True)
            if ret != 0:
                continue
            df = pd.read_csv(tmp_fnam,comment='#')
            df.columns = df.columns.str.strip()
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
                print(src_fnam)


        #if os.path.exists(tmp_fnam):
        #    os.remove(tmp_fnam)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
