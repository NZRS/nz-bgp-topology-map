import requests

# links -dump "http://nzix.net/cgi-bin/lg.cgi?query=bgp&protocol=IPv4&router
# =${ROUTESERVER}&addr=regexp%20^" > ${ROUTESERVER}.txt


# Collect data from the NZIX route servers
# RS_LIST=['wix', 'chix', 'hix', 'pnix', 'ape']
RS_LIST=['wix']

for rs_location in RS_LIST:
    for rs_server in range(1, 3):
        rs_name = "rs%s.%s.nzix.net" % (rs_server, rs_location)
        print(rs_name)

        r = requests.get('http://nzix.net/cgi-bin/lg.cgi',
                         params={'query': 'bgp', 'protocol': 'IPv4',
                                 'router': rs_name, 'addr': 'regexp ^'})

        with open("%s.html" % rs_name, 'wb') as f:
            f.write(r.content)

        with open("%s.txt" % rs_name, 'wb') as f:
            f.write(html2text.html2text(r.content))
