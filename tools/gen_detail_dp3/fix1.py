"""DP-3 수정 1회차(v2.31.0 -> v2.31.1) 실행기 - 헤드리스 세션 41081. usage(작업 폴더 tools/out/detail/DP-3/m1 에서):
    python -X utf8 -B ../../../../gen_detail_dp3/fix1.py <stage>
stage: pre | beam | bolts | meta
 pre  : 체크포인트 · 대기 자세 · 고치기 전 측정 · 빈 탭 둘레 광선(쓰는 부품 유무)
 beam : 뒷벽 탭 2개 다시 뚫음(옛 끝 자리 채움 상자가 1 mm 막은 것) + 빈 탭 6개 메움
 bolts: 덮개 볼트 CB5-12_M07_CAP x8 -> CB5-16_M07_CAP(실물 STEP, 컴포넌트 바디를 바꿔 끼움 - occurrence · 조인트 그대로)
 meta : 덮개 컴포넌트 설명(조임 토크 · 예외 번호)
단계마다 보낸 명령을 cmds_<stage>.json(편집 기록), 결과를 r_<tag>.json 에 남긴다."""
import json, sys, math, q
q.ask.__defaults__ = (470, 41081)   # 이 회차의 세션 포트
import os


def _call(name, req, timeout=470):
    """결과 파일을 작업 폴더(절대 경로)에 남긴다 - 세션 일꾼의 작업 폴더가 다르다"""
    req = dict(req)
    req['save'] = os.path.abspath('r_%s.json' % name).replace(os.sep, '/')
    q.ask(req, timeout)
    return q.unwrap(req['save'])


q.call = _call

REC = []


def C(command, **params):
    return {'command': command, 'params': params}


def run(tag, cmds, verbose=False, rollback=True, rec=True):
    if rec:
        REC.extend(cmds)
    u = q.call(tag, {'commands': cmds, 'rollback': rollback, 'verbose': verbose})
    d = u.get('data')
    if u.get('isError') or isinstance(d, str) or not d or not d.get('ok'):
        print('FAIL', tag, (json.dumps(d, ensure_ascii=False) if not isinstance(d, str) else d)[:2500])
        json.dump(REC, open('cmds_FAILED_%s.json' % tag, 'w', encoding='utf-8'), ensure_ascii=False)
        sys.exit(2)
    print('ok', tag, len(cmds), 'cmds', '%.1f s' % u['s'])
    return d['results']


def ex(tag, command, params, timeout=470):
    u = q.call(tag, {'tool': 'execute', 'arguments': {'command': command, 'params': params}}, timeout=timeout)
    return u


def meas(names, tag='meas'):
    out = {}
    for n in names:
        u = q.call(tag, {'tool': 'measure', 'arguments': {'body': n}})
        d = u['data']
        b = [x for x in d['bodies'] if x['name'] == n]
        b = b[0] if b else d['bodies'][0]
        out[n] = dict(name=b['name'], volume=round(b['volume_mm3'], 3), bbox=[round(v, 3) for v in b['bbox']['min'] + b['bbox']['max']], material=b.get('material'), mass=round(b.get('mass_g', 0), 3), shells=b.get('kernel', {}).get('shells'), faces=b.get('faces'), closed=b.get('closed'))
    return out


BEAM = 'P_M07_BEAM'


def cyl(name, tgt, r, base, axis, h, op='cut'):
    return C('solid.cylinder', radius=r, height=h, base=base, axis=axis, operation=op, targets=[tgt], name=name)


# ---- 자리 ----
REOPEN = [(1230.0, 300.0), (1230.0, 600.0)]            # 뒷벽 Y 312~320, 볼트 CB5-16_M07_NY:7 · :8
FILL_NZ = [(-310.0, 140.0), (-310.0, 180.0), (-160.0, 140.0), (-160.0, 180.0)]   # 아랫벽 Z 250~258 (옛 Cylinder31~34)
FILL_NY = [(-256.0, 276.0), (-244.0, 276.0)]           # 앞벽 Y 120~128 (관 클램프 L_6의 옛 자리)


def stage_pre():
    u = ex('ckpt', 'edit.checkpoint', {})
    print('checkpoint', json.dumps(u.get('data'), ensure_ascii=False)[:200])
    u = ex('rest', 'motion.play', {'study': 'REST', 'step': 0})
    print('rest', json.dumps(u.get('data'), ensure_ascii=False)[:300])
    rays = []
    tags = []
    for x, y in FILL_NZ:
        for dx, dy in ((0, 0), (4, 0), (-4, 0), (0, 4), (0, -4)):
            rays.append({'origin': [x + dx, y + dy, 100], 'dir': [0, 0, 1]})
            tags.append('botTap(%g,%g)+(%g,%g)' % (x, y, dx, dy))
    for x, z in FILL_NY:
        for dx, dz in ((0, 0), (0, 4), (0, -3.5)):
            rays.append({'origin': [x + dx, -100, z + dz], 'dir': [0, 1, 0]})
            tags.append('frontTap(%g,%g)+(%g,%g)' % (x, z, dx, dz))
    # 덮개 볼트 끝 앞(보 속): 볼트 끝에서 안쪽으로
    for x in (-2362.0, 1332.0):
        for z in (350.0, 550.0):
            rays.append({'origin': [x, 132.5, z], 'dir': [0, 1, 0]})
            tags.append('capTipF(%g,%g)' % (x, z))
            rays.append({'origin': [x, 307.5, z], 'dir': [0, -1, 0]})
            tags.append('capTipB(%g,%g)' % (x, z))
    u = ex('pick_pre', 'view.pick', {'rays': rays})
    hs = u['data'].get('hits', u['data']) if isinstance(u['data'], dict) else u['data']
    out = []
    for t, r, h in zip(tags, rays, hs):
        row = dict(tag=t, origin=r['origin'], dir=r['dir'], body=(h and h.get('body')), point=(h and [round(c, 3) for c in h['point']]))
        out.append(row)
        print(t, r['origin'], '->', row['body'], row['point'])
    json.dump(out, open('pre_rays.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    names = [BEAM, 'P_M07_BEAM_CAP']
    m = meas(names, 'pre_meas')
    json.dump(m, open('pre_meas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(json.dumps(m, ensure_ascii=False)[:900])


def stage_beam():
    before = meas([BEAM], 'B_before')
    c = [C('component.activate', component='U1_FRAME')]
    for i, (x, z) in enumerate(REOPEN):
        c.append(cyl('DP3F1_BEAM_TAP_PY_REOPEN_%d' % (i + 1), BEAM, 2.1, [x, 320.1, z], [0, -1, 0], 8.2))
    r = run('B1_reopen', c)
    m1 = meas([BEAM], 'B1_meas')
    c = []
    for i, (x, y) in enumerate(FILL_NZ):
        c.append(cyl('DP3F1_BEAM_FILL_NZ_%d' % (i + 3), BEAM, 2.4, [x, y, 250], [0, 0, 1], 8, 'join'))
    for i, (x, z) in enumerate(FILL_NY):
        c.append(cyl('DP3F1_BEAM_FILL_NY_%d' % (i + 3), BEAM, 2.4, [x, 120, z], [0, 1, 0], 8, 'join'))
    c.append(C('component.activate', component='root'))
    run('B2_fill', c)
    after = meas([BEAM], 'B_after')
    v0, v1, v2 = before[BEAM]['volume'], m1[BEAM]['volume'], after[BEAM]['volume']
    hole = math.pi * 2.1 ** 2 * 8
    print('reopen d %.3f exp %.3f (2 x 10.963)' % (v0 - v1, 2 * 10.963))
    print('fill   d %.3f exp %.3f' % (v2 - v1, 6 * hole))
    print('beam', after[BEAM])
    json.dump(dict(before=before, reopen=m1, after=after, exp_reopen=2 * 10.963, exp_fill=6 * hole), open('B_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)


def comps():
    return q.call('cl_now', {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})['data']['components']


def tm(T):
    X, Y, Z, P = T[0][:3], T[1][:3], T[2][:3], T[3][:3]
    return [X[0], Y[0], Z[0], P[0], X[1], Y[1], Z[1], P[1], X[2], Y[2], Z[2], P[2]]


def props(ids, tag='props'):
    r = run(tag, [C('occurrence.properties', occurrence=i) for i in ids], rec=False, verbose=True)
    return [dict(name=x['name'], bbox=[round(v, 3) for v in x['total']['bbox']['min'] + x['total']['bbox']['max']],
                 bodies=[(b['name'], round(b['volume_mm3'], 3), b['material']) for b in x['bodies']]) for x in r]


def stage_bolts():
    Cs = comps()
    BYID = {c['id']: c for c in Cs}
    BYNAME = {c['name']: c for c in Cs}
    c = BYNAME['CB5-12_M07_CAP']
    src = BYNAME['CB5-16_M07_NY']
    assert len(c['occurrences']) == 8 and len(c['bodies']) == 1, (len(c['occurrences']), c['bodies'])
    o1 = c['occurrences'][0]
    P = BYID[c['parent']]
    ids = [o['id'] for o in c['occurrences']]
    before = props(ids, 'props_b')
    r = run('cb_copy', [C('occurrence.copy', component='CB5-16_M07_NY', parent=P['name'])], verbose=True)
    tmp = r[0]['occurrence']
    run('cb_move', [C('occurrence.move', occurrence=tmp, space='local', to_matrix=tm(o1['transform']))])
    pn = props([tmp], 'props_t')[0]
    print('tmp', pn)
    ch = []
    cid = c['parent']
    while cid != 0:
        cc = BYID[cid]
        assert len(cc['occurrences']) == 1, cc['name']
        o = cc['occurrences'][0]
        ch.append((o['id'], o['name']))
        cid = cc['parent']
    ch = ch[::-1]
    disp = '%s (%s/%s)' % (src['bodies'][0], '/'.join(x[1] for x in ch), pn['name'])
    print('src body', disp)
    r = run('cb_cb', [C('component.copy_bodies', bodies=[disp], component=c['id'], component_path=[x[0] for x in ch] + [o1['id']])], verbose=True)
    nb = r[0]['bodies'][0]
    print('copied body', nb)
    run('cb_fin', [C('solid.remove', bodies=[c['bodies'][0]]), C('body.rename', body=nb, name='CB5-16_M07_CAP'),
                   C('component.rename', component=c['id'], name='CB5-16_M07_CAP'),
                   C('component.metadata.set', component=c['id'], part_number='CB5-16', bom_type='purchased',
                     description='MISUMI CB5-16 hex socket head cap screw M5x16 (real STEP) - beam end cap P_M07_BEAM_CAP x4 per end, through beam wall D5.5 into cap flange M5 tap t3. Tighten 1.0 N.m (max 1.5) + removable threadlocker, M-01 exception DP3-EX1 (DP-3 fix1, was CB5-12: tip only 0.8 past the flange)'),
                   C('selection.delete', occurrences=[tmp])])
    after = props(ids, 'props_a')
    for b, a in zip(before, after):
        print(b['name'], b['bbox'], '->', a['name'], a['bbox'], a['bodies'])
    json.dump(dict(kind='swap_real', comp=c['id'], occ=ids, before=before, after=after), open('D_cap.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)


def stage_meta():
    Cs = comps()
    c = [x for x in Cs if x['name'] == 'P_M07_BEAM_CAP'][0]
    u = ex('cap_meta_get', 'component.metadata.get', {'component': c['id']})
    print(json.dumps(u.get('data'), ensure_ascii=False)[:800])


if __name__ == '__main__':
    st = sys.argv[1]
    globals()['stage_' + st]()
    if REC:
        json.dump(REC, open('cmds_%s.json' % st, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
