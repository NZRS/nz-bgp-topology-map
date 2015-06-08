# NZ BGP Topology Map

*Author*: Sebastian Castro <sebastian@nzrs.net.nz>
Copyright 2014-2015 NZRS Ltd

This is a set of tools to produce a visualization of the New Zealand BGP
peering relationships available in public sources, like the one
available at http://bgp.topology.net.nz

The intention is to provide a visual way to explore how ISP and
organizations are connected in New Zealand, how relevant are Internet
Exchanges, etc.

## Installation

Some components are needed to produce the data used in the
visualization, if you are interested on generating your own view.

### Requirements

Several Python modules are required. You can use *pip* to install them
directly from the *requirements.txt* file.

pip install -r requirements.txt

To parse the MRT files from RouteViews, you need *libbgpdump* from RIPE

https://bitbucket.org/ripencc/bgpdump/wiki/Home

the code expects to find the script to read MRT at
/usr/local/bin/bgpdump

## Processing

This code will download the full BGP dumps from RouteViews available,
that will take time and bandwidth. Once the files are downloaded, it
will extract relevant AS Paths from the data, which takes more time.
Overall the initial data fetching and munging can take easily 30 minutes
or more.


