#!/bin/bash

for rib in $*; do
    echo $rib
    /opt/bgpdump/bin/bgpdump -m $rib | cut -d\| -f6,7 >> data/prefix-aspath.txt
done
