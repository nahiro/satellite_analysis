#!/usr/bin/env python
import os
import psutil
mem_size = int(psutil.virtual_memory().available*0.8e-6)
topdir = os.getcwd()
options = '-Xmx{}m'.format(mem_size) # Save memory for JAVA
options += ' -Djava.io.tmpdir='+topdir # Temporary directory
os.environ['_JAVA_OPTIONS'] = options
if os.name == 'nt':
    os.system('set _JAVA_OPTIONS="{}"'.format(options))
else:
    os.system('export _JAVA_OPTIONS="{}"'.format(options))
import sys
from snappy import ProductIO
from argparse import ArgumentParser,RawTextHelpFormatter

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-I','--inp_fnam',default=None,help='Input file name (%(default)s)')
parser.add_argument('-O','--out_fnam',default=None,help='Output file name (%(default)s)')
args = parser.parse_args()
if not os.path.exists(args.inp_fnam):
    raise IOError('Error, args.inp_fnam={}'.format(args.inp_fnam))

# Read original product
data = ProductIO.readProduct(os.path.abspath(args.inp_fnam))
band_list = list(data.getBandNames())
if args.out_fnam is None:
    for i,band in enumerate(band_list):
        sys.stdout.write('{:2d} {}\n'.format(i+1,band))
else:
    with open(args.out_fnam,'w') as fp:
        for i,band in enumerate(band_list):
            fp.write('{:2d} {}\n'.format(i+1,band))
