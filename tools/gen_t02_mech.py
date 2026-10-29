# T02 구동부 모델링(모델링부) 생성기: v0.2.1 -> v0.3.0
# 선정 지시서 docs/reports/mechanism/mech_T02_select.md 6절(T02-S01·S02) 그대로. 원본 tools/out/mech_T02/select/gen_sel.py.
# 좌표는 대기 자세(J_PRESSER 10, J_NEEDLE 0, J_HEAD_ROT 0)의 세계 좌표. component.activate 뒤 세계 좌표로 그린다.
# 출력: tools/out/mech_T02/model/build.json (solidcraft-cli run build.json --in FSAP_v0.2.1.sc --save FSAP_v0.3.0.sc)
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T02', 'model')
os.makedirs(OUT, exist_ok=True)
S = []
C = lambda c, p: S.append({"command": c, "params": p})


def box(x0, x1, y0, y1, z0, z1, name=None, op=None, targets=None):
    p = {"length": round(x1 - x0, 4), "width": round(y1 - y0, 4), "height": round(z1 - z0, 4),
         "center": [round((x0 + x1) / 2, 4), round((y0 + y1) / 2, 4), round((z0 + z1) / 2, 4)]}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.box", p)


def cyl(r, x, y, z0, z1, name=None, op=None, targets=None):
    p = {"radius": r, "height": round(z1 - z0, 4), "base": [x, y, z0], "axis": "Z"}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


C("material.create", {"name": "S50C", "density_g_cm3": 7.85, "color": "#8a8f96"})

# ---------------- HEAD (J_HEAD_ROT 0 = 세계) — 6-1·6-2·6-3 ----------------
C("component.activate", {"component": "HEAD"})
H = "STEP대기_SEWHEAD"
box(-50, 50, -30, 660, -59, -1.05, H)                               # 베드
box(-75, 75, 620, 860, -134, 250, op="join", targets=[H])           # 기둥
box(-35, 35, 30, 630, 100, 180, op="join", targets=[H])             # 윗팔
box(-40, 40, -40, 40, 60, 200, op="join", targets=[H])              # 머리
box(-40.1, 40.1, -25.1, 25.1, -4.05, 0.0, op="cut", targets=[H])    # 침판 홈
cyl(1.5, 0, 0, -15, -4.0, op="cut", targets=[H])                    # 바늘 구멍(훅 자리)
cyl(4.2, 0, 0, 59, 201, op="cut", targets=[H])                      # 바늘대 구멍 Ø8.4
cyl(5.2, 0, -18, 59, 201, op="cut", targets=[H])                    # 노루발대 구멍 Ø10.4
P = "P_T02_PLATE"
box(-40, 40, -25, 25, -4.05, -1.05, P)                              # 침판 t3
cyl(8.5, 0, 10, -1.55, 3.5, op="join", targets=[P])                 # 아래 노즈 r8.5
cyl(1.0, 0, 0, -5, 0, op="cut", targets=[P])                        # 바늘 구멍 Ø2
BI = "P_T02_BINDER"
box(-34, -10, 2, 40, 26, 60, BI)                                    # 바인더 외형(속 통로 안 그림)
C("component.activate", {"component": "root"})

# ---------------- PRESSER (대기 J_PRESSER 10: 세계 = 내림 + 10) — 6-4 ----------------
C("component.activate", {"component": "PRESSER"})
F = "P_T02_FOOT"
C("sketch.create", {"plane": {"origin": [-9, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, "name": "SK_T02_FOOT"})
pts = [(-26, 21.05), (18.5, 21.05), (18.5, 31.05), (-10, 31.05), (-10, 55), (-26, 55)]
for i in range(len(pts)):
    a, b = pts[i], pts[(i + 1) % len(pts)]
    C("sketch.line", {"points": [list(a), list(b)]})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_T02_FOOT", "profiles": "all", "distance": 18, "body_name": F})   # X -9~9
cyl(8.5, 0, 10, 16.5, 21.55, op="join", targets=[F])                # 위 노즈 r8.5 (내림 6.5~11.55)
cyl(1.3, 0, 0, 20.5, 31.5, op="cut", targets=[F])                   # 바늘 구멍 Ø2.6
PB = "STEP대기_SEWHEAD_PRESSERBAR"
cyl(5.0, 0, -18, 55, 210, PB)                                       # 노루발대 Ø10 (자루 윗면에 얹힘)
C("component.activate", {"component": "root"})

# ---------------- NEEDLE (대기 J_NEEDLE 0 = 세계) — 6-5 ----------------
C("component.activate", {"component": "NEEDLE"})
NB = "STEP대기_SEWHEAD_NEEDLEBAR"
cyl(4.0, 0, 0, 68, 200, NB)
cyl(1.05, 0, 0, 67, 78, op="cut", targets=[NB])                     # 바늘 자루 구멍
ND = "STEP대기_NEEDLE"
cyl(0.6, 0, 0, 20, 53.5, ND)                                        # 날 Ø1.2, 끝 Z 20
cyl(1.0, 0, 0, 53, 78, op="join", targets=[ND])                     # 자루 Ø2
C("component.activate", {"component": "root"})

# ---------------- BASE(바닥 고정) — 6-6 ----------------
C("component.activate", {"component": "BASE"})
HP = "P_T02_HEADPLATE"
box(-100, 100, 620, 860, -140, -134, HP)
P1, P2 = "STEP대기_HFS8-4080-460_P1", "STEP대기_HFS8-4080-460_P2"
T1, T2 = "STEP대기_HFS8-4080-580_T1", "STEP대기_HFS8-4080-580_T2"
box(-90, -50, 700, 780, -600, -140, P1)
box(50, 90, 700, 780, -600, -140, P2)
box(-90, -50, 200, 780, -680, -600, T1)
box(50, 90, 200, 780, -680, -600, T2)
C("component.activate", {"component": "root"})

# ---------------- 재질(E-09) ----------------
MAT = {H: "Steel", PB: "Steel", NB: "Steel", ND: "Steel", P: "S50C", F: "Rigid 10K", BI: "Rigid 10K",
       HP: "SUS304", P1: "Aluminum", P2: "Aluminum", T1: "Aluminum", T2: "Aluminum"}
bym = {}
for b, m in MAT.items():
    bym.setdefault(m, []).append(b)
for m, bs in bym.items():
    C("material.assign", {"bodies": bs, "material": m})

# ---------------- 컴포넌트 속성: 바디 -> 재질 / 만드는 법 / 형상 (T01-M02) ----------------
PROP = {
    "HEAD": {H: "Steel / 구매품 임시 형상(E-10, 기종 D-10) / 베드 100x690x57.95 + 기둥 150x240x384 + 윗팔 70x600x80 + 머리 80x80x140",
             P: "S50C / 밀링 / 침판 80x50 t3 + 아래 노즈 r8.5 Z -1.05~3.5, 바늘 구멍 Ø2",
             BI: "Rigid 10K / SLA Form 3 / 외형 24x38x34(속 테이프 통로는 시제품, 구매 여부 U-T02-2)"},
    "PRESSER": {F: "Rigid 10K / SLA Form 3 / L자 바닥 t10 + 자루 18x16 + 위 노즈 r8.5, 바늘 구멍 Ø2.6",
                PB: "Steel / 구매품 임시 형상(헤드 부품, D-10) / 노루발대 Ø10 L155"},
    "NEEDLE": {NB: "Steel / 구매품 임시 형상(헤드 부품, D-10) / 바늘대 Ø8 L132",
               ND: "Steel / 구매품 임시 형상(바늘 계통 D-10) / 날 Ø1.2 L33.5 + 자루 Ø2 L25"},
    "BASE": {HP: "SUS304 / 판금(레이저 평판) t6 / 200x240 헤드 받침판",
             P1: "Aluminum / 구매품 임시 형상(E-10, D-27) / 40x80 L460 기둥 받침",
             P2: "Aluminum / 구매품 임시 형상(E-10, D-27) / 40x80 L460 기둥 받침",
             T1: "Aluminum / 구매품 임시 형상(E-10, D-30) / 40x80 L580 바닥 연결",
             T2: "Aluminum / 구매품 임시 형상(E-10, D-30) / 40x80 L580 바닥 연결"},
}
DESC = {"HEAD": "봉제 헤드 묶음(고정 C-01, 헤드 회전 조인트는 T03 후보). 기종 D-10. T02: 헤드 임시 형상·침판·바인더",
        "PRESSER": "노루발(들기 조인트, T03). T02: 노루발 P_T02_FOOT·노루발대",
        "NEEDLE": "바늘(내림 조인트, T03). T02: 바늘대·바늘",
        "BASE": "고정부(바닥 고정). T01 프레임 + T02 헤드 받침(받침판·형재 4)"}
for comp, props in PROP.items():
    C("component.metadata.set", {"component": comp, "properties": props, "description": DESC[comp]})

# ---------------- 문서 설명, 저장 자세 ----------------
C("document.metadata.set", {"values": {"description": "T02 mechanism: sewing head placeholder, split r8.5 nose on foot and throat plate, SLA binder"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
NEW = {"HEAD": [H, P, BI], "PRESSER": [F, PB], "NEEDLE": [NB, ND], "BASE": [HP, P1, P2, T1, T2]}
json.dump({"material": MAT, "props": PROP, "new": NEW, "made": [P, BI, F, HP]}, open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(len(S), 'steps')
