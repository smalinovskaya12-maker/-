import json,math,numpy as np,cv2,potrace,sys
sys.path.insert(0,'.')
import printfont as PF   # gives C (old digits/punct), helpers
L=json.load(open('v5/segs_letters.json'))
C={k:[tuple(tuple(p) for p in s) for s in v] for k,v in L.items()}
fit=lambda segs,top,bot,mw: (lambda b:[tuple(((p[0]-b[0])*min((bot-top)/max(b[3]-b[1],1e-6), mw/max(b[2]-b[0],1e-6)),top+(p[1]-b[1])*(bot-top)/max(b[3]-b[1],1e-6)) for p in s) for s in segs])(PF.bbox(segs))
def bb(segs): return PF.bbox(segs)
def crop(segs,fx0,fx1,fy0,fy1):
    x0,y0,x1,y1=bb(segs); w=x1-x0; h=y1-y0
    k=lambda p: x0+fx0*w-1e-9<=p[0]<=x0+fx1*w+1e-9 and y0+fy0*h-1e-9<=p[1]<=y0+fy1*h+1e-9
    return [q for q in segs if k(q[0]) and k(q[1])]
def place(segs,X0,Y0,X1,Y1):
    x0,y0,x1,y1=bb(segs); w=max(x1-x0,1e-6); h=max(y1-y0,1e-6)
    return [tuple((X0+(p[0]-x0)/w*(X1-X0),Y0+(p[1]-y0)/h*(Y1-Y0)) for p in q) for q in segs]
# drop stray zero-length specks except where dots belong
for ch in list(C):
    if ch not in 'іїйij': C[ch]=[q for q in C[ch] if q[0]!=q[1]] or C[ch]
def despeck(segs,minlen=0.12):
    par={}
    def f(a):
        while par.setdefault(a,a)!=a: a=par[a]
        return a
    key=lambda p:(round(p[0],3),round(p[1],3))
    for q in segs: par[f(key(q[0]))]=f(key(q[1]))
    groups={}
    for q in segs: groups.setdefault(f(key(q[0])),[]).append(q)
    keep=[]
    for g in groups.values():
        L=sum(((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5 for a,b in g)
        if L>=minlen: keep+=g
    return keep or segs
for ch in list(C):
    if ch not in 'іїйij' and ch.isalpha(): C[ch]=despeck(C[ch])
# en O/P/I from her Ukrainian forms
C['o']=C['о']; C['p']=C['р']
# П from her own strokes: stems of Н + top bar of Т
H_=C['н']; T_=C['т']
lst=crop(H_,0,0.3,0,1); rst=crop(H_,0.7,1,0,1); bar=crop(T_,0,1,0,0.22)
C['п']=place(lst,0,-1,0.06,0)+place(rst,0.62,-1,0.68,0)+place(bar,-0.02,-1.03,0.7,-0.97)
# Ї / І / i from her І body + dots
body=[q for q in C['і'] if q[0]!=q[1] and min(q[0][1],q[1][1])>-1.02]
body=place(body,0,-1,bb(body)[2]-bb(body)[0] if bb(body)[2]>bb(body)[0] else 0.05,0)
cx=(bb(body)[0]+bb(body)[2])/2
D=lambda x,y:[((x,y),(x,y))]
C['і']=body+D(cx,-1.25); C['i']=C['і']; C['ї']=body+D(cx-0.13,-1.25)+D(cx+0.13,-1.25)
for d in '0123456789': C[d]=fit(PF.C[d],-1,0,0.6)
for p,(t,b) in {'[':(-1.15,0.2),']':(-1.15,0.2),'(':(-1.15,0.2),')':(-1.15,0.2),"'":(-1.1,-0.75),'?':(-1,0),'!':(-1,0),'/':(-1.1,0.15)}.items():
    C[p]=fit(PF.C[p],t,b,0.6)
for p in '.,:;«»—-+→@': C[p]=PF.C[p]
PEN=0.12; S=200
def render(ch,segs,out='font5'):
    x0,y0,x1,y1=PF.bbox(segs); pad=PEN
    W=int(math.ceil((x1-x0+2*pad)*S)); top=min(y0,-1.0)-pad; bot=max(y1,0)+pad
    H=int(math.ceil((bot-top)*S)); img=np.zeros((H,W),np.uint8); r=int(PEN*S/2)
    tr=lambda p:(int(round((p[0]-x0+pad)*S)),int(round((p[1]-top)*S)))
    for s in segs:
        a,b=tr(s[0]),tr(s[1]); cv2.line(img,a,b,255,thickness=2*r); cv2.circle(img,a,r,255,-1); cv2.circle(img,b,r,255,-1)
    msk=img>0
    path=potrace.Bitmap(~msk).trace(turdsize=20,alphamax=1.1,opticurve=True,opttolerance=0.5)
    k=100/S; ds=[]
    for c in path:
        p=c.start_point; seg=[f'M{p.x*k:.1f} {p.y*k:.1f}']
        for sg in c.segments:
            seg.append(f'L{sg.c.x*k:.1f} {sg.c.y*k:.1f}L{sg.end_point.x*k:.1f} {sg.end_point.y*k:.1f}' if sg.is_corner else f'C{sg.c1.x*k:.1f} {sg.c1.y*k:.1f} {sg.c2.x*k:.1f} {sg.c2.y*k:.1f} {sg.end_point.x*k:.1f} {sg.end_point.y*k:.1f}')
        ds.append(''.join(seg)+'Z')
    Wp,Hp=W*k,H*k; name='g_%04x'%ord(ch)
    open(f'{out}/{name}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wp:.0f} {Hp:.0f}" width="{Wp:.0f}" height="{Hp:.0f}"><path fill="#1E2A8C" fill-rule="evenodd" d="{" ".join(ds)}"/></svg>')
    band=msk[int((-1-top)*S):int((0-top)*S)]; cols=np.nonzero(band.sum(0))[0]
    cl,cr=(cols[0],cols[-1]) if len(cols) else (0,W)
    return dict(file=name+'.svg',W=Wp,H=Hp,bt=(0-top)*100,u=0.01,cl=cl*k,cr=cr*k,ink=Wp)
FM={ch:render(ch,s) for ch,s in C.items()}
json.dump(FM,open('font5/font2.json','w'),ensure_ascii=False); print(len(FM))
