# COLOR-01 완료 판정 확인 — 모델 색 통일(체결 부품 흑색 금지)

## 요약
- 판정: **ok = true** (완료 판정 3항목 모두 만족). 안 COLOR-S1 하나(WF-176, 비교 없음).
- 바뀌는 부품: 없음(형상 0). 명령 18개 = material.edit 6(색·불투명도만) + appearance.assign 12.
- 다시 계산(설계안 파일로 독립 계산, CAD 안 씀): 2,729 바디 최종 색 = 바디 지정(있으면) 아니면 편집 뒤 재질색 → 13칸 표 밖 0, 그룹 불일치 0.
- 결과 칸 수: F 1,198 · RW 832 · SS 216 · ST 137 · PM 109 · AL 103 · RG 66 · PT 25 · SF 25 · TP 7 · EV 6 · WP 3 · UR 2(설계안 counts와 같음).
- 체결 흑색(L* < 40): 0. COL_F #b4b9bf L* 74.9. 가장 어두운 칸 WP #5b6b7b L* 44.5(매트 모형, 체결 아님).
- 미완: 없음. 기록만: 평행핀 MSTH6-20_M05 ×2는 ST 칸(#9ea4ac, L* 67.1) — 핀은 볼트·너트·와셔가 아니라 그대로 둬도 흑색 금지 위반 아님.

## 1. 방법
- 입력: `tools/out/mech_COLOR-01/bodies_color.json`(측정, 바디마다 재질·현재색), `color_plan.json`(바디별 칸), `edit.json`(명령).
- 계산 스크립트: 스크래치 `dc.py`(읽기만). 재질 기본색은 측정 표(mech_COLOR-01_measure.md 1절)에 edit.json의 material.edit 6건을 덮어 씀. appearance.assign 이름은 설계안 CAD 확인대로 복사본 이름 `X (경로)`·`"X"@occ[...]`를 원본 이름 X로 풀어 적용.
- 원장 서명: 형상 변화 0이라 sigcheck 재사용(측정 reuse, 해시 같음). E-17 범위 검사·E-18 FEA 해당 없음(등급 S, 하중 경로 변화 0).

## 2. 항목별 판정
| 항목 | 다시 계산한 값 | 판정 |
|---|---|---|
| 색표 밖 색 바디 0(구매품 STEP 원색 예외 목록) | 2,729/2,729 바디가 13칸 색·불투명도 중 하나. 색 없는 바디(Default 239) 모두 지정됨, 남는 표 밖 색(Nylon #ece6d6·Stainless #babfc6·ABS #deded8·S45C #9aa0a6·SK5 #5f6670·A5052·A6061·SCM435·PET-CF #3a3a3a) 모두 편집 또는 지정으로 덮임. 원색 예외 0(측정: 설계 외관 지정 0, import 원색 없음) | 만족 |
| 체결 부품 흑색 0 | 체결 역할 1,188(측정 이름 규칙) + HNTT8 T너트 등 → F 칸 1,198 모두 #b4b9bf(L* 74.9). SCM435 651은 재질 편집 #3a3a3a → #b4b9bf, 나머지 547 바디 지정. 체결 이름(CB·LCB·SFB·FH·HNTT·NUT·WASHER·SETSCREW·ABOLT) 중 F 밖 바디는 평행핀 MSTH6-20 ×2(ST, L* 67.1)뿐 | 만족 |
| 형상·바디 수·BOM 변화 0 | edit.json 명령 종류 = material.edit 6(인자 material·color·opacity만, 밀도·이름 없음) + appearance.assign 12(bodies·color·opacity·name). 피처·재질 배정·조인트 명령 0 → 바디 수 2,729·질량·BOM 그대로 | 만족 |

## 3. 반박 시도와 결과
- 이름 모호: 같은 이름(또는 복사본을 원본으로 푼 이름)이 서로 다른 칸에 걸린 경우 0, 지정끼리 색 충돌 0(지정 이름 231개 원본). 원본 이름 하나에 지정하면 복사본 전부가 같이 바뀌지만 모두 같은 칸이라 결과가 같다.
- 재질 편집이 체결 아닌 바디를 끌고 가는지: SCM435 651은 모두 F 칸(설계안 CAD 확인: 체결 외 SCM435 0, 독립 계산도 그룹 불일치 0). PET-CF 6은 모두 RG, S45C·SK5는 ST, A5052·A6061은 AL·(공압 판은 그 칸) — 불일치 0.
- 내장 재질 Steel #9ea4ac = ST, Aluminum #ccd0d6 = AL로 편집 없이 표 안. SUS304 #c8ccd0 = SS, PA12 #e8e4da = RW, Urethane_A70 #d9a33a = UR.
- 인자 크기: 최대 20,510 B < 133 KB(안내서 '연결' 짧은 계산 범위).

## 4. 모델링부에 넘길 확인(설계안 4절 그대로)
- 적용 뒤 `appearance.list {}` + `material.list`로 바디 최종 색을 다시 계산해 color_plan.json과 불일치 0, 바디 수 2,729·질량 합 변화 0을 확인. 저장 전 REST step 0, 조인트 글리프 숨김(실행 규칙 19), 새 번호 저장(E-05).

## 워크플로우 메모
- 색 과제는 signatures.json에 색 항목이 없어 완료 확인을 파일 계산으로 했다(설계안 메모와 같음).
