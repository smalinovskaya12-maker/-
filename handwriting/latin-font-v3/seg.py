import cv2,numpy as np,json
img=cv2.imread('/root/.claude/uploads/3c6ddc69-e598-52ee-84ef-476fa02b92c5/da0d99e3-image.jpg')
img=cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE); cv2.imwrite('v6/rot.jpg',img)
print(img.shape)
f=img.astype(int); b,g,r=f[...,0],f[...,1],f[...,2]; s=b-r
strong=((s>30)&(b-g>12)).astype(np.uint8)
weak=((s>12)&(b-g>4)).astype(np.uint8)
strong=cv2.morphologyEx(strong,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
n,l,st,_=cv2.connectedComponentsWithStats(weak)
keep=np.zeros(n,bool); keep[np.unique(l[strong>0])]=True; keep[0]=False
m=keep[l].astype(np.uint8)
d=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,25)))
n,lab,st,cen=cv2.connectedComponentsWithStats(d)
comps=[(i,*st[i]) for i in range(1,n) if m[lab==i].sum()>20]
comps.sort(key=lambda c:c[2]+c[4]/2)
rows=[]
for c in comps:
    cy=c[2]+c[4]/2
    if rows and abs(cy-np.median([q[0] for q in rows[-1]]))<35: rows[-1].append((cy,c))
    else: rows.append([(cy,c)])
out=[];vis=img.copy()
for ri,row in enumerate(rows):
    row.sort(key=lambda t:t[1][1])
    for k,(cy,c) in enumerate(row):
        i,x,y,w,h,a=c; out.append(dict(row=ri,k=k,id=int(i),x=int(x),y=int(y),w=int(w),h=int(h)))
        cv2.rectangle(vis,(x,y),(x+w,y+h),(0,0,255),2); cv2.putText(vis,f'{ri}.{k}',(x,y-3),0,0.5,(0,0,255),1)
print([len(r) for r in rows])
json.dump(out,open('v6/comps.json','w')); np.save('v6/lab.npy',lab); np.save('v6/m.npy',m)
ys=[c['y'] for c in out]; xs=[c['x'] for c in out]
cv2.imwrite('v6/vis.jpg',vis[max(0,min(ys)-40):max(ys)+80, max(0,min(xs)-30):max(xs)+80])
