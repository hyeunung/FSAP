"""DP-4 저장 뒤: 저장본 전수 측정(v_meas_out.json) <-> 세션 마지막 측정 <-> 서명 -> 바뀐 것만 서명 · 체결 목록에 고쳐 넣는다(ledger.py sigpatch).
usage(작업 폴더 tools/out/detail/DP-4/m0 에서): python -X utf8 -B ../../../../gen_detail_dp4/patch.py v_meas_out.json [--write]"""
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
# 서명 전체와 견줘 바뀐 것(잎 이름으로)
changed = {}
for k, v in P.items():
    n = k.split('/', 1)[1] if '/' in k else k
    b = M.get(n) or M.get(v['name'])
    if b is None: continue
    w = dict(v); w.update(bbox=bb6(b), volume=r3(b['volume_mm3']), mass=r3(b['mass_g']), material=b['material'])
    db = max(abs(a - c) for a, c in zip(v['bbox'], w['bbox'])); dv = abs((v.get('volume') or 0) - w['volume'])
    if db > 0.05 or dv > max(1e-4 * abs(v.get('volume') or 0), 0.01) or v.get('material') != w['material']:
        if n.startswith('TU0') and dv <= 0.01: continue
        changed[k] = w
EXP = {'U4_WHEEL_N/P_M08_TUBE_BRKT_U6', 'U4_XCAR/P_RXDC03_T2_GUIDE_판금', 'U4_XAXIS/P_RXDC03_BEAM_CLAMP_판금',
       'CB5-12_RXDC03_CLAMP_1/CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_2/CB5-12_RXDC03_CLAMP_2'}
print('changed', sorted(changed), 'unexpected', sorted(set(changed) - EXP), 'missing', sorted(EXP - set(changed)))
for k in sorted(changed):
    print(' ', k, P[k]['bbox'], '->', changed[k]['bbox'], P[k]['volume'], '->', changed[k]['volume'], P[k]['mass'], '->', changed[k]['mass'], P[k]['material'], '->', changed[k]['material'])
bolts_changed = []
for b in BOL:
    if b['name'] in ('CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_2'):
        e = dict(b); nb = bb6(M[b['name']])
        e.update(pos=[b['pos'][0], 116, b['pos'][2]], bbox=nb, engage_mm=8.0,
                 tap=b['tap'] + ' · DP-4: 받침 t3 -> t4라 머리 자리 Y 117 -> 116, 볼트 끝 Y 129 -> 128(보 벽 안쪽 면)',
                 src='DP-4 디테일링(v2.31.2) 자리 옮김 -Y 1(받침 두께 +1), 볼트 그대로 CB5-12')
        e['dp4_2026-11-29'] = dict(old_pos=b['pos'], new_pos=e['pos'], thread_body='P_M07_BEAM', overlap_mm3=46.244, engage_mm=8.0, required_mm=7.5, ok=True,
                                   access='머리 위 -Y 방향 Ø8.5 x 30 프로브 겹침 0(가장 가까운 것 STEP대기_MR-PWS1CBL5M-A2-H_FIX 2.8)')
        bolts_changed.append(e)
assert len(bolts_changed) == 2
json.dump({'parts': changed}, open('changed_parts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(bolts_changed, open('changed_bolts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if '--write' in sys.argv:
    assert not diff and set(changed) == EXP
    for f in ('signatures', 'bolts'):
        if not os.path.exists(f + '_before_DP4.json'): shutil.copyfile(PRJ + '/out/%s.json' % f, f + '_before_DP4.json')
    sys.path.insert(0, ENG)
    import ledger
    rc = ledger.main(['sigpatch', '--project', PRJ, '--parts', os.path.abspath('changed_parts.json'), '--bolts', os.path.abspath('changed_bolts.json')])
    S2 = json.load(open(PRJ + '/out/signatures.json', encoding='utf-8')); B2 = json.load(open(PRJ + '/out/bolts.json', encoding='utf-8'))
    print('rc', rc, 'sig parts', len(S2['parts']), 'doc', S2['doc'], S2.get('doc_hash'), 'bolts_stale', S2.get('bolts_stale'), 'bolts', len(B2),
          [(b['name'], b['pos'], b['engage_mm']) for b in B2 if 'RXDC03_CLAMP' in b['name']])
