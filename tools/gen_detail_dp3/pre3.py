"""DP-3 사전 측정 3: 지울 탭 4개 둘레(쓰는 부품 유무), 덮개 볼트 자리 바깥(머리·렌치 길), 재질 목록."""
import json, q
rays=[]; tags=[]
def R(tag,o,d): rays.append({'origin':o,'dir':d}); tags.append(tag)
for x in (-255,-225):
    for dx,dy in ((0,0),(4,0),(-4,0),(0,4),(0,-4)): R('botTap%d'%x,[x+dx,248+dy,150],[0,0,1])
for z in (522,534):
    for dx,dz in ((0,0),(4,0),(-4,0)): R('frontTap%d'%z,[-345+dx,20,z+dz],[0,1,0])
for x in (-2362,1332):
    for z in (350,550):
        R('capF',[x,-200,z],[0,1,0]); R('capB',[x,700,z],[0,-1,0])
        R('capF+5',[x,-200,z+5],[0,1,0]); R('capB+5',[x,700,z+5],[0,-1,0])
u=q.call('pick3',{'tool':'execute','arguments':{'command':'view.pick','params':{'rays':rays}}})
hs=u['data'].get('hits',u['data']) if isinstance(u['data'],dict) else u['data']
for t,r,h in zip(tags,rays,hs): print(t,r['origin'],'->',(h and (h.get('body'),[round(c,2) for c in h['point']])))
u=q.call('matlist',{'tool':'execute','arguments':{'command':'material.list','params':{}}})
d=u['data']; ms=d.get('materials',d) if isinstance(d,dict) else d
print([ (m.get('name'),m.get('density')) for m in ms if isinstance(m,dict) and m.get('name') in ('PET-CF','SUS304','A5052','STKR400','SS400','SCM435')])
u=q.call('rules',{'tool':'execute','arguments':{'command':'sheet.rules','params':{}}})
print(json.dumps(u['data'],ensure_ascii=False)[:600])
