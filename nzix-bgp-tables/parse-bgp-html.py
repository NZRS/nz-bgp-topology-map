#!/usr/bin/env python

from bs4 import BeautifulSoup

with open('r1.ape.html') as bgpdata:
    html = BeautifulSoup(bgpdata)

    print html.title
