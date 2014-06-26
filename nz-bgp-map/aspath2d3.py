#!/usr/bin/env python

import json
import networkx as nx
from networkx.readwrite import json_graph
import csv

# Merge the NZIX view with the RouteViews view, generate a full json map
# that can be loaded into D3

with open('../nzix-bgp-tables/nzix.json', 'rb') as nzix_file:
    nzix_view = json.load( nzix_file )

ix_set = set()
path = []
for router_entry in nzix_view:
    ix_name = router_entry['routeserver'].split('.')[1]
    ix_set.add( ix_name )
    for prefix in router_entry['prefixes']:
        prev_as = ix_name
        for asn in prefix['aspath']:
            path.append([ prev_as, asn])
            prev_as = asn

G = nx.Graph()
G.add_edges_from( path )
for ix in ix_set:
    G.node[ ix ]['group'] = 'IX'
    G.node[ ix ]['name'] = ix.upper()
    G.node[ ix ]['stroke'] = 3

# Add labelling based on the country
with open('../nz-trace-destinations/as-from-rir.tsv', 'rb') as as_info_file:
    as_info = csv.reader(as_info_file, delimiter='\t')

    for asn in as_info:
        if G.node.has_key(asn[0]):
            if asn[1] == 'NZ':
                G.node[ asn[0] ]['group'] = 'NZ'
                G.node[ asn[0] ]['stroke'] = 1
            elif asn[1] == 'AU':
                G.node[ asn[0] ]['group'] = 'AU'
                G.node[ asn[0] ]['stroke'] = 2
            else:
                G.node[ asn[0] ]['group'] = 'unk'
                G.node[ asn[0] ]['stroke'] = 3

# Go over the list of nodes and add the degree attribute
for node_deg in G.degree_iter():
    G.node[ node_deg[0] ]['degree'] = node_deg[1]

json_dump = json_graph.node_link_data(G)
json.dump(json_dump, open('nz-bgp-map.json', 'w'))
