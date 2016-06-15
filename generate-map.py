import BGP.fetcher
import nzix.fetcher
import megaport.fetcher
import asrelationship.fetcher
import asrelationship.parser
import json
from IPy import IP, IPSet
import networkx as nx
from networkx.readwrite import json_graph
import asn_name_lookup
import math


verbose = False
refresh = 'nzix'


def normalize_weight(w):
    if w < 1:
        return 1
    else:
        return math.sqrt(w)


def calculate_ipset_weight(s):
    w = 0
    for ip in s:
        w += 2 ** (24-ip.prefixlen())

    return w


def country2group(c):
    if c == 'NZ':
        return 'NZ'
    elif c == 'AU':
        return 'AU'
    else:
        return 'other'

# Step 1, get the network view from Global BGP
if refresh in ['all', 'global']:
    global_view = BGP.fetcher.get_bgp_view()
    with open('global_view.json', 'wb') as f:
        json.dump(global_view, f, indent=2)
else:
    with open('global_view.json') as f:
        global_view = json.load(f)

# Step 2, get the network view from NZIX
if refresh in ['all', 'nzix']:
    nzix = nzix.fetcher.get_ix_view()
    with open('nzix.json', 'wb') as f:
        json.dump(nzix, f, indent=2)
else:
    with open('nzix.json') as f:
        nzix = json.load(f)

# Step 3, get the network view from Megaport
if refresh in ['all', 'megaport']:
    megaport_ix = megaport.fetcher.get_ix_view()
    with open('megaport.json', 'wb') as f:
        json.dump(megaport_ix, f, indent=2)
else:
    with open('megaport.json') as f:
        megaport_ix = json.load(f)

# Step 4, Fetch and Build the AS relationship
as_rel_file = asrelationship.fetcher.get_as_relationship_file()
as_rel = asrelationship.parser.AsRelationship(as_rel_file)
tier1 = as_rel.tier1_asn()

# print("Forward: %s" % as_rel.rel_char(24, 10343))
# print("Reverse: %s" % as_rel.rel_char(10343, 24))
# Step 5, read the IX information we have in the configuration
with open('conf/ix-info.json') as f:
    ix_info = json.load(f)

# Step 6, Build graph
G = nx.Graph()
for view in [nzix, megaport_ix, global_view]:
    for entry in view:
        # Calculate the aggregated list of networks observed
        ipset = IPSet([IP(p) for p in entry['prefixes']])
        w = calculate_ipset_weight(ipset)
        path = entry['path']
        for i in range(0, len(path)-1):
            # Exclude pre-pending and AS Path stuffing
            if path[i] == path[i+1]:
                continue

            if path[i] in ix_info or path[i+1] in ix_info:
                path_class = as_rel.peering()
            else:
                path_class = as_rel.rel2class(path[i], path[i+1])

            path_color = as_rel.class2color(path_class)
            if verbose:
                print("Path %s - %s: %s %s" % (path[i], path[i+1],
                                               path_class, w))
            G.add_edge(path[i], path[i+1], _class=path_class)
            if 'weight' not in G[path[i]][path[i+1]]:
                G[path[i]][path[i+1]]['w'] = 0
            G[path[i]][path[i+1]]['w'] += w

# Step 7, enrich the information in the graph
s = asn_name_lookup.AsnNameLookupService()
asn_names = s.lookup_many([n for n in G.nodes_iter()])

with open('as-names.json', 'wb') as f:
    json.dump(asn_names, f)

degree_list = []
for asn, degree in G.degree_iter():
    G.node[asn]['degree'] = degree
    degree_list.append(degree)
    if asn in ix_info:
        G.node[asn]['group'] = 'IX'
        G.node[asn]['name'] = ix_info[asn]['name']
        G.node[asn]['descr'] = ix_info[asn]['descr']
    elif asn in tier1:
        G.node[asn]['group'] = 'Tier1'
        G.node[asn]['name'] = asn_names[asn]['short_descr']
        G.node[asn]['descr'] = asn_names[asn]['long_descr']
    elif asn in asn_names and asn_names[asn]['short_descr'] == 'PRIVATE':
        G.node[asn]['group'] = 'priv'
        G.node[asn]['name'] = asn_names[asn]['short_descr']
        G.node[asn]['descr'] = asn_names[asn]['long_descr']
    else:
        G.node[asn]['group'] = country2group(asn_names[asn]['country'])
        G.node[asn]['name'] = asn_names[asn]['short_descr']
        G.node[asn]['descr'] = asn_names[asn]['long_descr']


# Step 8, save a JSON representation
graph_json = json_graph.node_link_data(G)
with open('nz-bgp-map.json', 'wb') as f:
    json.dump(graph_json, f, indent=2)

# Step 9, save a JSON representation that can be used by the web frontend
with open('nz-bgp-map.js', 'wb') as f:
    nodes = [{'group': n['group'],
              'id': n['id'],
              'value': n['degree'],
              'label': n['name'],
              'description': n['descr']}
             for n in graph_json['nodes']]
    edges =[{'to': nodes[e['target']]['id'],
             'from': nodes[e['source']]['id'],
             'value': normalize_weight(e['w']),
             'class': e['_class']} for e in graph_json['links']]
    weight_range =[e['value'] for e in edges]

    metadata = {'last_update': 'now',
                'dr': [min(degree_list), max(degree_list)],
                'wr': [min(weight_range), max(weight_range)]}
    f.write("var edges=%s;\n" % json.dumps(edges))
    f.write("var nodes=%s;\n" % json.dumps(nodes))
    f.write("var metadata=%s\n" % json.dumps(metadata))
