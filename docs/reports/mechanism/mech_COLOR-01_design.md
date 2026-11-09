# COLOR-01 기구설계 — 모델 색 통일(체결 부품 흑색 금지)

## 요약
- 대상 v2.8.1(config doc, 2,729 바디). 형상·바디 수·재질·조인트 변화 0 — 표시 색만 바꾼다(등급 S).
- 색표 13칸(COL_F 체결 #b4b9bf … ). 체결 1,198바디는 모두 COL_F 하나(흑색 0). 14가지 섞인 색 → 13칸 표 안.
- 방법: 설계 재질 기본색 편집 6건(SCM435·A5052·A6061·S45C·SK5·PET-CF) + 바디 외관 지정 1,609 이름(17 묶음, 묶음당 ≤ 300 이름, 최대 인자 20.5 KB).
- 명령 배열 `tools/out/mech_COLOR-01/edit.json`(18 명령), 바디별 그룹 `color_plan.json`, 생성기 `color_plan.py`.
- CAD 확인(MCP, 읽기만, checkpoint 120 → 원복): `material.edit SCM435 #b4b9bf`가 SCM435 바디 전부(볼트·멈춤나사·감속기 볼트)를 바꿈, `appearance.assign`가 복사본 이름 `X (경로)`·`"X"@occ[...]` 이름을 원본 바디로 풀어 줌 확인. 원복 뒤 appearance.list 빈 상태, SCM435 #3a3a3a 그대로, motion.play REST step 0.
- 구매품 STEP 원색 예외 0(측정: import 원색 없음). 미완 없음.

## 0. 출발점
- 벤치마크 없음 — 요구서 5절 COLOR-01 예시 색표(형재·알루미늄 은회색, 스테인리스 밝은 은색, 가공 강철 회색, 수지 흰색·연회색, 구매 기구품 회색, 공압 관 반투명 파랑, 안전 노랑, 체결 밝은 금속 회색 하나)를 그대로 색 값으로 정함.
- 원문: 요구서 5절 COLOR-01 "볼트·너트·와셔 등 체결 부품은 흑색 금지 — 밝은 금속 회색(아연 도금·스테인리스 느낌) 하나로 통일".

## 1. 색표(결정로그 COLOR-S1)
| 칸 | 외관 이름 | 색 | 불투명도 | 대상 | 바디 수 |
|---|---|---|---|---|---|
| F | COL_F_FASTENER | #b4b9bf | 1 | 체결 전부(CB·LCB·SFB·FH·멈춤나사·감속기 볼트·실린더 너트·와셔·HNTT T너트), 재질 무관 | 1,198 |
| AL | COL_AL | #ccd0d6 | 1 | 알루미늄(형재 HFS8·A5052·A6061 판·실린더 몸통·풀리) | 103 |
| SS | COL_SS | #c8ccd0 | 1 | SUS304 가공품 | 216 |
| ST | COL_ST | #9ea4ac | 1 | 강철(S45C·SK5·SS400 가공품, 서보·감속기·베어링·축·케이블 베어 임시 형상, 실린더 로드) | 137 |
| RW | COL_RW | #e8e4da | 1 | 수지 흰색(PA12 출력품, 나일론 볼 827) | 832 |
| RG | COL_RG | #d4d4d0 | 1 | 수지 연회색(PET-CF 출력품, ABS 게이지, 마감캡 HFC8-4080-B) | 66 |
| UR | COL_UR | #d9a33a | 1 | 우레탄 바퀴 트레드 | 2 |
| PM | COL_PM | #8c9198 | 1 | 재질 미지정 구매 기구·공압 기기(이음 KQ2, 밸브 SY·SS5Y3, MGPM, 베어링 6200ZZ, 센서 E32, igus 2400 링크, 벨트·풀리 N16, 867 헤드 임시 형상) | 109 |
| PT | COL_PT | #3d7fd1 | 0.55 | 공압 관 TU | 25 |
| SF | COL_SF | #f2c200 | 1 | 안전(F3SG 라이트 커튼·F39 브래킷·LR6 경광등) | 25 |
| EV | COL_EV | #9fc3e6 | 0.35 | 유닛 차지 상자(U3_LOWER_DRIVE 등 5) + U8_HMI_PANEL | 6 |
| WP | COL_WP | #5b6b7b | 1 | 매트 모형 MAT_L/S/G | 3 |
| TP | COL_TP | #d0453a | 1 | 테이프·봉제선·기준 표식 | 7 |
| 합 | | | | | 2,729 |

흑색 판정 기준: 밝기(L*) 40 미만을 흑색으로 본다. 가장 어두운 칸 WP #5b6b7b(L* 약 44)는 체결이 아니다. 체결 COL_F #b4b9bf L* 약 75.

## 2. 적용 방법(가장 적은 변경, 재질 그대로)
1. `material.edit` 6건 — 재질 이름·밀도 그대로, 색만: SCM435 → #b4b9bf, A5052·A6061 → #ccd0d6, S45C·SK5 → #9ea4ac, PET-CF → #d4d4d0. SUS304·PA12·Urethane_A70은 이미 표 색.
2. 내장 재질(Steel·Aluminum)은 표 색과 같아 그대로. Stainless Steel(4, 모두 FH 볼트)·Nylon(827 볼)·ABS(2)·Default(239)는 바디 외관으로 덮는다.
3. `appearance.assign {bodies, color, opacity, name}` — 재질 기본색(편집 뒤)이 바디의 표 칸과 다른 바디만: F 547(Steel 523 너트·T너트 등, SUS304 와셔 14, Stainless 4, Default 6), RW 827, PM 109, RG 60, PT 25, SF 25, EV 6, TP 7, WP 3 = 1,609 이름.
4. 이름이 같은 두 바디(`CB3-10_M08_PX_KDM`, `CB5-12_M08_PZ_KDM`)는 SCM435라 재질 편집으로 바뀌고 바디 지정에 넣지 않는다(이름 모호 피함).

## 3. CAD 확인(feasibility)
| 확인 | 결과 |
|---|---|
| 앱 상태 | running 빈 상태, 열린 문서 `FSAP_v2.8.1.sc`, dirty false |
| `material.edit {SCM435, #b4b9bf}` | 성공, 결과 바디 목록 = CB·SFB·FH·멈춤나사·PGX62 ABOLT/CLAMP_BOLT·STEP대기_CB 뿐(체결 외 SCM435 0) |
| `appearance.chain CB3-10_M08_PX_KDM` 편집 뒤 | active material #b4b9bf |
| `appearance.assign` 복사본 이름 `SY3120-5LZD-M5_M08 (U8_PNEU:1/…)`·`"HNTT8-5_M07K_PY_PX"@occ[2/7903]` | 원본 바디 `SY3120-5LZD-M5_M08`·`HNTT8-5_M07K_PY_PX`로 풀려 지정됨 → 복사본은 원본과 같은 색(모두 같은 칸이라 문제 없음) |
| 원복 | `edit.restore_checkpoint 120` → appearance.list 빈 상태, SCM435 #3a3a3a, `motion.play REST step 0` 오류 0 |
| 인자 크기 | 최대 명령 20,510 B < 133 KB(앱 짧은 계산 범위) |

## 4. 완료 판정
| 항목 | 만족 | 근거 |
|---|---|---|
| 색표 밖 색 바디 0 | 예(계획) | 2,729 바디 모두 13칸 중 하나에 배정(color_plan.json), 구매품 원색 예외 0 |
| 체결 부품 흑색 0 | 예(계획) | 체결 1,198 = COL_F #b4b9bf(SCM435 651 재질 편집 + 547 바디 지정) |
| 형상·바디 수·BOM 변화 0 | 예 | 명령은 material.edit(색만)·appearance.assign뿐. 재질 배정·밀도·피처 0 변경 |

모델링부 확인 방법: 적용 뒤 `appearance.list {}`(바디 지정 표)와 `material.list` 색으로 바디마다 결과 색 = 지정 있으면 지정, 없으면 재질 색을 계산해 color_plan.json의 칸 색과 비교 → 불일치 0. 바디 수 2,729·질량 합 변화 0.

## 5. 규칙 자기 점검
- E-02 "구동부 → 브래킷 → 디테일": 형상 변화 없는 표시 과제, 개념 충돌 없음.
- E-05 새 번호 저장: 형상은 같으나 문서가 바뀌므로 새 번호 .sc(모델링부).
- E-18 등급 S: 하중·체결 변화 0 → 손계산·FEA 해당 없음.
- U-07·E-10 추정 STEP: 새 구매품 0, STEP 바꿈 0.
- 마감캡 HFC8-4080-B: 실물은 검정(-B), 모델 표시는 RG 연회색. 형번(-S 밝은 회색) 바꿀지는 구매 결정이라 사용자 몫(STEP-05) — 기록만.
- 앞으로 넣는 바디: 새 구매품·가공품은 넣을 때 이 표 칸으로 외관을 준다(모델링 지시 9).

## 워크플로우 메모
- `motion.play`·`document.inspect` 결과가 80~96만 자로 화면 한도를 넘는다(verbose false도 같음). 결과를 파일로 받아 grep으로 확인했다.
- signatures.json에 색 항목이 없어 색 과제 검증은 appearance.list + 재질 색으로 따로 계산해야 한다.
