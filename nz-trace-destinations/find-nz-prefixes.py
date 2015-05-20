#!/usr/bin/python

import csv
from collections import OrderedDict, defaultdict
import json
import ipaddress

verbose = True

def is_nz_network(p):
    overlaps = False
    num_slash_24 = 0
    try:
        net_p = ipaddress.ip_network(p)
        num_slash_24 = int(net_p.num_addresses/256)
        for prefix in nz_registered_prefix_list:
            overlaps = prefix.overlaps(net_p)
            if overlaps:
                break
    except ValueError:
        print "ERR: prefix caused exception", p

    return dict(is_nz=overlaps, count24=num_slash_24)


def is_nz_as(asn):
    return asn in nz_as_list

""" Read the list of NZ prefixes from the data obtained from APNIC"""
nz_registered_prefix_list = []

with open("../data/nz-networks-from-rir.tsv", "rb") as rir_data:
    nz_networks = csv.reader(rir_data, delimiter='\t')

    for net in nz_networks:
        nz_registered_prefix_list.append(ipaddress.ip_network(net[0]))

print "{} NZ prefixes found".format(len(nz_registered_prefix_list))

""" Read the list of NZ ASes from the data obtained from APNIC"""
nz_as_list = set()

with open('../data/as-from-rir.tsv', 'rb') as nz_as:
    as_in = csv.reader(nz_as, delimiter='\t')

    for asn in as_in:
        nz_as_list.add(asn[0])


aspath_set = defaultdict(list)
prefix_list = dict()
line_cnt = 0

with open('../data/prefix-aspath.txt', 'rb') as aspath_file:
    aspath_list = csv.reader(aspath_file, delimiter='|')

    for aspath in aspath_list:

        # Special case to filter out some prefixes we don't want to see.
        if aspath[0] == "0.0.0.0/0":
            print "ERROR: Skipping default route"
            continue
        if line_cnt % 100000 == 0:
            print "{} paths processed".format(line_cnt)
        # Test if the origin AS is from NZ
        origin = aspath[1].split(' ')[-1]
        if is_nz_as(origin):
            netmask = int(aspath[0].split('/')[-1])
            if netmask <= 24:
                aspath_set[aspath[1]].append(aspath[0])
            else:
                print "ERROR: Skipping prefix {} with mask smaller to 24".format(aspath[0])
        else:   # If not, test if the prefix corresponds to NZ
            status = prefix_list.get(aspath[0], None)
            if status == None:  # The entry doesnt exist
                prefix_list[aspath[0]] = is_nz_network(aspath[0])
            elif status['is_nz']:  # The entry exists and it's from NZ
                aspath_set[aspath[1]].append(aspath[0])
        line_cnt += 1

nz_aspath = []
for aspath, prefixes in aspath_set.iteritems():
    nz_aspath.append(dict(path=list(OrderedDict.fromkeys(aspath.split(' '))), prefixes=prefixes))

with open('../data/rv-nz-aspath.json', 'wb') as nz_aspath_file:
    json.dump(dict(aspath=nz_aspath), nz_aspath_file)


