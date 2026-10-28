import json, numpy as np, re, os, math, random, shutil
import cv2, potrace
meta=json.load(open('out/glyphs.json'))
PAD=6
rows={'ua1':[],'ua2':[],'en1':[],'en2':[],'num':[]}
for k,v in meta.items():
    bot=v['y']+v['h']-PAD; cx=v['x']+v['w']/2
    if k.startswith('ua_'): rows['ua1' if v['y']<660 else 'ua2'].append(k)
    elif k.startswith('en_'): rows['en1' if v['y']<960 else 'en2'].append(k)
    elif k.startswith('num_'): rows['num'].append(k)
short={'ua1':'г е є ж и к л м н','ua2':'о п с т х ч ш ь ю я','en1':'a c e m n o','en2':'r s u v w x z'}
font={}
ASC={'б':1.6,'в':1.6,'ф':1.6,'й':1.45,'і':1.45,'ї':1.45,'ґ':1.3,'b':1.6,'d':1.6,'f':1.6,'h':1.6,'k':1.6,'l':1.6,'i':1.45,'j':1.45,'t':1.35}
def svgpath(name): return open(f'out/svg/{name}.svg').read().split(' d="')[1].split('"')[0]
fits={}
for r,names in rows.items():
    if r=='num': sh=names
    else: sh=[('ua_' if r.startswith('ua') else 'en_')+c for c in short[r].split()]
    xs=np.array([meta[n]['x']+meta[n]['w']/2 for n in sh]); bs=np.array([meta[n]['y']+meta[n]['h']-PAD for n in sh])
    a,b=np.polyfit(xs,bs,1)
    # robust: refit without worst outlier
    res=bs-(a*xs+b); keep=np.abs(res)<np.percentile(np.abs(res),80)+1
    a,b=np.polyfit(xs[keep],bs[keep],1)
    xh=np.median([meta[n]['h']-2*PAD for n in sh])
    fits[r]=(a,b,xh)
    print(r,round(a,4),round(b,1),xh)
letter_xh=np.mean([fits[r][2] for r in ['ua1','ua2','en1','en2']])
for r,names in rows.items():
    a,b,xh=fits[r]
    if r=='num': xh=fits['num'][2]/1.3   # digits ~1.3 x-height tall
    for n in names:
        v=meta[n]; cx=v['x']+v['w']/2; base=a*cx+b
        bt=base-v['y']; above=max(bt-PAD,1)
        ch=n.split('_',1)[1]
        if r=='num': ratio=1.45
        elif ch in ASC: ratio=ASC[ch]
        else: ratio=1.0
        u=ratio/above
        # guard: if a short letter sits oddly (tiny 'above'), fall back to row scale
        if not (0.6/xh < u < 1.6/xh): u=1/xh
        font[n]=dict(file=f'{n}.svg',W=v['w'],H=v['h'],bt=bt,u=u,ink=v['w']-2*PAD)
# split num_10 -> num_0 (right part) from png mask
im=cv2.imread('out/png/num_10.png',-1)[...,3]>100
cols=im.sum(0); inkc=np.nonzero(cols)[0]
gap=[c for c in range(inkc[0]+5,inkc[-1]-5) if cols[c]==0]
print('10 gaps',gap[:3],gap[-3:] if gap else None)
cut=gap[len(gap)//2] if gap else int(im.shape[1]*0.4)
sub=im[:,cut:]; ys,xs=np.nonzero(sub); sub=sub[:,xs.min():xs.max()+1]; sub=np.pad(sub,((0,0),(PAD,PAD)))
H,W=sub.shape
path=potrace.Bitmap(~sub).trace(turdsize=8,alphamax=1.0,opticurve=True,opttolerance=0.3)
ds=[]
for c in path:
    p=c.start_point; seg=[f'M{p.x:.1f} {p.y:.1f}']
    for sg in c.segments:
        seg.append(f'L{sg.c.x:.1f} {sg.c.y:.1f}L{sg.end_point.x:.1f} {sg.end_point.y:.1f}' if sg.is_corner else f'C{sg.c1.x:.1f} {sg.c1.y:.1f} {sg.c2.x:.1f} {sg.c2.y:.1f} {sg.end_point.x:.1f} {sg.end_point.y:.1f}')
    ds.append(''.join(seg)+'Z')
os.makedirs('font',exist_ok=True)
for f in os.listdir('out/svg'): shutil.copy('out/svg/'+f,'font/'+f)
open('font/num_0.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><path fill="#1E2A8C" fill-rule="evenodd" d="{" ".join(ds)}"/></svg>')
f10=font['num_10']; font['num_0']=dict(file='num_0.svg',W=W,H=H,bt=f10['bt'],u=f10['u'],ink=W-2*PAD)
# list arrow as inline arrow: centered at mid x-height
for n,cy in [('list_arrow',0.5),('list_dash',0.5)]:
    v=meta[n]; u=1/letter_xh
    font[n]=dict(file=f'{n}.svg',W=v['w'],H=v['h'],bt=v['h']/2+cy*letter_xh,u=u,ink=v['w']-2*PAD)
# synthetic punctuation, drawn in units where x-height = XH px
XH=35.0; SW=7.4
random.seed(3)
def wob(pts,amp=0.6):
    return [(x+random.uniform(-amp,amp),y+random.uniform(-amp,amp)) for x,y in pts]
def pl(pts):  # smooth polyline through points via quadratic midpoints
    pts=wob(pts)
    if len(pts)==2: return f'M{pts[0][0]:.1f} {pts[0][1]:.1f}L{pts[1][0]:.1f} {pts[1][1]:.1f}'
    d=f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(1,len(pts)-1):
        mx=(pts[i][0]+pts[i+1][0])/2; my=(pts[i][1]+pts[i+1][1])/2
        d+=f'Q{pts[i][0]:.1f} {pts[i][1]:.1f} {mx:.1f} {my:.1f}'
    d+=f'L{pts[-1][0]:.1f} {pts[-1][1]:.1f}'; return d
# shapes in coords: x from 0, y with baseline=0, up negative, units = px at XH
S={}
S['.']=[('dot',4,-3)]
S[',']=[[(5,-4),(5,1),(1,8)]]
S[':']=[('dot',4,-3),('dot',4,-26)]
S['«']=[[(10,-26),(2,-16),(10,-6)],[(20,-26),(12,-16),(20,-6)]]
S['»']=[[(2,-26),(10,-16),(2,-6)],[(12,-26),(20,-16),(12,-6)]]
S['[']=[[(10,-52),(2,-51),(1,-18),(2,10),(10,10)]]
S[']']=[[(0,-52),(8,-51),(9,-18),(8,10),(0,10)]]
S['(']=[[(12,-52),(1,-22),(12,10)]]
S[')']=[[(0,-52),(11,-22),(0,10)]]
S['/']=[[(0,8),(22,-50)]]
S['—']=[[(0,-17),(24,-19),(48,-18)]]
S['-']=[[(0,-17),(18,-18)]]
S["'"]=[[(4,-52),(2,-38)]]
S['+']=[[(0,-16),(24,-17)],[(12,-29),(12,-4)]]
S['!']=[[(4,-52),(3,-14)],('dot',3,-3)]
S['?']=[[(1,-42),(10,-52),(22,-44),(12,-28),(12,-14)],('dot',12,-3)]
syn_names={'.':'p_dot',',':'p_comma',':':'p_colon','«':'p_laquo','»':'p_raquo','[':'p_lbr',']':'p_rbr','(':'p_lpar',')':'p_rpar','/':'p_slash','—':'p_emdash','-':'p_hyphen',"'":'p_apos','+':'p_plus','!':'p_excl','?':'p_quest'}
for ch,parts in S.items():
    xs=[];ys=[]
    for p in parts:
        if isinstance(p,tuple): xs+= [p[1]];ys+=[p[2]]
        else: xs+=[q[0] for q in p]; ys+=[q[1] for q in p]
    m=SW/2+PAD
    x0,x1,y0,y1=min(xs)-m,max(xs)+m,min(ys)-m,max(ys)+m
    W,H=x1-x0,y1-y0
    body=''
    for p in parts:
        if isinstance(p,tuple): body+=f'<circle cx="{p[1]-x0:.1f}" cy="{p[2]-y0:.1f}" r="{SW*0.62:.1f}" fill="#1E2A8C"/>'
        else:
            q=[(a-x0,b-y0) for a,b in p]
            body+=f'<path d="{pl(q)}" fill="none" stroke="#1E2A8C" stroke-width="{SW:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
    n=syn_names[ch]
    open(f'font/{n}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.1f}" height="{H:.1f}">{body}</svg>')
    font[n]=dict(file=f'{n}.svg',W=W,H=H,bt=-y0,u=1/XH,ink=W-2*PAD)
# symbols (non inline) keep raw metrics
for n,v in meta.items():
    if n not in font: font[n]=dict(file=f'{n}.svg',W=v['w'],H=v['h'],bt=v['h'],u=1/letter_xh,ink=v['w']-2*PAD)
json.dump(font,open('font/font.json','w'),ensure_ascii=False,indent=0)
print(len(font))
# core side bearings: ink extent inside the x-height band
for n,g in font.items():
    pth=f'out/png/{n}.png'
    if not (n.startswith('ua_') or n.startswith('en_')) or not os.path.exists(pth):
        g['cl']=PAD; g['cr']=g['W']-PAD; continue
    a=cv2.imread(pth,-1)[...,3]>100
    xh=1/g['u']; b=int(round(g['bt'])); t=int(round(g['bt']-xh*0.95))
    band=a[max(t,0):max(b,1)]
    cols=np.nonzero(band.sum(0)>0)[0]
    if len(cols)<2: g['cl']=PAD; g['cr']=g['W']-PAD
    else: g['cl']=int(cols[0]); g['cr']=int(cols[-1])+1
json.dump(font,open('font/font.json','w'),ensure_ascii=False,indent=0)
