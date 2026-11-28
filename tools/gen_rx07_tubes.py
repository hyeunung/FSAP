# RX-07 U5_A 관을 U5_A1(밸브 2 A -> IR1000 :2 IN) + U5_A2(:2 OUT -> 기존 U5_A 체인 길)로 나누는 명령 생성기
# 출력: tools/out/mech_RX-07/stage_2_tubes.json
import json, math, os

R = 30.0
OUT = os.path.join(os.path.dirname(__file__), 'out', 'mech_RX-07')
ZE = 483.9  # 엘보 관 구멍 바닥(483.4)보다 0.5 위, 관 끝(496.7)에서 12.8 삽입


def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b): return [a[i] + b[i] for i in range(3)]
def mul(a, s): return [a[i] * s for i in range(3)]
def norm(a):
    l = math.sqrt(sum(x * x for x in a)); return [x / l for x in a]
def rnd(p): return [round(x, 4) for x in p]


def fillet_path(pts):
    """꺾은선 -> 직선/호(R30) 목록. 직선 길이 0은 넣지 않는다."""
    segs = []
    cur = pts[0]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        u = norm(sub(a, b)); v = norm(sub(c, b))
        t1 = add(b, mul(u, R)); t2 = add(b, mul(v, R))
        bis = norm(add(u, v))
        # 90도 꺾임: 중심은 b + bis*R*sqrt2, 호 중간점 = 중심 - bis*R
        cos_t = sum(u[k] * v[k] for k in range(3))
        half = math.acos(max(-1, min(1, cos_t))) / 2
        dc = R / math.sin(half)
        cen = add(b, mul(bis, dc))
        mid = sub(cen, mul(bis, R))
        if math.dist(cur, t1) > 1e-6:
            segs.append(('line', rnd(cur), rnd(t1)))
        segs.append(('arc', rnd(t1), rnd(mid), rnd(t2)))
        cur = t2
    if math.dist(cur, pts[-1]) > 1e-6:
        segs.append(('line', rnd(cur), rnd(pts[-1])))
    return segs


def arc_from_center(start, end, center):
    # 평면 Y=190 안의 작은 호/반원 호: 중간점 = 중심 + R*정규(시작+끝 - 2중심)
    r = math.dist(start, center)
    m = norm(sub(add(start, end), mul(center, 2)))
    return ('arc', rnd(start), rnd(add(center, mul(m, r))), rnd(end))


A1 = [(1060.25, 63, 331.4), (1060.25, 63, 286.4), (1060.25, 3, 286.4), (1060.25, 3, 600),
      (772.06, 3, 600), (772.06, 95, 600), (772.06, 95, ZE)]
A2 = [(827.94, 95, ZE), (827.94, 95, 690), (827.94, 190, 690), (-958.45, 190, 690)]

segA1 = fillet_path([list(p) for p in A1])
segA2 = fillet_path([list(p) for p in A2])
# 기존 U5_A 체인 쪽 끝(w9~w15) 그대로
segA2.append(arc_from_center([-958.45, 190, 690], [-961.54, 190, 689.84], [-958.4568649517696, 190, 660.2147668810454]))
segA2.append(('line', [-961.54, 190, 689.84], [-1238.46, 190, 661.16]))
segA2.append(arc_from_center([-1238.46, 190, 661.16], [-1241.55, 190, 661.0], [-1241.5431350482304, 190, 690.7852331189546]))
segA2.append(('line', [-1241.55, 190, 661.0], [-1276.0, 190, 661.0]))
# U자(반원)는 기존처럼 90도 호 두 개: 중간점은 꼭짓점 쪽 45도
c1 = [-1275.9890579710145, 220.01094202898543, 661.0]
r1 = math.dist([-1276.0, 190, 661], c1)
segA2.append(('arc', [-1276.0, 190, 661.0], rnd(add(c1, mul(norm([-1, -1, 0]), r1))), [-1306.0, 220.0, 661.0]))
c2 = [-1275.9890579710145, 219.98905797101457, 661.0]
segA2.append(('arc', [-1306.0, 220.0, 661.0], rnd(add(c2, mul(norm([-1, 1, 0]), r1))), [-1276.0, 250.0, 661.0]))
segA2.append(('line', [-1276.0, 250.0, 661.0], [-1222.5, 250.0, 661.0]))


def tube_cmds(name, segs, desc):
    sk = 'SK_' + name
    cmds = [{"command": "sketch.create", "params": {"plane": "XY", "name": sk}},
            {"command": "sketch.options", "params": {"sketch_3d": True}}]
    for s in segs:
        if s[0] == 'line':
            cmds.append({"command": "sketch.line3d", "params": {"points": [s[1], s[2]]}})
        else:
            cmds.append({"command": "sketch.arc3d", "params": {"start": s[1], "through": s[2], "end": s[3]}})
    cmds.append({"command": "sketch.finish", "params": {}})
    cmds.append({"command": "solid.pipe", "params": {"path_sketch": sk, "path": ["w%d" % (i + 1) for i in range(len(segs))],
                                                     "diameter": 6.0, "operation": "new", "body_name": name, "name": "PIPE_" + name}})
    cmds.append({"command": "material.assign", "params": {"bodies": [name], "material": "Default"}})
    cmds.append({"command": "component.create", "params": {"name": name, "parent": "U8_PNEU", "activate": False}})
    cmds.append({"command": "component.move_bodies", "params": {"bodies": [name], "component": name}})
    cmds.append({"command": "component.metadata.set", "params": {"component": name, "part_number": "TU0604", "bom_type": "purchased", "description": desc}})
    return cmds


cmds = [{"command": "timeline.delete", "params": {"features": ["Pipe67", "SK_TU0604_M08P_U5_A"]}},
        {"command": "component.delete", "params": {"component": "TU0604_M08P_U5_A"}},
        {"command": "component.activate", "params": {"component": "root"}}]
cmds += tube_cmds("TU0604_M08P_U5_A1", segA1, "SMC TU0604 OD6, RX-07 valve 2 A (U5 lift head = down) -> IR1000 :2 IN (KQ2L06-01AS_M08R_IN_2)")
cmds += tube_cmds("TU0604_M08P_U5_A2", segA2, "SMC TU0604 OD6, RX-07 IR1000 :2 OUT (KQ2L06-01AS_M08R_OUT_2) -> existing U5_A route (beam top Y190 Z690) -> U5C_1 chain")

json.dump(cmds, open(os.path.join(OUT, 'stage_2_tubes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
L = lambda segs: sum(math.dist(s[1], s[2]) if s[0] == 'line' else 0 for s in segs)
print('A1 segs', len(segA1), 'A2 segs', len(segA2), 'cmds', len(cmds))
for s in segA1: print('A1', s)
for s in segA2[:6]: print('A2', s)
