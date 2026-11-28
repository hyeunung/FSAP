"""DP-4 수정 1회차 저장 뒤: 저장본 전수 측정(v_meas_out.json) <-> 세션 마지막 측정 <-> 서명 -> 바뀐 것만 서명 · 체결 목록에 고쳐 넣는다(ledger.py sigpatch).
usage(작업 폴더 tools/out/detail/DP-4/m1 에서): python -X utf8 -B ../../../../gen_detail_dp4/m1_patch.py v_meas_out.json [--write]"""
import json, sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q
ENG = 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools'
PRJ = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools'
m = json.load(open(sys.argv[1], encoding='utf-8'))
if isinstance(m, list): m = m[-1]
if 'results' in m: m = m['results'][-1]
if 'result' in m and 'bodies' not in m: m = m['result']
S = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8')); P = S['parts']
BOL = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
r3 = lambda x: round(x, 3)
M = {b['name']: b for b in m['bodies']}
def bb6(b): return [r3(b['bbox']['min'][0]), r3(b['bbox']['max'][0]), r3(b['bbox']['min'][1]), r3(b['bbox']['max'][1]), r3(b['bbox']['min'][2]), r3(b['bbox']['max'][2])]
SES = {b['name']: b for b in q.unwrap('r_meas_final.json')['data']['bodies']}
diff = [n for n in set(M) | set(SES) if n not in M or n not in SES or max(abs(a - c) for a, c in zip(bb6(M[n]), bb6(SES[n]))) > 0.01
        or abs(M[n]['volume_mm3'] - SES[n]['volume_mm3']) > max(1e-5 * abs(SES[n]['volume_mm3']), 0.01) or M[n].get('material') != SES[n].get('material')]
print('saved file bodies', len(M), 'session', len(SES), 'different', len(diff), diff[:6], 'open bodies', [n for n, b in M.items() if not b.get('closed')][:5])
NEW = {  # 새 서명 키: (unit, component, bolt spec)
    'U4_XCAR/P_RXDC03_RISER_BRKT_밀링': ('U4_XCAR', 'U4_XCAR', ''), 'U4_PRESS/P_RXDC03_LEAD_GUIDE_3DP': ('U4_PRESS', 'U4_PRESS', ''),
    'CB5-16_RXDC03_RISER_1/CB5-16_RXDC03_RISER_1': ('U4_XCAR', 'CB5-16_RXDC03_RISER_1', 'CB5-16'), 'CB5-16_RXDC03_RISER_2/CB5-16_RXDC03_RISER_2': ('U4_XCAR', 'CB5-16_RXDC03_RISER_2', 'CB5-16'),
    'CB5-16_RXDCC1_RISER_3/CB5-16_RXDCC1_RISER_3': ('U4_XCAR', 'CB5-16_RXDCC1_RISER_3', 'CB5-16'),
    'CB5-16_RXDC03_GUIDE_1/CB5-16_RXDC03_GUIDE_1': ('U4_PRESS', 'CB5-16_RXDC03_GUIDE_1', 'CB5-16'), 'CB5-16_RXDC03_GUIDE_2/CB5-16_RXDC03_GUIDE_2': ('U4_PRESS', 'CB5-16_RXDC03_GUIDE_2', 'CB5-16')}
REMOVED = ['U4_XCAR/P_RXDC03_RISER_BRKT_판금', 'U4_PRESS/P_RXDC03_LEAD_GUIDE_판금', 'CB5-12_RXDC03_RISER_1/CB5-12_RXDC03_RISER_1', 'CB5-12_RXDC03_RISER_2/CB5-12_RXDC03_RISER_2',
           'CB4-12_RXDCC1_RISER_3/CB4-12_RXDCC1_RISER_3', 'CB5-12_RXDC03_GUIDE_1/CB5-12_RXDC03_GUIDE_1', 'CB5-12_RXDC03_GUIDE_2/CB5-12_RXDC03_GUIDE_2']
assert all(k in P for k in REMOVED), [k for k in REMOVED if k not in P]
gone = {k.split('/', 1)[1] for k in REMOVED}
assert not (gone & set(M)), gone & set(M)
changed = {}
for k, v in P.items():
    if k in REMOVED: continue
    n = k.split('/', 1)[1] if '/' in k else k
    b = M.get(n) or M.get(v['name'])
    if b is None: continue
    w = dict(v); w.update(bbox=bb6(b), volume=r3(b['volume_mm3']), mass=r3(b['mass_g']), material=b['material'])
    db = max(abs(a - c) for a, c in zip(v['bbox'], w['bbox'])); dv = abs((v.get('volume') or 0) - w['volume'])
    if db > 0.05 or dv > max(1e-4 * abs(v.get('volume') or 0), 0.01) or v.get('material') != w['material']:
        if n.startswith('TU0') and dv <= 0.01: continue
        changed[k] = w
for k, (unit, comp, spec) in NEW.items():
    n = k.split('/', 1)[1]; b = M[n]
    changed[k] = dict(name=n, unit=unit, component=comp, bbox=bb6(b), volume=r3(b['volume_mm3']), mass=r3(b['mass_g']), material=b['material'], bolt=bool(spec), spec=spec)
EXP = set(NEW) | {'U4_XCAR/P_RXDC03_T2_GUIDE_판금', 'U4_XAXIS/P_RXDC03_BEAM_CLAMP_판금', 'U4_XCAR/P_RX19_BLOCK_밀링',
                  'CB5-12_RXDC03_T2_2/CB5-12_RXDC03_T2_2', 'CB5-12_RXDC03_CLAMP_1/CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_2/CB5-12_RXDC03_CLAMP_2'}
print('changed', len(changed), 'unexpected', sorted(set(changed) - EXP), 'missing', sorted(EXP - set(changed)))
for k in sorted(changed):
    o = P.get(k)
    print(' ', k, (o['bbox'] if o else 'new'), '->', changed[k]['bbox'], (o['volume'] if o else ''), '->', changed[k]['volume'], changed[k]['mass'], changed[k]['material'])
B = {b['name']: b for b in BOL}
bolts_changed = []
def fast(old, new, pos, axis, unit, parts, engage, tap, thread_body, ov, src, access):
    e = dict(B[old]) if old in B else {}
    for kk in [x for x in e if x.startswith('fasten_') or x.startswith('dp4_')]: e.pop(kk)
    e.update(name=new, spec=new.split('_')[0], pos=pos, axis=axis, unit=unit, parts=parts, engage_mm=engage, tap=tap, pose='θ0·J_U4_X 0 월드', component=new, bbox=bb6(M[new]),
             temp_shape=False, material=M[new]['material'], src=src)
    e['dp4f1_2026-11-29'] = dict(old_name=old, old_pos=B[old]['pos'] if old in B else None, new_pos=pos, thread_body=thread_body, overlap_mm3=ov, engage_mm=engage, required_mm=7.5, ok=engage >= 7.5, access=access)
    bolts_changed.append(e)
RB, LG, BLK, SW = 'P_RXDC03_RISER_BRKT_밀링', 'P_RXDC03_LEAD_GUIDE_3DP', 'P_RX19_BLOCK_밀링', 'P_RX19_SWING_밀링'
acc = '머리 위 Ø8.5 x 30 프로브 겹침 0(probe1.json)'
fast('CB5-12_RXDC03_RISER_1', 'CB5-16_RXDC03_RISER_1', [-288, 90, 256], [0, 0, -1], 'U4_XCAR', [RB, BLK], 10.0, 'M5 관통 탭 14(블록 선반 Z 236~250, RXDC03_BLK_TAP_RS_1)', BLK, 57.805, 'DP-4 수정 1회차(v2.31.3): CB5-12 -> CB5-16(밑판 t6), 탭 막힌 깊이 10 -> 관통', acc)
fast('CB5-12_RXDC03_RISER_2', 'CB5-16_RXDC03_RISER_2', [-278, 90, 256], [0, 0, -1], 'U4_XCAR', [RB, BLK], 10.0, 'M5 관통 탭 14(블록 선반 Z 236~250, RXDC03_BLK_TAP_RS_2)', BLK, 57.805, 'DP-4 수정 1회차(v2.31.3): CB5-12 -> CB5-16(밑판 t6), 탭 막힌 깊이 10 -> 관통', acc)
fast('CB4-12_RXDCC1_RISER_3', 'CB5-16_RXDCC1_RISER_3', [-265.25, 79, 256], [0, 0, -1], 'U4_XCAR', [RB, BLK], 10.0, 'M5 관통 탭 14(블록 선반 Z 236~250, DP4_BLK_TAP_RS_3_M5)', BLK, 57.805, 'DP-4 수정 1회차(v2.31.3): CB4-12 (-280.5, 78.25) -> CB5-16 귀 자리 (-265.25, 79)(U-12, DP4-EX1)', acc + ' · 관 TU0604_M08P_U4_B_U4 1.75')
fast('CB5-12_RXDC03_GUIDE_1', 'CB5-16_RXDC03_GUIDE_1', [-252, 80, 150], [1, 0, 0], 'U4_PRESS', [LG, SW], 10.0, 'M5 관통 탭 12(그네 텅 X -246~-234) · 조임 1.5 N·m(PET-CF 좌면)', SW, 57.805, 'DP-4 수정 1회차(v2.31.3): CB5-12 -> CB5-16(좌면 패드 t6, DP4-EX2)', acc)
fast('CB5-12_RXDC03_GUIDE_2', 'CB5-16_RXDC03_GUIDE_2', [-252, 80, 159], [1, 0, 0], 'U4_PRESS', [LG, SW], 10.0, 'M5 관통 탭 12(그네 텅 X -246~-234) · 조임 1.5 N·m(PET-CF 좌면)', SW, 53.681, 'DP-4 수정 1회차(v2.31.3): CB5-12 -> CB5-16(좌면 패드 t6, DP4-EX2). 탭 축이 텅 X -246 면 윗변에서 1.0이라 물림 부피가 57.805보다 작다(기록만 — 그네는 RX-16 보류 자리가 아니나 묶음 밖)', acc)
T2, CL = 'P_RXDC03_T2_GUIDE_판금', 'P_RXDC03_BEAM_CLAMP_판금'
fast('CB5-12_RXDC03_T2_2', 'CB5-12_RXDC03_T2_2', [-284, 75, 233], [0, 0, 1], 'U4_XCAR', [T2, BLK], 9.0, 'M5 깊이 10(블록 선반 밑 Z 236~246, RXDC03_BLK_TAP_T2_2)', BLK, 52.025, 'DP-4 수정 1회차(v2.31.3): 자리 (-286, 75) -> (-284, 75)(M-04 구멍 사이, DP4-EX4)', '머리 밑 Ø8.5 x 30 프로브 겹침 0')
fast('CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_1', [-345, 117, 619.5], [0, 1, 0], 'U4_XAXIS', [CL, 'P_M07_BEAM'], 8.0, 'M5 관통 탭 8(보 앞 벽, RXDCC1_BEAM_TAP_1)', 'P_M07_BEAM', 46.244, 'DP-4 수정 1회차(v2.31.3): 받침 t4 -> t3라 머리 자리 Y 116 -> 117(DP4-EX3)', '머리 위 -Y 방향 Ø8.5 x 30 프로브 겹침 0')
fast('CB5-12_RXDC03_CLAMP_2', 'CB5-12_RXDC03_CLAMP_2', [-345, 117, 631.5], [0, 1, 0], 'U4_XAXIS', [CL, 'P_M07_BEAM'], 8.0, 'M5 관통 탭 8(보 앞 벽, RXDCC1_BEAM_TAP_2 — Z 630 -> 631.5)', 'P_M07_BEAM', 46.244, 'DP-4 수정 1회차(v2.31.3): 머리 자리 Y 116 -> 117, Z 630 -> 631.5(DP4-EX3)', '머리 위 -Y 방향 Ø8.5 x 30 프로브 겹침 0')
BREM = ['CB5-12_RXDC03_RISER_1', 'CB5-12_RXDC03_RISER_2', 'CB4-12_RXDCC1_RISER_3', 'CB5-12_RXDC03_GUIDE_1', 'CB5-12_RXDC03_GUIDE_2']
json.dump({'parts': changed}, open('changed_parts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(bolts_changed, open('changed_bolts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(dict(removed_parts=REMOVED, removed_bolts=BREM), open('removed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if '--write' in sys.argv:
    assert not diff and set(changed) == EXP, (diff[:5], sorted(set(changed) ^ EXP))
    for f in ('signatures', 'bolts'):
        if not os.path.exists(f + '_before_DP4F1.json'): shutil.copyfile(PRJ + '/out/%s.json' % f, f + '_before_DP4F1.json')
    sys.path.insert(0, ENG)
    import ledger
    rc = ledger.main(['sigpatch', '--project', PRJ, '--parts', os.path.abspath('changed_parts.json'), '--removed', ','.join(REMOVED), '--bolts', os.path.abspath('changed_bolts.json')])
    B2 = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
    left = [b['name'] for b in B2 if b['name'] in BREM]
    if left:   # 없어진 볼트 이름이 체결 목록에 남았으면 뺀다(sigpatch는 바뀐 이름만 갈아 끼운다)
        B2 = [b for b in B2 if b['name'] not in BREM]
        json.dump(B2, open(PRJ + '/out/bolts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    S2 = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8'))
    print('rc', rc, 'sig parts', len(S2['parts']), 'doc', S2['doc'], S2.get('doc_hash'), 'bolts_stale', S2.get('bolts_stale'), 'bolts', len(B2), 'removed-left', left,
          [(b['name'], b['pos'], b['engage_mm']) for b in B2 if 'RXDC03' in b['name'] or 'RXDCC1' in b['name']])
