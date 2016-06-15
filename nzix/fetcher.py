#!/usr/bin/env python

import bs4
import re
from collections import OrderedDict, defaultdict
import json
import requests
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


def asdot2asplain(aslist):
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
    # Append the ix_as to the beginning of the aspath
    aspath.insert(0, ix_as)
    if re.search('/', prefix) is None:
        prefix = "{0}/24".format(prefix)
#                print "{0} -> {1} : {2}".format(prefix, router, aspath)
#     for asn in aspath:
#         if asn in path_count:
#             path_count[asn] += 1
#         else:
#             path_count[asn] = 0

    return dict(prefix=prefix, aspath=" ".join(aspath))


def relevant_as(prefix):
    try:
        asn_score = max([path_count[asn] for asn in prefix['aspath']])
    except ValueError:
        print "ERROR: AS Path produced invalid score {0}".format(prefix)
        asn_score = 0

    return asn_score


def get_ix_as(name, ix_data):
    for ix_num, ix_info in ix_data.iteritems():
        if ix_info['name'].lower() == name:
            return ix_num

    return "0"


def path_elems(p):
    pe = []
    for e in p.split(' '):
        # When there are AS-Maps, the element will look like {<ASN>}.
        m = re.search('^\D*(\d+)\D*$', e)
        if m:
            pe.append(m.group(1))

    return pe


def get_ix_view():
    fieldwidths = (3, 17, 17, 24, 80)
    parse = make_parser(fieldwidths)
    path_count = {}

    aspath_set = defaultdict(set)

    # Read the existing information about IXs we have
    with open('conf/ix-info.json') as f:
        ix_data = json.load(f)

    # Collect data from the NZIX route servers
    RS_LIST = ['wix', 'chix', 'hix', 'dpe', 'ape']
    # RS_LIST = ['wix', 'chix']

    for rs_location in RS_LIST:
        for rs_server in range(1, 3):
            rs_name = "rs%s.%s.nzix.net" % (rs_server, rs_location)
            print(rs_name)

            r = requests.get('http://nzix.net/cgi-bin/lg.cgi',
                             params={'query': 'bgp', 'protocol': 'IPv4',
                                     'router': rs_name, 'addr': 'regexp ^'})

            soup = bs4.BeautifulSoup(r.content, "html.parser")

            for p in soup.find_all('pre'):
                prefixes = []
                ix_as = get_ix_as(rs_location, ix_data)
                print("IX ASN: %s" % ix_as)
                prev_prefix = None

                for line in p.get_text().split("\n"):
                    fields = parse(line)
                    if len(fields[0]) > 0 and fields[0][0] == '*':
                        prefix = fields[1].rstrip()
                        if len(prefix) == 0:
                            prefix = prefixes[-1]['prefix']
                        router = fields[2].rstrip()
                        # This line only contains the prefix, the rest of the
                        # route info is in the next line
                        if len(router) < 7:
                            # There is something wrong with the line
                            prev_prefix = prefix + router
                        else:
                            prev_prefix = None
                            route = prepare_route(prefix, ix_as, fields[4])
                            prefixes.append(route)
                    else:
                        try:
                            # The field 3 is an IP address
                            IP(fields[3])
                            route = prepare_route(prev_prefix, ix_as, fields[4])
                            prefixes.append(route)
                        except ValueError:
                            # Not interested on this line
                            pass

                for p in prefixes:
                    aspath_set[p['aspath']].add(p['prefix'])

    return [{'prefixes': list(prefixes), 'path': path_elems(path)}
            for path, prefixes in aspath_set.iteritems()]


if __name__ == "__main__":
    for p in get_ix_view():
        print(p)
