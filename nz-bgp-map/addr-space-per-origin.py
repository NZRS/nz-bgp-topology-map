__author__ = 'secastro'

"""
From the list of prefixes detected from RouteViews, calculates the number of /24 announced per origin AS.
We use that number as signal of AS importance
"""

import json
from collections import defaultdict
from IPy import IP, IPSet
import csv

def calculate_ipset_weight(s):
    w = 0
    for ip in s:
        w += 2 ** (24-ip.prefixlen())

    return w

with open("../data/rv-nz-aspath.json", "rb") as rv_file:
    route_data = json.load(rv_file)

addr_space = defaultdict(set)
for aspath in route_data['aspath']:
    origin = aspath['path'][-1]
    print origin
    for p in aspath['prefixes']:
        addr_space[origin].add(p)

# Collate all prefixes
aggr_space = dict()
origin_weight = dict()
for origin in addr_space:
    ipset = IPSet([IP(p) for p in addr_space[origin]])
    aggr_space[origin] = [ip.strNormal() for ip in ipset]
    origin_weight[origin] = calculate_ipset_weight(ipset)

with open('../data/address-space-per-origin.json', 'wb') as addr_space_file:
    json.dump(aggr_space, addr_space_file)

with open("../data/relevant-origin.csv", 'wb') as origin_file:
    fp = csv.writer(origin_file, delimiter="\t")

    for o, w in origin_weight.iteritems():
        fp.writerow((o,w))
