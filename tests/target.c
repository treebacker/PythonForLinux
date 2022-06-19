#include <stdio.h>
#include <unistd.h>


void help()
{
    puts("ssss");
    return;
}
int main()
{
    int pid = getpid();
    printf("target is running with pid: %d\n", pid);

    while(1){
        puts("i am running....");
        sleep(1);
    }

    return 0;
}