import json,base64
F=json.load(open('font6/font6.json'))
lines=[[c+'1' for c in 'abcdefghijklmnopqrstuvwxyz'],[c+'2' for c in 'abcdefghijklmnopqrstuvwxyz'],list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')]
XH=40;o=[];y=90
for ln in lines:
    x=30
    for k in ln:
        g=F[k]; s=XH*g['u']; svg=open('font6/'+g['file']).read()
        o.append(f'<img src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}" style="position:absolute;left:{x-g["cl"]*s}px;top:{y-g["bt"]*s}px;width:{g["W"]*s}px;height:{g["H"]*s}px">')
        x+=(g['cr']-g['cl'])*s+XH*0.45
    o.append(f'<div style="position:absolute;left:0;top:{y}px;width:2000px;height:1px;background:#f88"></div><div style="position:absolute;left:0;top:{y-XH}px;width:2000px;height:1px;background:#8cf"></div>')
    y+=XH*3
open('v6/alpha6.html','w').write('<html><body style="margin:0;background:#fff"><div style="position:relative">'+''.join(o)+'</div></body></html>')
