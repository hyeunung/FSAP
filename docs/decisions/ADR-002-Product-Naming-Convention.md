# ADR-002: Product Naming Convention

| Item   | Value      |
| ------ | ---------- |
| Status | Accepted   |
| Scope  | Naming     |
| Date   | 2026-07-29 |

---

## Context

FSAP 플랫폼에서 여러 제품이 순차적으로 개발될 예정이므로, 제품을 일관되게
식별하고 문서/코드/폴더 전반에서 동일하게 참조할 수 있는 명명 규칙이 필요했다.

## Decision

제품 코드는 다음 형식을 사용한다.

```text
<MATERIAL>-RS-<NNN>
```

- **MATERIAL**: 대상 소재/제품군 (MAT, CARPET, LEATHER, TEXTILE, ...)
- **RS**: 제품 계열 식별자 (봉제 시스템 계열)
- **NNN**: 3자리 순차 번호 (001부터 시작)

예시:

```text
MAT-RS-001      Automotive Mat Edge Binding Sewing System
MAT-RS-002      Next Generation Automotive Mat Edge Binding Sewing System
CARPET-RS-001   Industrial Carpet Edge Binding Sewing System
LEATHER-RS-001  Leather Edge Binding Sewing System
TEXTILE-RS-001  Industrial Textile Edge Binding Sewing System
```

프로젝트명은 `FSAP`, 단계 폴더는 `01_Planning` ~ `06_Business` 형식을 사용하며,
모든 문서에서 동일한 명명을 사용한다.

## Reason

- 소재 접두어로 제품군을 즉시 식별할 수 있다.
- 순차 번호로 세대 구분이 가능하다.
- 플랫폼 확장 시 새로운 소재 접두어만 추가하면 되므로 확장성이 좋다.

## Alternatives Considered

- **단순 순차 번호 (Product-001)**: 소재/제품군 식별 불가로 기각.
- **자유 형식 제품명만 사용**: 문서 간 참조 일관성 확보가 어려워 기각.

## Consequences

- 모든 문서, 폴더, 코드에서 제품 코드를 일관되게 사용해야 한다.
- 신규 제품 추가 시 이 규칙에 따라 코드를 부여한다.

## Validation

- 문서 전반에서 제품 코드 표기 불일치가 없는지 검토한다.

## Related Documents

- README.md — Current Product, Long-Term Product Roadmap
- CLAUDE.md — Naming Convention
- ADR-001 (Platform Architecture)

## Related GitHub Records

- Issue: TBD
- Pull Request: TBD
- Release: v0.1.0
