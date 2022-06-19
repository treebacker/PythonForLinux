# -*- coding: utf-8 -*-
import sys
import os
from linux.security import inject

class TestInject(object):

    def __init__(self, pid):
        self.injector = inject.Inject(pid)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("inject.py [PID]")
        sys.exit(-1)

    pid = int(sys.argv[1])
    h = TestInject(pid)
    #h.injector.execute_shellcode(b"H\xc7\xc0\x01\x00\x00\x00H\xc7\xc7\x01\x00\x00\x00H\x8d5\n\x00\x00\x00H\xc7\xc2\r\x00\x00\x00\x0f\x05\xc3Hello, world\n")\
    #h.injector.load_library("tests/lib.so")
    #h.injector.execute_python_code(b"print('i am from python')")
    h.injector.execute_python_file(b"/home/tree/code/PythonForLinux/tests/test.py")
    