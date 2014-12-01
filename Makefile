all: data/nz-bgp-map.json

IX_LIST=wix chix hix pnix ape

NZIX_ROUTESERVERS := $(foreach ix,$(IX_LIST),$(foreach n,1 2,rs$(n).$(ix).nzix.net))
NZIX_BGP_REQS := $(foreach rs,$(NZIX_ROUTESERVERS),nzix-bgp-tables/$(rs).txt)
NZIX_BGP_FILES := $(foreach rs,$(NZIX_ROUTESERVERS),$(rs).txt)

RV_MRT_FILES := $(wildcard rv-bgp-tables/*/rib.*.bz2)

# This is the day of the AS relationship data we are going to use
REL_DAY=20141001

PROD_SERVER ?= bgp-map
PROD_DIR ?= /usr/share/nginx/bgp-map
LOCAL_DIR ?= /var/www
DRUPAL_SERVER = srsov-drupal1
DRUPAL_DIR = bgp-map

data/nz-bgp-map.json: nz-bgp-map/aspath2d3.py data/nzix.json \
                        data/nz-as-rels.json \
                        data/as-from-rir.tsv \
                        data/substitute-as.json \
                        data/as-info.json
	cd nz-bgp-map && /usr/bin/python aspath2d3.py && cd ..

data/nzix.json: nzix-bgp-tables/parse-bgp-txt.py $(NZIX_BGP_REQS)
	cd nzix-bgp-tables && /usr/bin/python ./parse-bgp-txt.py $(NZIX_BGP_FILES) && cd ..

define NZIX_BGP_template
nzix-bgp-tables/${1}.txt: nzix-bgp-tables/fetch-bgp-tables.sh
	cd nzix-bgp-tables && bash fetch-bgp-tables.sh ${1} && cd ..
endef

$(foreach rs,${NZIX_ROUTESERVERS},$(eval $(call NZIX_BGP_template,${rs})))

data/prefix-aspath.txt: rv-bgp-tables/mrt2txt.sh $(RV_MRT_FILES)
	bash rv-bgp-tables/mrt2txt.sh $(RV_MRT_FILES)

as-rank/$(REL_DAY).as-rel.txt:
	wget -O - http://data.caida.org/datasets/as-relationships/serial-1/$(REL_DAY).as-rel.txt.bz2 | bzip2 -cd > $@_
	mv $@_ $@

data/nz-as-rels.json: as-relationships/get-as-relationships.py \
                            data/rv-nz-aspath.json \
                            data/nzix.json \
                            as-rank/$(REL_DAY).as-rel.txt \
                            data/local-as-rel-info.csv
	/usr/bin/python as-relationships/get-as-relationships.py \
        as-rank/$(REL_DAY).as-rel.txt data/local-as-rel-info.csv

data/rv-nz-aspath.json: data/prefix-aspath.txt \
        data/as-from-rir.tsv \
        nz-trace-destinations/find-nz-prefixes.py
	cd nz-trace-destinations && /usr/bin/python find-nz-prefixes.py && cd ..

data/as-from-rir.tsv: nz-trace-destinations/list-nz-as.py \
        nz-trace-destinations/delegated-apnic-latest
	cd nz-trace-destinations && /usr/bin/python list-nz-as.py && cd ..

nz-trace-destinations/delegated-apnic-latest:
	cd nz-trace-destinations && wget -q -N \
    http://ftp.apnic.net/stats/apnic/delegated-apnic-latest && \
    wget -q -N http://ftp.apnic.net/stats/apnic/delegated-apnic-latest.md5 && \
	md5sum -c delegated-apnic-latest.md5 && cd ..

# data/as-list.txt: data/rv-nz-aspath.json data/nzix.json \
#                     nz-bgp-map/extract-unique-asn.py
# 	cd nz-bgp-map && python extract-unique-asn.py && cd ..

clean-nzix:
	rm -f nzix-bgp-tables/*.txt

data/as-info.json: data/as-list.txt nz-bgp-map/fetch-as-names.py
	cd nz-bgp-map && /usr/bin/python fetch-as-names.py && cd ..

deploy-test: data/nz-bgp-map.json web-frontend/force.html web-frontend/alchemy.html
	cd /var/www && mkdir -p misc/data d3 scripts styles images
	rsync -a data/nz-bgp-map.alchemy.json ${LOCAL_DIR}/misc/data
	rsync -a web-frontend/alchemy.html ${LOCAL_DIR}/index.html
	rsync -a web-frontend/credits.html ${LOCAL_DIR}/
	rsync -a web-frontend/styles/* ${LOCAL_DIR}/styles/
	rsync -a web-frontend/scripts/* ${LOCAL_DIR}/scripts/
	rsync -a web-frontend/images/* ${LOCAL_DIR}/images/
	rsync -a web-frontend/images/favicon.png ${LOCAL_DIR}/

deploy-prod: data/nz-bgp-map.json web-frontend/force.html web-frontend/alchemy.html
	ssh ${PROD_SERVER} 'mkdir -p ${PROD_DIR} && cd ${PROD_DIR} && mkdir -p misc/data d3 scripts styles images'
	rsync -a data/nz-bgp-map.alchemy.json ${PROD_SERVER}:${PROD_DIR}/misc/data
	rsync -a web-frontend/alchemy.html ${PROD_SERVER}:${PROD_DIR}/index.html
	rsync -a web-frontend/credits.html ${PROD_SERVER}:${PROD_DIR}/
	rsync -a web-frontend/styles/* ${PROD_SERVER}:${PROD_DIR}/styles/
	rsync -a web-frontend/scripts/* ${PROD_SERVER}:${PROD_DIR}/scripts/
	rsync -a web-frontend/images/* ${PROD_SERVER}:${PROD_DIR}/images/
	rsync -a web-frontend/images/favicon.png ${PROD_SERVER}:${PROD_DIR}/

deploy-standalone: data/nz-bgp-map.json web-frontend/alchemy.html
	ssh ${PROD_SERVER} 'mkdir -p ${PROD_DIR} && cd ${PROD_DIR} && mkdir -p misc/data d3 scripts styles'
	rsync -a data/nz-bgp-map.alchemy.json ${PROD_SERVER}:${PROD_DIR}/misc/data
	rsync -a web-frontend/alchemy.html ${PROD_SERVER}:${PROD_DIR}/index.html
	rsync -a web-frontend/styles/* ${PROD_SERVER}:${PROD_DIR}/styles/
	rsync -a web-frontend/scripts/* ${PROD_SERVER}:${PROD_DIR}/scripts/

drupal-deploy: data/nz-bgp-map.json web-frontend/alchemy.html
	ssh ${DRUPAL_SERVER} 'mkdir -p ${DRUPAL_DIR} && cd ${DRUPAL_DIR} && mkdir -p data scripts styles'
	rsync -a data/nz-bgp-map.alchemy.json ${DRUPAL_SERVER}:${DRUPAL_DIR}/data
	rsync -a web-frontend/styles/* ${DRUPAL_SERVER}:${DRUPAL_DIR}/styles/
	rsync -a web-frontend/scripts/* ${DRUPAL_SERVER}:${DRUPAL_DIR}/scripts/
