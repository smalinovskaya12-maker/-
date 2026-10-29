import json,re,math,random
from layout6 import W,H,P,GEO,F
FO=json.load(open('font/font.json'))  # old glyphs: arrows/check
from ovalgen import oval_svg
TH={'A':dict(outer='#1F3B2E',page='#FBFAF5',shadow='#132820',line='#C9D6EA',margin='#C9D6EA',hole='#1F3B2E',ink='#1E2A8C',acc='#2E86C1',muted='#8A93B5',hl='#1E2A8C',foot='#E9E4D6',marker='#C1F993',check='#4CAF50'),
    'B':dict(outer='#0E1626',dot='#FFFFFF',ink='#FFFFFF',acc='#AAE3FF',muted='#7F8BA6',hl='#C1F993',marker=None,check='#C1F993')}
_inner={}
def inner(path_file):
    if path_file not in _inner:
        s=open(path_file).read(); _inner[path_file]=re.search(r' d="([^"]+)"',s).group(1)
    return _inner[path_file]
def glyph(q,color):
    return f'<path transform="translate({q["x"]} {q["y"]}) scale({q["s"]})" fill="{color}" fill-rule="evenodd" d="{inner("font5/"+F[q["c"]]["file"])}"/>'
def oldsym(n,color,x,y,w):
    g=FO[n]; s=w/g['W']; d=inner('font/'+g['file'])
    return f'<path transform="translate({x} {y}) scale({s:.4f})" fill="{color}" fill-rule="evenodd" d="{d}"/>'
def marker(x,y,w,h,col,seed):
    random.seed(seed); j=lambda a:a+random.uniform(-0.04,0.04)*h
    pts=[(x,j(y+h*0.12)),(x+w*0.5,j(y)),(x+w,j(y+h*0.08)),(x+w+h*0.05,j(y+h*0.55)),(x+w,j(y+h)),(x+w*0.5,j(y+h*0.95)),(x,j(y+h*0.9)),(x-h*0.06,j(y+h*0.45))]
    d='M'+' L'.join(f'{a:.1f} {b:.1f}' for a,b in pts)+'Z'
    return f'<path d="{d}" fill="{col}" opacity="0.92"/>'
def slide(geo,i,l):
    t=TH[geo]; g=GEO[geo]; o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    o.append(f'<rect id="background" width="{W}" height="{H}" fill="{t["outer"]}"/>')
    if geo=='A':
        px0,py0,px1,py1=60,g['top'],1020,1270
        o.append(f'<g id="paper"><rect x="{px0+10}" y="{py0+14}" width="{px1-px0}" height="{py1-py0}" rx="6" fill="{t["shadow"]}"/>')
        o.append(f'<rect x="{px0}" y="{py0}" width="{px1-px0}" height="{py1-py0}" rx="6" fill="{t["page"]}"/>')
        k=2
        while py0+P*k<py1-10:
            o.append(f'<rect x="{px0}" y="{py0+P*k}" width="{px1-px0}" height="2" fill="{t["line"]}"/>'); k+=1
        o.append(f'<rect x="{g["left"]-28}" y="{py0}" width="2" height="{py1-py0}" fill="{t["margin"]}"/>')
        x=px0+26
        while x<px1-30:
            o.append(f'<rect x="{x}" y="{py0+18}" width="14" height="24" rx="5" fill="{t["hole"]}"/>'); x+=40
        o.append('</g>')
    else:
        o.append('<g id="dot grid" opacity="0.13">')
        for yy in range(31,H,31):
            for xx in range(31,W,31): o.append(f'<circle cx="{xx}" cy="{yy}" r="1.6" fill="{t["dot"]}"/>')
        o.append('</g>')
    # highlights
    o.append('<g id="highlight">')
    for k,(x,y,x2,xh) in enumerate(l['marks']):
        if t.get('marker'):
            o.append(marker(x-0.4*xh,y-1.45*xh,x2-x+0.8*xh,1.9*xh,t['marker'],i*7+k))
        elif False:
            ow=x2-x+1.8*xh; oh=3.0*xh
            sv=oval_svg(ow,oh,0.16*xh,t['acc'],seed=i*7+k)
            body=re.sub(r'^<svg[^>]*>','',sv).replace('</svg>','')
            o.append(f'<g transform="translate({x-0.9*xh:.1f} {y-2.0*xh:.1f})">{body}</g>')
    o.append('</g>')
    if geo=='B' and l.get('brange'):
        a,b=l['brange']; gs=l['g'][a:b]
        x0=min(q['x'] for q in gs); y0=min(q['y'] for q in gs)
        x1=max(q['x']+F[q['c']]['W']*q['s'] for q in gs); y1=max(q['y']+F[q['c']]['H']*q['s'] for q in gs)
        o.insert(o.index('<g id="highlight">'),f'<rect id="plate" x="{x0-26:.0f}" y="{y0-12:.0f}" width="{x1-x0+52:.0f}" height="{y1-y0+34:.0f}" rx="18" fill="#FFFFFF" fill-opacity="0.10"/>')
    o.append('<g id="text">')
    for q in l['g']:
        col=t[q['r']]
        if geo=='A' and q['r']=='muted' and q['c'] and q['y']>0 and False: pass
        o.append(glyph(q,col))
    o.append('</g>')
    if geo=='A':
        ay=1270+(80-30)/2
        if 'arrow' in l['deco']: o.append(f'<g id="swipe arrow">{oldsym("sym_arrow_right",t["foot"],1020-130,1290,130)}</g>')
        if 'check' in l['deco']: o.append(f'<g id="check">{oldsym("sym_check",t["check"],g["right"]-90,1270-170,80)}</g>')
    else:
        if 'arrow' in l['deco']: o.append(f'<g id="swipe arrow">{oldsym("sym_arrow_right",t["ink"],g["right"]-150,H-P*2-26,150)}</g>')
        if 'check' in l['deco']: o.append(f'<g id="check">{oldsym("sym_check",t["check"],g["right"]-90,H-P*3-60,80)}</g>')
    o.append('</svg>'); return ''.join(o)
if __name__=='__main__':
    import os; os.makedirs('up6',exist_ok=True)
    html=['<html><body style="margin:0;background:#555;display:flex;flex-wrap:wrap;gap:20px;padding:20px;width:4400px">']
    for geo in 'AB':
        Ls=json.load(open(f'layout6{geo}.json'))
        for i,l in enumerate(Ls):
            sv=slide(geo,i,l); open(f'up6/{geo}_{i+1}.svg','w').write(sv); html.append(f'<div class="s">{sv}</div>')
    html.append('</body></html>'); open('preview6.html','w').write(''.join(html))
