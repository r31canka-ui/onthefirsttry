import datetime as dt
D=dt.date
reel={D(2026,10,8),D(2026,10,13),D(2026,10,16),D(2026,10,20),D(2026,10,23),D(2026,10,27),D(2026,10,30),D(2026,11,3)}
car={D(2026,10,11),D(2026,10,18),D(2026,10,25),D(2026,11,1)}
start,end=D(2026,10,8),D(2026,11,7)
mon=['','Jan','Shk','Mar','Pri','Maj','Qer','Kor','Gus','Sht','Tet','Nën','Dhj']
wd=['E Hënë','E Martë','E Mërkurë','E Enjte','E Premte','E Shtunë','E Diel']
d=start-dt.timedelta(days=start.weekday())
last=end+dt.timedelta(days=6-end.weekday())
cells=[]
while d<=last:
    if d<start or d>end: cells.append('<div class="c off"></div>')
    else:
        if d in reel: lab='<span class="r">Reel</span>'
        elif d in car: lab='<span class="k">Karusel</span>'
        else: lab='<span class="s">Stories</span>'
        cells.append(f'<div class="c"><b>{d.day} {mon[d.month]}</b>{lab}</div>')
    d+=dt.timedelta(days=1)
mark=open('mark.svg').read()
html=f'''<!doctype html><html lang="sq"><head><meta charset="utf-8"><title>Plani i postimeve</title>
<link rel="stylesheet" href="../fonts/local.css">
<style>
@page{{size:A4 landscape;margin:14mm}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font-family:"Plus Jakarta Sans",sans-serif;color:#1A1A1A}}
.head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6mm}}
h1{{font-family:"Bodoni Moda",serif;font-weight:500;font-size:28pt}}
h1 i{{color:#8C8C8C}}
.head p{{font-size:11pt;color:#555;margin-top:1mm}}
.logo{{width:18mm;height:18mm;color:#231F20}} .logo svg{{width:100%;height:100%}}
.legend{{display:flex;gap:6mm;font-size:10.5pt;margin-bottom:4mm;align-items:center}}
.grid{{display:grid;grid-template-columns:repeat(7,1fr);border-top:1px solid #231F20;border-left:1px solid #231F20}}
.h{{background:#231F20;color:#fff;font-weight:700;font-size:10pt;padding:2mm 3mm;border-right:1px solid #231F20}}
.c{{height:24mm;border-right:1px solid #231F20;border-bottom:1px solid #231F20;padding:2.5mm 3mm;display:flex;flex-direction:column;justify-content:space-between}}
.c b{{font-size:12pt}}
.c.off{{background:#F2F2F2}}
.r,.k,.s{{display:inline-block;align-self:flex-start;font-size:10pt;font-weight:800;padding:1mm 3.5mm;border-radius:99px}}
.r{{background:#231F20;color:#fff}} .k{{border:1.5px solid #231F20}} .s{{color:#777;font-weight:600;padding-left:0}}
</style></head><body>
<div class="head"><div><h1>Plani i postimeve <i>8 Tetor – 7 Nëntor</i></h1><p>Umano Felice · @klinika_umano_felice · Rritje Sade</p></div><div class="logo">{mark}</div></div>
<div class="legend"><span class="r">Reel</span> 8 &nbsp;&nbsp; <span class="k">Karusel</span> 4 &nbsp;&nbsp; <span class="s">Stories</span> çdo ditë tjetër</div>
<div class="grid">{''.join(f'<div class="h">{x}</div>' for x in wd)}{''.join(cells)}</div>
</body></html>'''
open('cal.html','w').write(html)
