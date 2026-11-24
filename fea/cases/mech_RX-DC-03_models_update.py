# RX-DC-03 해석부: fea/models.json 에 새 하중 부품 4개(개념 W 판금 받침)를 넣는다
import json, os
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, "..", "models.json")
raw = open(p, encoding="utf-8").read()
d = json.loads(raw)
P = d["parts"]
CR = {"value": "운전 SF 3, 오조작 SF 2, 영구 변형 SF < 1.2 = 동작(SUS304 항복 205, E 193 GPa, G 74 GPa). 처짐 6-2 미정(D-08) -> 기록, 이웃과의 틈과 비교",
      "source": "요구서 6-1(M-09 기본값)"}
CASE = "cases/mech_RX-DC-03_handcalc.py"
LD = "운전: 케이블 굽힘 되돌림 1줄 5 N x 2줄 + 받는 무게 x 3 g. 오조작: 케이블 1줄 손 당김 50 N(임시, PNEU-01과 같음, D-38 전)"
P["P_RXDC03_LEAD_GUIDE_판금"] = {
    "case": CASE,
    "fixed": "탭 X -249~-246 · Y 74~88 · Z 141~163이 그네 P_RX19_SWING_밀링 면에 Ø5.5 x2(Y 80, Z 150 · 159)로 체결 -> 팔(X -296.6~-246, 폭 14, t3) 외팔 47.6",
    "contact": "세운 판(X -296.6~-293.6 · Y 52~96 · Z 86~144, 5.676° 기울임)에 커넥터 2쌍(임시 22x22x50). 그네와 같이 돎(가동 굽힘 0)",
    "load": LD + ". 팔 끝 Z 방향(약한 쪽) 굽힘, Y 당김은 세운 판 밑(팔 58)에서 팔 비틀림 + 강한 쪽 굽힘",
    "criteria": CR,
    "status": "손계산 fea/results/mech_RX-DC-03_handcalc.json. FEA 못 함 — 환경 없음(D-16). 팔 운전 SF 6.99 · 오조작 1.81(디테일 RXDC03-FEA-D2), 비틀림+굽힘 오조작 VM SF 1.46(디테일), 1차 고유 진동 175 Hz",
    "step": "tools/out/mech_RX-DC-03/stepout/P_RXDC03_LEAD_GUIDE.step",
    "version": "v2.29.3"}
P["P_RXDC03_T2_GUIDE_판금"] = {
    "case": CASE,
    "fixed": "판 밑 플랜지 X -310.6~-280 · Z 233~236이 블록 밑면에 CB5-12 x2(X -296 · -286, Y 75, M5 막힌 탭 깊이 10)",
    "contact": "립 X -310.6~-307.6 · Y 66~84 · Z 212~236(매달림 21)에 PTFE 튜브 2(임시 OD 8 x ID 7 x 20), 연장 케이블이 미끄러져 지남",
    "load": LD + ". 립 끝 X 방향",
    "criteria": CR,
    "status": "손계산. 운전 SF 24.9 · 오조작 5.27. 과사양 아님(t3이 판금 최소 두께 쪽)",
    "step": "tools/out/mech_RX-DC-03/stepout/P_RXDC03_T2_GUIDE.step",
    "version": "v2.29.3"}
P["P_RXDC03_RISER_BRKT_판금"] = {
    "case": CASE,
    "fixed": "판 위 플랜지 X -296.6~-273 · Z 250~253이 블록 윗면에 CB5-12 x2(X -286(검도 고침 -288) · -278, Y 90)로 체결 -> 세운 판 X -296.6~-293.6(t3) · Y 83~97(14) · Z 253~392 외팔 139. 지렛대 받침점: +X 당김 플랜지 끝 X -273, -X 당김 판 바깥 면 X -296.6",
    "contact": "타이 판 X -318.6~-295 · Y 83~86 · Z 330~350(케이블 타이 Z 334 · 344), 위 팔 Z 389~392(타이). 구름 고리 쪽 연장 케이블이 위에서 당김",
    "load": LD + ". 두께 방향 X가 약한 쪽: 운전 위 팔 Z 390(팔 137), 오조작 타이 Z 344(팔 91) · 위 팔(137)",
    "criteria": CR,
    "status": "손계산. 운전 SF 2.89(기준 3 -4 %, 디테일) · 처짐 1.53(고리와 틈 1.75). 오조작 위 팔 SF 0.63 · 타이 0.95 -> 영구 변형(동작 RXDC03-FEA-P1). 1차 고유 진동 50.5~67.8 Hz(헤드 33~50 Hz 가까움). 고침안: 세운 판 -X 쪽 꺾음 날 X -308.6~-296.6 · Y 83~86 · Z 253~392(타이 판과 한 판) -> I 1,554 · 오조작 SF 4.63 · 341 Hz. 플랜지 볼트 오조작 411 N 암나사 전단 SF 15.1",
    "step": "tools/out/mech_RX-DC-03/stepout/P_RXDC03_RISER_BRKT.step",
    "version": "v2.29.3"}
P["P_RXDC03_BEAM_CLAMP_판금"] = {
    "case": CASE,
    "fixed": "벽 X -352~-338 · Y 117~120 · Z 507.5~540이 U1_BEAM 앞면 Y 120에 Ø5.5 x2(X -345, Z 522 · 534, 보 STKR400 벽 물림 8). 받침점 벽 밑 Z 507.5",
    "contact": "선반 Y 68~120 · Z 507.5~510.5(폭 14, t3) 위에 구름 고리(J_U4_X 95에서 틈 0.25로 얹힘)",
    "load": LD + ". 선반 끝(외팔 49) 아래 방향",
    "criteria": CR,
    "status": "손계산. 운전 SF 7.28 · 오조작 1.76(디테일 RXDC03-FEA-D3), 처짐 0.08/0.32. 벽 볼트 오조작 71 N 암나사 전단 SF 97.6",
    "step": "tools/out/mech_RX-DC-03/stepout/P_RXDC03_BEAM_CLAMP.step",
    "version": "v2.29.3"}
s = json.dumps(d, ensure_ascii=False, indent=1)
nl = "\r\n" if "\r\n" in raw else "\n"
open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl) + (nl if raw.endswith("\n") else ""))
print("ok", len(P))
