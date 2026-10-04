s=open('guide.html').read()
mark=open('mark.svg').read()
s=s.replace('%%LOGO%%','').replace('%%MARK%%',mark)
pillars=[('Edukim për prindërit',35,'“Fëmija 2 vjeç nuk bashkon dy fjalë”','#23463F'),
('Specialistët',25,'“Tantrumet çdo ditë: kur janë normale?”','#23463F'),
('Lidhja italiane',15,'“Pse Roma?” me CEO-n','#2B2420'),
('Vizita e parë',15,'“Vizita e parë, hap pas hapi”','#A9BFAE'),
('Dëshmi',10,'Prindër që tregojnë rrugëtimin, me pëlqim','#B8925A')]
s=s.replace('%%PILLARS%%',''.join(f'<div style="display:grid;grid-template-columns:62mm 1fr 16mm;gap:4mm;align-items:center"><div><p style="font-weight:700">{n}</p><p style="font-size:11.5pt;color:#5C6B66">{ex}</p></div><div style="height:8mm;background:#EEF1EE;border-radius:2mm;overflow:hidden"><div style="height:100%;width:{p/35*100:.0f}%;background:{c};border-radius:2mm"></div></div><p class="disp" style="font-size:21pt;color:#23463F;text-align:right">{p}%</p></div>' for n,p,ex,c in pillars))
weeks=[('Java 1','Njih shenjat','#F4F5F1','#1B2623',['Reel · 2 vjeç dhe nuk bashkon dy fjalë','Reel · 3 gjëra me qëllim të mirë','Karusel · Fjalët e para, sipas moshës']),
('Java 2','Kush jemi','#23463F','#fff',['Reel · Pse Roma? (CEO)','Reel · “Djemtë flasin më vonë”: mit apo fakt','Karusel · Logoped, psikolog apo neuropediatër?']),
('Java 3','Pa frikë','#A9BFAE','#1B2623',['Reel · Vizita e parë, nga lartësia e fëmijës','Reel · 6 specialistë, 1 pyetje (20 Nëntor)','Karusel · Vizita e parë, hap pas hapi']),
('Java 4','Hapi i parë','#2B2420','#F5F3EF',['Reel · Tantrumet: kur janë normale?','Reel · Një ditë me specialistët nga Roma','Karusel · 5 pyetje për çdo klinikë'])]
s=s.replace('%%WEEKS%%',''.join(f'<div style="background:{bg};color:{fg};border-radius:4mm;padding:6mm;min-height:70mm;{"border:1px solid #D5DCD7;" if bg=="#F4F5F1" else ""}"><p style="font-size:12pt;font-weight:700;opacity:.8">{w}</p><p class="disp" style="font-size:26pt;margin-top:1mm;{"color:#C9A46B;" if fg!="#1B2623" else "color:#23463F;"}">{t}</p><div style="margin-top:5mm;display:flex;flex-direction:column;gap:3mm;font-size:12.5pt">'+''.join(f'<p>{x}</p>' for x in items)+'</div></div>' for w,t,bg,fg,items in weeks))
steps=[('1','Ide','Temat nga pyetjet reale të prindërve.'),('2','Skript','Shkruajmë çdo video dhe postim.'),('3','Miratim','Specialisti kontrollon çdo fakt mjekësor.'),('4','Filmim','Një ditë në muaj në klinikë.'),('5','Publikim','Dhe raport me numra çdo muaj.')]
s=s.replace('%%STEPS%%',''.join(f'<div style="border-top:3px solid {"#B8925A" if n=="4" else "#23463F"};padding-top:4mm"><p class="disp" style="font-size:32pt;color:#23463F">{n}</p><p style="font-weight:700;margin-top:1mm">{t}</p><p style="font-size:12pt;color:#5C6B66;margin-top:1mm">{d}</p></div>' for n,t,d in steps))
needs=['Numri kryesor i WhatsApp-it për rezervime','Adresa e qendrës në Elbasan','Datat e ditëve me specialistët nga Roma','Leje me shkrim nga Don Orione dhe Bambino Gesù për emrin dhe logon','Emrat e testeve të vlerësimit','Historia juaj: pse u themelua klinika','2–3 specialistë në ditën e filmimit','Recepsioni të pyesë çdo pacient: “Si na gjetët?”']
s=s.replace('%%NEEDS%%',''.join(f'<p style="display:flex;gap:3mm"><span style="flex:none;width:5.5mm;height:5.5mm;border:1.5px solid #23463F;border-radius:1mm;margin-top:1mm"></span><span>{x}</span></p>' for x in needs))
rules=[('Asnjë fëmijë pa pëlqim me shkrim','nga prindi, për çdo video.'),('Asnjë fytyrë fëmije pranë një diagnoze','si autizëm, ADHD ose vonesë në të folur.'),('Asnjë premtim rezultati.','Flasim për procesin, jo për garanci.'),('Çdo fakt mjekësor kontrollohet','nga specialisti përpara publikimit.'),('Pyetjet personale kalojnë në privat.','Asnjë diagnozë në komente.')]
s=s.replace('%%RULES%%',''.join(f'<div style="display:grid;grid-template-columns:13mm 1fr;align-items:baseline;border-bottom:1px solid #D5DCD7;padding-bottom:4mm"><span class="disp" style="font-size:24pt;color:#B8925A">{i+1}</span><p><b>{a}</b> {b}</p></div>' for i,(a,b) in enumerate(rules)))
open('guide_built.html','w').write(s)
