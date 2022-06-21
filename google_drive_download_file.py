#!/usr/bin/env python
import os
import sys
import hashlib
from dateutil.parser import parse
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import pandas as pd
from subprocess import call
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
DRVDIR = os.path.join(HOME,'Work','GoogleDrive')
MAX_RETRY = 10

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--inp_list',default=None,help='Input file list (%(default)s)')
parser.add_argument('-D','--dstdir',default=None,help='Local destination directory (%(default)s)')
parser.add_argument('--drvdir',default=DRVDIR,help='GoogleDrive directory (%(default)s)')
parser.add_argument('-M','--max_retry',default=MAX_RETRY,type=int,help='Maximum number of retries to download data (%(default)s)')
parser.add_argument('-m','--modify_time',default=False,action='store_true',help='Modify last modification time (%(default)s)')
parser.add_argument('-v','--verbose',default=False,action='store_true',help='Verbose mode (%(default)s)')
parser.add_argument('--overwrite',default=False,action='store_true',help='Overwrite mode (%(default)s)')
args = parser.parse_args()
args.dstdir = os.path.abspath(args.dstdir)

folders = {}
def check_folder(row):
    global folders
    nlayer = row['nLayer']
    if nlayer < 1:
        return
    fnam = row['fileName']
    indx = fnam.rfind('/')
    if indx < 0:
        raise ValueError('Error, indx={}, nlayer={} >>> {}'.format(indx,nlayer,fnam))
    dnam = fnam[:indx]
    if dnam in folders:
        return
    dnams = dnam.split('/')
    if len(dnams) != nlayer:
        raise ValueError('Error, len(dnams)={}, nlayer={} >>> {}'.format(len(dnams),nlayer,fnam))
    fid = row['fileId']
    f = drive.CreateFile({'id':fid})
    for n in range(nlayer):
        dnam = '/'.join(dnams[:nlayer-n])
        if dnam in folders:
            break
        p = f['parents']
        if len(p) != 1:
            raise ValueError('Error, len(p)={} >>> {}'.format(len(p),dnam))
        fid = p[0]['id']
        f = drive.CreateFile({'id':fid})
        if f['title'] != dnams[nlayer-1-n]:
            raise ValueError('Error, f["title"]={}, dnams[{}]={}'.format(f['title'],nlayer-1-n,dnams[nlayer-1-n]))
        folders[dnam] = fid

df = pd.read_csv(args.inp_list,comment='#')
df.columns = df.columns.str.strip()

topdir = os.getcwd()
os.chdir(args.drvdir)

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

for index,row in df.iterrows():
    check_folder(row)
    #fileName,nLayer,fileSize,modifiedDate,fileId,md5Checksum
    nlayer = row['nLayer']
    src_fnam = row['fileName']
    src_id = row['fileId']
    #src_size = row['fileSize']
    #src_time = row['modifiedDate']
    #src_md5 = row['md5Checksum']
    f = drive.CreateFile({'id':src_id})
    if f['title'] != os.path.basename(src_fnam):
        sys.stderr.write('Warning, f["title"]={}, src_fnam={}\n'.format(f['title'],src_fnam))
        sys.stderr.flush()
    dst_fnam = os.path.normpath(os.path.join(args.dstdir,src_fnam))
    dst_dnam = os.path.dirname(dst_fnam)
    if not os.path.exists(dst_dnam):
        os.makedirs(dst_dnam)
    flag = False
    src_size = int(f['fileSize'])
    src_time = parse(f['modifiedDate']).timestamp()
    src_md5 = f['md5Checksum'].upper()
    if os.path.exists(dst_fnam):
        if args.overwrite:
            if args.verbose:
                sys.stderr.write('File exists, remove >>> {}\n'.format(dst_fnam))
                sys.stderr.flush()
            os.remove(dst_fnam)
        else:
            dst_size = os.path.getsize(dst_fnam)
            with open(dst_fnam,'rb') as fp:
                dst_md5 = hashlib.md5(fp.read()).hexdigest().upper()
            if (dst_size == src_size) and (dst_md5 == src_md5):
                if args.modify_time:
                    os.utime(dst_fnam,(src_time,src_time))
                if args.verbose:
                    sys.stderr.write('File exists, skip >>> {}\n'.format(dst_fnam))
                    sys.stderr.flush()
                continue
    for ntry in range(args.max_retry): # loop to download 1 file
        f.GetContentFile(dst_fnam)
        if os.path.exists(dst_fnam):
            dst_size = os.path.getsize(dst_fnam)
            with open(dst_fnam,'rb') as fp:
                dst_md5 = hashlib.md5(fp.read()).hexdigest().upper()
            if (dst_size != src_size) or (dst_md5 != src_md5):
                sys.stderr.write('Warning, dst_size={}, dst_md5={}, src_size={}, src_md5={} >>> {}\n'.format(dst_size,dst_md5,src_size,src_md5,dst_fnam))
                sys.stderr.flush()
            else:
                os.utime(dst_fnam,(src_time,src_time))
                flag = True
                break
    if not flag:
        sys.stderr.write('Warning, faild in downloading >>> {}\n'.format(dst_fnam))
        sys.stderr.flush()
for dnam in folders.keys():
    src_id = folders[dnam]
    f = drive.CreateFile({'id':src_id})
    src_time = parse(f['modifiedDate']).timestamp()
    dst_dnam = os.path.normpath(os.path.join(args.dstdir,dnam))
    if not os.path.isdir(dst_dnam):
        raise IOError('Error, no such directory >>> {}'.format(dst_dnam))
    os.utime(dst_dnam,(src_time,src_time))
os.chdir(topdir)
