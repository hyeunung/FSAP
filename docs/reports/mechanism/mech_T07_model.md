# T07 모델링 보고서 — 로딩·배출(v0.5.0 → v0.5.1 → v0.6.0)

**요약(10줄)**
- **A. T06-X03(v0.5.1):** 세 매트 `MAT_*_SEAM`을 ㄱ자 6점 단면 한 스케치 한 바디로 다시 그렸다. 바디마다 1,700.0 mm³, bbox는 그대로다. SEAM ↔ 같은 매트 BOUND·매트 겹침은 0이다. 저장·config·커밋·푸시까지 했다(커밋 0eedf44).
- **B. T07(v0.6.0):** `BASE` 아래에 `T07`을 만들고 BASE와 리지드로 묶었다. 형재 8(실물 460 ×2, STEP대기 2850·680·1580 각 ×2), 캡 `HFC8-4080-B` ×4, SUS304 t2 평판 3장을 넣었다. 새 조인트 0, 동작 연구 변경 0.
- **겹침:** 새 바디 15 ↔ 기존 146은 8개 단계 모두 0이다. 8개 연구 motion.interference 충돌 0(truncated false). 검사 상자 K_T07_* 7개도 겹침 0, 충돌 0이다.
- **PM 기대값과 같음:** G2 ↔ `1900_F` 0.0, ↔ 레일 10.02, ↔ 1900 캡 19.41, G4 ↔ 매트 64.80, 판 ↔ 매트 89.22, 검출면 ↔ 매트 44.80.
- **다르게 한 것:** `HFS8-4080-460`은 STEP이 있어서 중간 기둥을 실물 STEP으로 넣었다(T07-M03).
- **판정 못 한 것:** 캡 ↔ 1580 STEP대기 상자 4쌍은 불리언이 실패했다. 상자가 속이 차 있어서이며 STEP을 받으면 다시 본다(T07-M05).
- **통로:** MCP가 앱에 연결돼 있었다(서버는 headless로 떴지만 SolidCraft 앱이 켜져 있어 이어짐). 그래서 그리기·저장은 MCP로 했다. 검사는 MCP로 저장한 작업 사본(`tools/out/mech_T07/model/work_pre060.sc`)에 대고 CLI로 했다.
- **미완:** 없음. 볼트·브래킷·판 구멍은 지시서대로 안 그렸다(E-02). FEA는 환경이 없다(D-16).

## 1. 입력·통로

| 항목 | 값 |
|---|---|
| 지시서 | `mech_T07_select.md` 0·A·B1~B9 |
| 시작 | `3D_Modeling/FSAP_v0.5.1.sc`가 없었다 → `tools/config.json` doc v0.5.0에서 A부터 |
| 문서 확인 | 앱에 열려 있던 설계(옛 v0.4.1, path null)가 `dirty: false`였다 → `open v0.5.0`, errors 0, features 526 |
| 통로(실행 규칙 (2)) | MCP `open`·`batch`·`save {path}`로 그렸다. `save {}`는 쓰지 않았다. MCP 서버 안내의 Backend는 headless였지만 `solidcraft.exe`가 실행 중이었고 호출이 앱으로 이어졌다(`running`·`document.revision` 응답) |
| 검사 | 저장 전 작업 사본 `tools/out/mech_T07/model/work_pre060.sc`(깃 제외)에 대고 `solidcraft-cli run … --results`로 했다(MCP 결과가 1 MB가 넘어서). 그 뒤 같은 설계를 `save {path: FSAP_v0.6.0.sc}`로 저장했다 |
| 대기 포즈 | 저장 전 `motion.play 대기 0`: X 0, Y −700, ROT 0°, HEAD 0, 노루발 10, 바늘 0, 링1·2 0, 칼 0, 패드 −12.5 |

## 2. A — T06-X03(v0.5.1)

| 바디 | 전 | 후 |
|---|---|---|
| `MAT_LARGE_SEAM` | 2,448 mm³, X −30~38 · Y −110~−98 · Z −1~13 | 1,700.0 mm³, bbox 같음, 면 8 |
| `MAT_SMALL_SEAM` | 2,448 mm³, Y −610~−598 | 1,700.0 mm³, bbox 같음 |
| `MAT_GROOVE_SEAM` | 2,448 mm³, Y −110~−98 | 1,700.0 mm³, bbox 같음 |

- 방법: 각 SEAM 컴포넌트에서 `solid.remove` 옛 바디 → `sketch.create`(원점 (−30, 0, 0), x = Y, y = Z) → 6점 `sketch.line` 닫힘 → `solid.extrude` 68(+X). 스케치 `SK_T06X03_SEAM_<매트>`.
- 확인: `inspect.interference` (SEAM, BOUND, 매트) 3쌍 × 3매트 = 겹침 0(truncated false).
- 같이 고친 것: `tools/gen_t06_mech.py` `SEC`, `tools/motion_states.json` check_rule("SEAM ↔ 같은 매트 BOUND 겹침 0(T06-X01).") → config doc v0.5.1 → 커밋·푸시(요구서 8-5).

## 3. B — 만든 부품(세계 대기 좌표, mm)

| 부품(컴포넌트 / 바디) | 종류·재질 | bbox X / Y / Z | 부피 mm³ · 질량 g |
|---|---|---|---|
| `HFS8-4080-2850_G1` / `STEP대기_HFS8-4080-2850_G1` | 구매(E-10), Aluminum | −1425~1425 / −1740~−1700 / −680~−600 | 9,120,000 |
| `HFS8-4080-2850_G4` / `STEP대기_…_G4` | 구매(E-10), Aluminum | −1425~1425 / −1740~−1700 / −140~−60 | 9,120,000 |
| `HFS8-4080-680_SL`·`_SR` / `STEP대기_HFS8-4080-680_SL`·`_SR` | 구매(E-10), Aluminum | ∓(890~930) / −1700~−1020 / −680~−600 | 2,176,000 |
| `HFS8-4080-460_GL`·`_GR` | 구매 실물 STEP, Aluminum | ∓(870~950) / −1740~−1700 / −600~−140 | 513,010 |
| `HFS8-4080-1580_PL`·`_PR` / `STEP대기_HFS8-4080-1580_PL`·`_PR` | 구매(E-10), Aluminum, inseparable | ∓(1425~1505) / −1740~−1700 / −680~900 | 5,056,000 |
| `HFC8-4080-B_1580_PL/PR_ZP` | 구매 실물 STEP, Nylon | ∓(1425~1505) / −1740~−1700 / 892~903 | 6,346 |
| `HFC8-4080-B_1580_PL/PR_ZM` | 구매 실물 STEP, Nylon | ∓(1425~1505) / −1740~−1700 / −683~−672 | 6,346 |
| `P_T07_SKIRT_C` | 가공(SUS304 t2 레이저 평판) | −909.5~909.5 / −1742~−1740 / −680~−60, V홈 (−5, −60) (5, −60) (0, −65) | 17,886.2 g |
| `P_T07_SKIRT_L` | 가공(SUS304 t2) | −1505~−910.5 / −1742~−1740 / −680~−60 | 5,845.8 g |
| `P_T07_SKIRT_R` | 가공(SUS304 t2) | 910.5~1505 / −1742~−1740 / −680~−60 | 5,845.8 g |

- STEP 넣기(gen_s01_step.py 방식): root에 세계 행렬로 `file.insert_step` → `occurrence.reparent`. 460: STEP X → 세계 Z, STEP Y(80) → 세계 X, 원점 (∓910, −1720, −600). 캡: ex = 세계 X, n = 안쪽, ZP 행렬 [1,0,0,∓1465; 0,−1,0,−1720; 0,0,−1,900], ZM [1,0,0,∓1465; 0,1,0,−1720; 0,0,1,−680]. 들어온 bbox가 지시값과 같았다(ZP 892~903, ZM −683~−672).
- STEP대기 치수 출처: 미스미 HFS8-4080 단면 40 × 80(같은 계열 실물 STEP `HFS8-4080-460` bbox 실측 80 × 40과 같음). 길이는 형번 끝 숫자(길이 지정품). 장착 구멍이 없는 형재라 외곽만 그렸다(E-10).
- 판: Y −1740 XZ 평면 스케치 하나를 −Y로 2 밀었다(굽힘 없음, U-10 앞면 Y −1742 한 평면). 구멍은 이번에 안 냈다.
- 메타데이터: 형재 part_number = 형번(purchased, 1580은 inseparable), 캡 `HFC8-4080-B` purchased, `T07` phantom + 판 3장 속성.
- 지운 부품: 없음(A의 옛 SEAM 바디는 같은 이름으로 다시 그림).

## 4. 조인트·기계 정의(E-15)

| 항목 | 값 |
|---|---|
| 새 조인트 | 0. 리지드 그룹 1개 추가(`Rigid Group 2:888` = BASE:1 + T07:1, M-07) |
| joint.list | floating 0, conflicts 0, errors 0, 구동 조인트 10개 그대로 |
| 동작 연구 | 8개 그대로(대기 1, 큰 583, 작은 298, 홈 1039, 상태 461·93·92, 되감기 72) |
| tools/machine.json | 없음(SolidCraft는 설계 안 동작 연구). `tools/motion_states.json`에 `t07_zones`·doc v0.6.0만 더함 |
| 조인트 자기 점검 | 바꾼 유닛이 고정부(BASE)뿐이라 구동할 조인트가 없다. 대신 8개 연구 전 구간 motion.interference로 새 고정부 ↔ 움직이는 것을 봤다 |

## 5. 자기 점검(E-22, parts_only)

### 5-1. inspect.clearance 새 바디 15 ↔ 기존 바디 146(`chk1_out.json`)

| 단계 | 겹침 | 가장 가까운 것(mm) |
|---|---|---|
| 대기 0 | 0 | G2 ↔ `1900_F` 0.0, ↔ `SV2RL28-1800_F_RAIL` 10.02, ↔ `HFC8-4080-B_1900_F_XM/XP` 19.41 |
| 홈 923 | 0 | 위와 같음 + 매트 BOUND ↔ G4 64.80, 매트 ↔ G4 66.13, BOUND ↔ 판 C 89.22 |
| 홈 491 / 651 | 0 | G2 ↔ `P_S01_XSPACER_1/2` 66.21, ↔ 460_F 캡 71.26, ↔ 460_F 73.30 |
| 큰 74 | 0 | 매트 BOUND ↔ G4 64.80, ↔ 판 89.22 |
| 큰 54 · 작은 31 · 되감기 36 | 0 | 대기와 같음 |
| 새 바디끼리 | 0 | 맞댐 0.0. 캡 ↔ 1580 상자 4쌍 unchecked(불리언 실패) |

PM 기대값(겹침 0, G2 ↔ 1900_F 0, 레일 10.0, 1900 캡 19.4, G4 ↔ 매트 ≥ 64.8, 판 ↔ 매트 ≥ 89.1)과 모두 같다.

### 5-2. motion.interference(T07 occurrence 9개 ↔ MAT_X·MAT_Y·MAT_ROT·HEAD·PRESSER·NEEDLE·MAT_LARGE(매트 사슬 전부)·RING1·RING2, budget_s 3000)

| 연구 | 표본 | 충돌 | clear | truncated |
|---|---|---|---|---|
| 대기 | 2 | 0 | true | false |
| 사이클_큰매트 | 584 | 0 | true | false |
| 사이클_작은매트 | 299 | 0 | true | false |
| 사이클_홈매트 | 1,000(표본 상한, 1,040단계 중) | 0 | true | false |
| 상태_홈매트_홈 | 462 | 0 | true | false |
| 상태_홈매트_오목모서리 | 94 | 0 | true | false |
| 상태_큰매트_볼록모서리 | 93 | 0 | true | false |
| 되감기 | 73 | 0 | true | false |

### 5-3. 검사 상자 K_T07_*(`zs_out.json`, `zm_*_out.json`, `zf_out.json`)

BASE 아래 임시 컴포넌트에 상자를 그려 쟀다. 저장하지 않았다.
- 대기 정적, 전 바디 대상: 겹침 0. FIELD·CURTAIN 밑면 ↔ G4 윗면 0.0(맞닿음), BTN ↔ 끝 기둥 PR 2.0, A3 ↔ `STEP대기_SEWHEAD` 128.8, A4·A5 ↔ 끝 기둥 300.
- 사이클 3개·되감기 motion.interference: 충돌 0, truncated false(홈매트는 표본 1,000).
- 검출면 ↔ 매트 BOUND: 홈 923 · 큰 74에서 44.80.

### 5-4. 그 밖

| 항목 | 결과 |
|---|---|
| 숨김(E-11) | 0개 |
| 리지드 그룹 누락 | 0(floating 0, 새 STEP은 리지드로 들어와 T07 아래로 옮김) |
| 재질(E-09) | `tools/out/mach_props.json` → matcheck 불일치 0(BOM `FSAP_v0.6.0_made.csv`) |
| 타임라인 | 오류·경고 0 |
| 저장 뒤 | 다시 읽은 바디 247개 bbox·부피가 저장 전과 같다. 서명 `tools/out/signatures.json`(doc v0.6.0). v0.5.0 대비 바뀐 것은 SEAM 3, 더한 것은 T07 15바디(`sig_diff.json`) |
| 볼트 검사 | 새로 넣거나 옮긴 볼트 0(지시서 B5 안 그림) |
| 스크린샷 | `tools/out/mech_T07/T07_v060_iso.png`(저장만, 열지 않음) |
| 임시 STEP | `tools/out/mech_T07/stepout/P_T07_SKIRT_C.step`·`_L`·`_R` |

## 6. 임시값(자료대기)

| D | 쓴 값 | 어디 |
|---|---|---|
| D-41 | 형재 2850·680·1580 = 40 × 80 외곽 상자(STEP 대기, 미스미 로그인 풀림) | 형재 6 바디 |
| D-13 | 작업자 꺼냄, 자동 배출은 A3·A4·A5 자리만 | `t07_zones` |
| D-38 | 검출면 Y −1722~−1718, T ≤ 0.182 s | `K_T07_FIELD`, T07-Q3 |
| D-39 | 받침면 Z −680(캡 −683까지) | G1·끝 기둥 |
| D-40 | V홈 X 0, 폭 10·깊이 5 | `P_T07_SKIRT_C` |

## 7. 남긴 것

- 생성기 `tools/gen_t07_mech.py`(stage1 STEP 넣기 / stage2 나머지), 명령·결과 `tools/out/mech_T07/model/`
- BOM `docs/bom/FSAP_v0.6.0_made.csv`(+3)·`_purchased.csv`(HFC8 14 → 18, HFS8-460 4 → 6, 2850·680·1580·HBLFSN8 24·CB5-12·HNTT8-5 행)
- 설계검토서 `docs/review/FSAP_v0.6.0_review.md`(제어 순서 제약 T07-Q1~Q8), 결정로그 T07-M01~M07, 자료대기 D-13·D-38~D-41 '쓰는 곳', CHANGELOG
- config doc → `../3D_Modeling/FSAP_v0.6.0.sc`

## 8. 미완

없음. 지시서가 그리지 말라고 한 것(HBLFSN8 24, 판 체결, 커튼·버튼·조절발)은 미완이 아니다.

## 워크플로우 메모

- MCP 서버 안내가 "Backend: headless"라고 했지만 앱이 켜져 있어 호출이 앱으로 이어졌다. 실행 규칙 (2)의 "headless면 CLI" 판정은 안내문이 아니라 `running`·`document.revision` 응답으로 해야 한다. 서버를 앱보다 먼저 띄우면 안내문이 틀린다.
- MCP `inspect.clearance`·`measure`(본문 없이)·`motion.play` 결과가 1 MB가 넘었다(전 바디 목록). 검사는 저장한 작업 사본에 대고 CLI로 하는 쪽이 낫다. 안내서 '간섭'에 "MCP로는 bodies·against를 좁혀 부르거나 작업 사본 CLI로"를 더하면 좋겠다.
- `inspect.measure`는 `body` 인자를 무시하고 전 바디를 잰다. MCP `measure` 도구(`body`)는 하나만 잰다.
- `motion.interference` samples 상한이 1,000이라 1,039단계 연구(사이클_홈매트)는 전 단계를 다 보지 못한다. 단계 범위를 나눠 볼 인자가 없다.
- 속 찬 STEP대기 형재 상자와 실물 캡을 함께 두면 불리언이 실패해 unchecked가 된다(E-10 임시 형상과 U-19 캡이 부딪힘). STEP대기 형재에 캡 끼움 자리(홈 깊이 8)를 비워 두는 규칙이 있으면 판정이 된다.
