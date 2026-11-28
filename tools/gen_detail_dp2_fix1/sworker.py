"""디테일링 스냅샷부 읽기 세션: 헤드리스 SolidCraft 하나를 임시 사본으로 열어 붙잡고 로컬 TCP로 요청을 받는다(저장 안 함).
앱 MCP가 3D_Modeling/ 열기를 거부(--allow-path 없음)해 쓰는 통로다(실행 머리글 (바), mech_RGSEE/verify/vworker.py와 같은 방식).
usage: python -B sworker.py <port> <design.sc>
요청 한 줄 JSON: {"tool": 이름, "arguments": {...}, "save": 결과 파일} 또는 {"commands": [...], "save": 파일} 또는 {"quit": true}"""
import json, socket, subprocess, sys, time, os
port, sc = int(sys.argv[1]), sys.argv[2]
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
log = open('sworker_%d.log' % port, 'a', encoding='utf-8')
p = subprocess.Popen(['solidcraft-cli', 'mcp', '--headless', '--allow-any-path', '--in', sc], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open('sworker_%d.err' % port, 'ab'))
nid = [0]
def rpc(method, params=None, notify=False):
    msg = {'jsonrpc': '2.0', 'method': method}
    if params is not None: msg['params'] = params
    if not notify:
        nid[0] += 1; msg['id'] = nid[0]
    p.stdin.write((json.dumps(msg) + '\n').encode()); p.stdin.flush()
    if notify: return None
    while True:
        line = p.stdout.readline()
        if not line: raise RuntimeError('server closed')
        try: r = json.loads(line)
        except Exception: continue
        if r.get('id') == msg['id']: return r
t0 = time.time()
rpc('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'snap', 'version': '1'}})
rpc('notifications/initialized', notify=True)
r = rpc('tools/call', {'name': 'inspect_design', 'arguments': {'measure': False, 'sketches': False, 'timeline': 'summary', 'bodies': 'names', 'joints': False}})
json.dump(r, open('r_doc_open.json', 'w', encoding='utf-8'), ensure_ascii=False)
log.write('open %.1f s\n' % (time.time() - t0)); log.flush()
open('sworker_%d.ready' % port, 'w').write('%.1f' % (time.time() - t0))
srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); srv.bind(('127.0.0.1', port)); srv.listen(4)
while True:
    c, _ = srv.accept()
    try:
        f = c.makefile('rwb'); line = f.readline()
        if not line: c.close(); continue
        req = json.loads(line)
        if req.get('quit'): break
        t = time.time()
        try:
            if req.get('tool'):
                r = rpc('tools/call', {'name': req['tool'], 'arguments': req.get('arguments', {})})
            else:
                r = rpc('tools/call', {'name': 'batch', 'arguments': {'commands': req['commands'], 'rollback': bool(req.get('rollback', False)), 'verbose': bool(req.get('verbose', False))}})
            out = {'ok': True, 'result': r, 's': time.time() - t}
        except Exception as e:
            out = {'ok': False, 'error': repr(e), 's': time.time() - t}
        if req.get('save'):
            json.dump(out, open(req['save'], 'w', encoding='utf-8'), ensure_ascii=False)
            brief = {'ok': out['ok'], 's': out['s'], 'saved': req['save'], 'head': json.dumps(out.get('result', out.get('error')), ensure_ascii=False)[:1500]}
            f.write((json.dumps(brief) + '\n').encode())
        else:
            f.write((json.dumps(out) + '\n').encode())
        f.flush(); c.close()
        log.write('call %.1f s %s\n' % (out['s'], req.get('tool') or ('batch %d' % len(req.get('commands', []))))); log.flush()
    except Exception as e:
        log.write('conn fail %r\n' % e); log.flush()
        try: c.close()
        except Exception: pass
p.kill()
