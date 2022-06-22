import os
import sys
import re
from datetime import datetime
from glob import glob
import numpy as np
from subprocess import call
from proc_satellite_class import Satellite_Process

class Download(Satellite_Process):

    def run(self):
        # Start process
        super().run()

        # Check files/folders
        wrk_dir = os.path.join(self.s2_data)
        if not os.path.exists(wrk_dir):
            os.makedirs(wrk_dir)
        if not os.path.isdir(wrk_dir):
            raise ValueError('{}: error, no such folder >>> {}'.format(self.proc_name,wrk_dir))

        # Make file list
        tmp_fnam = os.path.join(wrk_dir,'temp.dat')
        if os.path.exists(tmp_fnam):
            os.remove(tmp_fnam)

        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
