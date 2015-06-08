## Downloading the BGP dump files

The script *download-rv.sh* will fetch the BGP dump files from RouteViews archive based on the list of prefixes
in *sources.txt*. The selected date to use is part of the script, will be a parameter sometime soon.

## Processing the BGP dump files

mrt2txt has as pre-requisite [bgpdump](https://bitbucket.org/ripencc/bgpdump/wiki/Home)

For Mac OS X, you can
- hg clone https://bitbucket.org/ripencc/bgpdump
- cd bgpdump
- bash bootstrap.sh
- make install

Please note these scripts are helpers and not intended for isolated consumption.

## License

    This file is part of 'NZ BGP Topology Map'.

    'NZ BGP Topology Map' is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as 
    published by the Free Software Foundation, either version 3 of the 
    License, or (at your option) any later version.

    'NZ BGP Topology Map' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public 
    License along with 'NZ BGP Topology Map'.  If not, see 
    <http://www.gnu.org/licenses/>.

