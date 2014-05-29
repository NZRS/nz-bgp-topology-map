#!/usr/bin/python

import urllib2
import urllib
import json
import time
import os
import sys
import time
import yaml

class CredentialsNotFound(Exception):
    pass

authfile = "%s/.atlas/auth" % os.environ['HOME'];

target_def = { "target": "www.nzrs.net.nz",
               "description": "nz test traceroute",
               "type": "traceroute",
               "protocol": "ICMP",
               "af": 4,
               "is_oneoff": True,
               "can_visualize": False,
               "is_public": False,
               "interval": 900
           }
probe_def = { "requested": 1,
              "type": "probes",
              "value": "0"
            }

msm = { "definitions": [],
        "probes": [] }

if not os.path.exists(authfile):
    raise CredentialsNotFound(authfile)
auth = open(authfile)
key = auth.readline()[:-1]
auth.close()

url = "https://atlas.ripe.net/api/v1/measurement/?key=%s" % key

# Process the measurement set file
if len(sys.argv) != 2:
    print "Usage: %s conf_file" % (sys.argv[0])
    raise WrongParams()
elif len(sys.argv) == 2:
    conf_file = sys.argv[1]

msm_conf = yaml.safe_load( file(conf_file, 'r') )

for dst in msm_conf['destinations']:
    # Prepare the measurement
#    target = target_def
#    target['target'] = dst
    msm['definitions'].append( dict(target_def, target=dst) )

for src in msm_conf['sources']:
#    probe = probe_def
#    probe['value'] = src
    msm['probes'].append( dict(probe_def, value=src, requested=len(msm_conf['sources'])) )


request = urllib2.Request(url)
request.add_header("Content-Type", "application/json")
request.add_header("Accept", "application/json")

try:
    json_data = json.dumps(msm)
    conn = urllib2.urlopen(request, json_data)
    results = json.load(conn) 
    print("Created {0}".format(results["measurements"]))
    conn.close()
    time.sleep(2) # Not really necessary
except urllib2.HTTPError as e:
    print >>sys.stderr, ("Fatal error: %s" % e.read())
    raise
conn.close()

