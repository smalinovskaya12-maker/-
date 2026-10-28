import json, random, re
from content import SLIDES
F=json.load(open('font/font.json'))
P={'.':'p_dot',',':'p_comma',':':'p_colon','«':'p_laquo','»':'p_raquo','[':'p_lbr',']':'p_rbr','(':'p_lpar',')':'p_rpar','/':'p_slash','—':'p_emdash','-':'p_hyphen',"'":'p_apos','+':'p_plus','!':'p_excl','?':'p_quest','→':'list_arrow'}
def gname(ch):
    if ch in P: return P[ch]
    if ch.isdigit(): return 'num_'+ch
    if 'a'<=ch<='z': return 'en_'+ch
    return 'ua_'+ch
W,H=1080,1350
LINE=58           # notebook line pitch
LEFT=150; RIGHT=W-70
TRACK=0.2; SPACE=0.78
def tokens(text):
    # returns words: list of (word, highlighted)
    out=[];hl=False
    text=re.sub(r'\{[^}]*\}',lambda m:m.group(0).replace(' ','\u00a0'),text)
    for para in text.split('\n'):
        words=[]
        for w in para.split(' '):
            cur='';parts=[]
            for ch in w:
                if ch=='{': hl=True; continue
                if ch=='}': hl=False; parts.append(('}',None)); continue
                parts.append((ch,hl))
            words.append(parts)
        out.append(words)
    return out
def wordwidth(parts,xh):
    w=0
    for ch,h in parts:
        if ch=='}': continue
        if ch=='\u00a0': w+=SPACE*xh; continue
        g=F[gname(ch)]; s=xh*g['u']; w+=(g['cr']-g['cl'])*s+TRACK*xh
    return w-TRACK*xh if parts else 0
def set_text(text,xh,x0,width,y0,pitch,glyphs,hls,maxlines=99):
    y=y0; lines=0
    for pi,para in enumerate(tokens(text)):
        x=x0
        for parts in para:
            ww=wordwidth(parts,xh)
            if x>x0 and x+ww>x0+width:
                x=x0; y+=pitch; lines+=1
            for ch,h in parts:
                if ch=='}': continue
                if ch=='\u00a0':
                    if h: hls.append((x,y,SPACE*xh,xh))
                    x+=SPACE*xh; continue
                gn=gname(ch); g=F[gn]; s=xh*g['u']
                # small jitter for natural look
                jy=random.uniform(-0.04,0.04)*xh
                glyphs.append(dict(g=gn,x=round(x-g['cl']*s,1),y=round(y-g['bt']*s+jy,1),s=round(s,4)))
                if h: hls.append((x,y,(g['cr']-g['cl'])*s,xh))
                x+=(g['cr']-g['cl'])*s+TRACK*xh
            x+=SPACE*xh
        y+=pitch*(1 if pi==len(tokens(text))-1 else 2); lines+=2
    return y
def merge_hls(hls,xh):
    # group consecutive highlighted glyphs on same baseline into boxes
    boxes=[]
    for x,y,w,h in hls:
        if boxes and abs(boxes[-1][1]-y)<1 and x-boxes[-1][2]<xh*1.2:
            boxes[-1][2]=x+w
        else: boxes.append([x,y,x+w])
    return boxes
def layout(i,sl):
    random.seed(i)
    glyphs=[];hls=[];deco=[]
    kind=sl.get('kind','prompt')
    if kind=='cover':
        y=LINE*5; xh=36
        y=set_text(sl['title'],xh,LEFT,RIGHT-LEFT,y,LINE*2,glyphs,hls)
        y+=LINE
        set_text(sl['body'],28,LEFT,RIGHT-LEFT,y,LINE,glyphs,hls)
        bxh=xh
    elif kind=='final':
        y=LINE*5; xh=40
        y=set_text(sl['title'],xh,LEFT,RIGHT-LEFT,y,LINE*2,glyphs,hls)
        y+=LINE
        set_text(sl['body'],27,LEFT,RIGHT-LEFT,y,LINE,glyphs,hls)
        bxh=27
    else:
        y=LINE*4; xh=36
        y=set_text(sl['title'],xh,LEFT,RIGHT-LEFT,y,LINE*2,glyphs,hls)
        y+=LINE
        set_text(sl['body'],24,LEFT,RIGHT-LEFT,y,LINE,glyphs,hls)
        bxh=24
    boxes=merge_hls(hls,bxh)
    # page counter top-right, handwritten
    cnt=f"{i+1}/{len(SLIDES)}"; cg=[]; cxh=22
    set_text(cnt,cxh,0,999,LINE*2-14,LINE,cg,[])
    wmax=max(g['x']+F[g['g']]['W']*g['s'] for g in cg)
    for g in cg: g['x']=round(g['x']+RIGHT-wmax,1)
    glyphs+=cg
    deco=[]
    if i<len(SLIDES)-1: deco.append(dict(g='sym_arrow_right',x=RIGHT-150,y=H-LINE*2-28,w=150))
    else: deco.append(dict(g='sym_check',x=RIGHT-90,y=H-LINE*3-60,w=80))
    return dict(deco=deco,glyphs=glyphs,ovals=[[round(a,1),round(b,1),round(c,1),bxh] for a,b,c in boxes],maxy=max(g['y']+F[g['g']]['H']*g['s'] for g in glyphs))
if __name__=='__main__':
    L=[layout(i,s) for i,s in enumerate(SLIDES)]
    json.dump(L,open('layout.json','w'))
    for i,l in enumerate(L): print(i,len(l['glyphs']),'maxy',round(l['maxy']),'ovals',len(l['ovals']))
