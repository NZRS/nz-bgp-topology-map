__author__ = 'secastro'

import csv
import networkx as nx
from networkx.readwrite import json_graph
import json

G = nx.Graph()
line_cnt = 0
for rib in ['rv-bgp-tables/data/prefix-aspath.txt',
            'rv-bgp-tables/RIPE-RIS-20150812.txt']:
    with open(rib, 'rb') as aspath_file:
        aspath_list = csv.reader(aspath_file, delimiter='|')

        for aspath in aspath_list:

            # Special case to filter out some prefixes we don't want to see.
            if aspath[0] == "0.0.0.0/0":
                print "ERROR: Skipping default route"
                continue
            if line_cnt % 100000 == 0:
                print "{} paths processed".format(line_cnt)
            # if line_cnt > 150000:
            #     break

            line_cnt += 1
            asn_seq = aspath[1].split(' ')
            for i in range(1, len(asn_seq)):
                # Remove the prepending
                if asn_seq[i-1] != asn_seq[i]:
                    G.add_edge(asn_seq[i-1], asn_seq[i])

for node_deg in G.degree_iter():
    [asn, degree] = node_deg
    # print asn, degree
    G.node[asn]['degree'] = degree

with open('raw-bgp-graph.json', 'wb') as f:
    json.dump(json_graph.node_link_data(G), f)
