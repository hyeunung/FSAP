# 준비 점검 — FSAP_v2.30.5 (2026-11-28, 엔진 v4.1.2, 구동부 끝 전 구간 회귀 앞 — RX-16 · RX-13-C1 보류 C-55)

요약
- 판정: **ready=true**, 빠진 것 0. 대상은 `3D_Modeling/FSAP_v2.30.5.sc`(tools/config.json doc, 64,984,519 B, sha1 98c7b5a5…, 커밋 1346a33 RX-DC-C1 해결본)다.
- **MCP로는 저장본을 못 열었다(앞 점검과 같음, 다음 부서가 알아야 할 것).** 이 세션의 MCP 서버(pid 42776)는 `--allow-path` 없이 떠 있다. `open {path: 3D_Modeling/FSAP_v2.30.5.sc}` → 「outside the folders this agent may use (…/SolidCraft/recovery, …/Temp/solidcraft-mcp-42776-27b6bf8)」. 이 실행 지시 (마) "MCP 서버가 3D_Modeling/ 열기를 거부하면 CLI로 하고 보고서에 적는다"대로 CLI로 쟀다. 설정은 고치지 않았다.
- 통로: 앱 상태는 MCP(`running` 빈 목록, 열린 문서 Untitled · dirty false · 피처 0), 측정은 CLI 한 번(`solidcraft-cli run script.json --in … --results`, 저장 없음, 5개 명령 한 묶음). 걸린 시간 205 s(거의 다 열기). 원본 `tools/out/prep2305/`(script.json · results.json · analyze.py · analyze.out).
- 타임라인: 피처 4,537(v2.30.3보다 +5), 마커 4537(끝), **오류 0**, 경고 254(BaseFeature 251 · Chamfer 3, 불러온 형상 — 앞보다 BaseFeature +1), 억제 · 롤백 0, dirty false. 바디 999.
- 조인트: 658개(rigid 379 · slider 265 · revolute 14 — 앞보다 rigid +1), 고정부 [0, 2], **floating 0**, conflicts 0, errors 0, 링크 36.
  - machine.json joints 247개 중 설계에 없는 것: `J_U4S_SLOT` 1개(기록용, 앞과 같음)
  - 설계의 움직이는 조인트 중 machine.json에 없는 것: 34개 `J_U5_CHN_*`(케이블 베어 링크, 기계 축 아님, 앞과 같음)
  - 상태 61개가 쓰는 조인트 48개와 연구 이름은 모두 설계에 있다.
- 연구 15개의 단계 수가 machine.json과 모두 같다: REST 1 · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_V2 630 · CYCLE_W1 583 · CYCLE_W2 585 · CYCLE_P1 461 · CYCLE_P2 627 · MAINT_HEAD 1 · MAINT_U7 14 · BIND_U7 4 · SEAM_U7 19(합 6,307단계 — 전 구간 회귀가 돌 양).
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 239, positions 3,488. 저장본이 이미 대기 포즈다.
- machine.json(sha1 f68c3994, 커밋 6cf5ea1 뒤 안 바뀜): units 27 · states 61 · path_parts 6 · workpiece_stages · temp_values 15. 유닛 21개(작업 대상 6개 제외)가 모두 설계 최상위 occurrence로 있다.
- 작업 대상 모형(서명 표 `tools/out/signatures.json`, doc_hash 98c7b5a5 = v2.30.5 — 서명이 지금 저장본과 맞는다):
  - 크기 범위 양 끝: 작은 끝 MAT_S, 큰 끝 MAT_L(D-01 임시값, 앞 점검 300×200×10 · 1500×1500×10 그대로)
  - 형상별: MAT_G(좁은 홈) · MAT_V · MAT_W · MAT_P, 두께 모형 MAT_T06 · MAT_T16
  - 가공 뒤 형상: 테이프 조각 TP_L 48 · TP_S 11 · TP_G 40 · TP_V 40 · TP_W 44 · TP_P 39, 이음매 겹 SEAM_L·S·G·V·W·P
  - 떨어지는 조각: 없음(D-07, machine.json fragments)
- 상태 ↔ 요구서 0-3 · 6-4: machine.json이 앞 점검 뒤 바뀌지 않았다(sha1 같음). 0-3의 ①~⑤ 각 단계와 6-4의 상태(직선 · 볼록 모서리 · 오목 모서리 · 홈 입구 · 홈 바닥 꺾임 · 시작·끝 이음매)에 상태가 하나 이상 대응한다(① 2 · ② 3 · ③ 25 · ④ 15 · ⑤/⑥ 배출 5 · 정비 2 · 그 밖 9).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).

## 다음 부서에 넘길 것

- **MCP 허용 폴더.** 같은 서버가 붙은 부서는 `3D_Modeling/` 경로 `open` · `save`가 거부된다. 그때는 지시 (마)대로 CLI로 한다. v2.30.5의 CLI 열기는 약 200 s다(안내서 '모델 무게' 상한 240 s 안).
- 앱은 빈 설계(Untitled, dirty false)다. 이번 점검은 앱 문서를 건드리지 않았다(편집 0, 저장 0, 포즈 변경 0).
- machine.json의 `doc` 칸이 `../3D_Modeling/FSAP_v2.30.2.sc`로 남아 있다(v2.30.3~v2.30.5 저장 때 안 고쳤다). 준비 못 함은 아니다(검사 대상은 config.json doc). 다음에 새 번호를 저장하는 모델링부가 고친다.
- RX-16 · RX-13-C1은 C-55로 보류라 이 점검에서 준비물을 따지지 않았다. U4 X 행정은 지금 모델(`J_U4_X` 0~95, d₁ 100~195) 그대로 본다.
- 전 구간 회귀부에: 연구 15개 · 6,307단계, 바디 999, 저장본 열기 약 200 s가 `regrun.py` 어림의 입력이다.

근거:
- E-03 "어느 단계든 합격의 첫 조건은 작업 대상을 넣은 전 구간 동작과 간섭 0이다"
- E-15 "기계의 모든 움직임은 CAD 조인트(슬라이드·회전)와 리지드 그룹·모션 링크로 정의한다"
- 안내서 '동작 검사'(고정부 · `joint.list`의 `floating` · 동작 연구 · 작업 대상 모형), '동작 상태 초기화'(`motion.play {"study","step":0}`)
- 안내서 '원복' "읽기 부서가 CLI로만 쟀다면 원복할 것이 없다"
- E-21 "이전 시도가 남긴 결과 파일을 먼저 읽고 남은 것만 한다"(스크립트 · 분석기는 `prep2303` 것을 다시 썼고, machine.json · 작업 대상 크기는 바뀌지 않아 앞 결과와 서명 표를 썼다)
- 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다"
- 실행 규칙 13 "RX-16 · RX-13-C1 보류 … 구동부는 지금 모델(d₁ 100~195)로 닫는다"

시간: 약 5분(예상 10분 안). 통로 MCP+CLI. CAD 호출 5(MCP `running` 1 · `inspect_design` 2 · `open` 거부 1, CLI `run` 1), 파일 열기 1, open_s 205, 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 워크플로우 세션의 MCP 서버가 `--allow-path` 없이 떠 있어 `3D_Modeling/` 열기가 또 거부됐다(WF-231 반복, 11-27 점검과 같은 pid 42776). 혼자 도는 읽기 부서가 MCP로 한 번 열고 이어 재는 길(실행 규칙 2)이 막혀 부서마다 CLI 열기 약 200 s가 붙는다.

---

# 준비 점검 — FSAP_v2.30.3 (2026-11-27, 엔진 v4.1.2, 구동 라운드 이어서 — RX-DC-C1 해석 불합격 수정 전)

요약
- 판정: **ready=true**, 빠진 것 0. 대상은 `3D_Modeling/FSAP_v2.30.3.sc`(tools/config.json doc, 68,109,251 B, sha1 af0caeca…, RX-DC-C1 모델링 1회차 저장본, 아직 커밋 안 됨)다.
- **MCP로는 저장본을 못 열었다(다음 부서가 알아야 할 것).** 이 세션에 붙은 MCP 서버는 `solidcraft-cli mcp`만으로 뜬 것(pid 42776, 2026-11-26 23:24 시작)이라 `--allow-path`가 없다. `open {path: 3D_Modeling/FSAP_v2.30.3.sc}` → 「outside the folders this agent may use (…/SolidCraft/recovery, …/Temp/solidcraft-mcp-42776-27b6bf8)」. `~/.claude.json`의 설정과 그렇게 뜬 서버(pid 37796·31100·44216, 02:07 뒤 시작)는 따로 있다. 설정은 고치지 않았다. 이 실행 지시 (f) "3D_Modeling/ 열기·저장이 거부되면 CLI로 하고 보고서에 적는다"대로 CLI로 쟀다.
- 통로: 앱 상태는 MCP(`running` 빈 목록, 열린 문서 Untitled · dirty false · 피처 0 — 02:09에 새로 켠 그대로), 측정은 CLI 한 번(`solidcraft-cli run script.json --in … --results`, 저장 없음). 스크립트 하나에 5개 명령을 묶어 저장본을 한 번만 열었다. 걸린 시간 179 s(명령 합 0.28 s, 나머지가 열기). 원본 `tools/out/prep2303/`(script.json · results.json · analyze.py · analyze.out).
- 타임라인: 피처 4,532(v2.30.2보다 +20), 마커 4532(끝), **오류 0**, 경고 253(BaseFeature 250 · Chamfer 3, 불러온 형상 — 앞과 같음), 억제·롤백 0, dirty false.
- 조인트: 657개(rigid 378 · slider 265 · revolute 14), 고정부 [0, 2], **floating 0**, conflicts 0, errors 0, 링크 36. v2.30.2와 같다(RX-DC-C1은 조인트를 바꾸지 않았다).
  - machine.json joints 247개 중 설계에 없는 것: `J_U4S_SLOT` 1개(기록용, 앞과 같음)
  - 설계의 움직이는 조인트 중 machine.json에 없는 것: 34개 `J_U5_CHN_*`(케이블 베어 링크, 기계 축 아님, 앞과 같음)
  - 상태 61개가 쓰는 조인트 48개와 연구 이름은 모두 설계에 있다.
- 연구 15개의 단계 수가 machine.json과 모두 같다: REST 1 · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_V2 630 · CYCLE_W1 583 · CYCLE_W2 585 · CYCLE_P1 461 · CYCLE_P2 627 · MAINT_HEAD 1 · MAINT_U7 14 · BIND_U7 4 · SEAM_U7 19.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 239, positions 3,487. 저장본이 이미 대기 포즈다.
- machine.json(sha1 f68c3994, 커밋 6cf5ea1 뒤 안 바뀜): units 27 · states 61 · path_parts 6 · workpiece_stages · temp_values 15. 유닛 21개(작업 대상 6개 제외)가 모두 설계 최상위 occurrence로 있다.
- 작업 대상 모형(서명 표 `tools/out/signatures.json`, doc_hash af0caeca = v2.30.3):
  - 크기 범위 양 끝: 작은 끝 MAT_S 300×200×10, 큰 끝 MAT_L 1500×1500×10(D-01 임시값)
  - 형상별: MAT_G(좁은 홈) · MAT_V · MAT_W · MAT_P, 두께 모형 MAT_T06 · MAT_T16
  - 가공 뒤 형상: 테이프 조각 TP_L 48 · TP_S 11 · TP_G 40 · TP_V 40 · TP_W 44 · TP_P 39, 이음매 겹 SEAM_L·S·G·V·W·P
  - 떨어지는 조각: 없음(D-07, machine.json fragments)
- 상태 ↔ 요구서 0-3·6-4: phase로 세면 ① 2 · ② 3 · ③ 25 · ④ 15 · ⑤/⑥ 배출 5 · 정비 2 · 그 밖 9. 0-3의 ①~⑤ 각 단계와 6-4의 상태(직선 · 볼록 모서리 · 오목 모서리 · 홈 입구 · 홈 바닥 꺾임 · 시작·끝 이음매)에 상태가 하나 이상 대응한다(앞 점검과 같음, machine.json 그대로).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).

## 다음 부서에 넘길 것

- **MCP 허용 폴더.** 다음 부서의 세션에도 같은 서버가 붙으면 `3D_Modeling/` 경로 `open`·`save`와 `tools/out/` 경로 `batch {path}`가 거부된다. 그때는 지시 (f)대로 CLI(`solidcraft-cli run <edit.json> --in <이전 버전> --save <새 번호>`)로 한다. 지금 v2.30.3의 CLI 열기는 약 180 s다(머리글의 13~27분보다 짧다 — RX-DC-C1 저장 확인 297 s와 맞는다).
- 앱은 빈 설계(Untitled, dirty false)다. 이번 점검은 앱 문서를 건드리지 않았다(편집 0, 저장 0, 포즈 변경 0).
- machine.json의 `doc` 칸이 `../3D_Modeling/FSAP_v2.30.2.sc`로 남아 있다(v2.30.3 모델링 1회차가 안 고쳤다). 준비 못 함은 아니다. RX-DC-C1 수정 회차를 저장하는 모델링부가 새 번호로 고친다.
- RX-DC-C1 수정은 조인트·연구를 바꾸지 않는 형상 추가(세움 받침 꺾음 날 아래 플랜지)다. 관련 조인트는 `J_U4_X`·`J_U4_LOOP`(U4_CABLE_LOOP), 모두 설계와 machine.json에 있다.

근거:
- E-03 "어느 단계든 합격의 첫 조건은 작업 대상을 넣은 전 구간 동작과 간섭 0이다"
- E-15 "기계의 모든 움직임은 CAD 조인트(슬라이드·회전)와 리지드 그룹·모션 링크로 정의한다"
- 안내서 '동작 검사'(고정부 · `joint.list`의 `floating` · 동작 연구 · 작업 대상 모형), '동작 상태 초기화'(`motion.play {"study","step":0}`)
- 안내서 '원복' "읽기 부서가 CLI로만 쟀다면 원복할 것이 없다"
- E-21 "이전 시도가 남긴 결과 파일을 먼저 읽고 남은 것만 한다"(machine.json · 작업 대상 크기는 바뀌지 않아 앞 결과와 서명 표를 썼다)
- 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다"

시간: 약 6분(예상 10분 안). 통로 MCP+CLI. CAD 호출 7(MCP `running` 2 · `document.metadata` · `list_commands` · `inspect_design` · `open` 거부 1, CLI `run` 1), 파일 열기 1, open_s 179, 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 워크플로우 세션에 붙는 MCP 서버가 `~/.claude.json`의 `--allow-path` 설정과 다른 프로세스다(인자 없는 `solidcraft-cli mcp`, 설정을 고친 서버보다 먼저 떠 있던 것). 앱을 새로 켜 열린 문서가 없으면 `3D_Modeling/`도 허용 폴더에 없다(11-24에는 앱에 저장본이 열려 있어 그 폴더는 허용됐다). 시작 때 '이 세션 서버의 허용 폴더에 프로젝트가 드는가' 확인이 없다(WF-231 반복).
- 지시 머리글의 'CLI 열기 13~27분'은 지금 모델에 맞지 않는다. v2.30.3은 179 s다. 통로를 고를 때 낡은 수치가 MCP 임시 복사본 우회 쪽으로 기울게 한다.

---

# 준비 점검 — FSAP_v2.30.2 (2026-11-24, 엔진 v4.0.0, 구동 라운드 다시 부름 — RX-DC-03 뒤)

요약
- 판정: **ready=true**, 빠진 것 0. 대상은 `3D_Modeling/FSAP_v2.30.2.sc`(tools/config.json doc, 커밋 6cf5ea1 RX-DC-03)다. 지시 머리글은 v2.25.2를 적었지만 실행 규칙 3 "최신 파일은 `tools/config.json` doc가 가리키는 것이다"를 따랐다. 파일은 68,183,407 B, sha1 54be2ad9…다.
- 모델이 v2.29.3에서 바뀌었으므로(RX-DC-03: U4_CABLE_LOOP, `J_U4_LOOP`) 조인트·연구·타임라인·초기화를 모두 다시 쟀다. 원본은 `tools/out/prep2302/`(jl·ml·di·mp.json, analyze.out)에 있다.
- 통로는 MCP다(`running` 빈 목록). 앱에 열린 문서는 FSAP_v2.30.2이고, 경로가 저장본과 같고, dirty false다. 그래서 다시 열지 않았다(file_opens 0). 저장 0, 편집 0.
- 타임라인: 피처 4,512, 마커 4512(끝), **오류 0**, 경고 253(BaseFeature 250 · Chamfer 3, 불러온 형상), 억제·롤백 0.
- 조인트: 657개(rigid 378 · slider 265 · revolute 14), 고정부 [0, 2], **floating 0**, conflicts 0, errors 0, 링크 36. 새 조인트는 `J_U4_LOOP`(slider)와 리지드 그룹 8개이고, `J_U4_LOOP`는 machine.json에 있다.
  - machine.json joints 247개 중 설계에 없는 것: `J_U4S_SLOT` 1개(기록용, 앞과 같음)
  - 설계의 움직이는 조인트 중 machine.json에 없는 것: 34개 `J_U5_CHN_*`(케이블 베어 링크, 기계 축 아님, 앞과 같음)
- 연구 15개의 단계 수가 machine.json과 모두 같다: REST 1 · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_V2 630 · CYCLE_W1 583 · CYCLE_W2 585 · CYCLE_P1 461 · CYCLE_P2 627 · MAINT_HEAD 1 · MAINT_U7 14 · BIND_U7 4 · SEAM_U7 19.
- machine.json 구성: units 27(U4_CABLE_LOOP 추가) · states 61 · path_parts 6 · workpiece_stages · temp_values 15(D-번호 임시값 — 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다"). `doc` 칸은 `../3D_Modeling/FSAP_v2.30.2.sc`로 고쳐졌다(앞 지적 해소).
- 작업 대상 모형:
  - 크기 범위 양 끝: 작은 끝 WP_MAT_S, 큰 끝 WP_MAT_L
  - 형상별 모형: WP_MAT_G · V · W · P, 두께 모형 MAT_T06·T16
  - 가공 뒤 형상: WP_TAPE_*(외곽 띠), WP_TP_*_SEAM(이음매 겹)
  - 떨어지는 조각: 없음(D-07, machine.json fragments)
- 상태 ↔ 요구서 0-3 ①~⑥·6-4: 상태 61의 phase가 ① 대기·로딩 ~ ⑤ 배출을 모두 덮어 앞 점검과 같다.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}`의 결과는 moved false, conflicts 0, unmoved 0, values 239, positions 3,487(+9, 새 루프 부품)이다.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).

근거:
- E-03 "동작·간섭이 최우선이다"
- 안내서 '동작 상태 초기화'(`motion.play {"study","step":0}`)
- E-08 원복
- E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"(분석 스크립트를 prep2293에서 재사용)

시간: 약 2분. 통로 MCP, CAD 호출 7(running · document.metadata · inspect_design ×2 · joint.list · motion.list · motion.play), 파일 열기 0, 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- `inspect_design`을 모두 false로 불러도 153 KB였다. 결함 목록 때문에 문서 이름과 dirty를 볼 때마다 큰 응답이 온다. 가벼운 문서 상태 명령이 있으면 좋겠다(앞 메모 반복).

---

# 준비 점검 — FSAP_v2.29.3 세 번째 확인 (2026-11-24, 엔진 v4.0.0, 구동 라운드 다시 부름 — STEPWAIT 재실행 2 뒤)

요약
- 판정: **ready=true**, 빠진 것 0. 대상 `3D_Modeling/FSAP_v2.29.3.sc`(tools/config.json doc). 지시 머리글은 v2.25.2라고 적었지만 실행 규칙 3 "최신 파일은 `tools/config.json` doc가 가리키는 것이다"를 따랐다.
- 모델은 바뀌지 않았다: sha1 80a0c10a…(같음), 68,222,639 B, 더 새 .sc 없음. 마지막 모델 커밋은 3808c84(v2.29.3)이고, 그 뒤 커밋(9b0966d · 28533ec · c47c3d1 등)은 보고서·회고·실행 기록뿐이다. E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"에 따라 조인트·연구·machine.json·작업 대상 모형·상태 대응은 `tools/out/prep2293/`의 결과를 그대로 썼다. 세 값은 앞 점검과 같다: 조인트 648, floating 0, 연구 15개.
- 통로는 MCP다(`running` 빈 목록). 앱에 열린 문서는 FSAP_v2.29.3이고 경로가 저장본 그대로다. dirty false, 마커 4447, `document.revision` 3. 그래서 다시 열지 않았다(file_opens 0). 저장 0, 편집 0.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}`의 결과는 moved false, conflicts 0, unmoved 0, values 239, positions 3,478로 앞 점검과 같다. 원본은 `tools/out/prep2293b/mp.json`.
- 남은 지적(준비 못 함 아님): machine.json의 `doc` 칸이 아직 `../3D_Modeling/FSAP_v2.28.1.sc`다. 다음에 저장하는 모델링부가 고친다.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).

근거:
- E-03 "동작·간섭이 최우선이다"
- E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"
- 안내서 '동작 상태 초기화'(`motion.play {"study","step":0}`)
- E-08 원복
- 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다"

시간: 약 1분. 통로 MCP, CAD 호출 6(running · list_commands · document.revision · document.metadata · inspect_design · motion.play), 파일 열기 0, 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 모델 해시가 같은 채 세 번째로 불렸다. 해시가 같으면 준비 점검을 건너뛰는 규칙이 있으면 좋겠다(앞 메모 반복).
- `motion.play`의 응답이 1.3 MB였다(positions 3,478 전부). 이것도 파일로 받아 요약만 봤다.

---

# 준비 점검 — FSAP_v2.29.3 다시 확인 (2026-11-24, 엔진 v4.0.0, 구동 라운드 다시 부름 — RX-DC-03-STEPWAIT 뒤)

요약
- 판정: **ready=true**, 빠진 것 0. 대상 `3D_Modeling/FSAP_v2.29.3.sc`(tools/config.json doc). 지시 머리글은 v2.25.2를 적었지만, 그 뒤 RX-19(v2.29.0~v2.29.2)와 RX-DC-02(v2.29.3)가 저장했다. 실행 규칙 3에 "최신 파일은 `tools/config.json` doc가 가리키는 것이다"라고 돼 있어 v2.29.3을 대상으로 했다.
- 앞 점검(아래 'FSAP_v2.29.3' 절) 뒤로 모델은 바뀌지 않았다: sha1 80a0c10a…(같음), 68,222,639 B, 더 새 .sc 없음. 그 뒤 커밋(1bace16 · b996d2a · 2d0444b · 1d7d9ac · 3d0c678)은 보고서·실행 기록·회고뿐이다. E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"에 따라 조인트·연구·machine.json 세기는 `tools/out/prep2293/` 결과를 그대로 쓰고, 열린 세션 상태와 동작 상태 초기화만 다시 쟀다.
- 통로: MCP(`running` 빈 목록). 앱에 v2.29.3이 저장 경로 그대로 열려 있다(이름 FSAP_v2.29.3, dirty false, redo 0, 마커 4447). 그래서 다시 열지 않았다(file_opens 0). 저장 0, 편집 0.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 239, positions 3,478. 앞 점검과 같은 값이다.
- 그대로 쓴 값(앞 점검):
  - 타임라인: 피처 4,447, 오류 0
  - 조인트: 648개, floating 0, 고정부 [0, 2]
  - 연구 15개: 단계 수가 machine.json과 같음
  - machine.json: units 26 · states 61 · path_parts 6 · workpiece_stages · temp_values 15
  - 작업 대상 모형: 작은 끝 WP_MAT_S 300×200, 큰 끝 WP_MAT_L 1500×1500, G·V·W·P, 가공 뒤 띠·테이프 조각·이음매 겹. 떨어지는 조각은 없음(D-07).
  - 상태 ↔ 요구서 0-3 ①~⑥ 단계와 6-4 상태: 모두 대응
- 남은 지적(준비 못 함 아님): machine.json `doc` 칸이 `../3D_Modeling/FSAP_v2.28.1.sc`로 남아 있다. 다음에 저장하는 모델링부가 고친다.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).

근거: E-03 "동작·간섭이 최우선이다", E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", 안내서 '동작 상태 초기화'(`motion.play {"study","step":0}`), E-08 원복, 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다".

시간: 약 1분. 통로 MCP. CAD 호출 3(running · inspect_design · motion.play), 파일 열기 0, 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 모델이 바뀌지 않은 채 다시 불렸다(STEPWAIT 실행 기록 뒤). 해시가 같으면 준비 점검을 건너뛰는 규칙이 있으면 시간을 줄일 수 있다.
- `inspect_design`을 timeline·bodies·joints·sketches 모두 false로 불러도 응답이 150 KB였다(불러온 형상 결함 목록 때문). `document.inspect`와 마찬가지로 파일로 받아 grep 하는 방식이 맞다.

---

# 준비 점검 — FSAP_v2.29.3 (2026-11-24, 엔진 v4.0.0, 구동 라운드 다시 부름 — RX-19·RX-DC-02 뒤)

요약
- 판정: **ready=true**, 빠진 것 0. 대상 `3D_Modeling/FSAP_v2.29.3.sc`(tools/config.json doc — 지시 머리글의 v2.25.2 뒤로 RX-19(v2.29.0~v2.29.2)·RX-DC-02(v2.29.3)가 저장했다. 최신은 config doc, 실행 규칙 3 "최신 파일은 `tools/config.json` doc가 가리키는 것이다"). 68,222,639 B, sha1 80a0c10a….
- 타임라인: 피처 4,447, **오류 0**, 경고 245(BaseFeature 242 · Chamfer 3 — 불러온 형상 경고), 억제·롤백 0, 마커 끝(4447). 불러온 형상 결함 목록 386(repaired 370 · needs_repair 16).
- 통로: MCP(앱 0.45.0 commit e8ce12ef, mode app, `running` 빈 목록). **앱에 v2.29.3이 저장 경로 그대로 열려 있었다**(이름 FSAP_v2.29.3, 경로 `3D_Modeling/FSAP_v2.29.3.sc`, dirty false, redo 0, undo 200 = 앞 모델링부가 편집 뒤 그 경로로 저장한 세션). dirty false라 다시 열지 않고 그 세션에서 쟀다(file_opens 0, open_s 0). 저장 0, 편집 0, 앱 재시작 0.
- 조인트 648(rigid 370 · slider 264 · revolute 14; RX-19로 rigid 401 → 370), 고정부 [0, 2], **floating 0**, conflicts 0, errors 0, 링크 35. U4 움직이는 조인트: J_U4_X · J_U4_PRESS(그네 피벗) · J_U4S_ROD · J_U4_STOP · J_U4_WHEEL_ROT · J_U4_DISK. machine.json joints 246 중 설계에 없는 것 1: `J_U4S_SLOT`(기록용, 앞 점검들과 같음). 설계의 움직이는 조인트 중 machine.json에 없는 것 34: `J_U5_CHN_B`·`J_U5_CHN_L02~L17`·`J_U5_CHN_U01~U17`(U5 케이블 베어 링크 — 기계 축 아님, 앞 점검과 같음).
- 연구 15개, 단계 수 machine.json과 모두 같음: REST 1 · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_V2 630 · CYCLE_W1 583 · CYCLE_W2 585 · CYCLE_P1 461 · CYCLE_P2 627 · MAINT_HEAD 1 · MAINT_U7 14 · BIND_U7 4 · SEAM_U7 19.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 239, positions 3,478. dirty false 그대로.
- machine.json: units 26, states 61, path_parts 6, workpiece_stages(fragments · sim_tape · WP_W · WP_P + 노트), temp_values 15(D-01 · D-02·D-03 · D-04 · D-06·D-07 · D-10 · D-93 · D-99 · D-104~D-107 · RX-12 · RX-17(D-213) · D-211 · D-212). _history에 v2.29.0·v2.29.1(RX-19)·v2.29.3(RX-DC-02) 기록 있음. **`doc` 칸이 `../3D_Modeling/FSAP_v2.28.1.sc`로 남아 있다** — _history와 연구 단계 수가 v2.29.3과 맞으므로 준비 못 함은 아니다(다음 저장하는 모델링부가 doc를 고친다).
- 작업 대상 모형(REST 포즈 occurrence): 매트 WP_MAT_S(작은 끝 300×200)·WP_MAT_L(큰 끝 1500×1500)·WP_MAT_G·V·W·P, 가공 뒤 띠 WP_TAPE_S·L·G·V·W·P, 붙는 테이프 조각 WP_TP_*(S 7 · L 43 · G 35 · V 35 · W 38 · P 27) + 이음매 겹 WP_TP_*_SEAM 6, 매트 평면 운동 축 WP_*_X·Y. 떨어지는 조각은 없음(machine.json workpiece_stages.fragments, D-07). 앞 점검과 같다.
- 상태 ↔ 요구서 0-3·6-4: 상태 61의 phase에 ① 대기·로딩 · ② 바퀴 내림(바늘 옆·먼 쪽) · ③ 외곽 봉제(직선·볼록 모서리·홈 입구·홈 안 벽·홈 바닥 꺾임·V 꼭짓점·오목 바닥·둥근 모서리·띠) · ④ 이음매 겹침·오목 안 모서리 회전 · ⑤/⑥ 배출이 모두 하나 이상 대응. 6-4 상태(직선, 볼록·오목 모서리, 홈 입구, 홈 바닥 꺾임, 이음매)도 대응(상태 집합은 v2.28.1 점검과 같고 RX-19는 값만 환산).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).

근거: E-03 "동작·간섭이 최우선이다", 안내서 '동작 상태 초기화'(`motion.play {"study","step":0}`), E-08 원복, E-21(이전 결과 파일부터), 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다". 원본 결과: `tools/out/prep2293/`(di.json · jl.json · ml.json · mp.json · analyze.py · analyze.out).

시간: 약 1분 30초(예상 10분 안). 통로 MCP, CAD 호출 6(running · version · document.inspect · motion.play · joint.list · motion.list), 파일 열기 0(저장 경로 그대로 열린 dirty false 문서 사용), 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- machine.json `doc` 칸이 이번에도 저장 버전(v2.29.3)을 따라가지 않았다(v2.28.1). 앞 점검 메모와 같은 문제 — 버전 올릴 때 doc 칸 확인을 모델링부 저장 단계에 두면 좋다.
- `document.inspect` 한 번(1.2 MB)으로 열린 문서 경로·dirty·undo·타임라인·결함을 다 얻었다. `inspect_design` 여러 번보다 빠르다.

---

# 준비 점검 — FSAP_v2.28.1 (2026-11-24, 엔진 v4.0.0, 구동 라운드 다시 부름)

요약
- 판정: **ready=true**, 빠진 것 0. 대상 `3D_Modeling/FSAP_v2.28.1.sc`(tools/config.json doc — 지시 머리글의 v2.25.2 뒤로 같은 날 RX-19 등 과제가 v2.26.0~v2.28.1까지 저장했다. 최신은 config doc를 따른다, 실행 규칙 3 "최신 파일은 `tools/config.json` doc가 가리키는 것이다"). 66,431,323 B, sha1 ae8716c8….
- 타임라인: 피처 4,321, **오류 0**, 경고 272(BaseFeature 269 · Chamfer 3 — 불러온 형상 경고, 앞 점검 271에서 +1), 억제·롤백 0, 마커 끝(4321). 불러온 형상 결함 목록 413(repaired 397 · needs_repair 16).
- 통로: MCP(앱 0.45.0 commit e8ce12ef, mode app, `running` 빈 목록). **앱에 v2.28.1 복사본이 이미 열려 있었다**: 이름 FSAP_v2.28.1, 경로 `C:/Users/hyeun/AppData/Local/Temp/solidcraft-mcp-32572-2f1dd8d0/FSAP_v2.28.1.sc`, dirty false, undo 21(앞 부서 포즈) — 복사본 sha1이 저장본과 같아(ae8716c8…) 다시 열지 않았다(file_opens 0, open_s 0). 저장 0, 편집 0, 앱 재시작 0.
- 조인트 679(rigid 401 · slider 264 · revolute 14), 고정부 [0, 2], **floating 0**, conflicts 0, errors 0, 링크 35. machine.json joints 246 중 설계에 없는 것 1: `J_U4S_SLOT`(기록용, 앞 점검들과 같음). 설계의 움직이는 조인트 중 machine.json에 없는 것 34: `J_U5_CHN_B`·`J_U5_CHN_L02~L17`·`J_U5_CHN_U01~U17`(U5 케이블 베어 링크 — 기계 축 아님, 앞 점검과 같음).
- 연구 15개, 단계 수 machine.json과 모두 같음: REST 1 · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_V2 630 · CYCLE_W1 583 · CYCLE_W2 585 · CYCLE_P1 461 · CYCLE_P2 627 · MAINT_HEAD 1 · MAINT_U7 14 · BIND_U7 4 · SEAM_U7 19.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 239, positions 3,509. 뒤에 dirty false(undo 22 = 포즈 하나 더), 마커 4321.
- machine.json: `doc` = `../3D_Modeling/FSAP_v2.28.1.sc`(맞음 — 앞 점검의 doc 칸 지적 풀림), units 26, states 61, path_parts 6, workpiece_stages(fragments · sim_tape · WP_W · WP_P + 노트), temp_values 15(D-01 · D-02·D-03 · D-04 · D-06·D-07 · D-10 · D-93 · D-99 · D-104~D-107 · RX-12 · RX-17(D-213) · D-211 · D-212).
- 작업 대상 모형(REST 포즈 occurrence로 셈): 매트 WP_MAT_S(작은 끝 300×200)·WP_MAT_L(큰 끝 1500×1500)·WP_MAT_G·V·W·P, 가공 뒤 띠 WP_TAPE_S·L·G·V·W·P, 붙는 테이프 조각 WP_TP_*(S 8 · L 44 · G 36 · V 36 · W 39 · P 28, 이음매 겹 WP_TP_*_SEAM 6개 포함). 떨어지는 조각은 없음(machine.json workpiece_stages.fragments, D-07).
- 상태 ↔ 요구서 0-3·6-4: 상태 61의 phase에 ① 대기·로딩 · ② 바퀴 내림(바늘 옆·먼 쪽) · ③ 외곽 봉제(직선·볼록 모서리·홈 입구·홈 안 벽·홈 바닥 꺾임·V 꼭짓점·오목 바닥·둥근 모서리·띠) · ④ 이음매 겹침·오목 안 모서리 회전 · ⑤/⑥ 배출이 모두 하나 이상 대응. 6-4 상태(직선, 볼록·오목 모서리, 홈 입구, 홈 바닥 꺾임, 이음매)도 대응. phase 없는 상태 5(정비·셋업 보조).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).

근거: E-03 "동작·간섭이 최우선이다", 안내서 '동작 상태 초기화'(`motion.play {"study","step":0}`), E-08 원복, E-21(이전 결과 파일부터), 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다". 원본 결과: `tools/out/prep2281/`(inspect.json · tl.json · jl.json · ml.json · mp.json · analyze.py).

시간: 약 2분 30초(예상 10분 안). 통로 MCP, CAD 호출 8(running · version · inspect_design 2 · motion.play · joint.list · motion.list), 파일 열기 0(같은 해시 복사본이 이미 열려 있음), 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- `joint.list`·`motion.list`·`motion.play`·`inspect_design`(timeline summary) 응답이 0.6~1.5 MB라 화면 한도를 넘어 파일로 떨어진다. 준비 점검은 처음부터 결과를 파일로 받아 스크립트로 세는 방식이 맞다(앞 점검과 같음).

---

# 준비 점검 — FSAP_v2.25.2 (2026-11-24, 엔진 v4.0.0, 구동 라운드: RX-19 먼저 → 남은 구동 과제 실행 전)

요약
- 판정: **ready=true**, 빠진 것 0. 대상 `3D_Modeling/FSAP_v2.25.2.sc`(tools/config.json doc, 64,775,729 B, sha1 7f37a99e…). 동작 정의·작업 대상 모형 다 있음.
- 타임라인: 피처 4,057, **오류 0**, 경고 271(BaseFeature 268 · Chamfer 3 — 불러온 형상 경고), 억제·롤백 0, 마커 끝(4057). 불러온 형상 결함 목록 412(repaired 396 · needs_repair 16). FIX-045 뒤 상태 그대로(다시 하지 않음).
- 통로: MCP(앱 0.45.0 commit e8ce12ef, mode app, `running` 빈 목록). **앱에 이미 v2.25.2가 열려 있었다**: 이름 FSAP_v2.25.2, 경로 `C:/Users/hyeun/AppData/Local/Temp/solidcraft-mcp-40196-3ada6fd0/check_v2.25.2.sc`, dirty false, undo 0 — 그 복사본 sha1이 저장본과 같아(7f37a99e…) 다시 열지 않고 그 세션에서 쟀다(file_opens 0, open_s 0). 저장 0, 편집 0, 앱 재시작 0.
- 조인트 666(rigid 400 · slider 255 · revolute 11), 고정부 [0, 2], **floating 0**, conflicts 0, errors 0, 링크 35. machine.json joints 233 중 설계에 없는 것 1: `J_U4S_SLOT`(기록용, 앞 점검들과 같음). 설계의 움직이는 조인트 중 machine.json에 없는 것 34: `J_U5_CHN_B`·`J_U5_CHN_L02~L17`·`J_U5_CHN_U01~U17`(U5 케이블 베어 링크 — 기계 축 아님, 연구 키로 따라감).
- 연구 15개, 단계 수 machine.json과 모두 같음: REST 1 · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_V2 630 · CYCLE_W1 583 · CYCLE_W2 585 · CYCLE_P1 461 · CYCLE_P2 627 · MAINT_HEAD 1 · MAINT_U7 14 · BIND_U7 4 · SEAM_U7 19.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 228, positions 3,307. 끝난 뒤 dirty false(undo 1 = 포즈), 마커 4057.
- machine.json: units 22, states 60, path_parts 6, workpiece_stages 있음(WP_S·L·G·V·W·P), temp_values 15(D-01 · D-02·D-03 · D-04 · D-06·D-07 · D-10 · D-93 · D-99 · D-104~D-107 · RX-12 · RX-17(D-213) · D-211 · D-212). **`doc` 칸이 `../3D_Modeling/FSAP_v2.23.0.sc`로 남아 있다**(v2.24~v2.25.2는 _history에 '조인트·연구 변화 0'으로 적혀 연구 단계 수가 다 맞으므로 준비 못 함은 아님 — RX-19 모델링부가 저장할 때 doc를 고친다).
- 작업 대상 모형: 매트 MAT_S(작은 끝)·MAT_L(큰 끝)·MAT_G·MAT_V·MAT_W·MAT_P(운전석, RX-17), 가공 뒤 테이프 조각 TP_S 11 · TP_L 48 · TP_G 40 · TP_V 40 · TP_W 44 · TP_P 39, 이음매 겹 SEAM_S·L·G·V·W·P. 떨어지는 조각은 없음(machine.json workpiece_stages.fragments, D-07).
- 상태 ↔ 요구서 0-3·6-4: 상태 60의 phase에 ① 대기·로딩 · ② 바퀴 내림 · ③ 외곽 봉제(직선·볼록·홈 입구·홈 안 벽·홈 바닥 꺾임·V 꼭짓점·오목 안 모서리·둥근 모서리) · ④ 이음매 겹침 · ⑤/⑥ 배출이 모두 하나 이상 대응. 6-4 상태(직선, 볼록·오목 모서리, 홈 입구, 홈 바닥 꺾임, 이음매)도 대응. 바인더·이음매 상태(RX-14·RX-15) 4개 더 있음.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- RX-19 몫(준비물 아님): U4 매달림 단순화 뒤 machine.json U4 조인트·상태 갱신, doc 칸 갱신. RX-16(d₁ 45 셋업)은 보류라 넣지 않는다.

근거: E-03 "동작·간섭이 최우선이다", 안내서 '동작 상태 초기화'(`motion.play {"study","step":0}`), E-08 원복, E-21(이전 결과 파일부터), 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다". 원본 결과: `tools/out/prep2252/`(tl.json · jl.json · ml.json · mp.json · bodies.json · timeline_issues.json · analyze.py).

시간: 약 2분 10초(예상 10분 안). 통로 MCP, CAD 호출 9(version 1 · running 1 · inspect_design 4 · joint.list · motion.list · motion.play), 파일 열기 0(이미 열린 같은 해시 복사본 사용), 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 앞 실행이 앱에 남긴 열린 문서가 저장본과 해시가 같으면 다시 열 필요가 없다(열기 200 s 넘게 아낌). 준비 점검 첫 단계로 '열린 문서 경로·dirty·undo + 복사본 sha1 비교'를 두면 좋다.
- machine.json `doc` 칸이 형상·조인트 변화 없는 버전 올림(v2.24~v2.25.2)에서 갱신되지 않았다. 버전 올릴 때 doc 칸을 같이 고치는 확인이 있으면 좋다.

---

# 준비 점검 — FSAP_v2.17.2 (2026-11-22, 엔진 v4.0.0, 구동 라운드: FIX-045 → RX-17 → RX-14 → … 실행 전)

요약
- 판정: **ready=true**, 빠진 것 0. 대상 `3D_Modeling/FSAP_v2.17.2.sc`(tools/config.json doc, 5,671,380 B, 2026-11-14, sha1 e6927e24…). 동작 정의(고정부·조인트·연구·machine.json)와 작업 대상 모형이 다 있다.
- 타임라인 **오류 103 · 경고 323은 그대로다**(앱 0.45.0, commit e8ce12ef). 오류 피처 집합이 2026-11-21 점검과 103개 모두 같다(id·이름 비교, 차 0). 사용자 결정이 끝난 알려진 상태(사용자 2026-11-22 "앞버전으로 못되돌려")라 '준비 못 함'으로 올리지 않는다. 과제 FIX-045가 먼저 혼자 돌아 0으로 만든다. 종류: ConvertToSheetMetal 28 · OffsetFaces 20 · Pipe 14 · BodyTransfer 13 · EdgeFlange 11 · Remove 7 · Chamfer 4 · Fillet 4 · Combine 1 · Thread 1. 목록 `tools/out/prep2172b/timeline_errors.json`.
- **MCP 허용 폴더 — 이번에도 거부됐다(FIX-045 모델링부가 알아야 할 것).** `~/.claude.json`에는 `--allow-path C:/Users/hyeun/OneDrive/Documents/workspace`가 들어 있고 그렇게 뜬 서버 프로세스도 있으나(pid 16468·37252), **이 워크플로우 세션에 붙은 서버는 `solidcraft-cli mcp`만으로 뜬 것**(pid 22072, 부모 16984, 00:06 시작)이다. `open {path: 3D_Modeling/FSAP_v2.17.2.sc}` → 「outside the folders this agent may use (…/SolidCraft/recovery, …/Temp/solidcraft-mcp-22072-29127a40)」. 설정은 고치지 않았다. 이 실행 지시 (f)대로 모델링부는 `3D_Modeling/` 열기·저장이 거부되면 CLI(`solidcraft-cli run --in --save`)로 한다.
- 통로: MCP. 앱 켜짐(pid 23484, `--control 27878`, 16:21 시작), `running` 빈 목록, 처음엔 빈 설계(Untitled, dirty false). 저장본을 서버 허용 임시 폴더에 복사해(sha1 같음, 원본 그대로) 한 번 열었다. `open`은 MCP 호출 시간 초과로 돌아왔고 서버 프로세스 22072가 사라져 「Server unavailable」이 약 2.5분 이어진 뒤 다시 붙었다(2026-11-21과 같은 현상). 열기는 210 s 안에 끝났다(정확한 초는 못 잼). 앱 재시작 0, 저장 0, 편집 0.
- 조인트 587(rigid 393 · slider 185 · revolute 9), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0, 링크 35. machine.json joints 161 중 설계에 없는 것 1: `J_U4S_SLOT`(기록용, 앞 점검과 같음).
- 연구 11개, 단계 수 machine.json과 모두 같음: REST 1 · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_W1 583 · CYCLE_W2 585 · MAINT_HEAD 1 · SEAM_U7 32 · MAINT_U7 13.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 156, positions 2,965. 끝난 뒤 dirty false, 피처 3,687(억제·롤백 0).
- machine.json: doc v2.17.2(맞음), units 21, states 44, path_parts 6, workpiece_stages 있음, temp_values 12. 작업 대상 모형 MAT_L·S·G·V·W + 테이프 조각 + SEAM 4(2026-11-21 점검 2절과 같음 — 파일이 같아 다시 재지 않음, E-21).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 지금 앱에 열린 것: 이름 FSAP_v2.17.2, 경로 `C:/Users/hyeun/AppData/Local/Temp/solidcraft-mcp-22072-29127a40/FSAP_v2.17.2.sc`(복사본), dirty false, 대기 포즈.

## 1. 이번에 다시 본 것과 앞 점검을 그대로 쓴 것

| 항목 | 이번(11-22) | 근거 |
|---|---|---|
| 앱 연결·막힘 | 연결됨, running 빈 목록 | `running`, `version`(0.45.0, mode app) |
| MCP 허용 폴더 | 워크스페이스 거부(위 요약) | `open` 오류 문구, 프로세스 명령줄 |
| 문서 확인 | 오류 103 · 경고 323 · 결함 목록 445, 앞 점검과 같은 집합 | prep2172b/inspect.json · timeline_errors.json |
| 고정부·floating | fixed [0, 2], floating 0, conflicts 0, errors 0 | prep2172b/joint_list.json |
| 연구 | 11개, 단계 수 machine.json과 같음 | prep2172b/motion_list.json |
| 대기 포즈 | REST step 0 moved false | prep2172b/rest_play.json |
| 원복 | dirty false, 피처 3,687 | prep2172b/inspect_after.json |
| 작업 대상 모형 · 상태 ↔ 요구서 0-3·6-4 | 앞 점검(아래 11-21 절 2·3) 그대로 — 저장본·machine.json이 그 뒤 바뀌지 않았다(파일 날짜 11-14 · 11-13) | 아래 절 |

- 상태 44개의 phase로 다시 세어 본 0-3 대응: ① 2 · ② 2 이상 · ③ 외곽 봉제(직선·볼록 모서리·홈 입구·홈 안 벽·홈 바닥 꺾임·V 꼭짓점·오목 안 모서리) · ④ 이음매 3 · ⑤ 배출 4. 각 단계에 상태 하나 이상 대응한다. 6-4 상태(직선, 볼록·오목 모서리, 홈 입구, 홈 바닥 꺾임, 이음매)도 모두 대응한다.
- 임시값으로 만든 준비물(있는 것으로 봄, 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다"): D-01, D-02·D-03, D-04, D-06·D-07, D-10, D-93, D-99, D-104~D-107, RX-12 매트.
- 준비물이 아니라 이번 과제 몫인 것: 운전석 매트 MAT_P · CYCLE_P(RX-17), U7 카세트 기준 연구·유닛·상태(SEAM_U7 · MAINT_U7 · U7_* · J_U7_* — RX-14가 걷으며 machine.json을 같이 고침), d₁ 45 셋업 상태(RX-16, J_U4_X 한계 0~95).

## 2. 다음 부서에 넘길 것

- FIX-045 전에는 어떤 과제도 저장하지 않는다(이 실행 지시 (f)).
- 오류 103이 있는 상태의 형상은 저장 때(11-14, 오류 0 · 경고 53 · 바디 정의 876)와 다르다(지금 바디 정의 896). FIX-045 전의 간섭 수치는 기준으로 쓰지 않는다.
- 이 세션의 MCP로는 워크스페이스 경로 `open`·`save`가 안 된다. 임시 폴더 복사본은 읽기에는 쓸 수 있으나 새 번호 저장은 `3D_Modeling/`에 해야 하므로 CLI다.
- MCP `open`은 이 파일에서 호출 시간 한도를 넘는다. 「Request timed out」 뒤 서버가 2~4분 사라졌다 돌아오고, 그동안 앱은 열기를 끝낸다. 다시 보내지 말고 `running`이 답할 때까지 기다린다.
- 큰 응답: inspect_design(요약) 55만 자, joint.list 58만, motion.list 74만, motion.play 114만 자 — 모두 파일로 떨어진다.

근거: E-03 "동작·간섭이 최우선이다", 안내서 '연결'(혼자 도는 읽기 부서는 MCP로 한 번 open, save 금지, 끝나면 동작 상태 초기화), 안내서 '동작 상태 초기화'(`motion.play {"study","step":0}`), E-08 원복, E-21(이전 결과 파일부터 읽고 남은 것만), 실행 규칙 7.

시간: 약 6분(예상 10분 안). 통로 MCP, CAD 호출 10(running 3 · version 1 · open 2 · inspect_design 3 · joint.list · motion.list · motion.play에서 open 실패 1 포함), 파일 열기 1, open_s 210 이하, 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 워크플로우 세션에 붙는 MCP 서버가 `~/.claude.json`의 `--allow-path` 설정과 다른 프로세스다(인자 없는 `solidcraft-cli mcp`, 부모가 다름). 설정을 고쳤는데도 두 실행 연속 같은 거부가 났다. 준비 점검 첫 단계에 '이 세션 서버의 허용 폴더에 프로젝트가 드는가'를 `open` 한 번으로 보는 확인이 있으면 모델링부가 헛돌지 않는다(반복 2).
- MCP `open`이 호출 한도보다 길면 서버 프로세스가 죽었다 다시 뜬다. 그동안 `running`도 답하지 않아 '앱 막힘' 절차를 쓸 수 없다(반복 2).
- joint.list · motion.list · motion.play · inspect_design에 요약 옵션이 없어 응답이 15만~114만 자다(반복).

---

# 준비 점검 — FSAP_v2.17.2 (2026-11-21, 엔진 v4.0.0, 구동 개념 v2.1 뒤 구동 라운드: RX-17 → RX-14 → … 실행 전)

요약
- 판정: **ready=false — 동작 정의·작업 대상 모형은 다 있으나, 지금 설치된 SolidCraft(0.45.0, 실행 파일 날짜 2026-11-19)로 v2.17.2를 열면 타임라인 오류 103 · 경고 323이 난다.** 저장 때(2026-11-14, mech_RX-10_model.md 11·29·70행)는 오류 0 · 경고 53 · 바디 정의 876이었다. 지금은 바디 정의 896(+20). 형상이 저장 때와 달라 간섭 판정(E-03)의 기준이 맞지 않는다. 안내서 '문서 확인' 원문 "모든 `error`·`warning`이 null이어야 한다"에 걸린다. 이 상태에서 새 번호로 저장하면 깨진 형상이 굳는다 — **사용자 결정 필요**(앱을 앞 버전으로 되돌릴지, 103개 피처를 고치는 과제를 먼저 할지).
- 오류 103의 종류: ConvertToSheetMetal 28(「not supported yet: a bend on the edge of a roll」 등 — M08 라이트 커튼 브래킷·X −2340/+1150 쪽 판), OffsetFaces 20(「the wall is too thick」), Pipe 14(관 쓸기 모서리 불리언 실패), BodyTransfer 13 · Remove 7(앞 피처가 못 만든 바디를 찾지 못함, 예 `TU0604_M08P_U7_6_B`), EdgeFlange 11 · Chamfer 4 · Fillet 4(「reference … no longer exists as it was picked」, 예 P_M04_INSERT·P_M07_BEAM), Combine 1, Thread 1. 목록 `tools/out/prep2172/timeline_errors.json`. 불러온 형상 결함 목록(defects) 445(repaired 409 · needs_repair 33 · face_left_out 2 · imported_as_surfaces 1).
- **MCP 허용 폴더 문제(둘째 막힘)**: 이 실행의 MCP 서버는 `solidcraft-cli mcp`로만 떠 있어(`--allow-path` 없음) `open {path: 3D_Modeling/FSAP_v2.17.2.sc}`가 거부됐다(「outside the folders this agent may use」, 허용: `AppData/Local/SolidCraft/recovery`와 `AppData/Local/Temp/solidcraft-mcp-21512-336b28c0`). 저장본을 허용 임시 폴더에 복사해 열었다(원본은 건드리지 않음). **모델링부는 지금 설정으로는 `3D_Modeling/`에 MCP `open`·`save`를 할 수 없다** — MCP 서버를 `--allow-path <workspace>`로 다시 띄워야 한다(사용자 몫).
- 통로: MCP(앱 pid 9028, 27878 듣는 중. 앱 명령줄에 `--control` 인자는 없으나 포트는 열려 있고 연결됨). `open`은 MCP 호출 시간 초과로 돌아왔고 그 직후 MCP 서버 프로세스(pid 21512)가 사라져 「Server unavailable」이 약 4분 이어졌다. 앱은 그동안 열기를 끝냈고(열기 300 s 이하, 정확한 초는 못 잼) 서버가 다시 붙었다. 그 사이 보험으로 띄운 CLI 실행 1개는 MCP가 돌아와 내가 끝냈다(결과 없음). 앱 재시작 0, 저장 0, 편집 0.
- 지금 앱에 열린 것: 이름 FSAP_v2.17.2, 경로 `C:/Users/hyeun/AppData/Local/Temp/solidcraft-mcp-21512-336b28c0/FSAP_v2.17.2.sc`(복사본), dirty false, 피처 3,687(억제·롤백 0), 대기 포즈.
- 조인트 587(rigid 393 · slider 185 · revolute 9), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0, 억제 0, 링크 35. machine.json joints 161 중 설계에 없는 것 1: `J_U4S_SLOT`(기록용, 앞 점검과 같음).
- 연구 11개, 단계 수 machine.json과 같음: REST 1(키 156) · CYCLE_S 450 · CYCLE_L 716 · CYCLE_G1 514 · CYCLE_G2 630 · CYCLE_V 486 · CYCLE_W1 583 · CYCLE_W2 585 · MAINT_HEAD 1 · SEAM_U7 32 · MAINT_U7 13.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false, conflicts 0, unmoved 0, values 156, positions 2,965. machine.json `rest`와 156개 모두 같음(차 0).
- machine.json: doc v2.17.2(맞음), units 21, states 44, path_parts 6, workpiece_stages 있음. 작업 대상 모형 MAT_L·S·G·V·W + 테이프 조각 TP_ 139 + SEAM 4.
- gmsh: 불러올 수 없음(ModuleNotFoundError).

## 1. 동작 정의

| 항목 | 결과 | 근거 |
|---|---|---|
| 고정부 | occurrence 0·2(U1_FRAME:1) | joint.list `fixed` |
| 끝까지 이어짐 | floating 0(앞 점검의 빈 컴포넌트 2묶음도 없어짐) | joint.list `floating` |
| 충돌·오류 | conflicts 0, errors 0 | joint.list |
| 대기 연구 | REST 1단계, step 0 재생 moved false | rest_play.json |
| 사이클 연구 | CYCLE_S·L·G1·G2·V·W1·W2 + SEAM_U7·MAINT_U7·MAINT_HEAD | motion_list.json |
| 기계 정의 | `tools/machine.json` 있음(units 21 · states 44 · path_parts 6) | 파일 |
| **문서 확인** | **타임라인 오류 103 · 경고 323**(저장 때 0 · 53) | inspect_design timeline summary |

- 조인트·연구·대기 포즈는 저장본 `document.json`(zip)에서 읽은 값과도 같다(조인트 587 · 링크 35 · 연구 11 · 단계 수). 조인트 쪽은 앱 버전 영향을 받지 않았다.
- 오류가 앱 버전 때문이라는 판단의 근거: `C:/Program Files/SolidCraft/solidcraft.exe`·`solidcraft-cli.exe` 날짜 2026-11-19(저장본은 11-14), 오류 문구가 커널의 '아직 지원 안 함'·참조 이름 풀이 실패다. 확인 못 한 것: 앞 버전 앱으로 같은 파일을 다시 열어 오류 0을 재현하지는 않았다(앞 버전 실행 파일이 없음). 저장본 원본을 CLI로 따로 열어 보는 확인도 하지 않았다(열기 13~27분, 중간에 끝냄).

## 2. 작업 대상 모형 (요구서 0-2, 6-4)

| 모형 | 크기 | 가공 뒤 형상 |
|---|---|---|
| MAT_L | 1500×1500 (D-01 최대) | TP_L 조각 + SEAM_L |
| MAT_S | 300×200 (D-01 최소) | TP_S + SEAM_S |
| MAT_G | 1200×1200 + U홈 폭 25 · 깊이 150 · 바닥 R12.5 (D-02·D-03 임시) | TP_G + SEAM_G |
| MAT_V | 1200×1200 + V홈 30° | TP_V + SEAM_V |
| MAT_W | 1500×700 + 오목 500×300 (임시, RX-12) | 없음(가공 전만 — RX-12-C3, RX-14 뒤) |

- 떨어지는 조각 없음(D-07). 6-4 '오목 모서리'는 MAT_W의 오목 안 모서리 1·2 상태로 덮인다(앞 점검의 빈 곳 풀림).
- 아직 없는 것(준비물 아님, 이번 과제): 운전석 매트 MAT_P · CYCLE_P(요구서 5절 RX-17, C-53).
- 모형용 조인트 J_WP_{L,S,G,V,W}_X·Y·ROT 15개 모두 있음.

## 3. 상태 목록 ↔ 요구서 0-3·6-4

| 0-3 단계 | 대응 상태 수 | 예 |
|---|---|---|
| ① 올리고 시작 | 2 | 대기, 큰 매트 로딩 끝 |
| ② 시작점·물림 | 3 | 큰·작은 매트 바퀴 내림, 오목 매트 시작 변 정지 |
| ③ 외곽 봉제 | 27 | 직선, 볼록 모서리, 홈 입구, 홈 안 벽, 홈 바닥 꺾임, V 꼭짓점, 오목 안 모서리 |
| ④ 이음매 | 3 | 큰·작은·홈 매트 이음매 겹침 끝 |
| ⑤ 배출 | 4 | 큰·작은·홈·오목 매트 배출 |
| 그 밖 | 5 | 정비 1, THICK_6·16, SETUP_D1_195, FLOAT_10_2 |

- 0-3 각 단계가 상태 하나 이상에 대응한다. 6-4 상태(직선·볼록·오목 모서리·홈 입구·홈 바닥 꺾임·이음매) 모두 대응.
- v2.1에서 바뀔 것(준비 부족 아님, 과제 몫): ②의 '바인더에 물림'과 ④ SEAM_U7·MAINT_U7 연구, 유닛 U7_TAPE·U7_ROLL_MOUNT·U7_TAPE_LINE, 조인트 J_U7_*는 위에서 내려오는 카세트 기준이다. RX-14가 걷으면서 machine.json units·states·studies·path_parts를 같이 고쳐야 한다. `SETUP_D1_195` 옆에 d₁ 45 셋업 상태(RX-16, J_U4_X 지금 한계 0~95)가 더해져야 한다.

## 4. 다음 부서에 넘길 것

- 사용자 결정 전에는 이 앱 버전에서 v2.17.2를 고쳐 새 번호로 저장하지 않는 것이 맞다(오류 103이 저장본에 굳는다).
- 앱에 임시 폴더 복사본이 열려 있다. 워크스페이스 경로로 `open`하면 거부된다. MCP 서버가 `--allow-path`로 다시 뜨면 같은 이름이라도 경로가 다르므로 원본 경로로 다시 `open`한다.
- 결과 파일 `tools/out/prep2172/`: joint_list.json · motion_list.json · rest_play.json · inspect.json(defects) · timeline_errors.json · body_names.json · inspect_after.json.
- MCP 응답 크기: inspect_design 15만~55만 자, joint.list 58만, motion.list 74만, motion.play 114만 자.

근거: E-03 "동작·간섭이 최우선이다", 안내서 '문서 확인' "모든 `error`·`warning`이 null이어야 한다", E-08 원복(읽기 부서는 동작 상태 초기화만), 실행 규칙 2 "혼자 도는 읽기 부서도 MCP로 잰다", 실행 규칙 7 "ready=false·done=false는 준비물을 아예 만들 수 없을 때만"(이번 것은 임시값 문제가 아니라 앱 버전이 저장본을 다르게 다시 계산하는 문제라 이 규칙의 '있는 것으로 본다'에 들지 않는다고 판단), CLAUDE.md "승인 뒤 재확인하지 않는다. 예외: 구조를 바꾸는 판단 … 문서에 없는 결정".

시간: 약 9분(예상 10분 안). 통로 MCP, 파일 열기 2(MCP 1 + 끝낸 CLI 1), open_s 300 이하, 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 앱·CLI가 실행 사이에 새 버전(0.45.0)으로 바뀌었는데 워크플로우에 '앱 버전이 저장 때와 같은가'를 보는 단계가 없다. 준비 점검이 타임라인 오류 수를 저장 때 기록과 견줘 우연히 잡았다. 저장할 때 앱 버전을 machine.json이나 원장에 적고 준비 점검이 견주면 바로 잡힌다.
- MCP 서버가 `--allow-path` 없이 뜨면 프로젝트 폴더의 저장본을 못 연다. 준비 점검 첫 단계에 '허용 폴더에 프로젝트가 들어 있는가' 확인이 있으면 좋다.
- MCP `open`이 호출 시간 한도보다 오래 걸리면 서버 프로세스가 사라졌다가 몇 분 뒤 다시 붙는다. 그동안 `running`·`pending`도 「Server unavailable」이라 '앱 막힘' 절차(먼저 `running`)를 쓸 수 없었다.
- 큰 응답(반복): joint.list·motion.list·motion.play·inspect_design에 요약 옵션이 없다.

---

# 준비 점검 — FSAP_v2.13.0 (2026-11-13, 엔진 v4.0.0, 구동 라운드 이어서: RX-07 검증·RX-11·RX-12·RX-06R 실행 전)

요약
- 판정: **ready=true**, 빠진 것 0. 대상 `3D_Modeling/FSAP_v2.13.0.sc`(tools/config.json doc, 5,705,083 B, 2026-11-12 23:06).
- 통로: **MCP**. 앱 켜짐(solidcraft.exe pid 38080, --control 27878), `running` 빈 목록(막힘 없음, 앱 재시작 0). 앱에 이미 v2.13.0이 열려 있고 `dirty` false(path·name 일치)라 다시 `open` 하지 않았다(같은 경로 open은 디스크를 다시 읽지 않는다 — 안내서 '원복'). 파일 열기 0, 저장 0, 편집 0. CAD 호출 7(running 1·inspect_design 2·joint.list·motion.list·motion.play·measure names_only). 결과 `tools/out/prep2130/`(joint_list.json, motion_list.json, rest_play.json, body_names.json).
- 문서: 피처 3,742, 타임라인 error 0, 억제·롤백 0. warning 61(Boolean retry 47, 떨어진 조각 6, 모서리 다시 집음 5, import 면 없음 3 — 모두 앞 버전부터 있던 종류, 이번 점검은 판정하지 않음). 바디 3,195(occurrence 포함), occurrence 2,944.
- 조인트 604(rigid 412·slider 183·revolute 9), 고정부 2(occurrence 0·2), conflicts 0, errors 0, 억제 0, 링크 36. **floating 2묶음 — 둘 다 바디 0인 빈 컴포넌트**(U4_CYL:1+U4_CYL_CLEVIS:1, U4_ROD:1+U4_ROD_NUT:1+I-020B_M02:1, M02R 잔재, v2.10.3부터). `measure names_only`로 이 다섯 occurrence 아래 바디 0을 다시 확인했다. 바디가 있는 부품의 floating은 0.
- machine.json joints 159 중 설계에 없는 것 1: `J_U4S_SLOT`(pin_slot, 설계 의도 기록용 — M02R 3회차에서 닫힌 고리 풀이가 앱을 멈춰 CAD에는 맺지 않고 링크 J_U4_PRESS → J_U4S_ROD −1.4535 mm/°로 대신함, mech_M02R_model.md 63·65행). 나머지 158 모두 있음.
- 연구 9개, 단계 수 machine.json과 같음: REST 1(키 153)·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·CYCLE_V 486·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false(이미 대기 포즈), conflicts 0, unmoved 0, values 153, positions 2,944. machine.json `rest` 값과 비교 153개 모두 같음(차 0). 끝난 뒤 `dirty` false, 피처 3,742 그대로(E-08 원복할 것 없음).
- machine.json: units 20, states 32(요구서 0-3 ①~⑤ 모두 대응), path_parts 6, workpiece_stages(가공 전·후 + sim_tape), temp_values 11. 작업 대상 모형 MAT_L·S·G·V + 테이프 조각 139 + SEAM 4.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음): ① machine.json `doc` 칸이 아직 v2.12.2(RX-07은 조인트·행정 변경 0이라 내용은 맞음, 칸만 어긋남). ② 빈 컴포넌트 floating 2묶음(디테일). ③ 6-4 계단형 오목 모서리 매트 모형 없음. ④ RX-12 시험 매트(긴 매트 + 넓은 오목)는 이번 과제로 만든다.

## 1. 동작 정의

| 항목 | 결과 | 근거 |
|---|---|---|
| 고정부 | occurrence 0·2 고정 | joint.list `fixed` |
| 조인트 끝까지 이어짐 | 바디 있는 부품 floating 0. 빈 컴포넌트 2묶음만 floating | joint.list `floating`, body_names.json |
| 충돌·오류 | conflicts 0, errors 0, suppressed 0 | joint.list |
| 대기 연구 | REST 1단계, 키 153, step 0 재생 moved false | motion.list, rest_play.json |
| 사이클 연구 | CYCLE_S·L·G1·G2·V(구동 키 36·72·64·64·64) + SEAM_U7·MAINT_U7·MAINT_HEAD | motion.list |
| 기계 정의 | `tools/machine.json` 있음(cad solidcraft, units 20·states 32·path_parts 6) | 파일 |

- 빈 컴포넌트 floating은 앞 검도가 디테일로 판정한 것을 그대로 따른다(mech_RX-08_verify1.md 56·74행 "바디가 없어 움직임·간섭에는 영향 없음", verify2 47행). 바디가 0이라 동작 검사(E-03)의 대상·결과에 들어가지 않는다. 지우기는 디테일링 몫이고(실행 규칙 13 순서), 이번 점검은 건드리지 않았다.
- v2.12.2 → v2.13.0에서 바뀐 것(mech_RX-07_model.md 8·45행, 이번에 v2.12.2를 열어 비교하지는 않음): 리지드 그룹 7개 추가(RX-07 새 occurrence 7개를 U8_PNEU에 묶음), 조인트·행정 변경 0. 연구 단계 수는 machine.json(v2.12.2 기준)과 같다.
- machine.json에 있고 REST 재생 값에 안 나오는 조인트 6: J_U4_DISK·J_U7_HGT·J_U4S_ROD·J_U4_X·J_U4_XSCREW(따라감·셋업 축, REST 키 없음)와 J_U4S_SLOT(기록용). REST 키가 있는 153개는 모두 rest 값과 같다.

## 2. 작업 대상 모형 (요구서 0-2, 6-4)

| 모형 | 크기 | 가공 뒤 형상 | 근거 |
|---|---|---|---|
| MAT_L (WP_L) | 1500×1500 (D-01 최대) | TP_L 조각 48바디 + SEAM_L | 자료대기 D-01, machine.json units |
| MAT_S (WP_S) | 300×200 (D-01 최소) | TP_S 11 + SEAM_S | 같음 |
| MAT_G (WP_G) | 1200×1200 + U홈 폭 25·깊이 150·바닥 R12.5 (D-02·D-03 임시) | TP_G 40 + SEAM_G | 같음 |
| MAT_V (WP_V) | 1200×1200 + V홈 30°·꼭짓점 R2 | TP_V 40 + SEAM_V | VGR-01 |

- 떨어지는 조각 없음(machine.json workpiece_stages.fragments, D-07) — 절단은 바인더 앞 한 번, 끝은 접어 넣음.
- 모두 D-번호 임시값으로 만든 것이라 있는 것으로 본다(실행 규칙 7, WF-113).
- 없는 것: 6-4 '오목 모서리'(계단형 날카로운 오목) 모형 — 홈 바닥 오목 반원으로 대신(앞 점검과 같음). 요구서 5절 RX-12(C-47, 긴 매트 + 넓은 오목, 매트가 바늘 +X로 넘어가는 경우)가 이번 실행 과제로 이 빈 곳을 다룬다. 준비물이 아니라 과제다.

## 3. 상태 목록 ↔ 요구서 0-3·6-4

| 0-3 단계 | 대응 상태 수 | 예 |
|---|---|---|
| ① 올리고 시작 | 2 | 대기, 큰 매트 로딩 끝 |
| ② 시작점·물림 | 2 | 바늘 옆 바퀴 내림, 먼 쪽 바퀴 내림 |
| ③ 외곽 봉제 | 17 | 직선, 볼록 모서리, 홈 입구, 홈 안 벽, 홈 바닥 꺾임, V 꼭짓점 |
| ④ 이음매 | 3 | 큰·작은·홈 매트 이음매 겹침 끝 |
| ⑤ 배출 | 3 | 큰·작은·홈 매트 배출(각 연구 마지막 단계) |
| 그 밖 | 5 | 정비 1, THICK_6·16, SETUP_D1_195, FLOAT_10_2 |

- 6-4 상태(직선, 볼록 모서리, 오목 모서리, 홈 입구, 홈 바닥 꺾임, 시작·끝 이음매) 가운데 '오목 모서리'만 홈 바닥 오목으로 대신한다(2절).
- 상태가 가리키는 연구 이름은 모두 설계에 있다.

## 4. 다음 부서에 넘길 것

- machine.json `doc` 칸을 v2.13.0으로 맞추는 일은 다음에 machine.json을 고치는 모델링부가 함께 한다(준비 점검은 읽기만 했다).
- RX-06R(C-46, U4 X축 볼나사·손잡이 빼기): 걸리는 조인트는 J_U4_X(직동 0~95, 연구 키 없음)·J_U4_XSCREW(회전, 링크 J_U4_X → J_U4_XSCREW 18°/mm). 볼나사를 빼면 J_U4_XSCREW와 그 링크, machine.json joints·units·_history를 같이 고친다.
- MCP 응답이 큰 명령: inspect_design 약 132만 자, joint.list 56만 자, motion.list 52만 자, motion.play 113만 자, measure names_only 36만 자 — 모두 파일로 떨어지므로 파이썬으로 요약해 읽는다. 이번 결과는 `tools/out/prep2130/`에 있으니 측정부는 다시 부르지 않아도 된다.

근거: E-03 "동작·간섭이 최우선이다", E-08 원복(읽기 부서는 동작 상태 초기화만), E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", 실행 규칙 2 "혼자 도는 읽기 부서도 MCP로 잰다", 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 요구서 0-2·0-3·6-4.

시간: 약 4분(예상 10분 안). 통로 MCP, CAD 호출 7, 파일 열기 0, open_s 0(열지 않음), 브라우저 0, 앱 재시작 0.

## 워크플로우 메모
- 준비 점검 기준 "joint.list에 floating 없음"은 바디 0인 빈 컴포넌트도 걸린다. '바디가 있는 occurrence의 floating'으로 좁히거나, 빈 컴포넌트를 따로 세는 칸이 있으면 판정이 갈리지 않는다(이번에는 `measure names_only`로 바디 0을 따로 확인).
- 앱에 대상 저장본이 이미 열려 있고 dirty false면 `open`을 건너뛰어도 되는지 안내서 '연결' 표에 적혀 있지 않다(이번에는 건너뜀 — 같은 경로 open이 디스크를 다시 읽지 않으므로 결과가 같다).
- 큰 응답(반복): joint.list·motion.list·motion.play·inspect_design에 요약만 돌려주는 옵션이 없어 호출마다 50만~130만 자가 파일로 떨어진다.

---

# 준비 점검 — FSAP_v2.10.2 (2026-11-12, 3차 이어서 다시 부름: M02R 다시 C-41)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.10.2.sc`(tools/config.json doc, machine.json doc도 같음). 앞 점검(11-11 22:14)과 결과가 모두 같다.
- 통로: **MCP**. 앱 켜짐(solidcraft.exe pid 28440, 포트 27878), `running` 빈 목록(막힘 없음, 앱 재시작 0). 지시문 (a)대로 앱에 남은 상태는 따지지 않고 `open` 1회로 v2.10.2를 다시 열었다(features 3453, errors 0). 저장 0, 편집 0. 결과 `tools/out/prep2102b/`(joint_list.json, motion_list.json, rest_play.json).
- 조인트 544(rigid 353·slider 181·revolute 10), **floating 0**, conflicts 0, errors 0. machine.json joints 157 모두 설계에 있음(빠짐 0). U4: J_U4_PRESS·WHEEL_ROT·DISK + 걷어 낼 M02R 따라감 3개(J_U4_CYL_PIN·CYL_ROD·ROD_PIN).
- 연구 9개: REST 1·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·CYCLE_V 486·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13(machine.json과 같음).
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false(이미 대기 포즈), conflicts 0, unmoved 0, values 152, positions 2877. 원복할 편집 없음(E-08).
- machine.json: units 16, states 30(요구서 0-3 ①~⑤ 대응, 앞 점검과 같음), path_parts 6. 작업 대상 모형 WP_L·WP_S·WP_G·WP_V(0-2 양 끝, 가공 뒤 형상) + SIM-01 테이프 조각. 떨어지는 조각 없음(D-07).
- gmsh: 불러올 수 없음(ModuleNotFoundError).
- 미완(막지 않음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

M02R에 넘길 것은 아래 앞 점검 절과 같다(조인트 3개 삭제 시 machine.json joints·_history 같이 고침, J_U4_PRESS 축·범위가 바뀌면 9개 연구 키 다시 맞춤).

근거: E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", E-08 원복.

## 워크플로우 메모
- 사용자 말 "이거 안보이냐고;;"로 같은 준비 점검이 다시 불렸다. 저장본이 바뀌지 않았으면(같은 doc, 같은 mtime) 앞 점검 결과를 그대로 넘기는 지름길이 있으면 좋다.

---

# 준비 점검 — FSAP_v2.10.2 (2026-11-11 3차, 엔진 v3.9.3, 재부팅·사용자 정정 뒤 재실행: M02R 다시)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.10.2.sc`(tools/config.json doc, 커밋 5bfc23e). machine.json `doc`도 v2.10.2(앞 점검 메모의 doc 칸 어긋남 풀림).
- 통로: **MCP**. 앱 켜짐(solidcraft.exe pid 28440, 포트 27878 LISTENING), `running` 빈 목록(막힘 없음, 앱 재시작 0). 지시문 (a)대로 앱에 남은 상태는 따지지 않고 `open` 1회로 v2.10.2를 다시 열었다(features 3453, errors 0). 그 뒤 `joint.list`·`motion.list`·`motion.play REST step 0`. 저장 0, 편집 0. 결과 `tools/out/prep2102/`(joint_list.json, motion_list.json, rest_play.json).
- 조인트 544(rigid 353·slider 181·revolute 10), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0. machine.json joints 157 모두 설계에 있음(빠짐 0). U4 조인트: J_U4_PRESS·WHEEL_ROT·DISK + M02R(v2.10.2) 따라감 3개 J_U4_CYL_PIN·CYL_ROD·ROD_PIN(키 없음, M-07 닫힌 고리).
- 연구 9개, 단계 수 machine.json과 같음: REST 1(키 152)·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·CYCLE_V 486·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13. 모든 연구에 J_U4_PRESS·J_U4_WHEEL_ROT·J_U3_PRESSER 키 있음.
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → **moved true**(열린 직후 포즈가 대기와 달랐다 — 저장본 포즈가 REST와 어긋났거나 open이 앞 세션 포즈를 남겼다), conflicts 0, unmoved 0, values 152, positions 2877. 지금 대기 포즈. 원복할 편집 없음(E-08).
- 기계 정의 `tools/machine.json`: units 16, states 30, path_parts 6, workpiece_stages 3(가공 전·후 + sim_tape), temp_values 11. 상태 30이 요구서 0-3 ①~⑤에 대응(앞 점검과 같음).
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G U홈·WP_V V홈 30°(요구서 0-2 양 끝, 가공 뒤 형상) + SIM-01 붙은 테이프 조각(J_TP_*). 떨어지는 조각 없음(D-07).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

## M02R 다시(C-41)에 넘길 것
- 걷어 낼 조인트 3개(J_U4_CYL_PIN·J_U4_CYL_ROD·J_U4_ROD_PIN)는 설계·machine.json 양쪽에 있다. 모델링부가 지울 때 machine.json joints·_history도 같이 고쳐야 한다(연구 키에는 없음 — 따라감 조인트라 연구 수정 불필요).
- J_U4_PRESS는 machine.json에서 rotate, axis [0,-1,0], origin [-300,0,70], rest 8.626, min -1.867 / max 8.626. 스윙 브래킷 그네 방식으로 바꾸면 축·범위가 바뀔 수 있으니 9개 연구의 J_U4_PRESS 키를 다시 맞춰야 한다.

근거: 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 실행 규칙 2 "혼자 도는 읽기 부서도 MCP로 잰다", E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", E-08 원복.

## 워크플로우 메모
- 이 실행을 부른 사용자 말은 "이거 안보이냐고;;"(무엇을 가리키는지 지시문에 없음). 준비 점검은 그 답을 정하지 않는다 — 앞 실행의 사용자 정정(C-41, M02R 실린더 위치)을 가리키는 것으로 보이며, 최종 보고 담당이 확인할 몫.
- `joint.list`(52만 자)·`motion.list`(52만 자)·`motion.play`(110만 자) 결과가 MCP 응답 상한을 넘어 파일로 떨어졌다. 요약만 돌려주는 옵션이 있으면 준비 점검이 가벼워진다(앞 점검 메모와 같은 문제, 반복).

---

# 준비 점검 — FSAP_v2.10.1 (2026-11-11, 엔진 v3.9.3, SIM-01 수정 1회차 뒤 재실행)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.10.1.sc`(tools/config.json doc, 11-11 13:01 저장, 깃 밖 새 파일). 지시문 (a)의 "v2.8.12"보다 config가 최신이라 config를 따랐다. v2.10.1 = SIM-01 수정 1회차(machine.json `_history` 끝 줄: "J_TP_L_16B·26B 더함, 조각 컴포넌트 부모 WP_TAPE_<M>, L 자름 고침"). CHANGELOG에는 아직 v2.10.1 줄이 없다(v2.10.0까지).
- 통로: **MCP**. 앱 켜짐(solidcraft.exe, 포트 27878 LISTENING), `running` 빈 목록. `open` 1회(FSAP_v2.10.1, features 3368, errors 0) → `joint.list`·`motion.list` → `motion.play REST step 0`. 저장 0, 편집 0. 결과 `tools/out/prep2101/`(joint_list.json, motion_list.json, rest_play.json).
- 조인트 537(rigid 346·slider 181·revolute 10), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0. 움직이는 조인트 191 = machine.json joints 157(설계에서 빠짐 0, SIM-01 J_TP_* 포함) + 체인 링크 34(`J_U5_CHN_*`, links 모두 a = J_U5_X(id 48)).
- 연구 9개, 단계 수 machine.json과 같음: REST 1(대기 포즈 step 0, 키 152)·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·CYCLE_V 486·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13.
- C-39 반영 그대로: 사이클 5개·SEAM_U7의 J_U3_PRESSER 값 {0, 20}(0 = 봉제·회전 중 낮은 누름), REST·MAINT 20.
- 기계 정의 `tools/machine.json`: units 16(U6_PRESS·U7_TAPE_LINE 더함), states 30, path_parts 6, workpiece_stages(가공 전·후 + sim_tape, 조각 없음 D-07), baseline_overlaps 23, temp_values 11. `doc` 칸은 v2.10.0을 가리킨다(조인트·연구 같은 구조, 막지 않음 — 모델링부가 다음 저장 때 고치면 됨).
- 상태 30이 요구서 0-3 ①~⑤에 대응(앞 점검과 같음): ① 대기·로딩 끝, ② 바퀴 내림(L·S), ③ 직선·볼록 45°/90°·홈 입구·안 벽·홈 바닥(오목)·두 번째 홈·V 입구1·꼭짓점·입구2, ④ 이음매 겹침 끝(L·S·G)·SEAM_U7, ⑤ 배출(L·S·G). 정비 1, 두께 THICK_6·THICK_16(6-4).
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G U홈·WP_V V홈 30°(MAT·TAPE·SEAM, 요구서 0-2 양 끝, 가공 뒤 형상) + SIM-01 붙은 테이프 조각(J_TP_*, 땀 진행 키). 떨어지는 조각 없음(D-07).
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false(이미 대기 포즈), conflicts 0, unmoved 0, values 152. 원복할 편집 없음(E-08).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 실행 규칙 2 "혼자 도는 읽기 부서도 MCP로 잰다", E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", E-08 원복.

## 워크플로우 메모
- 지시문 (a)가 계속 v2.8.12를 가리킨다. 실제 최신은 config doc v2.10.1(그 사이 DC-04·U6S·SIM-01이 저장됨). 지시문 대신 config doc을 기준으로 했다.
- 이 실행을 부른 사용자 말은 질문("그럼 step lite를 진행하는게 의미가 없다는거야?")이다. 준비 점검은 그 답을 정하지 않는다 — 최종 보고 담당이 답할 몫으로 남긴다.
- `motion.play` 결과가 1.1 MB(positions 2866)로 커졌다(SIM-01 조각 122개). 요약만 돌려주는 옵션이 있으면 준비 점검이 가벼워진다.

---

# 준비 점검 — FSAP_v2.8.13 (2026-11-11, 엔진 v3.9.3, 사용자 "엔진 바꿨어" 뒤 재실행: MOT-01·FUNC-01·PNEU-01·STEPWAIT 남음)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.8.13.sc`(tools/config.json doc, 11-11 01:03 저장, DC-04). 지시문 (a)의 "v2.8.12"보다 config가 최신이라 config를 따랐다. v2.8.13은 연구 키(J_U3_PRESSER)만 바뀌었다(CHANGELOG "형상·조인트·구매품 변화 없음").
- 통로: **MCP**. 앱 켜짐(solidcraft.exe, 포트 27878 열림), `running` 빈 목록. `open` 1회(FSAP_v2.8.13, features 3033, errors 0) → `joint.list`·`motion.list` → `motion.play REST step 0`. 저장 0, 편집 0. 결과 `tools/out/prep2813/`(joint_list.json, motion_list.json).
- 조인트 410(rigid 344·slider 56·revolute 10), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0. 움직이는 조인트 66 = machine.json joints 32(설계에서 빠짐 0) + 체인 링크 34(`J_U5_CHN_*`, links 34 모두 a = J_U5_X(id 48)). v2.8.12와 같다.
- 연구 9개, 단계 수 machine.json과 같음: REST 1(대기 포즈 step 0)·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·CYCLE_V 486·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13, 연구마다 키 27개.
- C-39 반영 확인: 사이클 연구 5개와 SEAM_U7의 J_U3_PRESSER 값이 {0, 20}(0 = 봉제·회전 중 낮은 누름, 20 = 로딩·배출 들림). REST·MAINT는 20. 요구서 0-3 ③ "노루발 낮은 누름으로 회전"에 대응.
- 기계 정의 `tools/machine.json`: doc v2.8.13(지난 점검 메모의 doc 칸 문제 풀림), units 14, states 30, path_parts 6, workpiece_stages 2(가공 전·후, 조각 없음 D-07), temp_values 11.
- 상태 30이 요구서 0-3 ①~⑤에 대응(v2.8.12 점검과 같음): ① 대기·로딩 끝, ② 바퀴 내림(L·S), ③ 직선·볼록 45°/90°·홈 입구·안 벽·홈 바닥(오목)·두 번째 홈·V 입구1·꼭짓점·입구2, ④ 이음매 겹침 끝(L·S·G)·SEAM_U7, ⑤ 배출(L·S·G). 정비 1, 두께 THICK_6·THICK_16(6-4).
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G U홈·WP_V V홈 30°(MAT·TAPE·SEAM, 요구서 0-2 양 끝, 가공 뒤 형상), 조인트 J_WP_L/S/G/V_X·Y·ROT 12개 joint.list에 있음. 떨어지는 조각 없음(D-07).
- 동작 상태 초기화: `motion.play {study:"REST", step:0}` → moved false(이미 대기 포즈), conflicts 0, unmoved 0, values 27. 원복할 편집 없음(E-08).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 실행 규칙 2 "혼자 도는 읽기 부서도 MCP로 잰다", E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", E-08 원복.

## 워크플로우 메모
- `joint.list`·`motion.list`·`motion.play` 결과가 각각 0.4~1 MB라 MCP 응답이 파일로 넘어간다. 요약만 돌려주는 옵션이 있으면 준비 점검이 가벼워진다.
- 지시문 (a)가 v2.8.12를 가리켰으나 이미 v2.8.13이 저장돼 있었다(DC-04가 앞 실행에서 끝남). 지시문 대신 config doc을 기준으로 했다.

---

# 준비 점검 — FSAP_v2.8.12 (2026-11-10 2차, 엔진 v3.9.3, C-38·C-39 결정 뒤 DC-03 닫기·DC-04·MOT-01·FUNC-01·PNEU-01·STEPWAIT 실행 전)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.8.12.sc`(tools/config.json doc, 11-10 19:13 저장). v2.8.9 뒤 v2.8.10 LITE(형상 변경 0)·v2.8.11·12 PNEU-01R(구멍 지름만)·DC-02(시간 키) — 조인트·연구 구조 변화가 없을 것으로 보였으나 저장본에 대고 다시 쟀다.
- 통로: **CLI**. SolidCraft 앱이 꺼져 있었다(`running` 빈 목록 + "app was not found, headless session", 포트 27878 닫힘, 프로세스는 solidcraft-cli 2개뿐 — 건드리지 않음). 실행 규칙 2 "앱이 꺼져 있거나 MCP 호출이 실제로 실패할 때만 CLI로 하고 이유를 보고서에 적는다". `joint.list`·`motion.list`를 스크립트 하나로 묶어 `solidcraft-cli run --results` 1회(열기 포함 450 s, 저장 없음). 결과 `tools/out/prep2812/results.json`.
- 조인트 410(rigid 344·slider 56·revolute 10), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0. 움직이는 조인트 66 = machine.json joints 32(빠짐 0) + 체인 링크 34(`J_U5_CHN_*`, links 34 모두 a = J_U5_X(id 48)로 따라 움직임). v2.8.9와 같다.
- 연구 9개, 단계 수 machine.json과 같음: REST 1(대기 포즈 step 0)·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·CYCLE_V 486·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13. 연구마다 키 27개.
- 기계 정의 `tools/machine.json`: units 14, states 30, path_parts 6, workpiece_stages(가공 전·후, 조각 없음 D-07). `doc` 칸이 아직 v2.8.9를 가리킨다(조인트·연구 같음, 막지 않음 — 모델링부가 다음 저장 때 고치면 됨).
- 상태 30이 요구서 0-3 ①~⑤에 대응(v2.8.9 점검과 같음): ① 대기·로딩 끝, ② 바퀴 내림(L·S), ③ 직선·볼록 45°/90°·홈 입구·안 벽·홈 바닥(오목)·두 번째 홈·V 입구1·꼭짓점·입구2, ④ 이음매 겹침 끝(L·S·G)·SEAM_U7, ⑤ 배출(L·S·G). 정비 1, 두께 THICK_6·THICK_16(6-4).
- 요구서 0-3 ③이 C-39로 "노루발을 낮은 누름으로 두고 회전"으로 바뀌었다. 지금 연구는 피벗 구간에서 J_U3_PRESSER 20(들림)이다(예: CYCLE_G1 88~178·210~390·422~512단계). 이 키 고침은 이번 실행 DC-04 모델링 몫(지시 (b) "연구 키(노루발 들기 값) 고침")이라 준비 부족으로 보지 않는다. 대응하는 상태(홈 입구·꼭짓점 회전)는 있다.
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G 좁은 U홈·WP_V V홈 30°(MAT·TAPE·SEAM, 요구서 0-2 양 끝, 가공 뒤 형상) — 조인트 J_WP_L/S/G/V_* 모두 joint.list에 있음. v2.8.10~12는 이 바디를 바꾸지 않았다(CHANGELOG). 떨어지는 조각 없음(D-07).
- 동작 상태 초기화: CLI로만 읽어 앱 포즈를 바꾸지 않았으므로 할 것 없음(안내서 '원복' "읽기 부서가 CLI로만 쟀다면 원복할 것이 없다"). 저장 0, 편집 0.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 실행 규칙 2(앱 꺼짐 → CLI), E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", E-08 원복.

## 워크플로우 메모
- 앱이 꺼진 채 워크플로우가 시작됐다. 준비 점검은 CLI 1회(450 s)로 끝났지만, 뒤의 모델링부는 실행 규칙 2상 MCP(앱)로 그려야 하므로 앱을 켜야 한다. 앱 켜짐 확인을 워크플로우 맨 앞에 두는 것이 좋다.
- machine.json `doc` 칸이 형상만 바뀐 버전(LITE·PNEU-01R)에서 갱신되지 않아 v2.8.9로 남았다.

---

# 준비 점검 — FSAP_v2.8.9 (2026-11-10 오후, 엔진 v3.9.3, 사용자 "잘 도는데 긴것도 혼자" 실행 전)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.8.9.sc`(tools/config.json doc, 11-10 09:57 저장). 지시문의 "v2.8.3"보다 config가 최신이라 config를 따랐다. v2.8.3 뒤 VGR-01(WP_V·CYCLE_V)·PNEU-01(관·체인 23링크)·DC-01(시간 키)로 조인트·연구가 바뀌어 다시 쟀다.
- 앱: `running` 빈 목록. 앱에 이미 v2.8.9가 열려 있었다(이름 FSAP_v2.8.9, path 같음, **dirty false**). 그래서 다시 열지 않았다(open 0, 원복 주의 — 같은 경로 open은 다시 읽지 않음). 저장 0, 편집 0. 결과 `tools/out/prep289/`(joints_studies.txt, joint_list_after.txt).
- 조인트 410(rigid 344·slider 56·revolute 10), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0.
- 움직이는 조인트 66 = machine.json joints 32 + 체인 링크 조인트 34(`J_U5_CHN_U01~U17·L02~L17·B`). 34개 모두 `links`로 J_U5_X에 묶여 따라 움직인다(links 34, a = J_U5_X). 독립 자유도가 아니라 machine.json에 없어도 빠진 것이 아니다.
- 연구 9개: REST(1단계, 대기 포즈 step 0), CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·CYCLE_V 486, MAINT_HEAD 1, SEAM_U7 32, MAINT_U7 13. machine.json studies 9와 단계 수까지 같다.
- 기계 정의 `tools/machine.json`: doc v2.8.9, units 14(WP_V 포함), states 30, path_parts 6, workpiece_stages(가공 전·후, 조각 없음 D-07).
- 상태 30이 요구서 0-3 ①~⑤에 대응: ① 대기·로딩 끝, ② 바퀴 내림(L·S), ③ 직선·볼록 45°/90°·홈 입구·안 벽·홈 바닥(오목)·두 번째 홈·V 입구1·꼭짓점·입구2, ④ 이음매 겹침 끝(L·S·G)·SEAM_U7, ⑤ 배출(L·S·G). 정비 1, 두께 THICK_6·THICK_16(6-4). 요구서 11-10 변경은 5절 행(PNEU-01·VGR-01·DC-01~03·PNEU-01R)뿐, 0-2·0-3·6-4 바뀜 없음.
- 작업 대상 모형: MAT·TAPE·SEAM의 L(1500×1500)·S(300×200)·G(U홈)·V(V홈 30°) 12바디 있음(요구서 0-2 양 끝, 가공 뒤 형상). 떨어지는 조각 없음(D-07).
- 동작 상태 초기화: 연구 8개 step 0 재생 + 마지막 `REST` step 0 배치를 보냈으나 앱이 응답 전에 연결이 끊겼고(os error 10060) 배치는 약 1,250 s 뒤 끝났다. 단계별 conflicts 결과는 받지 못했다. 끝난 뒤 `joint.list`로 확인: 모든 조인트가 machine.json '대기' 상태 값과 같다(차이 0), floating·conflicts 0. → 대기 포즈로 원복됨.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신). "긴것도 혼자"(DC-03)용 CYCLE_L U4 혼자 구간은 아직 연구에 없다 — 이번 실행의 모델링 몫이라 준비 부족으로 보지 않음.

근거: 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 실행 규칙 2 "혼자 도는 읽기 부서도 MCP로 잰다", 실행 규칙 2 "같은 경로를 다시 `open`해도 디스크에서 다시 읽지 않는다", E-08 원복.

## 워크플로우 메모
- v2.8.9에서 `motion.play` step 0 아홉 개 배치가 약 1,250 s 걸렸다(v2.8.3에서는 수 초). 회귀 20의 "한 점 470 s 넘음"과 같은 무게 증가다. 준비 점검은 연구 존재·step 0 원복만 보면 되므로 다음부터는 `motion.play REST step 0` 하나만 부르고, 연구별 step 0 재생은 빼는 것이 좋다.
- 배치가 오래 걸리면 MCP 연결이 10060으로 끊기고 결과가 사라진다. `running`으로 끝남을 확인하고 `joint.list` 값으로 포즈를 판정했다.

---

# 준비 점검 — FSAP_v2.8.3 (2026-11-10, 엔진 v3.9.3, VGR-01 이어서·PNEU-01·MOT-01·FUNC-01 실행 전)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.8.3.sc`(tools/config.json doc, 11-09 22:06 저장, F01-C1: 작업 대상 모형 원점 +6.5 X·연구 피벗 키 변경). 형상·조인트 원점이 바뀌어 v2.8.2 결과를 쓰지 않고 MCP로 다시 쟀다.
- 앱: `running` 빈 목록 → MCP `open` 1회(오류 0, 피처 2303). 저장 0. 결과 파일 `tools/out/prep283/`(motion_list.txt, joints_studies.txt).
- 조인트 372(rigid 343·slider 20·revolute 9), 고정부 2(occurrence 0·2), **floating 0**, conflicts 0, errors 0. 움직이는 조인트 29 = `tools/machine.json` joints 29(양쪽 차이 0). machine.json doc = v2.8.3, units 13, states 26, path_parts 6.
- 연구 8개: REST(1단계, 대기 포즈 step 0), CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630, MAINT_HEAD 1, SEAM_U7 32, MAINT_U7 13. 모두 step 0 conflicts 0, unmoved 0. machine.json studies 8과 같다.
- 상태 26이 요구서 0-3 ①~⑤에 대응: ① 대기·로딩 끝, ② 바퀴 내림(L·S), ③ 직선·볼록 45°/90°·홈 입구·안 벽·홈 바닥(오목)·두 번째 홈, ④ 이음매 겹침 끝(L·S·G)·SEAM_U7, ⑤ 배출(L·S·G). 정비 1, 두께 THICK_6·THICK_16(6-4). 요구서 11-10 00:29 변경은 5절 PNEU-01 행 고침·DC-01(VGR) 행 추가뿐(0-2·0-3·6-4 바뀜 없음).
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G 좁은 U홈(요구서 0-2 양 끝, 조인트 J_WP_L/S/G_X·Y·ROT 확인), 떨어지는 조각 없음(D-07).
- 동작 상태 초기화: 끝에 `motion.play REST step 0`(conflicts 0, moved false). edit.checkpoint 12는 배치 안에서 만들어져 복원이 거부됐으나 편집은 하지 않았고 포즈만 바꿨다가 REST로 되돌렸다.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신), V홈 시험 매트는 VGR-01 몫.

근거: 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 실행 규칙 2 "혼자 도는 읽기 부서도 MCP로 잰다", E-08 원복.

## 워크플로우 메모
- `edit.checkpoint`를 `batch` 안 단계로 두면 그 뒤 따로 부른 `edit.restore_checkpoint`가 "no checkpoint"로 거부됐다. 포즈만 바꾸는 읽기 부서는 REST step 0 재생으로 원복하는 것으로 충분했다.
- `joint.list`·`motion.list` 결과가 39만~70만 자라 MCP 응답 한도를 넘어 파일로 떨어졌다. 그 파일을 tools/out에 복사해 파이썬으로 요약했다.

---

# 준비 점검 — FSAP_v2.8.2 스케치 숨김 재저장 뒤 (2026-11-09 밤, 엔진 v3.9.3, VGR-01·F01-C1 실행 전)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.8.2.sc`(tools/config.json doc, 21:28 재저장 — 사용자 "스케치 쓸데없이 왜켜놔 숨겨", 실행 규칙 19).
- 바뀐 것 확인(설계 파일은 열지 않음): 커밋본(HEAD)과 재저장본의 zip 내용을 비교. `container.json`·`blobs/` 같음, `document.json` 차이는 `visibility/hidden_sketches` 0 → 208 하나뿐. 수치 차이 최대 1.7e-13 mm(저장 반올림), 조인트 372·occurrence 2563 같음 → 형상·조인트·연구 변화 0.
- 그래서 12:40 MCP 점검 결과 `tools/out/prep282/`를 그대로 씀(E-21 원문 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"): 조인트 372, 고정부 2, floating 0, 움직이는 조인트 29 = machine.json(11:31, 바뀜 없음). 연구 8개(REST 대기 포즈 step 0, CYCLE_S·L·G1·G2, MAINT_HEAD, SEAM_U7, MAINT_U7) step 0 conflicts 0. states 26이 0-3 각 단계와 THICK_6·THICK_16에 대응.
- 요구서 21:28 변경: 5절 VGR-01 행 하나 추가(0-2·0-3·6-4 바뀜 없음) → 대응 판정 그대로.
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G 좁은 U홈(요구서 0-2 양 끝), 떨어지는 조각 없음(D-07). V홈 시험 매트는 아직 없음 — VGR-01이 만들 것이라 준비 부족으로 보지 않음(막지 않음).
- 앱: `running` 빈 목록(idle). open·편집·저장 0, CAD 호출 1(running). 동작 상태를 바꾸지 않아 초기화할 것 없음.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신), V홈 시험 매트 없음(VGR-01 몫).

근거: E-21, 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 실행 규칙 19, 결정로그 C-34.

## 워크플로우 메모
- 표시만 바뀐 재저장은 .sc(zip)의 document.json을 비교하면 앱을 열지 않고 수 초에 '형상 변화 0'을 판정할 수 있었다.

---

# 준비 점검 — FSAP_v2.8.2 세 번째 확인 (2026-11-09 저녁, 엔진 v3.9.3, 미스미 재로그인·앱 재시작 뒤 재실행)

요약
- 판정: **ready=true**(12:40 MCP 점검 결과 `tools/out/prep282/`를 그대로 씀, E-21 원문 "다시 부르면 이전 결과 파일부터 읽고 남은 것만").
- 대상 `3D_Modeling/FSAP_v2.8.2.sc`(tools/config.json doc, 저장 11-09 11:30). 지시문의 "v2.6.5"보다 config가 최신이라 config를 따랐다.
- 12:40 뒤 바뀐 것 없음: 설계 파일 11:30, `tools/machine.json` 11:31, 요구서 11:41, 자료대기 11:17. 새 버전 .sc 없음(뒤 커밋 14:55~14:56은 보고·회고·실행 기록뿐).
- 유지되는 결과: 조인트 372, 고정부 2, floating 0, 움직이는 조인트 29 = machine.json. 연구 8개(REST 대기 포즈 step 0, CYCLE_S·L·G1·G2, MAINT_HEAD, SEAM_U7, MAINT_U7) step 0 conflicts 0. states 26이 0-3 각 단계와 THICK_6·THICK_16에 대응. C-34대로 높이 조정은 J_U7_HGT 하나(J_U6_HGT 0, 어긋난 자세는 회귀 자세에서 뺌).
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G 좁은 홈(요구서 0-2 양 끝), 떨어지는 조각 없음(D-07).
- 앱: 다시 켜져 있음, `running` 빈 목록. 바뀐 것이 없어 열지 않음 — open·편집·저장 0, CAD 호출 1(running). 동작 상태는 앱이 빈 상태라 초기화할 것 없음.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError, 다시 확인함).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: E-21, 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 결정로그 C-34.

---

# 준비 점검 — FSAP_v2.8.2 다시 확인 (2026-11-09 오후, 엔진 v3.9.3, STEPWAIT·REG-01 뒤 재실행)

요약
- 판정: **ready=true**(같은 날 12:40 MCP 점검 결과 `tools/out/prep282/`를 그대로 씀, E-21 원문 "다시 부르면 이전 결과 파일부터 읽고 남은 것만").
- 대상 `3D_Modeling/FSAP_v2.8.2.sc`(tools/config.json doc, 저장 11-09 11:30). 지시문의 "v2.6.5"보다 config가 최신이라 config를 따랐다.
- 앞 점검(12:40) 뒤 바뀐 것 없음: 설계 파일 11:30, `tools/machine.json` 11:31, 요구서 11:41, 자료대기 11:17 — 모두 앞 점검보다 이르다. 새 버전 .sc 없음(최근 커밋은 보고·회고 기록뿐).
- 유지되는 앞 점검 결과: 조인트 372, 고정부 2, floating 0, 움직이는 조인트 29(= machine.json). 연구 8개(REST 대기 포즈 step 0, CYCLE_S·L·G1·G2, MAINT_HEAD, SEAM_U7, MAINT_U7) step 0 conflicts 0. states 26이 0-3 각 단계와 THICK_6·THICK_16에 대응. C-34대로 높이 조정은 J_U7_HGT 하나(J_U6_HGT 0, 어긋난 자세는 회귀 자세에서 뺌).
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G 좁은 홈(요구서 0-2 양 끝), 떨어지는 조각 없음(D-07).
- 앱: 사용자 "솔리드크래프트 꺼져있어", `running` 빈 목록. open·편집·저장 0, CAD 호출 1(running).
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError, 다시 확인함).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: E-21, 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 결정로그 C-34.

---

# 준비 점검 — FSAP_v2.8.2 (2026-11-09, 엔진 v3.9.3, MOT-01·FUNC-01·COLOR-01 뒤)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.8.2.sc`(tools/config.json doc, 저장 11-09 11:30). 지시문의 "v2.6.5"보다 config가 최신이라 config를 따랐다.
- 통로: MCP(혼자 도는 읽기 부서, 실행 규칙 2). `running` 빈 목록 → `open` 한 번(피처 2303, 오류 0, 이름 FSAP_v2.8.2) → `motion.list` → 연구 7개 `motion.play step 0` → 마지막 `REST` step 0(원복) → `joint.list`. 편집·저장 0. 결과 `tools/out/prep282/`(motion_list.txt, studies_play.txt, joint_list.txt).
- 앞 점검(v2.6.8) 뒤 바뀐 것: FUNC-01이 새 조인트 **J_U5_FLOAT**(슬라이더 Z 0~20, U5_LIFT→U5_FLOAT)를 넣고 연구 8·states 26의 J_U5_LIFT 값을 (−10, FLOAT v+10)으로 바꿨다(machine.json _history). 그래서 이전 결과를 쓰지 않고 다시 쟀다(E-21).
- 조인트: 372개(rigid 343, slider 20, revolute 9), 고정부 2(occ 0·2), **floating 0**, errors 0, conflicts 0. 움직이는 조인트 29 = machine.json joints 29(빠짐·남음 0). **J_U6_HGT 0** → C-34대로 높이 조정은 J_U7_HGT 하나.
- 동작 연구 8: REST 1·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13단계. 모두 step 0 재생 conflicts 0, unmoved 0, stopped_by_contact 없음(호출당 0.1~1.0 s).
- machine.json: doc = v2.8.2, units 13, studies 8, states 26(0-3 사이클: 로딩·바퀴 내림·직선·볼록 45°/90°·홈 입구/안 벽/바닥 오목·이음매·배출, 정비 2, THICK_6·THICK_16), path_parts 6, temp_values 11.
- 작업 대상 모형: WP_L 1500×1500·WP_S 300×200·WP_G 좁은 홈(조인트 J_WP_L/S/G_X·Y·ROT 있음, 요구서 0-2 양 끝). 떨어지는 조각 없음(D-07). 요구서는 앞 점검 뒤 5절 FUNC-01·COLOR-01 행만 바뀜 → 0-2·0-3·6-4 대응 판정 그대로.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신). `edit.checkpoint`(129)는 연구 재생 뒤 '이미 버려짐'으로 되돌리기 못 함 — 편집이 없고 REST step 0으로 대기 자세에 돌려 두어 영향 없음(저장 0).

근거: E-03 동작 검사 준비, E-15 "움직임은 기계 정의의 조인트로만", E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"(조인트가 바뀌어 다시 잼), 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 결정로그 C-34.

## 워크플로우 메모
- `edit.checkpoint` 뒤 `motion.play` 8번을 하면 체크포인트가 사라졌다("no checkpoint 129 ... only the last 16 are kept"). 읽기 부서의 원복은 REST step 0으로 충분했다.
- `motion.list`·`motion.play`·`joint.list` 응답이 0.37~9.8 MB라 화면 한도를 넘는다. 요약만 돌려주는 인자가 있으면 좋다.

---

# 준비 점검 — FSAP_v2.6.8 (2026-11-09, 엔진 v3.9.3, STEPSWAP 뒤)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.6.8.sc`(tools/config.json doc, 저장 11-09 01:54). 지시문의 "v2.6.5"보다 config가 최신이라 config를 따랐다(REG-02 → v2.6.6·v2.6.7, STEPSWAP → v2.6.8).
- 통로: 없음(설계 파일 열지 않음). 사용자 "솔리드크래프트 꺼져있어", `running` 빈 목록. E-21 원문 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"대로 v2.6.7 점검(아래 절)과 STEPSWAP 저장본 검증 결과를 썼다. CAD 호출 1(running), open·편집·저장 0.
- v2.6.7 → v2.6.8 바뀐 것: 고정 유닛 U8 레귤레이터 IR1000-01BG ×3 실물 STEP 교체와 그 브래킷·볼트·KQ2L08·TU0805 관(mech_regression_14.md "고정 유닛 U8만 바뀌어 움직이는 바디의 형상·조인트 변화 0").
- 조인트(v2.6.8 저장본 검증, `tools/out/mech_STEPSWAP/r4/verify_joint_list.json`·`jl.json`): 324개(v2.6.7의 317 + 새 부품 rigid 7), 고정부 2(occ 0·2), **floating 0**, errors 0, conflicts 0. 움직이는 조인트 28 = machine.json joints 28. 저장본·앱 바디 2666 같음, 타임라인 2064 오류 0, `STEP대기_IR` 남음 0, dirty False, 이름 FSAP_v2.6.8(`r4/verify_summary.txt`).
- 동작 연구 8(REST 대기 포즈 step 0, CYCLE_S·L·G1·G2, MAINT_HEAD, SEAM_U7, MAINT_U7): STEPSWAP은 연구를 고치지 않았다(움직이는 조인트 변화 0) → v2.6.7 판정(step 0 conflicts 0, unmoved 0) 그대로.
- machine.json(11-09 01:55): `doc` = v2.6.8, joints 28, units 13, studies 8, states 26, path_parts 6, temp_values 11. J_U6_HGT는 주석·이력에만 남음(조인트 정의 0) → C-34 "한 높이 조정"·"어긋난 자세는 회귀 자세 정의에서 뺀다" 충족(THICK_6 −4 · THICK_16 +6).
- 요구서(11-09 02:36, 커밋 안 됨): 5절 MOT-01 행 고침과 COLOR-01 행 추가뿐. 0-2·0-3·6-4 칸 그대로 → 작업 대상 모형(WP_L 1500×1500·WP_S 300×200·WP_G 좁은 홈, 떨어지는 조각 없음 D-07)과 상태 대응 판정 그대로.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError, 다시 확인함).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 결정로그 C-34.

---

# 준비 점검 — FSAP_v2.6.7 다시 확인 (2026-11-09, 엔진 v3.9.3, 재실행)

요약
- 판정: **ready=true**(같은 날 00:26 MCP 점검 결과를 그대로 씀, E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"). 결과 `tools/out/prep267/`.
- 대상 `3D_Modeling/FSAP_v2.6.7.sc`(tools/config.json doc, 저장 11-08 22:25). 지시문의 "v2.6.5"보다 config가 최신이라 config를 따랐다.
- 앞 점검 뒤 바뀐 것: 요구서(11-09 01:01, 커밋 c39db92) — 5절 REG-01 행 상태와 RGSEE 행 추가뿐. 0-2·0-3·6-4 칸, 설계 파일, `tools/machine.json`(11-08 22:25), 자료대기(11-08 22:45)는 그대로 → 동작 정의·작업 대상 모형·상태 대응 판정 그대로.
- 앞 점검 결과(유지): 조인트 317, 고정부 2, floating 0, 움직이는 조인트 28(= machine.json). 동작 연구 8(REST 대기 포즈 step 0, CYCLE_S·L·G1·G2, MAINT_HEAD, SEAM_U7, MAINT_U7) step 0 conflicts 0. C-34대로 높이 조정은 J_U7_HGT 하나(J_U6_HGT 없음).
- 앱: 다시 켠 빈 상태, `running` 빈 목록. open·편집·저장 0, 설계 파일 연 수 0, CAD 호출 1.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError, 다시 확인함).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: E-21 원문 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다".

---

# 준비 점검 — FSAP_v2.6.7 (2026-11-09, 엔진 v3.9.3, REG-02 C-34 뒤)

요약
- 판정: **ready=true**. 대상 `3D_Modeling/FSAP_v2.6.7.sc`(tools/config.json doc, 저장 11-08 22:25). 지시문의 "v2.6.5"보다 config가 최신이라 config를 따랐다(REG-02가 v2.6.6·v2.6.7을 냄).
- 통로: MCP(혼자 도는 읽기 부서, 실행 규칙 2). `running` 빈 목록 → `open` 한 번(4초, 피처 2054, 오류 0) → `motion.list`·연구 8개 `motion.play step 0` → `joint.list` → 마지막 `REST` step 0(원복). 편집·저장 0. 결과 `tools/out/prep267/`(studies_batch.txt, joint_list.txt).
- 조인트: 317개, 고정부 2(occ 0·2), **floating 0**, errors 0, conflicts 0. 움직이는 조인트 28(machine.json joints 28과 같음). **J_U6_HGT 없음**, `J_U6_ON_U7FIX`는 rigid → C-34대로 높이 조정은 J_U7_HGT 하나.
- 동작 연구 8: REST(1단계)·CYCLE_S 450·CYCLE_L 716·CYCLE_G1 514·CYCLE_G2 630·MAINT_HEAD 1·SEAM_U7 32·MAINT_U7 13. 모두 step 0 재생 conflicts 0, unmoved 0.
- machine.json(11-08 22:25): `doc` = v2.6.7(앞 점검의 'v2.6.4를 가리킴' 미완 해소). J_U6_HGT 참조 0. states 26 — 0-3 사이클 단계(로딩·바퀴 내림·직선·볼록·홈 입구/안/바닥·이음매·배출)와 정비·THICK_6(J_U7_HGT −4)·THICK_16(+6) 대응. 두 높이가 다른 자세는 더 만들 수 없다(C-34 "어긋난 자세는 회귀 자세 정의에서 뺀다" 충족).
- 작업 대상 모형: WP_L·WP_S·WP_G(MAT·TAPE·SEAM) 조인트 9개 모두 풀림(errors 0). 떨어지는 조각 없음(workpiece_stages 주석, D-07). 요구서 0-2·0-3·6-4는 11-08 뒤 REG-01 행 한 줄만 바뀜 → 크기 범위 판정 그대로.
- gmsh: 불러올 수 없음(`python -B -c "import gmsh"` → ModuleNotFoundError).
- 미완(막지 않음, 앞과 같음): 6-4 계단형 오목 모서리 매트 모형 없음(홈 바닥 오목 반원으로 대신).

근거: 실행 규칙 2 원문 "혼자 도는 읽기 부서도 MCP로 잰다", 실행 규칙 7 "자료대기 D-번호 임시값으로 만든 준비물은 준비된 것으로 본다", 결정로그 C-34.

---

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
