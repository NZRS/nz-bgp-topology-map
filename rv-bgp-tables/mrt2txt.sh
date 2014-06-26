#!/bin/bash

for rib in */rib.*; do
    echo $rib
    /opt/bgpdump/bin/bgpdump -m $rib | cut -d\| -f6,7 >> prefix-aspath.txt
done
