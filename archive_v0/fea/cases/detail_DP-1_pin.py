"""디테일링 DP-1 해석부 2회차 손계산 (2026-10-31, 대상 FSAP_v0.6.5).

바뀐 하중 부품: STEP대기_MS3-8_T06 (맞춤핀, v0.6.4 원통+C0.3 -> v0.6.5 R=D 끝 + 15° 끝, SUJ2).
해석 못 함 — 환경 없음(자료대기 D-16). 손계산만.

1) 핀 STEP 형상 확인: 면 종류·자리(구 R3 중심 Z57, 원통 r1.5 Z54/57 시작, 원뿔 15° Z61 시작)
2) 전단면 Z57(팔 밑살 Z54~57 | 축 끝 Z57) 단면 = 원통 전체인지
3) 핀 전단 SF (지난 모델 그대로: 오조작 T 축 둘레 토크 9,139 N·mm, 핀 r5, 마찰 무시) + 마찰 분담 참고
4) 지압(새로 더함): 팔 SUS304 구멍(원통 물림 길이), 축 PSFJT 구멍
5) 팔·맞날 틈: 형상 그대로 -> detail_handcalc.json machined_L(th5, tv3, gap 0.4) 재사용
"""
import json, math, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
STEP = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-1', 'stepout', 'STEP대기_MS3-8_T06_v065.step')
OLD = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-1', 'stepout', 'STEP대기_MS3-8_T06.step')
PREV = os.path.join(ROOT, 'fea', 'results', 'detail_handcalc.json')
OUT = os.path.join(ROOT, 'fea', 'results', 'detail_DP-1_pin.json')


def surfaces(path):
    t = open(path, encoding='utf-8', errors='ignore').read()
    ent = dict(re.findall(r'^#(\d+)=(.*);\s*$', t, re.M))

    def pt(i):
        m = re.search(r"\(([^()]*)\)\)$", ent[i])
        return [round(float(v), 4) for v in m.group(1).split(',')]

    out = []
    for i, s in ent.items():
        m = re.match(r"(CYLINDRICAL_SURFACE|SPHERICAL_SURFACE|CONICAL_SURFACE|PLANE)\('',#(\d+)(.*)\)", s)
        if not m:
            continue
        ax = re.match(r"AXIS2_PLACEMENT_3D\('',#(\d+)", ent[m.group(2)])
        args = [float(v) for v in m.group(3).strip(',').split(',') if v]
        out.append({'type': m.group(1), 'origin': pt(ax.group(1)), 'args': [round(a, 4) for a in args]})
    return out


res = {'case': 'detail_DP-1_pin', 'fea': '해석 못 함 — 환경 없음(자료대기 D-16)', 'step': os.path.relpath(STEP, ROOT)}
res['surfaces_v065'] = surfaces(STEP)
res['surfaces_v064'] = surfaces(OLD)

# --- 형상 (모델 보고서 r2 + STEP 확인) ---
D = 3.0; R = D / 2
Z_ARM_BOT, Z_IF, Z_HOLE_END = 54.0, 57.0, 63.0     # 팔 밑면, 팔-축 맞댐(전단면), 축 핀 구멍 끝(Ø3 × 6)
Z_TAPER = 61.0                                     # 15° 시작
z_crown = 57.0 - math.sqrt(3.0 ** 2 - R ** 2)      # 구 R3 중심 Z57 이 r1.5 원통과 만나는 높이
res['geometry'] = {
    'crown_full_dia_from_Z': round(z_crown, 3),
    'shear_plane_Z': Z_IF,
    'shear_plane_full_cylinder': z_crown < Z_IF < Z_TAPER,
    'L_bear_arm_v065': round(Z_IF - z_crown, 3),
    'L_bear_arm_v064(C0.3)': round(Z_IF - (Z_ARM_BOT + 0.3), 3),
    'L_bear_shaft_v065': round(Z_TAPER - Z_IF, 3),
}

# --- 하중 (지난 모델 그대로, detail_fea.md 2-2) ---
Tz = 190.4 * (72.0 - 24.0)           # 오조작 T: 팔 Fy × 축–칼 거리 = 9,139 N·mm
r_pin = 5.0
T_fric = 0.15 * 6000.0 * 5.4         # M5 12.9 6 N·m 예압 마찰 4,838 N·mm
F_pin = Tz / r_pin                   # 마찰 무시(지난 모델, 보수)
F_pin_fric = max(0.0, Tz - T_fric) / r_pin
A = math.pi * R ** 2

tau_allow = 0.6 * 1000.0             # 지난 가정 그대로(SUJ2 58HRC~ 실제는 이보다 큼 -> 보수)
SY_SUS = 205.0                       # SUS304 팔
SY_SHAFT = 345.0                     # 축 PSFJT16: S45C 보수값(실물 재질 미확인, D-37)


def sf(a, b):
    return round(a / b, 2)


res['shear'] = {
    'Tz_Nmm': round(Tz), 'F_pin_N': round(F_pin), 'A_mm2': round(A, 3), 'tau_MPa': round(F_pin / A, 1),
    'allow_MPa': tau_allow, 'SF': sf(tau_allow, F_pin / A),
    'with_friction': {'F_pin_N': round(F_pin_fric), 'SF': sf(tau_allow, F_pin_fric / A)},
    'SUJ2_real_ref': {'allow_MPa(0.6×2000)': 1200, 'SF': sf(1200, F_pin / A)},
}


def bearing(F, L, sy):
    s = F / (D * L)
    return {'L_mm': round(L, 3), 'sigma_MPa': round(s, 1), 'SF_yield': sf(sy, s), 'SF_1.5Sy': sf(1.5 * sy, s)}


g = res['geometry']
res['bearing'] = {
    'arm_v065_no_friction': bearing(F_pin, g['L_bear_arm_v065'], SY_SUS),
    'arm_v064_no_friction': bearing(F_pin, g['L_bear_arm_v064(C0.3)'], SY_SUS),
    'arm_v065_friction': bearing(F_pin_fric, g['L_bear_arm_v065'], SY_SUS),
    'shaft_v065_no_friction': bearing(F_pin, g['L_bear_shaft_v065'], SY_SHAFT),
    'arm_pin_D4_no_friction': {'note': '참고: Ø4 핀이면', **{k: v for k, v in bearing(F_pin * 0 + F_pin, g['L_bear_arm_v065'], SY_SUS).items()}},
}
# Ø4 참고는 지름만 바꿔 다시
L4 = (Z_IF - Z_ARM_BOT) - (4.0 - math.sqrt(4.0 ** 2 - 2.0 ** 2))   # R=D=4 끝 높이 0.536을 뺀 팔 안 원통 물림
s4 = F_pin / (4.0 * L4)
res['bearing']['arm_pin_D4_no_friction'] = {'note': '참고: MS4 (R=D 끝) 이면', 'L_mm': round(L4, 3), 'sigma_MPa': round(s4, 1),
                                           'SF_yield': sf(SY_SUS, s4), 'SF_1.5Sy': sf(1.5 * SY_SUS, s4)}

# --- 팔·맞날 틈 재사용 ---
prev = json.load(open(PREV, encoding='utf-8'))
m = [x for x in prev['machined_L'] if x['th'] == 5.0 and x['gap_xp'] == 0.4][0]
res['arm_reuse'] = {'from': 'fea/results/detail_handcalc.json machined_L th5 tv3 gap0.4', **m,
                    'shear_gap_after_bracket_tilt': round(m['shear_gap_op'] - 0.041, 3)}

json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ('geometry', 'shear', 'bearing', 'arm_reuse')}, ensure_ascii=False, indent=1))
