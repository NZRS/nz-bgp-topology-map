#!/usr/bin/env python

import re
from collections import OrderedDict
import json
import sys

# shamelessly stolen from
# http://stackoverflow.com/questions/4914008/efficient-way-of-parsing-fixed-width-files-in-python

try:
    from itertools import izip_longest  # added in Py 2.6
except ImportError:
    from itertools import zip_longest as izip_longest  # name change in Py 3.x

try:
    from itertools import accumulate  # added in Py 3.2
except ImportError:
    def accumulate(iterable):
        'Return running totals (simplified version).'
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

fieldwidths = (3, 3, 17, 17, 24, 80)
parse = make_parser(fieldwidths)
ixviews = []

for ixfile in sys.argv[1:]:
    with open(ixfile) as bgpdata:

        rs = ''
        prefixes = []

        for line in bgpdata:
            res = re.match('\s+Router: (\S*)', line)
            if res != None:
                rs = res.group(1)
            fields = parse(line)
            if len(fields[1]) > 0 and fields[1][0] == '*':
                prefix = fields[2].rstrip()
                router = fields[3].rstrip()
                aspath = list(OrderedDict.fromkeys(fields[5].rstrip().split(' ')))
                # Remove the last element, it's the status of the prefix
                aspath.pop
                if re.search('/', prefix) == None:
                    prefix = "{0}/24".format(prefix)
                print "{0} -> {1} : {2}".format(prefix, router, aspath)
                prefixes.append( dict(prefix=prefix, router=router, aspath=aspath))

        ixviews.append( dict(routeserver=rs, prefixes=prefixes))

with open('nzix.json', 'wb') as ixfile:
    json.dump(ixviews, ixfile)
