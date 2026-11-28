"""DP-4 세션 요청 도우미. usage(작업 폴더 tools/out/detail/DP-4/m0 에서): python -X utf8 -B ../../../../gen_detail_dp4/q.py <name> '<json req 또는 파일>' [n]
-> r_<name>.json 저장, 풀어 낸 앞부분 출력"""
import json, socket, sys, os
PORT = 41082
def ask(req, timeout=470, port=PORT):
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
    req = dict(req); req['save'] = os.path.abspath('r_%s.json' % name).replace(os.sep, '/')
    ask(req, timeout)
    return unwrap(req['save'])
def tool(name, tool, timeout=470, **arguments):
    return call(name, {'tool': tool, 'arguments': arguments}, timeout)
def ex(_n, command, timeout=470, **params):
    return call(_n, {'tool': 'execute', 'arguments': {'command': command, 'params': params, 'verbose': False}}, timeout)
def batch(name, cmds, rollback=True, timeout=470):
    return call(name, {'commands': cmds, 'rollback': rollback, 'verbose': False}, timeout)
def C(command, **params):
    return {'command': command, 'params': params}
if __name__ == '__main__':
    name = sys.argv[1]; a = sys.argv[2]
    req = json.load(open(a, encoding='utf-8')) if os.path.exists(a) else json.loads(a)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    u = call(name, req)
    print(json.dumps(u, ensure_ascii=False)[:n])
