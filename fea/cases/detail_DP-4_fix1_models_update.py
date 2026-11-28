# -*- coding: utf-8 -*-
"""fea/models.json — 디테일링 DP-4 수정 1회차(v2.31.3). 하중 · 기준의 뜻은 바꾸지 않는다(자리 좌표와 형상 줄만 지금 형상으로).
 - P_RXDC03_RISER_BRKT_밀링 · P_RXDC03_LEAD_GUIDE_3DP: 새 줄(판금 품번이 밀링 · 출력 한 덩어리로 바뀜). 옛 줄 '_판금'에는 removed 한 줄만 더한다(기록으로 남김)
 - P_RXDC03_BEAM_CLAMP_판금 · P_RXDC03_T2_GUIDE_판금: fixed · contact · status · step · version(v2.31.2 status는 status_v2.31.2로 옮겨 둠)
다시 돌려도 같은 결과(같은 키를 덮어씀). 실행: python -X utf8 -B fea/cases/detail_DP-4_fix1_models_update.py"""
import json
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
P = ROOT + '/fea/models.json'
R = json.load(open(ROOT + '/fea/results/detail_DP-4_fix1_handcalc.json', encoding='utf-8'))
m = json.load(open(P, encoding='utf-8')); parts = m['parts']
HEAD = '2026-11-29 DP-4 수정 1회차(v2.31.3, 서명 8729f3cd46400f8b) 손계산 fea/results/detail_DP-4_fix1_handcalc.json · 형상 detail_DP-4_fix1_stepgeo.json · 단면 detail_DP-4_fix1_sections.json. FEA 못 함 — 환경 없음(D-16). '
SRC = '요구서 6-1(M-09 기본값)'
LOAD_CAB = '운전: 케이블 굽힘 되돌림 1줄 5 N x 2줄(D-232 임시) + 받는 무게 x 3 g. 오조작: 케이블 1줄 손 당김 50 N(임시, D-38 전). '

# ---------------- 세움 받침(밀링)
r1 = R['1_riser_milled']; e = r1['귀 뿌리 — +Y 50 N']; g1 = r1['지배 SF(오조작)']
ks = [k for k in e if k[:2] in ('A ', 'B ', 'C ', 'D ')]
A, B, C, D = (e[k] for k in sorted(ks))
key = '귀 뿌리 MPa · 첫 항복 SF · 소성 힌지 SF(x1.5)'
run1 = [v for k, v in r1.items() if k.startswith('운전 10 N')][0]
parts['P_RXDC03_RISER_BRKT_밀링'] = {
    'case': 'cases/detail_DP-4_fix1_handcalc.py (옛 판금 품번: cases/mech_RX-DC-C1_fea3_handcalc.py)',
    'fixed': ('v2.31.3: A5052(BOM 조질 H32) 밀링 한 덩어리. 밑판 t6(Z 250~256) X -305~-258 · Y 71.75~97에서 구석 X -305~-288 · Y 71.75~83을 뺀 꼴이 블록 P_RX19_BLOCK_밀링 선반 윗면(Z 250)에 얹힘. '
              'CB5-16 x3(4.5 N·m): 뒤 2개 (X -288 · -278, Y 90), 귀 1개 (X -265.25, Y 79) — 블록 M5 관통 탭 물림 10. 블록 윗면은 받침을 밀기만 한다. '
              '조임 상태(예압 4,500 N/개)에서 오조작 모멘트로는 밑판이 뜨지 않는다(보수 정역학 당김 1,975 N의 2.28배) -> +Y 당김의 귀 볼트 몫은 볼트 3개 누름 자리의 누름 변화로 셈(1,077 N). '
              '-Y 당김 받침점 = 기둥 앞면 Y 74.5(보수)'),
    'contact': ('기둥 X -288~-273 · Y 74.5~85 속 참(15 x 10.5) Z 256~470, Z 470~484.25는 웨브만 Y 82.25~85(15 x 2.75). 선반 X -318.6~-268 · Y 65~85 · Z 484.25~487(t2.75), '
                '케이블 타이 홈 4 x 2(R1) 가운데 X -300 · -280, Y 74. 하중점 = 먼 타이 (X -300, Y 74) Z 487 — 기둥 뿌리 Z 256까지 231, 웨브만 구간 밑 Z 470까지 17. '
                '안쪽 R3은 기둥 ±X 면 ↔ 밑판, 웨브 ±X 면 ↔ 선반 밑에만 있다(±Y 쪽 구석은 R 없음)'),
    'load': LOAD_CAB + '+Y · -Y · X · 아래로 각각, 그리고 가장 불리한 각(공간). 비틀림 팔 = 단면 가운데(기둥 X -280.5 · Y 79.75, 웨브 Y 83.625)에서 먼 타이까지(X 쪽 19.5, Y 쪽 5.75 · 9.625). 자중 x3 g %.2f N(축 방향)' % (r1['형상(STEP · gmsh 단면)']['부피 · 질량(서명)'][1] / 1000 * 9.81 * 3),
    'criteria': {'value': '운전 SF 3, 오조작 SF 2, 영구 변형 SF < 1.2 = 동작(A5052-H32 항복 195 — handcalc 표, E 70 GPa). 처짐 6-2 미정(D-08) -> 기록, 이웃과의 틈과 비교', 'source': SRC},
    'status': HEAD + ('오조작 지배 %s(웨브만 구간 Z 470, 가장 불리한 각) · 기둥 뿌리 %s · 선반 %s · 귀 뿌리(조임 상태) %s. 운전 웨브 %s · 기둥 %s. '
                      '귀 뿌리는 받침점 가정에 따라 갈린다: 밑판 강체 %s / 조임 상태 %s / 예압 없음 · 받침점 기둥 뒷면 %s(소성 힌지 %s) / 옛 표 받침점 Y 83.5 %s — 판정은 조임 상태(4.5 N·m 지정이 조건). '
                      '끝 처짐 오조작 Y %s · X %s mm(옛 ㄷ 단면 Y 1.46). H112(110 MPa)면 웨브만 구간 %s — 조질 H32 지정이 조건. 구석 R 없는 자리(웨브 앞 ↔ Z 470 턱)는 손계산으로 못 가름. 과사양 아님(지배/필요 %s)' % (
        g1['가장 작은 값'], g1['기둥 뿌리'], g1['선반'], g1['귀 뿌리(조임 상태)'], run1['웨브만 구간 SF'], run1['기둥 뿌리 SF'],
        A[key][1], B[key][1], C[key][1], C[key][2], D[key][1], r1['끝 처짐 mm']['오조작 Y · X'][0], r1['끝 처짐 mm']['오조작 Y · X'][1],
        r1['같은 단면 H112(110 MPa)면']['웨브만 구간'], r1['과사양']['지배 SF / 필요'])),
    'step': 'tools/out/detail/DP-4/stepout/P_RXDC03_RISER_BRKT.step', 'version': 'v2.31.3',
    'model_change': ('2026-11-29 DP-4 수정 1회차: 판금 ㄷ 단면(SUS304 t3) -> 밀링 한 덩어리(A5052-H32)라 표의 형상 줄을 새로 적었다. 하중 · 기준은 그대로. '
                     '+Y 당김의 받침점을 "웨브 밑 가운데 Y 83.5"(t3 판금에서 웨브가 유일한 길이던 때의 보수 가정)에서 조임 상태(볼트 3개 4.5 N·m, 안 벌어짐)로 바꿨다 — '
                     '밑판 t6이 속 찬 기둥 · 뒤꿈치 12와 한 덩어리이고 예압이 보수 당김의 2.28배라 뜨지 않는다. 옛 받침점을 같은 형상에 풀면 귀 뿌리 %s(해석부 단면: 유효 폭 16.25 · R3 안 가장 큰 단면) · %s(모델링부 단면: 온 폭 25.25 · R3 끝), 새 모델 %s' % (
        D[key][1], D['모델링부 식(온 폭 · R3 끝) MPa · SF'][1], B[key][1]))}
parts['P_RXDC03_RISER_BRKT_판금']['removed'] = 'v2.31.3(DP-4 수정 1회차, 예외 DP4-EX1)에서 P_RXDC03_RISER_BRKT_밀링으로 바뀜 — 기록으로만 남김'

# ---------------- 리드 안내(출력)
r2 = R['2_lead_guide_3dp']; o = r2['오조작 50 N']; ip = r2['볼트 2개의 면 안 돌림(Y′ 당김 50 N, 판정 밖)']; b2 = r2['볼트 CB5-16 x2 -> 그네 텅(A5052) 관통 탭 물림 10, 1.5 N·m']
kz = [k for k in o if k.startswith('다리 굽힘')][0]; kt = [k for k in o if '표 그대로 58' in k][0]; kt2 = [k for k in o if '잰 값' in k][0]
parts['P_RXDC03_LEAD_GUIDE_3DP'] = {
    'case': 'cases/detail_DP-4_fix1_handcalc.py (옛 판금 품번: cases/mech_RX-DC-03_handcalc.py)',
    'fixed': ('v2.31.3: PET-CF 출력 한 덩어리(층 법선 = 세운 판 폭 방향). 좌면 패드 X -252~-246(t6) · 그네 좌표 Y′ 74~94 · Z′ 132~164.5가 그네 P_RX19_SWING_밀링 텅 면(X -246, Y′ 65~85 · Z′ ~117~160)에 '
              'CB5-16 x2(Y′ 80, Z′ 150 · 159, 간격 9, 조임 1.5 N·m — PET-CF 좌면, 텅 M5 관통 탭 물림 10). 받침점: +Z′ 당김 = 텅 윗변 Z′ 160, -Z′ 당김 = 패드 밑변 Z′ 132'),
    'contact': ('다리 X -291.6~-252 · Y′ 74~90 · Z′ 132~144(16 x 12)가 세운 판 X -296.6~-291.6(t5, Y″ 52~96 · Z″ 86~144, 5.676° 기울임)을 받친다. 커넥터 2쌍(임시 22 x 22 x 50)이 판 앞면 X -296.6에 닿음. '
                '타이 판 X -318.6~-296.6 · t7 x 10. 그네와 같이 돎(가동 굽힘 0)'),
    'load': LOAD_CAB + '하중점 = 판 앞면 X -296.6(표 그대로) — 다리 뿌리 X -252까지 44.6, 패드 두께 가운데 X -249까지 47.6. Z′ 방향(다리 깊이 쪽 굽힘, 패드 판 굽힘), Y′ 당김은 세운 판 밑(Z″ 86)에서 — 다리 비틀림 팔 표 그대로 58(다리 가운데까지 잰 값 52), 볼트 2개 가운데까지 68.5',
    'criteria': {'value': '운전 SF 3, 오조작 SF 2, 영구 변형 SF < 1.2 = 동작(PET-CF 항복 60 · 층을 가로지르는 응력은 0.5배 30 MPa, E 5 GPa — handcalc 표 · DP-3과 같은 가정). 좌면 한계 60 MPa -> 조임 1.5 N·m', 'source': SRC + ', M-05 "층을 가로질러 당기면 해석 SF를 층 방향 강도로 본다"'},
    'status': HEAD + ('오조작: 다리 굽힘 %s · 다리 비틀림 + 굽힘 층간 %s(잰 팔 52면 %s) · 타이 판 %s · 좌면 패드 온 단면 %s · 첫 구멍 줄 구멍 뺀 단면 %s(위로 어림 — 지배, 기준 +9.5 %%라 FEA 확인 대상인데 환경 없음). 운전 지배 %s. '
                      '볼트 당김 %s N(예압 1,500 N의 1/%s), 좌면 1.5 N·m %s · 4.5 N·m %s(안 됨 -> 1.5 N·m 지정, PET-CF 좌면 볼트 43 + 2 = 45). '
                      'Y′ 당김의 면 안 돌림 %s N·m는 마찰(μ 0.2, 2.70 N·m)만으로는 미끄러진다(0.79) — 구멍 벽에 기대면 -Y′ 가장자리 살 3.25 전단 SF %s(μ 0.2) · 마찰 0이면 층간 기준 %s. 처짐 어림 Y′ 당김 %s mm(이웃 틈 1.835보다 작음). 과사양 아님' % (
        o[kz][1], o[kt][3], o[kt2][3], o[[k for k in o if k.startswith('타이 판')][0]][2], o[[k for k in o if '온 단면 20' in k][0]][1], o[[k for k in o if '구멍 뺀 단면' in k][0]][1], r2['운전']['지배 SF'],
        b2['오조작 당김 N'], b2['운용']['분리(예압/외력)'], b2['좌면(PET-CF 60 MPa) SF: 1.5 N·m · 4.5 N·m'][0], b2['좌면(PET-CF 60 MPa) SF: 1.5 N·m · 4.5 N·m'][1],
        round(ip['면 안 돌림 N·mm(50 N x 68.5)'] / 1000, 2), [v for k, v in ip['μ 0.20'].items() if '가장자리 살' in k][0][2], [v for k, v in ip['μ 0.00'].items() if '가장자리 살' in k][0][2],
        r2['처짐 어림 mm(오조작, 다리만 · E 5 GPa)']['Y′ 당김 판 밑'])),
    'step': 'tools/out/detail/DP-4/stepout/P_RXDC03_LEAD_GUIDE.step', 'version': 'v2.31.3',
    'model_change': ('2026-11-29 DP-4 수정 1회차: 판금(SUS304 t3, 팔 폭 14) -> PET-CF 출력 한 덩어리라 표의 형상 줄을 새로 적었다. 하중 자리 · 기준의 뜻은 그대로(재질 한계만 PET-CF로). '
                     '비틀림 응력 식을 Roark 사각 단면 최대 전단 식으로 썼다(앞 회차 · 모델링부는 비틀림 강성 계수를 응력에 써서 크게 나옴). 옛 식을 같은 형상에 풀면 다리 층간 2.31(모델링부 값), 새 식 %s' % o[kt][3])}
parts['P_RXDC03_LEAD_GUIDE_판금']['removed'] = 'v2.31.3(DP-4 수정 1회차, 예외 DP4-EX2)에서 P_RXDC03_LEAD_GUIDE_3DP로 바뀜 — 기록으로만 남김'

# ---------------- 보 앞 받침 · T2 안내
r3 = R['3_beam_clamp']; o3 = r3['오조작 50 N 아래로']; b3 = r3['볼트 CB5-12 x2 -> 보 앞벽 탭(STKR400 t8) 물림 8.0']
c = parts['P_RXDC03_BEAM_CLAMP_판금']
if c.get('version') == 'v2.31.2': c['status_v2.31.2'] = c['status']; c['fixed_v2.31.2'] = c['fixed']; c['contact_v2.31.2'] = c['contact']
c['case'] = 'cases/detail_DP-4_fix1_handcalc.py (v2.31.2 t4: cases/detail_DP-4_handcalc.py, v2.29.3 t3: cases/mech_RX-DC-03_handcalc.py)'
c['fixed'] = ('v2.31.3: 벽 X -357~-333(폭 24) · Y 117~120(t3) · Z 609.5~639가 U1_BEAM 앞면 Y 120에 Ø5.5 x2(X -345, Z 619.5 · 631.5, CB5-12, 보 STKR400 벽 물림 8.0). '
              '벽과 선반 사이 굽힘 안쪽 R3 · 바깥 R6(중심 Y 114 · Z 609.5) — 보 맞댐 평면은 Z 609.5부터. 아래로 당김의 받침점 = 맞댐 평면 밑 끝 Z 609.5')
c['contact'] = '선반 Y 68~114 · Z 603.5~606.5(폭 24, t3, 윗면 Z 606.5 그대로) 위에 구름 고리(J_U4_X 95에서 틈 0.25로 얹힘). 선반에 묶는 구멍 없음(위로 당김은 전해지지 않는다)'
c['load'] = '운전: 케이블 굽힘 되돌림 1줄 5 N x 2줄 + 받는 무게 x 3 g. 오조작: 케이블 1줄 손 당김 50 N(임시, PNEU-01과 같음, D-38 전). 선반 끝(Y 68) 아래 방향 — 벽 두께 가운데까지 팔 50.5'
kb = [k for k in o3 if k.startswith('굽힘 안쪽 겉면')][0]
c['status'] = HEAD + ('t4 · R4 · 폭 14 -> t3 · R3 · 폭 24(예외 DP4-EX3). 오조작 %s(필요 2, +%d %% — 굽힘 안쪽 겉면 %s MPa) · 운전 %s(필요 3). 선반 굽힘 끝선 %s, 아래 구멍 뺀 단면 %s(받침 반력 뺌) · %s(안 뺌), '
                      '볼트 당김 %s N — 암나사 전단 %s · 조임 암나사 전단 %s(4.5 N·m). 끝 처짐 오조작 %s mm. 과사양 아님(지배 SF/필요 %s)' % (
    o3['지배 SF'], round((o3['지배 SF'] / 2.0 - 1) * 100), o3[kb][0], r3['운전']['지배 SF'], o3[[k for k in o3 if k.startswith('선반 굽힘 끝선')][0]][1],
    o3['아래 구멍 뺀 단면(받침 반력 뺌) MPa · SF'][1], o3['아래 구멍 뺀 단면(반력 안 뺌 — 모델링부 식) MPa · SF'][1], b3['오조작 당김 N(가장 큰 것)'], b3['운용']['암나사 전단'], b3['조임']['조임 암나사 전단'],
    o3[[k for k in o3 if k.startswith('끝 처짐')][0]], r3['과사양']['오조작 지배 SF / 필요']))
c['step'] = 'tools/out/detail/DP-4/stepout/P_RXDC03_BEAM_CLAMP.step'; c['version'] = 'v2.31.3'

r4 = R['4_t2_guide']; o4 = r4['오조작 50 N']; b4 = r4['볼트 CB5-12 x2 -> 블록 턱 M5 탭(A5052-H32) 물림 9.0']
c = parts['P_RXDC03_T2_GUIDE_판금']
if c.get('version') == 'v2.31.2': c['status_v2.31.2'] = c['status']; c['fixed_v2.31.2'] = c['fixed']
c['case'] = 'cases/detail_DP-4_fix1_handcalc.py (v2.31.2: cases/detail_DP-4_handcalc.py, v2.29.3: cases/mech_RX-DC-03_handcalc.py)'
c['fixed'] = ('v2.31.3: 판 밑 플랜지 X -304.6~-276.5 · Z 233~236(t3, 폭 18)이 블록 턱 밑면 Z 236에 CB5-12 x2(X -296 · -284, Y 75, M5 탭 물림 9). '
              '플랜지와 립 사이 굽힘 안쪽 R3 · 바깥 R6(중심 X -304.6 · Z 230)')
c['status'] = HEAD + ('둘째 구멍 X -286 -> -284 · 판 끝 X -280 -> -276.5(예외 DP4-EX4). 립 · 첫 구멍 · 굽힘 그대로라 오조작 %s(필요 2) · 운전 %s(필요 3) 그대로. 볼트 당김 %s N(보수, 간격 12 — 앞 112.5), 블록 탭 조임 암나사 전단 H32 %s. 과사양 아님' % (
    o4['지배 SF'], r4['운전']['지배 SF'], b4['오조작 당김 N'], b4['조임']['조임 암나사 전단']))
c['step'] = 'tools/out/detail/DP-4/stepout/P_RXDC03_T2_GUIDE.step'; c['version'] = 'v2.31.3'

json.dump(m, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parts', len(parts))
for k in ('P_RXDC03_RISER_BRKT_밀링', 'P_RXDC03_LEAD_GUIDE_3DP', 'P_RXDC03_BEAM_CLAMP_판금', 'P_RXDC03_T2_GUIDE_판금'):
    print(k, '|', parts[k]['status'][len(HEAD):][:520])
