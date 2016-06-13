import BGP.fetcher
import nzix.fetcher
import megaport.fetcher
import asrelationship.fetcher
import asrelationship.parser
import json

# Step 1, get the network view from Global BGP
# global_view = BGP.fetcher.get_bgp_view()
# with open('global_view.json', 'wb') as f:
#     json.dump(global_view, f, indent=2)

# Step 2, get the network view from NZIX
# nzix = nzix.fetcher.get_ix_view()
# with open('nzix.json', 'wb') as f:
#     json.dump(nzix, f, indent=2)

# Step 3, get the network view from Megaport
# megaport_ix = megaport.fetcher.get_ix_view()
# with open('megaport.json', 'wb') as f:
#     json.dump(megaport_ix, f, indent=2)

# Step 4, Fetch and Build the AS relationship
as_rel_file = asrelationship.fetcher.get_as_relationship_file()
as_rel = asrelationship.parser.AsRelationship(as_rel_file)

# print("Forward: %s" % as_rel.rel_char(24, 10343))
# print("Reverse: %s" % as_rel.rel_char(10343, 24))
# Step 5, Improve AS relationships for the network views from NZIX and Megaport

# Step 6, Prepare map

# Step 7, Save map representation in long format
