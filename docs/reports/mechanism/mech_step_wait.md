# STEP 대기 재시도 (2026-11-06, 엔진 v3.9.3 재시작)

요약
- 대상: 최신 FSAP_v2.6.5 BOM(docs/bom/FSAP_v2.6.5_purchased.csv)의 STEP대기_ 행. 설계 파일은 열지 않음(BOM이 같은 목록, E-20·E-21 이전 결과 재사용).
- 바꿀 것(swap): 없음. purchased-step·PartsLibrary/index.csv 모두 해당 형번 없음(stepcheck).
- 다시 받지 않음: 같은 날 앞 실행에서 미스미 미게재·제조사 사이트 가입 필요로 확인됨(E-10 "못 받으면 다시 시도하지 않고").
- 미스미 로그인: 이번 부서는 브라우저를 열지 않아 확인 못 함(최종 보고 담당이 확인, 규칙 12).

| 형번 | 상태 | 이유 |
|---|---|---|
| F39-LSGF | 대기 | not_found, 옴론 CAD |
| IR1000-01BG | 대기 | not_found, SMC CAD |
| MHMF022L1U2M | 대기 | 파나소닉 CADENAS 가입 필요, MSMF 대체 사용자 결정 |
| VRXF-PB-60-10 | 대기 | not_found, 니덱 CAD |
| KC-40340 | 대기 | 제조사 미확인 D-121 |
| 2400.05.12PZ | 대기 | 형번 임시 D-115 |

형번 미정이라 뺀 것: 867-392342(D-10), BALL-D25.4, LEVELER-M8 2종, S-M5-2, INSERT_M3, SETSCREW·NUT·WASHER(D-127).
MHMF042L1U2M: v2.6.5 BOM에 STEP대기 행 없음(stepcheck도 없음).

## 재확인 (2026-11-06, 재호출)
- config doc = FSAP_v2.6.5.sc, BOM 같음. stepcheck 7형번 모두 없음, PartsLibrary/index.csv 해당 0줄. swap 없음, 같은 날 못 받은 것이라 다시 받지 않음(E-10). 설계 파일 열지 않음(E-21).

## 재확인 (2026-11-08, 엔진 v3.9.3)
- config doc = FSAP_v2.6.5.sc 그대로(REG-02 전). stepcheck 6형번 모두 없음, PartsLibrary 0줄. swap 없음.
- 미스미 재로그인됐으나 6형번은 미스미 미게재·제조사 가입 필요·형번 미정이라 로그인과 무관 — 다시 받지 않음(E-10). 설계 파일 열지 않음(E-21), CAD 호출 0.
