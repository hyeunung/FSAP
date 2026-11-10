# PNEU-01R 모델링 — 공압 관–구멍 벽 겹침 2쌍 (2026-11-10)

요약
- 저장: `3D_Modeling/FSAP_v2.8.11.sc`(기준 v2.8.10, 마지막 자리 +1 — 생기거나 없어진 컴포넌트 없음). `tools/config.json` doc 갱신.
- 바뀐 부품 2: P_M08_TUBE_COMB_U5_2 구멍 (−1235.5, 190, 661) 축 −X, P_M08_RISER_COMB_1 구멍 (1049.75, 53) 축 Z — 둘 다 r 3.25 → 3.5(Ø7.0, 높이 그대로).
- 부피 변화: −84.81 mm³(계산 84.8) / −42.41 mm³(계산 42.4) — 구멍이 지시 자리에 들어감.
- 겹침: 두 쌍 0. 최소 거리 U5_A ↔ COMB_U5_2 0.370 mm, U4_B ↔ RISER_COMB_1 0.109 mm(면 대 면 measure).
- 이웃 구멍 살 7.67(중심 간격 14.42) / 7.75(14.5) ≥ 1. 관 경로 그대로라 굽힘 R 최소 16 ≥ 15(TU0604) 그대로.
- 조인트·행정·기계 정의 변화 없음. 새 구매품·볼트 없음. 미완 없음.
- 통로 MCP(앱 --control 27878, running 빈 목록). 열기 약 600 s.

## 1. 한 일
지시서(선정 '회귀 동작 문제', 검도 mech_PNEU-01_verify2.md 4절 #1·#2, 결정로그 PNEU-01-R1·R2)대로 같은 base·축·높이에 반지름 3.5 원기둥을 cut 했다. 다른 구멍·관 경로는 바꾸지 않았다.

| 부품 | 명령 | base | 축 | h | 전 부피 | 후 부피 | 차 |
|---|---|---|---|---|---|---|---|
| P_M08_TUBE_COMB_U5_2(A5052) | solid.cylinder cut r 3.5 (Cylinder786) | (−1235.5, 190, 661) | −X | 19 | 25,346.38 | 25,261.57 | −84.81 |
| P_M08_RISER_COMB_1(A5052) | solid.cylinder cut r 3.5 (Cylinder787) | (1049.75, 53, 394.5) | +Z | 11 | 90,853.66 | 90,811.25 | −42.41 |

bbox는 둘 다 그대로(U5_2 X −1253~−1237·Y 158~197·Z 650.1~697, RISER X 1040~1112·Y −15~120·Z 396~432). 재질 A5052 그대로. 구멍 지름 확인: RISER 구멍 면 `measure` 지름 7.000, 중심 (1049.75, 53).

## 2. 완료 판정
| 항목 | 기준 | 결과 |
|---|---|---|
| 두 쌍 겹침 | 0 | 0(`inspect.clearance` min_volume 1e-7, tolerance 1e-9) |
| 벽 두께 ① | ≥ 1 | 이웃 (182, 673): 14.42 − 3.5 − 3.25 = 7.67. 상자 윗면 Y 197까지 3.5, 아랫면 Z 650.1까지 7.4 |
| 벽 두께 ② | ≥ 1 | 이웃 (1060.25, 63): 14.5 − 6.75 = 7.75. 판 끝 X 1040까지 6.25 |
| 관 굽힘 R | ≥ 최소 굽힘 반경 | 관을 바꾸지 않음 — TU0604 최소 R 16 ≥ 15(검도 verify2 그대로) |
| 과제 범위 간섭 | 0 | 두 부품 ↔ 주변 바디(bbox ±5) 20쌍 겹침 0(`tools/out/mech_PNEU-01R/check_standby.json`, 주변 목록 `near.json`) |

- 주변에서 거리 0(맞닿음, 겹침 부피 0): COMB_U5_2 ↔ CB5-16_M08_NZ_COMB:11(볼트 자리면), ↔ P_M07_BEAM 0.1; RISER_COMB_1 ↔ P_M07_BEAM·CB5-16_M08_PY:32·33(붙임면). 원래 붙어 있는 자리이고 바뀌지 않았다.
- RISER ↔ U4_B는 `inspect.clearance` near에 0.0으로 나왔으나 겹침 부피는 없고, 면 대 면 `measure`(관 면 ↔ 구멍 벽, 관 면 ↔ 판 윗면)로 0.109 mm다. 0.0은 판정 근사로 보고 겹침 0으로 적는다. 틈 0.109는 작아서 관이 판 모서리에 닿기 쉽다 — 디테일 후보(꼭짓점 Z 430 → 435 또는 구멍 모따기)로 남긴다.
- 관절 점 검사: 바뀐 두 부품과 맞닿는 관 구간은 모두 U8 공압 고정부(보에 볼트 고정)이고 움직이는 조인트를 따라가지 않는다. 그래서 0·25·50·75·100 % 점이 같은 형상이라 대기 자세(REST step 0) 한 번으로 갈음했다.

## 3. 조인트·리지드·숨김
- 조인트·행정·유닛 변화 없음 → `tools/machine.json`, 동작 연구 그대로. 조인트 자기 점검은 바꾼 조인트가 없어 하지 않았다.
- 새 부품 없음 → 리지드 그룹 변화 없음.
- 저장 전 `motion.play REST 0`(conflicts 0, moved false), `browser.visibility` joints 410·sketches 258 숨김(실행 규칙 19).
- 볼트 검사: 바꾼 볼트 없음.

## 4. 저장·서명
- 문서 설명 `PNEU-01R mechanism: tube hole r3.25->3.5 in COMB_U5_2 (-1235.5,190,661) and RISER_COMB_1 (1049.75,53)`, 이름 FSAP_v2.8.11(저장 경로).
- 저장 확인: CLI `eval`로 저장본의 바디 수·두 부품 부피를 다시 쟀다(`tools/out/mech_PNEU-01R/savecheck_out.json`, 결과는 5절).
- 서명: `ledger.py sigpatch --parts tools/out/mech_PNEU-01R/parts_changed.json`(지운 것 없음).
- 임시 STEP: 새로 힘을 받는 가공품 없음(구멍 지름만, 관 지지 하중 경로 그대로) → 내보내지 않음.
- 다시 실행 재료: `tools/out/mech_PNEU-01R/edit.json`, `edit_meta.json`.
- 스크린샷: `tools/out/mech_PNEU-01R/shot_iso.png`(CLI snapshot, 열어 보지 않음).

## 5. 저장 확인 결과
- CLI `eval` 저장본(FSAP_v2.8.11.sc): 바디 2,969(작업 전과 같음), 없어진 바디 0, 작업 전 bbox와 0.001 넘게 달라진 바디 0. 두 부품 부피 25,261.57·90,811.25(앱 측정과 같음). 앱 `document.revision` 7, 저장 뒤 편집 없음.
- CLI 한 번 8분 2초(열기 포함, 2,969바디 measure). 이 시간은 모델 무게 탓이다.

## 워크플로우 메모
- 앱 `open` 3,030 피처 저장본이 약 600 s(LITE 뒤 CLI 397 s보다 김). 모델 무게 상한 240 s 초과는 그대로.
- `batch` 안 `inspect.measure {body}`는 body를 무시하고 모든 바디(2,969)를 돌려줘 결과가 6 MB가 됐다. 한 바디는 `measure` 도구로 따로 부른다.
- `inspect.clearance`에 `against` 없이 `bodies`만 주면 bodies 사이만 본다(pairs_checked 0).
