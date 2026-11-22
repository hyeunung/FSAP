# -*- coding: utf-8 -*-
"""RX-14 수정 2회차 생성기 (v2.19.1 -> v2.19.2): 검증에서 나온 동작 문제 F8
python -X utf8 -B tools/gen_rx14_fix2.py   -> tools/out/mech_RX-14/model2/stage_*.json (MCP batch · CLI run 명령 배열)
좌표: 측정 좌표계 = 모델 좌표(바늘점 원점, 테이블 면 Z 0), mm.
 F8 홈통 바닥 밑 받침 띠 P_RX14_DUCT_STRIP (SUS304 t2, X 125~975 · Y -35~-5 · Z -8~-6):
    판넬 윗면 Z -8에 얹고 홈통 바닥 밑면 Z -6에 점용접. 볼 유닛 플랜지(Ø44 · Z -8~-6, 가운데 (150+100k, -50))
    8곳은 R 22.5로 따낸다(플랜지 윗면 Z -6이 그 자리에서 홈통 바닥을 받는다).
"""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mech_RX-14", "model2")
NAME = "P_RX14_DUCT_STRIP"
BALLS_X = [150 + 100 * k for k in range(8)]   # 150 ~ 850, Y -50 줄


def C(cmd, **p):
    return {"command": cmd, "params": p}


ROOT = C("component.activate", component=0)
st = {}

f8 = [C("component.create", name=NAME, parent="U7_BASE"),
      C("solid.box", corner=[125.0, -35.0, -8.0], length=850, width=30, height=2, operation="new",
        body_name=NAME, name="RX14F8_DUCT_STRIP")]
for i, x in enumerate(BALLS_X):
    f8.append(C("solid.cylinder", radius=22.5, height=3, base=[float(x), -50.0, -8.5], axis="Z", operation="cut",
                targets=[NAME], name="RX14F8_STRIP_RELIEF_%d" % (i + 1)))
f8 += [ROOT,
       C("material.assign", bodies=[NAME], material="SUS304"),
       C("component.metadata.set", component=NAME, part_number=NAME,
         description="RX-14 support strip under the tape duct floor, SUS304 t2.0 laser cut (fix2 F8): X 125-975, Y -35..-5, "
                     "Z -8..-6, sits on the panel top Z -8, spot-welded to the duct floor, 8 reliefs R22.5 around the ball unit "
                     "flanges (D44) at X 150..850 / Y -50")]
st["stage_1_f8_strip"] = f8

st["stage_9_presave"] = [
    C("motion.play", study="REST", step=0, quiet=True),
    ROOT,
    C("component.rename", component=0, name="FSAP_v2.19.2"),
    C("document.metadata.set", key="description",
      value="RX-14 mechanism fix2: t2 support strip under tape duct floor on panel top (hand load path), reliefs at ball flanges"),
    C("browser.visibility", visible=False, folder="joints"),
    C("browser.visibility", visible=False, folder="sketches"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k, v in st.items():
        json.dump(v, open(os.path.join(OUT, k + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
        print(k, len(v))
