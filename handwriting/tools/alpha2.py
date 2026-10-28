import json,base64,sys
F2=json.load(open('font2/font2.json'))
lines=sys.argv[1:] or ['а б в г ґ д е є ж з и і ї й к л м н о п','р с т у ф х ц ч ш щ ь ю я','a b c d e f g h i j k l m n o p q r s t','u v w x y z 0 1 2 3 4 5 6 7 8 9','промпт аналітик джерел шість','читається легко і рівно']
XH=40; o=[]; y=90
for t in lines:
    x=30
    for ch in t:
        if ch==' ': x+=XH*0.9; continue
        g=F2[ch]; s=XH*g['u']
        svg=open('font2/'+g['file']).read()
        o.append(f'<img src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}" style="position:absolute;left:{x-g["cl"]*s}px;top:{y-g["bt"]*s}px;width:{g["W"]*s}px;height:{g["H"]*s}px">')
        x+=(g['cr']-g['cl'])*s+XH*0.12
    o.append(f'<div style="position:absolute;left:0;top:{y}px;width:1800px;height:1px;background:#f88"></div><div style="position:absolute;left:0;top:{y-XH}px;width:1800px;height:1px;background:#8cf"></div>')
    y+=XH*2.6
open('alpha2.html','w').write('<html><body style="margin:0;background:#fff"><div style="position:relative;width:1600px;height:%dpx">'%(y)+''.join(o)+'</div></body></html>')
