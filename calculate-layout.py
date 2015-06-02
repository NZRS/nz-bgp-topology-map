__author__ = 'secastro'

import networkx as nx
from networkx.readwrite import json_graph
import json
import random
import math
from forceatlas import forceatlas2_layout

node_colors = ['black', 'red', 'orange', 'green', 'grey', 'blue']

# G = nx.path_graph(12)
G = nx.lollipop_graph(30, 10)
# pos = nx.spring_layout(G, dim=2, k=2/math.sqrt(30), scale=800, iterations=100)
pos = forceatlas2_layout(G, iterations=100)
# pos = nx.shell_layout(G, dim=2)
# random_layout fails on exporting??
# pos = nx.random_layout(G, dim=2)
# pos = nx.spectral_layout(G, dim=2)
json_dump = json_graph.node_link_data(G)

for n in json_dump['nodes']:
    n['id'] = int(n['id'])
    n['x'] = pos[n['id']][0] * 800
    n['y'] = pos[n['id']][1] * 800
    n['group'] = random.randint(1, 6)

json_dump['edges'] = [{'to': l['target'], 'from': l['source'], 'weight': random.randint(1, 5)} for l in json_dump['links']]

print "Nodes = ", json_dump['nodes']
with open('data/fixed-network.js', 'wb') as js_file:
    js_file.write("var nodes = {};\n".format(json.dumps(json_dump['nodes'])))
    js_file.write("var edges = {};\n".format(json.dumps(json_dump['edges'])))

# print json.dumps(json_dump, indent=2)
