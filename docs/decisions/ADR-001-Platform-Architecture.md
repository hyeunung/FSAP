# ADR-001: Platform Architecture

| Item   | Value      |
| ------ | ---------- |
| Status | Accepted   |
| Scope  | Platform   |
| Date   | 2026-07-29 |

---

## Context

자동차 매트 랏빠 자동 봉제 시스템(MAT-RS-001) 개발을 시작하면서, 이 프로젝트를
단일 장비 개발로 진행할 것인지, 재사용 가능한 플랫폼 구축으로 진행할 것인지
결정이 필요했다.

향후 카펫, 가죽, 산업용 직물 등 다양한 유연 소재로의 확장이 예상된다.

## Decision

FSAP는 단일 장비 프로젝트가 아닌 **재사용 가능한 자동 봉제 플랫폼**으로
개발한다.

- MAT-RS-001은 FSAP 플랫폼의 첫 번째 적용 제품이다.
- 모든 설계 결정은 미래 재사용 가치를 최대화하는 방향으로 내린다.
- 기계 설계, 소재 공급, Edge Binding, 봉제, Motion Control, Vision, 전장 제어,
  Software, 제조, 검증 기술을 플랫폼 자산으로 축적한다.
- 모듈화 설계와 표준 인터페이스를 우선한다.

## Reason

- 유연 소재 봉제 자동화의 핵심 기술(공급, 가이드, 경로 제어, 품질 확보)은 소재와
  제품이 달라져도 공통으로 재사용 가능하다.
- 단일 장비 최적화는 단기적으로 빠르지만, 후속 제품마다 기술을 재개발해야 하는
  비용이 발생한다.
- 플랫폼 자산 축적이 장기적으로 가장 높은 사업 가치를 제공한다.

## Alternatives Considered

- **MAT-RS-001 전용 단일 장비 개발**: 초기 개발 속도는 빠르나 제품별 재설계
  비용이 반복 발생하고, 기술 자산이 축적되지 않아 기각.

## Consequences

- 모든 설계/개발 산출물은 제품 전용이 아닌 플랫폼 관점에서 검토해야 한다.
- 단기적으로 설계 및 문서화 노력이 다소 증가한다.
- MAT-RS-002, CARPET-RS-001, LEATHER-RS-001, TEXTILE-RS-001 등 후속 제품 개발
  비용이 감소한다.
- 제품 최적화가 플랫폼 가치를 훼손하는 경우, 플랫폼 가치를 우선한다.

## Validation

- 후속 제품 개발 시 기존 모듈/기술의 재사용 비율로 검증한다.
- 신규 제품에서 플랫폼 공통 기술을 수정 없이 사용할 수 있는지 확인한다.

## Related Documents

- README.md — Overview, Vision, Final Goal
- CLAUDE.md — Core Philosophy, Long-Term Goal
- ADR-002 (Product Naming Convention)
- ADR-004 (Development Workflow)

## Related GitHub Records

- Issue: TBD
- Pull Request: TBD
- Release: v0.1.0
