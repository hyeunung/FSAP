# -*- coding: utf-8 -*-
"""DP-4 해석부 손계산(v2.31.2) — U4 캐리지 리드 받침. FEA 못 함 — 환경 없음(D-16). CAD 안 씀.
입력: fea/results/detail_DP-4_stepgeo.json(바뀐 STEP 2 + 재질만 바뀐 관 받침 STEP), tools/out/signatures.json(v2.31.2, 해시 3cecf9e76dccace8),
      앞 결과 fea/results/mech_RX-DC-C1_fea3_handcalc.json(세움 받침 — 형상 그대로) · mech_RX-DC-03_handcalc.json(리드 안내 — 형상 그대로)
하중(fea/models.json, D-232 · D-38 임시): 운전 = 케이블 되돌림 5 N x 2줄 + 받는 무게 x 3 g, 오조작 = 케이블 손 당김 50 N.
판정(요구서 6-1 = M-09 기본값): 운전 SF 3, 오조작 SF 2, SF < 1.2 = 영구 변형(동작). 과사양 = 지배하는 경우의 SF가 필요치의 3배 이상.
모델에서 달라진 것(이유는 보고서 맨 위): 판금 기능으로 바뀌면서 생긴 굽힘 R(안쪽 R = t)의 안쪽 겉면을 굽은 보 식으로 보고(곧은 보의 1.29배),
  볼트 구멍 자리는 구멍을 뺀 단면으로 본다(E-18 "손계산의 단면은 … 측정 자료의 최소 단면으로"). 고정 · 접촉 · 하중 자리는 표 그대로.
  옛 모델(벽 안쪽 면에서 곧은 외팔보)도 같은 형상에 풀어 차이를 남긴다.
실행: python -X utf8 -B fea/cases/detail_DP-4_handcalc.py -> fea/results/detail_DP-4_handcalc.json"""
import json, math, sys
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
import handcalc as hc
GEO = json.load(open(ROOT + '/fea/results/detail_DP-4_stepgeo.json', encoding='utf-8'))
SIG = json.load(open(ROOT + '/tools/out/signatures.json', encoding='utf-8'))
assert SIG['doc'].replace('\\', '/').endswith('FSAP_v2.31.2.sc') and SIG['doc_hash'] == '3cecf9e76dccace8', (SIG['doc'], SIG['doc_hash'])
PARTS = SIG['parts']
RIS = json.load(open(ROOT + '/fea/results/mech_RX-DC-C1_fea3_handcalc.json', encoding='utf-8'))
DC03 = json.load(open(ROOT + '/fea/results/mech_RX-DC-03_handcalc.json', encoding='utf-8'))

SY, E, G = 205.0, 193000.0, 74000.0          # SUS304
SY_AL, SY_AL112, E_AL = 195.0, 110.0, 70000.0  # A5052-H32 · H112(handcalc 표)
SY_PET, SY_PET_LAYER, E_PET = 60.0, 30.0, 5000.0   # PET-CF(handcalc 표) · 층간 0.5배(DP-3과 같은 가정)
g = 9.81
F_MIS, F_CAB, N_CAB = 50.0, 5.0, 2
NEED_RUN, NEED_MIS = 3.0, 2.0
R = {'_doc': SIG['doc'].replace('\\', '/'), '_doc_hash': SIG['doc_hash'],
     '_assume': {'케이블 되돌림 N/줄(D-232 임시)': F_CAB, '줄 수': N_CAB, '오조작 손 당김 N(D-38 전 임시)': F_MIS, '무게 배수': 3,
                 'SUS304 항복': SY, 'A5052-H32 · H112 항복': [SY_AL, SY_AL112], 'PET-CF 항복 · 층간': [SY_PET, SY_PET_LAYER], '조임 M5 N·m(관례) · PET-CF 좌면': [4.5, 1.5]}}


def ki_rect(ri, t):
    """굽은 보(사각 단면) 안쪽 겉면 응력 / 곧은 보 응력. Winkler: rn = t / ln(ro/ri), e = rc - rn."""
    ro, rc = ri + t, ri + t / 2.0
    rn = t / math.log(ro / ri); e = rc - rn
    return ((rn - ri) / (t * e * ri)) / (6.0 / t ** 2)      # 폭은 약분


def sf(s, sy=SY): return round(sy / s, 2) if s > 0 else None


def cyl(part, axis, r):
    return [c for c in GEO[part]['new']['cyl'] if c['axis'] == axis and abs(c['r'] - r) < 1e-6]


def sig(key):
    hit = [v for k, v in PARTS.items() if k.endswith('/' + key) or k == key]
    assert len(hit) == 1, (key, len(hit)); return hit[0]


def judge(v, need):
    return '동작(영구 변형)' if v < 1.2 else ('미달' if v < need else ('기준 ±10 % 안(FEA 대기)' if v < 1.1 * need else '됨'))


# ================================================================== 1) 보 앞 받침 P_RXDC03_BEAM_CLAMP_판금 (t3 -> t4, 판금)
bb = GEO['P_RXDC03_BEAM_CLAMP']['new']['bbox']
pl = dict(); [pl.setdefault(a, []).append(v) for a, v in GEO['P_RXDC03_BEAM_CLAMP']['planes_new']]
bend = cyl('P_RXDC03_BEAM_CLAMP', 'X', 4.0)[0]; bend_o = cyl('P_RXDC03_BEAM_CLAMP', 'X', 8.0)[0]
hz = sorted(c['center'][1] for c in cyl('P_RXDC03_BEAM_CLAMP', 'Y', 2.75))
b = bb[0][1] - bb[0][0]; t = bb[1][1] - sorted(pl['Y'])[1]            # 폭 14, 벽 두께 = Y 120 - 116
t_sh = sorted(pl['Z'])[1] - bb[2][0]                                    # 선반 두께 = 606.5 - 602.5
assert abs(t - 4.0) < 1e-6 and abs(t_sh - 4.0) < 1e-6 and abs(b - 14.0) < 1e-6, (b, t, t_sh)
y_tip, y_wall_in, y_face = bb[1][0], bb[1][1] - t, bb[1][1]             # 68, 116, 120
yc, zc = bend['center']                                                 # 굽힘 중심 (112, 610.5)
ri = bend['r']; assert abs(bend_o['r'] - ri - t) < 1e-6
y_mid = y_wall_in + t / 2.0                                             # 벽 두께 가운데 118
Z_g, A_g = b * t ** 2 / 6.0, b * t
Z_net = (b - 5.5) * t ** 2 / 6.0
KI = ki_rect(ri, t)
run1 = N_CAB * F_CAB + 0.07 * g * 3                                     # 표 그대로(받는 무게 70 g)
m1 = {'형상(STEP)': {'상자': bb, '폭': b, '벽 · 선반 두께': [t, t_sh], '굽힘 안쪽 R · 중심 (Y, Z)': [ri, [yc, zc]], '구멍 Ø5.5 Z': hz, '선반 끝 Y': y_tip,
                    '보 맞댐 평면이 시작하는 Z(바깥 R 8 끝)': zc, '서명 부피 · 질량': [sig('P_RXDC03_BEAM_CLAMP_판금')['volume'], sig('P_RXDC03_BEAM_CLAMP_판금')['mass']]},
      '굽은 보 계수(안쪽 R = t)': round(KI, 3), '운전 하중 N': round(run1, 2)}


def clamp_case(F, need):
    L_old = y_wall_in - y_tip                                           # 옛 모델: 벽 안쪽 면에서 곧은 외팔보
    old = F * L_old / Z_g
    s_shelf = F * (yc - y_tip) / Z_g                                    # 선반 쪽 굽힘 끝선(Y 112)
    M_w = F * (y_mid - y_tip)                                           # 벽 쪽 굽힘 끝선(Z 610.5): 팔 = 선반 끝 ~ 벽 두께 가운데 50
    s_wall = M_w / Z_g + F / A_g                                        # 곧은 보 식 + 축 힘
    s_bend = KI * M_w / Z_g + F / A_g                                   # 굽힘 안쪽 겉면(가장 큰 자리)
    # 볼트: 아래로 당김 -> 벽 윗끝이 보에서 뜸. 받침점 = 맞댐 평면 밑 끝(Z 610.5). 옛 표의 받침점(벽 밑 Z 602.5)도 같이
    out = {}
    for lbl, zp in (('받침점 맞댐 평면 밑 끝 Z %.1f' % zc, zc), ('받침점 벽 밑 Z %.1f(옛 표)' % bb[2][0], bb[2][0])):
        d = [z - zp for z in hz]; Mp = F * (y_face - y_tip)
        T = [Mp * x / sum(v * v for v in d) for x in d]
        Rc = sum(T)
        M_hole = M_w - Rc * (hz[0] - zp)                                # 아래 구멍 자리 벽 굽힘(받침 반력이 줄여 줌)
        out[lbl] = {'볼트 당김 N [아래, 위]': [round(x, 1) for x in T], '받침 반력 N': round(Rc, 1), '아래 구멍 자리 굽힘 N·mm': round(M_hole),
                    '구멍 뺀 단면 MPa · SF': [round(abs(M_hole) / Z_net + F / ((b - 5.5) * t), 1), sf(abs(M_hole) / Z_net + F / ((b - 5.5) * t))]}
    I = b * t ** 3 / 12.0
    return {'F N': round(F, 2), '옛 모델(곧은 외팔 %.0f) MPa · SF' % L_old: [round(old, 1), sf(old)],
            '모델링부 값(팔 48.9) MPa · SF': [round(F * 48.9 / Z_g, 1), sf(F * 48.9 / Z_g)],
            '선반 굽힘 끝선(팔 %.0f) MPa · SF' % (yc - y_tip): [round(s_shelf, 1), sf(s_shelf)],
            '벽 굽힘 끝선(팔 %.0f, 곧은 식) MPa · SF' % (y_mid - y_tip): [round(s_wall, 1), sf(s_wall)],
            '굽힘 안쪽 겉면(굽은 보) MPa · SF': [round(s_bend, 1), sf(s_bend)],
            '벽 구멍 · 볼트': out, '지배 SF': sf(s_bend), '필요': need, '판정': judge(SY / s_bend, need),
            '끝 처짐 mm(팔 %.0f 곧은 외팔 어림)' % (y_mid - y_tip): round(F * (y_mid - y_tip) ** 3 / (3 * E * I), 3)}


m1['운전'] = clamp_case(run1, NEED_RUN); m1['오조작 50 N 아래로'] = clamp_case(F_MIS, NEED_MIS)
Tmax = max(max(v['볼트 당김 N [아래, 위]']) for v in m1['오조작 50 N 아래로']['벽 구멍 · 볼트'].values())
bz = sig('CB5-12_RXDC03_CLAMP_1')['bbox']
le1 = bz[3] - y_face                                                    # 볼트 끝 Y 128 - 보 앞면 Y 120
m1['볼트 CB5-12 x2 -> 보 앞벽 탭(STKR400 t8)'] = {'머리 자리 Y · 볼트 끝 Y': [bz[2] + 5.0, bz[3]], '물림 mm': le1, '물림/d': le1 / 5.0,
                                           '오조작 당김 N(가장 큰 것)': Tmax, 'handcalc': hc.calc(5, le1, Tmax, 4.5, '12.9', 'SS400', 8.5, 5.5, sf_min=2.0)}
m1['볼트 CB5-12 x2 -> 보 앞벽 탭(STKR400 t8)']['좌면(SUS304 400 MPa) 4.5 N·m'] = round(400 * math.pi / 4 * (8.5 ** 2 - 5.5 ** 2) / 4500.0, 2)
# 과사양: 지배 = 오조작 2.35 / 필요 2
m1['과사양'] = {'오조작 지배 SF / 필요': round(m1['오조작 50 N 아래로']['지배 SF'] / NEED_MIS, 2), '문턱': 3.0, '판정': '아님'}
# t3로 되돌릴 때(예외 DP4-EX3의 구멍–굽힘 10.64 >= 9를 살리는 길): 같은 식, 폭만 넓힘
alt = {}
for tt, bw in ((3.0, 14.0), (3.0, 22.0), (3.0, 24.0), (4.0, 14.0)):
    Mw = F_MIS * (y_face - tt / 2.0 - y_tip); s = ki_rect(tt, tt) * Mw / (bw * tt ** 2 / 6.0) + F_MIS / (bw * tt)
    alt['t%g x 폭 %g' % (tt, bw)] = {'굽힘 안쪽 겉면 MPa': round(s, 1), 'SF': sf(s), '구멍–굽힘 기준 2t + R': 3 * tt, '질량 g(전개 78.5 x 폭 x t 어림)': round(78.5 * bw * tt * 7.93e-3, 1)}
bneed = ki_rect(3.0, 3.0) * F_MIS * (y_face - 1.5 - y_tip) / ((SY / NEED_MIS - 0.6) * 9.0 / 6.0)
alt['t3에서 SF 2에 필요한 폭 mm'] = round(bneed, 1)
m1['두께 · 폭 민감도(참고 — PM 예외 DP4-EX3 판단용)'] = alt
# 민감도(판정 근거 아님): 위로 당김 — 선반에 묶는 구멍이 없어 하중 표에 없다
up_net = F_MIS * (y_mid - y_tip) / Z_net; up_head = F_MIS * (y_mid - y_tip) / Z_g
m1['민감도: 위로 50 N(하중 표에 없음 — 선반에 묶는 구멍 0)'] = {'아래 구멍 뺀 단면(머리 밑, 죄어 있음) MPa · SF': [round(up_net, 1), sf(up_net)],
                                                '머리 가장자리 온 단면 MPa · SF': [round(up_head, 1), sf(up_head)]}
R['1_beam_clamp'] = m1

# ================================================================== 2) T2 안내 P_RXDC03_T2_GUIDE_판금 (t3 그대로, 판금)
bb2 = GEO['P_RXDC03_T2_GUIDE']['new']['bbox']
bd2 = cyl('P_RXDC03_T2_GUIDE', 'Y', 3.0)[0]
hx = sorted(c['center'][0] for c in cyl('P_RXDC03_T2_GUIDE', 'Z', 2.75))
b2, t2 = bb2[1][1] - bb2[1][0], 3.0
xc2, zc2 = bd2['center']                                                # (-304.6, 230)
z_tip, z_top = bb2[2][0], bb2[2][1]                                     # 212, 236
z_mid = z_top - t2 / 2.0                                                # 플랜지 두께 가운데 234.5
Zg2, Zn2, A2 = b2 * t2 ** 2 / 6.0, (b2 - 5.5) * t2 ** 2 / 6.0, b2 * t2
KI2 = ki_rect(bd2['r'], t2)
run2 = N_CAB * F_CAB + 0.02 * g * 3
m2 = {'형상(STEP)': {'상자': bb2, '폭': b2, '두께': t2, '굽힘 안쪽 R · 중심 (X, Z)': [bd2['r'], [xc2, zc2]], '구멍 Ø5.5 X': hx, '립 끝 Z': z_tip,
                    '서명 부피 · 질량': [sig('P_RXDC03_T2_GUIDE_판금')['volume'], sig('P_RXDC03_T2_GUIDE_판금')['mass']]}, '굽은 보 계수': round(KI2, 3), '운전 하중 N': round(run2, 2)}


def t2_case(F, need):
    old = F * 21.0 / Zg2                                                # 옛 모델: 플랜지 밑면(Z 233)에서 곧은 외팔 21
    s_lip = F * (zc2 - z_tip) / Zg2                                     # 립 쪽 굽힘 끝선 Z 230(팔 18)
    M = F * (z_mid - z_tip)                                             # 플랜지 쪽: 팔 22.5(힘이 플랜지와 나란해 팔이 일정)
    s_bend = KI2 * M / Zg2 + F / A2
    s_head = M / Zg2 + F / A2                                           # 볼트 머리 가장자리(X -300.25) 온 단면
    s_net = M / Zn2 + F / ((b2 - 5.5) * t2)                             # 첫 볼트 구멍을 뺀 단면(+X로 밀 때 굽힘 ~ 볼트 사이가 블록에서 뜸)
    x_end = bb2[0][1]
    d = [x_end - x for x in hx]                                         # +X로 밀 때 받침점 = 플랜지 +X 끝(-280): 팔 16 · 6
    T = M * max(d) / sum(v * v for v in d)
    T_cons = M / (hx[1] - hx[0])                                        # 보수: 받침점이 둘째 볼트 자리(피치 10)
    gov = max(s_bend, s_net)
    return {'F N': round(F, 2), '옛 모델(곧은 외팔 21) MPa · SF': [round(old, 1), sf(old)], '립 굽힘 끝선(팔 %.0f) MPa · SF' % (zc2 - z_tip): [round(s_lip, 1), sf(s_lip)],
            '굽힘 안쪽 겉면(굽은 보, 팔 %.1f) MPa · SF' % (z_mid - z_tip): [round(s_bend, 1), sf(s_bend)],
            '볼트 머리 가장자리 온 단면 MPa · SF': [round(s_head, 1), sf(s_head)], '첫 구멍 뺀 단면 MPa · SF': [round(s_net, 1), sf(s_net)],
            '첫 볼트 당김 N [끝 받침, 보수]': [round(T, 1), round(T_cons, 1)], '지배 SF': sf(gov), '필요': need, '판정': judge(SY / gov, need),
            '립 끝 처짐 mm(팔 %.1f 어림)' % (z_mid - z_tip): round(F * (z_mid - z_tip) ** 3 / (3 * E * b2 * t2 ** 3 / 12.0), 4)}


m2['운전'] = t2_case(run2, NEED_RUN); m2['오조작 50 N'] = t2_case(F_MIS, NEED_MIS)
bt = sig('CB5-12_RXDC03_T2_1')['bbox']
le2 = bt[5] - z_top                                                     # 볼트 끝 Z 245 - 블록 턱 밑면 Z 236
m2['볼트 CB5-12 x2 -> 블록 턱 M5 막힌 탭(A5052)'] = {'물림 mm': le2, '오조작 당김 N(보수)': m2['오조작 50 N']['첫 볼트 당김 N [끝 받침, 보수]'][1],
                                              'handcalc(H32)': hc.calc(5, le2, m2['오조작 50 N']['첫 볼트 당김 N [끝 받침, 보수]'][1], 4.5, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0),
                                              'handcalc(H112)': hc.calc(5, le2, m2['오조작 50 N']['첫 볼트 당김 N [끝 받침, 보수]'][1], 4.5, '12.9', 'A5052-H112', 8.5, 5.5, sf_min=2.0)}
m2['과사양'] = {'오조작 지배 SF / 필요': round(m2['오조작 50 N']['지배 SF'] / NEED_MIS, 2), '문턱': 3.0, '판정': '아님(t3은 이 묶음 판금의 가장 얇은 두께)'}
R['2_t2_guide'] = m2

# ================================================================== 3) 관 받침 P_M08_TUBE_BRKT_U6 (A5052 -> PET-CF, 형상 그대로)
g3 = GEO['P_M08_TUBE_BRKT_U6']['new']; s3 = sig('P_M08_TUBE_BRKT_U6')
assert s3['material'] == 'PET-CF' and all(abs(a - b_) < 1e-3 for a, b_ in zip(s3['bbox'], [x for p in g3['bbox'] for x in p])), s3
bolt_z = cyl('P_M08_TUBE_BRKT_U6', 'X', 2.75)[0]['center'][1]            # 236
tube = cyl('P_M08_TUBE_BRKT_U6', 'Y', 3.25)[0]                           # 관 구멍 Ø6.5 축 Y, (X -347, Z 262), Y -10~10
x_face, x_plate, x_tube = -330.0, -338.0, tube['center'][0]              # 블록 맞댐면, 밑판 -X 면, 관 축
w_pl, t_pl = g3['bbox'][1][1] - g3['bbox'][1][0], x_face - x_plate     # 32, 8
z_bot, z_top3 = g3['bbox'][2][0], g3['bbox'][2][1]                       # 222, 272
boss_y = tube['depth']; boss_z = z_top3 - 252.0                          # 관 턱 20 x 20(Z 252~272)
run3 = 6.3 + 0.03 * g * 3                                                # 압력 펴짐 0.5 MPa x Ø4 + 관 몫 30 g x 3 g
m3 = {'형상(STEP, 스냅샷 — 서명 상자와 같음)': {'상자': g3['bbox'], '밑판 t': t_pl, '밑판 폭': w_pl, '볼트 Ø5.5 x2 Z': bolt_z, '관 구멍': tube, '관 턱 Y x Z': [boss_y, boss_z]},
      '서명 부피 · 질량 · 재질': [s3['volume'], s3['mass'], s3['material']], '운전 하중 N': round(run3, 2)}


def u6_case(F):
    Zp = (w_pl - 2 * 5.5) * t_pl ** 2 / 6.0                              # 볼트 줄(Z 236) 단면, 구멍 2 뺌
    s_plate = F * (tube['center'][1] - bolt_z) / Zp                      # -X 당김: 볼트 줄 위로 외팔 26
    s_boss = F * (x_plate - x_tube) / (boss_y * boss_z ** 2 / 6.0)       # Z 당김: 턱 뿌리(X -338) 20 x 20, 팔 9
    s_lig = F / ((boss_z - 6.5) * boss_y)                                # 관 구멍 양옆 살(당김)
    T_x = F * (tube['center'][1] - z_bot) / (bolt_z - z_bot) / 2.0       # -X 당김, 받침점 밑 끝 Z 222
    T_z = F * (x_face - x_tube) / (bolt_z - z_bot) / 2.0                 # Z(아래) 당김
    gov = max(s_plate, s_boss, s_lig)
    return {'F N': round(F, 2), '밑판 볼트 줄 MPa': round(s_plate, 2), '관 턱 뿌리 MPa': round(s_boss, 2), '관 구멍 옆 살 MPa': round(s_lig, 3),
            'SF(PET-CF 60)': sf(gov, SY_PET), 'SF(층간 30)': sf(gov, SY_PET_LAYER), '옛 A5052 SF': sf(gov, SY_AL), '볼트 당김 N/개 [-X, Z]': [round(T_x, 1), round(T_z, 1)],
            '끝 처짐 mm(-X, 외팔 26)': round(F * 26.0 ** 3 / (3 * E_PET * (w_pl - 11.0) * t_pl ** 3 / 12.0), 3)}


m3['운전'] = u6_case(run3); m3['오조작 50 N'] = u6_case(F_MIS)
m3['판정'] = {'운전(필요 3, 층간)': judge(m3['운전']['SF(층간 30)'], NEED_RUN), '오조작(필요 2, 층간)': judge(m3['오조작 50 N']['SF(층간 30)'], NEED_MIS)}
bu = sig('U4_WHEEL_N/CB5-16_M08_PX (U4_WHEEL_N:1/CB5-16_M08_PX:4)')['bbox']
le3 = x_face - bu[1] if bu[1] < x_face else bu[1] - x_face
ab = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)
Tu = max(m3['오조작 50 N']['볼트 당김 N/개 [-X, Z]'])
m3['볼트 CB5-16_M08_PX x2 -> 블록 P_RX19_BLOCK(A5052) -X 면 탭'] = {
    '볼트 상자 X': bu[:2], '물림 mm': round(le3, 2), '오조작 당김 N/개': Tu,
    'handcalc 1.5 N·m(H32)': hc.calc(5, le3, Tu, 1.5, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0),
    '좌면(PET-CF 한계 60 MPa, 머리 Ø8.5 / 구멍 Ø5.5)': {'넓이 mm2': round(ab, 1), '한도 N': round(60 * ab), '좌면 SF': {'%.1f N·m' % tq: round(60 * ab / (tq * 1000 / (0.2 * 5)), 2) for tq in (4.5, 3.0, 2.0, 1.5)},
                                                 '옛 A5052(210) 4.5 N·m': round(210 * ab / 4500.0, 2)},
    '조임 1.5 N·m 지정 볼트 수': {'DP-3까지': 41, '이 품번': 2, '합': 43}}
m3['과사양'] = {'오조작 층간 SF / 필요': round(m3['오조작 50 N']['SF(층간 30)'] / NEED_MIS, 2), '문턱': 3.0,
               'note': '살은 볼트 머리 · 관 구멍 자리가 정한다(밑판 t8, 관 턱 20 x 20). 출력품 25.6 g — 줄여도 값 차이 없음'}
R['3_tube_brkt_u6'] = m3

# ================================================================== 4) 세움 받침 P_RXDC03_RISER_BRKT_판금 (형상 그대로 — 앞 결과 다시 판정)
s4 = sig('P_RXDC03_RISER_BRKT_판금')
assert abs(s4['volume'] - RIS['mass']['volume_mm3_model']) < 0.01 and s4['bbox'] == [-318.6, -268.0, 65.0, 97.0, 250.0, 487.0], s4
fb = RIS['plusY_50N']['flange_bending_head_to_fold']
loc = [(c['model'], c['SF_first_yield'], c['SF_plastic_hinge']) for c in fb['cases']]
m4 = {'형상': '서명 부피 %.3f · 상자가 v2.30.5 해석 때와 같다 -> 앞 결과 그대로(E-21)' % s4['volume'],
      'ㄷ 단면 뿌리(Z 253)': {c['load'] + ' ' + c['dir']: [c['vm'], c['SF'], c['crit']] for c in RIS['cases'] if c['model'].startswith('ㄷ')},
      '가장 불리한 각 50 N': RIS['worst_direction_50N'],
      '국부 플랜지(+Y 50 N, 머리 ~ 날 발 사이 팔 %.1f · 폭 7.5 x t3)' % fb['arm_to_fold_midplane_mm']: {m: {'첫 항복 SF': a, '소성 힌지 SF': p} for m, a, p in loc},
      '앞 누름 볼트 CB4-12 당김 N(보수)': RIS['M4_design_tension_N'], '끝 처짐 오조작 Y · X mm': [RIS['cases'][2]['tip_defl_mm'], RIS['cases'][3]['tip_defl_mm']]}
real = [a for m, a, p in loc if '자유' not in m and '가장 후함' not in m]
m4['이 묶음 판정(국부 플랜지 >= 2)'] = {'첫 항복 SF 범위(날 발 자유 ~ 막힘)': [loc[0][1], loc[3][1]], '소성 힌지 SF 범위': [loc[0][2], loc[3][2]],
                               '판정': '미달 — 모든 경계 가정에서 첫 항복 SF < 2(%.2f~%.2f). 한 덩어리 이음(일부 구속 ~ 막힘) %.2f~%.2f, 소성 힌지 %.2f 이상이라 영구 변형(동작)으로는 보지 않음' % (
                                   loc[0][1], loc[3][1], min(real), max(real), loc[0][2])}
# 고침안 수치(예외 DP4-EX1 판단용)
M_root = F_MIS * (487.0 - 253.0)                 # 표 하중점 Z 487, 뿌리 Z 253
M_mod = F_MIS * (486.0 - 252.0)                  # 모델링부가 쓴 팔(같은 234)
neck = {}
for tt in (4.0, 5.0, 6.0):
    s = 6 * M_mod / (17.0 * tt ** 2); neck['목 17 x t%g' % tt] = {'MPa': round(s, 1), 'SF': sf(s)}
neck['t4에서 SF 2에 필요한 목 폭 mm'] = round(6 * M_mod * NEED_MIS / (SY * 16.0), 1)
neck['목 17에서 SF 2에 필요한 두께 mm'] = round(math.sqrt(6 * M_mod * NEED_MIS / (SY * 17.0)), 2)
neck['목 18(구멍 규칙이 허락하는 한계) x t4'] = sf(6 * M_mod / (18.0 * 16.0))
m4['접히는 형상(웨브 목만 남음) — 모델링부 수치 다시 셈'] = neck


def rect_col(bx, hy, sy, e_mod):
    """속 찬 사각 기둥(밀링 한 덩어리): Y 당김 굽힘 + 비틀림(먼 타이 팔 19.5), X 당김."""
    sY = M_root / (bx * hy ** 2 / 6.0); sX = M_root / (hy * bx ** 2 / 6.0)
    a, c = max(bx, hy), min(bx, hy)
    ka = 1 / 3.0 - 0.21 * (c / a) * (1 - c ** 4 / (12 * a ** 4))
    tau = F_MIS * 19.5 / (ka * a * c ** 2)
    vm = math.hypot(sY, math.sqrt(3) * tau)
    return {'Y 당김 VM MPa': round(vm, 1), 'SF': sf(vm, sy), 'X 당김 MPa · SF': [round(sX, 1), sf(sX, sy)],
            '끝 처짐 Y mm 오조작 · 운전': [round(F_MIS * 234.0 ** 3 / (3 * e_mod * bx * hy ** 3 / 12.0), 2), round(10.0 * 234.0 ** 3 / (3 * e_mod * bx * hy ** 3 / 12.0), 2)]}


mill = {'기둥 15 x 10.5(지금 ㄷ 단면 외곽 X -288~-273 · Y 74.5~85) A5052-H32': rect_col(15.0, 10.5, SY_AL, E_AL),
        '같은 기둥 A5052-H112(조질 미지정)': rect_col(15.0, 10.5, SY_AL112, E_AL),
        '기둥 15 x 8 A5052-H32': rect_col(15.0, 8.0, SY_AL, E_AL), '기둥 15 x 8 A5052-H112': rect_col(15.0, 8.0, SY_AL112, E_AL),
        '질량 g 어림(기둥 15 x 10.5 x 231 + 선반 50.6 x 20 x 3 + 밑판 35.6 x 22.5 x 6)': round((15 * 10.5 * 231 + 50.6 * 20 * 3 + 35.6 * 22.5 * 6) * 2.68e-3, 1),
        '지금 SUS304 질량 g': s4['mass'], '지금 ㄷ 단면 처짐 Y mm 오조작 · 운전': [RIS['cases'][2]['tip_defl_mm'], RIS['cases'][0]['tip_defl_mm']]}
m4['고침안 A — 밀링 한 덩어리(예외 DP4-EX1 제안)'] = mill
# 앞 누름 볼트 M5, 귀 자리 (-265.25, 79)
M50 = F_MIS * (487.0 - 251.5)
ear_y = 79.0
T_cons = M50 / (83.5 - ear_y)                                          # 받침점 웨브 가운데 Y 83.5(보수, 앞 회차와 같은 가정)
kr = M50 / ((97.0 - ear_y) ** 2 + 2 * (97.0 - 90.0) ** 2)              # 밑판 강체 · 받침점 뒤 끝 Y 97
bolt5 = {'당김 N [보수(받침점 웨브 가운데, 팔 %.1f), 밑판 강체]' % (83.5 - ear_y): [round(T_cons), round(kr * (97.0 - ear_y))],
         '지금 M4 자리(팔 5.25) 당김 N': RIS['M4_design_tension_N']}
for lbl, base in (('H32', 'A5052'), ('H112', 'A5052-H112')):
    for le in (8.0, 9.0):
        c = hc.calc(5, le, round(T_cons), 4.5, '12.9', base, 8.5, 5.5, sf_min=2.0)
        bolt5['M5 물림 %g · 블록 %s' % (le, lbl)] = {'운용': c['sf_operating'], '조임 4.5 N·m': c['sf_tightening'], 'ok': c['ok'], 'needs_fea': c['needs_fea']}
c = hc.calc(5, 8.0, round(kr * (97.0 - ear_y)), 4.5, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
bolt5['M5 물림 8 · H32 · 밑판 강체(밀링 밑판 t6)'] = {'운용': c['sf_operating'], 'ok': c['ok']}
c = hc.calc(5, 10.0, round(T_cons), 4.5, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
bolt5['M5 물림 10 · H32(밀링 밑판 t6 + CB5-16, 턱 t14 관통 탭)'] = {'운용': c['sf_operating'], '조임 4.5 N·m': c['sf_tightening'], 'needs_fea': c['needs_fea']}
bolt5['좌면(받침이 A5052 밀링이면 210 MPa) 4.5 N·m'] = round(210 * ab / 4500.0, 2)
m4['고침안 — 앞 누름 볼트 CB5-12, 귀 자리 (-265.25, 79)'] = bolt5
R['4_riser_brkt'] = m4

# ================================================================== 5) 리드 안내 P_RXDC03_LEAD_GUIDE_판금 (형상 그대로 — 앞 결과 다시 판정)
s5 = sig('P_RXDC03_LEAD_GUIDE_판금'); lg = DC03['P_RXDC03_LEAD_GUIDE']
assert abs(s5['mass'] - 87.074) < 0.01, s5['mass']


def lg_arm(bw, tt):
    s_arm = F_MIS * 47.6 / (bw * tt ** 2 / 6.0)
    a, c = max(bw, tt), min(bw, tt)
    ka = 1 / 3.0 - 0.21 * (c / a) * (1 - c ** 4 / (12 * a ** 4))
    tau = F_MIS * 58.0 / (ka * a * c ** 2); sYs = F_MIS * 47.6 / (tt * bw ** 2 / 6.0)
    vm = math.hypot(sYs, math.sqrt(3) * tau)
    return {'팔 굽힘(Z 쪽) MPa · SF': [round(s_arm, 1), sf(s_arm)], '비틀림 + 굽힘(Y 당김) VM · SF': [round(vm, 1), sf(vm)], '지배 SF': min(sf(s_arm), sf(vm)),
            '운전 팔 SF(12.94 N)': sf(12.94 * 47.6 / (bw * tt ** 2 / 6.0))}


m5 = {'형상': '서명 질량 %.3f g = v2.29.3 해석 때 87.1 g -> 앞 결과 그대로(E-21)' % s5['mass'],
      '지금(폭 14 x t3, 외팔 47.6)': lg_arm(14.0, 3.0), '앞 결과 json': {'팔 오조작 SF': lg['arm_mis']['SF'], '비틀림 + 굽힘 SF': lg['arm_twist_mis']['SF'], '운전 SF': lg['arm_run']['SF']}}
assert m5['지금(폭 14 x t3, 외팔 47.6)']['팔 굽힘(Z 쪽) MPa · SF'][1] == lg['arm_mis']['SF'] and m5['지금(폭 14 x t3, 외팔 47.6)']['비틀림 + 굽힘(Y 당김) VM · SF'][1] == lg['arm_twist_mis']['SF']
m5['이 묶음 판정(팔 >= 2)'] = judge(m5['지금(폭 14 x t3, 외팔 47.6)']['지배 SF'], NEED_MIS)
m5['고침안 수치(예외 DP4-EX2 판단용)'] = {'폭 14 x t4(지시대로)': lg_arm(14.0, 4.0)}
for bw in (18.0, 20.0, 22.0, 24.0):
    m5['고침안 수치(예외 DP4-EX2 판단용)']['폭 %g x t3(두께 그대로 팔만 넓힘)' % bw] = lg_arm(bw, 3.0)
bw = 14.0
while lg_arm(bw, 3.0)['지배 SF'] < NEED_MIS: bw += 0.1
m5['고침안 수치(예외 DP4-EX2 판단용)']['t3에서 SF 2에 필요한 팔 폭 mm'] = round(bw, 1)
R['5_lead_guide'] = m5

# ================================================================== 6) 묶음 완료 판정(강도 3항)
R['6_judge'] = [
    {'항목': '선반(P_RXDC03_BEAM_CLAMP_판금 t4)', '기준': '오조작 SF >= 2', '값': m1['오조작 50 N 아래로']['지배 SF'], '판정': m1['오조작 50 N 아래로']['판정'],
     '운전': m1['운전']['지배 SF'], '비고': '굽힘 안쪽 겉면(굽은 보). 모델링부 3.13은 곧은 보 · 팔 48.9'},
    {'항목': 'T2 안내(P_RXDC03_T2_GUIDE_판금 t3, 판정 밖 — 바뀐 하중 부품)', '기준': '오조작 SF >= 2', '값': m2['오조작 50 N']['지배 SF'], '판정': m2['오조작 50 N']['판정'], '운전': m2['운전']['지배 SF']},
    {'항목': '관 받침 U6(PET-CF, 판정 밖 — 재질 바뀜)', '기준': '오조작 SF >= 2(층간 30 MPa)', '값': m3['오조작 50 N']['SF(층간 30)'], '판정': m3['판정']['오조작(필요 2, 층간)'], '운전': m3['운전']['SF(층간 30)']},
    {'항목': '세움 받침 국부 플랜지(P_RXDC03_RISER_BRKT_판금, 그대로)', '기준': '오조작 SF >= 2', '값': [loc[0][1], loc[3][1]], '판정': '미달'},
    {'항목': '리드 안내 팔(P_RXDC03_LEAD_GUIDE_판금, 그대로)', '기준': '오조작 SF >= 2', '값': m5['지금(폭 14 x t3, 외팔 47.6)']['지배 SF'], '판정': m5['이 묶음 판정(팔 >= 2)']},
]
json.dump(R, open(ROOT + '/fea/results/detail_DP-4_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 화면 요약(E-20, 15줄 안)
o = m1['오조작 50 N 아래로']
print('1 선반 t4: 옛 모델', o['옛 모델(곧은 외팔 48) MPa · SF'], '| 굽힘 안쪽', o['굽힘 안쪽 겉면(굽은 보) MPa · SF'], 'Ki', m1['굽은 보 계수(안쪽 R = t)'], '| 운전', m1['운전']['지배 SF'], '| 처짐', [v for k, v in o.items() if k.startswith('끝 처짐')])
print('  벽 · 볼트', {k[:12]: (v['볼트 당김 N [아래, 위]'], v['구멍 뺀 단면 MPa · SF']) for k, v in o['벽 구멍 · 볼트'].items()})
bc = m1['볼트 CB5-12 x2 -> 보 앞벽 탭(STKR400 t8)']; print('  볼트 물림', bc['물림 mm'], bc['handcalc']['sf_operating'], bc['handcalc']['sf_tightening'], 'ok', bc['handcalc']['ok'], '좌면', bc['좌면(SUS304 400 MPa) 4.5 N·m'])
print('  민감도', {k: (v if not isinstance(v, dict) else v.get('SF')) for k, v in alt.items()}, '| 위로', m1['민감도: 위로 50 N(하중 표에 없음 — 선반에 묶는 구멍 0)'])
o2 = m2['오조작 50 N']; print('2 T2 t3: 옛', o2['옛 모델(곧은 외팔 21) MPa · SF'], '굽힘', [v for k, v in o2.items() if k.startswith('굽힘 안쪽')], '구멍', o2['첫 구멍 뺀 단면 MPa · SF'], '머리', o2['볼트 머리 가장자리 온 단면 MPa · SF'], '운전', m2['운전']['지배 SF'], 'T', o2['첫 볼트 당김 N [끝 받침, 보수]'])
b2c = m2['볼트 CB5-12 x2 -> 블록 턱 M5 막힌 탭(A5052)']; print('  볼트 물림', b2c['물림 mm'], 'H32', b2c['handcalc(H32)']['sf_tightening'], b2c['handcalc(H32)']['ok'], 'H112', b2c['handcalc(H112)']['sf_tightening'], b2c['handcalc(H112)']['ok'])
print('3 U6 PET-CF: 오조작', m3['오조작 50 N'], '| 운전 SF', m3['운전']['SF(PET-CF 60)'], m3['운전']['SF(층간 30)'])
bu6 = m3['볼트 CB5-16_M08_PX x2 -> 블록 P_RX19_BLOCK(A5052) -X 면 탭']; print('  볼트 물림', bu6['물림 mm'], bu6['handcalc 1.5 N·m(H32)']['sf_operating'], bu6['handcalc 1.5 N·m(H32)']['sf_tightening'], '좌면', bu6['좌면(PET-CF 한계 60 MPa, 머리 Ø8.5 / 구멍 Ø5.5)']['좌면 SF'])
print('4 세움 받침 국부', loc, '| 목', neck)
print('  밀링', {k[:22]: (v.get('SF'), v.get('끝 처짐 Y mm 오조작 · 운전')) if isinstance(v, dict) else v for k, v in mill.items()})
print('  M5 귀', bolt5)
print('5 리드 안내', m5['지금(폭 14 x t3, 외팔 47.6)'], '|', {k: (v['지배 SF'] if isinstance(v, dict) else v) for k, v in m5['고침안 수치(예외 DP4-EX2 판단용)'].items()})
