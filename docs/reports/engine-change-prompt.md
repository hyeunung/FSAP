엔진 작업이다. MechDesign_Engine(v3.2.1)을 고친다. FSAP MAT-RS-001 실행에서 나온 문제를 반영한다. FSAP 저장소는 읽기만 하고 고치지 않는다.

먼저 읽을 것(FSAP 쪽, 읽기만):
- C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/docs/reports/engine-change-request_2026-11-01.md — 왜·무엇을 고치나(전체 정리)
- C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/docs/reports/engine-candidates.md — 개선후보 WF-051~056, WF-080~091 증거·제안
- C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/run-rules.md — 지금까지 shellNote로 매번 넣던 프로젝트 고정 규칙 13개(규칙 파일 예시)

고칠 것:
1. 완료될 때까지 스스로 이어 돌기 (roadmap R3·R2·R1)
   - R3 보류를 푼다. "모델링 해줘"를 받으면 구동부를 먼저 100% 끝낸다: modeling_round(mechanism)를 구동 과제·구동 후보가 0이 될 때까지 거듭 부르고, 그다음에 detailing_round를 한 번 부른다. 구동 ↔ 디테일링을 번갈아 돌지 않는다(사용자 2026-11-01 "구동부 하나 하고 디테일링하고 또 구동부 하나 하고 디테일링하고 이것도 하지 말라고 했잖아. 구동부 다 완료가 되고 나면 디테일링을 하라니까"). 합친 스크립트든 세션 절차든. 라운드마다 사용량은 보고하되 멈추지 않는다.
   - mechanism 라운드가 디테일링에서나 드러나던 구동 후보(높이 사슬, 볼트 렌치 접근을 막는 배치, 구매품 수량·외형 어긋남 등)를 구동 단계에서 미리 찾게 한다. 이번 FSAP 디테일링(docs/reports/detailing/detail_plan.md 5절)에서 구동 후보 7건이 나왔다 — 구동 단계가 놓친 것이다.
   - R2 완료 조건: 열린 구동 과제·구동 후보(motion_task_candidate)·마지막 회귀 동작 문제·디테일·형번이 정해졌는데 STEP대기_로 남은 구매품이 모두 0. 사용자 자료로만 풀리는 것(기종 미정, 납품처 기준, 사이트 로그인)만 남으면 '사용자 자료 대기'로 멈추고 그 목록을 최종 보고 맨 위에. '완료'라고 쓰지 않는다.
   - R1: tasks를 손으로 쓰지 않고, 요구서 5절 과제·디테일링 구동 후보·STEP대기_ 목록에서 다음 라운드 과제를 만든다.
   - E-02 순서(구동 → 브래킷 → 디테일)는 그대로.
2. 프로젝트 규칙 파일 인자
   - 두 워크플로우가 인자 rulesFile(예: <root>/tools/run-rules.md)을 받아 그 내용을 모든 부서 지시문 머리에 붙인다. shellNote는 실행마다 바뀌는 것만. 둘 다 주면 둘 다 붙인다. 파일이 없으면 시작하지 않고 알린다.
   - templates/project-layout.md 인자 표에 추가.
3. 개선후보 반영 (engine-candidates.md 제안 수정 칸대로)
   - WF-080 로그인 풀림 보고 단계(구매부 login:false + 최종 보고 맨 위 로그인 상태·못 받은 형번)
   - WF-081 STEP대기_ 다시 받아 실물로 바꾸는 단계(라운드 시작 또는 끝에 자동)
   - WF-082 MCP backend 판정을 안내문이 아니라 실제 연결 상태로(앱이 켜져 있으면 모델링부는 MCP)
   - WF-083 문서·커밋이 끝나기 전에 다음 과제를 시작하지 않거나, 멈춤 지점 명시
   - WF-084 외부 조건(login:false·STEP 미수령)이 원인인 남은 문제엔 수정 회차를 돌리지 않음
   - WF-085 엔진 tools/*.py UTF-8 출력
   - WF-086 machine.json 없으면 motion_states.json 또는 config 경로
   - WF-087 1000단계 넘는 연구의 전 단계 검사 방법(분할)
   - WF-088 gmsh 없으면 다른 측정 경로
   - WF-089 구매품 STEP bbox 대신 부피·끝면 프로브
   - WF-090 예외 승인 전 CLI 시험 1회
   - WF-091 버전 저장 뒤 ledger.py commit 필수
   - WF-051~056 (준비부 지시 모순, 0-2 빈칸, 6-4 덮음 확인, 초기화 대상 없음, CLI 함정 안내서, matcheck BOM 없음)
   - 반영한 것은 FSAP 쪽이 아니라 엔진 engine/improvement-candidates.md '반영' 표로 옮긴다.
4. 엔진 버전을 올리고 engine/CHANGELOG.md에 적는다. 가짜 에이전트 시험(node workflows/run_tests_node.js)을 통과시킨다.
