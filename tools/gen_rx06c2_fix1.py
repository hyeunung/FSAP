# -*- coding: utf-8 -*-
"""RX-06-C2 수정 1회차 (v2.15.1 -> v2.15.2) 명령 생성기.

검도 지적: 카세트 관 브래킷(P_M08_TUBE_BRKT_CST_V) 볼트 CB5-16_M05_1:2 · :3 의 끝 4 mm(X 46~50)가
고정부 P_M05_HOLDER +X 벽 살(X 46~50, 탭·구멍 없음)을 뚫는다.
고침: 두 occurrence 를 지우고 같은 머리 자리(받침면 X 62)에 CB5-12 를 놓는다.
      CB5-12_M05_7:1(받침면 X 61, Y -140, Z 262, 축 -X) 을 occurrence.copy 로 (1, -12.5, 42) · (1, -12.5, 58) 옮겨 놓음
      -> 받침면 (62, -152.5, 304) · (62, -152.5, 320), 나사 X 50~62 = 판 P_M05_CST_PLATE(X 50~58) 관통 탭에 8 mm(1.6d).
쓰는 법: python -B tools/gen_rx06c2_fix1.py  -> tools/out/mech_RX-06-C2/model/stage_fix1_*.json, edit.json, edit_meta.json
         앱(MCP) batch 로 stage_fix1_1 -> stage_fix1_2 순서로 보낸 뒤 save {path: FSAP_v2.15.2.sc}.
         CLI: solidcraft-cli run tools/out/mech_RX-06-C2/edit.json --in 3D_Modeling/FSAP_v2.15.1.sc --save <새 파일>
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "mech_RX-06-C2")
BASE = "3D_Modeling/FSAP_v2.15.1.sc"
RESULT = "3D_Modeling/FSAP_v2.15.2.sc"
NAME = "FSAP_v2.15.2"

OLD_OCC = [96424, 96426]            # CB5-16_M05_1:2 · :3 (v2.15.1 의 occurrence id)
SRC = "CB5-12_M05_7:1"              # 받침면 (61, -140, 262), 축 -X, 머리 X 61~66, 나사 X 49~61
SRC_BEARING = [61.0, -140.0, 262.0]
NEW_BEARING = [[62.0, -152.5, 304.0], [62.0, -152.5, 320.0]]


def C(command, **params):
    return {"command": command, "params": params}


def stages():
    s1 = [C("selection.delete", occurrences=OLD_OCC)]
    for bp in NEW_BEARING:
        tr = [round(bp[q] - SRC_BEARING[q], 4) for q in range(3)]
        s1.append(C("occurrence.copy", occurrence=SRC, parent="U7_CASSETTE", in_place=True, translate=tr))
    s2 = [C("component.rename", component=0, name=NAME),
          C("document.metadata.set", key="description",
            value="RX-06-C2 mechanism fix1: tube bracket bolts CB5-16_M05_1:2,3 -> CB5-12 "
                  "(end flush with plate back, no HOLDER wall overlap)"),
          C("motion.play", study="REST", step=0, quiet=True),
          C("joint.drive", joint="J_U7_HGT", value=0, quiet=True),
          C("joint.drive", joint="J_U4_X", value=0, quiet=True),
          C("browser.visibility", visible=False, folder="joints"),
          C("browser.visibility", visible=False, folder="sketches")]
    return [s1, s2]


def main():
    os.makedirs(os.path.join(OUT, "model"), exist_ok=True)
    st = stages()
    allc = []
    for i, s in enumerate(st, 1):
        with open(os.path.join(OUT, "model", "stage_fix1_%d.json" % i), "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
        allc += s
    with open(os.path.join(OUT, "edit.json"), "w", encoding="utf-8") as f:
        json.dump(allc, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "edit_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"base": BASE, "result": RESULT,
                   "note": "RX-06-C2 수정 1회차. 앱(MCP)에서 stage_fix1_1 -> stage_fix1_2 순서로 실행 뒤 save. "
                           "앞 회차(v2.15.0 -> v2.15.1) 기록은 edit_r0.json · edit_meta_r0.json"},
                  f, ensure_ascii=False, indent=1)
    print("stages", [len(s) for s in st], "edit.json", len(allc))


if __name__ == "__main__":
    main()
