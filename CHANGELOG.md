# CHANGELOG.md

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

---

# [Unreleased]

## Added

- 설계 v0.6.9 `3D_Modeling/FSAP_v0.6.9.sc`(디테일링 DP-3 수정 1회차, 작은 변경): `P_T05_HUB` +X 면에 렌치 구멍 Ø9 ×4 깊이 10(홀더 `CB5-16_T05_HD_1~4`와 같은 축, r 28.28) — 렌치 프로브 Ø8.5×30 겹침 0(M-01, PM 판정 DP3-X01·X02). 살 5.22·15.63, 허브 324.5 → 321.3 g. 동작 연구 9개 충돌 0·truncated false. 생성기 `tools/gen_dp3_detail.py fix1`, BOM `docs/bom/FSAP_v0.6.9_*.csv`(정비 비고), 보고서 `docs/reports/detailing/detail_DP-3_model1.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.8 `3D_Modeling/FSAP_v0.6.8.sc`(디테일링 DP-3 T05 테이프 공급, 작은 변경): 체결 16자리 실물 STEP — `CB5-16` ×8(평판 뿌리 2 물림 11, 홀더 4 물림 8.5, 안내 블록 2 물림 8), `CB5-20` ×2(홀더 귀 물림 7.5, 캡 보스 물림 8), `MBIS5-6.5-8` ×4, `STEP대기_SEWHEAD` M5 기초 구멍 6(D-10 임시). `P_T05_HOLDER` 카운터보어 Ø10 → Ø11·귀 윗면 Z 229·클램프 카운터보어 깊이 7.5·인서트 자리 9, `P_T05_CAP` 클램프 자리 고침, `P_T05_PAD` Z 43~63 한 덩어리 + NTJ-010C T홈(−X로 열림, 틈 0.2), `P_T05_GUIDE` 앞벽 t9.2(Y 553)·뿌리 R3 ×4·밑판 앞 윗모서리 R1. 생성기 `tools/gen_dp3_detail.py`, BOM `docs/bom/FSAP_v0.6.8_*.csv`(CB5-14·형번 미정 인서트 행 없앰), 결정로그 DL-D50~D57, 보고서 `docs/reports/detailing/detail_DP-3_model.md`
- 설계 v0.6.7 `3D_Modeling/FSAP_v0.6.7.sc`(디테일링 DP-2 수정 1회차, 작은 변경): `STEP대기_LBNR4_T01_*` ×24 지우고 스파이더 웹 밑 탭 너트판 `P_T01_NUTPLATE_R1/R2_1~3` ×6(A5052 t6 □40, Ø28.4, M4 관통 탭 ×4 PCD38 대각, C0.5, Z −104.5~−98.5) — `CB4-16` 물림 3.2 → 6, 스패너 자리 문제 없앰(PM 판정 DP2-X03). 스파이더 발 누름판 `P_T01_FOOTPLATE_1~3_N·_P` ×6(A5052 t6, 다리 쪽 C1) + `CB5-12_T01_SP*` ×12 → `STEP대기_CB5-18_T01_SP*` ×12(머리 자리 −224, 허브 물림 8). `P_T01_POST` 밑 플랜지 t8.5 → t12(윗면 −221) + 카운터보어 Ø9.5×3.5 ×3. 생성기 `tools/gen_dp2_r1.py`, BOM `docs/bom/FSAP_v0.6.7_*.csv`, 자료대기 D-37, 보고서 `docs/reports/detailing/detail_DP-2_model1.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.6 `3D_Modeling/FSAP_v0.6.6.sc`(디테일링 DP-2 T01 회전 묶음, 작은 변경): `P_T01_HUB` SUS304 t6 → t8(Z −241~−233, DG 테이블 Ø6.6 ×6·스파이더 발 M5 탭 ×12·기둥 M5 탭 ×3), `P_T01_SPIDER_1~3` SUS304 밀어내기 → A5052 t3 판금 모자형(바깥 발 22, 안 R3, `sheet.convert` 전개 390×364.14, 구멍–굽힘 최소 8.25), `P_T01_POST` 2 짧게 + 밑·위 플랜지 일체, `P_T01_DISC`·`P_T01_RING1`·`P_T01_RING2` 매트 면 모서리 R1, 링1 카운터보어·링2 머리 자리·띠 1·3·5 Ø5.5. 체결: 실물 `CB5-12` ×15·`CB5-16` ×9·`MBIS5-6.5-8` ×3, E-10 `STEP대기_CB4-16`·`_LBNR4` ×24씩·`_CB6-18` ×6, `PSFJ16-150` ×6 → `STEP대기_PSFJT16-150-M5`. `LHFR16` ×6 구멍 대각(45°·−15°·+15°), NTJ 같은 이름 → `_NTJ_A`·`_NTJ_B`. 생성기 `tools/gen_dp2_detail.py`, BOM `docs/bom/FSAP_v0.6.6_*.csv`, 결정로그 DL-D36~D43, 자료대기 D-37·D-42·D-43, 보고서 `docs/reports/detailing/detail_DP-2_model.md`. 조인트·행정·배치 변경 0. 미완: 스파이더 2·3 링1 안쪽 M4 너트 4개 스패너 자리(DL-D40, PM 결정)
- 설계 v0.6.5 `3D_Modeling/FSAP_v0.6.5.sc`(디테일링 DP-1 수정 2회차, 작은 변경): 맞춤핀 `STEP대기_MS3-8_T06`을 미스미 카탈로그 외형도대로(한끝 R=D, 다른 끝 15° ℓ1 1.0) 다시 그리고 재질 SUJ2(58HRC~, 밀도 7.83)로 — D-43 재질·경도 확인. 칼 전 행정 `joint.sweep`을 잎 컴포넌트로 나눠 헤드·T05·T06 잎 전부 멈춤 없음(DL-D31). 스크립트 `tools/out/detail/DP-1/r2/build.json`, BOM `docs/bom/FSAP_v0.6.5_*.csv`, 설계검토서 `docs/review/FSAP_v0.6.5_review.md`, 결정로그 DL-D30·D31, 자료대기 D-43, 보고서 `docs/reports/detailing/detail_DP-1_model2.md`. STEP 대기 7종은 미스미 로그인 풀림(login: false)으로 그대로. 조인트·행정·배치 변경 0
- 설계 v0.6.4 `3D_Modeling/FSAP_v0.6.4.sc`(디테일링 DP-1 수정 1회차, 작은 변경 — 중간 저장 v0.6.3 포함): 맞춤핀 형번 미스미 `MS3-8`로 정하고 `STEP대기_MS3-8_T06`(Ø3×8, T06_KNIFE, (77, −7.5) Z54~62)을 넣어 빈 핀 구멍 0(v0.6.3, 생성기 `tools/gen_dp1_r1.py`). 노루발 통로 입구 모따기 `Cone1` 시작을 주머니 끝벽 면에 맞춰 0.05 턱 면 2개 없앰(v0.6.4, MCP `timeline.edit`). 면 법선 두께 최소 1.018 ≥ 1.0. 홈매트 사이클은 두 연구(520·519단계)로 나눠 단계마다 검사. BOM `docs/bom/FSAP_v0.6.4_*.csv`(MS3-8 행), 설계검토서 `docs/review/FSAP_v0.6.4_review.md`, 결정로그 DL-D27~D29, 자료대기 D-43, 보고서 `docs/reports/detailing/detail_DP-1_model1.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.2 `3D_Modeling/FSAP_v0.6.2.sc`(디테일링 DP-1 헤드 둘레, 작은 변경): `P_T06_ARM` 판금 L t3 → SUS304 절삭 L(가로 t5·세로 t3, 축 자리 Ø16 H7 깊이 2 + Ø5.5 + 맞춤핀 Ø3 H7, 안 R1·바깥 C0.5), 체결 15자리(실물 `CB5-12` ×5, `STEP대기_CB4-16` ×4·`_LBNR4` ×4·`_LBNR5` ×2·`_NTJ-015C` 1), `PSFJ16-100_T06` → `STEP대기_PSFJT16-100-M5`(끝 Ø4.2×12 + 핀 Ø3×6), `STEP대기_CJ2B16-30SZ_ROD` Z49~99 + 임시 튜브 Ø5.4(T06-D01), `STEP대기_SEWHEAD` 브래킷 기초 구멍 Ø4.2×10 ×2, `P_T02_FOOT` Rigid 10K → A6061-T6 + 통로 입구 45° 모따기 + 안 모서리 R0.5, STEP대기 구매품 컴포넌트 part_number(P-02). 생성기 `tools/gen_dp1_detail.py`, BOM `docs/bom/FSAP_v0.6.2_*.csv`(made 가공법 칸, CB5-12 한 행), 설계검토서 `docs/review/FSAP_v0.6.2_review.md`, 보고서 `docs/reports/detailing/detail_DP-1_model.md`. 조인트·행정·배치 변경 0
- 설계 v0.6.1 `3D_Modeling/FSAP_v0.6.1.sc`(S02 STEP 대기 마무리, 작은 변경): 구매부가 `CJ2B16-30SZ`·`HFS8-4080-2850`·`-680`·`-1580` STEP을 또 못 받음(미스미 로그인 풀림) → 갈래 B. `STEP대기_HFS8-4080-1580_PL/PR` 상자를 Z −672~892로 줄여 끝마다 캡 끼움 깊이 8을 비움(S02-S03), 캡 4쌍 맞닿음 0.0·판정 불가 0. 조인트·동작 연구 변경 0, 8개 연구 겹침 0. BOM `docs/bom/FSAP_v0.6.1_*.csv`(STEP 대기 비고), 설계검토서 `docs/review/FSAP_v0.6.1_review.md`, 결정로그 S02-S01~S06·S02-M01~M03, 자료대기 D-37·D-41, 보고서 `mech_S02_*`
- v0.6.0 구동 T07 결과: 설계검토서 v0.6.0 검도·해석·디테일(T07-D01~D04)·예외 판정 요약, 결정로그 "구동 T07 결과", 요구서 T07 해결, 자료대기 D-41(1580 상자 캡 끼움 자리 비움 T07-X02, STEP 수령 뒤 교체·재판정), T07 검도·해석(손계산) 보고서
- 설계 v0.6.0 `3D_Modeling/FSAP_v0.6.0.sc`(T07 로딩·배출, 부품 묶음 신설): `BASE` 아래 `T07`(BASE와 리지드, 새 조인트 0, 동작 연구 변경 0) — 작업자 쪽 고정 가드틀. 형재 `HFS8-4080-460_GL/GR`(실물 STEP), `STEP대기_HFS8-4080-2850_G1/G4`·`-680_SL/SR`·`-1580_PL/PR`(D-41), 마감캡 `HFC8-4080-B` ×4(끝 기둥 위·아래), SUS304 t2 평판 `P_T07_SKIRT_C`(윗변 V홈 로딩 기준)·`_L`·`_R`. 커튼·버튼·자동 배출 자리는 `tools/motion_states.json` `t07_zones` 검사 상자. 8개 연구 새 겹침 0. 브래킷 HBLFSN8 24·판 체결은 안 그림. 생성기 `tools/gen_t07_mech.py`, BOM `docs/bom/FSAP_v0.6.0_*.csv`, 설계검토서 `docs/review/FSAP_v0.6.0_review.md`(제어 순서 제약 T07-Q1~Q8), 결정로그 T07-M02~M07, 자료대기 D-13·D-38~D-41, 보고서 `mech_T07_model.md`
- 설계 v0.5.1 `3D_Modeling/FSAP_v0.5.1.sc`(T06-X03): 세 매트 `MAT_*_SEAM` 아래 날개 없앤 ㄱ자 단면으로 다시 그림(바디당 2,448 → 1,700 mm³), SEAM ↔ BOUND 겹침 748 → 0. `tools/gen_t06_mech.py` 단면, `tools/motion_states.json` check_rule, 결정로그 T07-M01. 함께: T07 측정·구상·선정 보고서(`mech_T07_*`), 결정로그 T07-S01~S10, 자료대기 D-38~D-41
- v0.5.0 구동 T06 결과: 설계검토서 `docs/review/FSAP_v0.5.0_review.md`, 결정로그 "구동 T06 결과"(디테일 T06-D01~D08), 요구서 T06 해결·7절 이음매 마감 시제품 항목, 자료대기 D-07·D-37 갱신, BOM v0.5.0 비고, T06 검도·해석(손계산) 보고서. 예외 판정 T06-X01~X03(SEAM 단면 수정 → v0.5.1 대기)
- 설계 v0.5.0 `3D_Modeling/FSAP_v0.5.0.sc`(T06 시작·끝 이음매와 절단, 부품 묶음 신설): `HEAD` 아래 `T06`(SUS304 판금 ㄴ t4 `P_T06_BRACKET`, 실물 `LHFR16_T06`, `STEP대기_CJ2B16-30SZ`), `T06` 아래 `T06_KNIFE`(SUS304 판금 ㄱ t3 `P_T06_ARM`, SK85 t1.5 `P_T06_KNIFE`, 실물 `PSFJ16-100_T06`, `STEP대기_CJ2B16-30SZ_ROD`, 조인트 `J_T06_KNIFE` 직선 Z −30~0, 저장 0). 침판 `P_T02_PLATE` 칼 받이 관통 홈 2×22 + C0.5. 작업 대상 `MAT_*_SCRAP` 지우고 `MAT_*_SEAM`·`MAT_*_TAIL`(컴포넌트 이름 `MAT_*_SEAM`). 사이클 3개에 ④-0~④-7 43단계(큰 583·작은 298·홈 1039), 모든 연구에 J_T06_KNIFE 키. 볼트는 구멍만. 생성기 `tools/gen_t06_mech.py`, BOM `docs/bom/FSAP_v0.5.0_*.csv`, `tools/motion_states.json`, 결정로그 T06-M01~M10, 자료대기 D-07·D-10·D-37, 보고서 `mech_T06_*`
- 설계 v0.4.2 `3D_Modeling/FSAP_v0.4.2.sc`(S01 T06 전 구매품 실물 STEP 교체·형재 마감캡): 임시 형상 28바디를 실물 STEP으로 — `SV2RL28-1800`·`-1300` ×2씩(옛 SV2R20, 조립 높이 42 → 28), `DGM200R-AZAC`(출력 테이블은 MAT_ROT), `CJ2B16-60SZ` ×6, `CJ2B10-15Z`, `PSFJ16-100`, 새로 `ZH10DSA-06-06-08` ×2(580 안쪽 면). 마감캡 `HFC8-4080-B` ×14(드러난 끝면 전부). 높이 차 14: 새 `P_S01_XSPACER_1~4`(A5052 t14), `P_T01_YPLATE` 14 내림 + 모터 창, 새 `P_S01_DGSPACER`(A5052 U자 t50). 스파이더 다리 −235~−95.5·보스 구멍 Ø10.5, LHFR16 10.5 내림, 링2 띠 1·3·5 로드 끝 자리, `P_T05_GUIDE` 위판 t4. 남은 STEP대기는 재봉 헤드 4(D-10)뿐. 생성기 `tools/gen_s01_step.py`, BOM `docs/bom/FSAP_v0.4.2_*.csv`, 결정로그 S01-M01~M10, 자료대기 D-16~D-36 갱신, 보고서 `mech_S01_*`
- 설계 v0.4.1 `3D_Modeling/FSAP_v0.4.1.sc`(T05 수정 1회차): `P_T05_PLATE` SUS304 t3 → t5(X −80~−75, 오조작 손계산 SF 0.80 → 2.16), 맞대는 `P_T05_HOLDER` 플랜지·`P_T05_GUIDE` 등판 +X 끝 −78 → −80(t10 → t8). 테이프 길·롤·실린더 그대로. 생성기 `tools/gen_t05_mech_r1.py`, BOM `docs/bom/FSAP_v0.4.1_*.csv`(평판 뿌리 볼트 CB5-12 → CB5-14 ×2), 결정로그 T05-M09~M12, 보고서 `mech_T05_model1.md`. 함께: v0.4.0 T05 검증·해석(손계산) 보고서
- 설계 v0.4.0 `3D_Modeling/FSAP_v0.4.0.sc`(T05 테이프 공급·장력 유닛, 부품 묶음 신설): `HEAD` 아래 `T05`(SUS304 평판 t3, PET-CF 홀더·허브·캡·안내 블록 C틀, `STEP대기_PSFJ16-100`·`STEP대기_CJ2B10-15`), `T05_PAD`(PET-CF 패드 + 로드, 조인트 `J_T05_PAD` 직선 Z −13.5~0, 저장 −12.5), 작업 대상 외피 `T05_TAPE`(`MAT_TAPE_ROLL`·`MAT_TAPE_PATH`, BOM 밖). 볼트는 구멍만. 6개 연구 2,443단계 겹침 0. 생성기 `tools/gen_t05_mech.py`, BOM `docs/bom/FSAP_v0.4.0_made.csv`·`_purchased.csv`, 결정로그 T05-S01~S08·T05-M01~M08, 자료대기 D-06·D-10·D-33·D-34, 보고서 `mech_T05_*`.
- v0.4.1 구동 T05 결과: 설계검토서 FSAP_v0.4.1_review.md, 결정로그 "구동 T05 결과", 요구서 T05 해결, T05 검도·해석(손계산) 수정 1회차 보고서(mech_T05_verify1·fea1)
- v0.3.2 구동 T04 결과: 설계검토서 FSAP_v0.3.2_review.md, 결정로그 "구동 T04 결과", 요구서 T04 해결, T04 검도·해석(손계산) 보고서

- 설계 v0.3.2 `3D_Modeling/FSAP_v0.3.2.sc`(T04 가장자리 센서 배치): 노루발 `P_T02_FOOT`에 영역형 반사 화이버 주머니 12.0×3.15×8·검출 슬릿 11.0×1.0(바닥 관통)·화이버 통로 Ø2.6(+X 옆면 출구)을 깎음. 화이버 머리는 형번 미정(D-32)이라 그리지 않음. 생성기 `tools/gen_t04_mech.py`, BOM `docs/bom/FSAP_v0.3.2_made.csv`·`_purchased.csv`, 결정로그 T04-S01~S07·T04-M01~M04, 자료대기 D-32, 보고서 `mech_T04_*`.
- 설계 v0.3.1 `3D_Modeling/FSAP_v0.3.1.sc`: 미스미 실물 STEP으로 구매품 22개 교체(HFS8-4080-1300·460·1900·580 형재 10, LHFR16 6, PSFJ16-150 6). 생성기 `tools/gen_v031_step.py`, STEP 9종 `purchased-step/<형번>/`(BSS2020-1100·1450, HBLFSN8은 받기만 함). 결정로그 V031-01~05, C-10(유료 STEP은 받지 않음), 자료대기 D-17~D-31 갱신(SV2R20·ZH10DS 형번 없음, DGM200R·CJ2B16 미스미 CAD 없음).

- 설계 v0.1.0 `3D_Modeling/FSAP_v0.1.0.sc`(준비부): 동작 검사 준비물 — 고정부 `BASE`, 조인트 6개(매트 X·Y 이송, 매트 회전, 헤드 회전, 노루발 들기, 바늘), 동작 연구 `대기`·사이클 3개(큰·작은·홈 매트)·꺾임 정밀 3개, 작업 대상 모형 3종과 가공 뒤 형상·떨어진 조각(임시값, 결정로그 P-01~P-06). 기계 부품은 아직 없음.
- `tools/gen_motion_prep.py`(준비물 명령 스크립트 생성기), `tools/motion_states.json`(동작 연구 상태 → 단계 표).
- 보고서 `docs/reports/mechanism/mech_prep_check.md`(준비 점검), `mech_prep.md`(준비).
- 설계 요구서 초안 `docs/design-requirements.md`(엔진 양식, 과제 T01~T07).
- 결정로그 `docs/decision-log.md`(대화 단계 C-01~C-08, 예전 ADR 목록).
- 자료대기 목록 `docs/waiting-list.md`(D-01~D-15).
- 벤치마크·특허 조사 `docs/benchmark.md`(R375X·R375A, Richpeace, 만료 특허 7건).
- 엔진 기본 배치 폴더: `docs/reports/`, `tools/`, `purchased-step/`, `fea/cases/`, `fea/results/`, `deliverables/`.
- CAD를 SolidCraft로 정함(결정로그 C-09): `tools/config.json`(cad·doc), 설계 파일 폴더 `3D_Modeling/`, 자료대기 D-16(이 컴퓨터 실행 준비).

## Changed

- 요구서 8-2(설계 파일 이름·버전 규칙, v0.0.0 시작), 8-5(버전이 바뀔 때만 커밋·푸시), 8-6(CAD SolidCraft). 자료대기 D-15 해결.
- 시작 설계 `3D_Modeling/FSAP_v0.0.0.sc`(사용자가 앱에서 만든 빈 설계).

- 저장소를 MAT-RS-001 기구 개발 폴더로 바꿨다(결정로그 C-07). 기구 모델링은 MechDesign_Engine으로 한다.
- `README.md`, `CLAUDE.md`를 기구 개발용으로 다시 썼다(한글).
- ADR-004 상태를 Superseded로(C-07).
- `.gitignore`에 `tools/out/` 추가.

## Fixed

-

## Removed

- 6단계 폴더 `01_Planning` ~ `06_Business`(비어 있었음).
- `DECISIONS.md`(ADR 목록은 결정로그 "예전 ADR" 절로 옮김), `docs/decisions/ADR-TEMPLATE.md`(새 ADR을 만들지 않음).

## Deprecated

-

## Documentation

-

## Security

-

---

# [0.1.0] - 2026-07-29

## Added

- v0.3.2 구동 T04 결과: 설계검토서 FSAP_v0.3.2_review.md, 결정로그 "구동 T04 결과", 요구서 T04 해결, T04 검도·해석(손계산) 보고서

- Initial FSAP repository created.
- Project documentation established.
- README.md created.
- CLAUDE.md created.
- DECISIONS.md created.
- ADR management structure established.
- Initial Architecture Decision Records created (ADR-001 ~ ADR-004).
- Created phase folders (01_Planning ~ 06_Business).
- Created docs/decisions/ with ADR-TEMPLATE.md.

## Documentation

- Defined project vision.
- Defined repository structure.
- Defined documentation structure.
- Defined development workflow.
- Defined AI operating guidelines.
- Defined GitHub workflow.
- Synchronized CLAUDE.md with README.md: added ADR Management Rules and GitHub
  Rules sections, redefined DECISIONS.md as an ADR index, aligned CHANGELOG
  categories, and allowed phase repetition/overlap in the workflow.

---

# Changelog Rules

This file records completed changes only.

Do not record:

- Planned features
- Future ideas
- Discussions
- Draft documents
- Experimental concepts

Record only completed work.

---

# Categories

## Added

- v0.3.2 구동 T04 결과: 설계검토서 FSAP_v0.3.2_review.md, 결정로그 "구동 T04 결과", 요구서 T04 해결, T04 검도·해석(손계산) 보고서

New functionality.

---

## Changed

Behavior or architecture changes.

---

## Fixed

Bug fixes.

---

## Removed

Removed functionality.

---

## Deprecated

Features scheduled for removal.

---

## Documentation

Documentation updates.

---

## Security

Security-related improvements.

---

# Versioning

This project follows Semantic Versioning.

MAJOR.MINOR.PATCH

Example

v0.1.0

Initial release

↓

v0.2.0

Feature additions

↓

v0.3.0

Major improvements

↓

v1.0.0

Official release

---

# GitHub Release Policy

Each official GitHub Release should have a matching version in this file.

Example

GitHub Release

v0.2.0

↓

CHANGELOG

# [0.2.0]

The release notes and changelog should describe the same completed changes.

---

# Related Documents

README.md

Project overview.

CLAUDE.md

AI operating rules.

DECISIONS.md

ADR index.

docs/decisions/

Architecture Decision Records.

---

# Notes

Always keep the **Unreleased** section at the top.

When a new version is released:

1. Create a GitHub Release.
2. Move all completed items from **Unreleased** into the new version.
3. Create a fresh **Unreleased** section.
4. Keep versions in reverse chronological order.

---
