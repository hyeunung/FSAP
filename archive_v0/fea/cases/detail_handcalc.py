# -*- coding: utf-8 -*-
"""디테일링 해석부 손계산 (2026-10-31, 대상 v0.6.1 임시 STEP tools/out/detail/stepout/ 33개).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 손계산.
1) 형상 대조: detail/stepout 33개를 지난 과제 STEP(같은 이름, 가장 최근 과제)과 꼭짓점 bbox·면 위치·원통 반지름으로 대조
   → 같으면 지난 결과 재사용(E-18 "같은 입력은 다시 풀지 않는다", E-21).
2) T06 팔·칼·브래킷: 지난 케이스 cases/mech_T06_handcalc.py 를 그대로(입력 폴더만 detail/stepout으로) 실행해 같은 모델로 다시 확인하고,
   실형상 경계조건 what-if(팔 두께 t3~t6, +X 홈 틈)를 더한다. 모델(models.json P_T06_ARM)은 바꾸지 않는다.
3) 디테일 체결(새 볼트 자리) 손계산: 엔진 handcalc.calc (엔진 파일은 읽기만).
실행: PYTHONIOENCODING=utf-8 python -B fea/cases/detail_handcalc.py
결과: fea/results/detail_handcalc.json, 로그 fea/results/detail_handcalc_log.txt
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402

DET = os.path.join(ROOT, 'tools', 'out', 'detail', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'detail_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'detail_handcalc_log.txt')
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


# ------------------------------------------------------------------ T06 케이스 실행(입력 폴더만 바꿈)
src = open(os.path.join(HERE, 'mech_T06_handcalc.py'), encoding='utf-8').read()
src = src.replace("os.path.join(ROOT, 'tools', 'out', 'mech_T06', 'stepout')", repr(DET))
src = src.replace("'mech_T06_handcalc.json'", "'detail_T06_rerun.json'").replace("'mech_T06_handcalc_log.txt'", "'detail_T06_rerun_log.txt'")
ns = {'__file__': os.path.join(HERE, 'mech_T06_handcalc.py'), '__name__': 't06'}
exec(compile(src, 'mech_T06_handcalc.py(detail)', 'exec'), ns)
T6 = ns['res']
G = ns['G']                     # detail/stepout 33개 형상
read_step = ns['read_step']
res = {'source': 'tools/out/detail/stepout', 'fea': '해석 못 함 — 환경 없음(D-16)'}

# ------------------------------------------------------------------ 1. 형상 대조
ORDER = ['mech_T06/stepout', 'mech_S01/stepout', 'mech_T05/stepout1', 'mech_T05/stepout', 'mech_T04/stepout', 'mech_T02/stepout', 'mech_T01/stepout']
geo = {}
for name, g in sorted(G.items()):
    prev = None
    for d in ORDER:
        p = os.path.join(ROOT, 'tools', 'out', d, name + '.step')
        if os.path.exists(p):
            prev = (d, read_step(p)); break
    if prev is None:
        geo[name] = dict(prev=None, same=None, bbox=g['bbox']); continue
    q = prev[1]
    def close(a, b, tol=0.06):
        return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))
    same = (all(close(g['bbox'][k], q['bbox'][k]) for k in range(3)) and close(g['x_planes'], q['x_planes'])
            and close(g['y_planes'], q['y_planes']) and close(g['z_planes'], q['z_planes']) and close(g['cyl_r'], q['cyl_r']))
    geo[name] = dict(prev=prev[0], same=same, bbox=g['bbox'], prev_bbox=q['bbox'])
res['geometry'] = geo
diff = [k for k, v in geo.items() if v['same'] is False]
nop = [k for k, v in geo.items() if v['prev'] is None]
log(f'\n== 형상 대조: {len(geo)}개, 같음 {sum(1 for v in geo.values() if v["same"])}, 다름 {diff}, 지난 STEP 없음 {nop}')
for k in diff:
    log('  다름', k, geo[k]['prev'], geo[k]['prev_bbox'], '→', geo[k]['bbox'])

# ------------------------------------------------------------------ 2. T06 팔 what-if (실형상 경계조건, 같은 모델)
F_MAT, u = ns['F_MAT'], ns['TAPE_DIR']
GX0 = ns['GAP_XP']
wi = []
for gxp in (0.4, 0.25, 0.1):
    ns['GAP_XP'] = gxp
    for t in (3.0, 4.0, 5.0, 6.0):
        r = ns['tape_pull'](t); r['gap_xp'] = gxp
        # 굽힘 R = t(안쪽 R = t 유지 가정), 구멍–굽힘 2t, 칼 볼트 Z 42 → 굽힘 안쪽 Z 54 거리 12 - (t-3)(밑으로 두꺼워질 때)
        r['hole_bend_need'] = 2 * t
        wi.append(r)
ns['GAP_XP'] = GX0
res['whatif_arm'] = wi
for r in wi:
    log('  what-if', r)
# 처짐(칼 막힘 80.5 N) t별
E = 193000.0
for t in (3.0, 4.0, 5.0, 6.0):
    bm = handcalc.beam(t, 21.0, 48.0, load=ns['F_ROD'], e=E, sy=205.0, sf_min=2.0)
    res.setdefault('arm_beam_jam_t', []).append(dict(t=t, sf=bm['sf'], defl=bm['deflection_mm'], thin=bm['thin']))
log('  칼 막힘 handcalc.beam t3~6:', res['arm_beam_jam_t'])
# 질량 변화(팔 전개 110.54 × 21, SUS304 7.93 g/cm³)
res['arm_mass_g'] = {t: round(110.54 * 21 * t * 7.93e-3, 1) for t in (3, 4, 5, 6)}
log('  팔 질량(전개 110.54×21):', res['arm_mass_g'])

# ------------------------------------------------------------------ 3. 디테일 체결 손계산(새 볼트 자리)
B = {}
def hc(key, d, le, load, torque, base, need, **kw):
    r = handcalc.calc(d, le, load, torque=torque, bolt='12.9', base=base, sf_min=need, **kw)
    B[key] = dict(load_N=round(load, 1), le=le, torque=torque, base=base, need=need, worst=r['worst'], ok=r['ok'],
                  sf_op=r['sf_operating'], sf_tight=r['sf_tightening'], near=r['near_limit'], engage=r['engage_ratio'])
    log(f'  [{"됨" if r["ok"] else "미달"}] {key}: 하중 {load:.1f} N, 물림 {le}, 토크 {torque} → worst {r["worst"]} {r["sf_tightening"]}')
log('\n== 체결 손계산 ==')
F_ROD = ns['F_ROD']; Fx_arm5 = [r for r in wi if r['t'] == 5.0 and r['gap_xp'] == 0.4][0]['Fx_arm']
# 칼–팔 M5 ×2 + 너트: 너트 체결(좌면 SUS304 판, 너트 강도 등급 표준 → 물림 = 너트 높이 4)
hc('KNIFE_ARM_M5_nut_jam', 5, 4.0, F_ROD / 2, 6.0, 'SUS304', 2.0, dw=8.5, dh=5.5)
# 오조작 T: 칼 옆힘 Fx(팔 몫)이 볼트 줄(Z 12 절단 자세)→테이프 Z −0.5 지렛대 12.5, 볼트 2개 Y 피치 → 인장 ≈ Fx·12.5/(칼 두께 방향 지렛 1.5)… 칼 판이 팔 면에 맞댐: 지렛점 칼 끝 모서리, 볼트 축 거리 ≈ 판 맞댐 폭/2. 보수로 볼트 줄–모서리 거리 5(맞댐 위·아래 끝) 사용
for t in (3.0, 5.0):
    fx = [r for r in wi if r['t'] == t and r['gap_xp'] == 0.4][0]['Fx_arm']
    tens = fx * 12.5 / 5.0 / 2
    hc(f'KNIFE_ARM_M5_nut_T_t{int(t)}', 5, 4.0, tens, 6.0, 'SUS304', 2.0, dw=8.5, dh=5.5)
# 축–팔 M5(PSFJT16-100-M5 축 끝 암나사, 물림 = 축 탭 깊이 미확인 → 1.5d = 7.5 가정, 축 S45C 상당 → base 'S45C'가 없으면 SS400 보수)
M_T = ns['M_c']  # 칼 막힘 우력 F·(108−24)
# 축–팔은 우력이 팔 판을 통해 축 끝 면 맞댐 + 볼트 1개: 볼트 인장 ≈ M / (축 끝 면 반지름 8)
hc('SHAFT_ARM_M5_jam', 5, 7.5, M_T / 8.0, 6.0, 'S45C', 2.0)
# 오조작 T 비틀림(Fy_arm·H_ARM)이 축–팔 한 볼트로: 마찰 토크 μ·Fv·rm 비교
fy5 = [r for r in wi if r['t'] == 5.0 and r['gap_xp'] == 0.4][0]['Fy_arm']
T_tw = fy5 * ns['H_ARM']
Fv = 6.0e3 / (0.2 * 5)
T_fric = 0.15 * Fv * (8.0 + 2.75) / 2 * 1  # 좌면 + 축 끝 면 평균 반지름 근사, 마찰면 1
B['SHAFT_ARM_twist_T'] = dict(T_Nmm=round(T_tw, 0), T_fric_Nmm=round(T_fric, 0), sf=round(T_fric / T_tw, 2),
                              note='오조작 T 비틀림이 축–팔 M5 1개 마찰로 버티나. 미끄러지면 팔이 축 둘레로 돎(부러짐 아님) → 회전 멈춤(D컷·핀 또는 팔–축 2점) 필요 여부')
log(f'  축–팔 비틀림 오조작 T: T {T_tw:.0f} N·mm vs 마찰 {T_fric:.0f} → SF {T_fric / T_tw:.2f}')
# 로드–팔 NTJ-015C(M5 로드 나사, 팔 사이 끼움): 칼 막힘 80.5 N 인장 = 로드 축력, 물림 = 너트 높이 4
hc('ROD_ARM_NTJ_jam', 5, 4.0, F_ROD, 3.0, 'SUS304', 2.0, dw=8.0, dh=6.0)
# LHFR16 플랜지 CB4-16 + 너트(T06 케이스 그대로), 브래킷–헤드 CB5(T06 케이스 그대로) — 재사용
B['LHFR16_M4_x4'] = dict(reuse='fea/results/mech_T06_handcalc.json bolts.bushing_M4', **{k: T6['bolts']['bushing_M4']['hc'][k] for k in ('worst', 'ok', 'sf_tightening')})
B['BRACKET_HEAD_M5_x2'] = dict(reuse='fea/results/mech_T06_handcalc.json bolts.bracket_M5_오조작', **{k: T6['bolts']['bracket_M5_오조작']['hc'][k] for k in ('worst', 'ok', 'sf_tightening')})
# T07 스커트 M5 T너트(HNTT8-5) + CB5-12: 무릎 200 N(D-38) 판 가운데 → 둘레 볼트 몫(보수: 가장 가까운 4개가 받음), 판 앞→형재 앞면 압축이라 볼트는 인장 없음. 반대 방향(당김) 보수로 200/4
hc('SKIRT_HNTT8-5_pull', 5, 4.0, 200.0 / 4, 4.0, 'SS400', 2.0)  # T너트 강재 암나사(물림 = T너트 두께 4 가정)
res['bolts'] = B

# ------------------------------------------------------------------ 저장
res['t06_rerun'] = dict(summary=T6['summary'], cases=[{k: c[k] for k in ('name', 'part', 'sf', 'need', 'verdict')} for c in T6['cases']],
                       stiffness=T6['stiffness'], bush_radial=T6['bush_radial'], checks_bad=[c for c in T6['checks'] if not c['ok']])
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
log('저장', OUT)

# ------------------------------------------------------------------ 4. 절삭 L(가로 다리 th만 두껍게, 세로 다리 t3 그대로) — M-04 구멍–굽힘 2t 회피안
def mixed(th, tv=3.0, gxp=0.4, E_=193000.0, G_=77000.0, Sy=205.0):
    b = 21.0; H = ns['H_ARM']; L = ns['L_HL']; LKN = ns['L_KN']; LVL = ns['L_VL']
    Ih = b * th ** 3 / 12; Zh = b * th ** 2 / 6; Iv = b * tv ** 3 / 12
    bt = (1 / 3) * (1 - 0.630 * th / b); Jt = bt * b * th ** 3
    cvl = (LVL ** 3 / (3 * E_ * Iv) + LKN * LVL ** 2 / (2 * E_ * Iv)) + (LVL ** 2 / (2 * E_ * Iv) + LKN * LVL / (E_ * Iv)) * LKN
    cx = ns['c_knife'] + cvl + H ** 2 * L / (E_ * Ih)
    cin = LKN ** 3 / (3 * 206000.0 * (1.5 * b ** 3 / 12)) + (LKN + LVL) ** 3 / (3 * E_ * (tv * b ** 3 / 12))
    cy = H ** 2 * L / (G_ * Jt) + cin
    Fx_, Fy_ = abs(ns['Fx']), abs(ns['Fy'])
    fy = min(Fy_, ns['GAP_YM'] / cy); fx = min(Fx_, gxp / cx)
    ta = fy * H / (bt * b * th ** 2); sb = fx * H / Zh
    se = math.sqrt(sb ** 2 + 3 * ta ** 2)
    lev = ns['lev_k']
    tilt = ns['F_CUT'] * lev ** 2 / (2 * E_ * Ih) * H
    return dict(th=th, tv=tv, gap_xp=gxp, Fx_arm=round(fx, 1), Fy_arm=round(fy, 1), tau=round(ta, 1), sigma_b=round(sb, 1),
                sf_T=round(Sy / se, 2), sf_jam=round(Sy / (ns['F_ROD'] * lev / Zh), 2), sf_op=round(Sy / ((ns['F_CUT'] + ns['W_MOVE']) * lev / Zh), 2),
                shear_gap_op=round(ns['GAP_XM'] - (tilt - ns['SIDE'] * ns['F_CUT'] * cx), 4))
res['machined_L'] = [mixed(th, 3.0, g) for th in (4.0, 5.0, 6.0) for g in (0.4, 0.25)]
log('\n== 절삭 L 팔(가로 th, 세로 t3) what-if ==')
for r in res['machined_L']:
    log('  ', r)
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')
