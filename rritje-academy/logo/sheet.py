import re
def inl(name, h=None, w=None):
    s = open(f"svg/{name}").read()
    s = re.sub(r' width="[^"]+" height="[^"]+"', '', s, count=1)
    style = f'height:{h}px' if h else f'width:{w}px'
    return s.replace('<svg ', f'<svg style="{style};display:block" ', 1)
def panel(label, body, bg="#fff", fg="#5B6B6E", h=420):
    return f'<section style="background:{bg};height:{h}px"><div class="lab" style="color:{fg}">{label}</div><div class="c">{body}</div></section>'
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#fff;font-family:Inter,Helvetica,sans-serif;width:1600px}}
section{{position:relative;border-bottom:1px solid #eee}}
.c{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:90px}}
.lab{{position:absolute;left:40px;top:28px;font-size:15px;letter-spacing:.14em;text-transform:uppercase;font-weight:600}}
.row{{display:flex;align-items:flex-end;gap:36px}}
.cap{{font-size:12px;color:#8a9699;text-align:center;margin-top:10px}}
.split{{display:grid;grid-template-columns:1fr 1fr}}
</style></head><body>
{panel("1 · Logo e plotë", inl("rritje-academy-logo.svg", h=170), h=520)}
{panel("2 · Vetëm simboli", f"""
  <div>{inl("rritje-academy-simboli.svg", h=200)}<div class="cap">Simboli</div></div>
  <div>{inl("rritje-academy-ikona-app.svg", h=200)}<div class="cap">Ikona e aplikacionit / foto profili</div></div>
  <div class="row">
    <div>{inl("rritje-academy-ikona-app.svg", h=64)}<div class="cap">64 px</div></div>
    <div>{inl("rritje-academy-ikona-app.svg", h=32)}<div class="cap">32 px</div></div>
    <div>{inl("rritje-academy-simboli.svg", h=32)}<div class="cap">32 px</div></div>
    <div>{inl("rritje-academy-simboli.svg", h=16)}<div class="cap">16 px</div></div>
  </div>""", h=480)}
<div class="split">
{panel("3 · Një ngjyrë — e zezë", inl("rritje-academy-logo-zi.svg", h=110), bg="#F5F5F0", h=360)}
{panel("3 · Një ngjyrë — e bardhë", inl("rritje-academy-logo-bardhe.svg", h=110), bg="#111111", fg="#9aa", h=360)}
</div>
{panel("Bonus · Versioni negativ me ngjyrat e Rritje Sade", inl("rritje-academy-logo-negativ.svg", h=170), bg="#02464F", fg="#9FC3C0", h=420)}
</body></html>'''
open("prezantimi.html","w").write(html)
