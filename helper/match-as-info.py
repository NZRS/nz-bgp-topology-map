#!/usr/bin/env python

import csv
import json

def disp_as(asn):
    if as_info.has_key(asn):
        trans_ref = as_trans.get(asn)
        if trans_ref == None:
            trans_info = [ '-', '-' ]
        else:
            trans_info = [ as_trans[asn]['t'], as_trans[asn]['g'] ]
        info = "{} [{}](t: {} g: {})".format(
                    as_info[asn]['short_descr'], asn, trans_info[0],
                    trans_info[1])
    else:
        info = asn

    return info

# Load the short names for the ASes
with open('data/as-info.json', 'rb') as as_info_file:
    as_info = json.load(as_info_file)

# Load transit degrees
# with open('as-rank/as-transit-degree.json', 'r') as as_trans_file:
#     as_trans = json.load(as_trans_file)
as_trans = {}
with open('as-rank/20140601.degrees.txt', 'r') as as_trans_file:
    as_trans_data = csv.reader(filter(lambda row: row[0]!='#',as_trans_file), delimiter=" ")
    for asn, transit_deg, global_deg in as_trans_data:
        as_trans[asn] = dict(t=transit_deg, g=global_deg)

 
with open('local-as-rel-info.csv', 'rb') as rel_file:
    rel_info = csv.reader(rel_file, delimiter="|")

    for src,dst,rel in rel_info:
        if rel != '?':
            continue
        print "{0} -> {1}".format(disp_as(src), disp_as(dst))
