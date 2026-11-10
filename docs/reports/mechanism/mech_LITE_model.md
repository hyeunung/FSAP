# 모델링부 — LITE 모델 무게 줄이기 (2026-11-10, v2.8.9 → v2.8.10)

**요약**
- 형상 변경 0, 부품·컴포넌트 증감 0. 바꾼 것은 피처 이력 세 바디(P_M07_BEAM, P_M02_FRONT, P_M03_FRONT)뿐이다.
- 지시서 명령 기록 `tools/out/mech_LITE/design3/edit_lite3.json`(66단계)을 그대로 쓰고, 저장 전 4단계(대기 포즈·조인트·스케치 숨김·문서 설명)를 붙였다(`tools/out/mech_LITE/edit.json`, 70단계).
- **열기(CLI 잣대) 844.4 s → 396.9 s(−53 %)**. 상한 240 s는 못 맞췄다. 판정은 '줄인 만큼'이다(지시서 예상 360~430 s 안).
- lite_check: 바디 2,969/2,969, BOM 179행/2,616개 같음(차 0행), 모델 전체 bbox 차 0.000. 바뀐 바디는 보 하나(부피 −2.6 mm³, bbox·무게중심 차 0). 앞판 M02 34,586.57, M03 30,123.22 mm³로 전과 같다. → ok true.
- 통로: **CLI**. 앱(MCP)에 열린 v2.8.9가 `dirty: true`(undo 200)였다. 그래서 규칙대로 그 변경은 버리지 않고 앱은 건드리지 않았다. 지시서 단서("앱이 dirty면 CLI run --in v2.8.9 --save")대로 저장했다.
- 미완: 없음. 남은 무게(필렛 띠 탭 Combine 약 118 s, Cylinder1291, 앞판 Y 메움)는 형상을 바꿔야 줄어서 디테일로 넘긴다(설계보고서 mech_LITE_design1.md).

## 1. 연결·통로 (안내서 '연결', WF-121)
| 단계 | 결과 |
|---|---|
| `running` | 빈 목록(막힘 없음) |
| `open v2.8.9` | errors 0, features 3,082. 즉시 끝났다(앱에 이미 열려 있던 문서) |
| `document.revision` / `edit.checkpoint` | revision 6 / checkpoint 40 |
| `inspect_design`(측정·스케치·조인트 끔) | **`dirty: true`, undo 200** |

- 규칙 2·안내서 '문서 확인'은 "dirty면 open 전에 멈추고 보고, 버리지 않는다"이다. 그래서 앱 문서에는 편집·저장·원복을 하지 않았다. 앱의 저장 안 된 변경은 그대로 남아 있다(누가 무엇을 했는지는 모른다. 앞 부서의 측정·포즈 흔적일 수 있다).
- 지시서 단서대로 CLI로 했다: `solidcraft-cli run edit.json --in 3D_Modeling/FSAP_v2.8.9.sc --save 3D_Modeling/FSAP_v2.8.10.sc --results --timings`. rc 0, 벽시계 1,515 s, 명령 643.8 s.

## 2. 바꾼 것 (설계안 지시서 그대로)
| 단계 | 내용 | s |
|---|---|---|
| 0 | `timeline.delete` 63개: Combine40, 보 탭 공구 38(Cylinder1179~1220, 1209~1212 제외), Cylinder1281·1283·1284·1285·1289·1290·1292·989, 앞판 X 메움 782~785·794~797, 다시 뚫기 786~789·798~801 | 174.7 |
| 1~9 | roll_to Cylinder221 → Cylinder65~68·214~217 radius 2.1 | 8.8씩 |
| 10~57 | roll_to Box16 → 스케치 3장 + extrude cut 3(Y10: 원 30, cut 11 / Y12: (299,1159), cut 13 / Z: 원 7, cut 10, targets P_M07_BEAM) | 각 2 미만 |
| 58~62 | roll_to Extrude52 → 핀 join 4(r 2.4, (−126/−114,124,462) h 6.5, (1159,124,273/287) h 8.5, +Y) | 66.6 + 4.0×4 |
| 63~64 | roll_to {} → `solid.combine` P_M07_BEAM ← TAP_P_M07_BEAM_32~35 cut, keep_tools false | 225.4 + 117.8 |
| 65 | `inspect.measure` 세 바디 | 1.6 |
| 66~69 | `motion.play REST 0`(conflicts 0, moved false), `browser.visibility` joints 숨김(410)·sketches 숨김(258), `document.metadata.set description` "LITE mechanism: beam taps moved to sketch cuts after Box16, front plate X holes simplified; geometry unchanged" | — |

- 지울 부품·새 부품·새 조인트·구매품·볼트: 없다. 기계 정의 `tools/machine.json`은 바꾸지 않았다(조인트·행정·유닛 변화 0, E-15).
- 문서 이름: 저장 경로 `FSAP_v2.8.10.sc`에서 이름을 받는다.

## 3. 검증 수치 (E-16, 수치만)
저장 전(단계 65, 편집 결과):
| 바디 | 부피 mm³ (전 → 후) | bbox (전 = 후) |
|---|---|---|
| P_M07_BEAM | 34,452,828.9 → 34,452,826.3 (−2.6, 허용 ±50) | X −2380~1230, Y 120~320, Z 250~650 |
| P_M02_FRONT | 34,586.6 → 34,586.57 | X −139.9~−116.037, Y ±31, Z 55.65~136.545 |
| P_M03_FRONT | 30,123.2 → 30,123.22 | X −1832~−1820, Y ±31, Z 60~134 |

저장본 확인(`tools/out/mech_LITE/after/`, v2.8.10을 CLI로 한 번 열어 BOM·전체 바디·revision·설명 측정):
- revision 1: 저장 안 된 변경이 없다. 설명은 위 문장 그대로다.
- `tools/out/lite_check.json` check: bodies 2,969 → 2,969, bom_rows 179 → 179, bom_total 2,616 → 2,616, bom_diff 0, model_bbox_dmax 0.0, bad 0. 바뀐 바디는 P_M07_BEAM 하나(d_vol 2.6, d_bbox 0, d_com 0)다. 나머지 2,968 바디(사본 포함)는 bbox·무게중심·부피 차가 0이다. ok true.
- 새 겹침: 형상과 모든 바디 자리가 전과 같아서(bbox·무게중심 차 0) 새 겹침 0이다. 과제 범위 inspect.clearance는 따로 돌리지 않았다(바뀐 바디 형상 차 0, E-17·E-19).
- 조인트 자기 점검: 조인트·행정 변화가 없어 해당 없음. 대기 포즈 REST 0 conflicts 0.
- 숨김·리지드 그룹·재질: 바디 증감 0, 재질 그대로(보 Steel 7.85, 무게 270,454.7 g 같음).
- 스크린샷: 찍지 않았다. CLI snapshot은 저장본을 한 번 더 열어야 하고(약 400 s), 형상 변경이 0이다.

## 4. 열기 시간 (전후 실측, 같은 CLI 잣대)
| 문서 | 벽시계 s | 명령 s | 열기 s |
|---|---|---|---|
| v2.8.9 (측정부 base_check) | 983.8 | 139.4 | **844.4** |
| v2.8.10 (after_check) | 533.7 | 136.8 | **396.9** |

- 줄어든 몫은 447.5 s(−53 %)다. 상한 240 s는 넘는다. 안내서 '모델 무게'의 "한 번 했는데도 상한을 넘으면 다시 만들지 않고 남은 것을 보고"대로 남은 것을 적는다.
  - 보 필렛 띠 탭 Combine: 약 118 s
  - roll_to 끝 구간의 나머지 피처
  - 앞판 Y 메움
  - 사본 많은 구매품(BALL-D25.4 ×827 등)의 occurrence 비용
- 측정 표: `ledger.py sigpatch --parts tools/out/mech_LITE/model2/sig_parts.json` → 바뀜 3, 없어짐 0, 전체 2,881. doc v2.8.10, hash 74cab8e98f36c260.

## 5. 못 한 것 / 넘김
- 미완 없음.
- 임시 STEP: 새로 힘을 받는 가공품이 없어서 내보낸 것이 없다(형상 변경 0).
- 디테일로 넘김: 남은 무게(4절). 형상을 바꿔야 줄어든다(필렛 띠 밖으로 탭 옮기기 등).
- 앱의 dirty v2.8.9: 사용자가 확인한다. 저장 안 된 변경을 버리지 않았다.

## 워크플로우 메모
- 앱에 열린 문서가 앞 부서 뒤에 dirty(undo 200)로 남아 있었다. 그래서 모델링부가 MCP로 그리지 못하고 CLI로 갔다. 읽기 부서가 MCP로 잰 뒤 `edit.restore_checkpoint`로 되돌리지 않은 것으로 보인다(확인 못 함).
- `inspect_design`은 측정·스케치·조인트를 꺼도 1.08 MB라 dirty 하나 보려고 너무 크다. 가벼운 dirty 조회 명령이 있으면 좋다.
