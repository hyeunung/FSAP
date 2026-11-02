# 디테일링 DP-4(모델링부) 생성기: v0.6.10 -> v0.6.11 — MAT_X·MAT_Y 이송 체결(체결만, E-18)
# 지시(PM DP-4): (1) 같은 이름 블록 _A·_B (2) Y판 -> 1300 블록 CB5-16 x8(카운터보어 Ø9.5 깊이 7)
#                (3) DG 받침 -> Y판 CB5-20 x4 밑에서(받침 M5 탭 깊이 14, Y판 밑 카운터보어 Ø9.5 깊이 5.5)
#                (4) DGM 하우징 -> 받침 STEP대기_CB10-30 x4 (5) 1300 레일 볼트·HNTT8-5: 치수표 없음 -> 안 그림(미완, D-41)
#                (6) P_S01_XSPACER_1~4 그대로
# 좌표: 대기 자세 세계 좌표(J_MAT_X 0, J_MAT_Y -700, J_MAT_ROT 0). 단위 mm.
# 실측(v0.6.10, tools/out/detail/DP-4/q2_faces.txt):
#   Y판 X±200, Y -950~-450, Z -370~-355(t15), 창 X±47.5 Y -870~-665. 구멍 없음(면 10).
#   1300 블록 탭 r2.067, 원점 Z -380.4(윗면 -370 -> 깊이 10.4), 블록마다 (±134·±166, 블록 중심 Y + 6.5) 2개.
#   DG 받침 U자 X±100, Y -837.5~-600, Z -355~-305, 트임 X±47.5 Y -837.5~-665. DGM 탭 기초 Ø8.5 깊이 20(Z -325~-305) at (±85, -615/-785).
#   DGM 하우징 장착 구멍 Ø11 Z -305~-290(플랜지 15), 자리면 r15 Z -290.
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_dp4_detail.py [split|full] -> tools/out/detail/DP-4/build[_split].json
#   solidcraft-cli run tools/out/detail/DP-4/build.json --in 3D_Modeling/FSAP_v0.6.10.sc --save 3D_Modeling/FSAP_v0.6.11.sc
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-4')
os.makedirs(OUT, exist_ok=True)
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
VARIANT = sys.argv[1] if len(sys.argv) > 1 else 'full'
S = []
INFO = {"bolts": [], "temp": [], "blocks": []}


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


def cylz(d, x, y, z0, z1, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(z1 - z0), "base": [r6(x), r6(y), r6(z0)], "axis": "Z"}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def prism(name, sk, origin, xd, yd, pts, dist):
    C("sketch.create", {"plane": {"origin": [r6(v) for v in origin], "x_dir": [r6(v) for v in xd], "y_dir": [r6(v) for v in yd]}, "name": sk})
    C("sketch.line", {"points": [[r6(a), r6(b)] for a, b in pts], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": dist, "body_name": name})


def hexpts(af, rot=0.0):
    rc = af / math.sqrt(3)
    return [(rc * math.cos(math.radians(30 + 60 * k + rot)), rc * math.sin(math.radians(30 + 60 * k + rot))) for k in range(6)]


DOWN = lambda x, y, z: [0, 1, 0, r6(x), 0, 0, -1, r6(y), -1, 0, 0, r6(z)]   # STEP 몸통 +X -> 세계 -Z (머리 자리면 z)
UP = lambda x, y, z: [0, 1, 0, r6(x), 0, 0, 1, r6(y), 1, 0, 0, r6(z)]       # STEP 몸통 +X -> 세계 +Z


def insert(pn, nm, M, par, body0, desc, bt="purchased"):
    C("component.activate", {"component": "root"})
    C("file.insert_step", {"path": SP + "%s/%s.stp" % (pn, pn), "name": nm, "matrix": M})
    C("body.rename", {"body": body0, "name": nm})
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": bt, "description": desc})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": par})
    INFO["bolts"].append({"name": nm, "pn": pn, "parent": par, "matrix": M})


def comp(nm, par, pn, desc):
    C("component.activate", {"component": par})
    C("component.create", {"name": nm, "parent": par, "activate": True, "grounded": False})
    INFO["temp"].append((nm, par, pn, desc))


YP, DS, DGH = "P_T01_YPLATE", "P_S01_DGSPACER", "DGM200R-AZAC_T01_HOUSING"
# 같은 이름 블록: (단위, 바디 이름, 지울 두 번째 배치 id, 두 번째 자리로 옮길 양, A 자리, B 자리)
# 배치 id·자리는 q0_out.json 실측(첫 배치 = A: 1300은 Y -860, 1800은 X -180)
BLK = [
    ("MAT_Y", "SV2RL28-1300_L_BLOCK", 549, "Y -860", "Y -540"),
    ("MAT_Y", "SV2RL28-1300_R_BLOCK", 560, "Y -860", "Y -540"),
    ("MAT_X", "SV2RL28-1800_F_BLOCK", 527, "X -180", "X +180"),
    ("MAT_X", "SV2RL28-1800_B_BLOCK", 538, "X -180", "X +180"),
]
CORR = {}
if os.path.exists(os.path.join(OUT, 'copy_corr.json')):
    CORR = json.load(open(os.path.join(OUT, 'copy_corr.json'), encoding='utf-8'))

C("motion.play", {"study": "대기", "step": 0, "quiet": True})

# ================= (1) 같은 이름 블록 -> _A(첫 배치, 원래 바디) · _B(두 번째 배치 자리에 실물 바디 복사) =================
for unit, base, occ2, wa, wb in BLK:
    C("component.activate", {"component": unit})
    C("component.create", {"name": base + "_B", "parent": unit, "activate": True, "grounded": False})
    C("component.copy_bodies", {"bodies": [base + " (B:2)"] if VARIANT == 'splitB2' else [base], "component": base + "_B"})
    C("body.rename", {"body": base + " (2)", "name": base + "_B"})
    t = CORR.get(base, [0.0, 0.0, 0.0])
    if any(abs(v) > 1e-9 for v in t):
        C("solid.move", {"bodies": [base + "_B"], "translate": [r6(v) for v in t]})
    C("material.assign", {"bodies": [base + "_B"], "material": "Steel"})
    pn = base.split("_")[0]
    C("component.metadata.set", {"component": base + "_B", "bom_type": "reference",
                                 "description": "%s 의 일부(구매품 STEP 하위) — 블록 %s. 같은 이름 바디 둘을 A·B로 나눔(DP-4, DL-D18)" % (pn, wb)})
    C("component.activate", {"component": "root"})
    C("selection.delete", {"occurrences": [occ2]})
    C("body.rename", {"body": base, "name": base + "_A"})
    INFO["blocks"].append({"unit": unit, "A": base + "_A", "B": base + "_B", "A_at": wa, "B_at": wb})

if VARIANT.startswith('split'):
    C("motion.play", {"study": "대기", "step": 0, "quiet": True})
    for unit, base, occ2, wa, wb in BLK:
        C("model.faces", {"body": base + "_A"})
        C("model.faces", {"body": base + "_B"})
    C("occurrence.properties", {"occurrence": "MAT_Y:1"})
    C("occurrence.properties", {"occurrence": "MAT_X:1"})
    json.dump(S, open(os.path.join(OUT, 'build_%s.json' % VARIANT), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(S), 'steps', VARIANT)
    sys.exit(0)

# ================= (2) Y판 -> 1300 블록 4: 탭 8자리(블록 중심 Y + 6.5) =================
BT = []   # (x, y) 블록 탭
for x in (-166.0, -134.0, 134.0, 166.0):
    for yc in (-860.0, -540.0):
        BT.append((x, yc + 6.5))
C("component.activate", {"component": "MAT_Y"})
for x, y in BT:
    cylz(5.5, x, y, -371, -354, op="cut", targets=[YP])                 # Ø5.5 관통
    cylz(9.5, x, y, -362, -354, op="cut", targets=[YP])                 # 윗면 카운터보어 Ø9.5 깊이 7(바닥 Z -362)
# ================= (3) DG 받침 -> Y판: 받침 M5 탭 깊이 14 + Y판 Ø5.5 + 밑 카운터보어 Ø9.5 깊이 5.5 =================
DT = [(-73.75, -700.0), (73.75, -700.0), (-73.75, -810.0), (73.75, -810.0)]
for x, y in DT:
    cylz(4.2, x, y, -355.2, -341, op="cut", targets=[DS])               # M5 탭 기초 구멍 Ø4.2 깊이 14(Z -355 ~ -341)
    cylz(5.5, x, y, -371, -354, op="cut", targets=[YP])                 # Y판 Ø5.5 관통
    cylz(9.5, x, y, -371, -364.5, op="cut", targets=[YP])               # 밑 카운터보어 Ø9.5 깊이 5.5(바닥 Z -364.5)
C("component.activate", {"component": "root"})

for j, (x, y) in enumerate(BT, 1):
    side = "L" if x < 0 else "R"
    blk = "%s_%s" % (side, "A" if y < -700 else "B")
    insert("CB5-16", "CB5-16_T01_YB_%d" % j, DOWN(x, y, -362), "MAT_Y", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×16 — Y판 카운터보어 Ø9.5 깊이 7(바닥 Z-362) → 1300 블록 %s M5 탭(Y판 8 + 물림 8, 탭 바닥까지 2.4, DP-4)" % blk)
for j, (x, y) in enumerate(DT, 1):
    insert("CB5-20", "CB5-20_T01_DS_%d" % j, UP(x, y, -364.5), "MAT_Y", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×20 — Y판 밑 카운터보어 Ø9.5 깊이 5.5(자리 Z-364.5) → DG 받침 M5 탭 깊이 14(Y판 9.5 + 물림 10.5, 끝 틈 3.5, DP-4)")

# ================= (4) DGM 하우징 -> 받침: STEP대기_CB10-30 x4 =================
# 임시 형상(E-10, D-37): JIS B 1176 M10×30 머리 Ø16×10 + 몸통 Ø10×30 + 육각 구멍 8 깊이 5. 머리 자리 Z -290(하우징 자리면), 끝 Z -320.
DG = [(-85.0, -615.0), (85.0, -615.0), (-85.0, -785.0), (85.0, -785.0)]
for j, (x, y) in enumerate(DG, 1):
    nm = "STEP대기_CB10-30_T01_DG_%d" % j
    comp(nm, "MAT_Y", "CB10-30", "MISUMI 육각 구멍붙이 볼트 M10×30 (STEP 대기 D-37, 임시 형상 JIS B 1176 머리 Ø16×10 + 몸통 Ø10, 육각 구멍 8) — DGM200R 하우징 플랜지 15 → DG 받침 M10 탭(기초 Ø8.5 깊이 20, 물림 15, 끝 틈 5, DP-4)")
    cylz(16, x, y, -290, -280, nm)
    cylz(10, x, y, -320, -289.8, op="join", targets=[nm])
    prism("T_DP4_S10_%d" % j, "SK_DP4_S10_%d" % j, [x, y, -285], [1, 0, 0], [0, 1, 0], hexpts(8), 5.5)
    C("solid.combine", {"target": nm, "tools": ["T_DP4_S10_%d" % j], "operation": "cut"})
    C("material.assign", {"bodies": [nm], "material": "Steel"})
C("component.activate", {"component": "root"})
for nm, par, pn, desc in INFO["temp"]:
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": "purchased", "description": desc})

# ================= 컴포넌트 속성 =================
C("component.metadata.set", {"component": "MAT_Y", "properties": {
    DS: "A5052 / 밀링 / DGM 받침 U자 200×237.5×50(트임 95×172.5, -Y 열림), DGM 장착 탭 M10 기초 구멍 Ø8.5 깊이 20 ×4, 밑면 M5 탭 기초 Ø4.2 깊이 14 ×4 (±73.75, -700/-810)(Y판 CB5-20, DP-4)",
    YP: "A5052 / 밀링 / Y 이동판 400×500 t15(Z -370~-355), 모터·호스 창 95×205, 1300 블록 볼트 Ø5.5 관통 + 윗면 카운터보어 Ø9.5 깊이 7 ×8(CB5-16), DG 받침 볼트 Ø5.5 관통 + 밑면 카운터보어 Ø9.5 깊이 5.5 ×4(CB5-20) (DP-4)",
}})
C("document.metadata.set", {"values": {"description": "DP-4 detailing: MAT_X/MAT_Y fasteners - same-name rail blocks split to _A/_B, Y plate to 1300 blocks CB5-16 x8 (counterbore D9.5 depth 7), DG spacer to Y plate CB5-20 x4 from below (M5 taps depth 14, bottom counterbore D9.5 depth 5.5), DGM housing to spacer STEP-pending CB10-30 x4; rail bolts/T-nuts not drawn (HNTT8-5 pending); rest as v0.6.10"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(INFO, open(os.path.join(OUT, 'build_info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps', VARIANT)
