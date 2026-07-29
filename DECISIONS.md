# DECISIONS.md

# FSAP Architecture Decision Index

Version: 1.0

---

# Purpose

이 문서는 FSAP 프로젝트의 Architecture Decision Record(ADR) 목록을 관리하는
인덱스이다.

중요한 기술적, 구조적, 운영적 의사결정은 각각 하나의 ADR 파일로 작성하며, 이
문서에서는 ADR의 목록과 상태만 관리한다.

상세 내용은 각 ADR 파일을 참고한다.

---

# ADR Location

모든 ADR은 다음 위치에서 관리한다.

```text
docs/decisions/
```

예시

```text
docs/
└── decisions/
    ├── ADR-TEMPLATE.md
    ├── ADR-001-Platform-Architecture.md
    ├── ADR-002-Product-Naming-Convention.md
    ├── ADR-003-Edge-Binding-Terminology.md
    ├── ADR-004-Development-Workflow.md
    └── ADR-XXX-Short-English-Title.md
```

---

# ADR Status

| Status     | Description           |
| ---------- | --------------------- |
| Proposed   | 검토 중               |
| Accepted   | 공식 채택             |
| Rejected   | 채택되지 않음         |
| Deprecated | 더 이상 사용하지 않음 |
| Superseded | 새로운 ADR로 대체됨   |

---

# ADR Index

| ADR     | Title                     | Status   | Scope       | Date       |
| ------- | ------------------------- | -------- | ----------- | ---------- |
| ADR-001 | Platform Architecture     | Accepted | Platform    | 2026-07-29 |
| ADR-002 | Product Naming Convention | Accepted | Naming      | 2026-07-29 |
| ADR-003 | Edge Binding Terminology  | Accepted | Terminology | 2026-07-29 |
| ADR-004 | Development Workflow      | Accepted | Process     | 2026-07-29 |

---

# ADR Creation Rules

다음과 같은 변경은 ADR 작성 여부를 검토한다.

- Platform Architecture
- Machine Architecture
- Motion System
- Feeding System
- Binder Structure
- Vision Architecture
- PLC Architecture
- Software Architecture
- Communication Architecture
- Repository Structure
- Documentation Structure
- GitHub Workflow
- Naming Convention
- Development Workflow
- Engineering Standard

---

# Changes That Normally Do Not Require ADR

다음 변경은 일반적으로 ADR를 작성하지 않는다.

- 오타 수정
- 문서 표현 수정
- 작은 버그 수정
- UI 문구 변경
- 코드 리팩토링
- 테스트 코드 추가
- 파라미터 조정
- 스타일 수정

---

# ADR Numbering Rules

- ADR 번호는 순차적으로 증가한다.
- 기존 번호를 재사용하지 않는다.
- 삭제하지 않는다.
- 결번이 발생해도 그대로 유지한다.

예시

```text
ADR-001
ADR-002
ADR-003
...
ADR-120
```

---

# ADR Naming Rules

파일명은 항상 다음 형식을 사용한다.

```text
ADR-XXX-Short-English-Title.md
```

예시

```text
ADR-005-Servo-Axis-Structure.md

ADR-006-Edge-Detection-Algorithm.md

ADR-007-Repository-Structure.md

ADR-008-GitHub-Workflow.md
```

---

# ADR Workflow

새로운 기술적 의사결정은 다음 절차를 따른다.

```text
Need New Decision

↓

Search Existing ADR

↓

Check Existing Decision

↓

Conflict Review

↓

Create New ADR

↓

Update DECISIONS.md

↓

Update CHANGELOG.md

↓

Link GitHub Issue

↓

Link Pull Request
```

---

# Related Documents

README.md

프로젝트 소개

CLAUDE.md

AI 운영 규칙

CHANGELOG.md

변경 이력

docs/decisions/

Architecture Decision Records

---

# Notes

DECISIONS.md에는 ADR의 상세 내용을 작성하지 않는다.

각 ADR는 독립적인 Markdown 파일로 관리하며, 이 문서는 프로젝트의 ADR 인덱스
역할만 수행한다.

---
