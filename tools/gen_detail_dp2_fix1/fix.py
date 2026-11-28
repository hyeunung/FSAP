"""DP-2 수정 1회차: CB5-16_DP2:15 (U2_FLAP, XP_TAP_1 자리) → STEP대기_CB5-14_DP2 occurrence. usage: python -X utf8 -B fix.py"""
import json, q, sys
OLD = 101114
J = q.unwrap('r_jlist.json')['data']['joints']
js = [j for j in J if j.get('a') == OLD or j.get('b') == OLD]
print('joints on old occ', len(js), js[:2])
def run(tag, cmds, verbose=True):
    u = q.call(tag, {'commands': cmds, 'rollback': True, 'verbose': verbose}); d = u['data']
    if u.get('isError') or isinstance(d, str) or not d.get('ok'):
        print('FAIL', tag, json.dumps(d, ensure_ascii=False)[:1500]); sys.exit(2)
    return d['results']
def tm(T):
    X, Y, Z, P = T[0][:3], T[1][:3], T[2][:3], T[3][:3]
    return [X[0], Y[0], Z[0], P[0], X[1], Y[1], Z[1], P[1], X[2], Y[2], Z[2], P[2]]
T = [[0.0, 0.0, -1.0, 0.0], [0.0, 1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0], [1092.5, -330.0, -8.0, 1.0]]
before = run('props_b', [{'command': 'occurrence.properties', 'params': {'occurrence': OLD}}])[0]
print('before', before['name'], before['total']['bbox'], [(b['name'], round(b['volume_mm3'], 3), b['material']) for b in before['bodies']])
r = run('copy', [{'command': 'occurrence.copy', 'params': {'component': 'STEP대기_CB5-14_DP2', 'parent': 'U2_FLAP'}}])
new = r[0]['occurrence']; print('new occ', new, json.dumps(r[0], ensure_ascii=False)[:300])
cm = [{'command': 'occurrence.move', 'params': {'occurrence': new, 'space': 'local', 'to_matrix': tm(T)}}]
for j in js:
    other = j['a'] if j['b'] == OLD else j['b']; assert j['type'] == 'rigid'
    cm.append({'command': 'joint.rigid_group', 'params': {'occurrences': [other, new]}})
cm.append({'command': 'selection.delete', 'params': {'occurrences': [OLD]}})
run('swap', cm, verbose=False)
after = run('props_a', [{'command': 'occurrence.properties', 'params': {'occurrence': new}}])[0]
print('after', after['name'], after['total']['bbox'], [(b['name'], round(b['volume_mm3'], 3), b['material']) for b in after['bodies']])
json.dump([{'command': 'occurrence.copy', 'params': {'component': 'STEP대기_CB5-14_DP2', 'parent': 'U2_FLAP'}}] + cm, open('cmds_fix1.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(dict(old_occ=OLD, new_occ=new, before=before, after=after, joints=len(js)), open('log_fix1.json', 'w', encoding='utf-8'), ensure_ascii=False)
