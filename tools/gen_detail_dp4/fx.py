"""DP-4 수정 1회차(v2.31.2 -> v2.31.3) 도우미 - 헤드리스 세션 41083(작업 폴더 tools/out/detail/DP-4/m1).
결과는 r_<tag>.json, 보낸 편집 명령은 REC 에 모아 cmds_<stage>.json 으로 남긴다."""
import json, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q, nb
PORT = 41083
WD = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/m1'
REC = []


def C(command, **params):
    return {'command': command, 'params': params}


def call(name, req, timeout=470):
    req = dict(req)
    req['save'] = '%s/r_%s.json' % (WD, name)
    q.ask(req, timeout, PORT)
    return q.unwrap(req['save'])


def tool(name, tool_, timeout=470, **arguments):
    return call(name, {'tool': tool_, 'arguments': arguments}, timeout)


def ex(name, command, timeout=470, **params):
    return call(name, {'tool': 'execute', 'arguments': {'command': command, 'params': params, 'verbose': False}}, timeout)


def run(tag, cmds, verbose=False, rollback=True, rec=True, die=True):
    u = call(tag, {'commands': cmds, 'rollback': rollback, 'verbose': verbose})
    d = u.get('data')
    if u.get('isError') or isinstance(d, str) or not d or not d.get('ok'):
        print('FAIL', tag, (json.dumps(d, ensure_ascii=False) if not isinstance(d, str) else d)[:3000])
        if die:
            sys.exit(2)
        return None
    if rec:
        REC.extend(cmds)
        p = '%s/cmds_all.json' % WD
        old = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else []
        old.append({'tag': tag, 'commands': cmds})
        json.dump(old, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('ok', tag, len(cmds), 'cmds', '%.1f s' % u['s'])
    return d['results']


def meas(names, tag='meas'):
    out = {}
    for n in names:
        u = call(tag, {'tool': 'measure', 'arguments': {'body': n}})
        d = u['data']
        if not isinstance(d, dict):
            out[n] = str(d)[:200]
            continue
        b = [x for x in d['bodies'] if x['name'] == n]
        b = b[0] if b else d['bodies'][0]
        out[n] = dict(name=b['name'], volume=round(b['volume_mm3'], 3), bbox=[round(v, 3) for v in b['bbox']['min'] + b['bbox']['max']], material=b.get('material'), mass=round(b.get('mass_g', 0), 3),
                      faces=b.get('faces'), closed=b.get('closed'), com=[round(v, 3) for v in b.get('center_of_mass', [])])
    return out


def clr(tag, bodies, against, c=1.0, show=8):
    d = ex('c_' + tag, 'inspect.clearance', bodies=bodies, against=against, clearance=c)['data']
    if not isinstance(d, dict):
        print(tag, 'ERR', str(d)[:400])
        return None
    ok = d['pairs_checked'] + d['pairs_pruned'] > 0
    ov = [(p['a'], p['b'], round(p.get('volume_mm3', 0), 3)) for p in d.get('overlaps', [])]
    nr = sorted([(round(p['distance_mm'], 3), p['a'], p['b']) for p in d.get('near', []) if p['distance_mm'] > 1e-6])
    print(tag, 'measured', ok, 'trunc', d['truncated'], 'unchecked', len(d['unchecked']), 'overlaps', ov, 'near>0', nr[:show])
    return dict(measured=ok, truncated=d['truncated'], unchecked=d['unchecked'], overlaps=ov, near=nr, touching=[(p['a'], p['b']) for p in d.get('near', []) if p['distance_mm'] <= 1e-6])


def comps(tag='cl_now'):
    return call(tag, {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})['data']['components']


def tm(T):
    X, Y, Z, P = T[0][:3], T[1][:3], T[2][:3], T[3][:3]
    return [X[0], Y[0], Z[0], P[0], X[1], Y[1], Z[1], P[1], X[2], Y[2], Z[2], P[2]]


def drive(j, v):
    return ex('drv', 'joint.drive', joint=j, value=v, quiet=True)
