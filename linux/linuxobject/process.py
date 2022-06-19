import os
import re
import signal
import time
from linux  import utils


def pids():
    """
    Return a list of pid currently running on the system
    """
    return [int(x) for x in os.listdir(b(utils.get_procfs_path())) if x.isdigit()]


def pid_exits(pid):
    """
        Check a given pid if exits.
        refer `man 2 kill`
    """
    if pid == 0:
        return True
    
    try:
        os.kill(pid, 0)

    except ProcessLookupError:
        return False
    
    except PermissionError:
        return True

    else:
        return True

class Process(object):
    
    def __init__(self, pid):
        self.pid = pid
        self.__init_proc_files()                                                                                                             
        pass

    def __init_proc_files(self):
        self._procfs_path = utils.get_procfs_path()
        self._proc_map = "{}/{}/maps".format(self._procfs_path, self.pid)
        self._proc_mem = "{}/{}/mem".format(self._procfs_path, self.pid)


    def _parse_stat_file(self):
        """
            parse /proc/[pid]/stat file
        """
        data = utils.bcat("{}/{}/stat".format(self._procfs_path, self.pid))

        # Process name is between ().
        # It can contain spaces and other parenheses.
        rapr = data.rfind(b')')
        name = data[data.rfind(b'(')  + 1: rapr]
        fileds = data[rapr+2:].split()

        ret = {}
        ret["name"] = name
        ret["status"] = fileds[0]
        ret["ppid"] = fileds[1]
        ret["pgroup"] = fileds[2]
        ret["session"] = fileds[3]
        ret["ttynr"] = fileds[4]
        ret["utime"] = fileds[11]
        ret["stime"] = fileds[12]
        ret["cutime"] = fileds[13]
        ret["cstime"] = fileds[14]
        ret["nice"] = fileds[16]
        ret["num_threads"] = fileds[17]
        ret["start_time"] = fileds[19]
        ret["processor"] = fileds[39]

        return ret
    
    def stop(self):
        try:
            os.kill(self.pid, signal.SIGSTOP)
            while True:
                self._parse_stat_file()
                if self.status in [b"T", b"t"]:
                    break
                pass
                time.sleep(0.1)
        except Exception as e:
            print("Stop process {} failed: {}".format(self.pid, str(e)))

        pass

    def freeze(self):
        pass

    def cont(self):
        try:
            os.kill(self.pid, signal.SIGCONT)
            while True:
                self._parse_stat_file()
                if self.status not in [b"T", b"t"]:
                    break
                pass
                time.sleep(0.1)
        except Exception as e:
            print("Continue process {} failed: {}".format(self.pid, str(e)))
        pass


    def _read_status_file(self):
        with utils.open_binary("{}/{}/status".format(self._procfs_path, self.pid)) as f:
            return f.read()


    def _read_cgroup_file(self):
        with utils.open_binary("{}/{}/cgroup".format(self._procfs_path, self.pid)) as f:
            return f.read()

    
    def _read_smaps_file(self):
        with utils.open_binary("{}/{}/smaps".format(self._procfs_path, self.pid)) as f:
            return f.read()
    
    @property
    def maps(self):
        rets = []
        data = utils.bcat(self._proc_map)
        lines = data.split(b'\n')
        for line in lines[:-1]:
            fileds = line.split()
            rets.append({
                "start" : int(fileds[0].split(b'-')[0], 16),
                "end" : int(fileds[0].split(b'-')[1], 16),
                "perms" : fileds[1],
                "offset" : fileds[2],
                "inode" : fileds[-2],
                "name": fileds[-1]
            })
        return rets

    @property
    def cwd(self):
        try:
            return os.readlink("{}/{}/cwd".format(self._procfs_path, self.pid))
        except:
            if not pid_exits(self.pid):
                raise ValueError("No such process with pid: {}".format(self.pid))

    @property
    def syscalls(self):
        sys = dict()
        syscall_vals = utils.bcat("{}/{}/syscall".format(self._procfs_path, self.pid)).split(b" ")
        sys["rip"] = int(syscall_vals[-1][2:], 16)
        sys["rsp"] = int(syscall_vals[-2][2:], 16)
        return sys

    @property
    def threads(self):
        rets = []
        for name in os.listdir("{}/{}/tasks".format(self._procfs_path, self.pid)):
            rets.append(int(name))

    @property
    def exe(self):
        return os.readlink("{}/{}/exe".format(self._procfs_path, self.pid))

    @property
    def name(self):
        return self._parse_stat_file()["name"]

    @property
    def num_threads(self):
        return int(self._parse_stat_file()["num_threads"])

    @property
    def nice(self):
        return int(self._parse_stat_file()["nice"])

    @property
    def ppid(self):
        return int(self._parse_stat_file()["ppid"])
    
    @property
    def status(self):
        return self._parse_stat_file()["status"]


    @property
    def caps(self, 
                _capinh_re=re.compile(br"CapInh:\t(\d+)"),
                _capprm_re=re.compile(br"CapPrm:\t(\d+)"),
                _capeff_re=re.compile(br"CapEff:\t(\d+)"),
                _capbnd_re=re.compile(br"CapBnd:\t(\d+)"),
                _capamd_re=re.compile(br"CapAmb:\t(\d+)"),
                ):
        caps = {}
        data = self._read_status_file()

        caps["inherit"] = _capinh_re.findall(data)[0]
        caps["permmit"] = _capprm_re.findall(data)[0]
        caps["effect"]  = _capeff_re.findall(data)[0]
        caps["bound"]   = _capbnd_re.findall(data)[0]
        ambient         = _capamd_re.findall(data)
        if len(ambient):
            caps["ambient"] = ambient[0]

        return caps

def get_cuurent_process():
    return Process(os.getpid())