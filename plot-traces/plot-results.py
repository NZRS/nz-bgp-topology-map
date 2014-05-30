#!/usr/bin/env python

import json
import os, sys
import networkx as nx
from networkx.readwrite import json_graph

G = nx.Graph()

path = []
origins = []
destinations = []
for json_file in sys.argv[1:]:
    msm_data = json.load( file(json_file, 'r') )
    if msm_data:
        for msm in msm_data:
            # First element of the path is src_addr
            prev_hop = [ msm['src_addr'] ]
            origins.append( { "addr": msm['src_addr'], "name": msm['prb_id'] } )
            destinations.append( { "addr": msm['dst_addr'], "name": msm['dst_addr'] } )
            for result in msm['result']:
                hop_addr = set()
                for res in result['result']:
                    if res.has_key('from'):
                        hop_addr.add(res['from'])
                    if res.has_key('x'):
                        hop_addr.add( "{0}-hop{1}".format(msm['from'], result['hop']))
                # Add the hop addr as nodes in the graph
                for phop in prev_hop:
                    for hop in hop_addr:
                        path.append( [ phop, hop ] )
                prev_hop = hop_addr
            
# print path
G.add_edges_from( path )
for src in origins:
    G.node[ src['addr'] ]['group'] = 1
    G.node[ src['addr'] ]['name']  = src['name']
for dst in destinations:
    G.node[ dst['addr'] ]['group'] = 4
    G.node[ dst['addr'] ]['name'] = dst['name']
nx.write_dot(G, 'traceroute.dot')

# Dump the same data in JSON format for D3
json_dump = json_graph.node_link_data(G)
json.dump(json_dump, open('traceroute.json', 'w'))
