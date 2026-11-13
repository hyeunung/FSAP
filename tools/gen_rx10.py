# RX-10 명령 생성기 — U6 슈 바닥 Y 90 -> 130(-Y 끝) + 누름 실린더 축 Y -152 -> -166(180도 돌림, 포트 +Y)
# 기준 FSAP_v2.17.1 -> FSAP_v2.17.2. 출력: tools/out/mech_RX-10/edit.json(명령 배열), edit_meta.json
# 좌표: 피처·2D 스케치 점은 U6_SHOE 안 좌표(= REST 월드 X + 60), sketch.line3d/arc3d·occurrence.move(space world)는 REST 월드.
# 순서의 뜻: 이력 앞쪽(SK_M06_SHOE, 3,687개 중 909번째)을 고치면 그 뒤 전체가 다시 계산된다(약 20분).
#   그래서 marker를 EdgeFlange5 뒤로 내려 슈를 고치고 -> BodyTransfer398 뒤로 올려 나머지를 고친 뒤 -> 끝으로 한 번만 올린다.
import json, math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'mech_RX-10')
DX = -60.0          # U6_SHOE 안 좌표 -> REST 월드 X
CYL_Y = -166.0      # 새 실린더 축 Y(옛 -152)
MIRROR_Y = -159.0   # 옛 자리를 이 평면에 거울로 옮긴 자리
BOLT_Y = -177.0     # 브래킷 벽 볼트·인서트(옛 -170)


def W(p):
    return [round(p[0] + DX, 4), round(p[1], 4), round(p[2], 4)]


def ex(command, **params):
    return {"command": command, "params": params}


def sketch_move(sketch, moves):
    c = [ex("sketch.edit", sketch=sketch)]
    c += [ex("sketch.move_point", point=p, to=to) for p, to in moves]
    c.append(ex("sketch.finish"))
    return c


def tube(sketch, pipe, delete, segs, keep_tail, first_new):
    """segs: ('line', a, b) | ('arc', start, through, end) — U6_SHOE 안 좌표. first_new: 새 선의 첫 id 번호."""
    c = [ex("sketch.edit", sketch=sketch), ex("sketch.options", sketch_3d=True), ex("sketch.delete", entities=delete)]
    for s in segs:
        if s[0] == 'line':
            c.append(ex("sketch.line3d", points=[W(s[1]), W(s[2])]))
        else:
            c.append(ex("sketch.arc3d", start=W(s[1]), through=W(s[2]), end=W(s[3])))
    c.append(ex("sketch.finish"))
    path = ["w%d" % (first_new + i) for i in range(len(segs))] + keep_tail
    c.append(ex("timeline.edit", feature=pipe, set={"path": path}))
    return c


s = math.sqrt(0.5)
c225, s225 = math.cos(math.radians(22.5)), math.sin(math.radians(22.5))
TUBE_A = [('arc', (6.5, -146.5, 135.2), (6.5 + 15 * s, -161.5 + 15 * s, 135.2), (21.5, -161.5, 135.2)),
          ('line', (21.5, -161.5, 135.2), (21.5, -186.5, 135.2))]
TUBE_B = [('line', (-8, -146.5, 99.7), (-8, -146.5, 100)),
          ('arc', (-8, -146.5, 100), (2.6066 - 7.5, -157.1066 + 7.5, 100 + 15 * s), (2.6066, -157.1066, 115)),
          ('arc', (2.6066, -157.1066, 115), (-8 + 15 * c225, -167.7132 + 15 * s225, 115), (7, -167.7132, 115)),
          ('line', (7, -167.7132, 115), (7, -171, 115)),
          ('arc', (7, -171, 115), (7, -171 - 15 * s, 130 - 15 * s), (7, -186, 130)),
          ('line', (7, -186, 130), (7, -186, 200)),
          ('arc', (7, -186, 200), (-8 + 15 * s, -186, 200 + 15 * s), (-8, -186, 215)),
          ('line', (-8, -186, 215), (-40, -186, 215))]

cmds = [ex("motion.play", study="REST", step=0, quiet=True),
        ex("component.rename", component=0, name="FSAP_v2.17.2"),
        ex("document.metadata.set", key="description",
           value="RX-10 mechanism: U6 shoe sole Y 90 -> 130 (-Y end), press cylinder axis Y -152 -> -166 turned 180 deg, bracket/insert/tubes follow")]

# 1) 슈 P_M06_SHOE (판금 기능 그대로): 바닥 스케치 -Y 변 -195 -> -235, 입술 변 집는 점
cmds.append(ex("timeline.roll_to", feature=5048))                       # EdgeFlange5 뒤
cmds += sketch_move("SK_M06_SHOE", [("l1.start", [-22.0, -235.0]), ("l1.end", [1.0, -235.0])])
cmds.append(ex("timeline.edit", feature=5048, set={"edges": [[-9.0, -235.0, 14.5]]}))   # EdgeFlange5(입술 20도)

# 2) 로드 구멍·브래킷·캐리지 인서트 자리·관
cmds.append(ex("timeline.roll_to", feature=96843))                      # BodyTransfer398 뒤(관 B 다음)
cmds.append(ex("timeline.edit", feature=96817, set={"base": [-8.0, CYL_Y, 46.5]}))      # Cylinder789 슈 윗날개 로드 구멍 Ø6
cmds += sketch_move("SK_M06_PCYL_BRKT", [("p1", [-22.0, -184.5]), ("p2", [0.0, -184.5])])
cmds.append(ex("timeline.edit", feature=96827, set={"base": [-8.0, CYL_Y, 74.0]}))      # Cylinder800 브래킷 Ø8.5
cmds += sketch_move("SK_M06_PCYL_BRKT_H", [("c1.center", [BOLT_Y, 86.0])])              # 브래킷 벽 Ø5.5
cmds.append(ex("timeline.edit", feature=96830, set={"base": [-30.0, BOLT_Y, 86.0]}))    # Cylinder801 캐리지 인서트 Ø6.8 x 8
cmds.append(ex("timeline.edit", feature=96832, set={"base": [-33.0, BOLT_Y, 86.0]}))    # Cylinder1179 캐리지 Ø5.2 x 3
cmds += tube("SK_TU0604_M08P_U6P_A", 96837, ["w1"], TUBE_A, ["w2", "w3", "w4", "w5"], 6)
cmds += tube("SK_TU0604_M08P_U6P_B", 96842, ["w%d" % i for i in range(1, 8)], TUBE_B, [], 8)

# 3) 구매품 사본 옮기기(REST 월드). 실린더·피팅은 평면 Y -159 거울 자리(회전으로 같은 자세)
Z180 = dict(space="world", axis=[0, 0, 1], angle="180 deg", origin=[-68.0, MIRROR_Y, 0.0])
cmds += [ex("occurrence.move", occurrence=96789, **Z180),                                # CJ2B10-15Z_M06P:1 (몸 + 마운트 너트)
         ex("occurrence.move", occurrence=96793, space="world", translate=[0.0, -14.0, 0.0]),   # 로드(U6_PRESS)
         ex("occurrence.move", occurrence=96795, space="world", translate=[0.0, -14.0, 0.0]),   # NTJ-010C:1
         ex("occurrence.move", occurrence=96796, space="world", translate=[0.0, -14.0, 0.0]),   # NTJ-010C:2
         ex("occurrence.move", occurrence=96811, **Z180),                                # KQ2L06-M5A_M06:2 (출구 +Z)
         ex("occurrence.move", occurrence=96812, space="world", axis=[1, 0, 0], angle="180 deg",
            origin=[-68.0, MIRROR_Y, 135.2]),                                            # KQ2L06-M5A_M06:3 (출구 +X)
         ex("occurrence.move", occurrence=96805, space="world", translate=[0.0, -7.0, 0.0]),    # CB5-12_M06_3:2
         ex("occurrence.move", occurrence=96807, space="world", translate=[0.0, -7.0, 0.0])]    # MBIS5-6.5-8_M06_1:2

# 4) 끝으로 올리고(뒤 전체 다시 계산 한 번), 저장 전 상태
cmds += [ex("timeline.roll_to", position="end"),
         ex("motion.play", study="REST", step=0, quiet=True),
         ex("browser.visibility", visible=False, folder="joints"),
         ex("browser.visibility", visible=False, folder="sketches")]

os.makedirs(OUT, exist_ok=True)
json.dump(cmds, open(os.path.join(OUT, 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')
json.dump({"base": root + "/3D_Modeling/FSAP_v2.17.1.sc", "result": root + "/3D_Modeling/FSAP_v2.17.2.sc",
           "_note": "실제 실행에서는 관 A 스케치에서 좌표계를 한 번 잘못 그려 지운 선(w6·w7)이 있어 새 선 id가 w8·w9다. "
                    "이 기록은 깨끗이 다시 돌릴 때의 id(w6·w7)로 적었다. 형상은 같다."},
          open(os.path.join(OUT, 'edit_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('cmds', len(cmds))
