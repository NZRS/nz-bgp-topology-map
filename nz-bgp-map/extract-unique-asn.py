#!/usr/bin/env python

import json

# We have two input files, the NZIX AS Paths and the RouteViews AS
# Paths. Need to extract the unique ASes on those paths, to get their
# names for the final output

as_set = set()

with open('../data/nzix.json', 'rb') as ixfile:
    nzix_paths = json.load(ixfile)

    for router_entry in nzix_paths:
        for prefix in router_entry['prefixes']:
            for asn in prefix['aspath']:
                as_set.add(asn)

with open('../data/rv-nz-aspath.json', 'rb') as rv_file:
    rv_paths = json.load(rv_file)

    for aspath in rv_paths['aspath']:
        for asn in aspath:
            as_set.add(asn)

with open('../data/as-list.txt', 'wb') as as_list_file:
    as_list_file.writelines([ "{0}\n".format(asn) for asn in as_set ])

