"""DP-4 수정 1회차 세션 도우미(세션 41083, 사본 m1/base_v2312.sc). 작업 폴더 tools/out/detail/DP-4/m1"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q, nb
PORT = 41083
_ask = q.ask
def ask(req, timeout=470, port=PORT): return _ask(req, timeout, port)
q.ask = ask
from q import C
ex, tool, batch, call = q.ex, q.tool, q.batch, q.call
def clr(tag, bodies, against, c=1.0, show=14):
    d = q.ex('c_' + tag, 'inspect.clearance', bodies=bodies, against=against, clearance=c)['data']
    if not isinstance(d, dict):
        print(tag, 'ERR', str(d)[:400]); return None
    ok = d['pairs_checked'] + d['pairs_pruned'] > 0
    ov = [(p['a'], p['b'], round(p.get('volume_mm3', 0), 3)) for p in d.get('overlaps', [])]
    nr = sorted([(round(p['distance_mm'], 3), p['a'], p['b']) for p in d.get('near', [])])
    print(tag, 'measured', ok, 'checked', d['pairs_checked'], 'pruned', d['pairs_pruned'], 'trunc', d['truncated'], 'unchecked', len(d['unchecked']), 'overlaps', ov)
    for x in nr[:show]: print('   near', x)
    return dict(measured=ok, truncated=d['truncated'], unchecked=d['unchecked'], overlaps=ov, near=nr)
def meas(tag, body):
    d = q.tool('m_' + tag, 'measure', body=body, summary=True)['data']
    return d
if __name__ == '__main__':
    name = sys.argv[1]; a = sys.argv[2]
    req = json.load(open(a, encoding='utf-8')) if os.path.exists(a) else json.loads(a)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    print(json.dumps(q.call(name, req), ensure_ascii=False)[:n])
