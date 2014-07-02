#!/usr/bin/env python

import csv
from collections import OrderedDict
import json


as_list = {}

with open('../data/as-from-rir.tsv', 'rb') as nz_as:
    as_in = csv.reader(nz_as, delimiter='\t')

    for asn in as_in:
        as_list[asn[0]] = True

aspath_set = set()
with open('../data/prefix-aspath.txt', 'rb') as aspath_file:
    aspath_list = csv.reader(aspath_file, delimiter='|')

    for aspath in aspath_list:
        origin = aspath[1].split(' ')[-1]
        if as_list.has_key(origin):
            aspath_set.add(aspath[1])

nz_aspath = []
for aspath in aspath_set:
    nz_aspath.append( list(OrderedDict.fromkeys(aspath.split(' '))))

with open('../data/rv-nz-aspath.json', 'wb') as nz_aspath_file:
    json.dump(dict(aspath=nz_aspath), nz_aspath_file)


