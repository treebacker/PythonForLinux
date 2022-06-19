import os
from linux  import utils
from linuxobject import kernel_module, process


class System(object):

    """
    The state of the current ``Linux`` system where ``Python`` is running on
    """
    
    @property
    def processes(self):
        return self.enumerate_processes()


    @property
    def services(self):
        return self.enumerate_services()

    @property
    def computer_name(self):
        return utils.bcat("/proc/sys/kernel/hostname")

    @property
    def product_type(self):
        pass

    @property
    def version(self):
        return utils.bcat("/proc/sys/kernel/version")

    @property
    def kmods(self):
        return self.enumerate_kernel_modules()

    @staticmethod
    def enumerate_processes(self):
        res = []
        for pid in process.pids():
            res.append(process.Process(pid))
        return res

    @staticmethod
    def enumerate_services(self):
        pass


    @staticmethod
    def enumerate_kernel_modules(self):
        res = []
        for kname in kernel_module.kernel_modules():
            res.append(kernel_module.KernelModule(kname))
        pass