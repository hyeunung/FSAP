# FSAP

## Flexible Sewing Automation Platform

> Building the next generation of automated sewing technology for flexible
> materials.

---

## Overview

FSAP(Flexible Sewing Automation Platform)는 자동차 매트 자동 봉제 시스템 개발을
시작으로, 다양한 산업용 유연 소재(Flexible Material)의 자동 봉제 기술을
플랫폼화하기 위한 프로젝트이다.

이 프로젝트의 목적은 하나의 자동 봉제기를 만드는 것이 아니라, 다양한 제품과
소재에 재사용할 수 있는 자동 봉제 플랫폼을 구축하는 것이다.

FSAP 플랫폼에는 다음 기술이 포함된다.

- 기계 설계
- 유연 소재 공급 및 가이드 기술
- 봉제 기술
- Edge Binding 기술
- Motion Control
- Vision
- PLC 및 전장 제어
- HMI
- 자동화 Software
- 품질 검사
- 제조 및 조립 기술

프로젝트를 통해 개발되는 모든 기술은 FSAP 플랫폼 자산으로 관리하며, 차세대 제품
개발에 지속적으로 재사용한다.

---

## Vision

현재 첫 번째 개발 대상은 자동차 매트 자동 봉제 시스템이다.

그러나 FSAP의 최종 목표는 자동차 매트를 넘어 카펫, 가죽, 산업용 직물 및 다양한
유연 소재를 자동으로 봉제할 수 있는 세계 최고 수준의 자동 봉제 플랫폼을 구축하는
것이다.

FSAP는 제품 하나를 개발하는 프로젝트가 아니다.

기계 구조, 소재 공급, 봉제, 제어, Vision, Software, 제조 및 검증 기술을
지속적으로 축적하고 재사용하는 플랫폼 프로젝트이다.

---

## Current Product

### Product Code

`MAT-RS-001`

### Product Name — Korean

자동차 매트 랏빠 자동 봉제 시스템

### Product Name — English

Automotive Mat Edge Binding Sewing System

---

## Current Development Direction

MAT-RS-001은 자동차 매트의 외곽 경로를 따라 Edge Binding 봉제를 자동으로
수행하는 시스템을 목표로 한다.

현재 검토 중인 기본 개발 방향은 다음과 같다.

- 자동차 매트를 작업 영역에 고정한다.
- 봉제 헤드 또는 봉제 시스템이 매트 외곽 경로를 따라 이동한다.
- 매트의 형상과 곡률에 맞춰 봉제 경로를 제어한다.
- 매트 가장자리를 Binder 내부로 안정적으로 공급한다.
- 곡선, 오목 형상 및 작은 회전 반경에서도 일정한 봉제 품질을 확보한다.
- Motion, Vision 및 봉제 기술을 향후 다른 유연 소재에도 재사용할 수 있도록
  모듈화한다.

이 항목은 현재 개발 방향을 설명한다.

구체적인 기계 구조, Feeding 방식, Binder 구조, Motion 방식 및 Vision 구조가
결정되면 각각 별도의 ADR로 기록한다.

---

## Long-Term Product Roadmap

### Current Product

- `MAT-RS-001`
  - Automotive Mat Edge Binding Sewing System

### Future Product Candidates

- `MAT-RS-002`
  - Next Generation Automotive Mat Edge Binding Sewing System

- `CARPET-RS-001`
  - Industrial Carpet Edge Binding Sewing System

- `LEATHER-RS-001`
  - Leather Edge Binding Sewing System

- `TEXTILE-RS-001`
  - Industrial Textile Edge Binding Sewing System

향후 새로운 제품은 가능한 한 기존 FSAP 플랫폼의 공통 기술, 모듈 및 표준
인터페이스를 기반으로 개발한다.

---

## Target Industries

FSAP 플랫폼은 다음 산업과 소재로 확장하는 것을 목표로 한다.

- Automotive Floor Mat
- Trunk Mat
- Carpet
- Artificial Leather
- Natural Leather
- Industrial Textile
- Composite Flexible Material
- Industrial Fabric
- 기타 유연 소재 산업

---

## Core Technologies

### Mechanical Engineering

- Machine Structure
- Sewing Head Structure
- Motion Mechanism
- Feeding Mechanism
- Material Guiding Mechanism
- Edge Binding Technology
- Sewing Technology
- Jig and Fixture Design

### Electrical Engineering

- Servo Control
- Motor and Drive Integration
- PLC
- Sensor Integration
- Safety System
- Electrical Architecture

### Software and Control

- Motion Control
- Path Management
- HMI
- Machine Software
- Parameter Management
- Recipe Management
- Data Logging

### Vision

- Material Position Recognition
- Edge Recognition
- Path Tracking
- Sewing Quality Inspection

### Manufacturing

- Assembly
- Jig Design
- Process Optimization
- Quality Management
- Maintenance Standardization

---

## Development Process

FSAP 프로젝트는 다음 개발 절차를 기준으로 운영한다.

```text
Planning
   ↓
Concept
   ↓
Design
   ↓
Development
   ↓
Validation
   ↓
Business
```

### Planning

무엇을 만들 것인지 정의한다.

- 문제 정의
- 요구사항
- 개발 범위
- 목표
- 성공 기준

### Concept

어떤 원리와 구조로 문제를 해결할지 정의한다.

- 시스템 개념
- 기능 구성
- 기술 대안
- 핵심 아이디어
- 특허 가능성

### Design

선택한 개념을 실제 구현 가능한 설계로 변환한다.

- 기계 설계
- 전장 설계
- 제어 설계
- Software Architecture
- 인터페이스 정의

### Development

승인된 설계를 실제 장비와 Software로 구현한다.

- 제작
- 조립
- PLC
- Motion
- Vision
- HMI
- Software
- 시스템 통합

### Validation

개발 결과가 요구사항을 만족하는지 검증한다.

- 기능 시험
- 봉제 품질 시험
- 성능 시험
- 신뢰성 시험
- 안전 시험
- 실패 분석

### Business

검증된 기술과 제품을 사업화한다.

- 특허
- 제조 계획
- 원가 분석
- 고객 제안
- 마케팅
- 유지보수 계획

각 단계는 필요에 따라 반복하거나 일부 병행할 수 있다.

다만 핵심 요구사항과 기술적 의사결정이 확인되지 않은 상태에서 후속 단계의 결과를
최종 확정하지 않는다.

---

## Repository Structure

```text
FSAP/
├── README.md
├── CLAUDE.md
├── CHANGELOG.md
├── DECISIONS.md
│
├── docs/
│   └── decisions/
│       ├── ADR-TEMPLATE.md
│       ├── ADR-001-Platform-Architecture.md
│       ├── ADR-002-Product-Naming-Convention.md
│       ├── ADR-003-Edge-Binding-Terminology.md
│       ├── ADR-004-Development-Workflow.md
│       └── ADR-XXX-Short-English-Title.md
│
├── 01_Planning/
├── 02_Concept/
├── 03_Design/
├── 04_Development/
├── 05_Validation/
└── 06_Business/
```

---

## Documentation System

FSAP 프로젝트는 다음 핵심 문서를 기준으로 관리한다.

### README.md

프로젝트를 처음 접하는 사람이 FSAP를 빠르게 이해하기 위한 소개 문서이다.

주요 내용:

- 프로젝트 개요
- 비전
- 현재 제품
- 핵심 기술
- 개발 절차
- 저장소 구조
- 문서 관리 체계

### CLAUDE.md

AI와 프로젝트 참여자가 따라야 하는 작업 및 운영 규칙이다.

주요 내용:

- AI 작업 원칙
- 단계별 작업 기준
- 문서 동기화 규칙
- ADR 관리 규칙
- GitHub 운영 규칙
- 작업 완료 조건

### CHANGELOG.md

프로젝트에서 실제로 발생한 중요한 변경사항을 기록한다.

주요 내용:

- 기능 추가
- 설계 변경
- 구조 변경
- 오류 수정
- 문서 변경
- 공식 버전 이력

아직 발생하지 않은 예정 작업은 CHANGELOG에 완료된 변경처럼 기록하지 않는다.

### DECISIONS.md

FSAP 프로젝트의 ADR 인덱스이다.

DECISIONS.md에는 각 의사결정의 번호, 제목, 상태, 날짜, 범위 및 상세 문서 링크를
기록한다.

상세한 의사결정 내용은 다음 폴더의 개별 ADR 파일에 기록한다.

```text
docs/decisions/
```

### ADR Files

ADR은 Architecture Decision Record의 약자이다.

중요한 기술적·운영적 의사결정의 배경과 이유를 보존한다.

각 ADR에는 일반적으로 다음 내용이 포함된다.

- Context
- Decision
- Reason
- Alternatives Considered
- Consequences
- Validation
- Related Documents
- Related GitHub Records

---

## GitHub Repository Management

FSAP는 GitHub를 공식 버전 관리 및 협업 저장소로 사용한다.

GitHub에서 다음 항목을 관리한다.

- 프로젝트 문서
- 소스 코드
- 설계 관련 파일
- ADR
- Issue
- Branch
- Commit
- Pull Request
- Release
- 변경 검토 기록

기본 작업 흐름은 다음과 같다.

```text
Issue
   ↓
Working Branch
   ↓
Commit
   ↓
Pull Request
   ↓
Review and Validation
   ↓
Merge to main
   ↓
Release
```

### Main Branch

`main` 브랜치는 검토 및 승인된 상태를 유지한다.

원칙적으로 작업 내용을 `main` 브랜치에 직접 커밋하지 않는다.

### Working Branches

각 작업은 목적에 맞는 별도 브랜치에서 진행한다.

예시:

```text
feature/feeding-control
design/binder-structure
fix/motion-offset
docs/adr-management
refactor/project-structure
test/curved-sewing-path
experiment/vision-edge-detection
```

### Pull Requests

중요한 변경사항은 Pull Request를 통해 검토한 후 `main`에 병합한다.

Pull Request에는 가능한 한 다음 내용을 포함한다.

- 변경 목적
- 주요 변경사항
- 검증 방법 및 결과
- 영향 범위
- 관련 Issue
- 관련 ADR
- CHANGELOG 업데이트 여부

### Releases

공식 버전이 확정되면 Git Tag와 GitHub Release를 생성한다.

예시:

```text
v0.1.0
v0.2.0
v1.0.0
```

GitHub Release의 내용은 `CHANGELOG.md`의 해당 버전 내용과 일치해야 한다.

GitHub의 세부적인 Branch, Commit, Pull Request 및 Release 규칙은 `CLAUDE.md`에서
정의한다.

---

## Development Principles

FSAP는 다음 원칙을 따른다.

- Platform First
- Documentation First
- Decision Traceability
- Modular Design
- Reusable Technology
- Standard Interfaces
- Standardization
- Scalability
- Maintainability
- Testability
- Safety
- Continuous Improvement

---

## Decision and Change Traceability

중요한 프로젝트 변경은 다음 기록이 서로 연결되도록 관리한다.

```text
GitHub Issue
무엇이 문제이고 무엇이 필요한가

ADR
왜 특정 방향을 선택했는가

GitHub Pull Request
어떻게 변경하고 검토했는가

CHANGELOG
실제로 무엇이 변경되었는가

GitHub Release
어떤 버전으로 공식 배포되었는가
```

모든 작은 작업에 ADR이 필요한 것은 아니다.

그러나 플랫폼 구조, 기계 구조, 제어 방식, Software Architecture, 기술 선택 및
장기적인 표준에 영향을 미치는 결정은 ADR 작성 여부를 검토한다.

---

## Final Goal

자동차 매트 자동 봉제 시스템은 FSAP 플랫폼의 첫 번째 적용 제품이다.

FSAP의 최종 목표는 다음 기술을 하나의 재사용 가능한 플랫폼으로 통합하는 것이다.

- 기계 설계
- 유연 소재 공급
- Edge Binding
- 봉제
- Motion Control
- Vision
- 전장 제어
- Software
- 제조
- 검증
- 유지보수

프로젝트를 통해 확보되는 모든 기술, 데이터, 실패 경험 및 의사결정은 플랫폼
자산으로 축적하며 미래 제품 개발에 지속적으로 재사용한다.

---

## License

Copyright © FSAP Project

All Rights Reserved.
