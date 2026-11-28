# RX-19 해석부: fea/models.json 에 새 하중 부품 4개 넣고, 걷은 부품 상태에 '걷음 v2.29.0' 표시
import json, os
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, "..", "models.json")
raw = open(p, encoding="utf-8").read()
d = json.loads(raw)
P = d["parts"]
CR = {"value": "운전 SF 3, 오조작 SF 2(A5052 195 · E 70 GPa · G 26.3 GPa, S45C 343). 과사양 = 필요치 3배(note). 처짐 6-2 미정(D-08) — 과제 기준: 바퀴 접지점 처짐 합 < 0.5, 스톱 받침 처짐 < 플로팅 조인트 옆 뜸 0.5",
      "source": "요구서 6-1(M-09 기본값), 과제 RX-19 완료 판정"}
CASE = "cases/mech_RX-19_handcalc.py"
P["P_RX19_BLOCK_밀링"] = {
    "case": CASE,
    "fixed": "옛 P_RX06_CARRIAGE 몸(X -240~-125, Y 45~107, Z 250~482)이 레일 블록 SSEB13-570 x4에 그대로 앉음 -> 캐리지 몸 고정단. 선반 t14(Z 236~250) 밑에 러그·실린더 다리·스톱 받침·스토퍼 다리가 이어 붙은 한 덩어리",
    "contact": "러그 핀 구멍 Ø12 (Y 75, Z 135) <- 핀 PSFJ12-80 반력. 스톱 받침 머리 보(X -260~-228 · Y 17~29 · Z 150~160) +Y 면 Y 29 <- 스톱 블록 -Y 면 압축(나옴 X -248~-230, 겹침 18). 실린더 다리 -Y 면에 CDQSYB20 CB6-16 x4(물림 6). 스토퍼 다리 X -404에 CB5-16 x4(물림 4)",
    "load": "핀 반력 운전 최대 220.8 N(스톱 닿음, 246 - 29.9 Y · 무게 46.75 Z) / 오조작 717.3 N(0.5 MPa 당김 117.8 + 무게·스프링 x3 -> 스톱 821 N). 스톱 받침: 운전 245.7 N · 오조작 821.2 N(-Y, Z 155, 기둥 가운데에서 X 팔 25.25). 들기 157.1 N(D20 0.5 MPa)",
    "criteria": CR,
    "status": "손계산 fea/results/mech_RX-19_handcalc.json. FEA 못 함 — 환경 없음(D-16). 러그 SF 25.1/7.74, 받침 기둥 VM SF 5.71/1.71(오조작 미달 디테일 RX19-FEA-D1), 받침 처짐 운전 0.197 · 오조작 0.66(> 뜸 0.5, RX19-FEA-D2)",
    "step": "tools/out/mech_RX-19/stepout/P_RX19_BLOCK.step",
    "version": "v2.29.0"}
P["P_RX19_SWING_밀링"] = {
    "case": CASE,
    "fixed": "뺨 2(앞 X -132~-120, 뒤 X -172~-160, Y 59~91, 부시 MPFZ12-10 구멍 Ø18)가 핀 (Y 75, Z 135) 둘레로 돎 -> 핀이 받침, 텅 장공의 너클 핀이 둘째 받침(로드 축 힘)",
    "contact": "텅(X -246~-234 · Y 65~85 · Z 116~160, 위 X 8 · Z 160~205) -Y 면이 스톱 블록 +Y 면에 Z 150 모서리로 처음 닿음(1.515°). 장공에 너클 핀 Ø8. 앞판(X -132~-120)에 감속기·서보·바퀴, 앞 띠 목(12 x 12, Y 31~45)이 앞판과 윗판을 이음",
    "load": "스톱 운전 245.7 · 오조작 821.2 N(Z 150, 텅 뿌리 Z 116까지 팔 34). 들기 157.1 N(Z 180, 팔 64). 앞판 매단 무게 약 42 N x 1/3 g(목 굽힘 팔 43.6 · 비틀림 팔 44). 누름 끝 바퀴 51.6 N + 옆힘 16 N(μ0.4 x 40)",
    "criteria": CR,
    "status": "손계산 fea/results/mech_RX-19_handcalc.json. FEA 못 함 — 환경 없음(D-16). 텅 SF 18.8/5.59(들기 15.5), 뺨 SF 190/58.6, 목 VM SF 17.8/5.94(3 g), 바퀴 접지점 처짐 합 0.103 mm(< 0.5)",
    "step": "tools/out/mech_RX-19/stepout/P_RX19_SWING.step",
    "version": "v2.29.0"}
P["P_RX08_STOP_BLOCK_밀링"] = {
    "case": CASE,
    "fixed": "[RX-19 v2.29.0 새로 그림] X -268~-250(물러남, 나옴 +20) · Y 29~65.4 · Z 150~166, M8 탭(축 Y 47.2 · Z 158)으로 플로팅 조인트 JA30-8-125 수나사에 물리고 잠금 너트. 나옴 자세에서 -Y 면이 블록 머리 보 +Y 면(Y 29)에 얹힘(압축만)",
    "contact": "+Y 면 Y 65.4 <- 텅 -Y 면(폭 12, Z 150 모서리 선 닿음). -Y 면 -> 머리 보 18 x 10 면압. 조인트는 축 힘만(옆 뜸 ±0.5)",
    "load": "스톱 운전 245.7 N · 오조작 821.2 N(-Y). 축 힘: 스토퍼 밂 245.4 · 당김 206.2 N(0.5 MPa)은 마찰로만 블록에",
    "criteria": CR,
    "status": "손계산. 탭 밑 순 단면 압축 SF 65.7/19.7, 머리 보 면압 4.6 MPa, 텅 모서리 선 닿음 68.4 N/mm(오조작, 1 mm 자리 잡음 SF 2.85 — 모서리 C0.5 디테일 RX19-FEA-D4). 옛 v2.12.1 모델(브래킷 발 위 블록)은 걷음",
    "step": "tools/out/mech_RX-19/stepout/P_RX08_STOP_BLOCK.step",
    "version": "v2.29.0"}
P["STEP대기_PSFJ12-80(핀·부시 MPFZ12-10 몫)"] = {
    "case": CASE,
    "fixed": "부시 MPFZ12-10 두 개(뺨 앞 X -127~-117 · 뒤 X -175~-165) 가운데 X -122 · -170 받침, 경간 48",
    "contact": "러그(X -158~-136, 가운데 X -147) 구멍 Ø12에서 하중",
    "load": "핀 반력 운전 220.8 N · 오조작 717.3 N, 3점 굽힘(보수)",
    "criteria": CR,
    "status": "손계산. 굽힘 SF 22.0/6.76, 이중 전단 0.98/3.17 MPa, 부시 면압 0.92/2.99 MPa, 러그 면압 2.72 MPa",
    "step": "tools/out/mech_RX-19/stepout/STEP_PSFJ12-80_pin.step",
    "version": "v2.29.0"}
gone = ["P_M02_BASE", "P_M02_ARM_SIDE_N", "P_M02_ARM_SIDE_P", "P_M02_ARM_TIE", "P_M02S_SPRING_TAB_1·_2",
        "P_RX13_CYL_BRKT", "P_RX13_ROD_EXT", "P_RX08_STOP_BRKT_밀링", "P_M02_PIVOT_PIN", "P_M02_PIVOT_PIN(구매·부시 몫)"]
for k in gone:
    if k in P and "걷음 v2.29.0" not in P[k].get("status", ""):
        P[k]["status"] = "걷음 v2.29.0(RX-19, 블록·그네로 바뀜 — 기록으로만 남김) | " + P[k].get("status", "")
for k in ("P_RX06_CARRIAGE", "P_M02_FRONT"):
    if k in P and "RX-19" not in P[k].get("status", ""):
        P[k]["status"] = ("v2.29.0부터 P_RX19_BLOCK_밀링 몸(RX-19) | " if k == "P_RX06_CARRIAGE" else "v2.29.0부터 P_RX19_SWING_밀링 앞판(A5052로 바뀜, RX-19) | ") + P[k].get("status", "")
s = json.dumps(d, ensure_ascii=False, indent=1)
nl = "\r\n" if "\r\n" in raw else "\n"
open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl) + (nl if raw.endswith(("\n",)) else ""))
print("ok", len(P))
