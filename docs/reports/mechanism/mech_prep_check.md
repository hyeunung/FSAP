# 준비 점검 — FSAP_v2.5.5 (2026-11-05)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.5.5.sc`(config doc·machine.json doc 같음, 커밋 332f12e)에 고정부·조인트·대기 연구·사이클 연구·매트 모형 3장·가공 뒤 형상이 다 있다.
- 통로: **CLI**. 앱(127.0.0.1:27878) `running`에 다른 연결(71)의 `engine.batch`(3단계)가 **16,282초(약 4.5시간)째 실행 중**이고, 이 연결의 요청은 줄 서 있었다. 앱 MCP를 쓸 수 없어 실행 규칙 2 "MCP 호출이 실제로 실패할 때만 CLI로 하고 이유를 보고서에 적는다"(WF-121)에 따라 CLI로 쟀다. 앱 문서는 건드리지 않았다(open·save 0).
- `joint.list`: floating **0**, conflicts 0, errors 0, fixed [0, 2]. 조인트 254 = 리지드 225 + 슬라이더 20 + 회전 9. machine.json joints 29개가 이름까지 모두 있다.
- 동작 연구 8개 모두 `motion.play step 0` 성공(conflicts 0, unmoved 0): REST · CYCLE_L · CYCLE_S · CYCLE_G1 · CYCLE_G2 · MAINT_HEAD · SEAM_U7 · MAINT_U7. 마지막에 REST step 0.
- gmsh: **불러올 수 없음**(ModuleNotFoundError). 구상은 gmsh 없이 한다(WF-127).
- 미완(막지는 않음): 6-4 계단형 '오목 모서리' 매트 모형 없음(앞 점검과 같다). `STEP대기_` 바디 1,065개(이름 1,044종). 그중 6200ZZ·HTPA60S5M150-A-N16·CB6-20·CB3-10·MSTH6-20은 오늘 `purchased-step/`에 받아 두었다. 구매부·STEP 교체가 맡을 일이다.
- 바뀐 부품: 없음(읽기만, 저장 0).

## 1. 근거 규칙
- 안내서 '동작 검사': "끝까지 고정부에 이어졌는지 `joint.list`의 `floating`", "사이클(요구서 0-3)을 동작 연구로", "작업 대상 모형(요구서 0-2 크기 양 끝, 가공 뒤 형상·조각)".
- 안내서 '동작 상태 초기화': "설계 안에 \"대기\" 포즈를 0단계로 둔 동작 연구 … `motion.play {\"study\": \"<이름>\", \"step\": 0}`."
- 실행 규칙 7: "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다(ready=true …)"(WF-113).
- 실행 규칙 2: "앱이 꺼져 있거나 MCP 호출이 실제로 실패할 때만 CLI로 하고 이유를 보고서에 적는다(엔진 WF-121)."

## 2. 점검표

| 항목 | 필요 | 있음 | 근거 |
|---|---|---|---|
| 고정부 | 접지 컴포넌트 | 있음 | joint.list fixed [0, 2] |
| 조인트, floating 없음 | 0-8 v2 구동 | 있음 | 254개, floating [], conflicts [], errors [] |
| 대기 0단계 연구 | REST | 있음 | motion.play REST 0 ok |
| 사이클 연구 | 0-3 ①~⑤ | 있음 | CYCLE_L·S·G1·G2 / 정비 MAINT_HEAD·MAINT_U7 / 이음매 SEAM_U7, 모두 step 0 ok |
| 기계 정의 | 유닛·상태·path_parts | 있음 | tools/machine.json: units 13, joints 29, studies 8, states 26, path_parts 6(U2_~U7_), baseline_overlaps 19, temp_values 11 |
| 크기 범위 양 끝 | 0-2, D-01 | 있음(임시) | MAT_L, MAT_S (D-01) |
| 가장 좁은 홈 매트 | 6-4 | 있음(임시) | MAT_G (D-02·D-03) |
| 가공 뒤 형상 | 테이프 띠·이음매 | 있음(임시) | TAPE_L·S·G, SEAM_L·S·G (D-06·D-07) |
| 떨어진 조각 | 0-8-4 ⑤ | 해당 없음 | machine.json workpiece_stages.fragments: 조각 없음(D-07) |
| 매트 평면 운동 모형 | 볼 위 X·Y·회전 | 있음 | J_WP_k_X·Y·ROT(k=L·S·G), 기계 축 아님(실행 규칙 20) |

## 3. 상태 목록 ↔ 요구서 0-3·6-4
machine.json states 26개. 앞 점검(v2.3.4)과 같다.

| 요구서 | 대응 상태 |
|---|---|
| 0-3 ① 올리고 시작 | 대기, 큰 매트 로딩 끝 |
| 0-3 ② 시작점·바인더 물림 | 큰/작은 매트 바퀴 내림(+ SEAM_U7 연구) |
| 0-3 ③ 외곽 봉제·회전 | 직선, 볼록 모서리 45°·90°, 홈 입구 회전, 홈 안 벽, 홈 바닥 꺾임(오목), 모서리 끝 테이프 위, THICK_6·16 |
| 0-3 ④ 이음매·절단 | 이음매 겹침 끝(L·S·G) |
| 0-3 ⑤ 배출 | 배출(L·S·G) |
| 6-4 오목 모서리(계단형) | 없음. 홈 바닥 오목 반원만 있다(막지 않음) |

## 4. 결과 파일
- `tools/out/prep_check/check.json`·`results.json`(joint.list + motion.play 10회, CLI run --results, 저장 없음, 3분 49초)
- `tools/out/prep_check/insp.json`·`insp_out.json`(document.inspect measure false, 바디 2,619, 4분 31초)

## 워크플로우 메모
- 앱 MCP가 4.5시간째 다른 연결의 batch에 막혀 있다. 모델링부가 MCP로 그리려면 사용자가 앱 상태를 확인해야 할 수 있다(`running` 연결 71, id 7353, engine.batch 3단계). 이 점검부는 앱을 건드리지 않았다.
- 이 점검이 v2.5.5에서 P_M04_INSERT 바디를 찾지 못했다. M04R(센터판 빼기)은 이미 반영된 것으로 보인다. 확인은 과제 정리부가 한다.
- CLI에서 파일을 한 번 열 때마다 3~4.5분 걸렸다(2.6 MB, 바디 2,619). 측정은 스크립트 하나로 묶는 편이 낫다.
