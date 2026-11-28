"""수정 1회차 단계 4: 볼트 — CB5-16 5개(세움 받침 3 · 리드 안내 2)를 실물 CB5-16 컴포넌트 복사로 새로 놓고 옛 CB5-12 x4 · CB4-12 x1 컴포넌트를 지운다.
T2_2(+X 2) · CLAMP_1(+Y 1) · CLAMP_2(+Y 1, +Z 1.5)는 묶음을 풀고 옮긴 뒤 다시 묶는다."""
import json, time, sys, fx
from fx import ex, C, run, tm
st = sys.argv[1]
SEAT = {  # 옛 컴포넌트 이름: (새 이름, 부모 occurrence, 옮김 world, 설명)
 'CB5-12_RXDC03_RISER_1': ('CB5-16_RXDC03_RISER_1', 97893, (0, 0, 3), 'riser bracket P_RXDC03_RISER_BRKT (A5052-H32 milled, base t6) -> block ledge M5 through tap, engagement 10'),
 'CB5-12_RXDC03_RISER_2': ('CB5-16_RXDC03_RISER_2', 97893, (0, 0, 3), 'riser bracket P_RXDC03_RISER_BRKT (A5052-H32 milled, base t6) -> block ledge M5 through tap, engagement 10'),
 'CB4-12_RXDCC1_RISER_3': ('CB5-16_RXDCC1_RISER_3', 97893, (15.25, 0.75, 3), 'riser bracket ear (-265.25, 79) -> block ledge M5 through tap, engagement 10 (was CB4-12 at (-280.5, 78.25), U-12)'),
 'CB5-12_RXDC03_GUIDE_1': ('CB5-16_RXDC03_GUIDE_1', 33, (-3, 0, 0), 'lead guide P_RXDC03_LEAD_GUIDE_3DP (PET-CF printed, seat pad t6) -> swing tongue M5 through tap t12, engagement 10. Tighten 1.5 N.m (PET-CF seat)'),
 'CB5-12_RXDC03_GUIDE_2': ('CB5-16_RXDC03_GUIDE_2', 33, (-3, 0, 0), 'lead guide P_RXDC03_LEAD_GUIDE_3DP (PET-CF printed, seat pad t6) -> swing tongue M5 through tap t12, engagement 10. Tighten 1.5 N.m (PET-CF seat)')}
MOVE = {'CB5-12_RXDC03_T2_2': (97893, (2, 0, 0)), 'CB5-12_RXDC03_CLAMP_1': (97891, (0, 1, 0)), 'CB5-12_RXDC03_CLAMP_2': (97891, (0, 1, 1.5))}
Cs = fx.comps('cl_s4'); BY = {c['name']: c for c in Cs}
if st == 'paste':
    new = {}
    for old, (nn, par, d, desc) in SEAT.items():
        o = BY[old]['occurrences'][0]; T = [list(r) for r in o['transform']]
        T[3] = [T[3][0] + d[0], T[3][1] + d[1], T[3][2] + d[2]] + T[3][3:]
        r = run('s4_paste_' + nn[-7:], [C('component.paste_new', component='CB5-16_M07_NY', parent='root')], verbose=True)
        print(nn, json.dumps(r, ensure_ascii=False)[:500])
        new[old] = dict(new=nn, paste=r[0], seat=tm(T), parent=par, desc=desc)
    json.dump(new, open('s4_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if st == 'place':
    new = json.load(open('s4_new.json', encoding='utf-8'))
    BYID = {c['id']: c for c in Cs}
    cm = []
    for old, v in new.items():
        p = v['paste']; cid = p.get('component') or p.get('id'); c = BYID[cid]; oid = c['occurrences'][0]['id']
        v['cid'] = cid; v['oid'] = oid
        cm += [C('body.rename', body=c['bodies'][0], name=v['new']), C('component.rename', component=cid, name=v['new']),
               C('component.metadata.set', component=cid, part_number='CB5-16', bom_type='purchased', description='MISUMI CB5-16 hex socket head cap screw M5x16 (real STEP) - ' + v['desc'] + ' (DP-4 fix1)'),
               C('occurrence.move', occurrence=oid, space='local', to_matrix=v['seat']),
               C('joint.rigid_group', occurrences=[v['parent'], oid])]
    r = run('s4_place', cm, verbose=False)
    print(json.dumps(r, ensure_ascii=False)[:600])
    r = run('s4_delold', [C('component.delete', component=BY[old]['id']) for old in new], verbose=True)
    print(json.dumps(r, ensure_ascii=False)[:900])
    json.dump(new, open('s4_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(fx.meas([v['new'] for v in new.values()]))
if st == 'move':
    j = ex('jl_s4', 'joint.list')['data']
    cm = []
    for n, (par, d) in MOVE.items():
        oid = BY[n]['occurrences'][0]['id']
        js = [x for x in j['joints'] if x.get('type') == 'rigid' and oid in (x.get('a'), x.get('b'))]
        print(n, oid, [(x['id'], x.get('name'), x.get('a'), x.get('b')) for x in js])
        assert len(js) == 1, js
        cm += [C('joint.delete', joint=js[0]['id']), C('occurrence.move', occurrence=oid, space='world', translate=list(d)), C('joint.rigid_group', occurrences=[par, oid])]
    r = run('s4_move', cm, verbose=True)
    print(json.dumps(r, ensure_ascii=False)[:900])
    print(fx.meas(list(MOVE)))
