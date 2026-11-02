# T17 수정 1회차(모델링부) 생성기: v0.8.5 -> v0.8.6 — 기둥 θ270 리브 뿌리 R2(원통–평면 모서리)
# SolidCraft solid.fillet 은 평면–평면 모서리만 받는다("both faces next to the edge must be planar").
# 그래서 뿌리 R2 를 정확한 형상으로 직접 만든다(덧대기 아님: 같은 바디 P_T01_POST 에 join, 한 바디 유지).
#   - 세로 뿌리 2(리브 옆면 X ±5.25 – 원통 r30): XY 단면(직선 + R2 호, 두 면에 접함)을 Z -145~-118 로 밀어 join.
#   - 가로 뿌리 2(리브 윗면 Z -118·밑면 Z -145 – 원통 r30): 반경면 단면(R2 호)을 기둥 축 둘레로 돌린 띠(원환)를
#     리브 바닥 모양(리브 + 세로 뿌리)으로 잘라(intersect) join.
# 좌표는 세계 대기(J_MAT_X 0, J_MAT_Y -700, ROT 0, 링 0), 기둥 축 (0, -700), 겉 r30, mm.
# 쓰는 법: python -B tools/gen_t17_mech_r1.py -> tools/out/mech_T17/model/stage_g.json, stage_h.json (MCP batch)
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T17', 'model')
os.makedirs(OUT, exist_ok=True)
POST = "P_T01_POST"
CY = -700.0
R0, RF, HW = 30.0, 2.0, 5.25        # 기둥 겉 반지름, 뿌리 R, 리브 반폭
ZB, ZT = -145.0, -118.0             # 리브 밑·윗면
STAGES = {}
S = None


def stage(n):
    global S
    S = STAGES.setdefault(n, [])


def C(c, p):
    S.append({"command": c, "params": p})


def r(v):
    return round(v, 4)


# 세로 뿌리 R2 중심: X = HW + RF, 축에서 R0 + RF
cx = HW + RF
cyo = math.sqrt((R0 + RF) ** 2 - cx ** 2)          # 축에서 -Y 방향 거리
CF = (cx, CY - cyo)                                 # (7.25, -731.1679)
T1 = (HW, CF[1])                                    # 리브 옆면 접점
k = R0 / (R0 + RF)
T2 = (cx * k, CY - cyo * k)                         # 원통 접점
# 호 가운데 점: 중심에서 (리브 옆면–원통 모서리 쪽) 이등분 방향
ang1 = math.atan2(T1[1] - CF[1], T1[0] - CF[0])
ang2 = math.atan2(T2[1] - CF[1], T2[0] - CF[0])
am = (ang1 + ang2) / 2
MID = (CF[0] + RF * math.cos(am), CF[1] + RF * math.sin(am))


def flare(s):
    # s = +1 (+X), -1 (-X). 몸통 쪽으로 0.25~0.4 겹쳐 둔다(불 연산 안정)
    P = lambda p: [r(s * p[0]), r(p[1])]
    return [P(T1), P((HW - 0.25, T1[1])), P((HW - 0.25, -729.0)), P((6.6, -728.8)), P(T2)], P(MID)


# ---------------------------------------------------------------------------
# g: 세로 뿌리 2
stage('g')
C("component.activate", {"component": "MAT_ROT"})
C("sketch.create", {"plane": {"origin": [0, 0, ZB], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": "SK_T17_RIBROOT_V"})
for s in (1, -1):
    pts, mid = flare(s)
    C("sketch.line", {"points": pts, "closed": False})
    C("sketch.arc.three_point", {"start": pts[-1], "end": pts[0], "through": mid})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_T17_RIBROOT_V", "profiles": "all", "distance": ZT - ZB, "operation": "join", "targets": [POST]})

# ---------------------------------------------------------------------------
# h: 가로 뿌리 2(위·아래) — 원환 띠를 리브 바닥 모양으로 잘라 join
stage('h')
# 실제 세션에서 통한 순서(불 연산이 순서·자르개 크기에 민감했다, 보고서 2절):
#   밑 뿌리: 자르개를 0.02 안으로 줄인 것(5.23 / R2.02)으로 intersect.  위 뿌리: 자르개 그대로(5.25 / R2)로 intersect.
#   join 은 위 → 밑 순서. (밑 5.25 자르개 join 실패, 위 5.23 자르개 join 실패, 위를 밑 다음에 join 실패 — 모두 'no result')
C("component.activate", {"component": "MAT_ROT"})
RP = {"origin": [0, CY, 0], "x_dir": [0, -1, 0], "y_dir": [0, 0, 1]}     # 반경면 θ270: u = 반지름(세계 -Y), v = 세계 Z


def torus_profile(nm, zf, sg):
    zc = zf + sg * RF
    ta = [R0, r(zc)]
    tb = [R0 + RF, zf]
    mid = [r(R0 + RF - RF / math.sqrt(2)), r(zc - sg * RF / math.sqrt(2))]
    poly = [tb, [R0 + RF, r(zf - sg * 0.4)], [R0 - 0.4, r(zf - sg * 0.4)], [R0 - 0.4, r(zc)], ta]
    sk = "SK_T17_RIBROOT_%s" % nm
    C("sketch.create", {"plane": RP, "name": sk})
    C("sketch.line", {"points": poly, "closed": False})
    C("sketch.arc.three_point", {"start": ta, "end": tb, "through": mid})
    C("sketch.finish", {})
    C("solid.revolve", {"sketch": sk, "profiles": "all", "axis": "y", "angle": "30 deg", "direction": "symmetric",
                        "operation": "new", "body_name": "T17_RR_%s" % nm})


def clip_sketch(sk, z0, eps):
    # 리브 바닥 모양(리브 + 세로 뿌리 R2)을 eps 만큼 안으로 줄인 자르개. 축 쪽은 원통 안(y -722)으로.
    xa, ra = HW - eps, RF + eps
    ua = ((T2[0] - CF[0]) / RF, (T2[1] - CF[1]) / RF)
    um = ((MID[0] - CF[0]) / RF, (MID[1] - CF[1]) / RF)
    E2 = (CF[0] + ra * ua[0], CF[1] + ra * ua[1])
    M2 = (CF[0] + ra * um[0], CF[1] + ra * um[1])
    A = lambda s, q: [r(s * q[0]), r(q[1])]
    C("sketch.create", {"plane": {"origin": [0, 0, z0], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": sk})
    C("sketch.line", {"points": [A(-1, (xa, CF[1])), [-xa, -760], [xa, -760], A(1, (xa, CF[1]))], "closed": False})
    C("sketch.arc.three_point", {"start": A(1, (xa, CF[1])), "end": A(1, E2), "through": A(1, M2)})
    C("sketch.line", {"points": [A(1, E2), [r(E2[0]), -722], [r(-E2[0]), -722], A(-1, E2)], "closed": False})
    C("sketch.arc.three_point", {"start": A(-1, E2), "end": A(-1, (xa, CF[1])), "through": A(-1, M2)})
    C("sketch.finish", {})


# 밑 뿌리(Z -145): 원환 띠 -> 줄인 자르개(0.02)로 intersect
torus_profile("BOT", ZB, -1)
clip_sketch("SK_T17_RIBROOT_CLIP", ZB - 3, 0.02)
C("solid.extrude", {"sketch": "SK_T17_RIBROOT_CLIP", "profiles": "all", "distance": 33.0, "operation": "new", "body_name": "T17_RR_CLIP_BOT"})
C("solid.combine", {"target": "T17_RR_BOT", "tools": ["T17_RR_CLIP_BOT"], "operation": "intersect", "keep_tools": False})
# 위 뿌리(Z -118): 원환 띠 -> 자르개 그대로(0)로 intersect
torus_profile("TOP", ZT, 1)
clip_sketch("SK_T17_RIBROOT_CLIP_T", ZT - 3, 0.0)
C("solid.extrude", {"sketch": "SK_T17_RIBROOT_CLIP_T", "profiles": "all", "distance": 6.0, "operation": "new", "body_name": "T17_RR_CLIP_TOP"})
C("solid.combine", {"target": "T17_RR_TOP", "tools": ["T17_RR_CLIP_TOP"], "operation": "intersect", "keep_tools": False})
# join: 위 -> 밑
C("solid.combine", {"target": POST, "tools": ["T17_RR_TOP"], "operation": "join", "keep_tools": False})
C("solid.combine", {"target": POST, "tools": ["T17_RR_BOT"], "operation": "join", "keep_tools": False})

stage('i')
C("component.activate", {"component": "root"})
C("component.rename", {"component": "root", "name": "FSAP_v0.8.6"})
C("document.metadata.set", {"values": {"description": "T17 rev1: post theta270 rib root R2 (cylinder-plane) built as exact blend geometry joined to P_T01_POST (vertical x2 extruded, top/bottom x2 revolved and clipped)"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})

if __name__ == '__main__':
    for n in sorted(STAGES):
        json.dump(STAGES[n], open(os.path.join(OUT, 'stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print(n, len(STAGES[n]))
    allc = [c for n in sorted(STAGES) for c in STAGES[n]]
    json.dump(allc, open(os.path.join(ROOT, 'tools', 'out', 'mech_T17', 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('CF', CF, 'T1', T1, 'T2', T2, 'MID', MID)
