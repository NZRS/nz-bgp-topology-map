#!/usr/bin/env python

from bs4 import BeautifulSoup
import sys
import json

as_transit_deg = {}
for in_file in sys.argv[1:]:
    with open(in_file, 'rb') as as_rank_file:
        html = BeautifulSoup(as_rank_file)

        for table in html.body.find_all('table', attrs={'class': 'as-table'}):
            for tr in table.find_all('tr'):
                values = [ td.get_text() for td in tr.find_all('td') ]

                if (len(values) > 0):
                    as_transit_deg[values[1].rstrip().lstrip()] = values[11].rstrip().lstrip()


with open('as-transit-degree.json', 'wb') as as_transit_deg_file:
    json.dump(as_transit_deg, as_transit_deg_file)
