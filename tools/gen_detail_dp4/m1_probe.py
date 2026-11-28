"""수정 1회차 볼트 검사: 머리 위 Ø8.5 x 30 프로브(삽입 · 렌치) + 끼우는 길 프로브(M-12) + 블록 턱 탭 둘레 살(광선). 프로브는 재고 지운다."""
import json, math, fx, nb
from fx import ex, C, run, clr
RB = 'P_RXDC03_RISER_BRKT_밀링'; LG = 'P_RXDC03_LEAD_GUIDE_3DP'; T2 = 'P_RXDC03_T2_GUIDE_판금'; CL = 'P_RXDC03_BEAM_CLAMP_판금'
P = []
cm = [C('component.activate', component='U4_XCAR')]
for n, x, y in (('R1', -288, 90), ('R2', -278, 90), ('R3', -265.25, 79)):
    cm.append(C('solid.cylinder', radius=4.25, height=30, base=[x, y, 261.05], axis='Z', operation='new', name='PRB_' + n, body_name='PRB_' + n)); P.append('PRB_' + n)
cm.append(C('solid.cylinder', radius=4.25, height=30, base=[-284, 75, 197.95], axis='Z', operation='new', name='PRB_T2', body_name='PRB_T2')); P.append('PRB_T2')
cm.append(C('solid.box', corner=[-318.6, 65, 487.05], length=60.6, width=32, height=247, operation='new', name='PRB_PATH_R', body_name='PRB_PATH_R')); P.append('PRB_PATH_R')
cm.append(C('component.activate', component='U4_PRESS'))
for n, z in (('G1', 150), ('G2', 159)):
    cm.append(C('solid.cylinder', radius=4.25, height=30, base=[-287.05, 80, z], axis='X', operation='new', name='PRB_' + n, body_name='PRB_' + n)); P.append('PRB_' + n)
cm.append(C('component.activate', component='U4_XAXIS'))
for n, z in (('C1', 619.5), ('C2', 631.5)):
    cm.append(C('solid.cylinder', radius=4.25, height=30, base=[-345, 81.95, z], axis='Y', operation='new', name='PRB_' + n, body_name='PRB_' + n)); P.append('PRB_' + n)
cm.append(C('component.activate', component='root'))
run('prb_build', cm, rec=False)
m = fx.meas(P, 'm_prb')
for k, v in m.items(): print(k, v['bbox'])
SELF = [RB, LG, T2, CL, 'CB5-16_RXDC03_RISER_1', 'CB5-16_RXDC03_RISER_2', 'CB5-16_RXDCC1_RISER_3', 'CB5-16_RXDC03_GUIDE_1', 'CB5-16_RXDC03_GUIDE_2', 'CB5-12_RXDC03_T2_1', 'CB5-12_RXDC03_T2_2', 'CB5-12_RXDC03_CLAMP_1', 'CB5-12_RXDC03_CLAMP_2']
boxes = [v['bbox'][:1] + v['bbox'][3:4] + v['bbox'][1:2] + v['bbox'][4:5] + v['bbox'][2:3] + v['bbox'][5:6] for v in m.values()]
AG = sorted((set(nb.neighbors([], 4, boxes)) | set(SELF)) - set(P) - {'P_RXDC03_RISER_BRKT_판금', 'P_RXDC03_LEAD_GUIDE_판금', 'CB5-12_RXDC03_RISER_1', 'CB5-12_RXDC03_RISER_2', 'CB4-12_RXDCC1_RISER_3', 'CB5-12_RXDC03_GUIDE_1', 'CB5-12_RXDC03_GUIDE_2'})
print('against', len(AG))
R = {'bolts': clr('prb_bolts', [p for p in P if p != 'PRB_PATH_R'], AG, 3.0, 20), 'path_riser': clr('prb_path', ['PRB_PATH_R'], [a for a in AG if a not in (RB,)], 1.0, 20)}
run('prb_del', [C('timeline.delete', features=['PRB_' + n for n in ('R1', 'R2', 'R3', 'T2', 'PATH_R', 'G1', 'G2', 'C1', 'C2')])], rec=False)
# 블록 턱 탭 둘레 살: 구멍 벽 바로 바깥(살 속)에서 4방향 광선 — 블록에서 처음 만나는 면까지
rays = []; tags = []
for n, x, y, z in (('RS1', -288, 90, 243), ('RS2', -278, 90, 243), ('RS3', -265.25, 79, 243), ('T2_1', -296, 75, 241), ('T2_2', -284, 75, 241)):
    for dn, d in (('+X', (1, 0, 0)), ('-X', (-1, 0, 0)), ('+Y', (0, 1, 0)), ('-Y', (0, -1, 0))):
        rays.append({'origin': [x + 2.15 * d[0], y + 2.15 * d[1], z], 'dir': list(d)}); tags.append((n, dn))
d = ex('pick_wall', 'view.pick', rays=rays, all=True)['data']
H = d.get('hits', d.get('results', d)) if isinstance(d, dict) else d
W = {}
for (n, dn), ry, h in zip(tags, rays, H):
    hs = h if isinstance(h, list) else (h.get('hits') if isinstance(h, dict) and 'hits' in h else [h])
    b = [x for x in hs if x and x.get('body') == 'P_RX19_BLOCK_밀링']
    if b:
        p = b[0]['point']; W.setdefault(n, {})[dn] = round(math.dist(p, ry['origin']) + 0.05, 2)
for k, v in W.items(): print(k, v)
R['tap_wall_mm'] = W
json.dump(R, open('probe1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
i = fx.tool('insp_p', 'inspect_design', measure=False, sketches=False, timeline='summary', bodies='names', joints=False)['data']
fe = i['timeline']['features'] if isinstance(i['timeline'], dict) else i['timeline']
print('features', len(fe), 'bodies', len(i['bodies']), 'errors', sum(1 for f in fe if f.get('error')))
