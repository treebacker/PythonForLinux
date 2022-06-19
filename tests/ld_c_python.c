#include <stdio.h>
#include <dlfcn.h>
#include <Python.h>

// gcc ld_c_python.c -g -o ld_c_python $(python3-config --includes --embed --ldflags)

void exec_python_code(const char* py_code)
{
    Py_Initialize();
    PyRun_SimpleString(py_code);
    Py_Finalize();
    return ;
}

typedef void* (*arbitrary_function)();

void exec_so_python_code(const char* py_code)
{
    arbitrary_function atr_func;
    void* addr;
    void* handle = dlopen("/lib/x86_64-linux-gnu/libpython3.8.so.1.0", RTLD_NOW);

    addr = dlsym(handle, "Py_Initialize");
    *(void**)(&atr_func) = addr;
    printf("addr: %p\n", addr);
    atr_func();

    addr = dlsym(handle, "PyRun_SimpleString");
    *(void**)(&atr_func) = addr;
    atr_func(py_code);

    addr = dlsym(handle, "Py_Finalize");
    *(void**)(&atr_func) = addr;
    atr_func();

}

int main()
{
    exec_python_code("print('i am from python code.')");
    //exec_so_python_code("print('i am from python code.')");

    return 0;
}