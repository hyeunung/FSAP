# RX-01 주 공기 차단·잔압 배기 밸브 + 압력 스위치 명령 생성기 (v2.22.3 -> v2.22.4).
# 실행: python -B tools/gen_rx01.py  -> tools/out/mech_RX-01/model/stage_*.json (MCP batch path 로 순서대로 보냄)
# 좌표: 월드 mm, REST. 근거: docs/reports/mechanism/mech_RX-01_design.md R-4 지시서, mech_RX-01_design1.md 3절.
# 지시와 다른 것(보고서 2절): 보 탭 Z 299는 만든 피처를 찾지 못해 이력 끝 메움 피처(RX01_BEAM_FILL_299)로 없앰,
#   Z 261 탭(Cylinder1291)은 피처를 지움. TU0604_M08P_PSW 첫 직선 12 -> 11.99(엘보 입 끝 STEP 실측에 맞춤).
import json, math, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out', 'mech_RX-01', 'model')
STEP = os.path.join(os.path.dirname(ROOT), 'purchased-step').replace('\\', '/')
os.makedirs(OUT, exist_ok=True)

def C(cmd, **p): return {"command": cmd, "params": p}
def r4(v): return [round(float(x), 4) for x in v]
def box(name, x0, x1, y0, y1, z0, z1, op="new", tg=None, fname=None):
    p = dict(corner=r4([x0, y0, z0]), length=round(x1 - x0, 4), width=round(y1 - y0, 4), height=round(z1 - z0, 4), operation=op)
    if op == "new": p["body_name"] = name
    if tg: p["targets"] = tg
    if fname: p["name"] = fname
    return C("solid.box", **p)
def cyl(r, base, h, axis, op="new", tg=None, name=None, fname=None):
    p = dict(radius=r, height=h, base=r4(base), axis=axis, operation=op)
    if tg: p["targets"] = tg
    if name: p["body_name"] = name
    if fname: p["name"] = fname
    return C("solid.cylinder", **p)
def flat(cols, t):   # cols = 로컬 x·y·z 축의 월드 방향, row-major 3x4
    return [round(v, 9) for i in range(3) for v in (cols[0][i], cols[1][i], cols[2][i], t[i])]
def comp(name, body, pn, bom, desc, mat):
    return [C("material.assign", bodies=[body], material=mat),
            C("component.create", name=name, parent="U8_PNEU", activate=False),
            C("component.move_bodies", bodies=[body], component=name),
            C("component.metadata.set", component=name, part_number=pn, bom_type=bom, description=desc)]
X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]
W = "STEP대기_"
stages = {}

# ---- 1. 볼트·너트 사본(지울 :46에서 먼저 뜬다) — CB5-16 x4, HNTT8-5 x2
#   CB5-16_M08_PY:46 원점(머리 밑) (1159, 116, 261), 로컬 x = +Y.  HNTT8-5_M08_NY_PZ:1 원점 (-2360, 122.5, -300)
CB5 = [(1170, 114, 120), (1170, 114, 240), (1132, 116, 536), (1150, 116, 536)]
NUT = [(1170, 122.5, 120), (1170, 122.5, 240)]
stages['1_copies'] = (
    [C("occurrence.copy", occurrence="CB5-16_M08_PY:46", translate=[x - 1159, y - 116, z - 261]) for (x, y, z) in CB5] +
    [C("occurrence.copy", occurrence="HNTT8-5_M08_NY_PZ:1", translate=[x + 2360, y - 122.5, z + 300]) for (x, y, z) in NUT])

# ---- 2. 지우기: 마커를 첫 피처 앞으로 내리고 피처를 한 번에 지운 뒤 끝으로 올린다(다시 계산 한 번)
DEL = ([95903, 95904, 95905, 95906, 95907] +                                  # STEP대기_KQ2E08-00A_1
       [95908, 95909, 95910, 95911, 95912, 95913, 95916, 96687, 96688, 96689, 96690, 96691, 96692, 96693, 96694] +  # P_M08_AIR_IN_BRKT
       [95943, 95944, 95945, 95946] +                                         # STEP대기_TPH-01_2
       [96742])                                                               # 보 탭 Cylinder1291 (1159, Z 261)
stages['2a_rollback'] = [C("timeline.rollback", position=2026)]
stages['2b_delete'] = [C("timeline.delete", features=DEL)]
stages['2c_rollend'] = [C("timeline.rollback", position="end")]
stages['2d_deloccs'] = [C("selection.delete", components=[W + "KQ2E08-00A_1", "P_M08_AIR_IN_BRKT", W + "TPH-01_2"],
                          occurrences=["CB5-16_M08_PY:46", "CB5-16_M08_PY:47"])]

# ---- 3. 보: Z 299 탭 메움 + 스위치 받침 M5 탭 2 (U1_FRAME 활성)
stages['3_beam'] = [C("component.activate", component="U1_FRAME"),
                    cyl(2.5, [1159, 120, 299], 8, Y, "join", tg=["P_M07_BEAM"], fname="RX01_BEAM_FILL_299"),
                    cyl(2.1, [1132, 119.9, 536], 12.1, Y, "cut", tg=["P_M07_BEAM"], fname="RX01_BEAM_TAP_1"),
                    cyl(2.1, [1150, 119.9, 536], 12.1, Y, "cut", tg=["P_M07_BEAM"], fname="RX01_BEAM_TAP_2"),
                    C("component.activate", component="root")]

# ---- 4. 받침 판 + 밸브 임시 형상 + CB3-40 + 소음기
PL = "P_M08_VP_PLATE"
VP = W + "VP342-5DZ1-01A"
s4 = [C("component.activate", component="root"),
      box(PL, 1150, 1190, 114, 120, 111, 249, fname="RX01_VP_PLATE"),
      cyl(2.75, [1170, 113.9, 120], 6.2, Y, "cut", tg=[PL], fname="RX01_VP_PLATE_H1"),
      cyl(2.75, [1170, 113.9, 240], 6.2, Y, "cut", tg=[PL], fname="RX01_VP_PLATE_H2"),
      cyl(1.25, [1170, 113.9, 183], 6.2, Y, "cut", tg=[PL], fname="RX01_VP_PLATE_M3_1"),
      cyl(1.25, [1170, 113.9, 223], 6.2, Y, "cut", tg=[PL], fname="RX01_VP_PLATE_M3_2")]
s4 += comp(PL, PL, PL, "normal",
           "Main air valve mounting plate, A5052 flat bar t6 40x138, drill 2x D5.5 + tap 2x M3 through (milling 1 setup, provisional); "
           "2x CB5-16 + HNTT8-5 into column front T-slot X 1170 (RX-01)", "A5052")
# 밸브: 몸 상자 + (파일럿 + DIN) L꼴 한 스케치(바깥 면 Y 86·111이 같은 평면이라 상자 둘 join은 거부됨)
s4 += [box(VP, 1150, 1190, 83, 114, 174, 232, fname="RX01_VP_BODY"),
       C("sketch.create", plane={"origin": [0, 111, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}, name="SK_RX01_VP_PILOT"),
       C("sketch.line", points=[[1107.3, 136], [1155, 136], [1155, 129.1], [1185, 129.1], [1185, 174], [1155, 174], [1155, 164], [1107.3, 164]], closed=True),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_RX01_VP_PILOT", distance=25, operation="new", body_name=VP + "_PD", name="RX01_VP_PILOT"),
       C("solid.combine", target=VP, tools=[VP + "_PD"], operation="join"),
       cyl(4.3, [1149.9, 98.5, 203], 9.1, X, "cut", tg=[VP], fname="RX01_VP_PORT_A"),
       cyl(4.3, [1181, 98.5, 192.55], 9.1, X, "cut", tg=[VP], fname="RX01_VP_PORT_P"),
       cyl(4.3, [1181, 98.5, 213.45], 9.1, X, "cut", tg=[VP], fname="RX01_VP_PORT_R"),
       cyl(1.6, [1170, 82.9, 183], 31.2, Y, "cut", tg=[VP], fname="RX01_VP_MNT_1"),
       cyl(1.6, [1170, 82.9, 223], 31.2, Y, "cut", tg=[VP], fname="RX01_VP_MNT_2")]
s4 += comp(VP, VP, "VP342-5DZ1-01A", "purchased",
           "STEP pending (E-10): SMC VP342-5DZ1-01A 3-port solenoid valve N.C., Rc1/8, DIN terminal, DC24V. Placeholder: outline 102.9(Z) x 31(Y) x 82.7(X) "
           "and P-R pitch 20.9 from catalog (VP p.1057-1062); body 40x58, pilot, DIN, port faces (A on -X, P/R on +X), 2x D3.2 through pitch 40 temporary (RX-01)",
           "Default")
stages['4_valve'] = s4

def cb3(name, x, z, y_head0, y_tip, ln, desc):
    """M3 육각 렌치 볼트 임시 형상: 머리 D5.5 x 3(CB3-10 STEP 치수) + 축 D3 x ln. 머리 y_head0~+3 또는 반대."""
    d = 1 if y_tip > y_head0 else -1
    if d > 0:   # 머리 -Y 쪽, 축 +Y
        hb, sb, kb = y_head0, y_head0 + 3, y_head0 - 0.1
    else:       # 머리 +Y 쪽, 축 -Y
        hb, sb, kb = y_head0, y_tip, y_head0 + 3 - 1.6
    return ([cyl(2.75, [x, hb, z], 3, Y, "new", name=name, fname="RX01_%s_HEAD" % name[len(W):]),
             cyl(1.5, [x, sb, z], ln, Y, "join", tg=[name], fname="RX01_%s_SHANK" % name[len(W):]),
             cyl(1.25, [x, kb, z], 1.7, Y, "cut", tg=[name], fname="RX01_%s_SOCKET" % name[len(W):])] +
            comp(name, name, name[len(W):], "purchased", desc, "SCM435"))
s5 = cb3(W + "CB3-40", 1170, 183, 80, 123, 40,
         "STEP pending: hex socket head cap screw M3x40 (Misumi CB3-40), head D5.5x3 as CB3-10 STEP + shank 40; valve 2x D3.2 through -> plate M3 tap (U-12 exception: purchased part hole fixes M3) (RX-01)")
s5.append(C("occurrence.copy", occurrence=W + "CB3-40:1", translate=[0, 0, 40]))
AN = W + "AN110-01_3"
s5 += [cyl(5.5, [1190, 98.5, 213.45], 23, X, "new", name=AN, fname="RX01_AN110_BODY"),
       cyl(4.0, [1186, 98.5, 213.45], 4, X, "join", tg=[AN], fname="RX01_AN110_THREAD")]
s5 += comp(AN, AN, "AN110-01", "purchased", "STEP wait: SMC silencer R1/8 (D11 L23 temp) on main valve R port, exhaust to +X (RX-01)", "Default")
stages['5_bolts_sil'] = s5

# ---- 6. 이음(실물 STEP). 로컬: 나사 축 = y(나사 끝 -y), 관 입 = +x, 관 축은 y = 15.6(KQ2L08) / 14.2(KQ2L06), 좌면 y = 5.8 / 6.8
sA, cA = 9.5 / math.hypot(9.5, 77), 77 / math.hypot(9.5, 77)       # A 엘보 기울기 7.03도
s50, c50 = math.sin(math.radians(50)), math.cos(math.radians(50))
KQ = [("KQ2L08-01AS_M08V_A", "KQ2L08-01AS", [[0, sA, cA], [-1, 0, 0], [0, -cA, sA]], (1155.8, 98.5, 203),
       "SMC KQ2L08-01AS elbow R1/8-OD8 on main valve A port (-X face X 1150), tube mouth up tilted 7.03 deg -> TU0805_M08P_MAIN_1 (RX-01)"),
      ("KQ2L08-01AS_M08V_P", "KQ2L08-01AS", [[0, 0, -1], [1, 0, 0], [0, -1, 0]], (1184.2, 98.5, 192.55),
       "SMC KQ2L08-01AS elbow R1/8-OD8 on main valve P port (+X face X 1190), tube mouth down = factory air inlet OD8 (factory tube not modelled) (RX-01)"),
      ("KQ2L06-01AS_M08V_PSW", "KQ2L06-01AS", [[0, -s50, c50], [1, 0, 0], [0, c50, s50]], (1131.2, 107.5, 351),
       "SMC KQ2L06-01AS elbow R1/8-OD6 on manifold +X end plate P port (was plug TPH-01_2), mouth 50 deg from vertical toward -Y -> TU0604_M08P_PSW (RX-01)")]
s6 = [C("component.activate", component="root")]
for (name, spec, cols, t, desc) in KQ:
    s6 += [C("file.insert_step", path="%s/%s/%s.stp" % (STEP, spec, spec), name=name, matrix=flat(cols, t)),
           C("body.rename", body=spec, name=name),
           C("component.metadata.set", component=name, part_number=spec, bom_type="purchased", description=desc),
           C("material.assign", bodies=[name], material="Default"),
           C("occurrence.reparent", occurrence=name + ":1", parent="U8_PNEU")]
stages['6_fittings'] = s6

# ---- 7. 관
def unit(v):
    n = math.sqrt(sum(x * x for x in v)); return [x / n for x in v]
def arcmid(st, ce, en):
    R = math.dist(st, ce)
    m = unit([(st[i] - ce[i]) + (en[i] - ce[i]) for i in range(3)])
    return [ce[i] + m[i] * R for i in range(3)]
def tube(name, segs, dia, sk):
    c = [C("sketch.create", plane="XY", name=sk), C("sketch.options", sketch_3d=True)]
    L = 0.0
    for s in segs:
        if s[0] == "l":
            c.append(C("sketch.line3d", points=[r4(s[1]), r4(s[2])])); L += math.dist(s[1], s[2])
        else:
            st, ce, en = s[1], s[2], s[3]
            R = math.dist(st, ce)
            ang = math.acos(max(-1, min(1, sum((st[i] - ce[i]) * (en[i] - ce[i]) for i in range(3)) / R / R)))
            c.append(C("sketch.arc3d", start=r4(st), through=r4(arcmid(st, ce, en)), end=r4(en))); L += R * ang
    c += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (i + 1) for i in range(len(segs))], diameter=dia, operation="new", body_name=name,
            name="PIPE_%s_RX01" % name)]
    return c, L
# MAIN_1: 티 1 +X 끝 -> 클램프 -> R 28.2 -> A 엘보 입 끝
cM = [1112, 104.547, 252.012]
uA = [0, sA, cA]
aS = [cM[i] + 28.2 * uA[i] for i in range(3)]                  # (1112, 108.0, 280.0)
aE = [1140.2, cM[1], cM[2]]
mouthA = [1140.2, 98.5 + 16.4 * sA, 203 + 16.4 * cA]           # (1140.2, 100.508, 219.277)
M_segs = [("l", [998, 108, 280], aS), ("a", aS, cM, aE), ("l", aE, mouthA)]
tM, LM = tube("TU0805_M08P_MAIN_1", M_segs, 8.0, "SK_TU0805_M08P_MAIN_1_RX01")
# PSW: 끝판 엘보 입 끝 -> 직선 -> R 20 (50도) -> +Z -> S 굽힘 R 30 x2 -> +Z -> 스위치 엘보 입 끝
m50 = [0, -s50, c50]
p0 = [1145.4, 107.5 + 15.5 * m50[1], 351 + 15.5 * m50[2]]      # 엘보 입 끝 (1145.4, 95.626, 360.963)
L1 = (p0[1] - (99.30 - 20 * c50)) / s50                         # 호 중심 Y 99.30에 맞춘 직선 길이(11.99)
p1 = [p0[i] + L1 * m50[i] for i in range(3)]
c1 = [1145.4, 99.30, p1[2] + 20 * s50]
e1 = [1145.4, 79.30, c1[2]]
th = math.acos(1 - 4.4 / 60.0)                                  # 22.07도
a2s = [1145.4, 79.30, 420.0]; c2 = [1115.4, 79.30, 420.0]
a2e = [c2[0] + 30 * math.cos(th), 79.30, 420.0 + 30 * math.sin(th)]
c3 = [a2e[0] + 30 * math.cos(th), 79.30, a2e[2] + 30 * math.sin(th)]
a3e = [c3[0] - 30, 79.30, c3[2]]                                # (1141.0, 79.3, 442.553)
endS = [1141.0, 79.30, 470.5]
S_segs = [("l", p0, p1), ("a", p1, c1, e1), ("l", e1, a2s), ("a", a2s, c2, a2e), ("a", a2e, c3, a3e), ("l", a3e, endS)]
tS, LS = tube("TU0604_M08P_PSW", S_segs, 6.0, "SK_TU0604_M08P_PSW")
s7 = [C("component.activate", component="root"),
      C("solid.remove", bodies=["TU0805_M08P_MAIN_1"], name="RM_TU0805_M08P_MAIN_1_RX01")] + tM + [
      C("material.assign", bodies=["TU0805_M08P_MAIN_1"], material="Default"),
      C("component.move_bodies", bodies=["TU0805_M08P_MAIN_1"], component="TU0805_M08P_MAIN_1"),
      C("component.metadata.set", component="TU0805_M08P_MAIN_1", part_number="TU0805", bom_type="purchased",
        description="SMC TU0805 polyurethane tube OD8, main supply: valve A elbow -> R 28.2 bend -> clamp L_1 -> tee 1, cut length %.1f (RX-01, min bend R 20)" % LM)]
s7 += tS + comp("TU0604_M08P_PSW", "TU0604_M08P_PSW", "TU0604", "purchased",
                "SMC TU0604 polyurethane tube OD6, manifold +X end plate P -> pressure switch, cut length %.1f, bends R 20/30/30 (RX-01, min bend R 15)" % LS, "Default")
stages['7_tubes'] = s7

# ---- 8. 압력 스위치 임시 형상 + 받침 + CB3-8
SW = W + "ISE20-N-M-C6L-L"
BK = "P_M08_PSW_BRKT"
s8 = [C("component.activate", component="root"),
      box(SW, 1126, 1156, 45, 70, 471, 501, fname="RX01_PSW_BODY"),
      cyl(4.7, [1141, 70, 486], 9.3, Y, "join", tg=[SW], fname="RX01_PSW_STEM"),          # 뒤 엘보 가로 Y 70~79.3
      cyl(4.7, [1141, 79.30, 470.5], 20.2, Z, "join", tg=[SW], fname="RX01_PSW_ELBOW"),   # 세로 Z 470.5~490.7, Y 74.6~84
      cyl(1.25, [1131, 65.9, 486], 4.2, Y, "cut", tg=[SW], fname="RX01_PSW_M3_1"),        # 뒤 M3 탭 깊이 4(임시)
      cyl(1.25, [1151, 65.9, 486], 4.2, Y, "cut", tg=[SW], fname="RX01_PSW_M3_2")]
s8 += comp(SW, SW, "ISE20-N-M-C6L-L", "purchased",
           "STEP pending (E-10): SMC ISE20-N-M-C6L-L digital pressure switch, body 30x30x25 from catalog (ISE20 p.9-21), display to -Y; "
           "rear one-touch OD6 elbow (mouth down), rear 2x M3 tap pitch 20 depth 4 temporary (RX-01)", "Default")
s8 += [C("sketch.create", plane={"origin": [1124, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_RX01_PSW_BRKT"),
       C("sketch.line", points=[[70, 466], [74, 466], [74, 512], [120, 512], [120, 552], [116, 552], [116, 516], [70, 516]], closed=True),
       C("sketch.finish"),
       C("solid.extrude", sketch="SK_RX01_PSW_BRKT", distance=34, operation="new", body_name=BK, name="RX01_PSW_BRKT"),
       C("solid.fillet", edges=[[1141, 74, 512], [1141, 116, 516]], radius=4, body=BK, name="RX01_PSW_BRKT_RIN"),
       C("solid.fillet", edges=[[1141, 70, 516], [1141, 120, 512]], radius=8, body=BK, name="RX01_PSW_BRKT_ROUT"),
       cyl(8.0, [1141, 69.9, 486], 4.2, Y, "cut", tg=[BK], fname="RX01_PSW_BRKT_D16"),
       cyl(1.7, [1131, 69.9, 486], 4.2, Y, "cut", tg=[BK], fname="RX01_PSW_BRKT_D34_1"),
       cyl(1.7, [1151, 69.9, 486], 4.2, Y, "cut", tg=[BK], fname="RX01_PSW_BRKT_D34_2"),
       cyl(2.75, [1132, 115.9, 536], 4.2, Y, "cut", tg=[BK], fname="RX01_PSW_BRKT_D55_1"),
       cyl(2.75, [1150, 115.9, 536], 4.2, Y, "cut", tg=[BK], fname="RX01_PSW_BRKT_D55_2")]
s8 += comp(BK, BK, BK, "normal",
           "Pressure switch bracket, A5052 t4 sheet metal Z shape, 2 bends inner R4 (provisional); front flange D16 + 2x D3.4, wall flange 2x D5.5 -> "
           "2x CB5-16 into beam front wall M5 taps (RX-01)", "A5052")
s8 += cb3(W + "CB3-8", 1131, 486, 74, 66, 8,
          "STEP pending: hex socket head cap screw M3x8 (Misumi CB3-8), head D5.5x3 as CB3-10 STEP + shank 8; switch bracket front flange -> switch rear M3 tap (U-12 exception) (RX-01)")
s8.append(C("occurrence.copy", occurrence=W + "CB3-8:1", translate=[20, 0, 0]))
stages['8_switch'] = s8

# ---- 9. 리지드 묶음(STEP으로 넣은 이음) — 사본·컴포넌트 바디는 U8_PNEU 안에 그대로
stages['9_rigid'] = [C("joint.rigid_group", occurrences=["U8_PNEU:1"] + [k[0] + ":1" for k in KQ])]

order = ['1_copies', '2a_rollback', '2b_delete', '2c_rollend', '2d_deloccs', '3_beam', '4_valve', '5_bolts_sil', '6_fittings', '7_tubes', '8_switch', '9_rigid']
allc = []
for k in order:
    json.dump(stages[k], open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    allc += stages[k]
json.dump(allc, open(os.path.join(os.path.dirname(OUT), 'edit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({"MAIN_1": {"len": round(LM, 2), "segs": [[s[0]] + [r4(p) for p in s[1:]] for s in M_segs]},
           "PSW": {"len": round(LS, 2), "L1": round(L1, 3), "segs": [[s[0]] + [r4(p) for p in s[1:]] for s in S_segs]}},
          open(os.path.join(OUT, 'tubes.json'), 'w', encoding='utf-8'), indent=1)
print("stages", {k: len(stages[k]) for k in order}, "MAIN_1 %.2f PSW %.2f L1 %.3f" % (LM, LS, L1))
print("mouthA", r4(mouthA), "p0", r4(p0), "p1", r4(p1), "c1", r4(c1), "a3e", r4(a3e))
