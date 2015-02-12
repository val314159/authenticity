if [ ! -d .v ]; then
    virtualenv .v
fi
. .v/bin/activate
pip install wsaccel ujson
pip install bottle requests gevent-websocket leveldb markdown2
pip install websocket-client

alias readme='markdown2 README.md >static/readme.html'

readme
