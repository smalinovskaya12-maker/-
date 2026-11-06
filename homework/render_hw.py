import json,re,random,sys,math
sys.path.insert(0,'hw'); from text import DOC
FO=json.load(open('font/font.json')); F5=json.load(open('font5/font2.json')); F2=json.load(open('font2/font2.json'))
SWAP=set('dnptbg')
WIDE=set('шщюмжтф')
def SX(gn):
    g=FO[gn]
    if not gn.startswith(('ua_','en_')): return 1.0
    cw=(g['cr']-g['cl'])*g['u']; mx=1.7 if gn[3:] in WIDE else 1.3
    return max(0.6,min(1.0,mx/cw))
P={'.':'p_dot',',':'p_comma',':':'p_colon','(':'p_lpar',')':'p_rpar','/':'p_slash','—':'p_emdash','-':'p_hyphen',"'":'p_apos','!':'p_excl','?':'p_quest','+':'p_plus'}
INK='#1D2B8F'
_inner={}
def inner(path):
    if path not in _inner:
        s=open(path).read(); _inner[path]=re.sub(r'^<svg[^>]*>','',s).replace('</svg>','').replace('#1E2A8C',INK)
    return _inner[path]
def glyph(ch,xh):
    """returns (svgpath, W,H, scale_x, scale_y, bt_px, cl_px, cr_px)"""
    if ch in SWAP:
        g=F2[ch]; s=xh*g['u']
        return ('font2/'+g['file'],g['W'],g['H'],s,s,g['bt'],g['cl'],g['cr'])
    if 'a'<=ch<='z': n='en_'+ch
    elif ch.isdigit(): n='num_'+ch
    elif ch in P: n=P[ch]
    else: n=None
    if n:
        g=FO[n]; s=xh*g['u']; sx=SX(n)
        return ('font/'+g['file'],g['W'],g['H'],s*sx,s,g['bt'],g['cl'],g['cr'])
    k=ch.lower() if ch.isupper() else ch
    g=F5[k]; unit=xh*1.0 if ch==';' else xh*1.45
    s=unit*g['u']
    return ('font5/'+g['file'],g['W'],g['H'],s,s,g['bt'],g['cl'],g['cr'])
TRACK=0.10; SPACE=0.85
def adv(ch,xh):
    if ch==' ': return SPACE*xh
    f,W,H,sx,sy,bt,cl,cr=glyph(ch,xh); return (cr-cl)*sx+TRACK*xh
def width(s,xh): return sum(adv(c,xh) for c in s)-TRACK*xh
# page geometry (A4 @300dpi)
PW,PH=2480,3508; CELL=59; LEFT=CELL*4; RIGHT=PW-CELL*3; TOP=CELL*4; PITCH=CELL*2
BOTTOM=PH-CELL*3
STY={'name':34,'title':36,'h1':35,'h2':32,'ans':30,'p':30}
random.seed(7)
pages=[[]]; y=TOP
def newline(n=1):
    global y
    y+=PITCH*n
    if y>BOTTOM: pages.append([]); y=TOP
def put(text,x0,xh,drift):
    """place a single line of text starting at x0 on current baseline y"""
    x=x0; out=pages[-1]
    for i,ch in enumerate(text):
        if ch==' ': x+=SPACE*xh*random.uniform(0.9,1.12); continue
        f,W,H,sx,sy,bt,cl,cr=glyph(ch,xh)
        k=random.uniform(0.97,1.03); jy=random.uniform(-0.035,0.035)*xh
        by=y+drift(x)+jy
        out.append(('g',f,x-cl*sx*k,by-bt*sy*k,sx*k,sy*k,W,H,bt,random.random()))
        x+=(cr-cl)*sx*k+TRACK*xh*random.uniform(0.8,1.2)+(0.12*xh if ch in 'il1' else 0)
    return x
def mkdrift():
    a=random.uniform(-0.004,0.004); b=random.uniform(-3,3)
    return lambda x: b+a*(x-LEFT)
def wrap(text,xh,w):
    words=text.split(' '); lines=[]; cur=''
    for wd in words:
        t=(cur+' '+wd) if cur else wd
        if width(t,xh)<=w or not cur: cur=t
        else: lines.append(cur); cur=wd
    lines.append(cur); return lines
def underline(x0,x1):
    pts=[]; n=8
    for i in range(n+1):
        t=i/n; pts.append((x0+(x1-x0)*t, y+14+random.uniform(-2.5,2.5)+t*random.uniform(-3,3)))
    d='M'+' L'.join(f'{a:.1f} {b:.1f}' for a,b in pts)
    pages[-1].append(('u',d))
first=True
for sty,text in DOC:
    xh=STY[sty]
    if sty=='name':
        x0=RIGHT-width(text,xh); put(text,x0,xh,mkdrift()); newline(2); continue
    if sty=='title':
        for ln in wrap(text,xh,RIGHT-LEFT-CELL*2):
            x0=LEFT+(RIGHT-LEFT-width(ln,xh))/2; x1=put(ln,x0,xh,mkdrift()); newline()
        newline(); continue
    if sty=='h1':
        if not first: newline()
        first=False
        if y+PITCH*2>BOTTOM: pages.append([]); globals()['y']=TOP
        x1=put(text,LEFT,xh,mkdrift()); underline(LEFT-6,x1+6); newline(); continue
    if sty=='h2':
        if y+PITCH*2>BOTTOM: pages.append([]); globals()['y']=TOP
        x1=put(text,LEFT+CELL,xh,mkdrift()); underline(LEFT+CELL-4,x1+4); newline(); continue
    if sty=='ans':
        lab,rest=text.split(' ',1); ind=LEFT+CELL*2
        lines=wrap(rest,xh,RIGHT-ind)
        d=mkdrift(); put(lab,LEFT+CELL,xh,d)
        for i,ln in enumerate(lines):
            if i: d=mkdrift()
            put(ln,ind,xh,d); newline()
        continue
    if sty=='p':
        for ln in wrap(text,xh,RIGHT-LEFT-CELL):
            put(ln,LEFT+CELL,xh,mkdrift()); newline()
import math
_num=re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')
def warp_d(d,W,H,R):
    """smooth random deformation of absolute path coords (pairs)"""
    A=H*R.uniform(0.018,0.035); B=H*R.uniform(0.012,0.028)
    fx=R.uniform(0.6,1.4)*2*math.pi/H; fy=R.uniform(0.6,1.4)*2*math.pi/max(W,1)
    px,py=R.uniform(0,6.3),R.uniform(0,6.3)
    out=[];buf=[]
    pos=0; res=[]
    toks=re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?',d)
    nums=[]
    for t in toks:
        if t.isalpha():
            if nums: res.append(nums); nums=[]
            res.append(t)
        else: nums.append(float(t))
    if nums: res.append(nums)
    s=[]
    for r in res:
        if isinstance(r,str): s.append(r); continue
        q=[]
        for i in range(0,len(r)-1,2):
            x,y=r[i],r[i+1]
            nx=x+A*math.sin(fx*y+px); ny=y+B*math.sin(fy*x+py)
            q.append(f'{nx:.1f} {ny:.1f}')
        s.append(' '.join(q))
    return ''.join(x if x.isalpha() else x+' ' for x in s)
def vary(f,x,yy,sx,sy,W,H,bt,seed):
    R=random.Random(seed)
    body=inner(f)
    body=re.sub(r' d="([^"]+)"',lambda m:' d="'+warp_d(m.group(1),W,H,R)+'"',body)
    rot=R.gauss(0,2.2); sh=R.gauss(0,0.06)
    kx=R.uniform(0.92,1.08); ky=R.uniform(0.95,1.05)
    # pen pressure: thicken a bit with a stroke of ink colour, vary opacity
    thick=max(0,R.gauss(0.25,0.45))/max(sx,1e-6)
    op=R.uniform(0.88,1.0)
    body=body.replace('fill-rule="evenodd"',f'fill-rule="evenodd" stroke="{INK}" stroke-width="{thick:.2f}" stroke-linejoin="round"',)
    cx,cy=W/2,bt  # pivot at baseline centre
    tr=(f'translate({x:.1f} {yy:.1f}) scale({sx:.4f} {sy:.4f}) translate({cx:.1f} {cy:.1f}) '
        f'rotate({rot:.2f}) matrix({kx:.3f} 0 {sh:.3f} {ky:.3f} 0 0) translate({-cx:.1f} {-cy:.1f})')
    return f'<g opacity="{op:.2f}" transform="{tr}">{body}</g>'
def svg(items,pi):
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}"><rect width="{PW}" height="{PH}" fill="#FDFDFB"/>']
    o.append('<g opacity="0.55">')
    for k in range(0,PH//CELL+1): o.append(f'<rect x="0" y="{k*CELL+20}" width="{PW}" height="2" fill="#A9C2DD"/>')
    for k in range(0,PW//CELL+1): o.append(f'<rect x="{k*CELL+3}" y="0" width="2" height="{PH}" fill="#A9C2DD"/>')
    o.append('</g>')
    for it in items:
        if it[0]=='g':
            o.append(vary(*it[1:]))
        else: o.append(f'<path d="{it[1]}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append('</svg>'); return ''.join(o)
import os; os.makedirs('hw/out',exist_ok=True)
for i,p in enumerate(pages):
    open(f'hw/out/page{i+1}.svg','w').write(svg(p,i))
print('pages',len(pages))
