import ctypes

class Syscall(object):


    def __init__(self):
        self.libc = ctypes.CDLL("libc.so.6")
    
    def getuid(self):
        return self.libc.getuid()
    
    def geteuid(self):
        return self.libc.geteuid()

    def setuid(self, uid):
        return self.libc.seteuid(uid)
    
    def seteuid(self, euid):
        return self.libc.seteuid(euid)
    

    def kill(self, pid, sig):
        return self.libc.kill(pid, sig)
        
    def mmap(self):
        return self.mmap()

    
    def process_vm_readv(self, pid, local, 
                        local_cnt, remote, remote_cnt, flags):
        return self.libc.process_vm_readv(pid, local, 
                        local_cnt, remote, remote_cnt, flags)

    def process_vm_writev(self, pid, local, 
                        local_cnt, remote, remote_cnt, flags):
        return self.libc.process_vm_writev(pid, local, 
                        local_cnt, remote, remote_cnt, flags)