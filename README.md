Make rule to deploy to production install everything in /var/www, so you
can run a test by executing

cd /var/www && python -m SimpleHTTPServer 8888

and then direct your browser to

http://localhost:8888/alchemy
