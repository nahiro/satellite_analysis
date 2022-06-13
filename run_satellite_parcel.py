import os
import sys
import re
from datetime import datetime
try:
    import gdal
except Exception:
    from osgeo import gdal
from glob import glob
import numpy as np
from subprocess import call
from proc_class import Process

class Parcel(Process):

    def run(self):
        # Start process
        super().run()


        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
