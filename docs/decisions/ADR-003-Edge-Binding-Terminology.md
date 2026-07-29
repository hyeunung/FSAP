# ADR-003: Edge Binding Terminology

| Item   | Value       |
| ------ | ----------- |
| Status | Accepted    |
| Scope  | Terminology |
| Date   | 2026-07-29  |

---

## Context

자동차 매트 가장자리 마감 봉제 공정은 현장에서 "랏빠(ラッパ)"라는 일본어 유래
용어로 널리 불린다. 공식 문서, 영문 문서 및 플랫폼 기술 자산에서 사용할 표준
용어의 결정이 필요했다.

## Decision

- 공식 영문 표준 용어는 **Edge Binding**을 사용한다.
- 관련 부속 명칭은 **Binder**(바인더)를 사용한다.
- 한국어 제품명 등 현장 소통 맥락에서는 "랏빠"를 병기할 수 있다.
  - 예: 자동차 매트 랏빠 자동 봉제 시스템 = Automotive Mat Edge Binding Sewing
    System

## Reason

- "랏빠"는 일본어 유래 현장 용어로 국제 표준 문서에 부적합하다.
- Edge Binding은 공정의 본질(가장자리 감싸기 봉제)을 정확히 기술하는 표준 영문
  용어이다.
- 플랫폼이 카펫, 가죽, 직물로 확장되어도 동일 용어를 재사용할 수 있다.

## Alternatives Considered

- **현장 용어 "랏빠"를 공식 용어로 사용**: 국제화 및 특허/기술 문서 작성에
  부적합하여 기각.
- **Hemming / Edge Trimming 등 유사 용어**: 공정 특성(테이프로 가장자리를 감싸며
  봉제)을 정확히 표현하지 못해 기각.

## Consequences

- 모든 기술 문서, ADR, 코드, 제품명(영문)은 Edge Binding / Binder 용어를
  사용한다.
- 현장 소통 시 한국어 문서에는 "랏빠"를 병기하여 혼란을 방지한다.

## Validation

- 문서 전반에서 용어 사용 일관성을 검토한다.

## Related Documents

- README.md — Current Product, Core Technologies
- CLAUDE.md — Product Name
- ADR-002 (Product Naming Convention)

## Related GitHub Records

- Issue: TBD
- Pull Request: TBD
- Release: v0.1.0
