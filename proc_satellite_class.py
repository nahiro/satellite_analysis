from proc_class import Process

class Satellite_Process(Process):

    def __init__(self):
        super().__init__()
        self.s1_analysis = None
        self.s2_data = None
        self.s2_analysis = None