#!/usr/bin/env python
import os
import sys
import hashlib
from dateutil.parser import parse
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from subprocess import call
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
DRVDIR = os.path.join(HOME,'Work','GoogleDrive')

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-S','--srcdir',default=None,help='GoogleDrive source directory (%(default)s)')
parser.add_argument('--drvdir',default=DRVDIR,help='GoogleDrive directory (%(default)s)')
parser.add_argument('-O','--out_csv',default=None,help='Output CSV name (%(default)s)')
parser.add_argument('-N','--max_layer',default=None,type=int,help='Maximum layer number (%(default)s)')
parser.add_argument('-A','--append',default=False,action='store_true',help='Append csv file (%(default)s)')
args = parser.parse_args()

if args.out_csv is not None:
    args.out_csv = os.path.abspath(args.out_csv)
topdir = os.getcwd()
os.chdir(args.drvdir)

folders = {}

def query_folder(path):
    global folders
    parent = os.path.dirname(path)
    target = os.path.basename(path)
    if (parent == '') or (parent == '/'):
        l = drive.ListFile({'q': '"root" in parents and trashed = false and mimeType = "application/vnd.google-apps.folder" and title = "{}"'.format(target)}).GetList()
        n_list = len(l)
        if n_list != 1:
            os.chdir(topdir)
            raise ValueError('Error in finding folder, n_list={} >>> {}'.format(n_list,path))
        folders.update({path:l[0]})
        return 0
    elif not parent in folders:
        os.chdir(topdir)
        raise IOError('Error, no such folder >>> '+parent)
    l = drive.ListFile({'q': '"{}" in parents and trashed = false and mimeType = "application/vnd.google-apps.folder" and title = "{}"'.format(folders[parent]['id'],target)}).GetList()
    n_list = len(l)
    if n_list > 1:
        os.chdir(topdir)
        raise ValueError('Error in finding folder, n_list={} >>> {}'.format(n_list,path))
    elif n_list == 1:
        if not path in folders:
            folders.update({path:l[0]})
        return 0
    else:
        os.chdir(topdir)
        raise ValueError('Error, no such folder >>> {}'.format(target))
    return -1

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

l = args.srcdir.split(os.sep)
for i in range(len(l)):
    if not l[i]:
        continue
    d = os.sep.join(l[:i+1])
    query_folder(d)

src_id = folders[args.srcdir]['id']
qs = [src_id]
ds = ['']
ns = [0]
if args.out_csv is None:
    sys.stdout.write('fileName,nLayer,fileSize,modifiedDate,fileId,md5Checksum\n')
else:
    if args.append:
        with open(args.out_csv,'a') as fp:
            fp.write('# {}\n'.format(args.srcdir))
    else:
        with open(args.out_csv,'w') as fp:
            fp.write('fileName,nLayer,fileSize,modifiedDate,fileId,md5Checksum\n')
            fp.write('# {}\n'.format(args.srcdir))
while len(qs) != 0:
    src_id = qs.pop(0)
    srcdir = ds.pop(0)
    nlayer = ns.pop(0)
    fs = drive.ListFile({'q':'"{}" in parents and trashed = false'.format(src_id)}).GetList()
    for f in fs:
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            if args.max_layer is not None and nlayer >= args.max_layer:
                continue
            qs.append(f['id'])
            if srcdir == '':
                ds.append(f['title'])
            else:
                ds.append(srcdir+'/'+f['title'])
            ns.append(nlayer+1)
        else:
            if args.max_layer is not None and nlayer > args.max_layer:
                continue
            if srcdir == '':
                fnam = f['title']
            else:
                fnam = srcdir+'/'+f['title']
            if args.out_csv is None:
                sys.stdout.write('{},{},{},{},{},{}\n'.format(fnam,nlayer,f['fileSize'],f['modifiedDate'],f['id'],f['md5Checksum']))
            else:
                with open(args.out_csv,'a') as fp:
                    fp.write('{},{},{},{},{},{}\n'.format(fnam,nlayer,f['fileSize'],f['modifiedDate'],f['id'],f['md5Checksum']))
os.chdir(topdir)
