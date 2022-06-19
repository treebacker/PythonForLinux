import sys
import os
import linux
from linux.linuxobject import process

class TestProcess(object):

    def __init__(self, pid):
        self.proc = process.Process(pid)

    def get_proc_path(self):

        return self.proc._procfs_path
    def get_process_pids(self):
        pass
    

if __name__ == '__main__':

    tp = process.get_cuurent_process()

    print(tp.caps)
    print(tp.cwd)