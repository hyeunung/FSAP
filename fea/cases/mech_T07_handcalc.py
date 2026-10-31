# -*- coding: utf-8 -*-
"""T07 로딩·배출 — 작업자 쪽 가드 평판(SUS304 t2) 강도·처짐 손계산 (해석부, 2026-10-31, 대상 v0.6.0).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 손계산.
얇은 판(t/L < 0.1)이라 엔진 handcalc.beam을 먼저 본다(E-18). 보는 판(평판 4변 지지)이라
보 공식은 하한 비교로만 쓰고, 판정은 Roark 직사각 평판 공식(표 11.4 1d 단순 지지 / 8b 고정)으로 한다.
입력 형상: 모델링부 임시 STEP 3개(tools/out/mech_T07/stepout/*.step, 대기 세계 좌표).
판 bbox·두께·법선은 STEP의 VERTEX·PLANE에서 읽는다(옛 케이스 좌표 안 씀).
받침(형재 앞면) 위치는 mech_T07_model.md 3절 표(CAD bbox): G1 Z −680~−600, G4 Z −140~−60,
중간 기둥 460 X ±(870~950), 끝 기둥 1580 X ±(1425~1505). 볼트·T너트는 아직 안 그림(T07-S06) →
판 둘레는 형재 앞면에 볼트(피치 ≤ 300)로 붙는다고 보고 단순 지지(보수)와 고정(상한) 두 경계로 푼다.

하중(요구서 6-1 비어 있음 → M-09):
  오조작: 무릎 200 N, 접촉 반지름 50(D-38 임시값, T07 선정 2-3) — 판 칸 가운데(최대 모멘트 자리), 판 면에 수직(+Y, 기계 안쪽)
  운전: 작업자가 판에 기대거나 닿는 힘은 요구서에 없다 → 같은 200 N을 운전 기준 SF 3으로도 본다(보수)
  자중 ×3 g: 판은 세워져 있어 자중은 판 면 안(−Z). 받침면 위에 서거나 볼트로 매달림
단위 mm, N, MPa.  실행: PYTHONIOENCODING=utf-8 python -B fea/cases/mech_T07_handcalc.py
결과: fea/results/mech_T07_handcalc.json, 로그 fea/results/mech_T07_handcalc_log.txt
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T07', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T07_handcalc.json')
LOG = os.path.join(ROOT, 'fea', 'results', 'mech_T07_handcalc_log.txt')
g = 9.81
pi = math.pi
_log = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    _log.append(s)
    print(s)


E, SY, NU, RHO = 193000.0, 205.0, 0.3, 7.93e-6   # SUS304 (엔진 handcalc BASE 항복 205), kg/mm³
SF_OP, SF_MIS, SF_BREAK = 3.0, 2.0, 1.2           # M-09 기본값, SF < 1.2 = 영구 변형(부서 지시)
W_KNEE, R0 = 200.0, 50.0                          # D-38 임시값

# Roark 표 11.4 (7판) — a/b → 계수 (b = 짧은 변)
# 1d 단순 지지, 가운데 작은 원 하중: σ = 3W/(2πt²)[(1+ν)ln(2b/πr0') + β1], y = α W b²/(E t³)
SS_B1 = [(1.0, 0.000), (1.2, 0.217), (1.4, 0.348), (1.6, 0.423), (1.8, 0.480), (2.0, 0.510), (1e9, 0.565)]
SS_AL = [(1.0, 0.1267), (1.2, 0.1478), (1.4, 0.1621), (1.6, 0.1714), (1.8, 0.1769), (2.0, 0.1803), (1e9, 0.1849)]
# 8b 네 변 고정, 가운데 작은 원 하중: σ가운데 = 3W/(2πt²)[(1+ν)ln(2b/πr0') + β1], σ변 = β2 W/t², y = α W b²/(E t³)
FX_B1 = [(1.0, -0.238), (1.2, -0.078), (1.4, 0.011), (1.6, 0.053), (1.8, 0.068), (2.0, 0.067), (1e9, 0.067)]
FX_B2 = [(1.0, 0.7542), (1.2, 0.8940), (1.4, 0.9624), (1.6, 0.9906), (1.8, 1.0000), (2.0, 1.004), (1e9, 1.008)]
FX_AL = [(1.0, 0.0611), (1.2, 0.0706), (1.4, 0.0754), (1.6, 0.0777), (1.8, 0.0786), (2.0, 0.0788), (1e9, 0.0791)]


def interp(tab, r):
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if r <= x1:
            if x1 > 1e8:
                return y1 if r > 2.0 else y0
            return y0 + (y1 - y0) * (r - x0) / (x1 - x0)
    return tab[-1][1]


def read_step(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    ents = dict(re.findall(r'^#(\d+)=(.*);\s*$', txt, re.M))
    pts = {}
    for k, v in ents.items():
        m = re.match(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", v)
        if m:
            pts[k] = tuple(float(x) for x in m.group(1).split(','))
    dirs = {}
    for k, v in ents.items():
        m = re.match(r"DIRECTION\('[^']*',\(([^)]*)\)\)", v)
        if m:
            dirs[k] = tuple(float(x) for x in m.group(1).split(','))
    verts = []
    for v in ents.values():
        m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", v)
        if m:
            verts.append(pts[m.group(1)])
    planes = []
    for v in ents.values():
        m = re.match(r"PLANE\('[^']*',#(\d+)\)", v)
        if m:
            ax = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+),#(\d+)\)", ents[m.group(1)])
            planes.append((pts[ax.group(1)], dirs[ax.group(2)]))
    bb = [(min(p[i] for p in verts), max(p[i] for p in verts)) for i in range(3)]
    ys = sorted({round(o[1], 3) for o, n in planes if abs(abs(n[1]) - 1) < 1e-6})
    # 앞면(Y 최소) 다각형 넓이(XZ, 꼭짓점 순서를 각도로 정렬 — 볼록이 아니어도 V홈 하나뿐이라 따로 뺌)
    front = [p for p in verts if abs(p[1] - bb[1][0]) < 1e-6]
    notch = [p for p in front if bb[0][0] + 1e-6 < p[0] < bb[0][1] - 1e-6]
    return {'n_vert': len(verts), 'bbox': [[round(a, 3), round(b, 3)] for a, b in bb], 'y_planes': ys,
            'thickness': round(ys[-1] - ys[0], 3) if len(ys) >= 2 else None,
            'n_front_vert': len(front), 'notch_pts': [[round(c, 3) for c in p] for p in notch]}


def plate(name, a, b, t, w, r0, sf_req):
    a, b = max(a, b), min(a, b)
    r = a / b
    r0e = math.sqrt(1.6 * r0 ** 2 + t ** 2) - 0.675 * t if r0 < 0.5 * t else r0
    k = 3 * w / (2 * pi * t ** 2)
    L = math.log(2 * b / (pi * r0e))
    s_ss = k * ((1 + NU) * L + interp(SS_B1, r))
    y_ss = interp(SS_AL, r) * w * b ** 2 / (E * t ** 3)
    s_fx_c = k * ((1 + NU) * L + interp(FX_B1, r))
    s_fx_e = interp(FX_B2, r) * w / t ** 2
    s_fx = max(s_fx_c, s_fx_e)
    y_fx = interp(FX_AL, r) * w * b ** 2 / (E * t ** 3)
    res = {'panel': name, 'a': a, 'b': b, 'a_b': round(r, 3), 't': t, 'W': w, 'r0': r0,
           'simply_supported': {'sigma': round(s_ss, 2), 'sf': round(SY / s_ss, 2), 'defl': round(y_ss, 2)},
           'clamped': {'sigma_center': round(s_fx_c, 2), 'sigma_edge': round(s_fx_e, 2), 'sf': round(SY / s_fx, 2), 'defl': round(y_fx, 2)},
           'sf_req': sf_req}
    res['governing_sf'] = res['simply_supported']['sf']
    res['ok'] = res['governing_sf'] >= sf_req
    res['near'] = sf_req <= res['governing_sf'] < 1.1 * sf_req
    res['defl_over_t'] = round(y_ss / t, 2)
    return res


def main():
    R = {'case': 'mech_T07_handcalc', 'target': 'FSAP_v0.6.0', 'fea': '해석 못 함 — 환경 없음(자료대기 D-16)',
         'material': {'name': 'SUS304', 'E': E, 'Sy': SY, 'nu': NU}, 'criteria': {'sf_op': SF_OP, 'sf_mis': SF_MIS, 'sf_break': SF_BREAK,
                                                                                    'source': '요구서 6-1 기본값 M-09, 6-2 미정(변위 기본값 없음)'}}
    geo = {}
    for n in ('C', 'L', 'R'):
        geo[n] = read_step(os.path.join(STEPDIR, 'P_T07_SKIRT_%s.step' % n))
        log('STEP', n, geo[n]['bbox'], 't', geo[n]['thickness'], 'notch', geo[n]['notch_pts'])
    R['step'] = geo
    t = geo['C']['thickness']
    # 부피·질량(STEP bbox, V홈 삼각형 뺌) ↔ 모델 질량
    vol = {}
    for n in ('C', 'L', 'R'):
        bb = geo[n]['bbox']
        v = (bb[0][1] - bb[0][0]) * (bb[2][1] - bb[2][0]) * t
        if len(geo[n]['notch_pts']) == 3:
            xs = [p[0] for p in geo[n]['notch_pts']]; zs = [p[2] for p in geo[n]['notch_pts']]
            v -= 0.5 * (max(xs) - min(xs)) * (max(zs) - min(zs)) * t
        vol[n] = {'vol_mm3': round(v, 1), 'mass_kg': round(v * RHO, 3)}
    R['mass'] = vol
    R['mass_model_kg'] = {'C': 17.8862, 'L': 5.8458, 'R': 5.8458}
    # E-19 묶기: L·R 대칭(같은 bbox 치수·같은 질량·주변 같음) → L 하나로
    dl = [b - a for a, b in geo['L']['bbox']]; dr = [b - a for a, b in geo['R']['bbox']]
    mirror = all(abs(x - y) < 1e-6 for x, y in zip(dl, dr)) and abs(geo['L']['bbox'][0][0] + geo['R']['bbox'][0][1]) < 1e-6
    R['groups'] = {'L_R_mirror': mirror, 'rep': 'L'}
    log('L/R 거울 대칭', mirror)

    # 칸(받침 형재 앞면 사이의 자유 칸)
    panels = {
        'C': {'x': (-870.0, 870.0), 'z': (-600.0, -140.0), 'src': '중간 기둥 안쪽 ±870, G1 윗면 −600, G4 밑면 −140'},
        'L': {'x': (-1425.0, -950.0), 'z': (-600.0, -140.0), 'src': '끝 기둥 안쪽 −1425 ~ 중간 기둥 바깥 −950'},
    }
    R['panels'] = panels
    cases = []
    for pn, p in panels.items():
        a = p['x'][1] - p['x'][0]; b = p['z'][1] - p['z'][0]
        for lc, r0, sfr in (('오조작 무릎 200 N r0 50', R0, SF_MIS), ('운전 기준으로 같은 200 N r0 50(보수)', R0, SF_OP),
                            ('민감도: 오조작 접촉 r0 25(발끝·무릎 모서리)', 25.0, SF_MIS)):
            c = plate(pn, a, b, t, W_KNEE, r0, sfr)
            c['load_case'] = lc
            cases.append(c)
            log(pn, lc, 'σss', c['simply_supported']['sigma'], 'SF', c['governing_sf'], '/', sfr,
                'δss', c['simply_supported']['defl'], 'σfx', c['clamped']['sigma_center'], c['clamped']['sigma_edge'])
    R['plate_cases'] = cases

    # 보 공식(E-18 먼저): 칸 높이 460을 양끝 고정 보, 가운데 하중 → guided 반 길이 230, 하중 W/2
    # 유효 폭 b = 2·r0 = 100(하중 자리 폭만, 하한) — 판의 두 방향 휨을 못 보므로 비교용
    bm = handcalc.beam(t, 2 * R0, 230.0, load=W_KNEE / 2, e=E, sy=SY, end='guided', sf_min=SF_MIS)
    R['beam_first'] = bm
    log('beam(guided, b100, L230, 100 N)', 'σ', bm['stress_MPa'], 'SF', bm['sf'], 'δ×2(양쪽)', bm['deflection_mm'] * 2, 'thin', bm['thin'])

    # 큰 처짐 확인: δ/t > 0.5면 막(membrane) 효과로 실제 굽힘 응력은 선형값보다 작다(선형 = 보수)
    # 처짐 ↔ 판 뒤 가장 가까운 것: 판 뒷면 Y −1740 ↔ 매트 bbox 89.22(model 보고서 1줄 7), 매트 Z ≥ −1(판 칸 밖 위쪽).
    # 칸 뒤(Z −600~−140)에 있는 고정물: G2 680은 X ±(890~930) 중간 기둥 뒤라 칸 밖. BASE 앞면 Y −1020(G2 끝).
    gap_mov = 89.22
    worst_d = max(c['simply_supported']['defl'] for c in cases)
    R['deflection_check'] = {'max_defl_ss': worst_d, 'nearest_moving_bbox_gap': gap_mov, 'gap_to_BASE_front': 720.0,
                             'ok': worst_d < gap_mov, 'note': '6-2 변위 한도 없음 → 동작 판정은 뒤 바디와의 틈으로만'}
    log('처짐 최대', worst_d, '↔ 움직이는 바디 틈', gap_mov)

    # 자중 ×3 g (판 면 안)
    sw = {}
    for n in ('C', 'L'):
        m = R['mass_model_kg'][n]
        w3 = m * 3 * g
        bb = geo[n]['bbox']
        L = bb[0][1] - bb[0][0]
        sig = w3 / (L * t)
        # 매달림: 판 위 둘레 볼트 줄(G4 두 줄, 피치 ≤ 300)만으로 매달 때 볼트 하나 몫
        nb = 2 * (math.ceil(L / 300.0) + 1)
        sw[n] = {'W3g_N': round(w3, 1), 'sigma_inplane': round(sig, 3), 'bolts_top_two_lines': nb, 'per_bolt_N': round(w3 / nb, 1)}
        log('자중×3g', n, round(w3, 1), 'N σ', round(sig, 3), '볼트 하나', round(w3 / nb, 1))
    R['self_weight'] = sw

    # 과사양(M-09): 지배 SF ≥ 필요 × 3 이면 과사양. t 1.5로 줄였을 때 SF
    gov = min((c for c in cases if c['load_case'].startswith('오조작 무릎')), key=lambda c: c['governing_sf'])
    sf15 = round(gov['governing_sf'] * (1.5 / t) ** 2, 2)
    R['oversize'] = {'governing_panel': gov['panel'], 'sf': gov['governing_sf'], 'limit_oversize': SF_MIS * 3,
                     'oversize': gov['governing_sf'] >= SF_MIS * 3, 'sf_if_t1_5': sf15}
    log('과사양', R['oversize'])

    R['problems_motion'] = [c for c in cases if c['governing_sf'] < SF_BREAK]
    R['problems_detail'] = [{'panel': c['panel'], 'case': c['load_case'], 'sf': c['governing_sf'], 'req': c['sf_req']}
                            for c in cases if SF_BREAK <= c['governing_sf'] < c['sf_req'] and not c['load_case'].startswith('민감도')]
    R['near_limit'] = [{'panel': c['panel'], 'case': c['load_case'], 'sf': c['governing_sf'], 'req': c['sf_req']} for c in cases if c['near']]
    R['pass'] = not R['problems_motion'] and R['deflection_check']['ok']
    log('pass', R['pass'], '동작', len(R['problems_motion']), '디테일', len(R['problems_detail']), '근처', len(R['near_limit']))
    json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(LOG, 'w', encoding='utf-8').write('\n'.join(_log) + '\n')


if __name__ == '__main__':
    main()
