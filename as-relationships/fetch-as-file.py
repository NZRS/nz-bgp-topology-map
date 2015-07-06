__author__ = 'secastro'

from bs4 import BeautifulSoup
import urllib2
import re
import bz2
from progressbar import ProgressBar

start_url = "http://data.caida.org/datasets/as-relationships/serial-1/"

response = urllib2.urlopen(start_url)
html = BeautifulSoup(response.read())


link_list = []
for link in html.findAll('a', text=re.compile('as\-rel\.txt\.bz2$')):
    link_list.append(link['href'])

selected_link = sorted(link_list, reverse=True)[0]
print "Selected {}".format(selected_link)

block_zs = 1024 * 16
as_file = urllib2.urlopen(start_url + selected_link)
file_size = int(as_file.info().getheaders("Content-Length")[0])
print "Downloading: %s Bytes" % (file_size)

pbar = ProgressBar(maxval=file_size).start()
bz2d = bz2.BZ2Decompressor()
bytes_read = 0
with open(selected_link.rstrip(".bz2"), 'wb') as as_out_file:
    while True:
        block = as_file.read(block_zs)
        if not block:
            break

        bytes_read += len(block)
        pbar.update(bytes_read)
        dblock = bz2d.decompress(block)
        as_out_file.write(dblock)

pbar.finish()
