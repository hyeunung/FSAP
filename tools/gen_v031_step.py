# v0.3.0 -> v0.3.1: STEP대기_* 임시 형상을 미스미 실물 STEP(purchased-step/)으로 바꾼다.
# 바꾸는 것: HFS8-4080-1300·460·1900·580(10), LHFR16(6), PSFJ16-150(6). 나머지 STEP대기는 형번 미정·CAD 없음(자료대기).
# 배치: 임시 형상의 컴포넌트 로컬 바운딩 박스(tools/out/v031/insp_out.json, 대기 자세)에 맞춘다.
#   STEP 원래 좌표: 모두 +X가 길이 방향, 원점이 한쪽 끝. HFS8 단면 Y 80 x Z 40, PSFJ16 Ø16, LHFR16 플랜지 X 0~6(Ø48)·몸통 X 6~37(Ø28).
#   LHFR16은 플랜지 밑면(X 6)을 스파이더 윗면 Z -85에 얹는다(플랜지 Z -85~-79, 몸통 아래로 -116까지).
# 쓰는 법: python -B tools/gen_v031_step.py stage1  -> tools/out/v031/stage1.json
#   solidcraft-cli run stage1.json --in 3D_Modeling/FSAP_v0.3.0.sc --save tools/out/v031/stage1.sc --results > stage1_out.json
#          python -B tools/gen_v031_step.py stage2  -> tools/out/v031/stage2.json (stage1_out.json의 바디 이름을 읽는다)
#   solidcraft-cli run stage2.json --in tools/out/v031/stage1.sc --save 3D_Modeling/FSAP_v0.3.1.sc
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'v031')
STEP = os.path.join(ROOT, 'purchased-step').replace('\\', '/')
LEN = {'HFS8-4080-1300': 1300, 'HFS8-4080-460': 460, 'HFS8-4080-1900': 1900, 'HFS8-4080-580': 580, 'PSFJ16-150': 150}

# 원래 축(X, Y, Z)이 가는 로컬 방향
ALONG_Y = ((0, 1, 0), (0, 0, 1), (1, 0, 0))     # 길이 Y, 80 Z, 40 X
ALONG_X = ((1, 0, 0), (0, 0, 1), (0, -1, 0))    # 길이 X, 80 Z, 40 Y
UP_Z80Y = ((0, 0, 1), (0, 1, 0), (-1, 0, 0))    # 길이 Z, 80 Y, 40 X
UP_Z = ((0, 0, 1), (1, 0, 0), (0, 1, 0))        # 길이 Z(축)
DOWN_Z = ((0, 0, -1), (1, 0, 0), (0, -1, 0))    # 길이 -Z(LHFR16 플랜지 위)

# (부모 컴포넌트, 임시 바디, 형번, 축 방향, 이름 꼬리)
PH = json.load(open(os.path.join(OUT, 'insp_out.json'), encoding='utf-8'))
BB = {}


def walk(o):
    if isinstance(o, dict):
        if 'name' in o and 'bbox' in o:
            BB[o['name']] = (o['bbox']['min'], o['bbox']['max'])
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(PH[2])
JOBS = []
for s in ('L', 'R'):
    JOBS.append(('MAT_X', 'STEP대기_HFS8-4080-1300_' + s, 'HFS8-4080-1300', ALONG_Y, s))
for s in ('F', 'B'):
    JOBS.append(('MAT_X', 'STEP대기_HFS8-4080-460_' + s, 'HFS8-4080-460', ALONG_X, s))
    JOBS.append(('BASE', 'STEP대기_HFS8-4080-1900_' + s, 'HFS8-4080-1900', ALONG_X, s))
for s in ('P1', 'P2'):
    JOBS.append(('BASE', 'STEP대기_HFS8-4080-460_' + s, 'HFS8-4080-460', UP_Z80Y, s))
for s in ('T1', 'T2'):
    JOBS.append(('BASE', 'STEP대기_HFS8-4080-580_' + s, 'HFS8-4080-580', ALONG_Y, s))
for r in ('R1', 'R2'):
    for i in (1, 2, 3):
        JOBS.append(('MAT_ROT', 'STEP대기_LHFR16_%s_%d' % (r, i), 'LHFR16', DOWN_Z, '%s_%d' % (r, i)))
        JOBS.append(('RING1' if r == 'R1' else 'RING2', 'STEP대기_PSFJ16-150_%s_%d' % (r, i), 'PSFJ16-150', UP_Z, '%s_%d' % (r, i)))


def matrix(axes, pn, ph):
    (lo, hi) = BB[ph]
    ex, ey, ez = axes
    c = [(lo[k] + hi[k]) / 2 for k in range(3)]
    if pn == 'LHFR16':
        t = [c[0], c[1], -79.0]
    else:
        # 원점(길이 방향 시작, 단면 중심)을 임시 박스의 길이 방향 낮은 끝·단면 중심에 둔다
        k = [abs(v) for v in ex].index(1)
        t = list(c)
        t[k] = lo[k] if ex[k] > 0 else hi[k]
        assert abs((hi[k] - lo[k]) - LEN[pn]) < 1e-6, (ph, hi[k] - lo[k])
    R = [[ex[i], ey[i], ez[i]] for i in range(3)]
    return [R[i] + [round(t[i], 4)] for i in range(3)]


def nm(pn, tail):
    return '%s_%s' % (pn, tail)


if sys.argv[1] == 'stage1':
    S = []
    for comp, ph, pn, ax, tail in JOBS:
        S.append({"command": "component.activate", "params": {"component": comp}})
        S.append({"command": "file.insert_step", "params": {"path": "%s/%s/%s.stp" % (STEP, pn, pn), "name": nm(pn, tail),
                                                            "matrix": matrix(ax, pn, ph)}})
    S.append({"command": "component.activate", "params": {"component": "root"}})
    json.dump(S, open(os.path.join(OUT, 'stage1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump([list(j[:3]) + [j[4]] for j in JOBS], open(os.path.join(OUT, 'jobs.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(JOBS), 'inserts')
else:
    R1 = [r for r in json.load(open(os.path.join(OUT, 'stage1_out.json'), encoding='utf-8')) if isinstance(r, dict) and 'created_bodies' in r]
    assert len(R1) == len(JOBS)
    S = []
    MATS = {}
    DESC = {'HFS8-4080-1300': '알루미늄 프레임 8 시리즈 40x80 L1300', 'HFS8-4080-460': '알루미늄 프레임 8 시리즈 40x80 L460',
            'HFS8-4080-1900': '알루미늄 프레임 8 시리즈 40x80 L1900', 'HFS8-4080-580': '알루미늄 프레임 8 시리즈 40x80 L580',
            'LHFR16': '플랜지붙이 리니어 부시 Ø16 역 카운터보어', 'PSFJ16-150': '리니어 샤프트 Ø16 L150'}
    for (comp, ph, pn, ax, tail), r in zip(JOBS, R1):
        assert r['name'] == nm(pn, tail) and len(r['created_bodies']) == 1, r
        S.append({"command": "body.rename", "params": {"body": r['created_bodies'][0], "name": nm(pn, tail)}})
        MATS.setdefault('Aluminum' if pn.startswith('HFS8') else 'Steel', []).append(nm(pn, tail))
        S.append({"command": "component.metadata.set", "params": {"component": nm(pn, tail), "part_number": pn, "bom_type": "purchased",
                                                                 "description": "MISUMI %s (%s 자리)" % (DESC[pn], ph.replace('STEP대기_', ''))}})
    for m, bs in MATS.items():
        S.append({"command": "material.assign", "params": {"bodies": bs, "material": m}})
    for comp in ('MAT_X', 'BASE', 'MAT_ROT', 'RING1', 'RING2'):
        S.append({"command": "component.activate", "params": {"component": comp}})
        S.append({"command": "solid.remove", "params": {"bodies": [j[1] for j in JOBS if j[0] == comp]}})
    S.append({"command": "component.activate", "params": {"component": "root"}})
    S.append({"command": "document.metadata.set", "params": {"values": {"description": "v0.3.1: MISUMI STEP for HFS8 frames, LHFR16, PSFJ16-150 (placeholders replaced)"}}})
    S.append({"command": "motion.play", "params": {"study": "대기", "step": 0}})
    json.dump(S, open(os.path.join(OUT, 'stage2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(S), 'steps')
