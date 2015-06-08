/*
    Author: Sebastian Castro <sebastian@nzrs.net.nz>
    Copyright 2014-2015 NZRS Ltd

    This file is part of NZ BGP Topology Map.

    NZ BGP Topology Map is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    NZ BGP Topology Map is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public
    License along with NZ BGP Topology Map.  If not, see
    <http://www.gnu.org/licenses/>.

*/
var deg_domain = [1, 250];

var radius = d3.scale.log()
        .domain(deg_domain)
        .range([5, 60]);

var border = d3.scale.linear()
        .domain(deg_domain)
        .range([2, 8]);

var edge_width = d3.scale.sqrt()
        .domain([1, 23000])
        .range([1, 20]);

var node_color = {
    'other': d3.scale.linear()
                .domain(deg_domain)
                .range(['limegreen', 'darkgreen']),
    'IX':    d3.scale.linear()
                .domain(deg_domain)
                .range(['#E34234', '#A40000']),
    'AU':    d3.scale.linear()
                .domain(deg_domain)
                .range(['#FFF066', '#E5CE15']),
    'NZ':    d3.scale.linear()
                .domain(deg_domain)
                .range(['#707070', 'black']),
    'priv':  d3.scale.linear()
                .domain(deg_domain)
                .range(['blue', 'blue'])
};

var config = {
    dataSource: '/misc/data/nz-bgp-map.alchemy.json',
    nodeTypes: { "country": ["AU", "NZ", "IX", "priv", "other"] },
    nodeLabels: { 'AU': 'Australian AS', 'NZ': 'New Zealand AS',
    'IX': 'Internet Exchange', 'priv': 'Private AS', 'other':
    'Other Country AS' },
    edgeTypes: [ 'p2c', 'p2p', 's2s', 'unk' ],
    edgeLabels: { 'p2c': 'Customer to Provider',
        'p2p': 'Peer to Peer',
        's2s': 'Sibling to Sibling',
        'unk': 'Unknown' },
    edgeStrike: function(e) { return edge_width(e._weight); },
    cluster: false,
    nodeCaption: function(n, i) { if (i == 0) { return n.name; } else { return "(" + n.id + ")"; }},
    nodeRadius: function(n) { return radius(n.degree); },
    nodeStrike: function(n) { return border(n.degree); },
    nodeColour: function(n) {
        if (node_color[n.country] !== undefined) {
            return node_color[n.country](n.degree);
        }
        else {
            return 'blue';  /* Treat nodes with unknown group as private */
        }
    },
    linkDistance: function(edge, k) { return 15; },
    preLoad: function() {
        // There is extra info in the input file we could use to
        // set the right domain for the color scales
        this.preLoad.caller.arguments[0].dr.forEach(function(d) {
            if (node_color[d.country]) {
                node_color[d.country].domain([d.min, d.max])
            }
        });
        // There is also information about the range of weights in the edges
        edge_width.domain(this.preLoad.caller.arguments[0].wr);
    },
    afterLoad: function() {
        jQuery(".progress-label").text("Complete!");
        d3.select("#last_updated").append("h3")
            .attr("class", "legendHeader")
            .html("Data prepared on");
        d3.select("#last_updated").append("h4")
            .attr("class", "legendHeader")
            .html(this.afterLoad.caller.arguments[0].lastupdate);
        document.title = "NZ BGP Topology Map"
        d3.select("#brand-title").append("span")
            .html("NZ BGP Topology Map");
    },
    zoomControls: true,
//    graphHeight: function() { return 500; },
    initialScale: 0.4,
//    initialTranslate: [ 300, 100 ],
    scaleExtent: [ 0.4, 2.0 ],
    showFilters: true,
    showControlDash: true,
    nodeFilters: false,
    customFilters: true,
    showLegend: true,
    nodeLegend: true,
    edgeLegend: true,
    forceLocked: true
    };

alchemy.begin(config);
