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
