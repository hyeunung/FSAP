# S02 모델링 — STEP 대기 마무리 교체 (모델링부)

## 요약
- 저장 `3D_Modeling/FSAP_v0.6.1.sc`(이전 v0.6.0, E-05 작은 변경 → 수 +1). `tools/config.json` doc = `../3D_Modeling/FSAP_v0.6.1.sc`.
- 구매부가 4종을 모두 못 받았다(미스미 로그인 풀림, login: false). stepcheck 결과 `CJ2B16-30SZ`·`HFS8-4080-2850`·`-680`·`-1580`이 모두 '없음'이다. 그래서 **갈래 B만** 했다.
- 바뀐 부품: `STEP대기_HFS8-4080-1580_PL`·`_PR`. Z −680~900 → **Z −672~892**(80×40×1564, 5,004,800 mm³, 13.51 kg, Aluminum). 바뀐 서명은 이 2바디뿐이다(247 중).
- 캡 4쌍은 맞닿음 0.0·겹침 0·판정 불가 0이다(전에는 판정 불가 4). 정적 전수 겹침 0. 8개 동작 연구 motion.interference는 모두 clear, truncated false.
- 조인트·행정·배치 변경 0. 새 볼트·새 가공품 0. FEA 대상 없음(E-18).
- **미완:** 형번이 정해진 STEP대기 8바디(4종)가 남았다. 로그인 문제로 못 받은 목록은 6절에 있다.
- CAD 통로: MCP 서버 안내의 Backend가 "headless in-process"(앱 창 없음)였다. 실행 규칙 (2)대로 CLI `solidcraft-cli run m1.json --in v0.6.0 --save v0.6.1`로 그렸다.

## 1. 시작 점검
- v0.6.0 `document.inspect` 결과 dirty false. CLI는 저장본을 열어 새 이름으로만 저장한다. 그래서 v0.6.0은 바뀌지 않았다(원복 대상 없음, E-08).
- 동작 상태 초기화: `motion.play {study:"대기", step:0}`를 m0·m1 맨 앞(m1은 끝)에서 했다.
- 구매부 결과와 stepcheck(`tools/out/mech_S02/mdl/stepcheck.txt`): 4종 모두 '없음'이다. `purchased-step/` 아래에 그 폴더가 없다. 따라서 갈래 A 6형재·실린더는 하지 않았다.

## 2. 그린 것 (`tools/out/mech_S02/mdl/m1.json`)
| 순서 | 명령 | 내용 |
|---|---|---|
| 1 | edit.checkpoint | |
| 2 | component.activate `HFS8-4080-1580_PL` → solid.remove `STEP대기_HFS8-4080-1580_PL` → solid.box 80×40×1564 corner (−1505,−1740,−672) 같은 이름 | |
| 3 | 같은 일을 `_PR`에 corner (1425,−1740,−672)로 | |
| 4 | material.assign Aluminum(2바디) | E-09 |
| 5 | component.metadata.set: part_number `HFS8-4080-1580`, bom_type inseparable 그대로. 설명에 "상자는 Z −672~892, 끝마다 캡 끼움 깊이 8 비움(S02-S03)"을 더함 | |
| 6 | document.metadata description "S02 mechanism: HFS8-4080-1580 wait boxes trimmed to Z-672..892 for cap seats; STEP wait kept" | |
| 7 | motion.play 대기 step 0 → --save v0.6.1 | 저장 상태 |

- 임시 형상 치수 출처(E-10): 미스미 HFS8 시리즈 4080의 단면은 40×80이고, 길이는 형번 끝 숫자 1580이다. 기존 실물 `HFS8-4080-460` STEP 외곽과 같다(T07 모델링). 끝 8은 캡 STEP `purchased-step/HFC8-4080-B` 실측이다(로컬 bbox Z −3~8 → 끼움 8·돌출 3, 선정 p6).
- 1580 위치·길이 기준은 바뀌지 않았다. 받침면 Z −680, 위 끝 Z 900은 캡 바깥면 기준이다(캡 ZM Z −683~−672, ZP Z 892~903, v0.6.0 그대로). 장착면 X ±1425 안쪽 면과 Y −1740 앞면도 그대로다.
- 지운 것: 옛 상자 2개(같은 이름으로 다시 그림). 임시 프로브 컴포넌트는 만들지 않았다. 갈래 B에서는 끝면 프로브를 쓰지 않고 캡 clearance로 확인했다.

## 3. 검증 수치 (저장본 v0.6.1, 대기 0)
| 검사 | 결과 | 파일 |
|---|---|---|
| bbox(세계) | PL X −1505~−1425 · Y −1740~−1700 · Z −672~892, PR X 1425~1505(나머지 같음). 부피 각 5,004,800 mm³ | m2_out.json, sig_diff.json |
| 캡 4쌍 clearance | PL_ZP·PL_ZM·PR_ZP·PR_ZM 거리 0.0, overlaps 0, unchecked 0, truncated false | m2_out.json [1] |
| 맞닿음 | 1580_PL/PR ↔ `STEP대기_HFS8-4080-2850_G1`·`_G4` 0.0, ↔ `P_T07_SKIRT_L`/`_R` 0.0, 겹침 0 | m2_out.json [2] |
| 정적 전수(M-08, 기준선 없음) | 바뀐 2바디 ↔ 다른 148바디(경로 이름 11개 `CJ2B16-60SZ_R*_NTJ` 6·`CJ2B10-15Z_T05_NTJ`·`SV2RL28-*_BLOCK` 4 포함). overlaps 0, unchecked 0, truncated false. 그다음 가까운 것 `HFS8-4080-460_GL/GR` 475 | m3_out.json |
| 8개 연구 motion.interference(occurrences T07:1, against MAT_X·MAT_Y·MAT_ROT·HEAD·PRESSER·NEEDLE·RING1·RING2, samples 1000, budget_s 3000) | 대기 1 / 사이클_큰매트 583 / 사이클_작은매트 298 / 사이클_홈매트 1039 / 상태_홈매트_홈 461 / 상태_홈매트_오목모서리 93 / 상태_큰매트_볼록모서리 92 / 되감기 72단계: 모두 clear, collisions 0, **truncated false**. 각 19~21 s | M_0~7_out.json, runM.log |
| 사이클_홈매트 표본 밖 단계 | 1039단계 > 표본 1000. 새 상자는 옛 상자의 부분 집합(Z 8씩 줄임)이라, 어느 단계에서도 다른 바디까지 거리가 줄 수 없다. 옛 상자는 v0.6.0 검증(`tools/out/mech_T07_verify/B_GROOVE_*`, 단계별 clearance 청크)에서 전 단계 겹침 0이었다. 그래서 단계별 청크는 다시 돌리지 않았다 | — |
| BOM flat | HFS8-4080-2850 2, -680 2, -1580 2, HFC8-4080-B 18(그대로). `CJ2B16-30SZ`는 T06 컴포넌트 안 바디(자기 컴포넌트 없음)라 flat 행이 없다. 구매품 CSV에는 1(v0.6.0과 같음). 중복 집계 없음 | m2_out.json [4] |
| 숨김·조인트 | 숨김 0, joint.list floating 0, conflicts 0(23 조인트) | m2_out.json, fin_out.json |
| 재질 | 2바디 Aluminum(형재 규칙과 같음). matcheck는 바뀐 가공품이 없어 돌리지 않음 | — |
| 저장 상태 | 다시 연 v0.6.1 dirty false, 대기 step 0, 서명 diff = 위 2바디(경로 BASE:1/·T07:1/ 4키)만, 추가·제거 0 | fin_out.json, sig_diff.json, `tools/out/signatures.json`(doc v0.6.1) |
| 조인트 자기 점검 | 바꾼 조인트 없음(대상 없음) | — |

스크린샷(사람용, 열지 않음): `tools/out/mech_S02/v061_iso.png`

## 4. 강도·임시 STEP
하중 경로가 바뀌지 않았다(고정 부품 임시 상자의 끝을 줄였을 뿐이다). E-18 "판 두께·형상·하중 경로가 바뀐 부품만 FEA"에 따라 대상이 아니다. 새로 힘을 받는 가공품은 0개라 임시 STEP도 0개다. 새 볼트 0.

## 5. 제어 순서 제약 (U-09)
바뀌지 않는다. J_T06_KNIFE −30(절단)은 겹쳐 박기 ④가 끝나고 바늘이 올라간 뒤에만 한다. 공기가 끊기면 스프링 복귀로 0(칼 올림)이 된다. T07 커튼 검출 → 정지는 그대로다(D-38).

## 6. 못 한 것 — 형번이 정해졌는데 STEP대기로 남은 것
| 형번 | 남은 바디 | 이유 | 자료대기 |
|---|---|---|---|
| `CJ2B16-30SZ` | `STEP대기_CJ2B16-30SZ`(T06), `STEP대기_CJ2B16-30SZ_ROD`(T06_KNIFE) | login: false(미스미 검색 화면 머리에 '로그인 / 회원가입'). SMC 웹카탈로그 CAD는 '등록 회원 전용 — 로그인'. 재로그인·비밀번호 입력 안 함 | D-37 |
| `HFS8-4080-2850` | `STEP대기_HFS8-4080-2850_G1`·`_G4` | login: false. 미스미 전용 형재라 대체 사이트 없음 | D-41 |
| `HFS8-4080-680` | `STEP대기_HFS8-4080-680_SL`·`_SR` | login: false | D-41 |
| `HFS8-4080-1580` | `STEP대기_HFS8-4080-1580_PL`·`_PR`(Z −672~892로 줄임) | login: false | D-41 |

이 때문에 함께 남은 것: T06-D01(임시 로드가 −30에서 튜브 안 길이 없음)은 실물 30SZ를 받아야 확인한다. 30SZ ↔ LHFR16 2.85는 임시값 그대로다. 갈래 A 확인(끝면 프로브, S02-S04 캡 판정, J_T06_KNIFE sweep)은 받은 뒤 선정 5절 행렬대로 한다.
형번 미정인 재봉 헤드 4바디(D-10)는 대상이 아니다.

## 7. 문서
- BOM `docs/bom/FSAP_v0.6.1_made.csv`(v0.6.0과 같음), `_purchased.csv`(30SZ·2850·680·1580 비고에 S02 추가)
- 설계검토서 `docs/review/FSAP_v0.6.1_review.md`, CHANGELOG, 결정로그 S02-M01~M03, 자료대기 D-37·D-41 '쓰는 곳'

## 워크플로우 메모
- MCP 서버가 headless로 떠서(앱 창이 없음) 사용자가 실시간으로 볼 수 없었다. 규칙 (2)의 예외 조항대로 CLI로 했다.
- motion.interference(T07:1 ↔ 8)는 v0.6.1에서 연구마다 약 20 s 걸렸다. 사이클_홈매트 1039단계는 samples 상한 1000을 넘는다. 형상이 줄기만 한 변경에서는 부분 집합 논리로 청크 검사를 대신했다.
