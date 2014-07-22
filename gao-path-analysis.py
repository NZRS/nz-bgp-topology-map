#!/usr/bin/env python

import json
import csv

as_rel = {}

def rel_char( src, dst ):
    rv = '?'
    key = "{0}+{1}".format(src, dst)
    key_rev = "{0}+{1}".format(dst, src)
    if as_rel.has_key(key):
        rv = '-' if (as_rel[key] == 0) else '>'
    elif as_rel.has_key(key_rev):
        rv = '-' if (as_rel[key_rev] == 0) else '<'

    return rv

with open('data/rv-nz-aspath.json', 'rb') as rv_file:
    rv_paths = json.load(rv_file)

with open('as-rank/20140601.as-rel.txt', 'rb') as as_rel_file:
    as_rel_csv = csv.reader(filter(lambda row: row[0]!='#',as_rel_file), delimiter="|")
    for as_rel_entry in as_rel_csv:
        [ prov_as, cust_as, rel ] = as_rel_entry
        as_rel["{0}+{1}".format(prov_as,cust_as)] = int(rel)


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
#            print " ".join(deltas)
            pass
        else:
            print "WTF with {}".format(aspath)

with open('unknown-rel.csv', 'w') as unk_rel_file:
    unk_out = csv.writer(unk_rel_file, lineterminator="\n")

    for unk in set(unknown):
        unk_out.writerow([unk])

