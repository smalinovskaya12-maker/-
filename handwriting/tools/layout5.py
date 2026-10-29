import json,re
from content4 import SLIDES
F=json.load(open('font5/font2.json'))
W,H=1080,1350; P=62
TRACK=0.2; SPACE=0.72
GEO={'A':dict(left=175,right=965,top=80,ct=48,cb=30,ft=48,fb=29,lab=25,role=46,tool=25,body=27,r0=3),'B':dict(left=110,right=975,top=0,ct=52,cb=32,ft=52,fb=31,lab=27,role=52,tool=27,body=29,r0=4)}
def adv(ch,xh):
    if ch in(' ',' '): return SPACE*xh
    g=F[ch]; return (g['cr']-g['cl'])*g['u']*xh+TRACK*xh
def words(text):
    text=re.sub(r'\{[^}]*\}',lambda m:m.group(0).replace(' ',' '),text).replace(' → ',' → ')
    paras=[]
    for para in text.split('\n'):
        ws=[];hl=False
        for w in para.split(' '):
            parts=[]
            for ch in w:
                if ch=='{': hl=True; continue
                if ch=='}': hl=False; continue
                parts.append((ch,hl))
            ws.append(parts)
        paras.append(ws)
    return paras
def setblock(text,xh,x0,x1,y,pitch,role,out,marks):
    paras=words(text.lower())
    for pi,ws in enumerate(paras):
        x=x0
        for parts in ws:
            if [c for c,_ in parts]==['|']: x=x0; y+=pitch; continue
            ww=sum(adv(c,xh) for c,_ in parts)-TRACK*xh
            if x>x0 and x+ww>x1: x=x0; y+=pitch
            for ch,h in parts:
                if ch==' ':
                    if h: marks.append([x,y,x+SPACE*xh,xh])
                    x+=SPACE*xh; continue
                g=F[ch]; s=g['u']*xh
                out.append(dict(c=ch,x=round(x-g['cl']*s,1),y=round(y-g['bt']*s,1),s=round(s,4),r=('hl' if h else role)))
                if h: marks.append([x,y,x+(g['cr']-g['cl'])*s,xh])
                x+=adv(ch,xh)
            x+=SPACE*xh
        if pi<len(paras)-1: y+=pitch*2
    return y
def merge(marks):
    out=[]
    for x,y,x2,xh in marks:
        if out and abs(out[-1][1]-y)<1 and x-out[-1][2]<xh: out[-1][2]=x2
        else: out.append([x,y,x2,xh])
    return out
def layout(i,sl,geo):
    g=GEO[geo]; L,R,T=g['left'],g['right'],g['top']
    out=[];marks=[]
    base=lambda k: T+P*k
    kind=sl.get('kind','prompt')
    if kind=='cover':
        y=setblock(sl['title'],g['ct'],L,R,base(g['r0']+1),P*2,'ink',out,marks)
        setblock(sl['body'],g['cb'],L,R,y+P*2,P,'ink',out,marks)
    elif kind=='final':
        y=setblock(sl['title'],g['ft'],L,R,base(g['r0']+1),P*2,'ink',out,marks)
        setblock(sl['body'],g['fb'],L,R,y+P*2,P,'ink',out,marks)
    else:
        setblock(f"промпт {sl['n']}",g['lab'],L,R,base(g['r0']),P,'acc',out,[])
        y=setblock(sl['role'],g['role'],L,R,base(g['r0']+2),P*2,'ink',out,[])
        y=setblock(sl['tool'],g['tool'],L,R,y+P*2,P,'acc',out,[])
        setblock(sl['body'],g['body'],L,R,y+P,P,'ink',out,marks)
    # handle + counter
    hd=[]; setblock('@anton.tsevmenko',18,L,R,base(2),P,'muted',hd,[])
    cn=[]; setblock(f"{i+1}/{len(SLIDES)}",22,0,999,base(2),P,'muted',cn,[])
    wmax=max(q['x']+F[q['c']]['W']*q['s'] for q in cn)
    for q in cn: q['x']=round(q['x']+R-wmax,1)
    out+=hd+cn
    deco=[]
    if 0<i<len(SLIDES)-1: deco.append('arrow')
    if i==len(SLIDES)-1: deco.append('check')
    return dict(g=out,marks=merge(marks),deco=deco,maxy=max(q['y']+F[q['c']]['H']*q['s'] for q in out))
if __name__=='__main__':
    for geo in 'AB':
        Ls=[layout(i,s,geo) for i,s in enumerate(SLIDES)]
        json.dump(Ls,open(f'layout5{geo}.json','w'),ensure_ascii=False)
        print(geo,[round(l['maxy']) for l in Ls])
