# -*- coding: utf-8 -*-
"""Gjeneron rritje-academy.html (A4, faqe fikse). PDF-ja krijohet me render.js."""
import datetime as dt
import re
import pathlib

ROOT = pathlib.Path(__file__).parent

# ---------------------------------------------------------------- ikonat
def icon(name, size=18):
    p = {
        "video": '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3z"/>',
        "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><circle cx="17.5" cy="9" r="2.5"/><path d="M17 14c2.8 0 4.5 2 4.5 5"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
        "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
        "doc": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
        "check": '<path d="M4 12.5l5 5L20 6.5"/>',
        "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
        "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/>',
        "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
        "phone": '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
        "shield": '<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.2-7.5 9.5-4.3-1.3-7.5-4.9-7.5-9.5V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
        "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
        "chart": '<path d="M4 20V4M4 20h16"/><rect x="7.5" y="12" width="3" height="5"/><rect x="12.5" y="8" width="3" height="9"/><rect x="17.5" y="5" width="2.5" height="12"/>',
        "alert": '<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5M12 17.2v.3"/>',
        "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
        "bolt": '<path d="M13 2.5L5 13.5h6l-1 8 8-11h-6z"/>',
        "gift": '<rect x="3.5" y="8.5" width="17" height="4"/><path d="M5 12.5v8h14v-8M12 8.5v12M12 8.5c-1-3-5-4.5-5.5-2S10 8.5 12 8.5c2 0 5.5-.5 5.5-2.5S13 5.5 12 8.5z"/>',
        "cut": '<circle cx="6" cy="7" r="2.5"/><circle cx="6" cy="17" r="2.5"/><path d="M8 8.5L20 17M8 15.5L20 7"/>',
        "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
        "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="9.5" y="9.5" width="5" height="5"/><path d="M9 2.5V6M15 2.5V6M9 18v3.5M15 18v3.5M2.5 9H6M2.5 15H6M18 9h3.5M18 15h3.5"/>',
        "code": '<path d="M8.5 7L3.5 12l5 5M15.5 7l5 5-5 5M13.5 4.5l-3 15"/>',
        "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
        "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/>',
        "arrow": '<path d="M4 12h15M13.5 6.5L19 12l-5.5 5.5"/>',
        "money": '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M6 9.5v5M18 9.5v5"/>',
        "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    }[name]
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{p}</svg>')


LOGO_PATHS = ('<path d="M213 0L319 181H208L153 276H52Z"/><path d="M50 94H133L82 181H0Z"/>')


def logo(h, color="#D8FF2A"):
    w = round(h * 319 / 276, 1)
    return f'<svg class="logo" width="{w}" height="{h}" viewBox="0 0 319 276" fill="{color}">{LOGO_PATHS}</svg>'


HYP = '<span class="hyp">Hipotezë – për t’u testuar</span>'

# ---------------------------------------------------------------- modulet
MODULES = [
    dict(n=0, week="Java 1", title="Mirëseardhja: si ta nxjerrësh maksimumin nga akademia",
         goal="Studenti e di rrugën 6-javore, ka vendosur objektivin e vet me numra dhe është aktiv në komunitet që në ditën e parë.",
         videos=[("Kush jam, çfarë kam ndërtuar dhe pse e hapa këtë akademi", 6),
                 ("Si funksionon programi: videot, live-t, detyrat, feedback-u", 7),
                 ("Objektivi yt 6-javor: si ta vendosësh dhe si ta masësh", 8)],
         task="Plotëso “Kartën e objektivit” dhe posto në grup screenshot-in e profilit tënd sot (“Dita 0”).",
         res="Karta e objektivit 6-javor + kalendari personal i studimit (PDF)"),
    dict(n=1, week="Java 1", title="Themelet: tregu, audienca, pozicionimi",
         goal="Ke një pozicionim të qartë në një fjali dhe e di saktësisht kujt i flet.",
         videos=[("Tregu online në Shqipëri: çfarë shitet dhe çfarë jo", 10),
                 ("Zgjedhja e nishës: fitimi × interesi × aftësia", 9),
                 ("Avatari i klientit: nga “të gjithë” te një person i vetëm", 10),
                 ("Kërkimi i audiencës: komentet, DM-të dhe konkurrentët", 11),
                 ("Pozicionimi: pse ty dhe jo dikë tjetër", 9),
                 ("Fjalia e pozicionimit dhe testi me 10 njerëz", 7)],
         task="Shkruaj fjalinë e pozicionimit dhe testoje në bisedë ose DM me 10 njerëz nga audienca jote.",
         res="Template “Avatari i klientit” + skripti i 10 bisedave kërkimore"),
    dict(n=2, week="Java 2", title="Branding personal & i biznesit",
         goal="Profili yt i thotë një vizitori të ri brenda 3 sekondave çfarë bën, për kë dhe pse duhet të të ndjekë.",
         videos=[("Brandi është perceptim: çfarë mbajnë mend njerëzit për ty", 8),
                 ("Brand personal apo brand biznesi: kur përdoret secili", 8),
                 ("Identiteti vizual me buxhet zero: ngjyrat, fontet, stili", 10),
                 ("Toni i zërit: si flet brandi yt në shqip", 8),
                 ("Profili që konverton: bio, foto, highlights, link në bio", 11),
                 ("Storytelling: historia jote e origjinës në 60 sekonda", 9)],
         task="Rregullo profilin (screenshot para/pas) dhe publiko historinë tënde të origjinës si reel.",
         res="Checklist “Profili që konverton” (20 pika) + template Brand Sheet"),
    dict(n=3, week="Java 3", title="Content creation: ide, hooks, skript, filmim me telefon, editim",
         goal="Publikon 3 reels në javë me një proces që nuk zgjat më shumë se 4 orë në total.",
         videos=[("Sistemi i ideve: si të mos mbetesh kurrë pa ide", 9),
                 ("4 shtyllat e content-it: vlerë, histori, provë, ofertë", 8),
                 ("Hooks: 3 sekondat e para që vendosin gjithçka", 12),
                 ("Strukturat e skriptit që mbajnë vëmendjen deri në fund", 11),
                 ("Filmimi me telefon: kamera, drita, zëri", 10),
                 ("Të folurit para kamerës pa u ngrirë", 9),
                 ("Editimi në CapCut: prerjet, ritmi, titrat", 12),
                 ("Carousels dhe postime që ruhen e shpërndahen", 8),
                 ("Stories: content-i që ndërton besim çdo ditë", 7),
                 ("Batching: 7 video në një ditë filmimi", 10)],
         task="Publiko 3 reels + 1 carousel këtë javë. Ngarko 10 hooks në grup për feedback para filmimit.",
         res="Swipe file me 100 hooks në shqip + template skripti + kalendari i content-it"),
    dict(n=4, week="Java 4", title="Rritje organike: platformat, seritë, sistemi i konsistencës",
         goal="Ke një sistem publikimi javor dhe e di cilët 5 numra të lexosh çdo të hënë.",
         videos=[("Si funksionojnë algoritmet e Instagram-it dhe TikTok-ut", 11),
                 ("Metrikat që kanë rëndësi: retention, shares, saves", 10),
                 ("Seritë: formati që e kthen shikuesin në ndjekës", 9),
                 ("Riciklimi: 1 ide, 5 formate, 3 platforma", 8),
                 ("Collabs: rritja bashkë me llogari të tjera", 8),
                 ("Sistemi i konsistencës: kalendari 30-ditor", 9),
                 ("Analiza javore në 20 minuta", 7)],
         task="Nis një seri me 5 episode dhe plotëso analizën e parë javore në dashboard.",
         res="Dashboard i metrikave (Google Sheets) + kalendari 30-ditor"),
    dict(n=5, week="Java 5", title="Audienca që blen: besimi, lead magnets, DM, email",
         goal="Ke një lead magnet live dhe mbledh kontakte (email/WhatsApp) çdo javë.",
         videos=[("Psikologjia e blerjes: pse njerëzit blejnë, dhe pse jo", 11),
                 ("Besimi: provat, rezultatet dhe transparenca", 9),
                 ("Nga shikuesi te blerësi: rruga e plotë", 8),
                 ("Lead magnet: si ta ndërtosh në një ditë", 10),
                 ("CTA që funksionojnë në reels dhe stories", 7),
                 ("DM: biseda që kthehen në shitje pa qenë i bezdisshëm", 11),
                 ("Email dhe WhatsApp: lista që të përket ty", 10)],
         task="Publiko lead magnet-in tënd dhe mblidh 25 kontaktet e para.",
         res="Template lead magnet (Canva) + 10 skripte DM + sekuenca email 5-ditore"),
    dict(n=6, week="Java 6", title="Shitja online: oferta, çmimi, faqja, reklamat Meta, mbyllja në DM",
         goal="Oferta jote e parë është live dhe ke bërë të paktën 10 biseda shitëse.",
         videos=[("Oferta: si ta ndërtosh që “jo”-ja të duket gabim", 12),
                 ("Çmimi në tregun shqiptar: si ta vendosësh pa frikë", 10),
                 ("Faqja e shitjes: struktura dhe copy", 11),
                 ("Pagesat në Shqipëri: bankë, POK, kartë, cash", 8),
                 ("Reklamat Meta 1: bazat dhe buxheti i parë (5 €/ditë)", 12),
                 ("Reklamat Meta 2: testimi dhe leximi i rezultateve", 10),
                 ("Mbyllja në DM: nga “sa kushton?” te pagesa", 11),
                 ("Kundërshtimet: “e shtrenjtë”, “do e mendoj”, “s’kam kohë”", 9)],
         task="Publiko ofertën dhe faqen e shitjes, bëj 10 biseda shitëse dhe raporto rezultatet me numra.",
         res="Template faqeje shitjeje + skripti i mbylljes në DM + tabela e kundërshtimeve"),
    dict(n=7, week="Java 4", title="AI për marketing & content (bazat)",
         goal="Përdor AI për të ulur kohën e prodhimit, pa humbur zërin tënd.",
         videos=[("AI si asistent: ku ndihmon dhe ku dëmton", 8),
                 ("Prompt-e për ide, hooks dhe skripte në shqip", 11),
                 ("AI për editim, titra dhe vizuale", 10),
                 ("Workflow-i im me AI: nga ideja te postimi", 9)],
         task="Ndërto bibliotekën tënde me 10 prompt-e dhe prodho 1 video të plotë me workflow-in AI.",
         res="Biblioteka me 30 prompt-e në shqip"),
    dict(n=8, week="Java 6", title="Projekti final & hapat e ardhshëm",
         goal="Mbyll programin me një case study me numra dhe një plan 90-ditor.",
         videos=[("Projekti final: si ta prezantosh rezultatin tënd", 7),
                 ("Plani 90-ditor pas akademisë", 9)],
         task="Prezanto projektin final (5 min) në workshopin e fundit: para/pas, numrat, çfarë mësove.",
         res="Template case study + template i planit 90-ditor"),
]

N_VIDEOS = sum(len(m["videos"]) for m in MODULES)
N_MIN = sum(v[1] for m in MODULES for v in m["videos"])
AVG_MIN = N_MIN / N_VIDEOS
assert N_VIDEOS == 53, N_VIDEOS


def fmt_hours(minutes):
    return f"{minutes // 60} orë e {minutes % 60} min"


def num(x):
    return f"{x:,}".replace(",", ".")


# ---------------------------------------------------------------- faqet
pages = []


def page(body, cls="", footer=True):
    pages.append((body, cls, footer))


def sec(n, title, kicker=""):
    k = f'<div class="kicker">{kicker}</div>' if kicker else ""
    return (f'<header class="sec">{k}<div class="sec-row"><span class="secnum">{n:02d}</span>'
            f'<h1>{title}</h1></div></header>')


def sub(title):
    return f'<h2 class="sub">{title}</h2>'


# ---------- 01 Kopertina
page(f'''
<div class="cover">
  <div class="cover-top">
    <span class="tag-dark">Dokument i brendshëm strategjik</span>
    <span class="cover-date">Shtator 2026 · v1.0</span>
  </div>
  <div class="cover-mid">
    {logo(150)}
    <div class="cover-title">Rritje Academy</div>
    <div class="cover-by">— nga Rritje Sade</div>
    <p class="cover-promise">Nga content pa drejtim te një audiencë që blen — në 6 javë.</p>
  </div>
  <div class="cover-grid">
    <div><b>{N_VIDEOS}</b><span>video mësimi</span></div>
    <div><b>6</b><span>javë kohortë hibride</span></div>
    <div><b>6</b><span>workshope live në Tiranë</span></div>
    <div><b>14 jan 2027</b><span>lançimi zyrtar</span></div>
  </div>
  <div class="cover-foot">
    <span>Plani i kursit, çmimeve dhe lançimit · Themelues & mësues kryesor: Rei Canka</span>
    <span>Konfidencial — mos e shpërndaj jashtë ekipit</span>
  </div>
  <div class="cover-shard s1"></div><div class="cover-shard s2"></div>
</div>''', cls="dark", footer=False)

# ---------- Përmbajtja
toc = [(2, "Vizioni & pozicionimi", 3), (3, "Për kë është (dhe për kë NUK është)", 4),
       (4, "Transformimi: sot dhe pas 6 javësh", 6), (5, "Programi kryesor: kurset dhe videot", 7),
       (6, "Modeli hibrid: si duket një javë", 14), (7, "Paketat & çmimet", 15),
       (8, "Plani i marketingut & lançimit", 17), (9, "Numrat: objektivat & metrikat", 20),
       (10, "Prodhimi i videove", 21), (11, "Roadmap i akademisë", 23),
       (12, "Rreziqet & si i shmangim", 24), (13, "Plani në 1 faqe", 25)]
toc_html = "".join(
    f'<li><span class="toc-n">{n:02d}</span><span class="toc-t">{t.replace("→", "&rarr;")}</span><span class="toc-p">{{{{P{n:02d}}}}}</span></li>'
    for n, t, p in toc)
page(f'''
<div class="kicker">Përmbajtja</div>
<h1 class="big">Një dokument, një vendim për çdo faqe.</h1>
<p class="lead">Ky dokument është plani operativ i Rritje Academy për 6 muajt e ardhshëm: çfarë mësojmë, kujt, me çfarë çmimi dhe si e lançojmë duke nisur nga lista e pritjes që po ndërtojmë me dokumentin falas prej 60 faqesh.</p>
<ol class="toc">{toc_html}</ol>
<div class="grid2 mt">
  <div class="card soft">
    <div class="card-h">{icon("flag")}Si ta lexosh</div>
    <p>Çdo numër që s’është fakt i verifikuar është shënuar me {HYP}. Këto janë vendimet e para që testojmë me listën e pritjes dhe kohortën beta.</p>
  </div>
  <div class="card soft">
    <div class="card-h">{icon("money")}Monedha</div>
    <p>Çmimet jepen në EUR dhe lekë. Për thjeshtësi përdorim kursin e rrumbullakosur <b>1 € ≈ 100 lekë</b>; çmimet në lekë rrumbullakosen në numra “psikologjikë” (p.sh. 24.900 lekë).</p>
  </div>
</div>
''')

# ---------- 02 Vizioni
page(f'''
{sec(2, "Vizioni & pozicionimi", "Pse ekzistojmë")}
<div class="promise">
  <div class="promise-l">Premtimi</div>
  <p>Në 6 javë kalon nga postime pa drejtim te një sistem që të sjell çdo javë audiencë të re dhe shitjet e tua të para online — i mësuar në shqip, për tregun shqiptar, nga njerëz që e bëjnë këtë çdo ditë.</p>
</div>
<p class="note">Premtimi flet për <b>transformimin</b> (sistem + shitje), jo për temat (reels, branding, ads). Temat janë mjeti; askush nuk paguan për “një modul hooks”.</p>

{sub("Pse Rritje Academy dhe jo YouTube falas apo kurse të tjera shqiptare")}
<div class="grid3">
  <div class="card diff">
    <div class="diff-n">1</div>
    <h3>Eksperiencë reale agjencie</h3>
    <p>100M+ views në llogaritë personale dhe të klientëve të Rritje Sade. Çdo modul ndërtohet mbi case studies reale, me numra — jo teori të përkthyer nga anglishtja.</p>
    <div class="proof">Provë: 1 case study klienti për modul</div>
  </div>
  <div class="card diff">
    <div class="diff-n">2</div>
    <h3>Specifikat e tregut shqiptar</h3>
    <p>Audiencë e vogël, pagesa me bankë/POK/cash, çmime për fuqinë blerëse vendase, content në shqip. Një kurs amerikan nuk të mëson si të mbyllësh një shitje në DM në Tiranë.</p>
    <div class="proof">Provë: shembuj vetëm nga llogari shqiptare</div>
  </div>
  <div class="card diff">
    <div class="diff-n">3</div>
    <h3>Hibrid + komunitet në Tiranë</h3>
    <p>Video të shkurtra + 6 workshope live + feedback mbi detyrat. YouTube nuk ta kontrollon detyrën dhe nuk të vendos në një dhomë me 25 njerëz që ndërtojnë njësoj si ti.</p>
    <div class="proof">Provë: max 25 vende live për kohortë</div>
  </div>
</div>

<table class="tbl mt">
  <thead><tr><th></th><th>YouTube falas</th><th>Kurse të tjera shqiptare</th><th class="hl">Rritje Academy</th></tr></thead>
  <tbody>
    <tr><td>Kush mëson</td><td>Kreatorë të huaj, tregje të tjera</td><td>Shpesh teorikë ose trajnerë pa rezultate publike</td><td class="hl">Rei Canka + ekipi i Rritje Sade, rezultate publike</td></tr>
    <tr><td>Struktura</td><td>Video të shpërndara, pa rend</td><td>Leksione të gjata, ritëm fiks</td><td class="hl">9 module, {N_VIDEOS} video 5–12 min, detyrë çdo javë</td></tr>
    <tr><td>Feedback</td><td>Asnjë</td><td>I kufizuar</td><td class="hl">Feedback mbi detyrat + hot-seat live</td></tr>
    <tr><td>Rezultati</td><td>Njohuri</td><td>Certifikatë</td><td class="hl">Ofertë live, sistem content-i, shitjet e para</td></tr>
  </tbody>
</table>
<div class="decision">{icon("check")}<div><b>Vendim:</b> në çdo komunikim shesim rezultatin dhe provën, jo numrin e videove. Numri i videove është argument i dobët — YouTube ka më shumë.</div></div>
''')

# ---------- 03 Avatarët
AVATARS = [
    ("A", "Kreatori i ri / freelancer", "Klea, 20 vjeç, studente në Tiranë",
     "Poston herë pas here, ka 1.200 ndjekës. Bën “social media” për 2 biznese të të afërmve për 100 € në muaj.",
     "Punon shumë, rritet pak dhe nuk di si ta kthejë aftësinë në të ardhura të qëndrueshme.",
     "Nishë e qartë, 3–5 mijë ndjekës dhe 2 klientë që paguajnë 200–300 € në muaj secili.",
     "“S’kam para, dhe mund ta mësoj falas në YouTube.”",
     "Paketa Digital + pagesë me këste. Një klient i vetëm e shlyen kursin në muajin e parë.",
     "TikTok, IG reels", "Digital / Hybrid me këste", "≈ 45%"),
    ("B", "Pronari i biznesit të vogël", "Artan, 42 vjeç, dyqan mobiliesh në Durrës",
     "Faqja në Instagram ka postime të rralla. Klientët vijnë nga fjala e gojës. Ka paguar një agjenci, pa rezultat të matshëm.",
     "Nuk ka kohë, nuk i beson më marketingut dhe s’di çfarë të kërkojë nga stafi.",
     "Një sistem 3 postime/javë që e bën vetë ose me një punonjës, dhe kërkesa të rregullta nga DM çdo javë.",
     "“S’kam kohë dhe s’jam i mirë para kamerës.”",
     "90 min video në javë, batching, dhe stafi mund të filmojë. Paketa Hybrid ose VIP për auditim.",
     "Instagram, rekomandime", "Hybrid / VIP", "≈ 30%"),
    ("C", "Marketeri aspirues / social media manager", "Endi, 24 vjeç, punon në marketing me pagë fillestare",
     "Di bazat teorike, por s’ka portofol me rezultate. Aplikon për punë dhe klientë pa prova.",
     "Paguhet pak sepse s’ka asnjë case study me numra për të treguar.",
     "Portofol me 1 case study reale dhe ofertë si SMM 300–500 € në muaj për klient.",
     "“A më jep certifikatë? A vlen për CV-në?”",
     "Case study > certifikatë. Certifikata jepet vetëm për projektin final, jo për shikimin e videove.",
     "Instagram, LinkedIn", "Hybrid", "≈ 25%"),
]
av_html = ""
for key, role, who, sit, pain, res, obj, ans, ch, pk, w in AVATARS:
    av_html += f'''
<div class="avatar">
  <div class="av-head"><span class="av-k">{key}</span><div><h3>{role}</h3><div class="av-who">{who}</div></div></div>
  <div class="av-strip"><div><span>Kanali</span>{ch}</div><div><span>Paketa</span>{pk}</div><div><span>Pesha</span>{w}</div></div>
  <dl>
    <dt>Situata</dt><dd>{sit}</dd>
    <dt>Dhimbja</dt><dd>{pain}</dd>
    <dt>Rezultati i dëshiruar</dt><dd>{res}</dd>
    <dt>Kundërshtimi kryesor</dt><dd class="obj">{obj}</dd>
    <dt>Përgjigjja jonë</dt><dd>{ans}</dd>
  </dl>
</div>'''
page(f'''
{sec(3, "Për kë është (dhe për kë NUK është)", "Avatarët")}
<p class="lead">Tre profile blerësish. Çdo reel, email dhe faqe shitjeje duhet t’i flasë njërit prej tyre — kurrë “të gjithëve”.</p>
<div class="avatars">{av_html}</div>
<p class="small">{HYP} Pesha e avatarëve në kohortë verifikohet me pyetjen “Cili të përshkruan më mirë?” në formularin e listës së pritjes.</p>
<h2 class="sub">Për kë NUK është kjo akademi</h2>
<div class="grid2 tight">
  <ul class="xlist">
    <li><b>Kërkon para të shpejta pa punë.</b> Programi kërkon 5–7 orë në javë për 6 javë.</li>
    <li><b>Nuk je gati të publikosh.</b> Pa postuar publikisht, asnjë modul nuk funksionon.</li>
    <li><b>Do vetëm certifikatë për CV.</b> Certifikatën e japim vetëm për rezultat.</li>
  </ul>
  <ul class="xlist">
    <li><b>Kërkon kurs të avancuar reklamash.</b> Meta Ads këtu janë baza (2 video).</li>
    <li><b>Ke biznes me 50+ punonjës dhe ekip marketingu.</b> Të duhet konsulencë, jo kurs.</li>
    <li><b>Pret që dikush tjetër ta bëjë për ty.</b> Kjo është akademi, jo “done-for-you”.</li>
  </ul>
</div>
<div class="decision sm">{icon("check")}<div><b>Vendim:</b> lista “NUK është për ty” vendoset në faqen e shitjes dhe lexohet në workshop. Ul rimbursimet dhe rrit besimin te blerësit e duhur.</div></div>
''')

# ---------- 04 Transformimi
TRANS = [
    ("Content", "0–1 postime në javë, pa plan", "3 reels + 1 carousel në javë; 18+ pjesë content të publikuara"),
    ("Profili", "Bio e paqartë, pa link që mbledh kontakte", "Profil që kalon checklist-ën 20/20 dhe link që mbledh kontakte"),
    ("Rritja", "Poston dhe shpreson", "1 seri me 5 episode + analizë javore e 5 metrikave"),
    ("Lista", "0 kontakte në pronësi", "Lead magnet live + 50 kontaktet e para (email/WhatsApp)"),
    ("Oferta", "S’ka ofertë ose çmim të qartë", "1 ofertë me çmim dhe faqe shitjeje live"),
    ("Shitja", "0 shitje online", "10 biseda shitëse; objektivi: 1–3 shitjet/klientët e parë"),
    ("AI", "Përdor ChatGPT rastësisht", "Bibliotekë me 10 prompt-e + workflow që shkurton prodhimin"),
    ("Prova", "Asgjë për të treguar", "1 case study me numra para/pas"),
]
rows = "".join(f'<tr><td><b>{a}</b></td><td class="before">{b}</td><td class="arr">{icon("arrow",16)}</td><td class="after">{c}</td></tr>' for a, b, c in TRANS)
page(f'''
{sec(4, "Transformimi — ku je sot, ku do jesh pas 6 javësh", "Rezultati")}
<p class="lead">Çdo rresht më poshtë është i matshëm. Në ditën 0 studenti plotëson kolonën “Sot”; në javën 6 prezanton kolonën “Pas 6 javësh” në workshopin final.</p>
<table class="tbl trans">
  <thead><tr><th>Fusha</th><th>Sot</th><th></th><th class="hl">Pas 6 javësh</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<div class="grid3 mt">
  <div class="stat"><b>18+</b><span>pjesë content të publikuara nga çdo student që përfundon</span></div>
  <div class="stat"><b>50</b><span>kontakte në listën e studentit në javën 6 {HYP}</span></div>
  <div class="stat"><b>60%</b><span>e studentëve Hybrid dorëzojnë projektin final {HYP}</span></div>
</div>
<div class="decision">{icon("shield")}<div><b>Vendim ligjor/etik:</b> premtojmë <b>output</b> (content i publikuar, ofertë live, biseda shitëse), jo të ardhura të garantuara. “Shitjet e para” janë objektiv, jo garanci — kështu thuhet edhe në faqen e shitjes.</div></div>
''')

# ---------- 05 Programi – përmbledhje
mod_rows = "".join(
    f'<tr><td class="c"><span class="mnum">{m["n"]}</span></td><td>{m["title"]}</td><td>{m["week"]}</td>'
    f'<td class="c">{len(m["videos"])}</td><td class="c">{sum(v[1] for v in m["videos"])} min</td></tr>'
    for m in MODULES)
page(f'''
{sec(5, "Programi kryesor: struktura e kurseve dhe videove", "Flagship · kohortë 6-javore")}
<div class="grid4">
  <div class="stat dark"><b>{len(MODULES)}</b><span>module</span></div>
  <div class="stat dark"><b>{N_VIDEOS}</b><span>video</span></div>
  <div class="stat dark"><b>{fmt_hours(N_MIN).replace(" e ", "<br>")}</b><span>content total</span></div>
  <div class="stat dark"><b>{str(round(AVG_MIN,1)).replace(".", ",")} min</b><span>gjatësia mesatare</span></div>
</div>
<table class="tbl mt">
  <thead><tr><th class="c">Mod.</th><th>Tema</th><th>Java</th><th class="c">Video</th><th class="c">Kohëzgjatja</th></tr></thead>
  <tbody>{mod_rows}
  <tr class="total"><td></td><td>Totali</td><td>6 javë</td><td class="c">{N_VIDEOS}</td><td class="c">{N_MIN} min</td></tr></tbody>
</table>
<div class="grid2 mt">
  <div class="card soft">
    <div class="card-h">{icon("clock")}Pse video 5–12 minuta</div>
    <ul class="dots">
      <li><b>1 video = 1 ide = 1 veprim.</b> Studenti mbaron diçka në çdo seancë, dhe kjo e mban në kurs.</li>
      <li><b>Shikohet në telefon</b>, në autobus ose në pushim — aty ku audienca jonë konsumon content.</li>
      <li><b>Përditësohet lehtë.</b> Kur ndryshon algoritmi, rixhirojmë 1 video, jo 1 orë.</li>
      <li><b>Asnjë video mbi 12 min.</b> Nëse një temë kërkon më shumë, ndahet në dy.</li>
    </ul>
  </div>
  <div class="card soft">
    <div class="card-h">{icon("calendar")}Harta javore</div>
    <table class="mini">
      <tr><td>J1</td><td>Modulet 0 + 1 · Themelet</td></tr>
      <tr><td>J2</td><td>Moduli 2 · Branding</td></tr>
      <tr><td>J3</td><td>Moduli 3 · Content creation</td></tr>
      <tr><td>J4</td><td>Modulet 4 + 7 · Rritja + AI</td></tr>
      <tr><td>J5</td><td>Moduli 5 · Audienca që blen</td></tr>
      <tr><td>J6</td><td>Modulet 6 + 8 · Shitja + projekti final</td></tr>
    </table>
    <p class="small">AI vendoset në javën 4 sepse aty studenti ka nevojë të prodhojë më shpejt për të mbajtur ritmin e serisë.</p>
  </div>
</div>
''')


# ---------- Kartat e moduleve
def module_card(m):
    vids = "".join(
        f'<li><span class="vn">{m["n"]}.{i}</span><span class="vt">{t}</span><span class="vm">{mins} min</span></li>'
        for i, (t, mins) in enumerate(m["videos"], 1))
    tot = sum(v[1] for v in m["videos"])
    return f'''
<article class="mod">
  <div class="mod-head">
    <div class="mod-num"><span>Moduli</span><b>{m["n"]}</b></div>
    <div class="mod-t"><h3>{m["title"]}</h3>
      <div class="mod-meta">{icon("video",14)} {len(m["videos"])} video · {tot} min · {m["week"]}</div></div>
  </div>
  <div class="mod-goal"><b>Qëllimi:</b> {m["goal"]}</div>
  <ol class="vids">{vids}</ol>
  <div class="mod-foot">
    <div class="mf task">{icon("target",16)}<div><span>Detyra praktike</span>{m["task"]}</div></div>
    <div class="mf res">{icon("doc",16)}<div><span>Burimi për shkarkim</span>{m["res"]}</div></div>
  </div>
</article>'''


groups = [[0, 1, 2], [3, 4], [5, 6], [7, 8]]
for gi, g in enumerate(groups):
    head = f'<div class="kicker">05 · Kartat e moduleve · {gi + 1}/{len(groups)}</div>'
    extra = ""
    if gi == len(groups) - 1:
        res_rows = "".join(f'<tr><td class="c"><span class="mnum">{m["n"]}</span></td><td>{m["res"]}</td><td class="c">{len(m["videos"])}</td></tr>' for m in MODULES)
        extra = (sub("Kontrolli: burimet dhe numri i videove") +
                 f'<table class="tbl"><thead><tr><th class="c">Mod.</th><th>Burimi për shkarkim</th><th class="c">Video</th></tr></thead>'
                 f'<tbody>{res_rows}<tr class="total"><td></td><td>Totali: {len(MODULES)} burime, {N_MIN} min content</td><td class="c">{N_VIDEOS}</td></tr></tbody></table>')
    page(head + "".join(module_card(MODULES[i]) for i in g) + extra)

# ---------- 06 Modeli hibrid
page(f'''
{sec(6, "Modeli hibrid — si duket një javë", "Ritmi")}
<p class="lead">I njëjti ritëm çdo javë, për 6 javë. Studenti duhet ta dijë pa pyetur se çfarë ndodh të hënën, të enjten dhe të shtunën.</p>
<table class="tbl week">
  <thead><tr><th>Dita</th><th>Çfarë ndodh</th><th>Formati</th><th>Kush</th><th>Paketa</th></tr></thead>
  <tbody>
    <tr><td><b>E hënë 08:00</b></td><td>Hapen videot e javës + detyra</td><td>Platforma e kursit</td><td>Automatik</td><td>Të gjitha</td></tr>
    <tr><td><b>E hënë–e diel</b></td><td>Komuniteti: pyetje, “fitoret e ditës”, çifte përgjegjësie (buddy)</td><td>WhatsApp Community (3 grupe)</td><td>Asistenti + Rei</td><td>Të gjitha</td></tr>
    <tr><td><b>E mërkurë 20:00</b></td><td>Q&amp;A + hot-seat: 5–6 studentë ndajnë ekranin dhe marrin feedback live</td><td>Online (Zoom), 60 min</td><td>Rei</td><td>Hybrid, VIP</td></tr>
    <tr class="hlrow"><td><b>E enjte 19:00</b></td><td>Workshop praktik: punojmë mbi detyrën e javës në sallë</td><td>Tiranë në sallë + stream live, 2 orë</td><td>Rei (+ mysafir)</td><td>Hybrid, VIP</td></tr>
    <tr><td><b>E shtunë 23:59</b></td><td>Afati i dorëzimit të detyrës</td><td>Formular + link</td><td>Studenti</td><td>Të gjitha</td></tr>
    <tr><td><b>E diel–e martë</b></td><td>Feedback me shkrim/video mbi detyrën, brenda 48 orëve</td><td>Loom / komente</td><td>Rei + asistenti</td><td>Hybrid, VIP</td></tr>
    <tr><td><b>Sipas orarit</b></td><td>Seancë 1:1 (45 min) + auditim llogarie/oferte</td><td>Online ose Tiranë</td><td>Rei</td><td>VIP</td></tr>
  </tbody>
</table>
<div class="card soft mt">
  <div class="card-h">{icon("clock")}Koha që i kërkojmë studentit çdo javë: 5–7 orë</div>
  <div class="bars">
    <div><span>Video</span><i style="width:22%"></i><b>≈ 1–1,5 orë</b></div>
    <div><span>Detyra praktike</span><i style="width:52%"></i><b>≈ 3–4 orë</b></div>
    <div><span>Live + Q&amp;A</span><i style="width:30%"></i><b>≈ 2–3 orë</b></div>
  </div>
  <p class="small">Kjo thuhet hapur para blerjes — është filtri më i mirë kundër rimbursimeve.</p>
</div>
<div class="grid2 mt">
  <div class="card accent">
    <div class="card-h">{icon("users")}Max 25 studentë në sallë</div>
    <ul class="dots">
      <li><b>Hot-seat realist:</b> në 2 orë Rei jep feedback konkret për 8–10 persona; me 25 në sallë, çdo student del në hot-seat të paktën 2 herë në 6 javë.</li>
      <li><b>Kostoja e sallës</b> mbetet e ulët (sallë coworking në Tiranë) {HYP}.</li>
      <li><b>Mungesë e vërtetë</b> vendesh — argumenti ynë i vetëm i urgjencës, dhe është i ndershëm.</li>
      <li>Online live: max 25 të tjerë, me pyetje në chat.</li>
    </ul>
  </div>
  <div class="card soft">
    <div class="card-h">{icon("chat")}Komuniteti: një kanal, tre grupe</div>
    <ul class="dots">
      <li><b>Njoftime</b> — vetëm ekipi poston (orari, linke).</li>
      <li><b>Pyetje</b> — përgjigje brenda 24 orëve nga asistenti.</li>
      <li><b>Fitore</b> — studentët postojnë rezultate; këtu lindin testimonialet.</li>
    </ul>
    <p class="small"><b>Vendim:</b> WhatsApp, jo Telegram — audienca shqiptare e ka tashmë në telefon dhe njoftimet lexohen.</p>
  </div>
</div>
''')

# ---------- 07 Çmimet
TIERS = [
    ("Digital", "Mëso vetë, me ritmin tënd", 99, 79, "2 × 55 €", [
        f"{N_VIDEOS} video + të gjitha burimet",
        "Komuniteti WhatsApp",
        "Akses për 12 muaj",
        "Workshopi hyrës i regjistruar"], [
        "Pa workshope live", "Pa feedback mbi detyrat"], "pa limit", False),
    ("Hybrid", "Programi i plotë 6-javor", 249, 199, "3 × 89 €", [
        "Gjithçka te Digital",
        "6 workshope live (Tiranë ose online)",
        "6 Q&A / hot-seat online",
        "Feedback mbi çdo detyrë brenda 48 orëve",
        "Certifikatë për projektin final"], [], "25 në sallë + 25 online", True),
    ("VIP", "Puno drejtpërdrejt me Rein", 590, None, "3 × 209 €", [
        "Gjithçka te Hybrid",
        "3 seanca 1:1 me Rein (45 min)",
        "Auditim i llogarisë dhe ofertës (video)",
        "Akses WhatsApp direkt gjatë 6 javëve"], [], "vetëm 5 vende", False),
]
cards = ""
for name, tag, full, early, plan, inc, exc, seats, rec in TIERS:
    early_html = (f'<div class="eb">Early-bird (5 ditët e para): <b>{early} €</b> · {num(early*100)} lekë</div>'
                  if early else '<div class="eb">Pa early-bird — çmimi mbrohet nga numri i vendeve</div>')
    exc_html = "".join(f'<li class="no">{e}</li>' for e in exc)
    cards += f'''
<div class="price{' rec' if rec else ''}">
  {'<div class="rec-badge">E rekomanduar</div>' if rec else ''}
  <h3>{name}</h3><div class="ptag">{tag}</div>
  <div class="pbig">{full} €</div>
  <div class="pall">{num(full*100)} lekë</div>
  {early_html}
  <ul class="inc">{"".join(f"<li>{i}</li>" for i in inc)}{exc_html}</ul>
  <div class="pfoot"><div><span>Me këste</span><b>{plan}</b></div><div><span>Vende</span><b>{seats}</b></div></div>
</div>'''
page(f'''
{sec(7, "Paketat & çmimet", "Oferta")}
<p class="lead">Tre paketa, një rekomandim. Paketa Hybrid është produkti që duam të shesim; Digital e bën atë të duket e arsyeshme për ata që kanë buxhet të kufizuar, VIP e bën atë të duket e lirë.</p>
<div class="prices">{cards}</div>
<p class="small c mt-s">Të gjitha çmimet: {HYP} · Kohorta beta: 129 € (12.900 lekë) për përvojën Hybrid, 12 vende.</p>
{sub("Pse këto çmime për tregun shqiptar")}
<table class="tbl">
  <thead><tr><th>Paketa</th><th>Çmimi</th><th>≈ % e pagës mesatare mujore bruto*</th><th>Krahasimi që bën blerësi</th><th>Kthimi i investimit</th></tr></thead>
  <tbody>
    <tr><td><b>Digital</b></td><td>99 €</td><td>≈ 11%</td><td>Një darkë për dy + dalje / një muaj palestër premium</td><td>1 klient freelance me 100 €</td></tr>
    <tr class="hlrow"><td><b>Hybrid</b></td><td>249 €</td><td>≈ 27%</td><td>Kurs i zakonshëm në sallë në Tiranë (150–400 €) {HYP}</td><td>1 klient SMM me 250 €/muaj</td></tr>
    <tr><td><b>VIP</b></td><td>590 €</td><td>≈ 64%</td><td>1 muaj agjencie marketingu (400–800 €)</td><td>Rritje e shitjeve të biznesit</td></tr>
  </tbody>
</table>
<p class="small">* Paga mesatare bruto në Shqipëri ≈ 90–95 mijë lekë/muaj (INSTAT, 2025) — verifiko shifrën e fundit para publikimit. Avatari B (pronar biznesi) dhe studentët me familje në Tiranë kanë fuqi blerëse mbi mesataren.</p>

''')

page(f'''
<div class="kicker">07 · vazhdim</div>
<h2 class="sub first">Early-bird, këste, pagesa</h2>
<div class="grid3">
  <div class="card soft">
    <div class="card-h">{icon("bolt")}Early-bird</div>
    <p>Aktiv vetëm <b>5 ditët e para</b> të open cart (14–18 janar). Digital 79 €, Hybrid 199 €. Afati është real: pas orës 23:59 çmimi ndryshon në faqe dhe nuk rikthehet.</p>
  </div>
  <div class="card soft">
    <div class="card-h">{icon("calendar")}Pagesa me këste</div>
    <p>Digital 2 × 55 €, Hybrid 3 × 89 €, VIP 3 × 209 €. Totali me këste është 6–11% më i lartë. Kësti i parë jep akses; mungesa e kësti 2 pezullon aksesin live.</p>
  </div>
  <div class="card soft">
    <div class="card-h">{icon("money")}Mënyrat e pagesës</div>
    <p>Transfertë bankare, POK, kartë (nëpërmjet platformës, nëse mbështetet) dhe cash në Tiranë. Fatura/mandati i pagesës dërgohet brenda 24 orëve.</p>
  </div>
</div>

<div class="guarantee mt">
  <div class="g-ic">{icon("shield", 34)}</div>
  <div>
    <h3>Garancia 14-ditore e veprimit</h3>
    <p>Nëse brenda 14 ditëve nga fillimi i kohortës ke parë videot e javëve 1–2, ke dorëzuar 2 detyrat dhe mendon se programi nuk të vlen, të kthejmë <b>100% të parave</b>. Pa pyetje të tjera.</p>
    <ul class="dots two">
      <li>Pas ditës 14: pa rimbursim, por mund të kalosh <b>1 herë falas</b> në kohortën e ardhshme.</li>
      <li>VIP: rimbursim i plotë para seancës së parë 1:1; pas saj, rimbursim proporcional.</li>
      <li>Kushti “ke dorëzuar detyrat” largon ata që duan përmbajtjen falas.</li>
      <li>Vendi fizik në sallë nuk transferohet pas javës 2.</li>
    </ul>
  </div>
</div>
<div class="decision">{icon("check")}<div><b>Vendim:</b> nuk ulim kurrë çmimin pas lançimit. Çdo kohortë e re e rrit çmimin e Hybrid me 20–30 € sa kohë shtohen rezultatet e studentëve.</div></div>
{sub("Si e prezantojmë çmimin e Hybrid: “value stack”")}
<table class="tbl">
  <thead><tr><th>Çfarë merr studenti</th><th>Krahasimi në treg</th><th class="c">Vlera e perceptuar</th></tr></thead>
  <tbody>
    <tr><td>{N_VIDEOS} video + 9 burime (templates, swipe files, dashboard)</td><td>Kurs online i ngjashëm</td><td class="c">≈ 150 €</td></tr>
    <tr><td>6 workshope live në Tiranë (2 orë secili)</td><td>Workshop 1-ditor marketingu</td><td class="c">≈ 240 €</td></tr>
    <tr><td>6 Q&amp;A / hot-seat online</td><td>Seancë konsulence grupi</td><td class="c">≈ 120 €</td></tr>
    <tr><td>Feedback mbi 6 detyra brenda 48 orëve</td><td>Auditim nga agjencia (Rritje Sade)</td><td class="c">≈ 300 €</td></tr>
    <tr><td>Komuniteti + çifte përgjegjësie</td><td>—</td><td class="c">e pallogaritshme</td></tr>
    <tr class="total"><td>Vlera totale ≈ 810 €</td><td>Çmimi: 249 € (early-bird 199 €)</td><td class="c">≈ 3,3× vlerë</td></tr>
  </tbody>
</table>
<p class="small">{HYP} Vlerat janë krahasime që përdoren në faqen e shitjes dhe në workshop; përditësohen me çmimet reale të tregut dhe të Rritje Sade.</p>
''')

# ---------- 08 Lançimi – timeline
ORIGIN = dt.date(2026, 9, 28)
END = dt.date(2027, 3, 21)
SPAN = (END - ORIGIN).days


def pos(d):
    return (d - ORIGIN).days / SPAN * 100


PHASES = [
    ("Para-lançimi: lista e pritjes", dt.date(2026, 9, 28), dt.date(2027, 1, 13), "p1", 0),
    ("Prodhimi i videove", dt.date(2026, 10, 5), dt.date(2026, 11, 20), "p2", 1),
    ("Kohorta beta (12 studentë)", dt.date(2026, 11, 2), dt.date(2026, 12, 13), "p3", 2),
    ("Case studies", dt.date(2026, 12, 14), dt.date(2026, 12, 27), "p2", 3),
    ("Ngrohja", dt.date(2026, 12, 28), dt.date(2027, 1, 13), "p1", 3),
    ("Workshop + open cart", dt.date(2027, 1, 14), dt.date(2027, 1, 23), "p4", 4),
    ("Kohorta 1", dt.date(2027, 2, 1), dt.date(2027, 3, 14), "p3", 5),
]
months = [(dt.date(2026, 10, 1), "Tet"), (dt.date(2026, 11, 1), "Nën"), (dt.date(2026, 12, 1), "Dhj"),
          (dt.date(2027, 1, 1), "Jan"), (dt.date(2027, 2, 1), "Shk"), (dt.date(2027, 3, 1), "Mar")]
MON = ["jan", "shk", "mar", "pri", "maj", "qer", "korr", "gush", "sht", "tet", "nën", "dhj"]


def dshort(d):
    return f"{d.day} {MON[d.month - 1]}"


tl = '<div class="tl"><div class="tl-row tl-head"><div class="tl-l"></div><div class="tl-track">'
tl += "".join(f'<span class="tl-m" style="left:{pos(d):.2f}%">{l}</span>' for d, l in months)
tl += '</div></div>'
for name, s_, e, c, row in PHASES:
    grid = "".join(f'<i class="tl-grid" style="left:{pos(d):.2f}%"></i>' for d, _ in months)
    tl += (f'<div class="tl-row"><div class="tl-l"><b>{name}</b><span>{dshort(s_)} – {dshort(e)}</span></div>'
           f'<div class="tl-track">{grid}<div class="tl-bar {c}" style="left:{pos(s_):.2f}%;width:{pos(e + dt.timedelta(days=1)) - pos(s_):.2f}%"></div></div></div>')
tl += '</div>'

page(f'''
{sec(8, "Plani i marketingut & lançimit", "Nga lista e pritjes te kohorta 1")}
<p class="lead">Lançimi nis nga lista që po ndërtojmë me dokumentin falas prej 60 faqesh. Asnjë hap nuk kërkon reklama me pagesë para se të kemi prova nga kohorta beta.</p>
{tl}
<div class="grid2 mt">
  <div class="phase">
    <div class="ph-n">Faza 1 · 28 shtator – 13 janar</div>
    <h3>Para-lançimi: lista e pritjes</h3>
    <ul class="dots">
      <li><b>Objektivi:</b> 800 leads deri më 1 nëntor, <b>1.500 leads</b> deri më 13 janar (≈ 100–110 në javë) {HYP}</li>
      <li><b>Lead magnet:</b> dokumenti 60-faqësh jepet vetëm pas emailit + numrit WhatsApp. Pa këtë, s’ka listë pritjeje.</li>
      <li><b>Automatizim:</b> “Komento RRITJE” nën reels → DM automatik me linkun (ManyChat).</li>
      <li><b>Seria “Po ndërtoj Rritje Academy”</b>: 2 episode/javë behind-the-scenes (skriptet, filmimi, gabimet, numrat e listës). Përputhet me brandin “progres real”.</li>
      <li><b>Vlerë çdo javë:</b> 3 reels edukative me CTA drejt dokumentit.</li>
      <li><b>Formulari</b> pyet: avatari (A/B/C), buxheti, pengesa kryesore — të dhënat për çmimin.</li>
    </ul>
  </div>
  <div class="phase">
    <div class="ph-n">Faza 2 · 2 nëntor – 13 dhjetor</div>
    <h3>Kohorta beta: 12 studentë</h3>
    <ul class="dots">
      <li><b>Kush:</b> 10–15 studentë të zgjedhur me aplikim nga lista (mix A/B/C).</li>
      <li><b>Çmimi:</b> 129 € për përvojën e plotë Hybrid (≈ −50%).</li>
      <li><b>Në këmbim:</b> testimonial video, numra para/pas, formular feedback çdo javë, leje për case study.</li>
      <li><b>Pse para lançimit të madh:</b>
        <ol class="why">
          <li>Tregu shqiptar blen me prova sociale; pa të, konvertimi bie ndjeshëm.</li>
          <li>Testojmë videot, ritmin dhe completion para se të shesim te 1.500 njerëz.</li>
          <li>Të ardhurat e para (≈ 1.550 €) mbulojnë prodhimin.</li>
          <li>Rezultatet e beta-s bëhen content për lançimin e janarit.</li>
        </ol></li>
    </ul>
  </div>
</div>
''')

SEQ = [
    ("D−7", "Email + WhatsApp", "Ftesa", "“Workshop falas: si të marrësh 1.000 ndjekësit e parë që blejnë” + regjistrim"),
    ("D−3", "Email", "Problemi", "Pse po poston dhe s’po rritesh: 3 gabimet që shoh te llogaritë shqiptare"),
    ("D−1", "Email + WhatsApp", "Kujtesë", "Çfarë do të mësosh nesër + 1 rezultat nga beta"),
    ("D0", "WhatsApp", "Live", "Linku 2 orë dhe 10 minuta para fillimit"),
    ("Dita 1", "Email + WhatsApp", "Dyert u hapën", "Oferta, 3 paketat, early-bird, linku i replay-t"),
    ("Dita 2", "Email", "Replay", "Replay (48 orë) + përmbledhja e workshopit në 5 pika"),
    ("Dita 3", "Email + WhatsApp", "Case study", "Historia e një studenti beta me numra para/pas"),
    ("Dita 4", "Email", "FAQ / kundërshtime", "Koha, çmimi, “a funksionon për nishën time?”"),
    ("Dita 5", "Email + WhatsApp", "Afat real", "Early-bird mbyllet sonte në 23:59"),
    ("Dita 6", "Email", "Historia ime", "Pse e ndërtova akademinë — progres real, jo “ia dola”"),
    ("Dita 7", "Email", "Cila paketë?", "Krahasimi i paketave sipas avatarit A/B/C"),
    ("Dita 8", "WhatsApp", "Vendet", "Në sallë kanë mbetur X nga 25 vende (numri real)"),
    ("Dita 9", "Email", "Kostoja e pritjes", "Ku do jesh në mars nëse s’ndryshon asgjë + garancia 14-ditore"),
    ("Dita 10", "Email + WhatsApp ×2", "Mbyllja", "Mëngjes: “sot mbyllet”; 3 orë para: “mbyllet në 23:59”"),
]
seq_rows = "".join(f'<tr{" class=hlrow" if d in ("Dita 1","Dita 5","Dita 10") else ""}><td><b>{d}</b></td><td>{ch}</td><td><b>{a}</b></td><td>{t}</td></tr>' for d, ch, a, t in SEQ)
page(f'''
<div class="kicker">08 · vazhdim</div>
<div class="phase wide">
  <div class="ph-n">Faza 3 · 28 dhjetor – 23 janar</div>
  <h3>Lançimi zyrtar: workshop falas + open cart 10 ditë</h3>
  <div class="grid3 tight">
    <div class="kv">{icon("pin")}<div><b>E enjte, 14 janar 2027, 19:00</b><span>Workshop falas 90 min · Tiranë (80 vende) + live online</span></div></div>
    <div class="kv">{icon("calendar")}<div><b>14–23 janar</b><span>Open cart 10 ditë · early-bird deri më 18 janar</span></div></div>
    <div class="kv">{icon("users")}<div><b>Mungesë reale</b><span>25 vende në sallë, 5 VIP, afat early-bird</span></div></div>
  </div>
</div>
{sub("Sekuenca email + WhatsApp")}
<table class="tbl seq">
  <thead><tr><th>Kur</th><th>Kanali</th><th>Këndi</th><th>Mesazhi</th></tr></thead>
  <tbody>{seq_rows}</tbody>
</table>
<p class="small">Rregull: çdo mesazh ka 1 ide dhe 1 CTA. WhatsApp përdoret vetëm për ata që kanë dhënë leje në formular — max 1 mesazh/ditë, përveç ditës së fundit.</p>
''')

CONTENT = [
    ("Reels vlerë", "Instagram + TikTok", "3", "Reach — ndjekës të rinj në listë"),
    ("Reels behind-the-scenes", "Instagram + TikTok", "2", "Besim — “po e ndërtoj para jush”"),
    ("Rezultatet e beta-s", "Instagram, TikTok, stories", "2", "Provë — heq kundërshtimin “a funksionon?”"),
    ("Carousel", "Instagram", "2", "Saves/shares — mësim i thellë, ruhet"),
    ("Stories", "Instagram", "çdo ditë, 5–8 frames", "Lidhje — sondazhe, pyetje, numërim mbrapsht"),
    ("Video e gjatë / podcast", "YouTube", "1", "Autoritet + SEO; clip-et bëhen Shorts"),
    ("Live Q&A", "Instagram", "1", "Kundërshtimet live, në javën e open cart"),
    ("Email", "Lista", "2 (para) · 1/ditë (open cart)", "Konvertim"),
    ("WhatsApp Channel", "WhatsApp", "2–3 · 1/ditë (open cart)", "Konvertim + kujtesa"),
]
c_rows = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="c">{c}</td><td>{d}</td></tr>' for a, b, c, d in CONTENT)
page(f'''
<div class="kicker">08 · vazhdim</div>
<div class="phase wide">
  <div class="ph-n">Faza 4 · nga marsi 2027</div>
  <h3>Pas lançimit: evergreen</h3>
  <div class="grid2 tight">
    <ul class="dots">
      <li><b>Digital shitet gjatë gjithë vitit</b> nga faqja e shitjes + workshopi i regjistruar si webinar automatik.</li>
      <li><b>Kohorta Hybrid çdo 4 muaj:</b> shkurt, qershor, tetor (korriku–gushti është sezon i dobët) {HYP}.</li>
    </ul>
    <ul class="dots">
      <li><b>Referimi:</b> alumni marrin 15% (≈ 37 €) për çdo student Hybrid; i riu merr 20 € ulje.</li>
      <li><b>Rezultatet e studentëve = content:</b> 1 case study/javë, me leje me shkrim.</li>
    </ul>
  </div>
</div>
{sub("Plani i content-it për muajin e lançimit (janar)")}
<table class="tbl">
  <thead><tr><th>Lloji</th><th>Kanali</th><th class="c">Sa në javë</th><th>Çfarë bën</th></tr></thead>
  <tbody>{c_rows}</tbody>
</table>
<div class="grid3 mt">
  <div class="card soft"><div class="card-h">{icon("layers")}Instagram & TikTok</div><p>Kanali kryesor. I njëjti reel publikohet në të dyja; hook-u përshtatet. TikTok për avatarin A, Instagram për B dhe C.</p></div>
  <div class="card soft"><div class="card-h">{icon("mail")}Email & WhatsApp</div><p>Kanalet ku ndodh shitja. Lista është aseti ynë; platformat janë vetëm vendi ku e ndërtojmë.</p></div>
  <div class="card soft"><div class="card-h">{icon("users")}Partneritete</div><p>3–5 kreatorë/biznese shqiptare ndajnë workshopin; 2 universitete/klube studentore; klientët e Rritje Sade si case studies.</p></div>
</div>
''')

# ---------- 09 Numrat
FUNNEL = [("Leads në listë", 1500, None), ("Regjistrohen në workshop", 450, "30%"),
          ("Marrin pjesë live", 180, "40%"), ("Blejnë nga live-i", 18, "10%"),
          ("Blejnë nga replay + sekuenca", 20, "1,5% e 1.320 të tjerëve")]
fmax = 1500
f_html = ""
for i, (lab, v, conv) in enumerate(FUNNEL):
    w = max(8, (v / fmax) ** 0.5 * 100)
    f_html += (f'<div class="fr"><div class="fl">{lab}</div><div class="fbar"><i style="width:{w:.1f}%"></i>'
               f'<b>{num(v)}</b></div><div class="fc">{conv or ""}</div></div>')
REV = [("Digital", 20, 89, "mix early-bird/full"), ("Hybrid", 16, 224, "mix early-bird/full"), ("VIP", 2, 590, "full")]
rev_rows = "".join(f'<tr><td><b>{t}</b></td><td class="c">{b}</td><td class="c">{p} €</td><td class="c"><b>{num(b*p)} €</b></td></tr>' for t, b, p, n in REV)
rev_total = sum(b * p for _, b, p, _ in REV)
page(f'''
{sec(9, "Numrat: objektivat & metrikat", "Kohorta 1 · skenari bazë")}
<p class="lead">Të gjitha shifrat në këtë faqe janë {HYP}. Pas kohortës beta i zëvendësojmë me numrat realë.</p>
<div class="funnel">{f_html}
  <div class="fr total"><div class="fl">Blerës gjithsej</div><div class="fbar"><i style="width:16%"></i><b>38</b></div><div class="fc">2,5% e listës</div></div>
</div>
<div class="grid2 mt">
  <div>
    {sub("Të ardhurat për kohortë sipas paketës")}
    <table class="tbl">
      <thead><tr><th>Paketa</th><th class="c">Blerës</th><th class="c">Çmimi mesatar*</th><th class="c">Të ardhura</th></tr></thead>
      <tbody>{rev_rows}<tr class="total"><td>Totali</td><td class="c">38</td><td></td><td class="c">{num(rev_total)} €</td></tr></tbody>
    </table>
    <table class="tbl mt-s">
      <thead><tr><th>Skenari</th><th class="c">Leads</th><th class="c">Blerës</th><th class="c">Të ardhura</th></tr></thead>
      <tbody>
        <tr><td>Konservativ</td><td class="c">1.000</td><td class="c">20</td><td class="c">≈ 3.300 €</td></tr>
        <tr class="hlrow"><td><b>Bazë</b></td><td class="c">1.500</td><td class="c">38</td><td class="c">≈ {num(round(rev_total, -2))} €</td></tr>
        <tr><td>Optimist</td><td class="c">2.500</td><td class="c">70</td><td class="c">≈ 12.000 €</td></tr>
      </tbody>
    </table>
    <p class="small">* Mesatare e early-bird dhe çmimit të plotë. Kostot direkte për kohortë (salla, asistenti, platforma, reklamat e workshopit) ≈ 1.200–1.600 € {HYP}.</p>
  </div>
  <div>
    {sub("5 KPI që ndjekim çdo të hënë")}
    <ol class="kpis">
      <li><b>Leads të rinj në javë</b><span>Objektivi: ≥ 100</span></li>
      <li><b>Shkalla e hapjes së emailit</b><span>Objektivi: ≥ 40% (lista e ngrohtë)</span></li>
      <li><b>Show-up rate në workshop</b><span>Objektivi: ≥ 40% e të regjistruarve</span></li>
      <li><b>Konvertimi lista → blerës</b><span>Objektivi: ≥ 2,5%</span></li>
      <li><b>Completion javor</b><span>% e studentëve që dorëzojnë detyrën · objektivi ≥ 70%</span></li>
    </ol>
    <div class="grid2 tight mt-s">
      <div class="stat"><b>≈ 4,4 €</b><span>vlera e një leadi (6.544 € / 1.500)</span></div>
      <div class="stat"><b>≤ 1,5 €</b><span>kosto maksimale për lead nëse blejmë reklama</span></div>
    </div>
    <div class="decision sm">{icon("check")}<div>Nëse leads/javë &lt; 70 për 3 javë rresht, lançimi shtyhet 2 javë — nuk lançojmë mbi një listë të vogël.</div></div>
  </div>
</div>
''')

# ---------- 10 Prodhimi
page(f'''
{sec(10, "Prodhimi i videove", f"{N_VIDEOS} video në 7 ditë filmimi")}
<div class="grid2">
  <div>
    {sub("Pajisjet — versioni me buxhet")}
    <table class="tbl">
      <thead><tr><th>Pajisja</th><th>Zgjedhja</th><th class="c">Kosto</th></tr></thead>
      <tbody>
        <tr><td>{icon("phone",14)} Kamera</td><td>Telefoni ekzistues (4K, kamera e pasme)</td><td class="c">0 €</td></tr>
        <tr><td>{icon("mic",14)} Mikrofoni</td><td>Mikrofon wireless me klip (2 transmetues)</td><td class="c">60–100 €</td></tr>
        <tr><td>{icon("sun",14)} Drita</td><td>2 panele LED me softbox</td><td class="c">50–80 €</td></tr>
        <tr><td>Stativ + mbajtëse</td><td>Stativ 1,7 m me mbajtëse telefoni</td><td class="c">20–30 €</td></tr>
        <tr><td>Teleprompter</td><td>Aplikacion falas në tablet/telefon të dytë</td><td class="c">0 €</td></tr>
        <tr class="total"><td>Totali</td><td></td><td class="c">130–210 €</td></tr>
      </tbody>
    </table>
    <p class="small">Zëri ka më shumë rëndësi se imazhi: studentët falin një imazh mesatar, jo një zë me jehonë.</p>
  </div>
  <div>
    {sub("Filmimi me batch")}
    <div class="grid2 tight">
      <div class="stat"><b>8–10</b><span>video për ditë filmimi (≈ 9 mesatarisht)</span></div>
      <div class="stat"><b>7</b><span>ditë filmimi (6 + 1 rixhirim)</span></div>
    </div>
    <ul class="dots mt-s">
      <li><b>Mëngjesi (3 orë):</b> 4–5 video, e njëjta veshje dhe sfond për çdo modul.</li>
      <li><b>Pas dite (3 orë):</b> 4–5 video + b-roll për secilën.</li>
      <li><b>Rregulli:</b> skriptet mbyllen 3 ditë para filmimit; në set nuk shkruhet asgjë.</li>
    </ul>
  </div>
</div>
{sub("Workflow-i i editimit (1 video ≈ 2 orë pune)")}
<div class="flow">
  <div><span>1</span><b>Skripti</b><em>Notion, outline me pika</em></div>
  <div><span>2</span><b>Filmimi</b><em>Batch 8–10/ditë</em></div>
  <div><span>3</span><b>Upload</b><em>Google Drive, emërtim M3-07</em></div>
  <div><span>4</span><b>Rough cut</b><em>Editori, brenda 48 orëve</em></div>
  <div><span>5</span><b>Review</b><em>Rei, 1 raund komentesh</em></div>
  <div><span>6</span><b>Final</b><em>Titra shqip, grafika, eksport</em></div>
  <div><span>7</span><b>Publikimi</b><em>Platforma + burimi PDF</em></div>
</div>
{sub("Standardi i çdo videoje (checklist para publikimit)")}
<div class="grid3 tight">
  <div class="card soft"><div class="card-h">{icon("bolt")}Hapja</div><p>Në 10 sekondat e para: çfarë do mësosh dhe pse të duhet sot. Pa hyrje, pa “përshëndetje, sot do…”.</p></div>
  <div class="card soft"><div class="card-h">{icon("target")}1 ide, 1 shembull</div><p>Një koncept për video, me një shembull shqiptar (klient i Rritje Sade ose llogari publike).</p></div>
  <div class="card soft"><div class="card-h">{icon("check")}Mbyllja</div><p>Çdo video mbaron me veprimin konkret që studenti bën tani, i lidhur me detyrën e javës. Titra shqip në çdo video.</p></div>
</div>
<p class="small">Editimi: ≈ {N_VIDEOS * 2} orë pune gjithsej. Bëhet nga editori i Rritje Sade; kosto e brendshme që duhet llogaritur në ndarjen e të ardhurave.</p>
''')

PLAT = [
    ("Thinkific", "≈ 36–74 $/muaj", "Kartë nëpërmjet Stripe/PayPal — kontrollo nëse pranohet llogari shqiptare", "Regjistrim manual i studentëve, drip content, raporte completion", "Mbrojtje e kufizuar e videove"),
    ("Skool", "≈ 99 $/muaj", "Stripe — llogaritë shqiptare zakonisht nuk mbështeten", "Kurs + komunitet në një vend, gamification", "Dizajn fiks; dyfishon komunitetin WhatsApp"),
    ("WordPress + Tutor LMS + Bunny Stream", "≈ 15–30 €/muaj + setup", "Çdo metodë: bankë, POK, cash, procesor lokal kartash", "Kontroll i plotë, watermark dinamik, pa komision", "Kërkon setup nga partnerët web (1–2 javë)"),
]
p_rows = "".join(f'<tr{" class=hlrow" if i == 0 else ""}><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>' for i, (a, b, c, d, e) in enumerate(PLAT))
CAL = [
    ("28 sht – 2 tet", "Outline i 9 moduleve, skriptet M0–M1", ""),
    ("5 – 9 tet", "Skriptet M2–M3 · blerja e pajisjeve", ""),
    ("12 – 16 tet", "Filmim ditët 1–3 (M0–M3, 25 video)", "film"),
    ("19 – 30 tet", "Editimi M0–M3 · skriptet M4–M8", ""),
    ("2 – 6 nën", "Filmim ditët 4–6 (M4–M8, 28 video) · beta nis", "film"),
    ("9 – 20 nën", "Editimi M4–M8, publikim javor për beta-n", ""),
    ("14 – 20 dhj", "Dita 7: rixhirim i videove me feedback të dobët", "film"),
    ("21 – 31 dhj", "Burimet PDF finale · setup i platformës", ""),
]
cal_rows = "".join(f'<tr{" class=hlrow" if c == "film" else ""}><td><b>{a}</b></td><td>{b}</td></tr>' for a, b, c in CAL)
page(f'''
<div class="kicker">10 · vazhdim</div>
<h2 class="sub first">Ku e hostojmë kursin</h2>
<table class="tbl">
  <thead><tr><th>Platforma</th><th>Kosto</th><th>Pagesat nga Shqipëria</th><th>Plus</th><th>Minus</th></tr></thead>
  <tbody>{p_rows}</tbody>
</table>
<p class="small">Çmimet dhe mbështetja e pagesave ndryshojnë — verifiko para se të paguash. {HYP}</p>
<div class="decision">{icon("check")}<div><b>Rekomandim:</b> për beta-n dhe kohortën 1 marrim pagesat lokalisht (bankë/POK/cash) dhe i regjistrojmë studentët manualisht në <b>Thinkific</b> (setup në 2 ditë). Kalojmë në WordPress + Bunny Stream kur të kalojmë 200 studentë, ose kur pirateria bëhet problem real.</div></div>
{sub("Kalendari i prodhimit")}
<table class="tbl cal">
  <thead><tr><th>Periudha</th><th>Çfarë bëhet</th></tr></thead>
  <tbody>{cal_rows}</tbody>
</table>
<p class="small">Rreshtat e theksuar janë ditë filmimi. Beta-s i nevojiten vetëm videot e javës së ardhshme — kjo na lejon të fillojmë më 2 nëntor pa i pasur të gatshme të {N_VIDEOS} videot.</p>
''')

# ---------- 11 Roadmap
ROAD = [
    ("Faza 1", "Flagship: Marketing & content", "Tani", "Rei Canka", f"{N_VIDEOS}", "Baza — çdo kurs tjetër shitet te alumni i saj.", "video", True),
    ("Faza 2", "Web development", "Flagship ≥ 100 studentë që kanë paguar + completion ≥ 50% + ≥ 20% e alumni-ve kërkojnë faqe", "Partnerët e Rritje Sade (web)", "≈ 30", "“Ndërtoje vetë faqen e shitjes nga Moduli 6.” Alumni −25%.", "code", False),
    ("Faza 3", "App development", "Web dev ≥ 60 studentë + completion ≥ 40% + mentor i dytë i disponueshëm", "Partnerët e Rritje Sade (app)", "≈ 40", "Hapi i natyrshëm pas web dev; shitet te alumni i Fazës 2.", "phone", False),
    ("Faza 4", "AI për biznes (kursi i plotë)", "Moduli 7 me vlerësim ≥ 4,5/5 dhe ≥ 30% kërkesa në anketë — mund të dalë para Fazës 3", "Partnerët + Rei", "≈ 25", "Zgjeron Modulin 7; shitet edhe te pronarët e biznesit (avatari B).", "cpu", False),
    ("Më vonë", "Rritje Pass + certifikata", "≥ 3 kurse live + ≥ 300 alumni", "Ekipi", "—", "Anëtarësim 25 €/muaj ose 199 €/vit për të gjitha kurset {HYP}", "layers", False),
]
r_html = ""
for ph, name, trig, who, vids, cross, ic, cur in ROAD:
    r_html += f'''
<div class="road{' cur' if cur else ''}">
  <div class="road-ph">{icon(ic, 20)}<span>{ph}</span></div>
  <div class="road-b">
    <h3>{name}</h3>
    <div class="road-g">
      <div><span>Kur lançohet</span>{trig}</div>
      <div><span>Kush mëson</span>{who}</div>
      <div><span>Video</span>{vids}</div>
      <div><span>Cross-sell</span>{cross.replace("{HYP}", HYP)}</div>
    </div>
  </div>
</div>'''
page(f'''
{sec(11, "Roadmap i akademisë — fazat e ardhshme", "Lançojmë sipas kushteve, jo sipas datave")}
<div class="roads">{r_html}</div>
<div class="agree">
  <div class="card-h">{icon("doc")}Çfarë duhet rënë dakord me shkrim mes partnerëve, PARA se të regjistrohet kursi i parë i tyre</div>
  <div class="grid2 tight">
    <ul class="dots">
      <li><b>Ndarja e të ardhurave për kurs:</b> propozim — mësuesi 50% / akademia 50% e të ardhurave neto (pas platformës, reklamave, editimit) {HYP}.</li>
      <li><b>Pronësia e content-it:</b> Rritje Academy ka licencë ekskluzive për videot; mësuesi ruan të drejtën të japë mësim live gjetkë.</li>
    </ul>
    <ul class="dots">
      <li><b>Suporti:</b> kush u përgjigjet pyetjeve të studentëve, në sa orë, dhe kush e paguan asistentin.</li>
      <li><b>Nëse dikush largohet:</b> videot mbeten në akademi për min. 24 muaj; mësuesi merr pjesën e vet për atë periudhë; pa konkurrencë direkte për 12 muaj.</li>
    </ul>
  </div>
</div>
''')

# ---------- 12 Rreziqet
RISKS = [
    ("Completion i ulët", "Studentët blejnë, shikojnë 2 video dhe ndalen; pa rezultate, pa testimoniale.",
     "Video 5–12 min, afat çdo të shtunë, çifte buddy, “fitoret” në grup, telefonatë 5-min me çdo student që humbet 2 afate. Objektivi: ≥ 70% dorëzime në javë."),
    ("Shumë kurse njëherësh", "Web, app dhe AI dalin para se flagship të funksionojë; cilësia bie dhe ekipi shpërndahet.",
     "Roadmap-i me kushte (faqja {{P11}}). Maksimumi 1 kurs i ri në 6 muaj. Asnjë kurs i ri pa 100 studentë që kanë paguar për flagship."),
    ("Rei — pikë e vetme dështimi", "Sëmundje, lodhje ose kohë e zënë me agjencinë ndalon workshopet dhe feedback-un.",
     "Asistent (nga alumni i beta-s) për feedback dhe komunitetin; 1 bashkëthemelues gati të zëvendësojë në workshop; workshopi 6 bëhet me mysafirë; Rei ka max 8 orë/javë për akademinë."),
    ("Çmimi gabim për Shqipërinë", "Shumë i lartë: pak shitje. Shumë i ulët: s’mbulon kostot dhe ul perceptimin e vlerës.",
     "Anketë çmimi te lista (tetor), beta me 129 €, 3 paketa + këste. Pas 3 kohortave: ndryshim çmimi vetëm me të dhëna konvertimi."),
    ("Pirateria e videove", "Videot shpërndahen në grupe Telegram/Drive; vlera e paketës Digital bie.",
     "Pa shkarkime, watermark me emailin e studentit, vlera kryesore te live-i dhe feedback-u (s’piratohen), Digital me çmim të ulët, kushte përdorimi me shkrim, raportim i grupeve."),
]
rk = "".join(f'''
<div class="risk">
  <div class="rk-n">{i}</div>
  <div class="rk-b"><h3>{t}</h3><p class="rk-what">{w}</p></div>
  <div class="rk-m"><span>Si e shmangim</span>{m}</div>
</div>''' for i, (t, w, m) in enumerate(RISKS, 1))
page(f'''
{sec(12, "Rreziqet & si i shmangim", "Top 5")}
<div class="risks">{rk}</div>
<div class="decision">{icon("alert")}<div><b>Rreziku që s’duket:</b> dokumenti 60-faqësh jepet pa marrë emailin/WhatsApp-in. Atëherë mbledhim views, jo listë. Kontrollo sot që linku në bio kalon nga një formular.</div></div>
''')

# ---------- 13 Plani në 1 faqe
page(f'''
<div class="onepage">
  <div class="op-head">
    <div>{logo(38)}</div>
    <div><div class="op-k">13 · Plani në 1 faqe</div><h1>Rritje Academy — kohorta 1</h1></div>
  </div>
  <div class="op-promise">Në 6 javë: nga content pa drejtim te një sistem që sjell audiencë çdo javë dhe shitjet e para online.</div>
  <div class="op-grid">
    <div class="op-box">
      <h4>{icon("video",16)} Programi</h4>
      <ul>
        <li><b>{len(MODULES)} module · {N_VIDEOS} video · {fmt_hours(N_MIN)}</b></li>
        <li>Video 5–12 min, detyrë çdo javë</li>
        <li>6 workshope live në Tiranë + online</li>
        <li>Max 25 në sallë + 25 online</li>
        <li>WhatsApp Community · feedback 48 orë</li>
      </ul>
    </div>
    <div class="op-box">
      <h4>{icon("money",16)} Çmimet</h4>
      <table class="op-t">
        <tr><td>Digital</td><td>99 € · 9.900 L</td></tr>
        <tr class="rec"><td>Hybrid</td><td>249 € · 24.900 L</td></tr>
        <tr><td>VIP (5)</td><td>590 € · 59.000 L</td></tr>
        <tr><td>Beta</td><td>129 € · 12 vende</td></tr>
      </table>
      <p>Early-bird 5 ditë · këste · garanci 14 ditë</p>
    </div>
    <div class="op-box">
      <h4>{icon("target",16)} Objektivat</h4>
      <ul>
        <li><b>1.500</b> leads deri më 13 janar</li>
        <li><b>180</b> në workshop live</li>
        <li><b>38</b> blerës · <b>≈ 6.500 €</b></li>
        <li><b>≥ 70%</b> dorëzime javore</li>
        <li><b>≥ 60%</b> projekt final (Hybrid)</li>
      </ul>
    </div>
  </div>
  <div class="op-tl">
    <h4>{icon("calendar",16)} Datat</h4>
    <div class="op-steps">
      <div><b>28 sht</b><span>Lista e pritjes + seria “Po ndërtoj akademinë”</span></div>
      <div><b>12 tet</b><span>Filmimi fillon (7 ditë, ≈ 9 video/ditë)</span></div>
      <div><b>2 nën</b><span>Beta: 12 studentë, 6 javë</span></div>
      <div><b>14 dhj</b><span>Case studies + rixhirime</span></div>
      <div class="hot"><b>14 jan</b><span>Workshop falas + open cart</span></div>
      <div><b>23 jan</b><span>Mbyllja e shitjes</span></div>
      <div><b>1 shk</b><span>Kohorta 1 fillon</span></div>
    </div>
  </div>
  <div class="op-funnel">
    <div><b>1.500</b><span>leads</span></div><em>30%</em>
    <div><b>450</b><span>regjistrohen</span></div><em>40%</em>
    <div><b>180</b><span>në workshop</span></div><em>+ replay</em>
    <div class="hot"><b>38</b><span>blerës</span></div><em>=</em>
    <div class="hot"><b>≈ 6.500 €</b><span>kohorta 1</span></div>
  </div>
  <div class="op-grid two">
    <div class="op-box">
      <h4>{icon("chart",16)} 5 KPI çdo të hënë</h4>
      <ol>
        <li>Leads të rinj/javë (≥ 100)</li>
        <li>Hapja e emailit (≥ 40%)</li>
        <li>Show-up në workshop (≥ 40%)</li>
        <li>Lista → blerës (≥ 2,5%)</li>
        <li>Completion javor (≥ 70%)</li>
      </ol>
    </div>
    <div class="op-box dark">
      <h4>{icon("bolt",16)} 3 veprimet e kësaj jave</h4>
      <ol>
        <li>Vendos formularin (email + WhatsApp + avatari) para dokumentit 60-faqësh.</li>
        <li>Publiko episodin 1 të “Po ndërtoj Rritje Academy”.</li>
        <li>Nis anketën e çmimit te lista dhe hap aplikimet për beta-n.</li>
      </ol>
    </div>
  </div>
</div>
''', cls="op")

# ---------------------------------------------------------------- HTML
CSS = (ROOT / "style.css").read_text(encoding="utf-8")
FONTS = (ROOT / "fonts" / "local.css").read_text(encoding="utf-8")
total = len(pages)
out = []
secpage = {}
for i, (body, cls, footer) in enumerate(pages, 1):
    f = ""
    if footer:
        f = (f'<footer class="pf">{logo(12, "#02464F")}<span>Rritje Academy — nga Rritje Sade</span>'
             f'<span class="pf-mid">Dokument i brendshëm strategjik</span><span class="pf-n">{i:02d} / {total:02d}</span></footer>')
    out.append(f'<section class="page {cls}">{body}{f}</section>')
    m = re.search(r'class="secnum">(\d\d)<', body) or re.search(r'class="op-k">(\d\d) ', body)
    if m:
        secpage[m.group(1)] = i

body_html = "".join(out)
for k, v in secpage.items():
    body_html = body_html.replace('{{P' + k + '}}', str(v))
assert '{{P' not in body_html
body_html = re.sub(r'(\d) (€|%|lekë|L\b|min\b|orë|video\b)', r'\1&nbsp;\2', body_html)
body_html = re.sub(r'(≈|×|≥|≤) ', r'\1&nbsp;', body_html)
html = f'''<!doctype html>
<html lang="sq"><head><meta charset="utf-8">
<title>Rritje Academy — Plani strategjik</title>
<style>{FONTS}
{CSS}</style></head>
<body>{body_html}</body></html>'''
(ROOT / "rritje-academy.html").write_text(html, encoding="utf-8")
print(f"faqe: {total} · video: {N_VIDEOS} · minuta: {N_MIN} ({fmt_hours(N_MIN)}) · mesatarja {AVG_MIN:.1f}")
