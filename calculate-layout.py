__author__ = 'secastro'

import json
import random
import math
from igraph import *

node_colors = ['black', 'red', 'orange', 'green', 'grey', 'blue']

G = Graph.GRG(30, 0.2)
layout = G.layout("kk")

# Iterate over the list of Nodes (Vertex)
nodes = []
for n in G.vs:
    nodes.append({'id': n.index, 'group': random.randint(1, 6), 'x': 100*layout[n.index][0], 'y': 100*layout[n.index][1]})

edges = []
for e in G.es:
    edges.append({'to': e.target, 'from': e.source, 'weight': random.randint(1, 5)})

print "Nodes = ", nodes
with open('data/fixed-network.js', 'wb') as js_file:
    js_file.write("var nodes = {};\n".format(json.dumps(nodes)))
    js_file.write("var edges = {};\n".format(json.dumps(edges)))

G.write_svg('fixed-layout.svg', layout=layout)

