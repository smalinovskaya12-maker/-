import json,re
from PIL import ImageFont
from content2 import SLIDES
W,H,LINE,LEFT=1080,1350,66,150; RIGHT=W-80
FD='fonts/'
FONTS={'title':('Amatic SC','Bold','AmaticSC-Bold.ttf',(1016,245,1000),0.758),'body':('Neucha','Regular','Neucha.ttf',(787,292,1024),0.703)}
_c={}
def pil(kind,size):
    k=(kind,size)
    if k not in _c: _c[k]=ImageFont.truetype(FD+FONTS[kind][2],size)
    return _c[k]
def tw(kind,size,s): return pil(kind,size).getlength(s)
def wrap(kind,size,text,width):
    """returns list of lines; each line = list of (segment_text, highlighted)"""
    out=[]
    for para in text.split('\n'):
        para=re.sub(r'\{[^}]*\}',lambda m:m.group(0).replace(' ',' '),para).replace(' → ',' → ')
        words=para.split(' '); line=''
        lines=[]
        for w in words:
            t=(line+' '+w) if line else w
            if tw(kind,size,t.replace('{','').replace('}',''))<=width or not line: line=t
            else: lines.append(line); line=w
        lines.append(line)
        out.append(lines)
    return out
def setblock(kind,size,text,x,y,pitch,res,acc,upper=False):
    if upper: text=text.upper()
    paras=wrap(kind,size,text,RIGHT-x)
    capH=FONTS[kind][4]*size
    for pi,lines in enumerate(paras):
        for ln in lines:
            plain=ln.replace('{','').replace('}','').replace(' ',' ')
            res['texts'].append(dict(kind=kind,size=size,text=plain,x=x,baseline=y))
            # highlight bbox
            m=re.search(r'\{([^}]*)\}',ln)
            if m:
                pre=ln[:m.start()].replace('{','').replace('}','').replace(' ',' ')
                ph=m.group(1).replace(' ',' ')
                hx=x+tw(kind,size,pre); hw=tw(kind,size,ph)
                res['ovals'].append(dict(x=hx-0.45*capH,y=y-capH*1.5,w=hw+0.9*capH,h=capH*2.15,sw=max(3,size*0.07)))
            y+=pitch
        if pi<len(paras)-1: y+=pitch
    return y
def layout(i,sl):
    res=dict(texts=[],ovals=[],deco=[])
    kind=sl.get('kind','prompt')
    if kind=='cover':
        y=setblock('title',124,sl['title'],LEFT,LINE*5,LINE*2,res,True)
        setblock('body',54,sl['body'],LEFT,y+LINE,LINE,res,False)
    elif kind=='final':
        y=setblock('title',112,sl['title'],LEFT,LINE*5,LINE*2,res,True)
        setblock('body',52,sl['body'],LEFT,y+LINE,LINE,res,False)
    else:
        y=setblock('title',100,sl['title'],LEFT,LINE*4,LINE*2,res,True)
        setblock('body',52,sl['body'],LEFT,y+LINE,LINE,res,False)
    res['counter']=dict(text=f"{i+1}/{len(SLIDES)}",size=34,baseline=LINE*2-12)
    if 0<i<len(SLIDES)-1: res['deco'].append('arrow')
    if i==len(SLIDES)-1: res['deco'].append('check')
    res['maxy']=max(t['baseline'] for t in res['texts'])
    return res
if __name__=='__main__':
    L=[layout(i,s) for i,s in enumerate(SLIDES)]
    json.dump(L,open('layout2.json','w'),ensure_ascii=False)
    for i,l in enumerate(L): print(i,len(l['texts']),'lines maxy',l['maxy'],'ovals',len(l['ovals']))
