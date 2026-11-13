# RX-06R 모델링 보고 — U4 X축 볼나사·손잡이 빼기, 레일 + 블록 + 볼트 잠금 (모델링부, 2026-11-13)

요약(10줄 안):
- 저장 `3D_Modeling/FSAP_v2.15.0.sc`(앞 v2.14.0, 가운데 자리 +1 — 컴포넌트 5개 없어지고 볼트 컴포넌트 6개 생김). 통로 MCP(앱), `tools/config.json` doc·`tools/machine.json` 고침.
- **걷어 냄**: 볼나사 축·너트·BSW20(4바디)·BUN20(2바디)·스페이서 F·S·손잡이·너트 볼트 CB6-20 ×4 = 15바디, 빈 컴포넌트 5, 조인트 `J_U4_XSCREW`, 강체 조인트 8, motion link 1(36 → 35). 캐리지 너트 귀·구멍 5.
- **새로**: 잠금 날 `P_RX06R_LOCK_BLADE_판금`(SUS304 t2, 판금 기능 Z자, 전개 142.55 × 213, 58,633.9 mm³), 누름 판 `P_RX06R_LOCK_CLAMP_레이저`(SUS304 t3, 6,457.5 mm³), 잠금 볼트 `CB5-16_RX06R_LOCK_1·_2`, 날 볼트 `CB5-12_RX06R_BLADE_1~4`(실물 STEP).
- **고침**: 캐리지 웹 윗끝 Z 565 → 482 + M5 탭 2(383,445.8 mm³), 레일 2줄을 실물 STEP 자른 `SSEB13-220_RX06_RAIL`(X −335~−115, 17,180.23 mm³ ×2 — 레일 ↔ 블록 겹침 0), 보 앞벽 M5 탭 4(보 −440.0 mm³).
- 조인트: `J_U4_X` 0~95 그대로. 따라 움직이는 묶음 74 occurrence(77 − 5 + 2). `joint.list` floating 0 · errors 0 · conflicts 0, 조인트 587 → 584.
- 과제 범위 검사(truncated false): J_U4_X 0 · 47.5 · 95(PRESS 13.006 · STOP 0) + J_U4_X 0에서 PRESS 4 × STOP 2 = **10자세**에서 새 겹침 0(11바디 × 이웃 81, 11바디끼리, × 보). **24자세 가운데 14자세(X 47.5·95 × PRESS·STOP 변형)는 못 봄**(4·7절).
- 지시와 달리 한 것 2: 보 탭을 `U1_FRAME` 활성 원통 cut이 아니라 LITE의 앞쪽 탭 스케치 `Sketch15`에 원 4개로 넣음(끝에서 자르면 실패하거나 joint.drive마다 +270 s). 레일은 지시 순서를 한 번의 `timeline.delete`로 묶음.
- 미완·알릴 것은 7절.

## 1. 한 일 (지시서 번호 순)

| 지시 | 한 것 | 확인 수치 |
|---|---|---|
| 0 문서 | `running` 빈 목록 → 열린 문서 `FSAP_v2.14.0` dirty false · 타임라인 3,717 · 바디 882 · 오류 0 · 경고 55. `motion.play REST 0` moved false. `edit.checkpoint` 18. 루트 이름 `FSAP_v2.15.0`·설명 고치고 `save {path: FSAP_v2.15.0.sc}`(5,658,157 B), config.json doc 고침 | E-05 "형상이 바뀐 저장은 … 다른 이름으로 저장" |
| 1 걷어 내기 | `joint.delete {link: 35}` → `joint.delete` 98014·97992·97993·97999·98012 → `selection.delete {occurrences: [97906, 97981, 97982, 97983]}`(강체 98000~98003 같이 지워짐) → `timeline.delete` 22피처 한 번(37.2 s) → `component.delete` 5개 | 바디 이름에 BSS2020·BSW20·BUN20·HANDLE·P_RX06_SPACER 0, `J_U4_XSCREW` 없음, 링크 36 → 35, 그 뒤 실패 피처 0. 빈 컴포넌트는 20개 그대로(모두 작업 전부터 있던 조인트 받침·STEP 하위 노드 — M02R 보고 2절), RX-06 것 0 |
| 2 캐리지 | `sketch.edit 97926` → `sketch.move_point l2.end → (107, 482)`, `l3.end → (95, 482)`(한 번 약 37 s) → U4_XCAR 활성 → `solid.cylinder` r 2.1 × 12.2 축 Y cut @ (−225, 94.9, 468)·(−140, 94.9, 468) | bbox (−240, 45, 250)~(−125, 107, 482), **383,445.75 mm³**(기대 383,446 ± 0.2 %), 1,027.6 g A5052, 면 20(원통 8) |
| 3 레일 | Remove86·Box335·BodyTransfer583을 1의 `timeline.delete`에 같이 넣음 → RAIL 컴포넌트 활성 `solid.box cut`(RX06R_RAIL_CUT_220, 0.46 s) → `body.rename` → `component.move_bodies {component_path: [97895, 97897]}` | `RAIL_SSEB13-570:1` X −335~−115 · Y 112.5~120 · Z 260~272, `:2` Z 434~446, 각 **17,180.23 mm³** · 22.16 g · 면 53. 레일 2 × 블록 4 겹침 0(4절) |
| 4 보 탭 | `Sketch15`(96774, LITE가 보 탭을 모아 둔 스케치, Box16 바로 뒤)에 원 r 2.1 ×4 @ 스케치 (562, −315·−255·−195·−135) = 월드 (X −315·−255·−195·−135, Z 562). `Extrude143`(profiles all, cut 11, targets P_M07_BEAM)이 Y 119~130을 뚫음 | 보 34,452,386.28 → **34,451,946.24 mm³**(−440.0, 계산 4 × π 2.1² × 8 = 443.3), 원통 면 114 → 118, 오류 0. 과정은 5절 |
| 5 잠금 날 | U4_XAXIS 활성 → `sheet.manage_rules SUS304_t2_R2`(t 2, R 2) → 스케치 `SK_RX06R_LOCK_BLADE`(평면 X −335, x = 월드 Y · y = 월드 Z) 선 (120, 577)–(120, 543)–(94.5, 543)–(94.5, 457) → `sheet.flange contour` 213 → 긴 구멍(상자 183 × 5.5 + 원통 r 2.75 ×2) · 고정 구멍 r 2.75 ×4 → SUS304 | bbox (−335, 92.5, 457)~(−122, 120, 577), **58,633.89 mm³**(계산 58,635), 464.97 g, `sheet_metal` true. `sheet.flat_pattern`: 전개 142.55 × 213, 굽힘 2(위 90°·아래 90°, R 2, K 0.44), 컷아웃 5(원 4 + 긴 구멍 1) — `tools/out/mech_RX-06R/model/blade_flat_pattern.json` |
| 6 누름 판 | U4_XCAR 활성 `solid.box` corner (−237.5, 89.3, 458) 110 × 3 × 20 → r 2.75 ×2 cut → SUS304 | **6,457.47 mm³**(기대 6,457.5), 51.21 g, bbox (−237.5, 89.3, 458)~(−127.5, 92.3, 478) |
| 7 볼트 | 작은 설계 `model/d_<이름>.sc`(CLI, STEP 1개씩, 로컬 +x → 월드 +Y) → `component.insert_design`(루트, translate) → `break_link` → `joint.rigid_group` | LOCK_1·_2: Y 84.3~105.3(머리 밑 89.3, 끝 105.3), 중심 (−225·−140, 468), 554.95 mm³. BLADE_1~4: Y 113~130(머리 밑 118), 중심 (−315·−255·−195·−135, 562), 476.41 mm³. 강체 98273·98274(U4_XCAR), 98275~98278(U4_XAXIS) |
| 8 조인트 | `J_U4_X` 그대로. `joint.drive` 0 → 47.5 → 95 → 0 | 3절 |
| 9 검사 | 4절 | |
| 10 machine.json | `J_U4_XSCREW` 지움, `U4_XAXIS`·`U4_XCAR` parts·메모, `J_U4_X` 메모, doc, `_history` 1줄, 기준선 1줄(새 볼트 나사 물림). 상태 `SETUP_D1_195` 그대로 | `tools/out/mech_RX-06R/model/patch_machine.py` |
| 11 저장 | 6절 | |
| 12·13 문서 | 설계검토서·BOM·결정로그·자료대기는 문서 담당 몫. 모델에서 바뀐 수치는 8절 | |

### 좌표(월드, REST)

| 부품 | 묶임 | X | Y | Z | 부피 mm³ | 질량 g | 재질 |
|---|---|---|---|---|---|---|---|
| `P_RX06R_LOCK_BLADE_판금` | U4_XAXIS(고정) | −335~−122 | 92.5~120 | 457~577 | 58,633.89 | 464.97 | SUS304 |
| `P_RX06R_LOCK_CLAMP_레이저` | U4_XCAR | −237.5~−127.5 | 89.3~92.3 | 458~478 | 6,457.47 | 51.21 | SUS304 |
| `CB5-16_RX06R_LOCK_1·_2` | U4_XCAR 강체 | −229.25~−220.75 · −144.25~−135.75 | 84.3~105.3 | 463.75~472.25 | 554.95 | 0.72 | Default(STEP) |
| `CB5-12_RX06R_BLADE_1~4` | U4_XAXIS 강체 | 중심 −315·−255·−195·−135 ± 4.25 | 113~130 | 557.75~566.25 | 476.41 | 0.61 | Default(STEP) |
| `P_RX06_CARRIAGE` | U4_XCAR | −240~−125 | 45~107 | 250~482 | 383,445.75 | 1,027.63 | A5052 |
| `SSEB13-220_RX06_RAIL` ×2 | RAIL_SSEB13-570:1·:2 | −335~−115 | 112.5~120 | 260~272 · 434~446 | 17,180.23 | 22.16 | Default(STEP) |
| `P_M07_BEAM` | U1_FRAME | −2380~1230 | 120~320 | 250~650 | 34,451,946.24 | 270,447.78 | Steel |

## 2. 지운 것

| 무엇 | id | 방법 |
|---|---|---|
| motion link J_U4_X → J_U4_XSCREW 18°/mm | index 35 | `joint.delete {link}` |
| 조인트 `J_U4_XSCREW` | 98014 | `joint.delete` |
| 강체 조인트 8 | 97992·97993·97999·98012, 98000~98003 | `joint.delete` 4 + occurrence와 함께 4 |
| occurrence `CB6-20_M03_CAR:5~:8` | 97906·97981·97982·97983 | `selection.delete {occurrences}`. 컴포넌트 8723·:1~:4(U5_CAR)는 남음(occurrence 4) |
| 피처 22 | 97905·97915~97922(나사 부품·축·손잡이), 97942·97943·97946·97947(스페이서 F·S와 옮김), 97928~97933(너트 귀·구멍 5), 97923·97924·97925(Remove86·그린 레일 상자·옮김) | `timeline.delete` 한 번 |
| 컴포넌트 5 | BSW20_RX06(97903, 하위 BSW20_c 포함)·BUN20_RX06(97907)·BSS2020-1100_RX06_NUT(97911)·BSS2020-1100_RX06(97909)·STEP대기_HANDLE_D50(97913) | `component.delete`(피처를 먼저 지워야 됨 — "component supplies a recorded body transfer outside this subtree") |

## 3. 조인트 자기 점검 (E-15 "따라 움직인 부품이 그 유닛 부품 전부인지 … 수치로 확인")

- 조인트 그래프(`model/joint_list_after.json`에서 98013을 끊고 U4_XCAR:1에 이어진 것): **74 occurrence** = 측정 77 − 5(너트 97912, 너트 볼트 97906·97981~97983) + 2(잠금 볼트 98256·98259). U1_FRAME(2)는 안 들어감.
- `joint.drive J_U4_X 47.5`(실측, 모두 X −47.5): 캐리지 X −287.5~−172.5, 누름 판 −285~−175, 잠금 볼트 중심 −272.5·−187.5, 블록 :1 −285.45~−251.55, P_M02_BASE −377.5~−187.5, RX-08 U4 쪽 관 `TU0604_M08P_RX08_A_U4` X −332.5~−213.5 · `_B_U4` −267.0~−213.5(따라감). **안 움직임**: 날 (−335~−122), 날 볼트, 레일 (−335~−115), 멈춤 A·B, 고정 관 U4_A2.
- 행정 끝: J 95에서 블록 끝 ↔ `P_RX06_STOP_A`, J 0에서 ↔ `P_RX06_STOP_B`(RX-06 그대로, 4절 틈).
- `joint.drive J_U4_X` 한 번: 47.5로 약 13분(보 탭을 끝에 원통 cut 4개로 둔 상태), 95·0으로는 보 탭을 앞쪽 스케치로 옮긴 뒤 각각 약 10~11분·약 11~13분(뒤쪽은 `motion.play REST 0`·숨김 포함, MCP 호출이 300 s에 끊겨 `running`으로 잰 값). 링크를 지워도 줄지 않았다 — 원인은 링크가 아니라 구동 때마다 타임라인 2,798번째(Combine41)부터 끝까지 917피처를 다시 계산하는 것이다(5절).

## 4. 과제 범위 검사 (E-17, `inspect.clearance`, 앱)

대상 A(11): 캐리지·날·누름 판·잠금 볼트 2·날 볼트 4·레일 2. 이웃 B(81): 측정부 `against_names.json`에서 지운 15바디·A·보·긴 고정 관 9줄을 뺀 것(블록 4, 멈춤 2, `P_M03_IDLER_BRKT`와 아이들러 풀리·베어링·벨트, U5 레일 `SV2RL28-1800_RAIL`, 클램프 L_5·F_5·L_6과 볼트 PY:18·19·28~31, `P_M02_BASE`, 발 볼트 6, U4_WHEEL_N 묶음(그네·피벗 브래킷·스프링 탭·실린더·스토퍼 브래킷), RX-08 U4 쪽 관 2줄, 헤드 임시 상자). 목록 `model/check_lists.json`.

| 자세 (PRESS 13.006 · STOP 0) | A × B (clearance 0) | A끼리 (clearance 0.75) | 판정 |
|---|---|---|---|
| J_U4_X 47.5 | overlaps **0**, 쌍 27(가지치기 864), unchecked 0, truncated false, 25.8 s | overlaps **0**. 맞닿음 0.0: 날 ↔ 날 볼트 ×4(머리 좌면), 누름 판 ↔ 잠금 볼트 ×2(머리 좌면). 틈: 날 ↔ 누름 판 **0.20**, 날 ↔ 잠금 볼트 **0.25**(긴 구멍 5.5 ↔ Ø5), 날 ↔ 캐리지 웹 **0.50**(허용 0.3~0.7). unchecked 2 = 캐리지 ↔ 잠금 볼트(boolean Intersect no result — 탭 Ø4.2에 Ø5 축이 같은 축으로 물린 나사 물림, M-08 기준선) | 합격 |
| J_U4_X 95 | overlaps **0**, 쌍 27(가지치기 864, 다시 씀 2), unchecked 0, truncated false, 17.8 s | overlaps **0**(clearance 0.15). 맞닿음 0.0: 날 ↔ 날 볼트 ×4, 누름 판 ↔ 잠금 볼트 ×2(잠금 볼트 좌면 점 X −324.0·−239.2 = 47.5 때보다 −47.5). 날 ↔ 잠금 볼트·누름 판·웹은 0.15보다 멂(틈 0.25·0.2·0.5 그대로, 긴 구멍 끝 여유 1.5). unchecked 2 = 캐리지 ↔ 잠금 볼트(나사 물림) | 합격 |
| J_U4_X 0 (REST) | overlaps 1: `P_M02_BASE` ↔ `P_RX06_CARRIAGE` **0.0276 mm³**(넓이 103.1 mm², 두께 0.0005 mm, 자리 X −165.1~−157.0 · Y 89.9~98.0 · Z 250.0000~250.0005). 쌍 27, unchecked 0, truncated false, 25.6 s | overlaps **0**(clearance 0), 쌍 13, unchecked 2 = 캐리지 ↔ 잠금 볼트(나사 물림) | 새 겹침 0 — 0.0276 mm³은 이번에 안 건드린 자리의 맞닿음(아래) |

- × 보(`P_M07_BEAM`, 날·날 볼트 4·레일 2·캐리지·누름 판, 고정끼리라 한 번): overlaps **0**, 쌍 7, truncated false, unchecked 4 = 보 ↔ 날 볼트 ×4(나사 물림 자리, boolean no result), **705.9 s**. 날 ↔ 보·레일 ↔ 보 겹침 0.
- 완료 판정 ⑤: 레일 2 × 블록 4 겹침 0(RX-06 기준선 178.86 mm³ ×4 없어짐).
- 완료 판정 ④: RX-08 U4 쪽 관 2줄은 캐리지 묶음과 함께 움직였고(3절) 세 자세에서 A와 겹침 0.
- 긴 고정 관(U4_A2·U4_B·U5_A2·U5_B·U6·U7·RX08_A·B)은 against에 넣지 않았다. 새 부품 자리(Z ≥ 457, Y 84.3~120)와는 설계 5-1의 중심선 값으로 14(Z)·10.5(Y) 떨어져 있다. 볼트 렌치 길 프로브에서 U4_A2·U4_B·U5_A2·U5_B를 넣어 다시 봤다(아래).
- J_U4_PRESS 3.751·0·−4.11 × J_U4_STOP 20 자세: **J_U4_X 0에서 8조합 모두 봄**(저장본 CLI `model/grid_press_stop_1·2.json`, 구동 한 번 0.2~0.3 s): PRESS 13.006·3.751·0·−4.11 × STOP 0·20 — A × B overlaps는 8조합 모두 위 `P_M02_BASE` ↔ `P_RX06_CARRIAGE` 0.0276 mm³ 하나뿐, unchecked 0, truncated false(`model/grid1_out.json`·`grid2_out.json`). **J_U4_X 47.5·95에서는 PRESS 13.006 · STOP 0만 봄**(위 표). 나머지 14자세(47.5·95 × PRESS 3.751·0·−4.11 × STOP 0·20, 47.5·95 × PRESS 13.006 × STOP 20)는 저장본 CLI(`model/gridx_47_5.json`·`gridx_95.json`)를 띄웠으나 이 보고를 쓸 때까지 안 끝남(7절).
  - 못 본 14자세의 위험 어림(판정 아님): 움직이는 A(캐리지·누름 판·잠금 볼트) ↔ 캐리지에 매달린 묶음은 J_U4_X와 무관하고(같이 평행 이동) X 0의 8조합에서 봄. 움직이는 A ↔ 고정 이웃은 PRESS·STOP과 무관하고 X 0·47.5·95에서 봄. 고정 A(날·날 볼트·레일, Z ≥ 260) ↔ PRESS·STOP으로 움직이는 부품(그네 윗끝 Z 232.2, 윗판 P_M02_BASE Z 242~250 아래)은 Z로 27.8 이상 떨어져 있다.
- `P_M02_BASE` ↔ `P_RX06_CARRIAGE` 0.0276 mm³: **작업 전 v2.14.0 저장본에서도 같은 값**(CLI `model/base_sliver_out.json`: 0.027612 mm³, 같은 자리 X −165.06~−156.96 · Y 89.95~98.05 · Z 250.0000~250.0005). RX-06 때 윗판의 옛 관 구멍을 메운 피처(`gen_v2_rx06.py` 154줄, r 4.05 원통 join, 경고 "Boolean retry: tool displacement 7.6e-4 mm")가 윗판 윗면 위로 0.0005 mm 올라와 캐리지 발 밑면과 겹친 맞닿음이다. 이번에 만든 것이 아니고 두께 0.5 µm라 기준선(M-08) 후보로 적는다(J_U4_X 47.5·95에서는 0.01 mm³ 아래라 안 나옴).

### 볼트 검사 (안내서 '볼트 검사', M-01 "머리 위 축 방향 빈 공간 ≥ 볼트 길이 + 5 mm" — 프로브 max(30, L + 5) = 30)

저장본 CLI(`model/savecheck_probe.json`, 원본 안 바뀜): 프로브 = 머리 위 −Y로 Ø8.5 × 30 원통.

| 프로브 | 자리 | 대상 | 결과 |
|---|---|---|---|
| 잠금 볼트 ×2 | (X −225·−140, Z 468), Y 54.3~84.3 | A 11 + B 81 + 고정 관 U4_A2·U4_B·U5_A2·U5_B = 96바디 | 겹침 **0** |
| 잠금 볼트 쓸림(J 0~95) | X −324.25~−135.75 · Y 54.3~84.3 · Z 463.75~472.25 상자 | 같음 | 겹침 **0** |
| 날 고정 볼트 ×4 | (X −315·−255·−195·−135, Z 562), Y 83~113 | 같음 | 겹침 **0** |

쌍 28(가지치기 644), unchecked 0, truncated false, 1.4 s. 빈 구멍 0(탭 6·통과 구멍 6·긴 구멍 1에 볼트 6), 같은 자리 중복 볼트 0, 볼트 방향 = 탭 방향(+Y). 6개 모두 앞(−Y, 작업자 쪽)에서 4 mm 육각 렌치로 풀린다(M-02).

손계산(`handcalc.py`, 검증부와 같은 도구):

| 볼트 | 인자 | 결과 |
|---|---|---|
| CB5-16 잠금 ×2 | `--d 5 --pitch 0.8 --le 10.3 --load 0 --torque 3 --base A5052 --dw 8.5 --dh 5.5` | 예압 3,000 N, 물림 2.06d, 조임 볼트 응력 SF 4.69 · 좌면 2.31 · 암나사 전단 2.37, ok true |
| CB5-12 날 고정 ×4 | `--d 5 --pitch 0.8 --le 8 --load 0 --torque 4 --base SS400 --dw 8.5 --dh 5.5` | 예압 4,000 N, 물림 1.6d, 조임 볼트 응력 SF 3.51 · 좌면 4.04 · 암나사 전단 1.73, ok true |

잠금 유지력·날 굽힘·블록 하중은 설계 4절 값 그대로다(형상이 지시대로 나옴: 날 t2 × 213, 선반~볼트 75, 틈 0.5).

## 5. 보 탭 — 지시와 달리 한 곳과 이유

지시 4 "P_M07_BEAM 앞벽에 Ø4.2 관통 4개 … U1_FRAME 안에서".

| 시도 | 결과 |
|---|---|
| U1_FRAME 활성 + `solid.cylinder` r 2.1 × 8.2, 바닥 Y 119.9 | **실패** "boolean Cut: the operation failed: no result"(115.7 s) — batch가 되돌아가 캐리지 탭·누름 판을 다시 그림 |
| 루트에서 바닥을 면 위(Y 120)에 둔 원통 r 2.1 × 10(M02R F_6 방식) ×4 | 통과. 하나 55~65 s, 경고 "Boolean retry: tool displacement 7.27e-3 mm". 보 −439.8 mm³ |
| 끝에서 스케치 원 4 + `solid.extrude` cut 한 번 | **실패**(272.8 s) "the target's face 227 is planar but its mesh is not flat and the tool has 8 curved faces" |
| 원통 4개를 도구로 `solid.combine` cut 한 번 | 통과하지만 278.5 s(원통 4번 247 s보다 느림) → `undo` ×6으로 되돌림 |
| **고른 것**: LITE(v2.8.10)의 앞쪽 탭 스케치 `Sketch15`(index 35, Box16 바로 뒤)에 원 4개. `sketch.edit {restore_marker: null}` → 원 4 → `sketch.finish`(전체 재계산 한 번, 약 16~19분) | 통과. `Extrude143` 0.33 s, 경고 55 → **54**, 오류 0. 보 부피는 원통 방식과 같다(34,451,946.24 ↔ 34,451,946.45) |

- 왜 옮겼나: `joint.drive J_U4_X` 전후로 피처 계산 시간(`document.inspect`의 ms)을 비교하니 index 2,798(Combine41)부터 끝까지 917피처가 구동 때마다 다시 계산된다(합 794 s). 끝에 둔 보 탭 4개(271 s)가 여기 들어가 구동 한 번이 약 8.7분 → 13.2분이 됐다. 앞쪽 스케치에 넣으면 구동 때 다시 계산되지 않고 열기 시간도 늘지 않는다(E-04 '모델 무게').
- U1_FRAME은 접지라 탭이 루트 쪽 피처여도 움직이지 않는다(RX-06-F1이 걱정한 것은 움직이는 컴포넌트의 바디를 루트 피처로 자르는 경우). 구멍은 Y 119~130(벽 Y 120~128 관통 + 2)로, 지시 "Y 120~128 관통"과 형상이 같다.

## 6. 저장 전 검사·저장

| 항목 | 결과 |
|---|---|
| 타임라인 | 3,717피처, 오류 0, 경고 54(작업 전 55 — 보 탭을 앞쪽 스케치로 넣은 뒤 재계산에서 1 줄어듦), 되감긴 피처 0 |
| 안 묶인 부품(E-11) | `joint.list` floating **0**, errors 0, conflicts 0. 조인트 584(587 − 9 + 6), 링크 35. 새 볼트 6은 강체 98273~98278 |
| 숨김(E-11) | 숨긴 바디 97(작업 전 97과 같음 — 매트·테이프 모형의 안 쓰는 변형), 새로 숨긴 것 0. 조인트 글리프·스케치 숨김(스케치 299 가운데 보이는 것 0) |
| 재질(E-09) | 날·누름 판 SUS304, 캐리지 A5052, 보 Steel. `matcheck.py`: 불일치 2건은 작업 전부터 있던 우레탄 표기(P_M02·M03_WHEEL_TREAD 'Urethane_A70' ↔ BOM '우레탄 A70'), 새 불일치 0. BOM에 없는 부품 = 새 가공품 2(문서 담당이 행 추가) |
| BOM(`assembly.bom flat`) | SSEB13-220 1(조립), CB6-20 6(작업 전 10 − 4), CB5-16 492 · CB5-12 77(+2 · +4 포함), BSS2020·BSW20·BUN20·HDLC 행 없음 — `model/bom_final.json` |
| 대기 자세 | `joint.drive J_U4_X 0` → `motion.play REST 0`. J_U4_X 0 · J_U4_PRESS 13.006 · J_U4_STOP 0. P_M02_BASE X −330~−140(작업 전과 같음), RX-08 U4 쪽 관 A_U4 X −285.0~−166.0 |
| 저장 | `save {path: 3D_Modeling/FSAP_v2.15.0.sc}` 5,632,952 B. 저장 뒤 앱 dirty **false**, 경로 v2.15.0, 타임라인 3,717, 바디 정의 879. 저장 뒤 편집 없음(읽기·내보내기만) |
| 저장본 확인(안내서 '저장 확인', CLI) | 저장본에 `solidcraft-cli run model/savecheck_probe.json --in FSAP_v2.15.0.sc --results`(저장 안 함): 21바디(A 11 + 보 + P_M02_BASE·멈춤 2·블록·RX-08 U4 쪽 관 2 + 헤드·아이들러 브래킷·그네) bbox·부피가 앱 값과 **차 0**, 조인트 584 · 링크 35 · floating 0, J_U4_X 0 · PRESS 13.006 · STOP 0. 열기 약 1,120 s(CLI 4개를 함께 열어 느림) — `model/savecheck_out.json` |
| 서명(E-17) | `ledger.py sigpatch --parts out/mech_RX-06R/sig_changed.json --removed <21> --bolts out/mech_RX-06R/bolts_changed.json` → 바뀜 12, 없어짐 21(서명 17 + 체결 이름 4), 전체 3,188(앱 바디 수 3,188과 같음). `sigcheck` reuse. `bolts.json` 1,217 → 1,219 |
| 임시 STEP(해석용, E-06 예외) | `tools/out/mech_RX-06R/stepout/P_RX06R_LOCK_BLADE.step`(39,870 B) · `P_RX06R_LOCK_CLAMP.step`(15,059 B) · `P_RX06_CARRIAGE.step`(50,141 B) |
| 스크린샷 | 저장본 CLI `solidcraft-cli snapshot --view front` → `tools/out/mech_RX-06R/shot_v2150_front.png`(50,856 B, 열어 보지 않음 — E-16) |

## 7. 미완·알릴 것

| 무엇 | 상태 | 근거·넘길 것 |
|---|---|---|
| 과제 범위 검사 24자세 가운데 14자세(J_U4_X 47.5·95 × PRESS·STOP 변형) | **못 봄** | 앱 `joint.drive J_U4_X` 한 번이 10~13분이라 X 세 점은 PRESS 13.006 · STOP 0으로만 돌았다. PRESS·STOP 변형은 저장본 CLI에서 X 0의 8조합만 끝남. X 47.5·95용 CLI 2개(`model/gridx_47_5.json`·`gridx_95.json` → `gridx_*_out.json`)는 20분 넘게 안 끝남 — 결과 파일이 생겼으면 검도가 그것부터 읽는다(E-21). 저장본 CLI에서 PRESS·STOP 구동은 0.2~0.3 s |
| J_U4_X 25·75 % 점 | 안 봄 | 지시는 0·47.5·95. 라운드 끝 회귀 몫(M02R·RX-08 검도와 같음) |
| 해석 | 못 함 — 환경 없음(자료대기 D-16) | 손계산(4절·설계 4절). 임시 STEP 3개는 냄 |
| 보 탭 자리 | 지시와 다름(5절) | 형상은 같음(Ø4.2, 벽 관통). `U1_FRAME` 활성 cut은 실패 |
| 스크린샷 | 저장본 CLI `tools/out/mech_RX-06R/shot_v2150_front.png`(1200 × 800, 열어 보지 않음) | E-16 |
| 디테일(기록만) | 8절 마지막 줄 | E-02 |
| 모델 무게 | 저장본 CLI 열기 약 1,120 s(4개 동시)·앱 `joint.drive J_U4_X` 10~13분·전체 재계산 약 16~20분 — 상한 240 s를 크게 넘는다. LITE는 두 번 했으므로(실행 지시 f) 다시 넣지 않고 워크플로우 메모 1에 원인을 적음 | E-04 |
| 규칙 예외 요청 | 없음 | E-14 |

## 8. 문서 담당에게 넘기는 수치 (BOM·설계검토서·결정로그·자료대기)

| 문서 | 고칠 것 |
|---|---|
| BOM 구매품 | 삭제: BSS2020-1100(축 + 너트), BSW20, BUN20, HDLC-D50(임시), CB6-20 −4(U5 대차 4개는 남음). SSEB13-570 → **SSEB13-220**(레일 2 + 블록 4, 비고 "STEP SSEB13-570을 X −115에서 잘라 씀, 구멍 9 피치 25 끝 10"). CB5-16 +2(잠금, 3 N·m), CB5-12 +4(날 고정, 4 N·m) |
| BOM 가공품 | 삭제: P_RX06_SPACER_F·_S. 추가: `P_RX06R_LOCK_BLADE_판금`(SUS304 t2, 굽힘 2 R2, 전개 142.55 × 213, 464.97 g), `P_RX06R_LOCK_CLAMP_레이저`(SUS304 t3 110 × 20, 51.21 g). `P_RX06_CARRIAGE` 1,379.16 → **1,027.63 g**(−351.5), M5 탭 2 추가. `P_M07_BEAM` 비고 "앞벽 M5 탭 4(X −315·−255·−195·−135, Z 562)" |
| 설계검토서 | 제어 제약 3(d₁ 바꾸기는 바퀴 든 상태에서만 / d₂ ≥ d₁ + 240 / 잠금 풀림 센서 없음 — 바꾼 뒤 HMI에 d₁ 입력), 조절 순서 4단계(설계 2절), 조임 3 N·m(잠금)·4 N·m(날 고정) |
| 자료대기·결정로그 | 소멸(C-46): RX-06-E5(BSW15·BUN15), D-190(손잡이 STEP), D-191(축 끝 가공), RX-06-D3(지지 유닛 볼트), RX-06-D6(너트 볼트 컴포넌트 공유). RX-06-E4(레일 실물 STEP) 해결. 후보: SSEB13 '27년 판매종료 예정' 대체 형번 |
| 디테일(기록만, E-02) | 조임 토크 지정, 날–웹 틈 0.5 심 맞춤, d₁ 눈금, 날 판금성 표(M-04)·만드는 법 비교(M-13), RX-06-D1(레일·블록 볼트)·D2(발 볼트 물림)·D4(끝 멈춤 고정) 남음, 레일 +X 끝이 −125 → −115로 10 길어져 끝 멈춤 `P_RX06_STOP_B`(X −127~−125) 바깥으로 레일이 10 나옴(구멍 X −125 자리 살아남) |

## 9. 기록

- 생성기 `tools/gen_v2_rx06r.py` → `tools/out/mech_RX-06R/model/stage_0~10_*.json`, `mini_*.json`(볼트 작은 설계 `d_*.sc`), `tools/out/mech_RX-06R/edit.json`(79단계, 최종 길만)·`edit_meta.json`.
- 검사 원본: `model/joint_list_after.json`·`component_list_after.json`·`names_after.json`·`blade_flat_pattern.json`·`check_lists.json`·`savecheck_probe.json`.
- 해석용 임시 STEP: `tools/out/mech_RX-06R/stepout/`(6절).

## 워크플로우 메모

1. `joint.drive`가 느린 원인은 motion link가 아니었다. 구동 때마다 타임라인의 어느 자리(이 파일 index 2,798)부터 끝까지 전부 다시 계산한다(917피처 794 s). 그 구간에 든 무거운 보 탭(Combine40 103~197 s, Cylinder1219 89~177 s, Cylinder1327·1283·1326 30~87 s)이 구동 시간의 대부분이다. 이 다섯을 LITE 방식(앞쪽 스케치)으로 옮기면 구동·열기가 6분쯤 준다 — 엔진 안내서 '모델 무게'에 "이력 끝의 무거운 불리언은 구동마다 다시 계산된다"를 적으면 좋겠다.
2. 큰 구조물(보)에 대한 `inspect.clearance`는 7쌍에 706 s였다(나사 물림 4쌍은 no result). 탭에 물린 볼트 ↔ 보는 기준선으로 빼고 돌리는 편이 맞다(안내서 '간섭' 3).
3. MCP 호출은 300 s에 끊기고, `batch`가 끊기면 `pending`으로도 결과를 못 받는다(`execute` 하나는 `pending`으로 받음). 5분 넘을 호출은 `execute` 하나씩 보내는 편이 낫다.
4. `sheet.manage_rules`(또는 그 뒤 첫 판금 피처)가 큰 파일에서 전체 재계산(약 20분)을 일으켰다. 판금 규칙은 이력 맨 앞에서 한 번 만들어 두는 편이 낫다.
5. `batch`가 읽기 명령만 담고 실패하면 "undone: N"으로 되돌리는데, 앞 단계가 `edit.undo`였으면 그 undo까지 되돌려(redo) 지운 피처가 살아난다.
6. 지시문 절차 2("먼저 다른 이름으로 저장")와 안내서 '원복'("저장 뒤에는 편집하지 않는다")이 서로 다르게 읽힌다. 이번에는 절차 2대로 먼저 새 번호로 저장하고, 끝에 같은 새 경로로 `save {path}` 했다.
