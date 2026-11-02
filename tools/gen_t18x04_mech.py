# T18-X04(모델링부) 생성기: v0.8.3 -> v0.8.4 — X·Y 이송 너트 하중 경로 강화(오조작 2364 N)
# 지시서: docs/reports/mechanism/mech_T18_select.md 선정 지시서. 좌표는 세계 대기(J_MAT_X 0, J_MAT_Y -700, ROT 0), mm.
# P_T18_YNB(SUS304 t8 L) -> A6061-T6 절삭 cap + 고리, P_T18_XNP(SUS304 t8 평판) -> A6061-T6 절삭 옆판 + 밑판 + 고리.
# Y 너트 볼트·X 너트 볼트는 방향을 뒤집어 고리 탭에 물리고, YNB->Y판 체결 4개, XNP->1300_R 14조.
# 쓰는 법: python -B tools/gen_t18x04_mech.py -> tools/out/mech_T18/x04/stage_<a..f>.json (MCP batch 로 차례로 보냄)
#          edit.json = stage a..f 를 이어 붙인 것(tools/out/mech_T18/edit.json)
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T18', 'x04')
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
    return [r6(v) for v in (lx[0], ly[0], lz[0], t[0], lx[1], ly[1], lz[1], t[1], lx[2], ly[2], lz[2], t[2])]


def perp(d):
    return (0, 0, 1) if abs(d[2]) < 0.5 else (1, 0, 0)


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


STEELB = []


def ins(step, name, mat, body_old, desc):
    C("file.insert_step", {"path": SP + step + '/' + step + '.stp', "name": name, "matrix": mat})
    C("body.rename", {"body": body_old, "name": name})
    C("component.metadata.set", {"component": name, "part_number": step, "bom_type": "purchased", "description": desc})
    STEELB.append(name)


def bolt(step, name, seat, d, desc):
    # CB STEP: 머리 로컬 X -k~0, 몸통 +X. seat = 머리 자리면 점, d = 넣는 방향(gen_t18_mech.py 와 같음)
    ins(step, name, M(d, perp(d), seat), "Cut-Extrude1", desc)


def tnut(step, name, at, n, s, desc):
    # HNTT: 윗면 로컬 Y=0, 두께 -Y 9. at = 형재 겉면 구멍 중심, n = 겉면 바깥 법선, s = 홈 방향
    o = [at[i] - 2.5 * n[i] for i in range(3)]
    ins(step, name, M(s, n, o), "Tap1", desc)


YNB, XNP, YP = "P_T18_YNB", "P_T18_XNP", "P_T01_YPLATE"
YX, YZ = 85.0, -448.0          # Y 볼나사 축선
XY_, XZ = -410.0, -555.0       # X 볼나사 축선
YB = [(dx, dz) for dx in (-25.55, 25.55) for dz in (-14.75, 14.75)]   # Y 너트 PCD59 (gen_t18 순서)
XB = [(dy, dz) for dy in (-29.44, 29.44) for dz in (-17, 17)]         # X 너트 PCD68
XNP_Y = (-500, -470, -440, -410, -380, -350, -320)
XNP_Z = (-458, -418)

# ---------------------------------------------------------------------------
# a: 지우기 — 옛 YNB·XNP 피처, Y판 옛 M5 탭 피처(T18 Cyl545·546, T14 Cyl616·617), CB8-25 임시 형상 피처, 옛 볼트·T너트
stage('a')
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("timeline.delete", {"features": ["SK_P_T18_YNB", "Extrude43"] + ["Cylinder%d" % i for i in range(538, 547)]
                      + ["Cylinder616", "Cylinder617", "Box121"] + ["Cylinder%d" % i for i in range(589, 606)]})
for n in (["CB5-20_T18_YNUT_%d" % k for k in range(1, 5)] + ["CB5-16_T18_YNB_1", "CB5-16_T18_YNB_2"]
          + ["CB5-20_T18_XNP_%d" % k for k in range(1, 5)] + ["HNTT8-5_T18_XNP_%d" % k for k in range(1, 5)]):
    C("component.delete", {"component": n})

# ---------------------------------------------------------------------------
# b: P_T18_YNB A6061-T6 절삭 한 덩어리(T18_YN, MAT_Y 리지드)
stage('b')
C("component.activate", {"component": "T18_YN"})
box((20, 120, -670, -610, -476, -370), YNB)
box((19, 50, -671, -609, -477, -422), op="cut", targets=[YNB])           # cap 연장부(X20~50) 아래
box((49, 121, -671, -655, -477, -422), op="cut", targets=[YNB])          # 고리 앞(-Y)
box((49, 121, -643, -609, -477, -422), op="cut", targets=[YNB])          # 고리 뒤(+Y)
C("solid.fillet", {"edges": [[85, -655, -422], [85, -643, -422], [50, -649, -422]], "radius": 3})
cyl(48, (YX, -656, YZ), 'Y', 14, op="cut", targets=[YNB])                # 너트 몸 Ø46 + 반경 틈 1
for dx, dz in YB:
    cyl(4.2, (YX + dx, -656, YZ + dz), 'Y', 14, op="cut", targets=[YNB])   # M5 관통 탭
for y in (-657, -623):
    cyl(9.5, (30, y, -423), 'Z', 45, op="cut", targets=[YNB])            # 카운터보어 -422 -> -378
    cyl(5.5, (30, y, -379), 'Z', 10, op="cut", targets=[YNB])            # Ø5.5 -378 -> -370
    cyl(4.2, (112, y, -384), 'Z', 15, op="cut", targets=[YNB])           # M5 탭 깊이 14(-370 -> -384)

# ---------------------------------------------------------------------------
# c: Y판 구멍 + YNB 볼트
stage('c')
C("component.activate", {"component": "MAT_Y"})
for y in (-657, -623):
    cyl(4.2, (30, y, -371), 'Z', 12, op="cut", targets=[YP])             # M5 관통 탭(물림 8)
    cyl(5.5, (112, y, -371), 'Z', 12, op="cut", targets=[YP])            # Ø5.5 관통
C("component.activate", {"component": "T18_YN"})
for k, (dx, dz) in enumerate(YB, 1):
    bolt("CB5-20", "CB5-20_T18_YNUT_%d" % k, (YX + dx, -663.5, YZ + dz), (0, 1, 0),
         "MISUMI 육각 구멍붙이 볼트 CB5-20 — Y 너트 플랜지 -Y 카운터보어(바닥 Y-663.5) -> P_T18_YNB 고리 M5 탭(물림 11.5) (T18-X04 v0.8.4)")
for i, y in enumerate((-657, -623), 1):
    bolt("CB5-16", "CB5-16_T18_YNB_%d" % i, (30, y, -378), (0, 0, 1),
         "MISUMI 육각 구멍붙이 볼트 CB5-16 — P_T18_YNB cap 아래 카운터보어 -> Y판 M5 탭(물림 8, 끝-DG 받침 2.0) (T18-X04 v0.8.4)")
for i, y in enumerate((-657, -623), 3):
    bolt("CB5-20", "CB5-20_T18_YNB_%d" % i, (112, y, -360), (0, 0, -1),
         "MISUMI 육각 구멍붙이 볼트 CB5-20 — Y판 윗면 -> P_T18_YNB cap M5 탭(물림 10) (T18-X04 v0.8.4)")

# ---------------------------------------------------------------------------
# d: P_T18_XNP A6061-T6 절삭 한 덩어리(T18_XN, MAT_X 리지드)
stage('d')
C("component.activate", {"component": "T18_XN"})
box((130, 178, -530, -290, -590, -408), XNP)
box((129, 170, -531, -289, -478, -407), op="cut", targets=[XNP])         # 밑판 위·옆판 -X
box((129, 138, -531, -289, -591, -490), op="cut", targets=[XNP])         # 고리 -X
box((155, 179, -531, -289, -591, -490), op="cut", targets=[XNP])         # 고리 +X(너트 플랜지 자리)
box((137, 156, -531, -460, -591, -490), op="cut", targets=[XNP])         # 고리 -Y
box((137, 156, -360, -289, -591, -490), op="cut", targets=[XNP])         # 고리 +Y
C("solid.fillet", {"edges": [[170, -410, -478], [138, -410, -490], [155, -410, -490],
                             [146.5, -460, -490], [146.5, -360, -490]], "radius": 3})
cyl(54, (137, XY_, XZ), 'X', 19, op="cut", targets=[XNP])                # 너트 몸 Ø52 + 반경 틈 1
for dy, dz in XB:
    cyl(6.8, (137, XY_ + dy, XZ + dz), 'X', 19, op="cut", targets=[XNP])  # M8 관통 탭
for y in XNP_Y:
    for z in XNP_Z:
        cyl(5.5, (169, y, z), 'X', 10, op="cut", targets=[XNP])          # 옆판 Ø5.5 x14

# ---------------------------------------------------------------------------
# e: XNP 볼트 — X 너트 CB8-25 임시 형상(E-10, D-56) 뒤집음 + CB5-20/HNTT8-5 x14
stage('e')
C("component.activate", {"component": "T18_XN"})
WAITB = []
for k, (dy, dz) in enumerate(XB, 1):
    nm = "STEP대기_CB8-25_T18_XNUT_%d" % k
    cyl(13, (161.4, XY_ + dy, XZ + dz), 'X', 8, name=nm)                 # 머리 Ø13 x 8 (X 161.4~169.4)
    cyl(8, (136.4, XY_ + dy, XZ + dz), 'X', 25, op="join", targets=[nm])  # 몸통 Ø8 x 25 (X 136.4~161.4)
    WAITB.append(nm)
k = 0
for y in XNP_Y:
    for z in XNP_Z:
        k += 1
        bolt("CB5-20", "CB5-20_T18_XNP_%d" % k, (178, y, z), (-1, 0, 0),
             "MISUMI 육각 구멍붙이 볼트 CB5-20 — P_T18_XNP 옆판 -> 1300_R +X 홈 T너트 (T18-X04 v0.8.4)")
        tnut("HNTT8-5", "HNTT8-5_T18_XNP_%d" % k, (170, y, z), (1, 0, 0), (0, 1, 0),
             "MISUMI 후입 T너트 HNTT8-5 — HFS8-4080-1300_R +X 홈, CB5-20_T18_XNP 짝 (T18-X04 v0.8.4)")

# ---------------------------------------------------------------------------
# f: 재질·이름·대기
stage('f')
C("component.activate", {"component": "root"})
C("material.assign", {"bodies": [YNB, XNP], "material": "A6061-T6"})
C("material.assign", {"bodies": STEELB + WAITB, "material": "Steel"})
C("component.rename", {"component": "root", "name": "FSAP_v0.8.4"})
C("document.metadata.set", {"values": {"description": "T18 mechanism: X/Y ball nut load path, A6061 machined YNB/XNP with tapped rings, nut bolts reversed, XNP 14 bolts"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})

MADE = {
    YNB: "A6061-T6 / 절삭 한 덩어리 / cap X20~120·Y-670~-610·Z-422~-370 + 고리 X50~120·Y-655~-643·Z-476~-422(구멍 Ø48, M5 관통 탭 x4 PCD59), 안 R3, cap 아래 카운터보어 Ø9.5x44+Ø5.5 x2 (30,-657/-623), cap 위 M5 탭 깊이 14 x2 (112,-657/-623)",
    XNP: "A6061-T6 / 절삭 한 덩어리 / 옆판 X170~178·Y-530~-290·Z-490~-408(Ø5.5 x14) + 밑판 X130~178·Z-490~-478 + 고리 X138~155·Y-460~-360·Z-590~-490(구멍 Ø54, M8 관통 탭 x4 PCD68), 안 R3",
}
allc = []
for n in sorted(STAGES):
    json.dump(STAGES[n], open(os.path.join(OUT, 'stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    allc += STAGES[n]
    print(n, len(STAGES[n]))
json.dump(allc, open(os.path.join(ROOT, 'tools', 'out', 'mech_T18', 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump({"made": MADE, "waitbolts": WAITB, "steel": STEELB}, open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total', len(allc))
