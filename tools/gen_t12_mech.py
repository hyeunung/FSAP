# T12 옆·뒤 커버(모델링부) 생성기: v0.6.15 -> v0.7.0 (부품 묶음 T12 신설, 부 번호 +1, 요구서 8-2·E-05)
# 선정 지시서 docs/reports/mechanism/mech_T12_select.md 10절(T12-S) 그대로.
# 좌표: 세계 대기(바늘점 원점, 매트 밑면 Z 0, 헤드 쪽 +Y), mm. R(+X)을 적고 L은 X 거울.
#   * 형재 STEP이 없는 길이(2600·380·960·1580·2850·1420, D-41)는 외곽 상자 STEP대기_<형번>_<tag>(E-10), gen_t07_mech.py와 같은 방식.
#   * 캡 HFC8-4080-B는 root에 세계 행렬로 넣고(stage1) occurrence.reparent로 Q 기둥 컴포넌트에 옮긴다.
#   * 문 P_T12_DOOR는 판금(SUS304_t2_R2): 기본 판 + 네 변 edge flange 22(외곽 Y 920~942).
# 쓰는 법: python -B tools/gen_t12_mech.py stage1 -> tools/out/mech_T12/model/stage1.json
#          python -B tools/gen_t12_mech.py stage2 <stage1 결과 json> -> stage2.json
#          python -B tools/gen_t12_mech.py door -> door.json, python -B tools/gen_t12_mech.py joint -> joint.json
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out', 'mech_T12', 'model')
SP = os.path.join(ROOT, 'purchased-step').replace('\\', '/') + '/'
os.makedirs(OUT, exist_ok=True)
S = []


def C(c, p):
    S.append({"command": c, "params": p})


def mx(bb):
    return (-bb[1], -bb[0], bb[2], bb[3], bb[4], bb[5])


# ---------------- 형재(지시 2) ----------------
FR_R = [
    ('2600_T12_SLB', 'HFS8-4080-2600', (1465, 1505, -1700, 900, -680, -600), '옆 아래 가로대(앞 1580_P* 뒷면 Y-1700, 뒤 Q 앞면 Y900 맞댐)'),
    ('2600_T12_SLM', 'HFS8-4080-2600', (1465, 1505, -1700, 900, -220, -140), '옆 가운데 가로대(A4/A5 밑 6)'),
    ('2600_T12_SLT', 'HFS8-4080-2600', (1465, 1505, -1700, 900, 820, 900), '옆 위 가로대'),
    ('380_T12_SPL', 'HFS8-4080-380', (1465, 1505, -90, -10, -600, -220), '옆 아래 이음 기둥(SLB 윗면~SLM 밑면)'),
    ('960_T12_SPU', 'HFS8-4080-960', (1465, 1505, -90, -10, -140, 820), '옆 위 이음 기둥(SLM 윗면~SLT 밑면)'),
    ('1580_T12_Q', 'HFS8-4080-1580', (1425, 1505, 900, 940, -672, 892), '뒤 모서리 기둥(실물 Z-680~900, 상자는 캡 끼움 8 비움)'),
    ('1420_T12_D', 'HFS8-4080-1420', (460, 540, 900, 940, -600, 820), '문 기둥(BB 윗면~BT 밑면)'),
]
FR = []
for tag, pn, bb, d in FR_R:
    FR.append((tag + '_R', pn, bb, d + ' 오른쪽'))
    FR.append((tag + '_L', pn, mx(bb), d + ' 왼쪽'))
FR.append(('2850_T12_BB', 'HFS8-4080-2850', (-1425, 1425, 900, 940, -680, -600), '뒤 아래 가로대(Q_L/Q_R 안쪽 면 맞댐)'))
FR.append(('2850_T12_BT', 'HFS8-4080-2850', (-1425, 1425, 900, 940, 820, 900), '뒤 위 가로대'))


def comp_name(tag):
    return 'HFS8-4080-' + tag


def body_name(tag, pn):
    return 'STEP대기_' + comp_name(tag)


# ---------------- 마감캡(지시 3) ----------------
CAPS = []
for s, x in (('R', 1465), ('L', -1465)):
    CAPS.append(('HFC8-4080-B_T12_Q_%s_ZP' % s, '1580_T12_Q_' + s, (x, 920, 900), (0, 0, -1)))
    CAPS.append(('HFC8-4080-B_T12_Q_%s_ZM' % s, '1580_T12_Q_' + s, (x, 920, -680), (0, 0, 1)))


def cap_matrix(p, n):
    ex = (1, 0, 0)    # 80 방향 = 세계 X (T07 1580 캡과 같음)
    ey = (n[1] * ex[2] - n[2] * ex[1], n[2] * ex[0] - n[0] * ex[2], n[0] * ex[1] - n[1] * ex[0])
    return [ex[0], ey[0], n[0], p[0], ex[1], ey[1], n[1], p[1], ex[2], ey[2], n[2], p[2]]


# ---------------- 판(지시 4): SUS304 t2 레이저 평판 ----------------
PL_R = [
    ('SL_RF', (1505, 1507, -1742, -50.5, -680, -180.5), '옆 아래 앞 정비판(떼는 판) 1691.5x499.5'),
    ('SL_RR', (1505, 1507, -49.5, 942, -680, -180.5), '옆 아래 뒤 정비판(떼는 판) 991.5x499.5'),
    ('SU_RF', (1505, 1507, -1742, -50.5, -179.5, 900), '옆 위 앞판 1691.5x1079.5(D-13 채택 때 A4/A5 창 1300x148 낸 판으로 교체, T12-S05)'),
    ('SU_RR', (1505, 1507, -49.5, 942, -179.5, 900), '옆 위 뒤판 991.5x1079.5'),
]
PL = []
for tag, bb, d in PL_R:
    PL.append(('P_T12_' + tag, bb, d + ' 오른쪽'))
    PL.append(('P_T12_' + tag.replace('_R', '_L'), mx(bb), d + ' 왼쪽'))
PL.append(('P_T12_BK_R', (460, 1505, 940, 942, -680, 900), '뒤판 오른쪽 1045x1580'))
PL.append(('P_T12_BK_L', (-1505, -460, 940, 942, -680, 900), '뒤판 왼쪽 1045x1580'))


def r6(v):
    return round(v, 6)


def box(bb, name):
    C("solid.box", {"length": r6(bb[1] - bb[0]), "width": r6(bb[3] - bb[2]), "height": r6(bb[5] - bb[4]),
                    "center": [r6((bb[0] + bb[1]) / 2), r6((bb[2] + bb[3]) / 2), r6((bb[4] + bb[5]) / 2)],
                    "body_name": name, "operation": "new"})


DOOR = 'P_T12_DOOR'
DOOR_DESC = 'SUS304 / 판금 t2 안R2, 레이저+절곡 4변 안쪽(-Y) 접힘 22(외곽 Y920~942), 네 모서리 따냄(용접 없음) / 판 X-458.5~458.5 · Z-598.5~818.5(917x1417), 둘레 틈 1.5. 경첩·걸쇠·인터록 구멍은 형번 뒤(디테일링)'
JP = [-459.25, 943.0, 0.0]

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stage1':
        C("component.activate", {"component": "root"})
        for nm, ftag, p, n in CAPS:
            C("file.insert_step", {"path": SP + 'HFC8-4080-B/HFC8-4080-B.stp', "name": nm, "matrix": cap_matrix(p, n)})
        json.dump(S, open(os.path.join(OUT, 'stage1.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        print(len(S), 'steps')
    elif mode == 'stage2':
        R1 = json.load(open(sys.argv[2], encoding='utf-8'))
        BODY = {CAPS[i][0]: R1[i] for i in range(len(CAPS))}   # cap 이름 -> 만든 바디 이름 목록
        C("component.create", {"name": "T12", "parent": "BASE", "activate": True, "grounded": False})
        WAIT = []
        for tag, pn, bb, d in FR:
            C("component.create", {"name": comp_name(tag), "parent": "T12", "activate": True, "grounded": False})
            b = body_name(tag, pn)
            box(bb, b)
            WAIT.append(b)
            C("component.activate", {"component": "T12"})
        for nm, bb, d in PL:
            box(bb, nm)
        C("component.activate", {"component": "root"})
        for nm, ftag, p, n in CAPS:
            C("occurrence.reparent", {"occurrence": nm + ":1", "parent": comp_name(ftag)})
        REN = {}
        for nm, ftag, p, n in CAPS:
            bs = BODY[nm]
            REN.update({b: (nm if len(bs) == 1 else '%s_%d' % (nm, i + 1)) for i, b in enumerate(bs)})
        for old, new in REN.items():
            if old != new:
                C("body.rename", {"body": old, "name": new})
        C("material.assign", {"bodies": WAIT, "material": "Aluminum"})
        C("material.assign", {"bodies": list(REN.values()), "material": "Nylon"})
        C("material.assign", {"bodies": [p[0] for p in PL], "material": "SUS304"})
        for tag, pn, bb, d in FR:
            L = pn.split('-')[-1]
            C("component.metadata.set", {"component": comp_name(tag), "part_number": pn,
                                         "bom_type": "inseparable" if tag.startswith('1580') else "purchased",
                                         "description": "MISUMI 알루미늄 프레임 8 시리즈 40x80 L%s (T12 %s) — STEP 대기 임시 외곽 상자(E-10, D-41)" % (L, d)})
        for nm, ftag, p, n in CAPS:
            C("component.metadata.set", {"component": nm, "part_number": "HFC8-4080-B", "bom_type": "purchased",
                                         "description": "MISUMI HFS8 시리즈용 프레임 캡 4080 폴리아미드 검정 (%s 끝면)" % nm.replace('HFC8-4080-B_', '')})
        props = {nm: 'SUS304 / 레이저 절단 평판 t2(굽힘 없음) / X%g~%g · Y%g~%g · Z%g~%g, %s. 구멍은 디테일링(CB5-12 + HNTT8-5, D-41)' % (bb + (d,)) for nm, bb, d in PL}
        C("component.metadata.set", {"component": "T12", "bom_type": "phantom", "properties": props,
                                     "description": "옆·뒤 고정 커버(T12, BASE와 리지드). 형재 HFS8-4080 x16(STEP 대기), 캡 HFC8-4080-B x4, SUS304 t2 평판 x10, 뒤 정비 문 칸 X±460 · Z-600~820(문 T12_DOOR). 브래킷 HBLFSN8·판 체결은 안 그림(E-02)"})
        C("joint.rigid_group", {"occurrences": ["BASE:1", "T12:1"]})
        json.dump(S, open(os.path.join(OUT, 'stage2.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        json.dump({"frames": [comp_name(f[0]) for f in FR], "wait": WAIT, "plates": [p[0] for p in PL],
                   "caps": list(REN.values()), "fr": FR, "pl": PL},
                  open(os.path.join(OUT, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(len(S), 'steps; new bodies', len(WAIT) + len(PL) + len(REN))
    elif mode == 'door':
        C("component.activate", {"component": "root"})
        C("component.create", {"name": "T12_DOOR", "activate": True, "grounded": False})
        C("sheet.manage_rules", {"name": "SUS304_t2_R2", "thickness": 2, "k_factor": 0.44, "bend_radius": 2, "active": True})
        sk = 'SK_P_T12_DOOR'
        C("sketch.create", {"plane": {"origin": [0, 942, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, "name": sk})
        C("sketch.rectangle.two_point", {"p0": [-458.5, -598.5], "p1": [458.5, 818.5]})
        C("sketch.finish", {})
        C("sheet.flange", {"type": "base", "sketch": sk, "rule": "SUS304_t2_R2", "body_name": DOOR})
        json.dump(S, open(os.path.join(OUT, 'door.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        print(len(S), 'steps')
