all: traceroute.png

traceroute.png: traceroute.dot
	dot -Tpng -o $@ $<

copy: traceroute.json
	cp $< /var/www/data/
