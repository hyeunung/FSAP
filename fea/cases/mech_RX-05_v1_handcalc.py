# -*- coding: utf-8 -*-
"""RX-05 RX05-V1 해석부 손계산 (v2.26.0, E-18). FEA 못 함 — 환경 없음(D-16).
바뀐 것: 덮개 P_M03_GCOV_SM 윗판 구멍 Ø4.5 -> Ø5.4 x18(Y 37.5 · 96), 클린칭 너트 NFPS-M4-1 x18(윗판 밑, STEP대기_),
  볼트 CB4-12(홀더 탭) -> CB4-20(위에서, 홀더 Ø4.5 관통 -> 윗판 -> 너트, 물림 4), 솔 띠 B1 · B2 두 토막.
하중 경로: 솔 토막 무게는 홀더 밑면 -> 윗판 윗면(누름, 볼트 거치지 않음). 볼트는 예압(조임)과 들어 올림(손 오조작 100 N, 털 끌림)만 받는다.
  들어 올리면 볼트가 너트를 판 쪽으로 당겨 너트 몸이 윗판 밑면을 누른다(밀림 방향 아님).
기준: 요구서 6-1 = M-09 기본값(일반 3, 오조작 2). SF < 1.2 = 동작. 처짐 6-2 미정(D-08) -> 기록.
재질: 덮개 A5052-H32 Rp0.2 160(보수, 지난 회차와 같음), 홀더 A5052(D-224 임시), 너트 SUS304, 볼트 12.9.
카탈로그 값(tools/out/mech_RX-05/catalog.md, 사이트 열지 않음 — 임시): NFPS-M4-1 회전 강도 약 2.3 N·m, 밀림 약 1,300 N. 체결 토크 1.2 N·m(설계안 임시).
실행: python -X utf8 -B fea/cases/mech_RX-05_v1_handcalc.py -> fea/results/mech_RX-05_v1_handcalc.json"""
import json, math, re, subprocess, sys
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/"
OUT = ROOT + "fea/results/mech_RX-05_v1_handcalc.json"
HC = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
STEP = ROOT + "tools/out/mech_RX-05/stepout/P_M03_GCOV_SM.step"
RP, E, G = 160.0, 69000.0, 9.81
R = {}


def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf < need * 1.1: return "됨(기준 +10% 안)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"


def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in kw.items()}


def handcalc(args):
    r = subprocess.run([sys.executable, "-B", HC] + args, capture_output=True, text=True, encoding="utf-8")
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-800:], "err": r.stderr[-400:]}


# ---------------------------------------------------------------- 0. 형상 확인(STEP 텍스트: bbox, 반지름 2.7 원통 수)
txt = open(STEP, encoding="utf-8", errors="replace").read()
cp = {m.group(1): tuple(float(v) for v in m.groups()[1:]) for m in re.finditer(
    r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)\s*,\s*([-\d.Ee+]+)", txt)}
pts = [cp[m.group(1)] for m in re.finditer(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(\d+)", txt)]
bb = [[round(min(p[i] for p in pts), 2), round(max(p[i] for p in pts), 2)] for i in range(3)]
cyl = re.findall(r"CYLINDRICAL_SURFACE\s*\(\s*'[^']*'\s*,\s*#\d+\s*,\s*([-\d.Ee+]+)\s*\)", txt)
rad = {}
for r_ in cyl:
    k = round(float(r_), 3); rad[k] = rad.get(k, 0) + 1
rec("bbox_P_M03_GCOV_SM", bbox_xyz=bb, vertices=len(pts), cylinder_radius_count=rad,
    expect="X -2180~-420 · Y 27~120 · Z 290~520, 반지름 2.7 구멍 18(면이 나뉘면 36), 4.5 반지름 0")

# ---------------------------------------------------------------- 1. 앞 C단면 순단면(구멍 Ø5.4 Y 34.8~40.2가 윗 띠 Y 27~46을 끊는 자리)
def csec(rects):
    A = sum((y1 - y0) * (z1 - z0) for y0, y1, z0, z1 in rects)
    yc = sum((y1 - y0) * (z1 - z0) * (y0 + y1) / 2 for y0, y1, z0, z1 in rects) / A
    zc = sum((y1 - y0) * (z1 - z0) * (z0 + z1) / 2 for y0, y1, z0, z1 in rects) / A
    Iz = sum((z1 - z0) * (y1 - y0) ** 3 / 12 + (y1 - y0) * (z1 - z0) * ((y0 + y1) / 2 - yc) ** 2 for y0, y1, z0, z1 in rects)
    Iy = sum((y1 - y0) * (z1 - z0) ** 3 / 12 + (y1 - y0) * (z1 - z0) * ((z0 + z1) / 2 - zc) ** 2 for y0, y1, z0, z1 in rects)
    return A, yc, zc, Iz, Iy

gross = [(27, 29, 290, 466), (27, 46, 466, 468), (44, 46, 440, 466), (29, 37, 290, 292)]
net = [(27, 29, 290, 466), (27, 34.8, 466, 468), (40.2, 46, 466, 468), (44, 46, 440, 466), (29, 37, 290, 292)]
L, P = 1500.0, 100.0
M = P * L / 4
for name, rs in (("gross", gross), ("net_hole_5.4", net)):
    A, yc, zc, Iz, Iy = csec(rs)
    cy = max(abs(46 - yc), abs(yc - 27)); cz = max(abs(468 - zc), abs(zc - 290))
    # 구멍은 9개가 187.5 피치로 띄엄띄엄 -> 처짐은 총단면, 응력은 구멍 자리 순단면 x 응력집중 Kt(판 구멍 약 2.5, 순단면 기준은 띠가 좁아 보수로 순단면 응력에 그대로 곱하지 않고 띠 국부만 따로 봄)
    sh = M * cy / Iz; sv = M * cz / Iy
    rec("C_front_" + name, A_mm2=A, Iz_mm4=Iz, Iy_mm4=Iy,
        sigma_hand_Y_MPa=sh, SF_hand_Y=RP / sh, sigma_hand_Z_MPa=sv, SF=RP / sv, need=2.0,
        deflect_hand_Z_mm=P * L ** 3 / (48 * E * Iy), deflect_hand_Y_mm=P * L ** 3 / (48 * E * Iz))
# 구멍 둘레 국부: 윗 띠 막대 응력에 Kt. 손 100 N 아래(Z) 굽힘에서 윗 띠는 거의 중립축 먼 쪽(Z 468) -> 띠 응력 = sv 순단면
A, yc, zc, Iz, Iy = csec(net)
cz = 468 - zc
s_strip = M * cz / Iy
Kt = 2.5  # 띠 폭 대비 구멍(5.4/19) -> 피터슨 판 구멍 약 2.4~2.5
rec("hole_edge_peak_hand_Z", note="항복은 국부 첨두로 판정하지 않는 것이 보통이나 보수로 기록(정적, 연성 재질)",
    sigma_nominal_MPa=s_strip, Kt=Kt, sigma_peak_MPa=s_strip * Kt, SF=RP / (s_strip * Kt), need=2.0)

# ---------------------------------------------------------------- 2. 볼트 CB4-20 -> NFPS-M4-1 (물림 4, 토크 1.2 N·m 임시)
w_seg = (0.1769 + 0.0760) * G * 3 / 4  # A 토막 4볼트, 자중 3 g (누름이라 볼트엔 0 — 들어 올림 쪽으로 보수 합산)
F_lift = 100.0 + w_seg * 4  # 손 100 N 들어 올림을 볼트 1개가 다 받음(보수) + 토막 무게
rec("bolt_external_load", hand_lift_one_bolt_N=F_lift, brush_drag_N="≤ 20(설계안 임시, 마찰 — 볼트엔 전단, 예압 마찰로 받음)")
R["handcalc_CB4_20_into_NFPS"] = handcalc(["--d", "4", "--pitch", "0.7", "--le", "4", "--load", f"{F_lift:.1f}",
                                           "--torque", "1.2", "--bolt", "12.9", "--base", "SUS304", "--sf-min", "3"])
# 토크를 낮춰야 할 때 예: 0.8 N·m
R["handcalc_CB4_20_into_NFPS_T0.8"] = handcalc(["--d", "4", "--pitch", "0.7", "--le", "4", "--load", f"{F_lift:.1f}",
                                                "--torque", "0.8", "--bolt", "12.9", "--base", "SUS304", "--sf-min", "3"])
Fp = 1.2 / (0.2 * 0.004)
rec("preload", T_Nm=1.2, K=0.2, F_N=Fp)

# ---------------------------------------------------------------- 3. 너트 몸 받침 · 회전 · 밀림
A_nut = math.pi / 4 * (7.9 ** 2 - 5.4 ** 2)
rec("nut_body_bearing_plate", A_mm2=A_nut, sigma_MPa=(Fp + F_lift) / A_nut, SF=RP / ((Fp + F_lift) / A_nut), need=3.0,
    note="예압 + 손 들어 올림. 판은 홀더(위)와 너트 몸(아래) 사이 눌림 — 펀칭 아님")
rec("nut_torque_out", T_tight_Nm=1.2, T_out_catalog_Nm=2.3, SF=2.3 / 1.2, need=3.0,
    note="카탈로그 값 임시(사이트 열지 않음). 표준 토크 3.8 N·m로 조이면 SF 0.61 -> 너트 헛돎. 도면·설계검토서에 토크 지정 필요")
rec("nut_pushout", note="들어 올림 · 조임 모두 너트를 판 쪽으로 당김 -> 밀림 하중 0. 위에서 누르는 힘은 홀더가 윗판에 바로 전함", SF="해당 없음")
A_head = math.pi / 4 * (7.0 ** 2 - 4.5 ** 2)
rec("head_bearing_holder", A_mm2=A_head, sigma_MPa=(Fp + F_lift) / A_head, SF=RP / ((Fp + F_lift) / A_head), need=3.0,
    note="홀더 A5052 임시(D-224). 받침 허용을 항복과 같게 본 보수값")
# 홀더 10x10 띠에 구멍 Ø4.5 -> 남은 살 (10-4.5)/2 = 2.75 양쪽, 예압 압축은 받침으로 봄. 털 끌림 전단은 마찰
mu = 0.2
rec("segment_slip", bolts_A=4, F_fric_N=4 * Fp * mu, drag_N=20.0, SF=4 * Fp * mu / 20.0, need=3.0)

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k_, v in R.items():
    if isinstance(v, dict):
        keep = ("sigma_MPa", "SF", "SF_hand_Y", "deflect_hand_Z_mm", "verdict", "bbox_xyz", "cylinder_radius_count",
                "worst", "ok", "sf_tightening", "sf_operating", "hand_lift_one_bolt_N", "F_N")
        print(k_, json.dumps({kk: v[kk] for kk in keep if kk in v}, ensure_ascii=False)[:300])
