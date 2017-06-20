#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>

#include <asm/types.h>
#include <linux/types.h>

#define PFX "dcc-scalefactor: "


void usage(void )
{
	 fprintf (stderr, "\n");

     fprintf (stderr, "\n");
     fprintf (stderr, "Usage: "PFX" [options]\n");
     fprintf (stderr, "\n");
     fprintf (stderr, "Options:\n");
     fprintf (stderr, "  -h	--help	,Show help\n");
     fprintf (stderr, "  -a	--wsrc	,source width\n");
     fprintf (stderr, "  -b	--wdst	,destination width\n");
     fprintf (stderr, "  -c	--hsrc	,source height\n");
     fprintf (stderr, "  -d	--hdst	,destination height\n");

	 fprintf (stderr, "\n");
     fprintf (stderr, "Examples:\n");
     fprintf (stderr, "  ./dcc-scalefactor --wsrc 120 --wdst 240 --hsrc 159 --hdst 320\n");
}



unsigned int scaling_factor_float(unsigned short src_size, unsigned short dst_size) {
	unsigned int scalingFactor;
	if ((dst_size>src_size) || (src_size%dst_size)){
		scalingFactor = (unsigned short)((((float)(src_size-1))/((float)(dst_size)))* (1<<12));

		if (!(scalingFactor & 0xfff)) scalingFactor++;
		if(scalingFactor >= (16 << 12)){
			return 0;
		}
	}else{ //fast method to calculate the scaling factor (for details see the specification...)
		scalingFactor = ((unsigned short)(src_size/dst_size)<<12)+1;
	}

	return scalingFactor;
}


unsigned int scaling_factor_int(unsigned int src_size, unsigned int dst_size) {
	unsigned int scalingFactor = 0;

	if ((dst_size>src_size) || (src_size%dst_size)){
		scalingFactor = (unsigned short)( ((src_size-1)<<12) /dst_size)+1;

		if (!(scalingFactor & 0xfff))
			scalingFactor++;

		if(scalingFactor >= (16 << 12)){
			return 0;
		}
	}else{ //fast method to calculate the scaling factor (for details see the specification...)
		scalingFactor = ((unsigned short)((src_size<<12)/(dst_size)));
	}

//	if((src_size%dst_size!=0)&&(src_size<dst_size))
//		scalingFactor++;

	return scalingFactor;
}


unsigned int scaling_factor_int2(unsigned int src_size, unsigned int dst_size) {
	unsigned int scalingFactor = 0;

	if (src_size%dst_size==0){
		scalingFactor = (unsigned short)( (src_size<<12) /dst_size);

		//if (!(scalingFactor & 0xfff))
		//	scalingFactor++;

	}else{ //fast method to calculate the scaling factor (for details see the specification...)
		scalingFactor = ((unsigned short)(((src_size-1)<<12)/(dst_size))+1);
	}

	return scalingFactor;
}


int main (int argc, char **argv)
{
	int fd;
	int c;
	int digit_optind = 0;
	int sw = 0;
	int sh = 0;
	int dw = 0;
	int dh = 0;

	while (1) {
		int this_option_optind = optind ? optind : 1;
		int option_index = 0;
		static struct option long_options[] = {
			{"help"		, 0, 0, 'h'},
			{"wsrc"		, 1, 0, 'a'},
			{"wdst"		, 1, 0, 'b'},
			{"hsrc"		, 1, 0, 'c'},
			{"hdst"		, 1, 0, 'd'},
			{0, 0, 0, 0}
		};

		c = getopt_long (argc, argv, "ha:b:c:d:",
				long_options, &option_index);
		if (c == -1)
			break;

		switch (c) {

		case 'h':
			usage();
			return 0;
			break;
			
		case 'a':
			sscanf(optarg, "%d",&sw);
			break;
			
		case 'b':
			sscanf(optarg, "%d",&dw);
			break;
			
		case 'c':
			sscanf(optarg, "%d",&sh);
			break;
			
		case 'd':
			sscanf(optarg, "%d",&dh);
			break;
	
		default:
			printf ("?? getopt returned character code 0%o ??\n", c);
		}
	}

	if (optind < argc) {
		printf ("non-option ARGV-elements: ");
		while (optind < argc)
			printf ("%s ", argv[optind++]);
		printf ("\n");
	}

	if(!sw || !dw || !sh || !dh){
		usage();
		return 0;
	}

	unsigned int scalex = scaling_factor_float((unsigned short)sw, (unsigned short)dw);
	unsigned int scaley = scaling_factor_float(sh, dh);
	fprintf(stderr,PFX"Float algorithm :\n");
	fprintf(stderr,PFX"width : %d --> %d \tscalex=0x%04x\n",sw,dw,scalex);
	fprintf(stderr,PFX"height: %d --> %d \tscaley=0x%04x\n",sh,dh,scaley);

	scalex = scaling_factor_int2(sw, dw);
	scaley = scaling_factor_int2(sh, dh);

	fprintf(stderr,PFX"Integer algorithm :\n");
	fprintf(stderr,PFX"width : %d --> %d \tscalex=0x%04x\n",sw,dw,scalex);
	fprintf(stderr,PFX"height: %d --> %d \tscaley=0x%04x\n",sh,dh,scaley);
  
	return 0;
}

