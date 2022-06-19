#include <unistd.h>
#include <stdlib.h>
#include <string.h>
 
static void __attribute__ ((constructor)) \
  lib_init(void);
 
static void lib_init(void) {
 
  printf("Library ready. \n");
 
  return;
}