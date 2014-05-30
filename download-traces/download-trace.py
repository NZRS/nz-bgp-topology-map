#!/usr/bin/python

import urllib2
import urllib
import json
import os
import sys
import time
import yaml

class CredentialsNotFound(Exception):
    pass
class WrongParams(Exception):
    print "Usage: bla bla bla"
    pass

# constants
authfile = "download-api-key.txt"
base_url = "https://atlas.ripe.net/api/v1/measurement/"

# Read the API key
if not os.path.exists(authfile):
    raise CredentialsNotFound(authfile)
auth = open(authfile)
key = auth.readline()[:-1]
auth.close()


if len(sys.argv) != 2:
    print >>sys.stderr, ("Usage: %s msm_list_file" % sys.argv[0])
    raise WrongParams()
elif len(sys.argv) == 2:
    msm_file = sys.argv[1]

# Read the configuration file
msm_stream = file(msm_file, 'r')
 
for msm in msm_stream:
    msm = msm.rstrip('\n')
    print "Measurement %s" % msm

    request = urllib2.Request("%s/%s/result/?key=%s" % (base_url, msm, key))
    request.add_header("Accept", "application/json")
    try:
        conn = urllib2.urlopen(request)
        results = json.load(conn)
        json_out = file("{0}.json".format(msm), 'w')
        json.dump(results, json_out)
        conn.close()
    except urllib2.HTTPError as e:
        print >>sys.stderr, ("Fatal error: %s" % e.read())
        raise
