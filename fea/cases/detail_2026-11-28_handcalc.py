# -*- coding: utf-8 -*-
"""디테일링 2026-11-28 해석부 손계산 — v2.30.6, fea/models.json에 없던 부품과 t4 재검토.

FEA: 엔진 해석 환경 engine/fea/.venv 없음 -> 해석 못 함 — 환경 없음(자료대기 D-16).
형상: tools/out/detail/stepout/*.step 꼭짓점 좌표와 tools/out/signatures.json bbox(v2.30.6). CAD 안 씀.
판 L은 mech_M07-K1_fea1_handcalc.py와 같은 모델(굽힘 구석 t+R 고정 외팔, 머리 안쪽 가장자리에 힘, 곡률보 Kt 1.3).
임시값: 기대는 손 100 N(D-38), HMI 2.0 kg·누름 30 N(mech_M08_design.md 4절), CB5 예압 4 kN · 마찰 0.15(D-54),
접기·보내기 저항 2~10 N(D-06 미정), 공급 0.5 MPa(요구서 2-4 운전 압력 미정 — 지난 케이스와 같은 값).
"""
import json, math, sys
sys.path.insert(0, 'C:/Users/hyeun/OneDrive/Documents/workspace/MechDesign_Engine/engine/tools')
from handcalc import calc, beam  # 엔진 도구 읽기만

G = 9.80665
SUS, E_SUS = 205.0, 193000.0
A5052, E_AL = 195.0, 70000.0
CSP_HALF = 470.0      # SUS304-CSP 1/2H 0.2 % 내력 하한(JIS G 4313 기억값 — 임시)
KT = 1.3
R_HEAD = 4.25
FV, MU = 4000.0, 0.15  # D-54
out = {'task': 'detail_2026-11-28', 'dept': '해석부', 'doc': 'FSAP_v2.30.6', 'fea': '해석 못 함 — 환경 없음(자료대기 D-16)'}


def sf(rp, s):
    return round(rp / s, 2) if s > 0 else None


def leg(t, r_in, b, hole, force, rp=SUS):
    """굽힘 구석 고정 외팔: 팔 = 구멍 - (t + R) - 머리 반지름, Kt 1.3"""
    arm = max(hole - (t + r_in) - R_HEAD, 1.0)
    s = 6 * force * arm / (b * t * t) * KT
    return {'t': t, 'b': b, 'hole': hole, 'arm': round(arm, 2), 'F_N': round(force, 1), 'sigma_MPa': round(s, 1), 'sf': sf(rp, s)}


# ---------- 1. 판금 L(S·T·C형) t6 -> t4 (판금부 SH-01·SH-02가 물음) ----------
F_LAT, R_CM1 = 286.0, 473.8   # mech_M07-K1_fea1과 같은 하중
L = {}
for t in (6.0, 4.0):
    row = {}
    for name, hole in (('T(구멍 60)', 60.0), ('S(구멍 30)', 30.0), ('C(구멍 20)', 20.0)):
        row[name] = leg(t, t, 30.0, hole, F_LAT)
    m = R_CM1 * 30.0
    sb = m / (30.0 * t * t / 6)
    tt = m / (0.291 * 30.0 * t * t)
    row['가로대 끝(S형 22개) 굽힘'] = {'sigma_MPa': round(sb, 1), 'sf': sf(SUS, sb)}
    row['가로대 끝 비틀림'] = {'tau_MPa': round(tt, 1), 'sf': sf(0.577 * SUS, tt)}
    L['t%g' % t] = row
out['L_bracket_t6_vs_t4'] = L

# ---------- 2. 라이트 커튼 기둥 받침 ----------
# 앞오른 기둥 HFS8-4080-1175_M08_FR(Z -370~805)을 P_M08_LC_BRKT_FR_SM_1(Z -290)·_2(Z -52)가 잡는다. 꼭대기에 손 100 N.
H_top, z1, z2 = 805.0, -290.0, -52.0
R_up = 100.0 * (H_top - z1) / (z2 - z1)
R_lo = R_up - 100.0
lc = {'tier_force_N': {'위 SM_2': round(R_up, 1), '아래 SM_1': round(R_lo, 1)}}
for t in (4.0, 6.0):
    lc['t%g' % t] = {
        'SM_2 X 기댐(기둥 쪽 다리 75, 구멍 60, 폭 72)': leg(t, t, 72.0, 60.0, R_up),
        'SM_1 X 기댐(폭 80)': leg(t, t, 80.0, 60.0, R_lo),
        'SM_2 -Y 당김(레일 쪽 다리 60, 구멍 45)': leg(t, t, 72.0, 45.0, R_up),
    }
out['P_M08_LC_BRKT_FR_SM'] = lc

# 뒤 기둥 HFS8-4080-1175_M08_R: P_M08_LBRK_R1~R3(Z -300·150·600), 구멍 구석에서 20, 볼트 1개씩
R_r = 100.0 * (H_top - 150.0) / (600.0 - 150.0)
out['P_M08_LBRK_R'] = {'top_tier_N': round(R_r, 1), 't6': leg(6.0, 6.0, 30.0, 20.0, R_r), 't4': leg(4.0, 4.0, 30.0, 20.0, R_r)}

# 앞왼 2번 커튼 받침 P_M08_LC2F_BRKT_SM(t3, 폭 30, 긴 다리 구멍 22·짧은 다리 15)
F_half = 50.0
m_head = F_half * (1580.0 - 1537.0 - R_HEAD)     # 커튼 중심 Y -1537 <-> 볼트 Y -1580
s_head = 6 * m_head / (30.0 * 9.0)
m_bend = F_half * (1564.0 - 1537.0)
s_bend = 6 * m_bend / (30.0 * 9.0) * KT
r_eff = (2.0 / 3.0) * (8.5 ** 3 - 5.5 ** 3) / (8.5 ** 2 - 5.5 ** 2) / 2.0
w3g = 1.1386 * G * 3 / 2
out['P_M08_LC2F_BRKT_SM'] = {
    '손 100 N을 두 받침이 나눔(50 N)': {'머리 가장자리 sigma': round(s_head, 1), 'sf': sf(SUS, s_head), '굽힘 구석 sigma': round(s_bend, 1), 'sf_bend': sf(SUS, s_bend)},
    '한 받침이 100 N 전부(가정 검토)': {'sf': sf(SUS, 2 * s_head)},
    '볼트 1개 돌림(커튼 무게 x3 g, 팔 43)': {'T_Nmm': round(w3g * 43, 0), 'friction_Nmm': round(MU * FV * r_eff, 0), 'sf': round(MU * FV * r_eff / (w3g * 43), 2)},
}

# 앞왼 이음판 P_M08_LC_JOINT_FL_WJ(A5052 t6 160x460): 기둥 볼트 Z -700·-440, 꼭대기 Z 810
M_j = 100.0 * (810.0 + 570.0)
F_b = M_j / 260.0
arm = 80.0 - 2 * R_HEAD
s_j = 6 * F_b * arm / (130.0 * 36.0)
out['P_M08_LC_JOINT_FL_WJ'] = {'M_Nmm': M_j, 'bolt_couple_N': round(F_b, 1), 'strip_arm': arm, 'eff_width': 130.0, 'sigma_MPa': round(s_j, 1), 'sf_mis': sf(A5052, s_j)}

# ---------- 3. HMI 팔 뿌리 · 받침 판 ----------
m_panel, m_plate, m_arm = 2.0, 1.156, 1.716        # 패널 2.0 kg은 설계안 임시(모델 U8_HMI_PANEL 4.28 kg은 기본 재질이라 판정에서 뺌, E-09)
M1g = G * ((m_panel + m_plate) * 590.0 + m_arm * 285.0)
cases = {'운전 3 g': 3 * M1g, '운전 1 g + 누름 30 N': M1g + 30.0 * 632.0, '오조작 1 g + 손 100 N': M1g + 100.0 * 632.0}
hmi = {'M1g_Nmm': round(M1g)}
for k, m in cases.items():
    T = m / 80.0     # 팔 밑 모서리 Z 400이 받침점, 위 홈 Z 480
    need = 2.0 if '오조작' in k else 3.0
    hmi[k] = {'M_Nmm': round(m), '위 브래킷 당김 T_N': round(T, 1), 'T너트 미끄럼 SF(볼트 1 x 600 N)': round(MU * FV / T, 2),
              'H형 t6 세운 다리(구멍 30)': leg(6.0, 6.0, 30.0, 30.0, T), 'H형 t4로 바꾸면': leg(4.0, 4.0, 30.0, 30.0, T), 'need': need}
hmi['패널 4.28 kg(모델 기본 재질 값)이면 3 g T_N'] = round(3 * G * ((4.28 + m_plate) * 590.0 + m_arm * 285.0) / 80.0, 1)
hmi['고친 뒤(T형 L 2개를 팔 옆면 두 홈에 세로로, 구멍 간격 30)'] = {
    'T너트 홈 수직 힘 N(3 g)': round(cases['운전 3 g'] / 2 / 30.0, 1), '오조작': round(cases['오조작 1 g + 손 100 N'] / 2 / 30.0, 1),
    '받침판 쪽 볼트 당김 N(레버 40)': round(cases['운전 3 g'] / 40.0, 1), 'note': '마찰 길 -> 홈 턱 형상 받침. T너트 목·홈 턱 허용 하중은 카탈로그 값 없음(D-54)'}
out['HMI_arm_root(P_M08_LBRK_H1·H2 + HNTT8-5)'] = hmi

pl = {}
for t in (2.0, 3.0, 4.0):
    Zb = 214.0 * t * t / 6
    Zf = 100.0 * t * t / 6     # 플랜지 볼트 2개(Z 간격 40) + 45도 퍼짐
    I = 214.0 * t ** 3 / 12
    row = {}
    for name, F, a in (('누름 30 N 가운데', 30.0, 143.0), ('누름 30 N 먼 끝', 30.0, 279.0), ('손 100 N 가운데', 100.0, 143.0), ('손 100 N 먼 끝', 100.0, 279.0)):
        sb, sfl = F * a / Zb * KT, F * a / Zf
        row[name] = {'굽힘선 sigma': round(sb, 1), 'sf': sf(SUS, sb), '플랜지 볼트 줄 sigma': round(sfl, 1), 'sf_flange': sf(SUS, sfl),
                     '하중점 처짐 mm': round(F * a ** 3 / (3 * E_SUS * I), 2)}
    pl['t%g' % t] = row
out['P_M08_HMI_PLATE_SM'] = pl
out['P_M08_HMI_MOUNT_ML'] = {'note': 'A5052 t10, 보 앞면에 CB5-16 x4(X 간격 40, Z 간격 180). 팔 모멘트 3 g %d N·mm -> 볼트 당김 %.0f N/개(레버 180, 2개). 판은 보 면에 맞닿아 굽힘 없음' % (round(cases['운전 3 g']), cases['운전 3 g'] / 180.0 / 2),
                             'bolt': calc(5, 8.0, cases['오조작 1 g + 손 100 N'] / 180.0 / 2, torque=4.0, bolt='12.9', base='SS400', dw=8.5, dh=5.5, sf_min=2.0)}

# ---------- 4. 날개 판넬 P_RX12C2_PANEL_PX(SUS304 t4 183x1760) ----------
span, weff, t = 260.0, 130.0, 4.0     # 받침 HFS8-4080-166 x7 사이 가장 넓은 칸(피치 300 - 폭 40)
M = 100.0 * span / 4
s0 = M / (weff * t * t / 6)
s1 = s0 * 1.56                         # 볼 구멍 판 응력 계수(mech_M04R와 같은 값)
I = weff * t ** 3 / 12
out['P_RX12C2_PANEL_PX'] = {'M_Nmm': M, 'sigma_MPa': round(s1, 1), 'sf_mis': sf(SUS, s1), 'defl_mm': round(100.0 * span ** 3 / (48 * E_SUS * I), 2),
                           't3이면': {'sigma': round(s1 * 16 / 9, 1), 'sf': sf(SUS, s1 * 16 / 9), 'defl': round(100.0 * span ** 3 / (48 * E_SUS * weff * 27 / 12), 2)}}
# 테이블 판넬 6장: mech_M04R 값(SF 7.0~14.7, 3 g 8.9)을 t3로 환산(응력 x16/9, 처짐 x64/27)
out['P_M04_PANEL_t3_whatif'] = {'원판 구멍 가장자리 손 100 N': {'t4 sf': 7.0, 't3 sf': round(7.0 * 9 / 16, 2), 't4 defl': 0.94, 't3 defl': round(0.94 * 64 / 27, 2)},
                                'E2 칸 손 100 N': {'t4 sf': 9.3, 't3 sf': round(9.3 * 9 / 16, 2), 't4 defl': 1.08, 't3 defl': round(1.08 * 64 / 27, 2)},
                                '자중 3 g': {'t4 sf': 8.9, 't3 sf': round(8.9 * 3 / 4, 2), '1 g 처짐 t4': 0.19, 't3': round(0.19 * 16 / 9, 2)},
                                '질량 kg': {'t4 6장 + 날개': round((64.027 + 28.178 + 64.309 + 28.724 + 20.735 + 49.492 + 9.653), 1)}}

# ---------- 5. 작은 받침·링·롤러(눌림만) ----------
a_i = math.pi / 4 * (13.0 ** 2 - 5.5 ** 2)
out['P_M03_IDLER_WASHER_I·O'] = {'M5 예압 4 kN 면압 MPa': round(FV / a_i, 1), 'sf_vs_pG400': round(400.0 / (FV / a_i), 2), 'sf_vs_Rp205': round(205.0 / (FV / a_i), 2)}
out['P_F01_SPRING_SEAT'] = {'스프링 힘 N(오조작 453 N 전부)': 453.3, 'ring_bending_MPa': round(1.2 * 453.3 / 9.0, 1), 'sf': sf(SUS, 1.2 * 453.3 / 9.0), 'note': '고리 판 t3 Ø44/Ø16.5, 판 계수 1.2(보수)'}
out['P_M06_ROLL_WASHER'] = {'롤 빼는 손 100 N': {'sigma_MPa': round(1.2 * 100.0 / 9.0, 1), 'sf': sf(SUS, 1.2 * 100.0 / 9.0)}}
out['P_M06_G1·TOP_ROLLER'] = {'손 100 N 핀 면압 MPa(핀 Ø8 x 35.8)': round(100.0 / (8.0 * 35.8), 2), 'note': 'PET-CF 층간 약한 방향 30 MPa로 봐도 SF 86. 지름은 테이프 굽힘 반지름이 정함'}

# ---------- 6. 바퀴 접지면(우레탄 A70, Ø120 x 25, 살 10) ----------
E_U = 5.5
tread = {}
for F in (30.0, 100.0):
    p = F / 25.0
    a = math.sqrt(4 * p * 60.0 * 0.75 / (math.pi * E_U))
    tread['누름 %g N' % F] = {'접촉 반폭 mm': round(a, 2), '평균 압력 MPa': round(p / (2 * a), 3), '최대 압력 MPa': round(2 * p / (math.pi * a), 3),
                             '눌림 mm(어림 a^2/2R x 2)': round(a * a / 60.0, 3), '변형률(살 10)': round(a * a / 60.0 / 10.0, 3)}
tread['구동 접선 58.3 N 전단 MPa'] = round(58.3 / (2 * a * 25.0), 3)
tread['note'] = '되풀이 압축 변형률 한도 0.25(RX-12-C1 패드와 같은 지침). 매트 파일 눌림자국은 모델로 판정하지 않음(요구서 7절)'
out['P_M02·M03_WHEEL_TREAD'] = tread

# ---------- 7. U7 끝 처리(RX-15)에서 표에 없던 부품 ----------
A16 = math.pi / 4 * 16.0 ** 2
F_push = round(A16 * 0.5 - 20.0, 1)        # CJ2B16 단동 0.5 MPa - 스프링 20 N
F_feed = round(A16 * 0.5, 1)
rx = {'CJ2B16 밀기 N(0.5 MPa, 스프링 20 뺌)': F_push, 'CDJ2B16 밀기 N': F_feed}
# 접기 팔: 로드 축 (Y 5, Z -30) <-> 접기 판 볼트 (Y -12, Z -18)
ecc = math.hypot(17.0, 12.0)
Zrod = math.pi * 4.019 ** 3 / 32            # M5 나사 골
for name, F, need in (('운전(접는 저항 10 N 임시)', 10.0, 3.0), ('걸림(전 추력)', F_push, 2.0)):
    s = F * ecc / Zrod
    rx['접기 실린더 로드 M5 골 굽힘 — ' + name] = {'M_Nmm': round(F * ecc, 1), 'sigma_MPa': round(s, 1), 'sf(로드 205)': sf(205.0, s), 'sf(로드 450)': sf(450.0, s), 'need': need}
# 접기 판 귀(t0.8, 굽힘선 폭 8): 볼트 머리 가장자리 Z -13.75 <-> 레일 면 Z -9.6
Zear = 8.0 * 0.8 ** 2 / 6
for name, F in (('운전 10 N', 10.0), ('걸림 %g N' % F_push, F_push)):
    rx['접기 판 귀 굽힘 — ' + name] = {'팔 4.15(머리 가장자리)': {'sigma': round(F * 4.15 / Zear, 1), 'sf': sf(CSP_HALF, F * 4.15 / Zear)},
                                  '팔 8.4(볼트 중심, 보수)': {'sigma': round(F * 8.4 / Zear, 1), 'sf': sf(CSP_HALF, F * 8.4 / Zear)}}
rx['접기 판 레일 좌굴(8 x t0.8, 길이 35, 양끝 핀)'] = {'Pcr_N': round(math.pi ** 2 * E_SUS * (8.0 * 0.8 ** 3 / 12) / 35.0 ** 2, 1), 'sf_걸림': round(math.pi ** 2 * E_SUS * (8.0 * 0.8 ** 3 / 12) / 35.0 ** 2 / F_push, 2)}
# 접기 핀 Ø2 x 47, 외팔 39.5(슬라이드 물림 7.5)
Zp, Ip = math.pi * 2.0 ** 3 / 32, math.pi * 2.0 ** 4 / 64
for F in (2.0, 5.0):
    s = F * 24.5 / Zp
    rx['접기 핀 Ø2 — 테이프 당김 %g N(폭 30 가운데, 팔 24.5)' % F] = {'sigma_MPa': round(s, 1), 'sf(SUS304 205)': sf(205.0, s), 'sf(담금질 핀 1,500 어림)': sf(1500.0, s),
                                                         '하중점 처짐 mm': round(F * 24.5 ** 3 / (3 * E_SUS * Ip), 3)}
# 발톱 t0.3 폭 5 길이 10.6, 20도
Lc = 10.6
rx['보내기 발톱(판 스프링 t0.3)'] = {
    'beam_0.2': beam(0.3, 5.0, Lc, 0.0, 0.2, E_SUS, CSP_HALF, 'cantilever', 3.0),
    'beam_0.5': beam(0.3, 5.0, Lc, 0.0, 0.5, E_SUS, CSP_HALF, 'cantilever', 1.2),
    '끄는 힘 2 N(임시)': {'sigma': round(6 * 2.0 * math.sin(math.radians(20)) * Lc / (5.0 * 0.09), 1), 'sf': sf(CSP_HALF, 6 * 2.0 * math.sin(math.radians(20)) * Lc / (5.0 * 0.09))},
    '굽는 힘 N': round(CSP_HALF * 5.0 * 0.09 / (6 * math.sin(math.radians(20)) * Lc), 1)}
# 받침 블록 3개(A5052, 실린더 코 벽 4 mm, 판넬 밑에 매달림 팔 18)
s_blk = F_feed * 18.0 / (52.0 * 16.0 / 6)
rx['받침 블록 벽 t4(CUT·TUCK·FEED_BASE 가운데 가장 얇은 FEED)'] = {'sigma_MPa': round(s_blk, 1), 'sf_run': sf(A5052, s_blk)}
rx['FEED_SLIDE(POM) 너트 좌면'] = {'p_MPa': round(F_feed / (math.pi / 4 * (8.0 ** 2 - 5.0 ** 2)), 1), 'sf(POM 60)': round(60.0 / (F_feed / (math.pi / 4 * (8.0 ** 2 - 5.0 ** 2))), 1)}
out['RX15_tuck_feed'] = rx

# ---------- 8. 접이판 경첩 쪽 막대 P_RX12C1_FLAP_BAR_XP(A5052 15 x 30 x 895) ----------
W3g = 11.4 * G * 3
Fh = W3g / 2 / 2 + 100.0
Mh = Fh * 230.0 / 4
out['P_RX12C1_FLAP_BAR_XP'] = {'경첩 하나 힘 N(3 g 반 + 손 100)': round(Fh, 1), 'sigma_MPa': round(Mh / (15.0 * 900.0 / 6), 1), 'sf_mis': sf(A5052, Mh / (15.0 * 900.0 / 6))}

# ---------- 9. 가스 스프링 귀판 볼트 미끄럼(지금 하중으로 다시) ----------
out['P_RX12C1_GS_LUG_bolt_slip'] = {'F_run_N': 1573.0, 'friction_N(2 x 4 kN x 0.15)': 2 * FV * MU, 'slip_sf': round(2 * FV * MU / 1573.0, 2),
                                    '미끄러진 뒤 볼트 전단 sf': round(0.6 * 1100.0 / (1573.0 / 2 / 14.2), 1), '구멍 틈만큼 움직임 mm': 0.25}

p = 'C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/fea/results/detail_2026-11-28_handcalc.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def show(d, pre=''):
    for k, v in d.items():
        if isinstance(v, dict) and not any(isinstance(x, dict) for x in v.values()):
            print(pre + str(k), '|', json.dumps(v, ensure_ascii=False)[:230])
        elif isinstance(v, dict):
            print(pre + str(k)); show(v, pre + '  ')
        else:
            print(pre + str(k), '=', str(v)[:200])


show({k: v for k, v in out.items() if k not in ('task', 'dept', 'doc', 'fea')})
