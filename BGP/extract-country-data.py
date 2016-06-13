#!/usr/bin/env python

import pandas as pd
from collections import defaultdict
import json


def expand_asn_list(a):
    s = int(a['resource'])
    n = a['size']
    return [a for a in range(s + 1, s + n)]

# Get the delegation data from APNIC
apnic_url = 'http://ftp.apnic.net/stats/apnic/delegated-apnic-latest'
rir = pd.read_csv(apnic_url, delimiter="|", skiprows=31,
                  names=['rir', 'cc', 'resource_type', 'resource', 'size',
                         'created', 'status'],
                  comment="#")


nz_data = rir[rir['cc'] == 'NZ'][['resource_type', 'resource', 'size']]

# The asn resource require some extra processing, as one entry could covert
# multiple ASN
dlist = []
for idx, row in nz_data.query('(resource_type=="asn") & (size>1)').iterrows():
    for n in expand_asn_list(row):
        dlist.append(n)


# Expand the network mask for the prefixes
prefixes = defaultdict(list)
for idx, row in nz_data.query('(resource_type!="asn")').iterrows():
    if row['resource_type'] == 'ipv6':
        mask = row['size']
    elif row['resource_type'] == 'ipv4':
        mask = 32 - (row['size'] - 1).bit_length()

    prefixes[row['resource_type']].append("%s/%s" % (row['resource'], mask))

# Store everything in prefixes
prefixes['asn'] = nz_data.query('resource_type=="asn"')['resource'].tolist() + dlist

with open('nz-resources.json', 'wb') as f:
    json.dump(prefixes, f)

