# T07 로딩·배출(모델링부) 생성기: v0.5.1 -> v0.6.0 (새 묶음 T07 = 작업자 쪽 고정 가드틀, 부 번호 +1)
# 선정 지시서 docs/reports/mechanism/mech_T07_select.md(T07-C1 수정안, B1~B9) 그대로.
# 좌표: 대기 세계 좌표(P-02: 바늘점 원점, 매트 밑면 Z 0, 작업자 쪽 -Y). 단위 mm. BASE는 세계와 같은 자리(원점 0).
#   * STEP은 root에 세계 행렬(3x4 행 우선)로 넣고 occurrence.reparent(세계 위치 유지)로 옮긴다(gen_s01_step.py 방식).
#   * HFS8 STEP 원래 좌표: +X 길이, 원점 = 한쪽 끝·단면 중심, 단면 Y 80 x Z 40(gen_v031_step.py).
#   * HFC8 캡 STEP: Z0 면 = 끝면, +Z = 형재 안쪽, X = 80 방향(gen_s01_step.py CAPS). 8 끼우고 3 나온다.
#   * 형재 STEP이 없는 길이(2850·680·1580, D-41)는 같은 외곽 상자 STEP대기_<형번>_<tag>(E-10).
# 쓰는 법(Git Bash, 프로젝트 루트):
#   python -B tools/gen_t07_mech.py stage1  -> tools/out/mech_T07/model/stage1.json (root에 STEP 넣기)
#   python -B tools/gen_t07_mech.py stage2 <stage1 결과 json>  -> stage2.json (stage1이 만든 바디 이름을 읽는다)
#   모델링부는 두 스크립트를 SolidCraft MCP batch로 v0.5.1에 차례로 보내고 save {path: 3D_Modeling/FSAP_v0.6.0.sc}.
#   CLI로 다시 만들 때: solidcraft-cli run stage1.json --in v0.5.1 --save s1.sc --results > s1_out.json,
#                       stage2 s1_out.json, solidcraft-cli run stage2.json --in s1.sc --save FSAP_v0.6.0.sc
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T07', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
S = []


def C(c, p):
    S.append({"command": c, "params": p})


def r6(v):
    return round(v, 6)


# ---------------- 형재(B2): (태그, 형번, bbox x0,x1,y0,y1,z0,z1, 길이 축, 80 축, 설명) ----------------
FR = [
    ('2850_G1', 'HFS8-4080-2850', (-1425, 1425, -1740, -1700, -680, -600), 'X', 'Z', '아래 가로대 G1(받침면 Z -680)'),
    ('2850_G4', 'HFS8-4080-2850', (-1425, 1425, -1740, -1700, -140, -60), 'X', 'Z', '위 가로대 G4(윗면 Z -60 = 판 윗변)'),
    ('680_SL', 'HFS8-4080-680', (-930, -890, -1700, -1020, -680, -600), 'Y', 'Z', '이음대 G2 왼쪽(1900_F 앞면 Y -1020 맞댐)'),
    ('680_SR', 'HFS8-4080-680', (890, 930, -1700, -1020, -680, -600), 'Y', 'Z', '이음대 G2 오른쪽(1900_F 앞면 Y -1020 맞댐)'),
    ('460_GL', 'HFS8-4080-460', (-950, -870, -1740, -1700, -600, -140), 'Z', 'X', '중간 기둥 왼쪽(G1 윗면 ~ G4 아랫면)'),
    ('460_GR', 'HFS8-4080-460', (870, 950, -1740, -1700, -600, -140), 'Z', 'X', '중간 기둥 오른쪽(G1 윗면 ~ G4 아랫면)'),
    ('1580_PL', 'HFS8-4080-1580', (-1505, -1425, -1740, -1700, -680, 900), 'Z', 'X', '끝 기둥 왼쪽(받침면 Z -680 ~ 900)'),
    ('1580_PR', 'HFS8-4080-1580', (1425, 1505, -1740, -1700, -680, 900), 'Z', 'X', '끝 기둥 오른쪽(받침면 Z -680 ~ 900)'),
]
AX = {'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}


def has_step(pn):
    return os.path.isfile(SP + pn + '/' + pn + '.stp')


def frame_matrix(bb, la, wa):
    # STEP X(길이) -> 세계 la, STEP Y(80) -> 세계 wa, STEP Z(40) = X x Y(오른손)
    ex, ey = AX[la], AX[wa]
    ez = (ex[1] * ey[2] - ex[2] * ey[1], ex[2] * ey[0] - ex[0] * ey[2], ex[0] * ey[1] - ex[1] * ey[0])
    c = [(bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2, (bb[4] + bb[5]) / 2]
    k = 'XYZ'.index(la)
    c[k] = bb[2 * k]
    return [ex[0], ey[0], ez[0], c[0], ex[1], ey[1], ez[1], c[1], ex[2], ey[2], ez[2], c[2]]


# ---------------- 마감캡(B3): (이름, 형재 태그, 끝면 중심, 안쪽 n) ----------------
CAPS = []
for tag, x in (('PL', -1465), ('PR', 1465)):
    CAPS.append(('HFC8-4080-B_1580_%s_ZP' % tag, '1580_' + tag, (x, -1720, 900), (0, 0, -1)))
    CAPS.append(('HFC8-4080-B_1580_%s_ZM' % tag, '1580_' + tag, (x, -1720, -680), (0, 0, 1)))


def cap_matrix(p, n):
    ex = (1, 0, 0)    # 80 방향 = 세계 X
    ey = (n[1] * ex[2] - n[2] * ex[1], n[2] * ex[0] - n[0] * ex[2], n[0] * ex[1] - n[1] * ex[0])
    return [ex[0], ey[0], n[0], p[0], ex[1], ey[1], n[1], p[1], ex[2], ey[2], n[2], p[2]]


# ---------------- 판(B4): SUS304 t2 레이저 평판, Y -1740 XZ 스케치를 -Y로 2 ----------------
ZB, ZT = -680.0, -60.0
PL = {
    'P_T07_SKIRT_C': [(-909.5, ZB), (909.5, ZB), (909.5, ZT), (5, ZT), (0, ZT - 5), (-5, ZT), (-909.5, ZT)],
    'P_T07_SKIRT_L': [(-1505, ZB), (-910.5, ZB), (-910.5, ZT), (-1505, ZT)],
    'P_T07_SKIRT_R': [(910.5, ZB), (1505, ZB), (1505, ZT), (910.5, ZT)],
}
PL_DESC = {
    'P_T07_SKIRT_C': 'SUS304 / 레이저 절단 평판 t2(굽힘 없음) / X-909.5~909.5 · Y-1742~-1740 · Z-680~-60, 윗변 X0 V홈 10x5(로딩 X 기준, D-40). 구멍은 디테일링(CB5-12 + M5 T너트, D-41)',
    'P_T07_SKIRT_L': 'SUS304 / 레이저 절단 평판 t2(굽힘 없음) / X-1505~-910.5 · Y-1742~-1740 · Z-680~-60(C와 틈 1). 구멍은 디테일링',
    'P_T07_SKIRT_R': 'SUS304 / 레이저 절단 평판 t2(굽힘 없음) / X910.5~1505 · Y-1742~-1740 · Z-680~-60(C와 틈 1). 구멍은 디테일링',
}


def frame_name(tag):
    return 'HFS8-4080-' + tag


INS = []    # (insert 이름, 형번, 행렬, 옮길 부모)
for tag, pn, bb, la, wa, desc in FR:
    if has_step(pn):
        INS.append((frame_name(tag), pn, frame_matrix(bb, la, wa), 'T07'))
for nm, ftag, p, n in CAPS:
    INS.append((nm, 'HFC8-4080-B', cap_matrix(p, n), frame_name(ftag)))

if sys.argv[1] == 'stage1':
    C("component.activate", {"component": "root"})
    for nm, pn, M, par in INS:
        C("file.insert_step", {"path": SP + pn + '/' + pn + '.stp', "name": nm, "matrix": M})
    json.dump(S, open(os.path.join(OUT, 'stage1.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(S), 'steps')
    sys.exit()

# ================= stage2 =================
# stage1 결과(file.insert_step 응답 목록)에서 insert마다 만든 바디 이름
R1 = json.load(open(sys.argv[2], encoding='utf-8'))
R1 = R1.get('results', R1) if isinstance(R1, dict) else R1
R1 = [r for r in R1 if isinstance(r, dict) and 'created_bodies' in r]
assert len(R1) == len(INS), (len(R1), len(INS))
BODY = {INS[i][0]: R1[i]['created_bodies'] for i in range(len(INS))}

# 1) T07 컴포넌트(BASE 아래)와 STEP대기 형재 컴포넌트
C("component.create", {"name": "T07", "parent": "BASE", "activate": True, "grounded": False})
WAIT = []
for tag, pn, bb, la, wa, desc in FR:
    if has_step(pn):
        continue
    nm = frame_name(tag)
    C("component.create", {"name": nm, "parent": "T07", "activate": True, "grounded": False})
    b = 'STEP대기_%s_%s' % (pn, tag.split('_')[1])
    C("solid.box", {"length": r6(bb[1] - bb[0]), "width": r6(bb[3] - bb[2]), "height": r6(bb[5] - bb[4]),
                    "center": [r6((bb[0] + bb[1]) / 2), r6((bb[2] + bb[3]) / 2), r6((bb[4] + bb[5]) / 2)], "body_name": b})
    WAIT.append(b)
    C("component.activate", {"component": "T07"})

# 2) 판 3장(T07 바로 아래, 한 스케치 한 바디)
for b, pts in PL.items():
    sk = 'SK_' + b
    C("sketch.create", {"plane": {"origin": [0, -1740, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, "name": sk})
    C("sketch.line", {"points": [[r6(x), r6(z)] for x, z in pts], "closed": True})
    C("sketch.finish", {})
    C("solid.extrude", {"sketch": sk, "profiles": "all", "distance": 2, "body_name": b})
C("component.activate", {"component": "root"})

# 3) STEP 옮기기: 형재 -> T07, 캡 -> 끝 기둥 형재 컴포넌트
for nm, pn, M, par in INS:
    C("occurrence.reparent", {"occurrence": nm + ":1", "parent": par})

# 4) 바디 이름·재질(E-09)
REN = {}
for nm, pn, M, par in INS:
    bs = BODY[nm]
    if len(bs) == 1:
        REN[bs[0]] = nm
    else:
        for i, b in enumerate(bs):
            REN[b] = '%s_%d' % (nm, i + 1)
for old, new in REN.items():
    if old != new:
        C("body.rename", {"body": old, "name": new})
alu = WAIT + [REN[b] for nm, pn, M, par in INS if pn.startswith('HFS8') for b in BODY[nm]]
nyl = [REN[b] for nm, pn, M, par in INS if pn.startswith('HFC8') for b in BODY[nm]]
C("material.assign", {"bodies": alu, "material": "Aluminum"})
C("material.assign", {"bodies": nyl, "material": "Nylon"})
C("material.assign", {"bodies": list(PL), "material": "SUS304"})

# 5) 속성(BOM)
for tag, pn, bb, la, wa, desc in FR:
    nm = frame_name(tag)
    L = pn.split('-')[-1]
    wait = '' if has_step(pn) else ' — STEP 대기 임시 외곽 상자(E-10, D-41)'
    C("component.metadata.set", {"component": nm, "part_number": pn,
                                 "bom_type": "inseparable" if tag.startswith('1580') else "purchased",
                                 "description": "MISUMI 알루미늄 프레임 8 시리즈 40x80 L%s (T07 %s)%s" % (L, desc, wait)})
for nm, ftag, p, n in CAPS:
    C("component.metadata.set", {"component": nm, "part_number": "HFC8-4080-B", "bom_type": "purchased",
                                 "description": "MISUMI HFS8 시리즈용 프레임 캡 4080 폴리아미드 검정 (%s 끝면)" % nm.replace('HFC8-4080-B_', '')})
C("component.metadata.set", {"component": "T07", "bom_type": "phantom", "properties": PL_DESC,
                             "description": "로딩·배출 가드틀(T07, 고정 부품, BASE와 리지드). 작업자 쪽 -Y, 판 앞면 Y -1742 = 서는 선, 커튼 검출면 Y -1720 자리(검사 상자 K_T07_*). 선정 T07-C1 수정안. 브래킷 HBLFSN8 x24·판 체결은 안 그림(E-02)"})

# 6) 리지드(M-07): T07은 BASE와 함께 고정. 새 조인트 0
C("joint.rigid_group", {"occurrences": ["BASE:1", "T07:1"]})

C("document.metadata.set", {"values": {"description": "T07 mechanism: fixed operator-side guard frame (HFS8-4080 x8, HFC8 caps x4, SUS304 t2 skirts x3), manual unload, curtain/auto-eject zones"}})
C("motion.play", {"study": "대기", "step": 0, "quiet": True})
json.dump(S, open(os.path.join(OUT, 'stage2.json'), 'w', encoding='utf-8'), ensure_ascii=False)
NEW = WAIT + list(PL) + list(REN.values())
json.dump({"ins": INS, "rename": REN, "wait": WAIT, "plates": list(PL), "new_bodies": NEW,
           "frames": [frame_name(f[0]) for f in FR], "caps": [c[0] for c in CAPS]},
          open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(S), 'steps; new bodies', len(NEW))
