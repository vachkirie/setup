 #!/bin/sh
 exec /bin/nc.openbsd -x proxy-mu.intel.com:1080 -X5 "$1" "$2"
