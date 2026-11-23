# RX-10-F1 명령 생성기 — 슈 윗날개 로드 구멍 Ø6 -> Y 장공 5 x 10 + 윗 너트 틈 0.6, 브래킷 -Y 혀 + 아래로 접은 멈춤 턱
# 기준 FSAP_v2.22.1 -> FSAP_v2.22.2. 출력: tools/out/mech_RX-10/edit.json(명령 배열), edit_meta.json
# 좌표: 피처·2D 스케치 점은 컴포넌트 안 좌표. U6_SHOE(5013) = REST 월드 X + 60, U6_PRESS(96809) = REST 월드 X + 60 · Z - 4.5.
#   occurrence.move(space world)는 REST 월드. 편집은 REST 자세에서만 한다(0.45.0은 다시 계산할 때의 자세로 결과가 정해진다).
# 순서의 뜻: marker를 고칠 피처 바로 뒤로 내려 고친 뒤 한 번만 끝으로 올린다(끝으로 올리기 64~145 s).
# 함정(실측): ① 기본 스케치 곡선을 바꾸면 벽 플랜지 U6S_BRKT_WALL의 edge 이름이 다른 변을 가리킨다 -> edges 점을 다른 값으로 다시 준다
#   (같은 값이면 recomputed 0으로 안 바뀐다). ② 변의 일부에만 플랜지를 달고 굽힘선 연장선 위에 같은 판 살이 있으면
#   0.45.0이 그 살을 굽힘 폭만큼 통째로 잘라낸다(부피로만 잡힌다) -> 멈춤 턱은 굽힘선 연장선에 살이 없는 -Y 끝 변에 단다.
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'mech_RX-10')
ROD = (-8.0, -166.0)      # 로드 축(U6_PRESS·U6_SHOE 안 좌표)
SLOT_W, SLOT_CC = 5.0, 5.0   # 장공 폭, 호 중심 거리 -> 전체 10, 로드 Ø4 틈 X ±0.5 · Y ±3.0
NUT_GAP = 0.6             # 윗 너트 ↔ 윗날개 축 틈(아래 너트는 맞닿음)
STOP_Y = -226.0           # 멈춤 턱 바깥 면 = 혀 끝(로드에서 팔 60)
WALL_END = -216.5         # 벽 -Y 끝(멈춤 턱 굽힘 시작 Y -220 + 릴리프)
TONGUE_X = -15.5          # 혀 -X 변(벽 굽힘 끝 X -16 + 0.5)
STOP_H = 22.3             # 바깥 가상 모서리 Z 77.3 -> 턱 끝 Z 55.0(들린 윗날개 윗면 54.5 + 0.5)


def ex(command, **params):
    return {"command": command, "params": params}


r = SLOT_W / 2
y0, y1 = ROD[1] - SLOT_CC / 2, ROD[1] + SLOT_CC / 2
slot_sketch = {
    "type": "sketch", "name": "SK_M06_SHOE_RODSLOT", "component": 96809, "suppressed": False,
    "plane": {"plane": {"origin": [0.0, 0.0, 46.5], "x_dir": [1.0, 0.0, 0.0], "y_dir": [0.0, 1.0, 0.0]}, "type": "custom"},
    "sketch": {
        "constraints": [{"a": 0, "b": 1, "id": "k1", "type": "tangent"}, {"a": 2, "b": 1, "id": "k2", "type": "tangent"},
                        {"a": 0, "b": 3, "id": "k3", "type": "tangent"}, {"a": 2, "b": 3, "id": "k4", "type": "tangent"},
                        {"a": 3, "b": 1, "id": "k5", "type": "equal"}],
        "counters": {"a": 2, "k": 5, "l": 2, "p": 4},
        "curves": [{"a": 1, "b": 2, "construction": False, "id": "l1", "type": "line"},
                   {"a": 2, "b": 3, "c": 5, "construction": False, "id": "a1", "type": "arc"},
                   {"a": 3, "b": 4, "construction": False, "id": "l2", "type": "line"},
                   {"a": 4, "b": 1, "c": 6, "construction": False, "id": "a2", "type": "arc"}],
        "points": [{"fixed": True, "id": "origin", "pos": [0.0, 0.0]},
                   {"fixed": False, "id": "p1", "pos": [ROD[0] + r, y0]}, {"fixed": False, "id": "p2", "pos": [ROD[0] + r, y1]},
                   {"fixed": False, "id": "p3", "pos": [ROD[0] - r, y1]}, {"fixed": False, "id": "p4", "pos": [ROD[0] - r, y0]},
                   {"fixed": False, "id": "a1.center", "pos": [ROD[0], y1]}, {"fixed": False, "id": "a2.center", "pos": [ROD[0], y0]}]}}
slot_cut = {"type": "extrude", "name": "U6S_SHOE_RODSLOT", "component": 96809, "suppressed": False, "operation": "cut",
            "profiles": {"type": "all"}, "sketch": 99474, "targets": ["P_M06_SHOE"],
            "extent": {"convention": "total_distance", "direction": "positive", "distance": "5"}}
stop = {"type": "sheet_flange", "name": "RX10F1_BRKT_STOP", "component": 5013, "suppressed": False, "angle": "90",
        "body": "P_M06_PCYL_BRKT", "edges": [[-8.0, STOP_Y, 74.3]], "height": str(STOP_H), "position": "inside"}

cmds = [ex("motion.play", study="REST", step=0, quiet=True),
        ex("component.rename", component=0, name="FSAP_v2.22.2"),
        ex("document.metadata.set", key="description",
           value="RX-10 mechanism: RX-10-F1 shoe wing rod hole -> Y slot with nut gap, bracket -Y tongue with down stop flange over shoe"),
        # 1) 슈 윗날개: 로드 구멍 Cylinder789(Ø6) 지우고 Y 장공(스케치 + 컷). 새 스케치 id는 v2.22.1에서 99474
        ex("timeline.roll_to", feature=96817),
        ex("timeline.delete", feature=96817),
        ex("timeline.add", feature=slot_sketch),
        ex("timeline.add", feature=slot_cut),
        # 2) 브래킷: 기본 스케치를 벽 구간(Y -216.5~-122) + 혀(X -15.5~0, Y -226~-216.5)로, 벽 변 다시 집기, 멈춤 턱
        ex("timeline.roll_to", feature=96829),
        ex("sketch.edit", sketch="SK_M06_PCYL_BRKT"),
        ex("sketch.delete", entities=["l1"]),
        ex("sketch.move_point", point="p1", to=[-22.0, WALL_END]),
        ex("sketch.move_point", point="p2", to=[0.0, STOP_Y]),
        ex("sketch.line", points=[[-22.0, WALL_END], [TONGUE_X, WALL_END], [TONGUE_X, STOP_Y], [0.0, STOP_Y]]),
        ex("sketch.finish"),
        ex("timeline.edit", feature=96826, set={"edges": [[-22.0, -169.0, 77.3]]}),     # U6S_BRKT_WALL 변 다시 집기
        ex("timeline.add", feature=stop),
        # 3) 윗 로드 너트 NTJ-010C:1 을 0.6 위로(축 틈)
        ex("occurrence.move", occurrence=96795, space="world", translate=[0.0, 0.0, NUT_GAP]),
        # 4) 끝으로 올리고 저장 전 상태
        ex("timeline.roll_to", position="end"),
        ex("motion.play", study="REST", step=0, quiet=True),
        ex("browser.visibility", visible=False, folder="joints"),
        ex("browser.visibility", visible=False, folder="sketches")]

os.makedirs(OUT, exist_ok=True)
json.dump(cmds, open(os.path.join(OUT, 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, '/')
json.dump({"base": root + "/3D_Modeling/FSAP_v2.22.1.sc", "result": root + "/3D_Modeling/FSAP_v2.22.2.sc",
           "_note": "실제 실행에서는 멈춤 턱 자리를 네 번 고쳐 그렸다(+X 변 3번은 0.45.0이 판을 잘라내 버림, -Y 끝 Y -234 -> -226). "
                    "그래서 실제 스케치 선 id는 l5·l6·l10, 멈춤 턱 피처 id는 99483이다. 이 기록은 깨끗이 다시 돌릴 때의 순서로 적었다"
                    "(선 id l5·l6·l7). 형상은 같다. 옛 RX-10(v2.17.1 -> v2.17.2) 기록은 tools/gen_rx10.py로 다시 만든다."},
          open(os.path.join(OUT, 'edit_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('cmds', len(cmds))
