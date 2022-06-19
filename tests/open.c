
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>


int main()
{
    void *handle;
    handle = dlopen("lib.so", RTLD_LAZY);
        if (!handle) {
            fprintf(stderr, "%s\n", dlerror());
            exit(EXIT_FAILURE);
        }

    dlclose(handle);
}