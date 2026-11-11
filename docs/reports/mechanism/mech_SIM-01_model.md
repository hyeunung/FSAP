# SIM-01 모델링 2회차 — M02R 저장본에서 U4 묶음 간섭·영상 (모델링부, 2026-11-12)

요약(10줄 안):
- 저장 `3D_Modeling/FSAP_v2.10.4.sc`(기준 v2.10.3, 형상 변경 0 — 표시만). `tools/config.json` doc → v2.10.4.
- 바꾼 것: 저장본에서 숨어 있던 L 매트·테이프(MAT_L, SEAM_L, TP_L_* 48바디)를 켜서 저장. v2.10.3은 매트 4장·테이프 조각 전부가 숨김으로 저장돼 앱에서 테이프가 안 보였다(사용자 "이거 안보이냐고;;"). S·G·V 매트는 L과 같은 자리(겹침)라 숨김 유지. 조인트·스케치 숨김(규칙 19), REST step 0.
- check4(U4 묶음 against, budget_s 600, CLI 5병렬): CYCLE_L 716단계 276쌍, S 450단계 60쌍, G1 514단계 228쌍, G2 630단계 228쌍, V 486단계 228쌍 — 모두 collisions 0, truncated false.
- U4 밖 against는 1회차(v2.10.2)에서 겹침 0, 이번에 테이프 형상 변화 없음 → 다시 돌리지 않음(E-17).
- 영상 5연구 `tools/out/mech_SIM-01/anim3/`: 연구마다 전체 GIF + 바늘 근처 PNG 프레임, 각 167프레임(≥ 150), 접촉 정지 0.
- 굽힘 R ≥ 3(D-167)·풀림 차 ≤ 1 %(D-168)·비틀림(D-169): 테이프 줄 형상 변화 0이라 1회차 값(R 3/19, 풀림 차 ≤ 0.25 %) 그대로.
- 미완 0. 새 부품·볼트·조인트 0, 서명 sigpatch 대상 없음(형상 변화 0).

## 1. 통로·시간

| 항목 | 값 |
|---|---|
| 통로 | MCP(앱 실행 중, running 빈 목록) → open v2.10.3(오류 0, 피처 3,598) → 표시 batch → save {path v2.10.4}. 덮어쓰기 0 |
| CLI | 긴 간섭·영상은 규칙 2대로 CLI(저장본 v2.10.4). check4 5병렬 + 영상 5병렬 동시: 간섭 1,985~2,002 s, 영상 2,597~2,603 s(열기 포함, 10병렬이라 열기가 길어짐) |
| 이름 목록 | component.list(MCP) → `check4/allocc_v2104.json`(occurrence 2,898). 앞서 CLI로 같은 목록을 v2.10.3에 시작했다가 8분 넘어 멈춤(MCP로 대신) |

## 2. 바꾼 것(형상 변경 0)

- browser.visibility 켬: MAT_L, SEAM_L, TP_L_01a~41a, TP_L_06b·16b·16c·26b·26c·36b·36c. 숨김 유지: MAT_S·G·V, SEAM_S·G·V, TP_S_*·TP_G_*·TP_V_*(L과 같은 자리 대안 매트).
- 매트 bbox: L X −1493.5~6.5, Y −1050~450 / S X −293.5~6.5, Y −400~−200 / G·V X −1193.5~6.5, Y −900~300 (Z 0~10) — 겹쳐서 한 번에 하나만 켠다.
- 명령 기록 `tools/out/mech_SIM-01/edit.json`, `edit_meta.json`(base v2.10.3 → result v2.10.4). 1회차 기록은 `prev_r1/`.

## 3. check4 — U4 묶음 against (CLI `motion.interference`)

against: U4S_CYL:1, U4S_ROD:1, U4_CYL:1, U4_CYL_CLEVIS:1, U4_DISK:1, U4_PRESS:1, U4_ROD:1, U4_ROD_NUT:1, U4_WHEEL:1, U4_WHEEL_N:1(v2.10.4 이름 목록에서 U4로 시작하는 전부). occurrences: 테이프 줄·급송 + 그 연구의 WP_TP 조각·SEAM·WP_TAPE.

| 연구 | 단계 | 쌍 | 겹침 | truncated |
|---|---|---|---|---|
| CYCLE_L | 716 | 276 | 0 | false |
| CYCLE_S | 450 | 60 | 0 | false |
| CYCLE_G1 | 514 | 228 | 0 | false |
| CYCLE_G2 | 630 | 228 | 0 | false |
| CYCLE_V | 486 | 228 | 0 | false |

결과 원본 `tools/out/mech_SIM-01/check4/res_CYCLE_*.json`.

## 4. 영상 5연구

`tools/out/mech_SIM-01/anim3/` — CYCLE_L·S·G1·G2·V 각 `_all.gif`(800×500, 167프레임, 20 fps) + `_needle/` PNG 167장. S·G·V는 L 세트를 끄고 그 연구의 매트·조각을 켬. 접촉 정지 0. 800×500에서 엔진 한계 samples ≤ 167.

## 5. 완료 판정

| 항목 | 기준 | 값 | 판정 |
|---|---|---|---|
| 전 단계 테이프·조각 과제 범위 간섭 | 0, truncated false | U4 묶음 0(이번), U4 밖 0(1회차, 형상 변화 0) | 만족 |
| 굽힘 R | ≥ 3(D-167) | 3(가이드 출구), 19(G1·TOP) | 만족 |
| 풀림 차 | ≤ 1 %(D-168) | ≤ 0.25 % | 만족 |
| 비틀림 | ≤ 1 %(D-169) | 1회차 값 그대로(줄 형상 변화 0) | 만족 |
| 영상 | 5연구 | 5 × 167프레임 | 만족 |

## 워크플로우 메모

- 저장본에서 작업 대상(매트·테이프)이 숨김이면 사용자가 앱에서 못 본다. 모델링부 저장 전 점검에 '작업 대상 대표 세트 보임'이 없다.
- CLI 10병렬 동시 열기는 한 개당 약 33~43분(혼자 11분). 영상·간섭을 같은 열기 한 번에 묶는 편이 낫다.

---

# SIM-01 모델링 — 봉제 진행 테이프 시뮬레이션 (모델링부, 2026-11-11)

요약(10줄 안):
- 저장 `3D_Modeling/FSAP_v2.10.0.sc`(기준 v2.9.0, 가운데 자리 +1: 새 컴포넌트 U7_TAPE_LINE·U7_TAPE_FEED·WP_TP_* 122). 통로 MCP(앱 27878), 막힘·재시작 0.
- 새 테이프 줄: TL_UP 20,814 · TL_TWIST 7,528 · TL_LOW 9,298.9 · TL_FEED 225 mm³(지시 20,810 ±1 % · 7,475.5 · 9,298.9 · 225). 자리 상자 U7_TAPEWAY_H·V 지움(+그 BodyTransfer 2개). P_M05_GUIDE 출구 필렛 R3: 136,639.8 → 136,623.3 mm³.
- 붙은 테이프: TAPE_L·S·G·V → 조각 L 41·S 7·G 35·V 35 + SEAM 4 = 컴포넌트 122, 슬라이더 J_TP_* 122(0 붙음 / 2000 대기, 2000에서 bbox Z 2000~2011 확인). 조각 부피 합 = 원래 띠(차 ≤ 0.6 mm³).
- 연구 REST(모두 0)·CYCLE_L·S·G1·G2·V에 J_TP 키(땀이 조각 끝을 지난 단계). 끝에 붙은 조각: L 42/42, S 8/8, G1 4/36 → G2 36/36, V 4/36(V 연구는 V홈 구간만 꿰맴).
- 전 단계 간섭(CLI motion.interference, truncated false): 테이프 줄 + 조각 ↔ U3 노루발·바늘, U4 전체, U5 대차·승강·바퀴·플로트, U6 슈·누름·센서 — 5연구 모두 겹침 0. 테이프 줄 ↔ 그 매트: TL_FEED만 회전 중 겹침(최대 깊이 1.78~5.0, 기준선 7절).
- 판정 기준: 굽힘 R G1·TOP 19, 가이드 출구 R3(테이프 안쪽 3.5) ≥ D-167 3 → 만족. 풀림량 차 ≤ 0.25 % ≤ D-168 1 % → 만족(설계 측정 그대로, 줄 형상 지시대로).
- 사이클 영상: 연구 5 × (전체 GIF + 바늘 근처 PNG 프레임). 엔진 한계로 800×500에서 samples ≤ 167 → 167로 함(지시 min(단계+1, 300)). 결과 표 6절.
- 미완·벗어남: L 조각 2개 155.2 mm(>150), L 첫 모서리 자름 13.5 mm(<20) — split이 지역 좌표로 계산된 탓(3절). 새 구매품·볼트 0.

## 1. 통로·시간

| 항목 | 값 |
|---|---|
| 통로 | MCP(running 빈 목록 확인 → open v2.9.0 → dirty false → checkpoint 83) |
| 앱 무거운 호출 | timeline.delete 2번(앞쪽 피처 지움 → 뒤 2,000여 피처 다시 계산) 각 약 11분·17분. 조각 자르기+이름 바꾸기 묶음 L 96단계 약 16분, G 87단계 약 15분, V 87단계 약 15분(body.rename이 단계마다 1~10 s로 늘어남). 컴포넌트·조인트 단계는 0.3~0.9 s |
| CLI | 저장본 열기 약 11.5분(10~12병렬). 간섭 5연구 각 691~709 s(열기 포함) |
| 저장 | save {path v2.10.0} 3번(처음 다른 이름 저장 → 그림 뒤 저장 → BodyTransfer 오류 고친 뒤 저장). 덮어쓰기 save {} 0 |

## 2. 만든·지운 부품(좌표 mm)

| 바디 | 컴포넌트 | bbox X / Y / Z | 부피 mm³ | 비고 |
|---|---|---|---|---|
| TL_UP | U7_TAPE_LINE | 21.55~665.43 / −125.5~−94.5 / 575.99~615.85 | 20,814.0 | 경로 (665.416,600.570)→(504.51,605.507)→(44.381,614.496)→호→(24.5,595)→(24.5,576), 31×1 |
| TL_TWIST | U7_TAPE_LINE | 13.14~44.50 / −125.51~−94.49 / 333.71~576.01 | 7,528.0 | (24.5,576)→(29,334) twist 90°. 지시 7,475.5 대비 +0.7 %. 끝면이 경로에 수직이라 Z 333.71(0.29 기울어짐) |
| TL_LOW | U7_TAPE_LINE | 13.5~44.5 / −110.5~−95.77 / 41.51~334 | 9,298.9 | 지시 값과 같음 |
| TL_FEED | U7_TAPE_FEED | −2.5~7.5 / −9~−1.5 / −1~11 | 225.0 | ㄷ자 한 스케치 |
| P_M05_GUIDE(고침) | U7_CASSETTE | 그대로 | 136,623.3 | 출구 모서리(면 23|24, 에지 129) R3, −16.45 mm³ = 손계산 16.7 |
| U7_TAPEWAY_H·V(지움) | U7_ROLL_MOUNT | — | — | Box140·141과 BodyTransfer160·161 |

- 리지드: U7_ROLL_MOUNT:1 + U7_TAPE_LINE:1, U7_CASSETTE:1 + U7_TAPE_FEED:1(SIM-01-M1). 재질 Default(작업 대상 모형, BOM 밖).
- 틈(REST, inspect.clearance): TL_LOW ↔ 가이드·고정날·이송 집게 0(맞닿음), 바인더 0.77, HOLDER 1.5, TL_TWIST ↔ HOLDER 1.53, TL_UP ↔ G1 롤러 0.035·TOP 롤러 0, TL_FEED ↔ 바인더 2.0. TL_UP ↔ U7_TAPE_ROLL 357 mm³(풀림 접점, 롤 = 같은 테이프 → 기준선 SIM-01-M5).

## 3. 붙은 테이프 조각

- 자름: 각 띠를 대각(사각 바깥 꼭짓점 둘을 잇는 평면) 2번 + G·V는 Y −600(홈 꼭짓점)으로 '면'으로 나눈 뒤, 면마다 땀 방향 순서로 평면 자름(법선 = 땀 진행 방향, 남는 쪽이 이름 유지). 시작 자름 = 매트 좌표 (0, −300)(노루발 내림 단계 14의 바늘점).
- 발견: 루트에 새로 생기는 split 조각이 WP_TAPE_L·S·G 지역 좌표로 계산돼(+6.5 X 어긋남, F01-C1 e 6.5 이동 때문으로 보임) X −6.5에 놓였다 → `solid.move` +6.5로 제자리. V는 어긋남 0. L은 이것을 알기 전에 잘라 X 방향 자름이 6.5 밀림: L_16·L_26 155.2 mm, L_36 첫 자름 모서리에서 13.5 mm. 그 밖 조각 30~148.7 mm(S 135.4, G 52~148, V 30.1~147.9).
- 조각 표: `tools/out/mech_SIM-01/model/tp_plan_asrun.json`(조각·바디·땀 선 호 d0~d1·조인트 점). 부피 합: L 721,644.0 · S 116,644.0 · G 610,977.6 · V 602,878.6(원래 띠와 같음).
- 조인트: J_TP_<M>_<nn>·J_TP_<M>_SEAM slider, a = WP_MAT_<M>:1, b = 조각, 축 +Z, flip true, [0, 2000]. 2000 구동 시 TP_S_01a·b Z 2000~2011 확인 후 0으로 되돌림.
- 키(`model/keys.py` → `tp_keys.json`): 연구 키 J_WP_*_X·Y·ROT(선형)로 바늘점을 매트 좌표로 옮겨 땀 선 호 d(i)(노루발 0 구간, 되돌지 않음). 바늘점–땀 선 거리 0(모든 단계). 첫 조각 붙는 단계 L 56·S 116·G1 73·V 88, SEAM L 668·S 434·G2 574.

## 4. 기계 정의·연구

- machine.json: joints J_TP_* 122(model_only, sim_stage), units U7_TAPE_LINE 새로·WP_* parts에 TP_ 접두, U7_ROLL_MOUNT parts에서 U7_TAPEWAY 뺌, studies _keys_TP, workpiece_stages sim_tape, baseline_overlaps 4줄(SIM-01-M5), _history.
- 연구: REST 150키(옛 28 + J_TP 122 모두 0), CYCLE_S 36·L 70·G1 64·G2 64·V 64 키(옛 키 값 그대로 복사 — 소수 4자리 이하라 손실 0, `model/motion_list_before.json`).
- 저장 상태: motion.play REST 0(moved false), 조각·SEAM 140바디 숨김, 조인트·스케치 숨김(실행 규칙 19).

## 5. 검사(수치, E-16)

### 5-1. 전 단계 간섭(CLI motion.interference, 저장본 v2.10.0)
occurrences = U7_TAPE_LINE:1, U7_TAPE_FEED:1 + 그 매트 WP_TP_*:1 전부, against = U3_PRESSER·U3_NEEDLE·U4_PRESS·U4_WHEEL·U4_DISK·U4_CYL·U4_ROD·U5_CAR·U5_LIFT·U5_WHEEL·U5_FLOAT·U6_SHOE·U6_PRESS·U6_SENSOR. 검사 전 browser.visibility all 켬.

| 연구 | 표본 | 쌍 | truncated | 겹침 |
|---|---|---|---|---|
| CYCLE_L | 717 | 616 | false | 0 |
| CYCLE_S | 451 | 140 | false | 0 |
| CYCLE_G1 | 515 | 532 | false | 0 |
| CYCLE_G2 | 631 | 532 | false | 0 |
| CYCLE_V | 487 | 532 | false | 0 |

테이프 줄 ↔ 그 매트(WP_MAT_<M>:1): TL_FEED만 회전 단계에서 겹침 — L 84~601 깊이 1.78(17.9 mm³), S 23~398 1.78, G1 90~480 4.31(56.8), G2 32~514 1.78, V 104~437 5.0(75.2). 기준선 'TL_FEED ↔ WP_MAT_* 회전 중 = 바인더 출구에서 테이프 굽음(7절)'. TL_UP·TWIST·LOW ↔ 매트 0.
결과 `tools/out/mech_SIM-01/check/res_<연구>.json`.

### 5-2. 판정 기준
| 기준 | 값 | 판정 |
|---|---|---|
| D-167 ① 굽힘 R ≥ 3(테이프 안쪽 면) | G1 19, TOP 19(가운데 선 r 19.5 그대로 그림), 가이드 출구 필렛 R3 → 안쪽 3.5 | 만족 |
| D-167 ② 출구 장력 ≤ 20 N | 18.1 N(설계 손계산, 형상 지시대로라 그대로) | 만족 |
| D-168 풀림량–봉제 길이 차 ≤ 1 %(임시) | ≤ 0.25 %(설계 측정 unwind.json, 줄 경로 = 지시 좌표) | 만족 |
| D-169 비틀림 가장자리 늘어남 ≤ 1 % | 0.50 %(242 mm/31) | 만족 |

### 5-3. 그 밖
- 새 구매품 0, 볼트 0 → stepcheck·볼트 검사 대상 없음. P_M05_GUIDE는 가공품(PA12 출력), 하중 경로 변화 없음 → 임시 STEP 없음.
- 재질: 새 바디 Default(작업 대상 모형, BOM 밖) — matcheck 대상 아님.
- 숨김: 조각·SEAM 140(의도), 검사 때 모두 켬.
- 서명: sigpatch 바뀜 145(TL 4·가이드·조각 140), 없어짐 11(TAPEWAY 2·TAPE 4·옛 SEAM 경로 4·옛 가이드 경로 1) → 마지막 저장본 해시로.

## 6. 사이클 영상

명령 `motion.export_animation`, CLI `solidcraft-cli run anim/anim_<연구>.json --in FSAP_v2.10.0.sc --results`(--save 없음). 첫 단계에서 그 매트·조각·TL_* 켬, 조인트·스케치 숨김. 엔진이 800×500에서 samples ≤ 167만 받아(오류 "`samples` must be 2…167 for 800 × 500 frames") 167로 함.

| 연구 | ① 전체 GIF | frames | bytes | ② 바늘 근처 PNG 폴더 | frames | bytes | stopped |
|---|---|---|---|---|---|---|---|
| CYCLE_L | [CYCLE_L_all.gif](../../../tools/out/mech_SIM-01/anim/CYCLE_L_all.gif) | 167 | 1,212,669 | tools/out/mech_SIM-01/anim/CYCLE_L_needle/ | 167 | 55,229,345 | null |
| CYCLE_S | [CYCLE_S_all.gif](../../../tools/out/mech_SIM-01/anim/CYCLE_S_all.gif) | 167 | 278,177 | tools/out/mech_SIM-01/anim/CYCLE_S_needle/ | 167 | 69,074,000 | null |
| CYCLE_G1 | [CYCLE_G1_all.gif](../../../tools/out/mech_SIM-01/anim/CYCLE_G1_all.gif) | 167 | 1,139,848 | tools/out/mech_SIM-01/anim/CYCLE_G1_needle/ | 167 | 60,126,357 | null |
| CYCLE_G2 | [CYCLE_G2_all.gif](../../../tools/out/mech_SIM-01/anim/CYCLE_G2_all.gif) | 167 | 1,012,690 | tools/out/mech_SIM-01/anim/CYCLE_G2_needle/ | 167 | 58,707,119 | null |
| CYCLE_V | [CYCLE_V_all.gif](../../../tools/out/mech_SIM-01/anim/CYCLE_V_all.gif) | 167 | 1,101,577 | tools/out/mech_SIM-01/anim/CYCLE_V_needle/ | 167 | 60,175,683 | null |

합격(지시 8항): 10개 모두 frames = samples(167), bytes > 0, stopped_at·stopped_by_contact null. 결과 `tools/out/mech_SIM-01/anim/anim_results.json`. 렌더러 gpu. 판정은 5절 수치(E-16).

## 7. 못 한 것·벗어남

- L 조각 2개 155.2 mm(기준 ≤150), L 첫 모서리 자름 13.5 mm(기준 20): 다시 자르지 않음(SIM-01-M3).
- 영상 samples 167(지시 300): 엔진 한계.
- TL_TWIST 부피 +0.7 %(지시 7,475.5): 끝면이 경로에 수직(1.07° 기울어짐) — 프로브와 단면 방향 차. bbox X·Y는 프로브와 같음.
- 경로 스케치 dof 0 아님(점 고정 없음): 작업 대상 모형 경로.
- edit.json은 보낸 명령을 순서대로 이은 기록(다시 돌려 확인하지 않음 — 직렬 과제).
- 제어 순서 제약: 없음(새 구동 없음). 테이프 굽힘·바인더 출구 꺾임·모서리 주름은 7절.

## 워크플로우 메모

- `timeline.delete`(앞쪽 피처)의 답이 MCP 시간 초과로 사라져 `failing`(뒤 BodyTransfer 2개)을 못 봤고, CLI 열기에서야 "2 timeline feature(s) failed"로 드러나 지움·저장·CLI를 한 번 더 했다. 앞쪽 피처를 지우는 명령은 batch에 넣지 말고 단독으로 보내 `pending`으로 결과(failing)를 꼭 받는 규칙이 후보.
- `motion.study`는 keys를 통째로 바꿔(키 8개만 주면 8개가 됨) 조인트를 더할 때마다 옛 키 수백 점을 다시 보내야 한다. 키 더하기·바꾸기 명령이 있으면 연구 편집이 수십 배 가벼워진다.
- split_body로 생긴 바디가 원래 컴포넌트가 아닌 루트에, 원래 컴포넌트 지역 좌표로 놓였다(WP_TAPE_* +6.5 X 어긋남). 다른 컴포넌트 바디를 자를 때 생긴 바디 bbox를 원래와 비교하는 확인이 필요.
- body.rename 한 번이 피처가 쌓일수록 1 → 10 s로 늘었다. 많은 조각을 만들 때는 이름 없이 만든 뒤 bbox로 찾는 방식이 빠를 수 있다.
- motion.export_animation samples 상한이 크기에 따라 다르다(800×500에서 167). 설계 지시의 300은 시험 출력(3프레임)으로 잡히지 않았다.
