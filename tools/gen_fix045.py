# FIX-045 편집 기록 조립: 실제로 최종 결과를 만든 명령만 순서대로(탐색·실패·되돌린 것 제외)
import json
L=lambda n: json.load(open(n,encoding='utf-8'))
def nomeas(s): return [x for x in s if x['command'] not in('measure','inspect.measure','timeline.inspect')]
def C(c,**p): return {"command":c,"params":p}
def redef(fid,cmd,**p): return C("timeline.redefine",feature=fid,command=cmd,params=p)
E=[]
E+=[redef(1029,"solid.chamfer",body="P_M04_INSERT",distance="1",edges=[[-251.0,300.0,0.0],[-251.0,-300.0,0.0],[-380.0,151.0,0.0],[105.0,151.0,0.0],[11.0,65.0,0.0],[11.0,-65.0,0.0],[45.0,21.0,0.0]]),
    redef(1030,"solid.chamfer",body="P_M04_INSERT",distance="0.5",edges=[[-310.0,0.0,0.0]])]
E+=[C("timeline.roll_to",position=602),C("timeline.delete",feature=1065),C("component.activate",component=1062,occurrence=1063),
    C("solid.press_pull",face=[-381.482,2220.0,-45.653],distance="-1640",body="HFS8-4080-260_M04"),C("component.activate",component=0)]
E+=nomeas(L('stage_off_a.json'))
E+=[C("timeline.roll_to",feature=1989),
    redef(1988,"solid.chamfer",body="P_M04_INSERT",distance="1",edges=[[-251.0,315.0,0.0],[-251.0,-315.0,0.0],[-380.0,151.0,0.0],[105.0,151.0,0.0],[11.0,65.0,0.0],[11.0,-65.0,0.0],[45.0,21.0,0.0]]),
    redef(1989,"solid.chamfer",body="P_M04_INSERT",distance="0.5",edges=[[-310.0,0.0,0.0]])]
fl=lambda fid,body,pt,h,ang="90",**k: [C("timeline.roll_to",feature=fid),redef(fid,"sheet.flange",body=body,edges=[pt] if isinstance(pt[0],(int,float)) else pt,angle=ang,height=h,position="inside",**k)]
E+=[C("timeline.roll_to",feature=5083),C("timeline.suppress",feature=223,suppressed=True),
    redef(5083,"sheet.flange",body="P_M06_TOP_BRKT",edges=[[45.0,-88.0,571.0]],angle="90",height="52",position="inside"),
    C("timeline.suppress",feature=223,suppressed=False)]
E+=fl(5019,"P_M06_BASE",[-51.0,-90.0,151.0],"47")+fl(5020,"P_M06_BASE",[-142.0,-130.0,148.0],"31")
E+=fl(5047,"P_M06_SHOE",[-22.0,-155.0,14.5],"37.5")+fl(5048,"P_M06_SHOE",[-9.0,-235.0,14.5],"10.642","20")
E+=[C("solid.box",corner=[-23,-330,12],length=3.01,width=95,height=39,operation="cut",targets=["P_M06_SHOE"],name="FIX045_SHOE_WALL_TRIM")]
E+=fl(5076,"P_M06_G1_BRKT",[475.0,-85.0,560.0],"28")
E+=[C("timeline.roll_to",feature=9284),redef(9284,"solid.fillet",body="P_M07_BEAM",radius="12",edges=[[0.0,120.0,250.0],[0.0,320.0,250.0],[0.0,320.0,650.0],[0.0,120.0,650.0]])]
E+=fl(5293,"P_M07_SEAT_NX",[-2300.0,220.0,241.0],"100")+fl(5309,"P_M07_SEAT_PX",[1150.0,220.0,241.0],"100")
E+=nomeas(L('stage_off_x.json'))
E+=nomeas(L('stage_off_b1.json'))
rest=L('stage_off_pos_rest.json')
# 양(+) 오프셋 7개 가운데 OffsetFace22(6983, +470)는 뒤에서 지우고 −250 하나로 바꿨다 → 그 묶음과 e 묶음(9224~9226)은 빼고 아래에 실제 한 것으로 다시 적는다
out=[];skip=False;i=0
chunks=[];cur=[]
for st in rest:
    if st['command']=='timeline.roll_to' and cur and any(c['command']=='solid.press_pull' for c in cur): chunks.append(cur);cur=[]
    cur.append(st)
chunks.append(cur)
for ch in chunks:
    ids=[c['params'].get('feature') for c in ch if c['command']=='timeline.delete']
    if any(x in (6983,9224,9225,9226) for x in ids): continue
    E+=nomeas(ch)
E+=[C("timeline.roll_to",feature=9206),
    C("timeline.delete",feature=9225),C("component.activate",component=6984,occurrence=6985),C("solid.press_pull",face=[361.4822,-1593.6528,1530.0],distance="-725",body="HFS8-4080-1175_M08_FR"),C("component.activate",component=0),
    C("timeline.delete",feature=9226),C("component.activate",component=6987,occurrence=6988),C("solid.press_pull",face=[-2338.5178,86.3472,1530.0],distance="-725",body="HFS8-4080-1175_M08_R"),C("component.activate",component=0),
    C("timeline.delete",feature=9224),C("timeline.delete",feature=6983),C("component.activate",component=6980,occurrence=6981),C("solid.press_pull",face=[-2298.5178,-1593.6528,1060.0],distance="-250",body="HFS8-4080-1650_M08_FL"),C("component.activate",component=0)]
E+=nomeas(L('stage_cv0.json'))+nomeas(L('stage_cv1.json'))+nomeas(L('stage_cv2.json'))+nomeas(L('stage_cv3.json'))
E+=[C("timeline.roll_to",feature=8605),redef(8605,"sheet.flange",body="P_DC203_TRAY",edges=[[170.0,-40.0,-248.5],[-38.0,-158.0,-248.5],[170.0,-276.0,-248.5],[378.0,-158.0,-248.5]],angle="90",height="16.5",position="inside",corner_relief="1.5",corner_relief_shape="rectangular")]
E+=L('stage_pipes_dead.json')
E+=[C("timeline.roll_to",feature=95227),C("component.activate",component=32),
    C("solid.fillet",radius="3",body="P_M02_ARM_SIDE_N",edges=[[-214,-36.2026,139.1316],[-134,-36.2026,139.1316]],name="Fillet3_FIX045"),
    C("solid.fillet",radius="3",body="P_M02_ARM_SIDE_P",edges=[[-214,26.1556,124.7282],[-134,26.1556,124.7282]],name="Fillet4_FIX045"),
    C("component.activate",component=0),C("timeline.delete",features=[95228,95229])]
E+=[C("timeline.roll_to",feature=96816),redef(96816,"sheet.flange",body="P_M06_SHOE",edges=[[-80.0,-155.0,54.5]],angle="90",height="20",position="inside"),
    C("timeline.roll_to",feature=96826),redef(96826,"sheet.flange",body="P_M06_PCYL_BRKT",edges=[[-82.0,-149.0,77.3]],angle="90",height="19.7",position="inside")]
E+=[C("timeline.suppress",features=[95687,95689,95690,95691],suppressed=True)]
p=[x for x in L('stage_pipe98b.json') if not (x['command']=='timeline.delete' and x['params'].get('features')==[98452])]
p=nomeas(p)
# 새 관을 만든 뒤 옛 관·스케치를 지운다
k=[i for i,x in enumerate(p) if x['command']=='solid.pipe'][0]
p=p[:k+1]+[C("timeline.delete",features=[96032]),C("timeline.delete",features=[96031])]+p[k+1:]
E+=p
E+=[redef(98340,"solid.thread",face=[-1835.9,0.0,-24.0],designation="M5"),
    C("timeline.edit",feature=96817,set={"height":"10"}),
    C("timeline.roll_to",feature=95014),
    redef(95014,"solid.fillet",body="P_REG02_HGT_PLATE",radius="3",edges=[[-80.0,-96.5,157.0],[4.0,-96.5,157.0],[4.0,-96.5,287.0],[44.0,-96.5,287.0],[44.0,-96.5,330.0],[-14.0,-96.5,330.0],[-14.0,-96.5,195.0],[-80.0,-96.5,195.0]]),
    C("timeline.roll_to",position="end"),
    C("component.activate",component=0),C("component.rename",component=0,name="FSAP_v2.17.3"),
    C("document.metadata.set",key="description",value="FIX-045: repair of 103 features that failed to rebuild in SolidCraft 0.45.0 (no design change). U7 cassette items left suppressed for RX-14"),
    C("browser.visibility",visible=False,folder="joints"),C("browser.visibility",visible=False,folder="sketches"),
    C("motion.play",study="REST",step=0)]
json.dump(E,open('edit.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
R="C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/3D_Modeling/"
json.dump({"base":R+"FSAP_v2.17.2.sc","result":R+"FSAP_v2.17.3.sc","app":"SolidCraft 0.45.0 (e8ce12ef)","note":"MCP(앱) 세션에서 만든 기록. 다시 실행 확인은 하지 않았다(직렬 과제). press_pull이 만드는 스케치·돌출 id는 다시 실행하면 달라진다."},open('edit_meta.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
import collections
print(len(E),collections.Counter(x['command'] for x in E).most_common())
