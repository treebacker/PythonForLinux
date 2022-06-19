#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <Python.h>

//gcc exec_python_file.c -g -o exec_python_file $(python3-config --includes --embed --ldflags)

void exec_python_code(const char* py_code)
{
    PyGILState_STATE gstate;
    if(!Py_IsInitialized()){
        Py_Initialize();
    }
    PyEval_InitThreads();
    gstate = PyGILState_Ensure();
    PyRun_SimpleString(py_code);
    PyGILState_Release(gstate);
    PyEval_SaveThread();
}

void exec_python_file(const char* fname)
{

    PyGILState_STATE gstate;
    FILE* fp;
    if(!Py_IsInitialized()){
        Py_Initialize();
    }
    PyEval_InitThreads();
    gstate = PyGILState_Ensure();

    fp = _Py_fopen(fname, "r");
    PyRun_AnyFile(fp, fname);

    PyGILState_Release(gstate);
    PyEval_SaveThread();

    return;
}

int main(int argc, char** argv)
{
    exec_python_file(argv[1]);
}