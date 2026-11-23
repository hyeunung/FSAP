# -*- coding: utf-8 -*-
"""RX-05 해석부 손계산 (v2.23.0, E-18). FEA 못 함 — 환경 없음(D-16).
대상(새 하중 부품 STEP 2개): P_M03_GCOV_SM(A5052 t2 판금 덮개) · P_M03_GCOV_RBRKT_SM(A5052 t3 Z자 받침)
형상 bbox는 STEP CARTESIAN_POINT에서 다시 읽어 설계 표(mech_RX-05_design.md 2절, model.md 1절)와 맞춘다(옛 케이스 좌표 재사용 안 함).
하중: 자중 x 3 g(잰 질량, model.md 6절), 오조작 손 100 N(덮개 앞벽 수평 · 윗판 앞끝 아래 · 받침 윗 날개 위/아래), 솔 털 끌림(값 없음 -> 기록).
  액추에이터 추력 없음(덮개 · 받침은 고정, 움직이는 부품과 맞닿는 것은 솔 털뿐 — 기준선).
기준: 요구서 6-1 = M-09 기본값(일반 3, 오조작 2). SF < 1.2 = 동작. 처짐은 6-2 미정(D-08) -> 기록.
재질: A5052-H32 Rp0.2 160 MPa(보수, 설계안과 같음 — handcalc 표 A5052 195는 H34), E 69,000. 보 P_M07_BEAM STKR400(탭 모재, handcalc SS400 245).
실행: python -X utf8 -B fea/cases/mech_RX-05_handcalc.py -> fea/results/mech_RX-05_handcalc.json"""
import json, math, re, subprocess, sys
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/"
OUT = ROOT + "fea/results/mech_RX-05_handcalc.json"
HC = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
STEP = ROOT + "tools/out/mech_RX-05/stepout/"
RP, E, G = 160.0, 69000.0, 9.81
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf < need * 1.1: return "됨(기준 +10% 안 — FEA 확인 대상, 환경 없음 D-16)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in kw.items()}


def bbox(fn):
    txt = open(STEP + fn, encoding="utf-8", errors="replace").read()
    cp = {m.group(1): tuple(float(v) for v in m.groups()[1:]) for m in re.finditer(
        r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)", txt)}
    pts = [cp[m.group(1)] for m in re.finditer(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)", txt)]  # 꼭짓점만(축 원점 제외)
    return [[round(min(p[i] for p in pts), 2), round(max(p[i] for p in pts), 2)] for i in range(3)], len(pts)


def handcalc(args):
    r = subprocess.run([sys.executable, "-B", HC] + args, capture_output=True, text=True, encoding="utf-8")
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-800:], "err": r.stderr[-400:]}


# ---------------------------------------------------------------- 0. 형상 확인(STEP)
for fn in ("P_M03_GCOV_SM.step", "P_M03_GCOV_RBRKT_SM.step"):
    bb, n = bbox(fn)
    rec("bbox_" + fn[:-5], bbox_xyz=bb, points=n)
# 설계 표: GCOV X -2180~-420 · Y 27~120 · Z 290~520 / RBRKT X -2160~-440 · Y 100~150 · Z 247~261

# ---------------------------------------------------------------- 1. 덮개 앞 C단면(앞벽 Y 27~29 Z 290~466 · 윗 띠 Y 27~46 · 립 Y 44~46 Z 440~466 · 밑 날개 Y 29~37)
rects = [  # (y0, y1, z0, z1)
    (27, 29, 290, 466), (27, 46, 466, 468), (44, 46, 440, 466), (29, 37, 290, 292)]
A = sum((y1 - y0) * (z1 - z0) for y0, y1, z0, z1 in rects)
yc = sum((y1 - y0) * (z1 - z0) * (y0 + y1) / 2 for y0, y1, z0, z1 in rects) / A
zc = sum((y1 - y0) * (z1 - z0) * (z0 + z1) / 2 for y0, y1, z0, z1 in rects) / A
Iz = sum((z1 - z0) * (y1 - y0) ** 3 / 12 + (y1 - y0) * (z1 - z0) * ((y0 + y1) / 2 - yc) ** 2 for y0, y1, z0, z1 in rects)  # Y 방향 굽힘
Iy = sum((y1 - y0) * (z1 - z0) ** 3 / 12 + (y1 - y0) * (z1 - z0) * ((z0 + z1) / 2 - zc) ** 2 for y0, y1, z0, z1 in rects)  # Z 방향 굽힘
cy = max(abs(46 - yc), abs(yc - 27)); cz = max(abs(468 - zc), abs(zc - 290))
L = 1500.0  # 솔 창 길이 = 앞 C단면이 끝의 닫힌 윗판 사이를 건너는 길이(단순 지지, 보수)
P = 100.0
M = P * L / 4
s_h = M * cy / Iz; d_h = P * L ** 3 / (48 * E * Iz)
rec("C_front_hand_Y", load="손 100 N 수평(+Y) 창 가운데, 단순 지지 1500", A_mm2=A, yc=yc, Iz_mm4=Iz, c=cy,
    M_Nmm=M, sigma_MPa=s_h, SF=RP / s_h, need=2.0, deflect_mm=d_h)
s_v = M * cz / Iy; d_v = P * L ** 3 / (48 * E * Iy)
rec("C_front_hand_Z", load="손 100 N 아래(-Z) 윗판 앞끝 창 가운데", Iy_mm4=Iy, sigma_MPa=s_v, SF=RP / s_v, need=2.0, deflect_mm=d_v)
# 자중 x 3 g: 앞 C단면 + B1 솔(홀더+털 0.5786 kg / 1.52 m) + B3 솔(0.7864 kg / 1.756 m)
w = (A * 2.68e-6 + 0.5786 / 1520 + 0.7864 / 1756) * G * 3  # N/mm
Mw = w * L ** 2 / 8
rec("C_front_selfweight_3g", w_N_per_mm=w, M_Nmm=Mw, sigma_MPa=Mw * cz / Iy, SF=RP / (Mw * cz / Iy), need=3.0,
    deflect_mm=5 * w * L ** 4 / (384 * E * Iy))

# ---------------------------------------------------------------- 2. 앞벽 국부 판 굽힘(손 100 N 수평, 앞벽 t2를 윗 C 띠에서 아래로 뻗은 외팔 판)
t = 2.0; a = 466 - 297  # 윗 띠 ~ B3 홀더 볼트 줄
# (가) 홀더(10 x 10 A5052 연속 띠)를 무시: 반무한 외팔 판 가장자리 점 하중 뿌리 최대 모멘트 m ~ 0.509 P (Jaramillo) -> b_eff ~ a/0.509
m_a = 0.509 * P
s_a = 6 * m_a / t ** 2
b_eff = a / 0.509
d_a = P * a ** 3 / (3 * E * b_eff * t ** 3 / 12)
rec("wall_plate_no_holder", load="손 100 N 앞벽 아래 끝(+Y), 홀더 띠 무시(보수)", a_mm=a, m_root_N=m_a, b_eff_mm=b_eff,
    sigma_MPa=s_a, SF=RP / s_a, need=2.0, deflect_mm=d_a)
# (나) 홀더 띠를 탄성 기초 위 보로: 판 외팔 강성 k = 3 E (t^3/12) / a^3 (N/mm/mm), 띠 I = 10^4/12
k = 3 * E * (t ** 3 / 12) / a ** 3
Ib = 10 ** 4 / 12
beta = (k / (4 * E * Ib)) ** 0.25
q = P * beta / 2
s_b = 6 * q * a / t ** 2
rec("wall_plate_with_holder", load="같은 손 하중, B3 홀더 10x10 띠가 X로 나눔(탄성 기초 보)", k_N_mm2=k, beta_per_mm=beta,
    spread_len_mm=math.pi / beta, q_peak_N_per_mm=q, sigma_MPa=s_b, SF=RP / s_b, need=2.0,
    deflect_mm=P * beta / (2 * k))
# 앞벽이 +Y로 밀렸을 때 뒤에 있는 것: 관 U5C_1 최소 Y 42.5(앞벽 Y 29와 13.5), 솔 B3 홀더는 앞벽에 붙어 같이 움직임
rec("wall_push_room", gap_to_tube_U5C1_mm=42.5 - 29.0,
    total_push_mm=d_h + d_a, note="손 오조작 때만(탄성, 놓으면 되돌아옴). 보수(홀더 무시) 합 처짐이 틈 13.5를 넘으면 기록")

# ---------------------------------------------------------------- 3. 뒤 날개 볼트 CB5-12 x7 (보 앞면 STKR400 t8 M5 관통 탭, 물림 8)
# 손 100 N 아래 윗판 앞끝 Y 27: 앞 띠는 창(1500) 동안 뒤와 끊겨 있어 하중은 양 끝 닫힌 윗판으로 감 -> 끝 하나에 50 N(가운데)~100 N(끝 바로 위)
arm_load = 120 - 27; arm_bolt = 500 - 468  # 날개 밑 굽힘(Z 468)을 받침점으로
F_hand_end = 100.0 * arm_load / arm_bolt  # 끝 바로 위 손: 가까운 볼트 1개가 다 받음(보수)
m_cov = 2.995 + 1.157 + 0.786 + 0.06  # kg (model.md 6절)
W3 = m_cov * G * 3
F_w = W3 * 65 / arm_bolt / 7  # 무게중심 팔 약 65
F_bolt = F_hand_end + F_w
rec("rear_bolt_load", hand_end_N=F_hand_end, selfweight_3g_N_total=W3, selfweight_per_bolt_N=F_w,
    shear_per_bolt_N=W3 / 7, worst_bolt_N=F_bolt, note="손 하중을 볼트 1개가 다 받는다고 봄(보수). 끝 윗판이 브래킷에 얹힌 받침은 무시")
R["handcalc_rear_CB5"] = handcalc(["--d", "5", "--pitch", "0.8", "--le", "8", "--load", f"{F_bolt:.1f}",
                                   "--bolt", "12.9", "--base", "SS400", "--sf-min", "2"])

# ---------------------------------------------------------------- 4. 받침 P_M03_GCOV_RBRKT_SM (A5052 t3, Z자: 밑 다리 Y 117(114)~150 Z 247~250, 세운 판 Y 114~117, 윗 날개 Y 100~117 Z 258~261)
t3 = 3.0
y_load = 105.0  # B4 홀더 가운데(볼트 줄 Y 105)
y_bolt, y_heel, y_riser = 140.0, 150.0, 115.5
b = 100.0  # 손 폭(볼트 피치 210 안)
# 4-1 아래로 손 100 N: 앞이 내려가며 다리 뒤끝 Y 150이 보 밑면을 받침점으로 -> 볼트 인장
Fb_dn = P * (y_heel - y_load) / (y_heel - y_bolt)
m_b = 2.995 * 0 + 0.788 + 0.655 + 0.02
W3b = m_b * G * 3
Fb_w = W3b * (y_heel - y_load) / (y_heel - y_bolt) / 7
M_leg = (Fb_dn - P) * (y_heel - y_bolt)  # 볼트 자리 단면 모멘트
s_leg = 6 * M_leg / ((b - 5.5) * t3 ** 2)
rec("bracket_leg_hand_down", load="손 100 N 아래 B4 홀더(Y 105), 받침점 다리 뒤끝 Y 150", bolt_N=Fb_dn, selfweight_3g_per_bolt_N=Fb_w,
    M_leg_Nmm=M_leg, sigma_MPa=s_leg, SF=RP / s_leg, need=2.0)
M_r = P * (y_riser - y_load)
s_r = 6 * M_r / (b * t3 ** 2)
rec("bracket_riser_flange", load="같은 손, 세운 판 · 윗 날개 뿌리", M_Nmm=M_r, sigma_MPa=s_r, SF=RP / s_r, need=2.0,
    deflect_flange_mm=P * (y_riser - y_load) ** 3 / (3 * E * b * t3 ** 3 / 12))
# 4-2 위로 손 100 N: 세운 판 쪽(Y 117)이 받침점 -> 볼트 인장 작음
Fb_up = P * (117 - y_load) / (y_bolt - 117)
rec("bracket_hand_up", bolt_N=Fb_up)
# 과사양 검토: 다리 t2였다면
s_leg2 = 6 * M_leg / ((b - 5.5) * 2.0 ** 2)
rec("bracket_leg_if_t2", sigma_MPa=s_leg2, SF=RP / s_leg2, need=2.0, note="과사양 note용(문제로 세지 않음)")
R["handcalc_bracket_CB5"] = handcalc(["--d", "5", "--pitch", "0.8", "--le", "8", "--load", f"{Fb_dn + Fb_w:.1f}",
                                      "--bolt", "12.9", "--base", "SS400", "--sf-min", "2"])

# ---------------------------------------------------------------- 5. 솔 홀더 CB4-12 (홀더 M4 탭 — 임시 홀더 A5052, 물림 10)
w_B1 = 0.5786 * G * 3 / 9  # 9개, 3 g
R["handcalc_holder_CB4_selfweight"] = handcalc(["--d", "4", "--pitch", "0.7", "--le", "10", "--load", f"{w_B1:.2f}",
                                                "--bolt", "12.9", "--base", "A5052", "--sf-min", "3"])
rec("brush_drag", note="솔 털 끌림(대차가 털 사이를 지날 때 X 힘)은 마찰 값 없음 -> 기록만(7절 시제품, 설계검토서 제어 제약 'X 서보 토크 여유'). 홀더 · 덮개에 주는 힘은 털이 휘어 지나가는 크기라 손 100 N보다 작다고 봄(가정)")

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k_, v in R.items():
    if isinstance(v, dict):
        s = {kk: v[kk] for kk in ("sigma_MPa", "SF", "deflect_mm", "verdict", "worst_bolt_N", "bolt_N", "bbox_xyz") if kk in v}
        if "judge" in v or "ok" in v: s = {kk: v[kk] for kk in v if kk in ("ok", "judge", "min_sf", "verdict")}
        print(k_, json.dumps(s, ensure_ascii=False)[:300])
