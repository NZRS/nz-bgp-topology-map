#!/usr/bin/env python

import math
import json
import networkx as nx
from networkx.readwrite import json_graph
import csv
import sys

def substitute_as(asn):
    if as_sub_list.has_key(asn):
        return as_sub_list[asn]
    else:
        return asn

# Preload the list of substitute ASNs
with open('substitute-as.json', 'rb') as sub_as_file:
    as_sub_list = json.load(sub_as_file)

# Merge the NZIX view with the RouteViews view, generate a full json map
# that can be loaded into D3

with open('../data/nzix.json', 'rb') as nzix_file:
    nzix_view = json.load( nzix_file )

ix_set = set()
path = []
for router_entry in nzix_view:
    # If the name of the routeserver is rs1.ape.nzix.net, we keep 'ape'
    try:
        ix_name = router_entry['routeserver'].split('.')[1]
        ix_set.add( ix_name )
        for prefix in router_entry['prefixes']:
            prev_as = ix_name
            for asn in prefix['aspath']:
                asn = substitute_as(asn)
                path.append([ prev_as, asn])
                prev_as = asn
    except IndexError:
        sys.stderr.write('Something went really wrong with data from {0}\n'.format(router_entry['routeserver']))

G = nx.Graph()
G.add_edges_from( path )
for ix in ix_set:
    G.node[ ix ]['country'] = 'IX'
    G.node[ ix ]['name'] = ix.upper()
    G.node[ ix ]['descr'] = ix.upper()
    G.node[ ix ]['stroke'] = 3

# Add the paths extracted from RV
with open('../data/rv-nz-aspath.json', 'rb') as rv_file:
    rv_paths = json.load(rv_file)

for aspath in rv_paths['aspath']:
    if len(aspath) > 1:
        G.add_edges_from( [ [ substitute_as(aspath[i-1]), substitute_as(aspath[i]) ] for i in range(2, len(aspath)) ])

# Add style based on the country
with open('../data/as-from-rir.tsv', 'rb') as as_info_file:
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
with open('../data/as-info.json', 'rb') as as_info_file:
    as_info = json.load(as_info_file)

degree_set = {}
# Go over the list of nodes and add the degree attribute
for node_deg in G.degree_iter():
    [ asn, degree ] = node_deg
    G.node[ node_deg[0] ]['degree'] = node_deg[1]
    G.node[ node_deg[0] ]['radius'] = 8 + 10*math.log(node_deg[1],10)
    if as_info.has_key( node_deg[0]):
        G.node[ node_deg[0] ]['name'] = as_info[ node_deg[0]]['short_descr']
        G.node[ node_deg[0] ]['descr'] = as_info[ node_deg[0]]['long_descr']
        # Add a group based on the country for all nodes
        G.node[ asn ]['country'] = as_info[asn]['country'] if as_info[asn]['country'] in ['NZ', 'AU'] else 'other'

    country = G.node[ asn ]['country'] 
    if not degree_set.has_key(country):
        degree_set[country] = set()
    degree_set[country].add(node_deg[1])

degree_range = []
for country in degree_set:
    print "Country = {0}".format(country)
    print "Max = {0}, Min = {1}".format(max(degree_set[country]), min(degree_set[country]))
    degree_range.append(dict(country=country, min=min(degree_set[country]), max=max(degree_set[country])))

G.graph['dr']= degree_range


json_dump = json_graph.node_link_data(G)
json.dump(json_dump, open('../data/nz-bgp-map.json', 'w'))

