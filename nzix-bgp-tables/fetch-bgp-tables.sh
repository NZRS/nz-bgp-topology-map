#!/bin/bash

ROUTERS="rs1.ape.nzix.net
rs2.ape.nzix.net
rs1.wix.nzix.net
rs2.wix.nzix.net
rs1.chix.nzix.net
rs2.chix.nzix.net
rs1.hix.nzix.net
rs2.hix.nzix.net
rs1.pnix.nzix.net
rs2.pnix.nzix.net"

for router in $ROUTERS; do
    links -dump "http://nzix.net/cgi-bin/lg.cgi?query=bgp&protocol=IPv4&router=${router}&addr=regexp%20^" > $router.txt 
done

