# STEPLITE: F3SG-4RA0800-14 간이 형상 생성기(2026-11-10). 원본 STEP의 Y 단면을 띠(slab)로 밀어 만든다.
# 사용: python -B gen_v2_steplite.py sections <body> <out.json>  -> 단면 스크립트
#       python -B gen_v2_steplite.py build <sec_results.json> <out_cmds.json> <bodyname>
import json, math, sys

# (y0, y1, y_sample) 원본 STEP 좌표(길이 +Y). 몸 L(NONE (4))과 D(NONE (2))가 같은 띠를 쓴다.
SLABS = [(-15.0, 0.0, -5.0), (0.0, 0.6, 0.35), (0.6, 5.5, 3.0), (5.5, 10.35, 8.0), (10.35, 13.1, 11.5),
         (13.1, 13.85, 13.5), (13.85, 16.85, 15.0), (16.85, 17.85, 17.3), (17.85, 18.6, 18.2), (18.6, 23.35, 21.0),
         (23.35, 24.85, 24.1), (24.85, 27.85, 26.0), (27.85, 30.85, 29.0), (30.85, 35.6, 33.5), (35.6, 38.2, 37.0),
         (38.2, 827.8, 200.0), (827.8, 833.0, 830.0), (833.0, 834.2, 833.6), (834.2, 836.0, 835.0), (836.0, 840.0, 838.0),
         (840.0, 841.0, 840.6), (841.0, 843.0, 842.0), (843.0, 845.0, 844.0), (845.0, 846.5, 845.8), (846.5, 848.0, 847.2)]


def sections(body, out):
    cmds = []
    for i, (a, b, y) in enumerate(SLABS):
        cmds += [{"command": "sketch.create", "params": {"plane": {"origin": [0, y, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, "name": "SEC_%d" % i}},
                 {"command": "sketch.intersect", "params": {"refs": [{"body": body}], "projection_link": False}},
                 {"command": "sketch.inspect", "params": {}},
                 {"command": "sketch.finish", "params": {}}]
    json.dump(cmds, open(out, 'w'))


def loops_of(sec, tol=0.01):
    """단면 곡선(원본 XZ, x=X, y=Z)을 끝점으로 이어 닫힌 고리로. 호는 시작→끝 반시계."""
    segs = []
    for c in sec['curves']:
        if c['type'] == 'circle':
            segs.append(('circle', c['center_at'], c['radius']))
        elif c['type'] == 'line':
            if math.dist(c['start_at'], c['end_at']) > 1e-6:
                segs.append(('line', c['start_at'], c['end_at']))
        elif c['type'] == 'arc':
            cx, cy = c['center_at']; r = c['radius']
            a0 = math.atan2(c['start_at'][1] - cy, c['start_at'][0] - cx)
            a1 = math.atan2(c['end_at'][1] - cy, c['end_at'][0] - cx)
            sw = (a1 - a0) % (2 * math.pi)
            am = a0 + sw / 2
            segs.append(('arc', c['start_at'], c['end_at'], [cx + r * math.cos(am), cy + r * math.sin(am)]))
        else:
            raise ValueError(c['type'])
    # 점 합치기
    pts = []
    def pid(p):
        for i, q in enumerate(pts):
            if math.dist(p, q) < tol:
                return i
        pts.append(list(p)); return len(pts) - 1
    out = []
    for s in segs:
        if s[0] == 'circle':
            out.append(s)
        elif s[0] == 'line':
            out.append(('line', pid(s[1]), pid(s[2])))
        else:
            out.append(('arc', pid(s[1]), pid(s[2]), s[3]))
    return pts, out


def sk(p):   # 원본 (X, Z) -> 새 스케치 (x, y): 평면 x_dir +X, y_dir -Z (법선 +Y)
    return [round(p[0], 4), round(-p[1], 4)]


def build(secres, out, bodyname):
    r = json.load(open(secres, encoding='utf-8'))
    secs = [x for x in r if isinstance(x, dict) and 'curves' in x and 'profiles' in x]
    assert len(secs) == len(SLABS), (len(secs), len(SLABS))
    cmds = []
    for i, ((a, b, y), sec) in enumerate(zip(SLABS, secs)):
        pts, segs = loops_of(sec)
        name = 'SK_LITE_%s_%02d' % (bodyname, i)
        cmds.append({"command": "sketch.create", "params": {"plane": {"origin": [0, a, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, -1]}, "name": name}})
        for s in segs:
            if s[0] == 'circle':
                cmds.append({"command": "sketch.circle.center", "params": {"center": sk(s[1]), "radius": round(s[2], 4)}})
            elif s[0] == 'line':
                cmds.append({"command": "sketch.line", "params": {"points": [sk(pts[s[1]]), sk(pts[s[2]])]}})
            else:
                cmds.append({"command": "sketch.arc.three_point", "params": {"start": sk(pts[s[1]]), "end": sk(pts[s[2]]), "through": sk(s[3])}})
        cmds.append({"command": "sketch.inspect", "params": {}})
        cmds.append({"command": "sketch.finish", "params": {}})
    json.dump(cmds, open(out, 'w'))


if __name__ == '__main__':
    if sys.argv[1] == 'sections':
        sections(sys.argv[2], sys.argv[3])
    else:
        build(sys.argv[2], sys.argv[3], sys.argv[4])
