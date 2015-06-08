#!/usr/bin/env python

#    This file is part of 'NZ BGP Topology Map'.
#
#    'NZ BGP Topology Map' is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    'NZ BGP Topology Map' is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public
#    License along with 'NZ BGP Topology Map'.  If not, see
#    <http://www.gnu.org/licenses/>.

import sys
from twisted.names import client, error
from twisted.internet import reactor
from twisted.internet import defer, task
import json
import argparse


def send_dns_query( ( domain, resolver, asn )):
    d = resolver.lookupText(domain)
    d.addCallback(receive_dns_response, domain, asn)
    d.addErrback(printError, domain, asn)
    return d
    

def do_parallel_dns(name_list, count, callable, *args, **named):
    coop = task.Cooperator()
    work = (callable(name, *args, **named) for name in name_list)
    return defer.DeferredList([coop.coiterate(work) for i in xrange(count)])


def receive_dns_response(records, domainname, asn):
    """
    Receives TXT records and parses them
    """
    answers, authority, additional = records
    if answers:
        for x in answers:
            try:
                [ asn_, country, rir, date, descr ] = str(x.payload.data[0]).split(' | ')
                short_descr = descr.split(' ', 1)[0]
                long_descr  = ' '.join(descr.split(' ')[1:])
                as_info[asn_] = dict(country=country,
                    short_descr=short_descr, long_descr=long_descr)
            except ValueError:
                sys.stderr.write('ERROR decoding payload %s for %s\n' %
                (str(x.payload), domainname))
                as_info[asn] = dict(country='??', short_descr='NO INFO',
                    long_descr='NO INFO')
    else:
        sys.stderr.write(
            'ERROR: No TXT records found for name %r\n' % (domainname,))


def printError(failure, domainname, asn):
    """
    Print a friendly error message if the domainname could not be
    resolved.
    """
    failure.trap(error.DNSNameError)
    sys.stderr.write('ERROR: domain name not found %r\n' % (domainname,))


if __name__ == '__main__':
    NUM_WORKERS = 8
    as_info = {}

    parser = argparse.ArgumentParser("Fetches AS details for a list of ASN")
    parser.add_argument('--input', required=True, help="Input file with ASNs")
    parser.add_argument('--output', required=True, help="JSON file to save ASN info")
    args = parser.parse_args()

    domains = []
    resolver = client.Resolver('/etc/resolv.conf')
    with open(args.input, 'rb') as name_file:
        for line in name_file:
            asn = line.rstrip()
            try:
                if int(asn) in range(64512, 65534):
                    # These are private ASN
                    as_info[asn] = dict(country='priv', short_descr='PRIVATE',
                        long_descr='PRIVATE 16-bit ASN')
                else:
                    domains.append( [ "as{0}.asn.cymru.com".format(asn), resolver, asn ])
            except ValueError:
                # The asn provided is not a number
                print "AS {} is not a number, skipping".format(asn)
                pass

    finished = do_parallel_dns(domains, NUM_WORKERS, send_dns_query)

    finished.addCallback(lambda ignored: reactor.stop())
    finished.addErrback(printError)

    reactor.run()

    # Save the information we may have obtained
    with open(args.output, 'wb') as as_info_output:
        json.dump(as_info, as_info_output)
