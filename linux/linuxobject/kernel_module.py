from ctypes import util
import os
from linux import utils

class KernelModule(object):
    def __init__(self, name):
        
        self.name = name
        self._sysmod_path = utils.get_sysmod_path()
        pass

    @property
    def size(self):
        data = utils.bcat("{}/{}/coresize".format(self._sysmod_path, self.name))
        return int(data)

    @property
    def refcnt(self):
        data = utils.bcat("{}/{}/refcnt".format(self._sysmod_path, self.name))
        return int(data)

    @property
    def holders(self):
        rets = os.listdir("{}/{}/holders".format(self._sysmod_path, self.name))
        return rets

    
    def dump_from_memory(self):
        """
        Dump the module content from the memory.
        """
        pass
    


def kernel_modules():
    """ Get All loaded kernel module names on the system."""
    return  [x for x in os.listdir(utils.get_sysmod_path()) if os.path.exists(os.path.join(utils.get_sysmod_path(), x, "coresize"))]