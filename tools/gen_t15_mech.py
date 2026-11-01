"""T15 구동 모델링(v0.8.0 -> v0.8.1): T05 안내 블록 천장 Z76.5~80.5 + 너트 틈 Z80.5~85.5, 패드 윗 긴 모서리 C2 x2.
선정 T15-S1(T15-S02·S09). 같은 형상 다시 만들기:
  python -B tools/gen_t15_mech.py && solidcraft-cli run tools/out/mech_T15/gen_t15.json --in 3D_Modeling/FSAP_v0.8.0.sc --save <새 번호>.sc
(모델링부 실제 통로는 MCP batch, 같은 명령 순서. metadata 문구는 v0.8.1 저장본을 기준으로 한다.)
"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
C = []
def cmd(c, p): C.append({"command": c, "params": p})
GU, PA = "P_T05_GUIDE", "P_T05_PAD"
cmd("motion.play", {"study": "대기", "step": 0, "quiet": True})
cmd("component.activate", {"component": "T05"})
cmd("solid.box", {"length": 62, "width": 23, "height": 4.5, "center": [-119, 572.5, 78.75], "operation": "join", "targets": [GU]})       # F1 천장
cmd("solid.box", {"length": 27.5, "width": 23, "height": 6, "center": [-101.75, 572.5, 83], "operation": "join", "targets": [GU]})    # F2 탑 채움
cmd("sketch.create", {"plane": {"origin": [0, 580, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, "name": "T15_SLOT"})
cmd("sketch.rectangle.rounded", {"p0": [-160, 80.5], "p1": [-114, 85.5], "radius": 1})
cmd("sketch.finish", {})
cmd("solid.extrude", {"sketch": "T15_SLOT", "distance": 80, "direction": "symmetric", "operation": "cut", "targets": [GU]})
cmd("solid.box", {"length": 13, "width": 50, "height": 10.5, "center": [-153.5, 575, 81.25], "operation": "cut", "targets": [GU]})
cmd("solid.fillet", {"edges": [[-130, 562.2, 76.5]], "radius": 3, "body": GU})
cmd("solid.cylinder", {"diameter": 6, "height": 6, "base": [-126.9, 572.5, 75.5], "axis": "Z", "operation": "cut", "targets": [GU]})
cmd("component.activate", {"component": "T05_PAD"})
cmd("solid.chamfer", {"edges": [[-120, 562.5, 63]], "distance": 2, "body": PA})
cmd("solid.chamfer", {"edges": [[-120, 582.5, 63]], "distance": 2, "body": PA})
cmd("component.activate", {"component": "root"})
cmd("document.metadata.set", {"values": {"description": "T15 mechanism: T05 guide pocket ceiling Z76.5-80.5 + nut slot Z80.5-85.5 for thin spanner on SNJ, pad top C2 x2"}})
cmd("motion.play", {"study": "대기", "step": 0, "quiet": True})
cmd("joint.drive", {"joint": "J_T05_PAD", "value": -12.5, "quiet": True})
os.makedirs(os.path.join(H, "out", "mech_T15"), exist_ok=True)
json.dump(C, open(os.path.join(H, "out", "mech_T15", "gen_t15.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(C))
