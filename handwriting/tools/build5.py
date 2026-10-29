import json,numpy as np,cv2,potrace,math,sys
from skimage.morphology import skeletonize
sys.path.insert(0,'.')
V='v5/'
comps=json.load(open(V+'comps.json')); lab=np.load(V+'lab.npy'); m=np.load(V+'m.npy')
img=cv2.imread('/root/.claude/uploads/3c6ddc69-e598-52ee-84ef-476fa02b92c5/247dde5d-image.jpg').astype(int)
sb=img[...,0]-img[...,2]; sg=img[...,0]-img[...,1]
soft=np.clip((sb-3)/18.0,0,1)*(sg>1)   # soft ink map
rows=['абвгґдеєжзиіїйклм','нопрстуфхцчшщьюя',list('abcde')+['X']+list('fghijkl')+['X']+list('mnop'),list('qrstuvwxyz')]
UPS=4
def nb(sk):
    k=np.ones((3,3),np.uint8); k[1,1]=0
    return cv2.filter2D(sk.astype(np.uint8),-1,k,borderType=cv2.BORDER_CONSTANT)
def segs_from_mask(mask):
    a=mask.astype(np.float32)*255
    big=cv2.resize(a,None,fx=UPS,fy=UPS,interpolation=cv2.INTER_CUBIC)
    big=cv2.GaussianBlur(big,(5,5),0)>110
    n,lb,st,cen=cv2.connectedComponentsWithStats(big.astype(np.uint8))
    sk=skeletonize(big).astype(np.uint8)
    for _ in range(6):
        c=nb(sk); sk[(sk==1)&(c==1)]=0
    extra=[]
    for j in range(1,n):
        if st[j][4]<15: continue
        if not sk[lb==j].any(): cx,cy=cen[j]; extra.append((int(cy),int(cx)))
    ys,xs=np.nonzero(sk); S=set(zip(ys.tolist(),xs.tolist()))
    segs=[]
    for (y,x) in S:
        for dy,dx in ((0,1),(1,0),(1,1),(1,-1)):
            if (y+dy,x+dx) in S: segs.append(((x,y),(x+dx,y+dy)))
    for (y,x) in extra: segs.append(((x,y),(x,y)))
    return segs
def segs_from_soft(sm):
    big=cv2.resize(sm.astype(np.float32),None,fx=UPS,fy=UPS,interpolation=cv2.INTER_CUBIC)
    big=cv2.GaussianBlur(big,(7,7),0)>0.28
    big=cv2.morphologyEx(big.astype(np.uint8),cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))>0
    n,lb,st,cen=cv2.connectedComponentsWithStats(big.astype(np.uint8))
    # drop specks
    for j in range(1,n):
        if st[j][4]<25: big[lb==j]=False
    n,lb,st,cen=cv2.connectedComponentsWithStats(big.astype(np.uint8))
    sk=skeletonize(big).astype(np.uint8)
    for _ in range(5):
        cc=nb(sk); sk[(sk==1)&(cc==1)]=0
    extra=[]
    for j in range(1,n):
        if not sk[lb==j].any(): cx,cy=cen[j]; extra.append((int(cy),int(cx)))
    ys,xs=np.nonzero(sk); S=set(zip(ys.tolist(),xs.tolist()))
    segs=[]
    for (y,x) in S:
        for dy,dx in ((0,1),(1,0),(1,1),(1,-1)):
            if (y+dy,x+dx) in S: segs.append(((x,y),(x+dx,y+dy)))
    for (y,x) in extra: segs.append(((x,y),(x,y)))
    return segs
def bbox(segs):
    xs=[p[0] for s in segs for p in s]; ys=[p[1] for s in segs for p in s]
    return min(xs),min(ys),max(xs),max(ys)
def fit(segs,top,bot,maxw):
    x0,y0,x1,y1=bbox(segs); h=max(y1-y0,1e-6); w=x1-x0
    k=(bot-top)/h; kx=k
    if w*kx>maxw: kx=maxw/w
    return [tuple(((p[0]-x0)*kx,top+(p[1]-y0)*k) for p in s) for s in segs]
# class boxes (cap-height = 1): all same height
VB={'n':(-1,0),'desc':(-1,0.26),'acc':(-1.3,0),'dot':(-1.3,0)}
CLS={'д':'desc','ц':'desc','щ':'desc','й':'acc','ї':'dot','і':'dot','ґ':'acc','i':'dot','q':'n'}
WID={'ж':1.05,'ш':1.0,'щ':1.05,'ю':1.05,'м':0.95,'m':0.95,'w':1.05,'ф':0.95,'ы':1}
C={}
byrow={}
for c in comps: byrow.setdefault(c['row'],[]).append(c)
for ri,chars in enumerate(rows):
    cs=sorted(byrow[ri],key=lambda c:c['k'])
    assert len(cs)==len(chars),(ri,len(cs),len(chars))
    for ch,c in zip(chars,cs):
        if ch=='X': continue
        x,y,w,h=c['x'],c['y'],c['w'],c['h']
        reg=cv2.dilate((lab[y:y+h,x:x+w]==c['id']).astype(np.uint8),np.ones((5,5),np.uint8))>0
        sm=soft[y:y+h,x:x+w]*reg
        segs=segs_from_soft(sm)
        C[ch]=fit(segs,*VB[CLS.get(ch,'n')],WID.get(ch,0.82))
json.dump({k:v for k,v in C.items()},open(V+'segs_letters.json','w'))
print(len(C))
