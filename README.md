### PythonForLinux
PythonForLinux(PFL) is a base of code amied to make interaction with linux (on x86/x64) easier.
Its goal is to offer abstractions around some of the OS features in a (I hope) pythonic way. 

This project is inspired by [PythonForWindows](https://github.com/hakril/PythonForWindows) Project.
At the same time, i want the project will help me(any one) learn linux internals more effectivelly.

### Installation

```
python3 setup.py install
```
#### Process / Threads
PythonForLinux offers objecs around processes and allows you to:
* Retrieve basic process informations (pid, name, ppid, bitness, ...)
* Perform basic interprocess operation (allocation, read/write memory)
* Execute `native` and `Python` code int the context of a process.

I try my best to make th9oes features available for every creoss-bitness processes(32/64 in both ways).
You can also makre some oeration on threads(suspend/resume/wait/get(or set) context / kill)

#### Namespace

#### System Information

#### Securitys
* Inject process


