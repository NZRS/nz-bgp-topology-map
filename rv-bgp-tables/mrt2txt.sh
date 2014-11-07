#!/bin/bash

OFILE="data/prefix-aspath.txt"
rm -f $OFILE
for rib in $*; do
    echo $rib
    /usr/local/bin/bgpdump -m $rib | cut -d\| -f6,7 >> $OFILE
done
