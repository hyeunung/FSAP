# STEP 대기 재시도 — 2026-11-09 (FSAP_v2.6.8)

요약
- 대상: FSAP_v2.6.8 구매품 BOM(docs/bom/FSAP_v2.6.8_purchased.csv)의 STEP대기_ 행. CAD는 열지 않음(BOM 목록으로 충분, 파일 열기 0).
- swap 없음. IR1000-01BG는 v2.6.8에서 이미 교체됨.
- stepcheck: F39-LSGF·MHMF022L1U2M·MHMF042L1U2M·VRXF-PB-60-10·KC-40340·2400.05.12PZ 모두 저장소에 없음.
- 미스미에서 받을 수 있는 대기 형번이 없어 브라우저를 쓰지 않음 → login '확인 못 함'(최종 보고 담당이 확인).
- 형번 미정(BALL_D25, LEVELER_M8, NUT/WASHER/SETSCREW/INSERT 소품, FH4-M4-15, S-M5-2, F3SG-BRKT)과 재봉 헤드 867-392342(D-10 사용자 자료)는 뺌.

| 형번 | 상태 | 이유 |
|---|---|---|
| F39-LSGF | 대기 | not_found — 미스미 CAD 없음, 옴론 CAD 확인 필요 |
| MHMF022L1U2M | 대기 | login — 파나소닉 CADENAS 가입 필요(규칙 11 금지), MSMF 대체 사용자 결정 대기 |
| VRXF-PB-60-10 | 대기 | not_found — 니덱 CAD 확인 필요 |
| KC-40340 | 대기 | not_found — 제조사 미확인(D-121) |
| 2400.05.12PZ | 대기 | not_found — igus 형번 임시(D-115) |

근거: E-10 "못 받으면 다시 시도하지 않고 waiting에 이유와 함께", 실행 규칙 10 "로그인이 풀렸거나 STEP을 못 받으면 기다리지 않는다".
