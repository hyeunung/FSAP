"""DP-3 덮개 볼트 CB5-12 x8: paste_new 로 만든 컴포넌트(101220)를 이름 바꾸고 7개 더 놓는다."""
import json, sys, q
def C(command, **params): return {'command': command, 'params': params}
u = q.call('cl_cap', {'tool': 'execute', 'arguments': {'command': 'component.list', 'params': {'compact': True, 'bodies': True}}})
Cs = u['data']['components']; c = [x for x in Cs if x['id'] == 101220][0]
print(c['name'], c['bodies'], c['occurrences'])
o1 = c['occurrences'][0]['id']
cmds = [C('body.rename', body=c['bodies'][0], name='CB5-12_M07_CAP'), C('component.rename', component=101220, name='CB5-12_M07_CAP'),
        C('component.metadata.set', component=101220, part_number='CB5-12', bom_type='purchased', description='MISUMI CB5-12 hex socket head cap screw M5x12 (real STEP) - beam end cap P_M07_BEAM_CAP x4 per end, through beam wall D5.5 into cap flange M5 tap t3 (DP-3)')]
cmds += [C('occurrence.copy', component=101220, parent='U1_FRAME') for _ in range(7)]
r = q.call('capb1', {'commands': cmds, 'rollback': True, 'verbose': True}); d = r['data']
if not d.get('ok'): print('FAIL', json.dumps(d, ensure_ascii=False)[:1500]); sys.exit(2)
ids = [o1] + [x['occurrence'] for x in d['results'][3:]]
seats = []
for x in (-2362.0, 1332.0):
    for z in (350.0, 550.0):
        seats.append([0, 0, 1, x, 1, 0, 0, 120.0, 0, 1, 0, z])      # 앞벽: 머리 밑 Y 120, 넣는 방향 +Y
        seats.append([0, 0, -1, x, -1, 0, 0, 320.0, 0, 1, 0, z])    # 뒷벽: 머리 밑 Y 320, 넣는 방향 -Y
c2 = [C('occurrence.move', occurrence=i, space='local', to_matrix=m) for i, m in zip(ids, seats)]
c2 += [C('joint.rigid_group', occurrences=[2, i]) for i in ids]
c2 += [C('occurrence.properties', occurrence=i) for i in ids]
r = q.call('capb2', {'commands': c2, 'rollback': True, 'verbose': True}); d = r['data']
if not d.get('ok'): print('FAIL', json.dumps(d, ensure_ascii=False)[:1500]); sys.exit(2)
for x in d['results'][16:]: print(x['name'], [round(v, 2) for v in x['total']['bbox']['min'] + x['total']['bbox']['max']], [(b['name'], round(b['volume_mm3'], 2), b['material']) for b in x['bodies']])
json.dump(cmds + c2[:16], open('cmds_B4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(dict(comp=101220, occ=ids, seats=seats), open('capbolts.json', 'w'))
