"""DP-3 저장 전 검사: 바뀐 · 새 바디 × 주변 틈 · 겹침(inspect.clearance), 겹친 쌍만 부피(inspect.interference).
usage(작업 폴더에서): clr.py <전수 측정 r_*.json> <out prefix> [pose 꼬리표]"""
import json, sys, re, q
src, pre = sys.argv[1], sys.argv[2]
m = q.unwrap(src)['data']
M = {b['name']: b for b in m['bodies']}


def bb(b):
    return b['bbox']['min'] + b['bbox']['max']


def near(a, b, d):
    return all(a[i] - d < b[i + 3] and b[i] - d < a[i + 3] for i in range(3))


HEAD = lambda n: re.sub(r' \(.*', '', n)
S_HEADS = ('P_M07_BEAM_CAP', 'CB5-12_M07_CAP', 'CB5-20_M08_NZ_COMB', 'STEP대기_CB4-30_M08', 'P_M08_TUBE_COMB_')
S = [n for n in M if HEAD(n).startswith(S_HEADS)]
# 바꿔 놓은 occurrence: HMI CB5-20_DP2 4(U8_PNEU 아래) · LBRK CB5-14 1
S += [n for n in M if HEAD(n) == 'CB5-20_DP2' and 'U8_PNEU' in n] + [n for n in M if HEAD(n) == 'STEP대기_CB5-14_DP2' and n.endswith(':8)')]
FIX = ['P_M07_BEAM', 'P_M07_SPLICE_NX', 'P_M07_SPLICE_PX']
N = set(FIX)
for s in S:
    a = bb(M[s])
    for n, b in M.items():
        if n in S or n in N:
            continue
        if near(a, bb(b), 12.0):
            N.add(n)
N = sorted(N)
print('S', len(S), 'against', len(N))
json.dump(dict(S=S, N=N), open(pre + '_lists.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
u = q.call(pre + '_clr', {'tool': 'execute', 'arguments': {'command': 'inspect.clearance', 'params': {'bodies': S, 'against': N, 'clearance': 1.0}}}, timeout=470)
d = u['data']
if u.get('isError') or isinstance(d, str):
    print('FAIL', str(d)[:1500])
    sys.exit(2)
print({k: (v if not isinstance(v, (list, dict)) else len(v)) for k, v in d.items()}, '%.1f s' % u['s'])
pairs = d.get('pairs') or d.get('violations') or []
ov = [p for p in pairs if p.get('overlap') or p.get('interferes') or (p.get('distance') is not None and p['distance'] <= 1e-6) or (p.get('min_distance') is not None and p['min_distance'] <= 1e-6)]
print('pairs', len(pairs), 'touch/overlap', len(ov))
if pairs:
    print(json.dumps(pairs[0], ensure_ascii=False)[:400])
json.dump(d, open(pre + '_clr.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
