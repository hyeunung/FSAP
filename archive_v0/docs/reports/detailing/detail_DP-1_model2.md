# 디테일링 DP-1 모델링 보고서 — 수정 2회차

- 바뀐 부품: `STEP대기_MS3-8_T06`(맞춤핀)만 — 미스미 외형도대로 한끝 R=D(R3)·다른 끝 15° ℓ1 1.0, 재질 Steel → SUJ2(7.83). 서명 비교 바뀜 1·새 0·빠짐 0(`tools/out/detail/DP-1/r2/sig_compare.json`).
- 저장: `3D_Modeling/FSAP_v0.6.5.sc`(CLI `run --save`, MCP 서버 Backend headless). `tools/config.json` doc → v0.6.5.
- 핵심 수치: 핀 53.97 mm³ · 0.42 g, bbox 그대로 (75.5~78.5, −9~−6, 54~62), 겹침 0. 핀 전단 SF 2.3(허용 600 MPa, SUJ2 58HRC~로 보수). 팔 ↔ 헤드 1.0, 팔 ↔ 브래킷 14.0.
- 칼 전 행정 `joint.sweep`: 잎 컴포넌트로 나눠 헤드·T05·테이프·T06 잎 14개 모두 멈춤 없음(지난 미완 2 해결, DL-D31).
- MS3-8 재질·경도·끝 모양: 미스미 상품 페이지 외형도로 확인 — SUJ2, 58HRC~(지난 미완 3 해결, DL-D30, D-43).
- 미완: STEP 대기 7종 그대로 — 미스미 머리에 '로그인 / 회원가입'(**login: false**, 2026-10-31 확인), 재로그인 안 함.

## 1. 작업 전 확인

| 항목 | 결과 |
|---|---|
| 문서 | `3D_Modeling/FSAP_v0.6.4.sc`(config doc). 첫 회차 아님 → 원복 대상 없음. CLI로 열어 고침(MCP 서버 안내 `Backend: headless` → 지시 (2) 예외 조항대로 CLI, 사용자 앱 화면에는 안 보임) |
| 동작 상태 | 스크립트 처음·끝 `motion.play 대기 0` (J_T06_KNIFE 0, J_PRESSER 10, J_MAT_Y −700) |
| 미스미 | 크롬 새 탭으로 상품 페이지 열람. 머리 '로그인 / 회원가입' → **login: false**. STEP 받지 않음(요구서 3-2). 상품 페이지(로그인 없이 보임)에서 MS3-8 외형도·재질만 확인. 연 탭은 닫음 |
| stepcheck | 지시서 표 그대로(`CB4-16`·`LBNR4`·`LBNR5`·`PSFJT16-100-M5`·`CJ2B16-30SZ` 없음). `MS3-8`도 `purchased-step`에 없음 |

## 2. 지난 검증 문제마다 (원인 → 한 것)

| # | 문제 | 원인 | 한 것 | 결과 |
|---|---|---|---|---|
| 1 | STEP 대기 7종(MS3-8, CJ2B16-30SZ, PSFJT16-100-M5, CB4-16, LBNR4, LBNR5, NTJ-015C) | 미스미 로그인 풀림 | 다시 확인 — 여전히 풀림(login: false). 재로그인·비밀번호 입력은 금지라 못 받음. MS3-8은 받을 수 있는 정보(외형도)로 임시 형상을 카탈로그 모양으로 바로잡음 | **미완**(로그인 필요) |
| 2 | `joint.sweep J_T06_KNIFE`에 HEAD·T06을 넣으면 collision budget 초과 | `HEAD:1`·`T06:1`은 움직이는 `T06_KNIFE:1`을 자손으로 품는다 → 칼 유닛이 자기 자신·끼움 맞닿음과 비교됨. 그리고 축 ↔ `LHFR16_T06`은 전 행정 미끄럼 끼움(맞닿음 유지) | against를 잎 컴포넌트로 나눔(아래 3절). LHFR16은 축을 뺀 칼 유닛 잎 8개로 sweep. 컴포넌트 몸에 붙은 `P_T06_BRACKET`·축 ↔ LHFR16은 `joint.drive` 5위치 정확 `inspect.clearance` | **해결** — 멈춤 0 |
| 3 | MS3-8 재질·경도(SF 2.3의 600 MPa 가정)·끝 모양 미확인 | 카탈로그 미확인 | 미스미 상품 페이지 외형도: **재질 SUJ2, 경도 58HRC~**(FAQ: 총 담금질, 표면처리 없음, 배럴 연마), 한끝 R=D, 다른 끝 15° ℓ1 1.0(D3). 모델을 그 모양·재질로 다시 그림 | **해결** |

## 3. 바꾼 것 (전 → 후 · 이유, E-07)

| 부품 | 전(v0.6.4) | 후(v0.6.5) | 이유 |
|---|---|---|---|
| `STEP대기_MS3-8_T06` | `Cylinder180` Ø3×8 + `Chamfer5`·`Chamfer6` C0.3, Steel, 55.75 mm³ | `MS3_LOW` Ø3 Z54~57 ∩ `MS3_CROWN_R3` 구 R3 중심 Z57(아래 끝 R=D, 높이 0.40) + `MS3_MID` Ø3 Z57~61 + `MS3_TAPER15` 원뿔 Z61~62 Ø3 → Ø2.464(15°, ℓ1 1.0). 재질 SUJ2(material.create 7.83). 53.97 mm³, 0.42 g, 면 4(구·원통·원뿔·평면) | DL-D30. 15° 끝을 넣는 쪽(축 막힌 구멍)에, R 끝을 팔 밑면 쪽에. 자리·bbox·형번·bom_type 그대로 |

스크립트 `tools/out/detail/DP-1/r2/build.json`(13단계). 다른 부품은 건드리지 않음(서명 비교로 확인).

## 4. 칼 전 행정 joint.sweep (J_T06_KNIFE 0 → −30, step 0.5, report_gaps)

| against | 멈춤 | 최소 틈(mm) · 그때 값 | 결과 파일 |
|---|---|---|---|
| `STEP대기_SEWHEAD:1` | 없음 | 1.0 · 0(대기) | `r2/sw_head_out.json` |
| `T05:1` | 없음 | 559.6 | `r2/swl_00_out.json` |
| `T05_TAPE:1` | 없음 | 54.8 · −15 | `swl_01` |
| `CB5-12_T06_BR1:1`·`BR2:1` | 없음 | 19.88 · 19.93 | `swl_03`·`04` |
| `STEP대기_CJ2B16-30SZ:1` | 없음 | 0.119 · −30(로드 Ø5 ↔ 구멍 Ø5.4 반경 틈 0.2의 메시값, 허용 오차 0.147) | `swl_05` |
| `STEP대기_CB4-16_T06_1~4:1` | 없음 | 7.52~7.54 | `swl_06~09` |
| `STEP대기_LBNR4_T06_1~4:1` | 없음 | 7.15~7.19 | `swl_10~13` |
| `LHFR16_T06:1` ← 칼 유닛 잎 8(축 뺀: CB5-12 ×3, LBNR5 ×2, NTJ, 로드, 핀) | 없음 | 9.50 · −4.5(로드) | `swl_lh_out.json` |
| `LHFR16_T06:1` ← 칼 유닛 전체 | 도구 거부(budget) | — 축 ↔ 부시 끼움 맞닿음이 전 행정 이어짐 | `swl_02_err.txt` |

정확 틈(`r2/brk_out.json`, `joint.drive` 0·−7.5·−15·−22.5·−30): `P_T06_BRACKET` ↔ 축 1.0, ↔ 로드 2.75~4.85, ↔ CB5-12_SH 9.55~37.6, 겹침 0. `LHFR16_T06` ↔ 축 0.0(끼움, M-08), ↔ 로드 9.5~12.4, 겹침 0. PRESSER·NEEDLE은 지난 회차 sweep(`r1/mi/M_SWN2`) 멈춤 없음.

## 5. 수치 판정 (완료 판정)

| 판정 | 기준 | 결과 | 근거 |
|---|---|---|---|
| 팔 오조작 T / 칼 막힘 / 운전 SF | ≥ 2.0 / 2.0 / 3.0 | 2.29 / 4.64 / 10.23 | 팔 서명 그대로 — v0.6.2 손계산 |
| 축–팔 핀 전단 SF | ≥ 2.0 | **2.3** | Ø3 단면 1면(Z 57, 7.07 mm²), 허용 600 MPa — SUJ2 58HRC~ 확인으로 보수(D-43 해결). 끝 모양이 바뀌어도 전단면 Z 57은 곧은 Ø3 구간(Z 54.40~61) 안 |
| 칼–침판 맞날 틈 | ≥ 0.04 | 0.053 | 형상 그대로 |
| 대기 팔 ↔ 헤드 | ≥ 1.0 | **1.0** | `inspect.clearance` (`r2/ck_out.json`) |
| 팔 ↔ 브래킷 밑면 | ≥ 14 | **14.0** | 같음 |
| 로드 ↔ 실린더 겹침 | 0 | **0** | `inspect.interference` 11바디 count 0 |
| M-01 15자리 | 프로브 0, 물림, 2P, 빈 구멍 0 | 볼트 그대로(v0.6.2 4절). 빈 볼트 구멍 0, 핀 구멍 채움 | 핀 ↔ CB5-12_SH 0.092(R 끝, 전 0.0 면 맞닿음) — 머리가 핀 빠짐 막음 그대로 |
| 브래킷 M-04 | 8.32 | 서명 같음 | — |
| 노루발 SF / 얇은 살 | ≥ 2 / ≥ 1.0 | 약 5.2 / 1.018 | 서명 같음 |
| 재질 Default | 0 | 0 | 핀 SUJ2 |
| 숨김 | 0 | 0 | `document.inspect` |
| joint.list | floating 0 | floating 0, conflicts 0, errors 0 | `r2/ck_out.json` |
| E-03 | 새 겹침 0, truncated false | 6절 | — |

## 6. 동작·간섭 검사 (E-03)

`motion.interference`(occurrences `T06:1`·`T06_KNIFE:1`·`PRESSER:1` ↔ top 22, budget_s 3000) — v0.6.4와 같은 스크립트(`r2/mi/M_*.json`), 비교 `r2/mi/an.py` → `an_out.txt`.

| 연구 | 표본 | truncated | 쌍(v0.6.5 / v0.6.4) | 새 쌍·깊이 바뀜 |
|---|---|---|---|---|
| 대기 | 2 | false | 2 / 2 | 0 |
| 사이클_큰매트 | 584 | false | 4 / 4 | 0 |
| 사이클_작은매트 | 299 | false | 7 / 7 | 0 |
| 홈매트_분할_A (0~520) | 521 | false | 7 / 7 | 0 |
| 홈매트_분할_B (520~1039) | 520 | false | 7 / 7 | 0 |
| 상태_홈매트_홈 | 462 | false | 5 / 5 | 0 |
| 상태_홈매트_오목모서리 | 94 | false | 4 / 4 | 0 |
| 상태_큰매트_볼록모서리 | 93 | false | 2 / 2 | 0 |
| 되감기 | 73 | false | 2 / 2 | 0 |

- 남은 쌍은 전과 같다: `HEAD ↔ T06` 1.015(브래킷 볼트 나사 물림, M-08), `HEAD ↔ PRESSER` 0.347(전부터), 노루발·칼 ↔ 매트 모형(작업 대상 누름·절단 모형 중첩).

## 7. 저장·서명

- `solidcraft-cli run tools/out/detail/DP-1/r2/build.json --in 3D_Modeling/FSAP_v0.6.4.sc --save 3D_Modeling/FSAP_v0.6.5.sc`(rc 0). 다시 열어 측정·sweep 모두 오류 0, 대기 위치 그대로(`motion.play 대기 0` 값 J_MAT_Y −700 등).
- 서명: `tools/out/signatures.json` = `r2/signatures_v065.json`(267 경로), 비교 `r2/sig_compare.json`(v0.6.4 대비 바뀜 `STEP대기_MS3-8_T06` 하나).
- 임시 STEP(해석용, E-06 예외): `tools/out/detail/DP-1/stepout/STEP대기_MS3-8_T06_v065.step`. 팔·노루발은 형상 그대로라 `stepout/P_T06_ARM.step`·`P_T02_FOOT_v064.step` 그대로.
- 스크린샷 `tools/out/detail/DP-1/snap/v065_iso.png`(저장만, 열지 않음).
- BOM `docs/bom/FSAP_v0.6.5_made.csv`(v0.6.4와 같음)·`_purchased.csv`(MS3-8 행). 설계검토서 `docs/review/FSAP_v0.6.5_review.md`. 결정로그 DL-D30·D31, 자료대기 D-43.

## 8. 쓴 임시값 (자료대기)

| 값 | 쓴 곳 | 자료대기 |
|---|---|---|
| MS3-8 외형(카탈로그 외형도 치수, STEP 아님) | `STEP대기_MS3-8_T06` | D-43 |
| 핀 전단 허용 600 MPa(SUJ2 58HRC~에 대해 보수) | 손계산 SF 2.3 | D-43 |
| 그 밖 v0.6.2 8절 그대로 | — | D-10 · D-37 |

## 9. 못 한 것 (E-07)

1. STEP 대기 7종: `MS3-8`, `CJ2B16-30SZ`, `PSFJT16-100-M5`, `CB4-16`, `LBNR4`, `LBNR5`, `NTJ-015C`(60SZ 실물 복사 형상). 미스미 로그인 풀림(login: false) — 재로그인·비밀번호 입력은 하지 않는다(요구서 3-2, 실행 규칙 (11)·(12)). 사용자가 미스미에 다시 로그인하면 구매부가 받아 바꾼다.

## 10. 구동 과제 후보

- 없음(조인트·행정·배치 변경 0).

## 워크플로우 메모

- `joint.sweep`의 against(또는 occurrences)에 움직이는 컴포넌트의 조상(`HEAD:1`, `T06:1`)을 넣으면 자기 자신을 품어 "contact sweep collision budget" 오류가 난다. 잎 컴포넌트로 나눠 넣으면 돈다. 전 행정 맞닿음(축 ↔ 부시 끼움)이 있는 쌍도 같은 오류 — 그 쌍은 sweep에서 빼고 정확 틈으로 본다.
- 컴포넌트 몸에 직접 붙은 바디(자식 컴포넌트가 있는 컴포넌트의 바디, 예 `T06:1`의 `P_T06_BRACKET`)는 occurrence로 따로 고를 수 없다 → `joint.drive` + `inspect.clearance`.
- 미스미 상품 페이지는 로그인 없이 외형도·재질을 보여준다. STEP이 없어도 E-10 임시 형상을 카탈로그 모양으로 그릴 수 있다.
