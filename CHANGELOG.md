# CHANGELOG.md

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

---

# [Unreleased]

## Added

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
