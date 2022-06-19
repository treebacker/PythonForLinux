
from ctypes import util
import imp
import os
import re
import sys
import time
from ctypes import *
from linux  import utils
from linux.linuxobject import process,structs,syscall




class Inject(object):

    def __init__(self, pid):
        self.pid = pid
        self.proc = process.Process(pid)
        self.stack_backup_size = 0x8 * 0x10
        self.bad_codes = [0xdeadbeefdeadbeef, 0x1010101020202020, 0xffffffffffffffff]
        self.syscall = syscall.Syscall()


        self.code_backup = None
        self.stack_backup = None

        # init
        self.shell_stage_one = None
        self.stage_two_length = 0xffff

        self.stage_one_path = f"/tmp/stage_1_{format(os.urandom(16).hex())}"
        self.stage_two_path = f"/tmp/stage_2_{format(os.urandom(16).hex())}"
        self.stage_py_path = f"/tmp/stage_py_{format(os.urandom(16).hex())}"

    def find_region_by_perm(self, perm):
        pass

    def find_region_by_name(self, name):
        regions = []
        for rg in self.proc.maps:
            if name in rg["name"]:
                regions.append(rg)

        return regions

    def get_so_name_from_python_version(self):
        version = sys.version_info
        return "libpython{v.major}.{v.minor}.so".format(v=version).encode('utf-8')

    def find_python_so_to_inject(self):
        # Search python so library from current process
        self.py_so_name = self.get_so_name_from_python_version()

        if os.path.exists("/lib/x86_64-linux-gnu"):
            for name in os.listdir("/lib/x86_64-linux-gnu"):
                if self.py_so_name in name.encode('utf-8'):
                    return os.path.join("/", "lib", "x86_64-linux-gnu", name)

        pass
            

    def read_process_mem(self, addr, size):
        ret = b''
        local = (structs.iovec * 1)()
        remote = (structs.iovec * 1)()
        l_buffer = (c_char * 1024)()
        has_read = 0

        while size:
            to_read = min(size, 1024)
            local[0].iov_base = cast(byref(l_buffer), c_void_p)
            local[0].iov_len = to_read
            remote[0].iov_base = (c_void_p)(addr + has_read)
            remote[0].iov_len = to_read

            b_read = self.syscall.process_vm_readv(self.pid, local, 1, remote, 1, 0)
            if b_read != to_read:
                print("Read process {} at {} failed.".format(self.pid, hex(addr)))
                break
            ret += l_buffer[0:b_read]
            has_read += b_read
            size -= b_read

        return ret
        
    
    def write_process_mem(self, addr, chunk, size=0):
        ret = b''
        local = (structs.iovec * 1)()
        remote = (structs.iovec * 1)()
        has_write = 0

        if size == 0 :
            size = len(chunk)
            content = chunk
        else:
            c_size = len(chunk)
            content = chunk * (int(size / c_size))
            content += chunk[0:size % c_size]

        while size:
            to_write = min(size, 1024)
            l_buffer = c_char_p(content[has_write:])
            local[0].iov_base = cast(l_buffer, c_void_p)
            local[0].iov_len = to_write
            remote[0].iov_base = c_void_p(addr + has_write)
            remote[0].iov_len = to_write

            b_write = self.syscall.process_vm_writev(self.pid, local, 1, remote, 1, 0)
            if b_write != to_write:
                print("Write process {} at {} failed.".format(self.pid, hex(addr)))
                break
            size -= b_write
            has_write += b_write
            
        pass

    def construct_shellcode_stage_one(self):
        ret = utils.compile_asm(fr"""
            // backup register
            pushf
            push rax
            push rbx
            push rcx
            push rdx
            push rbp
            push rsi
            push rdi
            push r8
            push r9
            push r10
            push r11
            push r12
            push r13
            push r14
            push r15

            // open stage two
            mov rax, 2                      # SYS_OPEN
            lea rdi, path[rip]              # filename
            xor rsi, rsi                    # flags (O_RDONLY)
            xor rdx, rdx                    # mode 
            syscall
            mov r14, rax

            // mmap(addr, len, prot, flags, fd, off)
            mov rax, 9                      # 
            xor rdi, rdi                    # addr = NULL
            mov rsi, {self.stage_two_length}# lengh
            mov rdx, 7                      # prot (rwx)
            mov r10, 2                      # flags (MAP_PRIVATE)
            mov r8, r14                     # fd    
            xor r9, r9                      # off (0)
            syscall

            mov r15, rax                    # store the address

            // close(fd)
            mov rax, 3
            mov rdi, r14                    # close(fd)
            syscall

            // delete the stage2 file
            mov rax, 0x57                   # SYS_unlink
            lea rdi, path[rip]
            syscall

            // jmup to stage 2

            jmp r15

    path:
            .ascii "{self.stage_two_path}\0"
        """     , self.stage_one_path )

        if ret:
            with open(self.stage_one_path, "rb") as f:
                self.shell_stage_one = f.read()
        pass
    

    def construct_shellcode_stage_two(self, shellcode=b"", dl_open=0, lib_name=b""):
        """
            Type:
                1:  execute given shellcode and restore the orignal status
                2:  Load the given library and restore the orignal status
        """
        ret = False
        if len(shellcode) != 0:
            _type = 1
        elif dl_open != 0 and len(lib_name) != 0:
            _type = 2
        else:
            print("without shellcode and libname")

        ret = utils.compile_asm(fr"""
        // restore state
        cld
        fxsave moar_regs[rip]

        // open /proc/self/mem
        mov rax, 2
        lea rdi, proc_self_mem[rip]
        mov rsi, 2                   # flags (O_RDWR)
        xor rdx, rdx
        syscall
        mov r15, rax                 # save the fd

        // seek to code
        mov rax, 8                  # SYS_LSEEK
        mov rdi, r15                # fd
        mov rsi, {self.rip}         # offset
        xor rdx, rdx                # origin
        syscall

        // restore the code
        mov rax, 1                  # SYS_WRITE
        mov rdi, r15                # fd
        lea rsi, orig_code[rip]     # buffer
        mov rdx, {len(self.code_backup)} # length
        syscall

        // close /proc/self/mem
        mov rax, 3
        mov rdi, r15
        syscall

        // copy the pushed regs to fake stack
        lea rdi, fake_stack_base[rip - {self.stack_backup_size}]
        mov rsi, {self.rsp - self.stack_backup_size}
        mov rcx, {self.stack_backup_size}
        rep movsb

        // restore the stack
        mov rdi, {self.rsp - self.stack_backup_size}
        lea rsi, orig_stack[rip]
        mov rcx, {self.stack_backup_size}
        rep movsb

        // povit stack  
        // if we do this python code will need more stack
        //lea rax, fake_stack_base[rip]
        //lea rsp, fake_stack_base[rip-{self.stack_backup_size}]

        // do what you want
        // 1: exec shellcode
        // 2: load library
        mov rax, {_type}
        cmp rax, 1
        je exec_shellcode

    load_library:
        lea rdi, lib_name[rip]
        mov rsi, 2
        mov rdx, {dl_open}
        xor rcx, rcx
        mov rax, {dl_open}
        call rax
        jmp recovery

    exec_shellcode:
        lea rax, shellcode[rip]
        call rax
        
    recovery:
        xor rax, rax

        // restore regs stat
        fxrstor moar_regs[rip]
        pop r15
        pop r14
        pop r13
        pop r12
        pop r11
        pop r10
        pop r9
        pop r8
        pop rdi
        pop rsi
        pop rbp
        pop rdx
        pop rcx
        pop rbx
        pop rax
        popf

        # restore stack pointer and return to orig context
        mov rsp, {self.rsp}
        jmp orig_rip[rip]



proc_self_mem:
            .ascii "/proc/self/mem\0"
            
lib_name:
            .ascii "{lib_name}\0"

orig_rip:
            .quad {self.rip}

orig_code:
            .byte {",".join(map(str, self.code_backup))}

orig_stack:
            .byte {",".join(map(str, self.stack_backup))}

            .align 16
    
moar_regs:
            .space 512

shellcode:
            .byte {",".join(map(str, shellcode))}

fake_stack:
            .balign 0x8000

fake_stack_base:
        """, self.stage_two_path)

        if ret:
            with open(self.stage_two_path, "rb") as f:
                self.shell_stage_two = f.read()

        pass
    
    def generate_python_shellcode(self, py_code):
        regions = self.find_region_by_name(self.py_so_name)
        if len(regions) == 0:
            print("Failed to find {}".format(self.py_so_name))
            sys.exit(-1)
        
        ld_base = regions[0]["start"]

        self.PyEval_InitThreads = ld_base + utils.lookup_elf_symbol(self.py_so_path, "PyEval_InitThreads")
        self.PyEval_SaveThread = ld_base + utils.lookup_elf_symbol(self.py_so_path, "PyEval_SaveThread")
        self.Py_Initialize = ld_base + utils.lookup_elf_symbol(self.py_so_path, "Py_Initialize")
        self.Py_InitializeEx = ld_base + utils.lookup_elf_symbol(self.py_so_path, "Py_InitializeEx")
        self.Py_IsInitialized = ld_base + utils.lookup_elf_symbol(self.py_so_path, "Py_IsInitialized")
        self.PyGILState_Release = ld_base + utils.lookup_elf_symbol(self.py_so_path, "PyGILState_Release")
        self.PyGILState_Ensure = ld_base + utils.lookup_elf_symbol(self.py_so_path, "PyGILState_Ensure")
        self.PyRun_SimpleString = ld_base + utils.lookup_elf_symbol(self.py_so_path, "PyRun_SimpleString")
        self._Py_fopen = ld_base + utils.lookup_elf_symbol(self.py_so_path, "_Py_fopen")
        self.PyRun_AnyFile = ld_base + utils.lookup_elf_symbol(self.py_so_path, "PyRun_AnyFile")

        # script or file
        _type = 0
        if os.path.exists(py_code[0:-1]):
            _type = 2
        else:
            _type = 1
        ret = utils.compile_asm(fr"""
            mov rax, {self.Py_IsInitialized}
            call rax
            mov r10, rax
            test rax, rax
            jnz do_ensure
            
            mov rdi, 0
            push 0
            mov rax, {self.Py_InitializeEx}
            call rax
            pop rax

            mov rax, {self.PyEval_InitThreads}
            call rax
    do_ensure:
            mov rax, {self.PyGILState_Ensure}
            call rax
            mov r15, rax

            mov rax, {_type}
            cmp rax, 2
            jz exec_py_file

    exec_py_code:
            lea rdi, py_code[rip]
            push 0
            mov rax, {self.PyRun_SimpleString}
            call rax
            pop rbx
            
            jmp after_exec

    exec_py_file:
            lea rdi, py_code[rip]
            lea rsi, flags[rip]
            mov rax, {self._Py_fopen}
            call rax
            
            push 0
            mov rdi, rax
            lea rsi, py_code[rip]
            mov rax, {self.PyRun_AnyFile}
            call rax
            pop rax

    after_exec:

            mov rdi, r15
            mov r15, rax
            mov rax, {self.PyGILState_Release}
            call rax
            cmp r10, 0
            jnz return

            #if we call Py_IsInitialized
            # then PyEval_SaveThread
            mov rax, {self.PyEval_SaveThread}
            call rax

    return:
            ret

    py_code:
            .byte {",".join(map(str, py_code))}
    flags:
            .ascii "r\0"

        """, self.stage_py_path)
        if ret:
            with open(self.stage_py_path, 'rb') as p:
                return p.read()

    def execute_shellcode(self, code, stop="sigstop"):

        sys_vals = self.proc.syscalls
        self.rip = sys_vals["rip"]
        self.rsp = sys_vals["rsp"]

        self.construct_shellcode_stage_one()

        # stop the process to get process status
        if stop == "sigstop":
            self.proc.stop()
            pass

        elif stop == "freeze":
            self.proc.freeze()
            pass
        else:
            pass
        
        # backup text & stack status 
        # hihiack rip by /proc/[pid]/mem 
        with open(self.proc._proc_mem, "wb+") as mem:
            mem.seek(self.rip)
            self.code_backup = mem.read(len(self.shell_stage_one))

            mem.seek(self.rsp - self.stack_backup_size)
            self.stack_backup = mem.read(self.stack_backup_size)

            self.construct_shellcode_stage_two(shellcode=code)
            mem.seek(self.rip)
            mem.write(self.shell_stage_one)
        


        # continue the process
        if stop == "sigstop":
            self.proc.cont()
            pass

        elif stop == "freeze":
            pass
        else:
            pass

        pass
    
    def load_library(self, libname, stop="sigstop"):
        # find ld-.so
        regions = self.find_region_by_name(b"libc-2.31.so")
        if len(regions) == 0:
            print("Failed to find ld-so.")
        
        ld_path = regions[0]["name"]
        ld_base = regions[0]["start"]

        dl_open_offset = utils.lookup_elf_symbol(ld_path, "__libc_dlopen_mode")
        dl_open_addr = ld_base + dl_open_offset

        sys_vals = self.proc.syscalls
        self.rip = sys_vals["rip"]
        self.rsp = sys_vals["rsp"]

        self.construct_shellcode_stage_one()

        # stop the process to get process status
        if stop == "sigstop":
            self.proc.stop()
            pass
        elif stop == "freeze":
            pass

        # backup text & stack status 
        # hihiack rip by /proc/[pid]/mem 
        with open(self.proc._proc_mem, "wb+") as mem:
            mem.seek(self.rip)
            self.code_backup = mem.read(len(self.shell_stage_one))

            mem.seek(self.rsp - self.stack_backup_size)
            self.stack_backup = mem.read(self.stack_backup_size)

            # sencond shellcode:   call dl_open("libpath")
            self.construct_shellcode_stage_two(dl_open=dl_open_addr, lib_name=libname)
            mem.seek(self.rip)
            mem.write(self.shell_stage_one)

        # continue the process
        if stop == "sigstop":
            self.proc.cont()
            pass

        elif stop == "freeze":
            pass
        
        pass
    

    def execute_python_code(self, pycode, stop="sigstop"):
        self.py_so_path = self.find_python_so_to_inject()

        self.load_library(self.py_so_path)

        #wait for /proc/[pid]maps update
        time.sleep(1)
        shellcode = self.generate_python_shellcode(pycode + b"\x00")
        
        self.execute_shellcode(shellcode)
        pass


    def execute_python_file(self, pypath, stop="sigstop"):

        self.py_so_path = self.find_python_so_to_inject()

        self.load_library(self.py_so_path)

        #wait for /proc/[pid]maps update
        time.sleep(1)
        shellcode = self.generate_python_shellcode(pypath + b"\x00")
        
        self.execute_shellcode(shellcode)


        pass