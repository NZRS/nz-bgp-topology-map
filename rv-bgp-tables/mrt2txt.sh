#!/bin/bash

OFILE="data/prefix-aspath.txt"
TMPFILE="${OFILE%.txt}.tmp"
rm -f $TMPFILE
for rib in $*; do
    echo $rib
    /usr/local/bin/bgpdump -m $rib | cut -d\| -f6,7 >> $TMPFILE
done
if [ ! -z "$TMPFILE" ]; then
    mv "$TMPFILE" "$OFILE"
else
    echo "Script produced empty file, something went wrong"
    exit 1
fi
