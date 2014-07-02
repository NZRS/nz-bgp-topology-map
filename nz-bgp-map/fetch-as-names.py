#!/usr/bin/env python

import sys
from twisted.names import client, error
from twisted.internet import reactor
from twisted.internet import defer, task
from twisted.python import usage
import json

def send_dns_query( ( domain, resolver, asn )):
#    print "Querying for {0}".format(domain)
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
    Print the SRV records for the domainname or an error message if no
    SRV records were found.
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
    as_info_file = '../data/as-info.json'

    domains = []
    resolver = client.Resolver('/etc/resolv.conf')
    with open('../data/as-list.txt', 'rb') as name_file:
        for line in name_file:
            asn = line.rstrip()
            if int(asn) in range(64512, 65534):
                # These are private ASN
                as_info[asn] = dict(country='??', short_descr='PRIVATE',
                    long_descr='PRIVATE 16-bit ASN')
            else:
                domains.append( [ "as{0}.asn.cymru.com".format(asn), resolver, asn ])

    finished = do_parallel_dns(domains, NUM_WORKERS, send_dns_query)

    finished.addCallback(lambda ignored: reactor.stop())
    finished.addErrback(printError)

    reactor.run()

    # Save the information we may have obtained
    with open(as_info_file, 'wb') as as_info_output:
        json.dump(as_info, as_info_output)