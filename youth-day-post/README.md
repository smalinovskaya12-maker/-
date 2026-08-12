# International Youth Day — Instagram carousel (Europe Prykhystok)

6-slide carousel post for August 12, 2026, built from the brand's Figma file
("БФ Прихисток | Європа").

## Brand tokens (extracted from Figma)

| Token | Value | Use |
|---|---|---|
| Navy | `#003399` | headlines, date badge, primary panels |
| Blue | `#5D77AA` | secondary text, eyebrows, outlines |
| Gray | `#BCBCBC` | neutral / mid-tone |
| Yellow | `#FECD00` | accent, CTA button, star |
| Background | `#F7F7F7` | light panel background |

**Headline font:** Futura Now Headline Bold (licensed, not redistributable) →
substituted here with **Poppins ExtraBold/Bold**, the closest freely-licensed
geometric sans, uppercase with tight tracking to match the brand's look.

**Body font:** Cambria → substituted with **PT Serif**, the closest
freely-licensed serif matching x-height and proportions.

**Logo:** the brand mark (concentric navy/blue/gray circle with a yellow
star) is the exact SVG pulled from the Figma file, used as-is
(`assets/logo.svg`).

## Structure

- `assets/` — logo SVG + embedded font files used by the generator
- `build/generate.py` — builds the 6 slide HTML files from brand tokens + copy
- `slides/*.html` — one file per slide (self-contained, fonts inlined as base64)
- `slides/*.png` — rendered 2400×2400 (2x of a 1200×1200 IG square) exports

## Photo placeholders

Every slide reserves a dashed, labelled "PHOTO" block in place of a real
photograph — swap in the real image (object-fit: cover) before publishing.
Slide 1 has a full-bleed placeholder behind the date badge and logo; slide 5
(CTA) uses a smaller inset placeholder card on the navy background.

## Regenerating

```
cd build && python3 generate.py          # rewrites slides/*.html
node <playwright-script> in a headless   # re-export slides/*.png
browser at viewport 1200x1200, deviceScaleFactor 2
```

## Slides

1. **Cover** — International Youth Day · Aug 12, 2026 headline + date badge
2. **Context** — where International Youth Day comes from (1991/1999 UN history)
3. **Reality** — what four years of war mean for Ukrainian children
4. **What we do** — Europe Prykhystok's respite stays
5. **Call to action** — partner form CTA, yellow button
6. **Credit** — "Made possible by the Robert Bosch Stiftung"
