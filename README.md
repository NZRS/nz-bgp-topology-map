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

To produce the map, simply execute

```
make
```

This code will download the full BGP dumps from RouteViews available,
that will take time and bandwidth. Once the files are downloaded, it
will extract relevant AS Paths from the data, which takes more time.
Overall the initial data fetching and munging can take easily 30 minutes
or more.

To have your own version of the visualization, you can execute

```
make deploy-test
```

that will put the necessary files in one directory to be served by a web server.
If you want to change the destination of the files, edit *Makefile*


## TODO

There is always ways to improve code, documentation and the data. This is what we have in mind

- Remove some of the shell scripts and use pure Python solutions
- Separate the visualization framework from the setup and branding. Currently there are our own changes to Alchemy
  making things difficult to maintain.
- Test a different visualization framework.
- Prune the resulting graph to remove Autonomous System that don't add much value, like foreign stub ASes
- Generalize this framework to produce relevant visualizations for any country, not only NZ.

