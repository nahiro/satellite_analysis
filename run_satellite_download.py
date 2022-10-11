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
        if not os.path.exists(self.s2_data):
            os.makedirs(self.s2_data)
        if not os.path.isdir(self.s2_data):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,self.s2_data))
        netrc_dir = os.path.dirname(self.values['netrc_fnam'])
        if not os.path.isdir(netrc_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,netrc_dir))

        # Download Planting data
        itarg = self.list_labels['dflag'].index('planting')
        iflag = self.list_labels['oflag'].index('planting')
        if self.values['dflag'][itarg]:
            data_years = np.arange(d1.year,d2.year+1,1)
            for year in data_years:
                ystr = '{}'.format(year)
                # Make file list
                tmp_fnam = self.mktemp(suffix='.csv')
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'file_station_query.py'))
                command += ' --server "{}"'.format(self.values['server'])
                command += ' --port "{}"'.format(self.values['port'])
                command += ' --rcdir "{}"'.format(netrc_dir)
                command += ' --srcdir "{}"'.format('{}/{}'.format(self.values['trans_path'],year))
                command += ' --out_csv "{}"'.format(tmp_fnam)
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
                    #fileName,nLayer,fileSize,modifiedDate,folderName,md5Checksum
                    items = row['fileName'].strip().split('/')
                    if len(items) != 2:
                        continue
                    src_dnam = items[0]
                    src_fnam = items[1]
                    m = re.search('_('+'\d'*8+')_final.tif$',src_fnam)
                    if not m:
                        m = re.search('_('+'\d'*8+')_final.json$',src_fnam)
                        if not m:
                            continue
                    dstr = m.group(1)
                    d = datetime.strptime(dstr,'%Y%m%d')
                    if d < d1 or d > d2:
                        continue
                    src_pnam = row['folderName'].strip()
                    df.loc[index,'fileName'] = src_fnam
                    df.loc[index,'folderName'] = '{}/{}'.format(src_pnam,src_dnam)
                    df.loc[index,'nLayer'] = 0
                    inds.append(index)
                if len(inds) < 1:
                    self.print_message('No planting data for download ({})'.format(ystr),print_time=False)
                    continue
                tmp_fnam = self.mktemp(suffix='.csv')
                df.loc[inds].to_csv(tmp_fnam,index=False)
                # Download Data
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'file_station_download_file.py'))
                command += ' --server "{}"'.format(self.values['server'])
                command += ' --port "{}"'.format(self.values['port'])
                command += ' --rcdir "{}"'.format(netrc_dir)
                command += ' --inp_list "{}"'.format(tmp_fnam)
                command += ' --dstdir "{}"'.format(os.path.join(self.s1_data,'planting',ystr))
                command += ' --verbose'
                if self.values['oflag'][iflag]:
                    command += ' --overwrite'
                self.run_command(command,message='<<< Download planting data ({}) >>>'.format(ystr))
                if os.path.exists(tmp_fnam):
                    os.remove(tmp_fnam)

        # Download Sentinel-2 L2A
        itarg = self.list_labels['dflag'].index('L2A')
        iflag = self.list_labels['oflag'].index('L2A')
        if self.values['dflag'][itarg]:
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
                tmp_fnam = self.mktemp(suffix='.csv')
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'file_station_query.py'))
                command += ' --server "{}"'.format(self.values['server'])
                command += ' --port "{}"'.format(self.values['port'])
                command += ' --rcdir "{}"'.format(netrc_dir)
                command += ' --srcdir "{}"'.format('{}/{}'.format(self.values['l2a_path'],year))
                command += ' --out_csv "{}"'.format(tmp_fnam)
                command += ' --max_layer 0'
                try:
                    self.run_command(command,message='<<< Make Sentinel-2 L2A list ({}) >>>'.format(ystr))
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
                    #fileName,nLayer,fileSize,modifiedDate,folderName,md5Checksum
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
                    self.print_message('No Sentinel-2 L2A data for download ({})'.format(ystr),print_time=False)
                    continue
                tmp_fnam = self.mktemp(suffix='.csv')
                df.loc[inds].to_csv(tmp_fnam,index=False)
                # Download Data
                command = self.python_path
                command += ' {}'.format(os.path.join(self.scr_dir,'file_station_download_file.py'))
                command += ' --server "{}"'.format(self.values['server'])
                command += ' --port "{}"'.format(self.values['port'])
                command += ' --rcdir "{}"'.format(netrc_dir)
                command += ' --inp_list "{}"'.format(tmp_fnam)
                command += ' --dstdir "{}"'.format(os.path.join(self.s2_data,'L2A',ystr))
                command += ' --verbose'
                if self.values['oflag'][iflag]:
                    command += ' --overwrite'
                self.run_command(command,message='<<< Download Sentinel-2 L2A ({}) >>>'.format(ystr))
                if os.path.exists(tmp_fnam):
                    os.remove(tmp_fnam)

        # Download Sentinel-2 geocor/indices/parcel/atcor/interp/tentative_interp
        for i,(targ,pnam,enam) in enumerate(zip(['geocor','indices','parcel','atcor','interp','tentative_interp'],
                                                ['geocor','indices','parcel','atcor','interp','tentative'],
                                                ['geocor\S*\.\S*','indices\S*\.\S*','parcel\S*\.\S*','\S*\.\S*','interp\S*\.\S*','interp\S*\.\S*'])):
            itarg = self.list_labels['dflag'].index(targ)
            iflag = self.list_labels['oflag'].index(targ)
            if self.values['dflag'][itarg]:
                data_years = np.arange(first_dtim.year,last_dtim.year+1,1)
                for year in data_years:
                    ystr = '{}'.format(year)
                    # Make file list
                    tmp_fnam = self.mktemp(suffix='.csv')
                    command = self.python_path
                    command += ' {}'.format(os.path.join(self.scr_dir,'file_station_query.py'))
                    command += ' --server "{}"'.format(self.values['server'])
                    command += ' --port "{}"'.format(self.values['port'])
                    command += ' --rcdir "{}"'.format(netrc_dir)
                    command += ' --srcdir "{}"'.format('{}/{}'.format(self.values['{}_path'.format(pnam)],year))
                    command += ' --out_csv "{}"'.format(tmp_fnam)
                    command += ' --max_layer 0'
                    try:
                        self.run_command(command,message='<<< Make Sentinel-2 {} list ({}) >>>'.format(targ,ystr))
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
                        #fileName,nLayer,fileSize,modifiedDate,folderName,md5Checksum
                        src_fnam = row['fileName']
                        m = re.search('^('+'\d'*8+')_'+enam,src_fnam)
                        if not m:
                            continue
                        dstr = m.group(1)
                        d = datetime.strptime(dstr,'%Y%m%d')
                        if d < first_dtim or d > last_dtim:
                            continue
                        inds.append(index)
                    if len(inds) < 1:
                        self.print_message('No Sentinel-2 {} data for download ({})'.format(targ,ystr),print_time=False)
                        continue
                    tmp_fnam = self.mktemp(suffix='.csv')
                    df.loc[inds].to_csv(tmp_fnam,index=False)
                    # Download Data
                    command = self.python_path
                    command += ' {}'.format(os.path.join(self.scr_dir,'file_station_download_file.py'))
                    command += ' --server "{}"'.format(self.values['server'])
                    command += ' --port "{}"'.format(self.values['port'])
                    command += ' --rcdir "{}"'.format(netrc_dir)
                    command += ' --inp_list "{}"'.format(tmp_fnam)
                    command += ' --dstdir "{}"'.format(os.path.join(self.s2_data,targ,ystr))
                    command += ' --verbose'
                    if self.values['oflag'][iflag]:
                        command += ' --overwrite'
                    self.run_command(command,message='<<< Download Sentinel-2 {} ({}) >>>'.format(targ,ystr))
                    if os.path.exists(tmp_fnam):
                        os.remove(tmp_fnam)

        # Finish process
        super().finish()
        return
