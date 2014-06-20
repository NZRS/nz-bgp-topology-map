#!/usr/bin/env python

from bs4 import BeautifulSoup
import re

with open('r1.ape.html') as bgpdata:
    html = BeautifulSoup(bgpdata, 'html.parser')

    for code in html.body.find_all('code'):
        for a in code.find_all('a', attrs={'href': re.compile('lg.cgi')}):
            print a.string
