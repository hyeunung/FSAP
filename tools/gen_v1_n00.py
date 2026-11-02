# N00 전체 골격(U1~U9) 생성기 — v1.0.0 → v1.0.1 (모델링부 2026-11-03, 엔진 v3.7.1)
# 선정 지시서 docs/reports/mechanism/mech_N00_select.md 의 상자를 그대로 그린다.
# 출력: tools/out/mech_N00/model/stage_1..4.json (MCP batch로 차례로 보낸다), edit.json(이어 붙인 것)
# 좌표: 바늘점 원점, 작업면 Z 0, 이송 +Y, 작업자 -Y. 조인트 모두 0, 노루발 0(내림) 자세의 세계 좌표.
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_N00', 'model')


def box(name, x0, x1, y0, y1, z0, z1):
    return {"command": "solid.box", "params": {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0,
            "corner": [x0, y0, z0], "operation": "new", "body_name": name}}


def cut_box(target, x0, x1, y0, y1, z0, z1):
    return {"command": "solid.box", "params": {"length": x1 - x0, "width": y1 - y0, "height": z1 - z0,
            "corner": [x0, y0, z0], "operation": "cut", "targets": [target]}}


def cyl(name, cx, cy, r, z0, z1):
    return {"command": "solid.cylinder", "params": {"radius": r, "height": z1 - z0, "base": [cx, cy, z0],
            "operation": "new", "body_name": name}}


def comp(name):
    return {"command": "component.create", "params": {"name": name, "parent": "root", "activate": False}}


def move(bodies, c):
    return {"command": "component.move_bodies", "params": {"bodies": bodies, "component": c}}


FIXED = {
    "U1_HEAD": [box("U1_UPPER", -80, 500, -90, 90, 125, 560),
                box("U1_BUNDLE", -15, 15, -10, 15, 46, 124),
                box("U1_LOWER_POD", -30, 30, -45, 45, -120, 0),
                {"command": "solid.cylinder", "params": {"radius": 2, "height": 41, "base": [0, 0, -40],
                 "operation": "cut", "targets": ["U1_LOWER_POD"]}},
                box("U1_LOWER_DRIVE", 30, 500, -460, -20, -140, -60)],
    "U2_BRIDGE": [box("U2_BASE", -2175, 975, -1555, 1560, -900, -380),
                  box("U2_COLUMN", 500, 620, -520, -400, -380, 560),
                  box("U2_BOOM", -80, 620, -520, 90, 560, 680)],
    "U4_FIX": [box("U4_RAIL_A", -1400, 500, -1000, -920, -380, -340),
               box("U4_RAIL_B", -1400, 500, 920, 1000, -380, -340)],
    "U6_SENSOR": [box("U6_SENSOR_BOX", -10, 10, -75, -46, 13, 60)],
    "U7_TAPE": [box("U7_ROLL", 100, 400, -300, -120, 200, 520),
                box("U7_PATH", -10, 10, -140, -95, 70, 200)],
    "U8_CASSETTE": [box("U8_CASSETTE_BOX", -15, 15, -45, -21, 13, 124)],
    "U9_LOAD": [box("U9_LOAD_BOX", -1700, -100, -1595, -1555, -380, 0)],
}
POSTS = [(-1040, 900), (-840, 900), (-1040, -980), (-840, -980)]


def bodies_of(steps):
    return [s["params"]["body_name"] for s in steps if s["params"].get("operation") == "new"]


def stages():
    s1 = [{"command": "joint.drive", "params": {"joint": "J_U1_PRESSER", "value": 0, "quiet": True}}]
    for c, steps in FIXED.items():
        s1.append(comp(c))
        s1 += steps
        s1.append(move(bodies_of(steps), c))
    # U5 이동 에어 테이블(U4_X와 리지드) + U4_X 보
    s2 = [box("U4_X_BEAM", -1050, -750, -1000, 1000, -340, -260),
          move(["U4_X_BEAM"], "U4_X"),
          comp("U5_AIRTABLE"),
          box("U5_TABLE", -2010, 210, -1545, 1560, -40, 0),
          cut_box("U5_TABLE", -970, -830, -820, 820, -41, 1),       # 원판 홈
          cut_box("U5_TABLE", -1252.5, 220, -55, 55, -41, 1),       # 바늘(아랫유닛 받침) 홈, +X 끝 열림
          cut_box("U5_TABLE", -722.5, 220, -530, -390, -41, 1)]     # U2 기둥 홈, +X 끝 열림
    posts = []
    for i, (x0, y0) in enumerate(POSTS):
        n = "U5_POST_%d" % (i + 1)
        posts.append(n)
        s2.append(box(n, x0, x0 + 80, y0, y0 + 80, -260, -40))
    s2.append(move(["U5_TABLE"] + posts, "U5_AIRTABLE"))
    # U4_Y, U3_ROT, U1_PRESSER, U1_NEEDLE(기존 컴포넌트)
    s3 = [box("U4_Y_CARR", -1025, -775, -525, -275, -260, -230),
          box("U3_DRIVE", -965, -835, -465, -335, -230, -130),
          move(["U4_Y_CARR", "U3_DRIVE"], "U4_Y"),
          cyl("U3_PLATE", -900, -400, 60, -15, 0),
          cyl("U3_COLUMN", -900, -400, 50, -130, -15),
          move(["U3_PLATE", "U3_COLUMN"], "U3_ROT"),
          box("U1_PRESSER_BOX", -8, 8, -20, -2, 13, 25),
          move(["U1_PRESSER_BOX"], "U1_PRESSER"),
          cyl("U1_NEEDLE_PIN", 0, 0, 0.8, 13, 45),
          move(["U1_NEEDLE_PIN"], "U1_NEEDLE")]
    # 리지드(M-07): 고정 7 + REF_GROUND, U5 + U4_X
    s4 = [{"command": "joint.rigid_group", "params": {"occurrences": ["REF_GROUND:1"] + [c + ":1" for c in FIXED]}},
          {"command": "joint.rigid_group", "params": {"occurrences": ["U4_X:1", "U5_AIRTABLE:1"]}},
          {"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}}]
    return [s1, s2, s3, s4]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    allc = []
    for i, s in enumerate(stages(), 1):
        json.dump(s, open(os.path.join(OUT, 'stage_%d.json' % i), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        allc += s
        print('stage_%d' % i, len(s))
    json.dump(allc, open(os.path.join(ROOT, 'out', 'mech_N00', 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('total', len(allc))
