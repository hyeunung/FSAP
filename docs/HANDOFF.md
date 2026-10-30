# 이어가기 메모 (2026-10-30 Windows → 다음 컴퓨터)

엔진 MechDesign_Engine의 구동부 모델링 워크플로우(`workflows/modeling_round.js`, mode mechanism)를 이 컴퓨터에서 돌리다가 사용자 요청으로 멈췄다. 여기까지 한 것을 브랜치 `modeling/mat-rs-001`에 올렸다.

## 어디까지 했나

| 과제 | 상태 | 설계 파일 | 보고서(`docs/reports/mechanism/`) |
|---|---|---|---|
| 준비 | 완료: 매트 모형 3종(임시값), 조인트 골격, 동작 연구 7개 | `FSAP_v0.1.0.sc` | `mech_prep_check.md`, `mech_prep.md` |
| T01 매트 잡기·회전 | **해결**: 동심 진공 원판 + 링1·링2, DGM200R 회전, X·Y 레일. 수정 1회(회전 키 단위, 링2 t3→t5) | `FSAP_v0.2.1.sc` | `mech_T01_*`, BOM `docs/bom/FSAP_v0.2.1_*.csv`, 설계검토서 `docs/review/FSAP_v0.2.1_review.md` |
| T02 봉제 헤드 홈 진입 | **모델링 끝, 검증 중 멈춤**: 헤드 임시 형상, 침판·노루발 r8.5 노즈, SLA 바인더, 헤드 받침. 모델링 자체 검사 통과, 해석 통과. 검도·체결(검증)이 끝나지 않았다 | `FSAP_v0.3.0.sc` | `mech_T02_measure·concept1~3·select·model·fea.md` |
| 구매품 STEP | **실물 교체**: HFS8 형재 10·LHFR16 6·PSFJ16-150 6(미스미 STEP). SV2R20·ZH10DS는 형번이 없어 다시 정해야 함, DGM200R·CJ2B16은 제조사 STEP 필요 | `FSAP_v0.3.1.sc`(최신, `tools/config.json` doc) | 결정로그 V031-01~05 |
| T03~T07 | 시작 안 함 | — | — |

- 결정은 `docs/decision-log.md`(C-01~C-09, P-01~P-06, T01-*, T02-*), 모르는 수치·STEP 대기는 `docs/waiting-list.md`(D-01~D-31).
- 엔진 개선 후보(엔진 폴더는 건드리지 않아 여기 모음): `docs/reports/engine-candidates.md`(WF-051~056).
- 형상은 생성 스크립트로 다시 만들 수 있다: `tools/gen_motion_prep.py` → `gen_t01_mech.py` → `gen_t02_mech.py`.
- **올라가지 않은 것**: `tools/out/`(약 124 MB, 측정·검사 원본 JSON·프로브 스크립트)는 깃 제외다. 보고서가 그 파일을 원본으로 가리키지만 다른 컴퓨터에는 없다. 결론·수치는 보고서에 다 적혀 있다.

## 다른 컴퓨터에서 이어가기

1. 받기
   - `git clone https://github.com/hyeunung/FSAP.git` 후 `git checkout modeling/mat-rs-001`
   - 엔진 `git clone https://github.com/hyeunung/MechDesign_Engine.git`(**읽기만 한다. 엔진 폴더·저장소에는 아무것도 쓰지 않는다**, CLAUDE.md)
2. 준비(엔진 README "다른 컴퓨터에서 쓰기")
   - SolidCraft 앱·`solidcraft-cli`(이 컴퓨터는 0.26.1). 가능하면 Claude에 SolidCraft MCP 연결(허용 경로에 FSAP 폴더). 없으면 CLI로 한다(실행 규칙 (2)).
   - 파이썬 3, `gh`(PR·머지할 때).
   - 해석 환경 `engine/fea/.venv`는 엔진 폴더 안에 설치된다. 설치할지는 사용자가 정한다. 없으면 손계산으로 진행한다(자료대기 D-16).
3. 워크플로우 인자: `tools/workflow-args.json`
   - `root`, `engineRoot`, `tmpAscii`를 그 컴퓨터 경로로, `date`를 그날 날짜로 바꾼다. Mac이면 `hostPy`를 `python3 -B`로.
   - `shellNote`에 이번 실행에서 찾은 함정·규칙이 모두 들어 있다(엔진 읽기만, CLI 사용법, 임시값으로 준비됨, 회전 키는 도, matcheck BOM 없음 처리, 미스미 STEP 허락).
   - 과제는 T02~T07. T02는 측정 단계가 "이미 됨"을 먼저 판정해, 되면 구상·모델링을 건너뛰고 검증으로 간다.
4. 실행: Claude Code에서 "엔진으로 FSAP 이어서 모델링해줘, 인자는 tools/workflow-args.json" — `Workflow({scriptPath: "<엔진>/workflows/modeling_round.js", args: <그 JSON>})`.

## 사용자 결정 대기 (모아 둔 것)

| # | 무엇 | 출처 |
|---|---|---|
| 1 | **재봉 헤드 기종 조건**: 옆(+Y)에서 들어오는 긴 실린더 베드(바늘–기둥 ≥ 620, 폭 ≤ 100, 높이 ≤ 57.95, 길이 690), 노루발 자동 들기 ≥ 10, 톱니 이송 없음(또는 끌 수 있음). 기성품이 없으면 개조·주문 제작(금액 미확인). 아래로 내려오는 베드면 T01 안이 안 되고 차순위 C3로 | T01 선정 7-2, T02 선정 8절, D-10 |
| 2 | 바인더를 전문 업체에서 살지, `P_T02_BINDER`(SLA)로 만들지 | T02 선정 8절 |
| 3 | 중간 크기 매트(폭 600~740)를 시험 매트(요구서 6-4)에 더할지. 링 규칙상 잡는 힘이 모자라는 구간 | T01 선정 1-3 |
| 4 | 미스미 STEP 받기에 쓸 크롬(Mac·Windows 두 대가 연결돼 있음). 받을 형번은 D-17~D-31 | 2026-10-30 세션 |
| 5 | 실측 자료: 가장 좁은 홈 폭·깊이·바닥 반경(D-02·D-03), 매트 크기(D-01), 두께(D-04), 테이프(D-06), 작업 영상(D-07), 전임 기계(D-09) | 자료대기 |

## 알아 둘 것

- 요구서 8-5는 "버전이 바뀔 때만 커밋·푸시"인데, 엔진의 문서 단계는 과제가 끝날 때 문서만 커밋한다(커밋 `4951743`). 엔진 개선 후보로 남길 일(엔진은 사용자가 엔진 작업을 시킬 때 고친다).
- 이 컴퓨터는 git 작성자 설정이 없어 커밋마다 `-c user.name=hyeunung -c user.email=68310338+hyeunung@users.noreply.github.com`을 줬다.
