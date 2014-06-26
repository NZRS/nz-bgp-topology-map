#!/usr/bin/env python

import math
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

# Add the paths extracted from RV
with open('../nz-trace-destinations/rv-nz-aspath.json', 'rb') as rv_file:
    rv_paths = json.load(rv_file)

for aspath in rv_paths['aspath']:
    if len(aspath) > 1:
        G.add_edges_from( [ [ aspath[i-1], aspath[i] ] for i in range(2, len(aspath)) ])

# Add style based on the country
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

# Load the short names for the ASes
with open('as-info.json', 'rb') as as_info_file:
    as_info = json.load(as_info_file)

degree_set = set()
# Go over the list of nodes and add the degree attribute
for node_deg in G.degree_iter():
    G.node[ node_deg[0] ]['degree'] = node_deg[1]
    G.node[ node_deg[0] ]['radius'] = 8 + 10*math.log(node_deg[1],10)
    if as_info.has_key( node_deg[0]):
        G.node[ node_deg[0] ]['name'] = as_info[ node_deg[0]]['descr']
    degree_set.add( node_deg[1] )

json_dump = json_graph.node_link_data(G)
json.dump(json_dump, open('nz-bgp-map.json', 'w'))

with open('nodes.txt', 'wb') as node_file:
    node_out = csv.writer(node_file, lineterminator='\n')
    for node in G:
        node_out.writerow([ node])


with open('degree.txt', 'wb') as degree_file:
    degree_out = csv.writer(degree_file, delimiter='\t')

    for degree_value in degree_set:
        degree_out.writerow( [degree_value])
