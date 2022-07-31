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
from subprocess import call
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
RCDIR = HOME
PORT = 443
MAX_ITEM = 10000

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-s','--srcdir',default=None,help='NAS source directory (%(default)s)')
parser.add_argument('--rcdir',default=RCDIR,help='Directory where .netrc exists (%(default)s)')
parser.add_argument('-S','--server',default=None,help='Name of the server (%(default)s)')
parser.add_argument('-P','--port',default=PORT,type=int,help='Port# of the server (%(default)s)')
parser.add_argument('-M','--max_item',default=MAX_ITEM,type=int,help='Max# of items for listing (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-N','--max_layer',default=None,type=int,help='Maximum layer number (%(default)s)')
parser.add_argument('-l','--logging',default=False,action='store_true',help='Logging mode (%(default)s)')
parser.add_argument('-A','--append',default=False,action='store_true',help='Append csv file (%(default)s)')
args = parser.parse_args()

if args.out_csv is not None:
    args.out_csv = os.path.abspath(args.out_csv)

def get_size(fnam):
    s = 'None'
    if os.path.exists(fnam):
        size = os.path.getsize(fnam)
        if size > TB:
            s = '{:.2f} TB'.format(size/TB)
        elif size > GB:
            s = '{:.2f} GB'.format(size/GB)
        elif size > MB:
            s = '{:.2f} MB'.format(size/MB)
        elif size > KB:
            s = '{:.2f} KB'.format(size/KB)
        else:
            s = '{} B'.format(size)
    return s

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

if query_folder(args.srcdir) is None:
    sys.exit()
qs = [args.srcdir]
ns = [0]
if args.out_csv is None:
    sys.stdout.write('fileName,nLayer,fileSize,modifiedDate,srcPath,md5Checksum\n')
else:
    if args.append:
        with open(args.out_csv,'a') as fp:
            fp.write('# {}\n'.format(args.srcdir))
    else:
        with open(args.out_csv,'w') as fp:
            fp.write('fileName,nLayer,fileSize,modifiedDate,srcPath,md5Checksum\n')
            fp.write('# {}\n'.format(args.srcdir))
while len(qs) != 0:
    srcdir = qs.pop(0)
    nlayer = ns.pop(0)
    ds,fs = list_file(srcdir)
    for f in fs:
        if args.max_layer is not None and nlayer > args.max_layer:
            continue
        if srcdir == '':
            fnam = f
        elif srcdir == '/':
            fnam = srcdir+f
        else:
            fnam = srcdir+'/'+f
        v = query_file(fnam)
        if v is None:
            continue
        elif args.out_csv is None:
            sys.stdout.write('{},{},{},{},{},{}\n'.format(f,nlayer,v[1],v[2],srcdir,v[3]))
        else:
            with open(args.out_csv,'a') as fp:
                fp.write('{},{},{},{},{},{}\n'.format(f,nlayer,v[1],v[2],srcdir,v[3]))
    for d in ds:
        if args.max_layer is not None and nlayer >= args.max_layer:
            continue
        if srcdir == '':
            dnam = d
        elif srcdir == '/':
            dnam = srcdir+d
        else:
            dnam = srcdir+'/'+d
        qs.append(dnam)
        ns.append(nlayer+1)
