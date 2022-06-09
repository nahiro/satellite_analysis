import os
import sys
import numpy as np

def check_file(s,t):
    try:
        fnam = t.strip()
        if os.path.isdir(fnam):
            raise IOError('Error in {}, no such file but folder >>> {}'.format(s,fnam))
        elif not os.path.exists(fnam):
            raise IOError('Error in {}, no such file >>> {}'.format(s,fnam))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_files(s,t):
    try:
        for item in t.split('\n'):
            fnam = item.strip()
            if len(fnam) < 1:
                continue
            if os.path.isdir(fnam):
                raise IOError('Error in {}, no such file but folder >>> {}'.format(s,fnam))
            elif not os.path.exists(fnam):
                raise IOError('Error in {}, no such file >>> {}'.format(s,fnam))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_folder(s,t,make=False):
    try:
        dnam = t.strip()
        if make and not os.path.exists(dnam):
            os.makedirs(dnam)
        if not os.path.isdir(dnam):
            raise IOError('Error in {}, no such folder >>> {}'.format(s,dnam))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_folders(s,t,make=False):
    try:
        for item in t.split('\n'):
            dnam = item.strip()
            if len(dnam) < 1:
                continue
            if make and not os.path.exists(dnam):
                os.makedirs(dnam)
            if not os.path.isdir(dnam):
                raise IOError('Error in {}, no such folder >>> {}'.format(s,dnam))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_int(s,t,vmin=-sys.maxsize,vmax=sys.maxsize):
    try:
        n = int(t)
        if n < vmin or n > vmax:
            raise ValueError('Error in {}, out of range >>> {}'.format(s,t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False

def check_float(s,t,vmin=-sys.float_info.max,vmax=sys.float_info.max,allow_nan=False):
    try:
        v = float(t)
        if allow_nan and np.isnan(v):
            return True
        if v < vmin or v > vmax:
            raise ValueError('Error in {}, out of range >>> {}'.format(s,t))
        return True
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        return False
