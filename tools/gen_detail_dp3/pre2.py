"""DP-3 사전 측정 2: 클램프 15개의 원통(탭 자리 유무), 관 길(빗 D·E 앞), 받침·이음판 면."""
import json, q, collections
names=['P_M08_TUBE_CLAMP_F_%d'%i for i in range(1,7)]+['P_M08_TUBE_CLAMP_L_%d'%i for i in range(1,7)]+['P_M08_TUBE_CLAMP_SO_%d'%i for i in range(1,4)]+['P_M08_LBRK_R3_SM','P_M08_HMI_MOUNT_ML','P_M07_SPLICE_NX']
for b in names:
    u=q.call('cyl_'+b,{'tool':'body_topology','arguments':{'body':b,'faces':'cylinders'}})
    cs=u['data'].get('cylinders',[])
    c=collections.Counter((round(x['radius'],2),tuple(round(abs(a)) for a in x['axis'])) for x in cs)
    print(b,dict(c))
    if b in('P_M08_LBRK_R3_SM','P_M07_SPLICE_NX','P_M08_HMI_MOUNT_ML'):
        for x in cs: print('    ',round(x['radius'],3),[round(v,2) for v in x['origin']],x['axis'],x['extent'])
rays=[]
for x in (-650,-100,-1245):
    for y in range(122,160,4): rays.append({'origin':[x,y,760],'dir':[0,0,-1]})
for x in (250,50,650,950):
    for y in (118,121,123): rays.append({'origin':[x,y,760],'dir':[0,0,-1]})
u=q.call('pick_comb',{'tool':'execute','arguments':{'command':'view.pick','params':{'rays':rays}}})
hs=u['data'].get('hits',u['data']) if isinstance(u['data'],dict) else u['data']
for r,h in zip(rays,hs): print(r['origin'][:2],'->',(h and (h.get('body'),round(h['point'][2],2))))
