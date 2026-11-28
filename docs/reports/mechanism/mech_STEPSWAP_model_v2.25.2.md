# 모델링부 STEPSWAP r5 — HFS8-80160-1090 (v2.25.2, 2026-11-24)

요약
- 결과: **바꿀 것 없음 — 저장하지 않음.** v2.25.2에 살아 있는 `STEP대기_HFS8-80160-1090_*` 바디는 0개다. 기둥 2개는 이미 v2.5.6 STEPSWAP에서 미스미 실물 STEP `HFS8-80160-1090_M07` :1·:2로 바뀌어 있다(자료대기 D-128 'STEPSWAP(v2.5.6)' 기록과 같음).
- 선정 보고서(mech_step_wait.md 4행)의 "모델에 STEP대기_ 2개 남음"은 저장본 `document.json`·`cache/model.json`의 이름 검색에서 나왔다. 그 파일에는 지운 임시 바디의 **이력 이름**(타임라인 깊이 697~751, 피처 5274·5277이 만든 것, 뒤에서 지워짐)이 남아 있어 살아 있는 바디처럼 셌다.
- 판정 근거: 앱에 열린 문서 'FSAP_v2.25.2'(경로 Temp/solidcraft-mcp-40196-3ada6fd0/check_v2.25.2.sc, `cmp`로 3D_Modeling/FSAP_v2.25.2.sc와 바이트 같음, dirty false)에서 `measure {names_only}` 바디 3,549개 중 HFS8-80160 이름은 실물 2개뿐, `STEP대기_HFS8-80160` 0.
- 실물 기둥 bbox(세계, REST): :1 X −2380~−2300 · Y 120~280 · Z −840~250, 부피 4,253,268 mm³, 면 310 / :2 X 1270~1350 · Y 120~280 · Z −840~250, 같은 부피. (:2 X는 v2.5.6 때 1150~1230 → 뒤 라운드 틀 변경으로 옮겨짐.)
- 완료 판정: 지시 형번 STEP대기_ 0 — 이미 충족. 형상 변경 0이라 새 겹침 0(검사할 바뀐 바디 없음, E-17).
- 미완: 없음. 외부: 없음.

## 1. 통로·문서 확인
- `running` → 빈 목록. MCP `inspect_design` 응답: 문서 이름 FSAP_v2.25.2, dirty false.
- 열린 파일이 config.json doc(v2.25.2)와 바이트 같아서 다시 `open`하지 않았다(13~27분 절약). 편집·포즈 변경 없음 → checkpoint·원복·save 없음.
- 번호: 형상이 안 바뀌어 새 번호 없음(version_bump none). config.json doc 그대로 v2.25.2.

## 2. 남긴 기록
- `tools/out/mech_STEPSWAP/edit.json` = `[]`, `edit_meta.json` = {base v2.25.2, result null}. 지난 회차(r4, v2.6.8) 기록은 `edit_v2.6.8.json`·`edit_meta_v2.6.8.json`, 보고서는 `mech_STEPSWAP_model_v2.6.8.md`로 옮겨 남김.
- 측정 표(서명) sigpatch: 바뀐 바디 없음 → 부르지 않음.
- BOM·자료대기: D-128에 이미 'STEPSWAP(v2.5.6) 실물 STEP으로 바꿈'이 적혀 있어 고칠 것 없음.

## 워크플로우 메모
- STEP 대기 재시도(선정)가 저장본 zip의 이름 목록으로 남은 임시 형상을 세면, 지운 바디의 이력 이름까지 세어 이미 끝난 교체를 다시 과제로 만든다. `cache/model.json`의 `model_bodies`도 타임라인 깊이별 이력이라 같다. 살아 있는 바디는 `measure {names_only}`(앱) 또는 CLI `inspect.measure names_only`로 세야 한다.
