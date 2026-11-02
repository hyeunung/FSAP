# T18 X·Y 이송 구동 유닛(모델링부) 생성기: v0.7.2 -> v0.8.0 (부품 묶음 T18 신설, 부 번호 +1, 요구서 8-2·E-05)
# 지시서 docs/reports/mechanism/mech_T18_select.md 5절 + 선정 지시서(T18-S). 실물 STEP 실측으로 바꾼 곳은 보고서 mech_T18_model.md 'DEV' 표.
# 좌표: 세계 대기(J_MAT_X 0, J_MAT_Y -700, ROT 0), mm. 행렬은 3x4 행 우선(열 = 로컬 X·Y·Z 축의 세계 방향, 마지막 열 = 원점).
# 쓰는 법: python -B tools/gen_t18_mech.py -> tools/out/mech_T18/model/stage_<a..f>.json (MCP batch 로 차례로 보냄)
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T18', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
STAGES = {}
S = None


def stage(n):
    global S
    S = STAGES.setdefault(n, [])


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 4)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def M(lx, ly, t):
    lz = cross(lx, ly)
    return [lx[0], ly[0], lz[0], t[0], lx[1], ly[1], lz[1], t[1], lx[2], ly[2], lz[2], t[2]]


def perp(d):
    return (0, 0, 1) if abs(d[2]) < 0.5 else (1, 0, 0)


def ins(step, name, mat, rename=None, pn=None, desc=None, bom='purchased'):
    C("file.insert_step", {"path": SP + step + '/' + step + '.stp', "name": name, "matrix": [r6(v) for v in mat]})
    for old, new in (rename or {}).items():
        C("body.rename", {"body": old, "name": new})
    md = {"component": name, "part_number": pn or step, "bom_type": bom}
    if desc:
        md["description"] = desc
    C("component.metadata.set", md)


AX = {'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}


def cyl(d, base, axis, h, name=None, op=None, targets=None):
    p = {"diameter": d, "height": r6(h), "base": [r6(v) for v in base], "axis": axis}
    if op:
        p["operation"] = op
        p["targets"] = targets
    else:
        p["body_name"] = name
    C("solid.cylinder", p)


def cyl_span(d, axis, a0, a1, c1, c2, name=None, op=None, targets=None):
    # axis 방향 a0~a1, 나머지 두 좌표 c1,c2 (X축: (y,z), Y축: (x,z), Z축: (x,y))
    lo = min(a0, a1)
    if axis == 'X':
        base = [lo, c1, c2]
    elif axis == 'Y':
        base = [c1, lo, c2]
    else:
        base = [c1, c2, lo]
    cyl(d, base, axis, abs(a1 - a0), name, op, targets)


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


def bolt(step, name, seat, d):
    # CB STEP: 머리 X -k~0, 몸통 +X. seat = 머리 자리면 점, d = 넣는 방향
    ins(step, name, M(d, perp(d), seat), {"Cut-Extrude1": name}, step)
    STEELB.append(name)


def stepwait_bolt(name, seat, d, L, dh=13.0, kh=8.0, ds=8.0):
    # E-10 임시 형상: 머리 Ø13 x 8 + 몸통 Ø8 x L (CB8 카탈로그 외형)
    ax = 'X' if d[0] else ('Y' if d[1] else 'Z')
    s = d[0] + d[1] + d[2]
    a = seat[{'X': 0, 'Y': 1, 'Z': 2}[ax]]
    o = [seat[i] for i in range(3) if i != {'X': 0, 'Y': 1, 'Z': 2}[ax]]
    cyl_span(dh, ax, a - s * kh, a, o[0], o[1], name=name)
    cyl_span(ds, ax, a, a + s * L, o[0], o[1], op="join", targets=[name])
    WAITB.append(name)


def tnut(step, name, at, n, s):
    # HNTT: 윗면 로컬 Y=0(어깨 Y-3), 두께 -Y 9, 길이 로컬 X(홈 방향). at = 형재 겉면의 구멍 중심, n = 겉면 바깥 법선
    o = [at[i] - 2.5 * n[i] for i in range(3)]
    ins(step, name, M(s, n, o), {"Tap1": name}, step)
    STEELB.append(name)


WAITB = []
STEELB = []
SUS, STL, S45, ALU, A2017 = "SUS304", "Steel", "S45C", "Aluminum", "A2017"
MADE = {}
# ---------------------------------------------------------------------------
# a: 준비 + Y 축 묶음(T18_Y, MAT_X 리지드)
stage('a')
C("material.create", {"name": "S45C", "density_g_cm3": 7.85, "color": "#8a8f96"})
C("material.create", {"name": "A2017", "density_g_cm3": 2.79, "color": "#c0c4ca"})
C("component.activate", {"component": "root"})
C("component.create", {"name": "T18_Y", "activate": True, "grounded": False})
YX, YZ = 85.0, -448.0
ins("BSW15", "BSW15", M((0, 1, 0), (0, 0, 1), (YX, 223, -478)), pn="BSW15",
    desc="MISUMI 볼나사 고정측 서포트 유닛 각형 BSW15 (T18 Y 뒤 460_B 윗면 홈 Y223)")
ins("BUN15", "BUN15", M((0, 1, 0), (0, 0, 1), (YX, -957, -478)), pn="BUN15",
    desc="MISUMI 볼나사 지지측 서포트 유닛 각형 BUN15 (T18 Y 앞 460_F 윗면 홈 Y-957)")
# Y 볼나사 축 STEP대기_BSS2020-1240 (BSS2020-1258 STEP 단면 그대로, 나사부 18 짧게)
YS = "STEP대기_BSS2020-1240"
seg = [(-964.5, -952.5, 15), (-952.5, 192.5, 20), (192.5, 200.5, 15), (200.5, 215.5, 20), (215.5, 255.5, 15), (255.5, 275.5, 12)]
for i, (a0, a1, d) in enumerate(seg):
    if i == 0:
        cyl_span(d, 'Y', a0, a1, YX, YZ, name=YS)
    else:
        cyl_span(d, 'Y', a0, a1, YX, YZ, op="join", targets=[YS])
ins("SCXW46-12-19", "SCXW46-12-19", M((0, 1, 0), (1, 0, 0), (YX, 255, YZ)),
    {"Fillet1": "SCXW46-12-19_BODY", "Cut-Revolve1": "SCXW46-12-19_SCREW"}, "SCXW46-12-19",
    "MISUMI 커플링 디스크형 클램프 SCXW46 Ø12-Ø19 (GCPW39-12-19 미스미에 없음 -> 대체)")
# Y 서보 STEP대기_MHMF082L1U2M (80각 플랜지 t10, 인로 Ø70x3, 몸 Ø74, 축 Ø19)
SY = "STEP대기_MHMF082L1U2M_Y"
box((YX - 40, YX + 40, 308, 318, YZ - 40, YZ + 40), SY)
cyl_span(70, 'Y', 305, 308, YX, YZ, op="join", targets=[SY])
cyl_span(74, 'Y', 318, 438, YX, YZ, op="join", targets=[SY])
cyl_span(19, 'Y', 285, 305, YX, YZ, op="join", targets=[SY])
P45 = 31.8198
for dx in (-P45, P45):
    for dz in (-P45, P45):
        cyl_span(6.6, 'Y', 307, 319, YX + dx, YZ + dz, op="cut", targets=[SY])
# P_T18_YMB 모자형 판금 SUS304 t8 (안 R8 / 바깥 R16), Z -558~-400 밀고 자름
YMB = "P_T18_YMB"
C("sketch.create", {"plane": {"origin": [0, 0, -558], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": "SK_" + YMB})
C("sketch.line", {"points": [[-10, 243], [28, 243], [28, 300], [142, 300], [142, 243], [180, 243], [180, 251],
                             [150, 251], [150, 308], [20, 308], [20, 251], [-10, 251]], "closed": True})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_" + YMB, "profiles": "all", "distance": 158, "body_name": YMB})
C("solid.fillet", {"edges": [[20, 251, -479], [28, 300, -479], [142, 300, -479], [150, 251, -479]], "radius": 8})
C("solid.fillet", {"edges": [[28, 243, -479], [20, 308, -479], [150, 308, -479], [142, 243, -479]], "radius": 16})
box((36, 134, 299, 309, -560, -490), op="cut", targets=[YMB])
box((-11, 12, 242, 252, -480, -399), op="cut", targets=[YMB])
box((158, 181, 242, 252, -480, -399), op="cut", targets=[YMB])
cyl_span(70.1, 'Y', 299, 309, YX, YZ, op="cut", targets=[YMB])
for dx in (-P45, P45):
    for dz in (-P45, P45):
        cyl_span(4.2, 'Y', 299, 309, YX + dx, YZ + dz, op="cut", targets=[YMB])
for x in (2, 168):
    for z in (-538, -498):
        cyl_span(5.5, 'Y', 242, 252, x, z, op="cut", targets=[YMB])
MADE[YMB] = 'SUS304 / 판금 t8 모자형(굽힘 4, 안 R8) 레이저+절곡 / 모터 면 X20~150·Y300~308·Z-490~-400(인로 Ø70.1, M5 탭 x4 PCD90), 옆벽 X20~28·142~150·Y251~300·Z-558~-400, 탭 X-10~20·150~180·Y243~251·Z-558~-480(Ø5.5 x4 -> 460_B 뒷면 홈 Z-538·-498)'
# 체결: 유닛 M8(STEP 대기 CB8-35), T너트 HNTT8-8 / 탭 CB5-20 + HNTT8-5 / 서보 CB5-20
for tag, y in (("BSW15", 223), ("BUN15", -957)):
    for i, x in enumerate((55, 115), 1):
        stepwait_bolt("STEP대기_CB8-35_T18_%s_%d" % (tag, i), (x, y, -453), (0, 0, -1), 35)
        tnut("HNTT8-8", "HNTT8-8_T18_%s_%d" % (tag, i), (x, y, -478), (0, 0, 1), (1, 0, 0))
k = 0
for x in (2, 168):
    for z in (-538, -498):
        k += 1
        bolt("CB5-20", "CB5-20_T18_YMB_%d" % k, (x, 251, z), (0, -1, 0))
        tnut("HNTT8-5", "HNTT8-5_T18_YMB_%d" % k, (x, 243, z), (0, 1, 0), (1, 0, 0))
k = 0
for dx in (-P45, P45):
    for dz in (-P45, P45):
        k += 1
        bolt("CB5-20", "CB5-20_T18_SVY_%d" % k, (YX + dx, 318, YZ + dz), (0, -1, 0))

# ---------------------------------------------------------------------------
# b: Y 너트(T18_YN, MAT_Y 리지드)
stage('b')
C("component.activate", {"component": "root"})
C("component.create", {"name": "T18_YN", "activate": True, "grounded": False})
ins("BSS2020-1258", "BSS2020-1240_NUT", M((0, -1, 0), (1, 0, 0), (YX, -588, YZ)), {"Tap1": "BSS2020-1240_NUT"},
    "BSS2020-1240", "MISUMI 정밀 볼나사 BSS2020-1240의 너트(BSS2020-1258 STEP 너트 그대로, 축은 STEP대기_BSS2020-1240)")
C("body.rename", {"body": "Cut-Extrude1", "name": "TMP_SHAFT_BSS2020-1258"})   # STEP 축 바디를 고유 이름으로 바꾼 뒤 지움(너트만 남김)
C("selection.delete", {"items": [{"type": "body", "name": "TMP_SHAFT_BSS2020-1258"}]})
C("component.delete", {"component": "SHAFT_BSS2020-1258"})
YNB = "P_T18_YNB"
C("sketch.create", {"plane": {"origin": [50, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, "name": "SK_" + YNB})
# 굽힘 R은 스케치 호로(안 R8 / 바깥 R16) - solid.fillet 두 번째 모서리 점이 MAT_Y 변위만큼 어긋나 거부됨(보고서 워크플로우 메모)
C("sketch.line", {"points": [[-678, -386], [-678, -476], [-670, -476], [-670, -386]]})
C("sketch.arc.center_point", {"center": [-662, -386], "start": [-670, -386], "end": [-662, -378], "clockwise": True})
C("sketch.line", {"points": [[-662, -378], [-610, -378], [-610, -370], [-662, -370]]})
C("sketch.arc.center_point", {"center": [-662, -386], "start": [-662, -370], "end": [-678, -386]})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_" + YNB, "profiles": "all", "distance": 70, "body_name": YNB})
cyl_span(30, 'Y', -679, -669, YX, YZ, op="cut", targets=[YNB])
for dx in (-25.55, 25.55):
    for dz in (-14.75, 14.75):
        cyl_span(4.2, 'Y', -679, -669, YX + dx, YZ + dz, op="cut", targets=[YNB])
for x in (55, 115):
    cyl_span(5.5, 'Z', -379, -369, x, -640, op="cut", targets=[YNB])
MADE[YNB] = 'SUS304 / 판금 t8 L(굽힘 1, 안 R8) 레이저+절곡 / 웹 X50~120·Y-678~-670·Z-476~-378(축 구멍 Ø30, 너트 플랜지 M5 탭 x4 PCD59), 윗다리 Y-678~-610·Z-378~-370(Ø5.5 x2 -> Y판 M5 탭)'
# Y판(P_T01_YPLATE, A5052 t15, MAT_Y 컴포넌트 바디) 밑면 M5 탭 자리 Ø4.2 x 10 (물림 8)
C("component.activate", {"component": "MAT_Y"})
for x in (55, 115):
    cyl_span(4.2, 'Z', -371, -360, x, -640, op="cut", targets=["P_T01_YPLATE"])
C("component.activate", {"component": "T18_YN"})
k = 0
for dx in (-25.55, 25.55):
    for dz in (-14.75, 14.75):
        k += 1
        bolt("CB5-20", "CB5-20_T18_YNUT_%d" % k, (YX + dx, -655, YZ + dz), (0, -1, 0))
for i, x in enumerate((55, 115), 1):
    bolt("CB5-16", "CB5-16_T18_YNB_%d" % i, (x, -640, -378), (0, 0, 1))

# ---------------------------------------------------------------------------
# c: X 축 묶음(T18_X, BASE 리지드) - 가로대·이음·받침판·유닛
stage('c')
C("component.activate", {"component": "root"})
C("component.create", {"name": "T18_X", "activate": True, "grounded": False})
for tag, cx in (("XM", -567), ("XP", 836)):
    nm = "HFS8-4080-1140_T18_%s" % tag
    ins("HFS8-4080-1140", nm, M((0, 1, 0), (1, 0, 0), (cx, -980, -620)), {"Boss-Extrude1": nm}, "HFS8-4080-1140",
        "MISUMI 알루미늄 프레임 8 시리즈 40x80 L1140 (T18 X 가로대 %s, 끝은 1900_F/B 안쪽 면에 맞댐 -> 캡 없음)" % tag)
k = 0
for xs, sx in ((-607, -1), (-527, 1), (796, -1), (876, 1)):
    for yf, sy in ((-980, 1), (160, -1)):
        k += 1
        nm = "HBLFSN8_T18_%d" % k
        # 로컬 Y(다리 A 면 법선) -> 가로대 옆면 바깥(sx), 로컬 Z(다리 B) -> 1900 안쪽(sy), 로컬 X = Y x Z
        ins("HBLFSN8", nm, M((0, 0, sx * sy), (sx, 0, 0), (xs, yf, -620)), {"NONE": nm}, "HBLFSN8",
            "MISUMI 8 시리즈 탭붙이 브래킷 (T18 가로대 끝 ↔ 1900 안쪽 면)")
XZ = -555.0
XBP, XSP = "P_T18_XBP", "P_T18_XSP"
box((-607, -527, -490, -330, -600, -585), XBP)
box((796, 876, -490, -330, -600, -585), XSP)
for nm, xs, cx in ((XBP, (-558, -536), (-587, -547)), (XSP, (816,), (816, 856))):
    for x in xs:
        for y in (-447.5, -372.5):
            cyl_span(6.8, 'Z', -601, -584, x, y, op="cut", targets=[nm])
    for x in cx:
        for y in (-475, -345):
            cyl_span(5.5, 'Z', -601, -584, x, y, op="cut", targets=[nm])
            cyl_span(9.5, 'Z', -590, -584, x, y, op="cut", targets=[nm])
MADE[XBP] = 'SUS304 / 레이저 평판 t15 + 탭·자리파기 / X-607~-527·Y-490~-330·Z-600~-585, BSW20 M8 탭 x4(물림 15), 가로대 윗면 홈 X-587·-547에 CB5-20 x4(자리파기 Ø9.5 깊이 5)'
MADE[XSP] = 'SUS304 / 레이저 평판 t15 + 탭·자리파기 / X796~876·Y-490~-330·Z-600~-585, BUN20 M8 탭 x2(물림 15), 가로대 윗면 홈 X816·856에 CB5-20 x4(자리파기 Ø9.5 깊이 5)'
ins("BSW20", "BSW20", M((-1, 0, 0), (0, 0, 1), (-547, -410, -585)), pn="BSW20",
    desc="MISUMI 볼나사 고정측 서포트 유닛 각형 BSW20 (T18 X -X 가로대, 받침판 P_T18_XBP 위)")
ins("BUN20", "BUN20", M((-1, 0, 0), (0, 0, 1), (816, -410, -585)), pn="BUN20",
    desc="MISUMI 볼나사 지지측 서포트 유닛 각형 BUN20 (T18 X +X 가로대, 받침판 P_T18_XSP 위)")
k = 0
for x in (-558, -536):
    for y in (-447.5, -372.5):
        k += 1
        bolt("CB8-45", "CB8-45_T18_BSW20_%d" % k, (x, y, -555), (0, 0, -1))
for i, y in enumerate((-447.5, -372.5), 1):
    bolt("CB8-45", "CB8-45_T18_BUN20_%d" % i, (816, y, -555), (0, 0, -1))
k = 0
for tag, cx in (("XBP", (-587, -547)), ("XSP", (816, 856))):
    for x in cx:
        for y in (-475, -345):
            k += 1
            bolt("CB5-20", "CB5-20_T18_%s_%d" % (tag, k), (x, y, -590), (0, 0, -1))
            tnut("HNTT8-5", "HNTT8-5_T18_%s_%d" % (tag, k), (x, y, -600), (0, 0, 1), (0, 1, 0))

# ---------------------------------------------------------------------------
# d: X 축 묶음 계속 - 볼나사 축·커플링·서보·모터 브래킷
stage('d')
C("component.activate", {"component": "T18_X"})
XS = "STEP대기_BSS2520-1443"
seg = [(809, 827, 20), (-508, 809, 25), (-516, -508, 20), (-536, -516, 25), (-589, -536, 20), (-616, -589, 15)]
for i, (a0, a1, d) in enumerate(seg):
    if i == 0:
        cyl_span(d, 'X', a0, a1, -410, XZ, name=XS)
    else:
        cyl_span(d, 'X', a0, a1, -410, XZ, op="join", targets=[XS])
ins("SCXW46-15-19", "SCXW46-15-19", M((-1, 0, 0), (0, 1, 0), (-591, -410, XZ)),
    {"Fillet1": "SCXW46-15-19_BODY", "Cut-Revolve1": "SCXW46-15-19_SCREW"}, "SCXW46-15-19",
    "MISUMI 커플링 디스크형 클램프 SCXW46 Ø15-Ø19 (GCPW39-15-19 미스미에 없음 -> 대체)")
SX = "STEP대기_MHMF082L1U2M_X"
box((-656, -646, -450, -370, XZ - 40, XZ + 40), SX)
cyl_span(70, 'X', -646, -643, -410, XZ, op="join", targets=[SX])
cyl_span(74, 'X', -776, -656, -410, XZ, op="join", targets=[SX])
cyl_span(19, 'X', -643, -621, -410, XZ, op="join", targets=[SX])
for dy in (-P45, P45):
    for dz in (-P45, P45):
        cyl_span(6.6, 'X', -657, -645, -410 + dy, XZ + dz, op="cut", targets=[SX])
XMB = "P_T18_XMB"
C("sketch.create", {"plane": {"origin": [0, -365, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, "name": "SK_" + XMB})
C("sketch.line", {"points": [[-630, -648], [-540, -648], [-540, -640], [-630, -640]]})
C("sketch.arc.center_point", {"center": [-630, -632], "start": [-630, -640], "end": [-638, -632], "clockwise": True})
C("sketch.line", {"points": [[-638, -632], [-638, -505], [-646, -505], [-646, -632]]})
C("sketch.arc.center_point", {"center": [-630, -632], "start": [-646, -632], "end": [-630, -648]})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_" + XMB, "profiles": "all", "distance": 90, "body_name": XMB})
cyl_span(70.1, 'X', -647, -637, -410, XZ, op="cut", targets=[XMB])
for dy in (-P45, P45):
    for dz in (-P45, P45):
        cyl_span(4.2, 'X', -647, -637, -410 + dy, XZ + dz, op="cut", targets=[XMB])
for x in (-587, -547):
    cyl_span(5.5, 'Z', -649, -639, x, -410, op="cut", targets=[XMB])
MADE[XMB] = 'SUS304 / 판금 t8 L(굽힘 1, 안 R8) 레이저+절곡 / 판 X-646~-638·Y-455~-365·Z-648~-505(인로 Ø70.1, M5 탭 x4 PCD90), 발 X-646~-540·Z-648~-640(Ø5.5 x2 -> -X 가로대 밑면 홈 X-587·-547)'
k = 0
for dy in (-P45, P45):
    for dz in (-P45, P45):
        k += 1
        bolt("CB5-20", "CB5-20_T18_SVX_%d" % k, (-656, -410 + dy, XZ + dz), (1, 0, 0))
for i, x in enumerate((-587, -547), 1):
    bolt("CB5-20", "CB5-20_T18_XMB_%d" % i, (x, -410, -648), (0, 0, 1))
    tnut("HNTT8-5", "HNTT8-5_T18_XMB_%d" % i, (x, -410, -640), (0, 0, -1), (0, 1, 0))

# ---------------------------------------------------------------------------
# e: X 너트판(T18_XN, MAT_X 리지드)
stage('e')
C("component.activate", {"component": "root"})
C("component.create", {"name": "T18_XN", "activate": True, "grounded": False})
ins("BSS2520-1475", "BSS2520-1443_NUT", M((1, 0, 0), (0, 1, 0), (82, -410, XZ)), {"Tap1": "BSS2520-1443_NUT"},
    "BSS2520-1443", "MISUMI 정밀 볼나사 BSS2520-1443의 너트(BSS2520-1475 STEP 너트 그대로, 축은 STEP대기_BSS2520-1443)")
C("body.rename", {"body": "Cut-Extrude1", "name": "TMP_SHAFT_BSS2520-1475"})   # STEP 축 바디를 고유 이름으로 바꾼 뒤 지움(너트만 남김)
C("selection.delete", {"items": [{"type": "body", "name": "TMP_SHAFT_BSS2520-1475"}]})
C("component.delete", {"component": "SHAFT_BSS2520-1475"})
XNP = "P_T18_XNP"
box((170, 178, -460, -360, -581, -408), XNP)
cyl_span(30, 'X', 169, 179, -410, XZ, op="cut", targets=[XNP])
for dy in (-29.44, 29.44):
    for dz in (-17, 17):
        cyl_span(6.8, 'X', 169, 179, -410 + dy, XZ + dz, op="cut", targets=[XNP])
for y in (-440, -380):
    for z in (-458, -418):
        cyl_span(5.5, 'X', 169, 179, y, z, op="cut", targets=[XNP])
MADE[XNP] = 'SUS304 / 레이저 평판 t8 + 탭 / X170~178·Y-460~-360·Z-581~-408, 축 구멍 Ø30, 너트 플랜지 M8 탭 x4(PCD68), 1300_R 바깥 옆면 홈 Z-458·-418에 CB5-20 x4'
k = 0
for dy in (-29.44, 29.44):
    for dz in (-17, 17):
        k += 1
        stepwait_bolt("STEP대기_CB8-25_T18_XNUT_%d" % k, (155, -410 + dy, XZ + dz), (1, 0, 0), 25)
k = 0
for y in (-440, -380):
    for z in (-458, -418):
        k += 1
        bolt("CB5-20", "CB5-20_T18_XNP_%d" % k, (178, y, z), (-1, 0, 0))
        tnut("HNTT8-5", "HNTT8-5_T18_XNP_%d" % k, (170, y, z), (1, 0, 0), (0, 1, 0))

# ---------------------------------------------------------------------------
# f: 재질·속성·리지드 그룹
stage('f')
C("component.activate", {"component": "root"})
C("material.assign", {"bodies": list(MADE.keys()), "material": SUS})
C("material.assign", {"bodies": [YS, XS, "BSS2020-1240_NUT", "BSS2520-1443_NUT",
                                 "BSW15_b", "BSW15_c", "BSW15_n", "BUN15_b", "RRING-C-EXT-15",
                                 "BSW20_b", "BSW20_c", "BSW20_n", "BUN20_b", "RRING-C-EXT-20"], "material": S45})
C("material.assign", {"bodies": ["SCXW46-12-19_BODY", "SCXW46-15-19_BODY"], "material": A2017})
C("material.assign", {"bodies": ["HFS8-4080-1140_T18_XM", "HFS8-4080-1140_T18_XP"] + ["HBLFSN8_T18_%d" % i for i in range(1, 9)], "material": ALU})
C("material.assign", {"bodies": STEELB + WAITB + ["STEP대기_MHMF082L1U2M_Y", "STEP대기_MHMF082L1U2M_X", "SCXW46-12-19_SCREW", "SCXW46-15-19_SCREW"], "material": STL})
# 리지드 그룹(M-07, E-11): Y 축 묶음·X 너트판 = MAT_X, Y 너트 = MAT_Y, X 축 묶음 = BASE
C("joint.rigid_group", {"occurrences": ["MAT_X:1", "T18_Y:1", "T18_XN:1"]})
C("joint.rigid_group", {"occurrences": ["MAT_Y:1", "T18_YN:1"]})
C("joint.rigid_group", {"occurrences": ["BASE:1", "T18_X:1"]})
# STEP 하위 묶음(유닛·커플링·너트·브래킷)을 각 T18 컴포넌트에 리지드로(첫 저장 뒤 joint.list floating 16묶음 -> 0)
C("joint.rigid_group", {"occurrences": ["T18_Y:1", "BSW15:1", "BUN15:1", "SCXW46-12-19:1"]})
C("joint.rigid_group", {"occurrences": ["T18_YN:1", "BSS2020-1240_NUT:1"]})
C("joint.rigid_group", {"occurrences": ["T18_X:1", "BSW20:1", "BUN20:1", "SCXW46-15-19:1"] + ["HBLFSN8_T18_%d:1" % i for i in range(1, 9)]})
C("joint.rigid_group", {"occurrences": ["T18_XN:1", "BSS2520-1443_NUT:1"]})
# 축 고침: 유닛 칼라2(나사 쪽)가 축 어깨에 닿게(Y 어깨 205.5, X 어깨 -525), 지지측 스냅 링 홈. 자르면 축이 나뉘므로 combine으로 다시 한 바디
C("component.activate", {"component": "T18_Y"})
cyl_span(21, 'Y', 205.5, 215.5, YX, YZ, op="cut", targets=[YS]); cyl_span(15, 'Y', 205.5, 215.5, YX, YZ, op="join", targets=[YS])
cyl_span(16, 'Y', -962.65, -961.5, YX, YZ, op="cut", targets=[YS]); cyl_span(14.3, 'Y', -962.65, -961.5, YX, YZ, op="join", targets=[YS])
C("solid.combine", {"target": YS, "tools": [YS + " (1)", YS + " (2)"], "operation": "join"})
C("component.activate", {"component": "T18_X"})
cyl_span(26, 'X', -536, -525, -410, XZ, op="cut", targets=[XS]); cyl_span(20, 'X', -536, -525, -410, XZ, op="join", targets=[XS])
cyl_span(21, 'X', 823, 824.35, -410, XZ, op="cut", targets=[XS]); cyl_span(19, 'X', 823, 824.35, -410, XZ, op="join", targets=[XS])
C("solid.combine", {"target": XS, "tools": [XS + " (1)", XS + " (2)"], "operation": "join"})
C("component.activate", {"component": "root"})
C("document.metadata.set", {"values": {"description": "T18 mechanism: X/Y ball screw units BSS2020-1240/BSS2520-1443 (STEP wait), BSW/BUN units, SCXW46 couplings, servo STEP wait x2, SUS brackets"}})
json.dump({"made": MADE, "waitbolts": WAITB}, open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for n, st in STAGES.items():
    json.dump(st, open(os.path.join(OUT, 'stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(n, len(st))
