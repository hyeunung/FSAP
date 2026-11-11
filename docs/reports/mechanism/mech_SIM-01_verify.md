# SIM-01 검도 2회차 — v2.10.4 테이프 보임·U4 묶음 간섭·영상 (검도·체결부, 2026-11-12)

요약(10줄 안):
- 대상 `3D_Modeling/FSAP_v2.10.4.sc`(형상 변경 0, 표시만). 바뀐 부품 0, 새 볼트·조인트·간이 형상 0.
- 사용자 질문("이거 안보이냐고")의 원인 확인: v2.10.4를 MCP로 열어 숨김 목록을 읽음 — MAT_L·SEAM_L·TP_L_* 48바디는 숨김 목록에 없음(보임), 숨김 occurrence 0, 보이는 스케치 0. 숨김은 L과 같은 자리 대안 매트 S·G·V 세트만.
- check4(U4 묶음 10개 against, CLI, budget_s 600) 결과 파일 재확인: CYCLE_L 716단계 276쌍·S 450/60·G1 514/228·G2 630/228·V 486/228, 모두 collisions 0, truncated false.
- U4 묶음 밖 루트 M02 바디 21개(회전 원판 베어링·볼트, E32 센서)도 확인: REST에서 MAT_L과 최소 0.5 mm(원판 볼트, 매트 밑), 테이프·조각과 2 mm 안 쌍 0. 위치 논리로 전 단계 겹침 불가(아래 3절).
- 영상 5연구 anim3/: GIF 5개 + 바늘 근처 PNG 각 167장(≥ 150), 접촉 정지 0.
- 굽힘 R 3/19(≥ 3, D-167), 풀림 차 ≤ 0.25 %(≤ 1 %, D-168), 비틀림(D-169): 테이프 줄 형상 변화 0이라 1회차 값 유지.
- 동작 문제 0, 완료 판정 만족. 디테일 1(M02R 빈 볼트 컴포넌트 — M02R 과제 소관, 기록만).
- 등급 L 맞음.

## 1. 범위(E-17)

`ledger.py scope`: 전체 검사 예(바뀜 21, 새로 264, 없어짐 32, 이웃 227). 원장 서명이 v2.10.2 기준이라 M02R(v2.10.3) 변경이 함께 잡힌다. 이 과제(SIM-01) 범위는 테이프 줄(U7_TAPE_LINE·U7_TAPE_FEED)·조각(WP_TP_*·SEAM)·매트와 그 주변 유닛(U3·U4·U5·U6). 전체 사이클은 돌지 않는다(라운드 끝 전체 회귀).

E-17 원문: "검증 원장(out/ledger.json)과 바뀐 범위로 검사 범위를 정한다".

## 2. 테이프 보임 확인(사용자 질문)

MCP `open v2.10.4`(오류 0, 피처 3,598) → `edit.checkpoint` → 이미 숨은 MAT_S에 `browser.visibility {visible:false}`(변화 없는 호출)로 현재 숨김 상태를 읽음 → `edit.restore_checkpoint`.

| 항목 | 값 |
|---|---|
| 숨김 바디 | MAT_S·G·V, SEAM_S·G·V, TP_S_*·TP_G_*·TP_V_* 만 |
| MAT_L, SEAM_L, TP_L_01a~41a(+b·c) | 숨김 목록에 없음 → 보임 |
| 숨김 occurrence | 0 |
| 보이는 스케치 | 0 (규칙 19 원문: "저장 전에 `browser.visibility {visible:false, folder:"sketches"}`") |
| 조인트 글리프 | 숨김 목록에 들어 있음(규칙 19) |

판정: v2.10.4를 열면 L 매트와 테이프 조각이 보인다. 사용자 질문의 원인(v2.10.3에 매트·테이프 전부 숨김 저장)은 고쳐졌다.

## 3. 과제 범위 동작 검사(E-03)

### 3-1 U4 묶음 against — 모델링부 check4 결과 재확인

against: U4S_CYL, U4S_ROD, U4_CYL, U4_CYL_CLEVIS, U4_DISK, U4_PRESS(서보 HG-KR23_M02·감속기 PGX62·MPFZ 포함 — component.list로 부모가 U4_PRESS임을 확인), U4_ROD, U4_ROD_NUT, U4_WHEEL, U4_WHEEL_N. occurrences: 테이프 줄·급송 + 그 연구의 조각·SEAM.

| 연구 | 단계 | 쌍 | 겹침 | truncated | 원본 |
|---|---|---|---|---|---|
| CYCLE_L | 716 | 276 | 0 | false | check4/res_CYCLE_L.json |
| CYCLE_S | 450 | 60 | 0 | false | check4/res_CYCLE_S.json |
| CYCLE_G1 | 514 | 228 | 0 | false | check4/res_CYCLE_G1.json |
| CYCLE_G2 | 630 | 228 | 0 | false | check4/res_CYCLE_G2.json |
| CYCLE_V | 486 | 228 | 0 | false | check4/res_CYCLE_V.json |

검사 전에 `browser.visibility all 켬`이 들어가 숨긴 S·G·V 세트도 검사됐다(res의 hidden_bodies 0).

### 3-2 U4 묶음 밖 루트 M02 바디(검도가 더 본 것)

check4 against는 이름이 U4로 시작하는 occurrence만이라, 루트에 있는 M02 부품(원판 베어링 6004ZZ_M02_1·2, 볼트 CB5-16_M02_1~4·9·11~14·19~21, 센서 E32-D36P1_2M_M02 — 21바디)이 빠졌다. MCP로 REST(CYCLE_L step 0)에서 이 21바디 ↔ MAT_L·TL_*·TL_FEED·TP_L_* 전부·SEAM_L(54바디) `inspect.clearance {clearance:2}`:

| 쌍 | 최소 틈 |
|---|---|
| CB5-16_M02_19·20·21 ↔ MAT_L | 0.5 mm(매트 밑, 회전 원판 볼트 머리) |
| 6004ZZ_M02_1 ↔ MAT_L | 24 mm |
| 테이프 줄·조각·SEAM ↔ 21바디 | 2 mm 안 0쌍 |

전 단계 논리: 매트·조각·SEAM 147바디의 Z 범위는 0~12 mm(signatures), 원판 베어링·볼트는 Z ≤ −0.5 mm(U4_DISK와 함께 Z축 회전만, Z 불변), 매트 모형 조인트는 평면 X·Y·회전뿐(요구서 0-8-3)이라 Z 사이가 바뀌지 않는다. E32 센서는 그네와 함께 기울지만 X −113~−106·Z ≥ 53 근처(13° 기운 REST 위치)로 테이프 높이(≤ 12)보다 40 mm 넘게 위, 테이프 줄 TL_LOW(X 13.5~44.5)와 X로 100 mm 넘게 떨어진다.

다른 단계(25·50·75·100 %)의 같은 측정은 앱에 보냈으나 MCP 연결이 끊겨(10060, 앱은 계속 계산) 결과를 받지 못했다. 위 위치 논리로 판정하고 E-03 원문 "과제 안 검사는 바뀐 바디·주변을 관련 조인트 몇 점에서만"의 나머지 점은 라운드 끝 전체 회귀가 본다.

### 3-3 완료 판정

| 항목 | 기준 | 값 | 판정 |
|---|---|---|---|
| 전 단계 테이프 줄·조각 과제 범위 간섭 | 0, truncated false (TL_FEED↔매트 기준선 225 mm³ 제외) | U4 묶음 5연구 0·false(이번), U4 밖 U3·U5·U6 0(1회차, 테이프 형상 변화 0), 루트 M02 21바디 REST 0·위치상 불가 | 만족 |
| 굽힘 R | ≥ 3(D-167) | 3(가이드 출구), 19(G1·TOP) | 만족 |
| 풀림 차 | ≤ 1 %(D-168) | ≤ 0.25 % | 만족 |
| 비틀림 | ≤ 1 %(D-169) | 1회차 값 유지(줄 형상 변화 0) | 만족 |
| 영상 | 5연구 | CYCLE_L·S·G1·G2·V 각 GIF 1 + PNG 167장, stopped_by_contact 없음 | 만족 |

## 4. 볼트·리지드 그룹·포트·간이 형상·판금

이번 과제에서 새로 넣거나 옮긴 볼트·부품·LITE_ 간이 형상·판금 0 → M-01·M-04·M-06·E-10 검사 대상 없음. 모션 재생에서 unmoved 0, conflicts 0(CYCLE_L step 0, 2,898 occurrence).

## 5. 문제

| kind | 무엇 | 어디 | 수치 | 고치는 방법 |
|---|---|---|---|---|
| 디테일(M02R 소관, SIM-01 판정 밖) | 몸체 없는 빈 볼트·부품 컴포넌트가 남음 | CB5-16_M02R_1~4, CB5-20_M02R_1·2, CB4-12_M02R_CLV·CRK, I-020B_M02, CB5-12_M02_1·2, CB5-16_M02_10 (루트 occurrence, bodies 0) | 12개(커밋 7eef68a 메시지의 '빈 컴포넌트 21 남음'과 같은 무리) | M02R 다음 회차(v2.11.0)에서 실제 볼트 바디를 넣거나 걷어 낸 크랭크 쪽(I-020B·CRK·CLV)은 컴포넌트째 지운다. 몸체가 없으니 간섭 검사에 안 잡힌다 |

## 6. 통로·시간

- 통로 MCP: running 빈 목록 → open v2.10.4 1회 → checkpoint → 숨김 읽기 → component.list(결과 1.8 MB, `tools/out/mech_SIM-01/verify_complist_v2104.json`) → CYCLE_L step 0 + clearance(`verify_s0.json`) → 4점 묶음 batch에서 MCP 연결 끊김(앱 계산 계속) → 끝나면 restore_checkpoint·step 0.
- 4점 batch는 앱에서 약 15분 뒤 끝났으나(running 빈 목록) 끊긴 연결이라 결과를 못 받았다. 그 사이 batch 내부 체크포인트로 내 체크포인트 18이 밀려나 restore가 거부됨 → 바꾼 것은 이미 숨은 MAT_S에 대한 숨김(상태 변화 없음)과 자세뿐이라 `motion.play {study:REST, step:0}`로 원복(conflicts 0). 저장 안 함.
- 원장 `ledger.py commit --date 2026-11-11` 실행(부품 3,132, 통과 항목 84). 원장·서명의 doc는 아직 v2.10.2 — M02R 뒤 sigpatch가 안 된 상태(다음 측정부가 v2.10.4로 서명을 다시 찍어야 함).
- 걸린 시간 약 1,520 s(그중 끊긴 batch 대기 약 900 s).

## 워크플로우 메모

- 모델링부 check4 against를 '이름이 U4로 시작하는 occurrence'로 뽑으면 루트에 따로 놓인 같은 유닛 부품(원판 베어링·볼트·센서)이 빠진다. against는 원장 signatures의 unit 필드로 뽑는 편이 낫다.
- MCP `motion.play`의 결과에 positions 2,898개가 들어가 batch 결과가 1.4 MB가 된다. 짧은 확인에도 `verbose:false`가 이것을 줄이지 않는다. 여러 점 batch는 연결 시간 초과로 끊겼다.
