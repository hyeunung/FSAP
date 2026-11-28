"""DP-3 수정 1회차 저장 뒤: 저장본 전수 측정(v_meas_out.json) <-> 세션 마지막 측정 <-> 서명 -> 바뀐 것만 서명 · 체결 목록 · 가공품 재질표에 고쳐 넣는다(ledger.py sigpatch).
usage(작업 폴더 tools/out/detail/DP-3/m1 에서): python -X utf8 -B ../../../../gen_detail_dp3/fix1_patch.py v_meas_out.json [--write]"""
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


# 0) 저장 확인: 세션의 마지막 측정과 저장본(디스크에서 다시 연) 측정이 같은가
SES = {b['name']: b for b in q.unwrap('r_meas_final.json')['data']['bodies']}
diff = [n for n in set(M) | set(SES) if n not in M or n not in SES or max(abs(a - c) for a, c in zip(bb6(M[n]), bb6(SES[n]))) > 0.01 or abs(M[n]['volume_mm3'] - SES[n]['volume_mm3']) > max(1e-5 * abs(SES[n]['volume_mm3']), 0.01) or M[n]['material'] != SES[n]['material']]
print('saved file bodies', len(M), 'session', len(SES), 'different', len(diff), diff[:6], 'open bodies', [n for n, b in M.items() if not b.get('closed')][:5])


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
            loose.append((k, round(db, 2)))
        else:
            parts[k] = w
# 보는 부피 변화(+643 mm3)가 서명 허용차(1e-4 x 부피 = 3,442 mm3)보다 작아 걸리지 않는다 - 고친 바디라 직접 넣는다
k0 = 'U1_FRAME/P_M07_BEAM'
if k0 not in parts:
    b0 = M['P_M07_BEAM']
    w0 = dict(P[k0])
    w0.update(bbox=bb6(b0), volume=r3(b0['volume_mm3']), mass=r3(b0['mass_g']), material=b0['material'])
    assert abs(w0['volume'] - P[k0]['volume'] - 643.087) < 0.01, (w0['volume'], P[k0]['volume'])
    parts[k0] = w0
changed_keys = list(parts)
added = [n for n in M if n not in used]
HEAD = lambda n: re.sub(r' \(.*', '', n)
print('changed', len(changed_keys), changed_keys, 'removed', len(removed), 'added', len(added), 'loose tube boxes', loose)
print('removed heads', dict(collections.Counter(HEAD(k.split('/', 1)[1]) for k in removed)), 'added heads', dict(collections.Counter(HEAD(n) for n in added)))
assert set(HEAD(n) for n in added) == {'CB5-16_M07_CAP'} and len(added) == 8, added
assert set(HEAD(k.split('/', 1)[1]) for k in removed) == {'CB5-12_M07_CAP'} and len(removed) == 8, removed
assert changed_keys == ['U1_FRAME/P_M07_BEAM'], changed_keys
# 1) 새 바디 서명
for n in added:
    parts['U1_FRAME/' + n] = dict(name=n, unit='U1_FRAME', component='CB5-16_M07_CAP', bbox=bb6(M[n]), volume=r3(M[n]['volume_mm3']), mass=r3(M[n]['mass_g']), material=M[n]['material'], bolt=True, spec='CB5-16')
# 2) 체결 목록: 덮개 볼트 8(CB5-12 -> CB5-16), 다시 뚫은 탭의 볼트 2(물림 다시 잼)
th = json.load(open('c_thread.json', encoding='utf-8'))
ovl = {}
for p in th['overlaps']:
    for x, y in ((p['a'], p['b']), (p['b'], p['a'])):
        ovl.setdefault(x, []).append((y, p['volume_mm3']))
ring = math.pi * (2.5 ** 2 - 2.1 ** 2)
bolt_by_name = {b['name']: b for b in BOL}
bolts_changed = []
rem_left = set(removed)
for n in added:
    nb = bb6(M[n])
    t = [(o, v) for o, v in ovl.get(n, []) if v > 1.0]
    assert len(t) == 1 and HEAD(t[0][0]) == 'P_M07_BEAM_CAP', (n, t)
    vol = t[0][1]
    eng = round(vol / ring, 2)
    cand = [k for k in rem_left if all(abs(P[k]['bbox'][i] - nb[i]) < 4.01 for i in range(6))]
    assert len(cand) == 1, (n, cand)
    rem_left.discard(cand[0])
    old = bolt_by_name[P[cand[0]]['name']]
    e = dict(old)
    e.update(name=n, spec='CB5-16', bbox=nb, engage_mm=eng, old_name=old['name'], old_spec='CB5-12', component='CB5-16_M07_CAP', material=M[n]['material'],
             tap='덮개 플랜지 t3 M5 탭 관통(SUS304), 보 벽 Ø5.5 통과' + ('' if nb[2] < 200 else ', 이음판 Ø10 머리 구멍 속') + ' · 볼트 끝이 플랜지 안쪽 면을 4.8 지남',
             src='DP-3 디테일링 수정 1회차(v2.31.1) 길이 바꿈 CB5-12 -> CB5-16(예외 DP3-EX1 조건 3)')
    d0 = dict(old.get('dp3_2026-11-28') or {})
    d0['superseded_by'] = 'dp3f1_2026-11-29'
    e['dp3_2026-11-28'] = d0
    tip = nb[3] if nb[2] < 200 else nb[2]
    e['dp3f1_2026-11-29'] = dict(old_spec='CB5-12', new_spec='CB5-16', thread_body='P_M07_BEAM_CAP', overlap_mm3=round(vol, 3), engage_mm=eng, required_mm=3.0,
                                 rule='M-01 예외 DP3-EX1(조건부 승인): 물림 = 판 두께 3.0, 조임 목표 1.0 N.m · 상한 1.5 N.m + 분해 가능한 나사 고정제', tip_y=tip,
                                 tip_past_flange_mm=round((tip - 131.2) if nb[2] < 200 else (308.8 - tip), 2), tip_clear='끝 둘레 1 mm 안에 덮개 플랜지 탭 말고 다른 바디 0(inspect.clearance c_thread · c_static)', ok=abs(eng - 3.0) < 0.01)
    bolts_changed.append(e)
assert not rem_left
for tag in (':7)', ':8)'):
    n = [x for x in M if HEAD(x) == 'CB5-16_M07_NY' and x.endswith('CB5-16_M07_NY' + tag)][0]
    t = [(o, v) for o, v in ovl.get(n, []) if HEAD(o) == 'P_M07_BEAM']
    assert len(t) == 1, (n, t)
    ob = dict(bolt_by_name[n])
    eng = round(t[0][1] / ring, 2)
    ob['engage_mm'] = eng
    ob['dp3f1_2026-11-29'] = dict(old_spec=ob['spec'], new_spec=ob['spec'], thread_body='P_M07_BEAM', overlap_mm3=round(t[0][1], 3), engage_mm=eng, required_mm=7.5, ok=eng >= 7.5,
                                  note='볼트 그대로. v2.31.0에서 옛 끝 자리 채움 상자가 탭 구멍 안쪽 끝 1 mm를 막아 겹침 57.207이던 것을 다시 뚫음(Ø4.2, Y 311.9~320.1) -> 46.244')
    bolts_changed.append(ob)
print('bolts changed', len(bolts_changed), collections.Counter((b['spec'], b['engage_mm'], b['dp3f1_2026-11-29']['ok']) for b in bolts_changed))
json.dump({'parts': parts}, open('changed_parts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(bolts_changed, open('changed_bolts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(dict(removed=removed, changed=changed_keys, added=['U1_FRAME/' + n for n in added], loose=loose, saved_vs_session_diff=diff), open('changed_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if '--write' in sys.argv:
    assert not diff
    import shutil
    shutil.copyfile(PRJ + '/out/signatures.json', 'signatures_before_DP3F1.json')
    shutil.copyfile(PRJ + '/out/bolts.json', 'bolts_before_DP3F1.json')
    shutil.copyfile(PRJ + '/out/mach_props.json', 'mach_props_before_DP3F1.json')
    rm_names = [P[k]['name'] for k in removed]
    sys.path.insert(0, ENG)
    import ledger
    rc = ledger.main(['sigpatch', '--project', PRJ, '--parts', os.path.abspath('changed_parts.json'), '--removed', ','.join(removed + rm_names), '--bolts', os.path.abspath('changed_bolts.json')])
    S2 = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8'))
    B2 = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
    print('rc', rc, 'sig parts', len(S2['parts']), 'doc', S2['doc'], S2.get('doc_hash'), 'bolts_stale', S2.get('bolts_stale'), 'bolts', len(B2), 'unique', len({b['name'] for b in B2}),
          'CB5-12_M07_CAP left', sum(1 for b in B2 if 'CB5-12_M07_CAP' in b['name']), 'CB5-16_M07_CAP', sum(1 for b in B2 if 'CB5-16_M07_CAP' in b['name']))
    mp = json.load(open(PRJ + '/out/mach_props.json', encoding='utf-8'))
    w = parts['U1_FRAME/P_M07_BEAM']
    mp['P_M07_BEAM'] = dict(mp['P_M07_BEAM'], mats=[w['material']], mass_g=w['mass'])
    json.dump(mp, open(PRJ + '/out/mach_props.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('mach_props P_M07_BEAM', mp['P_M07_BEAM'])
