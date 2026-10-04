s=open('guide.html').read()
mark=open('mark.svg').read()
s=s.replace('%%LOGO%%','').replace('%%MARK%%',mark)
import re as _re
_full=open('logo_full.svg').read()
_c=[0]
def _lf(m):
    _c[0]+=1
    return _full.replace('glyph-','g%d-'%_c[0])
s=_re.sub('%%LOGOFULL%%',_lf,s)
pillars=[('Edukim për prindërit',35,'“Fëmija 2 vjeç nuk bashkon dy fjalë”','#231F20'),
('Specialistët',25,'“Tantrumet çdo ditë: kur janë normale?”','#231F20'),
('Lidhja italiane',15,'“Pse Roma?” me CEO-n','#3A3A3A'),
('Vizita e parë',15,'“Vizita e parë, hap pas hapi”','#C4C4C4'),
('Dëshmi',10,'Prindër që tregojnë rrugëtimin, me pëlqim','#8C8C8C')]
s=s.replace('%%PILLARS%%',''.join(f'<div style="display:grid;grid-template-columns:62mm 1fr 16mm;gap:4mm;align-items:center"><div><p style="font-weight:700">{n}</p><p style="font-size:11.5pt;color:#666666">{ex}</p></div><div style="height:8mm;background:#F0F0F0;border-radius:2mm;overflow:hidden"><div style="height:100%;width:{p/35*100:.0f}%;background:{c};border-radius:2mm"></div></div><p class="disp" style="font-size:21pt;color:#231F20;text-align:right">{p}%</p></div>' for n,p,ex,c in pillars))
weeks=[('Java 1','Njih shenjat','#F5F5F5','#1A1A1A',['Reel · 2 vjeç dhe nuk bashkon dy fjalë','Reel · 3 gjëra me qëllim të mirë','Karusel · Fjalët e para, sipas moshës']),
('Java 2','Kush jemi','#231F20','#FFFFFF',['Reel · Pse Roma? (CEO)','Reel · “Djemtë flasin më vonë”: mit apo fakt','Karusel · Logoped, psikolog apo neuropediatër?']),
('Java 3','Pa frikë','#C4C4C4','#1A1A1A',['Reel · Vizita e parë, nga lartësia e fëmijës','Reel · 6 specialistë, 1 pyetje','Karusel · Vizita e parë, hap pas hapi']),
('Java 4','Hapi i parë','#3A3A3A','#FFFFFF',['Reel · Tantrumet: kur janë normale?','Reel · Një ditë me specialistët nga Roma','Karusel · 5 pyetje për çdo klinikë'])]
s=s.replace('%%WEEKS%%',''.join(f'<div style="background:{bg};color:{fg};border-radius:4mm;padding:6mm;min-height:70mm;{"border:1px solid #DADADA;" if bg=="#F5F5F5" else ""}"><p style="font-size:12pt;font-weight:700;opacity:.8">{w}</p><p class="disp" style="font-size:26pt;margin-top:1mm;{"color:#BDBDBD;" if fg!="#1A1A1A" else "color:#231F20;"}">{t}</p><div style="margin-top:5mm;display:flex;flex-direction:column;gap:3mm;font-size:12.5pt">'+''.join(f'<p>{x}</p>' for x in items)+'</div></div>' for w,t,bg,fg,items in weeks))
steps=[('1','Ide','Temat nga pyetjet reale të prindërve.'),('2','Skript','Shkruajmë çdo video dhe postim.'),('3','Miratim','Specialisti kontrollon çdo fakt mjekësor.'),('4','Filmim','Një ditë në muaj në klinikë.'),('5','Publikim','Dhe raport me numra çdo muaj.')]
s=s.replace('%%STEPS%%',''.join(f'<div style="border-top:3px solid {"#8C8C8C" if n=="4" else "#231F20"};padding-top:4mm"><p class="disp" style="font-size:32pt;color:#231F20">{n}</p><p style="font-weight:700;margin-top:1mm">{t}</p><p style="font-size:12pt;color:#666666;margin-top:1mm">{d}</p></div>' for n,t,d in steps))
needs=['Numri kryesor i WhatsApp-it për rezervime','Adresa e qendrës në Elbasan','Datat e ditëve me specialistët nga Roma','Leje me shkrim nga Don Orione dhe Bambino Gesù për emrin dhe logon','Emrat e testeve të vlerësimit','Historia juaj: pse u themelua klinika','2–3 specialistë në ditën e filmimit','Recepsioni të pyesë çdo pacient: “Si na gjetët?”']
s=s.replace('%%NEEDS%%',''.join(f'<p style="display:flex;gap:3mm"><span style="flex:none;width:5.5mm;height:5.5mm;border:1.5px solid #231F20;border-radius:1mm;margin-top:1mm"></span><span>{x}</span></p>' for x in needs))
rules=[('Asnjë fëmijë pa pëlqim me shkrim','nga prindi, për çdo video.'),('Asnjë fytyrë fëmije pranë një diagnoze','si autizëm, ADHD ose vonesë në të folur.'),('Asnjë premtim rezultati.','Flasim për procesin, jo për garanci.'),('Çdo fakt mjekësor kontrollohet','nga specialisti përpara publikimit.'),('Pyetjet personale kalojnë në privat.','Asnjë diagnozë në komente.')]
s=s.replace('%%RULES%%',''.join(f'<div style="display:grid;grid-template-columns:13mm 1fr;align-items:baseline;border-bottom:1px solid #DADADA;padding-bottom:4mm"><span class="disp" style="font-size:24pt;color:#8C8C8C">{i+1}</span><p><b>{a}</b> {b}</p></div>' for i,(a,b) in enumerate(rules)))
open('guide_built.html','w').write(s)
