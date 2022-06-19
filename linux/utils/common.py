import imp
import sys
import subprocess
from tarfile import ENCODING

from traitlets import Instance
from elftools.elf.elffile import ELFFile, SymbolTableSection

FILE_READ_BUFFER_SIZE = 32 * 1024
_DEFAULT = object()

def open_binary(fname):
    return open(fname, 'rb', buffering=FILE_READ_BUFFER_SIZE)


def open_text(fname):
    return open(fname, 'rt', buffering=FILE_READ_BUFFER_SIZE,
        encoding=ENCODING)

def cat(fname, fallback=_DEFAULT, _open=open_text):
    if fallback is _DEFAULT:
        with _open(fname) as f:
            return f.read()
    else:
        try:
            with _open(fname) as  f:
                return f.read()
        except:
            return fallback

def bcat(fname, fallback=_DEFAULT):
    return cat(fname, fallback=fallback, _open=open_binary)


def write(fname, _open=open_binary):
    pass

def bwrite(fname, content):
    with open(fname, 'wb') as f:
        f.write(content)

def get_procfs_path():
    return "/proc"
    #return sys.modules["PythonForLinux"].linux.PROCFS_PATH

def get_sysmod_path():
    return "/sys/module"
    

def lookup_elf_symbol(path, sym_name):
    with open(path, "rb") as f:
        elf = ELFFile(f)


        for section in elf.iter_sections():
            if not isinstance(section, SymbolTableSection):
                continue
            for sym in section.iter_symbols():
                if sym_name == sym.name:
                    return sym.entry.st_value

        return None


def compile_asm(source, out_path):
    cmd = "gcc -x assembler - -o {} -nostdlib -Wl,--oformat=binary -m64".format(out_path)
    argv =  cmd.split(" ")
    prefix = b".intel_syntax noprefix\n.globl _start\n_start:\n"

    program = prefix + source.encode()
    pipe = subprocess.PIPE
    
    result = subprocess.run(argv, stderr=pipe, input=program)

    if result.returncode != 0:
        emsg = result.stderr.decode().strip()
        print("compile asm failed: {}".format(emsg))
        return False

    return True