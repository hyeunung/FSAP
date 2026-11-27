"""RGSEE: SolidCraft 0.50.0에서 깨져 열리는 FSAP_v2.30.5 복구 편집 목록 생성기(v2.30.5 -> v2.30.6, 형상 그대로).
tools/out/mech_RGSEE/design/fix050_gen.py + design/exp/p68gen.py를 한 파일로 합친 것이다(프로젝트 규칙 3).
입력: tools/out/mech_RGSEE/design/document_v2305.json(저장본 v2.30.5의 document.json), tools/out/mech_RGSEE/rebuild_0500_diff.json(0.50.0 오류 목록)
출력: <out>/fix050_stage_1_pipe.json ... fix050_stage_5_end.json, fix050_plan.json (기본 out = tools/out/mech_RGSEE/gen_fix050)
 1 관 경로 스케치 95775 맞춤점 14개(R 30 접선 호, p68 B안)  2 옮기기 from 132개  3 옮기기 3개 지움  4 둥글림 99556 다시 정의  5 마커 끝으로
돌리기: solidcraft-cli run(또는 헤드리스 세션 batch)으로 1 -> 5 순서. 편집 기록 전문은 tools/out/mech_RGSEE/edit.json.
usage: python -X utf8 -B tools/gen_fix050.py [out_dir]"""
import json, math, os, sys
T = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(T, 'out', 'mech_RGSEE', 'design')
H = sys.argv[1] if len(sys.argv) > 1 else os.path.join(T, 'out', 'mech_RGSEE', 'gen_fix050'); os.makedirs(H, exist_ok=True)
# ---- 관 경로(Pipe68, TU0604_M08P_U5_B) 접선 호 계산: design/exp/p68gen.py ----
def unit(v):
    n = math.sqrt(sum(x*x for x in v)); return [x/n for x in v]
def fillet(a, c, b, R):
    """corner c between a->c and c->b: return (start, through, end) of exact tangent arc radius R"""
    u1 = unit([c[i]-a[i] for i in range(3)]); u2 = unit([b[i]-c[i] for i in range(3)])
    cosang = sum(u1[i]*u2[i] for i in range(3)); th = math.acos(max(-1, min(1, cosang)))
    t = R*math.tan(th/2)
    s = [c[i]-u1[i]*t for i in range(3)]; e = [c[i]+u2[i]*t for i in range(3)]
    bis = unit([u2[i]-u1[i] for i in range(3)])
    cen = [c[i]+bis[i]*R/math.cos(th/2) for i in range(3)]
    m = [cen[i]-bis[i]*R for i in range(3)]
    return s, m, e, cen
def build(variant):
    segs = []
    P = lambda *a: [float(x) for x in a]
    x0 = 1060.25
    # exact R30 arcs
    k = 30*math.sqrt(0.5)
    a2 = (P(x0,63,650), P(x0,93-k,650+k), P(x0,93,680))
    a4 = (P(x0,152,680), P(1030.25+k,152+k,680), P(1030.25,182,680))
    a10 = (P(-1276,182,673), P(-1276-34*math.sqrt(0.5),216-34*math.sqrt(0.5),673), P(-1310,216,673))
    a11 = (P(-1310,216,673), P(-1276-34*math.sqrt(0.5),216+34*math.sqrt(0.5),673), P(-1276,250,673))
    o6 = (P(-959.63,182,680), P(-960,182,680), P(-960.37,182,679.99))
    o8 = (P(-1239.63,182,673.01), P(-1240,182,673), P(-1240.37,182,673))
    s6, m6, e6, _ = fillet(P(1030.25,182,680), P(-960,182,680), P(-1240,182,673), 30)
    s8, m8, e8, _ = fillet(P(-960,182,680), P(-1240,182,673), P(-1276,182,673), 30)
    o2 = (P(x0,63,650), P(x0,71.79,671.21), P(x0,93,680)); o4 = (P(x0,152,680), P(1051.46,173.21,680), P(1030.25,182,680))
    o10 = (P(-1276,182,673), P(-1300.04,191.96,673), P(-1310,216,673)); o11 = (P(-1310,216,673), P(-1300.04,240.04,673), P(-1276,250,673))
    big = variant in ('A','B','D','E'); tiny = variant in ('B','C','E')
    A2, A4, A10, A11 = (a2,a4,a10,a11) if big else (o2,o4,o10,o11)
    A6, A8 = ((s6,m6,e6),(s8,m8,e8)) if tiny else (o6,o8)
    segs.append(('L', P(x0,63,370.6), A2[0])); segs.append(('A',)+tuple(A2)); segs.append(('L', A2[2], A4[0])); segs.append(('A',)+tuple(A4))
    segs.append(('L', A4[2], A6[0]))
    if variant == 'D':   # no tiny arcs: straight corners
        segs[-1] = ('L', A4[2], P(-960,182,680)); segs.append(('L', P(-960,182,680), P(-1240,182,673))); segs.append(('L', P(-1240,182,673), A10[0]))
    else:
        segs.append(('A',)+tuple(A6)); segs.append(('L', A6[2], A8[0])); segs.append(('A',)+tuple(A8)); segs.append(('L', A8[2], A10[0]))
    if variant == 'E':   # one semicircle instead of two quarter arcs
        segs.append(('A', A10[0], A10[2], A11[2]))
    else:
        segs.append(('A',)+tuple(A10)); segs.append(('A',)+tuple(A11))
    segs.append(('L', A11[2], P(-1222.5,250,673)))
    return segs
def script(variant, name='SK_P68_'):
    segs = build(variant); cmds = [{'command': 'sketch.create3d', 'params': {'name': name+variant}}]
    for s in segs:
        if s[0] == 'L': cmds.append({'command': 'sketch.line3d', 'params': {'points': [s[1], s[2]]}})
        else: cmds.append({'command': 'sketch.arc3d', 'params': {'start': s[1], 'through': s[2], 'end': s[3]}})
    cmds.append({'command': 'sketch.finish', 'params': {}})
    return cmds, segs
# ---- 편집 목록: design/fix050_gen.py ----
d = json.load(open(os.path.join(D, 'document_v2305.json'), encoding='utf-8'))
F = d['features']; idx = {f['id']: i for i, f in enumerate(F)}
comp = {c['id']: c['name'] for c in d['components']}
errs = json.load(open(os.path.join(D, '..', 'rebuild_0500_diff.json'), encoding='utf-8'))['errors']
E = {e['id']: e['error'] for e in errs}
TAPE = {'TP_L': 76, 'TP_S': 91, 'TP_G': 106, 'TP_V': 95733}
# 0.50.0 규칙으로 바디가 든 컴포넌트를 따라간다: 나눈 조각은 원래 바디의 컴포넌트를 물려받는다.
where = {}
plan = {'edit_from': [], 'drop': [], 'cascade': [], 'other': []}
for i, f in enumerate(F):
    t = f.get('type')
    if t in ('box', 'extrude', 'cylinder', 'pipe', 'import') and f.get('operation', 'new_body') == 'new_body':
        for b in f.get('body_names', []): where.setdefault(b, f.get('component', 0))
    elif t == 'split':
        for b in f['body_names']: where[b] = where.get(f['body'], 0)
    elif t == 'body_transfer':
        for b in f['bodies']:
            if not b.startswith('TP_'):
                where[b] = f['to']; continue
            cur = where.get(b, 0)
            row = {'i': i, 'id': f['id'], 'name': f['name'], 'body': b, 'from_saved': f['from'], 'from_now': cur, 'to': f['to'], 'err': f['id'] in E}
            if cur == f['to']: plan['drop'].append(row)          # 이미 가 있을 컴포넌트 — 옮기기가 할 일이 없다
            elif cur != f['from']: plan['edit_from'].append(row)  # 출발 컴포넌트만 고친다
            elif f['id'] in E: plan['cascade'].append(row)        # 앞 옮기기가 풀리면 따라 풀린다
            where[b] = f['to']
for k in plan: print(k, len(plan[k]))
errset = set(e['id'] for e in errs if 'TP_' in e['error'])
covered = set(r['id'] for k in ('edit_from', 'drop', 'cascade') for r in plan[k])
print('TP errors', len(errset), 'covered', len(errset & covered), 'not covered', sorted(errset - covered), 'extra (no error now)', [r['name'] for k in ('edit_from', 'drop') for r in plan[k] if not r['err']])
json.dump(plan, open(os.path.join(H, 'fix050_plan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
# 단계 묶음
segs = build('B'); wires = F[idx[95775]]['sketch']['wires']; moves = []
for s, w in zip(segs, wires):
    new = [s[1], s[2]] if s[0] == 'L' else [s[1], s[2], s[3]]
    for k, (a, b) in enumerate(zip(new, w['fit'])):
        if max(abs(a[i] - b[i]) for i in range(3)) > 1e-9:
            moves.append({'command': 'sketch.move3d', 'params': {'wire': w['id'], 'index': k, 'to': [round(x, 9) for x in a]}})
C = lambda c, **p: {'command': c, 'params': p}
st1 = [C('timeline.roll_to', feature=95775), C('sketch.edit', sketch=95775, restore_marker=False)] + moves + [C('sketch.finish', restore_marker=False)]
st2 = [C('timeline.edit', feature=r['id'], set={'from': r['from_now']}) for r in plan['edit_from']]
st3 = [C('timeline.delete', features=[r['id'] for r in plan['drop']])]
st4 = [C('timeline.redefine', feature=99556, command='solid.fillet', params={'radius': '8', 'body': 'P_M08_PSW_BRKT', 'edges': [[1141.0, 70.0, 516.0], [1141.0, 120.0, 512.0]], 'name': 'RX01_PSW_BRKT_ROUT'})]
st5 = [C('timeline.roll_to', position='end')]
for n, s in (('1_pipe', st1), ('2_from', st2), ('3_drop', st3), ('4_rout', st4), ('5_end', st5)):
    json.dump(s, open(os.path.join(H, 'fix050_stage_%s.json' % n), 'w', encoding='utf-8'), ensure_ascii=False)
    print(n, len(s))
