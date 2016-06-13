#!/usr/bin/env python2

import bs4
import re


def get_aspath(l):
    aspath = l.split(':')[-1].lstrip().split(' ')
    aspath.insert(0, '64496')

    return aspath

with open('peer.43.243.22.2.html') as f:
    page = bs4.BeautifulSoup(f)

prefixes = []
for p in page.findAll('pre'):
    for l in p.get_text().split("\n"):
        if len(l) > 0 and l[0] == "\t":   # Indented line
            if re.search('BGP.as_path', l):
                print(l)
                prefixes.append((prefix, get_aspath(l)))
        else:
            prefix = l.split(' ')[0]
            print(prefix)

print(prefixes)
