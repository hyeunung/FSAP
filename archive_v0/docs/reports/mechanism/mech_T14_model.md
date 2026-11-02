# 구동 T14 모델링 — 회전부 높이 사슬 (v0.8.1 → v0.8.2)

모델링부, 2026-11-02. 통로 **MCP**(SolidCraft 앱 실행 중 `solidcraft.exe` 확인, `running`·`inspect_design` 응답 정상, 열린 설계 dirty false). 동작 연구 전 구간 검사는 저장본에 대고 CLI(`solidcraft-cli eval`)로 병렬 실행했다(규칙 2: 읽기·검사는 CLI 가능).

**요약(10줄)**
- 바뀐 부품 2: `P_T01_YPLATE` t15 → **t10**(Z −370~−360), `P_S01_DGSPACER` 50 → **55**(Z −360~−305). 새·지운 부품, 구매품, 볼트, 조인트 0. 옮긴 DP-1~3 체결 0.
- 매트 밑면 Z 0 변화 0(매트 ↔ 링1·원판 0.5, ↔ 링2 2.0 그대로). 진공 밀봉면(원판·링1 −0.5, 링2 −2) 그대로. DG 테이블 −241·블록 −370 그대로. 사슬 합 10+55+64+8+220.5+12+0.5 = 370.0.
- Y판 1,804,655.3 mm³ / 4,836.5 g, 받침 1,706,648.9 mm³ / 4,573.8 g — 지시서 시험값과 같다. MAT_Y 순 −2.0 kg.
- **지시서와 다른 점 1:** Y판은 `offset_face −5` 대신 지시서 3절의 '대안 경로'(탭 관통 + 상자 자르기)로 그렸다. `offset_face`로는 블라인드 탭 천장 면이 새 윗면(−360)과 두께 0으로 겹쳐 남았다(커널 면 20, 관통 아님). 대안 경로는 커널 면 18, 진짜 관통 탭이다. 부피·질량은 같다.
- 정적 틈(8 mm 안): 겹침 0. `CB5-16_T18_YNB_1` ↔ 받침 2.0, 모터 ↔ 받침·Y판 창 5.0. J_MAT_Y −860/40, J_MAT_X ±620 네 자세 겹침 0.
- 동작 연구 7개 `motion.interference`: 7개 모두 truncated false. 충돌은 기준선 3쌍(BASE↔MAT_X 1.665·부피 0, MAT_X↔MAT_Y 0.458·부피 0, MAT_Y↔T18_YN 0.622 = YNB 볼트 나사 물림)뿐이고 깊이가 v0.8.0 T18 기준선과 같다. **새 겹침 0.** (작은 매트 BOUND ↔ 링1 S-05 겹침은 MAT_ROT 쪽이라 이번 범위 밖, 바뀐 것 없음)
- 손계산(해석 못 함 — 환경 없음, D-16): Y판 t10 운전 3 g SF 6.21(필요 3), 오조작 SF 3.29(보수 모델, 필요 2; 구상 모델 6.67), 받침 옆힘 SF 약 390. M-09 SF ≥ 2 통과.
- 저장 `3D_Modeling/FSAP_v0.8.2.sc`(대기 자세), `tools/config.json` doc = v0.8.2. 해석용 임시 STEP 2개 `tools/out/mech_T14/stepout/`.
- 미완: 없음. 사이클_홈매트는 표본 상한 1000(1,040단계 중)이라 단계 하나 걸러 보는 구간이 있다(WF-126). SolidCraft 앱이 이 검사 중(08:27) 꺼져 마지막 한 연구는 CLI로 4묶음 나눠 돌렸다(저장은 그 전에 끝남).

## 1. 근거 규칙

| 규칙 | 원문 | 이 작업에서 |
|---|---|---|
| E-03 | "어느 단계든 합격의 첫 조건은 **작업 대상을 넣은 전 구간 동작과 간섭 0**이다." | 동작 연구 7개 + 네 행정 끝 정적 검사 |
| E-05 | 형상이 바뀌면 새 번호로 저장 | v0.8.1 → v0.8.2(작은 변경이라 수 번호 +1, 요구서 8-2) |
| M-09 | "SF가 필요치의 3배 이상 남으면 과사양 결함으로 보고하고 다운사이징 안(두께·형번·재질)과 가격을 붙인다" | Y판 운전 6.21/3 = 2.07배 → 과사양 해소 |
| M-01 | "상대 부품의 탭 또는 너트가 실제로 있음, 물림 ≥ 1.5d" | YNB `CB5-16` 물림 8 ≥ 7.5 그대로(관통 탭 t10 안) |
| U-10 | "판은 전체 길이로 고르게" | Y판 Z 평면 −370·−360 두 개뿐(단차 없음) |
| E-02 | "구동 단계에서 새로 본 디테일은 **기록만** 하고 수정 회차를 쓰지 않는다." | d1~d5는 5절에 기록만 |
| E-16 | 판정은 수치로만 | 스크린샷 `tools/out/mech_T14/v082_iso.png`는 저장만 |

## 2. 그린 것

순서(대기 자세 `motion.play 대기 step 0`, MAT_Y Y −700, 월드 좌표):

| 단계 | 명령 | 결과 |
|---|---|---|
| 1 | `open v0.8.1` → `inspect_design` dirty false → `save {path: v0.8.2}`(먼저 다른 이름 저장, E-05) | config doc → v0.8.2 |
| 2 | `solid.offset_face {faces:[[75,−700,−355]], distance:5, body:P_S01_DGSPACER}` | 받침 Z −360~−305, 1,706,648.9 mm³ |
| 3a | (시험) `solid.offset_face {faces:[[150,−500,−355]], distance:−5, body:P_T01_YPLATE}` | 부피는 1,804,655.3으로 맞았으나 위상 결함: 탭 Ø4.2 천장 면 2개(Z −360, 법선 −Z)가 남고 윗면에 탭 구멍 고리가 없음(커널 면 20). 천장과 윗면이 두께 0으로 포개진 막. 관통 원통 자르기도 바뀐 것 0 → 이 피처를 지움 |
| 3b | `solid.cylinder {Ø4.2, h17, base (55,−640,−371) / (115,−640,−371), cut, targets [P_T01_YPLATE]}` → `solid.box {410×510×6, center (0,−700,−357), cut, targets [P_T01_YPLATE]}` | Y판 Z −370~−360, 1,804,655.3 mm³, 커널 면 18(천장 면 없음, 진짜 관통 탭) |
| 4 | `document.metadata.set` 설명 "T14 mechanism: Y plate t15->t10 (Z-370~-360), DG spacer extended down to Z-360 (H55), mat bottom Z0 unchanged" | |
| 5 | `motion.play 대기 step 0` → `save {path: 3D_Modeling/FSAP_v0.8.2.sc}` | 14,265,280 bytes |

3b는 지시서 3절 '안 되는 순서'(탭을 먼저 관통으로 판 뒤 **offset_face**)와 다르다. 탭 관통 뒤 면 띄우기가 아니라 **상자 자르기**로 두께를 줄였고, 이 길은 선정 시험(`trial_a_out.json`)에서도 부피가 같게 나온 '대안 경로'다. 지시서의 기준(Y판 Z −370~−360, 부피 1,804,655.3 ± 1, Z 평면 2개, 관통 탭)을 지키는 쪽으로 정했다(절차 10 "지시 좌표가 실측과 다르면 지시서의 기준을 지키는 쪽으로").

생성기: `tools/gen_t14_mech.py`(→ `tools/out/mech_T14/gen_t14.json`, 7단계, 3b 경로).

### 부품 표

| 부품 | 컴포넌트 | 재질 | bbox (mm) | 부피 mm³ | 질량 g | 전 → 후 |
|---|---|---|---|---|---|---|
| `P_T01_YPLATE` | MAT_Y(바디) | A5052 | X ±200 · Y −950~−450 · Z −370~−360 | 1,804,655.3 | 4,836.5 | t15 7,255.1 g → t10 |
| `P_S01_DGSPACER` | MAT_Y(바디) | A5052 | X ±100 · Y −837.5~−600 · Z −360~−305 | 1,706,648.9 | 4,573.8 | H50 4,156.9 g → H55 |

그대로 둔 것(실측): Y판 모터·호스 창 X ±47.5 · Y −870~−665, 결속 Ø4.5 ×2 (±10, −590), M5 탭 Ø4.2 ×2 (55·115, −640) 관통. 받침 U 윤곽·트임 X ±47.5 · Y −837.5~−665, 윗면 −305, DGM 탭 기초 Ø8.5 깊이 20 ×4.

## 3. 검사 (저장 전, 수치)

| 검사 | 도구 | 결과 |
|---|---|---|
| 재질 | `measure` material | 두 바디 A5052(BOM과 같음). `matcheck.py` 불일치 0건(단, `out/mach_props.json`은 11-01 것이라 이번 두 바디는 measure로 따로 확인) |
| 리지드 그룹·숨김 | 바디만 바뀜(MAT_Y 컴포넌트 바디, 새 occurrence 0) | 누락 0, 숨김 변경 0 |
| 정적 틈 8 mm | `inspect.clearance {against:[두 바디], clearance:8}`(나머지 385바디) | 겹침 0, truncated false. 근접: Y판 ↔ YNB·Y 블록 4 = 0(맞닿음, 기존), 받침 ↔ DGM 하우징 0(기존), `CB5-16_T18_YNB_1` ↔ 받침 **2.0**, DGM 모터 ↔ 받침 5.0·Y판 창 5.0. unchecked 2쌍 Y판 ↔ `CB5-16_T18_YNB_1·2`(나사 물림, 바꾸기 전과 같음) |
| 행정 끝 | `joint.drive` J_MAT_Y −860·40, J_MAT_X −620·620 → 각 `inspect.clearance` | 네 자세 모두 겹침 0, truncated false, moved true(`tools/out/mech_T14/model_drive_checks.json`) |
| 매트 높이 | `inspect.clearance` 매트 3 ↔ 링1·원판·링2 | 0.5 / 0.5 / 2.0, 매트 밑면 Z 0.0 |
| 조인트 자기 점검 | 조인트·유닛 구성 변경 0 → 행정 끝 4자세 구동으로 대신 | 모두 moved, 멈춤 없음 |
| 저장본 재확인 | `solidcraft-cli run verify_saved.json --in v0.8.2 --results`(저장 뒤) | Y판 1,804,655.33·받침 1,706,648.90 mm³ 그대로, `motion.play 대기 step 0` moved false(대기 자세로 저장됨) |
| 동작 연구 7개 | `motion.interference` (아래 4절) | 7개 truncated false, 새 겹침 0(기준선 3쌍만) |

## 4. 동작 연구 (E-03·E-17)

바뀐 범위가 MAT_Y 바디 두 개뿐이라(E-17 parts_only) `occurrences:["MAT_Y:1"]`, `against`는 MAT_Y와 상대 운동하는 이웃 20개(MAT_X·BASE·MAT_ROT·T18_Y/YN/X/XN·DGM·RING1·RING2·SV2RL28 레일 4·YNB 볼트 2·매트 BOUND 3·HEAD)로 했다. 전 occurrence(320개)를 against로 주면 "too many bodies for a contact sweep"로 거부된다. 덧붙여 기하 논증: 새로 생긴 재료는 받침 Z −360~−355 띠 하나이고, 이 자리는 바로 전까지 같은 컴포넌트의 Y판 재료였다(받침 U 발자국은 Y판 창 밖). 그래서 MAT_Y 묶음의 재료 공간은 전보다 넓어진 곳이 없고, 새 겹침은 생길 수 없다.

| 연구 | 단계 / 표본 | 통로 | truncated | 충돌 쌍(깊이 mm, 부피 mm³) | 판정 |
|---|---|---|---|---|---|
| 사이클_큰매트 | 583 / 584 | CLI `run --results` | false | BASE↔MAT_X 1.665/0, MAT_X↔MAT_Y 0.458/0, MAT_Y↔T18_YN 0.622/null | 기준선만 |
| 사이클_작은매트 | 298 / 299 | CLI | false | 같은 3쌍, 같은 깊이 | 기준선만 |
| 사이클_홈매트 | 1,039 / 1,000(상한) | CLI 4묶음(MAT_Y+MAT_X / +BASE / +T18_YN·T18_Y / +T18_X·T18_XN) | false ×4 | MAT_X↔MAT_Y 0.458/0, MAT_Y↔T18_YN 0.622/null, 나머지 2묶음 clear | 기준선만 |
| 상태_홈매트_홈 | 461 / 462 | CLI | false | 같은 3쌍 | 기준선만 |
| 상태_홈매트_오목모서리 | 93 / 94 | MCP(앱) | false | 같은 3쌍 | 기준선만 |
| 상태_큰매트_볼록모서리 | 92 / 93 | CLI | false | 같은 3쌍 | 기준선만 |
| 되감기 | 72 / 73 | CLI | false | 같은 3쌍 | 기준선만 |

occurrences는 `MAT_Y:1, MAT_X:1, BASE:1, T18_YN:1, T18_Y:1, T18_X:1, T18_XN:1`(T18 모델링과 같은 묶음, 21쌍). `MAT_ROT:1`을 넣거나 against에 이웃 20개를 주면 "too many bodies for a contact sweep"로 거부된다. MAT_ROT·링·매트는 Z −305 위라 이번에 바뀐 Z −370~−305 띠와 만날 수 없다(정적 틈 검사에서 8 mm 안 근접 0). 기준선 3쌍은 v0.8.0 T18 모델링 보고서와 깊이가 같다: BASE↔MAT_X·MAT_X↔MAT_Y는 레일·블록 맞닿음(부피 0), MAT_Y↔T18_YN은 `CB5-16_T18_YNB` ↔ Y판 M5 탭 나사 물림(이제 관통 탭 t10 안 물림 8). 결과 `tools/out/mech_T14/check/mb_summary.json`, `mb_4_out_mcp.json`, `m[bh]_*_res.txt`.

## 5. 디테일 기록 (E-02, 수정 회차 안 씀)

| id | 내용 | 처리 |
|---|---|---|
| d1 | Y판 t10 밀링 평면도(블록 4개·받침 한 평면) | D-08 한도 대기 |
| d2 | Y판 1 g 처짐 0.015 → 0.051~0.054 mm | 요구서 7절 시제품 확인(봉제점 흔들림) |
| d3 | `CB5-16_T18_YNB` 끝 ↔ 받침 밑면 틈 2.0 — 길이 16 고정, 더 긴 볼트 금지 | BOM 비고 |
| d4 | Y판 ↔ 블록·받침 체결(DP-4) 모델에 없음 | 디테일링 DP-4(`tools/gen_dp4_detail.py` 미완, 안 씀) |
| d5 | 고체 FEA 못 함 — 환경 없음(D-16) | 손계산 `fea/cases/mech_T14_model_handcalc.py` |

## 6. 강도 (손계산, E-18)

`fea/cases/mech_T14_model_handcalc.py` → `tools/out/mech_T14/model_handcalc.json`. A5052 허용 175 MPa.

| 경우 | 모델 | σ MPa | SF | 필요 |
|---|---|---|---|---|
| Y판 운전 3 g | 81.8 kg × 3 g = 2,407 N, 블록 4개, 대각 팔 78.1, 폭 100, t10 | 28.2 | **6.21** | 3 |
| Y판 오조작 | 1,080 N × 팔 346 / 블록 쌍 간격 200 = 짝힘 1,868 N, 반을 블록 하나가 대각 팔 78.1·폭 100으로(구상의 폭 200 모델보다 불리) + 1 g | 53.2 | **3.29** | 2 |
| Y판 1 g 처짐 | 1/t³ | — | 0.051 mm(t15 0.015) | D-08 |
| 받침 H55 옆힘 | 1,080 N × 360, 단면 31,022 mm², Z 940,104 mm³ | 0.45 | 약 390 | 2 |
| YNB 물림 | 관통 탭 t10 안 물림 8 | — | 바뀌지 않음 | M-01 7.5 |

## 7. 바뀌지 않은 것

- 조인트·행정·연구 키·리지드 그룹 변경 0 → `changed_joints` false. `tools/motion_states.json`(machine.json 없음) 고칠 것 없음.
- 제어 순서 제약(U-09): 새 제약 없음. S-05 그대로(링은 매트를 꺼낸 뒤에만 올리고, 링1은 진공을 끊은 뒤 내린다).
- 구매품·STEP: 새 형번 0 → stepcheck·구매 대상 없음.

## 8. 산출물

- 모델 `3D_Modeling/FSAP_v0.8.2.sc`, 생성기 `tools/gen_t14_mech.py`
- 해석용 임시 STEP `tools/out/mech_T14/stepout/P_T01_YPLATE.step`, `P_S01_DGSPACER.step`(E-06 예외, 납품 아님)
- BOM `docs/bom/FSAP_v0.8.2_made.csv`(YPLATE·DGSPACER 행), `FSAP_v0.8.2_purchased.csv`(CB5-16 비고 YNB 길이 고정)
- 부품 서명 `tools/out/signatures.json` doc v0.8.2, 두 바디 bbox·부피·질량 갱신
- 검사 출력 `tools/out/mech_T14/model_drive_checks.json`, `tools/out/mech_T14/check/mi_*_out.json`, 스크린샷 `tools/out/mech_T14/v082_iso.png`
- 설계검토서 비고(문서 담당용): YPLATE "A5052 / 밀링 / Y 이동판 400×500 t10(Z −370~−360), 모터·호스 창 95×205, M5 관통 탭 ×2(YNB)", DGSPACER "A5052 / 밀링 / DGM 받침 U자 200×237.5×55(Z −360~−305)", CB5-16_T18_YNB "길이 16 고정 — 끝 ↔ DG 받침 2.0, 더 긴 볼트 금지"

## 워크플로우 메모

- MCP `open`으로 이미 열린 같은 경로 파일을 다시 열면 디스크에서 다시 읽지 않고 메모리의 설계를 그대로 둔다(피처 수 1,668로 편집이 남아 있었다). 안내서 '원복'의 "다시 열기 = 저장 안 된 작업 버림"은 다른 경로에서만 맞는 것으로 보인다(확인 필요).
- `solid.offset_face`로 판 윗면을 블라인드 구멍 바닥 높이까지 내리면 거부되지 않고 두께 0 막이 남는다. 부피·bbox로는 못 잡고 `body_topology`(천장 면·윗면 구멍 고리)나 커널 면 수로만 보인다. 선정 시험의 "관통 탭이 된다" 판정은 부피만 본 것이었다. 두께 줄이기 지시는 "구멍 관통 → 상자 자르기"가 안전하다.
- `solidcraft-cli eval --json-out`은 `motion.interference` 결과를 담지 않고 바디 측정 전체를 쓴다. 동작 검사는 `run --results`로 돌려야 한다(첫 7개 실행을 버리고 다시 돌림).
- MCP로 1,000표본 연구를 돌리던 중(약 45분) 앱이 꺼졌다. 긴 연구는 CLI에서 occurrences를 바꾼 쪽 + 이웃 하나씩으로 나눠 병렬로 돌리면 6분 안에 끝났다(WF-126 방법이 실제로 빠름).
- `motion.interference`는 against에 occurrence 320개를 주면 "too many bodies for a contact sweep"로 거부되고, 그 전에 저장본 읽기만 3분 30초 걸린다.
