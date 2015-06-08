#!/usr/bin/env python

import re
from collections import OrderedDict, defaultdict, Counter
import json
import sys
from IPy import IP
# shamelessly stolen from
# http://stackoverflow.com/questions/4914008/efficient-way-of-parsing-fixed-width-files-in-python
from itertools import izip_longest  # added in Py 2.6

try:
    from itertools import accumulate  # added in Py 3.2
except ImportError:
    def accumulate(iterable):
        """Return running totals (simplified version)."""
        total = next(iterable)
        yield total
        for value in iterable:
            total += value
            yield total


def make_parser(fieldwidths):
    cuts = tuple(cut for cut in accumulate(abs(fw) for fw in fieldwidths))
    pads = tuple(fw < 0 for fw in fieldwidths) # bool values for padding fields
    flds = tuple(izip_longest(pads, (0,)+cuts, cuts))[:-1]  # ignore final one
    parse = lambda line: tuple(line[i:j] for pad, i, j in flds if not pad)
    # optional informational function attributes
    parse.size = sum(abs(fw) for fw in fieldwidths)
    parse.fmtstring = ' '.join('{}{}'.format(abs(fw), 'x' if fw < 0 else 's')
                                                for fw in fieldwidths)
    return parse

def asdot2asplain(aslist=[]):
    rv = []
    # Some of the ASes are 32-bit and represented in adot
    # format (RFC5396). Converting to asplain
    for asn in aslist:
        if re.search('\.', asn):
            [high_bits, low_bits] = asn.split('.')
            rv.append(str((int(high_bits) << 16) + int(low_bits)))
        else:
            rv.append(asn)

    return rv


def prepare_route(prefix, ix_as, aspath_str):
    # This removes the AS-Path prepending
    aspath = list(OrderedDict.fromkeys(asdot2asplain(aspath_str.rstrip().split(' '))))
    # Remove the last element, it's the status of the prefix
    aspath.pop()
    # The origin AS (last in the list) could be actually a Multi-AS Origin that doesn't help us much.
    # If that's the case, we'll use the following value
    try:
        int(aspath[-1])
    except ValueError:
        # The origin AS is not a number, remove it from the list
        aspath.pop()

    # Append the ix_as to the beginning of the aspath
    aspath.insert(0, ix_as)
    if re.search('/', prefix) == None:
        prefix = "{0}/24".format(prefix)
#                print "{0} -> {1} : {2}".format(prefix, router, aspath)
    for asn in aspath:
        if asn in path_count:
            path_count[asn] += 1
        else:
            path_count[asn] = 0

    return dict(prefix=prefix, aspath=" ".join(aspath))

def relevant_as(prefix):
    try:
        asn_score = max([path_count[asn] for asn in prefix['aspath']])
    except ValueError:
        print "ERROR: AS Path produced invalid score {0}".format(prefix)
        asn_score = 0

    return asn_score



fieldwidths = (3, 3, 17, 17, 24, 80)
parse = make_parser(fieldwidths)
path_count = Counter()

# Read the file with IX info
with open('../data/ix-info.json', 'rb') as ix_info_file:
    ix_info = json.load(ix_info_file)

    ix_name2as = {}
    for k in ix_info.keys():
        ix_name2as[ix_info[k]['name']] = k

aspath_set = defaultdict(list)
for ixfile in sys.argv[1:]:
    with open(ixfile) as bgpdata:

        rs = ''
        prefixes = []
        ix_name = ''
        ix_as = 0

        for line in bgpdata:
            res = re.match('\s+Router: (\S*)', line)
            if res != None:
                rs = res.group(1)
                # The routeserver looks like rs1.ape.nzix.net, extract the
                # meaningful label to map to the corresponding AS number
                ix_name = rs.split('.')[1].upper()
                ix_as = ix_name2as[ix_name]

            fields = parse(line)
            if len(fields[1]) > 0 and fields[1][0] == '*':
                prefix = fields[2].rstrip()
                if len(prefix) == 0:
                    prefix = prefixes[-1]['prefix']
                router = fields[3].rstrip()
                # This line only contains the prefix, the rest of the
                # route info is in the next line
                if len(router) < 7:
                    # There is something wrong with the line
                    prev_prefix = prefix + router
                else:
                    prev_prefix = None

                    route = prepare_route(prefix, ix_as, fields[5])
                    prefixes.append(route)
            else:
                try:
                    # The field 3 is an IP address
                    IP(fields[3])
#                    print "Mark -> {0} learnt from {1}".format(prev_prefix, fields[3])
                    route = prepare_route(prev_prefix, ix_as, fields[5])
                    prefixes.append(route)
                except ValueError:
                    # Not interested on this line
                    pass

        for p in prefixes:
            aspath_set[p['aspath']].append(p['prefix'])

with open('../data/nzix.json', 'wb') as ixfile:
    json.dump(dict(aspath=[dict(prefixes=prefixes, path=path.split(' ')) for path, prefixes in aspath_set.iteritems()]), ixfile)

