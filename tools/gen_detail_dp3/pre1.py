"""DP-3 사전 측정: 보 끝판·속 면(광선), 관 빗 5종 면, 재질."""
import json, q
rays=[]
def R(o,d): rays.append({'origin':o,'dir':d})
# 끝판·속 면 (보 가운데 축 Y 220 Z 450, 모서리 Y 128.6 Z 258.6)
for y,z in ((220,450),(128.6,258.6)):
    R([-2400,y,z],[1,0,0]); R([-2300,y,z],[-1,0,0]); R([-2300,y,z],[1,0,0]); R([1225,y,z],[-1,0,0]); R([1225,y,z],[1,0,0]); R([1400,y,z],[-1,0,0])
    R([1221.5,y,z],[-1,0,0]); R([1221.5,y,z],[1,0,0])
u=q.call('pick_beam',{'tool':'execute','arguments':{'command':'view.pick','params':{'rays':rays}}})
for r,h in zip(rays,u['data'].get('hits',u['data']) if isinstance(u['data'],dict) else u['data']):
    print(r['origin'],r['dir'],'->',(h and (h.get('body'),[round(c,3) for c in h.get('point',[])],h.get('normal'))))
for b in ['P_M08_TUBE_COMB_ML_1','P_M08_TUBE_COMB_ML_5','P_M08_TUBE_COMB_ML_7','P_M08_TUBE_COMB_ML_8','P_M08_TUBE_COMB_U5_2','P_M08_TUBE_COMB_ML_9','P_M08_TUBE_COMB_ML_6','P_M08_TUBE_COMB_U5_1']:
    u=q.call('topo_'+b,{'tool':'body_topology','arguments':{'body':b}})
    d=u['data']; fs=d['faces']
    print(b,'faces',len(fs),'edges',len(d['edges']))
    for f in fs:
        n=f.get('normal'); c=f.get('centroid'); cyl=f.get('cylinder')
        if cyl: print('   cyl r',cyl['radius'],'o',[round(x,2) for x in cyl['origin']],'ax',cyl['axis'],'A',round(f['area'],1))
        else: print('   pl n',n and [round(x,2) for x in n],'c',[round(x,2) for x in c],'A',round(f['area'],1))
