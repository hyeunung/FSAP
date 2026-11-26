# RX-DC-C1 해석부: 세움 받침 STEP에서 꼭짓점(VERTEX_POINT)을 읽어 높이별 외곽을 본다(면 선택은 STEP 형상으로)
import re, sys, json, collections
p = sys.argv[1]
t = open(p, encoding='utf-8', errors='ignore').read()
ents = dict(re.findall(r'#(\d+)=([^;]*);', t))
pts = {}
for k, v in ents.items():
    m = re.match(r"CARTESIAN_POINT\('[^']*',\(([^)]*)\)\)", v)
    if m:
        pts[k] = tuple(round(float(x), 3) for x in m.group(1).split(','))
verts = []
for k, v in ents.items():
    m = re.match(r"VERTEX_POINT\('[^']*',#(\d+)\)", v)
    if m:
        verts.append(pts[m.group(1)])
xs = [a[0] for a in verts]; ys = [a[1] for a in verts]; zs = [a[2] for a in verts]
print('verts', len(verts), 'bbox X', min(xs), max(xs), 'Y', min(ys), max(ys), 'Z', min(zs), max(zs))
byz = collections.defaultdict(set)
for a in verts:
    byz[a[2]].add((a[0], a[1]))
for z in sorted(byz):
    s = sorted(byz[z])
    print('Z', z, len(s), s if len(s) <= 24 else s[:24])
