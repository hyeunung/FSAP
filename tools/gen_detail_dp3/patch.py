"""DP-3 저장 뒤: 저장본 전수 측정(v_meas_out.json) ↔ 세션 측정 ↔ 서명 → 바뀐 것만 서명 · 체결 목록 · 가공품 재질표에 고쳐 넣는다(ledger.py sigpatch).
usage(작업 폴더에서): python -X utf8 -B patch.py <저장본 측정 json> [--write]"""
import json, sys, re, math, os, collections, q
ENG = 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools'
PRJ = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools'
m = json.load(open(sys.argv[1], encoding='utf-8'))
if isinstance(m, list):
    m = m[-1]
if 'results' in m:
    m = m['results'][-1]
if 'result' in m and 'bodies' not in m:
    m = m['result']
S = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8'))
P = S['parts']
BOL = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
r3 = lambda x: round(x, 3)
M = {b['name']: b for b in m['bodies']}
assert len(M) == len(m['bodies'])


def bb6(b):
    return [r3(b['bbox']['min'][0]), r3(b['bbox']['max'][0]), r3(b['bbox']['min'][1]), r3(b['bbox']['max'][1]), r3(b['bbox']['min'][2]), r3(b['bbox']['max'][2])]


# 0) 저장 확인: 세션의 마지막 측정과 저장본 측정이 같은가
SES = {b['name']: b for b in q.unwrap('r_meas_final.json')['data']['bodies']}
diff = [n for n in set(M) | set(SES) if n not in M or n not in SES or max(abs(a - c) for a, c in zip(bb6(M[n]), bb6(SES[n]))) > 0.01 or abs(M[n]['volume_mm3'] - SES[n]['volume_mm3']) > max(1e-5 * abs(SES[n]['volume_mm3']), 0.01) or M[n]['material'] != SES[n]['material']]
print('saved file bodies', len(M), 'session', len(SES), 'different', len(diff), diff[:6])


def tail(k, v):
    t = k.split('/', 1)[1] if '/' in k else k
    if t in M:
        return t
    i = k.find(v['name'])
    return k[i:] if i >= 0 and k[i:] in M else None


used = {}
removed = []
parts = {}
loose = []
for k, v in P.items():
    n = tail(k, v)
    if n is None:
        removed.append(k)
        continue
    used[n] = k
    b = M[n]
    w = dict(v)
    w['bbox'] = bb6(b)
    w['volume'] = r3(b['volume_mm3'])
    w['mass'] = r3(b['mass_g'])
    w['material'] = b['material']
    db = max(abs(a - c) for a, c in zip(v['bbox'], w['bbox']))
    dv = abs((v.get('volume') or 0) - w['volume'])
    if db > 0.05 or dv > max(1e-4 * abs(v.get('volume') or 0), 0.01) or v.get('material') != w['material']:
        if n.startswith('TU0') and dv <= 0.01:
            loose.append((k, round(db, 2)))      # 쓸어 만든 관의 느슨한 상자(부피 같음) — 알려진 것, 서명은 그대로 둔다
        else:
            parts[k] = w
changed_keys = list(parts)
added = [n for n in M if n not in used]
print('changed', len(changed_keys), 'removed', len(removed), 'added', len(added), 'loose tube boxes', loose)
HEAD = lambda n: re.sub(r' \(.*', '', n)
print('changed heads', sorted(collections.Counter(HEAD(k.split('/', 1)[1]) for k in changed_keys).items()))
print('removed heads', dict(collections.Counter(HEAD(k.split('/', 1)[1]) for k in removed)), 'added heads', dict(collections.Counter(HEAD(n) for n in added)))
# 1) 새 바디 서명
SPEC = {'CB5-20_M08_NZ_COMB': 'CB5-20', 'CB5-20_DP2': 'CB5-20', 'STEP대기_CB5-14_DP2': 'CB5-14', 'STEP대기_CB4-30_M08': 'CB4-30', 'CB5-12_M07_CAP': 'CB5-12', 'P_M07_BEAM_CAP': ''}
UNIT = {'CB5-12_M07_CAP': 'U1_FRAME', 'P_M07_BEAM_CAP': 'U1_FRAME'}
newkeys = {}
for n in added:
    h = HEAD(n)
    u = UNIT.get(h, 'U8_PNEU')
    key = u + '/' + n
    parts[key] = dict(name=n, unit=u, component=h, bbox=bb6(M[n]), volume=r3(M[n]['volume_mm3']), mass=r3(M[n]['mass_g']), material=M[n]['material'], bolt=bool(SPEC[h]), spec=SPEC[h])
    newkeys[n] = key
# 2) 체결 목록
clr = json.load(open('pre_clr.json', encoding='utf-8'))
clr2 = json.load(open('pre_clr2.json', encoding='utf-8'))
tap = q.unwrap('r_chk_tap.json')['data']
ovl = {}
for src in (clr, clr2, tap):
    for p in src['overlaps']:
        a, b = p['a'], p['b']
        a2 = re.sub(r'U1_FRAME:1/|U8_PNEU:1/', '', a)
        b2 = re.sub(r'U1_FRAME:1/|U8_PNEU:1/', '', b)
        for x, y in ((a, b), (b, a)):
            ovl.setdefault(x, []).append((y, p['volume_mm3']))
bolt_by_name = {b['name']: b for b in BOL}


def inside(o, n, tol=0.06):
    return all(n[2 * i] - tol <= o[2 * i] and o[2 * i + 1] <= n[2 * i + 1] + tol for i in range(3))


def ring(spec):
    return math.pi * (2.0 ** 2 - 1.65 ** 2) if spec.startswith('CB4') else math.pi * (2.5 ** 2 - 2.1 ** 2)


rem_left = set(removed)
bolts_changed = []
REQ = {'CB4': 6.0, 'CB5': 7.5}
for n in added:
    h = HEAD(n)
    spec = SPEC[h]
    if not spec:
        continue
    nb = bb6(M[n])
    th = [(o, v) for o, v in ovl.get(n, []) if v > 1.0]
    assert len(th) == 1, (n, th)
    tb, vol = th[0]
    eng = round(vol / ring(spec), 2)
    if h == 'CB5-12_M07_CAP':
        front = nb[2] < 200
        e = dict(name=n, spec=spec, pos=[r3((nb[0] + nb[1]) / 2), 120.0 if front else 320.0, r3((nb[4] + nb[5]) / 2)], axis=[0, 1, 0] if front else [0, -1, 0], unit='U1_FRAME',
                 parts=['P_M07_BEAM', 'P_M07_BEAM_CAP'] if front else ['P_M07_BEAM', 'P_M07_BEAM_CAP', 'P_M07_SPLICE_NX' if nb[0] < 0 else 'P_M07_SPLICE_PX'], engage_mm=eng,
                 tap='덮개 플랜지 t3 M5 탭 관통(SUS304), 보 벽 Ø5.5 통과' + ('' if front else ', 이음판 Ø10 머리 구멍 속'), component=h, bbox=nb, temp_shape=False, material=M[n]['material'], src='DP-3 디테일링(v2.31.0) 새 볼트')
        req = 3.0
        e['dp3_2026-11-28'] = dict(old_spec=None, new_spec=spec, thread_body='P_M07_BEAM_CAP', overlap_mm3=round(vol, 2), engage_mm=eng, required_mm=req, rule='M-04 판 탭 t >= 피치 x 3 = 2.4, 물림 = 판 두께 3', ok=eng >= req - 1e-6)
        bolts_changed.append(e)
        continue
    cand = [k for k in rem_left if inside(P[k]['bbox'], nb) or inside(nb, P[k]['bbox'])]
    assert len(cand) == 1, (n, cand)
    k = cand[0]
    rem_left.discard(k)
    old = P[k]
    ob = bolt_by_name[old['name']]
    e = dict(ob)
    f0 = dict(ob.get('fasten_2026-11-28') or {})
    f0['superseded_by'] = 'dp3_2026-11-28'
    req = REQ[spec[:3]]
    e.update(name=n, spec=spec, bbox=nb, engage_mm=eng, old_name=old['name'], old_spec=old['spec'], component=h, temp_shape=n.startswith('STEP대기_'), material=M[n]['material'],
             tap=('M4' if spec.startswith('CB4') else 'M5') + ' 관통 탭(보 벽 t8 전부)', src='DP-3 디테일링(v2.31.0) 길이 바꿈')
    e['fasten_2026-11-28'] = f0
    e['dp3_2026-11-28'] = dict(old_spec=old['spec'], new_spec=spec, thread_body=HEAD(tb), overlap_mm3=round(vol, 2), engage_mm=eng, required_mm=req, ok=eng >= req - 1e-6)
    bolts_changed.append(e)
assert not rem_left, rem_left
# 그대로인 볼트 8개(REG 6 · 클램프 L_6 2): 새 탭에 물림만 고쳐 적는다
for p in tap['overlaps']:
    bn = p['b'] if p['a'] == 'P_M07_BEAM' else p['a']
    if 'LAMP' in bn:
        continue
    ob = dict(bolt_by_name[bn])
    f0 = dict(ob.get('fasten_2026-11-28') or {})
    f0['superseded_by'] = 'dp3_2026-11-28'
    ob['fasten_2026-11-28'] = f0
    eng = round(p['volume_mm3'] / ring(ob['spec']), 2)
    ob['engage_mm'] = eng
    ob['tap'] = ('M4' if ob['spec'].startswith('CB4') else 'M5') + ' 관통 탭(보 앞벽 t8, DP-3이 냄)'
    ob['dp3_2026-11-28'] = dict(old_spec=ob['spec'], new_spec=ob['spec'], thread_body='P_M07_BEAM', overlap_mm3=round(p['volume_mm3'], 2), engage_mm=eng, required_mm=REQ[ob['spec'][:3]], ok=True, note='볼트 그대로, 보에 관통 탭을 냄')
    bolts_changed.append(ob)
print('bolts changed', len(bolts_changed), collections.Counter((b['dp3_2026-11-28']['old_spec'], b['dp3_2026-11-28']['new_spec'], b['dp3_2026-11-28']['engage_mm'], b['dp3_2026-11-28']['ok']) for b in bolts_changed))
json.dump({'parts': parts}, open('changed_parts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(bolts_changed, open('changed_bolts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(dict(removed=removed, changed=changed_keys, added=list(newkeys.values()), loose=loose, saved_vs_session_diff=diff), open('changed_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if '--write' in sys.argv:
    import shutil
    shutil.copyfile(PRJ + '/out/signatures.json', 'signatures_before_DP3.json')
    shutil.copyfile(PRJ + '/out/bolts.json', 'bolts_before_DP3.json')
    shutil.copyfile(PRJ + '/out/mach_props.json', 'mach_props_before_DP3.json')
    rm_names = [P[k]['name'] for k in removed]
    sys.path.insert(0, ENG)
    import ledger
    rc = ledger.main(['sigpatch', '--project', PRJ, '--parts', os.path.abspath('changed_parts.json'), '--removed', ','.join(removed + rm_names), '--bolts', os.path.abspath('changed_bolts.json')])
    S2 = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8'))
    B2 = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
    print('rc', rc, 'sig parts', len(S2['parts']), 'doc', S2['doc'], S2.get('doc_hash'), 'bolts_stale', S2.get('bolts_stale'), 'bolts', len(B2), 'unique', len({b['name'] for b in B2}))
    mp = json.load(open(PRJ + '/out/mach_props.json', encoding='utf-8'))
    for k in changed_keys:
        n = P[k]['name']
        if n in mp:
            mp[n] = dict(mp[n], mats=[parts[k]['material']], mass_g=parts[k]['mass'])
    cap = [v for k, v in parts.items() if v['name'] == 'P_M07_BEAM_CAP'][0]
    mp['P_M07_BEAM_CAP'] = dict(mats=[cap['material']], mass_g=cap['mass'], nb=1)
    json.dump(mp, open(PRJ + '/out/mach_props.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('mach_props', len(mp))
