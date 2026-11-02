# DC-05 검도 — 아랫유닛 구동 자리 이동(v1.0.3)

요약
- 판정: **불합격(동작 1건)**. 완료 판정 "J_U4_X −200~1250 × Y 0 스윕 과제 범위 접촉 0"을 채우지 못했다. U1_LOWER_DRIVE X 650 ≥ 390은 맞다.
- 원인: DC-05가 고친 U5_TABLE 두 홈 연장과 U4_X_BEAM +X 깎기(edit.json 9·10·11단계)는 바디가 움직이는 컴포넌트(U5_AIRTABLE·U4_X)에 들어간 뒤에 자르기로 만들었다. 그래서 자르기 상자가 바디를 따라가지 않고 월드에 고정돼 있다. `joint.drive`로 다시 계산하면 대기(0) 자세에서만 맞고, 다른 자세에서는 자르기가 빠지거나 엉뚱한 자리를 깎는다.
- 수치(저장본 CLI와 앱 둘 다 같음):
  - J_U4_X 1250에서 U5_TABLE이 STEP대기_867-392342_LOWER와 99,000 mm³ 겹친다(X −30~−2.5). U2_COLUMN과도 132,000 mm³ 겹친다(X 500~527.5). 접촉은 1222.5부터 시작한다(1222에서 틈 0.5).
  - J_U4_X 1250에서 U4_X_BEAM 폭이 300(부피 48,000,000)으로 돌아가 U2_COLUMN과 틈 0이다.
  - J_U4_X 30에서는 U4_X_BEAM이 X −749~−720의 29 mm 조각(부피 4,640,000)으로 깎인다.
- `joint.sweep`은 형상을 다시 계산하지 않아 이 겹침을 못 잡는다(stopped_at null). 모델링부의 "스윕 접촉 0"은 이 때문이다.
- 사이클 경로: 전 단계(0.1단계 간격)에서 원판 중심이 xy_forbidden 안에 한 번도 들어가지 않는다. 새 U1 바디와의 최소 XY 틈은 80이다(CYCLE_S, U3_COLUMN↔U1_LOWER_LINK).
- 새 볼트·조인트·구매품 없음 → 볼트·포트 검사 대상 없음. 숨김 0. 원장 commit은 하지 않았다(불합격).
- 고칠 것: 세 자르기를 지우고, 바디를 루트에서 만든 뒤 컴포넌트로 옮긴다(N00과 같은 순서). 치수는 3절.

## 0. 통로·범위
| 항목 | 내용 |
|---|---|
| 통로 | MCP(`running` [] · `inspect_design` 정상, dirty false, 이름 FSAP_v1.0.3). `open 3D_Modeling/FSAP_v1.0.3.sc` 1회 → features 110, errors 0, 타임라인 error·warning 모두 null. 저장본 확인은 CLI `run --results`(저장 없음) 3회. 0.4 s 안팎이다 |
| 범위 | `ledger.py scope --joints-changed` → full. 바뀜은 U1_LOWER_DRIVE·U4_X_BEAM·U5_TABLE, 새로 만든 것은 LINK·STAND·STEP대기_MHMF042L1U2M, 이웃 17. 대상 바디 6개, against 20개(이웃 + U3_DRIVE·U2_COLUMN·U9_LOAD_BOX). `skip_within: component`, clearance 5 |
| 원복 | 끝에 `motion.play REST step 0`. U4_X_BEAM 46,400,000·U5_TABLE 255,099,000으로 대기 형상이 맞다. save 안 함 |
| 숨김 | 39바디 모두 visible true |

## 1. 과제 범위 동작 검사(E-03, E-17)
`joint.drive` + `inspect.clearance`(앱, `tools/out/mech_DC-05/verify_grid1.json`, 원자료 `verify_grid_raw1.txt`)

| J_U4_X / J_U4_Y | 기준선 밖 겹침(mm³) |
|---|---|
| −200 / 0·400·800 | 0 |
| −200 / −400·1200 | U3_PLATE↔U5_TABLE 49,498 · U3_COLUMN↔U5_TABLE 49,538 (기존 N00, 아래 디테일 2) |
| 525 / 400 | 0 |
| 525 / −400·1200 | 위와 같은 원판 홈 Y 끝 겹침(기존) |
| 875 / 400 (금지 띠 바로 앞) | 0 |
| **1250 / 0·300·400·500·862.5·−400·1200** | **867_LOWER↔U5_TABLE 99,000 · U2_COLUMN↔U5_TABLE 132,000(모든 Y)** |
| 1250 / 400 | 위 + U3_COLUMN↔U1_LOWER_LINK 81,620(xy_forbidden 안, 예상한 금지 띠) |
| 1250 / 300·500 (금지 띠 Y 경계 밖) | LINK 겹침 0 → 띠 |Y|<95가 맞다 |

저장본 CLI 확인(`verify_cli_1250_out.json`, `verify_cli_pos_out.json`, `verify_cli_sweep_out.json`):

| 자세 | U5_TABLE | U4_X_BEAM | 겹침·틈 |
|---|---|---|---|
| 0(대기) | 255,099,000, 면 22 | X −1050~−760, 46,400,000 | 맞음 |
| 30 | 255,099,000, 면 30(엉뚱한 자리 깎임) | **X −749~−720, 4,640,000** | 빔이 조각남 |
| 1222 | — | — | LOWER·U2_COLUMN↔TABLE 틈 0.5 |
| 1250 | 255,289,000(홈 연장 빠짐) | X 200~500, 48,000,000(깎기 빠짐) | 겹침 99,000·132,000, BEAM↔U2_COLUMN 틈 0 |
| `joint.sweep` −200→1250 step 25 | — | — | stopped_at null(형상 재계산 없음, 못 잡음) |

- 판정 근거 M-11 "상태 목록 중 하나라도 겹침 > 0이면 결함"이다. 대상 바디가 자세마다 형상이 바뀌는 것 자체도 M-07 "조인트·리지드 그룹은 실제로 함께 움직이는 관계대로"에 어긋난다. 자르기가 움직이는 바디를 따라가지 않는다.
- 사이클이 쓰는 J_U4_X 최대는 1212.5다(machine.json). 그래서 사이클 자세에서는 1222.5 접촉에 닿지 않는다. 다만 중간 자세에서 빔·테이블 형상이 깨지므로 모델링부의 사이클 표본 23자세 결과는 믿을 수 없다. 고친 뒤 다시 잰다.

## 2. 사이클 경로와 xy_forbidden(수치, `tools/out/mech_DC-05/verify_path.json`, 스크립트 `verify_path.py`)
연구 키(CYCLE_L·S·G2·REWIND = `prep_v1/study_*.json`, CYCLE_G1 = `mech_N01/edit.json`)를 0.1단계로 보간했다. 원판 중심 = (−900 + J_U4_X, −400 + J_U4_Y)이다.

| 연구 | 단계 | 금지 구역 진입 | 최소 XY 틈: COLUMN↔LINK | DRIVE↔STAND | CARR↔STAND |
|---|---|---|---|---|---|
| CYCLE_L | 659 | 0 | 730 | 1215 | 1155 |
| CYCLE_S | 491 | 0 | **80**(X 800, Y 355) | 565 | 505 |
| CYCLE_G1 | 528 | 0 | 367.5(1212.5/862.5) | 357.5 | 297.5 |
| CYCLE_G2 | 597 | 0 | 580 | 1065 | 1005 |
| REWIND_EMPTY | 72 | 0 | 945 | 1365 | 1305 |

- U3_DRIVE(Z −230~−130)와 LINK(Z −120~−60)는 Z로 10 떨어져 있어 XY로 겹쳐도 닿지 않는다. 실측 10.0, 모델링부 3-2와 같다.
- U3_DRIVE·U4_Y_CARR는 STAND(Z −380~−120)와 Z가 겹친다. 그런데 닿으려면 원판 중심 X ≥ 465·405가 필요하고, 행정 최대가 350이라 닿을 수 없다.

## 3. 문제와 고치는 법
### 동작 1 — 움직이는 바디의 자르기가 월드에 고정됨(U5_TABLE·U4_X_BEAM)
- 어디: v1.0.3 타임라인 끝 Box51·Box52·Box53(edit.json 9·10·11단계, 바디가 U5_AIRTABLE·U4_X 컴포넌트에 있는 상태에서 `solid.box … operation cut`)
- 고치는 법(새 번호 v1.0.4, 모델링부 MCP):
  1. 세 자르기 피처를 지운다. 또는 `solid.remove ["U5_TABLE","U4_X_BEAM"]`.
  2. 바디를 REST에서 루트에 다시 만든다. N00 `gen_v1_n00.py` 65~77줄과 같은 순서다.
     - `U4_X_BEAM` 상자 X −1050~**−760**·Y ±1000·Z −340~−260 → `component.move_bodies` U4_X
     - `U5_TABLE` 상자 X −2010~210·Y −1545~1560·Z −40~0
     - 원판 홈 X −970~−830·Y ±820
     - 바늘 홈 X **−1292.5**~220·Y ±55
     - 기둥 홈 X **−762.5**~220·Y −530~−390
     - 그 뒤 posts와 함께 `component.move_bodies` U5_AIRTABLE
     - 자르기는 모두 move 전에 한다
  3. U5_AIRTABLE↔U4_X 리지드(`joint.rigid_group`)와 floating 0을 확인한다.
- 확인 방법: `joint.sweep`이 아니라 `joint.drive` + `inspect.measure`/`inspect.clearance`로 잰다. CLI 저장본에서 J_U4_X −200·0·30·1222.5·1250 자세마다 다음을 본다.
  - 부피: U5_TABLE 255,099,000, U4_X_BEAM 46,400,000으로 모든 자세에서 같아야 한다.
  - 1250 자세: LOWER↔TABLE 틈 12.5, U2_COLUMN↔TABLE 틈 12.5, BEAM↔U2_COLUMN 틈 10.
  - 사이클 표본 23자세를 다시 잰다.

### 디테일 1 — xy_forbidden이 867 아랫유닛(STEP대기_867-392342_LOWER) 쪽을 덮지 않음
- 수치: LOWER X −30~30·Y ±45·Z −120~0이다. 원판 중심이 X −90~90·|Y| < 105 안에 들어오면 U3_PLATE r60(Z −15~0)이 LOWER와 겹친다. X −80~80·|Y| < 95 안에서는 U3_COLUMN r50도 겹친다.
- 지금 지도는 X −20~350만 덮는다. 사이클은 이 구역에 들어가지 않는다(CYCLE_S에서 COLUMN↔LOWER 최소 20). 다만 조그·N03 소프트 리밋이 이 구역을 빠뜨린다.
- 이 겹침은 N01부터 있었다.
- 고치는 법: machine.json xy_forbidden에 다음 항목을 더한다. `{"plate_center_x":[-90,90],"plate_center_y":[-105,105],"reason":"867 LOWER ↔ U3_PLATE r60·COLUMN r50"}`

### 디테일 2 — 원판 홈 Y 끝이 J_U4_Y 행정 끝을 못 덮음(기존 N00)
- 수치: 원판 홈은 Y ±820인데, J_U4_Y −400·1200에서 원판 중심은 Y ∓800이다. 그래서 r60 원판이 40만큼 나와 U3_PLATE↔U5_TABLE 49,498 mm³, U3_COLUMN↔U5_TABLE 49,538 mm³가 겹친다.
- 사이클이 쓰는 범위는 −350~1150(중심 ±750, 원판 끝 810 < 820)이라 사이클에서는 0이다. DC-05가 만든 겹침이 아니다.
- 고치는 법(아래 둘 중 하나, N03 몫):
  - 원판 홈을 Y ±870으로 넓힌다(위 동작 1 재작성 때 함께).
  - J_U4_Y 소프트 리밋을 −340~1140으로 둔다.

### 기록(수정 회차 없음, E-02)
- 새 볼트 0 → M-01·E-11 볼트 검사 대상 없음.
- 공압 포트 0 → M-06 대상 없음.
- U1_LOWER_STAND는 꽉 찬 차지 상자다. 판금 상세가 없어 M-04 대상이 아니다(디테일 단계).
- FEA: 환경 없음(D-16). 손계산은 선정 지시서 값 σ 4.2 MPa, SF 58이다.

## 4. 등급
S가 맞다. 새 구매품 형번은 D-81 임시 형상이고, 선정에서 이미 정했다. 조인트 변화는 없다. 기존 차지 상자 자리와 홈 치수만 바꿨다.

## 5. 원장·판정 기억
- 불합격이라 `ledger.py commit`은 하지 않았다.
- 허용으로 판정한 겹침: U3_COLUMN↔U1_LOWER_LINK(1250/400, 81,620)는 xy_forbidden 안의 금지 띠다(N03 소프트 리밋). 다만 조인트·배치가 v1.0.4에서 다시 바뀌므로 paircache judge는 고친 뒤 합격할 때 남긴다.

## 워크플로우 메모
- SolidCraft: 움직이는 컴포넌트 안 바디에 나중에 `solid.box … cut`을 하면, 자르기 상자가 월드 좌표에 고정되어 `joint.drive` 때 다시 계산된다(자세마다 형상이 바뀐다). `joint.sweep`은 다시 계산하지 않아 이것을 못 잡는다. 모델링 지시서·안내서에 "움직이는 유닛의 형상 수정은 루트에서 만들어 옮기거나, 바꾼 바디 부피를 행정 두 점 이상에서 `joint.drive` 뒤 확인"을 넣을 후보다.
- 과제 안 검사의 '스윕 접촉 0'은 `joint.sweep`만으로 판정하지 말고, 행정 끝 `joint.drive` + clearance로 함께 확인해야 한다.
