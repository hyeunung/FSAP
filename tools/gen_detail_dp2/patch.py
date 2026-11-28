"""DP-2 저장 뒤: 저장본 측정(v_meas_out.json) ↔ 서명 → 바뀐 것만 서명 · 체결 목록에 고쳐 넣는다(ledger.py sigpatch).
usage: python -X utf8 -B patch.py <measure json(저장본)> [--write]"""
import json, sys, re, math, os, collections
ENG = 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools'
PRJ = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools'
m = json.load(open(sys.argv[1], encoding='utf-8'))
if 'results' in m: m = m['results'][-1]
if 'result' in m and 'bodies' not in m: m = m['result']
S = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8')); P = S['parts']
BOL = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
r3 = lambda x: round(x, 3)
M = {b['name']: b for b in m['bodies']}
assert len(M) == len(m['bodies'])
def bb6(b): return [r3(b['bbox']['min'][0]), r3(b['bbox']['max'][0]), r3(b['bbox']['min'][1]), r3(b['bbox']['max'][1]), r3(b['bbox']['min'][2]), r3(b['bbox']['max'][2])]
def tail(k, v):
    t = k.split('/', 1)[1] if '/' in k else k
    if t in M: return t
    i = k.find(v['name'])
    return k[i:] if i >= 0 and k[i:] in M else None
used = {}; removed = []; parts = {}
for k, v in P.items():
    n = tail(k, v)
    if n is None: removed.append(k); continue
    used[n] = k; b = M[n]
    w = dict(v); w['bbox'] = bb6(b); w['volume'] = r3(b['volume_mm3']); w['mass'] = r3(b['mass_g']); w['material'] = b['material']
    db = max(abs(a - c) for a, c in zip(v['bbox'], w['bbox'])); dv = abs((v.get('volume') or 0) - w['volume'])
    if db > 0.05 or dv > max(1e-4 * abs(v.get('volume') or 0), 0.01) or v.get('material') != w['material']:
        parts[k] = w
changed_keys = list(parts)
added = [n for n in M if n not in used]
print('measured', len(M), 'changed', len(changed_keys), 'removed', len(removed), 'added', len(added))
# 새 볼트 ↔ 없어진 볼트: 옛 상자가 새 상자 안에 든다(머리 쪽 같음)
def inside(o, n, tol=0.06): return all(n[2 * i] - tol <= o[2 * i] and o[2 * i + 1] <= n[2 * i + 1] + tol for i in range(3))
clr = json.load(open('pre_clr_final.json', encoding='utf-8'))
ovl = collections.defaultdict(list)
for k, v in clr['overlaps'].items():
    a, b = k.split(' | '); ovl[a].append((b, v)); ovl[b].append((a, v))
near = collections.defaultdict(list)
for k, v in clr['near'].items():
    a, b = k.split(' | '); near[a].append((b, v[0])); near[b].append((a, v[0]))
SPEC = lambda n: re.sub(r'^STEP대기_', '', n).split('_')[0]
bolt_by_name = {b['name']: b for b in BOL}
rem_left = set(removed); pairs = []; bolts_changed = []
A_T = math.pi * (2.5 ** 2 - 2.067 ** 2); A_P = math.pi * (2.5 ** 2 - 2.1 ** 2)
for n in added:
    nb = bb6(M[n])
    cand = [k for k in rem_left if inside(P[k]['bbox'], nb)]
    assert len(cand) == 1, (n, cand)
    k = cand[0]; rem_left.discard(k); old = P[k]
    spec = SPEC(n)
    w = dict(old); w.update(name=n, bbox=nb, volume=r3(M[n]['volume_mm3']), mass=r3(M[n]['mass_g']), material=M[n]['material'], bolt=True, spec=spec)
    newkey = k.split('/', 1)[0] + '/' + n
    parts[newkey] = w; pairs.append((k, newkey))
    ob = bolt_by_name[old['name']]
    th = [(o, v) for o, v in ovl.get(n, []) if v > 1.0]
    assert len(th) == 1, (n, th)
    tb, vol = th[0]
    eng = round(vol / (A_T if tb.startswith('HNTT8') else A_P), 2)
    gaps = [d for o, d in near.get(n, []) if o.startswith('HFS8') and d > 0.01]
    e = dict(ob); f0 = dict(ob.get('fasten_2026-11-28') or {})
    e.update(name=n, spec=spec, bbox=nb, engage_mm=eng, old_name=old['name'], old_spec=old['spec'], temp_shape=n.startswith('STEP대기_'), material=M[n]['material'], src='DP-2 디테일링(v2.30.7) 길이 바꿈')
    if ob.get('tap', '').startswith('M5 깊이'): e['tap'] = 'M5 깊이 12(밑구멍 15)'
    f0['superseded_by'] = 'dp2_2026-11-28'
    e['fasten_2026-11-28'] = f0
    e['dp2_2026-11-28'] = dict(old_spec=old['spec'], new_spec=spec, thread_body=re.sub(r' \(.*', '', tb), overlap_mm3=round(vol, 2), engage_mm=eng, required_mm=7.5,
                               tip_to_slot_bottom_mm=(round(min(gaps), 2) if gaps else ('>=1.0' if tb.startswith('HNTT8') else None)), ok=eng >= 7.5 - 1e-6)
    bolts_changed.append(e)
assert not rem_left, rem_left
# 인서트 볼트 4: 지름 · 길이 · 자리 그대로, 물림 실측만 고쳐 적는다
ins = json.load(open('insert_engage.json', encoding='utf-8'))
for x in ins:
    bn = x['a'] if x['a'].startswith('CB5-12_M06') else x['b']
    ob = dict(bolt_by_name[bn]); f0 = dict(ob.get('fasten_2026-11-28') or {}); f0['superseded_by'] = 'dp2_2026-11-28'; ob['fasten_2026-11-28'] = f0
    ob['engage_mm'] = 7.56
    ob['dp2_2026-11-28'] = dict(old_spec='CB5-12', new_spec='CB5-12', thread_body='MBIS5-6.5-8', overlap_mm3=round(x['vol'], 2), engage_mm=7.56, required_mm=7.5, ok=True,
                                note='인서트 바디 X -90~-82(볼트 머리 밑에서 3.0~3.6 → 11.0~11.6), 나사 구멍 길이 7.56 전부에 볼트 생크가 지나감. 체결부의 -5.0~+3.2는 좌표 오류 — 인서트는 옮기지 않았다')
    bolts_changed.append(ob)
eng_all = [b['dp2_2026-11-28']['engage_mm'] for b in bolts_changed]
print('bolts changed', len(bolts_changed), 'engage min', min(eng_all), 'max', max(eng_all), 'not ok', [b['name'] for b in bolts_changed if not b['dp2_2026-11-28']['ok']])
print(collections.Counter((b['dp2_2026-11-28']['old_spec'], b['dp2_2026-11-28']['new_spec'], b['dp2_2026-11-28']['engage_mm'], str(b['dp2_2026-11-28'].get('tip_to_slot_bottom_mm'))) for b in bolts_changed))
json.dump({'parts': parts}, open('changed_parts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(bolts_changed, open('changed_bolts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(dict(removed=removed, pairs=pairs, changed=changed_keys), open('changed_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if '--write' in sys.argv:
    import shutil
    shutil.copyfile(PRJ + '/out/signatures.json', 'signatures_before_DP2.json'); shutil.copyfile(PRJ + '/out/bolts.json', 'bolts_before_DP2.json')
    rm_names = [P[k]['name'] for k in removed]
    sys.path.insert(0, ENG); import ledger
    rc = ledger.main(['sigpatch', '--project', PRJ, '--parts', os.path.abspath('changed_parts.json'), '--removed', ','.join(removed + rm_names), '--bolts', os.path.abspath('changed_bolts.json')])
    S2 = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8')); B2 = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
    print('rc', rc, 'sig parts', len(S2['parts']), 'doc', S2['doc'], S2.get('doc_hash'), 'bolts_stale', S2.get('bolts_stale'), 'bolts', len(B2), 'unique', len({b['name'] for b in B2}))
    # 가공품 질량 · 재질 표
    mp = json.load(open(PRJ + '/out/mach_props.json', encoding='utf-8'))
    for k in changed_keys:
        n = P[k]['name']
        if n in mp: mp[n] = dict(mp[n], mats=[parts[k]['material']], mass_g=parts[k]['mass'])
    json.dump(mp, open(PRJ + '/out/mach_props.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
