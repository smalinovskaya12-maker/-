import json,sys,math,numpy as np,cv2,potrace
sys.path.insert(0,'.'); sys.path.insert(0,'v5')
import importlib.util
spec=importlib.util.spec_from_file_location('b5','v5/build5.py')
src=open('v5/build5.py').read().split("comps=json.load")[0]   # helpers only
ns={}; exec(src,ns)
segs_from_soft=None
src2=open('v5/build5.py').read()
i=src2.index('def nb'); j=src2.index('def bbox')
from skimage.morphology import skeletonize; ns.update(UPS=4,cv2=cv2,np=np,skeletonize=skeletonize); exec(src2[i:j],ns); segs_from_soft=ns['segs_from_soft']
exec(src2[j:src2.index('# class boxes')],ns); fit=ns['fit']; bbox=ns['bbox']
img=cv2.imread('v7/rot.jpg'); g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
bg=cv2.GaussianBlur(cv2.dilate(g,np.ones((15,15))),(61,61),0); diff=bg-g
blu=(img[...,0].astype(int)-img[...,2].astype(int))>-5
soft=np.clip((diff-20)/30.0,0,1)*blu
comps=json.load(open('v7/comps.json')); lab=np.load('v7/lab.npy')
R={}
for c in comps: R.setdefault(c['row'],[]).append(c)
import json as _j
cnt={}
for c in comps: cnt[c['row']]=cnt.get(c['row'],0)+1
need=[18,8,18,8,16,10]; groups=[]; r=0
for nd in need:
    g=[];tot=0
    while tot<nd: g.append(r); tot+=cnt[r]; r+=1
    assert tot==nd,(nd,g,tot); groups.append(g)
print(groups)
labels=['abcdefghijklmnopqr','stuvwxyz','abcdefghijklmnopqr','stuvwxyz','ABCDEFGHIJKLMNOP','QRSTUVWXYZ']
VB={'s':(-1,0),'asc':(-1.55,0),'desc':(-1,0.55),'t':(-1.3,0),'dot':(-1.45,0),'jd':(-1.45,0.55),'cap':(-1.45,0)}
CL={}
for ch in 'bdfhkl': CL[ch]='asc'
for ch in 'gpqy': CL[ch]='desc'
CL['t']='t'; CL['i']='dot'; CL['j']='jd'
WID={'m':1.15,'w':1.1,'M':1.3,'W':1.35,'A':1.0,'D':1.0}
def smooth(segs,it=10,a=0.5):
    from collections import defaultdict
    key=lambda p:(round(p[0],2),round(p[1],2))
    adj=defaultdict(set); pos={}
    for p,q in segs:
        kp,kq=key(p),key(q); pos[kp]=list(p); pos[kq]=list(q)
        if kp!=kq: adj[kp].add(kq); adj[kq].add(kp)
    for _ in range(it):
        new={}
        for k,nb in adj.items():
            if len(nb)==2:
                mx=sum(pos[n][0] for n in nb)/2; my=sum(pos[n][1] for n in nb)/2
                new[k]=[pos[k][0]*(1-a)+mx*a,pos[k][1]*(1-a)+my*a]
        pos.update(new)
    out=[]
    for p,q in segs:
        out.append((tuple(pos[key(p)]),tuple(pos[key(q)])))
    return out
OUT={}
for gi,(rows,chars) in enumerate(zip(groups,labels)):
    cs=sorted(sum((R[r] for r in rows),[]),key=lambda c:c['x'])
    assert len(cs)==len(chars),(gi,len(cs))
    var=2 if gi in (2,3) else 1
    for ch,c in zip(chars,cs):
        x,y,w,h=c['x'],c['y'],c['w'],c['h']
        reg=cv2.dilate((lab[y:y+h,x:x+w]==c['id']).astype(np.uint8),np.ones((5,5),np.uint8))>0
        sub=soft[y:y+h,x:x+w]*reg
        bm=(sub>0.25).astype(np.uint8); nn,ll,ss,_=cv2.connectedComponentsWithStats(bm)
        big=max(ss[1:,4]) if nn>1 else 0
        keepc=[j for j in range(1,nn) if ss[j][4]>=max(10,0.015*big)]
        sub=sub*np.isin(ll,keepc)
        sub=sub*(cv2.dilate(np.isin(ll,keepc).astype(np.uint8),np.ones((3,3)))>0)
        segs=segs_from_soft(sub)
        segs=smooth(segs)
        cls='cap' if ch.isupper() else CL.get(ch,'s')
        mw=WID.get(ch,1.15 if ch.isupper() else 0.8)
        OUT[f'{ch}{var}' if ch.islower() else ch]=fit(segs,*VB[cls],mw)
dots=[q for q in OUT['i1'] if q[0]==q[1] and q[0][1]<-1.05]
if len(dots)>1:
    top=min(dots,key=lambda q:q[0][1]); OUT['i1']=[q for q in OUT['i1'] if not (q in dots and q!=top)]
# render with PF-style pen (reuse font5 renderer)
spec=open('v5/font5.py').read(); k=spec.index('PEN=0.12')
rsrc=spec[k:spec.index('FM={')]
import printfont as PF
ns2={'PF':PF,'math':math,'np':np,'cv2':cv2,'potrace':potrace}
exec(rsrc.replace("open(f'{out}/{name}.svg','w')","open(f'{out}/{name}.svg','w')"),ns2)
render=ns2['render']
FM={}
for key,segs in OUT.items():
    fake=chr(0xE000+len(FM))
    meta=render(fake,segs,out='font7'); FM[key]=meta
json.dump(FM,open('font7/font7.json','w')); print(len(FM))
