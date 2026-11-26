# RX-DC-C1 해석부 손계산 — P_RXDC03_RISER_BRKT_판금(v2.30.3) 세움 받침 외팔
# 형상 출처: tools/out/mech_RX-DC-C1/stepout/P_RXDC03_RISER_BRKT_판금.step 꼭짓점(fea/results/mech_RX-DC-C1_stepgeo.txt)
#   밑판 X -308.6~-273 · Y 83~97 · Z 250~253 / 웨브 X -288~-273 · Y 82~85 · Z 253~487
#   꺾음 날 X -288~-285 · Y 74.5~82 · Z 253~445 (밑면 Z 253 밑에 재료 없음: 밑판이 Y 83부터)
#   선반 X -318.6~-268 · Y 65~85 · Z 484~487, 케이블 타이 구멍 중심 X -300·-280, Y 74
# 하중(models.json P_RXDC03_RISER_BRKT_판금, D-232·D-38 임시): 운전 5 N x 2줄, 오조작 손 당김 50 N, 자중 x3 g
# 판정(요구서 6-1, M-09 기본): 운전 SF 3, 오조작 SF 2, SF < 1.2 = 영구 변형(동작)
import json, math
E = 193000.0; G = 74000.0; SY = 205.0
Z0, ZF, ZTOP = 253.0, 445.0, 487.0
L = ZTOP - Z0          # 234
Lw = ZTOP - ZF         # 42 (웨브만)

def sec(rects):
    A = sum((x1-x0)*(y1-y0) for x0, x1, y0, y1 in rects)
    cx = sum((x1-x0)*(y1-y0)*(x0+x1)/2 for x0, x1, y0, y1 in rects)/A
    cy = sum((x1-x0)*(y1-y0)*(y0+y1)/2 for x0, x1, y0, y1 in rects)/A
    Ix = sum((x1-x0)*(y1-y0)**3/12 + (x1-x0)*(y1-y0)*((y0+y1)/2-cy)**2 for x0, x1, y0, y1 in rects)  # Y 방향 하중
    Iy = sum((y1-y0)*(x1-x0)**3/12 + (x1-x0)*(y1-y0)*((x0+x1)/2-cx)**2 for x0, x1, y0, y1 in rects)  # X 방향 하중
    cym = max(abs(y-cy) for r in rects for y in r[2:]); cxm = max(abs(x-cx) for r in rects for x in r[:2])
    J = sum(max(x1-x0, y1-y0)*min(x1-x0, y1-y0)**3/3 for x0, x1, y0, y1 in rects)
    return dict(A=A, cx=cx, cy=cy, Ix=Ix, Iy=Iy, cym=cym, cxm=cxm, J=J)

WEB = (-288.0, -273.0, 82.0, 85.0)
FLG = (-288.0, -285.0, 74.5, 82.0)
roots = {
    "A_STEP그대로(웨브 밑 밑판 맞닿음 Y 83~85, 15x2)": sec([(-288.0, -273.0, 83.0, 85.0)]),
    "B_판금 실제(밑판 굽힘이 웨브로, 꺾음 날은 Z 253에서 자유 끝 -> 웨브 15x3)": sec([WEB]),
    "C_고침안(밑판을 꺾음 날 밑 Y 74.5까지, RX-DC-03 fix2와 같은 수 -> L 단면 뿌리)": sec([WEB, FLG]),
}
Lsec = sec([WEB, FLG]); Wsec = sec([WEB])
loads = [("운전 5 N x 2줄", 10.0, 3.0), ("운전 1줄 5 N", 5.0, 3.0), ("오조작 50 N", 50.0, 2.0)]
tie = (-300.0, 74.0)   # 먼 쪽 타이(가장 불리한 비틀림 팔)
res = {"roots": {}, "cases": []}
for rn, s in roots.items():
    res["roots"][rn] = {k: round(v, 2) for k, v in s.items()}
    for ln, F, crit in loads:
        for d in ("Y", "X"):
            I, c = (s["Ix"], s["cym"]) if d == "Y" else (s["Iy"], s["cxm"])
            M = F*L; sig = M*c/I
            # 비틀림: 하중선과 웨브 중심선 사이 팔
            arm = abs(tie[0]-(-280.5)) if d == "Y" else abs(tie[1]-83.5)
            T = F*arm; tau = T*3.0/s["J"]
            vm = math.sqrt(sig**2 + 3*tau**2)
            # 처짐: 뿌리~445는 L(C·B는 L이 붙어 있음), 445~487은 웨브만. 뿌리 단면 영향은 A만 따로(짧은 띠, 무시하고 B와 같게)
            IL = Lsec["Ix"] if d == "Y" else Lsec["Iy"]; IW = Wsec["Ix"] if d == "Y" else Wsec["Iy"]
            a = ZF - Z0
            # 외팔 끝 하중, 두 구간 강성(근사: 각 구간 곡률 적분)
            defl = F/E*((L**3 - Lw**3)/3/IL + Lw**3/3/IW)
            sf = SY/vm
            kind = "동작(영구 변형)" if sf < 1.2 else ("디테일(기준 미달)" if sf < crit else "합격")
            res["cases"].append(dict(root=rn, load=ln, dir=d, F=F, M=round(M), sigma=round(sig, 1), tau=round(tau, 1), vm=round(vm, 1), SF=round(sf, 2), crit=crit, judge=kind, tip_defl_mm=round(defl, 3)))
# 웨브만 구간 Z 445 (팔 42)
for ln, F, crit in loads:
    sig = F*Lw*Wsec["cym"]/Wsec["Ix"]
    res["cases"].append(dict(root="Z 445 웨브만(15x3)", load=ln, dir="Y", F=F, M=round(F*Lw), sigma=round(sig, 1), SF=round(SY/sig, 2), crit=crit))
# 밑판 볼트(CB5-12 x2, X -288·-278, Y 90): 오조작 Y 당김의 받침점 앞 끝 Y 82(고침안 74.5) · 뒤 끝 Y 97
F = 50.0; M = F*(ZTOP-250.0)
res["bolts"] = {
    "pivot_Y97(+Y로 들림)": dict(lever=7.0, total_N=round(M/7.0), per_bolt_N=round(M/7.0/2)),
    "pivot_Y82(-Y로 들림, B)": dict(lever=8.0, total_N=round(M/8.0), per_bolt_N=round(M/8.0/2)),
    "pivot_Y74.5(-Y, C 고침안)": dict(lever=15.5, total_N=round(M/15.5), per_bolt_N=round(M/15.5/2)),
}
# 자중 x3 g (151.1 g)
res["selfweight_3g_N"] = round(0.1511*9.81*3, 2)
json.dump(res, open("C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/mech_RX-DC-C1_fea_handcalc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in res["cases"]:
    if c["load"] != "운전 1줄 5 N":
        print(c["root"][:2], c["load"], c["dir"], "σ", c["sigma"], "VM", c.get("vm"), "SF", c["SF"], c.get("judge", ""), "처짐", c.get("tip_defl_mm", ""))
print(res["bolts"])
