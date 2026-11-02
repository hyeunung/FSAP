# 디테일링 DP-2 T01 회전 묶음(모델링부) 생성기: v0.6.5 -> v0.6.6
# 지시서: 이 실행의 DP-2 지시서(허브 t8·스파이더 판금 모자형·링/원판 매트 면 R1·링–축·LHFR16·기둥·원판 체결).
# 다르게 정한 곳은 보고서 docs/reports/detailing/detail_DP-2_model.md 'DEV' 표.
# 좌표: 대기 세계 좌표(바늘점 원점, 매트 밑면 Z 0). MAT_ROT·RING1·RING2 feature는 대기 자세의 세계 좌표로 받는다(gen_s01_step 과 같음).
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_dp2_detail.py   -> tools/out/detail/DP-2/build.json
#   solidcraft-cli run tools/out/detail/DP-2/build.json --in 3D_Modeling/FSAP_v0.6.5.sc --save 3D_Modeling/FSAP_v0.6.6.sc
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-2')
os.makedirs(OUT, exist_ok=True)
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
AX = (0.0, -700.0)
TH3 = (90.0, 210.0, 330.0)
S = []
INFO = {"bolts": [], "temp": [], "made": {}}


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


def uv(th):
    t = math.radians(th)
    u = (math.cos(t), math.sin(t))
    return u, (-u[1], u[0])


def pt(th, r, a=0.0):
    u, v = uv(th)
    return (r6(AX[0] + r * u[0] + a * v[0]), r6(AX[1] + r * u[1] + a * v[1]))


def polar(r, deg):
    t = math.radians(deg)
    return (r6(AX[0] + r * math.cos(t)), r6(AX[1] + r * math.sin(t)))


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


def comp(nm, par, pn, desc):
    C("component.activate", {"component": par})
    C("component.create", {"name": nm, "parent": par, "activate": True, "grounded": False})
    INFO["temp"].append((nm, par, pn, desc))


DOWN = lambda x, y, z: [0, 1, 0, r6(x), 0, 0, -1, r6(y), -1, 0, 0, r6(z)]   # STEP 몸통 +X -> 세계 -Z (머리 자리면 z)
UP = lambda x, y, z: [0, 1, 0, r6(x), 0, 0, 1, r6(y), 1, 0, 0, r6(z)]       # STEP 몸통 +X -> 세계 +Z


def insert(pn, nm, M, par, body0, desc, bt="purchased"):
    C("component.activate", {"component": "root"})
    C("file.insert_step", {"path": SP + "%s/%s.stp" % (pn, pn), "name": nm, "matrix": M})
    C("body.rename", {"body": body0, "name": nm})
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": bt, "description": desc})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": par})
    INFO["bolts"].append({"name": nm, "pn": pn, "parent": par, "matrix": M})


C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("sheet.manage_rules", {"name": "A5052_t3_R3", "thickness": 3, "k_factor": 0.44, "bend_radius": 3, "active": True})

# ================= (1) P_T01_HUB: SUS304 t6 -> t8 (Z -241~-233) =================
C("component.activate", {"component": "MAT_ROT"})
C("body.rename", {"body": "P_T01_HUB", "name": "OLD_P_T01_HUB_T6"})
C("solid.remove", {"bodies": ["OLD_P_T01_HUB_T6"]})
cylz(300, AX[0], AX[1], -241, -233, "P_T01_HUB")
cylz(40, AX[0], AX[1], -242, -232, op="cut", targets=["P_T01_HUB"])
TABLE = [(0, -622.5), (67.116969, -661.25), (67.116969, -738.75), (0, -777.5), (-67.116969, -738.75), (-67.116969, -661.25)]
for x, y in TABLE:
    cylz(6.6, x, y, -242, -232, op="cut", targets=["P_T01_HUB"])          # 테이블 볼트 Ø6.6 ×6 PCD155
FEET = []   # (스파이더 번호, x, y)
for i, th in enumerate(TH3):
    for rr in (110, 135):
        for a in (-44, 44):
            FEET.append((i + 1,) + pt(th, rr, a))
for _, x, y in FEET:
    cylz(4.2, x, y, -242, -232, op="cut", targets=["P_T01_HUB"])          # 스파이더 발 M5 관통 탭(기초 구멍 Ø4.2) ×12
POSTA = (30.0, 150.0, 270.0)
for ang in POSTA:
    x, y = polar(50, ang)
    cylz(4.2, x, y, -242, -232, op="cut", targets=["P_T01_HUB"])          # 기둥 M5 관통 탭 ×3 r50
C("material.assign", {"bodies": ["P_T01_HUB"], "material": "SUS304"})

# ================= (2) P_T01_SPIDER_1~3: A5052 t3 판금 모자형 =================
C("solid.remove", {"bodies": ["P_T01_SPIDER_%d" % (i + 1) for i in range(3)]})
HAT = [(-52, -233), (-52, -230), (-30, -230), (-30, -95.5), (30, -95.5), (30, -230), (52, -230), (52, -233),
       (27, -233), (27, -98.5), (-27, -98.5), (-27, -233)]
LH = {}   # (ring, i) -> (cx, cy, rot_deg)
for i, th in enumerate(TH3):
    n = "P_T01_SPIDER_%d" % (i + 1)
    u, v = uv(th)
    o = pt(th, 100)
    prism(n, "SK_DP2_SPIDER_%d" % (i + 1), [o[0], o[1], 0], [v[0], v[1], 0], [0, 0, 1], HAT, 390)
    E = lambda a, z: list(pt(th, 295, a)) + [z]
    C("solid.fillet", {"edges": [E(-30, -95.5), E(30, -95.5), E(-27, -233), E(27, -233)], "radius": 6, "body": n})   # 바깥 R6 = 안 R3 + t
    C("solid.fillet", {"edges": [E(-27, -98.5), E(27, -98.5), E(-30, -230), E(30, -230)], "radius": 3, "body": n})   # 안 R3
    for rr in (190, 410):
        x, y = pt(th, rr)
        cylz(10.5, x, y, -100, -94, op="cut", targets=[n])                 # SNJ 보스 Ø10.5 그대로
    for rr, ring in ((240, "R1"), (460, "R2")):
        x, y = pt(th, rr)
        cylz(28.4, x, y, -100, -94, op="cut", targets=[n])                 # 부시 구멍 Ø28.4
        for k in range(4):
            q = math.radians(th + 45 + 90 * k)
            cylz(4.5, x + 19 * math.cos(q), y + 19 * math.sin(q), -100, -94, op="cut", targets=[n])   # 부시 플랜지 Ø4.5 ×4 대각
        LH[(ring, i + 1)] = (x, y)
    for (j, x, y) in FEET:
        if j == i + 1:
            cylz(5.5, x, y, -234, -229, op="cut", targets=[n])             # 발 구멍 Ø5.5 ×4
    C("sheet.convert", {"body": n, "face": E(0, -95.5),
                        "bends": [E(28.243, -97.257), E(-28.243, -97.257), E(28.757, -231.243), E(-28.757, -231.243)],
                        "rule": "A5052_t3_R3", "body_name": n})
    C("material.assign", {"bodies": [n], "material": "A5052"})

# ================= (5) P_T01_POST: 길이 2 짧게 + 밑·위 플랜지 일체 =================
C("body.rename", {"body": "P_T01_POST", "name": "OLD_P_T01_POST"})
C("solid.remove", {"bodies": ["OLD_P_T01_POST"]})
cylz(60, AX[0], AX[1], -233, -12.5, "P_T01_POST")
cylz(120, AX[0], AX[1], -233, -224.5, op="join", targets=["P_T01_POST"])
cylz(100, AX[0], AX[1], -20.5, -12.5, op="join", targets=["P_T01_POST"])
cylz(40, AX[0], AX[1], -234, -11.5, op="cut", targets=["P_T01_POST"])
for ang in POSTA:
    x, y = polar(50, ang)
    cylz(5.5, x, y, -234, -223.5, op="cut", targets=["P_T01_POST"])       # 밑 플랜지 Ø5.5 ×3 r50
    x, y = polar(45, ang)
    cylz(5.5, x, y, -21.5, -11.5, op="cut", targets=["P_T01_POST"])       # 위 플랜지 Ø5.5 ×3 r45
C("material.assign", {"bodies": ["P_T01_POST"], "material": "PET-CF"})

# ================= (6) P_T01_DISC: 윗면 바깥 R1 + 인서트 자리 Ø6.4 × 9 =================
C("solid.fillet", {"edges": [[0, -645, -0.5]], "radius": 1, "body": "P_T01_DISC"})
for ang in POSTA:
    x, y = polar(45, ang)
    cylz(6.4, x, y, -13, -3.5, op="cut", targets=["P_T01_DISC"])
C("material.assign", {"bodies": ["P_T01_DISC"], "material": "Rigid 10K"})

# ================= (8) P_T01_RING1: 윗면 R1 ×2 + 축 자리 Ø5.5 + 카운터보어 Ø9.5 × 5.5 =================
C("component.activate", {"component": "RING1"})
C("solid.fillet", {"edges": [[0, -400, -0.5], [0, -625, -0.5]], "radius": 1, "body": "P_T01_RING1"})
for i, th in enumerate(TH3):
    x, y = pt(th, 240)
    cylz(5.5, x, y, -11, 0, op="cut", targets=["P_T01_RING1"])
    cylz(9.5, x, y, -6, 0, op="cut", targets=["P_T01_RING1"])

# ================= (9) P_T01_RING2 + 띠 1·3·5: 윗면 R1 ×2 + Ø10 / 띠 Ø5.5 =================
C("component.activate", {"component": "RING2"})
C("solid.fillet", {"edges": [[0, -180, -2], [0, -390, -2]], "radius": 1, "body": "P_T01_RING2"})
for i, th in enumerate(TH3):
    x, y = pt(th, 460)
    cylz(10, x, y, -7.5, -1.5, op="cut", targets=["P_T01_RING2"])
    cylz(5.5, x, y, -12.5, -6.5, op="cut", targets=["P_T01_RING2_STRAP_%d" % (2 * i + 1)])

# ================= (7) PSFJ16-150 -> STEP대기_PSFJT16-150-M5 (실물 형상 + 윗끝 Ø4.2 × 12) =================
C("component.activate", {"component": "root"})
for ring, z0, z1 in (("R1", -160.5, -10.5), ("R2", -162.0, -12.0)):
    for i, th in enumerate(TH3):
        C("component.delete", {"component": "PSFJ16-150_%s_%d" % (ring, i + 1)})
for ring, unit, z0, z1, rr in (("R1", "RING1", -160.5, -10.5, 240), ("R2", "RING2", -162.0, -12.0, 460)):
    for i, th in enumerate(TH3):
        x, y = pt(th, rr)
        nm = "STEP대기_PSFJT16-150-M5_%s_%d" % (ring, i + 1)
        comp(nm, unit, "PSFJT16-150-M5", "MISUMI 리니어 샤프트 Ø16 L150 한쪽 끝 M5 탭 (STEP 대기 D-37: PSFJ16-150 실물 형상 + 윗끝 Ø4.2×12 임시 D-37 (2))")
        cylz(16, x, y, z0, z1, nm)
        for z in (z0, z1):
            C("solid.chamfer", {"edges": [[r6(x + 8), r6(y), z]], "distance": 0.5, "body": nm})
        cylz(4.2, x, y, z1 - 12, z1 + 0.5, op="cut", targets=[nm])
        C("material.assign", {"bodies": [nm], "material": "Steel"})
C("component.activate", {"component": "root"})

# ================= (3) LHFR16 ×6: 자기 축 둘레로 돌려 플랜지 구멍을 스파이더 축에 대각 =================
LHOCC = {("R1", 1): 242, ("R1", 2): 248, ("R1", 3): 254, ("R2", 1): 260, ("R2", 2): 266, ("R2", 3): 272}
ROT = {1: 45.0, 2: -15.0, 3: 15.0}   # 지금 구멍은 세계 X·Y 축 위 -> th+45 (mod 90)
for (ring, i), occ in LHOCC.items():
    x, y = LH[(ring, i)]
    C("occurrence.move", {"occurrence": occ, "space": "world", "axis": [0, 0, 1], "angle": "%g deg" % ROT[i], "origin": [x, y, 0]})

# CB4-16 ×4(카운터보어 Ø7.5 깊이 4.1 안, 머리 Z -93.6~-89.6) + LBNR4 ×4(웹 밑 Z -101.7~-98.5) 임시 형상, 부시마다
for (ring, i), (x0, y0) in sorted(LH.items()):
    th = TH3[i - 1]
    for k in range(4):
        q = math.radians(th + 45 + 90 * k)
        x, y = x0 + 19 * math.cos(q), y0 + 19 * math.sin(q)
        nm = "STEP대기_CB4-16_T01_%s_%d_%d" % (ring, i, k + 1)
        comp(nm, "MAT_ROT", "CB4-16", "MISUMI 육각 구멍붙이 볼트 M4×16 (STEP 대기 D-37, 임시 형상 JIS B 1176 머리 Ø7×4 + 몸통 Ø4, 육각 구멍 3) — LHFR16 플랜지 카운터보어 안")
        cylz(7, x, y, -93.6, -89.6, nm)
        cylz(4, x, y, -109.6, -93.4, op="join", targets=[nm])
        prism("T_DP2_S4_%s_%d_%d" % (ring, i, k + 1), "SK_DP2_S4_%s_%d_%d" % (ring, i, k + 1), [x, y, -92.1], [1, 0, 0], [0, 1, 0], hexpts(3), 2.5)
        C("solid.combine", {"target": nm, "tools": ["T_DP2_S4_%s_%d_%d" % (ring, i, k + 1)], "operation": "cut"})
        nn = "STEP대기_LBNR4_T01_%s_%d_%d" % (ring, i, k + 1)
        comp(nn, "MAT_ROT", "LBNR4", "MISUMI 육각 너트 M4 (STEP 대기 D-37, 임시 형상 맞변 7 두께 3.2) — 스파이더 웹 밑")
        prism(nn, "SK_DP2_N4_%s_%d_%d" % (ring, i, k + 1), [x, y, -101.7], [1, 0, 0], [0, 1, 0], hexpts(7), 3.2)
        cylz(3.3, x, y, -102, -98.2, op="cut", targets=[nn])

# STEP대기_CB6-18 ×6 (허브 -> DG 테이블, 머리 Ø10×6 Z -233~-227, 몸통 Ø6 Z -251~-233, 물림 10)
for j, (x, y) in enumerate(TABLE, 1):
    nm = "STEP대기_CB6-18_T01_%d" % j
    comp(nm, "MAT_ROT", "CB6-18", "MISUMI 육각 구멍붙이 볼트 M6×18 (STEP 대기 D-37, 임시 형상 JIS B 1176 머리 Ø10×6 + 몸통 Ø6, 육각 구멍 5) — 허브 → DGM200R 출력 테이블 M6 탭(물림 10)")
    cylz(10, x, y, -233, -227, nm)
    cylz(6, x, y, -251, -232.8, op="join", targets=[nm])
    prism("T_DP2_S6_%d" % j, "SK_DP2_S6_%d" % j, [x, y, -230], [1, 0, 0], [0, 1, 0], hexpts(5), 3.5)
    C("solid.combine", {"target": nm, "tools": ["T_DP2_S6_%d" % j], "operation": "cut"})
C("component.activate", {"component": "root"})

# ================= (4)(5)(6)(8)(9) 실물 STEP 체결품 =================
for j, (si, x, y) in enumerate(FEET, 1):
    insert("CB5-12", "CB5-12_T01_SP%d_%d" % (si, (j - 1) % 4 + 1), DOWN(x, y, -230), "MAT_ROT", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×12 — 스파이더 발 t3 → 허브 t8 탭(물림 8, DP-2)")
for j, ang in enumerate(POSTA, 1):
    x, y = polar(50, ang)
    insert("CB5-16", "CB5-16_T01_PB_%d" % j, DOWN(x, y, -224.5), "MAT_ROT", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×16 — 기둥 밑 플랜지 8.5 → 허브 탭(물림 7.5, DP-2)")
    x, y = polar(45, ang)
    insert("CB5-16", "CB5-16_T01_PT_%d" % j, UP(x, y, -20.5), "MAT_ROT", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×16 — 기둥 위 플랜지 8 → 원판 인서트 MBIS5-6.5-8(밑에서, DP-2)")
    insert("MBIS5-6.5-8", "MBIS5-6.5-8_T01_%d" % j, UP(x, y, -12.5), "MAT_ROT", "MBIS5-6.5-8",
           "MISUMI 수지용 인서트 M5 L8 — 원판 Rigid 10K 밑면 자리 Ø6.4×9(DP-2)")
for i, th in enumerate(TH3):
    x, y = pt(th, 240)
    insert("CB5-12", "CB5-12_T01_RG1_%d" % (i + 1), DOWN(x, y, -6), "RING1", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×12 — 링1 카운터보어 → PSFJT16 윗끝 탭(링 4.5 + 물림 7.5, DP-2)")
    x, y = pt(th, 460)
    insert("CB5-16", "CB5-16_T01_RG2_%d" % (i + 1), DOWN(x, y, -7), "RING2", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×16 — 링2 띠 5 → PSFJT16 윗끝 탭(물림 11, 머리 윗면 = 링2 윗면 Z-2, DP-2)")

# ================= (10) NTJ 같은 이름 둘 -> _NTJ_A(아래)·_NTJ_B(위) =================
NTJ = json.load(open(os.path.join(OUT, 'ntj_map.json'), encoding='utf-8')) if os.path.exists(os.path.join(OUT, 'ntj_map.json')) else None
# ntj_map: [{"unit","base","occ_up","dx","dy","dz"}] — dz는 시험 실행(ntj_probe)에서 잰 복사본 Z 보정(6개 모두 +22.5)
if NTJ is None:
    NTJ = [{"unit": u, "base": b, "occ_up": o, "dx": 0.0, "dy": 0.0, "dz": 22.5} for u, b, o in (
        ("RING1", "CJ2B16-60SZ_R1_1", 585), ("RING1", "CJ2B16-60SZ_R1_2", 602), ("RING1", "CJ2B16-60SZ_R1_3", 619),
        ("RING2", "CJ2B16-60SZ_R2_1", 636), ("RING2", "CJ2B16-60SZ_R2_2", 653), ("RING2", "CJ2B16-60SZ_R2_3", 670))]
if NTJ:
    for m in NTJ:
        base = m["base"]
        C("component.activate", {"component": m["unit"]})
        C("component.create", {"name": base + "_NTJ_B", "parent": m["unit"], "activate": True, "grounded": False})
        C("component.copy_bodies", {"bodies": [base + "_NTJ"], "component": base + "_NTJ_B"})
        C("body.rename", {"body": base + "_NTJ (2)", "name": base + "_NTJ_B"})
        C("solid.move", {"bodies": [base + "_NTJ_B"], "translate": [r6(m["dx"]), r6(m["dy"]), r6(m["dz"])]})
        C("material.assign", {"bodies": [base + "_NTJ_B"], "material": "Steel"})
        C("component.metadata.set", {"component": base + "_NTJ_B", "part_number": "NTJ-015C", "bom_type": "reference",
                                     "description": "CJ2B16-60SZ 로드 끝 너트 위(Z -18~-14). 실린더 부속(BOM은 실린더 행). 같은 이름 바디 둘을 A·B로 나눔(DP-2)"})
        C("component.activate", {"component": "root"})
        C("selection.delete", {"occurrences": [m["occ_up"]]})
        C("body.rename", {"body": base + "_NTJ", "name": base + "_NTJ_A"})

# ================= 재질(E-09): 체결품·임시 형상 =================
C("component.activate", {"component": "root"})
C("material.assign", {"bodies": [b["name"] for b in INFO["bolts"]] + [t[0] for t in INFO["temp"] if not t[0].startswith("STEP대기_PSFJT")], "material": "Steel"})
for nm, par, pn, desc in INFO["temp"]:
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": "purchased", "description": desc})

# ================= 컴포넌트 속성(가공품 재질 / 만드는 법 / 형상) =================
C("component.metadata.set", {"component": "MAT_ROT", "properties": {
    "P_T01_HUB": "SUS304 / 레이저 평판 t8 / R20~R150 Z-241~-233(DP-2 t6->t8, 윗면 +2). 구멍: DG 테이블 Ø6.6 ×6 PCD155, 스파이더 발 M5 관통 탭 ×12, 기둥 M5 관통 탭 ×3 r50",
    "P_T01_SPIDER_1": "A5052 / 판금 t3 모자형(굽힘 4, 안 R3, K 0.44) / 웹 Z-98.5~-95.5, 다리 X±27~30, 바깥 발 폭 22 Z-233~-230, r100~490. 구멍: 부시 Ø28.4 ×2 + 플랜지 Ø4.5 ×8(대각), SNJ Ø10.5 ×2, 발 Ø5.5 ×4. 깊은 ㄷ 절곡은 업체 확인(D-42), 안 되면 3분할",
    "P_T01_SPIDER_2": "A5052 / 판금 t3 모자형 / 스파이더1과 같은 모양(허브 중심 +120°)",
    "P_T01_SPIDER_3": "A5052 / 판금 t3 모자형 / 스파이더1과 같은 모양(허브 중심 -120°)",
    "P_T01_POST": "PET-CF / FDM H2C / 관 Ø60/Ø40 Z-233~-12.5 + 밑 플랜지 Ø120×8.5(Ø5.5 ×3 r50) + 위 플랜지 Ø100×8(Ø5.5 ×3 r45) 한 덩어리. 조임 1.5 N·m, 와셔 D-43",
    "P_T01_DISC": "Rigid 10K / SLA Form 3 / 진공 원판 R55 t12, 윗면 바깥 R1, 밑면 인서트 자리 Ø6.4×9 ×3 r45(MBIS5-6.5-8)",
}})
C("component.metadata.set", {"component": "RING1", "properties": {
    "P_T01_RING1": "A5052 / 밀링 / 진공 링 R75~R300 t10, 윗면 안·바깥 R1, 축 자리 Ø5.5 관통 + 윗면 카운터보어 Ø9.5 깊이 5.5 ×3(CB5-12)",
}})
C("component.metadata.set", {"component": "RING2", "properties": {
    "P_T01_RING2": "A5052 / 레이저 평판 / 받침 링 R310~R520 t5, 윗면 안·바깥 R1(밀링 후가공), 축 자리 Ø10 관통 ×3(볼트 머리 자리)",
    "P_T01_RING2_STRAP_1": "A5052 / 레이저 평판 / 띠 40×195 t5, 축 자리 Ø5.5 관통(CB5-16), 밑면 로드 자리 Ø6×1.5(로드–띠 미는 접촉, 체결 안 함: 판금 SF-06)",
    "P_T01_RING2_STRAP_3": "A5052 / 레이저 평판 / 띠 40×195 t5, 축 자리 Ø5.5 관통(CB5-16), 밑면 로드 자리 Ø6×1.5(미는 접촉)",
    "P_T01_RING2_STRAP_5": "A5052 / 레이저 평판 / 띠 40×195 t5, 축 자리 Ø5.5 관통(CB5-16), 밑면 로드 자리 Ø6×1.5(미는 접촉)",
}})
C("document.metadata.set", {"values": {"description": "DP-2 detailing: T01 hub SUS304 t8 with DG table M6 x6, spiders A5052 t3 sheet-metal hat with feet (CB5-12 x12), LHFR16 diagonal holes with CB4-16/LBNR4 x24, post with integral flanges (CB5-16 x6, MBIS5 inserts), ring1/ring2/disc mat face R1, ring-shaft CB5 x6, PSFJT16-150-M5 STEP-wait, NTJ A/B names"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({"bolts": INFO["bolts"], "temp": INFO["temp"], "feet": FEET, "lh": {"%s_%d" % k: v for k, v in LH.items()},
           "table": TABLE, "rot": ROT}, open(os.path.join(OUT, 'build_info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps; bolts', len(INFO["bolts"]), 'temp', len(INFO["temp"]), 'ntj', bool(NTJ))
