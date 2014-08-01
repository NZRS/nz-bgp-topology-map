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

rel2class = { '-': 'p2p',
              '>': 'p2c',
              '<': 'c2p',
              '=': 's2s',
              '?': 'unk' }
def edge_rel2class(rel):
    return rel2class.get(rel, 'noinfo')

# Preload the list of substitute ASNs
with open('substitute-as.json', 'rb') as sub_as_file:
    as_sub_list = json.load(sub_as_file)

# Preload the IX information
with open('../data/ix-info.json', 'rb') as ix_info_file:
    ix_info = json.load(ix_info_file)

G = nx.Graph()

# Add the paths extracted from RV with their corresponding relationships
with open('../data/nz-as-rels.json', 'rb') as rv_file:
    rv_paths = json.load(rv_file)

for aspath in rv_paths['aspaths']:
    for src, rel, dst in aspath:
        _class = edge_rel2class(rel)
        _src = substitute_as(src)
        _dst = substitute_as(dst)
        G.add_edge( _src, _dst, _class=_class)

# Overwrite the information about the ASes representing IXes with
# prepared data
for ix_as, ix_data in ix_info.iteritems():
    G.node[ ix_as ]['country'] = 'IX'
    G.node[ ix_as ]['name']    = ix_data['name']
    G.node[ ix_as ]['descr']   = ix_data['descr']

# Load the short names for the ASes
with open('../data/as-info.json', 'rb') as as_info_file:
    as_info = json.load(as_info_file)

# Massage a little bit the AS info to drop a set of prefixes common on
# the names
for as_entry in as_info:
    [ descr, sep, suffix ] = as_info[as_entry]['short_descr'].rpartition('-')
    while( suffix in ['AS','AP', 'AU', 'NZ']):
        [ descr, sep, suffix ] = descr.rpartition('-')
    if (sep == ''):
        as_info[as_entry]['short_descr'] = suffix
    else:
        as_info[as_entry]['short_descr'] = sep.join([descr, suffix])


degree_set = {}
# Go over the list of nodes and add the degree attribute
for node_deg in G.degree_iter():
    [ asn, degree ] = node_deg
    G.node[ asn ]['degree'] = degree
    G.node[ asn ]['upstream'] = G.neighbors(asn)[0] if degree == 1 else asn
    # If I have info for this ASN and no info has been recorded before
    if as_info.has_key(asn) and not G.node[asn].has_key('name'):
        G.node[ asn ]['name'] = as_info[ asn ]['short_descr']
        G.node[ asn ]['descr'] = as_info[ asn ]['long_descr']
        # Add a group based on the country for all nodes
        G.node[ asn ]['country'] = as_info[asn]['country'] if as_info[asn]['country'] in ['NZ', 'AU', 'priv'] else 'other'

    try:
        country = G.node[ asn ]['country'] 
    except KeyError:
        sys.stderr.write('ASN {0} without country??\n'.format(asn))
        country = 'unknown'

    if not degree_set.has_key(country):
        degree_set[country] = set()
    degree_set[country].add(node_deg[1])

degree_range = []
for country in degree_set:
    print "Country = {0}".format(country)
    print "Max = {0}, Min = {1}".format(max(degree_set[country]), min(degree_set[country]))
    degree_range.append(dict(country=country, min=min(degree_set[country]), max=max(degree_set[country])))

# Go over the list of nodes and remove those with degree 1 and country
# 'other'
to_delete = []
for node in G.nodes_iter():
    if G.node[node]['country'] in ['other', 'AU'] and G.node[node]['degree'] == 1:
        to_delete.append(node)

# Save the list of nodes to remove for debugging
with open('nodes_to_remove.txt', 'w') as rem_file:
    rem_file.writelines([ "{} {}\n".format(n, G.node[n]['name']) for n in to_delete ])

G.remove_nodes_from(to_delete)

# Test: Set Vocus AS as root node for the visualization
for id in ['4826', '24130', '9560', '9439', '9503', '45177', '4648',
'38022', '4768', '23655', '24388']:
    G.node[id]['root'] = True

# Make a copy of the graph to generate a second output
json_dump = json_graph.node_link_data(G)
graph_json_dump = json_dump

# Re-adjusting the resulting graph to produce a structure compatible with
# graphJSON (Alchemy)
for node in graph_json_dump['nodes']:
    node['id'] = int(node['id'])
    node['upstream'] = int(node['upstream'])

for link in graph_json_dump['links']:
    link['source'] = graph_json_dump['nodes'][ link['source']]['id']
    link['target'] = graph_json_dump['nodes'][ link['target']]['id']

graph_json_dump['edges'] = graph_json_dump['links']
graph_json_dump['dr'] = degree_range
del graph_json_dump['links']

json.dump(json_dump, open('../data/nz-bgp-map.json', 'w'))
json.dump(graph_json_dump, open('../data/nz-bgp-map.alchemy.json', 'w'))

