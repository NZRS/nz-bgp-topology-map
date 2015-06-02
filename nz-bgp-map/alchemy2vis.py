__author__ = 'secastro'

from igraph import *
import json
from scales import Scale

_class2color = {
    'p2p': 'orange',
    'p2c': 'lightgreen',
    'c2p': 'lightgreen',
    's2s': 'red',
    'unk': 'cyan'
}

def class2color(edge_class):
    return _class2color.get(edge_class, 'gray')

def gen_title(n):
    return u"<p><b>{0}<br/></b>ASN {1}</br>{2} peer{3}</p>".format(n['name'], n['id'], n['degree'],
                                                                   's' if n['degree'] > 1 else '')


graph_json_dump = json.load(open('../data/nz-bgp-map.alchemy.json', 'rb'))

# Preparing for vis.js format
## Create a graph using igraph
VG = Graph.Formula()

idx = 0
n_idx = {}
for n in graph_json_dump['nodes']:
    n_idx[n['id']] = VG.vcount()
    VG.add_vertex(name=n['id'], title=gen_title(n), value=n['degree'], group=n['country'])

edge_scale = Scale([1, 23000], [1, 20], 0.5)
for e in graph_json_dump['edges']:
    # print "{} -> {}".format(e['source'], e['target'])
    # print [v['name'] for v in VG.vs.select(name=e['source'])]
    # print [v['name'] for v in VG.vs.select(name=e['target'])]
    VG.add_edge(n_idx[e['source']], n_idx[e['target']], color=class2color(e['_class']), width=edge_scale.get_value(e['_weight']))


layout = VG.layout("kk")

vis_nodes = []
vis_edges = []
for n in VG.vs:
    vis_nodes.append({'id': n['name'], 'group': n['group'], 'value': n['value'], 'title': n['title'],
                      'x': 100*layout[n.index][0], 'y': 100*layout[n.index][1]})

for e in VG.es:
    vis_edges.append({'to': e.target, 'from': e.source, 'color': e['color'], 'width': e['width']})


json.dump({'nodes': vis_nodes, 'edges': vis_edges}, open('../data/nz-bgp-map.vis.json', 'w'))
