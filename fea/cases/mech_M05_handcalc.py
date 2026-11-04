# -*- coding: utf-8 -*-
"""M05 해석부 손계산 — U7 테이프 툴 카세트(후보 tools/out/M05/cand.sc). FEA 환경 없음(D-16) -> 손계산만.
형상: 모델링부 mech_M05_model.md 2절 좌표 + stepout STEP bbox(아래 0절에서 다시 읽어 맞춤).
하중: 실린더 추력(요구서 2-4 운전 압력 미정 -> 앞 과제와 같은 0.5 MPa 임시, D-111), 작업 저항(봉제 반력 50 N·손 오조작 100 N D-83,
      테이프 절단 30 N 설계안 임시 D-M05-1, 테이프 장력 10 N D-06), 자중 x3 g(카세트 2.0 kg 설계안 D-M05-2), 걸쇠 당김 1,500 N(임시 D-M05-3).
판정: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2), 과사양 = 필요 SF의 3배 이상. SF < 1.2만 '동작'.
"""
import json, math, re, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import beam, calc

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
G = 9.81
P = 0.5                       # MPa 임시
SY = {'SUS304': 205.0, 'A5052': 195.0, 'PA12': 48.0, 'SK5': 1200.0, 'SUJ2': 1370.0}
E = {'SUS304': 193000.0, 'A5052': 70000.0, 'PA12': 1700.0, 'SK5': 206000.0}
SF_OP, SF_MIS = 3.0, 2.0
out = {'assume': {'P_MPa': P, 'cassette_kg': 2.0, 'sew_reaction_N': 50.0, 'hand_misuse_N': 100.0,
                  'cut_force_N': 30.0, 'tape_tension_N': 10.0, 'latch_N': 1500.0,
                  'UPPER_base': 'SS400 대용(867 주물 FC급, D-10) — handcalc 표에 FC 없음'}}

def verdict(sf, need):
    if sf < 1.2: return '동작'
    if sf < need: return '디테일'
    if sf >= 3 * need: return '과사양 note'
    return '됨'

# ---------- 0) STEP bbox ----------
pat = re.compile(r"CARTESIAN_POINT\('[^']*',\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*\)")
names = ['P_M05_CST_PLATE', 'P_M05_HOLDER', 'P_M05_BINDER_BRKT', 'P_M05_GUIDE', 'P_M05_CUT_FIX', 'P_M05_CYL_BRKT',
         'P_M05_FEED_BRKT', 'P_M05_CUT_HOLDER', 'P_M05_CUT_BLADE', 'P_M05_TUCK_HOLDER', 'P_M05_TUCK_BLADE', 'P_M05_FEED_CARR']
out['step_bbox'] = {}
for n in names:
    t = open(f'{ROOT}/tools/out/mech_M05/stepout/{n}.step', encoding='utf-8', errors='ignore').read()
    pts = [tuple(map(float, m)) for m in pat.findall(t)]
    out['step_bbox'][n] = {'n_pts': len(pts), 'min': [round(min(c), 2) for c in zip(*pts)] if pts else None,
                           'max': [round(max(c), 2) for c in zip(*pts)] if pts else None}

A10 = math.pi / 4 * 10 ** 2; A16 = math.pi / 4 * 16 ** 2
F10 = A10 * P; F16 = A16 * P; F16_pull = math.pi / 4 * (16 ** 2 - 5 ** 2) * P
out['thrust'] = {'CJ2B10_push_N': round(F10, 1), 'CDJ2B16_push_N': round(F16, 1), 'CDJ2B16_pull_N': round(F16_pull, 1),
                 'note': '실린더가 행정 끝에서 제 커버에 닿을 때 힘은 몸 안에서 닫힌다. 아래는 로드가 막혔을 때(걸림·오조작) 전 추력이 브래킷으로 간다고 본 보수 값'}
W = 2.0 * G
R = {}

# ---------- 1) P_M05_CYL_BRKT (SUS304 t3 L): CJ2B10 x2, 축 Y, 면 Y -174~-171 X 14~47 Z 34~110, 굽힘 X 47 ----------
F = 2 * F10
lev = 47 - 29
Zs = 76 * 3 ** 2 / 6
s = F * lev / Zs
sf = SY['SUS304'] / s
R['CYL_BRKT_bend_root'] = {'F_N': round(F, 1), 'lever_mm': lev, 'Z_mm3': round(Zs, 1), 'sigma': round(s, 2), 'SF': round(sf, 1),
                           'need': SF_OP, 'verdict': verdict(sf, SF_OP)}
# 실린더 한 개 자리(Ø8.5 구멍 주변) 판 굽힘: 판 고정단 X47에서 끝 X14까지 보, 실린더 하나 39 N, 판 폭 76 중 실린더 영향폭 26으로 줄여 봄
R['CYL_BRKT_local_beam'] = beam(t=3.0, b=26.0, length=float(lev), load=round(F10, 1), e=E['SUS304'], sy=SY['SUS304'], sf_min=SF_OP)
# 날개 볼트 CB5 x2 -> 판 탭 A5052 물림 8: Y 전단 + Z 축 모멘트(지레 X 21, 받침 굽힘 모서리 Y -174 ~ 볼트 Y -195 = 21)
Tb = F * (50 - 29) / 21 / 2
R['CYL_BRKT_bolt_CB5_le8_A5052'] = calc(d=5, le=8, load=round(Tb + F / 2, 1), torque=4.5, bolt='12.9', base='A5052', sf_min=SF_OP)

# ---------- 2) P_M05_FEED_BRKT (SUS304 t3 L): CDJ2B16 축 -Z at (X70, Y-106), 굽힘 X 61, 세운 다리 폭 Y -145~-115 ----------
Fz = F16 + 3 * 0.25 * G
lev = math.hypot(70 - 61, -106 - (-115))
Zs = 30 * 9 / 6
s = Fz * lev / Zs
sf = SY['SUS304'] / s
R['FEED_BRKT_bend_root'] = {'F_N': round(Fz, 1), 'lever_mm(X 9 + Y 내밈 9 합)': round(lev, 1), 'Z_mm3': Zs, 'sigma': round(s, 2),
                            'SF': round(sf, 1), 'need': SF_OP, 'verdict': verdict(sf, SF_OP)}
R['FEED_BRKT_leg_beam'] = beam(t=3.0, b=30.0, length=round(lev, 1), load=round(Fz, 1), e=E['SUS304'], sy=SY['SUS304'], sf_min=SF_OP)
Tb = Fz * (70 - 58) / (293 - 262) / 2
R['FEED_BRKT_bolt_CB5_le8_A5052'] = calc(d=5, le=8, load=round(Tb + Fz / 2, 1), torque=4.5, bolt='12.9', base='A5052', sf_min=SF_OP)

# ---------- 3) 날: CUT_BLADE SK5 t1.5, TUCK_BLADE SUS304 t1.5 (얇은 판 -> beam 먼저) ----------
# 칼 날 내밈: 잡이 앞면 Y -138 -> 날 끝 Y -120~-123.4 = 약 18. 날 벌림 힘(Z) = 절단 힘의 1/3 가정 + 막힘 시 전 추력은 판 면 안(Y) 방향
R['CUT_BLADE_separation_beam'] = beam(t=1.5, b=32.0, length=18.0, load=round(F10 / 3, 1), e=E['SK5'], sy=SY['SK5'], sf_min=SF_OP)
R['CUT_BLADE_inplane_buckle'] = {'note': 'Y 방향 39 N은 날 판 면 안 압축. 오일러 Pcr = pi^2 E I/(4L^2), I = 1.5*32^3/12 강축이 아닌 약축 32*1.5^3/12',
                                 'Pcr_N': round(math.pi ** 2 * E['SK5'] * (32 * 1.5 ** 3 / 12) / (4 * 18 ** 2), 0),
                                 'SF': round(math.pi ** 2 * E['SK5'] * (32 * 1.5 ** 3 / 12) / (4 * 18 ** 2) / F10, 1)}
R['TUCK_BLADE_push_beam'] = beam(t=1.5, b=30.0, length=18.0, load=round(F10 / 3, 1), e=E['SUS304'], sy=SY['SUS304'], sf_min=SF_OP)
R['TUCK_BLADE_inplane_buckle'] = {'Pcr_N': round(math.pi ** 2 * E['SUS304'] * (30 * 1.5 ** 3 / 12) / (4 * 18 ** 2), 0),
                                  'SF': round(math.pi ** 2 * E['SUS304'] * (30 * 1.5 ** 3 / 12) / (4 * 18 ** 2) / F10, 1)}
# 고정날 CUT_FIX SK5 t2: 안내 블록 위에 통째로 얹힘, 볼트 CB5-12 x2 -> 인서트(PA12). Y 면 안 전단만
R['CUT_FIX_bolts'] = {'shear_per_bolt_N': round(F10 / 2, 1), 'note': '인서트 MBIS5 (PA12) 전단·당김 허용 수백 N(카탈로그 값 미확인) 대비 작다'}

# ---------- 4) PA12 잡이·보내기 캐리어·안내 ----------
# CUT/TUCK_HOLDER 26x13x16 블록: 로드 끝 너트(M4/M5 급 좌면 약 35 mm2)로 39 N
pb = F10 / 35.0
R['CUT_TUCK_HOLDER_nut_bearing'] = {'p_MPa': round(pb, 2), 'SF': round(SY['PA12'] / pb, 1), 'verdict': verdict(SY['PA12'] / pb, SF_OP),
                                     'note': 'PA12 SLS 인장 약 48 MPa(임시). 날 볼트 CB5-16 -> 인서트는 날 면 안 전단 20 N/개'}
pb = F16 / 35.0
R['FEED_CARR_nut_bearing'] = {'p_MPa': round(pb, 2), 'SF': round(SY['PA12'] / pb, 1), 'verdict': verdict(SY['PA12'] / pb, SF_OP)}
Zc = 11.5 * 27 ** 2 / 6
s = (2 * 10.0) * (70 - 30) / Zc
R['FEED_CARR_body_bend'] = {'F_N(테이프 장력 x2)': 20.0, 'lever': 40, 'sigma': round(s, 2), 'SF': round(SY['PA12'] / s, 0),
                            'note': '몸 X 24~79 · Y 11.5 · Z 27, 로드 X 70, 발톱 X 약 30'}
R['FEED_CARR_claw'] = {'note': '한쪽 방향 휨 발톱(M05-X6)은 테이프를 문질러 넘는 유연 거동이라 모델로 판정하지 않는다(요구서 7절 시제품 확인). 강성은 발톱 치수가 정해지면 handcalc beam(guided)로 셈'}
R['GUIDE'] = {'note': '안내 블록은 판에 볼트 3 + 인서트로 붙고, 하중은 고정날 반력 39 N·테이프 장력 10 N뿐. 단면 38x26 기둥 232 높이 굽힘 50 N x 232 / (26*38^2/6) = '
                      + str(round(50 * 232 / (26 * 38 ** 2 / 6), 2)) + ' MPa'}

# ---------- 5) P_M05_BINDER_BRKT (A5052 L): 누운 다리 t6 X 0~50, 세운 다리 t8 ----------
mb = 0.3
Fv = 3 * mb * G + 10.0
Zl = 50 * 6 ** 2 / 6
s = Fv * (42 - 15) / Zl
R['BINDER_BRKT_lying_leg'] = {'F_N': round(Fv, 1), 'sigma': round(s, 2), 'SF': round(SY['A5052'] / s, 0), 'verdict': verdict(SY['A5052'] / s, SF_OP)}
# 봉제 반력 50 N(Y)이 바인더 Z 약 40 -> 누운 다리 Z 63: 비틀림 50 x 23 = 1150 N mm, 누운 다리 50x6 비틀림 상수 b t^2/3 근사
tau = 50 * 23 / (50 * 6 ** 2 / 3)
R['BINDER_BRKT_torsion'] = {'tau_MPa': round(tau, 2), 'SF': round(0.577 * SY['A5052'] / tau, 0)}
# 바인더 볼트 CB5-12 x2, 바인더 윗면 탭 물림 6(M05-X5), 바인더 재질 D-10 -> SS400 대용
R['BINDER_bolt_CB5_le6'] = calc(d=5, le=6, load=round(Fv / 2 + 50 * 23 / 25 / 2, 1), torque=4.5, bolt='12.9', base='SS400', sf_min=SF_OP)
R['BINDER_BRKT_to_plate_CB5_le8_A5052'] = calc(d=5, le=8, load=round(50 / 2 + 50 * (63 - 41.5) / 30 / 2, 1), torque=4.5, bolt='12.9', base='A5052', sf_min=SF_OP)

# ---------- 6) 핀 MSTH6-20 x2 · 판 구멍 · 걸이 팔 B 구멍 ----------
Mx = 50 * (300 - 40)
Fp_op = Mx / 65 + 3 * W / 2
Fp_mis = (100 * (300 - 220)) / 65 + 3 * W / 2 + 100 / 2
Ap = math.pi / 4 * 36
pins = {}
for cn, Fp, need in [('운전(봉제 반력+3W)', Fp_op, SF_OP), ('오조작(손 100 N, 손 구멍 Z 220)+3W', Fp_mis, SF_MIS)]:
    tau = Fp / Ap
    pins[cn] = {'F_per_pin_N': round(Fp, 1), 'tau_pin': round(tau, 1), 'SF_pin(SUJ2 0.577Rp)': round(0.577 * SY['SUJ2'] / tau, 0),
                'bearing_plate_A5052_8': round(Fp / 48, 1), 'SF_plate_hole': round(SY['A5052'] / (Fp / 48), 1),
                'bearing_armB_SUS_4': round(Fp / 24, 1), 'SF_armB_hole': round(SY['SUS304'] / (Fp / 24), 1),
                'pin_root_bend(내밈 12 중 걸이 t4 중심 10)': round(Fp * 10 / (math.pi * 6 ** 3 / 32), 1),
                'SF_root_bend': round(SY['SUJ2'] / (Fp * 10 / (math.pi * 6 ** 3 / 32)), 1), 'need': need}
R['PINS_MSTH6'] = pins

# ---------- 7) P_M05_HOLDER (SUS304 t4): 날개 A 떼짐, 팔 B 굽힘, 날개 C 걸쇠 당김 ----------
H = {}
# 7a 날개 C(XY 면, X 18~46 · Y 50, t4) 걸쇠 1,500 N(X 방향, 면 안): 순단면 인장·구멍 끝 전단 밀림·갈고리 면압
L = 1500.0
H['wingC_net_tension'] = round(L / ((50 - 10) * 4), 1)
H['wingC_shear_out(구멍 끝 X 32 -> 굽힘 X 46, 2면)'] = round(L / (2 * 14 * 4), 1)
H['wingC_hook_bearing(갈고리 폭 12)'] = round(L / (12 * 4), 1)
H['wingC_SF_min'] = round(SY['SUS304'] / max(H['wingC_net_tension'], H['wingC_shear_out(구멍 끝 X 32 -> 굽힘 X 46, 2면)'] / 0.577,
                                              H['wingC_hook_bearing(갈고리 폭 12)'] / 2), 1)
# 걸쇠 힘의 Z 성분(갈고리가 위에서 걸어 내림) 30 % 가정: 날개 C 굽힘 X 30 -> 굽힘 X 46 지레 16, 폭 Y 50
Fz = 0.3 * L
s = Fz * 16 / (50 * 16 / 6)
H['wingC_bend_Zcomp30%'] = {'sigma': round(s, 1), 'SF': round(SY['SUS304'] / s, 2), 'verdict': verdict(SY['SUS304'] / s, SF_OP),
                            'note': '토글 걸쇠 당김선은 몸 축(X)에 가깝다. Z 성분 비율은 KC-40340 STEP 대기(D-M05-3)'}
# 7b 팔 B: 봉제 반력 모멘트 13 N m, 면 안(강축) — 설계안 8.1 MPa 재확인
Zs = 4 * 49 ** 2 / 6
H['armB_inplane'] = {'M_Nmm': Mx, 'sigma': round(Mx / Zs, 1), 'SF': round(SY['SUS304'] / (Mx / Zs), 1)}
# 7c 날개 A(XZ 면, X 10~46 · Z 285~334): 팔 B의 X축 모멘트가 굽힘선 X 46에서 날개 A 면 밖(Y) 힘으로 들어온다.
#     아래 끝 Z 285를 받침으로 볼트 줄 Z 310까지 당김 T = M / 25, 이 T가 굽힘선 X 46 -> 가까운 볼트 X 36 지레 10 으로 날개 A를 판 굽힘
for cn, M, need in [('운전', Mx, SF_OP), ('오조작', 100 * (300 - 220) + Mx, SF_MIS)]:
    T = M / 25.0
    for bw in (24.0, 49.0):
        s = T * 10 / (bw * 16 / 6)
        H[f'wingA_peel_{cn}_width{int(bw)}'] = {'T_N': round(T, 0), 'sigma': round(s, 1), 'SF': round(SY['SUS304'] / s, 2),
                                                 'need': need, 'verdict': verdict(SY['SUS304'] / s, need)}
    H[f'wingA_bolt_{cn}_CB5_le10_UPPER'] = calc(d=5, le=10, load=round(T, 1), torque=4.5, bolt='12.9', base='SS400', sf_min=need)
R['HOLDER'] = H

# ---------- 8) P_M05_CST_PLATE (A5052 t8) ----------
C = {}
# 8a 걸쇠 몸 볼트 CB5-12 x2 -> 판 탭(물림 8) 1,500 N 당김
C['latch_bolt_CB5_le8_A5052'] = calc(d=5, le=8, load=L / 2, torque=4.5, bolt='12.9', base='A5052', sf_min=SF_OP)
# 8b 걸쇠 볼트 줄(Z 314) ~ 팔 B 위 끝 맞닿음(Z 약 330) 사이 판 굽힘, 유효 폭 40
s = L * 16 / (40 * 8 ** 2 / 6)
C['latch_local_bend'] = {'sigma': round(s, 1), 'SF': round(SY['A5052'] / s, 2), 'verdict': verdict(SY['A5052'] / s, SF_OP)}
# 8c 오조작 X+ 100 N(손 구멍 Z 220)로 판이 팔 B에서 떨어지는가: 위 끝 Z 334 받침, 걸쇠 Z 314 지레 20
Mres = L * (334 - 314); Mext = 100 * (334 - 220) + 3 * W * (50 - 35)
C['separation_misuse'] = {'M_latch': Mres, 'M_ext': round(Mext, 0), 'SF': round(Mres / Mext, 2), 'need': SF_MIS,
                          'verdict': verdict(Mres / Mext, SF_MIS)}
# 8d 판 몸: 아랫띠(Z 20~75, Y -200~-40)에 실린더·바인더, 윗띠(Y -200~-106)로 핀까지. 윗띠 굽힘(설계안) + 손 구멍 빼기
Zu = 8 * (94 - 40) ** 2 / 6
s = (50 * 260 + 100 * 80) / Zu
C['upper_band_with_hand_hole'] = {'sigma': round(s, 2), 'SF': round(SY['A5052'] / s, 0), 'verdict': verdict(SY['A5052'] / s, SF_MIS)}
C['self_weight_defl'] = {'note': '판 2 kg x 3 g, 핀에서 아랫띠까지 280 기둥, 면 밖(X) 하중 60 N x 지레 15 -> 900 N mm, I = 94*8^3/12; 처짐(mm)',
                         'defl_mm': round(900 * 280 ** 2 / (2 * E['A5052'] * 94 * 8 ** 3 / 12), 3)}
R['CST_PLATE'] = C

out['results'] = R
json.dump(out, open(f'{ROOT}/fea/results/mech_M05_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 15줄 요약
def sfof(x):
    if isinstance(x, dict):
        if 'sf_operating' in x: return min(x['sf_operating'].values())
        for k in ('SF', 'sf'):
            if k in x: return x[k]
    return None
lines = []
for k, v in R.items():
    if isinstance(v, dict) and sfof(v) is not None:
        lines.append(f'{k}: SF {sfof(v)}')
    elif isinstance(v, dict):
        for kk, vv in v.items():
            s_ = sfof(vv)
            if s_ is not None: lines.append(f'{k}.{kk}: SF {s_}')
print('\n'.join(lines))
