# -*- coding: utf-8 -*-
"""RX-11 해석부 수정 1회차 손계산(2026-11-13, v2.17.1). FEA 못 함 — 환경 없음(자료대기 D-16).
수정 1회차는 형상 그대로, CB5-20_RX11 x8 조임 지정 3 -> 0.6 N·m + 중강도 나사 고정제(mech_RX-11_model1.md).
E-21: 앞 회차 케이스(fea/cases/mech_RX-11_handcalc.py)를 그대로 다시 돌려 값이 같은지 보고(형상 STEP 해시 같음), 남은 것만 더 본다.
 A. 앞 회차 결과 재현(같은 STEP, 같은 machine.json _timing) — 다른 값 0이어야 함
 B. 지정 0.6 N·m: 새들 단면 전 구간 훑기(예압 + 바퀴 누름 겹침, 한쪽 줄 치우침 포함), 클램프, 볼트
 C. 예압 흩어짐: 토크 계수 K 0.25 / 0.20 / 0.15 / 0.12(나사 고정제 윤활 가정), 토크 +30 %
 D. 새로 본 것: 귀 반력 자리와 기둥 반력 자리가 어긋날 때 판 살에 걸리는 짝힘 -> 살 끝(새들 자리) 내려앉음 (완료 판정 ② 사슬)
 E. 완료 판정 ② 사슬(모델 값 + 새들 축 자리 내려앉음 + 판 살 짝힘), ④·⑤는 앞 회차 값 재현
실행: python -X utf8 -B fea/cases/mech_RX-11_fea1_handcalc.py
"""
import hashlib, json, math, runpy, sys

ROOT = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP'
PREV = sys.argv[1] if len(sys.argv) > 1 else None      # 앞 회차 결과 json 사본(대조용)
STEPD = ROOT + '/tools/out/mech_RX-11/stepout/'
OUT = {'_설명': 'RX-11 해석부 수정 1회차 손계산(v2.17.1, 조임 0.6 N·m). 좌표 = 세계 좌표(mm), 힘 N, 응력 MPa'}

# ---------- A. 앞 회차 케이스 재현 ----------
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    B = runpy.run_path(ROOT + '/fea/cases/mech_RX-11_handcalc.py')
R0 = json.loads(json.dumps(B['R'], ensure_ascii=False))
diff = None
if PREV:
    old = json.load(open(PREV, encoding='utf-8'))
    diff = []

    def walk(a, b, p=''):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b)):
                if k not in a or k not in b:
                    diff.append(p + '/' + k)
                else:
                    walk(a[k], b[k], p + '/' + k)
        elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, p + '/%d' % i)
        elif a != b:
            diff.append(p)
    walk(old, R0)
OUT['A 앞 회차 재현'] = {
    'STEP sha256 앞 16자': {f: hashlib.sha256(open(STEPD + f, 'rb').read()).hexdigest()[:16] for f in
                         ('P_RX11_SADDLE.step', 'P_RX11_CLAMP.step', 'P_M04_PANEL_W2.step', 'P_M04_PANEL_E2.step', 'HFS8-4080-560_M04_NOTCH.step')},
    'machine.json doc': json.load(open(ROOT + '/tools/machine.json', encoding='utf-8')).get('doc'),
    '앞 회차 json과 다른 값 수': None if diff is None else len(diff), '다른 키': diff[:10] if diff else []}

saddle_sec, saddle, clamp, calc = B['saddle_sec'], B['saddle'], B['clamp'], B['calc']
SY = B['SY']['A5052']; E_AL = B['E_AL']; TX = B['TX']
F_OP, F_MIS, F_HAND = B['F_OP'], B['F_MIS'], B['F_HAND']
SF_OP, SF_MIS, SF_PERM = B['SF_OP'], B['SF_MIS'], B['SF_PERM']
Y_H = 2 * 3.5 / math.pi                                 # 머리 좌면 고리(평균 반지름 3.5) 한쪽 도심
Y_SEAT = 11.0                                           # 축 홈 자리(롤러 2줄 Y ±11)


# ---------- B. 새들: 예압 + 바퀴 누름 겹침, 단면 전 구간 ----------
def sweep(loads, y_r, dy=0.02):
    """받침 ±y_r 단순보, loads = [(y, P 아래로)]. 전 구간 M(y) x 단면(saddle_sec) -> 최대 응력과 자리."""
    tot = sum(P for _, P in loads); Rr = sum(P * (y + y_r) for y, P in loads) / (2 * y_r); Rl = tot - Rr
    worst = (0.0, None, None); n = int(2 * y_r / dy)
    for i in range(1, n):
        y = -y_r + i * dy
        m = Rl * (y + y_r) - sum(P * (y - yi) for yi, P in loads if yi < y)
        s = saddle_sec(y)
        st, sb = m * s['c_top'] / s['I'], m * s['c_bot'] / s['I']
        sg = max(st, sb)
        if sg > worst[0]:
            worst = (sg, round(y, 2), '위(압축)' if st >= sb else '밑(인장)')
    return worst


def pre(P):
    return [(-Y_H, P / 2), (Y_H, P / 2)]


def wheel_sym(F):
    return [(-Y_SEAT, F / 2), (Y_SEAT, F / 2)]


def wheel_one(F):                                       # 바퀴가 한쪽 줄에만 얹힘(불리)
    return [(Y_SEAT, F)]


def saddle_case(P, y_r):
    row = {}
    for nm, extra, sfm in (('예압만', [], SF_OP), ('예압 + 운전 46.54 N(두 줄 반씩)', wheel_sym(F_OP), SF_OP), ('예압 + 운전 46.54 N(한 줄이 다)', wheel_one(F_OP), SF_OP),
                           ('예압 + 오설정 130 N(두 줄 반씩)', wheel_sym(F_MIS), SF_MIS), ('예압 + 오설정 130 N(한 줄이 다)', wheel_one(F_MIS), SF_MIS),
                           ('예압 + 손 100 N(한 줄이 다)', wheel_one(F_HAND), SF_MIS)):
        sg, y, side = sweep(pre(P) + extra, y_r)
        row[nm] = {'σ_max MPa': round(sg, 1), '자리 Y': y, '쪽': side, 'SF(195)': round(SY / sg, 2), '기준': sfm, 'ok': SY / sg >= sfm, '영구 변형 선 1.2': SY / sg >= SF_PERM}
    return row


bsec = {}
chk = sweep(pre(600.0), 24.75)
bsec['_확인(예압 600 N만, 받침 24.75)'] = {'σ_max': round(chk[0], 1), '자리': chk[1], '앞 회차 값': R0['새들·클램프(볼트 예압)']['조임 0.60 N·m']['새들 반력 귀 받침 가운데 Y 24.75(불리)']['최저 SF_탄성']}
for nm, yr in (('받침 Y 24.75(불리)', 24.75), ('받침 Y 23.5(유리)', 23.5)):
    bsec['지정 0.6 N·m(예압 600 N) ' + nm] = saddle_case(600.0, yr)
OUT['B 새들(지정 0.6 N·m, 예압 + 바퀴 누름)'] = bsec

# ---------- C. 예압 흩어짐 ----------
csec = {}
for nm, T, K in (('K 0.25(마른 면)', 0.6, 0.25), ('K 0.20(지정 계산값)', 0.6, 0.20), ('K 0.15', 0.6, 0.15), ('K 0.12(나사 고정제가 윤활할 때, 가정)', 0.6, 0.12),
                 ('토크 +30 % (0.78 N·m, K 0.20)', 0.78, 0.20), ('토크 +30 % · K 0.15', 0.78, 0.15)):
    P = T * 1000 / (K * 5)
    sc = saddle_case(P, 24.75)
    rows, w_c, w_11 = saddle(P, 24.75)
    mc, sgc = clamp(P, 26.75)
    csec[nm] = {'예압 N': round(P), '새들 SF 예압만': sc['예압만']['SF(195)'], '새들 SF + 운전(한 줄이 다)': sc['예압 + 운전 46.54 N(한 줄이 다)']['SF(195)'],
                '새들 SF + 오설정 130 N(한 줄이 다)': sc['예압 + 오설정 130 N(한 줄이 다)']['SF(195)'], '클램프 SF(불리)': round(SY / sgc, 2),
                '축 자리(Y 11) 내려앉음 mm': round(w_11, 4), '머리 좌면 MPa': round(P / B['HEAD_A'], 1)}
# 한계 예압(받침 24.75, 예압만): SF 3 / 2 / 1.2 / 1.0
s600 = sweep(pre(600.0), 24.75)[0]
lim = {}
for sf in (3.0, 2.0, 1.2, 1.0):
    Pl = 600.0 * SY / (sf * s600)
    lim['SF %.1f' % sf] = {'예압 N': round(Pl), '토크 N·m(K 0.20)': round(Pl * 0.2 * 5 / 1000, 2), '토크 N·m(K 0.12)': round(Pl * 0.12 * 5 / 1000, 2)}
csec['_한계 예압·토크(새들, 예압만)'] = lim
csec['_볼트(handcalc.calc 0.6 N·m, 물림 11.5, A5052 탭)'] = calc(5, 11.5, 0.0, torque=0.6, bolt='12.9', base='A5052', dw=8.5, dh=5.5, sf_min=SF_OP)
OUT['C 예압 흩어짐'] = csec

# ---------- D. 판 살에 걸리는 짝힘(귀 반력 자리 ↔ 기둥 반력 자리 어긋남) ----------
# 귀(판 윗면, |Y| 23 ~ 26.5)가 아래로 P/2, 클램프 기둥(판 밑면, |Y| 23.5 ~ 30)이 위로 P/2. 두 도심이 e만큼 어긋나면 살(뿌리 Y 80 외팔)에 짝힘 P/2 x e.
# 살 = 판 W2 SUS304 t 4, 폭 50 외팔보(앞 회차 '폭 50 보' 모델, 상한). 뿌리 회전 몫도 앞 회차와 같은 두 모델(접시 볼트 줄이 잡음 / 안 잡고 먼 레일까지 돎).
E_SUS = B['E_SUS']; T_PL, B_EFF, Y_ROOT = B['T_P'], 50.0, 80.0
I_PL = B_EFF * T_PL ** 3 / 12
G_SUS = E_SUS / 2.6


def couple(P, y_ear, y_post):
    Rr = P / 2; a1 = Y_ROOT - y_ear; a2 = Y_ROOT - y_post       # 뿌리에서 잰 거리. 귀(아래로) a1, 기둥(위로) a2

    def w_at(a_load, a_pt):                                   # 외팔 점하중 1 N(a_load)이 a_pt에 만드는 처짐
        a, x = (a_load, a_pt) if a_pt >= a_load else (a_pt, a_load)
        return a ** 2 * (3 * x - a) / (6 * E_SUS * I_PL)
    w = Rr * (w_at(a1, a1) - w_at(a2, a1))                    # 귀 자리 처짐(아래 +), 뿌리 고정
    m = Rr * abs(a1 - a2)
    th_scr = m * 20.0 / (3 * E_SUS * I_PL)                    # 뿌리 회전: 접시 볼트 줄(Y 100)이 잡음, 뒤 경간 20
    th_far = m * 220.0 / (3 * E_SUS * (216 * 0.64 * T_PL ** 3 / 12))   # 안 잡고 먼 레일(Y 300)까지 220, 폭 = 새들 피치 216 x 0.64
    return {'e mm': round(y_post - y_ear, 2), '짝힘 N·mm': round(m), '새들 자리 내려앉음 mm(뿌리 고정)': round(w, 4),
            '뿌리 회전 몫 mm(볼트 줄이 잡음 / 안 잡음)': [round(th_scr * a1, 4), round(th_far * a1, 4)],
            '새들 자리 내려앉음 상한 mm(뿌리 고정 + 안 잡음)': round(w + th_far * a1, 4), '판 살 굽힘 MPa(폭 50)': round(6 * m / (B_EFF * T_PL ** 2), 2)}


dsec = {'_모델': '판 W2 살 = 뿌리 Y 80 외팔 · 폭 50 x t 4(SUS304 E 193,000, 앞 회차 폭 50 보 모델 = 상한). 귀 도심 24.75(고른 면압) / 기둥 도심 26.75(고른 면압) ~ 23.5(안쪽 끝에 몰림 -> e ≤ 0, 하한 0)'}
for nm, P in (('3 N·m(앞 지정, 예압 3,000 N)', 3000.0), ('0.6 N·m K 0.20(600 N)', 600.0), ('0.6 N·m K 0.15(800 N)', 800.0), ('0.6 N·m K 0.12(1,000 N, 가정)', 1000.0)):
    dsec[nm] = {'고른 면압끼리(e 2.0, 상한)': couple(P, 24.75, 26.75), '귀 면압 MPa': round(P / 2 / (3.5 * TX), 1), '기둥 면압 MPa': round(P / 2 / (6.5 * TX), 1)}
# E2 끝 새들(X -326): 귀 받침 길은 X 방향(가로대 CM1 +X 면에서 살 9 x t 4 · 길이 42, 앞 회차 상한 모델)이라 Y로 어긋난 짝힘은 살을 비튼다. 긴 홈 닫힌 끝(X -317)은 안 셈(불리).
J_LIG = 0.24 * 9.0 * T_PL ** 3                            # 9 x 4 직사각형 비틀림 상수(b/t 2.25, β 0.24)
th_tw = (600.0 / 2 * 2.0) * 42.0 / (G_SUS * J_LIG)
dsec['E2 끝 새들(600 N, e 2.0) 살 9 비틀림'] = {'비틀림 각 rad': round(th_tw, 5), '귀 자리 내려앉음 mm(각 x 귀 폭 3.5)': round(th_tw * 3.5, 4)}
OUT['D 판 살 짝힘'] = dsec

# ---------- E. 완료 판정 ② 사슬 ----------
Z_MODEL = -0.0002                                        # 검도(v2.17.1, mech_RX-11_verify1.md) 롤러 윗면 모델 값
esec = {}
for nm, P in (('0.6 N·m K 0.20', 600.0), ('0.6 N·m K 0.15', 800.0), ('0.6 N·m K 0.12(가정)', 1000.0), ('3 N·m(앞 지정, 탄성분만)', 3000.0)):
    w11 = saddle(P, 24.75)[2]; cc = couple(P, 24.75, 26.75); wc = cc['새들 자리 내려앉음 mm(뿌리 고정)']; wcu = cc['새들 자리 내려앉음 상한 mm(뿌리 고정 + 안 잡음)']
    lo, mid, hi = abs(Z_MODEL) + w11, abs(Z_MODEL) + w11 + wc, abs(Z_MODEL) + w11 + wcu
    esec[nm] = {'새들 축 자리 내려앉음 mm': round(w11, 4), '판 살 짝힘 몫 mm(0 / 뿌리 고정 / 뿌리 돎 상한)': [0.0, wc, wcu],
                '롤러 윗면 낮아짐 mm(무부하: 하한 / 뿌리 고정 / 상한)': [round(lo, 3), round(mid, 3), round(hi, 3)], '한도 mm': 0.1, 'ok': hi <= 0.1}
OUT['E 완료 판정 ② 사슬(롤러 윗면 Z 0 ± 0.1)'] = esec

rl = R0['롤러·베어링·축']; tm = R0['회전 시간 키·SF(띠 항 없음)']
OUT['완료 판정 ④(앞 회차 재현)'] = {'롤러 처짐 mm 46.54 / 130 N': [rl['운전 46.54 N']['롤러 처짐 mm(한 줄이 다 받음, 가운데)'], rl['오설정 130 N']['롤러 처짐 mm(한 줄이 다 받음, 가운데)']],
                              '696ZZ 정적 SF 46.54 / 130 N': [rl['운전 46.54 N']['696ZZ 정적 SF(한 베어링이 다 받음)'], rl['오설정 130 N']['696ZZ 정적 SF(한 베어링이 다 받음)']],
                              '받침 합 처짐': R0['받침 합 처짐']}
OUT['완료 판정 ⑤(앞 회차 재현)'] = {'_최저 SF(L·G·V)': tm['_최저 SF(L·G·V)'], '_판정': tm['_판정']}

json.dump(OUT, open(ROOT + '/fea/results/mech_RX-11_fea1_handcalc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 화면 요약(E-20, 15줄 안) ----------
b = bsec['지정 0.6 N·m(예압 600 N) 받침 Y 24.75(불리)']; b2 = bsec['지정 0.6 N·m(예압 600 N) 받침 Y 23.5(유리)']
print('A 재현: 앞 회차와 다른 값', OUT['A 앞 회차 재현']['앞 회차 json과 다른 값 수'], OUT['A 앞 회차 재현']['다른 키'], '| doc', OUT['A 앞 회차 재현']['machine.json doc'])
print('B 확인(600 N만):', bsec['_확인(예압 600 N만, 받침 24.75)'])
for k, v in b.items():
    print('B 0.6 N·m 불리 |', k, '| σ', v['σ_max MPa'], '@Y', v['자리 Y'], v['쪽'], '| SF', v['SF(195)'], '/ 기준', v['기준'], '| 유리 SF', b2[k]['SF(195)'])
for k, v in csec.items():
    if not k.startswith('_'):
        print('C', k, '|', v)
print('C 한계:', lim)
print('D:', {k: (v.get('고른 면압끼리(e 2.0, 상한)', v)) for k, v in dsec.items() if not k.startswith('_')})
print('E:', {k: (v['롤러 윗면 낮아짐 mm(무부하: 하한 / 뿌리 고정 / 상한)'], v['ok']) for k, v in esec.items()})
print('④', OUT['완료 판정 ④(앞 회차 재현)']['롤러 처짐 mm 46.54 / 130 N'], OUT['완료 판정 ④(앞 회차 재현)']['696ZZ 정적 SF 46.54 / 130 N'], '⑤', OUT['완료 판정 ⑤(앞 회차 재현)'])
