all: data/nz-bgp-map.json

IX_LIST=wix chix hix pnix ape
# IX_LIST=pnix hix

NZIX_ROUTESERVERS := $(foreach ix,$(IX_LIST),$(foreach n,1 2,rs$(n).$(ix).nzix.net))
NZIX_BGP_REQS := $(foreach rs,$(NZIX_ROUTESERVERS),nzix-bgp-tables/$(rs).txt)
NZIX_BGP_FILES := $(foreach rs,$(NZIX_ROUTESERVERS),$(rs).txt)

RV_MRT_FILES := $(wildcard rv-bgp-tables/*/rib.*.bz2)

data/nz-bgp-map.json: nz-bgp-map/aspath2d3.py data/nzix.json \
                        data/rv-nz-as-rels.json \
                        data/as-from-rir.tsv \
                        data/substitute-as.json \
                        data/as-info.json 
	cd nz-bgp-map && python aspath2d3.py && cd ..

data/nzix.json: nzix-bgp-tables/parse-bgp-txt.py $(NZIX_BGP_REQS)
	cd nzix-bgp-tables && python ./parse-bgp-txt.py $(NZIX_BGP_FILES) && cd ..

define NZIX_BGP_template
nzix-bgp-tables/${1}.txt: nzix-bgp-tables/fetch-bgp-tables.sh 
	cd nzix-bgp-tables && bash fetch-bgp-tables.sh ${1} && cd ..
endef

$(foreach rs,${NZIX_ROUTESERVERS},$(eval $(call NZIX_BGP_template,${rs})))

data/prefix-aspath.txt: rv-bgp-tables/mrt2txt.sh $(RV_MRT_FILES)
	bash rv-bgp-tables/mrt2txt.sh $(RV_MRT_FILES)

data/nz-as-rels.json: as-relationships/get-as-relationships.py \
                            data/rv-nz-aspath.json \
                            data/nzix.json \
                            as-rank/20140601.as-rel.txt \
                            data/local-as-rel-info.csv
	python as-relationships/get-as-relationships.py \
        as-rank/20140601.as-rel.txt data/local-as-rel-info.csv

data/rv-nz-aspath.json: data/prefix-aspath.txt \
        data/as-from-rir.tsv \
        nz-trace-destinations/find-nz-as-path.py
	cd nz-trace-destinations && python find-nz-as-path.py && cd ..

data/as-from-rir.tsv: nz-trace-destinations/list-nz-as.py \
        nz-trace-destinations/delegated-apnic-latest
	cd nz-trace-destinations && python list-nz-as.py && cd ..
	
nz-trace-destinations/delegated-apnic-latest:
	cd nz-trace-destinations && wget -q -N \
    http://ftp.apnic.net/stats/apnic/delegated-apnic-latest && \
    wget -q -N http://ftp.apnic.net/stats/apnic/delegated-apnic-latest.md5 && \
	md5sum -c delegated-apnic-latest.md5 && cd ..

# data/as-list.txt: data/rv-nz-aspath.json data/nzix.json \
#                     nz-bgp-map/extract-unique-asn.py
# 	cd nz-bgp-map && python extract-unique-asn.py && cd ..

data/as-info.json: data/as-list.txt nz-bgp-map/fetch-as-names.py
	cd nz-bgp-map && python fetch-as-names.py && cd ..

deploy-test: data/nz-bgp-map.json web-frontend/force.html web-frontend/alchemy.html
	mkdir -p /var/www/d3 /var/www/data /var/www/alchemy/data /var/www/alchemy/scripts
	rsync -a d3/*.js /var/www/d3
	install data/nz-bgp-map.json /var/www/data
	install data/nz-bgp-map.alchemy.json /var/www/alchemy/data
	install web-frontend/force.html /var/www/nz-bgp-map.html
	install web-frontend/alchemy.html /var/www/alchemy/index.html
	install alchemy/alchemy.js alchemy/vendor.js /var/www/alchemy/scripts/
	rsync -a web-frontend/nzrs.css alchemy/styles/*.css \
        alchemy/styles/fonts alchemy/styles/images /var/www/alchemy/styles/

deploy-prod: data/nz-bgp-map.json web-frontend/force.html web-frontend/alchemy.html
	ssh turista 'mkdir -p /var/www/html/nz-bgp-map/data /var/www/html/d3 /var/www/html/alchemy/{data,scripts,styles}'
	rsync -a d3/*.js turista:/var/www/html/d3
	rsync -a data/nz-bgp-map.json turista:/var/www/html/nz-bgp-map/data
	rsync -a data/nz-bgp-map.alchemy.json turista:/var/www/html/alchemy/data
	scp web-frontend/force.html turista:/var/www/html/nz-bgp-map/index.html
	rsync -a web-frontend/alchemy.html turista:/var/www/html/alchemy/index.html
	rsync -a web-frontend/nzrs.css alchemy/styles/*.css \
        alchemy/styles/fonts alchemy/styles/images turista:/var/www/html/alchemy/styles
	rsync -a alchemy/*.js turista:/var/www/html/alchemy/scripts
