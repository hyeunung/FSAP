"""DP-3 볼트 교체. usage: bolts.py comb | hmi | lbrk | cb4
 comb: CB5-16_M08_NZ_COMB 11 -> CB5-20(컴포넌트 바디를 실물 CB5-20 으로, occurrence · 조인트 그대로)
 hmi : CB5-16_M08_PY:4~7 -> CB5-20_DP2 occurrence(같은 부모 · 같은 자리)
 lbrk: CB5-16_M08_PY:3 -> STEP대기_CB5-14_DP2 occurrence
 cb4 : CB4-25_M08 4 -> STEP대기_CB4-30_M08(받은 CB4-25 STEP 생크를 5 늘림)"""
import json, sys, q


def C(command, **params):
    return {'command': command, 'params': params}


REC = []


def run(tag, cmds, verbose=True, rec=True):
    if rec:
        REC.extend(cmds)
    u = q.call(tag, {'commands': cmds, 'rollback': True, 'verbose': verbose})
    d = u['data']
    if u.get('isError') or isinstance(d, str) or not d.get('ok'):
        print('FAIL', tag, json.dumps(d, ensure_ascii=False)[:2000])
        json.dump(REC, open('cmds_FAILED_%s.json' % tag, 'w', encoding='utf-8'), ensure_ascii=False)
        sys.exit(2)
    return d['results']


def comps():
    return q.call('cl_now', {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})['data']['components']


Cs = comps()
BYID = {c['id']: c for c in Cs}
BYNAME = {c['name']: c for c in Cs}
IDENT = [[1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]]


def tm(T):
    X, Y, Z, P = T[0][:3], T[1][:3], T[2][:3], T[3][:3]
    return [X[0], Y[0], Z[0], P[0], X[1], Y[1], Z[1], P[1], X[2], Y[2], Z[2], P[2]]


def props(ids):
    r = run('props', [C('occurrence.properties', occurrence=i) for i in ids], rec=False)
    return [dict(name=x['name'], bbox=[round(v, 3) for v in x['total']['bbox']['min'] + x['total']['bbox']['max']],
                 bodies=[(b['name'], round(b['volume_mm3'], 3), b['material']) for b in x['bodies']]) for x in r]


JL = q.unwrap('r_jlist.json')['data']['joints']


def joints_of(i):
    return [j for j in JL if j['a'] == i or j['b'] == i]


def chain(cid):
    out = []
    while cid != 0:
        c = BYID[cid]
        assert len(c['occurrences']) == 1, c['name']
        o = c['occurrences'][0]
        out.append((o['id'], o['name']))
        cid = c['parent']
    return out[::-1]


def replace_occ(occ_ids, srccomp, tag):
    """occurrence 일부만 바뀔 때: 새 형번 컴포넌트의 occurrence를 같은 부모 · 같은 자리에 놓고 옛 것을 지운다"""
    occs = {o['id']: (o, c) for c in Cs for o in c['occurrences']}
    T = [occs[i] for i in occ_ids]
    before = props(occ_ids)
    r = run(tag + '_copy', [C('occurrence.copy', component=srccomp, parent=BYID[o['parent']]['name']) for o, c in T])
    new = [x['occurrence'] for x in r]
    run(tag + '_move', [C('occurrence.move', occurrence=n, space='local', to_matrix=tm(o.get('transform') or IDENT)) for n, (o, c) in zip(new, T)], verbose=False)
    jc = []
    for n, i in zip(new, occ_ids):
        for j in joints_of(i):
            other = j['a'] if j['b'] == i else j['b']
            assert j['type'] == 'rigid'
            jc.append(C('joint.rigid_group', occurrences=[other, n]))
    if jc:
        run(tag + '_joint', jc, verbose=False)
    run(tag + '_del', [C('selection.delete', occurrences=occ_ids)], verbose=False)
    after = props(new)
    for b, a in zip(before, after):
        print(b['name'], b['bbox'], '->', a['name'], a['bbox'], a['bodies'])
    return dict(old=occ_ids, new=new, before=before, after=after, joints=len(jc))


st = sys.argv[1]
out = {}
if st == 'comb':
    c = BYNAME['CB5-16_M08_NZ_COMB']
    o1 = c['occurrences'][0]
    P = BYID[c['parent']]
    ids = [o['id'] for o in c['occurrences']]
    before = props(ids)
    src = BYNAME['CB5-20_DP2']
    r = run('cb_copy', [C('occurrence.copy', component='CB5-20_DP2', parent=P['name'])])
    tmp = r[0]['occurrence']
    run('cb_move', [C('occurrence.move', occurrence=tmp, space='local', to_matrix=tm(o1['transform']))], verbose=False)
    pn = props([tmp])[0]['name']
    ch = chain(c['parent'])
    disp = '%s (%s/%s)' % (src['bodies'][0], '/'.join(x[1] for x in ch), pn)
    r = run('cb_cb', [C('component.copy_bodies', bodies=[disp], component=c['id'], component_path=[x[0] for x in ch] + [o1['id']])])
    nb = r[0]['bodies'][0]
    print('copied body', nb)
    run('cb_fin', [C('solid.remove', bodies=[c['bodies'][0]]), C('body.rename', body=nb, name='CB5-20_M08_NZ_COMB'),
                   C('component.rename', component=c['id'], name='CB5-20_M08_NZ_COMB'),
                   C('component.metadata.set', component=c['id'], part_number='CB5-20', description='MISUMI CB5-20 hex socket head cap screw M5x20 (real STEP) - tube comb -> beam top wall t8 M5 through tap, full engagement 8 (DP-3, was CB5-16)'),
                   C('selection.delete', occurrences=[tmp])], verbose=False)
    after = props(ids)
    for b, a in zip(before, after):
        print(b['name'], b['bbox'], '->', a['name'], a['bbox'], a['bodies'])
    out = dict(kind='swap_real', occ=ids, before=before, after=after)
elif st == 'hmi':
    c = BYNAME['CB5-16_M08_PY']
    ids = [o['id'] for o in c['occurrences'] if o['name'] in ('CB5-16_M08_PY:4', 'CB5-16_M08_PY:5', 'CB5-16_M08_PY:6', 'CB5-16_M08_PY:7')]
    assert len(ids) == 4
    out = replace_occ(ids, 'CB5-20_DP2', 'hmi')
elif st == 'lbrk':
    c = BYNAME['CB5-16_M08_PY']
    ids = [o['id'] for o in c['occurrences'] if o['name'] == 'CB5-16_M08_PY:3']
    assert len(ids) == 1
    out = replace_occ(ids, 'STEP대기_CB5-14_DP2', 'lbrk')
elif st == 'cb4':
    c = BYNAME['CB4-25_M08']
    o1 = c['occurrences'][0]
    ids = [o['id'] for o in c['occurrences']]
    before = props(ids)
    T = o1['transform']
    X, Pp = T[0][:3], T[3][:3]
    base = [Pp[i] + X[i] * 25 for i in range(3)]
    run('cb4_a', [C('component.activate', component=c['id'], occurrence=o1['id']),
                  C('solid.cylinder', radius=2.0, height=5, base=base, axis=X, operation='join', targets=[c['bodies'][0]], name='DP3_CB4-30_SHANK_EXT'),
                  C('component.activate', component='root')], verbose=False)
    run('cb4_b', [C('body.rename', body=c['bodies'][0], name='STEP대기_CB4-30_M08'), C('component.rename', component=c['id'], name='STEP대기_CB4-30_M08'),
                  C('component.metadata.set', component=c['id'], part_number='CB4-30', description='TEMP shape for MISUMI CB4-30 (M4x30): received CB4-25 STEP with shank extended 5 mm, STEP not received (waiting-list). Solenoid manifold -> beam front wall t8 M4 through tap, full engagement 8 (DP-3, was CB4-25)')], verbose=False)
    after = props(ids)
    for b, a in zip(before, after):
        print(b['name'], b['bbox'], '->', a['name'], a['bbox'], a['bodies'])
    out = dict(kind='extend', occ=ids, before=before, after=after)
json.dump(REC, open('cmds_D_%s.json' % st, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(out, open('D_%s.json' % st, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
