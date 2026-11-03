# -*- coding: utf-8 -*-
"""DC-07 X 편구동 요 반력 생성기 — v1.0.16 -> v1.0.17 (모델링부 2026-11-03, 엔진 v3.7.2)
선정 지시서 docs/reports/mechanism/mech_DC-07_select.md(DC-07-S)를 그린다.
python -B tools/gen_v1_dc07.py -> tools/out/mech_DC-07/model/stage_*.json (MCP batch로 차례로 보냄), edit.json, edit_meta.json
좌표: 바늘점 원점 월드 mm, J_U4_X 0(REST)에서 그린다.
- 보(U4_X_BEAM) 구멍·턱은 보를 U4_X로 옮기는 BodyTransfer25 앞(Cylinder89 뒤)에 넣는다(N02·DC-05 메모: 옮긴 뒤 자르면 월드 고정).
- 카운터보어는 메우지 않고 원래 피처 Cylinder72~87의 base X를 고친다(U-10).
- 블록 occurrence 560·561(레일 A), 571·572(레일 B), 볼트 CB5-20_N03XB:1~8 은 월드 평행 이동.
- 멈춤나사 STEP대기_MSSF5-10_1~6(E-10 임시 형상)은 끝에서 만들고 U4_X로 옮긴다.
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "mech_DC-07")
BEAM = "U4_X_BEAM"
DX1, DX2 = -65.0, 55.0          # 블록 1(-935 -> -1000), 블록 2(-865 -> -810)
SS = "STEP대기_MSSF5-10"
SS_X = [-1012.0, -1000.0, -988.0, -822.0, -810.0, -798.0]
SS_Z = -360.0


def C(cmd, **p):
    return {"command": cmd, "params": p}


def box(x0, x1, y0, y1, z0, z1, op, tg):
    return C("solid.box", length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4),
             corner=[x0, y0, z0], operation=op, targets=tg)


# Cylinder72~87: XB_HOLES 순서 (y, 블록, s) 마다 [카운터보어 Ø9.5 base -340, 관통 Ø5.5 base -353]
def holes():
    out = []
    for y in (-960.0, 960.0):
        for xb in (-993.5, -816.5):
            for s in (-16.0, 16.0):
                out.append((xb, y + s))
    return out


def stage_beam():
    """실제 보낸 순서: 턱·탭을 Cylinder89 뒤에 넣고(1번 batch), 카운터보어 16피처 고침(2번), 마커 끝(3번)."""
    st = [C("motion.play", study="REST", step=0, quiet=True), C("timeline.roll_to", feature="Cylinder89")]
    for (x0, x1) in ((-1031.0, -969.0), (-841.0, -779.0)):
        st.append(box(x0, x1, -939.0, -931.0, -365.0, -351.9, "join", [BEAM]))   # 안쪽 기준 턱(위 0.1 겹쳐 join, 결과 형상 같음)
        st.append(box(x0, x1, -992.0, -982.0, -365.0, -351.9, "join", [BEAM]))   # 바깥 누름 턱
    for x in SS_X:                                                                # M5 탭 Ø4.2 관통(Y)
        st.append(C("solid.cylinder", radius=2.1, height=11, base=[x, -992.5, SS_Z], axis="Y",
                    operation="cut", targets=[BEAM]))
    k = 72
    for (x, y) in holes():
        st.append(C("timeline.edit", feature="Cylinder%d" % k, set={"base": [x, y, -340.0]}))
        st.append(C("timeline.edit", feature="Cylinder%d" % (k + 1), set={"base": [x, y, -353.0]}))
        k += 2
    st.append(C("timeline.rollback", position="end"))
    return st


RIGID_OLD = [765, 766, 767, 768, 833, 834, 835, 836, 837, 838, 839, 840]   # "Rigid Group 6:<occ>" (U4_X 묶음)


def stage_move():
    """블록·볼트는 U4_X(occ 6) 리지드 묶음에 잡혀 있어 묶음 조인트를 지우고 옮긴 뒤 같은 이름으로 다시 묶는다."""
    st = [C("motion.play", study="REST", step=0, quiet=True)]
    st += [C("joint.delete", joint=j) for j in RIGID_OLD]
    for occ, dx in ((560, DX1), (561, DX2), (571, DX1), (572, DX2)):
        st.append(C("occurrence.move", occurrence=occ, space="world", translate=[dx, 0, 0]))
    for k in range(1, 9):
        st.append(C("occurrence.move", occurrence="CB5-20_N03XB:%d" % k, space="world",
                    translate=[DX1 if k in (1, 2, 5, 6) else DX2, 0, 0]))
    st.append(C("component.capture_position"))
    for occ in (560, 561, 571, 572):
        st.append(C("joint.rigid_group", occurrences=[6, occ]))
    for k in range(1, 9):
        st.append(C("joint.rigid_group", occurrences=[6, "CB5-20_N03XB:%d" % k]))
    return st


def stage_screws():
    st = [C("motion.play", study="REST", step=0, quiet=True)]
    names = []
    for i, x in enumerate(SS_X, 1):
        nm = "%s_%d" % (SS, i)
        names.append(nm)
        st.append(C("solid.cylinder", radius=2.5, height=10, base=[x, -991.0, SS_Z], axis="Y",
                    operation="new", body_name=nm))
        # 육각 구멍 2.5 대변(외접원 반지름 1.4434), 깊이 3, 뒤끝 Y -991
        st.append(C("sketch.create", plane={"origin": [0, -991.0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]},
                    name="SK_DC07_SS%d" % i))
        st.append(C("sketch.polygon.circumscribed", center=[x, SS_Z], radius=1.25, sides=6))
        st.append(C("sketch.finish"))
        st.append(C("solid.extrude", distance=3, operation="cut", targets=[nm], direction="negative"))
        # 평끝 Ø3.5: 끝 모서리 0.75 모따기
        st.append(C("solid.chamfer", edges=[[x + 2.5, -981.0, SS_Z]], distance=0.75, body=nm))
    st.append(C("material.assign", bodies=names, material="Steel"))
    st.append(C("component.move_bodies", bodies=names, component="U4_X"))
    st.append(C("motion.play", study="REST", step=0, quiet=True))
    return st


STAGES = [("beam", stage_beam), ("move", stage_move), ("screws", stage_screws)]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    allc = []
    for i, (nm, f) in enumerate(STAGES, 1):
        s = f()
        json.dump(s, open(os.path.join(OUT, "model", "stage_%d_%s.json" % (i, nm)), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        allc += s
        print("stage_%d_%s" % (i, nm), len(s))
    json.dump(allc, open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"base": "3D_Modeling/FSAP_v1.0.16.sc", "result": "3D_Modeling/FSAP_v1.0.17.sc"},
              open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("total", len(allc))


if __name__ == "__main__":
    main()
