# T09 칼 팔 축 배치(모델링부) 생성기: v0.6.11 -> v0.6.12
# 지시서 docs/reports/mechanism/mech_T09_select.md (T09-C3 수정안) 그대로. 다르게 정한 곳은 mech_T09_model.md 'DEV' 표.
# 좌표: 대기 세계 좌표(바늘점 원점, 매트 밑면 Z 0, 헤드 쪽 +Y). feature 좌표 = 세계 대기 좌표(T06·T06_KNIFE 배치 = 단위 행렬).
# GB3는 (36, 87) -> (36, 125)로 옮김(T09-M03, 칼 내림 중 패드 M3 머리와 충돌). 모서리 R1/C0.5와 B~F 사이 Body 이름은 보고서 3절.
# 쓰는 법: python -B tools/gen_t09_mech.py -> tools/out/mech_T09/model/b_<A..G>.json (MCP batch로 차례로 보냄)
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T09', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
B = {}
S = None


def batch(k):
    global S
    S = B.setdefault(k, [])


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


def cyl(d, base, axis, h, op="cut", targets=None, name=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if name:
        p["body_name"] = name
    else:
        p["operation"] = op; p["targets"] = targets
    C("solid.cylinder", p)


def box(x0, x1, y0, y1, z0, z1, name=None, op=None, targets=None):
    p = {"length": r6(x1 - x0), "width": r6(y1 - y0), "height": r6(z1 - z0),
         "center": [r6((x0 + x1) / 2), r6((y0 + y1) / 2), r6((z0 + z1) / 2)]}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.box", p)


def prism(sk, origin, xd, yd, loops, dist, name=None, op=None, targets=None):
    C("sketch.create", {"plane": {"origin": origin, "x_dir": xd, "y_dir": yd}, "name": sk})
    for pts in loops:
        C("sketch.line", {"points": [[r6(a), r6(b)] for a, b in pts], "closed": True})
    C("sketch.finish", {})
    p = {"sketch": sk, "profiles": "all", "distance": dist}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.extrude", p)


def newcomp(nm, par):
    C("component.activate", {"component": par})
    C("component.create", {"name": nm, "parent": par, "activate": True, "grounded": False})


GB, AR = "P_T09_GBASE", "P_T09_ARM"
RL = "STEP대기_SSE2BZ12-120_RAIL"
BK = ["STEP대기_SSE2BZ12-120_BLK1", "STEP대기_SSE2BZ12-120_BLK2"]
CY, RO, NT = "STEP대기_CJ2B16-30SZ", "STEP대기_CJ2B16-30SZ_ROD", "STEP대기_NTJ-015C_T06"
HD = "STEP대기_SEWHEAD"
XC, YC = 24.0, -89.5          # 실린더·로드 축
YR = -62.5                    # 레일 가운데
DX, DY = -84.0, -82.0         # 실린더 묶음 이동

# ======================= A: 원복 자세, 지우기, 옮기기, 침판 홈 =======================
batch('A')
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("component.activate", {"component": "root"})
for c in (["LHFR16_T06", "CB5-12_T06_BR1", "CB5-12_T06_BR2"]
          + ["STEP대기_CB4-16_T06_%d" % i for i in range(1, 5)]
          + ["STEP대기_LBNR4_T06_%d" % i for i in range(1, 5)]
          + ["STEP대기_PSFJT16-100-M5", "CB5-12_T06_SH", "STEP대기_MS3-8_T06"]):
    C("component.delete", {"component": c})
C("component.activate", {"component": "T06"})
C("solid.remove", {"bodies": ["P_T06_BRACKET"]})
C("component.activate", {"component": "T06_KNIFE"})
C("solid.remove", {"bodies": ["P_T06_ARM"]})
# 브래킷 볼트 BR1·2용 헤드 탭 자리(Cylinder164·165) — 볼트를 지웠으므로 빈 구멍 0
C("component.activate", {"component": "root"})
C("timeline.delete", {"features": [938, 939]})
for nm in (CY, RO, NT):
    C("component.activate", {"component": nm})
    C("solid.move", {"bodies": [nm], "translate": [DX, DY, 0]})
C("component.activate", {"component": "root"})
# 침판 칼 홈 +X 벽 25.15 -> 24.90: Box110 길이 2 -> 1.75(모서리 X 23.15 그대로), C0.5 모서리 따라 옮김
C("timeline.edit", {"feature": 844, "set": {"length": "1.75"}})
C("timeline.edit", {"feature": 845, "set": {"edges": [[24.90, -7.5, -1.05]]}})

# ======================= B: P_T09_GBASE (T06, A5052 절삭 한 바디) =======================
batch('B')
C("component.activate", {"component": "T06"})
# 1) X 3.75 평면에 F1(Y-46~-40 Z62~152) + W(Y-80~-46 Z20~140) + W2(Y-110.5~-80 Z73~108) 한 루프, +X 8
L1 = [(-40, 62), (-40, 152), (-46, 152), (-46, 140), (-80, 140), (-80, 108), (-110.5, 108), (-110.5, 73),
      (-80, 73), (-80, 20), (-46, 20), (-46, 62)]
# sketch plane x_dir=+Y, y_dir=+Z -> normal +X
prism("SK_T09_GBASE_1", [3.75, 0, 0], [0, 1, 0], [0, 0, 1], [L1], 8, name=GB)
# 2) F1 나머지 X 11.75~43
prism("SK_T09_GBASE_2", [11.75, 0, 0], [0, 1, 0], [0, 0, 1], [[(-46, 62), (-40, 62), (-40, 152), (-46, 152)]], 31.25,
      op="join", targets=[GB])
# 3) 선반 SH X 11.75~38 · Y -110.5~-80.5 · Z 73~77
prism("SK_T09_GBASE_3", [11.75, 0, 0], [0, 1, 0], [0, 0, 1], [[(-110.5, 73), (-80.5, 73), (-80.5, 77), (-110.5, 77)]], 26.25,
      op="join", targets=[GB])
# 구멍: F1 장공 5.5 x 7.5 (X ±1) Y 관통 ×3
for (x, z) in ((10, 146), (36, 146), (36, 125)):
    for xx in (x - 1, x + 1):
        cyl(5.5, [xx, -46.5, z], "Y", 7, targets=[GB])
    box(x - 1, x + 1, -46.5, -39.5, z - 2.75, z + 2.75, op="cut", targets=[GB])
# W +X 면 M3 탭(기초 Ø2.5) X 관통 ×5
for z in (30, 55, 80, 105, 130):
    cyl(2.5, [3.25, YR, z], "X", 9, targets=[GB])
# 선반 구멍 Ø10.5 Z 관통
cyl(10.5, [XC, YC, 72.5], "Z", 5, targets=[GB])
C("material.assign", {"bodies": [GB], "material": "A5052"})
# 헤드 코 앞면 기초 구멍 Ø4.2 깊이 13 (Y -40 -> -27, 임시 헤드 D-10)
C("component.activate", {"component": HD})
for (x, z) in ((10, 146), (36, 146), (36, 125)):
    cyl(4.2, [x, -40.5, z], "Y", 13.5, targets=[HD])
C("component.activate", {"component": "root"})

# ======================= C: 레일 + CB3-10 ×5 (T06) =======================
batch('C')
newcomp(RL, "T06")
box(11.75, 19.75, YR - 6, YR + 6, 20, 140, name=RL)
for z in (30, 55, 80, 105, 130):
    cyl(3.5, [11.25, YR, z], "X", 9, targets=[RL])           # 관통 Ø3.5
    cyl(6.0, [16.25, YR, z], "X", 4, targets=[RL])            # 자리파기 Ø6 깊이 3.5 (X 16.25~19.75)
C("material.assign", {"bodies": [RL], "material": "Stainless Steel"})
C("component.activate", {"component": "root"})
for i, z in enumerate((30, 55, 80, 105, 130), 1):
    nm = "STEP대기_CB3-10_T09_RL%d" % i
    C("parts.insert", {"family": "socket_head_cap_screw", "size": "M3", "length": 10,
                       "point": [16.25, YR, z], "direction": [1, 0, 0], "name": nm})
    C("body.rename", {"body": "Body1", "name": nm})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": "T06"})

# ======================= D: P_T09_ARM (T06_KNIFE, SUS304 절삭 한 바디) =======================
batch('D')
C("component.activate", {"component": "T06_KNIFE"})
LA = [(3, 36.5), (3, 54), (-47.5, 54), (-47.5, 127), (-77.5, 127), (-77.5, 45), (-18, 45), (-18, 36.5)]
prism("SK_T09_ARM_1", [24.75, 0, 0], [0, 1, 0], [0, 0, 1], [LA], 3, name=AR)
prism("SK_T09_ARM_2", [27.75, 0, 0], [0, 1, 0], [0, 0, 1], [[(-77.5, 45), (-47.5, 45), (-47.5, 127), (-77.5, 127)]], 2,
      op="join", targets=[AR])
prism("SK_T09_ARM_3", [0, 0, 54], [1, 0, 0], [0, 1, 0],
      [[(24.75, -50), (40, -50), (40, 3), (24.75, 3)], [(17, -98.5), (31, -98.5), (31, -77.5), (17, -77.5)]], 5,
      op="join", targets=[AR])
for y in (-12.5, -2.5):
    cyl(5.5, [24.25, y, 42], "X", 4, targets=[AR])             # 칼 볼트 Ø5.5
for y in (-52.5, -72.5):
    for z in (61.85, 76.85, 101.85, 116.85):
        cyl(3.4, [24.25, y, z], "X", 6, targets=[AR])          # 블록 M3 통과 Ø3.4
cyl(6.0, [XC, YC, 53.5], "Z", 6, targets=[AR])                 # 로드 Ø6
C("material.assign", {"bodies": [AR], "material": "SUS304"})
C("component.activate", {"component": "root"})

# ======================= E: 블록 ×2 + CB3-8 ×8 (T06_KNIFE) =======================
batch('E')
for nm, z0 in zip(BK, (52.0, 92.0)):
    z1 = z0 + 34.7
    zc = (z0 + z1) / 2
    newcomp(nm, "T06_KNIFE")
    box(14.75, 24.75, -76, -49, z0, z1, name=nm)
    box(14.75, 19.75, YR - 6, YR + 6, z0 - 0.5, z1 + 0.5, op="cut", targets=[nm])   # 레일 자리(끼움면)
    for y in (-52.5, -72.5):
        for z in (zc - 7.5, zc + 7.5):
            cyl(2.5, [21.25, y, z], "X", 3.5, targets=[nm])                       # M3 탭 기초 Ø2.5 깊이 3.5(임시)
    C("material.assign", {"bodies": [nm], "material": "Stainless Steel"})
C("component.activate", {"component": "root"})
k = 0
for y in (-52.5, -72.5):
    for z in (61.85, 76.85, 101.85, 116.85):
        k += 1
        nm = "STEP대기_CB3-8_T09_BP%d" % k
        C("parts.insert", {"family": "socket_head_cap_screw", "size": "M3", "length": 8,
                           "point": [29.75, y, z], "direction": [1, 0, 0], "name": nm})
        C("body.rename", {"body": "Body1", "name": nm})
        C("occurrence.reparent", {"occurrence": nm + ":1", "parent": "T06_KNIFE"})

# ======================= F: CB5-16 ×3 실물 STEP (GBASE -> 헤드 코 앞면) =======================
batch('F')
C("component.activate", {"component": "root"})
for i, (x, z) in enumerate(((10, 146), (36, 146), (36, 125)), 1):
    nm = "CB5-16_T09_GB%d" % i
    M = [0, -1, 0, x, 1, 0, 0, -46, 0, 0, 1, z]     # STEP 국소 +X(나사부) -> 세계 +Y, 머리 Y -51~-46
    C("file.insert_step", {"path": SP + "CB5-16/CB5-16.stp", "name": nm, "matrix": M})
    C("body.rename", {"body": "Cut-Extrude1", "name": nm})
    C("component.metadata.set", {"component": nm, "part_number": "CB5-16", "bom_type": "purchased",
                                 "description": "MISUMI 육각 구멍붙이 볼트 M5×16 — P_T09_GBASE F1 장공 → 헤드 코 앞면(Y −40) 탭, 물림 10 (T09)"})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": "T06"})

json.dump(B, open(os.path.join(OUT, 'batches.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for k_, v in B.items():
    json.dump(v, open(os.path.join(OUT, 'b_%s.json' % k_), 'w', encoding='utf-8'), ensure_ascii=False)
    print(k_, len(v))
