# -*- coding: utf-8 -*-
"""RX-10 수정 1회차(RX-10-F1b, v2.22.2 -> v2.22.3) 편집 명령 생성기.
  python -X utf8 -B tools/gen_rx10_f1b.py  ->  tools/out/mech_RX-10/edit.json · edit_meta.json
고친 것: ① 슈 윗날개 로드 장공 +Y 호 중심 Y -163.5 -> -159.5(5 x 10 -> 5 x 14, 로드 Ø4 +Y 틈 3.0 -> 7.0)
        ② 윗 로드 너트 NTJ-010C:1 Z +1.7(축 틈 0.6 -> 2.3).
스케치는 move_point로 옮기면 풀이가 1e-3 흐트러져(실측 -5.4984) 지우고 정확한 좌표로 다시 넣는다.
새 스케치 id는 v2.22.2에서 99484(지운 99474·99475 다음 번호)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(chr(92), '/')
OUT = ROOT + '/tools/out/mech_RX-10/'
Y0, Y1, XC, R = -168.5, -159.5, -8.0, 2.5          # U6_PRESS 안 좌표(월드 X + 60)
SK = {"type": "sketch", "name": "SK_M06_SHOE_RODSLOT", "component": 96809, "suppressed": False,
      "plane": {"plane": {"origin": [0.0, 0.0, 46.5], "x_dir": [1.0, 0.0, 0.0], "y_dir": [0.0, 1.0, 0.0]}, "type": "custom"},
      "sketch": {"constraints": [{"a": 0, "b": 1, "id": "k1", "type": "tangent"}, {"a": 2, "b": 1, "id": "k2", "type": "tangent"},
                                 {"a": 0, "b": 3, "id": "k3", "type": "tangent"}, {"a": 2, "b": 3, "id": "k4", "type": "tangent"},
                                 {"a": 3, "b": 1, "id": "k5", "type": "equal"}],
                 "counters": {"a": 2, "k": 5, "l": 2, "p": 4},
                 "curves": [{"a": 1, "b": 2, "construction": False, "id": "l1", "type": "line"},
                            {"a": 2, "b": 3, "c": 5, "construction": False, "id": "a1", "type": "arc"},
                            {"a": 3, "b": 4, "construction": False, "id": "l2", "type": "line"},
                            {"a": 4, "b": 1, "c": 6, "construction": False, "id": "a2", "type": "arc"}],
                 "points": [{"fixed": True, "id": "origin", "pos": [0.0, 0.0]},
                            {"fixed": False, "id": "p1", "pos": [XC + R, Y0]}, {"fixed": False, "id": "p2", "pos": [XC + R, Y1]},
                            {"fixed": False, "id": "p3", "pos": [XC - R, Y1]}, {"fixed": False, "id": "p4", "pos": [XC - R, Y0]},
                            {"fixed": False, "id": "a1.center", "pos": [XC, Y1]}, {"fixed": False, "id": "a2.center", "pos": [XC, Y0]}]}}
CUT = {"type": "extrude", "name": "U6S_SHOE_RODSLOT", "component": 96809, "suppressed": False, "operation": "cut",
       "profiles": {"type": "all"}, "sketch": 99484, "targets": ["P_M06_SHOE"],
       "extent": {"convention": "total_distance", "direction": "positive", "distance": "5"}}
C = lambda c, **p: {"command": c, "params": p}
cmds = [C("motion.play", study="REST", step=0, quiet=True),
        C("component.rename", component=0, name="FSAP_v2.22.3"),
        C("document.metadata.set", key="description", value="RX-10 mechanism fix1: RX-10-F1b rod slot +Y end -161 -> -157 (gap 7), upper rod nut axial gap 0.6 -> 2.3"),
        C("timeline.roll_to", feature=99475),
        C("timeline.delete", feature=99475), C("timeline.delete", feature=99474),
        C("timeline.add", feature=SK), C("timeline.add", feature=CUT),
        C("occurrence.move", occurrence=96795, space="world", translate=[0.0, 0.0, 1.7]),
        C("timeline.roll_to", position="end"),
        C("motion.play", study="REST", step=0, quiet=True),
        C("browser.visibility", visible=False, folder="joints"), C("browser.visibility", visible=False, folder="sketches")]
json.dump(cmds, open(OUT + 'edit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({"base": ROOT + "/3D_Modeling/FSAP_v2.22.2.sc", "result": ROOT + "/3D_Modeling/FSAP_v2.22.3.sc",
           "_note": "수정 1회차(RX-10-F1b). 실제 실행에서는 먼저 sketch.move_point로 옮겼다가(풀이가 1e-3 흐트러짐) 스케치·컷을 지우고 다시 넣었다. 형상은 같다. 앞 회차(v2.22.1 -> v2.22.2)는 tools/gen_rx10_f1.py, 옛 RX-10(v2.17.1 -> v2.17.2)은 tools/gen_rx10.py"},
          open(OUT + 'edit_meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(cmds), 'commands')
