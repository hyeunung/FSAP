# 준비 점검 — 동작 검사(E-03) 가능 여부 (v0.7.2, 2026-11-01)

요약(10줄 안쪽)
- 대상: `3D_Modeling/FSAP_v0.7.2.sc`(config.json doc). T12 옆·뒤 커버(V071-01~04)와 T07 고정 가드틀(V072-01~03)을 뺀 판. CLI `solidcraft-cli`로 저장본만 읽음(MCP 안 씀, run-rules 2). sha1 `a689a29297bc9ab6cc7419b8d7bdf382eb040ac3` 점검 전후 같음
- **판정: 준비됨(ready = true), missing 없음.** 고정부 `fixed [0, 2]`, 조인트 10 + 리지드 그룹 18, `floating []`·`errors []`·`conflicts []`
- 동작 연구 8: `대기`(1단계, 0단계 = 대기 포즈), 사이클 3(큰 583·작은 298·홈 1039), 상태 정밀 3(461·93·92), `되감기` 72. 상태마다 한 단계씩 재생 67단계 모두 `unmoved []`·`conflicts 0`·`stopped_by_contact None`, 끝에 대기로 되돌림, `contact.check collisions []`
- 작업 대상 모형 14바디: 큰·작은·홈 매트 × (원형, `_BOUND`, `_SEAM`, `_TAIL`) + 테이프 2. 값은 자료대기 임시값(D-01~D-07, D-10, D-13)
- 기계 정의: `tools/machine.json` 없음 → `tools/motion_states.json`(WF-125·run-rules 8). doc = v0.7.2로 맞음, 사이클·상태 연구 6개 단계 수가 저장본과 같음
- gmsh: `python -B -c "import gmsh"` → `ModuleNotFoundError` (gmsh = false, WF-127)
- 지난 점검(v0.7.1) 뒤 바뀐 것: 리지드 `BASE 2 → T07(888)` 없어짐(가드틀 뺌), 바디 289 → 274, 컴포넌트 268 → 255, 타임라인 1474 → 1452. 조인트·연구는 같음
- 미완·주의(결함 아님, 5절): `J_T05_PAD` 연구 키 0/8(저장값 −12.5), 타임라인 경고 23(오류 0)
- 바뀐 부품: 없음(읽기만). 원복: 저장 안 함, 재생 마지막이 `motion.play {"study":"대기","step":0}`

점검 방법: `solidcraft-cli run <스크립트> --in FSAP_v0.7.2.sc --results`(`--save` 없음). 스크립트·결과 `tools/out/prep_check8/`: `check.json`·`check_out.json`(목록), `build.py`(motion_states → 재생 스크립트), `play.json`·`play_labels.json`·`play_out.json`(재생·초기화), 요약 `summ.py`·`s2.py`·`s3.py`, `sha_before.txt`.

규칙 근거:
- E-03 "동작 검사에는 항상 실제 작업 대상 모형(설계 요구서 0-2의 크기 범위 양 끝, 가공 뒤 형상과 떨어진 조각 포함)을 넣고, 대상이 함께 움직이는 전 구간(요구서 0-3 사이클, 6-4 상태 목록)에서 본다."
- E-15 "기계의 모든 움직임은 CAD 조인트(슬라이드·회전)와 리지드 그룹·모션 링크로 정의한다. 동작 상태 = 조인트 값의 묶음이다."
- 안내서 '동작 상태 초기화' "설계 안에 '대기' 포즈를 0단계로 둔 동작 연구(motion study)를 만들어 두고 `motion.play {"study": "<이름>", "step": 0}`" · 요구서 8-6 "동작 상태 초기화: 설계 안 대기 동작 연구의 0단계"
- run-rules 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다(ready=true, done=true, 임시값 목록 첨부)"

## 1. 저장본에서 읽은 것

| 명령 | 결과 | 근거 수치 |
|---|---|---|
| `document.inspect` | 저장 안 된 변경 없음 | `dirty: false`, revision 1, 타임라인 1452 중 error 0·warning 23, 바디 274, 숨김 0(E-11) |
| `component.list` | 컴포넌트 255 | 골격 BASE·MAT_X·MAT_Y·MAT_ROT·HEAD·PRESSER·NEEDLE, RING1·RING2, 매트, T05·T05_PAD·T05_TAPE, T06·T06_KNIFE, 구매품·체결품 |
| `joint.list` | 조인트 10 + 리지드 18 | `fixed [0, 2]`, `floating []`, `errors []`, `conflicts []`, 억제 0, `links []` |
| `motion.list` | 동작 연구 8 | `traces []` |
| `contact.check` | 대기 포즈 겹침 없음 | `collisions []` |

### 조인트 사슬

| 조인트 | 종류 | a → b(occurrence) | 한계 | 저장값 | 연구 키 |
|---|---|---|---|---|---|
| `J_MAT_X` | 직선 | BASE 2 → MAT_X 4 | −620 ~ 620 mm | 0 | 8/8 |
| `J_MAT_Y` | 직선 | MAT_X 4 → MAT_Y 6 | −860 ~ 40 mm | −700 | 8/8 |
| `J_MAT_ROT` | 회전 | MAT_Y 6 → MAT_ROT 8 | −360 ~ 0° | 0° | 8/8 |
| `J_HEAD_ROT` | 회전 | BASE 2 → HEAD 10 | −180 ~ 180° | 0° | 8/8 |
| `J_PRESSER` | 직선 | HEAD 10 → PRESSER 12 | 0 ~ 10 mm | 10 | 8/8 |
| `J_NEEDLE` | 직선 | HEAD 10 → NEEDLE 14 | −30 ~ 0 mm | 0 | 8/8 |
| `J_RING1` | 직선 | MAT_ROT 8 → RING1 130 | −60 ~ 0 mm | 0 | 8/8 |
| `J_RING2` | 직선 | MAT_ROT 8 → RING2 141 | −60 ~ 0 mm | 0 | 8/8 |
| `J_T06_KNIFE` | 직선 | T06 810 → T06_KNIFE 828 | −30 ~ 0 mm | 0 | 8/8 |
| `J_T05_PAD` | 직선 | T05 289 → T05_PAD 350 | −13.5 ~ 0 mm | −12.5 | **0/8** |
| 리지드 9 | 리지드 | MAT_ROT 8 → 매트 컴포넌트 | — | — | — |
| 리지드 6 | 리지드 | MAT_ROT 8 → 2413~2433(T11 배관 부품) | — | — | — |
| 리지드 3 | 리지드 | HEAD 10 → T05(289)·T05_TAPE(356)·T06(810) | — | — | — |

모든 사슬이 BASE(고정)에서 시작한다. v0.7.1의 `BASE 2 → T07(888)` 리지드는 가드틀을 빼면서 없어졌고, 그 때문에 떠 있는 부품은 없다(`floating []`).

## 2. 필요한 것과 있는지

| # | 필요한 것 | 근거 | 있나 | 확인 수치 |
|---|---|---|---|---|
| 1 | 고정부 | 안내서 '동작 검사' | 있음 | `fixed [0, 2]` |
| 2 | 조인트, 끝까지 고정부에 이어짐 | 안내서, M-07, E-15 | 있음 | 조인트 10, `floating []`, `errors []`, `conflicts []` |
| 3 | 대기 포즈 0단계 동작 연구 | 안내서 '동작 상태 초기화', 요구서 8-6 | 있음 | `대기`(1단계, 키 9). step 0 → X 0, Y −700, 회전 0°, 헤드 0°, 노루발 10, 바늘 0, 링1 0, 링2 0, 칼 0. 저장본이 이미 대기 포즈(첫 재생 `moved false`) |
| 4 | 사이클 동작 연구(요구서 0-3) | E-03 | 있음 | `사이클_큰매트` 583, `사이클_작은매트` 298, `사이클_홈매트` 1039 단계, 키 9 |
| 5 | 기계 정의(유닛·상태·path_parts) | E-15, WF-125 | 있음(대체) | `machine.json` 없음 → `motion_states.json`(joints 7, standby, reset, mats, studies 6, t11_routes). doc = v0.7.2. `t07_zones`는 가드틀과 함께 빠짐 |
| 6 | 작업 대상 모형 — 크기 범위 양 끝 | 요구서 0-2·6-4, D-01 | 있음(임시) | `MAT_LARGE`·`MAT_SMALL`, 가장 좁은 홈 `MAT_GROOVE`(D-02·D-03) |
| 7 | 가공 뒤 형상·떨어진 조각 | E-03 | 있음(임시) | `_BOUND` 3, `_SEAM` 3, `_TAIL` 3, 테이프 `MAT_TAPE_ROLL`·`MAT_TAPE_PATH` |
| 8 | gmsh | WF-127 | 없음 | `ModuleNotFoundError: No module named 'gmsh'` — 준비 판정에는 넣지 않음(구상 지시만 달라짐) |

## 3. 상태 목록 ↔ 요구서 0-3·6-4

| 요구서 단계 | 대응 상태(연구·단계) |
|---|---|
| ① 매트 올리고 시작 | 각 사이클 `① 로딩`(1) |
| ② 시작점 찾기·바인더 물림 | `② 시작점 찾기`·`② 바인더 물림`(큰 6·7, 작은 31·32, 홈 6·7) |
| ③ 외곽 한 바퀴 봉제 | 직선·볼록 모서리(세 사이클), 오목 모서리·홈 입구·홈 바닥 꺾임(홈 사이클), 정밀 연구 3 |
| ④ 이음매·테이프·실 절단 | `④ 시작·끝 이음매` ~ `④-7 칼 올림`, `④ X 되돌림`(세 사이클) |
| ⑤ 배출 | `⑤ 배출`(큰 583, 작은 298, 홈 1039) |
| 6-4 매트 3가지 | 큰·작은·홈 매트 사이클 각각 |
| 6-4 상태 6가지 | 직선, 볼록 모서리, 오목 모서리, 홈 입구, 홈 바닥 꺾임, 시작·끝 이음매 — 모두 한 단계 이상 |

0-3 다섯 단계와 6-4 상태 여섯이 모두 상태 하나 이상에 대응한다.

## 4. 재생 확인(상태마다 가운데 단계 + 되감기 + 대기 초기화)

- 67단계 재생: `unmoved []`, `conflicts 0`, `stopped_by_contact`·`stopped_by_loop` 없음 67/67(움직임 59, 이미 같은 자세 8)
- 예: `상태_큰매트_볼록모서리` 46 → Y −836.1, 회전 −45°, 노루발 0, 바늘 −30. `되감기` 36 → 회전 −180°
- 끝 상태: 대기 포즈로 되돌림(X 0, Y −700, 회전 0, 헤드 0, 노루발 10, 바늘 0, 링 0, 칼 0, 패드 −12.5), `floating []`, `contact.check collisions []`
- 이것은 준비물 확인이다. 전 구간 간섭(`motion.interference`, budget_s·truncated 확인)은 동작 검사 부서가 한다.

## 5. 미완·주의(결함 아님)

1. `J_T05_PAD`가 어느 동작 연구에도 키가 없다(지난 점검과 같음). 대기 0단계가 패드를 되돌리지 못한다. 사이클 ④-5 "T05 패드 P_hold(조인트 변화 없음)"으로 운전 위치에 고정된 것으로 쓰고 있다. 패드 움직임을 동작 검사에 넣으려면 연구에 키를 더해야 한다(모델링부 몫).
2. 타임라인 경고 23(오류 0): T06 팔 필렛·판금 면 재선택 3(Fillet4·Fillet5·ConvertToSheetMetal1), 불리언 재시도 20(Cone1, Chamfer 6, T09_GBASE_R1 5, T09_ARM_R1 8) — 변위 1e-4 mm 수준. 형상 결과에는 문제 없음.
3. `machine.json`이 없어 `motion_states.json`을 대신 쓴다(WF-125). `대기`·`되감기` 연구는 motion_states 'studies'에 없고 'standby'·'reset' 항목으로만 있다.
4. 작업 대상 모형 수치는 모두 자료대기 임시값(D-01~D-07, D-10, D-13).
5. 루트 컴포넌트 이름이 아직 `FSAP_v0.6.15`다(표시 이름일 뿐, 동작 검사와 무관).

## 워크플로우 메모

- 없음.
