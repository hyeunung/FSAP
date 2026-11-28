# -*- coding: utf-8 -*-
"""fea/models.json — 디테일링 DP-4(v2.31.2). 고정 · 접촉 · 하중의 뜻은 바꾸지 않는다(자리 좌표만 지금 형상으로).
 - P_RXDC03_BEAM_CLAMP_판금 · P_RXDC03_T2_GUIDE_판금: 형상(판금 기능 · 굽힘 R) · 판정 단면(model_change) · status · step · version
 - P_M08_TUBE_BRKT_U6: 새 줄(재질 A5052 -> PET-CF. 표에 없던 부품 — 실제 조립 경계조건으로 더함)
 - P_RXDC03_RISER_BRKT_판금 · P_RXDC03_LEAD_GUIDE_판금: 메모 note_detail_DP-4 한 줄(형상 그대로 — 고정 · 하중 줄 안 건드림)
다시 돌려도 같은 결과(같은 키를 덮어씀). 실행: python -X utf8 -B fea/cases/detail_DP-4_models_update.py"""
import json
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
P = ROOT + '/fea/models.json'
R = json.load(open(ROOT + '/fea/results/detail_DP-4_handcalc.json', encoding='utf-8'))
m = json.load(open(P, encoding='utf-8')); parts = m['parts']
HEAD = '2026-11-29 DP-4(v2.31.2, 서명 3cecf9e76dccace8) 손계산 fea/results/detail_DP-4_handcalc.json · 형상 detail_DP-4_stepgeo.json. FEA 못 함 — 환경 없음(D-16). '
CRIT = {'value': '운전 SF 3, 오조작 SF 2, 영구 변형 SF < 1.2 = 동작(SUS304 항복 205, E 193 GPa, G 74 GPa). 처짐 6-2 미정(D-08) -> 기록, 이웃과의 틈과 비교',
        'source': '요구서 6-1(M-09 기본값)'}
MC = ('2026-11-29 DP-4: 판금 기능으로 바뀌어 굽힘 R(안쪽 R = t)이 실제 형상이 됐다. 판정 단면을 (1) 굽힘 안쪽 겉면 — 굽은 보 식(곧은 보의 %s배) '
      '(2) 볼트 구멍을 뺀 단면(E-18 "측정 자료의 최소 단면")으로 본다. 고정 · 접촉 · 하중 자리는 그대로. 옛 모델(벽 안쪽 면에서 곧은 외팔보)을 같은 형상에 풀면 ')

b = R['1_beam_clamp']; o = b['오조작 50 N 아래로']; r = b['운전']; bolt = b['볼트 CB5-12 x2 -> 보 앞벽 탭(STKR400 t8)']
c = parts['P_RXDC03_BEAM_CLAMP_판금']
c['case'] = 'cases/detail_DP-4_handcalc.py (v2.29.3 t3: cases/mech_RX-DC-03_handcalc.py)'
c['fixed'] = ('v2.31.2: 벽 X -352~-338 · Y 116~120(t4) · Z 610.5~636이 U1_BEAM 앞면 Y 120에 Ø5.5 x2(X -345, Z 619.5 · 630, CB5-12, 보 STKR400 벽 물림 8.0). '
              '벽과 선반 사이 굽힘 안쪽 R4 · 바깥 R8(중심 Y 112 · Z 610.5) — 보 맞댐 평면은 Z 610.5부터. 아래로 당김의 받침점 = 맞댐 평면 밑 끝 Z 610.5(옛 표: 벽 밑)')
c['contact'] = '선반 Y 68~112 · Z 602.5~606.5(폭 14, t4, 윗면 Z 606.5 그대로) 위에 구름 고리(J_U4_X 95에서 틈 0.25로 얹힘). 선반에 묶는 구멍 없음(위로 당김은 전해지지 않는다)'
c['load'] = '운전: 케이블 굽힘 되돌림 1줄 5 N x 2줄 + 받는 무게 x 3 g. 오조작: 케이블 1줄 손 당김 50 N(임시, PNEU-01과 같음, D-38 전). 선반 끝(Y 68) 아래 방향 — 벽 두께 가운데까지 팔 50'
c['criteria'] = CRIT
c['model_change'] = (MC % b['굽은 보 계수(안쪽 R = t)']) + '오조작 SF %s, 새 모델 %s(굽힘 안쪽 겉면 %s MPa). 모델링부 값 3.13은 곧은 보 · 팔 48.9' % (
    o['옛 모델(곧은 외팔 48) MPa · SF'][1], o['지배 SF'], o['굽힘 안쪽 겉면(굽은 보) MPa · SF'][0])
c['status'] = HEAD + ('t3 -> t4. 오조작 %s(필요 2, +%d %%) · 운전 %s(필요 3). 선반 굽힘 끝선 %s, 벽 구멍 뺀 단면 %s, 볼트 당김 %s N — 암나사 전단 %s · 조임 암나사 전단 %s(4.5 N·m). '
                      '끝 처짐 오조작 %s mm. 과사양 아님(지배 SF/필요 %s). 옛 t3: 오조작 1.76(옛 모델) · %s(새 모델)' % (
    o['지배 SF'], round((o['지배 SF'] / 2.0 - 1) * 100), r['지배 SF'], o['선반 굽힘 끝선(팔 44) MPa · SF'][1],
    o['벽 구멍 · 볼트']['받침점 맞댐 평면 밑 끝 Z 610.5']['구멍 뺀 단면 MPa · SF'][1], bolt['오조작 당김 N(가장 큰 것)'], bolt['handcalc']['sf_operating']['암나사 전단'],
    bolt['handcalc']['sf_tightening']['조임 암나사 전단'], o['끝 처짐 mm(팔 50 곧은 외팔 어림)'], b['과사양']['오조작 지배 SF / 필요'],
    b['두께 · 폭 민감도(참고 — PM 예외 DP4-EX3 판단용)']['t3 x 폭 14']['SF']))
c['step'] = 'tools/out/detail/DP-4/stepout/P_RXDC03_BEAM_CLAMP.step'; c['version'] = 'v2.31.2'

t = R['2_t2_guide']; o2 = t['오조작 50 N']; tb = t['볼트 CB5-12 x2 -> 블록 턱 M5 막힌 탭(A5052)']
c = parts['P_RXDC03_T2_GUIDE_판금']
c['case'] = 'cases/detail_DP-4_handcalc.py (v2.29.3: cases/mech_RX-DC-03_handcalc.py)'
c['fixed'] = ('v2.31.2: 판 밑 플랜지 X -304.6~-280 · Z 233~236(t3, 폭 18)이 블록 턱 밑면 Z 236에 CB5-12 x2(X -296 · -286, Y 75, M5 막힌 탭 물림 9). '
              '플랜지와 립 사이 굽힘 안쪽 R3 · 바깥 R6(중심 X -304.6 · Z 230)')
c['contact'] = '립 X -310.6~-307.6 · Y 66~84 · Z 212~230(매달림 — 플랜지 두께 가운데까지 22.5)에 PTFE 튜브 2(임시 OD 8 x ID 7 x 20), 연장 케이블이 미끄러져 지남'
c['criteria'] = CRIT
c['model_change'] = (MC % t['굽은 보 계수']) + '오조작 SF %s, 새 모델 %s(첫 구멍 뺀 단면) · %s(굽힘 안쪽 겉면)' % (
    o2['옛 모델(곧은 외팔 21) MPa · SF'][1], o2['첫 구멍 뺀 단면 MPa · SF'][1], o2['굽힘 안쪽 겉면(굽은 보, 팔 22.5) MPa · SF'][1])
c['status'] = HEAD + ('두께 그대로 t3, 판금 기능(R3). 오조작 %s(필요 2) · 운전 %s(필요 3). 볼트 당김 %s N(보수), 블록 탭 조임 암나사 전단 H32 %s · H112 %s(조질 지정은 RXDCC1-FEA-D5 그대로). 과사양 아님' % (
    o2['지배 SF'], t['운전']['지배 SF'], tb['오조작 당김 N(보수)'], tb['handcalc(H32)']['sf_tightening']['조임 암나사 전단'], tb['handcalc(H112)']['sf_tightening']['조임 암나사 전단']))
c['step'] = 'tools/out/detail/DP-4/stepout/P_RXDC03_T2_GUIDE.step'; c['version'] = 'v2.31.2'

u = R['3_tube_brkt_u6']; ou = u['오조작 50 N']; ub = u['볼트 CB5-16_M08_PX x2 -> 블록 P_RX19_BLOCK(A5052) -X 면 탭']
parts['P_M08_TUBE_BRKT_U6'] = {
    'case': 'cases/detail_DP-4_handcalc.py',
    'fixed': '밑판 X -338~-330(t8) · Y -16~16 · Z 222~272가 블록 P_RX19_BLOCK_밀링 -X 면(X -330)에 CB5-16_M08_PX x2(Y ±8, Z 236, 블록 M5 탭 물림 8.0). 받침점 = 밑판 밑 끝 Z 222(-X 당김) ',
    'contact': '관 턱 X -356~-338 · Y -10~10 · Z 252~272의 Ø6.5 구멍(축 Y, X -347 · Z 262)에 관 TU0604(U6) 1줄이 끼워져 지남',
    'load': '운전: 압력 펴짐 6.3 N(0.5 MPa x Ø4) + 관 몫 30 g x 3 g. 오조작: 관 1줄 손 당김 50 N(임시, D-38 전) — -X(볼트 줄 위 외팔 26) · Z(턱 뿌리 팔 9) 가운데 불리한 쪽',
    'criteria': {'value': '운전 SF 3, 오조작 SF 2(PET-CF 항복 60 · 층간 0.5배 30 MPa로 판정, E 5 GPa — handcalc 표 · DP-3과 같은 가정). 좌면 한계 60 MPa -> 조임 1.5 N·m',
                 'source': '요구서 6-1(M-09 기본값), M-13 "하중은 M-09(재질이 바뀌면 다시 본다)"'},
    'status': HEAD + 'A5052 -> PET-CF(형상 그대로). 오조작 층간 SF %s(60 MPa로 %s, 옛 A5052 %s) · 운전 %s. 볼트 당김 %s N/개. 좌면 SF 4.5 N·m %s(안 됨) · 1.5 N·m %s -> 조임 1.5 N·m 지정(PET-CF 좌면 볼트 41 + 2 = 43)' % (
        ou['SF(층간 30)'], ou['SF(PET-CF 60)'], ou['옛 A5052 SF'], u['운전']['SF(층간 30)'], ub['오조작 당김 N/개'],
        ub['좌면(PET-CF 한계 60 MPa, 머리 Ø8.5 / 구멍 Ø5.5)']['좌면 SF']['4.5 N·m'], ub['좌면(PET-CF 한계 60 MPa, 머리 Ø8.5 / 구멍 Ø5.5)']['좌면 SF']['1.5 N·m']),
    'step': 'tools/out/detail/stepout/P_M08_TUBE_BRKT_U6.step', 'version': 'v2.31.2'}

r4 = R['4_riser_brkt']; j4 = r4['이 묶음 판정(국부 플랜지 >= 2)']; mill = r4['고침안 A — 밀링 한 덩어리(예외 DP4-EX1 제안)']; b5 = r4['고침안 — 앞 누름 볼트 CB5-12, 귀 자리 (-265.25, 79)']
parts['P_RXDC03_RISER_BRKT_판금']['note_detail_DP-4'] = HEAD + (
    '형상 그대로(서명 부피 · 상자 같음 — v2.30.5 결과 다시 씀). 이 묶음 완료 판정 "국부 플랜지 오조작 SF >= 2": 첫 항복 %s~%s -> 미달(기준). 접히는 형상(웨브 목 17 x t4) 뿌리 %s · t6이어도 %s, SF 2엔 목 %s 또는 t %s — 판금으로는 못 맞춤. '
    '고침안 수치: 밀링 A5052-H32 속 찬 기둥 15 x 10.5 오조작 %s(H112면 %s) · 끝 처짐 %s mm(지금 1.46), 앞 누름 볼트 M5 귀 자리 당김 %s N(보수) — 물림 8 암나사 전단 %s(기준 +5 %%) · 물림 10 %s · H112 %s' % (
        j4['첫 항복 SF 범위(날 발 자유 ~ 막힘)'][0], j4['첫 항복 SF 범위(날 발 자유 ~ 막힘)'][1],
        r4['접히는 형상(웨브 목만 남음) — 모델링부 수치 다시 셈']['목 17 x t4']['SF'], r4['접히는 형상(웨브 목만 남음) — 모델링부 수치 다시 셈']['목 17 x t6']['SF'],
        r4['접히는 형상(웨브 목만 남음) — 모델링부 수치 다시 셈']['t4에서 SF 2에 필요한 목 폭 mm'], r4['접히는 형상(웨브 목만 남음) — 모델링부 수치 다시 셈']['목 17에서 SF 2에 필요한 두께 mm'],
        mill['기둥 15 x 10.5(지금 ㄷ 단면 외곽 X -288~-273 · Y 74.5~85) A5052-H32']['SF'], mill['같은 기둥 A5052-H112(조질 미지정)']['SF'],
        mill['기둥 15 x 10.5(지금 ㄷ 단면 외곽 X -288~-273 · Y 74.5~85) A5052-H32']['끝 처짐 Y mm 오조작 · 운전'][0],
        b5['당김 N [보수(받침점 웨브 가운데, 팔 4.5), 밑판 강체]'][0], b5['M5 물림 8 · 블록 H32']['운용']['암나사 전단'],
        b5['M5 물림 10 · H32(밀링 밑판 t6 + CB5-16, 턱 t14 관통 탭)']['운용']['암나사 전단'], b5['M5 물림 8 · 블록 H112']['운용']['암나사 전단']))
r5 = R['5_lead_guide']; fx = r5['고침안 수치(예외 DP4-EX2 판단용)']
parts['P_RXDC03_LEAD_GUIDE_판금']['note_detail_DP-4'] = HEAD + (
    '형상 그대로(서명 질량 87.074 g). 이 묶음 완료 판정 "팔 오조작 SF >= 2": 팔 굽힘 %s · 비틀림 + 굽힘 %s -> 미달(기준). 고침안 수치: 폭 14 x t4 %s, 두께 t3 그대로 팔 폭 %s 이상(폭 20 %s · 22 %s)' % (
        r5['지금(폭 14 x t3, 외팔 47.6)']['팔 굽힘(Z 쪽) MPa · SF'][1], r5['지금(폭 14 x t3, 외팔 47.6)']['비틀림 + 굽힘(Y 당김) VM · SF'][1],
        fx['폭 14 x t4(지시대로)']['지배 SF'], fx['t3에서 SF 2에 필요한 팔 폭 mm'], fx['폭 20 x t3(두께 그대로 팔만 넓힘)']['지배 SF'], fx['폭 22 x t3(두께 그대로 팔만 넓힘)']['지배 SF']))
json.dump(m, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parts', len(parts))
for k in ('P_RXDC03_BEAM_CLAMP_판금', 'P_RXDC03_T2_GUIDE_판금', 'P_M08_TUBE_BRKT_U6'):
    print(k, '|', parts[k]['status'][len(HEAD):][:330])
for k in ('P_RXDC03_RISER_BRKT_판금', 'P_RXDC03_LEAD_GUIDE_판금'):
    print(k, '|', parts[k]['note_detail_DP-4'][len(HEAD):][:420])
