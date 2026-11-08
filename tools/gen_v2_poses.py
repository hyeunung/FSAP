# 회귀 자세 정의 생성기(REG-02, C-34, 2026-11-08)
# 입력: out/mech_REG-02/poses_v265.json (REG-01 회귀 자세 183점, v2.6.5 기준)
# 출력: out/mech_REG-01/poses.json, out/mech_REG-01/r5/poses.json, out/poses_v266.json
# 바꾸는 것: (1) J_U6_HGT != J_U7_HGT 인 자세(옛 POSE 8·9)를 뺀다 — 높이 조정이 하나라 생길 수 없다.
#            (2) J_U6_HGT 조인트가 없어졌으므로 모든 자세에서 J_U6_HGT 키를 지운다(U6는 J_U7_HGT를 따른다).
#            (3) 옛 번호 -> 새 번호 대응표를 out/mech_REG-02/poses_map.json 에 남긴다(옛 10~182 -> 새 8~180).
import json, os
H = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(H, 'out', 'mech_REG-02', 'poses_v265.json'), encoding='utf-8'))
new, mp, dropped = [], {}, []
for i, p in enumerate(src):
    u6, u7 = p.get('J_U6_HGT'), p.get('J_U7_HGT')
    if u6 is not None and u7 is not None and u6 != u7:
        dropped.append({'old': i, 'pose': p}); continue
    if u6 is not None and u7 is None:
        p = dict(p); p['J_U7_HGT'] = u6
    q = {k: v for k, v in p.items() if k != 'J_U6_HGT'}
    mp[i] = len(new); new.append(q)
for rel in (('out', 'mech_REG-01', 'poses.json'), ('out', 'mech_REG-01', 'r5', 'poses.json'), ('out', 'poses_v266.json')):
    json.dump(new, open(os.path.join(H, *rel), 'w', encoding='utf-8'))
json.dump({'old_to_new': mp, 'dropped': dropped, 'n_old': len(src), 'n_new': len(new)},
          open(os.path.join(H, 'out', 'mech_REG-02', 'poses_map.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(src), '->', len(new), 'dropped', [d['old'] for d in dropped])
