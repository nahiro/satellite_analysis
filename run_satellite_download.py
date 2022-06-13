import os
import sys
import re
from datetime import datetime
from glob import glob
import numpy as np
from subprocess import call
from proc_class import Process

class Download(Process):

    def run(self):
        # Start process
        super().run()


        # Finish process
        sys.stderr.write('Finished process {}.\n\n'.format(self.proc_name))
        sys.stderr.flush()
        return
