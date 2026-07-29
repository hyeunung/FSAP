# ADR-004: Development Workflow

| Item   | Value      |
| ------ | ---------- |
| Status | Accepted   |
| Scope  | Process    |
| Date   | 2026-07-29 |

---

## Context

FSAP는 기계, 전장, 제어, Software, Vision, 제조가 결합된 복합 시스템
프로젝트이다. 단계를 건너뛰는 개발은 재작업과 품질 문제를 유발하므로, 프로젝트
전체 수명주기를 관리할 표준 개발 절차의 결정이 필요했다.

## Decision

FSAP의 모든 개발은 다음 6단계 절차를 따른다.

```text
Planning → Concept → Design → Development → Validation → Business
```

| Phase          | Folder         | Goal                             |
| -------------- | -------------- | -------------------------------- |
| 01 Planning    | 01_Planning    | 무엇을 만들 것인지 정의          |
| 02 Concept     | 02_Concept     | 어떤 원리와 구조로 해결할지 정의 |
| 03 Design      | 03_Design      | 개념을 구현 가능한 설계로 변환   |
| 04 Development | 04_Development | 승인된 설계를 구현               |
| 05 Validation  | 05_Validation  | 요구사항 만족 여부 검증          |
| 06 Business    | 06_Business    | 검증된 기술과 제품의 사업화      |

- 각 단계는 필요에 따라 반복하거나 일부 병행할 수 있다.
- 다만 핵심 요구사항과 기술적 의사결정이 확인되지 않은 상태에서 후속 단계의
  결과를 최종 확정하지 않는다.
- 저장소 폴더 구조는 이 6단계를 그대로 반영한다.

## Reason

- 단계별 목표와 허용 작업을 명확히 하여 조기 최적화와 재작업을 방지한다.
- 문서와 산출물이 단계별 폴더에 정리되어 추적성이 확보된다.
- 후속 제품 개발 시 동일 절차를 재사용할 수 있다.

## Alternatives Considered

- **자유로운 애자일 방식 (단계 구분 없음)**: 하드웨어가 포함된 복합 시스템에서
  설계 미확정 상태의 제작 착수 위험이 커서 기각.
- **엄격한 워터폴 (반복 불허)**: 시제품 검증 결과를 설계에 반영하는 반복이
  필수적이므로 기각. 반복과 일부 병행을 허용하는 절충안을 채택.

## Consequences

- 모든 산출물은 해당 단계 폴더(01_Planning ~ 06_Business)에 저장한다.
- 각 단계의 허용/비허용 작업은 CLAUDE.md의 Phase Rules를 따른다.
- 단계를 건너뛴 산출물은 공식 결과물로 인정하지 않는다.

## Validation

- 산출물이 올바른 단계 폴더에 위치하는지 검토한다.
- 후속 단계 착수 전 선행 단계의 핵심 결정이 확인되었는지 검토한다.

## Related Documents

- README.md — Development Process, Repository Structure
- CLAUDE.md — Development Workflow, Phase Rules
- ADR-001 (Platform Architecture)

## Related GitHub Records

- Issue: TBD
- Pull Request: TBD
- Release: v0.1.0
