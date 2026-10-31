# -*- coding: utf-8 -*-
"""디테일링 DP-3 (v0.6.8) T05 테이프 공급 — 바뀐 하중 부품 손계산(해석부, 2026-11-01).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 손계산 +
엔진 handcalc(import, 엔진 폴더는 읽기만).
입력: tools/out/detail/DP-3/stepout/ 의 v0.6.8 임시 STEP 4개(HOLDER·CAP·GUIDE·PAD, 세계 좌표, 패드 저장값 -12.5).
하중: fea/models.json P_T05_* 행과 같은 식·같은 하중(mech_T05_fea1_handcalc.py). 바뀐 것만 다시 본다(E-18).
단위 mm, N, MPa.  실행: python -B -X utf8 fea/cases/detail_DP-3_handcalc.py
결과: fea/results/detail_DP-3_handcalc.json, 로그 fea/results/detail_DP-3_handcalc_log.txt
"""
import json, math, os, re, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENG = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.path.insert(0, os.path.join(ENG, 'engine', 'tools'))
import handcalc as HC  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'detail', 'DP-3', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'detail_DP-3_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'detail_DP-3_handcalc_log.txt')
PREV = json.load(open(os.path.join(ROOT, 'fea', 'results', 'mech_T05_fea1_handcalc.json'), encoding='utf-8'))
pi = math.pi
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


SG = 30.0            # PET-CF 층간 보수값(models.json P_T05_GUIDE)
E_PET = 6000.0
SF_OP, SF_MIS, SF_BREAK = 3.0, 2.0, 1.2
P_SUPPLY, BORE, ROD = 0.5, 10.0, 4.0
F_PUSH = pi / 4 * BORE ** 2 * P_SUPPLY
F_PULL = pi / 4 * (BORE ** 2 - ROD ** 2) * P_SUPPLY
T_MIS = 417.5
TAPE_W = 32.0        # D-06 임시(펼친 폭 32), MAT_TAPE_ROLL X -146.5~-114.5


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
    return dict(bbox=[[round(min(xs), 3), round(max(xs), 3)], [round(min(ys), 3), round(max(ys), 3)], [round(min(zs), 3), round(max(zs), 3)]],
                x_planes=lv(0), y_planes=lv(1), z_planes=lv(2), cylinders=cyls)


G = {f[:-5]: read_step(os.path.join(STEPDIR, f)) for f in sorted(os.listdir(STEPDIR)) if f.endswith('.step')}
res = dict(env='해석 못 함 — 환경 없음(자료대기 D-16)', step_dir=STEPDIR, checks=[])


def has(part, axis, val, tol=0.06):
    lst = G[part][axis + '_planes']
    ok = any(abs(v - val) <= tol for v in lst)
    res['checks'].append(dict(part=part, what=f'{axis}={val}', ok=ok))
    return ok


log('== STEP 확인 ==')
for k, v in G.items():
    log(k, 'bbox', v['bbox'])
    log('   x', v['x_planes']); log('   y', v['y_planes']); log('   z', v['z_planes'])
    log('   cyl', sorted(set((c['r'], tuple(abs(d) for d in c['dir'])) for c in v['cylinders'])))

# ============================================================ A. 안내 블록 앞벽(오조작B)
log('\n== A. P_T05_GUIDE 앞벽 오조작B ==')
for a, v in (('y', 553.0), ('y', 562.2), ('z', 45.0), ('z', 85.5), ('x', -147.0), ('x', -88.0)):
    log(f'  면 {a}={v}:', has('P_T05_GUIDE', a, v))
t_w, b_w = 562.2 - 553.0, -88.0 - (-147.0)
L_real, L_old = 85.5 - 45.0, 37.0
A = {}
for tag, L in (('실측_L40.5', L_real), ('옛식_L37', L_old)):
    bm = HC.beam(t_w, b_w, L, load=T_MIS, e=E_PET, sy=SG, sf_min=SF_MIS)
    A[tag] = dict(cantilever=bm, sf_cantilever=bm['sf'], sf_two_edge_est=round(2 * bm['sf'], 2))
    log(f'  {tag}: 외팔 σ {bm["stress_MPa"]} MPa SF {bm["sf"]} (needs_fea {bm["needs_fea"]}, 두께/길이 {t_w/L:.3f}) → 두 변 추정 SF {2*bm["sf"]:.2f}')
# 교차 확인: 항복선(모서리 삼각형) — 테이프 폭 32 선하중이 자유 모서리(X -147)에서 0.5~32.5에 걸린다.
#   삼각형 다리 w(밑 자유변, X 방향)·h(-X 자유변, Z 방향), 회전선 길이 L=√(w²+h²), 모서리 처짐 δ
#   내부일 = m·(w²+h²)/(w·h)·δ, 외부일 = (P/32)∫_{0.5}^{min(32.5,w)} δ(1-x/w)dx  → P_cap = m·(w²+h²)/(w·h) / f(w)
#   m = σ_allow·t²/6(탄성 단면, 보수) 와 σ·t²/4(소성) 둘 다 적는다. h ≤ 40.5, w ≤ 59.
best = None
for wi in range(10, 591):
    w = wi / 10
    a0, a1 = 0.5, min(32.5, w)
    f = ((a1 - a0) - (a1 ** 2 - a0 ** 2) / (2 * w)) / TAPE_W
    for hi in range(10, 406):
        h = hi / 10
        c = (w * w + h * h) / (w * h) / f
        if best is None or c < best[0]:
            best = (c, w, h)
c, w_b, h_b = best
P_el = c * SG * t_w ** 2 / 6
P_pl = c * SG * t_w ** 2 / 4
A['항복선_모서리'] = dict(w=w_b, h=h_b, coef=round(c, 3), P_elastic_m_N=round(P_el, 1), sf_elastic_m=round(P_el / T_MIS, 2),
                       P_plastic_m_N=round(P_pl, 1), sf_plastic_m=round(P_pl / T_MIS, 2),
                       note='상계(항복선)라 참고. 위·+X 고정변 음의 항복선은 이 삼각형 기구에 안 들어감. 점하중이 모서리 한 점이면 coef 2.0(최악)')
P_pt = 2.0 * SG * t_w ** 2 / 6
A['항복선_점하중_모서리'] = dict(P_elastic_m_N=round(P_pt, 1), sf_elastic_m=round(P_pt / T_MIS, 2), sf_plastic_m=round(1.5 * P_pt / T_MIS, 2))
log(f'  항복선(선하중 32): w {w_b} h {h_b} coef {c:.3f} → 탄성 m SF {P_el/T_MIS:.2f}, 소성 m SF {P_pl/T_MIS:.2f}')
log(f'  항복선(모서리 점하중, 최악): 탄성 m SF {P_pt/T_MIS:.2f}, 소성 m SF {1.5*P_pt/T_MIS:.2f}')
# 뿌리 R3 응력 집중(굽힘, r/t = 0.33, 큰 쪽 두께비 큼 → Kt 약 1.3, Peterson 계단 굽힘 근사) — 외팔 기준
Kt = 1.3
A['뿌리R3_Kt'] = dict(Kt=Kt, sf_cantilever_with_Kt=round(A['실측_L40.5']['sf_cantilever'] / Kt, 2),
                     note='PET-CF(FDM) 노치 민감도 불확실. 두 변 판 거동에서는 뿌리 최대 응력 자리가 바뀌어 근사로만 적음')
log(f'  R3 Kt {Kt}: 외팔 SF {A["실측_L40.5"]["sf_cantilever"]/Kt:.2f}')
res['A_guide_front_wall'] = A

# ============================================================ B. 홀더 플랜지 CB5-16 ×4
log('\n== B. P_T05_HOLDER 플랜지 CB5-16 ×4 (헤드 탭 물림 8.5, SS400 자리값 D-10, 1.5 N·m) ==')
holder_cb = [c for c in G['P_T05_HOLDER']['cylinders'] if abs(c['dir'][0]) > 0.99 and abs(c['r'] - 5.5) < 0.01]
log('  카운터보어 r5.5 X축 원통:', len(holder_cb), sorted(set((c['loc'][1], c['loc'][2]) for c in holder_cb)))
yb = G['P_T05_HOLDER']['bbox'][1]; zb = G['P_T05_HOLDER']['bbox'][2]
yz = sorted(set((round(c['loc'][1], 2), round(c['loc'][2], 2)) for c in holder_cb))
edge = min(min(y - 5.5 - 722.0, 778.0 - y - 5.5) for y, _ in yz) if yz else None
tb_mis = PREV['shaft_holder_hub']['오조작A']['holder_bolt_T_N']
B = {'bolt_T_misA_N': tb_mis, 'counterbore_edge_wall_mm': edge}
B['볼트'] = HC.calc(5, 8.5, tb_mis, torque=1.5, bolt='12.9', base='SS400', sf_min=SF_MIS)
B['좌면_와셔없음'] = HC.calc(5, 8.5, tb_mis, torque=1.5, bolt='12.9', base='PET-CF', dw=8.5, dh=5.5, sf_min=SF_MIS)
B['좌면_와셔Ø10'] = HC.calc(5, 7.5, tb_mis, torque=1.5, bolt='12.9', base='PET-CF', dw=10.0, dh=5.5, sf_min=SF_MIS)
log(f'  오조작A 볼트 인장 {tb_mis} N → 운전 {B["볼트"]["sf_operating"]} 조임 {B["볼트"]["sf_tightening"]}')
log(f'  좌면 PET-CF 와셔 없음 Ø8.5/Ø5.5: 조임 좌면 SF {B["좌면_와셔없음"]["sf_tightening"]["조임 좌면"]}')
log(f'  좌면 PET-CF 와셔 Ø10(D-43, 물림 8.5→7.5): 조임 좌면 SF {B["좌면_와셔Ø10"]["sf_tightening"]["조임 좌면"]}')
log(f'  카운터보어 Ø11 ↔ 플랜지 가장자리 살 {edge} mm')
res['B_holder_flange'] = B

# ============================================================ C. 평판 뿌리 CB5-16 ×2 (물림 9 → 11)
log('\n== C. 평판 뿌리 CB5-16 ×2 (헤드 물림 11, SS400 자리값, 6 N·m) ==')
C = {}
for name in ('운전', '오조작A_롤걸림', '오조작B_안내걸림'):
    T = PREV['root_bolt'][name]['T_single_N']
    sfm = SF_OP if name == '운전' else SF_MIS
    C[name] = HC.calc(5, 11.0, max(T, 1e-6), torque=6.0, bolt='12.9', base='SS400', sf_min=sfm)
    C[name]['seat_SUS304'] = HC.calc(5, 11.0, max(T, 1e-6), torque=6.0, bolt='12.9', base='SUS304', sf_min=sfm)['sf_tightening']['조임 좌면']
    log(f'  {name}: T {T} N → 운전 {C[name]["sf_operating"]} 조임 {C[name]["sf_tightening"]} 좌면(SUS304 평판) {C[name]["seat_SUS304"]}')
res['C_root_bolt'] = C

# ============================================================ D. 평판 → 안내 블록 CB5-16 ×2 + MBIS5-6.5-8 (물림 8, 1.5 N·m)
log('\n== D. 안내 블록 인서트 CB5-16 + MBIS5-6.5-8 ×2 (물림 8, 1.5 N·m) ==')
D = {}
for name in ('운전', '오조작A_롤걸림', '오조작B_안내걸림'):
    T = max(PREV['inserts'][name]['T_N'])
    sfm = SF_OP if name == '운전' else SF_MIS
    hc = HC.calc(5, 8.0, T, torque=1.5, bolt='12.9', base='PET-CF', sf_min=sfm)
    hc['sf_tightening']['조임 좌면'] = HC.calc(5, 8.0, T, torque=1.5, bolt='12.9', base='SUS304', sf_min=sfm)['sf_tightening']['조임 좌면']
    D[name] = hc
    log(f'  {name}: T {T} N → 운전 {hc["sf_operating"]} 조임 {hc["sf_tightening"]}')
D['note'] = 'PET-CF 직접 나사로 본 보수값(인서트 외경 6.8 널링 면적이 더 큼). 인서트 끌어냄 카탈로그 값은 D-41'
res['D_guide_inserts'] = D

# ============================================================ E. 클램프 CB5-20 ×2 + MBIS5-6.5-8 (홀더 귀 7.5, 캡 8)
log('\n== E. 클램프 CB5-20 (홀더 귀 물림 7.5, 캡 물림 8), 1.5 N·m ==')
E = {}
for tag, le in (('홀더귀', 7.5), ('캡', 8.0)):
    hc = HC.calc(5, le, 1e-6, torque=1.5, bolt='12.9', base='PET-CF', dw=8.5, dh=5.5, sf_min=SF_OP)
    E[tag] = dict(le=le, preload_N=hc['preload_N'], sf_tightening=hc['sf_tightening'], m01_ok=le >= 7.5)
    log(f'  {tag}: 물림 {le} 예압 {hc["preload_N"]} N 조임 {hc["sf_tightening"]}')
slip = 0.3 * 2 * 1500.0 * 8.0
E['클램프_미끄럼토크_Nmm'] = slip
E['운전_롤끌림토크_Nmm'] = round(3.0 * 97.0, 1)
E['sf_slip_op'] = round(slip / (3.0 * 97.0), 1)
log(f'  클램프 미끄럼 토크 {slip:.0f} N·mm (μ0.3 × 양쪽 × 1.5 kN × r8) vs 롤 끌림 3 N × r97 = {3*97} → SF {slip/291:.1f}')
res['E_clamp'] = E

# ============================================================ F. 패드 T홈 (Z 43~63)
log('\n== F. P_T05_PAD T홈 ==')
for a, v in (('z', 43.0), ('z', 49.0), ('z', 53.1), ('z', 60.4), ('z', 63.0), ('y', 570.3), ('y', 574.7)):
    log(f'  면 {a}={v}:', has('P_T05_PAD', a, v))
pk_w, nk_w = 7.4, 574.7 - 570.3
lip_over = (pk_w - nk_w) / 2
lip_t = 63.0 - 60.4
lip_len = -126.75 - (-145.0)
s_lip = (F_PULL / 2 / lip_len) * lip_over / (lip_t ** 2 / 6)
tau_lip = F_PULL / (2 * lip_len * lip_t)
p_rod = F_PUSH / (pi / 4 * ROD ** 2)
F = dict(neck=nk_w, pocket=pk_w, lip_overhang=lip_over, lip_t=lip_t, lip_len=round(lip_len, 2),
         F_pull=round(F_PULL, 2), s_lip=round(s_lip, 2), sf_lip=round(SG / s_lip, 1), tau_lip=round(tau_lip, 3),
         F_push=round(F_PUSH, 2), p_rod_end=round(p_rod, 2), sf_rod_end=round(SG / p_rod, 1),
         p_mat_kPa=round(F_PUSH / (28 * 20) * 1000, 1),
         note='턱 = 너트 위 Z 60.4~63(t2.6), 돌출 1.5, 길이 = 열린 끝 X -145 → 주머니 끝 -126.75. 밀기는 로드 끝 Ø4가 Z 49 면을 누름')
log(F)
res['F_pad'] = F

# ============================================================ 요약
summ = dict(
    front_wall_two_edge_real=A['실측_L40.5']['sf_two_edge_est'], front_wall_two_edge_L37=A['옛식_L37']['sf_two_edge_est'],
    front_wall_cantilever_real=A['실측_L40.5']['sf_cantilever'], front_wall_cantilever_L37=A['옛식_L37']['sf_cantilever'],
    yield_line_line_load_el=A['항복선_모서리']['sf_elastic_m'], yield_line_point_el=A['항복선_점하중_모서리']['sf_elastic_m'],
    holder_seat_no_washer=B['좌면_와셔없음']['sf_tightening']['조임 좌면'], holder_seat_washer10=B['좌면_와셔Ø10']['sf_tightening']['조임 좌면'],
    root_bolt_misB_worst=C['오조작B_안내걸림']['sf_operating'], insert_misA=D['오조작A_롤걸림']['sf_operating'],
    insert_tight=D['운전']['sf_tightening'], clamp=E['홀더귀']['sf_tightening'], pad_lip=F['sf_lip'])
res['summary'] = summ
log('\n== 요약 ==')
for k, v in summ.items():
    log(' ', k, v)
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
print('saved', OUT)
