# RX-19 수정 1회차(v2.29.0 -> v2.29.1): 스토퍼 사슬을 경로 3(PM 판정 RX19-EX1)으로 다시 그린다.
# 스토퍼 몸 축 (Y 47.5, Z 216) X -232~-184.5, 로드 -X로 당김/밂, L자 세운 판 + 스톱 발 한 덩어리,
# 주 실린더 관 A2·B와 스토퍼 관 2줄을 쓸림 자리 밖으로 다시 깐다. 출력: tools/out/mech_RX-19/model1/stage_*.json
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out', 'mech_RX-19', 'model1')
os.makedirs(OUT, exist_ok=True)
def C(cmd, **p): return {"command": cmd, "params": p}
CYL = "STEP대기_CDQ2A25-20DMZ"
ROD = "STEP대기_CDQ2A25-20DMZ_ROD"
PLATE = "P_RX08_STOP_BLOCK_밀링"
NUT = "STEP대기_NUT-M10_RX19"
AY, AZ = 47.5, 216.0          # 스토퍼 축
stages = {}

# A: 조인트 풀기, 옛 바디 걷기, 옮기기
A = [C("joint.delete", joint=j) for j in (100752, 100741, 100742, 100743, 100744, 100745, 100746, 100747, 100748, 100864)]
A += [C("solid.remove", bodies=["STEP대기_JA30-8-125", PLATE, ROD], name="RM_RX19F1_STOP_PARTS")]
A += [C("occurrence.move", occurrence="U4_STOP:1", space="world", to_matrix=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])]
A += [C("occurrence.move", occurrence=CYL + ":1", space="world", matrix=[[-1, 0, 0, -576.5], [0, 0, 1, -110.5], [0, 1, 0, 168.8]])]
for occ, y in (("CB5-16_RX08_LIP:1", 60.2), ("CB5-16_RX08_LIP:2", 60.2), ("CB5-16_RX08_LIP:3", 34.2), ("CB5-16_RX08_LIP:4", 34.2)):
    A.append(C("occurrence.move", occurrence=occ, space="world", matrix=[[-1, 0, 0, -576.5], [0, -1, 0, round(2 * y + 0.3, 4)], [0, 0, 1, 58]]))
A.append(C("occurrence.move", occurrence="KQ2L06-M5A_RX08_ROD:1", space="world", matrix=[[1, 0, 0, 126.5], [0, 0, 1, -110.5], [0, -1, 0, 263.2]]))
A.append(C("occurrence.move", occurrence="KQ2L06-M5A_RX08_HEAD:1", space="world", matrix=[[0, 1, 0, -239.2], [0, 0, 1, -110.5], [1, 0, 0, 600.5]]))
A.append(C("occurrence.move", occurrence="KQ2L06-M5A_M02S_ROD:1", space="world", matrix=[[0, 1, 0, -257.02], [-1, 0, 0, -222.98], [0, 0, 1, 0]]))
stages['A'] = A

# B: U4_STOP 새 바디(월드 = 컴포넌트 좌표)
hx = -266.75
hexa = [[AY + 8, AZ - 4.6188], [AY + 8, AZ + 4.6188], [AY, AZ + 9.2376], [AY - 8, AZ + 4.6188], [AY - 8, AZ - 4.6188], [AY, AZ - 9.2376]]
B = [C("component.activate", component="U4_STOP"),
     C("solid.cylinder", radius=6, height=43, base=[-255, AY, AZ], axis="X", operation="new", body_name=ROD, name="RX19F1_ROD"),
     C("solid.cylinder", radius=5, height=11, base=[-266, AY, AZ], axis="X", operation="join", targets=[ROD], name="RX19F1_ROD_M10"),
     C("material.assign", bodies=[ROD], material="Steel"),
     C("solid.box", corner=[-270, 29, 150], length=40, width=36.4, height=16, operation="new", body_name=PLATE, name="RX19F1_STOP_FOOT"),
     C("solid.box", corner=[-270, 37, 166], length=14.5, width=21, height=58, operation="join", targets=[PLATE], name="RX19F1_STOP_PLATE"),
     C("solid.box", corner=[-267, 39, 206.2], length=8.5, width=17, height=18.3, operation="cut", targets=[PLATE], name="RX19F1_STOP_TSLOT_NUT"),
     C("solid.box", corner=[-258.6, 42, 210.5], length=3.2, width=11, height=14, operation="cut", targets=[PLATE], name="RX19F1_STOP_TSLOT_NECK"),
     C("material.assign", bodies=[PLATE], material="SUS304"),
     C("sketch.create", plane={"origin": [hx, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}, name="SK_RX19F1_NUT"),
     C("sketch.line", points=hexa, closed=True),
     C("sketch.finish"),
     C("solid.extrude", sketch="SK_RX19F1_NUT", distance=8, operation="new", body_name=NUT, name="EX_RX19F1_NUT"),
     C("solid.cylinder", radius=5, height=8.2, base=[hx - 0.1, AY, AZ], axis="X", operation="cut", targets=[NUT], name="RX19F1_NUT_BORE"),
     C("material.assign", bodies=[NUT], material="Steel"),
     C("component.activate", component="root")]
stages['B'] = B

# C: 블록(U4_XCAR, 월드 = 컴포넌트 좌표, J_U4_X 0)
Cs = [C("timeline.delete", features=["RX19_BLK_TUBE_HOLE_C1", "RX19_BLK_TUBE_HOLE_C2", "RX19_BLK_TUBE_HOLE_C3", "RX19_BLK_TUBE_HOLE_C4",
                                     "RX19_BLK_STOP_HOLE_1", "RX19_BLK_STOP_HOLE_2", "RX19_BLK_STOP_HOLE_3", "RX19_BLK_STOP_HOLE_4", "RX19_BLK_STOP_LEG"]),
      C("component.activate", component="U4_XCAR"),
      C("solid.box", corner=[-405, 24.5, 235], length=75, width=46, height=16, operation="cut", targets=["P_RX19_BLOCK_밀링"], name="RX19F1_BLK_STRIP_CUT"),
      C("solid.box", corner=[-184.5, 27.5, 196], length=12, width=40, height=40, operation="join", targets=["P_RX19_BLOCK_밀링"], name="RX19F1_BLK_STOP_LEG")]
for i, (y, z) in enumerate(((60.5, 203), (60.5, 229), (34.5, 203), (34.5, 229)), 1):
    Cs.append(C("solid.cylinder", radius=2.75, height=14, base=[-185.5, y, z], axis="X", operation="cut", targets=["P_RX19_BLOCK_밀링"], name="RX19F1_BLK_STOP_HOLE_%d" % i))
for i, (x, y, h) in enumerate(((-179.506, 17.02, 16), (-296, 50, 16), (-225, 81, 30), (-192, 81, 30)), 1):
    Cs.append(C("solid.cylinder", radius=4, height=h, base=[x, y, 235], axis="Z", operation="cut", targets=["P_RX19_BLOCK_밀링"], name="RX19F1_BLK_TUBE_HOLE_%d" % i))
Cs.append(C("component.activate", component="root"))
stages['C'] = Cs

# D: 관 4줄(굽힘 R10)
s45 = 10 * (1 - math.cos(math.radians(45)))  # 2.9289
c45 = 10 * math.sin(math.radians(45))        # 7.0711
def L(a, b): return ("l", a, b)
def Ar(a, t, b): return ("a", a, t, b)
r = lambda v: [round(x, 4) for x in v]
XR = -179.506
A2 = [L([-225.5, 17.02, 211.5], [XR - 10, 17.02, 211.5]),
      Ar([XR - 10, 17.02, 211.5], [XR - 10 + c45, 17.02, 211.5 + s45], [XR, 17.02, 221.5]),
      L([XR, 17.02, 221.5], [XR, 17.02, 273]),
      Ar([XR, 17.02, 273], [XR, 17.02 + s45, 273 + c45], [XR, 27.02, 283]),
      L([XR, 27.02, 283], [XR, 69, 283]),
      Ar([XR, 69, 283], [XR + s45, 69 + c45, 283], [XR + 10, 79, 283]),
      Ar([XR + 10, 79, 283], [XR + 10 + c45, 79, 283 + s45], [XR + 20, 79, 293]),
      L([XR + 20, 79, 293], [XR + 20, 79, 340])]
XB = -296
Bt = [L([-254.5, -26.48, 211.5], [XB + 10, -26.48, 211.5]),
      Ar([XB + 10, -26.48, 211.5], [XB + 10 - c45, -26.48 + s45, 211.5], [XB, -16.48, 211.5]),
      L([XB, -16.48, 211.5], [XB, 40, 211.5]),
      Ar([XB, 40, 211.5], [XB, 40 + c45, 211.5 + s45], [XB, 50, 221.5]),
      L([XB, 50, 221.5], [XB, 50, 261]),
      Ar([XB, 50, 261], [XB, 50 + s45, 261 + c45], [XB, 60, 271]),
      Ar([XB, 60, 271], [XB + s45, 60 + c45, 271], [XB + 10, 70, 271]),
      L([XB + 10, 70, 271], [-169.506, 70, 271]),
      Ar([-169.506, 70, 271], [-169.506 + c45, 70, 271 + s45], [-159.506, 70, 281]),
      L([-159.506, 70, 281], [-159.506, 70, 340])]
# RX08_A: 로드 쪽 포트 X -225 -> (-169, 88, 340). Z 312에서 S 굽힘으로 Y 81 -> 88
al = math.acos(0.65); sa, ca = math.sin(al), math.cos(al); sh, ch = math.sin(al / 2), math.cos(al / 2)
c1 = (-215.0, 91.0); e1 = (c1[0] + 10 * sa, c1[1] - 10 * ca); t1 = (c1[0] + 10 * sh, c1[1] - 10 * ch)
c2 = (e1[0] + 10 * sa, e1[1] - 10 * ca + 0)  # 반대 굽힘 중심
c2 = (2 * e1[0] - c1[0], 2 * e1[1] - c1[1])
e2 = (c2[0], c2[1] + 10); t2 = (c2[0] - 10 * sh, c2[1] + 10 * ch)
RA = [L([-225, 81, 230.5], [-225, 81, 302]),
      Ar([-225, 81, 302], [-225 + s45, 81, 302 + c45], [-215, 81, 312]),
      Ar([-215, 81, 312], [t1[0], t1[1], 312], [e1[0], e1[1], 312]),
      Ar([e1[0], e1[1], 312], [t2[0], t2[1], 312], [e2[0], e2[1], 312]),
      L([e2[0], e2[1], 312], [-179, 88, 312]),
      Ar([-179, 88, 312], [-179 + c45, 88, 312 + s45], [-169, 88, 322]),
      L([-169, 88, 322], [-169, 88, 340])]
RB = [L([-192, 81, 230.5], [-192, 81, 292]),
      Ar([-192, 81, 292], [-192, 81 - s45, 292 + c45], [-192, 71, 302]),
      Ar([-192, 71, 302], [-182 - c45, 71 - c45, 302], [-182, 61, 302]),
      L([-182, 61, 302], [-179, 61, 302]),
      Ar([-179, 61, 302], [-179 + c45, 61, 302 + s45], [-169, 61, 312]),
      L([-169, 61, 312], [-169, 61, 340])]
D = []
for name, path in (("TU0604_M08P_U4_A2_U4", A2), ("TU0604_M08P_U4_B_U4", Bt), ("TU0604_M08P_RX08_A_U4", RA), ("TU0604_M08P_RX08_B_U4", RB)):
    sk = "SK_%s_RX19F1" % name
    D += [C("solid.remove", bodies=[name], name="RM_%s_RX19F1" % name),
          C("component.activate", component=name),
          C("sketch.create", plane="XY", name=sk),
          C("sketch.options", sketch_3d=True)]
    for seg in path:
        if seg[0] == "l": D.append(C("sketch.line3d", points=[r(seg[1]), r(seg[2])]))
        else: D.append(C("sketch.arc3d", start=r(seg[1]), through=r(seg[2]), end=r(seg[3])))
    D += [C("sketch.finish"),
          C("solid.pipe", path_sketch=sk, path=["w%d" % (i + 1) for i in range(len(path))], diameter=6.0, operation="new", body_name=name, name="PIPE_%s_RX19F1" % name),
          C("material.assign", bodies=[name], material="Default"),
          C("component.activate", component="root")]
stages['D'] = D

# E: 조인트 다시 맺기
E = [C("joint.rigid_group", occurrences=["U4_WHEEL_N:1", CYL + ":1", "CB5-16_RX08_LIP:1", "CB5-16_RX08_LIP:2", "CB5-16_RX08_LIP:3", "CB5-16_RX08_LIP:4",
                                         "KQ2L06-M5A_RX08_HEAD:1", "KQ2L06-M5A_RX08_ROD:1"]),
     C("joint.rigid_group", occurrences=["U4S_CYL:1", "KQ2L06-M5A_M02S_ROD:1"]),
     C("joint.as_built", type="slider", a=CYL + ":1", b="U4_STOP:1", at={"occurrence": CYL + ":1", "point": [-240, AY, AZ], "z": [-1, 0, 0]}, name="J_U4_STOP", limits=[[0, 20]])]
stages['E'] = E
for k, v in stages.items():
    json.dump(v, open(os.path.join(OUT, 'stage_%s.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(k, len(v))
print('e1', e1, 'e2', e2)
