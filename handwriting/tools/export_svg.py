import json,re,base64
from layout import F,W,H,LINE,LEFT
from render import TH
from ovalgen import oval_svg
L=json.load(open('layout.json'))
def inner(n,color):
    s=open('font/'+F[n]['file']).read()
    s=s.replace('#1E2A8C',color)
    return re.sub(r'^<svg[^>]*>','',s).replace('</svg>','')
def g(n,x,y,s,color,label=None):
    return f'<g id="{label or n}" transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{inner(n,color)}</g>'
for theme in ['dark','white']:
    t=TH[theme]
    for i,l in enumerate(L):
        o=[]
        for k,(x,y,x2,xh) in enumerate(l['ovals']):
            ox=x-0.6*xh; oy=y-2.1*xh; ow=x2-x+1.2*xh; oh=3.0*xh
            sv=oval_svg(ow,oh,0.17*xh,t['acc'],seed=int(x))
            body=re.sub(r'^<svg[^>]*>','',sv).replace('</svg>','')
            o.append(f'<g id="highlight" transform="translate({ox:.1f} {oy:.1f})">{body}</g>')
        o.append('<g id="text">'+''.join(g(q['g'],q['x'],q['y'],q['s'],t['ink']) for q in l['glyphs'])+'</g>')
        for d in l['deco']:
            f=F[d['g']]; s=d['w']/f['W']
            o.append(g(d['g'],d['x'],d['y'],s,t['ink'] if d['g']=='sym_arrow_right' else t['acc'],label='swipe arrow' if d['g']=='sym_arrow_right' else 'check'))
        open(f'up/{theme}_{i+1}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'+''.join(o)+'</svg>')
# glyph sheet: all glyphs in grid at native size*1.5
items=sorted(F); x=y=0; o=[]; cols=14; cell=120
for k,n in enumerate(items):
    f=F[n]; s=min(1.0,100/max(f['W'],f['H']))
    cx=(k%cols)*cell; cy=(k//cols)*cell
    o.append(g(n,cx,cy,s,'#1E2A8C'))
open('up/glyphs.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols*cell}" height="{(len(items)//cols+1)*cell}">'+''.join(o)+'</svg>')
