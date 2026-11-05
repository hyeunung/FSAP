import json
R="C:/Users/hyeun/OneDrive/Documents/workspace/FSAP/purchased-step/"
s=[]
# 1 new Y member under tray -X end, on :3 top
s+= [{"command":"file.insert_step","params":{"path":R+"HFS8-4080-1140/HFS8-4080-1140.stp","name":"HFS8-4080-300_DC203","matrix":[0,0,1,-18.0,1,0,0,-280.0,0,1,0,-290.0]}},
 {"command":"body.rename","params":{"body":"Boss-Extrude1","name":"HFS8-4080-300_DC203"}},
 {"command":"solid.offset_face","params":{"faces":[[0.5178,860.0,-283.6528]],"distance":-840.0,"body":"HFS8-4080-300_DC203"}},
 {"command":"component.metadata.set","params":{"component":"HFS8-4080-300_DC203","part_number":"HFS8-4080-300","bom_type":"purchased","description":"Misumi HFS8-4080-1140 STEP, end face offset to L300 (DC2-03 fix1 tray -X support)"}},
 {"command":"material.assign","params":{"bodies":["HFS8-4080-300_DC203"],"material":"Aluminum"}},
 {"command":"occurrence.reparent","params":{"occurrence":"HFS8-4080-300_DC203:1","parent":"U1_FRAME"}}]
# 2 end caps
for nm,m in [("HFC8-4080-B_DC203_S",[0,1,0,-18.0,0,0,1,-280.0,1,0,0,-290.0]),("HFC8-4080-B_DC203_N",[0,-1,0,-18.0,0,0,-1,20.0,1,0,0,-290.0])]:
  s+=[{"command":"file.insert_step","params":{"path":R+"HFC8-4080-B/HFC8-4080-B.stp","name":nm,"matrix":m}},
      {"command":"body.rename","params":{"body":"Fillet2","name":nm}},
      {"command":"component.metadata.set","params":{"component":nm,"part_number":"HFC8-4080-B","bom_type":"purchased"}},
      {"command":"material.assign","params":{"bodies":[nm],"material":"Default"}},
      {"command":"occurrence.reparent","params":{"occurrence":nm+":1","parent":"U1_FRAME"}}]
# 3 brackets to :3 top (same as M07 LBRKT joints)
for o in ["P_M07_LBRKT_PX_PZ:1","HNTT8-5_M07K_PZ_PX:1","CB5-16_M07K_NZ:1","HNTT8-5_M07K_PX_PY:19","CB5-16_M07K_NX:19"]:
  s.append({"command":"occurrence.copy","params":{"occurrence":o,"in_place":True,"translate":[2262.0,0.0,0.0]}})
for o in ["P_M07_LBRKT_NX_PZ:1","HNTT8-5_M07K_PZ_PX:9","CB5-16_M07K_NZ:9","HNTT8-5_M07K_NX_PY:5","CB5-16_M07K_PX:5"]:
  s.append({"command":"occurrence.copy","params":{"occurrence":o,"in_place":True,"translate":[-1148.0,0.0,0.0]}})
# 4 tray holes + bolts at X -18
for y in (-230.0,-170.0):
  s.append({"command":"solid.cylinder","params":{"radius":2.75,"height":4,"base":[-18.0,y,-251.0],"axis":"Z","operation":"cut","targets":["P_DC203_TRAY"]}})
for dy in (0.0,60.0):
  s.append({"command":"occurrence.copy","params":{"occurrence":"CB5-12_DC203:1","in_place":True,"translate":[-378.0,dy,0.0]}})
  s.append({"command":"occurrence.copy","params":{"occurrence":"HNTT8-5_DC203:1","in_place":True,"translate":[-378.0,dy,0.0]}})
# 5 final
s+=[{"command":"joint.rigid_group","params":{"occurrences":["U1_FRAME:1","HFS8-4080-300_DC203:1","HFC8-4080-B_DC203_S:1","HFC8-4080-B_DC203_N:1"]}},
 {"command":"motion.play","params":{"study":"REST","step":0,"quiet":True}},
 {"command":"browser.visibility","params":{"visible":False,"folder":"joints"}},
 {"command":"document.metadata.set","params":{"key":"description","value":"DC2-03 mechanism fix1: tray -X end support HFS8-4080-300 on lower rail, 2 LBRKT, caps, CB5-12 x2"}}]
json.dump(s,open("tools/out/mech_DC2-03/edit_fix1.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print(len(s))
