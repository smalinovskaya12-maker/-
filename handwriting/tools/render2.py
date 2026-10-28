import json,base64,html
from layout2 import W,H,LINE,LEFT,RIGHT,FONTS
from ovalgen import oval_svg
L=json.load(open('layout2.json'))
F=json.load(open('font/font.json'))
TH={'white':dict(bg='#FBFAF5',ink='#1E2A8C',acc='#D8343A',line='#C7D6EC',margin='#E7A3A3',handle='#8A93B5',grid=False),
    'dark':dict(bg='#0F1B2E',ink='#F2EEE3',acc='#FFC845',line='rgba(255,255,255,0.075)',handle='#7F8BA6',grid=True)}
def sym(n,color,x,y,w):
    s=open('font/'+F[n]['file']).read().replace('#1E2A8C',color)
    sc=w/F[n]['W']; return f'<image href="data:image/svg+xml;base64,{base64.b64encode(s.encode()).decode()}" x="{x}" y="{y}" width="{w}" height="{F[n]["H"]*sc}"/>'
def slide(theme,i,l):
    t=TH[theme]; o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" class="s"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    if t['grid']:
        st=LINE/2
        o+= [f'<rect x="0" y="{k*st}" width="{W}" height="1" fill="{t["line"]}"/>' for k in range(1,int(H/st)+1)]
        o+= [f'<rect x="{k*st}" y="0" width="1" height="{H}" fill="{t["line"]}"/>' for k in range(1,int(W/st)+1)]
    else:
        o+= [f'<rect x="0" y="{k*LINE}" width="{W}" height="2" fill="{t["line"]}"/>' for k in range(2,int(H/LINE)+1)]
        o.append(f'<rect x="{LEFT-30}" y="0" width="2" height="{H}" fill="{t["margin"]}"/>')
    o.append(f'<text x="{LEFT}" y="{LINE*2-16}" font-family="Inter" font-weight="500" font-size="22" fill="{t["handle"]}">@anton.tsevmenko</text>')
    c=l['counter']; o.append(f'<text x="{RIGHT}" y="{c["baseline"]}" text-anchor="end" font-family="Neucha" font-size="{c["size"]}" fill="{t["ink"]}">{c["text"]}</text>')
    for k,ov in enumerate(l['ovals']):
        sv=oval_svg(ov['w'],ov['h'],ov['sw'],t['acc'],seed=k+i)
        o.append(f'<image href="data:image/svg+xml;base64,{base64.b64encode(sv.encode()).decode()}" x="{ov["x"]}" y="{ov["y"]}" width="{ov["w"]:.0f}" height="{ov["h"]:.0f}"/>')
    for tx in l['texts']:
        fam=FONTS[tx['kind']][0]; wt='700' if tx['kind']=='title' else '400'
        o.append(f'<text x="{tx["x"]}" y="{tx["baseline"]}" font-family="{fam}" font-weight="{wt}" font-size="{tx["size"]}" fill="{t["ink"]}">{html.escape(tx["text"])}</text>')
    if 'arrow' in l['deco']: o.append(sym('sym_arrow_right',t['ink'],RIGHT-150,H-LINE*2-28,150))
    if 'check' in l['deco']: o.append(sym('sym_check',t['acc'],RIGHT-90,H-LINE*3-60,80))
    o.append('</svg>'); return ''.join(o)
ff=''.join(f"@font-face{{font-family:'{n}';font-weight:{w};src:url(fonts/{f})}}" for n,w,f in [('Neucha',400,'Neucha.ttf'),('Amatic SC',700,'AmaticSC-Bold.ttf')])
h=[f'<html><head><style>{ff}body{{margin:0;background:#555;display:flex;flex-wrap:wrap;gap:20px;padding:20px;width:4400px}}</style></head><body>']
for th in ['dark','white']:
    for i,l in enumerate(L): h.append(slide(th,i,l))
h.append('</body></html>'); open('preview2.html','w').write(''.join(h))
