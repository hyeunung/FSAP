# -*- coding: utf-8 -*-
"""DP-4 해석부 손계산 수정 1회차(v2.31.3) — U4 캐리지 리드 받침 4품번. FEA 못 함 — 환경 없음(D-16). CAD 안 씀.
입력: fea/results/detail_DP-4_fix1_stepgeo.json(원통 · 평면) · detail_DP-4_fix1_sections.json(gmsh로 잰 단면 · 부피), tools/out/signatures.json(v2.31.3, 해시 8729f3cd46400f8b)
하중(fea/models.json, D-232 · D-38 임시): 운전 = 케이블 되돌림 5 N x 2줄 + 받는 무게 x 3 g, 오조작 = 케이블 손 당김 50 N.
판정(요구서 6-1 = M-09 기본값): 운전 SF 3, 오조작 SF 2, SF < 1.2 = 영구 변형(동작). 기준 +10 % 안이면 FEA 확인 대상(E-18) — 환경이 없어 '확인 못 함'으로 적는다.
모델에서 달라진 것(이유는 보고서 0절): 세움 받침이 판금 ㄷ 단면 -> 밀링 한 덩어리, 리드 안내가 판금 -> PET-CF 출력 한 덩어리가 돼 표의 고정 · 단면 줄을 새 형상으로 다시 적는다.
  세움 받침 +Y 당김의 받침점은 '웨브 밑 가운데 Y 83.5'(t3 판금 웨브가 유일한 길이던 때의 가정)에서 조임 상태(볼트 3개 4.5 N·m, 안 벌어짐)로 본다. 옛 받침점도 같은 형상에 풀어 남긴다.
실행: python -X utf8 -B fea/cases/detail_DP-4_fix1_handcalc.py -> fea/results/detail_DP-4_fix1_handcalc.json"""
import json, math, sys
ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
import handcalc as hc
GEO = json.load(open(ROOT + '/fea/results/detail_DP-4_fix1_stepgeo.json', encoding='utf-8'))
SEC = json.load(open(ROOT + '/fea/results/detail_DP-4_fix1_sections.json', encoding='utf-8'))
SIG = json.load(open(ROOT + '/tools/out/signatures.json', encoding='utf-8'))
assert SIG['doc'].replace('\\', '/').endswith('FSAP_v2.31.3.sc') and SIG['doc_hash'] == '8729f3cd46400f8b', (SIG['doc'], SIG['doc_hash'])
PARTS = SIG['parts']

SY, E = 205.0, 193000.0                                   # SUS304
SY_AL, SY_AL112, E_AL = hc.BASE['A5052'][0], hc.BASE['A5052-H112'][0], 70000.0     # 195(BOM 조질 H32) · 110
SY_PET, SY_LAY, E_PET = hc.BASE['PET-CF'][0], 30.0, 5000.0   # 60 · 층간 0.5배(DP-3과 같은 가정)
g = 9.81
F_MIS, F_CAB, N_CAB = 50.0, 5.0, 2
NEED_RUN, NEED_MIS = 3.0, 2.0
TQ = 4.5                                                   # M5 조임 N·m(이 기계 관례), PET-CF 좌면은 1.5
AB = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)                   # M5 머리 좌면 넓이
R = {'_doc': SIG['doc'].replace('\\', '/'), '_doc_hash': SIG['doc_hash'],
     '_assume': {'케이블 되돌림 N/줄(D-232 임시)': F_CAB, '줄 수': N_CAB, '오조작 손 당김 N(D-38 전 임시)': F_MIS, '무게 배수': 3,
                 'SUS304 항복': SY, 'A5052 항복 H32(handcalc 표) · H112': [SY_AL, SY_AL112], 'PET-CF 항복 · 층간(0.5배 가정)': [SY_PET, SY_LAY],
                 '조임 M5 N·m(관례) · PET-CF 좌면': [TQ, 1.5], '너트 계수 K': 0.2}}


def sf(s, sy): return round(sy / s, 2) if s > 0 else None


def sig(key):
    hit = [v for k, v in PARTS.items() if k.endswith('/' + key) or k == key]
    assert len(hit) == 1, (key, len(hit)); return hit[0]


def judge(v, need):
    return '동작(영구 변형)' if v < 1.2 else ('미달' if v < need else ('됨 — 기준 +10 % 안(FEA 확인 대상, 환경 없음 D-16)' if v < 1.1 * need else '됨'))


def ki_rect(ri, t):
    """굽은 보(사각 단면) 안쪽 겉면 응력 / 곧은 보 응력(Winkler)."""
    ro, rc = ri + t, ri + t / 2.0
    rn = t / math.log(ro / ri); e = rc - rn
    return ((rn - ri) / (t * e * ri)) / (6.0 / t ** 2)


def tau_rect(T, s1, s2):
    """사각 단면 비틀림 최대 전단(긴 변 가운데). Roark: 3T/(a c^2) x [1 + 0.6095r + 0.8865r^2 - 1.8023r^3 + 0.9100r^4], r = c/a."""
    a, c = max(s1, s2), min(s1, s2); r = c / a
    return 3.0 * abs(T) / (a * c * c) * (1 + 0.6095 * r + 0.8865 * r ** 2 - 1.8023 * r ** 3 + 0.9100 * r ** 4)


def rect_vm(bx, hy, rx, ry, h, F):
    """사각 단면(X 변 bx, Y 변 hy)의 무게중심에서 (rx, ry, h) 떨어진 점에 힘 F=(Fx,Fy,Fz). 모서리 · 변 가운데의 VM 가운데 가장 큰 값."""
    Fx, Fy, Fz = F
    Mx = ry * Fz - h * Fy; My = h * Fx - rx * Fz; T = rx * Fy - ry * Fx
    A, Zx, Zy = bx * hy, bx * hy ** 2 / 6.0, hy * bx ** 2 / 6.0
    tq = tau_rect(T, bx, hy)                                # 짧은 변 가운데도 같은 값으로(위로 어림)
    n = abs(Fz) / A
    corner = abs(Mx) / Zx + abs(My) / Zy + n
    midY = math.hypot(abs(Mx) / Zx + n, math.sqrt(3) * tq)   # Y 쪽 면 가운데(Mx 굽힘 + 비틀림)
    midX = math.hypot(abs(My) / Zy + n, math.sqrt(3) * tq)
    return max(corner, midY, midX), {'Mx': round(Mx), 'My': round(My), 'T': round(T), 'τ': round(tq, 2), '모서리 σ': round(corner, 1), 'Y 면 가운데 VM': round(midY, 1), 'X 면 가운데 VM': round(midX, 1)}


def scan(bx, hy, rx, ry, h, Fmag, horizontal=True):
    worst = (0.0, None, None)
    for th in range(0, 360, 2):
        for ph in ([0] if horizontal else range(-90, 91, 5)):
            c = math.cos(math.radians(ph))
            F = (Fmag * c * math.cos(math.radians(th)), Fmag * c * math.sin(math.radians(th)), Fmag * math.sin(math.radians(ph)))
            v, d = rect_vm(bx, hy, rx, ry, h, F)
            if v > worst[0]: worst = (v, (th, ph), d)
    return worst


# ================================================================== 1) 세움 받침 P_RXDC03_RISER_BRKT_밀링 (SUS304 t3 판금 -> A5052-H32 밀링 한 덩어리)
s1 = sig('P_RXDC03_RISER_BRKT_밀링'); S = SEC['P_RXDC03_RISER_BRKT']
assert abs(S['volume'] - s1['volume']) < 0.01 and s1['material'] == 'A5052', (S['volume'], s1)
col = S['sections']['기둥 가운데 Z 360']['pieces'][0]['bbox']; web = S['sections']['웨브만 구간 가운데 Z 476']['pieces'][0]['bbox']
bx, hy = col[3] - col[0], col[4] - col[1]                   # 15 x 10.5
wb, wt = web[3] - web[0], web[4] - web[1]                   # 15 x 2.75
assert abs(S['sections']['기둥 가운데 Z 360']['area_sum'] - bx * hy) < 0.01 and abs(S['sections']['웨브만 구간 밑 Z 470.1']['area_sum'] - wb * wt) < 0.01
Z_BASE_BOT, Z_BASE_TOP, Z_WEB0, Z_SH0, Z_TOP = 250.0, 256.0, 470.0, 484.25, 487.0
slots = sorted(set(round(c['center'][0]) for c in GEO['P_RXDC03_RISER_BRKT']['new']['cyl'] if c['axis'] == 'Z' and abs(c['r'] - 1.0) < 1e-6))
x_tie_far, x_tie_near, y_tie = -300.0, -280.0, 74.0         # 타이 홈 가운데(R1 원통 X -301 · -299, -281 · -279 · Y 74)
assert slots == [-301, -299, -281, -279], slots
xc, yc = (col[0] + col[3]) / 2, (col[1] + col[4]) / 2       # 기둥 가운데 (-280.5, 79.75)
ywc = (web[1] + web[4]) / 2                                 # 웨브 가운데 Y 83.625
h_col, h_web = Z_TOP - Z_BASE_TOP, Z_TOP - Z_WEB0           # 231 · 17
W3 = s1['mass'] / 1000.0 * g * 3                            # 자중 x 3 g
run_F = N_CAB * F_CAB
m1 = {'형상(STEP · gmsh 단면)': {'부피 · 질량(서명)': [s1['volume'], s1['mass']], '기둥 단면 X x Y': [bx, hy], '기둥 Z': [Z_BASE_TOP, Z_WEB0], '웨브만 구간 단면 X x Y · Z': [wb, wt, [Z_WEB0, Z_SH0]],
                              '선반 두께': Z_TOP - Z_SH0, '밑판 두께': Z_BASE_TOP - Z_BASE_BOT, '안쪽 R3 자리(축 Y)': '기둥 ±X 면 ↔ 밑판 윗면, 웨브 ±X 면 ↔ 선반 밑면 — ±Y 면 쪽 구석(기둥 앞뒤 ↔ 밑판, 웨브 앞 ↔ 기둥 윗면 Z 470, 웨브 앞 ↔ 선반 밑)은 R 없음',
                              '볼트 구멍 Ø5.5': [(-288.0, 90.0), (-278.0, 90.0), (-265.25, 79.0)], '하중점': [x_tie_far, y_tie, Z_TOP]}}

# 1-a 기둥 뿌리(Z 256) · 웨브만 구간(Z 470)
cases = {}
for lbl, F in (('+Y 50 N', (0, F_MIS, 0)), ('-Y 50 N', (0, -F_MIS, 0)), ('X 50 N', (F_MIS, 0, 0)), ('아래로 50 N(타이 당김)', (0, 0, -F_MIS))):
    vc, dc = rect_vm(bx, hy, x_tie_far - xc, y_tie - yc, h_col, F)
    vw, dw_ = rect_vm(wb, wt, x_tie_far - xc, y_tie - ywc, h_web, F)
    cases[lbl] = {'기둥 뿌리 VM MPa · SF': [round(vc, 1), sf(vc, SY_AL)], '기둥': dc, '웨브만 구간 밑(Z 470) VM MPa · SF': [round(vw, 1), sf(vw, SY_AL)], '웨브': dw_}
wc = scan(bx, hy, x_tie_far - xc, y_tie - yc, h_col, F_MIS); ww = scan(wb, wt, x_tie_far - xc, y_tie - ywc, h_web, F_MIS)
wc3 = scan(bx, hy, x_tie_far - xc, y_tie - yc, h_col, F_MIS, False); ww3 = scan(wb, wt, x_tie_far - xc, y_tie - ywc, h_web, F_MIS, False)
cases['가장 불리한 각(수평면 2° 간격)'] = {'기둥 뿌리 VM · SF · 각°': [round(wc[0], 1), sf(wc[0], SY_AL), wc[1][0]], '웨브만 구간 VM · SF · 각°': [round(ww[0], 1), sf(ww[0], SY_AL), ww[1][0]]}
cases['가장 불리한 각(공간 — 방위 2° · 높이각 5°)'] = {'기둥 뿌리 VM · SF · (방위, 높이각)': [round(wc3[0], 1), sf(wc3[0], SY_AL), wc3[1]], '웨브만 구간 VM · SF · (방위, 높이각)': [round(ww3[0], 1), sf(ww3[0], SY_AL), ww3[1]]}
m1['오조작 50 N — 기둥 · 웨브'] = cases
gov_web = sf(ww3[0], SY_AL); gov_col = sf(wc3[0], SY_AL)
m1['같은 단면 H112(110 MPa)면'] = {'기둥 뿌리': sf(wc3[0], SY_AL112), '웨브만 구간': sf(ww3[0], SY_AL112)}
# 운전: 10 N 가장 불리한 각 + 자중 3 g(축 방향 눌림)
rw = scan(wb, wt, x_tie_far - xc, y_tie - ywc, h_web, run_F, False); rc = scan(bx, hy, x_tie_far - xc, y_tie - yc, h_col, run_F, False)
m1['운전 10 N + 자중 x3 g %.2f N' % W3] = {'기둥 뿌리 SF': sf(rc[0] + W3 / (bx * hy), SY_AL), '웨브만 구간 SF': sf(rw[0] + W3 / (wb * wt), SY_AL), '필요': NEED_RUN}
# 끝 처짐(외팔: 기둥 + 웨브만 구간, 밑판 돌아감 빼고)
Icy, Iwy = bx * hy ** 3 / 12, wb * wt ** 3 / 12; Icx = hy * bx ** 3 / 12; Iwx = wt * wb ** 3 / 12
t0 = Z_TOP - Z_SH0
dY = F_MIS / E_AL * ((h_col ** 3 - h_web ** 3) / 3 / Icy + (h_web ** 3 - t0 ** 3) / 3 / Iwy)
dX = F_MIS / E_AL * ((h_col ** 3 - h_web ** 3) / 3 / Icx + (h_web ** 3 - t0 ** 3) / 3 / Iwx)
k_tip = F_MIS / dY * 1000.0                                  # N/m
m_col = bx * hy * (Z_WEB0 - Z_BASE_TOP) * 2.68e-6; m_sh = S['sections']['선반 Z 485.6']['area_sum'] * (Z_TOP - Z_SH0) * 2.68e-6
m1['끝 처짐 mm'] = {'오조작 Y · X': [round(dY, 2), round(dX, 2)], '운전 Y': round(dY * run_F / F_MIS, 2), '옛 ㄷ 단면 Y(v2.30.5)': 1.46,
                 '이웃 틈과 비교': 'C-46 한계의 U5 바퀴 틈 8.9(X 쪽) - 오조작 X 처짐 = %.1f, 케이블 임시 형상 틈 1.0은 받침에 묶여 같이 움직임' % (8.9 - dX),
                 '1차 고유 진동 Hz(끝 질량 = 선반, +케이블 50 g 가정)': [round(math.sqrt(k_tip / (m_sh + 0.24 * m_col)) / (2 * math.pi)), round(math.sqrt(k_tip / (m_sh + 0.05 + 0.24 * m_col)) / (2 * math.pi))]}

# 1-b 선반 t2.75(먼 타이를 아래로 당김) — 웨브(15 x 2.75, 선반 뒤 끝)만 받친다
tsh = Z_TOP - Z_SH0
a_y = web[1] - y_tie                                         # 웨브 앞면까지 8.25
a_x = web[0] - x_tie_far                                     # 웨브 -X 면까지 12
shelf = {}
s_a = F_MIS * a_y / (wb * tsh ** 2 / 6)                      # 웨브 앞 단면, 폭 = 웨브 폭 15만
weff = wt + a_y                                              # 웨브 -X 면 옆 단면: 웨브 두께 + 45° 퍼짐
s_b = F_MIS * a_x / (weff * tsh ** 2 / 6)
s_full = F_MIS * a_x / ((S['sections']['선반 X -288.05(웨브 -X 면 옆)']['area_sum'] / tsh) * tsh ** 2 / 6)
slot_w = S['sections']['선반 먼 타이 홈 줄 X -300']['area_sum'] / tsh  # 홈 뺀 폭 18
shelf['웨브 앞 단면(Y 82.25, 폭 15, 팔 %.2f) MPa · SF' % a_y] = [round(s_a, 1), sf(s_a, SY_AL)]
shelf['웨브 -X 면 옆 단면(X -288, 유효 깊이 %.1f = 웨브 두께 + 45° 퍼짐, 팔 %.0f) MPa · SF' % (weff, a_x)] = [round(s_b, 1), sf(s_b, SY_AL)]
shelf['같은 단면 온 깊이 20(모델링부 식) MPa · SF'] = [round(s_full, 1), sf(s_full, SY_AL)]
vj, dj = rect_vm(wb, wt, x_tie_far - xc, y_tie - ywc, 0.0, (0, 0, -F_MIS))
shelf['웨브 ↔ 선반 이음 단면(15 x 2.75) MPa · SF'] = [round(vj, 1), sf(vj, SY_AL)]
shelf['먼 타이 홈 줄 남은 깊이 mm'] = round(slot_w, 2)
gov_shelf_r = min(sf(s_a, SY_AL), sf(s_b, SY_AL), sf(vj, SY_AL))
m1['선반 t%.2f — 아래로 50 N' % tsh] = shelf

# 1-c 귀 뿌리(+Y 당김) — 볼트 당김은 받침점 가정에 따라 갈린다
M_ot = F_MIS * (Z_TOP - Z_BASE_BOT)                          # 밑면 Z 250 둘레 넘어뜨리는 모멘트 11,850
y_ear, y_rear, y_back, y_heel = 79.0, 90.0, col[4], 97.0     # 귀 볼트 · 뒤 볼트 · 기둥 뒷면 85 · 밑판 뒤 끝
kr = M_ot / ((y_heel - y_ear) ** 2 + 2 * (y_heel - y_rear) ** 2)
T = {'A 밑판 강체(받침점 뒤 끝 Y 97, 볼트 3개 나눔)': kr * (y_heel - y_ear),
     'B 조임 상태(4.5 N·m, 안 벌어짐 — 볼트 3개 누름 자리의 누름 변화)': M_ot * (86.3333 - y_ear) / ((86.3333 - y_ear) ** 2 + 2 * (y_rear - 86.3333) ** 2),
     'C 예압 없음 · 받침점 기둥 뒷면 Y 85(뒤꿈치 · 뒤 볼트 도움 0)': M_ot / (y_back - y_ear),
     'D 옛 표의 받침점 Y 83.5(판금 웨브 밑 가운데)': M_ot / (83.5 - y_ear)}
pre = TQ * 1000 / (0.2 * 5)
# 단면: R3 끝(X -270)에서 볼트 축까지 4.75. R 안쪽으로 s 들어간 단면은 팔 4.75 + s · 두께 6 + 3 - sqrt(9 - s^2) — 가장 큰 곳을 찾는다
ear_w_full = S['sections']['귀 뿌리 X -270(R3 끝), Z 250~256']['area_sum'] / 6.0      # 25.25
head_r = 4.25; lever = (-265.25) - (-270.0)
ear_w_45 = min(y_ear + head_r + lever, y_heel) - max(y_ear - head_r - lever, 71.75)   # 머리 지름 + 45° 퍼짐, 밑판 앞 끝 Y 71.75에서 잘림 = 16.25
kmax, smax = max(((lever + s / 100.0) / (6 + 3 - math.sqrt(9 - (s / 100.0) ** 2)) ** 2, s / 100.0) for s in range(0, 300))
ear = {'넘어뜨리는 모멘트 N·mm(Z 250 둘레)': M_ot, '예압 N(4.5 N·m)': pre, '귀 폭: 온 폭 · 유효 폭(머리 Ø8.5 + 45° 퍼짐)': [ear_w_full, ear_w_45],
       '단면 계수(팔/t^2): R3 끝 · R 안 가장 큰 곳(s mm)': [round(lever / 36, 4), round(kmax, 4), smax]}
for k, t in T.items():
    s_j = 6 * t * kmax / ear_w_45                             # 해석부 판정 단면: 유효 폭 · R 안 가장 큰 곳
    s_m = 6 * t * (lever / 36) / ear_w_full                   # 모델링부 식: 온 폭 · R3 끝
    ear[k] = {'볼트 당김 N': round(t), '분리(예압/당김)': round(pre / t, 2), '귀 뿌리 MPa · 첫 항복 SF · 소성 힌지 SF(x1.5)': [round(s_j, 1), sf(s_j, SY_AL), round(1.5 * SY_AL / s_j, 2)],
              '모델링부 식(온 폭 · R3 끝) MPa · SF': [round(s_m, 1), sf(s_m, SY_AL)], '전단 MPa': round(t / (ear_w_45 * 6), 1)}
kB = 'B 조임 상태(4.5 N·m, 안 벌어짐 — 볼트 3개 누름 자리의 누름 변화)'; kC = 'C 예압 없음 · 받침점 기둥 뒷면 Y 85(뒤꿈치 · 뒤 볼트 도움 0)'; kD = 'D 옛 표의 받침점 Y 83.5(판금 웨브 밑 가운데)'
# 조임 상태 확인: 누름 자리(머리 Ø8.5에서 30°로 퍼진 고리, 밑면에서 Ø15.4) 누름 응력과 그 변화
d_cone = 8.5 + 2 * 6 * math.tan(math.radians(30)); a_cone = math.pi / 4 * (d_cone ** 2 - 5.5 ** 2)
ear['조임 상태 확인'] = {'누름 자리 지름 · 넓이': [round(d_cone, 1), round(a_cone, 1)], '예압 누름 응력 MPa': round(pre / a_cone, 1), '오조작으로 귀 자리 누름이 줄어드는 양 MPa': round(T[kB] / a_cone, 1),
                    '안 벌어짐 여유(예압/줄어드는 힘)': round(pre / T[kB], 2), '보수 정역학(C)으로 봐도 예압/당김': round(pre / T[kC], 2),
                    '판정': '예압 4,500 N이 보수 당김 %.0f N의 %.2f배(>= 2) -> 밑판은 블록에서 뜨지 않는다. 귀 뿌리는 B로 판정' % (T[kC], pre / T[kC])}
gov_ear = ear[kB]['귀 뿌리 MPa · 첫 항복 SF · 소성 힌지 SF(x1.5)'][1]
ear['판정 값(B) · 예압이 풀렸을 때(C) · 옛 표 받침점(D)'] = [gov_ear, ear[kC]['귀 뿌리 MPa · 첫 항복 SF · 소성 힌지 SF(x1.5)'][1], ear[kD]['귀 뿌리 MPa · 첫 항복 SF · 소성 힌지 SF(x1.5)'][1]]
ear['SF 2가 되는 받침점(예압 없음, 유효 폭 · R 안 단면)'] = 'Y %.1f 이상(기둥 뒷면에서 %.1f 뒤)' % (y_ear + M_ot / (SY_AL / NEED_MIS * ear_w_45 / (6 * kmax)), y_ear + M_ot / (SY_AL / NEED_MIS * ear_w_45 / (6 * kmax)) - y_back)
# 민감도(지시 근거 아님 — 예압에 기대지 않으려 할 때의 값): 밑판 t6 -> t7 · t8, 같은 식
alt = {}
for tb_ in (6.0, 7.0, 8.0):
    k_ = max((lever + s / 100.0) / (tb_ + 3 - math.sqrt(9 - (s / 100.0) ** 2)) ** 2 for s in range(0, 300))
    alt['밑판 t%g' % tb_] = {'C(예압 없음 · 받침점 Y 85) 첫 항복 SF': sf(6 * T[kC] * k_ / ear_w_45, SY_AL), 'D(옛 표 받침점) SF': sf(6 * T[kD] * k_ / ear_w_45, SY_AL), 'CB5-16 물림 mm': 16 - tb_}
ear['민감도 — 밑판 두께(예압 없이도 2를 넘기려면)'] = alt
# 응력 집중(구석 R 없음) — 손계산으로 못 가름. 공칭 응력이 항복의 1/2에 닿는 집중 계수만 적는다
bw_ = F_MIS * h_web / (wb * wt ** 2 / 6); tq_w = tau_rect(F_MIS * abs(x_tie_far - xc), wb, wt)
m1['구석 R 없는 자리(공칭 응력 · 허용 집중 계수)'] = {
    '웨브 앞면 ↔ 기둥 윗면 Z 470(+Y 당김에서 당겨지는 쪽)': {'공칭 굽힘 MPa': round(bw_, 1), '비틀림 τ MPa': round(tq_w, 1), 'VM이 항복/2가 되는 굽힘 집중 계수': round(math.sqrt((SY_AL / 2) ** 2 - 3 * tq_w ** 2) / bw_, 2)},
    '기둥 앞뒤 면 ↔ 밑판 윗면 Z 256(Y 당김)': {'공칭 굽힘 MPa': round(F_MIS * h_col / (bx * hy ** 2 / 6), 1), '항복/2가 되는 집중 계수': round(SY_AL / 2 / (F_MIS * h_col / (bx * hy ** 2 / 6)), 2)}}
m1['귀 뿌리 — +Y 50 N'] = ear
# 1-d 뒤꿈치(-Y 당김): 받침점 기둥 앞면 Y 74.5(보수), 뒤 볼트 2개가 당김
T_rear = M_ot / (2 * (y_rear - col[1]))
heel_w = min(-278.0 + head_r + (y_rear - y_back), -258.0) - max(-288.0 - head_r - (y_rear - y_back), -305.0)   # 머리 2개 + 45° 퍼짐 28.5
s_heel = 2 * T_rear * (y_rear - y_back) / (heel_w * 36 / 6)
m1['뒤꿈치 — -Y 50 N'] = {'뒤 볼트 당김 N/개(받침점 기둥 앞면 Y 74.5)': round(T_rear), '뒤꿈치 뿌리(Y 85, 유효 폭 %.1f x t6, 팔 5) MPa · SF' % heel_w: [round(s_heel, 1), sf(s_heel, SY_AL)], '분리(예압/당김)': round(pre / T_rear, 2)}
# 1-e 볼트(엔진 handcalc)
bolts = {}
for lbl, t in (('귀 CB5-16 · 조임 상태 당김(B)', T[kB]), ('귀 CB5-16 · 예압 없음 보수 당김(C)', T[kC]), ('귀 CB5-16 · 옛 표 받침점(D)', T[kD]), ('뒤 CB5-16 x2(-Y 당김)', T_rear)):
    for tl, b in (('H32', 'A5052'), ('H112', 'A5052-H112')):
        c = hc.calc(5, 10.0, round(t), TQ, '12.9', b, 8.5, 5.5, sf_min=2.0)
        bolts['%s · 블록 %s' % (lbl, tl)] = {'당김 N': round(t), '운용': c['sf_operating'], '조임': c['sf_tightening'], 'ok': c['ok'], 'needs_fea': c['needs_fea'], 'near': c['near_limit']}
m1['볼트 CB5-16 x3 -> 블록 선반(A5052) M5 관통 탭 물림 10'] = bolts
gov_r = min(gov_web, gov_col, gov_shelf_r, gov_ear)
m1['지배 SF(오조작)'] = {'웨브만 구간': gov_web, '기둥 뿌리': gov_col, '선반': gov_shelf_r, '귀 뿌리(조임 상태)': gov_ear, '가장 작은 값': gov_r, '판정': judge(gov_r, NEED_MIS)}
m1['과사양'] = {'지배 SF / 필요': round(gov_r / NEED_MIS, 2), '문턱': 3.0, '판정': '아님'}
R['1_riser_milled'] = m1

# ================================================================== 2) 리드 안내 P_RXDC03_LEAD_GUIDE_3DP (SUS304 t3 판금 -> PET-CF 출력 한 덩어리)
s2 = sig('P_RXDC03_LEAD_GUIDE_3DP'); L = SEC['P_RXDC03_LEAD_GUIDE']
assert abs(L['volume'] - s2['volume']) < 0.01 and s2['material'] == 'PET-CF', s2
# 기운 평면(그네 좌표)에서 치수를 읽는다: 법선 (0, 0.94251, -0.33419) = 그네 Y', (0, 0.33419, 0.94251) = 그네 Z'
tl = {}
for n, d in GEO['P_RXDC03_LEAD_GUIDE']['planes_tilted']: tl.setdefault(tuple(n), []).append(d)
dz = sorted(tl[(0.0, 0.33419, 0.94251)]); dy = sorted(v for k, vv in tl.items() if abs(abs(k[1]) - 0.94251) < 1e-4 for v in vv)
leg_h, pad_h = dz[1] - dz[0], dz[2] - dz[0]                 # 다리 깊이 12 · 패드 높이 32.5
leg_w, pad_w = dy[1] - dy[0], dy[2] - dy[0]                 # 다리 폭 16 · 패드 폭 20
A_leg = L['sections']['다리 X -270']['area_sum']; A_tie = L['sections']['타이 판 X -308']['area_sum']; A_pad = L['sections']['좌면 패드 X -249']['area_sum']
assert abs(A_leg - leg_w * leg_h) < 0.01 and abs(A_tie - 70.0) < 0.01 and abs(A_pad - (pad_w * pad_h - 2 * math.pi * 2.75 ** 2)) < 0.05, (A_leg, A_tie, A_pad, leg_w, leg_h, pad_w, pad_h)
X_CONN, X_PL1, X_LEG1, X_PADM, X_FACE = -296.6, -291.6, -252.0, -249.0, -246.0   # 커넥터 닿는 면 · 판 +X 면 · 패드 -X 면 · 패드 두께 가운데 · 그네 맞댐면
t_pad, t_pl, t_tie, h_tie, L_tie = X_FACE - X_LEG1, X_PL1 - X_CONN, 7.0, 10.0, X_CONN - (-318.6)
arm_leg = X_LEG1 - X_CONN                                    # 다리 뿌리까지 44.6(옛 표: 판 앞면 ~ 탭 -X 면 47.6)
arm_pad = X_PADM - X_CONN                                    # 패드 두께 가운데까지 47.6
# 그네 좌표 Z': 다리 132~144, 패드 132~164.5, 구멍 150 · 159, 텅 맞댐면 Z' ~117~160 · Y' 65~85(모델링부 광선 측정)
z_leg0, z_leg1, z_h1, z_h2, z_tongue_top, z_pl_bot = 132.0, 144.0, 150.0, 159.0, 160.0, 86.0
tors_tab, tors_leg, tors_bolt = 58.0, (z_leg0 + z_leg1) / 2 - z_pl_bot, (z_h1 + z_h2) / 2 - z_pl_bot      # 옛 표 58 · 다리 가운데까지 52 · 볼트 2개 가운데까지 68.5
run2 = 0.1 * g * 3 + N_CAB * F_CAB                           # 표 그대로(받는 무게 100 g)
m2 = {'형상(STEP · gmsh 단면)': {'부피 · 질량(서명)': [s2['volume'], s2['mass']], '다리 폭(Y′) x 깊이(Z′) · 넓이': [leg_w, leg_h, A_leg], '좌면 패드 폭 x 높이 x t · 구멍 뺀 넓이': [pad_w, pad_h, t_pad, A_pad],
                              '세운 판 t · 타이 판 t x 높이 x 길이': [t_pl, [t_tie, h_tie, L_tie]], '팔: 커넥터 닿는 면 ~ 다리 뿌리 · ~ 패드 두께 가운데': [arm_leg, arm_pad],
                              '비틀림 팔: 옛 표 · 판 밑 ~ 다리 가운데 · ~ 볼트 가운데': [tors_tab, tors_leg, tors_bolt], '출력 방향(모델링부)': '층 법선 = 판 폭 방향(Y″, 다리 폭 Y′와 5.7° 어긋남)'},
      '운전 하중 N': round(run2, 2)}
Zleg_z, Zleg_y = leg_w * leg_h ** 2 / 6, leg_h * leg_w ** 2 / 6      # Z′ 힘(깊이 쪽 굽힘) 384 · Y′ 힘(폭 쪽) 512


def lg(F, need):
    o = {}
    s_z = F * arm_leg / Zleg_z                                # Z′ 당김: 다리 굽힘(응력 X 방향 = 층 안)
    o['다리 굽힘(Z′ 당김, 팔 %.1f) MPa · SF(60)' % arm_leg] = [round(s_z, 1), sf(s_z, SY_PET)]
    for lbl, ta in (('표 그대로 58', tors_tab), ('잰 값 %.0f' % tors_leg, tors_leg)):
        tq = tau_rect(F * ta, leg_w, leg_h); s_y = F * arm_leg / Zleg_y; vm = math.hypot(s_y, math.sqrt(3) * tq)
        o['다리 비틀림 + 굽힘(Y′ 당김, 비틀림 팔 %s) τ · VM · SF(60) · SF(층간 30)' % lbl] = [round(tq, 2), round(vm, 1), sf(vm, SY_PET), sf(vm, SY_LAY)]
    # 좌면 패드: 위로 당기면(+Z′) 다리(Z′ 132~144)가 텅에서 뜨고 받침점은 텅 윗변 Z′ 160. 다리 위 ~ 첫 볼트 사이 패드가 모멘트를 다 받는다
    Mp = F * arm_pad
    s_g = Mp / (pad_w * t_pad ** 2 / 6); s_n = Mp / ((pad_w - 5.5) * t_pad ** 2 / 6)
    o['좌면 패드(+Z′ 당김): 머리 아래 끝 온 단면 20 x t6 MPa · SF(60)'] = [round(s_g, 1), sf(s_g, SY_PET)]
    o['좌면 패드: 첫 구멍 줄 구멍 뺀 단면(머리 밑 — 위로 어림) MPa · SF(60)'] = [round(s_n, 1), sf(s_n, SY_PET)]
    d1, d2 = z_tongue_top - z_h1, z_tongue_top - z_h2          # 10 · 1
    T1 = Mp * d1 / (d1 * d1 + d2 * d2)
    o['볼트 당김 N(+Z′ 당김, 받침점 텅 윗변): 아래 · 위'] = [round(T1, 1), round(Mp * d2 / (d1 * d1 + d2 * d2), 1)]
    # -Z′ 당김: 받침점 패드 밑변 Z′ 132, 패드는 텅에 눌린다
    e1, e2 = z_h1 - z_leg0, z_h2 - z_leg0
    o['볼트 당김 N(-Z′ 당김, 받침점 패드 밑변): 아래 · 위'] = [round(Mp * e1 / (e1 * e1 + e2 * e2), 1), round(Mp * e2 / (e1 * e1 + e2 * e2), 1)]
    s_tie_y = F * L_tie / (h_tie * t_tie ** 2 / 6); s_tie_z = F * L_tie / (t_tie * h_tie ** 2 / 6)
    o['타이 판 끝 %.0f N(팔 %.0f): Y 쪽 · Z 쪽 굽힘 MPa · SF(60, 응력이 X 방향 = 층 안)' % (F, L_tie)] = [round(s_tie_y, 1), round(s_tie_z, 1), sf(max(s_tie_y, s_tie_z), SY_PET)]
    gov = min(sf(s_z, SY_PET), o['다리 비틀림 + 굽힘(Y′ 당김, 비틀림 팔 표 그대로 58) τ · VM · SF(60) · SF(층간 30)'][3], sf(s_n, SY_PET), sf(max(s_tie_y, s_tie_z), SY_PET))
    o['지배 SF'] = gov; o['필요'] = need; o['판정'] = judge(gov, need)
    return o, T1


m2['오조작 50 N'], T1m = lg(F_MIS, NEED_MIS); m2['운전'], _ = lg(run2, NEED_RUN)
# 볼트 2개(간격 9)의 면 안 돌림 — Y′ 당김(판 밑)
pitch = math.hypot(GEO['P_RXDC03_LEAD_GUIDE']['new']['cyl'][1]['center'][0] - GEO['P_RXDC03_LEAD_GUIDE']['new']['cyl'][0]['center'][0],
                   GEO['P_RXDC03_LEAD_GUIDE']['new']['cyl'][1]['center'][1] - GEO['P_RXDC03_LEAD_GUIDE']['new']['cyl'][0]['center'][1])
pre2 = 1.5 * 1000 / (0.2 * 5)
M_in = F_MIS * tors_bolt
lig = 80.0 - 74.0 - 2.75                                     # 구멍(Y′ 80) ~ 패드 -Y′ 변(74) 살 3.25
inplane = {'볼트 간격 mm(STEP 구멍 2개)': round(pitch, 2), '면 안 돌림 N·mm(50 N x %.1f)' % tors_bolt: round(M_in), '예압 N(1.5 N·m)': pre2}
for mu in (0.2, 0.15, 0.0):
    cap = mu * pre2 * pitch                                   # 마찰 짝힘
    Fb = max(M_in - cap, 0.0) / pitch + (F_MIS / 2 if M_in > cap else 0.0)
    tau_so = Fb / (2 * lig * t_pad) if Fb else 0.0
    inplane['μ %.2f' % mu] = {'마찰이 버티는 돌림 N·mm · 미끄럼 여유': [round(cap), round(cap / M_in, 2)], '구멍 벽에 기대는 힘 N/개': round(Fb), '구멍 벽 면압 MPa · SF(60)': [round(Fb / (5 * t_pad), 1), sf(Fb / (5 * t_pad), SY_PET) if Fb else None],
                              '-Y′ 가장자리 살 %.2f 전단 MPa · SF(층 안 34.6) · SF(층간 17.3)' % lig: [round(tau_so, 1), sf(tau_so, SY_PET / math.sqrt(3)) if Fb else None, sf(tau_so, SY_LAY / math.sqrt(3)) if Fb else None]}
m2['볼트 2개의 면 안 돌림(Y′ 당김 50 N, 판정 밖)'] = inplane
cb = hc.calc(5, 10.0, round(T1m), 1.5, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
m2['볼트 CB5-16 x2 -> 그네 텅(A5052) 관통 탭 물림 10, 1.5 N·m'] = {'오조작 당김 N': round(T1m), '운용': cb['sf_operating'], '조임': cb['sf_tightening'], 'ok': cb['ok'],
                                                        '좌면(PET-CF 60 MPa) SF: 1.5 N·m · 4.5 N·m': [round(60 * AB / pre2, 2), round(60 * AB / 4500.0, 2)],
                                                        '조임 1.5 N·m 지정 볼트 수(PET-CF 좌면)': {'앞 회차까지': 43, '이 품번': 2, '합': 45}}
# 처짐 어림(다리만): Z′ 굽힘 · Y′ 당김(비틀림 + 굽힘)
G_PET = E_PET / 2.6; a_, c_ = max(leg_w, leg_h), min(leg_w, leg_h)
J = a_ * c_ ** 3 * (1 / 3.0 - 0.21 * c_ / a_ * (1 - c_ ** 4 / (12 * a_ ** 4)))
Lleg = X_LEG1 - X_PL1
dz_ = F_MIS * arm_leg ** 3 / (3 * E_PET * leg_w * leg_h ** 3 / 12)
dy_ = F_MIS * tors_tab * Lleg / (G_PET * J) * tors_tab + F_MIS * arm_leg ** 3 / (3 * E_PET * leg_h * leg_w ** 3 / 12)
m2['처짐 어림 mm(오조작, 다리만 · E 5 GPa)'] = {'Z′ 당김 판 자리': round(dz_, 2), 'Y′ 당김 판 밑': round(dy_, 2), '가장 가까운 이웃(모델링부 측정)': '스톱 블록 1.835(대기 자세) · 전원 케이블 1.853 — 처짐보다 큼'}
m2['민감도 — 좌면 패드 두께(첫 구멍 줄 구멍 뺀 단면, 지시 근거 아님)'] = {'t%g' % tp: {'MPa': round(F_MIS * (X_FACE - tp / 2 - X_CONN) / ((pad_w - 5.5) * tp ** 2 / 6), 1), 'SF(60)': sf(F_MIS * (X_FACE - tp / 2 - X_CONN) / ((pad_w - 5.5) * tp ** 2 / 6), SY_PET), 'CB5-16 물림 mm': 16 - tp} for tp in (6.0, 7.0, 8.0)}
m2['민감도 — 하중점(커넥터 축 = 판 앞 11, 임시 22 x 22 x 50)'] = {'좌면 패드 구멍 뺀 단면 MPa · SF': [round(F_MIS * (arm_pad + 11) / ((pad_w - 5.5) * t_pad ** 2 / 6), 1), sf(F_MIS * (arm_pad + 11) / ((pad_w - 5.5) * t_pad ** 2 / 6), SY_PET)],
                                                 '온 단면 MPa · SF': [round(F_MIS * (arm_pad + 11) / (pad_w * t_pad ** 2 / 6), 1), sf(F_MIS * (arm_pad + 11) / (pad_w * t_pad ** 2 / 6), SY_PET)]}
m2['과사양'] = {'오조작 지배 SF / 필요': round(m2['오조작 50 N']['지배 SF'] / NEED_MIS, 2), '문턱': 3.0, '판정': '아님'}
R['2_lead_guide_3dp'] = m2

# ================================================================== 3) 보 앞 받침 P_RXDC03_BEAM_CLAMP_판금 (t4 R4 폭 14 -> t3 R3 폭 24)
G3 = GEO['P_RXDC03_BEAM_CLAMP']['new']; bb = G3['bbox']; s3 = sig('P_RXDC03_BEAM_CLAMP_판금')
assert abs(SEC['P_RXDC03_BEAM_CLAMP']['volume'] - s3['volume']) < 0.01
cy = [c for c in G3['cyl'] if c['axis'] == 'X']; bend = min(cy, key=lambda c: c['r']); bend_o = max(cy, key=lambda c: c['r'])
hz = sorted(c['center'][1] for c in G3['cyl'] if c['axis'] == 'Y')
b = bb[0][1] - bb[0][0]; t = bend_o['r'] - bend['r']; yc3, zc3 = bend['center']
assert abs(b - 24.0) < 1e-6 and abs(t - 3.0) < 1e-6 and abs(SEC['P_RXDC03_BEAM_CLAMP']['sections']['선반 Y 90']['area_sum'] - b * t) < 0.01
y_tip, y_face = bb[1][0], bb[1][1]; y_mid = y_face - t / 2
Zg, Zn, Ag = b * t ** 2 / 6, (b - 5.5) * t ** 2 / 6, b * t
KI = ki_rect(bend['r'], t)
run3 = N_CAB * F_CAB + 0.07 * g * 3
m3 = {'형상(STEP)': {'상자': bb, '폭': b, '두께': t, '굽힘 안쪽 R · 중심 (Y, Z)': [bend['r'], [yc3, zc3]], '구멍 Ø5.5 Z': hz, '선반 끝 Y': y_tip, '보 맞댐 평면이 시작하는 Z': zc3, '부피 · 질량(서명)': [s3['volume'], s3['mass']]},
      '굽은 보 계수(안쪽 R = t)': round(KI, 3), '운전 하중 N': round(run3, 2)}


def clamp(F, need):
    Mw = F * (y_mid - y_tip)
    old = F * (y_face - t - y_tip) / Zg                       # 옛 모델: 벽 안쪽 면에서 곧은 외팔
    s_sh = F * (yc3 - y_tip) / Zg
    s_bend = KI * Mw / Zg + F / Ag
    d = [z - zc3 for z in hz]; Mp = F * (y_face - y_tip)
    Tb = [Mp * x / sum(v * v for v in d) for x in d]
    M_hole = Mw - sum(Tb) * (hz[0] - zc3)
    s_hole = abs(M_hole) / Zn + F / ((b - 5.5) * t)
    s_hole_full = Mw / Zn + F / ((b - 5.5) * t)               # 받침 반력이 덜어 주는 것을 안 뺀 값(모델링부 식)
    gov = max(s_bend, s_hole)
    return {'F N': round(F, 2), '옛 모델(곧은 외팔 %.0f) MPa · SF' % (y_face - t - y_tip): [round(old, 1), sf(old, SY)], '선반 굽힘 끝선(팔 %.0f) MPa · SF' % (yc3 - y_tip): [round(s_sh, 1), sf(s_sh, SY)],
            '굽힘 안쪽 겉면(굽은 보, 팔 %.1f) MPa · SF' % (y_mid - y_tip): [round(s_bend, 1), sf(s_bend, SY)],
            '아래 구멍 뺀 단면(받침 반력 뺌) MPa · SF': [round(s_hole, 1), sf(s_hole, SY)], '아래 구멍 뺀 단면(반력 안 뺌 — 모델링부 식) MPa · SF': [round(s_hole_full, 1), sf(s_hole_full, SY)],
            '볼트 당김 N [아래, 위](받침점 맞댐 평면 밑 끝 Z %.1f)' % zc3: [round(x, 1) for x in Tb], '지배 SF': sf(gov, SY), '필요': need, '판정': judge(SY / gov, need),
            '끝 처짐 mm(팔 %.1f 곧은 외팔 어림)' % (y_mid - y_tip): round(F * (y_mid - y_tip) ** 3 / (3 * E * b * t ** 3 / 12), 3)}, max(Tb)


m3['오조작 50 N 아래로'], Tm3 = clamp(F_MIS, NEED_MIS); m3['운전'], _ = clamp(run3, NEED_RUN)
bz = sig('CB5-12_RXDC03_CLAMP_1')['bbox']; le3 = bz[3] - 1.0 - y_face          # 볼트 끝(모따기 끝 1 뺌 — 물림 8.0은 검도 측정)
c3 = hc.calc(5, 8.0, round(Tm3, 1), TQ, '12.9', 'SS400', 8.5, 5.5, sf_min=2.0)
m3['볼트 CB5-12 x2 -> 보 앞벽 탭(STKR400 t8) 물림 8.0'] = {'볼트 상자 Y': bz[2:4], '오조작 당김 N(가장 큰 것)': round(Tm3, 1), '운용': c3['sf_operating'], '조임': c3['sf_tightening'], 'ok': c3['ok'],
                                                   '좌면(SUS304 400 MPa) 4.5 N·m': round(400 * AB / 4500.0, 2)}
hb = hc.beam(t, b, y_mid - y_tip, load=F_MIS, e=E, sy=SY, sf_min=NEED_MIS)
m3['엔진 handcalc beam(곧은 외팔 — 참고)'] = {k: hb[k] for k in ('stress_MPa', 'sf', 'deflection_mm', 'thin', 'needs_fea')}
m3['과사양'] = {'오조작 지배 SF / 필요': round(m3['오조작 50 N 아래로']['지배 SF'] / NEED_MIS, 2), '문턱': 3.0, '판정': '아님'}
m3['앞 회차(t4 · R4 · 폭 14)'] = {'오조작 SF': 2.35, '질량 g': 33.5}
R['3_beam_clamp'] = m3

# ================================================================== 4) T2 안내 P_RXDC03_T2_GUIDE_판금 (둘째 구멍 X -286 -> -284, 판 끝 -280 -> -276.5. 립 · 첫 구멍 그대로)
G4 = GEO['P_RXDC03_T2_GUIDE']['new']; bb4 = G4['bbox']; s4 = sig('P_RXDC03_T2_GUIDE_판금')
assert abs(SEC['P_RXDC03_T2_GUIDE']['volume'] - s4['volume']) < 0.01
bd = min((c for c in G4['cyl'] if c['axis'] == 'Y'), key=lambda c: c['r'])
hx = sorted(c['center'][0] for c in G4['cyl'] if c['axis'] == 'Z')
b4, t4 = bb4[1][1] - bb4[1][0], 3.0; xc4, zc4 = bd['center']; z_tip, z_top = bb4[2][0], bb4[2][1]; z_mid = z_top - t4 / 2
Zg4, Zn4, A4 = b4 * t4 ** 2 / 6, (b4 - 5.5) * t4 ** 2 / 6, b4 * t4
KI4 = ki_rect(bd['r'], t4); run4 = N_CAB * F_CAB + 0.02 * g * 3


def t2c(F, need):
    M = F * (z_mid - z_tip)
    s_bend = KI4 * M / Zg4 + F / A4; s_net = M / Zn4 + F / ((b4 - 5.5) * t4)
    gov = max(s_bend, s_net)
    return {'F N': round(F, 2), '굽힘 안쪽 겉면(굽은 보, 팔 %.1f) MPa · SF' % (z_mid - z_tip): [round(s_bend, 1), sf(s_bend, SY)], '첫 구멍 뺀 단면 MPa · SF': [round(s_net, 1), sf(s_net, SY)],
            '첫 볼트 당김 N(보수: 받침점 둘째 볼트, 간격 %.0f)' % (hx[1] - hx[0]): round(M / (hx[1] - hx[0]), 1), '지배 SF': sf(gov, SY), '필요': need, '판정': judge(SY / gov, need)}


m4 = {'형상(STEP)': {'상자': bb4, '폭': b4, '두께': t4, '굽힘 안쪽 R · 중심 (X, Z)': [bd['r'], [xc4, zc4]], '구멍 Ø5.5 X': hx, '부피 · 질량(서명)': [s4['volume'], s4['mass']]}, '굽은 보 계수': round(KI4, 3),
      '오조작 50 N': t2c(F_MIS, NEED_MIS), '운전': t2c(run4, NEED_RUN)}
T4 = m4['오조작 50 N']['첫 볼트 당김 N(보수: 받침점 둘째 볼트, 간격 %.0f)' % (hx[1] - hx[0])]
c4 = hc.calc(5, 9.0, T4, TQ, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
m4['볼트 CB5-12 x2 -> 블록 턱 M5 탭(A5052-H32) 물림 9.0'] = {'오조작 당김 N': T4, '운용': c4['sf_operating'], '조임': c4['sf_tightening'], 'ok': c4['ok']}
m4['앞 회차(둘째 구멍 X -286)'] = {'오조작 SF': 3.34, '첫 볼트 당김 N': 112.5}
R['4_t2_guide'] = m4

# ================================================================== 5) 묶음 완료 판정(강도 3항 + 바뀐 하중 부품)
o2 = m2['오조작 50 N']; o3 = m3['오조작 50 N 아래로']
R['5_judge'] = [
    {'항목': '세움 받침 국부(귀 뿌리 — 옛 국부 플랜지 자리)', '기준': '오조작 SF >= 2', '값': gov_ear, '판정': judge(gov_ear, NEED_MIS),
     '비고': '조임 상태(4.5 N·m) 판정. 예압이 풀렸다고 보면 %.2f(받침점 기둥 뒷면) · 옛 표 받침점 %.2f. 모델링부 2.38은 옛 표 받침점 + 온 폭 + R3 끝 단면' % (ear['판정 값(B) · 예압이 풀렸을 때(C) · 옛 표 받침점(D)'][1], ear['판정 값(B) · 예압이 풀렸을 때(C) · 옛 표 받침점(D)'][2])},
    {'항목': '세움 받침 전체(지배 = 웨브만 구간 Z 470)', '기준': '오조작 SF >= 2', '값': gov_r, '판정': judge(gov_r, NEED_MIS), '운전': m1['운전 10 N + 자중 x3 g %.2f N' % W3]['웨브만 구간 SF']},
    {'항목': '리드 안내 팔(다리 16 x 12)', '기준': '오조작 SF >= 2', '값': min(o2['다리 굽힘(Z′ 당김, 팔 %.1f) MPa · SF(60)' % arm_leg][1], o2['다리 비틀림 + 굽힘(Y′ 당김, 비틀림 팔 표 그대로 58) τ · VM · SF(60) · SF(층간 30)'][3]),
     '판정': judge(min(o2['다리 굽힘(Z′ 당김, 팔 %.1f) MPa · SF(60)' % arm_leg][1], o2['다리 비틀림 + 굽힘(Y′ 당김, 비틀림 팔 표 그대로 58) τ · VM · SF(60) · SF(층간 30)'][3]), NEED_MIS)},
    {'항목': '리드 안내 전체(지배 = 좌면 패드 첫 구멍 줄)', '기준': '오조작 SF >= 2', '값': o2['지배 SF'], '판정': o2['판정'], '운전': m2['운전']['지배 SF']},
    {'항목': '선반(보 앞 받침 t3 · R3 · 폭 24)', '기준': '오조작 SF >= 2', '값': o3['지배 SF'], '판정': o3['판정'], '운전': m3['운전']['지배 SF']},
    {'항목': 'T2 안내(판정 밖 — 바뀐 하중 부품)', '기준': '오조작 SF >= 2', '값': m4['오조작 50 N']['지배 SF'], '판정': m4['오조작 50 N']['판정'], '운전': m4['운전']['지배 SF']},
]
json.dump(R, open(ROOT + '/fea/results/detail_DP-4_fix1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 화면 요약(E-20, 15줄 안)
for j in R['5_judge']: print(j['항목'], '|', j['값'], '|', j['판정'], '| 운전', j.get('운전', '-'))
print('세움: 기둥 %s 웨브 %s 선반 %s | 귀 A~D' % (gov_col, gov_web, gov_shelf_r), [(round(T[k]), ear[k]['귀 뿌리 MPa · 첫 항복 SF · 소성 힌지 SF(x1.5)'][1:], ear[k]['모델링부 식(온 폭 · R3 끝) MPa · SF'][1], ear[k]['분리(예압/당김)']) for k in T])
print('  처짐', m1['끝 처짐 mm']['오조작 Y · X'], 'Hz', m1['끝 처짐 mm']['1차 고유 진동 Hz(끝 질량 = 선반, +케이블 50 g 가정)'], '| H112', m1['같은 단면 H112(110 MPa)면'], '| 뒤꿈치', m1['뒤꿈치 — -Y 50 N'])
print('  방향별', {k: (v.get('기둥 뿌리 VM MPa · SF', v.get('기둥 뿌리 VM · SF · 각°', v.get('기둥 뿌리 VM · SF · (방위, 높이각)'))), v.get('웨브만 구간 밑(Z 470) VM MPa · SF', v.get('웨브만 구간 VM · SF · 각°', v.get('웨브만 구간 VM · SF · (방위, 높이각)')))) for k, v in cases.items()})
print('  선반', shelf)
print('  볼트', {k: (v['운용'], v['조임'], v['ok']) for k, v in bolts.items() if 'H32' in k})
print('리드:', {k: v for k, v in o2.items() if k not in ('필요',)})
print('  면 안 돌림', inplane)
print('  볼트', m2['볼트 CB5-16 x2 -> 그네 텅(A5052) 관통 탭 물림 10, 1.5 N·m'], '| 처짐', m2['처짐 어림 mm(오조작, 다리만 · E 5 GPa)'])
print('보 앞:', {k: v for k, v in o3.items()}, '| 볼트', m3['볼트 CB5-12 x2 -> 보 앞벽 탭(STKR400 t8) 물림 8.0'], '| beam', m3['엔진 handcalc beam(곧은 외팔 — 참고)'])
print('T2:', m4['오조작 50 N'], '| 운전', m4['운전']['지배 SF'], '| 볼트', c4['sf_operating'], c4['sf_tightening'], c4['ok'])
