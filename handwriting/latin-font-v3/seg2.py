import cv2,numpy as np,json
img=cv2.imread('v6/rot.jpg'); g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
bg=cv2.GaussianBlur(cv2.dilate(g,np.ones((15,15))),(61,61),0)
diff=bg-g
b,gg,r=[img[...,i].astype(int) for i in range(3)]
blu=(b-r)>-5
strong=((diff>45)&blu).astype(np.uint8); weak=((diff>22)&blu).astype(np.uint8)
n,l,st,_=cv2.connectedComponentsWithStats(weak)
keep=np.zeros(n,bool); keep[np.unique(l[strong>0])]=True; keep[0]=False
m=keep[l].astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
# restrict to writing area
H,W=m.shape
d=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,27)))
n,lab,st,cen=cv2.connectedComponentsWithStats(d)
comps=[(i,*st[i]) for i in range(1,n) if m[lab==i].sum()>25 and st[i][3]>15]
comps.sort(key=lambda c:c[2]+c[4]/2)
rows=[]
for c in comps:
    cy=c[2]+c[4]/2
    if rows and abs(cy-np.median([q[0] for q in rows[-1]]))<38: rows[-1].append((cy,c))
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
