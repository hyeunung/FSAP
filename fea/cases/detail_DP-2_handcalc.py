# -*- coding: utf-8 -*-
"""디테일링 DP-2 (v0.6.6) T01 회전 묶음 — 강도·체결 손계산(해석부, 2026-10-31).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 손계산 + 엔진 handcalc(import, 엔진 폴더는 읽기만).
입력: tools/out/detail/DP-2/stepout/P_T01_*.step 7개(모델링부 해석용 임시 STEP). 구멍 자리·두께는 STEP에서 읽어 확인한다.
하중: T01 2회차 결과(fea/results/mech_T01_fea1_handcalc.json)의 링 받침 반력·회전 반력(링은 R1·구멍만 바뀌어 질량 −0.1 % → 옛 반력 = 보수)
      + 바뀐 질량(스파이더 1.132 kg, 체결품). 식은 mech_T01_fea1_handcalc.py(스파이더·허브·기둥)와 detail_hub_r85.py(허브 r85) 그대로.
모델 변경(보고서 맨 위): 허브·스파이더 받침이 '다리 끝면 r150 누름·r100 들림'에서 '발 볼트 4개(축 방향 110·135, 옆 ±44) + 허브 끝 피벗'으로 바뀜.
      옛 모델도 같은 하중으로 풀어 차이를 남긴다.
단위 mm, N, MPa, kg.  실행: python -B fea/cases/detail_DP-2_handcalc.py → fea/results/detail_DP-2_handcalc.json
"""
import json, math, os, re, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENG = os.path.abspath(os.path.join(ROOT, '..', 'MechDesign_Engine', 'engine', 'tools'))
sys.path.insert(0, ENG)
import handcalc as HC                                   # 엔진 도구(읽기만)
STEPDIR = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-2', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'detail_DP-2_handcalc.json')
T01 = json.load(open(os.path.join(ROOT, 'fea', 'results', 'mech_T01_fea1_handcalc.json'), encoding='utf-8'))
AX = (0.0, -700.0); g = 9.81; pi = math.pi
MAT = {'SUS304': (193000.0, 205.0, 7.93e-6), 'A5052': (70300.0, 175.0, 2.68e-6), 'PET-CF': (4000.0, 20.0, 1.29e-6),
       'Rigid10K': (10000.0, 65.0, 1.65e-6), 'Steel': (206000.0, 345.0, 7.85e-6)}
NG = 3.0; SF_REQ, SF_MIS, SF_BREAK = 3.0, 2.0, 1.2
P_SUPPLY = 0.5; F_CYL = P_SUPPLY * pi * 16 ** 2 / 4; T_DG_MAX = 50.0e3
R = dict(method='손계산(표준 라이브러리 + 엔진 handcalc). 해석 못 함 — 환경 없음(D-16)', step=[], parts={}, bolts={}, notes=[])


# ------------------------------------------------------------------ STEP 읽기(원통 면 자리, 평면 Z)
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
                cyl.append(dict(R=round(float(m.group(2)), 3), r=round(math.hypot(p[0] - AX[0], p[1] - AX[1]), 2),
                                th=round(math.degrees(math.atan2(p[1] - AX[1], p[0] - AX[0])), 2)))
        m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", s)
        if m:
            verts.append(pt(int(m.group(1))))
    zs = sorted(set(round(v[2], 2) for v in verts))
    return dict(cyl=cyl, z=zs, bbox=[[round(min(v[k] for v in verts), 2), round(max(v[k] for v in verts), 2)] for k in range(3)])


G = {f[:-5]: read_step(os.path.join(STEPDIR, f)) for f in sorted(os.listdir(STEPDIR)) if f.endswith('.step')}


def chk(part, what, got, want, tol=0.3):
    ok = abs(got - want) <= tol
    R['step'].append(dict(part=part, what=what, step=got, used=want, ok=ok))
    return got


def holes(part, Rr):
    return [c for c in G[part]['cyl'] if abs(c['R'] - Rr) < 0.01]


chk('P_T01_HUB', 'Z 밑', G['P_T01_HUB']['z'][0], -241.0); chk('P_T01_HUB', 'Z 위(t8)', G['P_T01_HUB']['z'][-1], -233.0)
hub_tap = holes('P_T01_HUB', 2.1); hub_tbl = holes('P_T01_HUB', 3.3)
chk('P_T01_HUB', 'M5 탭 수', len(hub_tap), 15, 0); chk('P_T01_HUB', 'M6 볼트 구멍 수(PCD155)', len(hub_tbl), 6, 0)
chk('P_T01_HUB', '테이블 볼트 r', hub_tbl[0]['r'], 77.5)
# 스파이더 1(θ 90°) 발 탭: 축 방향 a = r cos(Δθ), 옆 c = r sin(Δθ)
feet = [(round(c['r'] * math.cos(math.radians(c['th'] - 90)), 2), round(c['r'] * math.sin(math.radians(c['th'] - 90)), 2)) for c in hub_tap if abs(c['th'] - 90) < 30]
chk('P_T01_HUB', '스파이더1 발 탭 수', len(feet), 4, 0)
a_b = sorted(set(round(abs(a), 1) for a, c in feet)); c_b = max(abs(c) for a, c in feet)
chk('P_T01_HUB', '발 볼트 축 방향 안', a_b[0], 110.0, 0.5); chk('P_T01_HUB', '발 볼트 축 방향 바깥', a_b[1], 135.0, 0.5); chk('P_T01_HUB', '발 볼트 옆', c_b, 44.0, 0.5)
a_piv = math.sqrt(150.0 ** 2 - c_b ** 2)      # 발 볼트 줄에서 허브 끝(r150) = 피벗
sp = G['P_T01_SPIDER_1']
chk('P_T01_SPIDER_1', 'Z 발 밑', sp['z'][0], -233.0); chk('P_T01_SPIDER_1', 'Z 발 위', sp['z'][1], -230.0)
chk('P_T01_SPIDER_1', 'Z 웹 밑', sp['z'][-2], -98.5); chk('P_T01_SPIDER_1', 'Z 웹 위', sp['z'][-1], -95.5)
chk('P_T01_SPIDER_1', '폭(X)', sp['bbox'][0][1] - sp['bbox'][0][0], 104.0)
chk('P_T01_SPIDER_1', '안끝 r', sp['bbox'][1][0] - AX[1], 100.0); chk('P_T01_SPIDER_1', '바깥끝 r', sp['bbox'][1][1] - AX[1], 490.0)
chk('P_T01_SPIDER_1', '부시 구멍 R', holes('P_T01_SPIDER_1', 14.2)[0]['R'], 14.2, 0.01)
chk('P_T01_SPIDER_1', 'SNJ 구멍 R', holes('P_T01_SPIDER_1', 5.25)[0]['R'], 5.25, 0.01)
po = G['P_T01_POST']
chk('P_T01_POST', 'Z 밑', po['z'][0], -233.0); chk('P_T01_POST', '밑 플랜지 위', po['z'][1], -224.5)
chk('P_T01_POST', '위 플랜지 밑', po['z'][2], -20.5); chk('P_T01_POST', 'Z 위', po['z'][3], -12.5)
chk('P_T01_POST', '밑 볼트 r', [c for c in holes('P_T01_POST', 2.75) if c['r'] > 47][0]['r'], 50.0)
chk('P_T01_POST', '위 볼트 r', [c for c in holes('P_T01_POST', 2.75) if c['r'] < 47][0]['r'], 45.0)
di = G['P_T01_DISC']
chk('P_T01_DISC', '인서트 자리 R', holes('P_T01_DISC', 3.2)[0]['R'], 3.2, 0.01); chk('P_T01_DISC', '인서트 자리 위 Z', di['z'][1], -3.5)
r1 = G['P_T01_RING1']
chk('P_T01_RING1', '카운터보어 바닥 Z', r1['z'][1], -6.0); chk('P_T01_RING1', '볼트 r', holes('P_T01_RING1', 2.75)[0]['r'], 240.0)
chk('P_T01_RING2', '머리 자리 R', holes('P_T01_RING2', 5.0)[0]['R'], 5.0, 0.01)
chk('P_T01_RING2_STRAP_1', '볼트 구멍 r', holes('P_T01_RING2_STRAP_1', 2.75)[0]['r'], 460.0)
R['step_ok'] = all(c['ok'] for c in R['step'])

# ------------------------------------------------------------------ 하중(1 g) — T01 2회차 결과 재사용 + 바뀐 질량
P = T01['parts']; MK = T01['mass_kg']
c1 = P['P_T01_RING1']['샤프트_고정(회전 스프링)']; c2 = P['P_T01_RING2']['샤프트_고정(회전 스프링)']
reac1 = max(r['Fz'] for r in c1['reac_1g']); reac2 = max(r['Fz'] for r in c2['reac_1g'])
mrot1 = max(r['Mrot'] for r in c1['reac_1g']); mrot2 = max(r['Mrot'] for r in c2['reac_1g'])
m_cyl = MK['cyl_placeholder']; m_bush = MK['bush_placeholder']
m_fast_bush = 4 * (0.0028 + 0.0004)          # CB4-16 + LBNR4 (임시 형상 부피 × 7.85, 보수 올림)
m_fast_ring = 0.006                            # 링–축 CB5 1개(축 끝) — 링 반력 위에 더함
M_SP = 1.1320                                  # 모델 질량(A5052 t3 판금) — 옛 3.2395(T01 모델)
loads = [(reac1 + m_fast_ring * g + m_cyl * g, 190.0), ((m_bush + m_fast_bush) * g, 240.0),
         (reac2 + m_fast_ring * g + m_cyl * g, 410.0), ((m_bush + m_fast_bush) * g, 460.0)]


def spider_loads(r_root, m_sp):
    L = list(loads)
    frac = (490 - r_root) / 390.0
    L.append((m_sp * frac * g, (r_root + 490) / 2))
    V = sum(F for F, r in L); M = sum(F * (r - r_root) for F, r in L) + mrot1 + mrot2
    Mj = F_CYL * ((190 - r_root) + (410 - r_root)) + M
    return L, V, M, Mj


# ================================================================== SPIDER — A5052 t3 모자형 단면(굽힘 R 무시, 보수)
t = 3.0; zb = -233.0
parts = [(60.0, t, -97.0), (t, 131.5, -164.25), (t, 131.5, -164.25), (22.0, t, -231.5), (22.0, t, -231.5)]   # (b, h, z중심)
A = sum(b * h for b, h, z in parts); zc = sum(b * h * (z - zb) for b, h, z in parts) / A
I = sum(b * h ** 3 / 12 + b * h * ((z - zb) - zc) ** 2 for b, h, z in parts)
H = 137.5; Z_top = I / (H - zc); Z_bot = I / zc
I_lat = t * 60 ** 3 / 12 + 2 * (131.5 * t ** 3 / 12 + 131.5 * t * 28.5 ** 2) + 2 * (t * 22 ** 3 / 12 + 22 * t * 41 ** 2)
# 부시 구멍 단면(r240·r460): 웹 60 → 31.6
parts_h = [(60.0 - 28.4, t, -97.0)] + parts[1:]
A_h = sum(b * h for b, h, z in parts_h); zc_h = sum(b * h * (z - zb) for b, h, z in parts_h) / A_h
I_h = sum(b * h ** 3 / 12 + b * h * ((z - zb) - zc_h) ** 2 for b, h, z in parts_h)
E_a, SY_a = MAT['A5052'][0], MAT['A5052'][1]
sp_res = {}
for lab, r_root in (('새 모델: 발 볼트 피벗 r%.1f' % a_piv, a_piv), ('옛 모델: 끝면 r150', 150.0)):
    L, V, M, Mj = spider_loads(r_root, M_SP)
    sig = NG * M / min(Z_top, Z_bot); sig_j = Mj / min(Z_top, Z_bot)
    # 부시 구멍 단면 r240
    M240 = NG * (sum(F * (r - 240) for F, r in L if r > 240) + mrot2)
    sig_h = M240 / min(I_h / (H - zc_h), I_h / zc_h)
    F_tan = T_DG_MAX / 3 / 240.0
    sig_lat = F_tan * (240 - r_root) / (I_lat / 52.0)
    defl = sum(F * (r - r_root) ** 2 * (3 * (490 - r_root) - (r - r_root)) / (6 * E_a * I) for F, r in L)
    sp_res[lab] = dict(r_root=round(r_root, 2), V_1g=round(V, 2), M_root_1g=round(M, 1), sigma_3g=round(sig, 3), SF_3g=round(SY_a / sig, 1),
                       M_jam=round(Mj, 1), sigma_jam=round(sig_j, 3), SF_jam=round(SY_a / sig_j, 1),
                       bush_section_r240_sigma_3g=round(sig_h, 3), SF_bush_section=round(SY_a / sig_h, 1),
                       lateral_DGmax_sigma=round(sig_lat, 3), SF_lat=round(SY_a / sig_lat, 1), tip_defl_1g=round(defl, 5))
# 웹 국부: 실린더 장착 너트가 웹(다리 안쪽 54)을 누름 — T01 식 그대로(양단 고정 띠, 유효 폭 30)
Mw = max(F_CYL, NG * (reac2 + m_cyl * g)) * 54.0 / 8.0
sig_web = Mw / (30.0 * t ** 2 / 6)
# 발(바깥 22) 국부: 볼트 인장이 발을 다리에서 들어 올림 — 외팔(다리 바깥면 30 → 볼트 44 = 14), 폭 25(볼트 간격), 예압 무시(보수)
I_feet_d = 2 * ((a_piv - 110.0) ** 2 + (a_piv - 135.0) ** 2)          # 스파이더 하나 4볼트 Σd²
L_new, V_new, M_new, Mj_new = spider_loads(a_piv, M_SP)
Fb_3g = NG * M_new * (a_piv - 110.0) / I_feet_d
Fb_jam = Mj_new * (a_piv - 110.0) / I_feet_d
# 발 평평한 곳 시작 x 33(다리 바깥면 30 + 안 R3) → 볼트 중심 44: 레버 11. 예압 무시 외팔(보수 상한 레버 14 = 다리 바깥면부터도 남김)
LEV = 11.0
sig_foot = Fb_3g * LEV / (25.0 * t ** 2 / 6); sig_foot_j = Fb_jam * LEV / (25.0 * t ** 2 / 6)
sig_foot14 = Fb_3g * 14.0 / (25.0 * t ** 2 / 6)
beam_foot = HC.beam(t, 25.0, LEV, load=max(Fb_3g, Fb_jam), e=E_a, sy=SY_a, sf_min=SF_REQ)
# 예압이 있을 때 이음이 닫혀 있는지(편심 하중): 접촉 폭 x 33~52(16 → 19), 볼트 44, 핵 반경 19/6. 외력이 다리(x 30)에 걸려 볼트에서 14
k_core = (52.0 - 33.0) / 6.0
open_load = {tq: round(tq * 1e3 / (0.2 * 5) * k_core / 14.0, 1) for tq in (4.0, 5.0)}
# 고치는 안: 발 누름판(볼트 2개를 한 판으로, x 34~52 · 축 방향 45, 볼트 CB5-12 → CB5-18, 끝 Z 그대로 −242)
bar = {}
for mat, tb in (('A5052', 5.0), ('A5052', 6.0), ('SS400', 5.0), ('SS400', 6.0)):
    sy_b = {'A5052': 175.0, 'SS400': 245.0}[mat]
    s = 6 * max(Fb_3g, Fb_jam) * 10.0 / (22.5 * tb ** 2)
    bar['%s t%d' % (mat, tb)] = dict(sigma=round(s, 1), SF=round(sy_b / s, 2))
alt_t = {('t%d' % tt): round(SY_a / (Fb_3g * LEV / (25.0 * tt ** 2 / 6)), 2) for tt in (4.0, 5.0, 6.0)}
R['parts']['P_T01_SPIDER_1~3'] = dict(material='A5052 t3(판금 H32 가정 Rp 175 보수)', A=round(A, 1), zc_from_bottom=round(zc, 2), I=round(I, 0), Z_min=round(min(Z_top, Z_bot), 0),
                                      I_lat=round(I_lat, 0), cases=sp_res, web_local_sigma=round(sig_web, 2), SF_web=round(SY_a / sig_web, 2),
                                      foot_bolt_F_3g=round(Fb_3g, 1), foot_bolt_F_jam=round(Fb_jam, 1), foot_sigma_3g=round(sig_foot, 2), SF_foot_3g=round(SY_a / sig_foot, 1),
                                      foot_sigma_jam=round(sig_foot_j, 2), SF_foot_jam=round(SY_a / sig_foot_j, 2), foot_beam_handcalc=beam_foot,
                                      foot_lever=LEV, foot_SF_lever14=round(SY_a / sig_foot14, 2), foot_joint_open_load_N=open_load,
                                      foot_fix_clamp_bar=bar, foot_fix_spider_thickness_SF=alt_t, bolt_lever_d=[round(a_piv - 110.0, 2), round(a_piv - 135.0, 2)],
                                      mass_kg=M_SP, prev_T01=dict(SF_3g=P['P_T01_SPIDER_1~3']['SF_3g'], SF_jam=P['P_T01_SPIDER_1~3']['SF_jam'], SF_web=P['P_T01_SPIDER_1~3']['SF_web']))

# ================================================================== HUB — SUS304 t8, 받침 r85(DG 테이블 Ø170). detail_hub_r85.py 식
E_s, SY_s = MAT['SUS304'][0], MAT['SUS304'][1]
_, V150, M150, Mj150 = spider_loads(150.0, M_SP)       # 허브 식은 r150 기준 V·M(모멘트 정역학상 피벗 위치와 무관)


def hub_case(r_s, V, M, t_h, F_in_lever=50.0, r_in=100.0):
    F_in = M / F_in_lever; F_out = V + F_in
    Mh = F_out * (150 - r_s) - F_in * max(0.0, r_in - r_s)
    b = min(60 + 2 * (150 - r_s), 2 * pi * r_s / 3)
    sig = Mh / (b * t_h ** 2 / 6)
    EI = E_s * b * t_h ** 3 / 12; Lh = 150 - r_s
    defl = (V * Lh ** 3 / 3 + M * Lh ** 2 / 2) / EI; slope = (V * Lh ** 2 / 2 + M * Lh) / EI
    return dict(r=r_s, t=t_h, M_hub=round(Mh, 1), b_eff=round(b, 1), sigma=round(sig, 2), SF=round(SY_s / sig, 2), F_in=round(F_in, 1), defl_r150=round(defl, 4), slope=round(slope, 6))


hub = dict(V_1g=round(V150, 2), M_1g=round(M150, 1), M_jam=round(Mj150, 1))
for tt in (6.0, 8.0):
    hub['t%d' % tt] = dict(op_3g=hub_case(85.0, NG * V150, NG * M150, tt), jam=hub_case(85.0, V150 + 2 * F_CYL, Mj150, tt))
# 옛 모델(r150 누름·r100 들림, 들림 = M/50) vs 새 모델(발 볼트 축 110·135, 피벗 a_piv): 허브 판 굽힘 r85는 정역학상 같다 → 볼트 힘만 다르다
hub['bolt_force_compare'] = dict(old_model_F_in_per_spider_3g=round(NG * M150 / 50.0, 1), old_per_bolt_2=round(NG * M150 / 50.0 / 2, 1),
                                 new_model_max_bolt_3g=round(Fb_3g, 1), new_model_max_bolt_jam=round(Fb_jam, 1),
                                 note='옛 모델은 다리마다 볼트 2개(r100)로 들림을 받는다고 봄. 새 모델은 발 볼트 4개 선형 분포(Σd²)')
h1 = hub_case(85.0, V150, M150, 8.0)
hub['ring_drop_1g'] = dict(ring1=round(h1['defl_r150'] + h1['slope'] * 40, 4), ring2=round(h1['defl_r150'] + h1['slope'] * 260, 4))
hub['prev'] = dict(detail_hub_r85_t8_SF_3g=4.97, SF_jam=5.61)
hub['mass_g'] = 4378.4
R['parts']['P_T01_HUB'] = hub

# ================================================================== 체결(엔진 handcalc, 운전 SF 3, 조임 1.0)
B = R['bolts']
B['스파이더 발 → 허브 CB5-12 (SUS304 탭 물림 8)'] = [HC.calc(5, 8.0, max(Fb_3g, Fb_jam), tq, '12.9', 'SUS304', 8.5, 5.5) for tq in (4.0, 5.0, 6.0)]
# 허브 → DG 테이블 CB6-18 ×6 r77.5: 한 스파이더 몫 기울임(3 g) 전부를 6개가 받음(나머지 스파이더 상쇄 무시 = 보수), 피벗 = 테이블 끝 r85
Mot = NG * (M150 + V150 * (150 - 85))
d6 = [85.0 - 77.5 * math.cos(math.radians(a)) for a in (0, 60, 120, 180, 240, 300)]
F_tbl = Mot * max(d6) / sum(d * d for d in d6)
B['허브 → DG 테이블 STEP대기_CB6-18 (테이블 탭 물림 10, 재질 미확인 → A5052 보수)'] = [HC.calc(6, 10.0, F_tbl, tq, '12.9', 'A5052', 10.0, 6.6) for tq in (4.5, 6.0)]
mu = 0.15
fv6 = 4.5e3 / (0.2 * 6)
B['허브 → DG 테이블 미끄럼(DG 최대 토크 50 N·m, 4.5 N·m 조임, μ 0.15)'] = dict(F_overturn_max_bolt=round(F_tbl, 1), friction_torque_Nm=round(mu * 6 * fv6 * 77.5 / 1e3, 1),
                                                                     SF=round(mu * 6 * fv6 * 77.5 / T_DG_MAX, 1))
# 기둥: 오조작 옆힘(작은 매트가 부딪쳐 마찰 한계, T01) 275.6 N at 원판 위(Z −0.5)
F_lat_mis = P['P_T01_POST']['F_lat_mis']; F_lat = P['P_T01_POST']['F_lat']
M_base_mis = F_lat_mis * (-0.5 - (-233.0)); M_base = F_lat * (-0.5 - (-233.0))


def ring_bolt(M, n, r_b, r_edge):
    worst = 0.0
    for k in range(0, 360, 5):
        ph = math.radians(k)
        d = [r_edge + r_b * math.cos(ph + 2 * pi * i / n) for i in range(n)]
        worst = max(worst, M * max(d) / sum(x * x for x in d))
    return worst


Fpb = ring_bolt(M_base_mis, 3, 50.0, 60.0)
B['기둥 밑 → 허브 CB5-16 (SUS304 탭 물림 7.5, 좌면 PET-CF 플랜지)'] = [HC.calc(5, 7.5, Fpb, 1.5, '12.9', 'SUS304', 8.5, 5.5, sf_min=SF_MIS)]
B['기둥 밑 좌면 PET-CF(와셔 없음, 1.5 N·m)'] = HC.calc(5, 7.5, Fpb, 1.5, '12.9', 'PET-CF', 8.5, 5.5, sf_min=SF_MIS)
B['기둥 밑 좌면 PET-CF(M5 와셔 Ø10, D-43 (2))'] = HC.calc(5, 7.5, Fpb, 1.5, '12.9', 'PET-CF', 10.0, 5.5, sf_min=SF_MIS)
M_top_mis = F_lat_mis * (-0.5 - (-20.5))
Fpt = ring_bolt(M_top_mis, 3, 45.0, 50.0)
B['기둥 위 → 원판 인서트 CB5-16 (MBIS5 황동 물림 8)'] = HC.calc(5, 8.0, max(Fpt, 1.0), 1.5, '12.9', 'A5052', 8.5, 5.5, sf_min=SF_MIS)
# 기둥 몸·플랜지
Zp = pi * (60 ** 4 - 40 ** 4) / 64 / 30
sig_tube_mis = F_lat_mis * (-0.5 - (-224.5)) / Zp
Fl_w = 40.0; Fl_t = 8.5; lever = 50.0 - 30.0 - 4.25
sig_fl = Fpb * lever / (Fl_w * Fl_t ** 2 / 6)
fl_fix = {('t%.1f' % tf): round(MAT['PET-CF'][1] / (Fpb * lever / (Fl_w * tf ** 2 / 6)), 2) for tf in (8.5, 10.0, 11.0, 12.0)}
B['스파이더 발 좌면 A5052 t3'] = [HC.calc(5, 8.0, max(Fb_3g, Fb_jam), tq, '12.9', 'A5052', 8.5, 5.5) for tq in (4.0, 5.0)]
R['parts']['P_T01_POST_flange_fix_SF'] = fl_fix
R['parts']['P_T01_POST'] = dict(tube_root_sigma_mis=round(sig_tube_mis, 2), SF_tube_mis=round(MAT['PET-CF'][1] / sig_tube_mis, 2),
                                prev_SF_mis=round(P['P_T01_POST']['SF_mis'], 2), prev_SF=round(P['P_T01_POST']['SF'], 1),
                                bottom_bolt_F_mis=round(Fpb, 1), top_bolt_F_mis=round(Fpt, 1), flange_sigma_mis=round(sig_fl, 2), SF_flange_mis=round(MAT['PET-CF'][1] / sig_fl, 2),
                                note='관 단면·하중 그대로(길이 −2). 플랜지 굽힘: 볼트 r50 ← 관 바깥 r30, 레버 20 − 머리 4.25, 유효 폭 40, PET-CF 층간 자리값 20 MPa(보수)')
# 원판: 받침이 관 r30 → 위 플랜지 r50, 돌출 25 → 5
mR = MAT['Rigid10K']
w_d = NG * (0.1866 + MK['mat_small']) * g / (pi * (55 ** 2 - 50 ** 2))
sig_d = 6 * (w_d * 5.0 ** 2 / 2) / 12 ** 2
p_vac = 0.058; sig_skin = 0.75 * p_vac * 3.2 ** 2 / 3.0 ** 2
fv_ins = 1.5e3 / (0.2 * 5)
R['parts']['P_T01_DISC'] = dict(sigma_3g=round(sig_d, 4), SF_3g=round(mR[1] / max(sig_d, 1e-9), 0), skin_over_insert_t=3.0, skin_sigma_vac=round(sig_skin, 3),
                                insert_pull_preload_N=round(fv_ins, 0), insert_pull_op_mis_N=round(Fpt, 1),
                                insert_note='MBIS5-6.5-8은 열가소성 수지용 열압입 인서트. Rigid 10K는 광경화(열경화성) 수지라 열압입으로 붙지 않는다 → 접착(에폭시) 또는 압입·나사 인서트 필요. 인서트 빠짐 강도 자료 없음')
# 링1: 링–축 CB5-12 축 탭(물림 7.5, Steel). 축이 링 기울기를 막는 회전 반력 Mrot → 축 끝면 Ø15(C0.5) 끝에서 지렛대 7.5
M_r1_3g = NG * mrot1; M_r1_jam = F_CYL * 50.0          # 막힘: 로드 r190 → 축 r240 (T01 띠 식과 같은 상한)
F_r1 = max(M_r1_3g, M_r1_jam) / 7.5
B['링1 → 축 CB5-12 (축 탭 물림 7.5, Steel; 좌면 A5052 카운터보어)'] = [HC.calc(5, 7.5, F_r1, tq, '12.9', 'S45C', 8.5, 5.5) for tq in (4.0, 5.0)]
B['링1 좌면 A5052'] = HC.calc(5, 7.5, F_r1, 5.0, '12.9', 'A5052', 8.5, 5.5)
# 링2 띠: 띠 → 축 CB5-16 물림 11
M_s_3g = P['P_T01_RING2_STRAP_1~6']['M_3g']; M_s_jam = P['P_T01_RING2_STRAP_1~6']['M_jam']
F_r2 = max(M_s_3g, M_s_jam) / 7.5
B['링2 띠 → 축 CB5-16 (축 탭 물림 11, Steel; 좌면 띠 A5052)'] = [HC.calc(5, 11.0, F_r2, tq, '12.9', 'A5052', 8.5, 5.5) for tq in (4.0, 5.0)]
# 링1·링2 판: 받침 자리 구멍
r1c = P['P_T01_RING1']['샤프트_고정(회전 스프링)']; r2c = P['P_T01_RING2']['샤프트_고정(회전 스프링)']
f1 = 225.0 / (225.0 - 9.5 * 4.5 / 10 - 5.5 * 5.5 / 10)        # 단면 감소(카운터보어 Ø9.5×4.5 + Ø5.5×5.5, 폭 225 t10) 근사
f2 = 210.0 / (210.0 - 10.0)
R['parts']['P_T01_RING1'] = dict(SF_3g=round(r1c['SF_3g'] / f1, 1), SF_jam=round(r1c['jam']['SF'] / f1, 1), SF_jam_rigid=round(r1c['jam_rigid_supports']['SF'] / f1, 1),
                                 net_factor=round(f1, 4), mass_g=7098.5, note='R1 블렌드·자리 구멍만. 받침점 단면에 구멍이 있다고 보고 순단면으로 나눔(보수)')
R['parts']['P_T01_RING2'] = dict(SF_3g=round(r2c['SF_3g'] / f2, 2), SF_jam=round(r2c['jam']['SF'] / f2, 2), SF_jam_rigid=round(r2c['jam_rigid_supports']['SF'] / f2, 2),
                                 net_factor=round(f2, 4), local_Kt_hole_bending=2.0, SF_jam_local_peak=round(r2c['jam']['SF'] / f2 / 2.0, 2), mass_g=7331.3,
                                 note='Ø10 머리 자리 r460(받침점). 정적 연성 → 순단면 판정, 구멍 가장자리 국부 첨두(Kt≈2)는 참고')
fs = 40.0 / (40.0 - 5.5)
R['parts']['P_T01_RING2_STRAP_1~6'] = dict(SF_3g=round(P['P_T01_RING2_STRAP_1~6']['SF_3g'] / fs, 2), SF_jam=round(P['P_T01_RING2_STRAP_1~6']['SF_jam'] / fs, 2), net_factor=round(fs, 4),
                                           note='띠 r460 Ø5.5 구멍 = 모멘트 최대 자리 → 순단면 34.5 × 5')
# LHFR16 플랜지 M4 + LBNR4: 부시가 받는 축 기울기 모멘트(막힘 상한 F_CYL×50)를 대각 볼트 4개(PCD38, 줄 간격 26.87)
M_b = max(NG * mrot2, F_CYL * 50.0)
F_m4 = M_b / (2 * 26.87)
B['LHFR16 → 스파이더 웹 CB4-16 + LBNR4 (표준 너트 높이 3.2, 좌면 웹 A5052)'] = [HC.calc(4, 3.2, F_m4, tq, '12.9', 'A5052', 6.3, 4.5) for tq in (1.5, 2.0)]
B['_note_M4'] = 'handcalc의 물림 판정(le ≥ 1.5d)은 탭 기준. LBNR4는 표준 너트(m 3.2 = 0.8d, 강도 구분 맞춤)라 나사산 전단은 너트 쪽이 볼트보다 강하게 맞춰져 있다 → ok=false는 물림 규칙 때문. 너트 자재 전단은 SS400 자리값으로 따로'
B['LHFR16 너트 나사산(SS400 자리값)'] = HC.calc(4, 3.2, F_m4, 2.0, '12.9', 'SS400', 6.3, 4.5)
B['LHFR16 너트 나사산(SS400 자리값) 1.5 N·m'] = HC.calc(4, 3.2, F_m4, 1.5, '12.9', 'SS400', 6.3, 4.5)

# ================================================================== DG 관성·하중 변화(참고, D-17·D-36)
I_hub = lambda m: m * (0.150 ** 2 + 0.020 ** 2) / 2
I_bar = lambda m: m * (0.490 ** 3 - 0.100 ** 3) / (3 * 0.390)
dI = (I_hub(4.3784) - I_hub(3.3034)) + 3 * (I_bar(M_SP) - I_bar(3.0541))
R['DG'] = dict(dI_kgm2=round(dI, 4), dmass_kg=round((4.3784 - 3.3034) + 3 * (M_SP - 3.0541) + (0.5902 - 0.4508), 3),
               note='회전 관성 줄어듦 → DG 토크 여유 늘어남. 허용 관성·모멘트는 D-17·D-36 (2) 미확인')

# ================================================================== 판정 모음
J = []
def judge(item, val, req, kind_if_fail='기준'):
    st = 'ok' if val >= req else ('동작' if val < SF_BREAK else kind_if_fail)
    near = req <= val < 1.1 * req
    J.append(dict(item=item, value=val, required=req, status=st, needs_fea=near))
hn = R['parts']['P_T01_HUB']['t8']
judge('허브 t8 운전 3 g', hn['op_3g']['SF'], 3.0); judge('허브 t8 막힘', hn['jam']['SF'], 2.0)
spn = R['parts']['P_T01_SPIDER_1~3']['cases'][list(sp_res)[0]]
judge('스파이더 운전 3 g', spn['SF_3g'], 3.0); judge('스파이더 막힘', spn['SF_jam'], 2.0)
judge('스파이더 부시 단면 r240', spn['SF_bush_section'], 3.0); judge('스파이더 옆(DG 최대 토크)', spn['SF_lat'], 2.0)
judge('스파이더 웹 국부', R['parts']['P_T01_SPIDER_1~3']['SF_web'], 3.0)
judge('스파이더 발 국부 3 g', R['parts']['P_T01_SPIDER_1~3']['SF_foot_3g'], 3.0); judge('스파이더 발 국부 막힘', R['parts']['P_T01_SPIDER_1~3']['SF_foot_jam'], 2.0)
judge('기둥 관 오조작', R['parts']['P_T01_POST']['SF_tube_mis'], 2.0); judge('기둥 플랜지 오조작', R['parts']['P_T01_POST']['SF_flange_mis'], 2.0)
judge('원판 3 g', R['parts']['P_T01_DISC']['SF_3g'], 3.0)
judge('링1 막힘(순단면)', R['parts']['P_T01_RING1']['SF_jam'], 2.0); judge('링2 막힘(순단면)', R['parts']['P_T01_RING2']['SF_jam'], 2.0)
judge('링2 막힘(받침 강체, 순단면)', R['parts']['P_T01_RING2']['SF_jam_rigid'], 2.0)
judge('링2 띠 막힘(순단면)', R['parts']['P_T01_RING2_STRAP_1~6']['SF_jam'], 2.0)
R['judge'] = J
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('step_ok', R['step_ok'], [c for c in R['step'] if not c['ok']])
for j in J:
    print(j)
print('hub', json.dumps(R['parts']['P_T01_HUB'], ensure_ascii=False))
print('spider', json.dumps({k: v for k, v in R['parts']['P_T01_SPIDER_1~3'].items() if k != 'foot_beam_handcalc'}, ensure_ascii=False))
for k, v in R['bolts'].items():
    vv = v if isinstance(v, list) else [v]
    for x in vv:
        if isinstance(x, dict) and 'sf_operating' in x:
            print(k, x['inputs']['torque_Nm'], x['inputs']['load_N'], x['sf_operating'], x['sf_tightening'], x['ok'], x['needs_fea'])
        else:
            print(k, x)
print('post', R['parts']['P_T01_POST'], R['parts']['P_T01_POST_flange_fix_SF']); print('disc', R['parts']['P_T01_DISC']); print('DG', R['DG'])
print('rings', R['parts']['P_T01_RING1'], R['parts']['P_T01_RING2'], R['parts']['P_T01_RING2_STRAP_1~6'])
