#include <stdio.h>
#include <stdlib.h>
#include <Python.h>

//gcc exec_python_inter.c -o exec_python_inter -I/usr/include/python2.7 -I/usr/include/x86_64-linux-gnu/python2.7 -lpython2.7 -lpthread -ldl  -lutil -lm


int main(int argc, char** argv)
{
    Py_Initialize();
    Py_Main(argc, argv);
    Py_Finalize();
}