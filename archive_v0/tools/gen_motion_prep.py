# 준비부: 동작 검사 준비물(고정부·조인트·대기/사이클 동작 연구·작업 대상 모형)을 만드는 SolidCraft 명령 스크립트 생성기
# 출력: out/prep/prep_build.json(명령 스크립트), out/prep/prep_info.json(임시값·상태 -> 단계 표)
# 쓰는 법(FSAP 루트에서):
#   python -B tools/gen_motion_prep.py
#   "C:/Program Files/SolidCraft/solidcraft-cli.exe" run tools/out/prep/prep_build.json --in 3D_Modeling/FSAP_v0.0.0.sc --save 3D_Modeling/FSAP_v<새 번호>.sc
# 자료대기(D-01~D-07, D-10) 값이 오면 아래 임시값을 바꾸고 다시 만든다. 동작 연구 키는 숫자라서 형상 파라미터를 바꿔도 따라오지 않는다.
import json, math, sys, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'prep')
os.makedirs(OUT, exist_ok=True)

# ---- 임시값 (자료대기 D-번호). 근거는 보고서 mech_prep.md 3절 ----
T_MAT = 10.0      # D-04 매트 두께 (자리값, 근거 없음)
TAPE_T = 1.0      # D-06 테이프 두께 (자리값)
TAPE_W = 10.0     # D-06 테이프 날개 폭 (자리값)
SCRAP_L = 30.0    # D-07 절단 끝단 길이 (자리값)
RC = 30.0         # D-03 볼록 모서리 반경 (자리값)
RCC = 10.0        # D-03 오목 모서리 반경 (자리값)
G_W = 20.0        # D-02 가장 좁은 홈 폭 (자리값)
G_D = 100.0       # D-02 홈 깊이 (자리값)
STANDBY_GAP = 100.0   # 대기 위치에서 큰 매트 가장자리-바늘 거리 (자리값, 헤드 몸체 D-10 미정)
PRESSER_LIFT = 10.0   # D-10 노루발 들림 (자리값)
NEEDLE_DOWN = -30.0   # D-10 바늘 내림 행정 (자리값)
DK = 2.5             # 키 간격: 꺾임은 2.5도마다 키(선형 보간 오차 < 0.25 mm)
DS, DTH = 20.0, 5.0   # 사이클 연구 단계 간격: 받침 이동 20 mm 또는 회전 5도마다 1단계(키 사이 최소 1단계)
FINE = (2.0, 1.0, 1.0)  # 상태별 정밀 연구: 키 1도, 이동 2 mm 또는 회전 1도마다 1단계
SHARP_R = 10.0        # 이 반경 이하 꺾임은 노루발을 들고 돈다 (T03 자리값)

MATS = {
    'LARGE': dict(L=1200.0, W=1200.0, kind='rr', label='가장 큰 매트'),   # D-01 임시: 벤치마크 공개 상한(우리 사양 아님)
    'SMALL': dict(L=300.0, W=200.0, kind='rr', label='가장 작은 매트'),    # D-01 임시: 벤치마크 공개 하한(우리 사양 아님)
    'GROOVE': dict(L=1200.0, W=1200.0, kind='groove', label='가장 좁은 홈 매트'),
}
W_MAX = max(m['W'] for m in MATS.values())
STANDBY = dict(x=0.0, y=-(W_MAX / 2 + STANDBY_GAP), rot=0.0, head=0.0, presser=PRESSER_LIFT, needle=0.0)

# 세그먼트: ('L', p0, p1) | ('A', c, r, a0, a1)  a는 도, 볼록은 a 증가(CCW), 오목은 a 감소(CW) | ('P', p, phi0, phi1) 날카로운 꺾임
def rr(L, W, r):
    x, y = L / 2, W / 2
    return [
        ('L', (0, y), (-x + r, y)), ('A', (-x + r, y - r), r, 90, 180),
        ('L', (-x, y - r), (-x, -y + r)), ('A', (-x + r, -y + r), r, 180, 270),
        ('L', (-x + r, -y), (x - r, -y)), ('A', (x - r, -y + r), r, 270, 360),
        ('L', (x, -y + r), (x, y - r)), ('A', (x - r, y - r), r, 0, 90),
        ('L', (x - r, y), (0, y)),
    ]

def groove(L, W):
    x, y = L / 2, W / 2
    nx, ny = x - 150, y - 150          # 계단 오목 모서리 자리(왼쪽 위 150x150 자리값)
    gw = G_W / 2
    gb = -y + G_D - gw                 # 홈 바닥 반원 중심 y
    return [
        ('L', (0, y), (-nx + RC, y)), ('A', (-nx + RC, y - RC), RC, 90, 180),
        ('L', (-nx, y - RC), (-nx, ny + RCC)), ('A', (-nx - RCC, ny + RCC), RCC, 0, -90),
        ('L', (-nx - RCC, ny), (-x + RC, ny)), ('A', (-x + RC, ny - RC), RC, 90, 180),
        ('L', (-x, ny - RC), (-x, -y + RC)), ('A', (-x + RC, -y + RC), RC, 180, 270),
        ('L', (-x + RC, -y), (-gw, -y)), ('P', (-gw, -y), 270, 360),
        ('L', (-gw, -y), (-gw, gb)), ('A', (0, gb), gw, 180, 0),
        ('L', (gw, gb), (gw, -y)), ('P', (gw, -y), 180, 270),
        ('L', (gw, -y), (x - RC, -y)), ('A', (x - RC, -y + RC), RC, 270, 360),
        ('L', (x, -y + RC), (x, y - RC)), ('A', (x - RC, y - RC), RC, 0, 90),
        ('L', (x - RC, y), (0, y)),
    ]

def outline(m):
    return rr(m['L'], m['W'], RC) if m['kind'] == 'rr' else groove(m['L'], m['W'])

def r2(v):
    return [round(v[0], 4), round(v[1], 4)]

def offset_outline(segs, d):
    """윤곽을 바깥(+d)·안(-d)으로 띄운다. 직선은 바깥 법선으로, 호는 반경 +-d, 날카로운 꺾임은 바깥이면 호, 안이면 두 직선의 교점."""
    out = []
    for s in segs:
        if s[0] == 'L':
            p0, p1 = s[1], s[2]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(dx, dy)
            nx, ny = dy / ln, -dx / ln
            out.append(['L', (p0[0] + d * nx, p0[1] + d * ny), (p1[0] + d * nx, p1[1] + d * ny)])
        elif s[0] == 'A':
            c, r, a0, a1 = s[1], s[2], s[3], s[4]
            rn = r + d if a1 > a0 else r - d
            if rn <= 0:
                raise SystemExit('offset collapses arc')
            out.append(['A', c, rn, a0, a1])
        elif s[0] == 'P':
            out.append(['P', s[1], s[2], s[3]])
    res = []
    for i, s in enumerate(out):
        if s[0] != 'P':
            res.append(s); continue
        p, f0, f1 = s[1], s[2], s[3]
        if d > 0:
            res.append(['A', p, d, f0, f1])
        else:
            a, b = res[-1], out[i + 1]
            (x1, y1), (x2, y2) = a[1], a[2]
            (x3, y3), (x4, y4) = b[1], b[2]
            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            X = (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
            a[2] = X; b[1] = X
    return [tuple(x) for x in res]

def curve_ids(segs):
    ids, nl, na = [], 0, 0
    for s in segs:
        if s[0] == 'L':
            nl += 1; ids.append('l%d' % nl)
        elif s[0] == 'A':
            na += 1; ids.append('a%d' % na)
    return ids

def sketch_cmds(segs):
    cmds = []
    for s in segs:
        if s[0] == 'L':
            cmds.append({"command": "sketch.line", "params": {"points": [r2(s[1]), r2(s[2])]}})
        elif s[0] == 'A':
            c, r, a0, a1 = s[1], s[2], s[3], s[4]
            p0 = (c[0] + r * math.cos(math.radians(a0)), c[1] + r * math.sin(math.radians(a0)))
            p1 = (c[0] + r * math.cos(math.radians(a1)), c[1] + r * math.sin(math.radians(a1)))
            prm = {"center": r2(c), "start": r2(p0), "end": r2(p1)}
            if a1 < a0:
                prm["clockwise"] = True
            cmds.append({"command": "sketch.arc.center_point", "params": prm})
    return cmds

# ---- 봉제 경로 -> 받침 자세 ----
def pose(p, phi):
    th = 90.0 - phi
    t = math.radians(th)
    rx = math.cos(t) * p[0] - math.sin(t) * p[1]
    ry = math.sin(t) * p[0] + math.cos(t) * p[1]
    return (-rx, -ry, th)

def path_samples(segs, dk):
    """(p, phi, tag, presser_up) 목록. phi는 이어지게(unwrap) 둔다."""
    out = []
    phi_base = None
    def add(p, phi, tag, up):
        out.append((p, phi, tag, up))
    phi_cur = 90.0
    for s in segs:
        if s[0] == 'L':
            p0, p1 = s[1], s[2]
            d = (p1[0] - p0[0], p1[1] - p0[1])
            phi = math.degrees(math.atan2(d[1], d[0])) - 90.0
            while phi < phi_cur - 180: phi += 360
            while phi > phi_cur + 180: phi -= 360
            phi_cur = phi
            add(p0, phi, '직선', False); add(p1, phi, '직선', False)
        elif s[0] == 'A':
            c, r, a0, a1 = s[1], s[2], s[3], s[4]
            convex = a1 > a0
            n = max(2, int(math.ceil(abs(a1 - a0) / dk)))
            up = r <= SHARP_R
            tag = ('볼록 모서리' if convex else ('홈 바닥 꺾임' if abs(a1 - a0) >= 179 else '오목 모서리'))
            for i in range(n + 1):
                a = a0 + (a1 - a0) * i / n
                p = (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
                phi = a if convex else a + 180.0
                while phi < phi_cur - 180: phi += 360
                while phi > phi_cur + 180: phi -= 360
                phi_cur = phi
                add(p, phi, tag, up)
        elif s[0] == 'P':
            p, f0, f1 = s[1], s[2], s[3]
            while f0 < phi_cur - 180: f0 += 360; f1 += 360
            while f0 > phi_cur + 180: f0 -= 360; f1 -= 360
            n = max(2, int(math.ceil(abs(f1 - f0) / dk)))
            for i in range(n + 1):
                phi = f0 + (f1 - f0) * i / n
                add(p, phi, '홈 입구', True)
            phi_cur = f1
    return out

def build_study(key, m, dk=DK, ds=DS, dth=DTH, sub=None, name=None, local=False):
    segs = outline(m)
    samp = path_samples(segs, dk)
    frames = []   # (x,y,rot,head,presser,needle, state)
    sb = STANDBY
    def F(x, y, rot, presser, needle, state, p=None):
        frames.append(dict(x=x, y=y, rot=rot, head=0.0, presser=presser, needle=needle, state=state, p=p))
    F(sb['x'], sb['y'], sb['rot'], sb['presser'], sb['needle'], '0 대기')
    F(sb['x'], sb['y'], sb['rot'], sb['presser'], sb['needle'], '① 로딩')
    x0, y0, th0 = pose(samp[0][0], samp[0][1])
    F(x0, y0, th0, PRESSER_LIFT, 0.0, '② 시작점 찾기')
    F(x0, y0, th0, 0.0, NEEDLE_DOWN, '② 바인더 물림')
    prev_up = False
    for (p, phi, tag, up) in samp:
        x, y, th = pose(p, phi)
        if up and not prev_up:
            F(x, y, th, 0.0, NEEDLE_DOWN, '③ ' + tag, p)          # 도착, 노루발 내림
            F(x, y, th, PRESSER_LIFT, NEEDLE_DOWN, '③ ' + tag, p)  # 노루발 들기
        elif (not up) and prev_up:
            F(x, y, th, PRESSER_LIFT, NEEDLE_DOWN, '③ ' + tag, p)
            F(x, y, th, 0.0, NEEDLE_DOWN, '③ ' + tag, p)
            prev_up = up
            continue
        F(x, y, th, PRESSER_LIFT if up else 0.0, NEEDLE_DOWN, '③ ' + tag, p)
        prev_up = up
    xe, ye, the = frames[-1]['x'], frames[-1]['y'], frames[-1]['rot']
    F(xe, ye, the, 0.0, NEEDLE_DOWN, '④ 시작·끝 이음매')
    F(xe, ye, the, PRESSER_LIFT, 0.0, '④ 테이프·실 절단')
    F(sb['x'], sb['y'], the, PRESSER_LIFT, 0.0, '⑤ 배출')
    # 중복 프레임 제거(같은 자세 연속)
    fr = [frames[0]]
    for f in frames[1:]:
        g = fr[-1]
        same = all(abs(f[k] - g[k]) < 1e-6 for k in ('x', 'y', 'rot', 'presser', 'needle')) and f['state'] == g['state']
        if not same:
            fr.append(f)
    if sub:
        runs = []
        for i, f in enumerate(fr):
            if runs and runs[-1][0] == f['state'] and runs[-1][2] == i - 1:
                runs[-1][2] = i
            else:
                runs.append([f['state'], i, i])
        ra = [r for r in runs if r[0] == sub[0]][sub[1] - 1]
        rb = [r for r in runs if r[0] == sub[2]][sub[3] - 1]
        fr = fr[max(0, ra[1] - 1):rb[2] + 2]
    # 단계 배분
    step = 0
    steps = [0]
    for a, b in zip(fr[:-1], fr[1:]):
        d = math.hypot(b['x'] - a['x'], b['y'] - a['y'])
        if local and a['p'] is not None:
            t = math.radians(b['rot']); q = a['p']
            wx = math.cos(t) * q[0] - math.sin(t) * q[1] + b['x']
            wy = math.sin(t) * q[0] + math.cos(t) * q[1] + b['y']
            d = math.hypot(wx, wy)   # 바늘에 있던 매트 점이 움직인 거리
        n = max(1, int(math.ceil(max(d / ds, abs(b['rot'] - a['rot']) / dth))))
        step += n
        steps.append(step)
    joints = [('J_MAT_X', 'x'), ('J_MAT_Y', 'y'), ('J_MAT_ROT', 'rot'), ('J_HEAD_ROT', 'head'),
              ('J_PRESSER', 'presser'), ('J_NEEDLE', 'needle')]
    keys = []
    for jn, k in joints:
        pts = []
        for s, f in zip(steps, fr):
            v = round(f[k], 4)
            if pts and pts[-1][0] == s:
                pts[-1] = [s, v]
            else:
                pts.append([s, v])
        keys.append({"joint": jn, "points": pts})
    states = []
    for s, f in zip(steps, fr):
        if not states or states[-1]['state'] != f['state']:
            states.append(dict(state=f['state'], from_step=s, to_step=s))
        else:
            states[-1]['to_step'] = s
    ext = dict(x=[min(f['x'] for f in fr), max(f['x'] for f in fr)],
               y=[min(f['y'] for f in fr), max(f['y'] for f in fr)],
               rot=[min(f['rot'] for f in fr), max(f['rot'] for f in fr)])
    return dict(name=name or ('사이클_' + {'LARGE': '큰매트', 'SMALL': '작은매트', 'GROOVE': '홈매트'}[key]),
                steps=step, keys=keys, states=states, extent=ext, nkeys=len(fr))

def main():
    S = []
    C = lambda c, p: S.append({"command": c, "params": p})
    # 1) 골격 컴포넌트
    C("component.create", {"name": "BASE", "grounded": True, "activate": False})
    for n in ("MAT_X", "MAT_Y", "MAT_ROT", "HEAD", "PRESSER", "NEEDLE"):
        C("component.create", {"name": n, "activate": False})
    desc = {
        "BASE": "고정부(바닥 고정). 프레임은 T01·T02 모델링에서 넣는다",
        "MAT_X": "매트 이송 X축 이동체(T01 자리)",
        "MAT_Y": "매트 이송 Y축 이동체(T01 자리)",
        "MAT_ROT": "매트 잡기·회전 유닛(T01 자리, 진공 원판·판 클램프 후보 C-03)",
        "HEAD": "봉제 헤드 묶음(고정 C-01, 헤드 회전 조인트는 T03 후보). 기종 D-10",
        "PRESSER": "노루발(들기 조인트, T03)",
        "NEEDLE": "바늘(내림 조인트, T03)",
    }
    for n, d in desc.items():
        C("component.metadata.set", {"component": n, "description": d, "bom_type": "phantom"})
    # 2) 작업 대상 모형
    mat_comps = []
    for key, m in MATS.items():
        segs = outline(m)
        base = "MAT_" + key
        # 2-1 생매트
        C("component.create", {"name": base, "activate": True})
        C("sketch.create", {"plane": "XY", "name": "SK_" + base})
        S.extend(sketch_cmds(segs))
        C("sketch.finish", {})
        C("solid.extrude", {"sketch": "SK_" + base, "profiles": "all", "distance": T_MAT, "body_name": base})
        # 2-2 가공 뒤 형상(테이프 감싼 가장자리)
        bn = base + "_BOUND"
        C("component.create", {"name": bn, "activate": True})
        C("sketch.create", {"plane": "XY", "name": "SK_" + bn + "_OUT"})
        S.extend(sketch_cmds(offset_outline(segs, TAPE_T)))
        C("sketch.finish", {})
        C("solid.extrude", {"sketch": "SK_" + bn + "_OUT", "profiles": "all", "distance": T_MAT + 2 * TAPE_T,
                            "start_offset": -TAPE_T, "body_name": bn})
        C("sketch.create", {"plane": "XY", "name": "SK_" + bn + "_IN"})
        S.extend(sketch_cmds(offset_outline(segs, -TAPE_W)))
        C("sketch.finish", {})
        C("solid.extrude", {"sketch": "SK_" + bn + "_IN", "profiles": "all", "distance": T_MAT + 2 * TAPE_T,
                            "start_offset": -TAPE_T, "operation": "cut", "targets": [bn]})
        C("sketch.create", {"plane": "XY", "name": "SK_" + bn + "_MAT"})
        S.extend(sketch_cmds(segs))
        C("sketch.finish", {})
        C("solid.extrude", {"sketch": "SK_" + bn + "_MAT", "profiles": "all", "distance": T_MAT,
                            "operation": "cut", "targets": [bn]})
        # 2-3 떨어진 조각(이음매 자리의 테이프 절단 끝단)
        sn = base + "_SCRAP"
        C("component.create", {"name": sn, "activate": True})
        C("solid.box", {"length": 2 * TAPE_W + T_MAT, "width": SCRAP_L, "height": TAPE_T,
                        "center": [0, m['W'] / 2 + TAPE_T + SCRAP_L / 2, T_MAT / 2], "body_name": sn})
        for n, d in ((base, f"작업 대상 모형 {m['label']} {m['L']:.0f}x{m['W']:.0f}x{T_MAT:.0f} mm(임시값 D-01·D-04)"),
                     (bn, f"가공 뒤 형상: 테이프 두께 {TAPE_T} 날개 {TAPE_W} mm(임시값 D-06)"),
                     (sn, f"떨어진 조각: 테이프 절단 끝단 {SCRAP_L} mm(임시값 D-07)")):
            C("component.metadata.set", {"component": n, "description": d, "bom_type": "reference"})
        mat_comps += [base, bn, sn]
    C("component.activate", {"component": "root"})
    # 3) 조인트 (모두 영점 자세에서 세계 원점 기준으로 맺는다)
    def J(t, a, b, name, z=None, limits=None, pt=(0, 0, 0)):
        oa = {"occurrence": a, "point": list(pt)}
        ob = {"occurrence": b, "point": list(pt)}
        if z:
            oa["z"] = z; ob["z"] = z
        prm = {"type": t, "a": oa, "b": ob, "flip": True, "name": name}
        if limits:
            prm["limits"] = limits
        C("joint.create", prm)
    J("slider", "BASE", "MAT_X", "J_MAT_X", z=[1, 0, 0], limits=[[-900, 900]])
    J("slider", "MAT_X", "MAT_Y", "J_MAT_Y", z=[0, 1, 0], limits=[[-900, 900]])
    J("revolute", "MAT_Y", "MAT_ROT", "J_MAT_ROT", z=[0, 0, 1])
    J("revolute", "BASE", "HEAD", "J_HEAD_ROT", z=[0, 0, 1], limits=[[-180, 180]])
    J("slider", "HEAD", "PRESSER", "J_PRESSER", z=[0, 0, 1], limits=[[0, PRESSER_LIFT]])
    J("slider", "HEAD", "NEEDLE", "J_NEEDLE", z=[0, 0, 1], limits=[[NEEDLE_DOWN, 0]])
    C("joint.rigid_group", {"occurrences": ["MAT_ROT"] + mat_comps})
    # 4) 동작 연구
    sb = STANDBY
    std_keys = [{"joint": j, "points": [[0, v], [1, v]]} for j, v in
                (("J_MAT_X", sb['x']), ("J_MAT_Y", sb['y']), ("J_MAT_ROT", sb['rot']), ("J_HEAD_ROT", sb['head']),
                 ("J_PRESSER", sb['presser']), ("J_NEEDLE", sb['needle']))]
    C("motion.study", {"name": "대기", "steps": 1, "keys": std_keys})
    studies = {}
    for key, m in MATS.items():
        st = build_study(key, m)
        studies[key] = st
        C("motion.study", {"name": st['name'], "steps": st['steps'], "keys": st['keys']})
    # 상태별 정밀 연구(꺾임 구간만, 키 1도·단계 2 mm/1도)
    fine = [('GROOVE', '상태_홈매트_홈', ('③ 홈 입구', 1, '③ 홈 입구', 2)),
            ('GROOVE', '상태_홈매트_오목모서리', ('③ 오목 모서리', 1, '③ 오목 모서리', 1)),
            ('LARGE', '상태_큰매트_볼록모서리', ('③ 볼록 모서리', 1, '③ 볼록 모서리', 1))]
    for key, nm, sub in fine:
        st = build_study(key, MATS[key], dk=FINE[1], ds=FINE[0], dth=FINE[2], sub=sub, name=nm, local=True)
        if key == 'LARGE':
            pass
        studies[nm] = st
        C("motion.study", {"name": nm, "steps": st['steps'], "keys": st['keys']})
    # 5) 대기 포즈로 돌린 뒤 확인
    C("motion.play", {"study": "대기", "step": 0})
    C("joint.list", {})
    C("motion.list", {})
    json.dump(S, open(os.path.join(OUT, "prep_build.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    info = dict(standby=STANDBY, values=dict(T_MAT=T_MAT, TAPE_T=TAPE_T, TAPE_W=TAPE_W, SCRAP_L=SCRAP_L, RC=RC, RCC=RCC,
                G_W=G_W, G_D=G_D, STANDBY_GAP=STANDBY_GAP, PRESSER_LIFT=PRESSER_LIFT, NEEDLE_DOWN=NEEDLE_DOWN,
                DS=DS, DTH=DTH, SHARP_R=SHARP_R),
                mats={k: dict(L=m['L'], W=m['W'], label=m['label']) for k, m in MATS.items()},
                studies={k: dict(name=v['name'], steps=v['steps'], nkeys=v['nkeys'], extent=v['extent'], states=v['states'])
                         for k, v in studies.items()})
    json.dump(info, open(os.path.join(OUT, "prep_info.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in studies.items():
        print(k, v['name'], 'steps', v['steps'], 'keys', v['nkeys'], v['extent'])

main()
