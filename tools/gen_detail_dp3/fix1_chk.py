"""DP-3 수정 1회차 저장 전 검사(검도의 과제 안 검사와 같은 도구 · 같은 범위, E-22) - 헤드리스 세션 41081.
usage(작업 폴더 tools/out/detail/DP-3/m1 에서): python -X utf8 -B ../../../../gen_detail_dp3/fix1_chk.py <stage ...>
stage: measall static thread poses topo joints export insp"""
import json, sys, re, math, os, time, q
q.ask.__defaults__ = (470, 41081)


def _call(name, req, timeout=470):
    req = dict(req)
    req['save'] = os.path.abspath('r_%s.json' % name).replace(os.sep, '/')
    q.ask(req, timeout)
    return q.unwrap(req['save'])


q.call = _call
T = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/'
VR = T + 'out/detail/DP-3/vr/'
HEAD = lambda n: re.sub(r' \(.*', '', n)
OUT = json.load(open('chk_fix1.json', encoding='utf-8')) if os.path.exists('chk_fix1.json') else {}


def ex(tag, command, params, timeout=470):
    u = q.call(tag, {'tool': 'execute', 'arguments': {'command': command, 'params': params}}, timeout=timeout)
    if u.get('isError') or isinstance(u.get('data'), str) or 'rpc_error' in u:
        print('FAIL', tag, json.dumps(u, ensure_ascii=False)[:1200])
        return None
    return u['data']


def tool(tag, name, args, timeout=470):
    u = q.call(tag, {'tool': name, 'arguments': args}, timeout=timeout)
    if u.get('isError') or 'rpc_error' in u:
        print('FAIL', tag, json.dumps(u, ensure_ascii=False)[:1200])
        return None
    return u['data']


def summarize(d):
    ov = d.get('overlaps', [])
    near = d.get('near', d.get('pairs', []))
    return dict(checked=d.get('pairs_checked'), pruned=d.get('pairs_pruned'), reused=d.get('pairs_reused'), truncated=d.get('truncated'), overlaps=len(ov), near=len(near), unchecked=len(d.get('unchecked', []) or []))


def clr(tag, bodies, against, c=1.0):
    t = time.time()
    d = ex(tag, 'inspect.clearance', {'bodies': bodies, 'against': against, 'clearance': c})
    if d is None:
        return None
    json.dump(d, open('c_%s.json' % tag, 'w', encoding='utf-8'), ensure_ascii=False)
    s = summarize(d)
    s['s'] = round(time.time() - t, 1)
    print(tag, s)
    OUT.setdefault('clr', {})[tag] = s
    return d


def allbodies():
    return {b['name']: b for b in q.unwrap(os.path.abspath('r_meas_final.json'))['data']['bodies']}


def pairs_of(d):
    rows = []
    for p in d.get('overlaps', []):
        rows.append((p['a'], p['b'], round(p.get('volume_mm3', 0), 3)))
    return rows


stages = sys.argv[1:]
if 'measall' in stages:
    t = time.time()
    d = tool('meas_final', 'measure', {})
    print('measure all', len(d['bodies']), 'bodies', '%.1f s' % (time.time() - t), 'open', [b['name'] for b in d['bodies'] if not b.get('closed')][:5])

if any(s in stages for s in ('static', 'thread', 'poses')):
    M = allbodies()
    CAPB = sorted(n for n in M if HEAD(n) == 'CB5-16_M07_CAP')
    assert len(CAPB) == 8, CAPB
    S = ['P_M07_BEAM'] + CAPB
    L = json.load(open(VR + 'lists.json', encoding='utf-8'))
    sig = json.load(open(T + 'out/signatures.json', encoding='utf-8'))['parts']
    SIG = {p['name']: p for p in sig.values()}

if 'static' in stages:
    # 검도의 정적 범위(바뀐 59 + 이웃 198 + 움직이는 주변 139)에서 옛 덮개 볼트 이름만 새 이름으로
    AG = sorted((set(L['AG']) - set(n for n in L['AG'] if HEAD(n) == 'CB5-12_M07_CAP') | set(CAPB)) & set(M))
    miss = [n for n in L['AG'] if n not in M and HEAD(n) != 'CB5-12_M07_CAP']
    print('S', len(S), 'against', len(AG), 'missing', miss[:5])
    d = clr('static', S, AG, 1.0)
    if d:
        ov = pairs_of(d)
        import collections
        print('overlap volumes', sorted(collections.Counter(v for a, b, v in ov).items()))
        OUT['static_overlaps'] = ov
        nr = d.get('near', [])
        OUT['static_near_min'] = sorted([(round(p.get('distance', p.get('min_distance', 9)), 3), p['a'], p['b']) for p in nr])[:8]
        print('near min', OUT['static_near_min'][:5])

if 'thread' in stages:
    bolts = json.load(open(T + 'out/bolts.json', encoding='utf-8'))
    A = M['P_M07_BEAM']['bbox']
    pre = tuple(json.load(open(T + 'config.json', encoding='utf-8'))['bolt_prefixes'])
    BB = sorted(n for n, b in M.items() if (HEAD(n).startswith(pre) or HEAD(n).startswith('STEP대기_CB') or HEAD(n).startswith('STEP대기_SFB')) and all(b['bbox']['min'][i] - 1 < A['max'][i] and A['min'][i] - 1 < b['bbox']['max'][i] for i in range(3)))
    print('bolts touching beam box', len(BB))
    capn = sorted(n for n in M if HEAD(n) == 'P_M07_BEAM_CAP')
    d = clr('thread', BB, ['P_M07_BEAM'] + capn + ['P_M07_SPLICE_NX', 'P_M07_SPLICE_PX'], 0.3)
    if d:
        import collections
        ov = pairs_of(d)
        byv = collections.Counter((HEAD(b if HEAD(a).startswith('P_M07') else a)[:3], HEAD(a if HEAD(a).startswith('P_M07') else b), v) for a, b, v in ov)
        for k, n in sorted(byv.items()):
            print('  ', k, n)
        OUT['thread'] = dict(bolts=len(BB), overlaps=ov)
        ny = [(a, b, v) for a, b, v in ov if 'CB5-16_M07_NY:7)' in a + b or 'CB5-16_M07_NY:8)' in a + b]
        cap = [(a, b, v) for a, b, v in ov if 'CB5-16_M07_CAP' in a + b]
        print('NY:7 · :8', ny)
        print('cap bolts', len(cap), sorted(set((HEAD(a), HEAD(b), v) for a, b, v in cap)))
        OUT['thread_ny78'] = ny
        OUT['thread_cap'] = cap

if 'poses' in stages:
    MV = sorted((set(L['EX']) | set(n for n in L['N'] if SIG.get(n, {}).get('unit', '').startswith(('U5_', 'U4_')))) & set(M))
    print('moving against', len(MV))
    res = {}
    for j, vals in (('J_U5_X', [0, 345, 690, 1035, 1380]), ('J_U4_X', [0, 23.75, 47.5, 71.25, 95])):
        for v in vals:
            r = ex('drv', 'joint.drive', {'joint': j, 'value': v, 'quiet': True})
            tag = 'pose_%s_%s' % (j, str(v).replace('.', 'p'))
            d = clr(tag, S, MV, 1.0)
            if d:
                nr = d.get('near', [])
                res[tag] = dict(overlaps=pairs_of(d), near_min=min([p.get('distance', p.get('min_distance', 9)) for p in nr] or [None]) if nr else None)
        ex('drv', 'joint.drive', {'joint': j, 'value': 0, 'quiet': True})
    r = ex('rest', 'motion.play', {'study': 'REST', 'step': 0, 'quiet': True})
    print('rest', json.dumps(r, ensure_ascii=False)[:120])
    OUT['poses'] = res
    print('pose overlaps', {k: (len(v['overlaps']), sorted(set(x[2] for x in v['overlaps'])), v['near_min']) for k, v in res.items()})

if 'topo' in stages:
    d = tool('topo_beam', 'body_topology', {'body': 'P_M07_BEAM', 'faces': 'cylinders'})
    cy = d['cylinders']
    import collections
    print('cylinders', len(cy), collections.Counter(round(c['radius'], 3) for c in cy))

    def axis_key(c):
        a = c['axis']
        o = c['origin']
        k = max(range(3), key=lambda i: abs(a[i]))
        return (k,) + tuple(round(o[i], 2) for i in range(3) if i != k)
    targets = {'reopen': [(1, 1230.0, 300.0), (1, 1230.0, 600.0)], 'fill_nz': [(2, -310.0, 140.0), (2, -310.0, 180.0), (2, -160.0, 140.0), (2, -160.0, 180.0)], 'fill_ny': [(1, -256.0, 276.0), (1, -244.0, 276.0)]}
    rep = {}
    for nm, ks in targets.items():
        for k in ks:
            hit = [c for c in cy if axis_key(c) == k]
            o = [(round(c['radius'], 3), [round(e, 3) for e in c['extent']], round(c['origin'][k[0]], 3), round(c['axis'][k[0]], 0)) for c in hit]
            rep['%s %s' % (nm, k)] = o
            print(nm, k, o)
    OUT['topo'] = dict(cylinders=len(cy), radii=sorted(collections.Counter(round(c['radius'], 3) for c in cy).items()), spots=rep)
    json.dump(cy, open('beam_cylinders.json', 'w', encoding='utf-8'), ensure_ascii=False)

if 'joints' in stages:
    d = ex('jl', 'joint.list', {'exclude_rigid_groups': True})
    if d:
        s = {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in d.items()}
        print('joint.list', s, 'floating', d.get('floating'))
        OUT['joints'] = s

if 'export' in stages:
    os.makedirs(T + 'out/detail/DP-3/stepout', exist_ok=True)
    for n in ['P_M07_BEAM']:
        d = tool('exp', 'export', {'path': T + 'out/detail/DP-3/stepout/%s.step' % n, 'bodies': [n]})
        print('export', n, json.dumps(d, ensure_ascii=False)[:200])

if 'insp' in stages:
    d = tool('insp', 'inspect_design', {'measure': False, 'sketches': False, 'timeline': 'summary', 'bodies': 'names', 'joints': False})
    tl = d.get('timeline') or []
    fe = tl.get('features') if isinstance(tl, dict) else tl
    s = dict(name=d.get('name'), dirty=d.get('dirty'), marker=d.get('marker'), features=len(fe), errors=[f.get('name') for f in fe if f.get('error')], warnings=sum(1 for f in fe if f.get('warning')), suppressed=sum(1 for f in fe if f.get('suppressed')), rolled_back=sum(1 for f in fe if f.get('rolled_back')), bodies=len(d.get('bodies', [])), path=d.get('path'))
    print('inspect', s)
    OUT['insp'] = s

json.dump(OUT, open('chk_fix1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
