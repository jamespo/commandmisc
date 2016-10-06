#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <dirent.h>
#include <string.h>
//#include <fcntl.h>

#define BUFFER_SIZE 1024
#define on_error(...) { fprintf(stderr, __VA_ARGS__); fflush(stderr); }
#define on_fatal(...) { fprintf(stderr, __VA_ARGS__); fflush(stderr); exit(1); }

int main (int argc, char *argv[]) {
  char dir[BUFFER_SIZE];
  if (argc < 2) {
    getcwd(dir, BUFFER_SIZE);
  } else {
    strncpy(dir, argv[1], BUFFER_SIZE);
  }

  DIR *dp;
  struct dirent *ep;

  int numfiles = 0;
  dp = opendir (dir);
  if (dp != NULL)
    {
      while (ep = readdir (dp))
	if (ep->d_type == DT_REG)
	  numfiles++;
      //puts (ep->d_name);
      (void) closedir (dp);
      printf("Files in %s: %d\n", dir, numfiles);
    }
  else
    perror ("Couldn't open the directory");

  return 0;
}
