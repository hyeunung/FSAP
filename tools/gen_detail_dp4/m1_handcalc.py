# -*- coding: utf-8 -*-
"""DP-4 수정 1회차 모델링부 손계산(넘기기 전 확인, E-22) — 해석부 fea/cases/detail_DP-4_handcalc.py 와 같은 하중 · 팔 · 식.
하중: 오조작 = 케이블 손 당김 50 N(D-232 · D-38 임시). 판정: 오조작 SF >= 2(요구서 6-1). 재질: A5052-H32 195 · PET-CF 60(층간 30) · SUS304 205 MPa.
실행: python -X utf8 -B tools/gen_detail_dp4/m1_handcalc.py -> tools/out/detail/DP-4/m1/handcalc_m1.json"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
import handcalc as hc
SY, SY_AL, SY_AL112, E_AL, SY_PET, SY_LAY = 205.0, 195.0, 110.0, 70000.0, 60.0, 30.0
F = 50.0


def sf(s, sy): return round(sy / s, 2)


def ka(a, c):
    a, c = max(a, c), min(a, c)
    return 1 / 3.0 - 0.21 * (c / a) * (1 - c ** 4 / (12 * a ** 4))


def ki_rect(ri, t):
    ro, rc = ri + t, ri + t / 2.0
    rn = t / math.log(ro / ri); e = rc - rn
    return ((rn - ri) / (t * e * ri)) / (6.0 / t ** 2)


R = {}
# ---------------- 1) 세움 받침 P_RXDC03_RISER_BRKT_밀링 (A5052-H32)
M_root = F * 234.0
bx, hy = 15.0, 10.5
sYc = M_root / (bx * hy ** 2 / 6); tau = F * 19.5 / (ka(bx, hy) * bx * hy ** 2); vm = math.hypot(sYc, math.sqrt(3) * tau)
sXc = M_root / (hy * bx ** 2 / 6)
col = {'단면': '15 x 10.5 속 참(Z 256~470), 뿌리 X 쪽 R3', 'Y 당김 굽힘 MPa': round(sYc, 1), '비틀림(먼 타이 팔 19.5) MPa': round(tau, 1), 'VM MPa': round(vm, 1),
       'SF H32': sf(vm, SY_AL), 'SF H112': sf(vm, SY_AL112), 'X 당김 MPa · SF': [round(sXc, 1), sf(sXc, SY_AL)],
       '끝 처짐 Y mm(오조작)': round(F * 234.0 ** 3 / (3 * E_AL * bx * hy ** 3 / 12), 2)}
tw = 2.75
Zw = bx * tw ** 2 / 6; Zws = tw * bx ** 2 / 6
sW = F * 16.0 / Zw; tauW = F * 19.5 / (ka(bx, tw) * bx * tw ** 2); vmW = math.hypot(sW, math.sqrt(3) * tauW)
dn = F * (83.625 - 74) / Zw + F * 19.5 / Zws
cn = F * 18.625 / Zw + F * 38.1 / Zws
web = {'단면': '웨브만 15 x 2.75(Z 470~484.25, Y 82.25~85 — 케이블 쪽 0.25 물림)', 'Y 당김(Z 486, 팔 16) 굽힘 MPa': round(sW, 1), '비틀림(팔 19.5) MPa': round(tauW, 1),
       'VM MPa': round(vmW, 1), 'SF H32': sf(vmW, SY_AL), '굽힘만 SF(PM 어림과 같은 식 — t3이면 35.6 MPa 5.5)': sf(sW, SY_AL),
       '아래로 당김(먼 타이 X -300 · Y 74) MPa · SF': [round(dn, 1), sf(dn, SY_AL)],
       '민감도: 선반 구석(X -318.6 · Y 65) 아래로 50 N(하중 표에 없음) MPa · SF': [round(cn, 1), sf(cn, SY_AL)]}
sh1 = F * 12.0 / ((20 - 2) * tw ** 2 / 6); sh2 = F * 8.25 / Zw; sh3 = F * 17.25 / Zw
shelf = {'단면': '선반 t2.75(밑면 Z 484.25)', '아래로 당김(먼 타이): 기둥 -X 면 단면(폭 20 - 홈 2, 팔 12) MPa · SF': [round(sh1, 1), sf(sh1, SY_AL)],
         '웨브 앞 단면(폭 15, 팔 8.25) MPa · SF': [round(sh2, 1), sf(sh2, SY_AL)], '민감도: 구석 누름(팔 17.25, 폭 15) MPa · SF': [round(sh3, 1), sf(sh3, SY_AL)]}
M50 = F * (487.0 - 251.5); ear_y = 79.0
kr = M50 / ((97 - ear_y) ** 2 + 2 * (97 - 90) ** 2)
T_rigid = kr * (97 - ear_y); T_back = M50 / (85.0 - ear_y); T_cons = M50 / (83.5 - ear_y)
Zear = 25.25 * 6.0 ** 2 / 6
ear = {'단면': '귀 뿌리 = R3 끝 X -270(볼트 축에서 4.75), 폭 25.25 x t6',
       '볼트 당김 N [밑판 강체(받침점 Y 97), 받침점 기둥 뒷면 Y 85, 해석부 보수(Y 83.5)]': [round(T_rigid), round(T_back), round(T_cons)],
       'MPa': [round(t * 4.75 / Zear, 1) for t in (T_rigid, T_back, T_cons)], 'SF H32': [sf(t * 4.75 / Zear, SY_AL) for t in (T_rigid, T_back, T_cons)],
       'R 없이 기둥 면 X -273(팔 7.75)일 때 SF': [sf(t * 7.75 / Zear, SY_AL) for t in (T_rigid, T_back, T_cons)]}
T90 = M50 / (2 * (90 - 74.5))
t90r = kr * 7
heel = T_rigid + 2 * t90r; Mb = heel * 12 - 2 * t90r * 5
sbase = Mb / (39 * 36 / 6)
base = {'기둥 뒷면 Y 85 단면(+Y 밀기, 받침점 Y 97, 유효 폭 39 x t6) MPa · SF': [round(sbase, 1), sf(sbase, SY_AL)], '뒤 볼트 2 당김 N/개(-Y 당김, 받침점 기둥 앞면 Y 74.5)': round(T90)}
bolts = {}
for lbl, T, le in (('귀 CB5-16 물림 10 · 보수 당김', T_cons, 10.0), ('귀 CB5-16 물림 10 · 밑판 강체', T_rigid, 10.0), ('뒤 CB5-16 x2 물림 10', T90, 10.0)):
    for tl, b in (('H32', 'A5052'), ('H112', 'A5052-H112')):
        c = hc.calc(5, le, round(T), 4.5, '12.9', b, 8.5, 5.5, sf_min=2.0)
        bolts['%s · 블록 %s' % (lbl, tl)] = {'당김 N': round(T), '운용 SF': c['sf_operating'], '조임 4.5 N·m SF': c['sf_tightening'], 'ok': c['ok']}
ab = math.pi / 4 * (8.5 ** 2 - 5.5 ** 2)
bolts['좌면(A5052 210 MPa) 4.5 N·m SF'] = round(210 * ab / 4500.0, 2)
gov = min(col['SF H32'], web['SF H32'], sf(sh1, SY_AL), sf(sh2, SY_AL), ear['SF H32'][2], sf(sbase, SY_AL))
R['1_riser_milled'] = {'기둥 뿌리': col, 'Z 470 웨브만 구간': web, '선반': shelf, '귀 뿌리': ear, '밑판': base, '볼트': bolts, '지배 SF(오조작, H32)': gov, '판정(>= 2)': gov >= 2.0,
                       '과사양 비(지배 SF / 필요 2, 문턱 3)': round(gov / 2.0, 2), '질량 g': 114.2}


# ---------------- 2) 리드 안내 P_RXDC03_LEAD_GUIDE_3DP (PET-CF, 층 법선 = 세운 판 폭 방향)
def leg(bw, tt):
    s_arm = F * 47.6 / (bw * tt ** 2 / 6)
    tq = F * 58.0 / (ka(bw, tt) * max(bw, tt) * min(bw, tt) ** 2)
    sYs = F * 47.6 / (tt * bw ** 2 / 6); v = math.hypot(sYs, math.sqrt(3) * tq)
    return {'굽힘(Z 쪽) MPa · SF(60)': [round(s_arm, 1), sf(s_arm, SY_PET)], '비틀림 MPa': round(tq, 1), '비틀림 + 굽힘(Y 당김) VM': round(v, 1), 'SF(60)': sf(v, SY_PET), 'SF(층간 30)': sf(v, SY_LAY)}


tie = F * 22.0 / (10 * 7.0 ** 2 / 6)
pad = F * 47.6 / (20 * 6.0 ** 2 / 6); padn = F * 47.6 / ((20 - 5.5) * 6.0 ** 2 / 6)
plate = F * 46.0 / ((16 + 2 * 5) * 5.0 ** 2 / 6)
Tb = F * 47.6 * 10 / (10 ** 2 + 1 ** 2)
cb = hc.calc(5, 10.0, round(Tb), 1.5, '12.9', 'A5052', 8.5, 5.5, sf_min=2.0)
L16 = leg(16.0, 12.0)
lg = {'다리 16 x 12(외팔 47.6, 비틀림 팔 58 — 해석부와 같은 팔)': L16, '다리 14 x 12': leg(14.0, 12.0), '다리 14 x 8(PM 시작값)': leg(14.0, 8.0),
      '타이 판 t7 x 폭 10(끝 50 N, 팔 22) MPa · SF(60) · SF(30)': [round(tie, 1), sf(tie, SY_PET), sf(tie, SY_LAY)],
      '좌면 패드 20 x t6: 다리 위 단면 MPa · SF(60)': [round(pad, 1), sf(pad, SY_PET)], '구멍 뺀 단면(머리 밑, 죄어 있음) MPa · SF(60)': [round(padn, 1), sf(padn, SY_PET)],
      '세운 판 t5(X 밀기, 다리 밑 단면 유효 폭 26, 팔 46) MPa · SF(60)': [round(plate, 1), sf(plate, SY_PET)],
      '볼트 CB5-16 x2 -> 그네 텅(A5052) 관통 탭 물림 10, 1.5 N·m': {'당김 N': round(Tb), '운용 SF': cb['sf_operating'], '조임 SF': cb['sf_tightening'], 'ok': cb['ok']},
      '좌면(PET-CF 60 MPa) 1.5 N·m SF': round(60 * ab / 1500.0, 2), '질량 g': 34.5}
g2 = min(L16['SF(층간 30)'], sf(tie, SY_LAY), sf(pad, SY_PET), sf(padn, SY_PET), sf(plate, SY_PET))
lg['지배 SF(오조작)'] = g2; lg['판정(>= 2)'] = g2 >= 2.0
R['2_lead_guide_3dp'] = lg
# ---------------- 3) 보 앞 받침 선반 (SUS304 t3 R3 폭 24)
k = ki_rect(3.0, 3.0); arm = 118.5 - 68.0
sb = k * F * arm / (24 * 9 / 6); sn = F * arm / ((24 - 5.5) * 9 / 6)
T2 = F * arm * 28 / (16 ** 2 + 28 ** 2)
cc = hc.calc(5, 8.0, round(T2), 4.5, '12.9', 'SS400', 8.5, 5.5, sf_min=2.0)
R['3_beam_clamp_t3_w24'] = {'굽은 보 계수(R3 · t3)': round(k, 3), '굽힘 안쪽 겉면 MPa · SF': [round(sb, 1), sf(sb, SY)], '아래 구멍 뺀 단면 MPa · SF': [round(sn, 1), sf(sn, SY)],
                            '지배 SF': min(sf(sb, SY), sf(sn, SY)), '판정(>= 2)': min(sf(sb, SY), sf(sn, SY)) >= 2.0, '폭 14였다면 SF': sf(k * F * arm / (14 * 9 / 6), SY),
                            '위 볼트 당김 N · 운용 SF': [round(T2), cc['sf_operating']], '질량 g': 46.0}
json.dump(R, open('C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/tools/out/detail/DP-4/m1/handcalc_m1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False))
