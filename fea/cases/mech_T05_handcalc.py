# -*- coding: utf-8 -*-
"""T05 테이프 공급·장력 유닛 — 강도 손계산 (해석부, 2026-10-31, 대상 v0.4.0).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 손계산.
체결은 엔진 handcalc.calc, 얇은 판은 handcalc.beam(E-18)을 import해 쓴다(엔진 파일은 읽기만).
입력 형상: 모델링부 임시 STEP 6개(tools/out/mech_T05/stepout/P_T05_*.step, 세계 좌표, 패드 저장값 -12.5).
면 위치는 STEP의 VERTEX bbox·PLANE 위치/법선·CYLINDRICAL_SURFACE로 확인한다(옛 케이스 좌표 안 씀).
STEP이 없는 것(STEP대기_PSFJ16-100, STEP대기_CJ2B10-15, 테이프)은 mech_T05_model.md 2-1절 값.

단위 mm, N, MPa.  실행: PYTHONIOENCODING=utf-8 python -B fea/cases/mech_T05_handcalc.py
결과: fea/results/mech_T05_handcalc.json, 로그 fea/results/mech_T05_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T05', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T05_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T05_handcalc_log.txt')
g = 9.81
pi = math.pi
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


# ------------------------------------------------------------------ 재료 (E MPa, 허용 MPa, 출처)
MAT = {
    'SUS304': (193000.0, 205.0, '엔진 fea.py MAT / handcalc BASE (항복 205)'),
    'PET-CF': (6000.0, 30.0, '선정(mech_T05_select.md 4절)과 같은 보수값: 층간 30 MPa(handcalc BASE Rp 60은 체결 계산에만)'),
    'Steel': (206000.0, 345.0, 'PSFJ(S45C 상당) 항복 345 자리값'),
}
SF_OP, SF_MIS = 3.0, 2.0          # M-09 기본값(요구서 6-1 비어 있음)
SF_BREAK = 1.2                    # 부서 지시: SF < 1.2 = 영구 변형(동작)

# ------------------------------------------------------------------ 하중 근거
P_SUPPLY = 0.5                    # MPa, 요구서 0-6 공급압 0.5 MPa(운전 압력 미정 2-4 → 공급압 최대)
BORE, ROD = 10.0, 4.0             # CJ2B10 (D-33 임시)
F_PUSH = pi / 4 * BORE ** 2 * P_SUPPLY            # 39.27 N
F_PULL = pi / 4 * (BORE ** 2 - ROD ** 2) * P_SUPPLY
MU_MAX = 0.4                      # D-06 임시 0.2~0.4
T_OP = 2 * MU_MAX * F_PUSH + 0.44                 # 바인더 쪽 장력 최대(패드 2μF + 롤 쪽)
T_MIS = 417.5                     # 오조작: 테이프가 걸려 매트가 미끄러지기 전 최대 힘(fea/models.json P_T02_BINDER와 같은 근거, D-05·D-04)
M_ROLL = 0.48                     # kg, D-06 임시(가득 롤)

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


log('== STEP 확인 ==')
for k, v in G.items():
    log(k, 'bbox', v['bbox'], 'cyl r', v['cyl_r'][:8])
PL = G['P_T05_PLATE']; GD = G['P_T05_GUIDE']; PD = G['P_T05_PAD']; HD = G['P_T05_HOLDER']
chk('PLATE', 'X 두께 시작', PL['bbox'][0][0], -78.0); chk('PLATE', 'X 끝(기둥 면)', PL['bbox'][0][1], -75.0)
chk('PLATE', 'Y 혀 끝', PL['bbox'][1][0], 560.0); chk('PLATE', 'Z 밑', PL['bbox'][2][0], 30.0)
chk('PLATE', '혀 윗변 Z 100 평면 있음', 100.0 if 100.0 in PL['z_planes'] else -1, 100.0)
chk('PLATE', '혀 뿌리 Y 620 평면 있음', 620.0 if 620.0 in PL['y_planes'] else -1, 620.0)
chk('GUIDE', '+X 면(평판 맞댐)', GD['bbox'][0][1], -78.0); chk('GUIDE', 'Y 뒤 끝', GD['bbox'][1][1], 612.0)
chk('GUIDE', 'Y 앞 끝', GD['bbox'][1][0], 553.0); chk('GUIDE', 'Z 밑', GD['bbox'][2][0], 36.0)
# 막대 r8은 기운 축이라 유리 B-스플라인 면 2장으로 나온다(CYLINDRICAL_SURFACE 아님) → 제어점 bbox로 확인
_gt = open(os.path.join(STEPDIR, 'P_T05_GUIDE.step'), encoding='utf-8').read()
_bs = re.findall(r"#(\d+)=\(BOUNDED_SURFACE\(\)B_SPLINE_SURFACE\(2,1,\(\((.*?)\)\),", _gt)
_ids = [int(x) for _, body in _bs for x in re.findall(r'#(\d+)', body)]
_cp = {int(a): tuple(float(v) for v in b.split(',')) for a, b in re.findall(r"#(\d+)=CARTESIAN_POINT\('',\(([^)]*)\)\)", _gt)}
_pp = [_cp[i] for i in _ids if i in _cp]
BAR_CP = [[round(min(q[k] for q in _pp), 2), round(max(q[k] for q in _pp), 2)] for k in range(3)]
log('막대 B-스플라인 면', len(_bs), '장, 제어점 bbox', BAR_CP)
chk('GUIDE', '막대 B-스플라인 면 2장', float(len(_bs)), 2.0)
chk('GUIDE', '막대 X 길이(제어점, 축 길이 37 × 0.981 + r 투영)', round(BAR_CP[0][1] - BAR_CP[0][0], 1), 39.1, tol=1.0)
chk('GUIDE', '막대 Z 중심 51', round((BAR_CP[2][0] + BAR_CP[2][1]) / 2, 1), 51.0, tol=1.5)
chk('PAD', 'Z 밑(저장값 -12.5)', PD['bbox'][2][0], 43.0)
chk('HOLDER', '플랜지 +X 면', HD['bbox'][0][1], -78.0)
bad = [c for c in checks if not c['ok']]
log('STEP 대조', len(checks), '건, 어긋남', len(bad), bad if bad else '')

res = {'checks': checks, 'step': {k: {kk: v[kk] for kk in ('bbox', 'x_planes', 'y_planes', 'z_planes', 'cyl_r')} for k, v in G.items()}}

# ================================================================== 하중
log('\n== 하중 ==')
log(f'실린더 밀기 {F_PUSH:.2f} N, 당기기 {F_PULL:.2f} N @ {P_SUPPLY} MPa; 운전 장력 최대 {T_OP:.2f} N; 오조작 장력 {T_MIS} N')
# 막대 감김 합력: 롤 쪽으로 떠나는 방향 u1(내려오는 테이프 (612.02,62.63)->(653.12,211.67), X 성분 0),
# 바인더 쪽 u2 = 경간 방향 (+0.193, -0.981, 0)(중심선 X = -22 - 0.197(Y-40)).
dy, dz = 653.12 - 612.02, 211.67 - 62.63
L = math.hypot(dy, dz)
u1 = (0.0, dy / L, dz / L)
n2 = math.hypot(0.197, 1.0)
u2 = (0.197 / n2, -1.0 / n2, 0.0)
wrap = 180 - math.degrees(math.acos(sum(a * b for a, b in zip(u1, u2))))
BAR = (-132.3, 600.0, 51.0)
PADC = (-131.0, 572.5, 43.5)      # 패드·받침면 마찰 합력 자리(패드 밑면 Z 43 + 테이프 0.5)
log(f'막대 감김각 {wrap:.1f}° (가득 롤), 합력 계수 {math.dist((0,0,0), tuple(a+b for a,b in zip(u1,u2))):.3f}')
W_GUIDE = (144.2 + 121.0 + 3.7 + 3.0) / 1000 * 3 * g   # 안내 블록 + 실린더 + 패드 + 로드 ×3 g

CASES = {
    # 이름: (힘 벡터 리스트 [(점, F)], SF 기준, 설명)
    '운전': ([(PADC, (T_OP * u2[0], T_OP * u2[1], 0.0)), (BAR, (0, 0, -W_GUIDE))], SF_OP,
             f'바인더 쪽 장력 {T_OP:.1f} N이 패드 구간 마찰로 안내 블록에 걸림(막대 쪽 장력 ≤ 0.65 N 무시) + 자중 ×3 g'),
    '오조작A_롤걸림': ([(BAR, tuple(T_MIS * (a + b) for a, b in zip(u1, u2)))], SF_MIS,
                    f'롤이 멈추고 매트가 테이프를 {T_MIS} N으로 끎 → 막대 감김 합력'),
    '오조작B_안내걸림': ([(PADC, (T_MIS * u2[0], T_MIS * u2[1], 0.0))], SF_MIS,
                     f'이음매·꼬임이 안내 블록 틈(Z 42~45)·패드 밑에 걸려 {T_MIS} N이 안내 블록에 바로'),
}


def moments(loads, about):
    F = [0.0, 0.0, 0.0]; M = [0.0, 0.0, 0.0]
    for p, f in loads:
        r = [p[i] - about[i] for i in range(3)]
        for i in range(3):
            F[i] += f[i]
        M[0] += r[1] * f[2] - r[2] * f[1]
        M[1] += r[2] * f[0] - r[0] * f[2]
        M[2] += r[0] * f[1] - r[1] * f[0]
    return F, M


def rect_torsion_beta(b, t):
    return (1 / 3) * (1 - 0.630 * t / b)


# ================================================================== A. 평판 혀 (Y 560~620, Z 30~100, t3)
log('\n== A. P_T05_PLATE 혀 뿌리 단면(Y 612~620, 안내 블록이 끝나고 기둥이 시작하기 전) ==')
T_PL = PL['bbox'][0][1] - PL['bbox'][0][0]            # 3
B_PL = 100.0 - PL['bbox'][2][0]                       # 70
SEC = (-76.5, 616.0, 65.0)
E_S, SY_S, _ = MAT['SUS304']


def plate_section(t, loads):
    F, M = moments(loads, SEC)
    s_out = abs(M[2]) / (B_PL * t ** 2 / 6)           # 판 밖 굽힘(Z축 둘레)
    s_in = abs(M[0]) / (t * B_PL ** 2 / 6)            # 판 안 굽힘(X축 둘레)
    s_ax = abs(F[1]) / (B_PL * t)
    tau_t = abs(M[1]) / (rect_torsion_beta(B_PL, t) * B_PL * t ** 2)   # Y축 비틀림
    tau_v = 1.5 * math.hypot(F[0], F[2]) / (B_PL * t)
    sig = s_out + s_in + s_ax
    vm = math.sqrt(sig ** 2 + 3 * (tau_t + tau_v) ** 2)
    return F, M, dict(s_out=s_out, s_in=s_in, s_ax=s_ax, tau_t=tau_t, tau_v=tau_v, vm=vm, sf=SY_S / vm)


res['plate'] = {}
for name, (loads, sfmin, desc) in CASES.items():
    F, M, s = plate_section(T_PL, loads)
    # 같은 형상에서 SF 기준을 넘는 두께, SF 1.2가 되는 장력
    t_need = next(t / 2 for t in range(4, 41) if plate_section(t / 2, loads)[2]['sf'] >= sfmin)
    beq = handcalc.beam(T_PL, B_PL, 60.0, load=abs(M[2]) / 60.0, e=E_S, sy=SY_S, sf_min=sfmin)
    row = dict(desc=desc, F=[round(x, 1) for x in F], M=[round(x) for x in M],
               **{k: round(v, 1) for k, v in s.items() if k != 'sf'}, sf=round(s['sf'], 2), sf_min=sfmin,
               t_need_mm=t_need, handcalc_beam_out_of_plane=beq)
    if name != '운전':
        row['T_at_sf1_2_N'] = round(T_MIS * s['sf'] / SF_BREAK, 0)
        row['T_at_sfmin_N'] = round(T_MIS * s['sf'] / sfmin, 0)
        for tt in (5.0, 6.0):
            row[f'sf_t{int(tt)}'] = round(plate_section(tt, loads)[2]['sf'], 2)
    res['plate'][name] = row
    log(f'{name}: F {row["F"]} M {row["M"]} | σ판밖 {row["s_out"]} σ판안 {row["s_in"]} τ비틀림 {row["tau_t"]} '
        f'VM {row["vm"]} MPa SF {row["sf"]} (기준 {sfmin}) 필요 t {t_need}')
    if 'sf_t5' in row:
        log(f'   t5 SF {row["sf_t5"]}, t6 SF {row["sf_t6"]}; SF 1.2가 되는 장력 {row["T_at_sf1_2_N"]} N, SF 2 장력 {row["T_at_sfmin_N"]} N')
# 처짐(운전, 혀 끝 막대 자리, 판 밖)
Fop, Mop, _ = plate_section(T_PL, CASES['운전'][0])
I_out = B_PL * T_PL ** 3 / 12
rot = abs(Mop[2]) * 60 / (E_S * I_out)      # 뿌리 60(Y 620→560 지렛대) 동안 같은 모멘트 → 끝 회전
res['plate_deflect_op'] = dict(tip_rot_deg=round(math.degrees(rot), 3), tip_disp_mm=round(abs(Mop[2]) * 60 ** 2 / (2 * E_S * I_out), 3),
                               pad_shift_mm=round(math.degrees(rot) * pi / 180 * 54.5, 3))
log('운전 처짐(혀 끝, 판 밖):', res['plate_deflect_op'])

# ================================================================== B. 혀 뿌리 볼트 (640,45) CB5-12 → 기둥 탭
log('\n== B. 평판 뿌리 볼트 (Y 640, Z 45) CB5-12, 기둥 탭(재질 D-10 → SS400 자리값) ==')
res['root_bolt'] = {}
for name, (loads, sfmin, _) in CASES.items():
    F, M = moments(loads, (-76.5, 620.0, 65.0))
    t_single = abs(M[2]) / 20.0        # 보수: 기둥 모서리 Y 620을 받침으로 가까운 볼트 하나가 다 받음(지렛대 20)
    ys = [20.0, 110.0, 110.0, 150.0, 150.0, 220.0]   # 640, 730×2, 770×2, 840 (강체판 분배 = 하한)
    t_rigid = abs(M[2]) * 20.0 / sum(y * y for y in ys)
    hc = handcalc.calc(5, 9.0, max(t_single, 1e-6), torque=6.0, bolt='12.9', base='SS400', sf_min=sfmin)
    res['root_bolt'][name] = dict(T_single_N=round(t_single, 1), T_rigid_N=round(t_rigid, 1), handcalc=hc)
    log(f'{name}: 볼트 인장 {t_single:.0f} N(가까운 볼트 하나, 보수) / {t_rigid:.0f} N(강체판) → worst {hc["worst"]} '
        f'SF {hc["sf_operating"]} 조임 {hc["sf_tightening"]} ok {hc["ok"]}')

# ================================================================== C. 안내 블록 ↔ 평판 인서트 2 (570,50)·(600,80)
log('\n== C. 안내 블록 M5 열압입 인서트 2(물림 8, PET-CF) ==')
INS = [(570.0, 50.0), (600.0, 80.0)]
res['inserts'] = {}
for name, (loads, sfmin, _) in CASES.items():
    F, M = moments(loads, (-78.0, 582.5, 64.0))
    # My(Y축): +이면 위 모서리(Z 92)가 눌리고 아래쪽 인서트가 당겨짐, -이면 반대(Z 36 받침)
    zp = 92.0 if M[1] > 0 else 36.0
    yp = 553.0 if M[2] > 0 else 612.0
    lz = [abs(zp - z) for _, z in INS]; ly = [abs(yp - y) for y, _ in INS]
    T = [abs(M[1]) * lz[i] / sum(v * v for v in lz) + abs(M[2]) * ly[i] / sum(v * v for v in ly) for i in range(2)]
    T = [max(0.0, t - max(0.0, F[0]) / 2) if False else t for t in T]   # 평판 쪽으로 미는 Fx는 보수로 빼지 않음
    tmax = max(T)
    shear = math.hypot(F[1], F[2]) / 2
    # 볼트는 평판 쪽(+X)에서 들어가 머리가 SUS304 평판에 앉는다 → 좌면은 SUS304로 따로 본다
    res['inserts'][name] = dict(T_N=[round(t, 1) for t in T], shear_each_N=round(shear, 1))
    for tq in (2.0, 1.5):
        hc = handcalc.calc(5, 8.0, tmax, torque=tq, bolt='12.9', base='PET-CF', sf_min=sfmin)
        seat = handcalc.calc(5, 8.0, tmax, torque=tq, bolt='12.9', base='SUS304', sf_min=sfmin)['sf_tightening']['조임 좌면']
        hc['sf_tightening']['조임 좌면'] = seat
        hc['ok'] = all(v >= sfmin for v in hc['sf_operating'].values()) and all(v >= 1.0 for v in hc['sf_tightening'].values())
        res['inserts'][name][f'torque_{tq}Nm'] = hc
        log(f'{name} @{tq} N·m: 인서트 인장 {[round(t) for t in T]} N, 전단 각 {shear:.0f} N → 운전 {hc["sf_operating"]} 조임 {hc["sf_tightening"]} ok {hc["ok"]}')

# ================================================================== D. 안내 블록 몸체
log('\n== D. P_T05_GUIDE 몸체 (PET-CF 30 MPa) ==')
SG = MAT['PET-CF'][1]
gd = {}
# D1 C틀: 실린더 밀기 반력 — 위판(장착)·등판·밑판(패드 받침), 지렛대 = 등판 안쪽 면 X -88 → 실린더 축 X -131
arm = -88.0 - (-131.0)
Mc = F_PUSH * arm
for part, b, t in (('위판 Y555~595 t10', 40.0, 10.0), ('등판 Y553~612 t10', 59.0, 10.0), ('밑판 Y553~600 t6', 47.0, 6.0)):
    s = Mc / (b * t * t / 6)
    gd['C틀_' + part] = dict(M=round(Mc), s=round(s, 2), sf=round(SG / s, 1), sf_min=SF_OP)
    log(f'C틀 {part}: σ {s:.2f} MPa SF {SG/s:.1f}')
# D2 막대 r8 Ø16 × 37, 양 옆벽 받침(단순 지지, 보수), 오조작 A
Fbar = T_MIS * math.dist((0, 0, 0), tuple(a + b for a, b in zip(u1, u2)))
Mb = Fbar * 37.0 / 4
sb = Mb / (pi * 16 ** 3 / 32)
gd['막대_오조작A'] = dict(F=round(Fbar, 1), M=round(Mb), s=round(sb, 2), sf=round(SG / sb, 2), sf_min=SF_MIS)
log(f'막대 오조작A: F {Fbar:.0f} N σ {sb:.1f} MPa SF {SG/sb:.2f}')
# D3 옆벽 t3(판 안 하중, 막대 높이 Z 51 - 밑판 윗면 42 = 9 지렛대), -X 옆벽 길이 Y 582.8~606 = 23.2
fy, fz = T_MIS * (u1[1] + u2[1]) / 2, T_MIS * (u1[2] + u2[2]) / 2
sw = abs(fy) * 9.0 / (3.0 * 23.2 ** 2 / 6) + abs(fz) / (3.0 * 23.2)
gd['옆벽_오조작A'] = dict(Fy=round(fy, 1), Fz=round(fz, 1), s=round(sw, 2), sf=round(SG / sw, 2), sf_min=SF_MIS)
log(f'옆벽(-X, 23.2 × t3) 오조작A: σ {sw:.1f} MPa SF {SG/sw:.2f}')
# D4 오조작 B — 앞벽(Y 555~562.2 = 7.2, X -147~-88 = 59, 위판에서 Z 82→45 = 37 늘어짐, +X 변은 등판에 붙음)
#      걸림이 앞벽 밑 모서리에 걸린다고 보고 위·옆 두 변 고정 판 → 외팔(보수)과 그 1/2(두 변)을 함께 적음
Mw = T_MIS * 37.0
sw1 = Mw / (59.0 * 7.2 ** 2 / 6)
gd['앞벽_오조작B'] = dict(M=round(Mw), s_cantilever=round(sw1, 1), sf_cantilever=round(SG / sw1, 2),
                        sf_two_edge_est=round(2 * SG / sw1, 2), sf_min=SF_MIS,
                        note='걸림 자리가 앞벽 밑 모서리일 때만. 두 변 고정 판은 외팔의 약 1/2 응력(추정, 3D 효과 → D-16 환경 생기면 고체 FEA)')
log(f'앞벽 오조작B(밑 모서리 걸림): 외팔 σ {sw1:.1f} MPa SF {SG/sw1:.2f}, 두 변 추정 SF {2*SG/sw1:.2f}')
res['guide'] = gd

# ================================================================== E. 패드
log('\n== E. P_T05_PAD ==')
pd = {}
A_pad = 28.0 * 20.0
pd['접촉압_kPa'] = round(F_PUSH / A_pad * 1000, 1)
pd['T홈바닥_압축_MPa'] = round(F_PUSH / (7.4 * 18.0), 2)          # 바닥 1.5는 테이프·받침면이 받침(압축)
lip = F_PULL / 2 / 18.0 * 1.5 / (2.0 ** 2 / 6)                       # 패드가 걸려 실린더가 당길 때 T홈 턱(돌출 1.5, 두께 2, 길이 18 ×2)
pd['T홈턱_당김_MPa'] = round(lip, 2); pd['T홈턱_sf'] = round(SG / lip, 1)
log(pd)
res['pad'] = pd

# ================================================================== F. 축·홀더·허브
log('\n== F. STEP대기_PSFJ16-100 · P_T05_HOLDER · P_T05_HUB/CAP ==')
sh = {}
W_roll = (M_ROLL + 0.3245 + 0.0569) * 3 * g
arm_roll = -110.0 - (-130.5)        # 홀더 -X 면 → 롤 테이프 중심
for name, F in (('운전', W_roll + T_OP * 0 + 0.65), ('오조작A', T_MIS)):
    M = F * arm_roll
    s = M / (pi * 16 ** 3 / 32)
    sh[name] = dict(F=round(F, 1), M=round(M), s=round(s, 2), sf=round(345.0 / s, 1))
    # 홀더 구멍 면압(길이 30, 우력 포함)
    p = F / (16 * 30) + 6 * M / (16 * 30 ** 2)
    sh[name]['holder_bore_p_MPa'] = round(p, 2); sh[name]['holder_bore_sf'] = round(SG / p, 1)
    # 홀더 플랜지 볼트 4(CB5-16, 기둥 탭, 물림 16-4.5-3=8.5): 모멘트 = F × (평판 면 X -78 → -130.5)
    Mf = F * 52.5
    tb = Mf * 48 / (2 * (8 ** 2 + 48 ** 2))
    sh[name]['holder_bolt_T_N'] = round(tb, 1)
    sh[name]['holder_bolt'] = handcalc.calc(5, 8.5, max(tb, 1e-6), torque=6.0, bolt='12.9', base='SS400',
                                            sf_min=SF_OP if name == '운전' else SF_MIS)
    log(f'축 {name}: F {F:.1f} N σ {s:.2f} MPa SF {345/s:.0f} | 홀더 구멍 p {p:.2f} MPa | 플랜지 볼트 {tb:.0f} N '
        f'SF {sh[name]["holder_bolt"]["sf_operating"]}')
# 오조작A에서 허브가 축에 들러붙으면 축 비틀림 → 홀더 슬릿 클램프가 미끄러짐(부러짐 아님)
Tq = T_MIS * 97.0
sh['비틀림_허브고착'] = dict(T_Nmm=round(Tq), tau=round(16 * Tq / (pi * 16 ** 3), 1),
                         clamp_slip_Nmm_est=round(0.3 * 2 * 2000 * 8),
                         note='클램프 M5 예압 약 2 kN(2 N·m) × μ0.3 × 양쪽 → 약 9.6 N·m < 40.5 N·m: 축이 홀더에서 돈다(미끄럼, 부러짐 아님)')
log(sh['비틀림_허브고착'])
# 허브 플랜지 Ø200 t3(PET-CF): 롤 자중 반경 하중은 심 Ø76이 받는다. 플랜지 축 방향 하중 정의 없음 → 손으로 미는 10 N 가정 beam
# 허브 플랜지 Ø200 t3: 운전에서 축 방향 하중이 없다(테이프가 롤에서 X 방향 성분 0으로 떠남, 축 수평).
# 정의된 하중이 없어 판정하지 않는다. 참고로 롤 자중 ×3 g 전부가 플랜지 끝(지렛대 62, 띠 폭 = 심 둘레 1/4 ≈ 60)에 걸려도:
hb = handcalc.beam(3.0, 60.0, 62.0, load=M_ROLL * 3 * g, e=MAT['PET-CF'][0], sy=SG, sf_min=SF_OP)
sh['허브플랜지_참고'] = hb
log('허브 플랜지(참고: 롤 자중 ×3 g를 끝에, 띠 60):', hb)
res['shaft_holder_hub'] = sh

# ================================================================== 요약
res['loads'] = dict(F_push=round(F_PUSH, 2), F_pull=round(F_PULL, 2), T_op=round(T_OP, 2), T_mis=T_MIS, wrap_deg=round(wrap, 1),
                    W_guide_3g=round(W_GUIDE, 2), W_roll_3g=round(W_roll, 2), u1=[round(x, 3) for x in u1], u2=[round(x, 3) for x in u2])
res['materials'] = MAT
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
print('saved', OUT)
