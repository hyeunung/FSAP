# DC-05 모델링 수정 1회차 — 자르기 피처 위치 고침(v1.0.3 → v1.0.4)

요약(10줄 안쪽)
- 저장본 `3D_Modeling/FSAP_v1.0.4.sc`(문서 이름 FSAP_v1.0.4, REST, 바디 39). `tools/config.json` doc을 바꿨다. 통로는 MCP(앱 --control 27878)다.
- 바꾼 부품은 U5_TABLE(홈 두 개의 −X 끝)과 U4_X_BEAM(+X 면 −760)이다. 새 부품·지운 부품·조인트 변경은 없다. U1 새 바디 4개는 v1.0.3 그대로 둔다.
- 원인: v1.0.3의 자르기 3개(Box51~53)는 바디가 U4_X·U5_AIRTABLE에 들어간 뒤에 잘렸다. 그래서 자르기가 월드에 고정되어 자세마다 형상이 바뀌었다.
- 고친 법: 세 자르기를 지웠다. N00이 컴포넌트에 넣기 전에 만든 원래 피처 Box30·Box33·Box34의 치수를 `timeline.edit`로 고쳤다. 이것은 gen_v1_n00.py 65·70·71행의 값을 바꾼 것과 같다.
- 핵심 수치: J_U4_X −200·0·30·1222.5·1250에서 부피가 일정하다(TABLE 255,099,000 mm³, BEAM 46,400,000 mm³).
  - 1250에서 LOWER↔TABLE 10.0, U2_COLUMN↔TABLE 10.0, BEAM↔U2_COLUMN 10.0이다.
  - 1222.5에서도 둘 다 10.0이다.
- 스윕 ①② stopped_at null이다. 사이클 표본 25자세의 겹침은 0이다. floating은 0이고 리지드 U4_X↔U5_AIRTABLE(Rigid Group 6:118)는 그대로다.
- 다시 실행: edit.json을 v1.0.3에, edit_full_v102.json을 v1.0.2에 돌렸다. 두 결과 모두 저장본과 바디 39개의 부피·bbox가 같다.
- 미완: 없다. 지시서 ③의 1212.5/862.5 자세 검사는 사이클 표본과 스윕으로 갈음했다(아래 3절). 서보 STEP은 외부 대기다(D-81).

## 1. 문서 확인·원복

- 앱에는 FSAP_v1.0.3이 dirty false로 열려 있었다. `open FSAP_v1.0.3.sc`의 결과는 errors 0, 피처 110이다. 타임라인의 error·warning은 모두 null이다.
- `edit.checkpoint`(251)를 남기고 `motion.play REST step 0`을 했다. 원복할 흔적은 없었다. 첫 회차의 흔적은 저장본 안의 Box51~53이고, 이번에 지웠다.

## 2. 고친 것(지난 검증 문제 1건, 근거 mech_DC-05_verify.md 1절)

| 피처 | 전 | 후 | 바디 |
|---|---|---|---|
| Box51·Box52·Box53 (v1.0.3 edit 9~11단계) | 컴포넌트 안 자르기(월드 고정) | **지움** (`timeline.delete`) | U5_TABLE·U4_X_BEAM |
| Box30 (N00, U4_X로 옮기기 전) | 길이 300 (X −1050~−750) | 길이 290 (X −1050~−760) | U4_X_BEAM |
| Box33 (N00, U5_AIRTABLE로 옮기기 전) | 바늘 홈 X −1252.5~220 | X −1292.5~220 (corner −1292.5, 길이 1512.5) | U5_TABLE |
| Box34 (N00, 같음) | 기둥 홈 X −722.5~220 | X −762.5~220 (corner −762.5, 길이 982.5) | U5_TABLE |

- 검증부 fix는 '루트에 다시 만들고 자른 뒤 move_bodies'를 제안했다. 원래 생성 피처를 고쳐도 결과 형상과 순서(자르기 → move_bodies)가 같다. 바디 이름·재질·리지드·조인트 참조도 그대로 남고 남는 바디도 없어서 이 방법을 골랐다. 이렇게 해도 지시서 C1의 "생성기 70·71행 시작값을 바꾼 것과 같다"를 그대로 지킨다.
- 피처 수: 110 → 107(−3). 다른 바디는 건드리지 않았다.

## 3. 검증 수치(E-16 수치만, E-17 과제 범위)

### 3-1. 자세별 형상 불변(앱 MCP, joint.drive + inspect.measure + inspect.clearance clearance 30)

| J_U4_X | BEAM bbox X | BEAM mm³ | TABLE bbox X | TABLE mm³ | 가까운 쌍(틈) |
|---|---|---|---|---|---|
| −200 | −1250~−960 | 46,400,000 | −2210~10 | 255,099,000 | LOWER↔TABLE 10.0 |
| 0 | −1050~−760 | 46,400,000 | −2010~210 | 255,099,000 | LOWER↔TABLE 10.0, LINK↔TABLE 22.4 |
| 30 | −1020~−730 | 46,400,000 | −1980~240 | 255,099,000 | LOWER↔TABLE 10.0, LINK↔TABLE 22.4 |
| 1222.5 | 172.5~462.5 | 46,400,000 | −787.5~1432.5 | 255,099,000 | LOWER↔TABLE 10.0, U2_COLUMN↔TABLE 10.0, LINK·DRIVE↔TABLE 22.4 |
| 1250 | 200~490 | 46,400,000 | −760~1460 | 255,099,000 | **BEAM↔U2_COLUMN 10.0**, LOWER↔TABLE 10.0, U2_COLUMN↔TABLE 10.0 |

- 모든 자세에서 겹침은 0이다. 검증부가 기대한 값보다 TABLE 틈은 작다(기대 12.5, 실측 10.0). 홈 폭이 정해져 있어 Y 방향 틈(홈 벽 Y ±55 ↔ LOWER Y ±45, 기둥 홈 −530 ↔ 기둥 −520)이 10이기 때문이다. X 끝 틈은 −1292.5+1250 = −42.5 ↔ LOWER −30으로 12.5다.
- 손계산 부피는 255,099,000이다. 원판 275,724,000에서 원판 홈 9,184,000, 바늘 홈 6,611,000, 기둥 홈 5,446,000을 빼고 겹친 부분 616,000을 더하면 이 값이 나와 실측과 같다.

### 3-2. 스윕(앱 MCP joint.sweep)

- 대상: occurrences U3_ROT·U4_Y·U4_X·U5_AIRTABLE, against U1_HEAD·U2_BRIDGE·U4_FIX·U6_SENSOR·U7_TAPE·U8_CASSETTE·U9_LOAD(28쌍).
- ① J_U4_X −200→1250, 25 간격 59점: stopped_at null.
  - 좁은 곳 1150→1250은 5 간격 21점(요구서 6-4 좁은 곳 5 mm)으로 따로 돌렸고, stopped_at null이다.
- ② J_U4_Y −400→1200, X 0, 25 간격 65점: stopped_at null.
- touching_at_start: U4_FIX↔U4_X 한 쌍이다. 빔이 레일 위에 얹힌 설계상 접촉이고 N00부터 있었다.
- 지난 검증은 "joint.sweep이 이것을 못 잡는다"고 했다. 그래서 3-1의 자세별 부피·틈으로 형상이 정말 일정한지 따로 확인했다.

### 3-3. 사이클 표본(저장본 CLI `solidcraft-cli run --results`, `tools/out/mech_DC-05/fix1_cyc.json` → `fix1_cyc_out.json`)

- 자세: 지난 표본(cyc.json)의 REST·CYCLE_L·CYCLE_S·CYCLE_G1·CYCLE_G2·REWIND_EMPTY 25자세를 썼다.
- 검사: 자세마다 두 가지를 쟀다.
  - U1 새 바디 4개 ↔ U3·U4·U5·매트·테이프
  - TABLE·BEAM ↔ LOWER·U2_COLUMN·U2_BASE·U4_RAIL_A/B·U1 새 바디
- 겹침: 0.
- 최소 틈
  - U1_LOWER_LINK 22.4(TABLE, REWIND_EMPTY 72)
  - U1_LOWER_DRIVE 22.4(TABLE, CYCLE_G1 396)
  - STEP대기_MHMF042L1U2M 32.0(TABLE, CYCLE_S 123)
  - U1_LOWER_STAND 81.4
  - LOWER↔TABLE 10.0, U2_COLUMN↔TABLE 10.0
  - BEAM↔RAIL 0.0: 얹힘 접촉이고 겹침 부피는 없다.
- 지시서 ③(1212.5/862.5, 1250/0, 0/0): 1250/0과 0/0은 3-1에서 쟀다. 1212.5/862.5는 사이클 표본에 그 끝 자세가 들어 있고 X 스윕도 지나가는 점이다. 이번에 바꾼 바디의 형상은 자세와 상관없이 일정하다(3-1). 그래서 따로 재지 않았다.
- 지시서 ④(1250/400 금지 띠): DC-05 첫 회차의 결과와 같고 지도(xy_forbidden)에 기록돼 있다. 이번에는 바꾸지 않았다.

### 3-4. 조인트·리지드·재질

- `joint.list`: floating [], fixed [0,2]. J_U4_X·J_U4_Y·J_U3_ROT·J_U1_PRESSER·J_U1_NEEDLE의 한계와 값은 전과 같다. Rigid Group 6:118(U4_X↔U5_AIRTABLE)도 그대로다.
- 재질: 이번에 바꾼 TABLE·BEAM은 N00 차지 상자라 Default 그대로다(재질은 디테일 단계). U1 새 바디 3개는 SS400 그대로다.
- 숨김 0. 새 볼트·새 구멍 0.

## 4. 저장·확인

- 저장 전 `motion.play REST step 0`(X 0·Y 0·회전 0·노루발 20·바늘 0)을 했다.
- `save {path: 3D_Modeling/FSAP_v1.0.4.sc}`의 응답은 name FSAP_v1.0.4, 149,286 bytes다. 저장 뒤에는 편집하지 않았다.
- 저장 확인: 저장본에 대고 CLI `inspect.measure`를 했다. 바디는 39다. TABLE·BEAM·U1 새 바디의 부피·bbox는 3-1의 0 자세와 같다.
- 서명: `ledger.py sigpatch --parts tools/out/mech_DC-05/fix1_changed_parts.json`의 결과는 "바뀜 2, 없어짐 0, 전체 39"다.
- 다시 실행(E-25 재료)
  - `edit.json`(6명령, base v1.0.3) → 임시 사본: 저장본과 차이 0.
  - `edit_full_v102.json`(v1.0.2 → v1.0.4, 바르게 고친 전체 순서) → 임시 사본: 저장본과 차이 0.
  - 결과는 `tools/out/mech_DC-05/replay.json`에 있다.
- 생성기 `tools/gen_v1_dc05.py`
  - stage_1_geom에서 잘못된 자르기 3개를 뺐다.
  - stage_2_fix를 더했다.
  - edit.json·edit_meta.json·edit_full_v102.json을 쓴다.
- 스크린샷 `tools/out/mech_DC-05/dc05_fix1_iso.png`: 저장만 했고 열어 보지 않았다.

## 5. 임시 STEP·구매품

- 새로 힘을 받는 가공품의 형상은 이번에 바뀌지 않았다. LINK·STAND·DRIVE는 v1.0.3과 같다. 그래서 `tools/out/mech_DC-05/stepout/U1_LOWER_*.step`(v1.0.3에서 내보낸 것)을 그대로 쓴다.
- STEP대기_MHMF042L1U2M은 그대로다(D-81, 외부 대기). 치수 근거는 첫 회차 보고서 mech_DC-05_model.md와 같다(플랜지 □60·몸 110, 임시). 자료대기 D-81 '쓰는 곳'에 v1.0.4를 더했다.

## 6. 제어 순서 제약(U-09) — 첫 회차와 같다

- N03 소프트 리밋: 원판 중심이 X −20~350 · |Y| < 95 안에 들어가지 않게 한다(machine.json xy_forbidden).
- 아랫축 서보는 헤드 주축과 1:1로 전자 동기한다(N01-S06).
- 디테일로 기록만 할 것(E-02): 커플링 형번, 각관 안 베어링, LINK·STAND·끝판·서보의 볼트와 렌치 길(±Y 측면), 가마↔바늘 정렬, U3_DRIVE와 LINK의 Z 틈 10 유지.

## 워크플로우 메모

- 바디를 움직이는 컴포넌트에 넣은 뒤 `solid.box operation cut`으로 자르면 자르기가 월드 좌표에 고정된다. 그래서 자세마다 형상이 바뀐다. `joint.sweep`은 이것을 접촉으로 잡지 못한다. 한번 넣은 바디를 고칠 때는 넣기 전의 생성 피처를 `timeline.edit`로 고치는 편이 안전하다. 안내서 '알아둘 것'에 더할 후보다(회고가 engine-candidates.md에 모은다).
