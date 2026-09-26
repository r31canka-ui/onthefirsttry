# -*- coding: utf-8 -*-
"""Gjeneron logon e Rritje Academy (SVG) + fletën e prezantimit (HTML)."""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

TEAL, LIME, OFF, BLACK, WHITE = "#02464F", "#D8FF2A", "#F5F5F0", "#111111", "#FFFFFF"
K = math.tan(math.radians(30))  # 0.577 — i njëjti kënd 60° si shenja e Rritje Sade


def r(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


# ---------------- simboli (rrjet 0..100 në lartësi)
STEM_TOP, APEX_X, BASE, W = 16, 56, 66, 24
a = APEX_X - STEM_TOP * K                 # ku fillon ngjitja
right = APEX_X + BASE * K                 # maja djathtas e kokës
C_TOP, C_BOT, INSET = 34, 48, 26          # hapësira e brendshme
cr_top = APEX_X - INSET + C_TOP * K
cr_bot = APEX_X - INSET + C_BOT * K
LEG_L, LEG_R = 40, 66
dx = (100 - BASE) * K
SYMBOL = (
    # një path i vetëm: stem + kokë trekëndore + këmbë 60°, me hapësirën e brendshme
    f'<path fill-rule="evenodd" d="M0 {STEM_TOP}H{r(a)}L{APEX_X} 0L{r(right)} {BASE}H{LEG_R}'
    f'L{r(LEG_R+dx)} 100H{r(LEG_L+dx)}L{LEG_L} {BASE}H{W}V100H0Z'
    f'M{W} {C_TOP}H{r(cr_top)}L{r(cr_bot)} {C_BOT}H{W}Z"/>'
)
SYM_W = LEG_R + dx if LEG_R + dx > right else right


# ---------------- wordmark si path (pa varësi nga fontet)
def text_path(font_file, text, height_cap, tracking_em):
    f = TTFont(font_file)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    upm = f["head"].unitsPerEm
    cap = f["OS/2"].sCapHeight
    s = height_cap / cap
    x, parts = 0, []
    for i, ch in enumerate(text):
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, height_cap)))
        parts.append(pen.getCommands())
        x += hmtx[g][0] * s
        if i < len(text) - 1:
            x += tracking_em * upm * s
    # gjerësia pa hapësirën anësore të shkronjës së fundit
    last = cmap[ord(text[-1])]
    lsb_last = hmtx[last][1] * s
    bounds_w = x - (hmtx[last][0] * s) + (gs[last].width * s) - 0
    return " ".join(parts), x


def wordmark(cap_main=40, gap=12, cap_sub=None):
    main_d, main_w = text_path("fonts/Manrope-800.ttf", "RRITJE", cap_main, 0.02)
    cap_sub = cap_sub or cap_main * 0.42
    # tracking i ACADEMY llogaritet që të ketë të njëjtën gjerësi me RRITJE
    _, w0 = text_path("fonts/Manrope-600.ttf", "ACADEMY", cap_sub, 0)
    f = TTFont("fonts/Manrope-600.ttf")
    s = cap_sub / f["OS/2"].sCapHeight
    track = (main_w - w0) / 6 / (f["head"].unitsPerEm * s)
    sub_d, sub_w = text_path("fonts/Manrope-600.ttf", "ACADEMY", cap_sub, track)
    return main_d, sub_d, main_w, cap_main, cap_sub, gap


def svg(inner, w, h, bg=None, pad=0):
    b = f'<rect x="{-pad}" y="{-pad}" width="{r(w+2*pad)}" height="{r(h+2*pad)}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {r(w+2*pad)} {r(h+2*pad)}" '
            f'width="{r((w+2*pad)*4)}" height="{r((h+2*pad)*4)}">{b}{inner}</svg>')


def full_logo(sym_color, main_color, sub_color):
    md, sd, mw, cm, cs, gap = wordmark()
    tx = SYM_W + 22                       # hapësira simbol–tekst
    ty = 100 - (cm + gap + cs)            # teksti ulet në bazën e simbolit
    inner = (f'<g fill="{sym_color}">{SYMBOL}</g>'
             f'<g transform="translate({r(tx)} {r(ty)})"><path fill="{main_color}" d="{md}"/>'
             f'<path fill="{sub_color}" transform="translate(0 {r(cm+gap)})" d="{sd}"/></g>')
    return inner, tx + mw, 100


def icon(color):
    return f'<g fill="{color}">{SYMBOL}</g>', SYM_W, 100


def app_icon(bg, fg):
    size = 160
    sc = 0.9
    ox = (size - SYM_W * sc) / 2
    oy = (size - 100 * sc) / 2
    inner = (f'<rect width="{size}" height="{size}" rx="34" fill="{bg}"/>'
             f'<g transform="translate({r(ox)} {r(oy)}) scale({sc})" fill="{fg}">{SYMBOL}</g>')
    return inner, size, size


FILES = {
    "rritje-academy-logo.svg": (full_logo(TEAL, TEAL, TEAL), None),
    "rritje-academy-logo-negativ.svg": (full_logo(LIME, OFF, OFF), TEAL),
    "rritje-academy-logo-zi.svg": (full_logo(BLACK, BLACK, BLACK), None),
    "rritje-academy-logo-bardhe.svg": (full_logo(WHITE, WHITE, WHITE), None),
    "rritje-academy-simboli.svg": (icon(TEAL), None),
    "rritje-academy-simboli-zi.svg": (icon(BLACK), None),
    "rritje-academy-simboli-bardhe.svg": (icon(WHITE), None),
    "rritje-academy-ikona-app.svg": (app_icon(TEAL, LIME), None),
}
import os
os.makedirs("svg", exist_ok=True)
for name, ((inner, w, h), bg) in FILES.items():
    pad = 0 if "app" in name else 0
    open(f"svg/{name}", "w").write(svg(inner, w, h, bg, pad=20 if bg else 0))
print("simboli:", r(SYM_W), "x 100 · këndi 60° · path-et:", SYMBOL[:80], "...")
