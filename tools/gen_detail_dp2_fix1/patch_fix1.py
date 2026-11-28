"""DP-2 수정 1회차 저장 뒤: 바뀐 볼트 1개만 서명 · 체결 목록에 고쳐 넣는다(ledger.py sigpatch). usage: python -X utf8 -B patch_fix1.py [--write]"""
import json, sys, os, shutil, math, q
ENG = 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools'
PRJ = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools'
OLDKEY = 'U2_TABLE/CB5-16_DP2 (U2_TABLE:1/U2_FLAP:1/CB5-16_DP2:15)'
NEW = 'STEP대기_CB5-14_DP2 (U2_TABLE:1/U2_FLAP:1/STEP대기_CB5-14_DP2:7)'
NEWKEY = 'U2_TABLE/' + NEW
S = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8')); P = S['parts']
BOL = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
src = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else None
if src:   # 저장본 CLI 측정
    m = json.load(open(src, encoding='utf-8'))
    if isinstance(m, list): m = m[-1]
    if 'results' in m: m = m['results'][-1]
    if 'result' in m and 'bodies' not in m: m = m['result']
else:
    m = q.unwrap('r_meas_session.json')['data']
M = {b['name']: b for b in m['bodies']}
r3 = lambda x: round(x, 3)
b = M[NEW]
bb = [r3(b['bbox']['min'][0]), r3(b['bbox']['max'][0]), r3(b['bbox']['min'][1]), r3(b['bbox']['max'][1]), r3(b['bbox']['min'][2]), r3(b['bbox']['max'][2])]
old = P[OLDKEY]
w = dict(old); w.update(name=NEW, bbox=bb, volume=r3(b['volume_mm3']), mass=r3(b['mass_g']), material=b['material'], bolt=True, spec='CB5-14')
pc = json.load(open('pre_check.json', encoding='utf-8'))
ov = [o for o in pc['rest']['overlaps']]; assert len(ov) == 1 and 'P_RX12C1_FLAP_BAR_XP' in (ov[0]['a'], ov[0]['b'])
vol = ov[0]['volume_mm3']; A_P = math.pi * (2.5 ** 2 - 2.1 ** 2); eng = round(vol / A_P, 2)
tap = [c for c in pc['topo_P_RX12C1_FLAP_BAR_XP'] if abs(c['axis'][2]) > 0.9][0]
bottom = tap['origin'][2] + min(tap['extent']); top = tap['origin'][2] + max(tap['extent'])
tip = bb[4]
ob = [x for x in BOL if x['name'] == old['name']]; assert len(ob) == 1; ob = ob[0]
e = dict(ob)
e.update(name=NEW, spec='CB5-14', bbox=bb, engage_mm=eng, temp_shape=True, material=b['material'], src='DP-2 디테일링 수정 1회차(v2.30.8) CB5-16 → CB5-14')
d0 = dict(ob.get('dp2_2026-11-28') or {}); d0['superseded_by'] = 'dp2_fix1_2026-11-28'; e['dp2_2026-11-28'] = d0
e['dp2_fix1_2026-11-28'] = dict(old_spec='CB5-16', new_spec='CB5-14', orig_spec='CB5-12', thread_body='P_RX12C1_FLAP_BAR_XP', tap_feature='RX12C1_FLAP_BAR_XP_TAP_1',
                                 pilot_hole_z=[r3(top), r3(bottom)], pilot_depth_mm=r3(top - bottom), bolt_tip_z=tip, entry_mm=r3(top - tip), overlap_mm3=round(vol, 3), engage_mm=eng, required_mm=7.5,
                                 tip_to_hole_bottom_mm=r3(tip - bottom), tap_callout='M5 유효 깊이 ≥ 9(밑구멍 12)', ok=eng >= 7.5 - 1e-6 and tip - bottom >= 2.4,
                                 why='검증 문제(기준): CB5-16은 밑구멍 깊이 12에 11 들어가 끝–바닥 1.0(1.25피치) — 불완전 나사에 걸려 머리가 앉기 전에 멈춘다(M-01)')
print(json.dumps(w, ensure_ascii=False)); print(json.dumps(e['dp2_fix1_2026-11-28'], ensure_ascii=False))
json.dump({'parts': {NEWKEY: w}}, open('changed_parts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump([e], open('changed_bolts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if '--write' in sys.argv:
    shutil.copyfile(PRJ + '/out/signatures.json', 'signatures_before_fix1.json'); shutil.copyfile(PRJ + '/out/bolts.json', 'bolts_before_fix1.json')
    sys.path.insert(0, ENG); import ledger
    rc = ledger.main(['sigpatch', '--project', PRJ, '--parts', os.path.abspath('changed_parts.json'), '--removed', ','.join([OLDKEY, old['name']]), '--bolts', os.path.abspath('changed_bolts.json')])
    S2 = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8')); B2 = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
    import collections
    print('rc', rc, 'sig parts', len(S2['parts']), 'doc', S2['doc'], S2.get('doc_hash'), 'bolts_stale', S2.get('bolts_stale'), 'bolts', len(B2), 'unique', len({x['name'] for x in B2}))
    print(collections.Counter(x['spec'] for x in B2 if x['spec'] in ('CB5-16', 'CB5-14', 'CB5-12', 'CB5-20', 'CB5-22', 'SFB5-16')))
    print('old key gone', OLDKEY not in S2['parts'], 'new key in', NEWKEY in S2['parts'], 'old bolt gone', not [x for x in B2 if x['name'] == old['name']])
