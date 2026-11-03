import math
def run(W,H,n=400):
    # 사각 매트, 바늘=원점, 이송 방향 +Y, 매트 몸은 바늘 왼쪽(-X). 직선 구간은 미끄러지고 모서리는 바늘 중심 90도 회전.
    corners=[(-W/2,-H/2),(W/2,-H/2),(W/2,H/2),(-W/2,H/2)]
    xs=[];ys=[];env=0;minx=0;maxy=0;miny=0
    # 한 변 위의 바늘점 p, 그 변 방향이 +Y가 되게 회전한 좌표에서 중심 c와 꼭짓점들
    sides=[(W,H),(H,W),(W,H),(H,W)]
    for L,D in sides:
        for k in range(n+1):
            s=-L/2+L*k/n          # 바늘점의 변 위 위치
            c=(-D/2,-s)            # 중심(무게중심) 위치
            xs.append(c[0]);ys.append(c[1])
            for cx,cy in [(-D,-s-L/2),(-D,-s+L/2),(0,-s-L/2),(0,-s+L/2)]:
                minx=min(minx,cx);maxy=max(maxy,cy);miny=min(miny,cy)
        # 모서리 회전: 끝점(s=L/2)에서 바늘 중심으로 90도
        for k in range(n+1):
            a=math.radians(-90*k/n)
            for px,py in [(-D/2,-L/2)]+[(-D,-L),(-D,0),(0,-L),(0,0)]:
                rx=px*math.cos(a)-py*math.sin(a); ry=px*math.sin(a)+py*math.cos(a)
                if (px,py)==(-D/2,-L/2): xs.append(rx);ys.append(ry)
                else: minx=min(minx,rx);maxy=max(maxy,ry);miny=min(miny,ry)
    return min(xs),max(xs),min(ys),max(ys),minx,miny,maxy
for W,H in [(1200,1200),(1500,1500),(300,200),(1200,500)]:
    a=run(W,H)
    print(f"{W}x{H}: 원판중심 X {a[0]:.0f}~{a[1]:.0f} (행정 {a[1]-a[0]:.0f}), Y {a[2]:.0f}~{a[3]:.0f} (행정 {a[3]-a[2]:.0f}) | 매트가 쓰는 영역 X {a[4]:.0f}~0, Y {a[5]:.0f}~{a[6]:.0f}")
