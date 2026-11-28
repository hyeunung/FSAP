import json, q, re, collections
f = json.load(open('../../fasten_v2306/f_bolts.json', encoding='utf-8'))
d = q.unwrap('r_complist.json')['data']
comps = d['components']; byid = {c['id']: c for c in comps}; byname = {c['name']: c for c in comps}
occ = {}
for c in comps:
    for o in c['occurrences']:
        occ[o['name']] = dict(o, comp=c['name'], comp_id=c['id'], n_occ=len(c['occurrences']))
def target(k, x):
    sp = x['spec']; th = x.get('thread_hole'); tk = x.get('thread_kind'); tb = x.get('thread_body') or ''
    short = any('물림 부족' in i for i in x['issues'])
    if not short: return None
    if sp == 'SFB5-10': return 'SFB5-16'
    if tk == 'T너트' and sp.startswith('CB5-'):
        L = int(sp.split('-')[1]); a, b = th; bottom = b + 1.25
        for Ln in (16, 20, 25, 14, 22):   # 표준 길이 먼저, 바닥에 닿을 때만 둘째 선택 길이(지시서 표)
            if Ln <= L: continue
            if min(Ln, b) - a >= 7.5 and bottom - Ln >= 0.5: return 'CB5-%d' % Ln
        return 'NONE'
    if sp == 'CB5-12' and (tb.startswith('P_RX12C1_FLAP_BAR') or tb.startswith('P_RX12C1_GS_ARM_BLK') or tb in ('P_M06_G1_PIN', 'P_M06_TOP_PIN')): return 'CB5-16'
    if sp == 'CB5-12' and tb.startswith('PGX62-H-10'): return 'CB5-16'
    return None
T = []
for k, x in f.items():
    t = target(k, x)
    if not t: continue
    m = re.search(r'/([^/]+:\d+)\)$', k)
    if m: on = m.group(1)
    else:
        on = byname[k]['occurrences'][0]['name']
    o = occ[on]
    T.append(dict(key=k, occ=on, occ_id=o['id'], comp=o['comp'], comp_id=o['comp_id'], n_occ=o['n_occ'], parent=o['parent'], parent_name=byid[o['parent']]['name'] if o['parent'] in byid else 'root', transform=o.get('transform'), old=x['spec'], new=t, thread=x['thread_hole'], tb=x['thread_body'], tk=x['thread_kind'], unit=x['unit']))
json.dump(T, open('targets.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(T), collections.Counter((t['old'], t['new']) for t in T))
g = collections.defaultdict(list)
for t in T: g[(t['comp'], t['new'])].append(t)
bycomp = collections.Counter(t['comp'] for t in T)
for (c, n), v in sorted(g.items()):
    print(c, '->', n, len(v), 'of', v[0]['n_occ'], 'ALL' if bycomp[c] == v[0]['n_occ'] and len(v)==v[0]['n_occ'] else 'mixed', 'parents', collections.Counter(t['parent_name'] for t in v), 'thr', sorted(set(tuple(t['thread']) for t in v)))
