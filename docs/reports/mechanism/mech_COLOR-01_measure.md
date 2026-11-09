# COLOR-01 측정 — 모델 색 통일(체결 부품 흑색 금지)

## 요약
- 대상: `3D_Modeling/FSAP_v2.8.1.sc`(config doc, 과제문 'v2.6.8'은 그 뒤 버전이 최신이라 v2.8.1로 잼). 측정 표 sigcheck = reuse(해시 같음, 2,729 바디).
- **설계 안에 지정된 외관(body·face·component appearance)은 0개**(`appearance.list` → bodies {}·faces []·components []·in_design []). 모든 바디의 색은 **재질 기본색**에서만 온다(`appearance.chain` 표본 8개 모두 active = material 또는 null).
- 그래서 받은 STEP의 원색은 지금 모델에 남아 있지 않다 → '구매품 STEP 원색 예외'는 현재 0개.
- 색 종류 13 + 미지정(앱 기본색, 재질 Default) 1 = 14가지.
- **체결 부품 흑색 651바디**: 재질 SCM435(#3a3a3a) — CB·LCB 볼트 634 + 멈춤나사·감속기 볼트 17. 재질 SCM435의 기본색 하나만 바꾸면 651개가 한 번에 바뀐다(`material.edit {material: SCM435, color}`).
- 체결 부품 중 Default(색 미지정) 6: `CB6-20_M03_CAR` ×4·`CB6-20_M03_LIFT` ×2(재질 누락).
- 흑색 비체결: PET-CF(#3a3a3a) 가공품 6(벨트 클램프 2, P_M06_CARR, 롤러·허브 3) — 탄소섬유 재질색이라 색표에서 정할 것.
- 미지정 색(Default) 239바디: 구매품 121(케이블 베어 2400 링크 등), 공압·안전 94(F3SG 라이트 커튼 등), STEP대기 867 헤드 3, 유닛 차지 상자 5, 매트·테이프·기준 표식 10, 볼트 6.
- 판정: already_ok = **false**. 형상·조인트 변화가 필요 없는 표시 과제이고, 재질 기본색 편집 + 소수 바디 appearance 지정으로 끝난다.

## 0. 측정 표·통로
| 항목 | 값 |
|---|---|
| sigcheck | `{"mode":"reuse","reason":"문서·해시가 같다","parts":2729}` |
| 통로 | MCP(앱 켜짐, running 빈 상태 확인 뒤 `open` 1회 — 2,303 피처, 오류 0) |
| 원복 | 편집 없음, 저장 없음. 끝에 `motion.play {study: REST, step: 0}` 성공(conflicts 0) |
| 통로·프로브 | 색 과제라 공간 통로·작업 대상 이동 경로는 해당 없음(형상 변화 0) |

## 1. 재질별 색(앱 실측, `material.list`·`material.inspect`)
| 재질 | 기본색 | 사용자 정의 |
|---|---|---|
| Default | 없음(앱 기본색) | - |
| Steel | #9ea4ac | 내장 |
| Stainless Steel | #babfc6 | 내장 |
| Aluminum | #ccd0d6 | 내장 |
| Nylon | #ece6d6 | 내장 |
| ABS Plastic | #deded8 | 내장 |
| S45C | #9aa0a6 | 설계 |
| SUS304 | #c8ccd0 | 설계 |
| **SCM435** | **#3a3a3a(흑색)** | 설계 |
| A5052 | #b8c0c8 | 설계 |
| A6061 | #aab4be | 설계 |
| Urethane_A70 | #d9a33a | 설계 |
| **PET-CF** | **#3a3a3a(흑색)** | 설계 |
| PA12 | #e8e4da | 설계 |
| SK5 | #5f6670 | 설계 |

## 2. 역할 × 재질 × 색 바디 수(2,729)
역할은 이름 규칙으로 나눔(체결 = bolt 표시 또는 CB·LCB·MS·FH·SETSCREW·WASHER·NUT·ABOLT 이름, 가공 = P_, 공압 = U8·SMC 형번, STEP대기 = 이름 머리). 전체 목록 `tools/out/mech_COLOR-01/bodies_color.json`(바디마다 이름·유닛·재질·색·역할·bbox), 표 원본 `classify.txt`, 스크립트 `classify.py`.

| 역할 | 재질 | 색 | 수 | 예 |
|---|---|---|---|---|
| 체결 | SCM435 | #3a3a3a | 651 | CB5-16_*, CB6-*, 멈춤나사 STEP대기_SETSCREW_M4x25, PGX62 ABOLT |
| 체결 | Steel | #9ea4ac | 513 | 실린더 너트·와셔 등 |
| 체결 | SUS304 | #c8ccd0 | 14 | P_M02_*_WASHER, P_M03_IDLER_WASHER, P_M06_ROLL_WASHER |
| 체결 | Stainless Steel | #babfc6 | 4 | STEP대기_FH4-M4-15_REG02_1~4 |
| 체결 | Default | 미지정 | 6 | CB6-20_M03_CAR ×4, CB6-20_M03_LIFT ×2 |
| 가공 | SUS304 | #c8ccd0 | 206 | P_DC203_TRAY, P_DC205_DISC_* … |
| 가공 | A5052 / A6061 | #b8c0c8 / #aab4be | 9 / 3 | P_M02_DISK, P_M03_CAR_PLATE / P_M02_WHEEL |
| 가공 | S45C | #9aa0a6 | 8 | P_M01_FOOT, 핀·축 |
| 가공 | Steel | #9ea4ac | 5 | P_M07_BEAM·SEAT·SPLICE(BOM SS400·STKR400) |
| 가공 | PA12 | #e8e4da | 5 | P_M05_BINDER·GUIDE … |
| 가공 | PET-CF | #3a3a3a | 6 | P_M03_BELT_CLAMP_*, P_M06_CARR·롤러 |
| 가공 | SK5 | #5f6670 | 2 | P_M05_CUT_BLADE·FIX |
| 가공 | Urethane_A70 | #d9a33a | 2 | 바퀴 트레드 |
| 공압·안전 | Default | 미지정 | 94 | F3SG-4RA0800-14 라이트 커튼, 이음, 관 TU0805 |
| 공압·안전 | Aluminum / Steel | #ccd0d6 / #9ea4ac | 12 / 7 | 실린더 몸통 / 로드 |
| 공압·안전 | A5052 / SUS304 | | 6 / 10 | P_M08_* 판·브래킷(가공품) |
| 공압·안전 | ABS | #deded8 | 2 | IR1000 게이지 |
| 구매 | Aluminum | #ccd0d6 | 67 | HFS8-4080 형재 |
| 구매 | Default | 미지정 | 121 | igus 2400 케이블 베어 링크 등 |
| 구매 | Steel / S45C / A6061 | | 55 / 6 / 5 | HNTT8 T너트(이름 앞 따옴표로 체결로 안 잡힘 — 실제 체결), PGX62 축·키, 풀리 |
| STEP대기 | Nylon | #ece6d6 | 827 | STEP대기_BALL_D25_M04 |
| STEP대기 | Steel / S45C / Aluminum | | 60 / 4 / 1 | 케이블 베어·인서트·PSCS16·SCXW46 |
| STEP대기 | Default | 미지정 | 3 | 867 헤드 UPPER·LOWER·NOSE |
| 차지 상자 | Default | 미지정 | 5 | U3_LOWER_DRIVE, U7_TAPE_ROLL … |
| 매트·기준 | Default | 미지정 | 10 | MAT_L/S/G, TAPE·SEAM, REF_NEEDLE_AXIS_MARK |

참고: 체결 합계 1,188(+ HNTT8 T너트 일부 '구매'로 분류된 것). BOM 가공품 103행 재질은 위 재질과 같고 SS400·STKR400만 앱 재질 Steel로 들어가 있다(색 과제와 무관, 기록만).

## 3. 구상·모델링이 쓸 사실
- 색은 재질 기본색 → 바디 appearance → 면 appearance 순으로 덮인다(`appearance.chain` steps: face·body·component·material). 지금은 위 3단이 모두 비어 있다.
- 가장 적은 변경: (1) 설계 재질 기본색 편집(`material.edit`, SCM435·PET-CF 등), (2) 내장 재질 색이 색표와 다르면 `appearance.replace` 또는 `appearance.assign {bodies}`, (3) Default 239바디는 역할별로 `appearance.assign {components 또는 bodies}`. 재질은 바꾸지 않는다(질량·BOM 변화 0 조건).
- 내장 재질(Steel·Aluminum 등)은 `material.edit` 대상이 아니다(설계 정의 재질만). 내장 재질 색을 바꾸려면 바디 appearance로 덮어야 한다.
- 받은 STEP 원색은 import 때 남지 않았으므로 '원색 유지'를 고르면 STEP을 다시 넣어야 한다 → 형상 변화가 생겨 이 과제(형상 0) 밖. 색표에서 구매품은 '역할색'으로 정하는 것이 맞다.

## 4. 관련 기록·기각 이유
- STEP-05(결정로그): 형재 마감캡 HFC8-4080-B 검정 — "색은 문서에 정해진 것이 없어 검정으로 둠". 사용자 2026-11-09 지시로 색표가 정해지면 마감캡 표시색도 그에 따른다(형번 `-S` 밝은 회색 선택은 구매 결정이라 사용자 몫, 모델은 표시색만).
- 요구서 5절 COLOR-01: 예시 색표(형재·알루미늄 = 은회색, 스테인리스 = 밝은 은색, 가공 강철 = 회색, 수지 = 흰색·연회색, 구매 기구품 = STEP 색 유지 또는 회색, 공압 관 = 반투명 파랑, 안전 = 노랑), 체결은 밝은 금속 회색 하나.
- 결정로그에 색표 결정은 아직 없음(excerpt 'COLOR-01'·'색' 검색 0건).

## 5. 이미 되는가
| 완료 판정 | 지금 | 결과 |
|---|---|---|
| 체결 부품 흑색 0 | SCM435 #3a3a3a 651 | 미달 |
| 색표 밖 색 바디 0 | 색표 없음, 14가지 색 섞임, 미지정 239 | 미달 |
| 형상·바디 수·BOM 변화 0 | 해당(아직 변경 없음) | - |

already_ok = false.

## 워크플로우 메모
- signatures.json에 색(look) 항목이 없다. 색 과제는 재질에서 유도했다(외관 지정 0이라 정확).
- `motion.play` 결과가 96만 자로 화면 한도를 넘었다(결과는 성공). 읽기 부서 원복에 verbose를 줄일 방법이 있으면 좋다.
