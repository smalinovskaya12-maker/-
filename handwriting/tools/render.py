import json,sys
from layout import F,W,H,LINE,LEFT
L=json.load(open('layout.json'))
TH={'white':dict(bg='#FBFAF5',ink='#1E2A8C',acc='#D8343A',line='#C7D6EC',margin='#E7A3A3',handle='#8A93B5',grid=False),
    'dark':dict(bg='#0F1B2E',ink='#F2EEE3',acc='#FFC845',line='rgba(255,255,255,0.075)',margin=None,handle='#7F8BA6',grid=True)}
svgs={k:open('font/'+v['file']).read() for k,v in F.items()}
def colored(n,c):
    return svgs[n].replace('#1E2A8C',c)
import base64
from ovalgen import oval_svg
def uri(n,c,stretch=False):
    s=colored(n,c)
    if stretch: s=s.replace('<svg ','<svg preserveAspectRatio="none" ',1)
    return 'data:image/svg+xml;base64,'+base64.b64encode(s.encode()).decode()
def _old(n,c): return 'data:image/svg+xml;base64,'+base64.b64encode(colored(n,c).encode()).decode()
def page(theme,i,l):
    t=TH[theme]; o=[]
    o.append(f'<div class="s" style="background:{t["bg"]}">')
    if t['grid']:
        step=LINE/2
        for k in range(1,int(H/step)+1): o.append(f'<i style="top:{k*step}px;left:0;width:{W}px;height:1px;background:{t["line"]}"></i>')
        for k in range(1,int(W/step)+1): o.append(f'<i style="left:{k*step}px;top:0;height:{H}px;width:1px;background:{t["line"]}"></i>')
    else:
        for k in range(2,int(H/LINE)+1): o.append(f'<i style="top:{k*LINE}px;left:0;width:{W}px;height:2px;background:{t["line"]}"></i>')
        o.append(f'<i style="left:{LEFT-30}px;top:0;height:{H}px;width:2px;background:{t["margin"]}"></i>')
    o.append(f'<b style="left:{LEFT}px;top:{LINE*2-34}px;color:{t["handle"]}">@anton.tsevmenko</b>')
    for x,y,x2,xh in l['ovals']:
        ox=x-0.6*xh; oy=y-2.1*xh; ow=x2-x+1.2*xh; oh=3.0*xh
        sv=oval_svg(ow,oh,0.17*xh,t['acc'],seed=int(x))
        o.append(f'<img src="data:image/svg+xml;base64,{base64.b64encode(sv.encode()).decode()}" style="left:{ox}px;top:{oy}px;width:{ow:.0f}px;height:{oh:.0f}px">')
    for g in l['glyphs']:
        f=F[g['g']]
        o.append(f'<img src="{uri(g["g"],t["ink"])}" style="left:{g["x"]}px;top:{g["y"]}px;width:{f["W"]*g["s"]}px;height:{f["H"]*g["s"]}px">')
    for d in l['deco']:
        f=F[d['g']]; s=d['w']/f['W']
        o.append(f'<img src="{uri(d["g"],t["acc"] if d["g"]!="sym_arrow_right" else t["ink"])}" style="left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;height:{f["H"]*s}px">')
    o.append('</div>'); return ''.join(o)
html=['<html><head><style>body{margin:0;background:#555;display:flex;flex-wrap:wrap;gap:20px;padding:20px;width:%dpx}.s{position:relative;width:%dpx;height:%dpx;overflow:hidden}.s *{position:absolute}b{font:500 22px Inter,sans-serif;letter-spacing:.2px}</style></head><body>'%(4*1100,W,H)]
for theme in ['dark','white']:
    for i,l in enumerate(L): html.append(page(theme,i,l))
html.append('</body></html>')
open('preview.html','w').write(''.join(html))
