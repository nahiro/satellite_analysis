#!/usr/bin/env python
import os
import sys
import re
import shutil
import hashlib
from base64 import b64encode
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging
from http.client import HTTPConnection
import time
from datetime import datetime,timedelta
from dateutil.parser import parse
import pytz
import pandas as pd
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
RCDIR = HOME
PORT = 443
MAX_ITEM = 10000
MAX_RETRY = 10

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-i','--inp_list',default=None,help='Input file list (%(default)s)')
parser.add_argument('-D','--dstdir',default=None,help='Local destination directory (%(default)s)')
parser.add_argument('-s','--srcdir',default=None,help='NAS source directory (%(default)s)')
parser.add_argument('--rcdir',default=RCDIR,help='Directory where .netrc exists (%(default)s)')
parser.add_argument('-S','--server',default=None,help='Name of the server (%(default)s)')
parser.add_argument('-P','--port',default=PORT,type=int,help='Port# of the server (%(default)s)')
parser.add_argument('-M','--max_item',default=MAX_ITEM,type=int,help='Max# of items for listing (%(default)s)')
parser.add_argument('-R','--max_retry',default=MAX_RETRY,type=int,help='Maximum number of retries to download data (%(default)s)')
parser.add_argument('-m','--modify_time',default=False,action='store_true',help='Modify last modification time (%(default)s)')
parser.add_argument('-l','--logging',default=False,action='store_true',help='Logging mode (%(default)s)')
parser.add_argument('-v','--verbose',default=False,action='store_true',help='Verbose mode (%(default)s)')
parser.add_argument('--overwrite',default=False,action='store_true',help='Overwrite mode (%(default)s)')
args = parser.parse_args()
args.dstdir = os.path.abspath(args.dstdir)

def get_time(s):
    try:
        t = datetime.utcfromtimestamp(s).replace(tzinfo=pytz.UTC)
    except Exception:
        raise ValueError('Error in time >>> '+s)
    return t

def list_file(path=None):
    ds = []
    fs = {}
    try:
        resp = session.get(common_url+'&func=get_list&path={}&limit={}'.format(path,args.max_item))
        params = resp.json()
        if 'datas' in params:
            items = params['datas']
            for item in items:
                if item['isfolder'] == 1:
                    ds.append(item['filename'])
                else:
                    fs.update({item['filename']:{'size':int(item['filesize']),'mtime':get_time(item['epochmt'])}})
        else:
            status = params['status']
            raise ValueError('Error, status={}'.format(status))
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        sys.stderr.write('Error in listing file >>> {}\n'.format(path))
        sys.stderr.flush()
        return None,None
    return ds,fs

def query_file(path):
    parent = os.path.dirname(path)
    target = os.path.basename(path)
    try:
        resp = session.get(common_url+'&func=checksum&file_total=1&path={}&file_name={}'.format(parent,target))
        params = resp.json()
        if 'datas' in params:
            item = params['datas'][0]
        else:
            status = params['status']
            raise ValueError('Error, status={}'.format(status))
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        sys.stderr.write('Error in querying file >>> {}\n'.format(path))
        sys.stderr.flush()
        return None
    return item['filename'],int(item['filesize']),get_time(item['mt']),item['checksum']

def query_folder(path):
    parent = os.path.dirname(path)
    target = os.path.basename(path)
    try:
        resp = session.get(common_url+'&func=stat&file_total=1&path={}&file_name={}'.format(parent,target))
        params = resp.json()
        if 'datas' in params:
            item = params['datas'][0]
        else:
            status = params['status']
            raise ValueError('Error, status={}'.format(status))
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        sys.stderr.write('Error in querying file >>> {}\n'.format(path))
        sys.stderr.flush()
        return None
    if item['isfolder'] != 1:
        sys.stderr.write('Error, not a folder >>> {}\n'.format(path))
        sys.stderr.flush()
        return None
    else:
        return item['filename'],int(item['filesize']),get_time(item['epochmt'])

def download_file(src_path,dst_path):
    parent = os.path.dirname(src_path)
    target = os.path.basename(src_path)
    try:
        resp = session.get(common_url+'&func=download&source_total=1&source_path={}&source_file={}'.format(parent,target))
        if resp.status_code != 200:
            raise ValueError('Error, status={}'.format(resp.status_code))
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        sys.stderr.write('Error in querying file >>> {}\n'.format(path))
        sys.stderr.flush()
        return None
    with open(dst_path,'wb') as fp:
        fp.write(resp.text)

folders = {}
def check_folder(row):
    global folders
    nlayer = row['nLayer']
    if nlayer < 1:
        return
    fnam = row['fileName']
    pnam = row['folderName']
    indx = fnam.rfind('/')
    if indx < 0:
        raise ValueError('Error, indx={}, nlayer={} >>> {}'.format(indx,nlayer,fnam))
    dnam = fnam[:indx]
    if dnam in folders:
        return
    dnams = dnam.split('/')
    if len(dnams) != nlayer:
        raise ValueError('Error, len(dnams)={}, nlayer={} >>> {}'.format(len(dnams),nlayer,fnam))
    for n in range(nlayer):
        dnam = '/'.join(dnams[:nlayer-n])
        if dnam in folders:
            break
        v = query_folder(pnam+'/'+dnam)
        if v is None:
            raise IOError('Error in finding {}'.format(dnam))
        folders[dnam] = v[2]

fnam = os.path.join(args.rcdir,'.netrc')
if not os.path.exists(fnam):
    raise IOError('Error, no such file >>> '+fnam)
server = None
username = None
password = None
flag = False
with open(fnam,'r') as fp:
    for line in fp:
        m = re.search('machine\s+(\S+)',line)
        if m:
            if re.search(args.server,m.group(1)):
                flag = True
                server = m.group(1)
            else:
                flag = False
            continue
        m = re.search('login\s+(\S+)',line)
        if m:
            if flag:
                username = m.group(1)
            continue
        m = re.search('password\s+(\S+)',line)
        if m:
            if flag:
                password = m.group(1)
            continue
if server is None or username is None or password is None:
    raise ValueError('Error, server={}, username={}, password={}'.format(server,username,password))
encode_string = b64encode(password.encode()).decode()

# Create a requests session
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
session = requests.sessions.Session()
session.verify = False
# Get session ID
url = 'https://{}:{}/cgi-bin/authLogin.cgi?user={}&pwd={}'.format(server,args.port,username,encode_string)
try:
    resp = session.get(url)
    m = re.search('<authSid><!\[CDATA\[(\S+)\]\]><\/authSid>',resp.text)
    sid = m.group(1)
except Exception as e:
    sys.stderr.write('Login failed >>> '+str(e)+'\n')
    sys.stderr.flush()
    sys.exit()
common_url = 'https://{}:{}/cgi-bin/filemanager/utilRequest.cgi?sid={}'.format(server,args.port,sid)
if args.logging:
    log = logging.getLogger('urllib3')
    log.setLevel(logging.DEBUG)
    stream = logging.StreamHandler()
    stream.setLevel(logging.DEBUG)
    log.addHandler(stream)
    HTTPConnection.debuglevel = 1

df = pd.read_csv(args.inp_list,comment='#')
df.columns = df.columns.str.strip()

for index,row in df.iterrows():
    check_folder(row)
    #fileName,nLayer,fileSize,modifiedDate,folderName,md5Checksum
    nlayer = row['nLayer']
    src_fnam = row['fileName']
    src_dnam = row['folderName']
    #src_size = row['fileSize']
    #src_time = parse(row['modifiedDate']).timestamp()
    #src_md5 = row['md5Checksum']
    dst_fnam = os.path.normpath(os.path.join(args.dstdir,src_fnam))
    dst_dnam = os.path.dirname(dst_fnam)
    if not os.path.exists(dst_dnam):
        os.makedirs(dst_dnam)
    flag = False
    fnam = src_dnam+'/'+src_fnam
    v = query_file(fnam)
    if v is None:
        raise IOError('Error in finding {}'.format(fnam))
    src_size = v[1]
    src_time = v[2].timestamp()
    src_md5 = v[3].upper()
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
        download_file(fnam,dst_fnam)
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
"""
for dnam in folders.keys():
    src_id = folders[dnam]
    f = drive.CreateFile({'id':src_id})
    src_time = parse(f['modifiedDate']).timestamp()
    dst_dnam = os.path.normpath(os.path.join(args.dstdir,dnam))
    if not os.path.isdir(dst_dnam):
        raise IOError('Error, no such directory >>> {}'.format(dst_dnam))
    os.utime(dst_dnam,(src_time,src_time))
"""
