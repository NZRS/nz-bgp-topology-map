from bs4 import BeautifulSoup
import urllib2
import re
import bz2
from progressbar import ProgressBar
import os

__author__ = 'secastro'


def get_as_relationship_file():
    start_url = "http://data.caida.org/datasets/as-relationships/serial-1/"

    response = urllib2.urlopen(start_url)
    html = BeautifulSoup(response.read(), "html.parser")

    link_list = []
    for link in html.findAll('a', text=re.compile('as\-rel\.txt\.bz2$')):
        link_list.append(link['href'])

    selected_link = sorted(link_list, reverse=True)[0]
    # print("AS relationship file: %s" % selected_link)
    output_file = os.path.join('data', selected_link.rstrip(".bz2"))

    if not os.path.isfile(output_file):
        block_zs = 1024 * 16
        as_file = urllib2.urlopen(start_url + selected_link)
        file_size = int(as_file.info().getheaders("Content-Length")[0])
        print "Downloading: %s Bytes" % file_size

        pbar = ProgressBar(maxval=file_size).start()
        bz2d = bz2.BZ2Decompressor()
        bytes_read = 0
        with open(output_file, 'wb') as as_out_file:
            while True:
                block = as_file.read(block_zs)
                if not block:
                    break

                bytes_read += len(block)
                pbar.update(bytes_read)
                dblock = bz2d.decompress(block)
                as_out_file.write(dblock)

        pbar.finish()

    return output_file

if __name__ == "__main__":
    print(get_as_relationship_file())
