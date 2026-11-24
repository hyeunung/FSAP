# RX-DC-03 해석부 2회차: fea/models.json 의 세움 받침 행을 fix1 형상(v2.30.1)으로 고친다
import json, os
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, "..", "models.json")
raw = open(p, encoding="utf-8", newline="").read()
d = json.loads(raw)
r = d["parts"]["P_RXDC03_RISER_BRKT_판금"]
r["case"] = "cases/mech_RX-DC-03_fix1_handcalc.py (1회차 cases/mech_RX-DC-03_handcalc.py)"
r["fixed"] = ("판 위 플랜지 X -296.6~-273 · Y 83~97 · Z 250~253이 블록 윗면에 CB5-12 x2(X -288 · -278, Y 90)로 체결. "
              "세운 판 X -296.6~-293.6(t3) · Y 83~97 · Z 253~392 + 꺾음 날 X -308.6~-296.6 · Y 83~86 · Z 253~392(fix1). "
              "Z 250~253 층에 X -296.6보다 -X 재료 없음 -> 꺾음 날 아래 끝은 자유단, 뿌리 Z 253 모멘트는 세운 판 단면(14 x 3)만 받는다. "
              "지렛대 받침점: +X 당김 플랜지 끝 X -273, -X 당김 판 바깥 면 X -296.6")
r["status"] = ("손계산 2회차 fea/results/mech_RX-DC-03_fix1_handcalc.json. FEA 못 함 — 환경 없음(D-16). fix1 그대로: 뿌리 Z 253 오조작 위 팔 SF 0.63 · 타이 0.95 "
               "(꺾음 날이 뿌리까지 이어지지 않음 -> 동작 RXDC03-FEA-P1 남음), 운전 뿌리 SF 2.89(디테일), 처짐 운전 0.43 · 오조작 1.96, f1 92.5~119 Hz. "
               "뿌리 위 L 단면(비대칭 굽힘)은 오조작 SF 3.48. 고침안 A: 플랜지를 X -308.6~-296.6 · Y 83~97 · Z 250~253으로 늘려 꺾음 날 아래 끝과 한 몸(모서리 용접 또는 플랜지에서 접어 올림) "
               "-> 오조작 SF 3.48 · 처짐 0.14 · 341 Hz, +4.0 g, 볼트 411 N 암나사 전단 SF 15.1. 대안 B: 세운 판 t6(SF 2.51)")
r["step"] = "tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT_fix1.step"
r["version"] = "v2.30.1"
s = json.dumps(d, ensure_ascii=False, indent=1)
nl = "\r\n" if "\r\n" in raw else "\n"
open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl) + (nl if raw.endswith(("\n", "\r\n")) else ""))
print("ok")
