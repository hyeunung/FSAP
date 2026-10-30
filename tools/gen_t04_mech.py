# T04 가장자리 센서 배치 — 노루발 P_T02_FOOT에 화이버 주머니·검출 슬릿·화이버 통로를 깎는다(선정 T04-C2 수정안).
# 좌표는 대기 자세(J_PRESSER 10)의 세계 좌표. 대기 세계 Z = 내림 Z + 10. PRESSER를 활성화하고 그린다(T02 생성기와 같은 방식).
# 출력: tools/out/mech_T04/model/build.json
#   solidcraft-cli run build.json --in 3D_Modeling/FSAP_v0.3.1.sc --save 3D_Modeling/FSAP_v0.3.2.sc
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_T04', 'model')
os.makedirs(OUT, exist_ok=True)
S = []


def C(cmd, params):
    S.append({"command": cmd, "params": params})


F = "P_T02_FOOT"
PB = "STEP대기_SEWHEAD_PRESSERBAR"

C("motion.play", {"study": "대기", "step": 0, "quiet": True})
C("component.activate", {"component": "PRESSER"})
# (1) 주머니 T_POCKET: Z 23.05 -> 31.05 (바닥 판 윗면에서 열림)
C("sketch.create", {"plane": {"origin": [0, 0, 23.05], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": "SK_T04_POCKET"})
C("sketch.line", {"points": [[1.5139, -6.2493], [-5.3260, 3.6105], [-7.9141, 1.8149], [-1.0742, -8.0449]], "closed": True})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_T04_POCKET", "profiles": "all", "distance": 8.0, "body_name": "T_POCKET"})
# (2) 검출 슬릿 T_SLIT: 바닥면 Z 21.05 -> 23.05, 11.0 x 1.0
C("sketch.create", {"plane": {"origin": [0, 0, 21.05], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, "name": "SK_T04_SLIT"})
C("sketch.line", {"points": [[0.6962, -6.2110], [-5.5736, 2.8271], [-6.3952, 2.2570], [-0.1254, -6.7811]], "closed": True})
C("sketch.finish", {})
C("solid.extrude", {"sketch": "SK_T04_SLIT", "profiles": "all", "distance": 2.0, "body_name": "T_SLIT"})
# (3) 화이버 통로 T_CHAN: Ø2.6, 주머니 A끝 -> +X 옆면 (9, -19.80, 27.05)
C("solid.cylinder", {"radius": 1.3, "height": 16.9041, "base": [-0.0652, -6.7363, 27.05],
                     "axis": [0.56999, -0.821652, 0], "body_name": "T_CHAN"})
C("solid.combine", {"target": F, "tools": ["T_POCKET", "T_SLIT", "T_CHAN"], "operation": "cut"})
C("component.activate", {"component": "root"})

PROPS = {F: "Rigid 10K / SLA Form 3 / L자 바닥 t10 + 자루 18x16 + 위 노즈 r8.5, 바늘 구멍 Ø2.6"
            " + T04 화이버 주머니 12.0x3.15x8(바닥 판 윗면에서 열림) + 검출 슬릿 11.0x1.0 바닥 관통"
            " + 화이버 통로 Ø2.6 곧게 +X 옆면(9,-19.80,27.05)으로. 화이버 머리 형번 미정 D-32, 안 그림",
         PB: "Steel / 구매품 임시 형상(헤드 부품, D-10) / 노루발대 Ø10 L155"}
C("component.metadata.set", {"component": "PRESSER", "properties": PROPS,
                             "description": "노루발(들기 조인트, T03). T02: 노루발 P_T02_FOOT·노루발대."
                                            " T04: 노루발 안 영역형 반사 화이버 주머니·슬릿·통로(머리 형번 미정 D-32, 안 그림)"})
C("document.metadata.set", {"values": {"description": "T04 mechanism: edge sensor pocket, 11x1 detection slit and fiber channel cut in presser foot"}})
C("motion.play", {"study": "대기", "step": 0})

json.dump(S, open(os.path.join(OUT, 'build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(S), 'steps')
