# -*- coding: utf-8 -*-
"""M02R U4 누운 실린더 + 핀 축 크랭크 생성기 — v2.10.1 -> v2.10.2 (모델링부 2026-11-11)
설계안 docs/reports/mechanism/mech_M02R_design.md(v2.10.1 기준). 좌표: 바늘점 원점, J_U4_PRESS 0(θ0) 세계 좌표.
python -X utf8 -B tools/gen_v2_m02r.py -> tools/out/mech_M02R/model/stage_*.json, routes.json
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(ROOT).replace("\\", "/")
OUT = os.path.join(ROOT, "out", "mech_M02R", "model")
STEP = PRJ + "/purchased-step/"
sys.path.insert(0, ROOT)
from gen_v2_pneu01 import tube_cmds, length, C, r4, box, cyl, cross, norm, sub, addv, dot  # noqa: E402

# ---------------------------------------------------------------- 기하
PIV = (-300.0, 70.0)
F = [-161.006, 0.0, 225.0]          # 고정 클레비스 핀
C0 = [-347.8, 0.0, 203.6]           # 크랭크 핀 θ0
POLD = [-161.006, 0.0, 325.72]      # 옛 클레비스 핀(REST)
DOLD = norm([-0.045649646316104076, 0.0, -0.9989575115044756])
DNEW = norm(sub(C0, F))
L0 = math.dist(F, C0)
L_RET = 183.5
EXT0 = L0 - L_RET


def mv(R, v):
    return [sum(R[i][j] * v[j] for j in range(3)) for i in range(3)]


A = [-v for v in DOLD]; N = [A[2], 0.0, -A[0]]; E3 = cross(A, N)
An = [-v for v in DNEW]; Nn = [0.0, 1.0, 0.0]; F3 = cross(An, Nn)
R = [[An[i] * A[j] + Nn[i] * N[j] + F3[i] * E3[j] for j in range(3)] for i in range(3)]
_t = [F[i] - mv(R, POLD)[i] for i in range(3)]
M = [R[0][0], R[0][1], R[0][2], _t[0], R[1][0], R[1][1], R[1][2], _t[1], R[2][0], R[2][1], R[2][2], _t[2]]
M = [round(v, 10) for v in M]


def xf(p):
    return [mv(R, p)[i] + _t[i] for i in range(3)]


def rotp(p, th):
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    dx, dz = p[0] - PIV[0], p[1] - PIV[1]
    return (PIV[0] + dx * c - dz * s, PIV[1] + dx * s + dz * c)


def ext(th):
    q = rotp((C0[0], C0[2]), th)
    return math.hypot(F[0] - q[0], F[2] - q[1]) - L_RET


# 실린더 포트(REST 옛 위치, mech_M08 fix1 실측) -> 새 자리. 피팅: lx = 소켓 방향, ly = 포트 바깥 법선
PORT_OLD = {"1": [-150.76, 0.0, 287.21], "2": [-153.99, 0.0, 216.28]}   # 1 = 머리 쪽(B), 2 = 로드 쪽(A)
PORT = {k: xf(p) for k, p in PORT_OLD.items()}
LX = [-v for v in F3]               # 180° 돌린 뒤 소켓 방향(아래, 실린더 축에 수직)
OUTLET = {k: [p[i] + 15.5 * LX[i] + 14.2 * Nn[i] for i in range(3)] for k, p in PORT.items()}

J_A = [-161.006, 94.0, 225.0]
J_B = [-161.006, 70.0, 225.0]


def below(o, z):
    """소켓 축 위, 높이 z인 점(관이 소켓으로 들어가기 전 곧은 구간 시작)."""
    L = (o[2] - z) / (-LX[2])
    return [o[i] + L * LX[i] for i in range(3)]


ROUTES = {}


def tube(name, pts, Rl, parent, r=3.0, pn="TU0604", note="", reuse=None):
    ROUTES[name] = {"pts": [[r4(v) for v in p] for p in pts], "R": Rl, "r": r, "parent": parent, "len": round(length(pts, Rl), 1),
                    "pn": pn, "note": note}
    if reuse:
        s = [C("solid.remove", bodies=[reuse])]
        if reuse != name:
            s.append(C("component.rename", component=reuse, name=name))
    else:
        s = [C("component.create", name=name, parent=parent, activate=False)]
    tc = tube_cmds(name, pts, Rl, r)
    for c in tc:   # 옛 관 스케치 이름과 겹치지 않게(같은 이름이면 solid.pipe가 옛 스케치를 잡는다)
        if c["command"] == "sketch.create":
            c["params"]["name"] = "SK_%s_M02R" % name
        if c["command"] == "solid.pipe":
            c["params"]["path_sketch"] = "SK_%s_M02R" % name
    s += tc
    s += [C("material.assign", bodies=[name], material="Default"),
          C("component.move_bodies", bodies=[name], component=name),
          C("component.metadata.set", component=name, part_number=pn, bom_type="purchased",
            description="SMC %s polyurethane tube OD%d, cut to length (M02R route, bends R>=%s)" % (pn, int(2 * r), min(Rl)))]
    return s


def mat_loc(cols, t):
    return [round(v, 9) for i in range(3) for v in (cols[0][i], cols[1][i], cols[2][i], t[i])]


def bolt_cols(a):
    ref = (0, 0, 1) if abs(a[2]) < 0.5 else (1, 0, 0)
    y = (ref[1] * a[2] - ref[2] * a[1], ref[2] * a[0] - ref[0] * a[2], ref[0] * a[1] - ref[1] * a[0])
    z = (a[1] * y[2] - a[2] * y[1], a[2] * y[0] - a[0] * y[2], a[0] * y[1] - a[1] * y[0])
    return [a, y, z]


def bolt(nm, pn, d, at):
    return [C("file.insert_step", path=STEP + "%s/%s.stp" % (pn, pn), name=nm, matrix=mat_loc(bolt_cols(d), at)),
            C("body.rename", body="Cut-Extrude1", name=nm),
            C("component.metadata.set", component=nm, part_number=pn, bom_type="purchased"),
            C("material.assign", bodies=[nm], material="SCM435")]


def cy(r, x, z, y0, y1, op, tg=None, name=None):
    return cyl(r, [x, y0, z], y1 - y0, [0, 1, 0], op, tg, name)


def cz(r, x, y, z0, z1, op, tg=None, name=None):
    return cyl(r, [x, y, z0], z1 - z0, [0, 0, 1], op, tg, name)


def cx(r, y, z, x0, x1, op, tg=None, name=None):
    return cyl(r, [x0, y, z], x1 - x0, [1, 0, 0], op, tg, name)


# ---------------------------------------------------------------- 단계
def stage_move():
    """실린더 묶음 나머지 옮김 + 클레비스 핀 묶음 Z -100.72 + 피팅 180° (U4_CYL:1은 stage_0에서 옮김)."""
    s = [C("occurrence.move", occurrence=o, space="world", matrix=M, tolerance=1e-6)
         for o in ("U4_CYL_CLEVIS:1", "U4_ROD:1", "U4_ROD_NUT:1", "I-020B_M02:1")]
    dz = F[2] - POLD[2]
    s += [C("solid.move", bodies=["P_M02_CLEVIS_PIN", "P_M02_CLEVIS_WASHER"], translate=[0, 0, r4(dz)]),
          C("occurrence.move", occurrence="CB4-12_M02_CLV:1", space="world", translate=[0, 0, r4(dz)])]
    for k in ("1", "2"):
        s.append(C("occurrence.move", occurrence="KQ2L06-01AS_M08_U4_%s:1" % k, space="world", axis=[0, 1, 0], angle=math.pi,
                   origin=[r4(v) for v in PORT[k]]))
    return s


BRK = "P_M02R_CYLBRKT"
BOLT_BRK = [(-175, 20), (-175, -20), (-149, 20), (-149, -20)]


def stage_bracket():
    s = [C("solid.remove", bodies=["P_M02_CYLBRKT", "CB5-12_M02_1", "CB5-12_M02_2"])]   # 빈 컴포넌트는 stage_cleanup 한 번에
    # 날개 + 귀 2(옛 귀 안 틈 ±15.5 그대로, 귀 t4 — 기존 클레비스 핀 머리 Y -21.5·와셔 19.5~21.5가 귀 밖에 남게)
    s += [box(BRK, -183, -141, -28, 28, 234, 242),
          box(None, -175, -147, 15.5, 19.5, 214, 234.5, "join", [BRK]),
          box(None, -175, -147, -19.5, -15.5, 214, 234.5, "join", [BRK]),
          box(None, -176, -146, -15.5, 15.5, 233.9, 237, "cut", [BRK]),      # 눈 위 틈(위 Z 237)
          box(None, -185, -176, -15.5, 15.5, 233.9, 237, "cut", [BRK]),      # -X 쪽으로 엶(클레비스 사각 끝 Z 235.3)
          cy(4.0, F[0], F[2], -29, 29, "cut", [BRK])]                       # 핀 구멍 Ø8
    s += [cz(2.1, x, y, 233.9, 242.1, "cut", [BRK]) for (x, y) in BOLT_BRK]  # M5 탭 t8
    s += [C("material.assign", bodies=[BRK], material="SUS304"),
          C("component.move_bodies", bodies=[BRK], component="U4_WHEEL_N")]
    # BASE 윗판: 볼트 Ø5.5 ×4, 관 Ø8 ×2
    s += [cz(2.75, x, y, 241.9, 250.1, "cut", ["P_M02_BASE"]) for (x, y) in BOLT_BRK]
    s += [cz(4.0, J[0], J[1], 241.9, 250.1, "cut", ["P_M02_BASE"]) for J in (J_A, J_B)]
    for i, (x, y) in enumerate(BOLT_BRK, 1):
        s += bolt("CB5-16_M02R_%d" % i, "CB5-16", (0, 0, -1), (x, y, 250))
    s.append(C("joint.rigid_group", occurrences=["U4_WHEEL_N:1", "CB4-12_M02R_CLV:1"] + ["CB5-16_M02R_%d:1" % i for i in range(1, 5)]))
    return s


def stage_base_fill():
    """옛 브래킷 자리 정리(빈 구멍 0): 옛 통과 장공 34x30, 옛 M5 탭 2 메움."""
    return [box(None, -179, -145, -15, 15, 242, 250, "join", ["P_M02_BASE"]),
            cz(2.1, -176, 24, 242, 250, "join", ["P_M02_BASE"]),
            cz(2.1, -148, -24, 242, 250, "join", ["P_M02_BASE"])]


CRK, PIN, WSH = "P_M02R_CRANK", "P_M02R_CRANK_PIN", "P_M02R_CRANK_WASHER"
BOLT_CRK = [(-270, 0), (-260, 0)]


def stage_crank():
    s = [C("solid.remove", bodies=["P_M02_KNUCKLE_PIN", "P_M02_KNUCKLE_SPACER_N", "P_M02_KNUCKLE_SPACER_P", "P_M02_KNUCKLE_WASHER",
                                   "CB4-12_M02_KNK"])]
    # 패드(두 팔 사이, 팔 안쪽 면에 0.1 겹침) + 팔 2(XZ 장공 폭 20, t8)
    s += [box(CRK, -275, -255, -10.6, 10.6, 121, 131)]
    for nm, y0 in (("SK_M02R_CRANK_P", 18.5), ("SK_M02R_CRANK_N", -10.5)):
        s += [C("sketch.create", plane={"origin": [0, y0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name=nm),
              C("sketch.slot.center_to_center", p0=[-265, 126], p1=[C0[0], C0[2]], width=20),
              C("sketch.finish"),
              C("solid.extrude", sketch=nm, distance=8, operation="join", targets=[CRK], name=nm.replace("SK_", "EX_"))]
    s += [box(None, -290, -240, -20, 20, 100, 121, "cut", [CRK]),            # 패드 밑면 Z 121 아래 팔 끝 잘라냄
          cy(4.05, C0[0], C0[2], -19, 19, "cut", [CRK])]                    # 핀 구멍 Ø8.1
    s += [cz(2.75, x, y, 120.9, 131.1, "cut", [CRK]) for (x, y) in BOLT_CRK]
    s += [cz(2.1, x, y, 109, 121.1, "cut", ["P_M02_ARM_TIE"]) for (x, y) in BOLT_CRK]   # M5 탭 깊이 12
    # 핀(머리 Ø14x2 + 축 Ø8, +Y 끝 M4 탭 10), 와셔 Ø14 t2
    s += [cy(7.0, C0[0], C0[2], -20.5, -18.5, "new", name=PIN),
          cy(4.0, C0[0], C0[2], -18.6, 18.5, "join", [PIN]),
          cy(1.65, C0[0], C0[2], 8.5, 18.6, "cut", [PIN]),
          cy(7.0, C0[0], C0[2], 18.5, 20.5, "new", name=WSH),
          cy(2.25, C0[0], C0[2], 18.4, 20.6, "cut", [WSH])]
    s += [C("material.assign", bodies=[CRK], material="A5052"),
          C("material.assign", bodies=[PIN], material="S45C"),
          C("material.assign", bodies=[WSH], material="SUS304"),
          C("component.move_bodies", bodies=[CRK, PIN, WSH], component="U4_PRESS")]
    for i, (x, y) in enumerate(BOLT_CRK, 1):
        s += bolt("CB5-20_M02R_%d" % i, "CB5-20", (0, 0, -1), (x, y, 131))
    s += bolt("CB4-12_M02R_CRK", "CB4-12", (0, -1, 0), (C0[0], 20.5, C0[2]))
    s.append(C("joint.rigid_group", occurrences=["U4_PRESS:1", "CB4-12_M02R_CRK:1", "CB5-20_M02R_1:1", "CB5-20_M02R_2:1"]))
    return s


def stage_arm_fill():
    """옛 너클 핀 구멍 Ø9 (−160, 122) 메움(빈 구멍 0)."""
    return [cy(4.5, -160, 122, -37, -31, "join", ["P_M02_ARM_SIDE_N"]),
            cy(4.5, -160, 122, 31, 37, "join", ["P_M02_ARM_SIDE_P"])]


def stage_joints():
    return [C("joint.as_built", type="revolute", name="J_U4_CYL_PIN", a="U4_WHEEL_N:1", b="U4_CYL:1",
              at={"occurrence": "U4_WHEEL_N:1", "point": F, "z": [0, 1, 0]}, limits=[[-15, 15]], quiet=True),
            C("joint.as_built", type="slider", name="J_U4_CYL_ROD", a="U4_CYL:1", b="U4_ROD:1",
              at={"occurrence": "U4_CYL:1", "point": F, "z": [r4(v) for v in DNEW]}, limits=[[-0.01, 25]], quiet=True),
            C("joint.drive", joint="J_U4_CYL_ROD", value=round(EXT0, 4), quiet=True),
            C("joint.as_built", type="revolute", name="J_U4_ROD_PIN", a="U4_ROD:1", b="U4_PRESS:1",
              at={"occurrence": "U4_PRESS:1", "point": C0, "z": [0, 1, 0]}, quiet=True)]


def stage_u4c():
    s = []
    qb = below(OUTLET["1"], 175.0)
    s += tube("TU0604_M08P_U4C_B", [J_B, [J_B[0], J_B[1], 175.0], qb, OUTLET["1"]], [25, 25], "U4_CYL",
              note="J_B(핀 축, 밸브 B) -> 머리 쪽 포트 피팅")
    qa = below(OUTLET["2"], 168.0)
    s += tube("TU0604_M08P_U4C_A", [J_A, [J_A[0], J_A[1], 168.0], qa, OUTLET["2"]], [25, 25], "U4_CYL",
              note="J_A(핀 축, IR 감압) -> 로드 쪽 포트 피팅")
    return s


def stage_u8():
    s = []
    # IR(U4) IN 엘보 KQ2L06-01AS (OUT_1을 Z축 (700, 95) 둘레 180°)
    lx, ly = [0, 0, -1], [-1, 0, 0]
    lz = cross(lx, ly)
    p = [686.26, 95.0, 481.2]
    comp = "KQ2L06-01AS_M08R_IN_1"
    s += [C("file.insert_step", path=STEP + "KQ2L06-01AS/KQ2L06-01AS.stp", name=comp,
            matrix=[r4(v) for i in range(3) for v in (lx[i], ly[i], lz[i], p[i])]),
          C("body.rename", body="KQ2L06-01AS", name=comp),
          C("component.metadata.set", component=comp, part_number="KQ2L06-01AS", bom_type="purchased",
            description="SMC KQ2L06-01AS elbow R1/8-OD6 on IR1000 (U4) IN (M02R, was KQ2L08-01AS)"),
          C("material.assign", bodies=[comp], material="Default"),
          C("occurrence.reparent", occurrence=comp + ":1", parent="U8_PNEU"),
          C("joint.rigid_group", occurrences=["U8_PNEU:1", comp + ":1"])]
    # STEP대기_KQ2R06-08A_2 (E-10 임시: 몸 Ø12.8 x 19, 줄기 Ø8은 티 안)
    tw = "STEP대기_KQ2R06-08A_2"
    s += [C("component.create", name=tw, parent="U8_PNEU", activate=False),
          cx(6.4, 108, 280, 833.9, 852.9, "new", name=tw),
          C("material.assign", bodies=[tw], material="Default"),
          C("component.move_bodies", bodies=[tw], component=tw),
          C("component.metadata.set", component=tw, part_number="KQ2R06-08A", bom_type="purchased",
            description="SMC KQ2R06-08A plug-in reducer OD6 tube - OD8 stem (STEP pending, E-10 placeholder D 12.8 x 19)")]
    # 관
    s += tube("TU0604_M08P_U4_A1", [[1049.75, 53, 331.4], [1049.75, 53, 286.4], [1049.75, -7, 286.4], [1049.75, -7, 440],
                                     [980, 110, 440], [780, 110, 440], [755, 95, 440], [715, 95, 400], [672.06, 95, 400],
                                     [672.06, 95, 465.7]], [30, 30, 30, 30, 30, 30, 30, 25], "U8_PNEU",
              note="밸브 1 A -> IR1000(U4) IN", reuse="TU0604_M08P_U4_A")
    s += tube("TU0604_M08P_U4_A2", [[727.94, 95, 465.7], [727.94, 95, 440], [700, 110, 440], [-174.9, 110, 440],
                                     [-174.9, 100, 312], [-161.006, 94, 290.4], J_A], [16, 30, 30, 30, 30], "U8_PNEU",
              note="IR1000(U4) OUT -> J_A(핀 축, 로드 쪽)", reuse="TU0805_M08P_MAIN_3")
    s += tube("TU0604_M08P_U4_B", [[1049.75, 53, 370.6], [1049.75, 53, 430], [1000, 110, 430], [-125, 110, 430],
                                    [-161.006, 100, 430], [-161.006, 100, 312], [-161.006, 70, 293.25], J_B], [30, 30, 30, 30, 30, 30],
              "U8_PNEU", note="밸브 1 B -> J_B(핀 축, 머리 쪽)", reuse="TU0604_M08P_U4_B")
    s += tube("TU0604_M08P_REG1_SUP", [[833.9, 108, 280], [760, 108, 280], [760, 108, 350], [729.1, 82, 350], [729.1, 82, 240],
                                        [960, 82, 240], [1010, 95, 240], [1049.75, 95, 240], [1049.75, 95, 285]],
              [20, 20, 20, 30, 30, 30, 30], "U8_PNEU", note="티2 서 -> KQ2R06-08A -> 스페이서 1 SUP(주 공급)", reuse="TU0604_M08P_REG1_OUT")
    # 클램프 F_6 (F_2와 같은 형상: 24x18x50, 관 구멍 r3.25 x2, CB5-16 자리 x2)
    f6 = "P_M08_TUBE_CLAMP_F_6"
    s += [box(f6, 788, 812, 102, 120, 420, 470),
          cx(3.25, 110, 440, 787, 813, "cut", [f6]),
          cx(3.25, 110, 430, 787, 813, "cut", [f6])]
    for x in (794, 806):
        s += [cyl(2.75, [x, 111.5, 462], 9.0, [0, 1, 0], "cut", [f6]),
              cyl(4.75, [x, 101.5, 462], 10.5, [0, 1, 0], "cut", [f6]),
              C("occurrence.copy", occurrence="CB5-16_M08_PY:4", parent="U8_PNEU", in_place=True, translate=[x - 1170, 2, 112]),
              cyl(2.1, [x, 120, 462], 10, [0, 1, 0], "cut", ["P_M07_BEAM"])]
    s += [C("material.assign", bodies=[f6], material="A5052"),
          C("component.create", name=f6, parent="U8_PNEU", activate=False),
          C("component.move_bodies", bodies=[f6], component=f6),
          C("component.metadata.set", component=f6, part_number=f6, bom_type="normal",
            description="Tube clamp block on beam front, A5052 milled, 2 tube holes, 2x CB5-16 counterbored (M02R, same as F_2)")]
    return s


def stage_l2():
    """L_2 MAIN 구멍 (800,108,280) r4.25 -> r3.25 (REG1_SUP Ø6)."""
    return [cx(4.3, 108, 280, 788.5, 811.5, "join", ["P_M08_TUBE_CLAMP_L_2"]),
            cx(3.25, 108, 280, 787, 813, "cut", ["P_M08_TUBE_CLAMP_L_2"])]


def main():
    os.makedirs(OUT, exist_ok=True)
    st = {"1_move": stage_move(), "2_bracket": stage_bracket(), "2b_basefill": stage_base_fill(), "3_crank": stage_crank(),
          "3b_armfill": stage_arm_fill(), "4_joints": stage_joints(), "5_u4c": stage_u4c(), "6_u8": stage_u8(), "6b_l2": stage_l2()}
    for k, v in st.items():
        json.dump(v, open(os.path.join(OUT, "stage_%s.json" % k), "w", encoding="utf8"), ensure_ascii=False, indent=0)
    info = {"M": M, "EXT0": EXT0, "L0": L0, "DNEW": DNEW, "PORT": PORT, "OUTLET": OUTLET, "LX": LX,
            "ext": {th: round(ext(th), 4) for th in (-1.867, -0.54, 0.0, 2.4289, 8.626)}, "routes": ROUTES}
    json.dump(info, open(os.path.join(OUT, "geom_m02r.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: len(v) for k, v in st.items()}))
    print("EXT0", round(EXT0, 4), "ext", info["ext"])
    print("PORT", {k: [r4(x) for x in v] for k, v in PORT.items()})
    print("OUTLET", {k: [r4(x) for x in v] for k, v in OUTLET.items()})
    for n, r in ROUTES.items():
        print(n, r["len"], r["R"])


if __name__ == "__main__":
    main()
