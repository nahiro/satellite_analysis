#!/usr/bin/env python
import os
import sys
import re
from glob import glob
from datetime import datetime
import numpy as np
from matplotlib.dates import date2num,num2date
from csaps import csaps
import matplotlib.pyplot as plt
from argparse import ArgumentParser,RawTextHelpFormatter

# Default values
TMIN = '20190315'
TMAX = '20190615'
TMGN = 30.0 # day
TSTP = 0.1 # day
SMOOTH = 0.01
DATDIR = '.'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-s','--tmin',default=TMIN,help='Min date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date of transplanting in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=float,help='Margin of input data in day (%(default)s)')
parser.add_argument('-S','--smooth',default=SMOOTH,type=float,help='Smoothing factor from 0 to 1 (%(default)s)')
parser.add_argument('-D','--datdir',default=DATDIR,help='Input data directory, not used if input_fnam is given (%(default)s)')
parser.add_argument('--search_key',default=None,help='Search key for input data, not used if input_fnam is given (%(default)s)')
parser.add_argument('-o','--out_fnam',default=OUT_FNAM,help='Output GeoTIFF name (%(default)s)')
args = parser.parse_args()
