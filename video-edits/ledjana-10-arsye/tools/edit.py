"""Short-form edit of raw.mp4 in the style of the two reference videos.

Pipeline:
  1. EDL: source ranges (picked by hand from the transcript) + caption text.
  2. Internal pauses inside each range are cut out -> list of clips.
  3. Video: every frame rendered in Python (punch-ins alternating per cut,
     zoom-blur whip on section changes), piped to ffmpeg.
  4. Captions: ASS file (Quicksand Medium, golden yellow, centred, 1-3 words,
     soft fade) burned in with libass.
  5. Audio: voice clips crossfaded, EQ/compression, music bed under voice,
     whoosh / pop / impact / ding SFX at cut points, loudness to ~-9 LUFS.
"""
import json, subprocess, os, math, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = f"{ROOT}/raw.mp4"
VAD = json.load(open(f"{ROOT}/asr/raw.vad.json"))
OUT_W, OUT_H, FPS = 1080, 1920, 30
SRC_W, SRC_H, SRC_FPS = 480, 854, 24

# ----------------------------------------------------------------------------
# 1. EDL — (source_in, source_out, caption text, flags)
#    "sec": starts a new section -> whoosh + zoom-blur whip transition
#    "pill": show the Instagram follow pill at that caption word index
# ----------------------------------------------------------------------------
EDL = [
    dict(a=0.88, b=5.10, sec=True, impact=True,
         text="Do ju listoj 10 arsye se përse ia vlen të merrni pjesë në grupet e dobësimit me Ledjanën.",
         pill="Ledjanën."),
    dict(a=5.70, b=11.90, sec=True,
         text="E para është eksperienca. Unë kam mbi 6 vite që bëj trajnime online, dhe këtë vit bëj 5 vite me grupe dobësimi."),
    dict(a=12.14, b=14.72, sec=True, ding="8",
         text="E dyta, humbisni deri në 8 kilogramë brenda muajit."),
    dict(a=17.58, b=24.56, sec=True,
         text="E treta, në grup ju paguani 50% më lirë. Pra çmimet e grupeve janë ekstremisht super ekonomike."),
    dict(a=34.80, b=40.56, sec=True,
         text="Gjithashtu, grupi ndiqet vetëm nga unë, nuk ka staf për trajnimet, por gjithçka e nis dhe e përfundoj vetë."),
    dict(a=42.92, b=47.96, sec=True,
         text="Grupi përbëhet nga një numër i limituar vajzash dhe grash, që të kem mundësi t'i ndjek të gjitha mesazhet."),
    dict(a=51.90, b=57.19, sec=True,
         text="Grupi ka llogaridhënie: çdo ditë ju më dërgoni vaktet me foto, edhe hapat tuaj ditorë."),
    dict(a=75.39, b=81.60, sec=True,
         text="Grupi përfshin seanca stërvitore që mund t'i kryeni në shtëpi ose në palestër, me video të regjistruara, në çdo shtet të botës."),
    dict(a=113.34, b=121.54, sec=True,
         text="Ekziston vetëm një problem me grupet tona të dobësimit: ju vini vetëm për një qëllim, dhe dilni akoma më mirë se sa e kishit menduar."),
    dict(a=121.57, b=127.50, sec=False, final=True,
         text="Brenda një muaji do ta shihni që grupet tona të dobësimit funksionojnë, dhe do doni të bëheni pjesë e jona përjetë.",
         pill="përjetë."),
]

GAP_KEEP = 0.07      # padding kept on each side of a removed pause
GAP_MIN = 0.22       # pauses longer than this are cut

# ----------------------------------------------------------------------------
# 2. Build clips (src in/out) and word timings
# ----------------------------------------------------------------------------
def islands(a, b):
    out = []
    for s, e in VAD:
        s2, e2 = max(s, a), min(e, b)
        if e2 - s2 > 0.05:
            out.append([s2, e2])
    return out

def syl_weight(w):
    w = re.sub(r"[^\wëçË%]", "", w.lower())
    v = len(re.findall(r"[aeiouyë]", w))
    if "%" in w or w.isdigit():
        v = {"10": 2, "6": 2, "5": 2, "8": 2, "50": 4}.get(w.strip("%"), 2) + ("%" in w) * 3
    return max(1, v) + 0.15 * len(w)

clips, words, sections = [], [], []
t_out = 0.0
for ri, r in enumerate(EDL):
    isl = islands(r["a"], r["b"])
    # pieces: merge islands separated by short gaps
    pieces = []
    for s, e in isl:
        if pieces and s - pieces[-1][1] <= GAP_MIN:
            pieces[-1][1] = e
        else:
            pieces.append([s, e])
    pieces[0][0] = max(r["a"], pieces[0][0] - GAP_KEEP)
    pieces[-1][1] = min(r["b"], pieces[-1][1] + GAP_KEEP)
    for p in pieces[1:]:
        p[0] -= GAP_KEEP
    for p in pieces[:-1]:
        p[1] += GAP_KEEP
    sections.append(t_out)
    # word timing: distribute words across speech islands by syllable weight
    toks = r["text"].split()
    wts = np.array([syl_weight(w) for w in toks])
    speech = [(s, e) for s, e in isl]
    tot_sp = sum(e - s for s, e in speech)
    cum = np.concatenate([[0], np.cumsum(wts)]) / wts.sum() * tot_sp

    def sp2src(x):  # speech-time -> source-time
        for s, e in speech:
            if x <= e - s + 1e-6:
                return s + x
            x -= e - s
        return speech[-1][1]

    def src2out(x):
        acc = t_out
        for p in pieces:
            if x <= p[1]:
                return acc + max(0, x - p[0])
            acc += p[1] - p[0]
        return acc

    for i, w in enumerate(toks):
        s = src2out(sp2src(cum[i] + 1e-4))
        e = src2out(sp2src(cum[i + 1] - 1e-4))
        words.append(dict(w=w, s=s, e=e, r=ri))
    for pi, p in enumerate(pieces):
        clips.append(dict(a=p[0], b=p[1], t=t_out, r=ri, first=(pi == 0)))
        t_out += p[1] - p[0]
TOTAL = t_out
print(f"total {TOTAL:.2f}s, {len(clips)} clips")

# zoom plan: split long clips into framing beats (no source jump), then
# alternate wide / punch-in on every cut or beat, like the references
ZW, ZT = 1.18, 1.55          # wide / tight
FACE_Y = 380                 # face centre in source px
SENT_BREAKS = [w["e"] for w in words if re.search(r"[.,:]$", w["w"])]
beats = []
for c in clips:
    dur = c["b"] - c["a"]
    cuts = [c["t"]]
    if dur > 3.0:
        cands = [x for x in SENT_BREAKS + [w["s"] for w in words] if c["t"] + 1.2 < x < c["t"] + dur - 1.2]
        n = int(dur // 2.6)
        for k in range(1, n + 1):
            target = c["t"] + dur * k / (n + 1)
            if cands:
                best = min(cands, key=lambda x: abs(x - target) - (0.4 if x in SENT_BREAKS else 0))
                if all(abs(best - y) > 1.0 for y in cuts):
                    cuts.append(best)
    cuts.sort()
    for j, ct in enumerate(cuts):
        end = cuts[j + 1] if j + 1 < len(cuts) else c["t"] + dur
        beats.append(dict(c, a=c["a"] + (ct - c["t"]), b=c["a"] + (end - c["t"]), t=ct, first=c["first"] and j == 0))
clips = beats
for i, c in enumerate(clips):
    c["z"] = ZW if i % 2 == 0 else ZT
    c["push"] = 0.0
for c in clips:
    if EDL[c["r"]].get("ding") or EDL[c["r"]].get("final"):
        c["push"] = 0.06
print(len(clips), "beats")

# ----------------------------------------------------------------------------
# 3. Captions (ASS)
# ----------------------------------------------------------------------------
def chunk_words(ws):
    groups, cur = [], []
    for w in ws:
        txt = " ".join(x["w"] for x in cur + [w])
        if cur and (len(txt) > 15 or len(cur) >= 3 or w["r"] != cur[-1]["r"]):
            groups.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.,:]$", w["w"]):
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    return groups

def ass_t(x):
    x = max(0, x)
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

groups = chunk_words(words)
lines = []
for gi, g in enumerate(groups):
    s = g[0]["s"] - 0.04
    nxt = groups[gi + 1][0]["s"] - 0.04 if gi + 1 < len(groups) else TOTAL
    e = min(nxt, g[-1]["e"] + 0.30)
    txt = " ".join(x["w"] for x in g).rstrip(",:")
    txt = re.sub(r"(?<!\d)\.$", "", txt)
    lines.append((s, e, txt))

ASS = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {OUT_W}
PlayResY: {OUT_H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Quicksand Light Medium,66,&H0000C4EC,&H0000C4EC,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for s, e, txt in lines:
    ASS += f"Dialogue: 0,{ass_t(s)},{ass_t(e)},Cap,,0,0,0,,{{\\pos({OUT_W//2},{int(OUT_H*0.50)})\\fad(70,170)\\blur0.6}}{txt}\n"
open(f"{HERE}/captions.ass", "w").write(ASS)
json.dump(dict(lines=lines, clips=clips, total=TOTAL), open(f"{HERE}/plan.json", "w"), ensure_ascii=False, indent=1)

# follow-pill events (time ranges)
pills = []
for r_i, r in enumerate(EDL):
    if r.get("pill"):
        w = [x for x in words if x["r"] == r_i and x["w"] == r["pill"]][0]
        sec_end = sections[r_i + 1] if r_i + 1 < len(sections) else TOTAL
        pills.append((w["s"], min(sec_end - 0.05, w["s"] + 1.6)))

# ----------------------------------------------------------------------------
# 4. Video render
# ----------------------------------------------------------------------------
ONLY_AUDIO = os.environ.get('ONLY_AUDIO') == '1'
if not ONLY_AUDIO:
    def load_frames():
        cmd = ["ffmpeg", "-v", "error", "-i", RAW, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        raw = subprocess.run(cmd, capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.uint8).reshape(-1, SRC_H, SRC_W, 3)

    FR = load_frames()
    print("frames", FR.shape)

    def make_pill():
        s = 3  # supersample
        W, H = 300 * s, 84 * s
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, W - 1, H - 1], radius=H // 2, fill=(255, 255, 255, 245))
        # gradient app-icon square
        ic = 60 * s
        grad = Image.new("RGBA", (ic, ic))
        gp = grad.load()
        for y in range(ic):
            for x in range(ic):
                k = (x + (ic - y)) / (2 * ic)
                c0, c1, c2 = np.array([254, 218, 117]), np.array([214, 41, 118]), np.array([79, 91, 213])
                c = c0 + (c1 - c0) * min(1, k * 2) if k < .5 else c1 + (c2 - c1) * (k - .5) * 2
                gp[x, y] = (*[int(v) for v in c], 255)
        mask = Image.new("L", (ic, ic), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, ic - 1, ic - 1], radius=16 * s, fill=255)
        im.paste(grad, (12 * s, 12 * s), mask)
        d = ImageDraw.Draw(im)
        cx, cy = 12 * s + ic // 2, 12 * s + ic // 2
        d.rounded_rectangle([cx - 19 * s, cy - 19 * s, cx + 19 * s, cy + 19 * s], radius=11 * s, outline="white", width=4 * s)
        d.ellipse([cx - 9 * s, cy - 9 * s, cx + 9 * s, cy + 9 * s], outline="white", width=4 * s)
        d.ellipse([cx + 10 * s, cy - 15 * s, cx + 15 * s, cy - 10 * s], fill="white")
        f = ImageFont.truetype(f"{ROOT}/fonts/l600.ttf", 40 * s)
        d.text((92 * s, H // 2), "Follow", font=f, fill=(20, 20, 20), anchor="lm")
        im = im.resize((W // s, H // s), Image.LANCZOS)
        sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 90), (20, 26), im.split()[3])
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        sh.alpha_composite(im, (20, 20))
        return sh.resize((int(sh.width * 1.35), int(sh.height * 1.35)), Image.LANCZOS)

    PILL = make_pill()

    def crop_zoom(img, z, cy):
        vw, vh = SRC_W / z, SRC_H / z
        top = min(max(0, cy - 0.36 * vh), SRC_H - vh)
        left = (SRC_W - vw) / 2
        return img.transform((OUT_W, OUT_H), Image.EXTENT, (left, top, left + vw, top + vh), Image.BICUBIC)

    def ease_out(x):
        return 1 - (1 - x) ** 3

    WHIP = 0.22   # seconds of zoom-blur at a section start
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                            f"{HERE}/video_noaudio.mp4"], stdin=subprocess.PIPE)
    nfr = int(math.ceil(TOTAL * FPS))
    ci = 0
    for n in range(nfr):
        t = n / FPS
        while ci + 1 < len(clips) and clips[ci + 1]["t"] <= t:
            ci += 1
        c = clips[ci]
        lt = t - c["t"]
        src_t = c["a"] + lt
        fi = min(len(FR) - 1, int(src_t * SRC_FPS + 0.5))
        img = Image.fromarray(FR[fi])
        dur = c["b"] - c["a"]
        z = c["z"] * (1 + c["push"] * min(1, lt / max(dur, 0.01)))
        sec_start = c["first"] and (EDL[c["r"]].get("sec"))
        if sec_start and lt < WHIP:
            k = ease_out(lt / WHIP)
            zz = z * (1.45 - 0.45 * k)
            samples = [crop_zoom(img, zz * (1 + 0.05 * j * (1 - k)), FACE_Y) for j in range(4)]
            arr = np.mean([np.asarray(s, dtype=np.float32) for s in samples], axis=0)
            out = Image.fromarray(arr.astype(np.uint8))
        else:
            out = crop_zoom(img, z, FACE_Y)
        for ps, pe in pills:
            if ps <= t < pe:
                u = t - ps
                sc = min(1, ease_out(min(1, u / 0.18)) * 1.08) if u < 0.25 else 1.0
                if pe - t < 0.15:
                    sc = (pe - t) / 0.15
                if sc > 0.02:
                    p = PILL.resize((max(1, int(PILL.width * sc)), max(1, int(PILL.height * sc))), Image.LANCZOS)
                    o = out.convert("RGBA")
                    o.alpha_composite(p, (OUT_W // 2 - p.width // 2, int(OUT_H * 0.585) - p.height // 2))
                    out = o.convert("RGB")
        enc.stdin.write(out.tobytes())
    enc.stdin.close(); enc.wait()


# ----------------------------------------------------------------------------
# 5. Audio
# ----------------------------------------------------------------------------
SFX = f"{ROOT}/sfx"
inputs = ["-i", RAW]
fc = []
vlabels = []
XF = 0.012
aclips = []  # merge framing-only beats back into continuous audio
for c in clips:
    if aclips and abs(aclips[-1]["b"] - c["a"]) < 1e-6:
        aclips[-1] = dict(aclips[-1], b=c["b"])
    else:
        aclips.append(dict(c))
for i, c in enumerate(aclips):
    d = c["b"] - c["a"]
    fc.append(f"[0:a]atrim={c['a']:.3f}:{c['b']:.3f},asetpts=PTS-STARTPTS,aresample=44100,"
              f"afade=t=in:d={XF}:curve=tri,afade=t=out:st={d - XF:.3f}:d={XF}:curve=tri[v{i}]")
    vlabels.append(f"[v{i}]")
fc.append("".join(vlabels) + f"concat=n={len(aclips)}:v=0:a=1,"
          "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=250:t=q:w=1:g=-1.5,"
          "acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4,"
          "loudnorm=I=-11:TP=-1.5:LRA=7[voice]")

sfx_events = []  # (file, time, gain_db)
for ri, s in enumerate(sections):
    r = EDL[ri]
    if r.get("impact"):
        sfx_events.append(("impact.wav", 0.0, -9))
        sfx_events.append(("whoosh.wav", 0.0, -14))
    elif r.get("sec"):
        sfx_events.append(("whoosh.wav", max(0, s - 0.24), -13))
for ri, r in enumerate(EDL):
    if r.get("ding"):
        w = [x for x in words if x["r"] == ri and x["w"] == r["ding"]][0]
        sfx_events.append(("ding.wav", w["s"], -20))
for ps, pe in pills:
    sfx_events.append(("pop.wav", ps, -12))
    sfx_events.append(("pop.wav", pe - 0.12, -20))
sfx_events.append(("whoosh_short.wav", TOTAL - 0.35, -16))
# subtle pop on the non-section punch-ins (every 3rd cut) like the reference tick sounds
for i, c in enumerate(clips):
    if not c["first"] and i % 3 == 0:
        sfx_events.append(("whoosh_short.wav", max(0, c["t"] - 0.12), -24))

slabels = []
for j, (f, t, g) in enumerate(sfx_events):
    inputs += ["-i", f"{SFX}/{f}"]
    k = j + 1
    fc.append(f"[{k}:a]aresample=44100,volume={g}dB,adelay={int(t * 1000)}|{int(t * 1000)},apad=whole_dur={TOTAL:.3f}[s{j}]")
    slabels.append(f"[s{j}]")
mi = len(sfx_events) + 1
inputs += ["-i", f"{SFX}/music.wav"]
fc.append(f"[{mi}:a]atrim=0:{TOTAL + 0.5:.2f},volume=-27dB,afade=t=in:d=0.4,afade=t=out:st={TOTAL - 1.2:.2f}:d=1.2[mus]")
fc.append(f"[voice]asplit=2[vo][vsc]")
fc.append(f"[vsc]apad=whole_dur={TOTAL:.3f}[vsc2];[mus][vsc2]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=350[musd]")
fc.append("[vo][musd]" + "".join(slabels) +
          f"amix=inputs={2 + len(slabels)}:normalize=0:duration=longest,"
          f"loudnorm=I=-9.5:TP=-1.0:LRA=8,atrim=0:{TOTAL:.3f}[aout]")
open(f"{HERE}/audio_graph.txt", "w").write(";\n".join(fc))
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
                "-map", "[aout]", "-ar", "44100", "-c:a", "pcm_s16le", f"{HERE}/audio.wav"], check=True)

# ----------------------------------------------------------------------------
# 6. Burn captions + mux
# ----------------------------------------------------------------------------
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{HERE}/video_noaudio.mp4", "-i", f"{HERE}/audio.wav",
                "-vf", f"unsharp=5:5:0.5:5:5:0.0,ass={HERE}/captions.ass:fontsdir={ROOT}/fonts/ttf",
                "-c:v", "libx264", "-preset", "slow", "-maxrate", "5M", "-bufsize", "10M", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
                f"{HERE}/final.mp4"], check=True)
print("done", TOTAL)
