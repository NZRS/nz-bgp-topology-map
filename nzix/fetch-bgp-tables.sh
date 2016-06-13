#!/bin/bash

if [ $# != 1 ]; then
    echo "Usage: $0 routeserver"
    exit 1
fi

# XXX: Validate if the name makes sense
ROUTESERVER=$1

echo "Fetching from routeserver $ROUTESERVER"

links -dump "http://nzix.net/cgi-bin/lg.cgi?query=bgp&protocol=IPv4&router=${ROUTESERVER}&addr=regexp%20^" > ${ROUTESERVER}.txt 

