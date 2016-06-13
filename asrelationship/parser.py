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

import csv


class AsRelationship:
    as_rel = {}

    def __init__(self, rel_file=None):
        with open(rel_file, 'r') as as_rel_file:
            as_rel_csv = csv.reader(filter(lambda row: row[0] != '#',
                                           as_rel_file), delimiter="|")
            for as_rel_entry in as_rel_csv:
                [prov_as, cust_as, rel] = as_rel_entry
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

