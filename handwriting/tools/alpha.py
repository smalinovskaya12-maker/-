import json,base64
from layout import set_text,F
from render import colored
g=[];h=[]
y=120
for t in ['а б в г ґ д е є ж з и і ї й к л м н о','п р с т у ф х ц ч ш щ ь ю я','a b c d e f g h i j k l m n o p q r s','t u v w x y z 0 1 2 3 4 5 6 7 8 9 10','швидко читається текст, рівні літери.']:
    set_text(t,40,40,1900,y,140,g,h); y+=140
o=['<html><body style="margin:0;background:#fff"><div style="position:relative;width:2000px;height:820px">']
for i in range(6): o.append(f'<div style="position:absolute;left:0;top:{120+140*i}px;width:2000px;height:1px;background:#f99"></div><div style="position:absolute;left:0;top:{80+140*i}px;width:2000px;height:1px;background:#9cf"></div>')
for q in g:
    f=F[q['g']]; u='data:image/svg+xml;base64,'+base64.b64encode(colored(q['g'],'#1E2A8C').replace('<svg ','<svg preserveAspectRatio="none" ',1).encode()).decode()
    o.append(f'<img src="{u}" style="position:absolute;left:{q["x"]}px;top:{q["y"]}px;width:{f["W"]*q["s"]*q.get("sx",1)}px;height:{f["H"]*q["s"]}px">')
o.append('</div></body></html>'); open('alpha.html','w').write(''.join(o))
