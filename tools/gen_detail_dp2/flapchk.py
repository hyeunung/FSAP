import json, q, re, sys
m = q.unwrap('r_meas_all.json')['data']
B = {b['name']: b['bbox'] for b in m['bodies']}
sd = json.load(open('pre_sigdiff.json', encoding='utf-8'))
C = q.unwrap('r_cl_now.json')['data']['components']
byid = {c['id']: c for c in C}
flap = [c for c in C if c['name'] == 'U2_FLAP'][0]
def under(cid, root):
    while cid:
        if cid == root: return True
        cid = byid[cid]['parent']
    return False
own = set(flap['bodies'])
inflap = lambda n: ('U2_FLAP:1/' in n) or (n in own)
h = lambda n: re.sub(r' \(.*', '', n)
mine = [n for n in list(sd['added']) + [k.split('/', 1)[1] for k in sd['changed']] if inflap(n)]
box = dict(min=[380, -1260, -760], max=[1150, -280, 10])
def touch(a, b): return all(a['min'][i] <= b['max'][i] and b['min'][i] <= a['max'][i] for i in range(3))
ag = [n for n, bb in B.items() if touch(bb, box) and not inflap(n)]
flap_bodies = own
print('flap changed', len(mine), 'against', len(ag), 'flap bodies', len(flap_bodies))
base = json.load(open('pre_clr_final.json', encoding='utf-8'))['overlaps']
out = {}
for ang in (-22.5, -45.0, -67.5, -90.0):
    u = q.call('flap_drive', {'tool': 'execute', 'arguments': {'command': 'joint.drive', 'params': {'joint': 'J_U2_FLAP', 'value': ang}}})
    if u.get('isError'): print('drive err', u['data']); break
    u = q.call('flap_clr_%d' % abs(int(ang)), {'tool': 'execute', 'arguments': {'command': 'inspect.clearance', 'params': {'bodies': mine, 'against': ag, 'clearance': 0.0}}}, timeout=900)
    d = u['data']
    if isinstance(d, str): print('ERR', d[:300]); break
    newov = [(o['a'], o['b'], round(o['volume_mm3'], 2)) for o in d['overlaps'] if ' | '.join(sorted((o['a'], o['b']))) not in base]
    out[ang] = dict(checked=d['pairs_checked'], pruned=d['pairs_pruned'], overlaps=len(d['overlaps']), new=newov, unchecked=len(d.get('unchecked', [])), s=u['s'])
    print(ang, out[ang])
u = q.call('rest_after_flap', {'tool': 'execute', 'arguments': {'command': 'motion.play', 'params': {'study': 'REST', 'step': 0}}})
print('REST moved', u['data'].get('moved'), 'conflicts', u['data'].get('conflicts'))
json.dump(out, open('flap_selfcheck.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
