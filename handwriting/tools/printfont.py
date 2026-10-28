import json, numpy as np, cv2, potrace, math, re
from skimage.morphology import skeletonize
F=json.load(open('font/font.json'))
UPS=4
WIDE=set('шщюмжтф')
def SX(gn):
    g=F[gn]
    if not gn.startswith(('ua_','en_')): return 1.0
    cw=(g['cr']-g['cl'])*g['u']; mx=1.7 if gn[3:] in WIDE else 1.3
    return max(0.6,min(1.0,mx/cw))
def neighbors_count(sk):
    k=np.ones((3,3),np.uint8); k[1,1]=0
    return cv2.filter2D(sk.astype(np.uint8),-1,k,borderType=cv2.BORDER_CONSTANT)
def skel_segments(name):
    """segments in glyph-unit coords (x from core-left, y from baseline, xh=1)"""
    g=F[name]
    src='out/png/'+name+'.png'
    a=cv2.imread(src,-1)[...,3].astype(np.float32)
    big=cv2.resize(a,None,fx=UPS,fy=UPS,interpolation=cv2.INTER_CUBIC)
    big=cv2.GaussianBlur(big,(5,5),0)>110
    sk=skeletonize(big).astype(np.uint8)
    # prune spurs
    for _ in range(9):
        nc=neighbors_count(sk); ends=(sk==1)&(nc==1); sk[ends]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(big.astype(np.uint8))
    extra=[]
    for j in range(1,n):
        if not sk[lab==j].any():
            cx,cy=cen[j]; extra.append((int(cy),int(cx)))
    ys,xs=np.nonzero(sk); S=set(zip(ys.tolist(),xs.tolist()))
    sx=SX(name); u=g['u']
    def U(y,x): return ((x/UPS-g['cl'])*u*sx, (y/UPS-g['bt'])*u)
    segs=[]
    for (y,x) in S:
        for dy,dx in ((0,1),(1,0),(1,1),(1,-1)):
            if (y+dy,x+dx) in S: segs.append((U(y,x),U(y+dy,x+dx)))
    for (y,x) in extra: segs.append((U(y,x),U(y,x)))
    return segs
def bbox(segs):
    xs=[p[0] for s in segs for p in s]; ys=[p[1] for s in segs for p in s]
    return min(xs),min(ys),max(xs),max(ys)
def crop(segs,fx0=0,fx1=1,fy0=0,fy1=1):
    x0,y0,x1,y1=bbox(segs); w=x1-x0; h=y1-y0
    keep=lambda p: x0+fx0*w-1e-9<=p[0]<=x0+fx1*w+1e-9 and y0+fy0*h-1e-9<=p[1]<=y0+fy1*h+1e-9
    return [s for s in segs if keep(s[0]) and keep(s[1])]
def norm(segs):
    x0,y0,x1,y1=bbox(segs); w=max(x1-x0,1e-6); h=max(y1-y0,1e-6)
    return [tuple(((p[0]-x0)/w,(p[1]-y0)/h) for p in s) for s in segs]
def box(segs,x0,y0,x1,y1,flipx=False,flipy=False):
    n=norm(segs); out=[]
    for s in n:
        q=[]
        for (a,b) in s:
            if flipx: a=1-a
            if flipy: b=1-b
            q.append((x0+a*(x1-x0), y0+b*(y1-y0)))
        out.append(tuple(q))
    return out
_cache={}
def P(name): 
    if name not in _cache: _cache[name]=skel_segments(name)
    return _cache[name]
# straight hand-drawn line piece: shaft of the down arrow (top 75%), normalized along y
LINEP=None
def line(p0,p1,wob=0.035):
    global LINEP
    if LINEP is None: LINEP=norm(crop(P('sym_arrow_down'),0,1,0,0.74))
    (x0,y0),(x1,y1)=p0,p1; L=math.hypot(x1-x0,y1-y0); dx,dy=(x1-x0)/L,(y1-y0)/L; nx,ny=-dy,dx
    out=[]
    for s in LINEP:
        q=[]
        for (a,b) in s:
            v=(a-0.5)*wob*2  # across
            q.append((x0+dx*b*L+nx*v, y0+dy*b*L+ny*v))
        out.append(tuple(q))
    return out
def take(name): return P(name)
def sub(name,fy0,fy1,x0,y0,x1,y1): return box(crop(P(name),0,1,fy0,fy1),x0,y0,x1,y1)
C={}
T=-1.0
C['т']=line((0,T),(0.8,T))+line((0.4,T),(0.4,0))
C['п']=line((0,T),(0,0))+line((0,T),(0.7,T))+line((0.7,T),(0.7,0))
C['г']=line((0,T),(0,0))+line((0,T),(0.55,T))
C['ґ']=C['г']+line((0.55,T),(0.55,-1.28))
C['и']=line((0,T),(0,0))+line((0,0),(0.7,T))+line((0.7,T),(0.7,0))
C['л']=line((-0.04,-0.02),(0.3,T))+line((0.3,T),(0.7,T))+line((0.7,T),(0.7,0))+line((-0.16,-0.12),(-0.04,-0.02))
C['м']=line((0,0),(0,T))+line((0,T),(0.42,-0.3))+line((0.42,-0.3),(0.84,T))+line((0.84,T),(0.84,0))
C['ш']=line((0,T),(0,0))+line((0.45,T),(0.45,0))+line((0.9,T),(0.9,0))+line((0,0),(0.9,0))
C['щ']=line((0,T),(0,0))+line((0.45,T),(0.45,0))+line((0.9,T),(0.9,0))+line((0,0),(1.0,0))+line((1.0,0),(1.0,0.3))
C['ц']=line((0,T),(0,0))+line((0.7,T),(0.7,0))+line((0,0),(0.82,0))+line((0.82,0),(0.82,0.3))
C['н']=line((0,T),(0,0))+line((0.7,T),(0.7,0))+line((0,-0.5),(0.7,-0.5))
C['ю']=line((0,T),(0,0))+line((0,-0.5),(0.2,-0.5))+box(P('ua_о'),0.2,T,0.95,0)
C['я']=line((0.66,T),(0.66,0))+box(P('ua_о'),0.04,T,0.68,-0.42)+line((0.36,-0.44),(0.02,0))
C['в']=line((0,T),(0,0))+box(P('num_3'),0.02,T,0.6,0)
C['з']=box(P('num_3'),0,T,0.6,0)
C['д']=line((0.1,0),(0.32,T))+line((0.32,T),(0.72,T))+line((0.72,T),(0.72,0))+line((-0.06,0),(0.88,0))+line((-0.06,0),(-0.06,0.26))+line((0.88,0),(0.88,0.26))
C['й']=C['и']+sub('ua_й',0,0.22,0.12,-1.42,0.58,-1.16)
C['ч']=line((0,T),(0,-0.62))+box(crop(P('ua_о'),0,1,0.5,1),0,-0.8,0.7,-0.4)+line((0.7,T),(0.7,0))
# letters taken as-is from her writing (re-rendered with uniform pen)
TAKE={'а':'en_a','б':'ua_б','е':'en_e','є':'ua_є','ж':'ua_ж','і':'ua_і','ї':'ua_ї','к':'ua_к','о':'ua_о','р':'ua_р','с':'ua_с','у':'en_y','ф':'ua_ф','х':'en_x','ь':'ua_ь'}
def fit(segs,top,bot,maxw=1.0):
    x0,y0,x1,y1=bbox(segs); h=y1-y0; w=x1-x0
    k=(bot-top)/h; kx=k
    if w*kx>maxw: kx=maxw/w
    return [tuple(((p[0]-x0)*kx,top+(p[1]-y0)*k) for p in s) for s in segs]
VB={'short':(-1,0),'asc':(-1.55,0),'dot':(-1.45,0),'desc':(-1,0.55),'both':(-1.5,0.5),'t':(-1.3,0),'digit':(-1.45,0),'jdot':(-1.45,0.55)}
CLS={'б':'asc','і':'dot','ї':'dot','р':'desc','у':'desc','ф':'both','b':'asc','d':'asc','f':'asc','h':'asc','k':'asc','l':'asc','t':'t','i':'dot','j':'jdot','g':'desc','p':'desc','q':'desc','y':'desc'}
WID={'ж':1.25,'ш':1.3,'m':1.15,'w':1.15,'ф':1.1}
for ch,n in TAKE.items():
    c=CLS.get(ch,'short'); C[ch]=fit(take(n),*VB[c],WID.get(ch,0.85))
for ch in 'abcdefghijklmnopqrstuvwxyz':
    c=CLS.get(ch,'short'); C[ch]=fit(take('en_'+ch),*VB[c],WID.get(ch,0.85))
for d in '123456789': C[d]=fit(take('num_'+d),*VB['digit'],0.75)
C['0']=box(P('ua_о'),0,-1.45,0.7,0)

# --- explicit composites that read better than the cursive originals ---
O=lambda x0,y0,x1,y1: box(P('ua_о'),x0,y0,x1,y1)
ARC=lambda x0,y0,x1,y1,flip=False: box(crop(P('ua_о'),0,1,0,0.5),x0,y0,x1,y1,flipy=flip)
DOT=lambda x,y: [((x,y),(x,y))]
BODY_I=lambda: fit(crop(P('ua_і'),0,1,0.35,1),-1,0,0.3)
def iota(dots):
    b=BODY_I(); x0,_,x1,_=bbox(b); cx=(x0+x1)/2+0.05
    return b+sum((DOT(cx+d,-1.38) for d in dots),[])
C['і']=iota([0]); C['i']=iota([0]); C['ї']=iota([-0.13,0.15])
C['j']=fit(crop(P('en_j'),0,1,0.3,1),-1,0.55,0.45); _x=bbox(C['j'])[2]; C['j']+=DOT(_x-0.02,-1.38)
C['р']=line((0,-1),(0,0.55))+O(0,-1,0.62,0); C['p']=C['р']
C['q']=O(0,-1,0.62,0)+line((0.62,-1),(0.62,0.55))
C['у']=line((0,-1),(0.36,-0.04))+line((0.72,-1),(0.14,0.55)); C['y']=C['у']
C['g']=O(0,-1,0.6,0)+line((0.6,-1),(0.6,0.38))+line((0.6,0.38),(0.12,0.52))
C['d']=O(0,-1,0.6,0)+line((0.6,-1.55),(0.6,0))
C['b']=line((0,-1.55),(0,0))+O(0,-1,0.6,0)
C['n']=line((0,-1),(0,0))+ARC(0,-1,0.62,-0.6)+line((0.62,-0.7),(0.62,0))
C['h']=line((0,-1.55),(0,0))+ARC(0,-1,0.62,-0.6)+line((0.62,-0.7),(0.62,0))
C['m']=line((0,-1),(0,0))+ARC(0,-1,0.48,-0.62)+line((0.48,-0.72),(0.48,0))+ARC(0.48,-1,0.96,-0.62)+line((0.96,-0.72),(0.96,0))
C['u']=line((0,-1),(0,-0.3))+ARC(0,-0.4,0.62,0,True)+line((0.62,-1),(0.62,0))
C['r']=line((0,-1),(0,0))+ARC(0,-1,0.5,-0.62)
C['t']=line((0.22,-1.3),(0.22,-0.1))+ARC(0.22,-0.35,0.55,0,True)+line((0,-0.92),(0.5,-0.92))

# punctuation with the same pen
L_=line
C['.']=DOT(0.05,-0.06)
C[',']=L_((0.08,-0.08),(0.0,0.22))
C[':']=DOT(0.05,-0.06)+DOT(0.05,-0.72)
C[';']=DOT(0.08,-0.72)+L_((0.08,-0.08),(0.0,0.22))
C['«']=L_((0.22,-0.75),(0.04,-0.47))+L_((0.04,-0.47),(0.22,-0.2))+L_((0.46,-0.75),(0.28,-0.47))+L_((0.28,-0.47),(0.46,-0.2))
C['»']=L_((0.04,-0.75),(0.22,-0.47))+L_((0.22,-0.47),(0.04,-0.2))+L_((0.28,-0.75),(0.46,-0.47))+L_((0.46,-0.47),(0.28,-0.2))
C['[']=L_((0.22,-1.45),(0.0,-1.45))+L_((0.0,-1.45),(0.0,0.3))+L_((0.0,0.3),(0.22,0.3))
C[']']=L_((0.0,-1.45),(0.22,-1.45))+L_((0.22,-1.45),(0.22,0.3))+L_((0.22,0.3),(0.0,0.3))
C['(']=box(crop(P('ua_о'),0,0.5,0,1),0,-1.45,0.3,0.3)
C[')']=box(crop(P('ua_о'),0.5,1,0,1),0,-1.45,0.3,0.3)
C['/']=L_((0.0,0.25),(0.5,-1.45))
C['—']=L_((0.0,-0.5),(0.9,-0.52))
C['-']=L_((0.0,-0.5),(0.42,-0.5))
C["'"]=L_((0.06,-1.5),(0.0,-1.1))
C['+']=L_((0.0,-0.5),(0.7,-0.5))+L_((0.35,-0.85),(0.35,-0.15))
C['!']=L_((0.05,-1.45),(0.05,-0.4))+DOT(0.05,-0.06)
C['?']=box(crop(P('num_2'),0,1,0,0.6),0,-1.45,0.6,-0.55)+L_((0.3,-0.6),(0.3,-0.35))+DOT(0.3,-0.06)
C['→']=L_((0.0,-0.5),(0.9,-0.5))+L_((0.62,-0.75),(0.9,-0.5))+L_((0.9,-0.5),(0.62,-0.25))
C['@']=O(0.18,-0.75,0.62,-0.25)+box(P('ua_о'),0,-1.05,0.95,0.15)

PEN=0.17; S=200  # px per unit at render
def render(ch,segs):
    x0,y0,x1,y1=bbox(segs); pad=PEN
    W=int(math.ceil((x1-x0+2*pad)*S)); top=min(y0,-1.0)-pad; bot=max(y1,0)+pad
    H=int(math.ceil((bot-top)*S))
    img=np.zeros((H,W),np.uint8); r=int(PEN*S/2)
    tr=lambda p:(int(round((p[0]-x0+pad)*S)),int(round((p[1]-top)*S)))
    for s in segs:
        a,b=tr(s[0]),tr(s[1]); cv2.line(img,a,b,255,thickness=2*r,lineType=cv2.LINE_8); cv2.circle(img,a,r,255,-1)
    m=img>0
    path=potrace.Bitmap(~m).trace(turdsize=20,alphamax=1.1,opticurve=True,opttolerance=0.5)
    k=100/S; ds=[]
    for c in path:
        p=c.start_point; seg=[f'M{p.x*k:.1f} {p.y*k:.1f}']
        for sg in c.segments:
            seg.append(f'L{sg.c.x*k:.1f} {sg.c.y*k:.1f}L{sg.end_point.x*k:.1f} {sg.end_point.y*k:.1f}' if sg.is_corner else f'C{sg.c1.x*k:.1f} {sg.c1.y*k:.1f} {sg.c2.x*k:.1f} {sg.c2.y*k:.1f} {sg.end_point.x*k:.1f} {sg.end_point.y*k:.1f}')
        ds.append(''.join(seg)+'Z')
    Wp,Hp=W*k,H*k
    name='g_'+('%04x'%ord(ch))
    open(f'font2/{name}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wp:.0f} {Hp:.0f}" width="{Wp:.0f}" height="{Hp:.0f}"><path fill="#1E2A8C" fill-rule="evenodd" d="{" ".join(ds)}"/></svg>')
    # bearings within x-height band
    band=m[int((-1-top)*S):int((0-top)*S)]
    cols=np.nonzero(band.sum(0))[0]
    cl,cr=(cols[0],cols[-1]) if len(cols) else (0,W)
    return dict(file=name+'.svg',W=Wp,H=Hp,bt=(0-top)*100,u=0.01,cl=cl*k,cr=cr*k,ink=Wp)
FM={}
for ch,segs in C.items(): FM[ch]=render(ch,segs)
json.dump(FM,open('font2/font2.json','w'),ensure_ascii=False)
print(len(FM))
