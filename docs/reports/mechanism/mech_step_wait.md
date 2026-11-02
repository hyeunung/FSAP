# STEP 대기 재시도 (v1.0 첫 라운드, 2026-11-03, 엔진 v3.7.1)

요약
- 대상 모델: 3D_Modeling/FSAP_v1.0.0.sc (tools/config.json doc)
- 'STEP대기_' 임시 형상: 0개 (document.inspect 이름 목록에 STEP 문자열 없음, tools/out/sw_out.json)
- swap 없음, waiting 없음. 구매품 CAD 사이트 로그인 필요 없음 → login '확인 못 함'
- 저장 안 함, 편집 안 함(CLI eval 읽기만, 저장본 불변). MCP·브라우저 안 씀.

근거: E-10 임시 형상은 'STEP대기_<형번>'로 둔다. v1.0.0은 빈 설계에서 만든 골격(유닛 상자·매트 모형·조인트)이라 구매품이 아직 없다.

## 워크플로우 메모
- `solidcraft-cli script`는 컴포넌트가 있는 설계에서 "not supported yet (#886)"로 실패. 목록은 `eval` + `document.inspect`로 대신했다.
