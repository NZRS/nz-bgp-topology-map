#!/usr/bin/env python

import json
import string

suffixes = ['AS','AP', 'AU', 'NZ']

with open('data/as-info.json', 'rb') as as_info_file:
    as_info = json.load(as_info_file)

for as_entry in as_info:
    [ descr, sep, suffix ] = as_info[as_entry]['short_descr'].rpartition('-')
    print "Starting point = %s" % (as_info[as_entry]['short_descr'])
    print "Description    = %s" % (descr)
    while( suffix in suffixes):
        [ descr, sep, suffix ] = descr.rpartition('-')
        print "Description   = %s" % (descr)
    if (sep == ''):
        print "End point      = %s" % (suffix)
    else:
        print "End point      = %s" % sep.join([descr, suffix])

with open('data/as-info-short.json', 'wb') as as_info_file:
    json.dump(as_info, as_info_file)

