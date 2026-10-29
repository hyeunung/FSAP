# FSAP MAT-RS-001 — 자동차 매트 랏빠 자동 봉제기 기구 개발

자동차 매트의 가장자리에 랏빠(바인딩) 테이프를 감싸 자동으로 봉제하는 기계(MAT-RS-001, Automotive Mat Edge Binding Sewing System)의 **기구 개발 저장소**다. 작업자는 매트를 올리고 시작만 누르고, 그 뒤 외곽 한 바퀴 봉제는 사람 손 없이 자동으로 돈다.

- 벤치마크: RI.MA.C. **R375X**(이탈리아). 구조는 이를 따르고, **좁은 홈까지 깔끔한 마감**과 **눌림자국 없음**에서 앞선다. 자세히는 [`docs/benchmark.md`](docs/benchmark.md).
- 기구 모델링은 공통 엔진 **MechDesign_Engine**(`hyeunung/MechDesign_Engine`)의 워크플로우로 한다. 이 저장소는 엔진의 L4(프로젝트 설정)다.
- FSAP(Flexible Sewing Automation Platform)는 이 기계에서 시작해 다른 유연 소재 봉제로 넓히려는 제품 계열 이름이다([ADR-001](docs/decisions/ADR-001-Platform-Architecture.md)).

## 지금 상태 (2026-10-30)

- 대화 단계. 설계 요구서 초안을 썼다. 모르는 치수(홈 폭·반경, 매트 크기, 테이프 폭 등)는 [자료대기](docs/waiting-list.md)에 있다.
- 기술 방향은 [결정로그](docs/decision-log.md) C-01~C-09.
- CAD는 **SolidCraft**(C-09). 이 컴퓨터의 실행 준비(MCP 연결·해석 환경)는 자료대기 D-16.
- 모델 없음. 사용자가 "모델링 해줘"라고 하면 엔진이 과제 목록 → 구동부 → 디테일링 → 회귀 → 보고 → 회고를 돈다.

## 폴더

엔진 기본 배치(MechDesign_Engine `templates/project-layout.md`)를 따른다. 폴더·파일 이름은 영문(Fusion import가 한글 경로를 못 읽음).

| 경로 | 무엇 |
|---|---|
| `docs/design-requirements.md` | 설계 요구서. 엔진의 모든 부서가 이 문서로 판단한다 |
| `docs/decision-log.md` | 결정로그(기계 결정과 이유) |
| `docs/waiting-list.md` | 자료대기 목록(측정·외부 자료·시험·사용자 결정, D-번호) |
| `docs/benchmark.md` | R375X·비슷한 기계·특허 조사 |
| `docs/reports/` | 워크플로우 보고서 |
| `docs/decisions/` | 예전 ADR(001~004). 새 결정은 결정로그에 쓴다 |
| `3D_Modeling/` | SolidCraft 설계 파일 `FSAP_v<버전>.sc`(요구서 8-2) |
| `tools/` | 점검 설정 `config.json`(cad: solidcraft). SolidCraft는 동작 검사를 설계 안 동작 연구로 해서 기계 전용 동작 모듈이 없다. `tools/out/`은 깃 제외 |
| `purchased-step/<형번>/` | 구매품 실제 STEP |
| `fea/cases/`, `fea/results/` | 해석 케이스·결과(솔버는 엔진 `engine/fea/`) |
| `deliverables/<문서 번호>/` | 납품 STEP·조립 STEP·도면. 완성본일 때만 |

## 다른 컴퓨터에서

1. 이 저장소와 MechDesign_Engine을 함께 받는다. 엔진 쪽 준비(해석 환경 설치, CAD 연결)는 엔진 README "다른 컴퓨터에서 쓰기".
2. Claude Code로 열면 `CLAUDE.md`가 읽힌다.

## Git

- `main`에 바로 커밋하지 않는다. 작업 브랜치에서 하고 PR로 합친다.
- 설계 버전이 바뀔 때만(새 번호 .sc 저장) 커밋하고 푸시한다(요구서 8-5). 모델링 작업 브랜치는 `modeling/mat-rs-001`.
- 변경 이력은 [`CHANGELOG.md`](CHANGELOG.md).
