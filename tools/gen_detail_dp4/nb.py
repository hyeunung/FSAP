"""서명 표에서 이웃 찾기"""
import json, os
SIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'signatures.json')
def parts():
    s = json.load(open(SIG, encoding='utf-8'))['parts']
    return list(s.values()) if isinstance(s, dict) else s
def neighbors(names, margin=6, boxes=None):
    P = parts(); by = {p['name']: p for p in P}
    out = []
    bl = [by[n]['bbox'] for n in names if n in by] + (boxes or [])
    for p in P:
        if p['name'] in names: continue
        B = p['bbox']
        for A in bl:
            if all(A[2*i] - margin <= B[2*i+1] and B[2*i] - margin <= A[2*i+1] for i in range(3)):
                out.append(p['name']); break
    return out
