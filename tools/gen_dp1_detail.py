# 디테일링 DP-1 헤드 둘레(모델링부) 생성기: v0.6.1 -> v0.6.2
# 지시서 docs/reports/detailing/detail_plan.md 'DP-1' 그대로. 다르게 정한 곳은 보고서 detail_DP-1_model.md 'DEV' 표.
# 좌표: 대기 세계 좌표(바늘점 원점, 매트 밑면 Z 0). feature 좌표 = 세계 대기 좌표(gen_t06·gen_t04와 같은 방식).
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_dp1_detail.py   -> tools/out/detail/DP-1/build.json
#   solidcraft-cli run tools/out/detail/DP-1/build.json --in 3D_Modeling/FSAP_v0.6.1.sc --save 3D_Modeling/FSAP_v0.6.2.sc
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-1')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
S = []


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op; p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def cylz(d, x, y, z0, z1, name=None, op=None, targets=None):
    cyl(d, [x, y, z0], "Z", z1 - z0, name, op, targets)


def cylx(d, x0, x1, y, z, name=None, op=None, targets=None):
    cyl(d, [min(x0, x1), y, z], "X", abs(x1 - x0), name, op, targets)


def prism(name, sk, origin, xd, yd, pts, dist):
    C("sketch.create", {"plane": {"origin": origin, "x_dir": xd, "y_dir": yd}, "name": sk})
    C("sketch.line", {"points": [[r6(a), r6(b)] for a, b in pts], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": dist, "body_name": name})


def hexpts(af, rot=0.0):
    rc = af / math.sqrt(3)            # 꼭짓점 반지름(맞변/√3·... = af/(2cos30))
    return [(rc * math.cos(math.radians(30 + 60 * k + rot)), rc * math.sin(math.radians(30 + 60 * k + rot))) for k in range(6)]


YC, XS, XC = -7.5, 72.0, 108.0
AR, KN, BR = "P_T06_ARM", "P_T06_KNIFE", "P_T06_BRACKET"
CY, RO = "STEP대기_CJ2B16-30SZ", "STEP대기_CJ2B16-30SZ_ROD"
SHO, SH = "PSFJ16-100_T06", "STEP대기_PSFJT16-100-M5"
HD = "STEP대기_SEWHEAD"
F = "P_T02_FOOT"
PINX = 77.0

C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("material.create", {"name": "A6061-T6", "density_g_cm3": 2.70, "color": "#b8bcc2"})

# ================= (1) P_T06_ARM: 판금 L -> SUS304 절삭 L =================
C("component.activate", {"component": "T06_KNIFE"})
C("body.rename", {"body": AR, "name": "OLD_P_T06_ARM_SHEET"})
C("solid.remove", {"bodies": ["OLD_P_T06_ARM_SHEET"]})
prism(AR, "SK_DP1_ARM", [0, 3, 0], [1, 0, 0], [0, 0, 1],
      [(24.75, 36.5), (27.75, 36.5), (27.75, 54), (120, 54), (120, 59), (24.75, 59)], 21)   # Y 3 -> -18
C("solid.fillet", {"edges": [[27.75, YC, 54]], "radius": 1, "body": AR})                   # 안 모서리 R1
C("solid.chamfer", {"edges": [[24.75, YC, 59]], "distance": 0.5, "body": AR})               # 바깥 모서리 C0.5
for y in (-12.5, -2.5):
    cylx(5.5, 24.25, 28.25, y, 42, op="cut", targets=[AR])                                  # 칼 볼트 Ø5.5 ×2
cylz(6, XC, YC, 53.5, 59.5, op="cut", targets=[AR])                                        # 로드 Ø6 관통
cylz(16, XS, YC, 57, 59.5, op="cut", targets=[AR])                                         # 축 자리 Ø16 H7 깊이 2
cylz(5.5, XS, YC, 53.5, 57.5, op="cut", targets=[AR])                                      # 축 볼트 Ø5.5 관통
cylz(3, PINX, YC, 53.5, 59.5, op="cut", targets=[AR])                                      # 맞춤핀 Ø3 H7 관통
C("material.assign", {"bodies": [AR], "material": "SUS304"})

# ================= (3) T06-D01: 로드 Ø5 Z 49~69 -> 49~99, 실린더 임시 형상 Ø5.4 Z 69~101 =================
cylz(5, XC, YC, 68.5, 99, op="join", targets=[RO])
C("component.activate", {"component": "T06"})
cylz(5.4, XC, YC, 68.9, 101, op="cut", targets=[CY])

# ================= (2) PSFJ16-100_T06 -> STEP대기_PSFJT16-100-M5 =================
C("component.activate", {"component": "root"})
C("component.delete", {"component": SHO})                                  # 가져온 바디는 깎을 수 없다 -> 같은 형상을 다시 그림
C("component.activate", {"component": "T06_KNIFE"})
C("component.create", {"name": SH, "parent": "T06_KNIFE", "activate": True, "grounded": False})
cylz(16, XS, YC, 57, 157, SH)                                              # PSFJ16-100 실물: Ø16 L100, 끝 모따기
for z in (57, 157):
    C("solid.chamfer", {"edges": [[XS + 8, YC, z]], "distance": 0.5, "body": SH})
cylz(4.2, XS, YC, 56.5, 69, op="cut", targets=[SH])                                        # M5 기초 구멍 Ø4.2 × 12(D-37 (2))
cylz(3, PINX, YC, 56.5, 63, op="cut", targets=[SH])                                        # 핀 구멍 Ø3 × 6
C("material.assign", {"bodies": [SH], "material": "Steel"})
C("component.activate", {"component": "root"})

# ================= 브래킷–헤드 탭 자리: STEP대기_SEWHEAD Ø4.2 × 10(D-10 임시) =================
C("component.activate", {"component": "HEAD"})
for y in (-27.0, 12.0):
    cylx(4.2, 30, 40.5, y, 130, op="cut", targets=[HD])

# ================= (4) 체결: 실물 CB5-12 ×5 (root에 세계 행렬, reparent) =================
C("component.activate", {"component": "root"})
BOLTS = [  # 이름, 부모, 행렬(3x4 행 우선). STEP: 머리 X -5~0, 몸통 +X 0~12
    ("CB5-12_T06_KN1", "T06_KNIFE", [-1, 0, 0, 27.75, 0, -1, 0, -12.5, 0, 0, 1, 42]),
    ("CB5-12_T06_KN2", "T06_KNIFE", [-1, 0, 0, 27.75, 0, -1, 0, -2.5, 0, 0, 1, 42]),
    ("CB5-12_T06_BR1", "T06", [-1, 0, 0, 44, 0, -1, 0, -27, 0, 0, 1, 130]),
    ("CB5-12_T06_BR2", "T06", [-1, 0, 0, 44, 0, -1, 0, 12, 0, 0, 1, 130]),
    ("CB5-12_T06_SH", "T06_KNIFE", [0, 1, 0, XS, 0, 0, 1, YC, 1, 0, 0, 54]),
]
for nm, par, M in BOLTS:
    C("file.insert_step", {"path": SP + "CB5-12/CB5-12.stp", "name": nm, "matrix": M})
    C("body.rename", {"body": "Cut-Extrude1", "name": nm})
    C("component.metadata.set", {"component": nm, "part_number": "CB5-12", "bom_type": "purchased",
                                 "description": "MISUMI 육각 구멍붙이 볼트 M5×12 (DP-1 T06)"})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": par})

# ================= STEP대기 체결품(E-10): 각자 컴포넌트, 그 유닛 아래 =================
def comp(nm, par, pn, desc):
    C("component.activate", {"component": par})
    C("component.create", {"name": nm, "parent": par, "activate": True, "grounded": False})
    return (nm, pn, desc)


TMP = []
# LBNR5 ×2 (맞변 8 · 두께 4) 칼 -X 면 X 19.25~23.25, 나사 자리 Ø4.2(물림 표시)
for i, y in enumerate((-12.5, -2.5), 1):
    nm = "STEP대기_LBNR5_T06_%d" % i
    TMP.append(comp(nm, "T06_KNIFE", "LBNR5", "MISUMI 육각 너트 M5 (STEP 대기 D-37, 임시 형상 맞변 8 두께 4)"))
    prism(nm, "SK_DP1_LBNR5_%d" % i, [19.25, y, 42], [0, 1, 0], [0, 0, 1], hexpts(8, 30), 4)   # +X 4
    cylx(4.2, 19, 23.5, y, 42, op="cut", targets=[nm])
# LHFR16 -> 브래킷: CB4-16 ×4(머리 Ø7×4 플랜지 윗면 Z 83~87, 몸통 Ø4 Z 67~83) + LBNR4 ×4(맞변 7 · 두께 3.2, Z 69.8~73)
d = 13.435
for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1)), 1):
    x, y = XS + sx * d, YC + sy * d
    nm = "STEP대기_CB4-16_T06_%d" % i
    TMP.append(comp(nm, "T06", "CB4-16", "MISUMI 육각 구멍붙이 볼트 M4×16 (STEP 대기 D-37, 임시 형상 JIS B 1176 머리 Ø7×4)"))
    cylz(7, x, y, 83, 87, nm)
    cylz(4, x, y, 67, 83.2, op="join", targets=[nm])
    prism("T_DP1_SOCK4_%d" % i, "SK_DP1_SOCK4_%d" % i, [x, y, 85], [1, 0, 0], [0, 1, 0], hexpts(3), 2.5)  # 육각 구멍 맞변 3 깊이 2
    C("solid.combine", {"target": nm, "tools": ["T_DP1_SOCK4_%d" % i], "operation": "cut"})
    nn = "STEP대기_LBNR4_T06_%d" % i
    TMP.append(comp(nn, "T06", "LBNR4", "MISUMI 육각 너트 M4 (STEP 대기 D-37, 임시 형상 맞변 7 두께 3.2)"))
    prism(nn, "SK_DP1_LBNR4_%d" % i, [x, y, 69.8], [1, 0, 0], [0, 1, 0], hexpts(7), 3.2)          # +Z 3.2
    cylz(3.3, x, y, 69.5, 73.5, op="cut", targets=[nn])
# 로드 위 너트: CJ2B16-60SZ 실물 STEP의 NTJ-015C 형상 복사 -> STEP대기_NTJ-015C (팔 위 Z 59~63)
NT = "STEP대기_NTJ-015C_T06"
TMP.append(comp(NT, "T06_KNIFE", "NTJ-015C", "SMC 로드 끝 너트 M5 (CJ2B16-60SZ 실물 STEP의 NTJ-015C 형상 복사, 30SZ STEP 대기 D-37)"))
# 모델 안 CJ2B16-60SZ(T01 R1_1) 실물 STEP의 NTJ-015C 바디를 복사(대기 세계 중심 (0,-510,-20), 축 Z) -> (108,-7.5,61)
C("component.copy_bodies", {"bodies": ["CJ2B16-60SZ_R1_1_NTJ"], "component": NT})
C("body.rename", {"body": "CJ2B16-60SZ_R1_1_NTJ (2)", "name": NT})
C("solid.move", {"bodies": [NT], "translate": [XC, YC + 510, 61 + 38.5]})   # 복사본은 원본 첫 자리(중심 Z -38.5)에 생김: 실측으로 맞춤
C("component.activate", {"component": "root"})

# ================= (6) 구매 P-02: STEP대기 구매품을 컴포넌트로 묶어 part_number =================
GRP = [  # 컴포넌트(=바디) 이름, 부모, part_number, bom_type
    (CY, "T06", "CJ2B16-30SZ", "purchased", "SMC 에어 실린더 CJ2B16-30SZ 본체 (STEP 대기 D-37, 60SZ 실측 보수 외곽)"),
    (RO, "T06_KNIFE", "CJ2B16-30SZ", "reference", "CJ2B16-30SZ 로드(본체와 한 구매품, BOM은 본체 행에서 셈)"),
    (HD, "HEAD", "(기종 미정 D-10)", "purchased", "재봉 헤드 본체 (기종 미정 D-10, 임시 형상)"),
    ("STEP대기_SEWHEAD_PRESSERBAR", "PRESSER", "(기종 미정 D-10)", "reference", "재봉 헤드 노루발대(헤드와 한 구매품, BOM은 헤드 행)"),
    ("STEP대기_SEWHEAD_NEEDLEBAR", "NEEDLE", "(기종 미정 D-10)", "reference", "재봉 헤드 바늘대(헤드와 한 구매품, BOM은 헤드 행)"),
    ("STEP대기_NEEDLE", "NEEDLE", "(기종 미정 D-10)", "reference", "재봉 바늘(헤드 기종에 따름, BOM은 헤드 행)"),
]
for nm, par, pn, bt, desc in GRP:
    C("component.activate", {"component": par})
    C("component.create", {"name": nm, "parent": par, "activate": False, "grounded": False})
    C("component.move_bodies", {"bodies": [nm], "component": nm})
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": bt, "description": desc})
C("component.activate", {"component": "root"})
for nm, pn, desc in TMP:
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": "purchased", "description": desc})
C("component.metadata.set", {"component": SH, "part_number": "PSFJT16-100-M5", "bom_type": "purchased",
                             "description": "MISUMI 리니어 샤프트 Ø16 L100 한쪽 끝 M5 탭 (STEP 대기 D-37: PSFJ16-100 실물 형상 + 끝 Ø4.2×12 + 핀 구멍 Ø3×6 임시)"})

# ================= (5) P_T02_FOOT: A6061-T6, 통로 입구 살 없애기, 주머니·슬릿 안 모서리 R0.5 =================
C("component.activate", {"component": "PRESSER"})
DX, DY = 0.56999, -0.821652
B0 = (0.2198, -7.1471)               # 주머니 끝벽 가운데(통로 입구), Z 27.05
e = 0.05
C("solid.cone", {"radius": 2.1 + e, "top_radius": 1.25, "height": 0.85 + e,
                 "base": [r6(B0[0] - e * DX), r6(B0[1] - e * DY), 27.05], "axis": [DX, DY, 0],
                 "operation": "cut", "targets": [F]})
# 주머니 B끝 안 모서리 2개 + 슬릿 안 모서리 4개 R0.5 (A끝 2개는 통로 입구가 열려 모서리가 끊김 -> DEV)
for p in ((-5.3260, 3.6105, 27.05), (-7.9141, 1.8149, 27.05)):
    C("solid.fillet", {"edges": [list(p)], "radius": 0.5, "body": F})
C("solid.fillet", {"edges": [[0.6962, -6.2110, 22.05], [-0.1254, -6.7811, 22.05]], "radius": 0.5, "body": F})
C("solid.fillet", {"edges": [[-5.5736, 2.8271, 22.05], [-6.3952, 2.2570, 22.05]], "radius": 0.5, "body": F})
C("material.assign", {"bodies": [F], "material": "A6061-T6"})
C("component.activate", {"component": "root"})

# ================= 재질(E-09): 체결품 =================
C("material.assign", {"bodies": [b[0] for b in BOLTS] + [t[0] for t in TMP], "material": "Steel"})

# ================= 컴포넌트 속성(바디 -> 재질 / 만드는 법 / 형상) =================
C("component.metadata.set", {"component": "T06_KNIFE", "properties": {
    AR: "SUS304 / 절삭(밀링) L — 판금 아님(U-05: 판금 t3~t6 모두 M-04 구멍–굽힘 2t 미달, 판금 t5 SF 1.97 < 2, 다리 두께가 달라 판금 불가) / 세로 다리 X24.75~27.75·Z36.5~59(t3) + 가로 다리 X24.75~120·Z54~59(t5), 폭 Y-18~+3, 안 모서리 R1, 바깥 C0.5. 구멍: 칼 볼트 Ø5.5 ×2(Z42), 로드 Ø6(108,-7.5), 축 자리 Ø16 H7 깊이 2 + Ø5.5 관통 + 맞춤핀 Ø3 H7 관통(77,-7.5)",
    RO: "Steel / 구매품 임시 형상(E-10, D-37) / CJ2B16-30SZ 로드 Ø5 Z49~99(T06-D01) + 로드 끝 아래 너트 외곽 Ø9.24 Z50~54",
}})
C("component.metadata.set", {"component": "T06", "properties": {
    CY: "Steel / 구매품 임시 형상(E-10, D-37) / CJ2B16-30SZ: 60SZ 실측 보수 외곽 튜브 Ø18.3 Z77~215 + 보스 Ø10 Z69~77 + 장착 너트 외곽 Ø16.2 Z69~73, 로드 자리 Ø5.4 Z69~101, 포트 M5 +X(Z210)",
}})
C("component.metadata.set", {"component": "PRESSER", "properties": {
    F: "A6061-T6 / 절삭(밀링) + 경질 아노다이징(도면 지시) / L자 바닥 t10 + 자루 18x16 + 위 노즈 r8.5, 바늘 구멍 Ø2.6 + T04 화이버 주머니 12.0x3.15x8(B끝 안 모서리 R0.5) + 검출 슬릿 11.0x1.0 바닥 관통(안 모서리 R0.5) + 화이버 통로 Ø2.6 +X 옆면(9,-19.80,27.05)으로, 통로 입구 45° 모따기 Ø4.2(주머니 모서리 살 제거, DP-1)",
}})
C("document.metadata.set", {"values": {"description": "DP-1 detailing: T06 knife arm machined SUS304 L t3/t5 with shaft seat, 15 fasteners (CB5-12 x5, CB4-16, LBNR4/5, NTJ), rod extension, PSFJT16 tap, presser foot A6061-T6 with fiber channel entry, STEP-wait part numbers"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(S), 'steps')
