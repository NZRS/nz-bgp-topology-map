#!/usr/bin/env python

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import bs4
import re
from collections import defaultdict


def get_aspath(l):
    aspath = '64496 ' + l.split(':')[-1].lstrip()

    return aspath


def get_ix_view(verbose=False):
    lg_url = 'https://lg.megaport.com'
    user_agent = 'NZRS BGP Topology Map Generator. http://bgp.topology.net.nz'

    # BGP Summary for getting all the peers
    bgp_summary = {'option': 'BGP Summary',
                   'variable': '',
                   'router': '125',
                   'submit': 'Submit',
                   '.cgifields': 'option'}
    m = MultipartEncoder(
        fields=bgp_summary
    )
    r = requests.post(lg_url, data=m, headers={'Content-Type': m.content_type})


    # 43.243.22.2          63839    Established
    peer_list = []
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    for pre in soup.find_all('pre'):
        for l in pre.get_text().split("\n"):
            peer_addr = l[:21].rstrip()
            peer_asn = l[21:30].rstrip()
            peer_status = l[30:45].rstrip()

            if peer_status == "Established":
                if verbose:
                    print "%s  %s" % (peer_addr, peer_asn)
                peer_list.append((peer_addr, peer_asn))

    show_neighbour = bgp_summary
    show_neighbour['option'] = 'Show Neighbour Routes'
    aspath_set = defaultdict(set)
    for peer in peer_list:
        # Get the page with the BGP summary for this peer
        show_neighbour['variable'] = peer[0]
        m = MultipartEncoder(fields=show_neighbour)
        r = requests.post(lg_url, data=m, headers={'Content-Type': m.content_type})

        page = bs4.BeautifulSoup(r.content, "html.parser")

        for p in page.findAll('pre'):
            for l in p.get_text().split("\n"):
                if len(l) > 0 and l[0] == "\t":  # Indented line
                    if re.search('BGP.as_path', l):
                        aspath_set[get_aspath(l)].add(prefix)
                else:
                    prefix = l.split(' ')[0]

    return [dict(prefixes=list(prefixes), path=path.split(' ')) for path, prefixes in aspath_set.iteritems()]


if __name__ == "__main__":
    for p in get_ix_view():
        print(p)
