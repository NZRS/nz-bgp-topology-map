__author__ = 'secastro'

from bs4 import BeautifulSoup
import urllib2
import yaml
from multiprocessing import Pool
import re
import datetime
import os

def find_latest(url):
    print "Processing {}".format(url)
    response = urllib2.urlopen(url)
    html = BeautifulSoup(response.read())
    link_list = []
    for link in html.findAll('a', href=re.compile('rib\.\d{8}\.\d{4}\.bz2$')):
        link_list.append(link['href'])

    """Return the largest value found, representing the latest month available"""
    return url + sorted(link_list, reverse=True)[0]


def download_rib(url):
    block_zs = 1024 * 16
    site = url.split('/')[3]
    filename = url.split('/')[-1]
    print "Url {}".format(url)
    print "Site {} Filename {}".format(site, filename)
    fparts = filename.split('.')
    print fparts[1], fparts[2]

    out_dir = "{}/{}.{}".format(site, fparts[1], fparts[2])
    print out_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    rib_file = urllib2.urlopen(url)
    with open("{}/{}".format(out_dir, filename), 'wb') as rib_out_file:
        while True:
            block = rib_file.read(block_zs)
            if not block:
                break

            rib_out_file.write(block)


with open('bgp-sources.yaml', 'rb') as src_config:
    config = yaml.load(src_config)

today = datetime.date.today()
pool = Pool(processes=4)
rib_urls = pool.map(find_latest, ["{}/{:04d}.{:02d}/RIBS/".format(e['url'], today.year, today.month) for e in config])
print rib_urls
pool2 = Pool(processes=4)
pool2.map(download_rib, rib_urls)
