import math, random
def oval_svg(w,h,sw,color,seed=0):
    random.seed(seed)
    cx,cy=w/2,h/2; rx=w/2-sw; ry=h/2-sw
    pts=[]; t0=math.radians(200); span=math.radians(380)  # overlap ends
    n=48
    for k in range(n+1):
        t=t0+span*k/n
        f=1+0.05*math.sin(3*t+seed)+random.uniform(-0.01,0.01)
        drift=(k/n)*0.12*ry  # spiral so ends don't meet exactly
        x=cx+rx*f*math.cos(t); y=cy+(ry-drift)*f*math.sin(t)-0.04*ry*math.cos(t)
        pts.append((x,y))
    d=f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(1,len(pts)-1):
        mx=(pts[i][0]+pts[i+1][0])/2; my=(pts[i][1]+pts[i+1][1])/2
        d+=f'Q{pts[i][0]:.1f} {pts[i][1]:.1f} {mx:.1f} {my:.1f}'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}"><path d="{d}" fill="none" stroke="{color}" stroke-width="{sw:.1f}" stroke-linecap="round"/></svg>'
