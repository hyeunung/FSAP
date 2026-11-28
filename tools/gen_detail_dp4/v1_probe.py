"""DP-4 검도 수정 1회차: 볼트 검사(M-01) · 끼우는 길(M-12) · 잘못 끼움 시험 · 탭 둘레 살 · 임시 STEP. 세션 41085, 저장 안 함.
프로브·사본은 root에 REST 자세 월드 좌표로 만들고, 끝나면 edit.restore_checkpoint 로 되돌린다.
usage: python -X utf8 -B v1_probe.py <ckpt|bolt|path|mis|wall|exp|restore ...>"""
import sys, os, json, math
import fx, nb
fx.PORT = 41085
fx.WD = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/v1'
os.chdir(fx.WD)
from fx import ex, tool, C, clr, run
T2 = 'P_RXDC03_T2_GUIDE_판금'; CL = 'P_RXDC03_BEAM_CLAMP_판금'; RB = 'P_RXDC03_RISER_BRKT_밀링'; LG = 'P_RXDC03_LEAD_GUIDE_3DP'
BR = ['CB5-16_RXDC03_RISER_1', 'CB5-16_RXDC03_RISER_2', 'CB5-16_RXDCC1_RISER_3']; BG = ['CB5-16_RXDC03_GUIDE_1', 'CB5-16_RXDC03_GUIDE_2']
BT = ['CB5-12_RXDC03_T2_1', 'CB5-12_RXDC03_T2_2']; BC = ['CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_2']
SELF = [T2, CL, RB, LG] + BR + BG + BT + BC
what = sys.argv[1:]
OUT = {}


def isflex(a):
    return a.startswith('STEP대기_MR-') or a.startswith('STEP대기_HG-KR23_LEAD') or a.startswith('STEP대기_HG-KR23_CONN') or a.startswith('TU0') or 'PTFE' in a or a.startswith('CBL') or 'CABLE' in a


def sbox(b):  # measure bbox(min xyz, max xyz) -> 서명 모양(x0,x1,y0,y1,z0,z1)
    return [b[0], b[3], b[1], b[4], b[2], b[5]]


def rot180(d, p):
    n = math.sqrt(sum(x * x for x in d)); d = [x / n for x in d]
    R = [[2 * d[i] * d[j] - (1 if i == j else 0) for j in range(3)] for i in range(3)]
    t = [p[i] - sum(R[i][j] * p[j] for j in range(3)) for i in range(3)]
    return [R[0] + [t[0]], R[1] + [t[1]], R[2] + [t[2]]]


def frame_map(src, dst):  # src/dst = (origin, e1, e3) -> 3x4
    def fr(o, e1, e3):
        e2 = [e3[1] * e1[2] - e3[2] * e1[1], e3[2] * e1[0] - e3[0] * e1[2], e3[0] * e1[1] - e3[1] * e1[0]]
        return o, [e1, e2, e3]
    os_, Es = fr(*src); od, Ed = fr(*dst)
    R = [[sum(Ed[k][i] * Es[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    t = [od[i] - sum(R[i][j] * os_[j] for j in range(3)) for i in range(3)]
    return [R[0] + [t[0]], R[1] + [t[1]], R[2] + [t[2]]]


if 'ckpt' in what:
    print('ckpt', json.dumps(ex('ckpt', 'edit.checkpoint')['data'], ensure_ascii=False)[:200])
    print('act', json.dumps(ex('act', 'component.activate', component='root')['data'], ensure_ascii=False)[:200])
if 'bolt' in what:
    P = []; cm = []
    def cyl(n, base, axis):
        cm.append(C('solid.cylinder', radius=4.25, height=30, base=base, axis=axis, operation='new', name='PRB_' + n, body_name='PRB_' + n)); P.append('PRB_' + n)
    cyl('R1', [-288, 90, 261.05], 'Z'); cyl('R2', [-278, 90, 261.05], 'Z'); cyl('R3', [-265.25, 79, 261.05], 'Z')
    cyl('T1', [-296, 75, 197.95], 'Z'); cyl('T2', [-284, 75, 197.95], 'Z')
    cyl('G1', [-287.05, 84.725, 147.467], 'X'); cyl('G2', [-287.05, 87.733, 155.949], 'X')
    cyl('C1', [-345, 81.95, 619.5], 'Y'); cyl('C2', [-345, 81.95, 631.5], 'Y')
    run('prb_build', cm, rec=False)
    m = fx.meas(P, 'm_prb')
    for k, v in m.items(): print(k, v['bbox'], v['volume'])
    boxes = [sbox(v['bbox']) for v in m.values()]
    AG = sorted((set(nb.neighbors([], 4, boxes)) | set(SELF)) - set(P))
    print('against', len(AG))
    OUT['bolt_probe'] = clr('prb_bolts', P, AG, 3.0, 30)
    OUT['bolt_probe_bbox'] = {k: v['bbox'] for k, v in m.items()}
if 'path' in what:
    # 끼우는 길: 부품 사본을 끼우는 방향 반대로 단계마다 옮겨(끝 = 부품 길이 + 10) 굳은 부품과 겹침을 잰다
    plan = {'RB': (RB, [-1, 0, 0], 70.6, 8), 'LG': (LG, [-1, 0, 0], 82.6, 8), 'T2': (T2, [0, 0, -1], 34.0, 5), 'CL': (CL, [0, -1, 0], 62.0, 7),
            'RBz': (RB, [0, 0, 1], 247.0, 6), 'CLz': (CL, [0, 0, 1], 45.5, 5)}
    res = {}
    for tag, (body, d, L, n) in plan.items():
        cm = []; names = []
        for i in range(1, n + 1):
            s = L * i / n; nm = 'PP_%s_%d' % (tag, i)
            cm.append(C('solid.move', bodies=[body], translate=[d[0] * s, d[1] * s, d[2] * s], copy=True, name=nm, body_names=[nm])); names.append(nm)
        r = run('pp_%s' % tag, cm, rec=False, die=False)
        if r is None: res[tag] = 'build fail'; continue
        m = fx.meas(names, 'm_pp')
        names = [k for k, v in m.items() if not isinstance(v, str)]
        print(tag, 'copies', len(names), 'last bbox', m[names[-1]]['bbox'] if names else None)
        boxes = [sbox(m[k]['bbox']) for k in names]
        own = {body} | set({RB: BR, LG: BG, T2: BT, CL: BC}[body])
        AG = sorted(set(nb.neighbors([], 2, boxes)) - own - set(n_ for n_ in sum([[]], [])))
        AG = [a for a in AG if not a.startswith('PP_') and not a.startswith('PRB_') and not a.startswith('MIS_')]
        hard = [a for a in AG if not isflex(a)]; flex = [a for a in AG if isflex(a)]
        res[tag] = dict(dir=d, length=L, steps=n, hard=clr('pp_h_%s' % tag, names, hard, 0.5, 12), flex=clr('pp_f_%s' % tag, names, flex, 0.5, 6) if flex else None, hard_n=len(hard), flex_names=flex)
    OUT['path'] = res
if 'mis' in what:
    u = [0, 3.008 / 9.0, 8.482 / 9.0]
    un = math.sqrt(u[1] ** 2 + u[2] ** 2); u = [0, u[1] / un, u[2] / un]
    w = [0, -u[2], u[1]]
    poses = {
        'LG_A_rotX180': (LG, rot180([1, 0, 0], [-249, 86.229, 151.708])), 'LG_B_flip_holeline': (LG, rot180(u, [-249, 86.229, 151.708])), 'LG_C_flip_perp': (LG, rot180(w, [-249, 86.229, 151.708])),
        'T2_A_rotZ180': (T2, rot180([0, 0, 1], [-290, 75, 234.5])), 'T2_B_flip_holeline': (T2, rot180([1, 0, 0], [-290, 75, 234.5])), 'T2_C_flip_perp': (T2, rot180([0, 1, 0], [-290, 75, 234.5])),
        'CL_A_rotY180': (CL, rot180([0, 1, 0], [-345, 118.5, 625.5])), 'CL_B_flip_holeline': (CL, rot180([0, 0, 1], [-345, 118.5, 625.5])), 'CL_C_flip_perp': (CL, rot180([1, 0, 0], [-345, 118.5, 625.5])),
    }
    fT2 = ([-290, 75, 236], [1, 0, 0], [0, 0, 1]); fCL = ([-345, 120, 625.5], [0, 0, 1], [0, 1, 0])
    neg = lambda f: (f[0], [-x for x in f[1]], f[2])
    poses['T2_at_CL_1'] = (T2, frame_map(fT2, fCL)); poses['T2_at_CL_2'] = (T2, frame_map(fT2, neg(fCL)))
    poses['CL_at_T2_1'] = (CL, frame_map(fCL, fT2)); poses['CL_at_T2_2'] = (CL, frame_map(fCL, neg(fT2)))
    own = {RB: BR, LG: BG, T2: BT, CL: BC}
    res = {}
    for tag, (body, M) in poses.items():
        nm = 'MIS_' + tag
        r = run('mis_%s' % tag, [C('solid.move', bodies=[body], matrix=M[0] + M[1] + M[2], copy=True, name=nm, body_names=[nm])], rec=False, die=False)
        if r is None: res[tag] = 'build fail'; continue
        m = fx.meas([nm], 'm_mis')
        if isinstance(m.get(nm), str): res[tag] = 'no body ' + m[nm]; print(tag, res[tag]); continue
        bb = m[nm]['bbox']
        place_own = set([body]) | set(own[body])
        if tag.startswith('T2_at_CL'): place_own |= {CL} | set(BC)
        if tag.startswith('CL_at_T2'): place_own |= {T2} | set(BT)
        AG = sorted(set(nb.neighbors([], 1, [sbox(bb)])) - place_own)
        AG = [a for a in AG if not a.startswith(('PP_', 'PRB_', 'MIS_'))]
        hard = [a for a in AG if not isflex(a)]; flex = [a for a in AG if isflex(a)]
        print(tag, 'bbox', bb, 'vol', m[nm]['volume'])
        res[tag] = dict(bbox=bb, matrix=M, hard=clr('mis_h_%s' % tag, [nm], hard, 0.2, 10) if hard else None, flex=clr('mis_f_%s' % tag, [nm], flex, 0.2, 6) if flex else None, hard_names=hard, flex_names=flex)
    OUT['mis'] = res
if 'wall' in what:
    rays = []; tags = []
    for n, x, y, z in (('RS1', -288, 90, 243), ('RS2', -278, 90, 243), ('RS3', -265.25, 79, 243), ('T2_1', -296, 75, 241), ('T2_2', -284, 75, 241)):
        for dn, d in (('+X', (1, 0, 0)), ('-X', (-1, 0, 0)), ('+Y', (0, 1, 0)), ('-Y', (0, -1, 0))):
            rays.append({'origin': [x + 2.15 * d[0], y + 2.15 * d[1], z], 'dir': list(d)}); tags.append((n, dn))
    # 받침 구멍 Ø5.5 가장자리 살: 구멍 벽 바로 바깥에서 부품 겉면까지
    for n, body, x, y, z, dirs in (('RB_h1', RB, -288, 90, 253, 'xy'), ('RB_h2', RB, -278, 90, 253, 'xy'), ('RB_h3', RB, -265.25, 79, 253, 'xy')):
        for dn, d in (('+X', (1, 0, 0)), ('-X', (-1, 0, 0)), ('+Y', (0, 1, 0)), ('-Y', (0, -1, 0))):
            rays.append({'origin': [x + 2.8 * d[0], y + 2.8 * d[1], z], 'dir': list(d)}); tags.append((n + '@' + body, dn))
    d = ex('pick_wall', 'view.pick', rays=rays, all=True)['data']
    H = d.get('hits', d.get('results', d)) if isinstance(d, dict) else d
    W = {}
    for (n, dn), ry, h in zip(tags, rays, H):
        hs = h if isinstance(h, list) else (h.get('hits') if isinstance(h, dict) and 'hits' in h else [h])
        want = n.split('@')[1] if '@' in n else 'P_RX19_BLOCK_밀링'
        b = [x for x in hs if x and x.get('body') == want]
        off = 0.05 if '@' not in n else 0.05
        if b: W.setdefault(n.split('@')[0], {})[dn] = round(math.dist(b[0]['point'], ry['origin']) + off, 2)
        else: W.setdefault(n.split('@')[0], {})[dn] = None
    for k, v in W.items(): print(k, v)
    OUT['wall_mm'] = W
if 'exp' in what:
    os.makedirs('stepout', exist_ok=True)
    ev = {}
    for fn, body in (('RISER', RB), ('LEAD_GUIDE', LG), ('T2_GUIDE', T2), ('BEAM_CLAMP', CL), ('RX19_BLOCK', 'P_RX19_BLOCK_밀링')):
        r = tool('exp_' + fn, 'export', path=fx.WD + '/stepout/%s.step' % fn, bodies=[body])
        ev[fn] = str(r.get('data'))[:200]; print(fn, ev[fn])
    OUT['export'] = ev
if 'restore' in what:
    print('restore', json.dumps(ex('rst', 'edit.restore_checkpoint')['data'], ensure_ascii=False)[:300])
    i = tool('insp_end', 'inspect_design', measure=False, sketches=False, timeline='summary', bodies='names', joints=False)['data']
    fe = i['timeline']['features'] if isinstance(i['timeline'], dict) else i['timeline']
    bn = [b if isinstance(b, str) else b.get('name') for b in i.get('bodies', [])]
    OUT['end'] = dict(features=len(fe), bodies=len(bn), left=[b for b in bn if b.startswith(('PRB_', 'PP_', 'MIS_'))], errors=sum(1 for f in fe if f.get('error')))
    print('end', OUT['end'])
old = json.load(open('v1p.json', encoding='utf-8')) if os.path.exists('v1p.json') else {}
old.update(OUT)
json.dump(old, open('v1p.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
