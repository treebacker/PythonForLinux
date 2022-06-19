import os
from linux  import utils
from linuxobject import kernel_module, process


class Password(object):

    def __init__(self, pid):
        self.proc = process.Process(pid)
        pass
    
    def dump_password_from_memory(self):
        """
            Dump password from process's memory
        """
        
        pass