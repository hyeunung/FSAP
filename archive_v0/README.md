# archive_v0 — v0.x 참고본 (2026-10-30 ~ 2026-11-02)

v0.1.0~v0.10.1은 전체 구동 개념 없이 과제를 하나씩 풀어 쌓은 모델이다. 핵심 가정(헤드 자체 이송 없음, 기계 서보가 매트를 한 땀씩 옮김)이 벤치마크와 반대여서 동결했다(결정로그 C-12, `docs/concept/v1-drive-concept-discussion.md`).

v1.0은 요구서 0-8(확립 2026-11-03)로 빈 파일에서 새로 시작한다. 여기 것은 참고만 한다 — 좁은 코 노루발·침판(r 8.5), 노루발 슬릿 센서 자리, 동심 진공 링 같은 따져 본 내용은 새 개념에 맞을 때만 가져온다.

| 폴더 | 무엇 |
|---|---|
| `3D_Modeling/` | v0.0.0~v0.10.1 설계 파일(.sc) |
| `docs/bom/`, `docs/review/` | BOM·설계검토서 |
| `docs/reports/mechanism/`, `docs/reports/detailing/` | 부서 보고서 |
| `tools/` | 형상 생성기 `gen_*.py`, 동작 상태 `motion_states.json`, 옛 실행 인자 `workflow-args.json` |
| `fea/` | 해석 케이스·결과 |
| (깃 밖) `tools/out_v0/` | 점검 원본·전체 회귀 기록(`mech_regression_v0101/`) |
