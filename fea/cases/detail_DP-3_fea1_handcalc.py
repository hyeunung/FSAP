# -*- coding: utf-8 -*-
"""DP-3 해석부 수정 1회차 손계산(v2.31.1). FEA 못 함 — 환경 없음(D-16). CAD 안 씀.
같은 계열 스크립트(detail_DP-3_handcalc.py)를 입력만 바꿔 다시 돈다(E-18 "케이스는 계열별 고정 스크립트에 입력 · 태그를 인자로"):
  - 형상: fea/results/detail_DP-3_fea1_stepgeo.json(다시 내보낸 보 STEP — 메움 6 · 다시 뚫은 탭 2)
  - 질량 · 상자: tools/out/signatures.json(v2.31.1, 해시 587fb3c7f3bb4b2a)
  - 덮개 볼트 CB5-12 -> CB5-16(예외 DP3-EX1 조건 ③): 볼트 질량을 서명에서 읽음
앞 회차 결과(fea/results/detail_DP-3_handcalc.json, v2.31.0)는 그대로 두고 값 차이를 6절에 남긴다.
더 본 것: 7) 덮개 탭 t3 조임 조건(목표 1.0 · 상한 1.5 N·m, K 0.2 · 0.14 — PM 손계산 대조) 8) 다시 뚫은 뒷벽 탭에 물리는 이음판 볼트 CB5-16_M07_NY
실행: python -X utf8 -B fea/cases/detail_DP-3_fea1_handcalc.py -> fea/results/detail_DP-3_fea1_handcalc.json"""
import json, math, sys
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
OUT = ROOT + '/fea/results/detail_DP-3_fea1_handcalc.json'
PREV = json.load(open(ROOT + '/fea/results/detail_DP-3_handcalc.json', encoding='utf-8'))
assert PREV['_doc'].endswith('FSAP_v2.31.0.sc'), PREV['_doc']        # 앞 회차 결과가 덮어써지지 않았는지

src = open(ROOT + '/fea/cases/detail_DP-3_handcalc.py', encoding='utf-8').read()
SUBS = [
    ("'/fea/results/detail_DP-3_stepgeo.json'", "'/fea/results/detail_DP-3_fea1_stepgeo.json'"),
    ("+ 4 * 0.00374", "+ 4 * PARTS['U1_FRAME/CB5-16_M07_CAP']['mass'] / 1000.0"),
    ("'덮개 CB5-12 x8 -> 덮개 플랜지 탭 t3(1.5 N·m 지정)'", "'덮개 CB5-16 x8 -> 덮개 플랜지 탭 t3(상한 1.5 N·m)'"),
]
for a, b in SUBS:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
TAIL = "\njson.dump(R, open(ROOT + '/fea/results/detail_DP-3_handcalc.json'"
assert src.count(TAIL) == 1
src = src.split(TAIL)[0]                                               # 앞 회차 결과 파일은 쓰지 않는다
ns = {'__name__': 'dp3_fea1'}
exec(compile(src, 'detail_DP-3_handcalc.py(v2.31.1 입력)', 'exec'), ns)
R, PARTS, bolt, GEO = ns['R'], ns['PARTS'], ns['bolt'], ns['GEO']
assert R['_doc'].endswith('FSAP_v2.31.1.sc'), R['_doc']
RUN, MIS = '운전 3 g + 끌림 Y 30 N', '오조작 3 g + 손 500 N + 끌림 Y 100 N'


def pick(d, pre):
    return [v for k, v in d.items() if k.startswith(pre)][0]


# ------------------------------------------------------------------ 6) 앞 회차(v2.31.0) 대비 차이
def tip(Rx, pre, case): return pick(Rx['1d_tipping'], pre)[case]['볼트 복원 포함 SF']


diff = []
def row(name, a, b, need=None):
    diff.append({'항목': name, 'v2.31.0': a, 'v2.31.1': b, '차': (round(b - a, 4) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else ('같음' if a == b else '다름')), '기준': need})


row('보 질량 kg(서명)', PREV['1a_section']['m_beam_kg(서명)'], round(PARTS['U1_FRAME/P_M07_BEAM']['mass'] / 1000.0, 4))
for pre, lbl in (('A ', 'A 표 모델 그대로'), ('B0', 'B0 DP-3 전 형상'), ('B ', 'B 표 하중 + 지금 형상(판정)'), ('C ', 'C 지금 질량 어림'), ('D 지금', 'D 지금 질량 + 받침 Y 132'), ('E ', 'E 표 하중 + 받침 Y 132'), ('D + ', 'D + 이음판 볼트 6')):
    row('넘어짐 %s 운전' % lbl, tip(PREV, pre, RUN), tip(R, pre, RUN), 3.0)
    row('넘어짐 %s 오조작' % lbl, tip(PREV, pre, MIS), tip(R, pre, MIS), 2.0)
for k2 in ('B', 'C'):
    for cs, need in ((RUN, 3.0), (MIS, 2.0)):
        row('열린 끝 찌그러짐 %s %s' % (k2, cs[:3]), PREV['1e_open_end_distortion'][k2][cs]['SF'], R['1e_open_end_distortion'][k2][cs]['SF'], need)
    s0, s1 = PREV['1e_open_end_distortion'][k2]['얹힘 길이 80 띠 혼자(가장 보수)'], R['1e_open_end_distortion'][k2]['얹힘 길이 80 띠 혼자(가장 보수)']
    row('얹힘 80 띠 혼자 %s 운전' % k2, s0['운전 MPa · SF'][1], s1['운전 MPa · SF'][1], 3.0)
    row('얹힘 80 띠 혼자 %s 오조작' % k2, s0['오조작 MPa · SF'][1], s1['오조작 MPa · SF'][1], 2.0)
row('웨브 크리플링 SF', PREV['1f_web_crippling']['SF(앞 웨브 1장)'], R['1f_web_crippling']['SF(앞 웨브 1장)'], 2.0)
for k, v in R['1g_beam_stress'].items():
    row('보 굽힘 ' + k, PREV['1g_beam_stress'][k]['SF(전체 단면)'], v['SF(전체 단면)'], v['필요'])
    row('보 구멍 Kt 3 ' + k, PREV['1g_beam_stress'][k]['구멍 Kt 3 SF'], v['구멍 Kt 3 SF'], v['필요'])
row('Z 처짐 X 0 표 하중 mm', PREV['1h_beam_deflection_Z_mm']['X 0']['1 g 표 하중'], R['1h_beam_deflection_Z_mm']['X 0']['1 g 표 하중'])
row('이음판 순단면 x Kt 3 SF', PREV['2_splice']['SF'], R['2_splice']['SF'], 3.0)
row('덮개 손 100 N SF', PREV['3_cap']['손 100 N 가운데']['t3 MPa · SF'][1], R['3_cap']['손 100 N 가운데']['t3 MPa · SF'][1], 2.0)
row('덮개 볼트 전단 N/개(자중 3 g)', PREV['3_cap']['자중 3 g 볼트 전단 N/개'], R['3_cap']['자중 3 g 볼트 전단 N/개'])
for k, v in R['4_pet_cf_parts'].items():
    for kk in ('SF(PET-CF 60)', 'SF', '턱 혼자(볼트 풀림) SF'):
        if kk in v: row('PET-CF ' + k, PREV['4_pet_cf_parts'][k][kk], v[kk], 2.0)
pb = dict(PREV['5_bolts']); pb['덮개 CB5-16 x8 -> 덮개 플랜지 탭 t3(상한 1.5 N·m)'] = pb.pop('덮개 CB5-12 x8 -> 덮개 플랜지 탭 t3(1.5 N·m 지정)')
for k, v in R['5_bolts'].items():
    row('볼트 ' + k + ' 운전 최소', min(pb[k]['운전'].values()), min(v['운전'].values()), v['기준'])
    row('볼트 ' + k + ' 조임 암나사', pb[k]['조임 암나사 전단'], v['조임 암나사 전단'], 1.0)
moved = [d for d in diff if d['차'] not in (0, 0.0, '같음')]
R['6_fix1_diff'] = {'비교 수': len(diff), '값이 달라진 줄': moved, '전체': diff,
                    'note': '메움 6(Ø4.2: 아랫벽 X -310 · -160 x Y 140 · 180, 앞벽 X -256 · -244 x Z 276) · 다시 뚫은 뒷벽 탭 2(X 1230, Z 300 · 600) — 벽 두께 안의 변경이라 단면 · 하중 경로 그대로. '
                            '보 질량 +5.0 g, 덮개 볼트 4개 +2.3 g(CB5-12 3.74 -> CB5-16 4.357 g)'}

# 메운 6개는 보의 응력 집중원이 줄어드는 쪽이다: 그 자리의 굽힘 응력(B 하중)과 메우기 전 Kt 3 값을 기록
A, Iy, Iz = ns['A'], ns['Iy'], ns['Iz']; D, B_, XA, XB = ns['D'], ns['B'], ns['XA'], ns['XB']
loc = {}
for nm, gf, ex, drag, need in ns['CASES'][1:]:
    for x in (-310.0, -160.0, -256.0):
        Mm = max(ns['mom'](ns['pts_table'](gf, ns['CAR_T'][1][c]) + list(ex), gf, x) for c in (0, 1))
        s = Mm / (Iy / (D / 2))
        loc.setdefault(nm, {})['X %d' % x] = {'M_Nmm': round(Mm), '아랫벽 바깥 굽힘 MPa': round(s, 2), '메우기 전 Kt 3 SF': round(245.0 / (3 * s), 1), '지금(구멍 없음) SF': round(245.0 / s, 1), '필요': need}
R['6b_filled_holes_local'] = {'자리': loc, 'note': '아랫벽(당김 쪽)의 X -310 · -160 구멍 4개가 없어져 그 자리의 Kt 3 응력 집중이 사라진다. 판정값(1g 보 굽힘 · 구멍 Kt 3)은 남은 구멍(아랫벽 Y 140 줄 7개 등)에 그대로 적용'}

# ------------------------------------------------------------------ 7) 덮개 탭 t3 조임 조건(예외 DP3-EX1 조건 ① · ③)
SY_SUS = 205.0
ath3 = math.pi * 5 * 3.0 * 0.375
lim = 0.6 * SY_SUS * ath3
capx = {'암나사 전단 한도 N': round(lim, 1), '손 100 N 볼트당 외력 N': 25.0}
for kf in (0.2, 0.14):
    for tq in (1.0, 1.5):
        c = bolt(d=5, le=3.0, load=25.0, torque=tq, base='SUS304', dw=8.5, dh=5.5, k=kf, sf_min=2.0)
        capx['K %.2f · %.1f N·m' % (kf, tq)] = {'예압 N': c['preload_N'], '조임 암나사 전단': c['sf_tightening']['조임 암나사 전단'], '조임 볼트 응력': c['sf_tightening']['조임 볼트 응력'],
                                              '좌면(보 벽 STKR400 490)': round(490 * math.pi / 4 * (8.5 ** 2 - 5.5 ** 2) / c['preload_N'], 2),
                                              '분리(예압/외력)': c['sf_operating']['분리(예압/외력)'], '운전 암나사 전단': c['sf_operating']['암나사 전단'],
                                              '기준 ±10 % 안': c['near_limit']}
m_cap = ns['m_cap']
capx['마찰로 덮개 잡기(1.0 N·m x4, μ 0.15) / 자중 3 g'] = round(4 * 1000.0 * 0.15 / (m_cap * 9.81 * 3), 1)
cb = PARTS['U1_FRAME/CB5-16_M07_CAP']['bbox']; cp = PARTS['U1_FRAME/P_M07_BEAM_CAP']['bbox']
tip_y, fl_in = cb[3], cp[2] + 3.0                                         # 앞벽 쪽 볼트: 끝 Y 136, 플랜지 Y 128.2~131.2
capx['볼트 끝이 플랜지 안쪽 면을 지난 길이 mm(서명 상자)'] = round(tip_y - fl_in, 2)
capx['머리 밑 길이 16 = 벽 8 + 틈 0.2 + 플랜지 3 + 나옴'] = round(16 - 8 - 0.2 - 3, 2)
capx['불완전 나사부 2피치(1.6, 가정) 뒤 남는 온 나사 여유 mm'] = round(tip_y - fl_in - 1.6, 2)
capx['note'] = ('물림은 판 두께 3.0 그대로라 한도 2,174 N은 CB5-12 때와 같다. 볼트가 4 길어져 달라진 것은 끝 나옴 0.8 -> 4.8(끝 모따기 · 불완전 나사부가 물림을 깎지 않음)과 볼트 질량 +0.6 g/개뿐. '
                'PM 손계산(K 0.14: 1.0 N·m 1,429 N -> 1.52, 1.5 N·m 2,143 N -> 1.01)과 같은 값. 1.5 N·m · K 0.14는 기준 1.0의 +1 %라 상한선이다 — 목표 1.0 N·m를 지켜야 한다. '
                '나사산 뭉개짐은 고체 FEA로 보는 항목이 아니라 시제품 조임 · 풀림 3회(요구서 7절)로 확인')
R['7_cap_tap_exception'] = capx

# ------------------------------------------------------------------ 8) 다시 뚫은 뒷벽 탭에 물리는 이음판 볼트
ny = [v for k, v in PARTS.items() if v.get('name', '').startswith('CB5-16_M07_NY') and (v['bbox'][4] + v['bbox'][5]) / 2 >= 250.0]   # 보 쪽 8개(Z 300 · 600). 기둥 쪽 8개(Z 175 · 220)는 T너트
assert len(ny) == 8, len(ny)
walls = []
for v in ny:
    y0, y1 = v['bbox'][2], v['bbox'][3]
    walls.append(round(min(y1, 320.0) - max(y0, 312.0), 2))               # 뒷벽 Y 312~320 안에 든 볼트 길이(상자)
c4 = bolt(d=5, le=8.0, load=0.0, torque=4.0, base='SS400', sf_min=3.0)     # D-54 임시 예압 4 kN(4 N·m)
c45 = bolt(d=5, le=8.0, load=0.0, torque=4.5, base='SS400', sf_min=3.0)
R['8_splice_beam_bolts(CB5-16_M07_NY)'] = {'개수': len(ny), '뒷벽 안 길이(서명 상자) min · max': [min(walls), max(walls)],
                                           '4.0 N·m(D-54)': c4['sf_tightening'], '4.5 N·m(관례)': c45['sf_tightening'],
                                           '넘어짐 복원 마찰 몫 N/개(μ 0.15 x 4 kN)': 600.0, '볼트 전단으로 받는다면 SF(12.9 전단 0.6 x 1080 x 14.2)': round(0.6 * 1080 * 14.2 / 600.0, 1),
                                           'note': ':7 · :8 (X 1230, Z 300 · 600)의 탭이 벽 전체(8.0)로 뚫려 8개가 같은 물림이다. 넘어짐 식의 이음판 마찰 2,400 N(기둥 쪽 4개)은 그대로 — 이 볼트들은 보 쪽 4개/끝'}

# ------------------------------------------------------------------ 기준 근처(±10 %) 모음
near = []
for d in diff:
    if isinstance(d['v2.31.1'], (int, float)) and d['기준'] and 0.9 * d['기준'] <= d['v2.31.1'] < 1.1 * d['기준']:
        near.append({'항목': d['항목'], '값': d['v2.31.1'], '기준': d['기준'], '%': round((d['v2.31.1'] / d['기준'] - 1) * 100, 1)})
under = [{'항목': d['항목'], '값': d['v2.31.1'], '기준': d['기준']} for d in diff if isinstance(d['v2.31.1'], (int, float)) and d['기준'] and d['v2.31.1'] < d['기준']]
R['9_near_limit(±10 %)'] = near
R['9_under'] = under
R['_fea1'] = {'입력 형상': 'fea/results/detail_DP-3_fea1_stepgeo.json', '보 STEP 원통 축': len(GEO['P_M07_BEAM']['new']['cyl']), '앞 회차': PREV['_doc_hash'], 'FEA': '해석 못 함 — 환경 없음(자료대기 D-16)'}
json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('문서', R['_doc'].split('/')[-1].split('\\')[-1], R['_doc_hash'], '| 비교', len(diff), '줄, 값이 달라진 줄', len(moved))
for d in moved[:8]: print('  달라짐:', d['항목'], d['v2.31.0'], '->', d['v2.31.1'])
print('넘어짐 B(판정) 운전 · 오조작:', tip(R, 'B ', RUN), tip(R, 'B ', MIS), '| C', tip(R, 'C ', RUN), tip(R, 'C ', MIS), '| D', tip(R, 'D 지금', RUN), tip(R, 'D 지금', MIS))
dB = R['1e_open_end_distortion']['B']
print('열린 끝 B:', dB[RUN]['SF'], dB[MIS]['SF'], '| 띠 혼자', dB['얹힘 길이 80 띠 혼자(가장 보수)'])
print('덮개 탭:', {k: (v['조임 암나사 전단'], v['분리(예압/외력)']) for k, v in capx.items() if k.startswith('K ')}, '끝 나옴', capx['볼트 끝이 플랜지 안쪽 면을 지난 길이 mm(서명 상자)'])
print('이음판 볼트 NY:', R['8_splice_beam_bolts(CB5-16_M07_NY)']['개수'], R['8_splice_beam_bolts(CB5-16_M07_NY)']['뒷벽 안 길이(서명 상자) min · max'], c4['sf_tightening'])
print('메운 자리:', json.dumps(loc[RUN], ensure_ascii=False))
print('기준 ±10 % 안:', near)
print('기준 미달:', under)
print('->', OUT)
