import sys
import os
import linux
from linux.linuxobject import kernel_module

class TestModule(object):

    def __init__(self, name):
        self.proc = kernel_module.KernelModule(name)


if __name__ == '__main__':

    for name in  kernel_module.kernel_modules():
        mod = kernel_module.KernelModule(name)
        print(mod.name, mod.size, mod.refcnt, mod.holders)