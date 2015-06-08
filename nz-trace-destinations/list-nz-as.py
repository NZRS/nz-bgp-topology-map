#!/usr/bin/env python

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

import csv

# apnic|JP|asn|173|1|20020801|allocated

as_country = set()
as_country.add('NZ')
as_list = {}
prefix_list = {}
with open('delegated-apnic-latest', 'rb') as csvfile:
    csvin = csv.reader(csvfile, delimiter='|')

    for row in csvin:
        if row[-1] == 'allocated':
            if row[2] == 'asn' and row[1] in as_country:
                as_list[ row[3] ] = row[1]
            if row[2] == 'ipv4' and row[1] == 'NZ':
                prefix = row[3]
                mask = 32 - (int(row[4]) - 1).bit_length()
                prefix = "{0}/{1}".format(row[3], mask)
                prefix_list[ prefix ] = True


with open('../data/as-from-rir.tsv', 'wb') as tsvfile:
    tsvout = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')

    for asn in as_list.iteritems():
        tsvout.writerow(asn)

with open('../data/nz-networks-from-rir.tsv', 'wb') as tsvfile:
    tsvout = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')

    for p in prefix_list.keys():
        tsvout.writerow([p])

