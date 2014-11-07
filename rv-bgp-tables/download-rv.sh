#!/bin/bash

# curl
# http://archive.routeviews.org/route-views{3,4}/bgpdata/2014.06/RIBS/rib.20140625.0000.bz2
DAY=20141101
for url in `cat sources.txt`; do
    base=$(echo $url | cut -d/ -f4)
    echo $base
    mkdir -p $base
    wget -O - "$url/$(echo $DAY |cut -c1-4).$(echo $DAY|cut -c5-6)/RIBS/rib.$DAY.0000.bz2" > $base/rib.$DAY.0000.bz2
done
