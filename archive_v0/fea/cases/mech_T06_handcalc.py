# -*- coding: utf-8 -*-
"""T06 시작·끝 이음매와 절단 — 강도·강성 손계산 (해석부, 2026-10-31, 대상 v0.5.0).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 손계산.
체결은 엔진 handcalc.calc, 얇은 판은 handcalc.beam(E-18)을 import해 쓴다(엔진 파일은 읽기만).
입력 형상: 모델링부 임시 STEP 4개(tools/out/mech_T06/stepout/*.step, 대기 세계 좌표, J_T06_KNIFE 0).
면 위치는 STEP의 VERTEX bbox·PLANE 위치/법선·CYLINDRICAL_SURFACE로 확인한다(옛 케이스 좌표 안 씀).
STEP이 없는 것(STEP대기_CJ2B16-30SZ, 실물 LHFR16·PSFJ16-100 위치)은 mech_T06_model.md 1-1절 측정값.

하중 경로(T06_KNIFE 자유물체): 로드가 팔 X 108을 −Z로 F, 칼(X 24)에 절단 저항 +Z F,
안내축(X 72, LHFR16 부시)이 우력 F·(108 − 24)를 받는다(축–팔 체결은 D-37 (2), 우력 전달을 전제).
브래킷은 실린더 반력 +Z F(X 108) + 부시 우력 → 등가로 X 24 선 위의 +Z F.

단위 mm, N, MPa.  실행: PYTHONIOENCODING=utf-8 python -B fea/cases/mech_T06_handcalc.py
결과: fea/results/mech_T06_handcalc.json, 로그 fea/results/mech_T06_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T06', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T06_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T06_handcalc_log.txt')
g = 9.81
pi = math.pi
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


# ------------------------------------------------------------------ 재료 (E MPa, 항복 MPa, G MPa, 출처)
MAT = {
    'SUS304': (193000.0, 205.0, 77000.0, '엔진 handcalc BASE (항복 205)'),
    'SK85': (206000.0, 390.0, 79000.0, '보수값: 풀림 상태 항복 390(열처리 HRC 58이면 1,500 이상) — 열처리 조건 미확인이라 풀림값'),
    'S50C': (206000.0, 345.0, 79000.0, 'fea/models.json P_T02_PLATE 자리값 345'),
    'Steel': (206000.0, 345.0, 79000.0, 'PSFJ(S45C 상당) 항복 345 자리값'),
}
SF_OP, SF_MIS = 3.0, 2.0          # M-09 기본값(요구서 6-1 비어 있음)
SF_BREAK = 1.2                    # 부서 지시: SF < 1.2 = 영구 변형(동작)

# ------------------------------------------------------------------ 하중 근거
P_SUPPLY = 0.5                    # MPa, 요구서 0-6 공급압(2-4 운전 압력 미정 → 공급압 최대)
BORE = 16.0                       # CJ2B16-30SZ (D-37)
F_PRESS = pi / 4 * BORE ** 2 * P_SUPPLY           # 100.53 N
F_SPRING = 20.0                   # D-36 (1)과 같은 가정(T06 선정)
F_ROD = F_PRESS - F_SPRING        # 80.53 N = 칼이 낼 수 있는 최대 힘
F_CUT = 30.0                      # D-06 임시 절단력(T06 선정)
SIDE = 0.3                        # 칼 옆힘 = 절단력 × 0.3(T06 선정 4절 가정)
F_MAT = 835.0 * 0.5               # 417.5 N: 매트가 진공에서 미끄러지기 전 최대 힘(D-05·D-04, models.json과 같은 근거)
TAPE_DIR = (40.0, -20.5)          # 줄 (−10, 0.5) → (30, −20) (T06 선정 1-1, 바인더 → 매트 쪽)
M_MOVE = (53.6 + 5.4 + 157.7 + 4.6) / 1000.0     # kg 팔 + 칼 + 축 + 로드(모델 질량, mech_T06_model 1-1)
M_FIX = (225.1 + 293.2 + 169.2) / 1000.0          # kg 브래킷 + 실린더 + 부시


# ================================================================== STEP 읽기
def read_step(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    ent = {}
    for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)', txt, re.S):
        ent[int(m.group(1))] = m.group(2).replace('\n', '')

    def pt(i):
        v = re.search(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", ent[i])
        return tuple(float(x) for x in v.group(1).split(','))

    def dirn(i):
        v = re.search(r"DIRECTION\('[^']*',\(([^)]*)\)\)", ent[i])
        return tuple(float(x) for x in v.group(1).split(','))

    def ax(i):
        a = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+),#(\d+)\)", ent[i])
        return pt(int(a.group(1))), dirn(int(a.group(2)))

    verts, planes, cyls = [], [], []
    for i, s in ent.items():
        m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", s)
        if m:
            verts.append(pt(int(m.group(1))))
        m = re.match(r"PLANE\('[^']*',#(\d+)\)", s)
        if m:
            loc, n = ax(int(m.group(1)))
            planes.append(dict(loc=loc, normal=n))
        m = re.match(r"CYLINDRICAL_SURFACE\('[^']*',#(\d+),([-\d.Ee+]+)\)", s)
        if m:
            loc, n = ax(int(m.group(1)))
            cyls.append(dict(r=round(float(m.group(2)), 3), loc=[round(c, 3) for c in loc], dir=[round(c, 3) for c in n]))
    xs, ys, zs = zip(*verts)

    def lv(k):
        return sorted(set(round(p['loc'][k], 2) for p in planes if abs(abs(p['normal'][k]) - 1) < 1e-6))
    return dict(n_vert=len(verts),
                bbox=[[round(min(xs), 3), round(max(xs), 3)], [round(min(ys), 3), round(max(ys), 3)], [round(min(zs), 3), round(max(zs), 3)]],
                x_planes=lv(0), y_planes=lv(1), z_planes=lv(2),
                cyl_r=sorted(set(c['r'] for c in cyls)), cylinders=cyls)


G = {}
for f in sorted(os.listdir(STEPDIR)):
    if f.endswith('.step'):
        G[f[:-5]] = read_step(os.path.join(STEPDIR, f))
checks = []


def chk(part, what, got, want, tol=0.06):
    ok = abs(got - want) <= tol
    checks.append(dict(part=part, what=what, step=got, used=want, ok=ok))
    return want


def has(lst, v, tol=0.06):
    return v if any(abs(x - v) <= tol for x in lst) else -999.0


log('== STEP 확인 ==')
for k, v in G.items():
    log(k, 'bbox', v['bbox'], 'cyl r', v['cyl_r'][:8])
    log('   X', v['x_planes'][:12], 'Y', v['y_planes'][:12], 'Z', v['z_planes'][:12])
KN = G['P_T06_KNIFE']; AR = G['P_T06_ARM']; BR = G['P_T06_BRACKET']; PL = G['P_T02_PLATE']
# 칼
chk('KNIFE', 'X 시작', KN['bbox'][0][0], 23.25); chk('KNIFE', 'X 끝', KN['bbox'][0][1], 24.75)
chk('KNIFE', 'Y 앞', KN['bbox'][1][0], -18.0); chk('KNIFE', 'Y 뒤', KN['bbox'][1][1], 3.0)
chk('KNIFE', 'Z 날 끝(대기)', KN['bbox'][2][0], 27.5); chk('KNIFE', 'Z 위', KN['bbox'][2][1], 52.5)
chk('KNIFE', '볼트 구멍 r', has(KN['cyl_r'], 2.75), 2.75)
# 팔
chk('ARM', 'X 시작', AR['bbox'][0][0], 24.75); chk('ARM', 'X 끝', AR['bbox'][0][1], 120.0)
chk('ARM', 'Y 앞', AR['bbox'][1][0], -18.0); chk('ARM', 'Y 뒤', AR['bbox'][1][1], 3.0)
chk('ARM', 'Z 세로 다리 밑', AR['bbox'][2][0], 36.5); chk('ARM', 'Z 윗면', AR['bbox'][2][1], 57.0)
chk('ARM', '가로 다리 밑면 Z 54', has(AR['z_planes'], 54.0), 54.0)
chk('ARM', '세로 다리 안면 X 27.75', has(AR['x_planes'], 27.75), 27.75)
chk('ARM', '굽힘 안쪽 R3', has(AR['cyl_r'], 3.0), 3.0)
# 브래킷
chk('BRACKET', 'X 시작(헤드 면)', BR['bbox'][0][0], 40.0); chk('BRACKET', 'X 끝', BR['bbox'][0][1], 122.0)
chk('BRACKET', 'Y 앞', BR['bbox'][1][0], -34.0); chk('BRACKET', 'Y 뒤', BR['bbox'][1][1], 19.0)
chk('BRACKET', 'Z 밑', BR['bbox'][2][0], 73.0); chk('BRACKET', 'Z 위', BR['bbox'][2][1], 140.0)
chk('BRACKET', '가로 판 윗면 Z 77', has(BR['z_planes'], 77.0), 77.0)
chk('BRACKET', '세로 다리 안면 X 44', has(BR['x_planes'], 44.0), 44.0)
chk('BRACKET', '축 구멍 r9', has(BR['cyl_r'], 9.0), 9.0); chk('BRACKET', '보스 구멍 r5.25', has(BR['cyl_r'], 5.25), 5.25)
chk('BRACKET', '부시 구멍 r2.25', has(BR['cyl_r'], 2.25), 2.25)
# 침판
chk('PLATE', 'X', PL['bbox'][0][0], -40.0); chk('PLATE', 'X 끝', PL['bbox'][0][1], 40.0)
chk('PLATE', '판 밑 Z −4.05', has(PL['z_planes'], -4.05), -4.05); chk('PLATE', '판 위 Z −1.05', has(PL['z_planes'], -1.05), -1.05)
chk('PLATE', '홈 −X 벽 X 23.15', has(PL['x_planes'], 23.15), 23.15); chk('PLATE', '홈 +X 벽 X 25.15', has(PL['x_planes'], 25.15), 25.15)
chk('PLATE', '홈 −Y 끝 Y −18.5', has(PL['y_planes'], -18.5), -18.5); chk('PLATE', '홈 +Y 끝 Y 3.5', has(PL['y_planes'], 3.5), 3.5)
bad = [c for c in checks if not c['ok']]
log('STEP 대조', len(checks), '건, 어긋남', len(bad), bad if bad else '')

res = {'checks': checks, 'step': {k: {kk: v[kk] for kk in ('bbox', 'x_planes', 'y_planes', 'z_planes', 'cyl_r')} for k, v in G.items()},
       'cases': [], 'bolts': {}, 'stiffness': {}, 'over': []}


def rec(name, part, mat, desc, stress, need, kind='bend', extra=None):
    sy = MAT[mat][1]
    sf = sy / stress if stress > 0 else float('inf')
    verdict = '됨' if sf >= need else ('디테일' if sf >= SF_BREAK else '동작')
    d = dict(name=name, part=part, mat=mat, desc=desc, stress_MPa=round(stress, 2), allow_MPa=sy, sf=round(sf, 2), need=need,
             verdict=verdict, near=bool(need <= sf < 1.1 * need))
    if extra:
        d.update(extra)
    res['cases'].append(d)
    log(f'  [{verdict}] {name}: σeq {stress:.1f} MPa, SF {sf:.2f} (기준 {need}) — {desc}')
    return sf


# ================================================================== 기하(STEP에서)
t_arm = AR['bbox'][2][1] - 54.0                    # 3
b_arm = AR['bbox'][1][1] - AR['bbox'][1][0]        # 21
x_knife = (KN['bbox'][0][0] + KN['bbox'][0][1]) / 2  # 24.0
X_SHAFT, X_ROD = 72.0, 108.0                       # 축·로드 (mech_T06_model 1-1, 브래킷 구멍 중심)
t_kn = KN['bbox'][0][1] - KN['bbox'][0][0]          # 1.5
b_kn = KN['bbox'][1][1] - KN['bbox'][1][0]          # 21
t_br = 4.0
b_br = BR['bbox'][1][1] - BR['bbox'][1][0]          # 53
Z_KB = 42.0                                         # 칼 볼트 줄(대기)
Z_BEND_IN = 54.0                                    # 팔 가로 다리 밑면(대기)
Z_ARM_MID = (54.0 + AR['bbox'][2][1]) / 2           # 55.5
STROKE = 30.0
Z_TAPE = -0.5                                       # 절단 자세 테이프 하중 높이(침판 윗면 −1.05 위 테이프 t1 가운데)
Z_KB_CUT = Z_KB - STROKE                            # 12
L_KN = Z_KB_CUT - Z_TAPE                            # 칼 외팔(볼트 줄 → 테이프) 12.5
L_VL = Z_BEND_IN - Z_KB                             # 세로 다리 굽힘 안쪽 → 볼트 12
H_ARM = (Z_ARM_MID - STROKE) - Z_TAPE               # 가로 다리 중립면 → 테이프 26
L_HL = X_SHAFT - (AR['bbox'][0][0] + t_arm / 2)     # 가로 다리 비틀림·굽힘 길이(축 → 세로 다리 중심) 45.75
GAP_XP = 25.15 - KN['bbox'][0][1]                   # +X 벽 틈 0.4
GAP_XM = KN['bbox'][0][0] - 23.15                   # −X 벽 틈 0.1 (맞날)
GAP_YM = KN['bbox'][1][0] - (-18.5)                 # −Y 끝 틈 0.5
z_tip_lo, z_tip_hi = KN['bbox'][2][0] - STROKE, 29.7 - STROKE   # 날 끝 −2.5(Y −18) ~ −0.3(Y +3)
y_in_groove = -18.0 + (-1.05 - z_tip_lo) / (z_tip_hi - z_tip_lo) * 21.0   # 날이 침판 윗면 밑으로 든 끝 Y
log(f'\n기하: 팔 t{t_arm} × {b_arm}, 칼 t{t_kn} × {b_kn}, 칼 X {x_knife}, 칼 외팔 {L_KN}, 세로 다리 {L_VL}, 가로 다리 높이차 {H_ARM}, 길이 {L_HL}')
log(f'  절단 자세 날 끝 Z {z_tip_lo:.2f}~{z_tip_hi:.2f}, 침판 홈 안(Z < −1.05)에 든 날 Y −18 ~ {y_in_groove:.2f}; 틈 +X {GAP_XP:.2f}, −X {GAP_XM:.2f}, −Y {GAP_YM:.2f}')
res['geom'] = dict(t_arm=t_arm, b_arm=b_arm, x_knife=x_knife, L_knife=L_KN, L_vleg=L_VL, H_arm=H_ARM, L_hleg=L_HL,
                   gap_xp=round(GAP_XP, 3), gap_xm=round(GAP_XM, 3), gap_ym=round(GAP_YM, 3), y_in_groove=round(y_in_groove, 2))

log('\n== 하중 ==')
W_MOVE = M_MOVE * g * 3
log(f'실린더 {F_PRESS:.2f} N − 스프링 {F_SPRING} = {F_ROD:.2f} N; 절단 {F_CUT} N (비 {F_ROD / F_CUT:.2f}); 매트 미끄럼 {F_MAT} N; 움직이는 묶음 자중 ×3 g {W_MOVE:.2f} N')

# ================================================================== A. P_T06_ARM (SUS304 t3)
E_S, SY_S, G_S, _ = MAT['SUS304']
log('\n== A. P_T06_ARM 가로 다리(축 X 72에서 칼까지 외팔, 단면 t3 × 21) ==')
I_h = b_arm * t_arm ** 3 / 12; Z_h = b_arm * t_arm ** 2 / 6
lev_k = X_SHAFT - x_knife                            # 48
F_op = F_CUT + W_MOVE                                # 절단 30 + 자중 3 g(같은 방향 보수)
rec('ARM_op_cut', 'P_T06_ARM', 'SUS304', f'운전: 절단 저항 {F_CUT} N + 자중 3 g, 외팔 {lev_k}', F_op * lev_k / Z_h, SF_OP)
sf_arm_jam = rec('ARM_mis_jam', 'P_T06_ARM', 'SUS304', f'오조작: 칼이 막힘 → 실린더 최대 {F_ROD:.1f} N, 외팔 {lev_k}', F_ROD * lev_k / Z_h, SF_MIS)
t_need = t_arm * math.sqrt(SF_MIS / sf_arm_jam)
log(f'  칼 막힘 SF 2에 필요한 두께 {t_need:.2f} → t4면 SF {sf_arm_jam * (4 / t_arm) ** 2:.2f}')
bm = handcalc.beam(t_arm, b_arm, lev_k, load=F_ROD, e=E_S, sy=SY_S, sf_min=SF_MIS)
log('  handcalc.beam(칼 막힘):', json.dumps(bm, ensure_ascii=False))
res['arm_beam_jam'] = bm
res['arm_t_need_jam'] = round(t_need, 2)

# 세로 다리: 절단 옆힘(X)과 테이프 끌림
# ================================================================== B. 칼 옆 강성 — 맞날 틈 0.1 유지 (정밀 체인)
log('\n== B. 칼 끝 X 방향 강성(절단 자세, 하중 Z −0.5) ==')
E_K = MAT['SK85'][0]
I_kn = b_kn * t_kn ** 3 / 12
I_vl = b_arm * t_arm ** 3 / 12
c_knife = L_KN ** 3 / (3 * E_K * I_kn)
# 세로 다리(굽힘 안쪽 → 볼트 줄 L_VL), 끝에 힘 F와 모멘트 F·L_KN
c_vl = (L_VL ** 3 / (3 * E_S * I_vl) + L_KN * L_VL ** 2 / (2 * E_S * I_vl)) + (L_VL ** 2 / (2 * E_S * I_vl) + L_KN * L_VL / (E_S * I_vl)) * L_KN
# 가로 다리: 모멘트 F·H_ARM이 L_HL 위에 → 회전 θ = F·H·L/(EI), 칼 끝 이동 θ·H
c_hl = H_ARM ** 2 * L_HL / (E_S * I_h)
c_x = c_knife + c_vl + c_hl
k_x = 1 / c_x
for nm, F in (('운전 옆힘 0.3×30', SIDE * F_CUT), ('칼 막힘 옆힘 0.3×80.5', SIDE * F_ROD)):
    log(f'  {nm}: {F:.1f} N → 칼 끝 X {F * c_x:.4f} mm (칼 {F * c_knife:.4f} · 세로 다리 {F * c_vl:.4f} · 가로 다리 {F * c_hl:.4f}), 맞날 틈 {GAP_XM:.2f} → {GAP_XM + F * c_x:.3f}')
res['stiffness']['knife_x'] = dict(k_N_mm=round(k_x, 1), c_knife=c_knife, c_vleg=c_vl, c_hleg=c_hl,
                                   op_side_N=SIDE * F_CUT, op_dx_mm=round(SIDE * F_CUT * c_x, 4),
                                   jam_side_N=round(SIDE * F_ROD, 2), jam_dx_mm=round(SIDE * F_ROD * c_x, 4),
                                   gap_shear=round(GAP_XM, 3), gap_op=round(GAP_XM + SIDE * F_CUT * c_x, 3))
# 세로 하중(절단 저항 +Z)이 가로 다리 끝을 기울여 칼 끝을 −X(맞날 벽 쪽)로 민다: θ = F·L²/(2EI), 이동 θ·H
def tilt_dx(F, t=t_arm):
    I = b_arm * t ** 3 / 12
    return F * lev_k ** 2 / (2 * E_S * I) * H_ARM
for nm, F, Fs in (('운전', F_CUT, SIDE * F_CUT), ('칼 막힘', F_ROD, SIDE * F_ROD)):
    dm = tilt_dx(F); dp = Fs * c_x
    log(f'  {nm} 세로 {F:.1f} N → 칼 끝 −X {dm:.4f} mm, 옆힘 +X {dp:.4f} → 순 −X {dm - dp:.4f}; 맞날 틈 {GAP_XM:.2f} → {GAP_XM - (dm - dp):.3f} (브래킷 기울기 ±{0:.0f} 별도)')
    res['stiffness'][f'shear_gap_{nm}'] = dict(tilt_minus_x=round(dm, 4), side_plus_x=round(dp, 4), gap_after=round(GAP_XM - (dm - dp), 4))
# 칼 자체 응력(옆힘, 볼트 줄 → 테이프)
Z_kn = b_kn * t_kn ** 2 / 6
rec('KNIFE_op_side', 'P_T06_KNIFE', 'SK85', f'운전: 옆힘 {SIDE * F_CUT:.0f} N, 외팔 {L_KN}', SIDE * F_CUT * L_KN / Z_kn, SF_OP)
rec('KNIFE_mis_side', 'P_T06_KNIFE', 'SK85', f'오조작: 칼 막힘 옆힘 {SIDE * F_ROD:.1f} N, 외팔 {L_KN}', SIDE * F_ROD * L_KN / Z_kn, SF_MIS)
# 칼 세로(면내) 압축·볼트 구멍 지압: 80.5 N을 Ø5.5 구멍 2개 t1.5
rec('KNIFE_mis_bearing', 'P_T06_KNIFE', 'SK85', f'오조작: {F_ROD:.1f} N 볼트 구멍 지압 2 × Ø5 × t1.5', F_ROD / (2 * 5.0 * t_kn), SF_MIS)

# ================================================================== C. 오조작 T: 칼이 내려간 채(스프링 20 N이 못 올림) 매트가 움직여 테이프가 칼을 끎
log('\n== C. 오조작 T: 칼이 내려간 채 매트가 움직임 → 테이프가 칼을 끎 (최대 417.5 N, 줄 방향) ==')
u = (TAPE_DIR[0] / math.hypot(*TAPE_DIR), TAPE_DIR[1] / math.hypot(*TAPE_DIR))
Fx, Fy = F_MAT * u[0], F_MAT * u[1]
log(f'  줄 방향 (bin→mat) {u[0]:.3f}, {u[1]:.3f} → Fx {Fx:.1f} N(+X 벽 틈 {GAP_XP:.2f}), Fy {Fy:.1f} N(−Y 끝 틈 {GAP_YM:.2f})')
# Y 강성: 가로 다리 비틀림(축 X 72 ← 세로 다리), 높이 H_ARM. 칼·세로 다리 면내 굽힘은 무시할 만큼 강함(계산해 더함)
beta = (1 / 3) * (1 - 0.630 * t_arm / b_arm)
J = beta * b_arm * t_arm ** 3
c_tw = H_ARM ** 2 * L_HL / (G_S * J)
I_kn_in = t_kn * b_kn ** 3 / 12; I_vl_in = t_arm * b_arm ** 3 / 12
c_inplane = L_KN ** 3 / (3 * E_K * I_kn_in) + (L_KN + L_VL) ** 3 / (3 * E_S * I_vl_in)
c_y = c_tw + c_inplane
k_y = 1 / c_y
Fy_arm = min(abs(Fy), k_y * GAP_YM)
Fx_arm = min(abs(Fx), k_x * GAP_XP)
log(f'  Y 강성 {k_y:.1f} N/mm(비틀림 J {J:.1f}) → 틈 {GAP_YM} 닫는 힘 {k_y * GAP_YM:.1f} N; 팔이 받는 Fy {Fy_arm:.1f} N, 나머지 {abs(Fy) - Fy_arm:.1f} N은 침판 홈 −Y 끝')
log(f'  X 강성 {k_x:.1f} N/mm → 틈 {GAP_XP:.2f} 닫는 힘 {k_x * GAP_XP:.1f} N; 팔이 받는 Fx {Fx_arm:.1f} N, 나머지 {abs(Fx) - Fx_arm:.1f} N은 침판 홈 +X 벽')
T_tw = Fy_arm * H_ARM
tau = T_tw / (beta * b_arm * t_arm ** 2)
M_hl = Fx_arm * H_ARM
s_hl = M_hl / Z_h
s_eq = math.sqrt(s_hl ** 2 + 3 * tau ** 2)
sf_T = rec('ARM_mis_tape_pull', 'P_T06_ARM', 'SUS304',
           f'오조작 T: 줄 방향 417.5 N 중 팔 몫 Fy {Fy_arm:.0f}·Fx {Fx_arm:.0f} N, 가로 다리 비틀림 τ {tau:.1f} + 굽힘 {s_hl:.1f}', s_eq, SF_MIS,
           extra=dict(tau=round(tau, 2), sigma_b=round(s_hl, 2), Fy_arm=round(Fy_arm, 1), Fx_arm=round(Fx_arm, 1)))
# what-if(실형상 경계조건, 팔 두께만 바꿈): t4
def tape_pull(t):
    I = b_arm * t ** 3 / 12; Zh = b_arm * t ** 2 / 6
    bt = (1 / 3) * (1 - 0.630 * t / b_arm); Jt = bt * b_arm * t ** 3
    Ivl = b_arm * t ** 3 / 12
    cvl = (L_VL ** 3 / (3 * E_S * Ivl) + L_KN * L_VL ** 2 / (2 * E_S * Ivl)) + (L_VL ** 2 / (2 * E_S * Ivl) + L_KN * L_VL / (E_S * Ivl)) * L_KN
    cx = c_knife + cvl + H_ARM ** 2 * L_HL / (E_S * I)
    cy = H_ARM ** 2 * L_HL / (G_S * Jt) + c_inplane
    fy = min(abs(Fy), GAP_YM / cy); fx = min(abs(Fx), GAP_XP / cx)
    ta = fy * H_ARM / (bt * b_arm * t ** 2); sb = fx * H_ARM / Zh
    se = math.sqrt(sb ** 2 + 3 * ta ** 2)
    return dict(t=t, Fx_arm=round(fx, 1), Fy_arm=round(fy, 1), tau=round(ta, 1), sigma_b=round(sb, 1), sf=round(SY_S / se, 2),
                jam_sf=round(SY_S / (F_ROD * lev_k / Zh), 2), shear_gap_op=round(GAP_XM - (tilt_dx(F_CUT, t) - SIDE * F_CUT * cx), 4))
res['whatif_arm_t'] = [tape_pull(t) for t in (3.0, 4.0, 5.0)]
for w in res['whatif_arm_t']:
    log('  what-if 팔', w)
# 같은 하중을 +Y로(줄 방향이 아님) 준 경우: 날이 홈에 든 구간(Y −18 ~ y_in_groove)은 +Y로 7 이상 가야 홈 +Y 끝에 닿는다 → 참고
tau_py = F_MAT * H_ARM / (beta * b_arm * t_arm ** 2)
res['ref_plusY_417'] = dict(tau=round(tau_py, 1), sf=round(SY_S / (math.sqrt(3) * tau_py), 2),
                            note='+Y 417.5 N은 하중 출처가 없다: 바인더 쪽 테이프는 T05 장력(운전 31.9 N)이고, 롤 걸림이면 양쪽 장력이 같아 칼 위 수평 합력이 상쇄된다. 참고값')
log(f'  참고(+Y 417.5 N, 출처 없음): τ {tau_py:.1f} → SF {SY_S / (math.sqrt(3) * tau_py):.2f}')
# 칼 Y 끝 지압·X 벽 지압(침판 S50C, 날이 홈 안에 든 부분)
depth = -1.05 - z_tip_lo                               # 1.45
len_in = y_in_groove - (-18.0)
A_x = 0.5 * len_in * depth                             # 삼각 지압 면적
A_y = t_kn * depth
rec('PLATE_mis_wall_x', 'P_T02_PLATE', 'S50C', f'오조작 T: 홈 +X 벽 지압 {abs(Fx) - Fx_arm:.0f} N / 삼각 {A_x:.1f} mm²', (abs(Fx) - Fx_arm) / A_x, SF_MIS)
rec('PLATE_mis_end_y', 'P_T02_PLATE', 'S50C', f'오조작 T: 홈 −Y 끝 지압 {abs(Fy) - Fy_arm:.0f} N / {A_y:.2f} mm² (칼 쪽도 같은 면적)', max(abs(Fy) - Fy_arm, 0) / A_y, SF_MIS)
rec('KNIFE_mis_tape_pull', 'P_T06_KNIFE', 'SK85', f'오조작 T: 칼 옆 굽힘 팔 몫 Fx {Fx_arm:.0f} N, 외팔 {L_KN}(벽 닿은 뒤는 홈 벽이 받침)', Fx_arm * L_KN / Z_kn, SF_MIS)

# ================================================================== D. P_T06_BRACKET (SUS304 t4 ㄴ)
log('\n== D. P_T06_BRACKET (가로 판 X 40~122, 세로 다리 X 40~44, 볼트 Z 130) ==')
# 가로 판 모멘트: M(x) = F(108 − x) (x > 72), F(24 − x) (x < 72) → 최대 |M| = 48F (X 72 −쪽, 축 구멍 Ø18 단면), 굽힘선 X 44에서 20F
W_FIX = M_FIX * g * 3
for nm, F, need in (('운전', F_CUT, SF_OP), ('오조작_칼막힘', F_ROD, SF_MIS)):
    M72 = F * (X_SHAFT - x_knife); M44 = F * (44.0 - x_knife)
    Z72 = (b_br - 18.0) * t_br ** 2 / 6
    Z44 = b_br * t_br ** 2 / 6
    s72 = M72 / Z72 + (W_FIX * (X_SHAFT - 44.0) / Z44 if nm == '운전' else 0)
    rec(f'BRACKET_{nm}_x72', 'P_T06_BRACKET', 'SUS304', f'{nm}: {F:.1f} N, X 72 −쪽 M {M72:.0f} N·mm, 순폭 {b_br - 18:.0f}(축 구멍 Ø18) — 부시 플랜지 Ø48이 덮는 자리라 보수', s72, need)
    # 보수 비교: 선정 4절 모델(부시 우력 무시, 실린더 반력 X 108 → 굽힘 X 44, 64F)
    rec(f'BRACKET_{nm}_sel_model', 'P_T06_BRACKET', 'SUS304', f'{nm}: 선정 모델(우력 무시) M = {F:.1f} × 64, 전폭 53', F * 64.0 / Z44, need)
# 과사양 판정(M-09): 우력 반영 X 72 단면 오조작 SF / 2
sf_b = [c for c in res['cases'] if c['name'] == 'BRACKET_오조작_칼막힘_x72'][0]['sf']
if sf_b >= 3 * SF_MIS:
    t_min = t_br * math.sqrt(3 * SF_MIS / sf_b) if False else t_br * math.sqrt(SF_MIS * 1.0 / sf_b)
    res['over'].append(dict(part='P_T06_BRACKET', sf=sf_b, need=SF_MIS,
                            note=f'과사양(오조작 SF {sf_b}, 필요 2의 3배 이상). 강도만 보면 t{t_min:.1f}면 SF 2. 다만 칼 맞날 틈 0.1을 지키는 강성(부시 기울기)과 판금 t3 이하에서 부시 플랜지 볼트 자리·굽힘 R 규칙(M-04 2t)이 함께 바뀌어 지금은 줄이지 않는다(디테일링 몫, 가격 미확인)'))
# 브래킷 강성 → 칼 끝 Z·X 이동(부시 기울기)
I_br = b_br * t_br ** 3 / 12
th72 = (F_ROD * (X_SHAFT - x_knife) * 0 + F_ROD * (44.0 - x_knife)) * (X_SHAFT - 44.0) / (E_S * I_br)
res['stiffness']['bracket_tilt_jam_rad'] = th72
# 굽힘선 X 44 → X 72: M(x) = F(24 − x)는 X 44~72에서 −20F~−48F, 평균 34F
th72 = F_ROD * 34.0 * (X_SHAFT - 44.0) / (E_S * I_br)
dx_tip = th72 * (77.0 - Z_TAPE)  # 부시 기울기가 칼 끝 X로(부시 판 Z 77 → 테이프)
log(f'  칼 막힘 80.5 N에서 부시 자리 기울기 {th72 * 1000:.3f} mrad → 칼 끝 X {dx_tip:.4f} mm (운전 30 N이면 {dx_tip * F_CUT / F_ROD:.4f})')
res['stiffness']['bracket_tilt_jam_rad'] = th72
res['stiffness']['bracket_tip_dx_jam'] = round(dx_tip, 4)
res['stiffness']['bracket_tip_dx_op'] = round(dx_tip * F_CUT / F_ROD, 4)

# ================================================================== E. 안내축 PSFJ16-100 · LHFR16 우력
log('\n== E. 안내축 PSFJ16-100 · 부시 LHFR16 ==')
M_c = F_ROD * (X_ROD - x_knife)
s_sh = 32 * M_c / (pi * 16.0 ** 3)
rec('SHAFT_mis_jam', 'PSFJ16-100_T06', 'Steel', f'오조작: 우력 {M_c:.0f} N·mm, Ø16', s_sh, SF_MIS)
# 부시 반력(길이 37 양 끝 집중 가정)
R_b = M_c / 37.0
log(f'  부시 반경 하중(우력 / 길이 37) 칼 막힘 {R_b:.0f} N, 운전 {F_CUT * (X_ROD - x_knife) / 37:.0f} N — LHFR16 허용 하중 미확인(D-37 (6))')
res['bush_radial'] = dict(jam_N=round(R_b, 1), op_N=round(F_CUT * (X_ROD - x_knife) / 37, 1), allow='미확인 D-37 (6)')
# 오조작 T의 X 몫이 축에 주는 굽힘(축 자유 길이: 절단 자세 팔 윗면 Z 27 → 부시 밑 Z 77 = 50)
M_T = Fx_arm * (H_ARM + 0) + Fx_arm * 0
res['shaft_free_cut'] = 50.0

# ================================================================== F. 체결(이번에 새로 낸 구멍, 볼트는 디테일링에서 그림)
log('\n== F. 체결 손계산(handcalc.calc) ==')
# 브래킷 → 헤드 +X 면 M5 ×2: 등가 하중 +Z F at X 24 → 헤드 면(X 40) 기준 모멘트 16F, 아래 모서리 Z 73 지렛점, 볼트 Z 130
for nm, F, need in (('운전', F_CUT + W_FIX, SF_OP), ('오조작', F_ROD, SF_MIS)):
    t_each = F * (40.0 - x_knife) / (130.0 - 73.0) / 2
    t_sel = F * 68.0 / 57.0 / 2      # 선정 모델(보수)
    tb = max(t_each, t_sel)
    hc = handcalc.calc(5, 8.0, tb, torque=6.0, bolt='12.9', base='SS400', sf_min=need)
    res['bolts'][f'bracket_M5_{nm}'] = dict(tension_each_N=round(tb, 1), model_tension=round(t_each, 1), shear_each_N=round(F / 2, 1), hc=hc)
    log(f'  브래킷 CB5-12 ×2 {nm}: 인장 {tb:.1f} N/개(우력 모델 {t_each:.1f}), 전단 {F / 2:.1f} → worst {hc["worst"]} ok {hc["ok"]} 근처 {hc["near_limit"]}')
# LHFR16 → 브래킷 M4 ×4 + 너트: 우력 M_c, 플랜지 가장자리(r 24) 지렛점, 볼트 PCD 38 45°
r_out = 24.0; off = 13.435
d1, d2 = r_out + off, r_out - off
tmax = M_c * d1 / (2 * (d1 ** 2 + d2 ** 2))
hc4 = handcalc.calc(4, 6.0, tmax, torque=2.5, bolt='12.9', base='SUS304', dw=7.0, dh=4.5, sf_min=SF_MIS)
res['bolts']['bushing_M4'] = dict(tension_each_N=round(tmax, 1), hc=hc4, note='너트 체결(LBNR4 표준 너트, 물림은 너트 높이 — le 6은 너트를 표준 강도로 본 자리값). 좌면은 자리파기 Ø7.5 안 Ø7')
log(f'  LHFR16 CB4-16 ×4 칼 막힘: 인장 {tmax:.1f} N/개 → worst {hc4["worst"]} ok {hc4["ok"]}')
# 칼 → 팔 M5 ×2 + 너트: 전단 F/2(마찰로 받음), 옆힘 모멘트
fs = F_ROD / 2
mu = 0.15
fv = 6.0 * 1000 / (0.2 * 5)
res['bolts']['knife_M5'] = dict(shear_each_N=round(fs, 1), preload_N=fv, slip_sf=round(mu * fv / fs, 1),
                                shank_tau=round(fs / (pi / 4 * 5 ** 2), 2))
log(f'  칼 CB5-12 ×2 + 너트: 전단 {fs:.1f} N/개, 예압 {fv:.0f} N × μ{mu} → 미끄럼 SF {mu * fv / fs:.1f}')

# ================================================================== G. 침판 P_T02_PLATE (홈 추가 후 옛 케이스 단면 확인)
log('\n== G. P_T02_PLATE 홈(X 23.15~25.15 · Y −18.5~3.5) 뒤 ==')
t_pl = 3.0
lig = (PL['bbox'][1][1] - 3.5) + (-18.5 - PL['bbox'][1][0])   # 홈 단면 남은 폭 21.5 + 6.5
rec('PLATE_mis_X_lig', 'P_T02_PLATE', 'S50C', f'옛 오조작 417.5 N +X 지압 경로가 홈 단면을 지남: 남은 폭 {lig:.1f} × t3 압축', F_MAT / (lig * t_pl), SF_MIS)
# 칼 절단력이 홈 가장자리를 누름 → 판은 베드에 앉음(models.json) → 지압. 가장자리 띠 접촉 0.5 폭 가정
rec('PLATE_op_cut_edge', 'P_T02_PLATE', 'S50C', f'운전: 절단 {F_CUT} N이 홈 두 가장자리(길이 22 × 접촉 0.5 × 2)를 누름, 판은 베드에 앉음', F_CUT / (22 * 0.5 * 2), SF_OP)
# 홈 −Y 쪽 띠(Y −25~−18.5, 폭 6.5, X 방향 2.0 홈 위 다리) — 베드 지지라 굽힘 없음, 참고: 베드 없다고 보면 양단 고정 보 L 2.0
log('  홈 −Y 쪽 띠 폭 6.5는 베드가 받침(models.json 경계) — 굽힘 없음')

# ================================================================== 요약
over = []
for c in res['cases']:
    if c['sf'] >= 3 * c['need'] and c['part'] in ('P_T06_ARM', 'P_T06_KNIFE', 'P_T06_BRACKET'):
        over.append(c['name'])
res['over_cases'] = over
probs = [c for c in res['cases'] if c['verdict'] != '됨']
res['summary'] = dict(n_cases=len(res['cases']), motion=[c['name'] for c in probs if c['verdict'] == '동작'],
                      detail=[c['name'] for c in probs if c['verdict'] == '디테일'],
                      near=[c['name'] for c in res['cases'] if c['near']], step_mismatch=len(bad))
log('\n== 요약 ==', json.dumps(res['summary'], ensure_ascii=False))
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
