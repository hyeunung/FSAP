# T17(모델링부) 생성기: v0.8.4 -> v0.8.5 — 진공 배관 회전부 건너기(T17-C1 수정안)
# 지시서: docs/reports/mechanism/mech_T17_select.md 선정 지시서. 좌표는 세계 대기(J_MAT_X 0, J_MAT_Y -700, ROT 0, 링 0), mm.
# 다르게 정한 곳은 docs/reports/mechanism/mech_T17_model.md 'DEV' 표.
# 쓰는 법: python -B tools/gen_t17_mech.py -> tools/out/mech_T17/model/stage_<a..f>.json (MCP batch 로 차례로 보냄)
#          edit.json = stage a..f 를 이어 붙인 것(tools/out/mech_T17/edit.json)
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T17', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
STAGES = {}
S = None
CX, CY = 0.0, -700.0


def stage(n):
    global S
    S = STAGES.setdefault(n, [])


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 4)


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def box(bb, name=None, op=None, targets=None):
    p = {"length": r6(bb[1] - bb[0]), "width": r6(bb[3] - bb[2]), "height": r6(bb[5] - bb[4]),
         "center": [r6((bb[0] + bb[1]) / 2), r6((bb[2] + bb[3]) / 2), r6((bb[4] + bb[5]) / 2)]}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
        p["operation"] = "new"
    C("solid.box", p)


UP = lambda x, y, z: [0, 1, 0, r6(x), 0, 0, 1, r6(y), 1, 0, 0, r6(z)]       # STEP 몸통 +X -> 세계 +Z


def insert(pn, nm, M, par, body0, desc):
    C("component.activate", {"component": "root"})
    C("file.insert_step", {"path": SP + "%s/%s.stp" % (pn, pn), "name": nm, "matrix": M})
    C("body.rename", {"body": body0, "name": nm})
    C("component.metadata.set", {"component": nm, "part_number": pn, "bom_type": "purchased", "description": desc})
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": par})


YP, DG, POST, DISC, R1 = "P_T01_YPLATE", "P_S01_DGSPACER", "P_T01_POST", "P_T01_DISC", "P_T01_RING1"
CL1, CL2 = "P_T17_TCLAMP_1", "P_T17_TCLAMP_2"

# ---------------------------------------------------------------------------
# a: 이젝터 2개 X축 180도 뒤집어 DG 받침 ±X 면으로, BASE -> MAT_Y
#    T1: 몸통 Y -797.7~-736.0 이 되도록 y' = -y - 436.0 (지시 -440.6 은 지시 범위와 4.6 어긋남 -> 범위 기준, DEV-1)
stage('a')
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("occurrence.move", {"occurrence": "ZH10DSA-06-06-08_T1:1", "space": "world",
                      "matrix": [1, 0, 0, 150, 0, -1, 0, -436.0, 0, 0, -1, -997.6]})
C("occurrence.move", {"occurrence": "ZH10DSA-06-06-08_T2:1", "space": "world",
                      "matrix": [1, 0, 0, -150, 0, -1, 0, -324.3, 0, 0, -1, -997.6]})
C("occurrence.reparent", {"occurrence": "ZH10DSA-06-06-08_T1:1", "parent": "MAT_Y"})
C("occurrence.reparent", {"occurrence": "ZH10DSA-06-06-08_T2:1", "parent": "MAT_Y"})

# ---------------------------------------------------------------------------
# b: Y판 Ø10 x2 + M5 관통 탭 x4, DG 받침 ±X 브래킷 탭(M3 x2 x2, 브래킷 Ø3.2 구멍 축)
stage('b')
C("component.activate", {"component": "MAT_Y"})
for x in (109.6, -109.6):
    cyl(10, (x, -711.2, -371), 'Z', 12, op="cut", targets=[YP])
# DEV-4: Y판 가운데는 r35 구멍이 아니라 X±47.5·Y-870~-665 사각 창이다(실측). (±44) 탭은 창 안이라 살이 없다 -> X ±54(창 가장자리 살 4.4)
for (x, y) in ((54, -724), (54, -698), (-54, -698), (-54, -724)):
    cyl(4.2, (x, y, -371), 'Z', 12, op="cut", targets=[YP])
# 브래킷 ZH2-BK1A 붙이는 판 Ø3.2 구멍 x2(옮긴 뒤 body_topology 실측: 축 X, Y -770.9(T1)/-651.1(T2), Z -352.5·-335.5)
# -> DG 받침 옆면 M3 탭(밑구멍 Ø2.5, 깊이 8). 볼트는 디테일 T17-D1.
BRK_TAPS = [(1, -770.9, z) for z in (-352.5, -335.5)] + [(-1, -651.1, z) for z in (-352.5, -335.5)]
for sx, y, z in BRK_TAPS:
    x0 = 91.9 if sx > 0 else -100.1
    cyl(2.5, (x0, y, z), 'X', 8.2, op="cut", targets=[DG])

# ---------------------------------------------------------------------------
# c: P_T17_TCLAMP_1/_2 (PET-CF 3D 출력, MAT_Y 하위) + CB5-12 x4
stage('c')
CLAMP_DESC = ("PET-CF / FDM 3D 출력 / 관 C클립 받침 한 덩어리: 날개 t4 X34~64·Y-730~-692(Ø5.5 x2 X54), 기둥 X36~52·Z-397.5~-373.5, "
              "팔 X23~36·Z-397.5~-388.5, C클립 고리 (19.05,-711) 안 Ø6.5·바깥 Ø11·Z-398~-388(-Y로 4.5 열림, _2는 +Y), 모서리 R1 (T17 v0.8.5)")


def clamp(nm, sgn):
    # sgn +1: _1(+X). -1: _2 = _1 을 (0,-711) Z축 둘레 180도(x -> -x, y -> -1422 - y)
    def bb(x0, x1, y0, y1, z0, z1):
        if sgn > 0:
            return (x0, x1, y0, y1, z0, z1)
        return (-x1, -x0, -1422 - y1, -1422 - y0, z0, z1)

    def P(x, y):
        return (x, y) if sgn > 0 else (-x, -1422 - y)
    C("component.activate", {"component": "MAT_Y"})
    C("component.create", {"name": nm, "parent": "MAT_Y", "activate": True, "grounded": False})
    box(bb(34, 64, -730, -692, -374, -370), nm)                                   # 날개
    # 기둥 + 팔: 옆(XZ) L 단면 한 스케치를 Y -706 -> -716 으로 밀어 join(같은 평면 바깥면 join 거부 피함, DEV-3)
    sk = "SK_T17_CLAMP_%d" % (1 if sgn > 0 else 2)
    C("sketch.create", {"plane": {"origin": [0, -706, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, "name": sk})
    L = [(23, -397.5), (52, -397.5), (52, -373.5), (36, -373.5), (36, -388.5), (23, -388.5)]
    C("sketch.line", {"points": [[r6(sgn * x), z] for (x, z) in L], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 10, "operation": "join", "targets": [nm]})
    cx, cy = P(19.05, -711)
    cyl(11, (cx, cy, -398), 'Z', 10, op="join", targets=[nm])                     # 고리 바깥 Ø11
    cyl(6.5, (cx, cy, -399), 'Z', 12, op="cut", targets=[nm])                     # 고리 안 Ø6.5
    box(bb(16.8, 21.3, -717, -711, -399, -387), op="cut", targets=[nm])           # 입 4.5, -Y 로 열림(DEV-2)
    for (x, y) in ((54, -724), (54, -698)):
        hx, hy = P(x, y)
        cyl(5.5, (hx, hy, -375), 'Z', 6, op="cut", targets=[nm])                  # Ø5.5 관통
    # 모서리 R1: 날개 바깥 세로 모서리 4 + 기둥 바깥 세로 모서리 2
    e = []
    for (x, y) in ((34, -730), (64, -730), (64, -692), (34, -692)):
        px, py = P(x, y)
        e.append([px, py, -372])
    for (x, y) in ((52, -716), (52, -706)):
        px, py = P(x, y)
        e.append([px, py, -386])
    C("solid.fillet", {"edges": e, "radius": 1})
    C("component.metadata.set", {"component": nm, "part_number": nm, "bom_type": "normal", "description": CLAMP_DESC})


clamp(CL1, 1)
clamp(CL2, -1)
BOLTS = []
for k, (x, y) in enumerate(((54, -724), (54, -698), (-54, -698), (-54, -724)), 1):
    nm = "CB5-12_T17_CL_%d" % k
    insert("CB5-12", nm, UP(x, y, -374), "MAT_Y", "Cut-Extrude1",
           "MISUMI 육각 구멍붙이 볼트 M5×12 — P_T17_TCLAMP 날개 t4 밑에서 -> Y판 M5 관통 탭(물림 8) (T17 v0.8.5)")
    BOLTS.append(nm)

# ---------------------------------------------------------------------------
# d: P_T01_POST — 벽 Ø8(θ270, Z-100), 속 안내 갈래 2(150·30도, r15, Z-192~-182), 바깥 세로 리브 + 연속 C홈
stage('d')
C("component.activate", {"component": "MAT_ROT"})
cyl(8, (0, -732, -100), 'Y', 14, op="cut", targets=[POST])                     # Y -732 ~ -718 (r18~32)
GUIDES = []
for a in (150.0, 30.0):
    gx, gy = r6(15 * math.cos(math.radians(a))), r6(CY + 15 * math.sin(math.radians(a)))
    GUIDES.append((gx, gy))
    cyl(11, (gx, gy, -192), 'Z', 10, op="join", targets=[POST])                  # C 바깥 R5.5 (r9.5~20.5, 벽에 붙음)
    cyl(5.9, (gx, gy, -193), 'Z', 12, op="cut", targets=[POST])                  # 안 Ø5.9 꽉 끼움
    # 축 쪽 입 4.5: 갈래 중심에서 축 방향으로 나가는 띠(스케치 평행사변형)
    ux, uy = -math.cos(math.radians(a)), -math.sin(math.radians(a))             # 축 쪽 단위벡터
    vx, vy = -uy, ux
    pts = []
    for (s, t) in ((0, -2.25), (7, -2.25), (7, 2.25), (0, 2.25)):
        pts.append([r6(gx + s * ux + t * vx), r6(gy + s * uy + t * vy)])
    sk = "SK_T17_GUIDE_%d" % int(a)
    C("sketch.create", {"plane": {"origin": [0, 0, -193], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": sk})
    C("sketch.line", {"points": pts, "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 12, "operation": "cut", "targets": [POST]})
# 바깥 세로 리브 θ270: X -5.25~5.25, r30(겉면 안으로 1 묻음)~56.25, Z -145~-118
box((-5.25, 5.25, -756.25, -728.5, -145, -118), op="join", targets=[POST])
cyl(6.5, (0, -751, -146), 'Z', 29, op="cut", targets=[POST])                    # 연속 C홈 Ø6.5 중심 r51
box((-2.25, 2.25, -757, -751, -146, -117), op="cut", targets=[POST])            # -Y 로 4.5 열림
# 리브 바깥 모서리 R1(바깥 끝 세로 4 + 위·아래 바깥 가로)
C("solid.fillet", {"edges": [[5.25, -756.25, -131.5], [-5.25, -756.25, -131.5]], "radius": 1})
C("solid.fillet", {"edges": [[3.75, -756.25, -118], [-3.75, -756.25, -118], [3.75, -756.25, -145], [-3.75, -756.25, -145]], "radius": 1})
# 뿌리 R2(리브 옆면-기둥 원통 모서리)는 SolidCraft가 거부("both faces next to the edge must be planar") -> 디테일 T17-D7

# ---------------------------------------------------------------------------
# e: 원판 가운데 인서트 + Ø3, 링1 M5 탭 + Ø3, 피팅 임시 형상(E-10)
stage('e')
C("component.activate", {"component": "MAT_ROT"})
cyl(6.4, (0, -700, -12.6), 'Z', 8.1, op="cut", targets=[DISC])                 # MBIS 자리 Z -12.5~-4.5 (기존 Ø6.4 와 같음)
cyl(3, (0, -700, -4.6), 'Z', 4.3, op="cut", targets=[DISC])                    # Ø3 관통 -4.5 ~ -0.5
C("component.activate", {"component": "RING1"})
cyl(4.2, (0, -800, -10.6), 'Z', 6.1, op="cut", targets=[R1])                   # M5 탭 깊이 6 (-10.5~-4.5)
cyl(3, (0, -800, -4.6), 'Z', 4.3, op="cut", targets=[R1])                      # Ø3 관통
insert("MBIS5-6.5-8", "MBIS5-6.5-8_T17_D", UP(0, -700, -12.5), "MAT_ROT", "MBIS5-6.5-8",
       "MISUMI 수지용 인서트 M5 L8 — 원판 Rigid 10K 가운데 밑면 자리 Ø6.4x8, 진공 피팅 KQ2H06-M5A (T17 v0.8.5)")
FITS = []
FDESC = ("SMC 원터치 피팅 KQ2H06-M5A(관 Ø6, M5) — STEP 대기 임시 외곽 Ø12.8x18 + M5 수나사 Ø5x4 "
         "(카탈로그 외형 임시값, 자료대기 새 항목: STEP 수령 -> 바디 교체) (T17 v0.8.5)")
for nm, par, x, y, z0, z1 in (("STEP대기_KQ2H06-M5A_D", "MAT_ROT", 0, -700, -30.5, -12.5),
                               ("STEP대기_KQ2H06-M5A_R1", "RING1", 0, -800, -28.5, -10.5)):
    C("component.activate", {"component": par})
    C("component.create", {"name": nm, "parent": par, "activate": True, "grounded": False})
    cyl(12.8, (x, y, z0), 'Z', z1 - z0, name=nm)
    cyl(5, (x, y, z1 - 0.5), 'Z', 4.5, op="join", targets=[nm])                 # 수나사 z1 ~ z1+4
    C("component.metadata.set", {"component": nm, "part_number": "KQ2H06-M5A", "bom_type": "purchased",
                                 "description": FDESC})
    FITS.append(nm)

# ---------------------------------------------------------------------------
# f: 재질·이름·대기
stage('f')
C("component.activate", {"component": "root"})
C("material.assign", {"bodies": [CL1, CL2], "material": "PET-CF"})
C("material.assign", {"bodies": BOLTS + FITS + ["MBIS5-6.5-8_T17_D"], "material": "Steel"})
C("component.rename", {"component": "root", "name": "FSAP_v0.8.5"})
C("document.metadata.set", {"values": {"description": "T17 mechanism: vacuum line across rotation — ejectors ZH10DSA x2 moved to MAT_Y (flipped, DG spacer sides), Y plate holes, PET-CF tube clamps x2, post wall hole/guides/rib groove, disc centre insert + port, ring1 M5 port, KQ2H06-M5A STEP-wait x2"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})

MADE = {
    CL1: CLAMP_DESC, CL2: CLAMP_DESC,
    POST: "PET-CF / 기존 형상 + 벽 Ø8 θ270 Z-100, 속 안내 갈래 C(안 Ø5.9) 150·30도 r15 Z-192~-182, θ270 바깥 리브 X±5.25·r30~56.25·Z-145~-118 + 연속 C홈 Ø6.5 r51(-Y 4.5 열림)",
    DISC: "Rigid 10K / 가운데 밑면 MBIS 자리 Ø6.4x8 + Ø3 관통",
    R1: "A5052 / (0,-800) 밑면 M5 탭 깊이 6 + Ø3 관통",
    YP: "A5052 t10 / Ø10 관통 x2 (±109.6,-711.2), M5 관통 탭 x4 (±54,-724/-698)",
}
if __name__ == '__main__':
    allc = []
    for n in sorted(STAGES):
        json.dump(STAGES[n], open(os.path.join(OUT, 'stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        allc += STAGES[n]
        print(n, len(STAGES[n]))
    json.dump({"made": MADE, "bolts": BOLTS, "fits": FITS, "guides": GUIDES}, open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('total', len(allc))
