# 준비 점검 — FSAP_v2.6.5 (2026-11-08, 엔진 v3.9.3, REG-02 C-34 실행)

요약
- 판정: **ready=true**(2026-11-06 15:41 CLI 점검 결과를 그대로 씀, E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"). 결과 `tools/out/prep265/prep_results.json`.
- 대상 `3D_Modeling/FSAP_v2.6.5.sc`(tools/config.json doc, 저장 2026-11-06 12:39, 그 뒤 바뀌지 않음). `tools/machine.json`(11-06 08:51)·자료대기(11-06 08:52)도 그대로.
- 바뀐 것: 요구서·결정로그(11-08 20:32) — 5절 REG-02 행 한 줄과 C-34만. 0-2·0-3·6-4 칸은 바뀌지 않음 → 동작 정의·상태 대응 판정 그대로.
- 앱: 다시 켠 빈 상태, `running` 빈 목록. open·편집·저장 0, 설계 파일 연 수 0, CAD 호출 1(running).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError, 다시 확인함).
- C-34 관련(막지 않음, 모델링부 몫): machine.json J_U6_HGT·J_U7_HGT는 아직 따로 된 두 조인트(주석 "두 조인트는 같은 값"). 묶기(공통 판·장공 하나)와 회귀 자세 정의에서 어긋난 자세(POSE 8 등) 빼기는 아직 안 됨. 바뀌면 machine.json·회귀 자세 목록을 고쳐야 함.
- 미완(막지 않음, 앞과 같음): machine.json `doc`가 아직 v2.6.4를 가리킴. 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거 규칙: E-21 원문 "다시 부르면 이전 결과 파일부터 읽고 남은 것만". 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다".

---

# 준비 점검 — FSAP_v2.6.5 다시 확인 (2026-11-06 19:16, 엔진 v3.9.3 재시작 3회차)

요약
- 판정: **ready=true**(앞 15:41 점검 결과를 그대로 씀, E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만").
- 대상 `3D_Modeling/FSAP_v2.6.5.sc`(tools/config.json doc, 저장 12:39). 지시문의 "v2.6.4"보다 config가 최신이라 config를 따랐다.
- 앞 점검(15:39~15:41, 17:47 재확인) 뒤로 설계 파일·`tools/machine.json`(08:51)·자료대기(08:52)·요구서(15:34) 모두 바뀌지 않아 CLI 재측정 안 함. 결과 `tools/out/prep265/prep_results.json`.
- 앱: `running` 빈 목록. open·편집·저장 0, 설계 파일 연 수 0, CAD 호출 1(running).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError, 다시 확인함).
- 미완(막지 않음): machine.json `doc`가 아직 v2.6.4를 가리킴. 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).
- 아래는 앞 점검 본문(같은 파일·같은 결과).

---

# 준비 점검 — FSAP_v2.6.5 다시 확인 (2026-11-06 17:5x, 엔진 v3.9.3 재시작 2회차)

요약
- 판정: **ready=true**(앞 15:41 점검 결과를 그대로 씀, E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만").
- 대상 `3D_Modeling/FSAP_v2.6.5.sc`(config doc, 저장 12:39). 지시문의 "v2.6.4"보다 config가 최신이라 config를 따랐다. 앞 점검(15:39~15:41) 뒤로 설계 파일·`tools/machine.json`(08:51) 모두 바뀌지 않아 CLI 재측정 안 함. 결과 `tools/out/prep265/prep_results.json`.
- 앱: `running` 빈 목록, `document.revision` = 3(id dadb5dc056d0303d-5). open·편집·저장 0. 설계 파일 연 수 0.
- gmsh: 불러올 수 없음(ModuleNotFoundError, 다시 확인함).
- 미완(막지 않음): machine.json `doc`가 아직 v2.6.4. 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).
- 아래는 앞 점검 본문(같은 파일·같은 결과).

---

# 준비 점검 — FSAP_v2.6.5 (2026-11-06, 엔진 v3.9.3 재시작)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.6.5.sc`(tools/config.json doc). 지시문의 "v2.6.4"보다 config가 최신(v2.6.5 LITE, 커밋 e80641a)이라 config를 따랐다.
- 통로: **CLI**(MCP open 안 함). `running` 빈 목록. 앱의 열린 문서는 여전히 `FSAP_v2.6.4`, **`dirty: true`, `path: null`**, 메타 "STEPSWAP mechanism: … CB5-6 x2 … swapped"(앞 점검과 같은 상태). open 하면 이 변경이 버려지므로 열지 않았다. 버린 것 없음.
- CLI `solidcraft-cli run tools/out/prep265/prep_check.json --in FSAP_v2.6.5.sc --results`(저장 없음) 1회, **101 s**(v2.6.4 때 242 s).
- `joint.list`: floating **0**, conflicts 0, errors 0, fixed [0, 2]. 조인트 317 = 리지드 288 + 슬라이더 20 + 회전 9. machine.json joints 29개 이름 모두 있음.
- 동작 연구 8개 `motion.play step 0` 모두 conflicts 0, unmoved 0. 마지막 REST step 0(대기 포즈).
- 작업 대상 모형(v2.6.5 document.json 안 이름): MAT_L·MAT_S·MAT_G, TAPE_L·S·G·G_IN, SEAM_L·S·G·U7.
- gmsh: **불러올 수 없음**(ModuleNotFoundError). 구상은 gmsh 없이(WF-127).
- 미완(막지 않음): machine.json `doc`가 아직 v2.6.4를 가리킴(config는 v2.6.5). 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신). 바뀐 부품 없음(읽기만, 저장 0).

## 1. 근거 규칙
- 안내서 '문서 확인': "앱에 연결돼 있고 열린 설계가 `dirty`(저장 안 된 변경)면 `open` 전에 멈추고 보고한다. … 그 변경은 사람이 한 것으로 보고 버리지 않는다(E-01·E-04)." — dirty true라 MCP open 안 함.
- 실행 규칙 2: "앱이 꺼져 있거나 MCP 호출이 실제로 실패할 때만 CLI로 하고 이유를 보고서에 적는다" — 이유: open 하면 앱의 저장 안 된 변경을 버리게 됨.
- 안내서 '동작 검사': 고정부까지 이어짐(`joint.list` floating), 사이클(요구서 0-3) 동작 연구, 작업 대상 모형(요구서 0-2 크기 양 끝, 가공 뒤 형상·조각).
- 안내서 '동작 상태 초기화': "`motion.play {\"study\": \"<이름>\", \"step\": 0}`" — CLI 스크립트 마지막 단계 REST step 0.
- 실행 규칙 7·WF-113: "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다".

## 2. 점검표

| 항목 | 필요 | 있음 | 근거 |
|---|---|---|---|
| 고정부 | 접지 컴포넌트 | 있음 | joint.list fixed [0, 2] |
| 조인트, floating 없음 | 0-8 v2 구동 | 있음 | 317개, floating [], conflicts [], errors [] |
| 대기 0단계 연구 | REST | 있음 | motion.play REST 0, conflicts 0 |
| 사이클 연구 | 0-3 ①~⑤ | 있음 | CYCLE_L·S·G1·G2, MAINT_HEAD·MAINT_U7, SEAM_U7 — step 0 모두 ok |
| 기계 정의 | 유닛·상태·path_parts | 있음 | tools/machine.json: units 13, joints 29, studies 8, states 26, path_parts 6, temp_values 11 (doc 줄은 v2.6.4) |
| 크기 범위 양 끝 | 0-2, D-01 | 있음(임시) | MAT_L(1500×1500), MAT_S(300×200) |
| 가장 좁은 홈 매트 | 6-4 | 있음(임시) | MAT_G (D-02·D-03) |
| 가공 뒤 형상 | 테이프 띠·이음매 | 있음(임시) | TAPE_L·S·G·G_IN, SEAM_L·S·G·U7 (D-06·D-07) |
| 떨어진 조각 | 0-8-4 ⑤ | 해당 없음 | machine.json workpiece_stages: 조각 없음(D-07) |
| 매트 평면 운동 모형 | 볼 위 X·Y·회전 | 있음 | J_WP_k_X·Y·ROT, 기계 축 아님(실행 규칙 20) |

## 3. 상태 목록 ↔ 요구서 0-3·6-4
machine.json states 26개(앞 점검과 같음).

| 요구서 | 대응 상태 |
|---|---|
| 0-3 ① 올리고 시작 | 대기, 큰 매트 로딩 끝 |
| 0-3 ② 시작점·바인더 물림 | 큰/작은 매트 바퀴 내림(+ SEAM_U7) |
| 0-3 ③ 외곽 봉제·회전 | 직선, 볼록 모서리 45°·90°, 홈 입구 회전, 홈 안 벽, 홈 바닥 꺾임(오목), 모서리 끝 테이프 위, THICK_6·16 |
| 0-3 ④ 이음매 | 큰·작은·홈 매트 이음매 겹침 끝 |
| 0-3 ⑤ 배출 | 큰·작은·홈 매트 배출 |
| 정비 | MAINT_HEAD, MAINT_U7 |
| 6-4 오목 모서리(계단형) | 없음 — 홈 바닥 오목 반원으로 대신(막지 않음) |

## 4. 원복
- 앱: 편집 없음(document.revision·inspect_design 읽기만). 저장본: CLI `run` --save 없음, 마지막 단계 REST step 0. 저장 0.
- 결과 파일: `tools/out/prep265/prep_results.json`(9 MB), 스크립트 `tools/out/prep265/prep_check.json`.

## 워크플로우 메모
- 앱의 `FSAP_v2.6.4`(path null·dirty true, STEPSWAP 메타)가 두 번째 점검에도 그대로 남아 있다. MCP를 쓸 부서마다 open 못 하고 CLI로 돌아간다. 사용자/모델링부가 이 문서를 저장하든 버리든 정해야 한다(반복).
- dirty·name·path만 보는 가벼운 질의가 없어 `inspect_design`(전부 끔)이 70만 자를 냈다(반복).
- machine.json `doc`는 모델링부가 새 버전을 저장할 때 config와 함께 고치지 않는다(v2.6.5 저장 뒤에도 v2.6.4).
