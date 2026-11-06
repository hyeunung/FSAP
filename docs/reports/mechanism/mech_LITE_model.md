# 모델링부 — LITE 모델 무게 줄이기 (2026-11-06, v2.6.4 → v2.6.5)

**요약**
- 바뀐 부품 2개, 피처 이력만 바꿈: `P_M07_BEAM`(보), `P_DC205_STRIP`(띠). 지운 부품·새 부품·조인트·리지드 그룹·컴포넌트 변화 0.
- **CLI 혼자 열기 242.1 s → 100.1 s**(상한 240 s, 설계 어림 90~130 s 안). 전체 호출 491.2 s → 351.3 s.
- `lite_check.json` check ok: BOM 125행/2,457 같음, 바디 2,649개(보·띠 뺀 2,647개 bbox·무게중심·부피 차 0.000), 모델 bbox 같음(X −2650~1442, Y −2015~2195, Z −900~915.5), 질량 +27.8 g.
- 보: X −2380~1230, Y 120~320, Z 250~650, 부피 34,457,287.3 mm³, 면 80, CoM 차 0.024 mm, bbox 차 0.012 mm(커널 nudge 없어짐, 공칭 복귀).
- 띠: bbox 같음, 부피 602,125.7 mm³(+2.3), CoM 차 0.000 mm, 면 58, cosmetic 나사 M5 ×8.
- 타임라인 error 0. boolean retry는 보 Extrude51~55·Box148 6개 → Extrude52 1개(허용).
- 통로: **CLI**(앱 문서 dirty, path null — 지시서 D-10). 저장 `3D_Modeling/FSAP_v2.6.5.sc`, config.json doc 바꿈.
- 미완 없음.

## 1. 통로·문서 확인
- MCP `running` 빈 목록(막힘 없음). 앱 `inspect_design`: `name FSAP_v2.6.4`, **`dirty: true`, `path: null`**, undo 0, redo 0, revision 635 — 측정부가 본 상태 그대로다.
- 안내서 '문서 확인' 원문 "앱에 연결돼 있고 열린 설계가 `dirty`(저장 안 된 변경)면 `open` 전에 멈추고 보고한다 … 버리지 않는다". 지시서 D-10 원문 "앱 문서가 dirty면 바꿔 끼우지 않는다. 멈춰 보고하거나, 이유를 적고 solidcraft-cli run edit.json --in FSAP_v2.6.4.sc --save FSAP_v2.6.5.sc로 한다."
- 그래서 앱 문서는 열지도 바꾸지도 않았다(앱 쪽 원복·포즈 변경 없음). **보고: 앱에 열린 FSAP_v2.6.4는 지금도 dirty(path null)이다.** 사람이 확인해 주어야 한다.
- 편집은 `solidcraft-cli run model/run_edit.json --in 3D_Modeling/FSAP_v2.6.4.sc --save 3D_Modeling/FSAP_v2.6.5.sc --results --timings`(rc 0, 1,011 s, 백그라운드) 한 번이다. 앞쪽 25단계가 `tools/out/mech_LITE/edit.json`이고, 뒤 5단계는 저장 전 측정이다.
- 명령 뜻은 먼저 작은 빈 설계(t1·t2.json)로 확인했다: `reorder_many` position = 0부터 센 끼울 자리, `roll_to {feature}` → 명령 → `roll_to {}`로 중간에 넣기, `timeline.edit`의 `plane.plane.origin`·`extent.distance`.

## 2. 그린 것(edit.json 25단계)
| # | 명령 | 결과 |
|---|---|---|
| 1 | `timeline.delete OffsetFace20` | 지움(5841) |
| 2 | `timeline.delete SK_M07_BEAM_OUT` | 스케치+Extrude51 지움. 중간 상태에서 Extrude55·Box147 등 failing이 났으나 3~4단계 뒤 모두 풀림(최종 error 0) |
| 3 | `timeline.edit Box16` corner (−2380,120,250), length 3610, width 200 | 1,962 피처 다시 계산(205 s) |
| 4 | `timeline.reorder_many` HB·Extrude53·HK·Extrude54·HT·Extrude55 → 자리 1140 | IN 앞으로 |
| 5~7 | `roll_to Extrude55` → `solid.fillet` R12, 모서리 점 (0,120,250)(0,320,250)(0,320,650)(0,120,650), body P_M07_BEAM → `roll_to` 끝 | Fillet1(1148). fillet 실패 대안(옛 OUT cut)은 쓸 일 없음 |
| 8~9 | `timeline.edit SK_M07_BEAM_IN` 평면 X −2381, `Extrude52` 3612 | |
| 10 | `timeline.delete Hole1~8` | |
| 11~21 | `roll_to Cylinder332` → `timeline.add SK_DC205_TAP`(원점 (0,0,−12.8), r2.1 ×8, X −1750·−1600·−1400·−1250·−1000·−800·−600·−450) → `TAP_DC205` cut +Z 9.8 → `solid.thread` M5 L8.3 cosmetic ×8(면 점 X+2.1, 0, −6.0) → `roll_to` 끝 | 나사 Z −11.3~−3.0 ×8, 바닥 Z −3.0 |
| 22 | `motion.play REST step 0` | moved false |
| 23 | `browser.visibility joints false` | 317 숨김 |
| 24 | `document.metadata.set description` "LITE mechanism: M07 beam history reorder (box, holes, R12 fillet, core) and DC205 strip tap holes as one cut" | |

- 최종 순서: Box16(34) … SK_DC205_TAP(730)·TAP_DC205(731) … HB~Extrude55(1142~1147), Fillet1(1148), SK_M07_BEAM_IN(1149), Extrude52(1150) … Box147(1224)·Box148. 피처 1,999(지움 11, 더함 11).
- 문서 이름: SolidCraft에는 이름 바꾸는 명령이 없고(`document.` 계열은 units·metadata·inspect·revision뿐) 이름은 파일 이름에서 온다 → FSAP_v2.6.5(앞 보고서들과 같음).

## 3. 저장 전 검사(수치, E-16)
- 타임라인: error 0. warning은 전부 전부터 있던 것(6004ZZ·6200ZZ 볼 import, Extrude30, Box132, OffsetFace16·18, ConvertToSheetMetal25·26)과 Extrude52 retry 1개. 보 Extrude51·53·54·55·Box148 retry는 없어졌다.
- 측정(같은 run): 보 34,457,287.33 mm³, bbox (−2380,120,250)~(1230,320,650), CoM (−574.868, 220.028, 449.973), 면 80, Steel, 270.49 kg. 띠 602,125.70 mm³, bbox (−1826,−25,−11.8)~(−391,25,0), CoM (−1108.390, 0, −4.2855), 면 58, A5052. 설계부 빈 설계 시험값과 같다.
- 주변 겹침(E-22, 저장본 v2.6.4·v2.6.5 둘 다 CLI `inspect.clearance`, 이웃 = before bbox ±1 mm 겹치는 바디: 보 68종·띠 16종, truncated false):
  - 겹침: v2.6.4 0, **v2.6.5 0**.
  - unchecked: 보 ↔ 볼트 26개, 띠 ↔ CB5-12_DC205 1개 — 전후 같은 목록. 나사 물림(M-08 의도)이다.
  - 보 ↔ `P_M07_SPLICE_NX` unchecked("facets pass through")는 v2.6.5에서 없어지고 겹침 0으로 판정됐다(결정로그 M07-D9 "보 뒷면 커널 retry(Y 320.0045)로 이음판 NX 겹침 판정 못 함"이 풀림).
- 조인트 자기 점검: 바뀐 조인트·유닛 동작 없음(보 U1_FRAME 고정, 띠 U2_TABLE 고정) — 할 것 없음. 숨김·리지드 그룹·재질은 바디 이름·컴포넌트 그대로라 변화 없음(lite_check 바디별 component 같음).
- 볼트: 바꾼 볼트 없음. 띠 탭 정보는 `bolts.json`이 자체로 들고 있다(설계부 1절).

## 4. 저장 확인·열기 시간
- 저장본 `3D_Modeling/FSAP_v2.6.5.sc` 4,428,047 B(전 4,428,487 B). `tools/config.json` doc → `../3D_Modeling/FSAP_v2.6.5.sc`.
- `run_base.sh` 방식(같은 스크립트: assembly.bom + component.properties 루트 + 볼 컴포넌트, `--timings`)으로 v2.6.5를 CLI 혼자 열었다: 전체 351.3 s, 단계 합 251.2 s → **열기 100.1 s**(전 242.1 s, −59 %). 결과 `tools/out/mech_LITE/model/after_check.out.json`, 판정 `tools/out/lite_check.json` after·check.
- 서명: `ledger.py sigpatch --parts model/sig_parts.json` → 바뀜 2, 없어짐 0, 전체 2,649, doc v2.6.5.

## 5. 해석·임시 STEP
- 새로 힘을 받는 가공품 없음: 보는 단면·길이·구멍이 같고 공칭으로 돌아왔을 뿐(+0.010 %), 띠는 구멍 깊이·지름 같음. exported_steps 없음. 해석 환경 없음(D-16)과 관계없이 대상 0.

## 6. 생성기(실행 규칙 3)
- `tools/gen_v2_m07.py` stage_beam: Box16 고치기(timeline.edit) → 구멍 HB·HK·HT → fillet R12 → IN(X −2381, 3612). 옛 OUT cut 없앰.
- `tools/gen_v2_m07_fix1.py` stage_beam: offset_face 80 없앰(끝판 Box 둘은 그대로).
- `tools/gen_dc2_05.py`: solid.hole ×8 → SK_DC205_TAP 스케치 cut 한 번 + solid.thread ×8.
- 주의: 이 생성기들은 이제 v2.6.5 이력을 만든다. v2.6.4 이전 이력을 다시 만들 때는 git 이전 판을 쓴다. 문법 확인만 했고 생성기를 처음부터 다시 돌려 보지는 않았다.

## 7. 시간·통로
- 통로 CLI(이유 1절). CAD 호출: MCP 4(running, list_commands ×2, inspect_design) + describe 3, CLI 6(작은 시험 2, 편집·저장 1, 열기 측정 1, 겹침 2). 저장본 열기 4번(편집 1, 열기 측정 1, 겹침 v2.6.4·v2.6.5 병렬 2). 가장 긴 열기 = 편집 run의 v2.6.4 열기(약 242 s, 측정부 값), 새 파일 100.1 s.
- 걸린 시간 약 40분(예산 180분).

## 워크플로우 메모
- 큰 모델의 `timeline.edit`(앞쪽 Box16)은 뒤 피처 1,962개를 다시 계산해 205 s가 걸렸다. 앞쪽 피처를 고칠 때는 편집 명령을 한 run에 묶어야 한다(MCP였다면 batch 하나 5분 상한에 걸림).
- `inspect.clearance {bodies:[A,B]}`만 주면 A↔B만 본다(pairs 0). 이웃은 `against`로 꼭 준다.
- `inspect.measure {body}`는 CLI에서 body를 무시하고 전 바디를 돌려 88 s 걸렸다. 바디 하나 재기는 `component.properties`나 결과에서 골라 쓰는 편이 낫다.
