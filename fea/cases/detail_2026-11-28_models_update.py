# -*- coding: utf-8 -*-
"""fea/models.json에 디테일링 2026-11-28 해석부가 새로 본 부품 줄을 더한다(E-18: 표에 없는 부품은 실제 조립 경계조건으로 정해 더한다).
옛 줄은 바꾸지 않는다(모델 변경 0). L 브래킷 줄에는 t4 재검토 메모만 더한다. 다시 돌려도 같은 결과(키가 있으면 덮어씀)."""
import json
P = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/models.json'
m = json.load(open(P, encoding='utf-8'))
parts = m['parts']
CASE = 'cases/detail_2026-11-28_handcalc.py'
CRIT = {'value': '운전 SF 3, 오조작 SF 2, 3배 넘으면 과사양. 처짐은 6-2 미정(D-08) -> 기록', 'source': '요구서 6-1(M-09 기본값)'}
ST = '손계산 fea/results/detail_2026-11-28_handcalc.json. FEA 못 함 — 환경 없음(D-16). 형상은 tools/out/detail/stepout STEP 꼭짓점 + signatures bbox(v2.30.6)'
new = {
 'P_M08_LC_BRKT_FR_SM_1·_2': dict(
     fixed='레일 쪽 다리(Y -1524~-1520, X 300~360)가 HFS8-4080-2680_M07 · -2555_M04 -Y 면에 CB5-12 x2(X 315, Z 간격 40). 굽힘 구석 t+R 고정 외팔(M07-K1과 같은 모델, Kt 1.3)',
     contact='기둥 쪽 다리(X 356~360, Y -1595~-1520)가 기둥 HFS8-4080-1175_M08_FR -X 면에 CB5-12 x2(Y -1580)',
     load='기둥 꼭대기 Z 805에 기대는 손 100 N(D-38 임시) X·Y 각각. 두 단(Z -290 · -52, 간격 238) 반력 360.1 · 460.1 N',
     status=ST + '. t4: X 기댐 SM_2 1.38 · SM_1 1.96, -Y 당김 2.01(오조작 기준 2 미달). t6면 3.38 · 4.80 · 5.15'),
 'P_M08_LBRK_R1~R3_SM': dict(
     fixed='다리 하나가 HFS8-80160-1090_M07 -Y 면에 CB5-16 x1(구석에서 20)', contact='다른 다리가 뒤 기둥 HFS8-4080-1175_M08_R -X 면에 CB5-16 x1',
     load='기둥 꼭대기 손 100 N(D-38 임시). 세 단(Z -300 · 150 · 600) 가운데 맨 위 단 145.6 N',
     status=ST + '. t6 SF 52.0(과사양), t4 R4면 11.2'),
 'P_M08_LBRK_H1·H2_SM + HNTT8-5(HMI 팔 뿌리)': dict(
     fixed='세운 다리가 받침판 P_M08_HMI_MOUNT_ML(Y 110)에 CB5-16 x1(구석에서 30), 누운 다리가 팔 HFS8-4080-570_M08_HMI 윗면·밑면 홈에 CB5-16 x1 + HNTT8-5(구석에서 25)',
     contact='팔 끝면(Y 110)이 받침판에 맞닿음(누르기만). 받침점 팔 밑 모서리 Z 400, 위 홈 Z 480(레버 80). 홈이 팔 축(Y)과 나란해 당김은 T너트 마찰(예압 4 kN x 0.15 = 600 N, D-54)만 받는다',
     load='패널 2.0 kg(설계안 임시 — 모델 U8_HMI_PANEL 4.28 kg은 기본 재질이라 뺌) + 판 1.156 + 팔 1.716 kg. 운전 x3 g / 운전 1 g + 누름 30 N / 오조작 1 g + 손 100 N(패널 끝 Y -522)',
     status=ST + '. 위 브래킷 당김 864.6 / 525.2 / 1,078.2 N -> T너트 미끄럼 SF 0.69 / 1.14 / 0.56, 세운 다리 t6 2.39 / 3.93 / 1.91(t4면 0.82 / 1.35 / 0.66)'),
 'P_M08_HMI_PLATE_SM': dict(
     fixed='플랜지(X 1163~1165, Y -465~-400)가 팔 -X 면에 CB5-12 x2(Y -431, Z 420 · 460) + HNTT8-5', contact='세운 판(Y -465~-463, X 1163~1442)에 HMI 패널. 팔 끝면과는 틈 3',
     load='운전: 화면 누름 30 N(설계안 임시) 가운데 X 1306 · 먼 끝 X 1442. 오조작: 손 100 N 같은 자리. 굽힘선 Kt 1.3, 플랜지 유효 폭 100(볼트 2 + 45도)',
     status=ST + '. t2: 누름 30 N 5.24 / 2.69(플랜지 3.19 / 1.63), 손 100 N 1.57 / 0.81(플랜지 0.96 / 0.49). t4면 손 먼 끝 3.23(플랜지 1.96)'),
 'P_M08_HMI_MOUNT_ML': dict(fixed='보 앞면 Y 120에 CB5-16 x4(물림 8)', contact='팔 끝면·L 브래킷', load='팔 뿌리 모멘트(위와 같음)', status=ST + '. 볼트 당김 240 N/개, 암나사 전단 28.9 · 분리 16.7. 판은 보 면에 맞닿아 굽힘 없음'),
 'P_M08_LC2F_BRKT_SM_1·_2': dict(
     fixed='긴 다리(X -2303~-2300)가 기둥 HFS8-4080-1650_M08_FL -X 면에 CB5-12 x1(Y -1580)', contact='짧은 다리(Y -1561~-1558)에 F39-LSGF + 커튼 2E(CB5-6 x1)',
     load='운전 커튼 1.14 kg(모델 값, 기본 재질 — 카탈로그 값 대기) x3 g, 두 받침. 오조작 손 100 N(커튼 가운데, 두 받침이 50 N씩)',
     status=ST + '. 손 4.76(한 받침 전부면 2.38), 볼트 1개 돌림 마찰 2.96(3 g)'),
 'P_M08_LC_JOINT_FL_WJ': dict(fixed='HFS8-4080-510_M07 -X 면 CB5-12 x2(Y -1500, Z -700 · -440)', contact='기둥 HFS8-4080-1650_M08_FL -X 면 CB5-12 x2(Y -1580)',
     load='기둥 꼭대기 Z 810 손 100 N X(판 면 밖). 볼트 짝힘 530.8 N, 띠 팔 71.5 · 유효 폭 130', status=ST + '. 48.7 MPa SF 4.01'),
 'P_RX12C2_PANEL_PX': dict(fixed='HFS8-4080-166_RX12C2 x7(Y -100~1500, 가장 넓은 칸 260) + HFS8-4080-1760 위에 얹힘', contact='윗면 매트',
     load='오조작 손 100 N 칸 가운데(유효 폭 130, 볼 구멍 판 응력 계수 1.56 — mech_M04R와 같은 값)', status=ST + '. 29.2 MPa SF 7.01, 처짐 0.27. t3면 3.94 · 0.65'),
 'P_RX15_TUCK_ARM(+접기 실린더 로드)': dict(fixed='CJ2B16-60SZ_RX15_TUCK 로드 끝 M5(Y 5, Z -30)에 나사 물림', contact='접기 판 귀를 CB5-12(Y -12, Z -18)로 묶음. 편심 20.8',
     load='운전 접는 저항 10 N(임시, D-06 미정). 오조작 걸림 = 전 추력 80.5 N(0.5 MPa - 스프링 20 N)', status=ST + '. 로드 M5 골 굽힘 6.28 / 0.78(로드 내력 205. 450이면 13.8 / 1.71)'),
 'P_RX15_TUCKER': dict(fixed='귀(X 192~192.8, Z -24~-10)가 볼트 머리와 팔 사이에 물림. 머리 가장자리 Z -13.75', contact='레일(Y -16~-8, t0.8)이 판넬 장공 안에서 미끄럼',
     load='위와 같음. 귀 굽힘선 폭 8, 팔 4.15(머리 가장자리)~8.4(볼트 중심)', status=ST + '. 운전 9.66(4.77), 걸림 1.20(0.59). 레일 좌굴 6.59. SUS304-CSP 1/2H 내력 470 임시'),
 'P_RX15_PIN': dict(fixed='P_RX15_CUT_SLIDE에 7.5 물림(Y -83.5~-76)', contact='테이프 꼬리가 핀 바깥 30 구간에 감김', load='테이프 당김 2~5 N(임시, D-06). 외팔 39.5, 하중 중심 팔 24.5',
     status=ST + '. SUS304: 2 N 3.29 / 5 N 1.31, 처짐 0.07~0.16. 담금질 핀이면 9.6 이상'),
 'P_RX15_FEED_CLAW': dict(fixed='발(X 322~322.3)이 블록에 CB5-12', contact='끝이 테이프 밑면에 닿음(모델은 닿음 0)', load='판 스프링 t0.3 폭 5 길이 10.6, 20도. 끄는 힘 2 N(임시)',
     status=ST + '. handcalc beam: 휨 0.2 mm SF 3.04, 0.5 mm 1.22. 끄는 힘 2 N 4.86, 9.7 N에서 굽음'),
 'P_RX15_CUT·TUCK·FEED_BASE': dict(fixed='판넬 밑면에 매달림', contact='실린더 코 너트', load='실린더 추력 100.5 N(행정 끝마다 걸림 = 운전), 팔 18', status=ST + '. 벽 t4 13.0 MPa SF 14.95'),
 'P_RX15_FEED_SLIDE': dict(fixed='로드 너트 2개 사이', contact='POM', load='100.5 N', status=ST + '. 좌면 3.3 MPa SF 18.3'),
 'P_M02·M03_WHEEL_TREAD': dict(fixed='바퀴 몸 Ø100에 붙음(살 10)', contact='매트', load='누름 30~100 N(D-92), 접선 58.3 N', status=ST + '. 100 N: 반폭 6.46, 최대 0.39 MPa, 변형률 0.069(한도 0.25). 매트 자국은 요구서 7절'),
 'P_M03_IDLER_WASHER_I·O': dict(fixed='아이들러 축 끝 CB5', contact='베어링 안륜', load='M5 예압 4 kN', status=ST + '. 36.7 MPa SF 5.58'),
 'P_F01_SPRING_SEAT_N·P': dict(fixed='축 PSFJ16', contact='스프링', load='오조작 453 N 전부(보수)', status=ST + '. 60.4 MPa SF 3.39'),
 'P_M06_ROLL_WASHER': dict(fixed='롤 축 끝 볼트', contact='롤 허브', load='손 100 N', status=ST + '. SF 15.4'),
 'P_M06_G1·TOP_ROLLER': dict(fixed='핀 Ø8', contact='테이프', load='손 100 N', status=ST + '. 면압 0.35 MPa'),
 'P_RX12C1_FLAP_BAR_XP': dict(fixed='판에 CB5-12 줄', contact='경첩 잎 HHPSN8', load='접이판 묶음 11.4 kg x3 g 반 + 손 100 N이 경첩 하나에', status=ST + '. 4.7 MPa SF 41.5'),
}
for k, v in new.items():
    v['case'] = CASE; v['criteria'] = CRIT; v['version'] = 'v2.30.6'
    parts[k] = v
note = ('2026-11-28 디테일링: 같은 모델로 t4 R4를 풀었다(detail_2026-11-28_handcalc.json L_bracket_t6_vs_t4). '
        'C형 26.47 -> 5.69(됨), S형 7.22 -> 2.49, T형 2.27 -> 0.92(안 됨), 가로대 끝 S형 2.60 -> 1.15(안 됨). 형상은 v2.30.6에서 굽힘 R이 판금 기능으로 그려진 것 말고 같다')
for k in ('P_M07_LBRK·LBRKT·LBRKC(판금 L SUS304 t6, S·T·C)', 'P_M04_LBRK·LBRKC + P_M04R 가로대 끝(판금 L SUS304 t6)'):
    parts[k]['note_detail_2026-11-28'] = note
json.dump(m, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parts', len(parts), 'added/updated', len(new))
