# -*- coding: utf-8 -*-
"""디테일링 DP-2 수정 1회차 (v0.6.7) T01 회전 묶음 — 바뀐 하중 부품 손계산(해석부, 2026-10-31).

해석 못 함 — 환경 없음(자료대기 D-16). 손계산 + 엔진 handcalc(import, 엔진 폴더는 읽기만).
입력: tools/out/detail/DP-2/stepout/ 의 v0.6.7 임시 STEP 13개(너트판 6, 누름판 6, 기둥 1). 두께·구멍 자리는 STEP에서 읽어 확인.
하중: 지난 회차 fea/results/detail_DP-2_handcalc.json(v0.6.6)과 같은 식·같은 하중(T01 2회차 링 반력) + 바뀐 질량(너트판·누름판·CB5-18, LBNR4 빠짐).
E-19: 같은 형상 반복(너트판 6, 누름판 6)은 STEP 서명(bbox 크기·면 Z·구멍 수)으로 묶고 하중 최대 자리 하나로 판정.
단위 mm, N, MPa, kg.  실행: python -B fea/cases/detail_DP-2_fea1_handcalc.py → fea/results/detail_DP-2_fea1_handcalc.json
"""
import json, math, os, re, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENG = os.path.abspath(os.path.join(ROOT, '..', 'MechDesign_Engine', 'engine', 'tools'))
sys.path.insert(0, ENG)
import handcalc as HC                                   # 엔진 도구(읽기만)
STEPDIR = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-2', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'detail_DP-2_fea1_handcalc.json')
T01 = json.load(open(os.path.join(ROOT, 'fea', 'results', 'mech_T01_fea1_handcalc.json'), encoding='utf-8'))
PREV = json.load(open(os.path.join(ROOT, 'fea', 'results', 'detail_DP-2_handcalc.json'), encoding='utf-8'))
AX = (0.0, -700.0); g = 9.81; pi = math.pi
MAT = {'SUS304': (193000.0, 205.0), 'A5052': (70300.0, 175.0), 'PET-CF': (4000.0, 20.0)}
NG = 3.0; SF_REQ, SF_MIS, SF_BREAK = 3.0, 2.0, 1.2
F_CYL = 0.5 * pi * 16 ** 2 / 4
R = dict(method='손계산(표준 라이브러리 + 엔진 handcalc). 해석 못 함 — 환경 없음(D-16)', step=[], groups={}, parts={}, bolts={}, notes=[])


def read_step(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    ent = {int(m.group(1)): m.group(2).replace('\n', '') for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', txt, re.S)}
    def pt(i):
        return tuple(float(x) for x in re.search(r"\(([^()]*)\)\)\s*$", ent[i]).group(1).split(','))
    cyl, verts = [], []
    for i, s in ent.items():
        m = re.match(r"CYLINDRICAL_SURFACE\('[^']*',#(\d+),([-\d.Ee+]+)\)", s)
        if m:
            a = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+)", ent[int(m.group(1))])
            p = pt(int(a.group(1))); d = pt(int(a.group(2)))
            if abs(abs(d[2]) - 1) < 1e-6:
                cyl.append(dict(R=round(float(m.group(2)), 3), x=round(p[0], 2), y=round(p[1], 2),
                                r=round(math.hypot(p[0] - AX[0], p[1] - AX[1]), 2),
                                th=round(math.degrees(math.atan2(p[1] - AX[1], p[0] - AX[0])), 2)))
        m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", s)
        if m:
            verts.append(pt(int(m.group(1))))
    zs = sorted(set(round(v[2], 2) for v in verts))
    bb = [[round(min(v[k] for v in verts), 2), round(max(v[k] for v in verts), 2)] for k in range(3)]
    return dict(cyl=cyl, z=zs, bbox=bb)


G = {f[:-5]: read_step(os.path.join(STEPDIR, f)) for f in sorted(os.listdir(STEPDIR)) if f.endswith('.step')}
NEW = [k for k in G if 'NUTPLATE' in k or 'FOOTPLATE' in k] + ['P_T01_POST']


def chk(part, what, got, want, tol=0.3):
    ok = abs(got - want) <= tol
    R['step'].append(dict(part=part, what=what, step=got, used=want, ok=ok))
    return got


def uniq_holes(part, Rr):
    seen = {}
    for c in G[part]['cyl']:
        if abs(c['R'] - Rr) < 0.01:
            seen[(round(c['x'], 1), round(c['y'], 1))] = c
    return list(seen.values())


# ------------------------------------------------------------------ STEP 대조 + 묶음(E-19)
def sig(part):
    s = G[part]; bb = s['bbox']
    dims = sorted([round(bb[0][1] - bb[0][0], 1), round(bb[1][1] - bb[1][0], 1)])
    return (tuple(dims), round(bb[2][1] - bb[2][0], 2), tuple(sorted(set(c['R'] for c in s['cyl']))))


for fam in ('NUTPLATE', 'FOOTPLATE'):
    mem = sorted(k for k in G if fam in k)
    sigs = {k: sig(k) for k in mem}
    R['groups'][fam] = dict(members=mem, signatures={k: str(v) for k, v in sigs.items()}, same=len(set(sigs.values())) == 1)
    # 회전·거울 배치라 bbox 평면 크기는 각도에 따라 다를 수 있다 → 두께·구멍 반경 집합만 같으면 같은 형상으로 봄
    R['groups'][fam]['same_thickness_holes'] = len(set((v[1], v[2]) for v in sigs.values())) == 1

for k in sorted(k for k in G if 'NUTPLATE' in k):
    s = G[k]
    chk(k, 'Z 밑', s['z'][0], -104.5); chk(k, 'Z 위', s['z'][-1], -98.5)
    taps = uniq_holes(k, 1.65); chk(k, 'M4 탭 기초 구멍 Ø3.3 수', len(taps), 4, 0)
    ctr = uniq_holes(k, 14.2); chk(k, '가운데 Ø28.4 수', len(ctr), 1, 0)
    if ctr and taps:
        pcd = [math.hypot(t['x'] - ctr[0]['x'], t['y'] - ctr[0]['y']) for t in taps]
        chk(k, 'M4 탭 PCD/2', round(max(pcd), 2), 19.0, 0.05)
for k in sorted(k for k in G if 'FOOTPLATE' in k):
    s = G[k]
    chk(k, 'Z 밑', s['z'][0], -230.0); chk(k, 'Z 위', s['z'][-1], -224.0)
    hs = uniq_holes(k, 2.75); chk(k, 'Ø5.5 구멍 수', len(hs), 2, 0)
    if hs:
        rs = sorted(h['r'] for h in hs)
        # 스파이더 축 방향 a, 옆 c: 스파이더 축 방향 = 두 구멍을 잇는 방향
        th0 = math.atan2(hs[0]['y'] - AX[1], hs[0]['x'] - AX[0])
        th = [math.atan2(h['y'] - AX[1], h['x'] - AX[0]) for h in hs]
        d = math.hypot(hs[0]['x'] - hs[1]['x'], hs[0]['y'] - hs[1]['y'])
        chk(k, '구멍 간격(축 방향 135−110)', round(d, 2), 25.0, 0.1)
po = G['P_T01_POST']
chk('P_T01_POST', 'Z 밑', po['z'][0], -233.0)
chk('P_T01_POST', '카운터보어 바닥', [z for z in po['z'] if abs(z + 224.5) < 0.01][0] if any(abs(z + 224.5) < 0.01 for z in po['z']) else 0.0, -224.5)
chk('P_T01_POST', '밑 플랜지 윗면(t12)', [z for z in po['z'] if abs(z + 221.0) < 0.01][0] if any(abs(z + 221.0) < 0.01 for z in po['z']) else 0.0, -221.0)
cb = [c for c in uniq_holes('P_T01_POST', 4.75)]
chk('P_T01_POST', '카운터보어 Ø9.5 수', len(cb), 3, 0)
if cb:
    chk('P_T01_POST', '카운터보어 r', cb[0]['r'] if False else round(math.hypot(cb[0]['x'] - AX[0], cb[0]['y'] - AX[1]), 2), 50.0, 0.5)
R['step_ok'] = all(c['ok'] for c in R['step'])

# ------------------------------------------------------------------ 하중(지난 회차 식 그대로) + 바뀐 질량
P = T01['parts']; MK = T01['mass_kg']
c1 = P['P_T01_RING1']['샤프트_고정(회전 스프링)']; c2 = P['P_T01_RING2']['샤프트_고정(회전 스프링)']
reac1 = max(r['Fz'] for r in c1['reac_1g']); reac2 = max(r['Fz'] for r in c2['reac_1g'])
mrot1 = max(r['Mrot'] for r in c1['reac_1g']); mrot2 = max(r['Mrot'] for r in c2['reac_1g'])
m_cyl = MK['cyl_placeholder']; m_bush = MK['bush_placeholder']
M_NP = 0.0149; M_FP = 0.0121; M_CB518 = 0.0047; M_CB512 = 0.0038     # 너트판·누름판(모델 질량), CB5-18/12(부피 × 7.85 근사)
m_fast_bush_old = 4 * (0.0028 + 0.0004)
m_fast_bush = 4 * 0.0028 + M_NP                                         # CB4-16 4 + 너트판(LBNR4 빠짐)
m_fast_ring = 0.006
M_SP = 1.1320
a_piv = math.sqrt(150.0 ** 2 - 44.0 ** 2)


def loads(mfb):
    return [(reac1 + m_fast_ring * g + m_cyl * g, 190.0), ((m_bush + mfb) * g, 240.0),
            (reac2 + m_fast_ring * g + m_cyl * g, 410.0), ((m_bush + mfb) * g, 460.0)]


def spider_loads(r_root, mfb, extra=()):
    L = loads(mfb) + list(extra)
    frac = (490 - r_root) / 390.0
    L.append((M_SP * frac * g, (r_root + 490) / 2))
    V = sum(F for F, r in L); M = sum(F * (r - r_root) for F, r in L) + mrot1 + mrot2
    Mj = F_CYL * ((190 - r_root) + (410 - r_root)) + M
    return L, V, M, Mj


# 누름판 2장 + CB5-18 4개(발 위, 축 방향 r100~145 가운데 r122.5)는 피벗(143.4) 안쪽 → 스파이더 볼트 힘을 줄이는 쪽이라 볼트 힘 계산에서 뺌(보수).
# 허브 r85 굽힘에는 더한다(r150 기준 V에 넣고 M 팔 0 = 보수, 실제 팔은 −27.5).
m_foot_set = 2 * M_FP + 4 * (M_CB518 - M_CB512)
_, V_old, M_old, Mj_old = spider_loads(a_piv, m_fast_bush_old)
_, V_new, M_new, Mj_new = spider_loads(a_piv, m_fast_bush)
I_d = 2 * ((a_piv - 110.0) ** 2 + (a_piv - 135.0) ** 2)
Fb_3g = NG * M_new * (a_piv - 110.0) / I_d
Fb_jam = Mj_new * (a_piv - 110.0) / I_d
Fb = max(Fb_3g, Fb_jam)
R['loads'] = dict(spider_V_1g_old=round(V_old, 3), spider_V_1g_new=round(V_new, 3), M_root_1g_old=round(M_old, 1), M_root_1g_new=round(M_new, 1),
                  foot_bolt_F_3g=round(Fb_3g, 1), foot_bolt_F_jam=round(Fb_jam, 1), prev_foot_bolt_F_3g=PREV['parts']['P_T01_SPIDER_1~3']['foot_bolt_F_3g'],
                  mass_change_per_bush_kg=round(m_fast_bush - m_fast_bush_old, 4), foot_set_per_spider_kg=round(m_foot_set, 4))

# ================================================================== HUB — SUS304 t8 r85(형상 그대로, 하중만 조금 바뀜)
E_s, SY_s = MAT['SUS304']
_, V150, M150, Mj150 = spider_loads(150.0, m_fast_bush)
V150 += m_foot_set * g


def hub_case(r_s, V, M, t_h, F_in_lever=50.0, r_in=100.0):
    F_in = M / F_in_lever; F_out = V + F_in
    Mh = F_out * (150 - r_s) - F_in * max(0.0, r_in - r_s)
    b = min(60 + 2 * (150 - r_s), 2 * pi * r_s / 3)
    s = Mh / (b * t_h ** 2 / 6)
    return dict(M_hub=round(Mh, 1), sigma=round(s, 2), SF=round(SY_s / s, 2))


R['parts']['P_T01_HUB'] = dict(op_3g=hub_case(85.0, NG * V150, NG * M150, 8.0), jam=hub_case(85.0, V150 + 2 * F_CYL, Mj150, 8.0),
                               prev=dict(SF_3g=PREV['parts']['P_T01_HUB']['t8']['op_3g']['SF'], SF_jam=PREV['parts']['P_T01_HUB']['t8']['jam']['SF'], DP1_target=4.97),
                               mass_g=4378.4, mass_target_g=4404, note='형상 그대로(v0.6.6 STEP). 하중만 너트판·누름판·CB5-18 질량을 더함')

# ================================================================== 스파이더 발 누름판 P_T01_FOOTPLATE_*  (A5052 t6, x 34~52, 축 방향 45)
SY_a = MAT['A5052'][1]
tb = 6.0; x_in = 34.0; x_bolt = 44.0; head_r = 8.5 / 2; hole_r = 2.75; Lax = 45.0
fp = {}
# (가) 지난 회차 식(볼트 중심 레버 10, 볼트당 폭 22.5 총단면) — 수정 지시의 근거였던 값과 같은 식
s_a = 6 * Fb * (x_bolt - x_in) / (Lax / 2 * tb ** 2)
fp['지난 회차 식: 볼트 중심 레버 10, 폭 22.5(총단면)'] = dict(sigma=round(s_a, 2), SF=round(SY_a / s_a, 2))
# (나) 보수 하한: 볼트 중심 단면 순단면(22.5 − 5.5 = 17), 레버 10(머리 누름 무시)
s_b = 6 * Fb * (x_bolt - x_in) / ((Lax / 2 - 2 * hole_r) * tb ** 2)
fp['보수 하한: 볼트 중심 순단면 17, 레버 10'] = dict(sigma=round(s_b, 2), SF=round(SY_a / s_b, 2))
# (다) 실제 판정 단면: 머리 가장자리(x 39.75, 구멍 밖 → 총단면 22.5), 들림점 = 판 안쪽 끝 34(C1이면 35) → 레버 5.75
s_c = 6 * Fb * (x_bolt - head_r - x_in) / (Lax / 2 * tb ** 2)
fp['판정: 머리 가장자리 단면, 레버 5.75, 폭 22.5'] = dict(sigma=round(s_c, 2), SF=round(SY_a / s_c, 2))
fp['beam_handcalc(판정 단면)'] = HC.beam(tb, Lax / 2, x_bolt - head_r - x_in, load=Fb, e=MAT['A5052'][0], sy=SY_a, sf_min=SF_REQ)
fp['F_bolt_max'] = round(Fb, 1)
# 지렛대(prying): 판 바깥 끝 x 52가 발에 받쳐지면 볼트 힘이 늘어난다. 예압이 이음을 닫고 있는 동안은 생기지 않는다.
k_core = (52.0 - (x_in + 1.0)) / 6.0      # 접촉 x 35~52(C1) → 핵 반경
e_leg = x_bolt - 30.0                      # 다리 바깥면 30 → 볼트 44
fp['joint_open_load_N'] = {('%.0f N·m' % tq): round(tq * 1e3 / (0.2 * 5) * k_core / e_leg, 1) for tq in (4.0, 5.0)}
fp['joint_closed_margin_3g'] = {kk: round(v / Fb_3g, 2) for kk, v in fp['joint_open_load_N'].items()}
fp['note'] = '6장 같은 형상(N·P 거울). 하중 최대 볼트(r110, 704 N 계열) 자리 하나로 판정(E-19). 판 밑면은 발 윗면에 평평히 앉고 예압으로 닫힘'
R['parts']['P_T01_FOOTPLATE_*'] = fp

# 스파이더 발 t3 국부(누름판이 생긴 뒤): 다리 평평한 곳 시작 x33 → 누름판 접촉 시작(판 끝 34, 밑 모서리 C1 → 35)
tf = 3.0
foot = {}
for lab, lev, w in (('판정: 레버 2(33→35), 폭 25', 2.0, 25.0), ('레버 1(33→34, C1 무시)', 1.0, 25.0),
                     ('상한: 레버 5(다리 바깥면 30→35), 폭 25', 5.0, 25.0), ('상한 레버 5, 폭 45(누름판 길이)', 5.0, 45.0)):
    s = Fb * lev / (w * tf ** 2 / 6)
    foot[lab] = dict(sigma=round(s, 2), SF=round(SY_a / s, 2))
foot['prev_lever11_SF'] = PREV['parts']['P_T01_SPIDER_1~3']['SF_foot_3g']
R['parts']['P_T01_SPIDER_1~3 발 국부(누름판 뒤)'] = foot

# ================================================================== 너트판 P_T01_NUTPLATE_*  (A5052 t6 □40, M4 관통 탭 물림 6)
F_m4 = max(NG * mrot2, F_CYL * 50.0) / (2 * 26.87)
B = R['bolts']
B['LHFR16 → 너트판 CB4-16 (A5052 탭 물림 6, 좌면 LHFR16 플랜지 카운터보어 — 강, SS400 자리값)'] = [HC.calc(4, 6.0, F_m4, tq, '12.9', 'A5052', 6.3, 4.5) for tq in (1.5, 2.0, 2.5)]
B['LHFR16 좌면(SS400 자리값)'] = HC.calc(4, 6.0, F_m4, 2.0, '12.9', 'SS400', 6.3, 4.5)
# 너트판 굽힘: 볼트가 판을 위로 당기고 판은 웹 밑면(□40 전체가 웹 60 아래)에 면으로 앉음 → 굽힘 경로 없음.
# 최악(웹 구멍 Ø28.4 가장자리가 받침, 탭 r19까지 외팔 19 − 14.2 = 4.8, 폭 = 탭 간격 대각 26.9)
s_np = 6 * F_m4 * (19.0 - 14.2) / (26.87 * 6.0 ** 2)
# 조임 때(예압 2 N·m = 2,500 N)도 판은 웹에 눌려 압축 — 탭 사이 살(탭–가운데 구멍 2.8)의 지압
fv2 = 2.0e3 / (0.2 * 4)
R['parts']['P_T01_NUTPLATE_*'] = dict(F_m4=round(F_m4, 1), plate_bending_worst_sigma=round(s_np, 2), SF_plate=round(SY_a / s_np, 1),
                                      ligament_tap_to_center_mm=2.8, ligament_tap_to_edge_mm=4.57,
                                      note='6장 같은 형상(E-19). 판은 웹 밑면에 면 접촉, 볼트 당김은 웹이 받는다. 탭 물림 6 = 1.5d(M-01)')
# 스파이더 발 → 허브 CB5-18(STEP 대기, 허브 SUS304 탭 물림 8 그대로, 좌면 누름판 A5052)
B['스파이더 발 → 허브 STEP대기_CB5-18 (SUS304 탭 물림 8, 좌면 누름판 A5052 t6)'] = [HC.calc(5, 8.0, Fb, tq, '12.9', 'SUS304', 8.5, 5.5) for tq in (4.0, 5.0)]
B['누름판 좌면 A5052'] = [HC.calc(5, 8.0, Fb, tq, '12.9', 'A5052', 8.5, 5.5) for tq in (4.0, 5.0)]

# ================================================================== 기둥 P_T01_POST (PET-CF, 밑 플랜지 t12 + 카운터보어 Ø9.5×3.5)
PP = PREV['parts']['P_T01_POST']
F_lat_mis = P['P_T01_POST']['F_lat_mis']
Zp = pi * (60 ** 4 - 40 ** 4) / 64 / 30
s_tube = F_lat_mis * (-0.5 - (-221.0)) / Zp
Fpb = PP['bottom_bolt_F_mis']                     # 볼트 힘은 플랜지 밑면(−233) 모멘트로 정해져 그대로
post = dict(tube_root_sigma_mis=round(s_tube, 2), SF_tube_mis=round(MAT['PET-CF'][1] / s_tube, 2), prev_SF_tube_mis=PP['SF_tube_mis'])
for lab, tf_, lev in (('판정: 관 뿌리 단면 t12, 레버 15.75(머리 끝 → 관 r30), 폭 40', 12.0, 50.0 - 30.0 - 4.25),
                      ('상한: 레버 20(볼트 중심 → 관), t12', 12.0, 20.0),
                      ('참고: 카운터보어 바닥 t8.5가 판정 단면이라 볼 때(레버 15.75)', 8.5, 50.0 - 30.0 - 4.25)):
    s = Fpb * lev / (40.0 * tf_ ** 2 / 6)
    post[lab] = dict(sigma=round(s, 2), SF=round(MAT['PET-CF'][1] / s, 2))
# 카운터보어 바닥(t8.5 고리)은 바로 밑이 허브 윗면 → 압축만. 카운터보어 벽 바깥 살(Ø9.5 ↔ 플랜지 Ø120 바깥 r60): 60 − 50 − 4.75
post['counterbore_outer_wall_mm'] = round(60.0 - 50.0 - 4.75, 2)
post['counterbore_to_tube_mm'] = round(50.0 - 4.75 - 30.0, 2)
post['bolt_F_mis'] = Fpb; post['prev_SF_flange_mis_t8.5'] = PP['SF_flange_mis']; post['mass_g'] = 627.5
R['parts']['P_T01_POST'] = post
B['기둥 밑 → 허브 CB5-16 (SUS304 탭 물림 7.5, 좌면 PET-CF 카운터보어 바닥)'] = HC.calc(5, 7.5, Fpb, 1.5, '12.9', 'SUS304', 8.5, 5.5, sf_min=SF_MIS)
B['기둥 밑 좌면 PET-CF(와셔 없음, 1.5 N·m)'] = HC.calc(5, 7.5, Fpb, 1.5, '12.9', 'PET-CF', 8.5, 5.5, sf_min=SF_MIS)
B['기둥 밑 좌면 PET-CF(M5 와셔 Ø10, D-43 (2)) — 카운터보어 Ø9.5에 와셔 Ø10은 안 들어감'] = HC.calc(5, 7.5, Fpb, 1.5, '12.9', 'PET-CF', 9.4, 5.5, sf_min=SF_MIS)

# ================================================================== 질량
R['mass'] = dict(spider_body_kg=M_SP, spider_with_plates_kg=round(M_SP + 2 * M_NP + 2 * M_FP, 4), nutplate_g=14.9, footplate_g=12.1, post_g=627.5,
                 hub_g=4378.4, added_rotating_kg=round(6 * M_NP + 6 * M_FP + 12 * (M_CB518 - M_CB512) - 24 * 0.0004 + 0.0373, 4))

# ================================================================== 판정
J = []
def judge(item, val, req):
    st = 'ok' if val >= req else ('동작' if val < SF_BREAK else '기준')
    J.append(dict(item=item, value=val, required=req, status=st, needs_fea=req <= val < 1.1 * req))
judge('허브 t8 운전 3 g', R['parts']['P_T01_HUB']['op_3g']['SF'], 3.0)
judge('허브 t8 막힘', R['parts']['P_T01_HUB']['jam']['SF'], 2.0)
judge('누름판 t6 (판정 단면)', fp['판정: 머리 가장자리 단면, 레버 5.75, 폭 22.5']['SF'], 3.0)
judge('누름판 t6 (지난 회차 식)', fp['지난 회차 식: 볼트 중심 레버 10, 폭 22.5(총단면)']['SF'], 3.0)
judge('스파이더 발 국부(누름판 뒤, 레버 2)', foot['판정: 레버 2(33→35), 폭 25']['SF'], 3.0)
judge('너트판 굽힘(최악)', R['parts']['P_T01_NUTPLATE_*']['SF_plate'], 3.0)
judge('기둥 관 오조작', post['SF_tube_mis'], 2.0)
judge('기둥 밑 플랜지 t12 오조작', post['판정: 관 뿌리 단면 t12, 레버 15.75(머리 끝 → 관 r30), 폭 40']['SF'], 2.0)
R['judge'] = J
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('step_ok', R['step_ok'], len(R['step']), [c for c in R['step'] if not c['ok']])
print('groups', {k: (v['same'], v['same_thickness_holes']) for k, v in R['groups'].items()})
print('loads', R['loads'])
for j in J:
    print(j)
print('hub', R['parts']['P_T01_HUB'])
print('foot', foot)
print('fp', {k: v for k, v in fp.items() if 'beam' not in k})
print('post', post)
print('np', R['parts']['P_T01_NUTPLATE_*'])
for k, v in B.items():
    for x in (v if isinstance(v, list) else [v]):
        print(k[:40], x['inputs']['torque_Nm'], round(x['inputs']['load_N'], 1), x['sf_operating'], x['sf_tightening'], x['ok'], x['needs_fea'])
print('mass', R['mass'])
