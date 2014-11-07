#!/usr/bin/env python

import json
import csv
import sys

as_rel = {}

def rel_char( src, dst ):
    rv = '?'
    key = "{0}+{1}".format(src, dst)
    key_rev = "{0}+{1}".format(dst, src)
    if as_rel.has_key(key):
        if (as_rel[key] == 0):
            rv = '-'
        elif (as_rel[key] < 0):
            rv = '>'
        elif (as_rel[key] == 1):
            rv = '<'
        else:
            rv = '='
    elif as_rel.has_key(key_rev):
        if (as_rel[key_rev] == 0):
            rv = '-'
        elif (as_rel[key_rev] < 0):
            rv = '<'
        elif (as_rel[key_rev] == 1):
            rv = '>'
        else:
            rv = '='

    return rv

def load_as_relationship(file_list):
    as_rel = {}
    for filename in file_list:
        with open(filename, 'r') as as_rel_file:
            print "Loading AS relationships from {}".format(filename)
            as_rel_csv = csv.reader(filter(lambda row: row[0]!='#',as_rel_file), delimiter="|")
            for as_rel_entry in as_rel_csv:
                [ prov_as, cust_as, rel ] = as_rel_entry
                as_rel["{0}+{1}".format(prov_as,cust_as)] = int(rel)

    return as_rel

# Handle the input files as parameters from the command line
as_rel = load_as_relationship(sys.argv[1:])

# Store the AS Path loaded
as_paths = []

# Store the unique list of ASes seen (to fetch names later)
as_set = set()

for aspath_file in ['data/rv-nz-aspath.json', 'data/nzix.json']:
    print "Loading AS Path data from {}".format(aspath_file)
    with open(aspath_file, 'rb') as rv_file:
        rv_paths = json.load(rv_file)

    for aspath in rv_paths['aspath']:
        if len(aspath) > 1:
            as_links = []
            for i in range(1, len(aspath)):
                rel = rel_char( aspath[i-1], aspath[i])
                as_links.append([ aspath[i-1], rel, aspath[i] ])
                as_set.add(aspath[i-1])
                as_set.add(aspath[i])

            as_paths.append(as_links)

with open('data/nz-as-rels.json', 'wb') as as_rel_file:
    json.dump(dict(aspaths=as_paths), as_rel_file)

with open('data/as-list.txt', 'wb') as as_list_file:
    as_list_file.writelines([ "{0}\n".format(asn) for asn in as_set ])
