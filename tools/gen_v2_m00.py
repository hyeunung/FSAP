# M00 모델링부 생성기: v2.0.0 -> v2.0.1 (유닛 차지 공간 상자 32개 + J_U5_X 한계 0~1380 + machine.json 고침).
# 상자 표는 tools/out/mech_M00/design/boxes.py(기구설계부 원본)를 옮긴 것. 쓰는 법:
#   python -B tools/gen_v2_m00.py            -> tools/out/mech_M00/edit.json 다시 만듦
#   python -B tools/gen_v2_m00.py --machine  -> tools/machine.json 도 M00 값으로 고침
#   solidcraft-cli run tools/out/mech_M00/edit.json --in 3D_Modeling/FSAP_v2.0.0.sc --save <새.sc> 로 같은 형상
# 좌표 = 세계 좌표, 조인트 값 0 자세(노루발·바퀴 내림, 대차 d2 1800). 임시값 D-105·D-107·D-10.
import json, sys
ROOT = "C:/Users/hyeun/OneDrive/Documents/workspace/FSAP"
OUT = ROOT + "/tools/out/mech_M00"
JOINTS = ["J_U3_PRESSER", "J_U3_NEEDLE", "J_U4_PRESS", "J_U4_WHEEL_ROT", "J_U5_X", "J_U5_LIFT", "J_U5_WHEEL_ROT",
          "J_WP_L_X", "J_WP_L_Y", "J_WP_L_ROT", "J_WP_S_X", "J_WP_S_Y", "J_WP_S_ROT", "J_WP_G_X", "J_WP_G_Y", "J_WP_G_ROT"]

def B(name, comp, x0, x1, y0, y1, z0, z1, cuts=()):
    return {"name": name, "comp": comp, "kind": "box", "x": [x0, x1], "y": [y0, y1], "z": [z0, z1], "cuts": list(cuts)}
def C(name, comp, cx, cy, r, z0, z1, cuts=()):
    return {"name": name, "comp": comp, "kind": "cyl", "c": [cx, cy], "r": r, "z": [z0, z1], "cuts": list(cuts)}
def cutB(x0, x1, y0, y1, z0, z1):
    return {"kind": "box", "x": [x0, x1], "y": [y0, y1], "z": [z0, z1]}
def cutC(cx, cy, r, z0, z1):
    return {"kind": "cyl", "c": [cx, cy], "r": r, "z": [z0, z1]}

XW = -1800.0  # 먼 쪽 바퀴 중심 X(J_U5_X 0)
POCKET = cutB(400, 1160, -1565, -250, -901, 1)   # 작업자 자리(휘두름 밖, pocket.json 최소 틈 86.5)
BOXES = [
    # U1 프레임 + 보 (고정)
    B("U1_BEAM", "U1_FRAME", -2300, 1150, 120, 420, 250, 650),
    B("U1_COL_NX", "U1_FRAME", -2450, -2300, 120, 420, -900, 650),
    B("U1_COL_PX", "U1_FRAME", 1150, 1300, 120, 420, -900, 650),
    B("U1_BASE", "U1_FRAME", -2300, 1150, -1555, 1560, -900, -250, [POCKET]),
    # U2 볼 테이블 (고정)
    B("U2_PLATE", "U2_TABLE", -2175, 975, -1555, 1560, -40, 0,
      [POCKET, cutC(-175, 0, 135, -41, 1), cutB(-45, 45, -65, 65, -41, 1)]),
    B("U2_SUB", "U2_TABLE", -2175, 975, -1555, 1560, -250, -40,
      [POCKET, cutB(-320, 520, -200, 200, -251, -39)]),
    # U3 재봉 헤드 (고정 몸체)
    B("U3_UPPER", "U3_HEAD", -80, 500, -90, 90, 125, 560),
    B("U3_HANGER", "U3_HEAD", 0, 400, 90, 120, 300, 650),
    B("U3_LOWER_POD", "U3_HEAD", -40, 40, -60, 60, -200, 0, [cutC(0, 0, 2, -40, 1)]),
    B("U3_LOWER_DRIVE", "U3_HEAD", 40, 500, -60, 60, -200, -60),
    # U3 노루발·바늘 (가동, 값 0 = 내림·바늘 위)
    B("U3_PRESSER_BOX", "U3_PRESSER", -8, 8, -20, 15, 12.5, 100, [cutC(0, 0, 2, 12, 101)]),
    C("U3_NEEDLE_PIN", "U3_NEEDLE", 0, 0, 0.8, 13, 110),
    # U4 바늘 옆 바퀴
    B("U4_MOUNT", "U4_WHEEL_N", -380, -90, -60, 120, 210, 380),
    C("U4_DISK", "U4_WHEEL_N", -175, 0, 125, -12, 0),
    C("U4_DISK_BRG", "U4_WHEEL_N", -175, 0, 60, -60, -12),
    B("U4_DRIVE", "U4_PRESS", -380, -115, -45, 45, 30, 115),
    B("U4_HOLDER", "U4_PRESS", -380, -87.5, -45, 45, 135, 170),
    # U5 먼 쪽 바퀴 대차
    B("U5_RAIL", "U5_WHEEL_F", -2140, -340, 100, 120, 400, 480),
    B("U5_CHAIN", "U5_WHEEL_F", -2200, -300, 150, 390, 650, 750),
    B("U5_CARRIAGE", "U5_CAR", XW - 272.5, XW + 12.5, 50, 98, 220, 500),
    B("U5_DRIVE", "U5_LIFT", XW - 272.5, XW - 15, -45, 45, 30, 115),
    B("U5_HOLDER", "U5_LIFT", XW - 272.5, XW + 12.5, -45, 45, 135, 180),
    # U6 가장자리 센서 + 슈 (바늘 앞 = 들어오는 쪽 -Y)
    B("U6_SHOE_SENSOR", "U6_SENSOR", -85, 10, -200, -100, 12.5, 90),
    # U7 테이프
    B("U7_BINDER", "U7_TAPE", -15, 30, -95, -25, 12.5, 60),
    B("U7_PATH_V", "U7_TAPE", 30, 110, -135, -95, 12.5, 250),
    B("U7_PATH_H", "U7_TAPE", 110, 520, -135, -95, 200, 250),
    B("U7_ROLL", "U7_TAPE", 520, 820, -220, 20, 250, 550),
    # U8 공압·안전 자리
    B("U8_REG", "U8_PNEU", 600, 1000, 40, 120, 300, 600),
    B("U8_LC_L", "U8_PNEU", -2350, -2300, -1605, -1555, -900, 1000),
    B("U8_LC_R", "U8_PNEU", 350, 400, -1605, -1555, -900, 1000),
    B("U8_HMI", "U8_PNEU", 1150, 1300, -900, -700, -900, 500),
    C("U8_LAMP", "U8_PNEU", 1225, 270, 30, 650, 1000),
]

def solid(o, op="new", target=None, name=None):
    if o["kind"] == "box":
        p = {"length": round(o["x"][1] - o["x"][0], 3), "width": round(o["y"][1] - o["y"][0], 3),
             "height": round(o["z"][1] - o["z"][0], 3), "corner": [o["x"][0], o["y"][0], o["z"][0]], "operation": op}
        cmd = "solid.box"
    else:
        p = {"radius": o["r"], "height": round(o["z"][1] - o["z"][0], 3), "base": [o["c"][0], o["c"][1], o["z"][0]], "operation": op}
        cmd = "solid.cylinder"
    if target: p["targets"] = [target]
    if name: p["body_name"] = name
    return {"command": cmd, "params": p}

def build_cmds():
    cmds = []
    for b in BOXES:
        cmds.append(solid(b, "new", name=b["name"]))
        for c in b["cuts"]:
            cmds.append(solid(c, "cut", target=b["name"]))
    comps = {}
    for b in BOXES:
        comps.setdefault(b["comp"], []).append(b["name"])
    for comp, names in comps.items():
        cmds.append({"command": "component.move_bodies", "params": {"bodies": names, "component": comp}})
    return cmds

ZERO = [("J_U3_PRESSER", 0), ("J_U3_NEEDLE", 0), ("J_U4_PRESS", 0), ("J_U5_X", 0), ("J_U5_LIFT", 0)]
def drive(vals):
    return [{"command": "joint.drive", "params": {"joint": j, "value": v, "quiet": True}} for j, v in vals]


def stage():
    s = drive(ZERO) + build_cmds()
    s.append({"command": "joint.limits", "params": {"joint": "J_U5_X", "min": 0, "max": 1380}})
    s.append({"command": "motion.play", "params": {"study": "REST", "step": 0, "quiet": True}})
    s.append({"command": "browser.visibility", "params": {"visible": False, "joints": JOINTS}})
    return s

def patch_machine():
    p = ROOT + "/tools/machine.json"
    m = json.load(open(p, encoding="utf-8"))
    m["doc"] = "../3D_Modeling/FSAP_v2.0.1.sc"
    j = m["joints"]["J_U5_X"]
    j["max"] = 1380.0
    j["_note"] = ("먼 쪽 대차 X. d2(바늘–먼 쪽 바퀴) = 1800 - 값. 0 = 대기(d2 1800), 1380 = d2 420(M00-D05: d2 300이면 "
                  "U4·U5 서보 묶음 겹침 4쌍). 큰 매트 d2 1000(값 800), 홈 매트 d2 800(값 1000), 작은 매트 내리지 않음. d2 420~1800(M00-D05)")
    j["min"] = 0
    note = {"U1_FRAME": "고정(접지). 상자 U1_BEAM·U1_COL_NX·U1_COL_PX·U1_BASE(M00)",
            "U2_TABLE": "고정. 볼 테이블 상자 U2_PLATE(윗면 Z 0)·U2_SUB(M00)",
            "U6_SENSOR": "상자 U6_SHOE_SENSOR(바늘 -Y, M00-D08). 슈 비키는 실린더 조인트는 M06",
            "U7_TAPE": "상자 U7_BINDER·U7_PATH_V·U7_PATH_H·U7_ROLL(M00-D09)",
            "U8_PNEU": "상자 U8_REG·U8_LC_L·U8_LC_R·U8_HMI·U8_LAMP(자리만, M08·D-38)"}
    for u, n in note.items():
        m["units"][u]["_note"] = n
    m["units"]["U3_HEAD"]["_note"] = "상자 U3_UPPER·U3_HANGER·U3_LOWER_POD·U3_LOWER_DRIVE(고정 몸체), U3_PRESSER_BOX(U3_PRESSER), U3_NEEDLE_PIN(U3_NEEDLE)"
    m["units"]["U4_WHEEL_N"]["_note"] = "상자 U4_MOUNT·U4_DISK(Ø250 중심 X -175, M00-D04)·U4_DISK_BRG, U4_DRIVE·U4_HOLDER(U4_PRESS)"
    m["units"]["U5_WHEEL_F"]["_note"] = "상자 U5_RAIL·U5_CHAIN(고정), U5_CARRIAGE(U5_CAR), U5_DRIVE·U5_HOLDER(U5_LIFT)"
    tv = m["temp_values"]
    tv["D-105"] = "대차 d2 420~1800(M00-D05, 옛 300~1800), 대기 1800, 큰 매트 d2 1000·홈 매트 800·작은 매트 안 내림"
    tv["D-107"] = "M00 골격 임시값: 작업면 높이 900, 보 Z 250~650, 기둥 150x300, 윗헤드 몸체 X -80~500 Z 125~560, 원판 중심 X -175, 서보 묶음 길이 265, 포켓 X 400~1160 Y <= -250"
    bl = m["baseline_overlaps"]
    txt = "U2_PLATE·U3_LOWER_POD·U4_DISK ↔ WP_* 밑면 Z 0 맞닿음(부피 0)"
    if not any(b.get("a") == txt for b in bl):
        bl.append({"a": txt, "b": "WP_MAT_*·WP_TAPE_*", "reason": "볼 윗면 = 바늘판 윗면 = 원판 윗면 Z 0에 매트 밑면이 얹힘(M00, 겹침 부피 0)"})
    json.dump(m, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return p

if __name__ == "__main__":
    s = stage()
    json.dump(s, open(OUT + "/edit.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"base": "3D_Modeling/FSAP_v2.0.0.sc", "result": "3D_Modeling/FSAP_v2.0.1.sc",
               "channel": "MCP", "note": "MCP batch 2회(0~29, 30~58) + motion.play REST 0 + browser.visibility, 그다음 save"},
              open(OUT + "/edit_meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("edit steps", len(s), "bodies", len(BOXES))
    if "--machine" in sys.argv:
        print("machine", patch_machine())
