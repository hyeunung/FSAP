# RX-DC-C1 설계안 손계산: 새 세움 받침(L 단면 t3 SUS304) 외팔 굽힘
# 단면: 웨브 X -318.6~-303 (15.6) x Y 83~86 (t3), 꺾음 날 X -306~-303 (t3) x Y 71~83 (12)
# 뿌리 Z 253, 꺾음 날 끝 Z 445, 하중점(선반) Z 487
E=193000.0; SY=205.0
rects=[(-318.6,-303.0,83.0,86.0),(-306.0,-303.0,71.0,83.0)]  # x0,x1,y0,y1
A=sum((x1-x0)*(y1-y0) for x0,x1,y0,y1 in rects)
cx=sum((x1-x0)*(y1-y0)*(x0+x1)/2 for x0,x1,y0,y1 in rects)/A
cy=sum((x1-x0)*(y1-y0)*(y0+y1)/2 for x0,x1,y0,y1 in rects)/A
Ixx=sum((x1-x0)*(y1-y0)**3/12+(x1-x0)*(y1-y0)*((y0+y1)/2-cy)**2 for x0,x1,y0,y1 in rects)  # 굽힘: 하중 Y방향
Iyy=sum((y1-y0)*(x1-x0)**3/12+(x1-x0)*(y1-y0)*((x0+x1)/2-cx)**2 for x0,x1,y0,y1 in rects)  # 하중 X방향
cymax=max(abs(y-cy) for r in rects for y in r[2:]); cxmax=max(abs(x-cx) for r in rects for x in r[:2])
L=487-253
web_I_y=15.6*3**3/12; web_I_x=3*15.6**3/12; Lw=487-445
out=[]
for name,F in (("운전 5 N(D-232 임시, RX-DC-03 handcalc와 같음)",5.0),("오조작 50 N(케이블 손 당김, PNEU-01과 같음)",50.0)):
    for d,I,c in (("Y",Ixx,cymax),("X",Iyy,cxmax)):
        M=F*L; s=M*c/I; dl=F*L**3/(3*E*I)
        out.append(f"{name} {d}: M {M:.0f} N·mm, σ {s:.1f} MPa, SF {SY/s:.2f}, 처짐 {dl:.2f} mm")
    Mw=F*Lw
    sw=Mw*1.5/web_I_y
    out.append(f"  웨브만(Z 445~487, 팔 {Lw}) Y: σ {sw:.1f} MPa SF {SY/sw:.2f}")
print(f"A {A:.1f} mm², 중심 ({cx:.2f},{cy:.2f}), Ixx {Ixx:.0f} Iyy {Iyy:.0f} mm⁴")
print("\n".join(out))
