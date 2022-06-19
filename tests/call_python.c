#include <stdio.h>
#include <stdlib.h>
#include <Python.h>

//gcc call_python.c -o call_python $(python2-config --includes --ldflags)
void exec_python_code(const char* py_code)
{
    Py_Initialize();
    PyRun_SimpleString(py_code);
    Py_Finalize();
}

int main()
{
    exec_python_code("print('i am from python')");
}