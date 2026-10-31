# CHANGELOG.md

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

---

# [Unreleased]

## Added

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
