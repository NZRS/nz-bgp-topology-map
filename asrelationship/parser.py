#!/usr/bin/env python

#    This file is part of 'NZ BGP Topology Map'.
#
#    'NZ BGP Topology Map' is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    'NZ BGP Topology Map' is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public
#    License along with 'NZ BGP Topology Map'.  If not, see
#    <http://www.gnu.org/licenses/>.

import re


class AsRelationship:
    as_rel = {}
    tier1 = []
    _rel2class = {'-': 'p2p',
                  '>': 'p2c',
                  '<': 'c2p',
                  '=': 's2s',
                  '?': 'unk'}

    _class2color = {'p2p': {'color': 'rgba(255,165,0,0.3)',
                            'highlight': 'rgba(255,165,0,1.0)'},
                    'p2c': {'color': 'rgba(144,238,144,0.3)',
                            'highlight': 'rgba(144,238,144,1.0)'},
                    'c2p': {'color': 'rgba(144,238,144,0.3)',
                            'highlight': 'rgba(144,238,144,1.0)'},
                    's2s': {'color': 'rgba(255,0,0,0.3)',
                            'highlight': 'rgba(255,0,0,1.0)'},
                    'unk': {'color': 'rgba(0,255,255,0.3)',
                            'highlight': 'rgba(0,255,255,1.0)'}}

    _class2dash = {'p2p': False,
                   'p2c': [8, 4],
                   'c2p': [8, 4],
                   's2s': [5, 5],
                   'unk': [6, 2]}

    def __init__(self, rel_file=None):
        with open(rel_file, 'r') as as_rel_file:
            for line in as_rel_file.readlines():
                if re.search('^# inferred clique:', line):
                    self.tier1 = line.rstrip("\n").split(':')[-1].split(' ')
                elif re.search('^#', line):
                    continue
                else:
                    [prov_as, cust_as, rel] = line.rstrip("\n").split('|')
                    self.as_rel["%s+%s" % (prov_as, cust_as)] = int(rel)

    def rel_char(self, src, dst):
        rv = '?'
        key = "{0}+{1}".format(src, dst)
        key_rev = "{0}+{1}".format(dst, src)
        if key in self.as_rel:
            if self.as_rel[key] == 0:
                rv = '-'
            elif self.as_rel[key] < 0:
                rv = '>'
            elif self.as_rel[key] == 1:
                rv = '<'
            else:
                rv = '='
        elif key_rev in self.as_rel:
            if self.as_rel[key_rev] == 0:
                rv = '-'
            elif self.as_rel[key_rev] < 0:
                rv = '<'
            elif self.as_rel[key_rev] == 1:
                rv = '>'
            else:
                rv = '='

        return rv

    def rel2class(self, src, dst):
        return self._rel2class[self.rel_char(src, dst)]

    def class2color(self, c):
        return self._class2color[c]

    def class2dash(self, c):
        return self._class2dash[c]

    def peering(self):
        return self._rel2class['-']

    def tier1_asn(self):
        return self.tier1
