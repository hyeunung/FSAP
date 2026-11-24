# 모델링부(회귀 수정) — J_U7_HGT 대기값 6 → 0, 연구 대기 키 보강 (v2.28.0 → v2.28.1, 2026-11-24)

## 요약
- 저장: `3D_Modeling/FSAP_v2.28.1.sc`(md5 eac4b525…, MCP 임시 폴더에 save 뒤 복사, 같음). `tools/config.json`·`tools/machine.json` doc 갱신.
- 형상 변경 없음. 바뀐 것은 조인트 값 하나(J_U7_HGT 6.0 → 0.0)와 동작 연구 11개의 키뿐. 컴포넌트 증감 0 → 번호 마지막 자리 +1(E-05).
- 원인: v2.28.0이 J_U7_HGT 6.0으로 저장됐고, REST 연구에 J_U7_HGT 키가 없어 `motion.play REST 0`이 되돌리지 못했다.
- 고침: ① `joint.drive J_U7_HGT 0` ② REST에 키 5개(J_U7_HGT·J_U4_X·J_U2_FLAP·J_U2_FLAP_LATCH_A·B), CYCLE_* 10개 연구에 키 12개씩(위 5 + J_U4_STOP·J_U7_KIT_T06·T10·T16·J_WP_T06_Z·T10_Z·T16_Z) 대기값 상수로 더함. 이미 있던 키는 그대로 뒀다.
- 확인: HGT 6으로 옮긴 뒤 REST 0을 재생하면 HGT 0이 되고, 조인트 679개 값이 v2.28.0 저장값과 같다(HGT만 0). CYCLE_V 0단계도 HGT 0·U4_X 0으로 되돌린다.
- 되돌린 48바디 둘레의 겹침: 새 겹침 0. 기준선 1쌍(관 이음 TU0604_M08P_U6 ↔ TU0604_M08P_U6_L 113.1 mm³)은 v2.25.2(HGT 0)와 같은 자리다.
- 미완: 없음. RX-16 입력(헤드 밑 여유)은 이번 일의 범위가 아니다.

## 근거 규칙
- E-05 번호 정하기: "새 컴포넌트가 생기거나 없어지면 가운데 자리 +1·마지막 0, 아니면 마지막 자리 +1" → v2.28.1.
- 안내서 '동작 상태 초기화': "저장 전에는 항상 이 포즈로 돌려놓는다". REST 연구가 HGT를 키로 갖지 않아 이 규칙이 지켜지지 않았다. 그래서 키를 더했다.
- machine.json 대기값(`rest`): J_U7_HGT 0, J_U4_X 0, J_U4_STOP 0, J_U5_FLOAT 0, J_U2_FLAP 0, LATCH_A·B 0, J_U7_KIT_T06 −2000, T10 0, T16 −2200, J_WP_T06_Z −2500, T10_Z 0, T16_Z −2600.
- 실행 규칙 19: 저장 전에 조인트·스케치 글리프를 숨긴다.

## 1. 통로·문서 확인
- 앱(solidcraft 40328)이 켜져 있어 MCP를 썼다. `running` [] → `inspect_design`: 열린 문서 FSAP_v2.28.0, dirty false.
- `3D_Modeling/`은 MCP 허용 폴더 밖이다(`open` 거부 문구). 그래서 앞 회차들처럼 저장본을 MCP 임시 폴더에 `base_regfix_v2.28.0.sc`로 복사해(md5 같음) 열었다. 같은 경로를 다시 열면 디스크에서 읽지 않으므로 다른 이름으로 복사했다.
- 첫 `open`은 MCP 호출 시간 초과로 돌아왔고, 그때 MCP 서버(12200)가 끊겼다가 새 서버(32572)로 다시 붙었다. 앱이 막힌 것은 아니어서 앱은 다시 켜지 않았다. 열기는 끝나 있었다: 이름 FSAP_v2.28.0, dirty false, undo 0, 피처 4,321, 타임라인 error 0·warning 272.
- `edit.checkpoint` 2를 먼저 잡았다.

## 2. 고친 것
| 단계 | 명령 | 결과 |
|---|---|---|
| 1 | `joint.drive {J_U7_HGT, 0}` | moved true, 0.0 |
| 2 | `motion.study {study, keys}` ×11(`tools/out/mech_regfix/r3/studies_cmds.json`, 4.1 s) | 아래 표 |
| 3 | `motion.play REST 0`, `browser.visibility` joints·sketches 숨김, `document.metadata.set description` | ok |
| 4 | `save {path: …/solidcraft-mcp-32572-2f1dd8d0/FSAP_v2.28.1.sc}` → `3D_Modeling/`로 복사 | 66,431,323 B, 이름 FSAP_v2.28.1 |

| 연구 | 단계 수 | 키 수 전 → 후 | 더한 대기 키 |
|---|---|---|---|
| REST | 1 | 234 → 239 | J_U7_HGT 0, J_U4_X 0, J_U2_FLAP 0, LATCH_A 0, LATCH_B 0 |
| CYCLE_S·L·G1·G2·V·W1·W2·P1·P2·V2 | 450~716 | +12씩 | 위 5 + J_U4_STOP 0, KIT_T06 −2000, KIT_T10 0, KIT_T16 −2200, WP_T06_Z −2500, WP_T10_Z 0, WP_T16_Z −2600 |

- J_U5_FLOAT는 모든 연구에 이미 키가 있다. CYCLE_G2·P2·V2의 0단계 값 10은 앞 연구(G1·P1·V)의 끝 자세를 이어받는 값이어서 바꾸지 않았다.
- REST는 KIT·WP_T*·U4_STOP 키를 이미 갖고 있었다.
- MAINT_HEAD·MAINT_U7·BIND_U7·SEAM_U7는 대기 연구도 사이클 연구도 아니어서 손대지 않았다(지시 범위: REST·CYCLE).

## 3. 확인(수치)
- `tools/out/mech_regfix/r3/rest_play_test.json`: HGT 6 → REST 0 재생 → `joint.list` 679개. v2.28.0 저장값(reg26 jointlist_40911)과 다른 값 0개(HGT만 0으로 기대값과 같음), unmoved [].
- `cycle_play_test.json`: HGT 6, U4_X 50으로 옮긴 뒤 CYCLE_V 0 재생 → HGT 0.0, U4_X 0.0, U4_STOP 0.0, FLAP 0.0, LATCH_A 0.0, KIT_T10 0.0, WP_T06_Z −2500. 이어서 REST 0으로도 같다.
- 겹침(`clr.json`): 되돌린 48바디를 HGT 0 자리 둘레 20 mm 안의 53바디와 비교(skip_within component, 43쌍 잼, truncated false). 겹침은 1쌍뿐이다: TU0604_M08P_U6 ↔ TU0604_M08P_U6_L 113.1 mm³(X −350~−344 · Z 210.3~214.3, Ø6 관 끝 4 mm 맞물림 = π·3²·4). 같은 bbox가 v2.25.2(reg25 bodies_v2252: U6_L Z 155.65~214.3)에도 있어서 이번 변경이 만든 것이 아니다. HGT 6이었던 v2.28.0에서는 관 둘이 6 mm 어긋나 있었다. 이번에 이음 자리가 원래대로 돌아왔다.
- 재질·리지드 그룹·볼트: 형상·체결 변경이 없어 대상이 없다. 힘을 받는 바꾼 가공품이 없어 임시 STEP도 없다.

## 4. 워크플로우 메모
1. MCP `open`(65.8 MB)이 호출 시간 초과로 돌아온 뒤 MCP 서버가 바뀌었다(12200 → 32572). 허용 임시 폴더도 같이 바뀌어서, 저장은 새 서버 폴더에 했다. 열기는 앱에서 끝나 있었다(약 150 s 안).
2. REST에 키가 없는 조인트는 `motion.play`로 되돌릴 수 없다. 새 조인트를 만드는 과제는 REST와 CYCLE_* 0단계에 대기 키를 함께 넣어야 한다. 이번처럼 회귀에서야 드러나지 않게 하려는 것이다.

## timing
- 걸린 시간 약 10분, CAD 호출 15, 파일 열기 1(MCP, 가장 긴 열기 약 150 s), 브라우저 0, 앱 재시작 0.
