#!/usr/bin/env python

import json
import csv

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
        else:
            rv = '<'
    elif as_rel.has_key(key_rev):
        if (as_rel[key_rev] == 0):
            rv = '-'
        elif (as_rel[key_rev] < 0):
            rv = '<'
        else:
            rv = '>'

    return rv

def load_as_relationship(file_list):
    as_rel = {}
    for filename in file_list:
        with open(filename, 'r') as as_rel_file:
            as_rel_csv = csv.reader(filter(lambda row: row[0]!='#',as_rel_file), delimiter="|")
            for as_rel_entry in as_rel_csv:
                [ prov_as, cust_as, rel ] = as_rel_entry
                as_rel["{0}+{1}".format(prov_as,cust_as)] = int(rel)

    return as_rel

with open('data/rv-nz-aspath.json', 'rb') as rv_file:
    rv_paths = json.load(rv_file)

as_rel = load_as_relationship(['as-rank/20140601.as-rel.txt', 'data/local-as-rel-info.csv'])

# print "{} {} {}".format('9500', rel_char('9500', '9901'), '9901')

unknown = []
for aspath in rv_paths['aspath']:
    if len(aspath) > 1:
        deltas = [ aspath[0] ]
        for i in range(1, len(aspath)):
            rel = rel_char( aspath[i-1], aspath[i])
            deltas.append( rel )
            deltas.append(aspath[i])
            if rel == '?':
                unknown.append( "|".join([aspath[i-1], aspath[i], rel]))
        if (len(deltas) > 0):
            print " ".join(deltas)
            pass
        else:
            print "Unexpected result at {}".format(aspath)

with open('unknown-rel.csv', 'w') as unk_rel_file:
    unk_out = csv.writer(unk_rel_file, lineterminator="\n")

    for unk in set(unknown):
        unk_out.writerow([unk])

