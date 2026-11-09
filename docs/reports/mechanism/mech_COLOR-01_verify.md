# COLOR-01 검도·체결 — 모델 색 통일(체결 부품 흑색 금지)

## 요약
- 대상 `3D_Modeling/FSAP_v2.8.2.sc`(MCP open 1회, 읽기만, save 0). 판정: **통과(동작 문제 0), 완료 판정 충족.**
- 범위(E-17): `ledger.py scope` → 바뀜 0·새로 0·없어짐 0·이웃 0, `sigcheck` → "문서·해시가 같다"(2,729 부품). 형상 변화가 없어 조인트 점 동작 검사·간섭 검사 대상 없음.
- 형상: 피처 2,303·오류 0, 고유 바디 632, dirty false(저장 뒤 그대로).
- 색(저장본에서 직접 다시 잼): 632 고유 바디 해석 색(appearance.list body별, CLI) 13종 = 색표 13칸, 색표 밖 0. 체결 1,198 바디 #b4b9bf(흑색 #3a3a3a 0, L*<40 0).
- 디테일 1: 147 고유 바디(체결 141 + SFB5·HFS8·SV2RL 블록 6, 복사 포함 640)의 STEP 가져온 면 칠 #cad1ee가 남아 있다. appearance.chain 결과 면 단계 null·활성 = 재질 색이라 화면 색은 색표 안. 다만 '구매품 STEP 원색 예외 목록'에 적어 둔다(모델링 보고서의 '예외 0'을 바로잡음).
- 원장 갱신(ledger commit 2026-11-08, 부품 2,729·통과 항목 53). REST step 0(moved false).

## 1. 범위(E-17)
| 항목 | 결과 | 근거 |
|---|---|---|
| scope | full false, 바뀜·새로·없어짐·이웃 0 | `tools/out/scope.json` |
| sigcheck | mode reuse, "문서·해시가 같다", parts 2,729 | ledger.py sigcheck |
| 바뀐 부품 | [] (지시서) | 모델링 결과 |

E-17 원문: "검증 원장(out/ledger.json)과 바뀐 범위로 검사 범위를 정한다." 바뀐 바디가 0이라 E-03 과제 안 검사(관련 조인트 0·25·50·75·100 %)는 대상이 없다. 작업 대상 길에 닿는 부품 변화도 0 → 매트 모형 검사 없음. 전체 사이클은 라운드 끝 회귀 몫.

## 2. 완료 판정 확인
| 완료 판정 | 결과 | 근거 |
|---|---|---|
| 색표 밖 색 바디 0 | 0 (632 고유 바디 해석 색 13종 모두 색표 안) | `tools/out/verify_COLOR-01/faces_out.json` |
| 체결 부품 흑색 0 | 0 (체결 해석 색 #b4b9bf 하나) | 같은 파일, appearance.list 설계 지정 COL_F_FASTENER 67 + SCM435 재질 651 |
| 형상·바디 수·BOM 변화 0 | 피처 2,303·오류 0·고유 바디 632·재질 이름·밀도 그대로 | open·inspect_design·material.list |

- 재질 색(material.list): S45C·SK5 #9ea4ac, SUS304 #c8ccd0, SCM435 #b4b9bf, A5052·A6061 #ccd0d6, Urethane_A70 #d9a33a, PET-CF #d4d4d0, PA12 #e8e4da. 기본 재질 Steel(117 바디)·Aluminum(80 바디)은 해석 색이 #9ea4ac·#ccd0d6로 나와 색표 안(표본 I-020B_M02, CDM2C20-25Z_BODY).
- 설계 지정(appearance.list {}): 9 외관(COL_TP·WP·EV·PM·F_FASTENER·RG·RW·PT·SF), 컴포넌트 지정 0, 설계 단계 면 지정 0.

## 3. 디테일 — STEP 가져온 면 칠 #cad1ee (예외 목록 누락)
- 무엇: body별 appearance.list의 faces에 'Custom' #cad1ee가 147 고유 바디·151 면(복사 포함 640 바디: 체결 634, 강 4, 알루 2)에 남아 있다. 예: CB5-16_M01_1 면 2, HFS8-80160-1090_M07 면 162·199·292·293, SV2RL28-1800_BLOCK 면 70·72, SFB5-10_M04 면 3. 목록 `tools/out/verify_COLOR-01/face_looks.json`.
- 화면 색: appearance.chain {body CB5-16_M01_1, face 2}·{HFS8-80160-1090_M07, face 162} → face·body·component 단계 null, active = material(#b4b9bf·#ccd0d6). 안내문 "Imported paint is a display fallback outside the four steps" — 재질 색이 있으면 쓰이지 않는다. #cad1ee는 흑색도 아니다(L* 약 83).
- 판정: 완료 판정 미달 아님(해석 색 색표 안, 흑색 0). 다만 완료 판정 괄호의 '구매품 STEP 원색 예외 목록'에 이 147 바디를 올려야 기록이 맞다. 모델링 보고서 '구매품 STEP 원색 예외 0', '얼굴 지정 0'은 설계 지정 기준이고 가져온 칠은 안 셌다.
- 고치는 법(선택, 형상 변화 없음): 결정로그 COLOR 색표에 'STEP 가져온 면 칠 #cad1ee — 재질 색에 가려 보이지 않음, 147 바디' 예외 줄을 더한다. 칠을 아예 없애려면 다음 버전에서 `appearance.assign {bodies:[147 이름], color:"#b4b9bf"}`(체결)·재질 색(강 #9ea4ac, 알루 #ccd0d6)로 바디 지정을 덮는다 — 이번엔 보이는 색이 같아 하지 않아도 된다.

## 4. 볼트·리지드 그룹·포트·판금
새로 넣거나 옮긴 볼트 0, 판금 변경 0, 조인트·리지드 그룹 변화 0 → M-01·E-11·M-06·M-04 검사 대상 없음.

## 5. 등급
S 맞음. E-18 "체결만 바뀐 자리는 손계산, FEA는 형상·하중 경로가 바뀐 부품만" — 표시 속성만 바뀌어 새 구매품·조인트·유닛 걸친 형상 변경 없음. FEA·손계산 대상 없음(해석 환경 없음 D-16과 무관).

## 6. 통로·시간
- MCP: running [] 확인 → open v2.8.2 1회(features 2,303, errors 0) → appearance.list·material.list·appearance.chain → motion.play REST step 0(moved false) → inspect_design dirty false. save 0.
- CLI: body별 appearance.list 632단계를 `solidcraft-cli run --results`로 한 번(4분 33초, 출력 23.7 MB 파일). MCP 응답이 바디당 약 26 KB라 파일 출력이 필요한 긴 읽기라 CLI로 보냄(규칙 2 'CLI로 보낼 것: 100단계 넘는 연구').
- 재료: `tools/out/verify_COLOR-01/faces.json`·`faces_out.json`·`face_looks.json`.

## 워크플로우 메모
- 모델링부 색 검증(verify_color.py)은 계획(color_plan)과 보낸 명령으로 셈한 것이고 저장본의 body별 해석 색·면 칠을 재지 않았다. 색 과제 검증은 저장본에서 appearance.list {body}로 면까지 다시 재야 가져온 STEP 칠이 드러난다.
