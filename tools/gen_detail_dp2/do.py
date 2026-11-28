"""DP-2 볼트 교체 실행기(헤드리스 세션 41050). usage: python -X utf8 -B do.py <stage>
단계마다 결과를 log_<stage>.json 에 남긴다. 실행한 명령은 cmds_<stage>.json (edit 기록)."""
import json, sys, q, os

def comps():
    u = q.call('cl_now', {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})
    return u['data']['components']

C = comps()
BYID = {c['id']: c for c in C}
BYNAME = {c['name']: c for c in C}
NAMES = set()
for c in C:
    NAMES.add(c['name']); NAMES.update(c['bodies'])
REC = []

def run(tag, cmds, verbose=True):
    REC.extend(cmds)
    u = q.call(tag, {'commands': cmds, 'rollback': True, 'verbose': verbose})
    d = u['data']
    if u.get('isError') or isinstance(d, str) or not d.get('ok'):
        print('FAIL', tag, json.dumps(d, ensure_ascii=False)[:1500] if not isinstance(d, str) else d[:1500])
        json.dump(REC, open('cmds_FAILED_%s.json' % tag, 'w', encoding='utf-8'), ensure_ascii=False)
        sys.exit(2)
    return d['results']

def tm(T):
    X, Y, Z, P = T[0][:3], T[1][:3], T[2][:3], T[3][:3]
    return [X[0], Y[0], Z[0], P[0], X[1], Y[1], Z[1], P[1], X[2], Y[2], Z[2], P[2]]

IDENT = [[1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]]

def chain(comp_id):
    """root 쪽부터 [(occ id, occ name)] — 부모 컴포넌트가 한 번만 놓였다고 본다(확인됨)"""
    out = []
    cid = comp_id
    while cid != 0:
        c = BYID[cid]
        assert len(c['occurrences']) == 1, c['name']
        o = c['occurrences'][0]; out.append((o['id'], o['name'], o.get('transform'))); cid = c['parent']
    return out[::-1]

def props(occ_ids):
    r = run('props', [{'command': 'occurrence.properties', 'params': {'occurrence': i}} for i in occ_ids])
    REC[:] = REC[:-len(occ_ids)]  # 읽기 명령은 기록에서 뺀다
    return [dict(name=x['name'], bbox=x['total']['bbox'], bodies=[(b['name'], round(b['volume_mm3'], 3), b['material']) for b in x['bodies']]) for x in r]

def check(before, after, what):
    """머리 쪽은 그대로, 한 축으로만 길어졌는지(자리 확인)"""
    for b, a in zip(before, after):
        bm, bM, am, aM = b['bbox']['min'], b['bbox']['max'], a['bbox']['min'], a['bbox']['max']
        d = [round(am[i] - bm[i], 3) for i in range(3)] + [round(aM[i] - bM[i], 3) for i in range(3)]
        nz = [x for x in d if abs(x) > 0.02]
        if len(nz) != 1:
            print('CHECK FAIL', what, b['name'], d); json.dump(REC, open('cmds_CHECKFAIL.json', 'w', encoding='utf-8'), ensure_ascii=False); sys.exit(3)

def unique(n):
    return n if n not in NAMES else n + '_DP2'

def swap_real(compname, newspec, dp2comp, dp2body, desc, src_occ=None, seat=None):
    """컴포넌트의 모든 occurrence가 같은 실물 STEP 형번으로 바뀔 때: 바디만 바꿔 끼운다(occurrence · 조인트 그대로)"""
    c = BYNAME[compname]; o1 = c['occurrences'][0]; P = BYID[c['parent']] if c['parent'] else None
    before = props([o['id'] for o in c['occurrences']])
    ch = chain(c['parent'])
    if src_occ is None:
        r = run('sw_copy', [{'command': 'occurrence.copy', 'params': {'component': dp2comp, 'parent': P['name']}}])
        tmp = r[0]['occurrence']
        r = run('sw_move', [{'command': 'occurrence.move', 'params': {'occurrence': tmp, 'space': 'local', 'to_matrix': seat or tm(o1.get('transform') or IDENT)}}])
        pn = props([tmp])[0]['name']
        disp = '%s (%s/%s)' % (dp2body, '/'.join(x[1] for x in ch), pn)
    else:
        tmp = None; disp = dp2body
    newname = unique('%s_%s' % (newspec, compname.split('_', 1)[1]))
    r = run('sw_cb', [{'command': 'component.copy_bodies', 'params': {'bodies': [disp], 'component': c['id'], 'component_path': [x[0] for x in ch] + [o1['id']]}}])
    nb = r[0]['bodies'][0]
    cmds = [{'command': 'solid.remove', 'params': {'bodies': [c['bodies'][0]]}},
            {'command': 'body.rename', 'params': {'body': nb, 'name': newname}},
            {'command': 'component.rename', 'params': {'component': c['id'], 'name': newname}},
            {'command': 'component.metadata.set', 'params': {'component': c['id'], 'part_number': newspec, 'description': desc}}]
    if tmp is not None:
        cmds.append({'command': 'selection.delete', 'params': {'occurrences': [tmp]}})
    run('sw_fin', cmds, verbose=False)
    NAMES.add(newname)
    after = props([o['id'] for o in c['occurrences']])
    check(before, after, compname)
    return dict(kind='swap_real', comp=compname, new=newname, spec=newspec, occ=[o['id'] for o in c['occurrences']], before=before, after=after)

def extend(compname, newname, newspec, base_off, height, desc, feat):
    """임시 형상: 받은 STEP 바디의 생크를 축 방향으로 늘린다(컴포넌트 정의 하나, occurrence 전부 함께)"""
    c = BYNAME[compname]; o1 = c['occurrences'][0]
    assert all(x[2] is None for x in chain(c['parent'])), 'parent not identity'
    T = o1.get('transform') or IDENT
    X, Pp = T[0][:3], T[3][:3]
    base = [Pp[i] + X[i] * base_off for i in range(3)]
    before = props([o['id'] for o in c['occurrences']])
    cmds = [{'command': 'component.activate', 'params': {'component': c['id'], 'occurrence': o1['id']}},
            {'command': 'solid.cylinder', 'params': {'radius': 2.5, 'height': height, 'base': base, 'axis': X, 'operation': 'join', 'targets': [c['bodies'][0]], 'name': feat}},
            {'command': 'component.activate', 'params': {'component': 'root'}}]
    run('ext_a', cmds, verbose=False)
    return rename_temp(c, newname, newspec, desc, before)

def rename_temp(c, newname, newspec, desc, before):
    cmds = [{'command': 'body.rename', 'params': {'body': c['bodies'][0], 'name': newname}},
            {'command': 'component.rename', 'params': {'component': c['id'], 'name': newname}},
            {'command': 'component.metadata.set', 'params': {'component': c['id'], 'part_number': newspec, 'description': desc}}]
    run('ext_b', cmds, verbose=False)
    NAMES.add(newname)
    after = props([o['id'] for o in c['occurrences']])
    return dict(kind='extend', comp=c['name'], new=newname, spec=newspec, occ=[o['id'] for o in c['occurrences']], before=before, after=after)

JL = None
def joints_of(occ_id):
    global JL
    if JL is None:
        JL = q.unwrap('r_jlist.json')['data']['joints']
    return [j for j in JL if j['b'] == occ_id or j['a'] == occ_id]

def replace_occ(targets, dp2comp, first_occ=None):
    """occurrence 일부만 바뀔 때: 새 형번 컴포넌트의 occurrence를 같은 부모 · 같은 자리(local 행렬)에 놓고 옛 것을 지운다"""
    out = []
    before = props([t['occ_id'] for t in targets])
    new_ids = []
    cp = []
    for i, t in enumerate(targets):
        if i == 0 and first_occ is not None:
            new_ids.append(first_occ); continue
        cp.append({'command': 'occurrence.copy', 'params': {'component': dp2comp, 'parent': t['parent_name']}})
    if cp:
        r = run('rp_copy', cp)
        new_ids += [x['occurrence'] for x in r]
    mv = [{'command': 'occurrence.move', 'params': {'occurrence': n, 'space': 'local', 'to_matrix': tm(t['transform'] or IDENT)}} for n, t in zip(new_ids, targets)]
    run('rp_move', mv, verbose=False)
    jc = []
    for n, t in zip(new_ids, targets):
        for j in joints_of(t['occ_id']):
            other = j['a'] if j['b'] == t['occ_id'] else j['b']
            assert j['type'] == 'rigid'
            jc.append({'command': 'joint.rigid_group', 'params': {'occurrences': [other, n]}})
    if jc: run('rp_joint', jc, verbose=False)
    run('rp_del', [{'command': 'selection.delete', 'params': {'occurrences': [t['occ_id'] for t in targets]}}], verbose=False)
    after = props(new_ids)
    check(before, after, dp2comp)
    for t, n, b, a in zip(targets, new_ids, before, after):
        out.append(dict(kind='replace', key=t['key'], old_occ=t['occ_id'], new_occ=n, parent=t['parent_name'], old=t['old'], new=t['new'], before=b, after=a, joints=len(joints_of(t['occ_id']))))
    return out

T = json.load(open('targets.json', encoding='utf-8'))
def tg(comp, new):
    return [t for t in T if t['comp'] == comp and t['new'] == new]

stage = sys.argv[1]
LOG = []
if stage == 'A':   # 실물 CB5-16 제자리 교체: PY(이미 바디 복사됨) + PX는 뒤에, 허브 2 · 핀 2
    c = BYNAME['CB5-12_M08_PY']
    before = None
    newname = unique('CB5-16_M08_PY')
    run('A1', [{'command': 'solid.remove', 'params': {'bodies': ['CB5-12_M08_PY']}},
               {'command': 'body.rename', 'params': {'body': 'CB5-16_DP2 (2)', 'name': newname}},
               {'command': 'component.rename', 'params': {'component': c['id'], 'name': newname}},
               {'command': 'component.metadata.set', 'params': {'component': c['id'], 'part_number': 'CB5-16', 'description': 'Misumi CB5-16 STEP (DP-2: CB5-12 -> CB5-16, T-nut engagement 5.5 -> 9.0)'}}], verbose=False)
    NAMES.add(newname)
    LOG.append(dict(kind='swap_real', comp='CB5-12_M08_PY', new=newname, spec='CB5-16', occ=[o['id'] for o in c['occurrences']], after=props([o['id'] for o in c['occurrences']])))
    for cn, d in (('CB5-12_M02_HUB', 'Misumi CB5-16 STEP (DP-2: hub bolt CB5-12 -> CB5-16, shaft tap engagement 4.75 -> 8.75)'),
                  ('CB5-12_M03_HUB', 'Misumi CB5-16 STEP (DP-2: hub bolt CB5-12 -> CB5-16, shaft tap engagement 4.75 -> 8.75)'),
                  ('CB5-12_M06_9', 'Misumi CB5-16 STEP (DP-2: roll pin bolt CB5-12 -> CB5-16, engagement 6 -> 10)'),
                  ('CB5-12_M06_10', 'Misumi CB5-16 STEP (DP-2: roll pin bolt CB5-12 -> CB5-16, engagement 6 -> 10)')):
        LOG.append(swap_real(cn, 'CB5-16', 'CB5-16_DP2', 'CB5-16_DP2', d))
elif stage == 'A2':  # 롤 핀 볼트 2: 옛 컴포넌트 좌표가 표준 자리(머리 밑 원점)가 아니라 자리 행렬을 직접 준다(머리 밑 (1312, 7.5, z), 넣는 방향 -Y)
    for cn, z in (('CB5-12_M06_9', 15.0), ('CB5-12_M06_10', 681.0)):
        LOG.append(swap_real(cn, 'CB5-16', 'CB5-16_DP2', 'CB5-16_DP2', 'Misumi CB5-16 STEP (DP-2: roll pin bolt CB5-12 -> CB5-16, engagement 6 -> 10)', seat=[0, 1, 0, 1312.0, -1, 0, 0, 7.5, 0, 0, 1, z]))
elif stage == 'B':  # 임시 형상(받은 STEP 생크 늘림): SFB5-16 · CB5-22 · CB5-14(전부 바뀌는 컴포넌트)
    c = BYNAME['SFB5-10_M04']   # 생크는 이미 늘렸다(DP2_SFB5-16_M04_EXT)
    LOG.append(rename_temp(c, 'STEP대기_SFB5-16_M04', 'SFB5-16', 'TEMP shape (STEP wait): Misumi SFB5-10 STEP with shank extended to L16 (JIS B 1194 M5x16). DP-2: T-nut engagement 3.5 -> 9.0', None))
    LOG.append(extend('SFB5-10_M04R', 'STEP대기_SFB5-16_M04R', 'SFB5-16', 6.2, 7.0, 'TEMP shape (STEP wait): Misumi SFB5-10 STEP with shank extended to L16 (JIS B 1194 M5x16). DP-2: T-nut engagement 3.5 -> 9.0', 'DP2_SFB5-16_M04R_EXT'))
    LOG.append(extend('CB5-20_M04R', 'STEP대기_CB5-22_M04R', 'CB5-22', 19.0, 3.0, 'TEMP shape (STEP wait): Misumi CB5-20 STEP with shank extended to L22 (JIS B 1176 M5x22). DP-2: T-nut engagement 5.5 -> 7.5', 'DP2_CB5-22_M04R_EXT'))
    for cn in ('CB5-12_M08_PX_LC', 'CB5-12_M08_NX_LC'):
        LOG.append(extend(cn, 'STEP대기_CB5-14_' + cn.split('_', 1)[1], 'CB5-14', 11.0, 3.0, 'TEMP shape (STEP wait): Misumi CB5-12 STEP with shank extended to L14 (JIS B 1176 M5x14). DP-2: T-nut engagement 6.25~6.5 -> 8.25~8.5', 'DP2_CB5-14_' + cn.split('_', 1)[1] + '_EXT'))
elif stage == 'C':  # 섞인 컴포넌트: CB5-16_DP2 occurrence로 바꿈(M03_3 36 · RX14 2)
    LOG += replace_occ(tg('CB5-12_M03_3', 'CB5-16'), 'CB5-16_DP2')
    LOG += replace_occ(tg('CB5-12_RX14', 'CB5-16'), 'CB5-16_DP2')
elif stage == 'C2':  # M03_3 :42~45 (나사 구간 6.5~15.5) → CB5-16
    done = {L['key'] for L in json.load(open('log_C.json', encoding='utf-8'))}
    LOG += replace_occ([t for t in tg('CB5-12_M03_3', 'CB5-16') if t['key'] not in done], 'CB5-16_DP2')
elif stage == 'D':  # CB5-14 임시 형상 새 컴포넌트(M03_3 4 · M08_PX 2) → 그다음 M08_PX 8은 제자리 교체
    t14 = tg('CB5-12_M03_3', 'CB5-14') + tg('CB5-12_M08_PX', 'CB5-14')
    r = run('D_paste', [{'command': 'component.paste_new', 'params': {'component': BYNAME['CB5-12_M03_3']['id'], 'parent': 'U2_FLAP_MOUNT'}}])
    cid, oid, fid = r[0]['component'], r[0]['occurrence'], r[0]['features'][0]
    C2 = comps(); nb = [c for c in C2 if c['id'] == cid][0]['bodies'][0]
    run('D_name', [{'command': 'component.rename', 'params': {'component': cid, 'name': 'STEP대기_CB5-14_DP2'}},
                   {'command': 'body.rename', 'params': {'body': nb, 'name': 'STEP대기_CB5-14_DP2'}},
                   {'command': 'timeline.rename', 'params': {'feature': fid, 'name': 'STEP대기_CB5-14_DP2'}},
                   {'command': 'component.metadata.set', 'params': {'component': cid, 'part_number': 'CB5-14', 'description': 'TEMP shape (STEP wait): Misumi CB5-12 STEP with shank extended to L14 (JIS B 1176 M5x14). DP-2: T-nut engagement 6.25~6.5 -> 8.25~8.5'}},
                   {'command': 'occurrence.move', 'params': {'occurrence': oid, 'space': 'local', 'to_matrix': tm(t14[0]['transform'])}}], verbose=False)
    Tm = t14[0]['transform']; X, Pp = Tm[0][:3], Tm[3][:3]
    run('D_ext', [{'command': 'component.activate', 'params': {'component': cid, 'occurrence': oid}},
                  {'command': 'solid.cylinder', 'params': {'radius': 2.5, 'height': 3.0, 'base': [Pp[i] + X[i] * 11.0 for i in range(3)], 'axis': X, 'operation': 'join', 'targets': ['STEP대기_CB5-14_DP2'], 'name': 'DP2_CB5-14_DP2_EXT'}},
                  {'command': 'component.activate', 'params': {'component': 'root'}}], verbose=False)
    LOG += replace_occ(t14, 'STEP대기_CB5-14_DP2', first_occ=oid)
    C[:] = comps(); BYID.update({c['id']: c for c in C}); BYNAME.clear(); BYNAME.update({c['name']: c for c in C})
    LOG.append(swap_real('CB5-12_M08_PX', 'CB5-16', 'CB5-16_DP2', 'CB5-16_DP2', 'Misumi CB5-16 STEP (DP-2: CB5-12 -> CB5-16, T-nut engagement 3.5~5.5 -> 7.5~9.0)'))
elif stage == 'E':  # CB5-20: M04K_NY 6(새 occurrence) · U3_BRKT 4(제자리)
    t20 = tg('CB5-16_M04K_NY', 'CB5-20')
    r = run('E_paste', [{'command': 'component.paste_new', 'params': {'component': BYNAME['CB5-20_M07_NX']['id'], 'parent': 'U2_FLAP_MOUNT'}}])
    cid, oid, fid = r[0]['component'], r[0]['occurrence'], r[0]['features'][0]
    C2 = comps(); nb = [c for c in C2 if c['id'] == cid][0]['bodies'][0]
    run('E_name', [{'command': 'component.rename', 'params': {'component': cid, 'name': 'CB5-20_DP2'}},
                   {'command': 'body.rename', 'params': {'body': nb, 'name': 'CB5-20_DP2'}},
                   {'command': 'timeline.rename', 'params': {'feature': fid, 'name': 'CB5-20_DP2'}},
                   {'command': 'component.metadata.set', 'params': {'component': cid, 'part_number': 'CB5-20', 'description': 'Misumi CB5-20 STEP (DP-2 detailing: CB5-16 -> CB5-20, T-nut engagement 5.5 -> 9.0)'}}], verbose=False)
    LOG += replace_occ(t20, 'CB5-20_DP2', first_occ=oid)
    C[:] = comps(); BYID.update({c['id']: c for c in C}); BYNAME.clear(); BYNAME.update({c['name']: c for c in C})
    LOG.append(swap_real('CB5-16_U3_BRKT', 'CB5-20', 'CB5-20_DP2', 'CB5-20_DP2', 'Misumi CB5-20 STEP (DP-2: CB5-16 -> CB5-20, T-nut engagement 5.0 -> 9.0)'))
json.dump(LOG, open('log_%s.json' % stage, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(REC, open('cmds_%s.json' % stage, 'w', encoding='utf-8'), ensure_ascii=False)
for L in LOG:
    if L['kind'] == 'replace':
        print('replace', L['key'][:50], L['old'], '->', L['new'], 'bbox', [round(v, 2) for v in L['before']['bbox']['min'] + L['before']['bbox']['max']], '->', [round(v, 2) for v in L['after']['bbox']['min'] + L['after']['bbox']['max']], L['after']['bodies'][0][:2])
    else:
        b = L.get('before'); a = L['after']
        print(L['kind'], L['comp'], '->', L['new'], len(L['occ']), 'occ; first bbox', ([round(v, 2) for v in b[0]['bbox']['min'] + b[0]['bbox']['max']] if b else None), '->', [round(v, 2) for v in a[0]['bbox']['min'] + a[0]['bbox']['max']], a[0]['bodies'])
