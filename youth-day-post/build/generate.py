#!/usr/bin/env python3
"""
Generates the 6 HTML slides for the "International Youth Day" carousel post
for Europe Prykhystok, using the brand colors / fonts / logo extracted from
the Figma brand file.

Brand tokens (from Figma file o9IP4RnwuKGGg54hZ8C1TF):
  navy    #003399  - primary brand color (headlines, badges, panels)
  blue    #5D77AA  - secondary text / accents
  gray    #BCBCBC  - neutral / placeholder
  yellow  #FECD00  - accent (star, highlights)
  bg      #F7F7F7  - light background
  Headline font -> Futura Now Headline Bold (substituted with Poppins ExtraBold,
                   closest freely-licensed geometric sans)
  Body font     -> Cambria (substituted with PT Serif, closest freely-licensed
                   serif with a matching text color)
"""
import base64
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FONTS = os.path.join(ASSETS, "fonts")
SLIDES_DIR = os.path.join(ROOT, "slides")
os.makedirs(SLIDES_DIR, exist_ok=True)

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

POPPINS_600 = b64(os.path.join(FONTS, "Poppins-600.ttf"))
POPPINS_700 = b64(os.path.join(FONTS, "Poppins-700.ttf"))
POPPINS_800 = b64(os.path.join(FONTS, "Poppins-800.ttf"))
PTSERIF_400 = b64(os.path.join(FONTS, "PTSerif-400.ttf"))
PTSERIF_700 = b64(os.path.join(FONTS, "PTSerif-700.ttf"))

with open(os.path.join(ASSETS, "logo.svg")) as f:
    LOGO_SVG = f.read()

FONT_FACES = f"""
@font-face {{
  font-family: 'Brand Headline';
  font-weight: 600;
  src: url(data:font/ttf;base64,{POPPINS_600}) format('truetype');
}}
@font-face {{
  font-family: 'Brand Headline';
  font-weight: 700;
  src: url(data:font/ttf;base64,{POPPINS_700}) format('truetype');
}}
@font-face {{
  font-family: 'Brand Headline';
  font-weight: 800;
  src: url(data:font/ttf;base64,{POPPINS_800}) format('truetype');
}}
@font-face {{
  font-family: 'Brand Body';
  font-weight: 400;
  src: url(data:font/ttf;base64,{PTSERIF_400}) format('truetype');
}}
@font-face {{
  font-family: 'Brand Body';
  font-weight: 700;
  src: url(data:font/ttf;base64,{PTSERIF_700}) format('truetype');
}}
"""

BASE_CSS = """
:root{
  --navy:#003399;
  --blue:#5D77AA;
  --gray:#BCBCBC;
  --yellow:#FECD00;
  --bg:#F7F7F7;
  --ink:#1c2b4a;
}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1200px;height:1200px;}
body{
  font-family:'Brand Body',serif;
  background:var(--bg);
  position:relative;
  overflow:hidden;
}
.canvas{width:1200px;height:1200px;position:relative;background:var(--bg);}

/* ---- photo placeholder ---- */
.photo{
  position:absolute;
  background:
    repeating-linear-gradient(135deg, rgba(93,119,170,0.10) 0 18px, rgba(93,119,170,0.16) 18px 36px),
    linear-gradient(180deg,#E2E6EE 0%, #D2D8E4 100%);
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden;
}
.photo .frame{
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:18px;
  color:#8b98b3;
}
.photo .frame svg{width:84px;height:84px;opacity:0.75;}
.photo .frame span{
  font-family:'Brand Headline',sans-serif;
  font-weight:700;
  font-size:24px;
  letter-spacing:0.28em;
  text-transform:uppercase;
  color:#7c8ab0;
}
.photo::after{
  content:"";
  position:absolute;
  inset:18px;
  border:2px dashed rgba(93,119,170,0.45);
  border-radius:inherit;
  pointer-events:none;
}

/* ---- logo badge ---- */
.logo{display:block;}

/* ---- headline / body ---- */
.eyebrow{
  font-family:'Brand Headline',sans-serif;
  font-weight:700;
  font-size:22px;
  letter-spacing:0.22em;
  text-transform:uppercase;
}
.headline{
  font-family:'Brand Headline',sans-serif;
  font-weight:800;
  text-transform:uppercase;
  line-height:1.14;
  letter-spacing:-0.01em;
}
.body-copy{
  font-family:'Brand Body',serif;
  font-weight:400;
  line-height:1.5;
}
.footer{
  position:absolute;
  left:75px;right:75px;bottom:44px;
  display:flex;
  align-items:center;
  justify-content:space-between;
}
.footer .brandmark{
  display:flex;align-items:center;gap:14px;
  font-family:'Brand Headline',sans-serif;
  font-weight:700;
  font-size:19px;
  letter-spacing:0.14em;
  color:var(--navy);
  text-transform:uppercase;
}
.footer .brandmark img{width:40px;height:auto;display:block;}
.footer .page{
  font-family:'Brand Headline',sans-serif;
  font-weight:700;
  font-size:19px;
  letter-spacing:0.08em;
  color:var(--blue);
}
"""

def camera_icon():
    return """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 8.5C4 7.67157 4.67157 7 5.5 7H7.5L8.4 5.4C8.6 5 9.05 4.75 9.5 4.75H14.5C14.95 4.75 15.4 5 15.6 5.4L16.5 7H18.5C19.3284 7 20 7.67157 20 8.5V17.5C20 18.3284 19.3284 19 18.5 19H5.5C4.67157 19 4 18.3284 4 17.5V8.5Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
    <circle cx="12" cy="13" r="3.4" stroke="currentColor" stroke-width="1.6"/>
    </svg>"""

def logo_svg_sized(size=96, circle_bg=None):
    svg = LOGO_SVG.replace('width="119" height="127.429"', f'width="{size}" height="{size*127.429/119:.1f}"')
    return svg

def photo_block(top, height, radius="0 0 60px 60px", left=0, width=1200, label="PHOTO"):
    r = f"border-radius:{radius};"
    return f"""<div class="photo" style="top:{top}px;left:{left}px;width:{width}px;height:{height}px;{r}">
      <div class="frame">{camera_icon()}<span>{label}</span></div>
    </div>"""

def footer(page_label, on_dark=False, y=44):
    color = "#FFFFFF" if on_dark else None
    style_extra = f"color:{color};" if on_dark else ""
    logo_html = logo_svg_sized(34)
    brand_color = "#FFFFFF" if on_dark else "var(--navy)"
    page_color = "#FFFFFF" if on_dark else "var(--blue)"
    return f"""<div class="footer" style="bottom:{y}px;">
      <div class="brandmark" style="color:{brand_color};">
        <span style="display:inline-flex;width:34px;">{logo_svg_sized(34)}</span>
        EUROPE PRYKHYSTOK
      </div>
      <div class="page" style="color:{page_color};">{page_label}</div>
    </div>"""

def wrap(slide_id, body_html, extra_style=""):
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>
{FONT_FACES}
{BASE_CSS}
{extra_style}
</style></head>
<body>
<div class="canvas" id="{slide_id}">
{body_html}
</div>
</body></html>"""

TOTAL = 6

# ---------------------------------------------------------------- SLIDE 1
def slide1():
    photo = photo_block(0, 760, radius="0 0 60px 60px", label="PHOTO")
    date_badge = f"""
    <div style="position:absolute;top:60px;left:75px;width:190px;height:222px;background:var(--navy);border-radius:0 0 16px 16px;box-shadow:0 10px 24px rgba(0,20,60,0.28);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;">
      <div style="font-family:'Brand Headline',sans-serif;font-weight:800;font-size:100px;line-height:1;">12</div>
      <div style="font-family:'Brand Body',serif;font-weight:700;font-size:32px;margin-top:10px;letter-spacing:0.05em;">AUG</div>
    </div>"""
    logo_badge = f"""
    <div style="position:absolute;top:60px;right:75px;width:104px;height:111px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 24px rgba(0,20,60,0.22);">
      <span style="display:inline-flex;width:74px;">{logo_svg_sized(74)}</span>
    </div>"""
    bottom = f"""
    <div style="position:absolute;top:760px;left:0;width:1200px;height:440px;background:var(--bg);padding:52px 75px 0 75px;">
      <div class="eyebrow" style="color:var(--blue);">INTERNATIONAL YOUTH DAY &middot; AUGUST 12, 2026</div>
      <div class="headline" style="color:var(--navy);font-size:60px;margin-top:20px;max-width:1050px;">
        For Ukrainians, this day<br>lands differently
      </div>
    </div>"""
    body = photo + date_badge + logo_badge + bottom + footer("01/06")
    return wrap("slide-1", body)

# ---------------------------------------------------------------- SLIDE 2
def slide2(n, kicker, headline, paragraph, page_label):
    photo = photo_block(0, 660, radius="0 0 60px 60px")
    bottom = f"""
    <div style="position:absolute;top:660px;left:0;width:1200px;height:540px;background:var(--bg);padding:56px 75px 0 75px;">
      <div class="eyebrow" style="color:var(--blue);">{kicker}</div>
      <div class="headline" style="color:var(--navy);font-size:48px;margin-top:18px;max-width:1050px;">
        {headline}
      </div>
      <div class="body-copy" style="color:var(--ink);font-size:29px;margin-top:26px;max-width:1050px;">
        {paragraph}
      </div>
    </div>"""
    return wrap(f"slide-{n}", photo + bottom + footer(page_label))

# ---------------------------------------------------------------- SLIDE 5 (CTA)
def slide5():
    bg = """<div style="position:absolute;inset:0;background:var(--navy);"></div>"""
    photo = photo_block(90, 470, radius="28px", left=110, width=980, label="PHOTO")
    headline = """
    <div class="headline" style="position:absolute;top:610px;left:75px;width:1050px;color:var(--yellow);font-size:46px;">
      If your city is ready to give Ukrainian children that chance &mdash; we are ready to make it happen
    </div>"""
    cta = """
    <div style="position:absolute;top:900px;left:75px;width:1050px;">
      <div style="display:inline-flex;align-items:center;gap:16px;background:var(--yellow);color:var(--navy);
                  font-family:'Brand Headline',sans-serif;font-weight:800;font-size:26px;letter-spacing:0.02em;
                  padding:24px 36px;border-radius:14px;">
        FILL OUT THE PARTNERSHIP FORM
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="#003399" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <div class="body-copy" style="color:#C9D3E8;font-size:24px;margin-top:20px;">
        Link in the description
      </div>
    </div>"""
    return wrap("slide-5", bg + photo + headline + cta + footer("05/06", on_dark=True))

# ---------------------------------------------------------------- SLIDE 6 (credit)
def slide6():
    photo = photo_block(0, 640, radius="0 0 60px 60px", label="PHOTO")
    bottom = f"""
    <div style="position:absolute;top:640px;left:0;width:1200px;height:560px;background:var(--bg);
                display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 100px;">
      <span style="display:inline-flex;width:110px;margin-bottom:34px;">{logo_svg_sized(110)}</span>
      <div class="eyebrow" style="color:var(--blue);">MADE POSSIBLE BY</div>
      <div class="headline" style="color:var(--navy);font-size:52px;margin-top:16px;">
        The Robert Bosch Stiftung
      </div>
      <div class="body-copy" style="color:var(--ink);font-size:26px;margin-top:22px;max-width:820px;">
        Europe Prykhystok &mdash; respite stays for Ukrainian children across Europe.
      </div>
    </div>"""
    return wrap("slide-6", photo + bottom + footer("06/06"))

slides = {
    "01-cover": slide1(),
    "02-context": slide2(
        2,
        "WHERE THIS DAY COMES FROM",
        "Young people deserve a future worth building",
        "The idea for International Youth Day was first proposed in 1991 by young people gathered in Vienna for the World Youth Forum of the United Nations. In 1999, the UN General Assembly officially declared August 12 as International Youth Day.",
        "02/06",
    ),
    "03-problem": slide2(
        3,
        "THE REALITY IN UKRAINE",
        "For Ukrainian children, that space has been taken away",
        "For four years, Ukrainian children have been growing up under the weight of war. Air raid alerts during school lessons, nights spent in shelters, cities where the playgrounds they knew no longer exist. An entire generation navigating a reality that no child should ever have to face.",
        "03/06",
    ),
    "04-solution": slide2(
        4,
        "WHAT EUROPE PRYKHYSTOK DOES",
        "We cannot stop the war. But we can offer a few weeks of peace",
        "Europe Prykhystok organises respite stays for groups of Ukrainian children in cities across Europe &mdash; two weeks away from sirens, fear, and the daily weight of living in a country at war. Two weeks of simply being young, in a place where that is still possible.",
        "04/06",
    ),
    "05-cta": slide5(),
    "06-credit": slide6(),
}

for name, html in slides.items():
    path = os.path.join(SLIDES_DIR, f"{name}.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)
