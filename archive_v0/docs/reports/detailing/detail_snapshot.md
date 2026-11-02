# 디테일링 스냅샷 — FSAP_v0.6.1 (2026-10-31)

요약(10줄 안쪽)
- 대상: `3D_Modeling/FSAP_v0.6.1.sc`(tools/config.json doc). CLI로 저장본에만 대고 쟀다(MCP 안 씀, 저장 안 함, 원복할 것 없음 — 안내서 '원복' "읽기 부서가 CLI로만 쟀다면 원복할 것이 없다"). 파일 시각 12:18:13 그대로.
- 문서 상태: dirty false, 타임라인 557개 error·warning 0, 조인트 23개 floating 0·conflicts 0·errors 0.
- 직전 v0.6.0과 형상 다름(빈 버전 아님): `STEP대기_HFS8-4080-1580_PL/PR` Z −680~900 → −672~892, 부피 5,056,000 → 5,004,800 mm³(S02 캡 끼움 8 비움, 결정로그 T07-X02). 나머지 243 서명 같음.
- **볼트 0개.** 모델 안에 볼트·너트·T너트 바디도 BOM 행도 없다(CB·LCB·MSB·MS·NETW·SMSB·HNTT·PUSS 0). 체결 자리는 구멍만 있거나 구멍도 없다 → 디테일링 첫 일.
- 숨김 0(E-11, document.inspect 바디 150개 모두 visible).
- 가공품(P_) 36바디, 그중 하중 가공품 33개 임시 STEP을 `tools/out/detail/stepout/`에(E-06 예외, 스커트 3장 제외).
- 원장 scope: 전체 검사 아니오, 바뀐 쌍만 예, 바뀜 0·새로 0·없어짐 0(원장이 이미 v0.6.1). groups: 거울 쌍 79, 체결 묶음 0(체결 수 0).
- 미완: 볼트 집계 대상 없음, 재질 matcheck은 BOM 없음(가공품 BOM `docs/bom/*made*.csv` 없음, WF-056) → '검사 대상 없음(BOM 없음)'.

## 1. 문서 확인 (안내서 '문서 확인')

| 항목 | 값 |
|---|---|
| 문서 | FSAP_v0.6.1 (`3D_Modeling/FSAP_v0.6.1.sc`, 3,465,551 B, 2026-10-31 12:18:13) |
| dirty | false (CLI 저장본, 앱 열린 설계는 건드리지 않음) |
| 타임라인 | 557 피처, error·warning 0 |
| 메타 설명 | "S02 mechanism: HFS8-4080-1580 wait boxes trimmed to Z-672..892 for cap seats; STEP wait kept" |
| 조인트 | 23, floating [] · conflicts [] · errors [] |
| 동작 상태 | 스크립트 처음·끝 `motion.play {study:"대기", step:0}` |

### 직전 버전과 비교 (same_as_previous = false)

| 부품 | v0.6.0 bbox Z | v0.6.1 bbox Z | 부피 mm³ |
|---|---|---|---|
| BASE:1 / T07:1 `STEP대기_HFS8-4080-1580_PL` (X −1505~−1425, Y −1740~−1700) | −680 ~ 900 | −672 ~ 892 | 5,056,000 → 5,004,800 |
| BASE:1 / T07:1 `STEP대기_HFS8-4080-1580_PR` (X 1425~1505) | −680 ~ 900 | −672 ~ 892 | 5,056,000 → 5,004,800 |

근거: `ledger.diff(signatures_v060, 지금)` → changed 4(같은 두 바디가 두 occurrence 경로에 잡힘), added 0, removed 0. 결과 `tools/out/detail/snap/compare.json`. 12:21에 S02가 만든 v0.6.1 서명과는 차이 0.

## 2. 볼트 전수 집계 (U-12, 안내서 '목록·볼트 집계')

`assembly.bom {levels:"flat"}` 24행·71 occurrence, 바디 이름 전수(고유 123 이름)에서 볼트·너트 접두(config `bolt_prefixes`·`nut_prefixes`) 0건.

| 형번 | 수량 | 지름 |
|---|---|---|
| (없음) | 0 | M3·M4·M5·M6·M8·M10 모두 0 |

모델에 볼트가 없으므로 사용처 표도 비어 있다. 체결 자리로 앞 과제가 남긴 것(디테일링 대상, 결정로그·설계검토서 '디테일 과제'):

| id | 자리 | 계획 체결 |
|---|---|---|
| T05-D3 | T05 평판 8(뿌리 CB5-14 2 포함)·홀더 5·캡 1, 안내 블록 M5 인서트 2 — 빈 구멍 16 | CB5, M5 인서트 |
| T05-D5 / F1 | `P_T05_HOLDER` CB5-16 머리 PET-CF 좌면 | 와셔·금속 슬리브 |
| S01-D3 | CJ2B10 로드 NTJ-010C ↔ `T05_PAD` | 로드–패드 체결 |
| S01-D4 | X 받침·DGM 받침·Y판(체결 구멍 없음, DGM 받침 기초 구멍 Ø8.5×4) | CB5, M10(U-12 예외: 구매품 DGM 탭) |
| T06-D02 | 칼–팔 M5×2·너트, 브래킷–헤드 M5×2, LHFR16_T06 M4×4·너트×4, 로드 너트, 축–팔 M5 — 15자리 구멍만 | CB5, CB4-16(LHFR16 구매품 탭 지름), LBNR4/5, NTJ-015C |
| T07-D03 | `P_T07_SKIRT_C/L/R` ↔ G1·G4·GL/GR·PL/PR 앞면 — 구멍·볼트 0 | M5 T너트 HNTT8-5(D-41) + CB5-12 |
| 1(v0.2.1)·5 | 링2 샤프트·로드 윗끝 ↔ 띠 1·3·5 맞닿기만 | 체결 필요 |

## 3. 숨김·부품 목록·질량·재질 (E-11, E-09)

- 숨김: 0 / 150(document.inspect bodies 모두 visible true). occurrence.properties는 표시 상태를 주지 않는다.
- 바디: 서명 경로 247(자식 occurrence가 부모에도 잡혀 중복), 이름+bbox로 고유 155바디, 질량 합 441.9 kg(매트 모형·STEP대기 상자 포함).
- 재질(고유 바디): Steel 69, Aluminum 18, Nylon 18(마감캡), A5052 14, Default 14, SUS304 11, PET-CF 6, Rigid 10K 3, S50C 1, SK85 1. **Default는 작업 대상 모형(MAT_LARGE·SMALL·GROOVE와 BOUND·TAIL, MAT_TAPE_ROLL)뿐** — 가공품·구매품 재질 빈칸 0.
- matcheck: 가공품 BOM `docs/bom/*made*.csv` 없음 → 검사 대상 없음(BOM 없음), 실행 지시 (9).

가공품(P_) 36바디:

| 부품 | 유닛 | 재질 | 질량 g |
|---|---|---|---|
| P_S01_DGSPACER | MAT_Y | A5052 | 4156.9 |
| P_S01_XSPACER_1~4 | MAT_X | A5052 | 157.6 ×4 |
| P_T01_DISC | MAT_ROT | Rigid 10K | 188.2 |
| P_T01_HUB | MAT_ROT | SUS304 | 3303.4 |
| P_T01_POST | MAT_ROT | PET-CF | 450.8 |
| P_T01_RING1 | RING1 | A5052 | 7103.7 |
| P_T01_RING2 | RING2 | A5052 | 7337.3 |
| P_T01_RING2_STRAP_1~6 | RING2 | A5052 | 104.4~104.5 ×6 |
| P_T01_SPIDER_1~3 | MAT_ROT | SUS304 | 3054.1 ×3 |
| P_T01_YPLATE | MAT_Y | A5052 | 7257.1 |
| P_T02_BINDER | HEAD | Rigid 10K | 51.2 |
| P_T02_FOOT | PRESSER | Rigid 10K | 25.5 |
| P_T02_HEADPLATE | BASE | SUS304 | 2283.8 |
| P_T02_PLATE | HEAD | S50C | 101.2 |
| P_T05_CAP / GUIDE / HOLDER / HUB / PAD | T05 / T05_PAD | PET-CF | 56.9 / 119.6 / 55.8 / 324.5 / 3.7 |
| P_T05_PLATE | T05 | SUS304 | 2118.8 |
| P_T06_ARM | T06_KNIFE | SUS304(t3) | 53.6 |
| P_T06_BRACKET | T06 | SUS304 | 225.1 |
| P_T06_KNIFE | T06_KNIFE | SK85 | 5.4 |
| P_T07_SKIRT_C / L / R | BASE·T07 | SUS304 | 17886.2 / 5845.8 / 5845.8 |

임시 STEP(E-06 예외, 해석용): `tools/out/detail/stepout/` 33개 = 위 표에서 스커트 3장 뺀 전부(스커트는 덮개, `tools/out/mech_T07/stepout/`에 이미 있음).

## 4. 서명·체결 목록·변경 범위·묶음 (E-17, E-19)

- `tools/out/signatures.json` 247 경로(v0.6.1, 다시 씀), `tools/out/bolts.json` = [](볼트 0).
- `ledger.py scope`: 전체 검사 아니오, 바뀐 쌍만 예, 바뀜 0, 새로 0, 없어짐 0, 이웃 0(원장 doc = v0.6.1, 2026-10-31, passed 3). 이전 scope.json은 `tools/out/detail/snap/scope_prev.json`.
- `groups.py`: 거울 쌍 79(가공품: SPIDER_2↔3, XSPACER_1↔2·3↔4, RING2_STRAP_2↔6·3↔5, SKIRT_L↔R), 체결 묶음 0, 체결 수 0.

## 5. 디테일링 대상 목록 (설계검토서 v0.2.1·v0.3.2·v0.4.1·v0.4.2·v0.5.0·v0.6.0·v0.6.1 '못 한 것'·'디테일 과제', 결정로그 '디테일 과제')

전문은 `tools/out/detail/snap/detail_items.txt`(검토서 행 38)와 `tools/out/known_details_2026-10-31.json`(12). v0.6.1 검토서에는 새 행 없음. 묶으면:
- 체결(볼트 0 해소): T05-D3·D5·F1·F3, S01-D3·D4, T06-D02, T07-D03, v0.2.1-5(링2 띠).
- 두께·강도: T06-D03·D05·D06(팔 t3 → t5 기본, 지시 (13)), T05-D6/F2(안내 블록 앞벽), T05-D2·D4(패드 T홈 살 1.5, 홀더 귀 살 1.0), v0.2.1-6(허브 SF), v0.3.2-3~5(노루발 얇은 살·SF·칼날 살).
- 확인·기록만: S01-D1·D2(M-08), T06-D04(요구서 7), T06-D08·v0.2.1-7(카탈로그 D-37·D-17), T07-D04(조절발 D-39).
- 구동 과제 후보(디테일링에서 고치지 않음): T06-D07 축 이동안, T07-D02·U-T07-1 옆·뒤 커버, T05-D1 패드 위치(이동이면 구동), v0.2.1-3 링2 포트 방향.
- STEP 대기: T06-D01(CJ2B16-30SZ), T07-D01(1580 캡 판정), D-37·D-41 형번.

## 워크플로우 메모

- `occurrence.properties`(descendants 기본)가 자식 occurrence의 바디를 부모에도 넣어 서명 경로 247 중 고유 바디는 155다. ledger 비교에는 문제 없으나 질량 합·부품 수를 서명에서 바로 세면 겹친다.
- `document.inspect` bodies는 150개라 고유 155와 맞지 않는다(STEP 넣은 구매품 일부가 빠지는 듯). 숨김 판정의 범위가 그만큼 좁다.
- 바디의 `path` 값은 피처 번호 같은 짧은 목록이라 고유 키로 못 쓴다.
