__author__ = 'secastro'

from twisted.names import client, error
from twisted.internet import reactor
from twisted.internet import defer, task


class AsnNameLookupService:
    private_AS = range(64512, 65534)
    resolver = None
    as_info = {}

    def __init__(self):
        self.name = 'Lookup'
        self.resolver = client.Resolver('/etc/resolv.conf')
        self.num_workers = 4
        self.lookup_list = []

    def _clean(self, d):
        [descr, sep, suffix] = d.rpartition('-')
        while suffix in ['AS', 'AP', 'AU', 'NZ']:
            [descr, sep, suffix] = descr.rpartition('-')

        if sep == '':
            return suffix
        else:
            return sep.join([descr, suffix])

    def _receive_dns_response(self, records, name, asn):
        """
        Receives TXT records and parses them
        """
        answers, authority, additional = records
        if answers:
            for x in answers:
                try:
                    [asn_, country, rir, date, descr] = str(x.payload.data[0]).split(' | ')
                    short_descr = descr.split(' ', 1)[0]
                    long_descr = ' '.join(descr.split(' ')[1:])
                    self.as_info[asn_] = dict(country=country,
                                              short_descr=self._clean(short_descr),
                                              long_descr=long_descr)
                except ValueError:
                    self.as_info[asn] = dict(country='??',
                                             short_descr='NO INFO',
                                             long_descr='NO INFO')

    def _handle_dns_error(self, failure, name, asn):
        failure.trap(error.DNSNameError)
        self.as_info[asn] = dict(country="??", short_descr='NO INFO', long_descr='NO INFO')

    def _send_dns_query(self, entry):
        [name, asn] = entry
        d = self.resolver.lookupText(name)
        d.addCallback(self._receive_dns_response, name, asn)
        d.addErrback(self._handle_dns_error, name, asn)
        return d

    def _do_parallel_dns(self):
        coop = task.Cooperator()
        work = (self._send_dns_query(name) for name in self.lookup_list)
        return defer.DeferredList([coop.coiterate(work) for i in xrange(self.num_workers)])

    def lookup_many(self, asn_list):
        self.lookup_list = []
        for asn in asn_list:
            if asn is None:
                continue
            if int(asn) in self.private_AS:
                self.as_info[asn] = dict(country='priv', short_descr='PRIVATE',
                                         long_descr='PRIVATE 16-bit ASN')
            else:
                self.lookup_list.append(["as{0}.asn.cymru.com".format(asn), asn])

        finished = self._do_parallel_dns()

        finished.addCallback(lambda ignored: reactor.stop())

        reactor.run()

        return self.as_info

    def lookup_one(self, asn):
        return self.lookup_many([asn])
