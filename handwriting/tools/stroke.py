import cv2, numpy as np, json, potrace
F=json.load(open('font/font.json'))
UP=4
def width(m):
    cs,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    per=sum(cv2.arcLength(c,True) for c in cs)
    return 2*m.sum()/max(per,1)
names=[n for n in F if n.startswith(('ua_','en_','num_')) and n!='num_0']
masks={};ws={}
for n in names:
    src='out/png/num_10.png' if n=='num_0' else f'out/png/{n}.png'
    a=cv2.imread(src,-1)[...,3].astype(np.float32)
    if n=='num_0':
        # rebuild num_0 mask from its svg size: take right part like buildfont did
        W=int(round(F[n]['W'])); a=a[:, a.shape[1]-W:] if a.shape[1]>=W else a
    big=cv2.resize(a,None,fx=UP,fy=UP,interpolation=cv2.INTER_CUBIC)>127
    masks[n]=big; ws[n]=width(big)/UP
ratios={n:ws[n]*F[n]['u'] for n in names}
target=float(np.median(list(ratios.values())))*1.2
print('target stroke/xh',round(target,3), 'range',round(min(ratios.values()),3),round(max(ratios.values()),3))
for n in names:
    big=masks[n]; want=target/F[n]['u']; d=(want-ws[n])/2*UP
    if d>0.5:
        dt=cv2.distanceTransform((~big).astype(np.uint8),cv2.DIST_L2,5); big=dt<=d
    elif d<-0.5:
        dt=cv2.distanceTransform(big.astype(np.uint8),cv2.DIST_L2,5); big=dt>-d
    path=potrace.Bitmap(~big).trace(turdsize=30,alphamax=1.0,opticurve=True,opttolerance=0.4)
    ds=[]
    for c in path:
        p=c.start_point; seg=[f'M{p.x/UP:.1f} {p.y/UP:.1f}']
        for sg in c.segments:
            seg.append(f'L{sg.c.x/UP:.1f} {sg.c.y/UP:.1f}L{sg.end_point.x/UP:.1f} {sg.end_point.y/UP:.1f}' if sg.is_corner else f'C{sg.c1.x/UP:.1f} {sg.c1.y/UP:.1f} {sg.c2.x/UP:.1f} {sg.c2.y/UP:.1f} {sg.end_point.x/UP:.1f} {sg.end_point.y/UP:.1f}')
        ds.append(''.join(seg)+'Z')
    H,W=big.shape[0]/UP,big.shape[1]/UP
    open('font/'+F[n]['file'],'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}"><path fill="#1E2A8C" fill-rule="evenodd" d="{" ".join(ds)}"/></svg>')
# synthetic punctuation stroke: match target
import re
for n,g in F.items():
    if n.startswith('p_'):
        s=open('font/'+g['file']).read()
        sw=target/g['u']
        s=re.sub(r'stroke-width="[\d.]+"',f'stroke-width="{sw:.1f}"',s)
        s=re.sub(r'r="[\d.]+"',f'r="{sw*0.62:.1f}"',s)
        open('font/'+g['file'],'w').write(s)
