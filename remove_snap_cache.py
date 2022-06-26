#!/usr/bin/env python
import os
import sys
import time
from glob import glob
from datetime import datetime,timedelta
from subprocess import check_output,PIPE
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')

# Default values
DT_MAX = 300 # 5 minutes

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-m','--dt_max',default=DT_MAX,type=float,help='Max time difference in sec (%(default)s)')
parser.add_argument('-f','--force',default=False,action='store_true',help='Force to remove (%(default)s)')
args = parser.parse_args()

tcur = time.time()
files = glob('/tmp/jffi*')
files.extend(glob('/tmp/imageio*'))
files.extend(glob(os.path.join(HOME,'.snap/var/cache/temp/imageio*')))

for f in files:
    t = os.path.getmtime(f)
    dt = tcur-t
    if dt <= args.dt_max:
        continue
    try:
        out = check_output('fuser '+f,stderr=PIPE,shell=True)
        # fuser returns a non-zero return code if none of the specified
        # files is accessed or in case of a fatal error. If at least one
        # access has been found, fuser returns zero.
        sys.stderr.write('{} is used by {}\n'.format(f,out.decode().strip()))
        if args.force:
            raise ValueError('')
    except Exception:
        if os.path.exists(f):
            os.remove(f)
            sys.stderr.write('{} is removed\n'.format(f))
