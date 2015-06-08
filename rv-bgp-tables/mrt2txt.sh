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
