# RX-DC-03 해석부 손계산 2회차 (세움 받침 fix1, v2.30.1, 2026-11-24). FEA 못 함 — 환경 없음(D-16).
# 형상: tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT_fix1.step 꼭짓점에서 직접 읽음(옛 케이스 좌표 안 씀)
#   세운 판 X -296.6~-293.6 · Y 83~97 · Z 253~392, 꺾음 날 X -308.6~-296.6 · Y 83~86 · Z 253~392,
#   플랜지 X -296.6~-273 · Y 83~97 · Z 250~253(볼트 X -288 · -278, Y 90), 타이 판 X -318.6~-295 · Y 83~86 · Z 330~350
#   Z 250~253 층에는 X -296.6보다 -X 쪽 재료가 없다 -> 꺾음 날 아래 끝(Z 253)은 자유단이다.
# 재질 SUS304(항복 205, E 193 GPa, G 74 GPa). 하중·기준은 1회차(mech_RX-DC-03_handcalc.py)와 같다.
import json, math, os, re, sys
sys.path.insert(0, "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools")
import handcalc as hc
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
STEP = ROOT + "/tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT_fix1.step"
SY, E, G = 205.0, 193000.0, 74000.0
g = 9.81; F_MIS = 50.0; F_RUN = 2*5.0 + 0.03*g*3
def sf(s): return round(SY/s, 2)

# 0) STEP 꼭짓점으로 형상 확인
t = open(STEP).read()
vid = set(re.findall(r"VERTEX_POINT\('[^']*',#(\d+)\)", t))
pts = set()
for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", t):
    if m.group(1) in vid:
        pts.add(tuple(round(float(v), 2) for v in m.group(2).split(",")))
bb = [(min(p[i] for p in pts), max(p[i] for p in pts)) for i in range(3)]
z250_minx = min(p[0] for p in pts if abs(p[2]-250) < 0.01)
z253_minx = min(p[0] for p in pts if abs(p[2]-253) < 0.01)
geo = {"bbox": bb, "Z250_min_X": z250_minx, "Z253_min_X": z253_minx,
       "fold_bottom_free": z250_minx > -296.7 and z253_minx < -308.5}

# 단면 도구(직사각형 조각 합, X=u, Y=v)
def sec(rects):
    A = sum((x2-x1)*(y2-y1) for x1, x2, y1, y2 in rects)
    xc = sum((x2-x1)*(y2-y1)*(x1+x2)/2 for x1, x2, y1, y2 in rects)/A
    yc = sum((x2-x1)*(y2-y1)*(y1+y2)/2 for x1, x2, y1, y2 in rects)/A
    Iyy = Ixx = Ixy = 0.0   # Iyy: X 방향 굽힘(X 거리 제곱), Ixx: Y 방향 굽힘
    for x1, x2, y1, y2 in rects:
        b, h = x2-x1, y2-y1; a = b*h; cx, cy = (x1+x2)/2-xc, (y1+y2)/2-yc
        Iyy += h*b**3/12 + a*cx*cx; Ixx += b*h**3/12 + a*cy*cy; Ixy += a*cx*cy
    corners = [(x, y) for x1, x2, y1, y2 in rects for x in (x1, x2) for y in (y1, y2)]
    return dict(A=A, xc=xc, yc=yc, Iyy=Iyy, Ixx=Ixx, Ixy=Ixy, corners=corners)
def sig_max(s, Mx_dir, My_dir):
    # 비대칭 굽힘: 힘 X 방향이면 모멘트가 X 방향 거리에 응력을 만든다. sigma = (Mu*Ixx - Mv*Ixy)/D * u + (Mv*Iyy - Mu*Ixy)/D * v
    D = s["Iyy"]*s["Ixx"] - s["Ixy"]**2
    best = 0.0
    for x, y in s["corners"]:
        u, v = x-s["xc"], y-s["yc"]
        sg = (Mx_dir*s["Ixx"] - My_dir*s["Ixy"])/D*u + (My_dir*s["Iyy"] - Mx_dir*s["Ixy"])/D*v
        best = max(best, abs(sg))
    return best
PLATE = (-296.6, -293.6, 83.0, 97.0); FOLD = (-308.6, -296.6, 83.0, 86.0)
sP = sec([PLATE]); sL = sec([PLATE, FOLD])
J_L = (14 + 12)*3**3/3                            # 열린 얇은 단면 비틀림 상수(근사)
out = {"geometry_from_step": geo,
       "section_plate": {k: round(sP[k], 2) for k in ("Iyy", "Ixx")},
       "section_L": {k: round(sL[k], 2) for k in ("xc", "yc", "Iyy", "Ixx", "Ixy")}, "J_L": J_L}

cases = {"run_top": (F_RUN, 137), "mis_tie": (F_MIS, 91), "mis_top": (F_MIS, 137)}
res = {}
for k, (F, L) in cases.items():
    M = F*L
    s_root = sig_max(sP, M, 0)        # 뿌리 Z 253: 꺾음 날 아래 끝이 자유단 -> 세운 판 단면만 모멘트를 받는다
    s_Labove = sig_max(sL, M, 0)      # 뿌리 위(꺾음 날이 다 일하는 곳, 보수 쪽으로 같은 M)
    res[k] = {"F": round(F, 2), "arm": L, "root_sigma": round(s_root, 1), "root_SF": sf(s_root),
              "L_sigma": round(s_Labove, 1), "L_SF": sf(s_Labove)}
# 처짐·진동: 뿌리 근처 꺾음 날이 덜 일하는 길이(전단 지연, 날 너비 12)를 세운 판만으로, 나머지는 L 단면
le = 12.0
def tip_defl(F, L):
    th = F*L*le/(E*sP["Iyy"])                          # 뿌리 구간 회전
    return th*L + F*(L-le)**3/(3*E*sL["Iyy"])
for k, (F, L) in cases.items():
    res[k]["defl_mm"] = round(tip_defl(F, L), 2)
k_tip = 1.0/tip_defl(1.0, 137)*1000.0                    # N/m
f = {}
for mt in (0.02, 0.05):
    f["tip%dg" % int(mt*1000)] = round(math.sqrt(k_tip/(mt + 0.236*0.1079))/(2*math.pi), 1)
res["f1_Hz"] = f
# Y 방향 당김(타이 판 끝 X -318.6에서, 팔 91): 강한 쪽 굽힘 + 비틀림(전단 중심 = 모서리 X -295.1, Y 84.5 근처)
T = F_MIS*abs(-318.6 - (-295.1))
tau = T*3/J_L
sYb = sig_max(sP, 0, F_MIS*91)                           # 뿌리는 세운 판만(보수 쪽)
res["mis_Y_tie"] = {"T_Nmm": round(T, 0), "tau": round(tau, 1), "sigma_root": round(sYb, 1),
                    "vm": round(math.hypot(sYb, math.sqrt(3)*tau), 1), "SF": sf(math.hypot(sYb, math.sqrt(3)*tau))}
out["fix1_as_built"] = res

# 고침안 A: 플랜지를 꺾음 날 밑까지 늘린다(X -308.6~-296.6 · Y 83~97 · Z 250~253) + 날 아래 끝과 모서리 용접(또는 날을 플랜지에서 접어 올림)
#   -> 뿌리 단면이 L, 모멘트가 늘린 플랜지 -> 블록 윗면(-X 당김 압축) · 볼트(+X 당김 인장)로 간다
A = {}
for k, (F, L) in cases.items():
    s = sig_max(sL, F*L, 0); A[k] = {"sigma": round(s, 1), "SF": sf(s), "defl_mm": round(F*L**3/(3*E*sL["Iyy"]), 3)}
kA = 3*E*sL["Iyy"]/137**3*1000
A["f1_Hz_tip50g"] = round(math.sqrt(kA/(0.05 + 0.236*0.1119))/(2*math.pi), 1)
# 날 아래 끝 인장 합력(+X 당김): F_fold = M/Iyy * A_fold * (x_fold - xc)
M = F_MIS*137
Ff = M/sL["Iyy"]*36*abs(-302.6 - sL["xc"])
A["fold_bottom_force_N"] = round(Ff, 0)
A["ext_to_flange_shear_MPa"] = round(Ff/(14*3), 1)        # 늘린 플랜지가 원래 플랜지와 X -296.6 단면(14 x 3)에서 이어짐
A["fillet_weld_a2_len12_MPa"] = round(Ff/(0.7*2*12*2), 1)  # 날 아래 끝 양쪽 모살 a2(목 1.4) x 12 x 2
# 볼트: +X 당김 받침점 X -273(볼트 팔 15·5, 1회차와 같음), -X 당김 받침점 X -308.6
dp = [15.0, 5.0]; dn = [20.6, 30.6]
Fbp = M*max(dp)/sum(d*d for d in dp); Fbn = M*max(dn)/sum(d*d for d in dn)
A["bolt_N_plusX"] = round(Fbp, 0); A["bolt_N_minusX"] = round(Fbn, 0)
A["bolt_calc"] = hc.calc(5, 9, max(Fbp, Fbn), 0.0, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
A["mass_add_g"] = round(12*14*3*7.93e-3, 1)
out["fixA_flange_extend"] = A
# 고침안 B(대안): 세운 판 두께만 키움(꺾음 날 그대로, 뿌리는 판 단면)
B = {}
for tt in (4.0, 5.0, 6.0):
    W = 14*tt*tt/6; s = F_MIS*137/W
    B["t%d" % tt] = {"sigma": round(s, 1), "SF": sf(s)}
out["fixB_thicker_plate"] = B

os.makedirs(ROOT + "/fea/results", exist_ok=True)
json.dump(out, open(ROOT + "/fea/results/mech_RX-DC-03_fix1_handcalc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("geo", geo)
print("secL", out["section_L"], "plate", out["section_plate"])
for k in cases: print(k, res[k])
print("f1", res["f1_Hz"], "Y", res["mis_Y_tie"])
print("A", {k: A[k] for k in A if k != "bolt_calc"})
print("A bolt", A["bolt_calc"])
print("B", B)
