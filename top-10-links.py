__author__ = 'secastro'

import json
from pandas import DataFrame

with open('data/nz-bgp-map.json', 'rb') as map_file:
    bgp_map = json.load(map_file)

p = DataFrame(bgp_map['edges'], columns=['source', 'target', '_weight'])
print p.sort(columns=['_weight'], ascending=False)[0:10]
