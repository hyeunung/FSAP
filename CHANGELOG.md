# CHANGELOG.md

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

---

# [Unreleased]

## Added

- 설계 요구서 초안 `docs/design-requirements.md`(엔진 양식, 과제 T01~T07).
- 결정로그 `docs/decision-log.md`(대화 단계 C-01~C-08, 예전 ADR 목록).
- 자료대기 목록 `docs/waiting-list.md`(D-01~D-15).
- 벤치마크·특허 조사 `docs/benchmark.md`(R375X·R375A, Richpeace, 만료 특허 7건).
- 엔진 기본 배치 폴더: `docs/reports/`, `tools/`, `purchased-step/`, `fea/cases/`, `fea/results/`, `deliverables/`.
- CAD를 SolidCraft로 정함(결정로그 C-09): `tools/config.json`(cad·doc), 설계 파일 폴더 `cad/`, 자료대기 D-16(이 컴퓨터 실행 준비).

## Changed

- 요구서 8-2(설계 파일 이름·버전 규칙, v0.0.0 시작), 8-5(버전이 바뀔 때만 커밋·푸시), 8-6(CAD SolidCraft). 자료대기 D-15 해결.
- 빈 설계 `cad/MAT-RS-001_v0.0.0.sc`(단위 mm) 추가.

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
