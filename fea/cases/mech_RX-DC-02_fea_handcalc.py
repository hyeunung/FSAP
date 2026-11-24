# -*- coding: utf-8 -*-
"""RX-DC-02 해석부 손계산 (v2.29.3, U2_FLAP 감쇠 가스 스프링 로드 아래 뒤집기, E-18).
FEA 못 함 — 환경 없음(D-16). 엔진 handcalc import.
치수: mech_RX-DC-02_model.md 3절 표 + 새 하중 부품 STEP(tools/out/mech_RX-DC-02/stepout/*.step) CARTESIAN_POINT bbox.
가스 스프링 힘: tools/out/mech_RX-12-C1/r2_gasspring.json — 눈 중심 간 길이 범위(271.76~320.51)가 RX-12-C1과 같아 힘 표 그대로.
  운전 = 공차 끝(L_ext 327 · F1 1,232) 최대값(-90).
  오조작 = 펴는 중 손 놓침 -> 펴짐 끝 감쇠가 판 운동 에너지를 받을 때 핀이 당겨짐(인장).
    E 20.339 J(공차 끝, mech_RX-12-C1_fix1_handcalc.py E_free_tol), 감쇠 구간 15 mm(D-231 임시값),
    감쇠력 최고/평균 1.5(임시값 — 감쇠 곡선 없음, D-231). 순 인장 = E/s x 1.5.
모델(fea/models.json 관례, RX-12-C1과 같음): 외팔 핀 팔 = 귀판 두께 가운데 ~ 눈 가운데, 귀판 지압은 평균, 귀판 면 밖 굽힘 = F x 팔 / (폭 x t^2/6).
기준: 요구서 6-1 = M-09 기본값(운전 SF 3, 오조작 SF 2). SF < 1.2 = 동작.
실행: python -X utf8 -B fea/cases/mech_RX-DC-02_fea_handcalc.py -> fea/results/mech_RX-DC-02_fea_handcalc.json"""
import json, math, re, glob, os, importlib.util
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
ENG = "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools/handcalc.py"
sp = importlib.util.spec_from_file_location("handcalc", ENG); hc = importlib.util.module_from_spec(sp); sp.loader.exec_module(hc)
OUT = ROOT + "/fea/results/mech_RX-DC-02_fea_handcalc.json"
SY_AL, SY_SUS, SY_SCM = 195.0, 205.0, 785.0      # A5052-H32 · SUS304 · SCM435 (이 프로젝트 값)
E_ST = 206000.0
R = {}

def verdict(sf, need):
    if sf < 1.2: return "동작(SF < 1.2)"
    if sf < need: return "디테일(기준 미달)"
    if sf >= 3 * need: return "됨(과사양 note)"
    return "됨"

def rec(key, **kw):
    if "SF" in kw and "need" in kw: kw["verdict"] = verdict(kw["SF"], kw["need"])
    R[key] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in kw.items()}

# ---- STEP bbox(면 선택 대신 치수 확인)
bb = {}
for f in sorted(glob.glob(ROOT + "/tools/out/mech_RX-DC-02/stepout/*.step")):
    pts = re.findall(r"CARTESIAN_POINT\('[^']*',\(([-\d.E+, ]+)\)\)", open(f, encoding="latin-1").read())
    xs = [tuple(float(v) for v in p.split(",")) for p in pts]
    xs = [p for p in xs if len(p) == 3 and all(abs(c) > 1e-9 for c in p)]   # 축 배치 원점(0,0,0) 빼기
    if xs:
        bb[os.path.basename(f)[:-5]] = [[round(min(p[i] for p in xs), 2), round(max(p[i] for p in xs), 2)] for i in range(3)]
R["_step_bbox"] = bb

# ---- 하중
gs = json.load(open(ROOT + "/tools/out/mech_RX-12-C1/r2_gasspring.json", encoding="utf-8"))
tol = gs["cases"]["Lext327_F1232"]["rows"]
F_OP = max(r["F"] for r in tol)                 # 운전 최대(압축)
E_TOL, S_DAMP, PEAK = 20.339, 15.0, 1.5
F_MIS = E_TOL / (S_DAMP / 1000.0) * PEAK        # 오조작 순 인장
W_SPRING = (57714.9 + 16241.1) * 7.85e-6 * 9.80665 * 3   # 자중 x3 g(N) — 무시할 크기 확인용
rec("loads", F_op_N=F_OP, F_misuse_tension_N=F_MIS, self_weight_3g_N=W_SPRING,
    note="운전 = 스프링 압축 최대(공차 끝). 오조작 = 펴짐 끝 감쇠가 판 운동 에너지를 받는 순 인장(임시: 감쇠 15 mm, 최고/평균 1.5)")

d = 8.0; A = math.pi * d * d / 4; Zp = math.pi * d ** 3 / 32
cases = (("op", F_OP, 3.0), ("misuse", F_MIS, 2.0))

# ---- 1. 핀 P Ø8 SCM435: 귀판 t6(Y -1230~-1224) 외팔. 하중점 = 몸통 눈 가운데 Y -1242. 팔 = 3 + 7(SPACER_P) + 5 = 15
lev_P = 3.0 + 7.0 + 5.0
for tag, F, need in cases:
    s = F * lev_P / Zp
    rec("PIN_P_bend_" + tag, part="P_RX12C1_GS_PIN_P", F_N=F, lever_mm=lev_P, sigma=s, SF=SY_SCM / s, need=need)
    rec("PIN_P_shear_" + tag, part="P_RX12C1_GS_PIN_P", tau=F / A, SF=0.58 * SY_SCM / (F / A), need=need)
s_old = F_OP * 8.0 / Zp
rec("PIN_P_bend_before", part="P_RX12C1_GS_PIN_P", lever_mm=8.0, sigma=s_old, SF=SY_SCM / s_old,
    note="RX-12-C1 v2.27.1(눈이 귀판에 바로 붙음) 같은 식")
rec("PIN_P_bend_op_modelingref", part="P_RX12C1_GS_PIN_P", lever_mm=12.0, F_N=1420.0,
    sigma=1420.0 * 12.0 / Zp, SF=SY_SCM / (1420.0 * 12.0 / Zp), note="모델링부 식(귀판 면 고정, 1,420 N) 참고")

# ---- 2. 귀판 GS_LUG SUS304 t6 폭 40: 지압(평균) + 면 밖 굽힘(팔 15)
for tag, F, need in cases:
    brg = F / (d * 6.0)
    rec("LUG_bearing_" + tag, part="P_RX12C1_GS_LUG", p=brg, SF=SY_SUS / brg, need=need)
    s_l = F * lev_P / (40 * 6 ** 2 / 6)
    rec("LUG_outplane_" + tag, part="P_RX12C1_GS_LUG", sigma=s_l, SF=SY_SUS / s_l, need=need)
# 참고: 외팔 핀의 귀판 모서리 지압(선형 분포, 매우 보수) — 판정에 쓰지 않음(models.json 관례는 평균 지압)
e = lev_P; t = 6.0
p_edge = F_OP / (d * t) * (1 + 6 * e / t)
rec("LUG_edge_bearing_ref", part="P_RX12C1_GS_LUG", p_edge=p_edge, ratio_to_Sy=p_edge / SY_SUS,
    before=F_OP / (d * t) * (1 + 6 * 8.0 / t), note="선형 지압 분포 상한(참고). 판정 = 평균 지압. D1 고침(Ø10 또는 양쪽 받침)이면 사라짐")

# ---- 3. 핀 A Ø8 SCM435: 클레비스 볼 두 장(가운데 Y -1251 / -1219, 사이 32), 하중점 로드 눈 Y -1242
a, b = -1242.0 - (-1251.0), -1219.0 - (-1242.0)
a, b = abs(a), abs(b); Lw = a + b
for tag, F, need in cases:
    M = F * a * b / Lw; s = M / Zp
    Rm, Rp = F * b / Lw, F * a / Lw
    rec("PIN_A_bend_" + tag, part="P_RX12C1_GS_PIN_A", F_N=F, a_mm=a, b_mm=b, M_Nmm=M, sigma=s, SF=SY_SCM / s, need=need)
    rec("PIN_A_shear_" + tag, part="P_RX12C1_GS_PIN_A", R_minusY_N=Rm, R_plusY_N=Rp, tau=Rm / A, SF=0.58 * SY_SCM / (Rm / A), need=need)
    # 4. 클레비스 -Y 볼(깎은 뒤 X 1059~1104 · Z -385~-330, t6), 핀 A (1073, -368), 뒤판 X 1104
    brg = Rm / (d * 6.0)
    rec("CLEVIS_wall_bearing_" + tag, part="P_RX12C1_GS_CLEVIS", R_N=Rm, p=brg, SF=SY_AL / brg, need=need)
    # 빠짐(shear-out): 운전 = 핀이 -Z로(아래 끝 Z -385까지 17), 오조작 = +Z로(깎은 면 -330까지 38)
    edge = 17.0 if tag == "op" else 38.0
    tear = 2 * (edge - 4.1) * 6.0 * 0.58 * SY_AL
    rec("CLEVIS_wall_shearout_" + tag, part="P_RX12C1_GS_CLEVIS", edge_mm=edge, cap_N=tear, SF=tear / Rm, need=need)
    # 판 안 굽힘: 뒤판 X 1104에서 핀 X 1073까지 외팔 31, 단면 t6 x 높이 55
    Mw = Rm * 31.0; sw = Mw / (6.0 * 55.0 ** 2 / 6)
    rec("CLEVIS_wall_inplane_" + tag, part="P_RX12C1_GS_CLEVIS", M_Nmm=Mw, sigma=sw, SF=SY_AL / sw, need=need,
        note="깎기 전 높이 131(Z -385~-254) -> 55. 뿌리 모서리 Kt 미반영(R 정보 없음)")
    # 축 기울기 +6.76°의 X 성분이 -X 끝(13)으로 미는 빠짐
    Fx = Rm * math.sin(math.radians(6.76))
    tearx = 2 * (13.0 - 4.1) * 6.0 * 0.58 * SY_AL
    rec("CLEVIS_wall_shearout_X_" + tag, part="P_RX12C1_GS_CLEVIS", Fx_N=Fx, cap_N=tearx, SF=tearx / Fx, need=need)

# ---- 5. 받침 고리 SPACER_A SUS304 Ø14/Ø8.2 t15: 지름 방향 하중은 핀 -> 볼로 감(고리는 길이만 채움).
#     축 방향은 마찰·기울기 몫. 보수로 스프링 힘 10 % 를 축 방향 압축으로
As = math.pi / 4 * (14 ** 2 - 8.2 ** 2)
for tag, F, need in cases:
    sa = 0.1 * F / As
    rec("SPACER_A_axial_" + tag, part="P_RXDC02_GS_SPACER_A", area_mm2=As, sigma=sa, SF=SY_SUS / sa, need=need,
        note="지름 방향 하중 경로 아님(핀 Ø8 ↔ 고리 Ø8.2 틈 0.1, 핀 처짐보다 큼 — 아래 PIN_A_defl)")
Ip = math.pi * d ** 4 / 64
defl = F_OP * a ** 2 * b ** 2 / (3 * E_ST * Ip * Lw)
rec("PIN_A_defl", delta_mm=defl, gap_spacer_mm=0.1, note="하중점 처짐 < 고리 틈 0.1이면 고리는 지름 방향 하중을 안 받음")

# ---- 6. 로드 Ø10 좌굴(구매품 몫, 참고): 핀-핀 전체 길이 320.5를 로드만으로(보수)
Ir = math.pi * 10 ** 4 / 64
Pcr = math.pi ** 2 * E_ST * Ir / 320.51 ** 2
rec("ROD_buckling_ref", Pcr_N=Pcr, SF=Pcr / F_OP, need=3.0, note="구매품(D-231) 사양 몫 — 참고. 몸통 Ø22 강성 무시한 보수")

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in R.items():
    if k.startswith("_"): continue
    print(k, {kk: vv for kk, vv in v.items() if kk in ("SF", "sigma", "p", "verdict", "F_N", "delta_mm", "p_edge", "F_op_N", "F_misuse_tension_N")})
