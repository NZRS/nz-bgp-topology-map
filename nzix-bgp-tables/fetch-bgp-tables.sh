#!/bin/bash

#    This file is part of 'NZ BGP Topology Map'.
#
#    'NZ BGP Topology Map' is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    'NZ BGP Topology Map' is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public
#    License along with 'NZ BGP Topology Map'.  If not, see
#    <http://www.gnu.org/licenses/>.

if [ $# != 1 ]; then
    echo "Usage: $0 routeserver"
    exit 1
fi

# XXX: Validate if the name makes sense
ROUTESERVER=$1

echo "Fetching from routeserver $ROUTESERVER"

links -dump "http://nzix.net/cgi-bin/lg.cgi?query=bgp&protocol=IPv4&router=${ROUTESERVER}&addr=regexp%20^" > ${ROUTESERVER}.txt 

