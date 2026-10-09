import datetime as dt
D=dt.date
days=['E Hënë','E Martë','E Mërkurë','E Enjte','E Premte','E Shtunë','E Diel']
mon=['Jan','Shk','Mar','Pri','Maj','Qer','Kor','Gus','Sht','Tet','Nën','Dhj']
feed={D(2026,10,8):('reel','Reel 1 · 20:30','✓ U postua'),D(2026,10,11):('car','Karusel 1 · 20:00',''),D(2026,10,13):('reel','Reel 2 · 20:30',''),D(2026,10,16):('reel','Reel 3 · 20:30',''),D(2026,10,18):('car','Karusel 2 · 20:00',''),D(2026,10,20):('reel','Reel 4 · 20:30',''),D(2026,10,23):('reel','Reel 5 · 20:30',''),D(2026,10,25):('car','Karusel 3 · 20:00',''),D(2026,10,27):('reel','Reel 6 · 20:30',''),D(2026,10,30):('reel','Reel 7 · 20:30',''),D(2026,11,1):('car','Karusel 4 · 20:00',''),D(2026,11,3):('reel','Reel 8 · 20:30','')}
work={D(2026,10,10):'Karuseli 1 gati',D(2026,10,15):'Karuseli 2 gati',D(2026,10,16):'Skriptet e 3 videove gati',D(2026,10,19):'Klinika miraton skriptet',D(2026,10,21):'Filmimi i 3 videove',D(2026,10,22):'Karuseli 3 gati · kontrolli i Insights',D(2026,10,24):'Editimi i 3 videove gati',D(2026,10,29):'Karuseli 4 gati',D(2026,11,4):'Filmimi i muajit tjetër',D(2026,11,7):'Raporti mujor'}
special={D(2026,10,10):'Dita Botërore e Shëndetit Mendor',D(2026,10,22):'Dita Ndërkombëtare e Belbëzimit'}
def stories(d):
    wd=d.weekday()
    if d in feed and feed[d][0]=='reel':
        return [('12:00','Teaser i Reel-it të sotëm'),('21:30','Ndarje e Reel-it + sondazh'),('09:00 (nesër)','—')][:2]
    if d in feed and feed[d][0]=='car':
        return [('12:00','Pyetje e lehtë / sondazh'),('21:00','Ndarje e karuselit + "Ruajeni"')]
    if d==D(2026,10,10): return [('10:00','Dita Botërore e Shëndetit Mendor: citat i psikologes'),('18:00','Rezervim + link WhatsApp')]
    if d==D(2026,10,22): return [('10:00','Dita e Belbëzimit: 2–3 Stories nga logopedi'),('19:00','Kuiz')]
    if d in (D(2026,10,21),D(2026,11,4)): return [('10:00','Prapaskenë live nga filmimi'),('19:00','"Çfarë po përgatisim" (pa zbuluar temat)')]
    if d==D(2026,11,6): return [('11:00','"Ky muaj te Umano Felice"'),('20:00','Rindarje e Reel-it më të mirë')]
    m={0:[('10:00','Kutia e pyetjeve'),('19:00','Teaser për Reel-in e nesërm')],
       1:[('10:00','Rikujtim i Reel-it të fundit'),('19:00','Prapaskenë')],
       2:[('10:00','Prapaskenë nga klinika'),('19:00','Përgjigje nga kutia (video 15 sek)')],
       3:[('10:00','Kuiz'),('19:00','Specialisti i javës')],
       4:[('10:00','Rikujtim i Reel-it të fundit'),('19:00','Përgjigje nga kutia')],
       5:[('11:00','Rezervim: oraret e javës + link WhatsApp'),('18:00','Vlerësime Google (me leje)')],
       6:[('11:00','Sondazh i lehtë'),('19:00','Rikujtim i karuselit të fundit')]}
    return m[wd]
def morning_after(d):
    prev=d-dt.timedelta(days=1)
    return prev in feed and feed[prev][0]=='reel'
rows=[]
d=D(2026,10,8)
week=0
while d<=D(2026,11,7):
    if d==D(2026,10,8) or d.weekday()==0:
        week+=1
        rows.append(f'<tr class="wk"><td colspan="4">Java {week}</td></tr>')
    f=feed.get(d)
    fhtml=f'<span class="tag {f[0]}">{"Reel" if f[0]=="reel" else "Karusel"}</span> {f[1].split(" · ")[0]} <span class="t">{f[1].split(" · ")[1]}</span>'+(f' <span class="done">✓</span>' if f[2] else '') if f else '<span class="none">—</span>'
    st=stories(d)
    if d==D(2026,10,8): st=[('21:30','Ndarje e Reel 1 + sondazh')]
    if morning_after(d) and d!=D(2026,10,9): st=[('09:00','Rikujtim i Reel-it të djeshëm')]+st
    if d==D(2026,10,9): st=[('09:00','Rikujtim i Reel 1'),('19:00','Prapaskenë nga klinika')]
    shtml=' · '.join(t.split(' ')[0] for t,x in st)
    extra='Filmim' if d in (D(2026,10,21),D(2026,11,4)) else ''
    cls=' class="hasfeed"' if f else ''
    rows.append(f'<tr{cls}><td class="date"><b>{d.day} {mon[d.month-1]}</b><span>{days[d.weekday()]}</span></td><td>{fhtml}</td><td class="st">{shtml}</td><td>{extra}</td></tr>')
    d+=dt.timedelta(days=1)
mark=open('mark.svg').read()
html=f'''<!doctype html><html lang="sq"><head><meta charset="utf-8"><title>Plani i postimeve</title>
<link rel="stylesheet" href="../fonts/local.css">
<style>
@page{{size:A4;margin:14mm 13mm 14mm}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font-family:"Plus Jakarta Sans",sans-serif;color:#1A1A1A;font-size:10pt;line-height:1.4}}
.head{{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #231F20;padding-bottom:5mm;margin-bottom:5mm}}
.head h1{{font-family:"Bodoni Moda",serif;font-weight:500;font-size:24pt;line-height:1.05;white-space:nowrap}}
.head h1 i{{color:#8C8C8C}}
.head p{{font-size:11pt;color:#555;margin-top:2mm}}
.logo{{width:18mm;height:18mm;color:#231F20}} .logo svg{{width:100%;height:100%}}
.sum{{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin-bottom:5mm}}
.sum div{{border:1px solid #231F20;border-radius:2.5mm;padding:3mm 4mm}}
.sum b{{font-family:"Bodoni Moda",serif;font-size:22pt;font-weight:500;display:block;line-height:1}}
.sum span{{font-size:9pt;color:#555}}
.sum div.dark{{background:#231F20;color:#fff}} .sum div.dark span{{color:#ccc}}
.legend{{font-size:9pt;color:#555;margin-bottom:4mm}}
table{{width:100%;border-collapse:collapse}}
thead th{{background:#231F20;color:#fff;font-size:9pt;text-align:left;padding:2mm 2.5mm;font-weight:700}}
td{{border-bottom:.5pt solid #D0D0D0;padding:1.5mm 2.5mm;vertical-align:middle}}
tr{{break-inside:avoid}}
tr.wk td{{background:#EDEDED;font-weight:800;font-size:9.5pt;letter-spacing:.04em;text-transform:uppercase;padding:1.6mm 2.5mm;border-bottom:0}}
tr.hasfeed td{{background:#FAFAFA}}
td.date{{width:28mm}} td.date b{{display:block;font-size:10.5pt;line-height:1.15}} td.date span{{display:block;font-size:8.5pt;color:#666;white-space:nowrap}}
td:nth-child(2){{width:62mm}} td:nth-child(4){{width:22mm;font-size:9pt;font-weight:700}} td.st{{font-variant-numeric:tabular-nums;font-size:9.5pt}}
.tag{{display:inline-block;font-size:7.5pt;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:.6mm 2mm;border-radius:99px;margin-right:1mm}}
.tag.reel{{background:#231F20;color:#fff}} .tag.car{{border:1px solid #231F20}}
.t{{color:#666;font-size:9pt}} .done{{font-size:8pt;color:#666}} .none{{color:#999;font-size:9pt}}
.s{{font-size:9pt}} .s b{{display:inline-block;min-width:13mm;font-variant-numeric:tabular-nums}}
.sp{{font-weight:700}} .wk2{{color:#444}}
h2{{font-family:"Bodoni Moda",serif;font-weight:500;font-size:20pt;margin:7mm 0 3mm;break-after:avoid}}
.rules{{display:grid;grid-template-columns:1fr 1fr;gap:3mm 6mm}}
.rules div{{border-top:1.5px solid #231F20;padding-top:2mm;break-inside:avoid}}
.rules b{{display:block;font-size:10.5pt}} .rules p{{font-size:9.5pt;color:#444}}
.foot{{margin-top:6mm;font-size:8.5pt;color:#777;border-top:.5pt solid #ccc;padding-top:2mm}}
</style></head><body>
<div class="head"><div><h1>Plani i postimeve <i>8 Tetor – 7 Nëntor</i></h1><p>Umano Felice · @klinika_umano_felice · Përgatitur nga Rritje Sade</p></div><div class="logo">{mark}</div></div>
<div class="sum"><div class="dark"><b>8</b><span>Reels · e martë dhe e premte, 20:30</span></div><div><b>4</b><span>Karusele · e diel, 20:00</span></div><div><b>31</b><span>ditë me Stories</span></div><div><b>2</b><span>ditë filmimi · 21 Tetor dhe 4 Nëntor</span></div></div>
<table><thead><tr><th>Data</th><th>Feed</th><th>Stories</th><th>Filmim</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</body></html>'''
open('plan.html','w').write(html)
