# RX-DC-03 해석부 손계산 3회차 (세움 받침 fix2, v2.30.2, 2026-11-24). FEA 못 함 — 환경 없음(D-16).
# 형상: tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT_fix2.step 꼭짓점에서 직접 읽음(옛 케이스 좌표 안 씀)
#   fix1 + 꺾음 날 아래 플랜지 X -308.6~-296.6 · Y 83~97 · Z 250~253(join, 한 몸). 블록 윗면은 X -305부터(검도 2회차 광선).
# 재질 SUS304(항복 205, E 193 GPa, G 74 GPa). 하중·기준은 1·2회차와 같다(운전 SF 3, 오조작 SF 2, 영구 변형 SF<1.2).
import json, math, os, re, sys
sys.path.insert(0, "C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools")
import handcalc as hc
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
STEP = ROOT + "/tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT_fix2.step"
SY, E, G = 205.0, 193000.0, 74000.0
g = 9.81; F_MIS = 50.0; F_RUN = 2*5.0 + 0.03*g*3
def sf(s): return round(SY/s, 2)

# 0) STEP 꼭짓점·면 수로 형상 확인
t = open(STEP).read()
vid = set(re.findall(r"VERTEX_POINT\('[^']*',#(\d+)\)", t))
pts = set()
for m in re.finditer(r"#(\d+)\s*=\s*CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", t):
    if m.group(1) in vid:
        pts.add(tuple(round(float(v), 2) for v in m.group(2).split(",")))
bb = [(min(p[i] for p in pts), max(p[i] for p in pts)) for i in range(3)]
z250 = sorted({p[0] for p in pts if abs(p[2]-250) < 0.01})
z253 = sorted({p[0] for p in pts if abs(p[2]-253) < 0.01})
geo = {"n_vertex": len(pts), "n_face": len(re.findall(r"ADVANCED_FACE\(", t)),
       "n_solid": len(re.findall(r"MANIFOLD_SOLID_BREP\(", t)), "bbox": bb,
       "Z250_X": z250, "Z253_X": z253,
       "fold_bottom_tied": min(z250) < -308.5}

def sec(rects):
    A = sum((x2-x1)*(y2-y1) for x1, x2, y1, y2 in rects)
    xc = sum((x2-x1)*(y2-y1)*(x1+x2)/2 for x1, x2, y1, y2 in rects)/A
    yc = sum((x2-x1)*(y2-y1)*(y1+y2)/2 for x1, x2, y1, y2 in rects)/A
    Iyy = Ixx = Ixy = 0.0
    for x1, x2, y1, y2 in rects:
        b, h = x2-x1, y2-y1; a = b*h; cx, cy = (x1+x2)/2-xc, (y1+y2)/2-yc
        Iyy += h*b**3/12 + a*cx*cx; Ixx += b*h**3/12 + a*cy*cy; Ixy += a*cx*cy
    corners = [(x, y) for x1, x2, y1, y2 in rects for x in (x1, x2) for y in (y1, y2)]
    return dict(A=A, xc=xc, yc=yc, Iyy=Iyy, Ixx=Ixx, Ixy=Ixy, corners=corners)
def sig_max(s, Mu, Mv):
    D = s["Iyy"]*s["Ixx"] - s["Ixy"]**2
    return max(abs((Mu*s["Ixx"] - Mv*s["Ixy"])/D*(x-s["xc"]) + (Mv*s["Iyy"] - Mu*s["Ixy"])/D*(y-s["yc"]))
               for x, y in s["corners"])
PLATE = (-296.6, -293.6, 83.0, 97.0); FOLD = (-308.6, -296.6, 83.0, 86.0)
sL = sec([PLATE, FOLD]); J_L = (14 + 12)*3**3/3
out = {"geometry_from_step": geo, "section_L_root": {k: round(sL[k], 2) for k in ("xc", "yc", "Iyy", "Ixx", "Ixy")}}

# 1) 뿌리 Z 253: 꺾음 날 아래 끝이 플랜지에 붙어 L 단면 전체가 일한다
cases = {"run_top": (F_RUN, 137), "mis_tie": (F_MIS, 91), "mis_top": (F_MIS, 137)}
res = {}
for k, (F, L) in cases.items():
    s = sig_max(sL, F*L, 0)
    res[k] = {"F": round(F, 2), "arm": L, "sigma": round(s, 1), "SF": sf(s),
              "defl_mm": round(F*L**3/(3*E*sL["Iyy"]), 3)}
# Y 당김(타이 판 끝 X -318.6, 팔 91): 강한 쪽 굽힘 + 비틀림, 뿌리 L 단면
T = F_MIS*abs(-318.6 - (-295.1)); tau = T*3/J_L
sYb = sig_max(sL, 0, F_MIS*91); vm = math.hypot(sYb, math.sqrt(3)*tau)
res["mis_Y_tie"] = {"T_Nmm": round(T), "tau": round(tau, 1), "sigma": round(sYb, 1), "vm": round(vm, 1), "SF": sf(vm)}
k_tip = 3*E*sL["Iyy"]/137**3*1000
res["f1_Hz"] = {"tip20g": round(math.sqrt(k_tip/(0.02 + 0.236*0.1119))/(2*math.pi), 1),
                "tip50g": round(math.sqrt(k_tip/(0.05 + 0.236*0.1119))/(2*math.pi), 1)}
# 2) 꺾음 날 아래 끝 합력(+X 당김 인장 / -X 당김 압축)과 이음
M = F_MIS*137
Ff = M/sL["Iyy"]*36*abs(-302.6 - sL["xc"])
res["fold_bottom_force_N"] = round(Ff)
res["ext_to_flange_shear_MPa"] = round(Ff/(14*3), 1)
res["fillet_weld_a2_len12x2_MPa"] = round(Ff/(0.7*2*12*2), 1)
# 날 밑 연장 판은 위에 꺾음 날(Y 83~86, 높이 139)이 서 있어 X 방향 깊은 보다. 이음 X -296.6에서 날+연장 단면(3x142 세움)으로 굽힘
Zweb = 3*142**2/6
res["ext_deep_beam_sigma_MPa"] = round(Ff*abs(-302.6 - (-296.6))/Zweb, 2)
# -X 당김: 날 밑 누름이 블록 밖 돌출(X -308.6~-305, 3.6)에 다 걸리는 최악
s_ov = Ff*3.6/(14*3**2/6)
res["overhang_worst"] = {"M_Nmm": round(Ff*3.6), "sigma": round(s_ov, 1), "SF": sf(s_ov)}
# 꺾음 날 압축 쪽 국부 좌굴(자유단 outstand 12/3, k 0.43)
scr = 0.43*math.pi**2*E/(12*(1-0.3**2))*(3/12)**2
res["fold_outstand_buckling_MPa"] = round(scr)
# 3) 볼트: +X 당김 받침점 플랜지 끝 X -273(팔 15·5), -X 당김 받침점 블록 -X 끝 X -305(팔 17·27; fix1 계산 -308.6에서 바로잡음)
dp = [15.0, 5.0]; dn = [17.0, 27.0]
Fbp = M*max(dp)/sum(d*d for d in dp); Fbn = M*max(dn)/sum(d*d for d in dn)
res["bolt_N_plusX"] = round(Fbp); res["bolt_N_minusX"] = round(Fbn)
res["bolt_calc"] = hc.calc(5, 9, max(Fbp, Fbn), 0.0, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
# 4) 판 앞 면 X -293.6 ~ 볼트 머리 끝 X -292.25: 맨 플랜지 1.35 mm. 볼트 머리 누름 원뿔(30°, 판 3) 반지름 4.25+1.73 -> X -293.98까지
res["bare_flange_span_mm"] = round(-292.25 - (-293.6), 2)
res["clamp_cone_edge_X"] = round(-288 - (4.25 + 3*math.tan(math.radians(30))), 2)
res["mass_g"] = 111.9
out["fix2_as_built"] = res

os.makedirs(ROOT + "/fea/results", exist_ok=True)
json.dump(out, open(ROOT + "/fea/results/mech_RX-DC-03_fix2_handcalc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("geo", {k: geo[k] for k in geo})
print("secL", out["section_L_root"])
for k, v in res.items():
    if k != "bolt_calc": print(k, v)
print("bolt", res["bolt_calc"])
