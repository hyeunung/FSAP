# STEP 대기 재시도 (2026-11-28, v2.30.5)

요약
- swap: 없음. waiting 19형번(2026-11-27과 같음), lite: F3SG-4RA0800-14(실행 지시 (h)로 STEPLITE는 넣지 않음).
- 모델 v2.30.3 → v2.30.5(RX-DC-C1)는 STEP대기 부품을 넣거나 빼지 않았다: BOM v2.30.5 '모델 바디' 칸 STEP대기_ 56행이 v2.30.3과 같고, 저장본 이름 비교도 더함 0·뺌 0. 그래서 앞 결과(tools/out/step_wait.json)를 이어 썼다(E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만").
- stepcheck 19형번 다시 확인: 모두 '없음'(PartsLibrary에도 같은 형번 없음). HFS8-80160-1090은 이미 실물(살아 있는 STEP대기_ 바디 0)이라 swap 아님.
- 미스미 로그인: 확인 못 함 — Claude in Chrome 연결된 브라우저 0(list_connected_browsers). 받지 않았고 기다리지 않음(규칙 10·실행 지시 (마)).
- CAD: 열지 않음(저장본 열기 13~27분, 목록이 바뀌지 않아 BOM·저장본 이름으로 판정). 원복할 것 없음(E-08).
- 형번 미정(뺌): 앞 실행과 같음(BALL_D25, BRSEAL_B25·B40, F39-LSGF, LEDBAR_L100, LEVELER_M8, NUT-M8, TPH-01, WASHER_M5S, MC01-5_ARM 등).

waiting: AN110-01, AS1211F-M5-06, AS2201F-01-06S, CB3-40, CB3-8, CDQ2A25-20DMZ, ISE20-N-M-C6L-L, KQ2H08-01AS, KQ2T08-00A, M-5P, MC01-5, RORLM20-6-L200, SFJ6-213, SS5Y3-20-09, SY30M-38-1A-C6, VP342-5DZ1-01A, MR-J3ENCBL5M-A2-H, MR-PWS1CBL5M-A2-H, PSCS12-10 — 모두 blocked(브라우저 미연결), E-10 "STEP을 못 받으면 임시 형상으로 진행" 대로 임시 형상 유지.

## 워크플로우 메모
- 브라우저 미연결이 2026-11-24·27·28 세 실행째 이어져 waiting 19형번이 그대로다. 사용자가 Chrome 확장을 연결해야 풀린다.

# STEP 대기 재시도 (2026-11-24 15시 재호출, v2.29.3)

- 앞 결과(tools/out/step_wait.json, 같은 날·같은 모델 v2.29.3)를 그대로 다시 씀(E-21). stepcheck 재확인: HFS8-80160-1090 있음(swap), AN110-01·CB3-40 없음.
- 로그인 확인 못 함(Chrome 미연결), CAD 열지 않음.

# STEP 대기 재시도 (2026-11-24 재실행, v2.28.1 기준)

요약
- swap: HFS8-80160-1090 (purchased-step에 STEP 있음, 모델에 STEP대기_HFS8-80160-1090_M07_NX·PX 남음)
- 미스미 로그인: 확인 못 함 — Claude in Chrome 미연결(재실행 때도 같음). 받지 않음, 재시도 안 함
- 대기 17종은 같은 날 앞 실행(v2.25.2)과 같음. v2.28.1에서 새로 보인 이름(CDQ2YA20-25DMZ, CDQSYB20-25DCM, MHMF022L1U2M, VRXF-PB-60-10, PSFJ12-200, SCXW46-14-15 등)은 document.json 문자열 검색이라 이력에 남은 이름인지 실제 바디인지 CAD로 가리지 않았다 — 다음 측정에서 목록 확인
- lite: F3SG-4RA0800-14 (실행 지시 (h)로 넣지 않음)
- CAD: 열지 않음 — 원복할 것 없음

## 워크플로우 메모
- 저장본 zip document.json 문자열 검색은 지운 바디 이름까지 잡는다. 바디 목록만 뽑는 도구가 필요하다(엔진 후보로 회고에 넘김).

# STEP 대기 재시도 (2026-11-24, v2.25.2 기준)

요약
- swap: HFS8-80160-1090 (purchased-step·PartsLibrary에 STEP 있음, 모델에 STEP대기_ 2개 남음)
- 미스미 로그인: 확인 못 함 — Claude in Chrome 미연결. 받지 않음
- 대기 17종: AN110-01, AS1211F-M5-06, AS2201F-01-06S, CB3-40, CB3-8, CDQ2A25-20DMZ, ISE20-N-M-C6L-L, KQ2H08-01AS, KQ2R06-08A, KQ2T08-00A, M-5P, MC01-5, RORLM20-6-L200, SFJ6-213, SS5Y3-20-09, SY30M-38-1A-C6, VP342-5DZ1-01A
- 형번 미정(뺌): BALL_D25, BRSEAL_B25·B40, F39-LSGF, LEDBAR_L100, LEVELER_M8, NUT-M8, TPH-01, WASHER_M5S, MC01-5_ARM
- lite: F3SG-4RA0800-14 (11-22 heavy 결과 재사용, 실행 지시 (h)로 넣지 않음)
- CAD: 열지 않음(저장본 zip의 document.json 이름 목록) — 원복할 것 없음

## 재실행 2026-11-24 (v2.29.3, RX-19·RX-DC-02 뒤)

요약: 같은 날 11:12 결과를 이어 썼다(E-21). CAD는 열지 않았다(RX-19·RX-DC-02는 STEP대기 부품을 새로 넣거나 빼지 않음). stepcheck로 18형번을 다시 확인 — 결과 그대로.
- swap: HFS8-80160-1090(저장소에 STEP 있음, 아직 임시 형상)
- waiting 17형번: 저장소·PartsLibrary 없음. 브라우저 받기는 이번에도 하지 않음(오전에 Claude in Chrome 확장 미연결 — 같은 과제 안 재시도 금지, 규칙 10). PartsLibrary에 같은 계열(SS5Y3-20-06, KQ2L…)만 있고 같은 형번은 없음.
- lite: F3SG-4RA0800-14
- 미스미 로그인: 확인 못 함

## 재호출 2026-11-24 (v2.29.3, 같은 모델)

요약: 모델이 앞 실행과 같은 v2.29.3이라 tools/out/step_wait.json을 그대로 이어 썼다(E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만"). stepcheck 재확인(HFS8-80160-1090 있음 → swap, AN110-01·SY30M-38-1A-C6 없음). CAD·브라우저 열지 않음, 원복할 것 없음. 로그인 확인 못 함.

## 재호출 2026-11-24 (v2.30.2, RX-DC-03 뒤)

요약: v2.29.3 결과를 이어 썼다(E-21). 저장본 document.json 이름 차이만 봤다(CAD·브라우저 열지 않음, 원복할 것 없음).
- v2.30.x에서 새로 생긴 STEP대기_: MR-J3ENCBL5M-A2-H·MR-PWS1CBL5M-A2-H(미쓰비시 서보 케이블, 형번 정해짐 → stepcheck 없음 → waiting), HG-KR23_CONN/LEAD(모터 리드·커넥터 임시 형상, 별도 형번 없음 → 뺌. 모터 HG-KR23 본체 STEP은 저장소에 있음), PTFE_TUBE_8x7(형번 미정 → 뺌)
- swap: HFS8-80160-1090(그대로)
- waiting 19형번(앞 17 + 케이블 2), lite: F3SG-4RA0800-14(실행 지시 (h)로 넣지 않음)
- 미스미 로그인: 확인 못 함

## 재호출 2026-11-27 (v2.30.3, RX-DC-C1 이어 하기 전)

요약
- swap: **없음.** 앞 결과의 HFS8-80160-1090은 뺐다 — 기둥 2개는 v2.5.6 STEPSWAP 때 이미 실물 STEP(HFS8-80160-1090_M07:1·:2)이다(BOM v2.30.3 58행, mech_STEPSWAP_model.md r10 "살아 있는 바디 가운데 STEP대기_HFS8-80160-1090_*은 0개"). 앞 실행들이 저장본 document.json 문자열 검색으로 이력에 남은 옛 이름을 잡아 r5~r10 여섯 번 헛 과제를 냈다.
- waiting 19형번: 앞 18(KQ2R06-08A는 BOM v2.30.3에 없어 뺀 상태 그대로) + PSCS12-10(고정 칼라 Ø12 ×2, 형번 정해짐·stepcheck 없음 — 앞 실행에서 빠져 있었다). 모두 저장소·PartsLibrary 없음.
- 형번 미정·임시라 뺌: 867 헤드·바인더(D-10·D-211), BALL_D25, LEVELER_M8, INSERT_M3, SETSCREW/NUT/WASHER, F39-LSGF, FH4-M4-15, SCXW46-14-15(아랫축 지름 D-10), PSCS16, SPRING, TPH-01, CDQSYB20-25DCM·Y-020B·NT-02(D-188 사용자 결정), BRSEAL, NFPS-M4-1(표기 확인 D-230), LEDBAR, HHPSN8, GASSPRING, PSFJ12-80, NUT-M10, HG-KR23_CONN, PTFE_TUBE, 2400.05.12PZ.
- 미스미 로그인: 확인 못 함 — Claude in Chrome 연결된 브라우저 0개. 받지 않았고 기다리지 않았다(실행 지시).
- lite: F3SG-4RA0800-14(11-22 heavy 결과 재사용, 11-22 뒤 새로 받은 STEP 없음. 실행 지시 (h)로 LITE 과제는 넣지 않음).
- CAD: 열지 않음(MCP running 빈 목록·열린 문서 Untitled 확인 2회만). 목록은 BOM v2.30.3 '모델 바디' 칸과 저장본 이름 비교(v2.30.2 ↔ v2.30.3 STEP대기_ 이름 집합 같음)로 냈다. 원복할 것 없음.
- 규칙: E-10 "못 받으면 다시 시도하지 않고", E-21 "다시 부르면 이전 결과 파일부터 읽고 남은 것만", 프로젝트 규칙 10 "로그인이 풀렸거나 STEP을 못 받으면 기다리지 않는다".

### 워크플로우 메모
- STEP 대기 재시도의 swap 판정이 document.json 문자열 검색에 기대면 이미 바꾼 형번이 계속 swap으로 나온다(HFS8-80160-1090, STEPSWAP r5~r10). swap은 살아 있는 바디 목록(BOM '모델 바디' 칸 또는 measure names_only)으로만 판정해야 한다.
- v2.30.3 열기는 13~27분이라 목록만 보려고 열지 않았다. 살아 있는 STEP대기_ 바디 목록을 모델링부가 저장 때 tools/out에 남기면 이 부서가 CAD 없이 정확히 판정할 수 있다.
