#!/usr/bin/env python

import csv
import json

as_info_json = {}
with open('as-names.txt', 'rb') as as_info_file:
    as_info = csv.reader(as_info_file, quotechar='',
    quoting=csv.QUOTE_NONE, delimiter='|')

    for entry in as_info:
        asn = entry[0].lstrip('"').rstrip()
        country = entry[1].strip()
        description = entry[4].lstrip().split(' ',1)[0]
        as_info_json[asn] = dict(country=country, descr=description)

with open('as-info.json', 'wb') as as_info_file:
    json.dump(as_info_json, as_info_file)
