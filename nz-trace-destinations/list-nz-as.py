#!/usr/bin/env python

import csv

# apnic|JP|asn|173|1|20020801|allocated

as_list = {}
with open('delegated-apnic-latest', 'rb') as csvfile:
    csvin = csv.reader(csvfile, delimiter='|')

    for row in csvin:
        if row[-1] == 'allocated' and row[1] == 'NZ' and row[2] == 'asn':
            as_list[ row[3] ] = True

prefix_list = []

with open('prefix2AS-20140527.txt', 'rb') as tsvfile:
    tsvin = csv.reader(tsvfile, delimiter='\t')

    for prefix in tsvin:
        if as_list.has_key( prefix[1] ):
            prefix_list += [ prefix ]

with open('nz-networks.tsv', 'wb') as tsvfile:
    tsvout = csv.writer(tsvfile, delimiter='\t')

    tsvout.writerows(prefix_list)
