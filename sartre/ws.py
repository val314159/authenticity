from prelude import *
from bottle import request, response, Bottle, abort, static_file
app = Bottle()

def DB(_=[]):
    from leveldb import LevelDB
    if not _: _.append(LevelDB('.db'))
    return _[0]

class obj:
    @staticmethod
    def dbCreate(rec):
        print  "DB CREATE", repr(rec)
        obj = rec['params'][0]
        obj_id = obj.pop('id')
        DB().Put(obj_id+'.~meta', '{}')
        for k,v in obj.iteritems():
            DB().Put(obj_id+'.'+k, json.dumps(v))
            pass
        return "DB CREATE", repr(rec)
    @staticmethod
    def dbRead(rec):
        print  "DB READ", repr(rec)
        return "DB READ", repr(rec)
    @staticmethod
    def dbUpdate(rec):
        print  "DB UPDATE", repr(rec)
        print  "DB UPDATE", repr(rec['params'])
        obj=rec['params'][0]
        obj_id=obj.pop('id')
        for k,v in obj.iteritems():
            print "----- UP", repr((k,v))
            DB().Put(obj_id+'.'+k, json.dumps(v))
            pass
        return "DB UPDATE"
    @staticmethod
    def dbDelete(rec):
        print  "DB DELETE", repr(rec)
        return "DB DELETE", repr(rec)

    @staticmethod
    def sub(*a,**kw):
        return "SUB", repr((a,kw))
    @staticmethod
    def pub(*a,**kw):
        return "PUB", repr((a,kw))

    @staticmethod
    def ping(*a,**kw):
        return "PONG", repr((a,kw))
    @staticmethod
    def load(path):
        print "LOAD", repr(path)
        path = path['params'][0]
        data=open(path).read()
        arr=path.split('/')
        d = dict(
            dirname='/'.join(arr[:-1]),
            filename=arr[-1],
            data=data,
            )
        print "D", repr(d)
        return d
    @staticmethod
    def save(obj):
        print "SAVBE", repr(obj)
        filename, data = obj['params']
        f=open(filename,'w')
        f.write(data)
        f.close()
        return dict(result=true)

    @staticmethod
    def filesystem_walk(x):
        return dict((name,(dirs,files))
                    for name,dirs,files in os.walk(x['params'][0]))
    @staticmethod
    def motd(x):
        import subprocess
        x=subprocess.Popen(['fortune'],stdout=subprocess.PIPE)
        y = x.communicate()
        return y[0]
    pass

_ClientObj=obj
def set_client_obj(obj):global _ClientObj;_ClientObj=obj
set_client_obj(obj)

from common import authorize_token
from geventwebsocket import WebSocketError

@app.route('/test')
def test():
    response.headers['Access-Control-Allow-Origin'] = '*'
    tok = authorize_token(None)
    return ['ok']

@app.route('/websocket')
def handle_websocket():
    response.headers['Access-Control-Allow-Origin'] = '*'

    tok = authorize_token()

    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    while True:
        try:
            message = wsock.receive()
            #print("Your message was: %r" % message)
            if not message: break
            j=json.loads(message)
            #print("Your message was::" + repr(j))

            method=j['method']
            _id=j.get('id',None)
            j['_ws'] = wsock
            fn=getattr(_ClientObj,method)
            try:
                ret=fn(j)
                #print "RET", repr(ret)
                if ret:
                    wsock.send(json.dumps(dict(id=_id,
                                               method=method,
                                               result=ret)))
                    pass
            except:
                #print "EXCEPT"
                print_exc()
        except WebSocketError:
            #print "WEB SOCKET ERROR"
            print_exc()
            break
    print "BYE!"

@app.route('/static/<filename:path>')
def serve_static(filename):
    if filename.endswith('.md'):
        from markdown2 import markdown_path
        response.headers['Access-Control-Allow-Origin'] = '*'
        return markdown_path(filename)
    resp = static_file(filename, root='static')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def dump_db():
    print "DUMP DB"
    for x in DB().RangeIter():
        print "X", x

from common import glaunch
if __name__=='__main__':
    print 'DB0', '='*80
    dump_db()
    print 'DB9', '='*80
    glaunch(app,8080,8443)
