"""usage: python -X utf8 -B q.py <name> '<json req>'  -> saves r_<name>.json, prints unwrapped text head"""
import json, socket, sys, os
def ask(req, timeout=470, port=41050):
    s = socket.create_connection(('127.0.0.1', port), timeout=timeout)
    f = s.makefile('rwb'); f.write((json.dumps(req) + '\n').encode()); f.flush()
    r = json.loads(f.readline()); s.close(); return r
def unwrap(path):
    o = json.load(open(path, encoding='utf-8'))
    if not o.get('ok'): return o
    r = o['result']
    if 'error' in r: return {'rpc_error': r['error']}
    c = r['result'].get('content', [])
    t = c[0]['text'] if c else ''
    try: d = json.loads(t)
    except Exception: d = t
    return {'isError': r['result'].get('isError', False), 'data': d, 's': o['s']}
def call(name, req, timeout=470):
    req = dict(req); req['save'] = 'r_%s.json' % name
    b = ask(req, timeout)
    return unwrap(req['save'])
if __name__ == '__main__':
    name = sys.argv[1]; a = sys.argv[2]
    req = json.load(open(a, encoding='utf-8')) if os.path.exists(a) else json.loads(a)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    u = call(name, req)
    print(json.dumps(u, ensure_ascii=False)[:n])
