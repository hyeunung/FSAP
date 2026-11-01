# -*- coding: utf-8 -*-
"""T12 옆·뒤 커버 — 판(SUS304 t2)·정비 문·형재 손계산 (해석부, 2026-11-01, 대상 v0.7.0).

해석 못 함 — 환경 없음(자료대기 D-16): engine/fea/.venv 없음(설치하지 않음). 표준 라이브러리 손계산.
얇은 판(t/L < 0.1)이라 엔진 handcalc.beam을 먼저 본다(E-18). 4변 받침 판이라 보 공식은 하한 비교로만,
판정은 Roark 표 11.4 1d(단순 지지, 가운데 작은 원 하중; Timoshenko β = 1 − γ1, 정사각 0.435 ~ 긴 띠 1.000).
입력 형상: 모델링부 임시 STEP 4개(tools/out/mech_T12/stepout/*.step). bbox·두께는 STEP VERTEX·PLANE에서 읽는다.
받침(형재 면) 위치는 mech_T12_model.md 4절 bbox와 bodies_standby.json(앞 기둥 1580_PR Y −1740~−1700):
  옆(X 1505 면): 앞 기둥 Y −1700, SPU/SPL Y −90~−10, 뒤 기둥 Q Y 900 / SLB 윗면 Z −600, SLM Z −220~−140, SLT 밑면 Z 820
  뒤(Y 940 면): D_R X 460~540, Q_R X 1425~1505 / BB 윗면 Z −600, BT 밑면 Z 820
  문: 4변 접힘 22(Y 920~942), 경첩 축 X −459.25(J_T12_DOOR), 경첩·걸쇠 형번 미정(새 D)
판 둘레는 형재 면에 볼트(아직 안 그림, 디테일) → 단순 지지(보수).

하중(요구서 6-1 비어 있음 → M-09, D-38 임시값):
  오조작: 무릎 200 N, 접촉 r0 50(민감도 r0 25), 칸 가운데, 판 면에 수직(기계 안쪽) — SF 2
  운전: 기댐 100 N(D-38 기둥 윗끝 기댐 값을 판에도) — SF 3
  자중 ×3 g: 판은 세워져 있어 판 면 안 — 무시할 크기(아래 계산)
  문: 자중(STEP 부피 × 7.93e-6) ×1·×3 g, 연 문 끝 기댐(수직) 200 N, 연 문 끝 옆 밀기 100 N(정지 자리에 따라)
단위 mm, N, MPa.  실행: python -X utf8 -B fea/cases/mech_T12_handcalc.py
결과: fea/results/mech_T12_handcalc.json
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ENGINE = os.environ.get('ENGINE_ROOT', os.path.join(os.path.dirname(ROOT), 'MechDesign_Engine'))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ENGINE, 'engine', 'tools'))
import handcalc  # noqa: E402  (읽기만)

STEPDIR = os.path.join(ROOT, 'tools', 'out', 'mech_T12', 'stepout')
OUT = os.path.join(ROOT, 'fea', 'results', 'mech_T12_handcalc.json')
g = 9.81
pi = math.pi
E, SY, NU, RHO = 193000.0, 205.0, 0.3, 7.93e-6
SF_OP, SF_MIS, SF_BREAK = 3.0, 2.0, 1.2

# Roark 표 11.4 1d (b = 짧은 변): β = 1 − γ1(Timoshenko), α 처짐
SS_B = [(1.0, 0.435), (1.2, 0.650), (1.4, 0.789), (1.6, 0.875), (1.8, 0.927), (2.0, 0.958), (1e9, 1.000)]
SS_A = [(1.0, 0.1267), (1.2, 0.1478), (1.4, 0.1621), (1.6, 0.1715), (1.8, 0.1770), (2.0, 0.1805), (1e9, 0.1851)]


def interp(tab, r):
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if r <= x1:
            if x1 > 1e8:
                return y0 + (y1 - y0) * min(1.0, (r - x0) / 2.0)
            return y0 + (y1 - y0) * (r - x0) / (x1 - x0)
    return tab[-1][1]


def read_step(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    ents = dict(re.findall(r'^#(\d+)\s*=\s*(.*);\s*$', txt, re.M))
    pts, dirs = {}, {}
    for k, v in ents.items():
        m = re.match(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", v)
        if m:
            pts[k] = tuple(float(x) for x in m.group(1).split(','))
        m = re.match(r"DIRECTION\('[^']*',\(([^)]*)\)\)", v)
        if m:
            dirs[k] = tuple(float(x) for x in m.group(1).split(','))
    verts = [pts[m.group(1)] for v in ents.values() for m in [re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", v)] if m]
    normals = {}
    for v in ents.values():
        m = re.match(r"PLANE\('[^']*',#(\d+)\)", v)
        if m:
            ax = re.match(r"AXIS2_PLACEMENT_3D\('[^']*',#(\d+),#(\d+),#(\d+)\)", ents[m.group(1)])
            o, n = pts[ax.group(1)], dirs[ax.group(2)]
            for i in range(3):
                if abs(abs(n[i]) - 1) < 1e-6:
                    normals.setdefault('XYZ'[i], set()).add(round(o[i], 3))
    bb = [(min(p[i] for p in verts), max(p[i] for p in verts)) for i in range(3)]
    return {'n_vert': len(verts), 'bbox': [[round(a, 3), round(b, 3)] for a, b in bb],
            'plane_levels': {k: sorted(v) for k, v in normals.items()}}


def plate(name, a, b, t, w, r0, sf_req, gap=None):
    a, b = max(a, b), min(a, b)
    r = a / b
    r0e = math.sqrt(1.6 * r0 ** 2 + t ** 2) - 0.675 * t if r0 < 0.5 * t else r0
    s = 3 * w / (2 * pi * t ** 2) * ((1 + NU) * math.log(2 * b / (pi * r0e)) + interp(SS_B, r))
    y = interp(SS_A, r) * w * b ** 2 / (E * t ** 3)
    sf = SY / s
    res = {'panel': name, 'a': a, 'b': b, 'a_b': round(r, 3), 't': t, 'W': w, 'r0': r0, 'sigma': round(s, 1),
           'sf': round(sf, 2), 'sf_req': sf_req, 'defl_linear': round(y, 1), 'defl_over_t': round(y / t, 1),
           'ok': sf >= sf_req, 'near': sf_req <= sf < 1.1 * sf_req, 'break': sf < SF_BREAK,
           'overspec': sf >= 3 * sf_req}
    if gap is not None:
        res['gap_to_moving'] = gap
        res['gap_after_defl'] = round(gap - y, 1)
        res['gap_band_25_100'] = 25 <= gap - y <= 100
    return res


def main():
    R = {'case': 'mech_T12_handcalc', 'target': 'FSAP_v0.7.0', 'fea': '해석 못 함 — 환경 없음(자료대기 D-16)',
         'material': {'name': 'SUS304', 'E': E, 'Sy': SY, 'nu': NU},
         'criteria': {'sf_op': SF_OP, 'sf_mis': SF_MIS, 'sf_break': SF_BREAK, 'source': '요구서 6-1 비어 있음 → M-09, D-38 임시'}}
    geo = {n: read_step(os.path.join(STEPDIR, 'P_T12_%s.step' % n)) for n in ('SU_RF', 'SL_RF', 'BK_R', 'DOOR')}
    R['step'] = geo
    for n, gg in geo.items():
        print('STEP', n, gg['bbox'])
    t = round(geo['SU_RF']['bbox'][0][1] - geo['SU_RF']['bbox'][0][0], 3)  # X 두께
    # 받침 사이 자유 칸(형재 면 기준)
    spans = {
        'SU_RF': (-90 - (-1700), 820 - (-140), 171.4),     # Y −1700~−90, Z −140~820, 바깥판 ↔ 홈매트(선정 측정)
        'SU_RR': (900 - (-10), 820 - (-140), 171.4),       # Y −10~900
        'SL_RF': (-90 - (-1700), -220 - (-600), 171.4),    # Y −1700~−90, Z −600~−220
        'SL_RR': (900 - (-10), -220 - (-600), 171.4),
        'BK_R': (1425 - 540, 820 - (-600), 329.0),         # X 540~1425, Z −600~820, 뒤판 ↔ 매트
    }
    P = []
    for n, (a, b, gap) in spans.items():
        P.append(plate(n + ' 무릎 200 N 오조작', a, b, t, 200.0, 50.0, SF_MIS, gap))
        P.append(plate(n + ' 무릎 200 N r0 25 민감도', a, b, t, 200.0, 25.0, SF_MIS, gap))
        P.append(plate(n + ' 기댐 100 N 운전', a, b, t, 100.0, 50.0, SF_OP, gap))
    # E-18: 보 하한 비교(짧은 변 띠, 폭 100, 양끝 단순 지지 → guided 근사 대신 외팔 반경간으로 보수)
    R['beam_check_SU'] = handcalc.beam(t=t, b=100.0, length=960 / 2, load=100.0, e=E, sy=SY, end='cantilever', sf_min=SF_MIS)
    # 문
    db = geo['DOOR']['bbox']
    W_d, H_d, D_f = db[0][1] - db[0][0], db[2][1] - db[2][0], db[1][1] - db[1][0]  # 917, 1417, 22
    vol_door = 2771205.45  # mech_T12_model.md 4절(판 + 접힘)
    G = vol_door * RHO * g
    P.append(plate('DOOR 판 무릎 200 N 오조작(접힘 안쪽, 단순 지지)', W_d - 4, H_d - 4, t, 200.0, 50.0, SF_MIS, 329.0))
    P.append(plate('DOOR 판 무릎 200 N r0 25 민감도', W_d - 4, H_d - 4, t, 200.0, 25.0, SF_MIS, 329.0))
    P.append(plate('DOOR 판 기댐 100 N 운전', W_d - 4, H_d - 4, t, 100.0, 50.0, SF_OP, 329.0))
    R['plates'] = P
    # 문 전체 굽힘 단면(폭 H_d 판 + 위·아래 접힘 2장, 깊이 D_f) — 경첩 변 ↔ 걸쇠 변 경간 W_d
    A_p, A_f = H_d * t, 2 * D_f * t
    yb = (A_p * t / 2 + A_f * D_f / 2) / (A_p + A_f)
    I = A_p * (t ** 2 / 12 + (yb - t / 2) ** 2) + 2 * (t * D_f ** 3 / 12) + A_f * (D_f / 2 - yb) ** 2
    c = D_f - yb
    door = {'mass_kg': round(vol_door * RHO, 2), 'weight_N': round(G, 1), 'I_section': round(I, 0), 'c': round(c, 2)}
    # 닫힌 문 가운데 무릎 200 N: 경첩 변·걸쇠 변 받침(문틀 기둥과 X 틈 1.5, 받침면 없음)
    M = 200 * W_d / 4
    s = M * c / I
    door['closed_knee_global'] = {'M': round(M), 'sigma': round(s, 1), 'sf': round(SY / s, 2), 'defl': round(200 * W_d ** 3 / (48 * E * I), 2),
                                  'latch_N': 100.0, 'hinge_each_N': 50.0}
    # 경첩 당김(경첩 간격 미정: 700·1200 두 값)
    arm = W_d / 2 + 0.75
    door['hinge_pull'] = {}
    for h in (700.0, 1200.0):
        door['hinge_pull']['h%d' % h] = {'self_1g': round(G * arm / h, 1), 'self_3g': round(3 * G * arm / h, 1),
                                         'open_lean200': round((G * arm + 200 * W_d) / h, 1)}
    # 연 문 끝 옆 밀기 100 N: 정지 자리에 따라 문 판 굽힘
    door['open_push'] = {}
    for name, xs in (('정지가 경첩 안(내장 정지)', 0.0), ('스테이 450', 450.0), ('스테이 600', 600.0), ('끝 받침 880', 880.0)):
        for F in (100.0, 200.0):
            Ml = F * (W_d - xs)
            sl = Ml * c / I
            door['open_push']['%s_%dN' % (name, F)] = {'M': round(Ml), 'sigma': round(sl, 1), 'sf': round(SY / sl, 2)}
    door['open_push50_defl_free'] = round(50 * W_d ** 3 / (3 * E * I), 2)
    R['door'] = door
    # 판 자중 ×3 g(판 면 안 압축/매달림): SU_RF 판 질량 28.96 kg, 단면 2 × 1691.5
    R['self_weight_3g_SU_RF'] = {'N': round(28.96 * 3 * g, 1), 'sigma_inplane': round(28.96 * 3 * g / (2 * 1691.5), 3)}
    # 형재 위 가로대 SLT(HFS8-4080, Al) 경간 1610, 가운데 기댐 100 N, 약축 I 가정(단면 상수 미확인 → 낮은 값 2개)
    beams = []
    for Ia in (2.0e5, 1.0e5):
        L = 1610.0
        Mb = 100 * L / 4
        sb = Mb * 20 / Ia
        beams.append({'name': 'SLT 가로대 약축 I=%g(가정)' % Ia, 'M': Mb, 'sigma': round(sb, 2), 'sf_6063T5_145': round(145 / sb, 1),
                      'defl': round(100 * L ** 3 / (48 * 69000 * Ia), 2)})
    R['beams'] = beams
    json.dump(R, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for p in P:
        print('%-40s σ %6.1f SF %5.2f / %.1f  처짐 %5.1f  틈후 %s %s' % (p['panel'], p['sigma'], p['sf'], p['sf_req'], p['defl_linear'],
              p.get('gap_after_defl'), 'NEAR' if p['near'] else ('OK' if p['ok'] else 'NG')))
    print('door', json.dumps(door, ensure_ascii=False))
    print('beam_check_SU', R['beam_check_SU']['sf'], 'beams', [b['sf_6063T5_145'] for b in beams])


if __name__ == '__main__':
    main()
