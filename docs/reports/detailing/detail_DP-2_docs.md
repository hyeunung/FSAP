# 디테일링 DP-2 문서 담당 — 체결 길이 · 탭 깊이 (FSAP_v2.30.8, 2026-11-28, 엔진 v4.1.2)

## 요약

- 대상: `3D_Modeling/FSAP_v2.30.8.sc`(v2.30.6 → v2.30.7 → v2.30.8, 검도 합격). CAD는 쓰지 않았다.
- BOM을 새 번호로 복사해 고쳤다: `docs/bom/FSAP_v2.30.8_purchased.csv`(130 → 132행) · `FSAP_v2.30.8_made.csv`(145행 그대로).
- 구매 BOM 볼트: CB5-16 536 → 579, CB5-12 129 → 63, CB5-20 49 → 55, SFB5-10 109 → 행을 SFB5-16 109로 바꿈, CB5-14 13 · CB5-22 4 행 더함. 형번별 모델 수 ↔ BOM 차이 0, 볼트 916 그대로, 숫자 수량 합 2,862 그대로.
- 가공 BOM: 탭 깊이 · 질량 5행(플랩 바 L1(L2 · L3) · XN · XP, 팔 블록, 롤 핀), 재질 메모 4행(보 · 받침 · 이음판 2), POM 멈춤 조임 지시 1행.
- 설계검토서 `docs/review/FSAP_v2.30.8_review.md`(변경 표 · 볼트 · 조립 지시 · 회귀 · 강도 · 못 한 것).
- 결정로그 끝에 '디테일링 DP-2 결과 (2026-11-28)' 절(DP2-1~4, DP2-M1~M8). 예외 요청 0. CHANGELOG 한 줄.
- 검증 원장 commit: 부품 3,759 · 통과 항목 106. matcheck 불일치 0.
- 커밋 · 푸시: 요구서 8-5 "설계 버전이 바뀔 때만(새 번호 .sc를 저장했을 때) 커밋하고 푸시한다" — 새 번호가 생겼으므로 했다. DP-1이 미뤄 둔 문서도 함께 넣었다(3절).
- 미완: 없음. 기록만 한 디테일은 설계검토서 5절.

## 1. 근거 규칙

- 요구서 8-2 "BOM은 `docs/bom/`, 설계검토서는 `docs/review/`, 파일 이름에 같은 버전 번호".
- E-07 "변경 표(부품·전 → 후·바꾼 이유·검증 수치)". M-01 "상대 부품의 탭 또는 너트가 실제로 있음, 물림 ≥ 1.5d". U-12 "되도록이면 다 하나로" — 이 묶음은 길이만 바꿔 지름 예외가 없다.
- E-17 · WF-130: 원장 commit으로 다음 묶음의 범위가 부풀지 않게 한다.

## 2. BOM을 고친 방법

스크립트 `tools/out/detail/DP-2/docs/mkbom.py`(입력: v2.30.6 BOM 두 파일 · `tools/out/bolts.json` · `tools/out/mach_props.json`, 결과 `bom_result.json`).

| 구매 BOM 형번 | 전 | 후 | 내용 |
|---|---|---|---|
| CB5-16 | 536 | 579 | +54(CB5-12에서) −10(→ CB5-20) −1(→ CB5-14, 수정 1회차) |
| CB5-12 | 129 | 63 | −54(→ CB5-16) −12(→ CB5-14) |
| CB5-20 | 49 | 55 | +10(CB5-16에서) −4(→ CB5-22) |
| SFB5-10 | 109 | 행 없앰 | 옛 비고는 SFB5-16 행 끝에 옮김 |
| SFB5-16 | — | 109 | 새 행. 임시 형상(D-241), 끝–홈 바닥 0.50(D-242) |
| CB5-14 | — | 13 | 새 행. 임시 형상(D-241). 플랩 판 윗면 (1092.5, −330) 자리 표시 |
| CB5-22 | — | 4 | 새 행. 임시 형상(D-241) |

- 수량은 `bolts.json`의 형번별 수를 그대로 썼다(모델 916). 대조 차이 0.
- 가공 BOM 질량은 `mach_props.json`(모델링부 측정)으로 바꿨다: 플랩 바 L 530.8 → 530.0, XN 1286.2 → 1285.3, XP 1070.9 → 1069.7, 팔 블록 140.0 → 139.3, 롤 핀 31.8 → 31.5 g.
- 보 `P_M07_BEAM`의 BOM 질량 칸(270,460)은 모델 질량(279,141)과 다르다. DP-2가 바꾼 값이 아니라 그대로 두고 비고에 모델 질량을 적었다.
- matcheck: 불일치 0. "BOM에 없는 부품" 53개는 DP-1이 같은 형상으로 합친 바디다(품번 칸이 아니라 '모델 바디' 칸에 있다 — DP-1 워크플로우 메모 2).

## 3. 커밋에 넣은 파일

- 새 버전: `3D_Modeling/FSAP_v2.30.7.sc` · `FSAP_v2.30.8.sc`, `tools/config.json`, `tools/out/signatures.json`
- 문서: `docs/bom/FSAP_v2.30.8_*.csv`, `docs/review/FSAP_v2.30.8_review.md`, `docs/decision-log.md`, `docs/waiting-list.md`, `CHANGELOG.md`, `docs/reports/detailing/`(DP-2 6개 + 점검 · 선정 6개 + DP-1)
- DP-1이 미룬 것(요구서 8-5 "버전이 바뀌지 않은 문서만의 변경은 다음 버전 커밋에 함께 넣는다"): `docs/bom/FSAP_v2.30.6_*.csv`, `docs/review/FSAP_v2.30.6_review.md`, `tools/machine.json`
- 생성기 · 해석: `tools/gen_detail_dp2.py` · `tools/gen_detail_dp2/` · `tools/gen_detail_dp2_fix1.py` · `tools/gen_detail_dp2_fix1/`, `fea/models.json`, `fea/cases/detail_*.py`, `fea/results/detail_*.json`
- 넣지 않은 것: `tools/out/` 원본(깃 제외), `fea/results/cache/`, `docs/images/r375x/`, 옛 `3D_Modeling/*.sc`, `docs/benchmark.md`, `tools/run-args.json`, `tools/out/mech_STEPSWAP/`, `docs/reports/queue_2026-11-28_3.md` — 내가 쓴 파일이 아니다(실행 지시 (차)).

## 워크플로우 메모

1. 지시문의 볼트 수 문장("CB5-12 → CB5-16 54 · CB5-14 12")은 0회차 값이다. 수정 1회차 뒤 최종은 CB5-16 53 · CB5-14 13이라 문서에는 최종 값을 썼다.
2. BOM 볼트 수량을 손으로 더하고 빼지 않고 `bolts.json` 형번별 수로 썼다. 체결 목록이 원본이면 문서 담당의 대조가 한 줄로 끝난다.
3. 지시문의 커밋 꼬리말(Co-Authored-By)이 세션 안내의 것과 달랐다. 세션 안내의 것을 썼다.

## 시간 (E-23)

- 걸린 시간 약 20분(예상 15분). CAD 호출 0 · 설계 파일 열기 0 · 브라우저 0. 통로 없음. 회귀 0분(문서 담당).
