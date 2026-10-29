import cv2,numpy as np,json
img=cv2.imread('/root/.claude/uploads/3c6ddc69-e598-52ee-84ef-476fa02b92c5/247dde5d-image.jpg')
print(img.shape)
f=img.astype(int); b,g,r=f[...,0],f[...,1],f[...,2]; s=b-r
strong=((s>30)&(b-g>15)).astype(np.uint8)
weak=((s>14)&(b-g>6)).astype(np.uint8)
strong=cv2.morphologyEx(strong,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
n,l,st,_=cv2.connectedComponentsWithStats(weak)
keep=np.zeros(n,bool); keep[np.unique(l[strong>0])]=True; keep[0]=False
m=keep[l].astype(np.uint8)
cv2.imwrite('mask.png',m*255)
d=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,31)))
n,lab,st,cen=cv2.connectedComponentsWithStats(d)
comps=[(i,*st[i]) for i in range(1,n) if m[lab==i].sum()>30]
# rows by y center
comps.sort(key=lambda c:c[2]+c[4]/2)
rows=[];
for c in comps:
    cy=c[2]+c[4]/2
    if rows and abs(cy-rows[-1][-1][0])<45: rows[-1].append((cy,c))
    else: rows.append([(cy,c)])
out=[]
vis=img.copy()
for ri,row in enumerate(rows):
    row.sort(key=lambda t:t[1][1])
    for k,(cy,c) in enumerate(row):
        i,x,y,w,h,a=c; out.append(dict(row=ri,k=k,id=int(i),x=int(x),y=int(y),w=int(w),h=int(h)))
        cv2.rectangle(vis,(x,y),(x+w,y+h),(0,0,255),2); cv2.putText(vis,f'{ri}.{k}',(x,y-4),0,0.6,(0,0,255),2)
print([len(r) for r in rows])
json.dump(out,open('comps.json','w')); np.save('lab.npy',lab); np.save('m.npy',m)
cv2.imwrite('vis.jpg',vis[400:900,330:1700])
