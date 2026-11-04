# 모델링부 — DC2-04 매트 두께 높이 사슬 (2026-11-04)

요약
- 새 버전 `3D_Modeling/FSAP_v2.3.1.sc`(1,813,157 B, md5 5d24555b…). 기준 v2.3.0. `tools/config.json`·`tools/machine.json` doc → v2.3.1. 생성기 `tools/gen_v2_dc204.py`, 기록 `tools/out/mech_DC2-04/edit.json`(26명령).
- 통로: **CLI**(앱 MCP 안 씀). `running` 실측: 앱에 `inspect.clearance` 하나가 11,948 s째 돌고 있어 모든 MCP 호출이 그 뒤에 줄을 선다(M06과 같은 막힘). 실행 규칙 2 "MCP 호출이 실제로 실패할 때만 CLI" — 막힘을 실패로 봤다.
- 바꾼 부품: `P_M06_BASE` 붙임면 Ø5.5 2 → 세로 장공 5.5 × 중심선 Z 174~184(부피 −330), `P_M05_HOLDER` 날개 A Ø5.5 2 → 세로 장공 Z 304~314(부피 −440), `U3_NEEDLE_PIN` +Z 6(Z 19~116).
- 조인트: 새 slider `J_U6_HGT`(U3_HEAD ↔ U6_SENSOR)·`J_U7_HGT`(U3_HEAD ↔ U7_FIXED) +Z −4~+6, 값 0. 지운 리지드 2(`Rigid Group 2:14`, `Rigid Group 8:4719`). 볼트 4개 U3_HEAD로 옮김. `J_U3_PRESSER` −4~20, `J_U3_NEEDLE` −36~0. floating 0·conflicts 0·errors 0.
- 검사: 과제 범위 겹침 **0**(REST HGT 5점, THICK_6·THICK_16 봉제·칼/접기 15·앞끝 보내기 150, 바늘 −36). 두께 6·16 띠 ↔ 두 바퀴 0.002(접촉), 노루발 0(접촉), 슈 0.5, 바인더 1.0.
- 새 부품 0, 지운 부품 0, 새 구매품 0 → 마지막 자리 +1(E-05).
- 미완: 없음. 외부: 헤드 사양(노루발 봉제 높이 8~18·바늘 위 끝 Z 19, D-10), 해석 환경 없음(D-16).

## 1. 근거 규칙 (원문)
- E-05: "새로 생기거나 없어지는 컴포넌트가 없으면 마지막 자리 +1" → v2.3.0 → **v2.3.1**. 컴포넌트 생김·없어짐 0(볼트 4개는 같은 컴포넌트를 U3_HEAD 밑으로 옮김).
- M-07: "조인트는 실제 구동 관계대로, 볼트는 물린 부품과 같은 그룹" → 장공 볼트 `CB5-12_M06_1·2`·`CB5-12_M05_11·12`는 UPPER 탭에 물리므로 U3_HEAD로(`occurrence.reparent`, 세계 위치 그대로). BASE·HOLDER가 볼트에 대해 미끄러진다.
- M-02: "조정은 장공 + 미는 볼트" → 장공은 이번, 미는 볼트·눈금은 디테일 DC2-04-X1(설계안 그대로).
- E-15: "움직임은 기계 정의의 조인트로만" → `tools/machine.json` 고침(4절).
- 실행 규칙 19: "저장 전에 browser.visibility {visible:false, folder:"joints"}" → 기록 끝에 있음.
- 실행 규칙 2: "앱이 꺼져 있거나 MCP 호출이 실제로 실패할 때만 CLI" → 위 요약.

## 2. 만든·바꾼 것 (세계 mm, 바늘점 원점, 테이블 Z 0, h 0)

| 부품·조인트 | 무엇 | 좌표·값 | 지시와 다른 점 |
|---|---|---|---|
| P_M06_BASE (U6_SENSOR, SUS304 t3) | 스케치 `SK_DC204_BASE_SLOT`(XZ, Y −89) 장공 2, 깊이 5 cut | (X −70, Z 174~184)·(X −32, Z 174~184), 폭 5.5, 끝 R 2.75. 장공 Z 171.25~186.75 → 위 끝 195까지 8.25 ≥ 2.5, 굽힘선 151까지 20.25 ≥ 6 | 없음 |
| P_M05_HOLDER (U7_FIXED, SUS304 t4) | 스케치 `SK_DC204_HOLDER_SLOT`(XZ, Y −89.9) 장공 2, 깊이 4.2 cut | (X 18, Z 304~314)·(X 36, Z 304~314), 폭 5.5. 팔 B 핀 구멍·날개 C 걸쇠 구멍 그대로 | 없음 |
| U3_NEEDLE_PIN (U3_NEEDLE) | `solid.move` +Z 6 | Z 13~110 → 19~116, Ø1.6 그대로 | 없음 |
| J_U6_HGT | slider, a U3_HEAD:1 · b U6_SENSOR:1, 원점 (−51, −90, 180), z +Z, flip, 한계 −4~6, 값 0 | 따라 움직임: U6_SENSOR 전부(BASE·CJ2B16 몸·피팅) + J_U6_SHIFT 밑 U6_SHOE 전부 | **지운 리지드는 U6_SENSOR ↔ U1_FRAME**(`Rigid Group 2:14`, 실측). 지시서는 'U6_SENSOR↔UPPER(U3_HEAD)'. U3_HEAD도 U1_FRAME 리지드라 같은 고정이며, 새 slider는 지시대로 U3_HEAD에 맺었다 |
| J_U7_HGT | slider, a U3_HEAD:1 · b U7_FIXED:1, 원점 (27, −90, 310), z +Z, flip, 한계 −4~6, 값 0 | 따라 움직임: U7_FIXED(HOLDER) + CST_STAGE·CASSETTE·CUT·TUCK·FEED·LATCH | 없음(`Rigid Group 8:4719` 지움) |
| CB5-12_M06_1·2, CB5-12_M05_11·12 | `occurrence.reparent` → U3_HEAD | 자리 그대로(머리 Y −98~−93 / −99~−94, Z 180 / 310) | 없음 |
| J_U3_PRESSER | `joint.limits` −4~20 | 대기 20 그대로 | 없음 |
| J_U3_NEEDLE | `joint.limits` −36~0 | 대기 0, 연구 −30 키 그대로(끝 Z −11) | 없음 |

- "값 0으로 잠근다": SolidCraft slider에는 잠금 칸이 없다. 값 0으로 만들고(`values:[0]`, `joint.drive 0`) 연구에 키를 넣지 않아 사이클에서 움직이지 않는다(motion.play는 키가 있는 조인트만 놓음). 저장본에서 값 0 확인.
- 연구(motion.study)는 고치지 않았다(새 조인트는 setup 조인트라 키 없음).

## 3. 검증 수치 (CLI `run --results` 한 번, 저장 전 `tools/out/mech_DC2-04/model/trial_*`, 214 s, truncated 없음)

움직인 것 87바디(U6_SENSOR·U6_SHOE·U7_TAPE, 볼트 4 제외) + 노루발·바늘 ↔ 고정 198바디(볼트 4 포함, 테이블·매트·위 700 넘는 것 제외), `inspect.clearance` 1 mm.

| 자세 | 겹침 | 1 mm 안 0 맞닿음 | 1 mm 안 가장 가까운 비접촉 |
|---|---|---|---|
| REST, HGT −4 / −1.5 / +1 / +3.5 / +6 (0·25·50·75·100 %) | 0 / 0 / 0 / 0 / 0 | UPPER↔BASE·HOLDER(붙임면), BASE↔CB5-12_M06_1·2, HOLDER↔CB5-12_M05_11·12(머리 자리면) | NOSE↔FOOT 0.5, NOSE↔BINDER 0.5, +6에서 HOLDER↔U7_TAPEWAY_V 0.5(설계안과 같음) |
| 볼트 4 ↔ BASE·HOLDER, HGT −4 · +6 (0.5 mm) | 0 · 0 | 머리 자리면 4 | 장공 끝 — 자루 r 2.5 ↔ 끝 R 2.75 = 0.25 |
| THICK_6 봉제(HGT −4, 노루발 −4, U4 −0.54°, U5_X 800 · LIFT −2, 슈 0) | 0 | 같음 | 같음 |
| THICK_6 칼·접기 15 / 앞끝 보내기 150 | 0 / 0 | 같음 | 같음 |
| THICK_16 봉제(+6, 6, 2.4289°, 800 · 8, 0) | 0 | 같음 | + HOLDER↔TAPEWAY_V 0.5 |
| THICK_16 칼·접기 15 / 앞끝 보내기 150 | 0 / 0 | 같음 | 같음 |
| 바늘 −36(끝 Z −17) ↔ 고정 | 0 | — | 1 mm 안 0 |
| 바늘 0(끝 Z 19) ↔ 고정 (10 mm) | 0 | — | NOSE 1.2, UPPER 밑 125와 9.0(지시 확인값과 같음) |

매트 띠(두께 t + 2 = 이음매 윗면, Z 0~8 · 0~18, 2500×1600) ↔ 움직인 것 + 노루발·바늘 + U4·U5 바디(3 mm):

| 띠 | 겹침 | 노루발 | U4 바퀴 | U5 바퀴 | 슈 | 바인더 | 바늘 |
|---|---|---|---|---|---|---|---|
| 두께 6 (Z 8) | 0 | 0 (밑 Z 8.000) | 0.002 (밑 8.001) | 0.002 (8.001) | 0.5 (8.5) | 1.0 (9.0) | 11 (19.0) |
| 두께 16 (Z 18) | 0 | 0 (18.000) | 0.002 (18.001) | 0.002 (18.001) | 0.5 (18.5) | 1.0 (19.0) | 1.0 (19.0) |

- 두 바퀴 누름 접촉 > 0: U4 θ −0.54 · 2.4289는 한계 −1.867~8.626 안(두께 6에서 레버가 더 내려갈 수 있음 = 실린더 행정 끝 전 접촉), U5 LIFT −2 · 8은 한계 −10~30 안. 바퀴 밑과 띠 사이 0.002는 θ 키 넷째 자리 반올림 — 맞닿음.
- 조인트 자기 점검(E-15): `J_U6_HGT`·`J_U7_HGT` 9 → 6에서 멈춤(BASE Z 126~201, CARR 27~162, SHOE 18.5~51, CJ2B16 132.85~151.15, HOLDER 291~340, CST_PLATE 26~334, GUIDE 44~276, BINDER 19~66 — 모두 +6.000), −9 → −4에서 멈춤(모두 −4.000). 볼트 4는 그대로(UPPER 쪽). `J_U3_PRESSER` −10 → −4(발바닥 Z 8.000), `J_U3_NEEDLE` −50 → −36(끝 Z −17.000). 행정 끝 = 조인트 한계(장공 끝·헤드 사양).
- 측정 노이즈: HGT +6·+9 자세에서 HOLDER·BINDER 부피가 −86·−3 mm³로 나왔고 원위치(0·−4)에서는 저장본과 같다. 움직인 자리의 측정 값이며 형상은 그대로(저장본 32,843.975·165,712.866).
- 숨김(E-11): 기록의 숨김 명령은 조인트 글리프(folder joints)뿐, 바디 숨김 0. 리지드 누락: `joint.list` floating 0, 새 바디 0.
- 재질(E-09): 바꾼 바디 재질 그대로(BASE·HOLDER SUS304, 바늘 Default, 볼트 SCM435). matcheck는 BOM에 v2.3.1 행이 아직 없어 돌리지 않음(실행 규칙 9, BOM은 문서 단계).
- 볼트 검사: 바꾼 볼트 4개는 형번·자리·물림(UPPER 탭 9 / 8) 그대로이고 소속만 바뀜. 장공은 Z 방향뿐이라 머리 앞 렌치 길(−Y)은 M06·M05 때와 같다. 빈 구멍 0(옛 Ø5.5 구멍은 장공에 흡수).

## 4. 기계 정의(`tools/machine.json`, E-15)
- doc → `../3D_Modeling/FSAP_v2.3.1.sc`.
- joints: `J_U6_HGT`(unit U6_SHOE, axis [0,0,1], origin [−51, −90, 180], −4~6, rest 0, setup true)·`J_U7_HGT`(unit U7_TAPE, origin [27, −90, 310], 같음). _note '제품 교체 때 손 조정, 값 = 매트 두께 − 10, 두 조인트는 같은 값, 기계 축 아님, 사이클 연구에서 움직이지 않음'.
- `J_U3_PRESSER` min −4, `J_U3_NEEDLE` min −36, _note 고침.
- `J_U4_PRESS` _note 식 z = 70 + 200·sinθ − 60·cosθ − 12.5·|sinθ|, 키 표 `keys_z` {6 −1.0815, 7 −0.8105, 8 −0.5400, 11 0.3053, 12 0.6101, 16 1.8245, 17 2.1269, 18 2.4289}.
- temp_values D-04 '매트 두께 범위 6~16(임시)'.
- states: `THICK_6`(J_U6_HGT −4, J_U7_HGT −4, J_U3_PRESSER −4, J_U4_PRESS −0.5400, J_U5_X 800, J_U5_LIFT −2, J_U6_SHIFT 0)·`THICK_16`(+6, +6, 6, 2.4289, 800, 8, 0) — 이음매 윗면 접촉 봉제 자세. 나머지 상태에 J_U6_HGT·J_U7_HGT 0을 넣음.
- baseline_overlaps: U4·U5 바퀴 ↔ 테이프 두 줄('깊이 1.0 mm, 부피 0'·'남으면 키 0.310')을 '접촉 추종(J_U4_PRESS θ(z) 식, J_U5_LIFT = z − 10)으로 겹침 0, 맞닿음(부피 0)만 허용 — DC2-04 측정 6자세 최소 틈 0.002~0.134'로 고침(M00-X6).
- units: U6_SENSOR moving true·joints [J_U6_HGT], 볼트 2개 빼서 U3_HEAD parts로. U7_TAPE joints_setup [J_U7_HGT]. U3_HEAD에 장공 볼트 4.
- 고치기 전 사본: `tools/out/mech_DC2-04/model/machine_before.json`.

## 5. 저장·저장 확인·서명
- 저장: `solidcraft-cli run tools/out/mech_DC2-04/edit.json --in 3D_Modeling/FSAP_v2.3.0.sc --save 3D_Modeling/FSAP_v2.3.1.sc`(183 s). 기록 끝 `motion.play REST 0`, 조인트 글리프 숨김, 설명 'DC2-04 mechanism: mat thickness 6-16 height chain, U6/U7 vertical slots and setup sliders, presser -4, needle +6'. 문서 이름은 파일 이름에서 온다(`document.metadata`에 이름 칸 없음, 합치기 보고서와 같음) → FSAP_v2.3.1. J_U6_HGT·J_U7_HGT 0.
- 저장 확인(저장본 CLI, 177 s): 바디 3,754(v2.3.0과 같음), joint.list 157(v2.3.0 157 − 리지드 2 + slider 2), floating·conflicts·errors 0. 바꾸지 않은 UPPER·FOOT·SHOE·CARR·BINDER·CST_PLATE·두 바퀴 bbox·부피가 서명과 같음. BASE 40,670.82(−330 = 장공 2 × 5.5 × 10 × t3), HOLDER 32,843.975(−440 = 2 × 5.5 × 10 × t4), 바늘 Z 19~116.
- 서명: `ledger.py sigpatch --parts tools/out/mech_DC2-04/changed_parts.json(7: 바뀐 3 + 볼트 4 새 경로 U3_HEAD/) --removed U6_SENSOR/CB5-12_M06_1,U6_SENSOR/CB5-12_M06_2,U7_FIXED/CB5-12_M05_11,U7_FIXED/CB5-12_M05_12 --bolts tools/out/mech_DC2-04/changed_bolts.json(4)` → 전체 3,753, sigcheck reuse. 고치기 전 사본 `model/signatures_before.json`·`bolts_before.json`.
- 해석용 임시 STEP: `tools/out/mech_DC2-04/stepout/P_M06_BASE.step`·`P_M05_HOLDER.step`(구멍 → 장공, 하중 경로 같음). 해석 못 함 — 환경 없음(D-16), 손계산은 설계안 4절(장공 마찰 SF 60).
- 스크린샷(사람용, 열지 않음): `tools/out/mech_DC2-04/FSAP_v2.3.1_iso.png`.
- 다시 실행 재료: `tools/out/mech_DC2-04/edit.json`(저장본을 만든 명령 그대로), `edit_meta.json`.

## 6. 디테일 (E-02, 기록만)
- 설계안 DC2-04-X1(높이 조정 미는 볼트·눈금, M-02)·X2(HOLDER 날개 A 구멍 X 36 가장자리–굽힘선 7.25 < 2t 8, M05부터) 그대로.
- DC2-04-M1: HOLDER는 판금 기능이 아닌 프리즘 바디(M05)라 장공도 스케치 slot cut으로 냈다(BASE와 같은 방법). 

## 7. 설계검토서 제어 순서 제약 (U-09, 지시서 그대로)
- (a) 레시피의 매트 두께 t로 h = t − 10을 정하고, 공압을 끈 채 카세트를 장착한 상태에서 `J_U6_HGT`·`J_U7_HGT`를 같은 눈금으로 맞춘다.
- (b) 헤드 노루발 봉제 높이 h, 바늘 위 끝 Z 19 이상은 헤드 조건(D-10).
- (c) 바퀴 누름은 공압 접촉이라 설정값이 없다.

## 8. 못 한 것
- 없음(지시 1~9 모두). 외부: 헤드 사양 D-10, 해석 환경 D-16.

## 워크플로우 메모
- 앱 MCP가 다른 연결의 긴 `inspect.clearance`(11,948 s)로 막혀 M06에 이어 또 CLI로 그렸다. 사용자가 앱 화면으로 보지 못한다. 측정부의 긴 clearance가 앱에 남지 않게 읽기 부서가 끝날 때 `running`을 확인하는 단계가 필요해 보인다.
- 지시서는 U6_SENSOR 리지드 상대를 UPPER(U3_HEAD)로 적었으나 실제는 U1_FRAME이었다. 설계안 지시서에 리지드 상대를 `joint.list` 실측으로 적으면 좋다.
