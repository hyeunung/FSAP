# RX-DC-03 해석부 3회차: fea/models.json 의 세움 받침 행을 fix2 형상(v2.30.2)으로 고친다
import json, os
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, "..", "models.json")
raw = open(p, encoding="utf-8", newline="").read()
d = json.loads(raw)
r = d["parts"]["P_RXDC03_RISER_BRKT_판금"]
r["case"] = "cases/mech_RX-DC-03_fix2_handcalc.py (2회차 cases/mech_RX-DC-03_fix1_handcalc.py, 1회차 cases/mech_RX-DC-03_handcalc.py)"
r["fixed"] = ("판 위 플랜지 X -308.6~-273 · Y 83~97 · Z 250~253(fix2: 꺾음 날 아래 X -308.6~-296.6 연장, 한 몸)이 블록 윗면(X -305부터)에 CB5-12 x2(X -288 · -278, Y 90)로 체결. "
              "세운 판 X -296.6~-293.6(t3) · Y 83~97 · Z 253~392 + 꺾음 날 X -308.6~-296.6 · Y 83~86 · Z 253~392. 뿌리 Z 253은 L 단면 전체. "
              "지렛대 받침점: +X 당김 플랜지 끝 X -273, -X 당김 블록 -X 끝 X -305(블록 밖 돌출 3.6)")
r["status"] = ("손계산 3회차 fea/results/mech_RX-DC-03_fix2_handcalc.json. FEA 못 함 — 환경 없음(D-16). fix2: 뿌리 L 단면 오조작 위 팔 SF 3.48 · 타이 5.23 · Y 당김+비틀림 VM 4.03, "
               "운전 SF 15.97, 처짐 오조작 0.143 · 운전 0.031, f1 341~437 Hz, 날 밑 합력 641 N(이음 전단 15.3 MPa, 모살 a2 19.1 MPa), 볼트 +X 411 N · -X 182 N 암나사 전단 SF 15.09. "
               "블록 밖 돌출 3.6 최악(날 밑 누름 전부 끝에) SF 1.87(디테일 RXDC03-FEA-D4), 고르게 나누면 16.5 MPa. 동작 문제 0(P1 풀림)")
r["step"] = "tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT_fix2.step"
r["version"] = "v2.30.2"
s = json.dumps(d, ensure_ascii=False, indent=1)
nl = "\r\n" if "\r\n" in raw else "\n"
open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl) + (nl if raw.endswith(("\n", "\r\n")) else ""))
print("ok")
