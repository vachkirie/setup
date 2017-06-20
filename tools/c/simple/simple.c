#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>

#include <asm/types.h>
#include <linux/types.h>

int main (int argc, char **argv)
{
	int sw = 0;

	while((sw++)<1000){}

	printf("sw=%d\n", sw);
	return 0;
}

