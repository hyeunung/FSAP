# 모델링부 — DC2-04 수정 1회차 (2026-11-04)

요약
- 새 버전 `3D_Modeling/FSAP_v2.3.2.sc`(1,826,745 B). 기준 v2.3.1(덮어쓰지 않음, E-05). `tools/config.json`·`tools/machine.json` doc → v2.3.2. 생성기 `tools/gen_v2_dc204_fix1.py`, 기록 `tools/out/mech_DC2-04/edit.json`(45명령, v2.3.1에 돌림; 앞 회차 기록은 `edit_v231.json`).
- 통로: **CLI**. `mcp running` 실측 "no SolidCraft app is listening at 127.0.0.1:27878" — 앱 꺼짐(실행 규칙 2, WF-121).
- 고친 문제: `P_M05_HOLDER` 날개 A 장공이 조임 마찰로만 Z를 버팀(손 X 100 N 짝힘, 미끄럼 SF 1.18).
- 새 부품: 받침 블록 `P_DC204_PUSH_BLK`(SUS304 절삭), 미는 볼트 `STEP대기_SETSCREW_M4x25_DC204_1·2`(U7_FIXED), 잠금 너트 `STEP대기_NUT_M4_DC204_1·2`, 평 와셔 `STEP대기_WASHER_M5_DC204_1·2`, 블록 볼트 `CB5-12_DC204_1·2`(실물 STEP). 바꾼 것: `CB5-12_M05_11·12` −Y 1(와셔 자리), UPPER −Y 면 M5 탭 2.
- 검사: 과제 범위 겹침 **0**(J_U7_HGT 5점, U7 카세트 조인트 6개 × 25·50·75·100 %, THICK_6·THICK_16 칼·접기 15·보내기 150). floating 0, conflicts 0.
- 지운 부품 0. 조인트 바꿈 없음(새 부품은 기존 유닛 리지드 안). 버전 마지막 자리 +1(지시: 수정 1회차).
- 미완: 없음. 외부: 멈춤나사·너트·와셔 형번·STEP(D-127), 해석 환경 없음(D-16).

## 1. 근거 규칙 (원문)
- E-05: "수정 회차도 앞 파일을 덮어쓰지 않는다" → v2.3.1을 그대로 두고 v2.3.2에 저장.
- M-02: "조정은 장공 + 미는 볼트" → 장공(v2.3.1)에 미는 볼트를 더함. 검증 고칠 안 "DC2-04-X1의 미는 볼트를 1개에서 2개로 늘려 구동 단계로 당긴다".
- M-07: "조인트는 실제 구동 관계대로, 볼트는 물린 부품과 같은 그룹" → 블록·너트·와셔·블록 볼트는 UPPER에 물리므로 U3_HEAD. 미는 볼트는 제품 교체 때 J_U7_HGT를 맞춘 뒤 날개 끝에 대고 잠그므로 위치가 J_U7_HGT를 따른다 → U7_FIXED에 두어 끝이 늘 날개 아래 끝에 닿게 했다(나사산은 블록 구멍 Ø4에서 미끄러짐, 맞닿음 0).
- 실행 규칙 10: STEP 못 받으면 외형 치수로 `STEP대기_` 임시 형상 → 멈춤나사·너트·와셔.
- 실행 규칙 19: 저장 전 `browser.visibility {visible:false, folder:"joints"}` → 기록 끝에 있음.

## 2. 만든·바꾼 것 (세계 mm, 바늘점 원점, 테이블 Z 0, h 0)

| 부품 | 무엇 | 좌표·치수 | 유닛·재질 |
|---|---|---|---|
| P_DC204_PUSH_BLK | 받침 블록(절삭) | X 8~48 · Y −98~−90 · Z 250~276, 부피 6,771.2. M4 탭(호칭 Ø4) 관통 Z 방향 2 (X 14·42, Y −94.1). Ø5.5 관통 + 자리파기 Ø9.5 깊이 5.4 ×2 (X 28, Z 257·269), −Y 세로 모서리 C0.5 | U3_HEAD, SUS304 |
| CB5-12_DC204_1·2 | 블록 → UPPER (실물 `purchased-step/CB5-12/CB5-12.stp`) | 머리 밑 (28, −92.6, 257)·(28, −92.6, 269), 축 +Y, bbox Y −97.6~−80.6(UPPER에 9.4 물림) | U3_HEAD, SCM435 |
| UPPER −Y 면 탭 | `STEP대기_867-392342_UPPER`에 Ø4.2 깊이 12 ×2 | (28, Z 257·269), Y −90~−78. 부피 −332 | U3_HEAD |
| STEP대기_SETSCREW_M4x25_DC204_1·2 | 미는 볼트 멈춤나사 평끝 M4×25 | X 14·42, Y −96.1~−92.1(축 −94.1), Z 260~285(h 0) — 끝 = 날개 A 아래 끝 Z 285, 날개(Y −94~−90)와 1.9 폭 맞닿음. 육각 구멍 자리 Ø2.3 깊이 2 | U7_FIXED, SCM435 |
| STEP대기_NUT_M4_DC204_1·2 | 잠금 너트 M4 1종 맞변 7 · 높이 3.2 | 블록 윗면 Z 276~279.2, 맞변이 UPPER 면과 나란(Y −97.6~−90.6, 돌릴 때 꼭짓점 4.04 → −90.06, UPPER와 0.06) | U3_HEAD, Steel |
| STEP대기_WASHER_M5_DC204_1·2 | 평 와셔 M5 소형 Ø10 · 안 Ø5.3 · t1 | Y −95~−94, (18, 310)·(36, 310) | U3_HEAD, SUS304 |
| CB5-12_M05_11·12 | 와셔 자리만큼 −Y 1 | 머리 Y −100~−95, 끝 −83(UPPER 물림 8 → 7) | U3_HEAD |

- 자리 고른 근거(실측 `tools/out/mech_DC2-04/fix1/probe_out.json`, HGT −4·0·+6): 날개 A 밑 X 0~56 · Y −110~−90 · Z 235~285에서 걸리는 것은 FEED_CARR(Y ≤ −98.5), GUIDE(Y ≤ −104.5), CST_PLATE(X ≥ 50 · Y ≤ −106)뿐 → Y −98.5~−90 띠가 비어 있어 블록 깊이를 8(Y −98)로 했다(FEED_CARR와 0.5). 블록 볼트는 FEED_CARR가 앞을 막아 머리를 자리파기에 묻었다.
- 길이: h −4에서 날개 아래 끝 281 → 너트 위 1.8 틈, h +6에서 미는 볼트 아래 끝 266 → 블록 안 10 + 너트 3.2 물림, h −4에서 아래 끝 256(블록 밑 250 위).
- 장공·HGT 조인트·BASE 쪽은 건드리지 않았다. U6 BASE 쪽 미는 볼트(X1)는 이번 지적이 없어 디테일 그대로.

## 3. 검증 수치 (CLI `run --results`, 저장 전 `tools/out/mech_DC2-04/fix1/check_*`, 909 s, truncated 없음)

새·바뀐 11바디 ↔ 둘레 72바디(새 부품 상자 X −40~100 · Y −150~−60 · Z 200~520에 걸치는 것 + U7_TAPE 전부), `inspect.clearance` 1 mm.

| 자세 | 겹침 | 0 맞닿음 | 1 mm 안 가장 가까운 비접촉 |
|---|---|---|---|
| J_U7_HGT −4 / −1.5 / +1 / +3.5 / +6 | 0 / 0 / 0 / 0 / 0 | HOLDER↔미는 볼트 2, UPPER↔블록, 와셔↔HOLDER·볼트 | HOLDER↔CB5-12_M05 자루 0.25(장공 끝), 블록↔FEED_CARR 0.5, UPPER↔너트 0.6 |
| 새 부품끼리(같은 5점) | 0 | 블록↔볼트·너트·미는 볼트, 너트↔미는 볼트 | — |
| J_U7_CST_X·CST_Y·FEED·CUT·TUCK·LATCH 25·50·75·100 % (24자세) | 0 | 같음 | 같음 |
| THICK_6(HGT −4) 칼·접기 15 / 보내기 150 | 0 / 0 | 같음 | 같음 |
| THICK_16(HGT +6) 칼·접기 15 / 보내기 150 | 0 / 0 | 같음 | 같음 |

- 못 잰 짝(unchecked) 4: UPPER ↔ CB5-12_M05_11·12·CB5-12_DC204_1·2 "boolean Intersect: no result" — 볼트 자루가 UPPER 탭 Ø4.2에 같은 축으로 물린 나사 물림 자리(앞 회차와 같은 짝, 나사 물림 제외).
- 조인트 자기 점검(E-15): `J_U7_HGT` 9 → 6에서 멈춤(HOLDER Z 291~340, 미는 볼트 266~291 — 함께 +6), −9 → −4에서 멈춤(HOLDER 281~330, 미는 볼트 256~281). 블록·너트는 그대로(250~276, 276~279.2). joint.list floating 0, conflicts 0, 조인트 157.
- 손계산(새로 힘 받는 것, 해석부가 다시 봄): 짝힘 100 N × 90 = 9,000 N·mm / 미는 볼트 간격 28 = 321 N + 자중 몫 10 → 하나 약 331 N. M4 응력 단면 8.78 mm² → 38 MPa. 날개 끝 맞닿음 약 6.1 mm²(폭 1.9) → 54 MPa(SUS304 항복 205, SF 3.8). 블록 CB5-12 ×2 전단 각 331 N(자루 응력 단면 14.2 mm² 23 MPa, 조임 마찰 별도). 미는 볼트는 위치로 막으므로 장공 마찰 SF와 상관없다.

## 4. 저장·저장 확인
- 저장: `solidcraft-cli run tools/out/mech_DC2-04/fix1/edit_fix1.json --in 3D_Modeling/FSAP_v2.3.1.sc --save 3D_Modeling/FSAP_v2.3.2.sc`(181 s, 실패 단계 없음). 기록 끝 `motion.play REST 0`, 조인트 글리프 숨김, 설명 'DC2-04 mechanism fix1: U7 holder slot push screws M4 x2 with block on UPPER, M5 washers under slot bolts'. 문서 이름은 파일 이름 → FSAP_v2.3.2.
- 저장본 확인(`fix1/savechk_out.json`): 새 바디 9개 bbox·재질 위 표대로. 바꾸지 않은 HOLDER 32,843.975·BASE 40,670.82·GUIDE·FEED_CARR·NEEDLE_PIN(Z 19~116)·FOOT bbox·부피가 서명과 같음. J_U6_HGT·J_U7_HGT 0, J_U3_PRESSER 20, J_U3_NEEDLE 0.
- 서명: `ledger.py sigpatch --parts fix1/changed_parts.json --bolts fix1/changed_bolts.json` → 바뀜 12, 없어짐 0, 전체 3,762.
- 임시 STEP(해석용, E-06 예외): `tools/out/mech_DC2-04/stepout/P_DC204_PUSH_BLK.step`.
- 스크린샷(사람용, 열지 않음): `tools/out/mech_DC2-04/FSAP_v2.3.2_iso.png`.

## 5. machine.json (E-15)
- `units.U3_HEAD.parts`에 `P_DC204_PUSH_BLK`·`STEP대기_NUT_M4_DC204`·`STEP대기_WASHER_M5_DC204`·`CB5-12_DC204`, `units.U7_TAPE.parts`에 `STEP대기_SETSCREW_M4x25_DC204`, `_note_DC204_fix1`. `J_U7_HGT._note`에 "맞춘 뒤 미는 볼트 M4 ×2를 날개 A 아래 끝에 대고 잠금 너트로 잠근다". doc → v2.3.2. 조인트·연구·상태는 그대로.

## 6. 설계검토서에 넘길 제어·작업 순서 제약 (U-09)
- (a) 레시피 두께 t → h = t − 10. 공압을 끈 채 카세트 장착 상태에서 잠금 너트 2개를 풀고 미는 볼트를 내린 뒤, 장공 볼트를 풀어 J_U6_HGT·J_U7_HGT를 같은 눈금으로 맞추고, 미는 볼트 2개를 날개 A 아래 끝에 대고 잠금 너트를 잠근 다음 장공 볼트를 조인다.
- (b) 블록 고정 볼트 CB5-12_DC204는 FEED_CARR가 앞(−Y)을 막는다 — 카세트를 뺀 상태(J_U7_CST_Y 250)에서 푼다. 미는 볼트 육각 구멍은 블록 밑(Z 250 아래)에서 L 렌치.
- (c) DC2-04 앞 회차 (a)~(c)는 그대로.

## 7. 디테일로 남김 (E-02, 기록만)
- DC2-04-X1(남은 몫): U6 `P_M06_BASE` 장공 쪽 미는 볼트·눈금, U7 눈금.
- 잠금 너트 렌치 접근: 블록 윗면–날개 아래 끝 틈 1.8(h −4)~11.8(h +6), 너트 맞변 7 얇은 스패너가 ±X 옆에서 들어감 — 렌치 원통 검사는 디테일.
- 미는 볼트 끝 맞닿음 폭 1.9(날개 두께 4 중) — 날개 아래 끝에 받침 턱을 더할지는 디테일.

## 워크플로우 메모
- 첫 검사 스크립트를 `against` = 전체 3,753바디로 만들었더니 7.8 MB 인자·10분 넘게 안 끝나 멈추고 둘레 72바디로 좁혀 다시 돌렸다(909 s). 과제 범위 검사는 처음부터 bbox로 좁힌 against를 쓰는 편이 빠르다.
- `inspect.clearance {bodies:[X]}`만 주고 against를 빼면 짝이 0개(pairs_checked 0)로 끝난다 — against를 늘 준다.
