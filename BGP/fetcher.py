#!/usr/bin/env python

from _pybgpstream import BGPStream, BGPRecord, BGPElem
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
import json
import progressbar
from radix import Radix
import pandas as pd

verbose = True


def expand_asn_list(a):
    s = int(a['resource'])
    n = a['size']
    return [a for a in range(s + 1, s + n)]


def get_country_resources(cc='NZ'):
    # Get the delegation data from APNIC
    apnic_url = 'http://ftp.apnic.net/stats/apnic/delegated-apnic-latest'
    rir = pd.read_csv(apnic_url, delimiter="|", skiprows=31,
                      names=['rir', 'cc', 'resource_type', 'resource', 'size',
                             'created', 'status'],
                      comment="#")

    nz_data = rir[rir['cc'] == cc][['resource_type', 'resource', 'size']]

    # The asn resource require some extra processing, as one entry could covert
    # multiple ASN
    dlist = []
    for idx, row in nz_data.query(
            '(resource_type=="asn") & (size>1)').iterrows():
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
    prefixes['asn'] = nz_data.query('resource_type=="asn"')[
                          'resource'].tolist() + dlist

    return prefixes


def prefix_in_country(rt, p):
    p = unicode(p)
    [net, mask] = p.split('/')
    try:
        if rt.search_best(network=net, masklen=int(mask)):
            return True
    except ValueError:
        print "ERR: prefix %s caused exception" % p

    return False


def get_bgp_view():
    nz_data = get_country_resources()

    rt = Radix()
    for pfx in nz_data['ipv4']:
        rt.add(network=pfx)

    # Create a new bgpstream instance and a reusable bgprecord instance
    stream = BGPStream()
    rec = BGPRecord()

    stream.add_filter('collector', 'route-views.sg')
    # stream.add_filter('collector', 'route-views.sydney')
    stream.add_filter('project', 'ris')
    stream.add_filter('project', 'routeviews')

    # Consider RIBs dumps only
    stream.add_filter('record-type', 'ribs')

    # Consider the time interval between 12 hours in the past, +/- 10 minutes
    # now = datetime.utcnow()
    now = datetime(2016, 3, 14, 0, 0)
    epoch = datetime.utcfromtimestamp(0)
    start_t = int((now - timedelta(minutes=10) - epoch).total_seconds())
    end_t = int((now + timedelta(minutes=10) - epoch).total_seconds())
    # start_t = int((now - timedelta(hours=12) - epoch).total_seconds())
    # end_t = int((now - timedelta(hours=10) - epoch).total_seconds())
    print "Time interval %s to %s" % (start_t, end_t)
    stream.add_interval_filter(start_t, end_t)

    # Set up the progress bar
    pbar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

    # Start the stream
    stream.start()

    # The key is going to be a string representing an AS-PATH, and the values a
    # list of prefixes sharing that common AS-PATH
    aspath_set = defaultdict(set)
    prefix_list = {}
    record_cnt = 0

    print("Fetching BGP data")
    # Get next record
    while(stream.get_next_record(rec)):
        elem = rec.get_next_elem()
        while(elem):
            # Get the prefix
            pfx = elem.fields['prefix']

            # Get the list of ASes in the AS path
            aspath = elem.fields['as-path']
            if len(aspath) > 0:
                aspath_set[pfx].add(aspath)

            record_cnt += 1
            if record_cnt % 10000 == 0:
                pbar.update(record_cnt)
            elem = rec.get_next_elem()

    # If the default route is in the list, remove it
    aspath_set.pop('0.0.0.0/0', None)

    print("Searching for covering prefixes")
    path_bar = progressbar.ProgressBar(max_value=len(aspath_set))
    path_cnt = 0
    # Go over the list of prefixes we have deduplicated, it should run faster
    sel_aspath = defaultdict(set)
    for pfx, aspaths in aspath_set.iteritems():
        if path_cnt % 10000 == 0:
            path_bar.update(path_cnt)
        path_cnt += 1
        for aspath in aspaths:
            origin = aspath.split(' ')[-1]
            # Test if the origin AS is from the country we are interested on
            if origin in nz_data['asn']:
                netmask = int(pfx.split('/')[-1])
                if netmask <= 24:
                    sel_aspath[aspath].add(pfx)
                else:
                    pass
            else:   # If not, test if the prefix corresponds to the country
                if prefix_in_country(rt, pfx):
                    sel_aspath[aspath].add(pfx)

    path_bar.update(path_cnt)

    return [dict(prefixes=list(prefixes), path=path.split(' ')) for path, prefixes in sel_aspath.iteritems()]


if __name__ == "__main__":
    for p in get_bgp_view():
        print(p)
