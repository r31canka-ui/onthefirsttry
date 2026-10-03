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

def speech_runs(thr=-40.0, hop=0.02, min_gap=0.12):
    """Speech regions from 20 ms energy; quiet gaps shorter than min_gap are bridged."""
    import soundfile as sf
    x, sr = sf.read(f"{ROOT}/asr/raw16.wav")
    h = int(hop * sr); n = len(x) // h
    db = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    sp = db >= thr
    runs, i = [], 0
    while i < n:
        if sp[i]:
            j = i
            while j < n and sp[j]: j += 1
            if runs and (i - runs[-1][1]) * hop < min_gap: runs[-1][1] = j
            else: runs.append([i, j])
            i = j
        else: i += 1
    return [[a * hop, b * hop] for a, b in runs if (b - a) * hop >= 0.06]
VAD = speech_runs()
OUT_W, OUT_H, FPS = 1080, 1920, 30
SRC_W, SRC_H, SRC_FPS = 480, 854, 24

# ----------------------------------------------------------------------------
# 1. EDL — (source_in, source_out, caption text, flags)
#    "sec": starts a new section -> whoosh + zoom-blur whip transition
#    "pill": show the Instagram follow pill at that caption word index
# ----------------------------------------------------------------------------
EDL = [   # edges sit on measured quiet points (never inside a word)
    dict(a=0.86, b=5.50, sec=True, impact=True,
         text="Do ju listoj 10 arsye se përse ia vlen të merrni pjesë në grupet e dobësimit me Ledjanën.",
         pill="Ledjanën."),
    dict(a=5.70, b=11.86, sec=True,
         text="E para është eksperienca. Unë kam mbi 6 vite që bëj trajnime online, dhe këtë vit bëj 5 vite me grupe dobësimi."),
    dict(a=12.10, b=14.76, sec=True, ding="8", punch=True,
         text="E dyta, humbisni deri në 8 kilogramë brenda muajit."),
    dict(a=17.55, b=24.50, sec=True,
         text="E treta, në grup ju paguani 50% më lirë. Pra çmimet e grupeve janë ekstremisht super ekonomike."),
    dict(a=34.78, b=40.54, sec=True,
         text="Gjithashtu, grupi ndiqet vetëm nga unë, nuk ka staf për trajnimet, por gjithçka e nis dhe e përfundoj vetë."),
    dict(a=42.84, b=48.02, sec=True,
         text="Grupi përbëhet nga një numër i limituar vajzash dhe grash, që të kem mundësi t'i ndjek të gjitha mesazhet."),
    dict(a=51.88, b=57.22, sec=True,
         text="Grupi ka llogaridhënie: çdo ditë ju më dërgoni vaktet me foto, edhe hapat tuaj ditorë."),
    dict(a=75.36, b=82.00, sec=True,
         text="Grupi përfshin seanca stërvitore që mund t'i kryeni në shtëpi ose në palestër, me video të regjistruara, në çdo shtet të botës."),
    dict(a=113.34, b=121.56, sec=True,
         text="Ekziston vetëm një problem me grupet tona të dobësimit: ju vini vetëm për një qëllim, dhe dilni akoma më mirë se sa e kishit menduar."),
    dict(a=121.56, b=125.40, sec=False, final=True,
         text="Brenda më pak se një muaj do ta shihni që grupet tona të dobësimit funksionojnë.",
         pill="funksionojnë."),
]

GAP_KEEP = 0.10      # padding kept on each side of a removed pause
GAP_MIN = 0.30       # only real pauses longer than this are cut

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
    pieces[0][0] = r["a"]
    pieces[-1][1] = r["b"]
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

# zoom plan (matches the references): one steady chest-up framing, a subtle
# ~6% framing shift on each real jump cut, a clear punch-in only on the
# results line, and a slow push-in on the closing line.
ZB, ZJ, ZP = 1.22, 1.30, 1.45
FACE_Y = 380                 # face centre in source px
for i, c in enumerate(clips):
    c["z"] = ZB if i % 2 == 0 else ZJ
    c["push"] = 0.0
    if EDL[c["r"]].get("punch"):
        c["z"] = ZP
    if EDL[c["r"]].get("final"):
        c["z"], c["push"] = ZB, 0.08

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
        pills.append((w["s"], min(sec_end + 0.5, w["s"] + 1.4, TOTAL - 0.05)))

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
        d.rounded_rectangle([0, 0, W - 1, H - 1], radius=H // 2, fill=(236, 236, 236, 205))
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
        return sh.resize((int(sh.width * 1.8), int(sh.height * 1.8)), Image.LANCZOS)

    PILL = make_pill()

    def crop_zoom(img, z, cy):
        vw, vh = SRC_W / z, SRC_H / z
        top = min(max(0, cy - 0.36 * vh), SRC_H - vh)
        left = (SRC_W - vw) / 2
        return img.transform((OUT_W, OUT_H), Image.EXTENT, (left, top, left + vw, top + vh), Image.BICUBIC)

    def ease_out(x):
        return 1 - (1 - x) ** 3

    INTRO = 0.5   # seconds of the opening zoom
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
        if t < INTRO:   # opening zoom-out, as in reference 1 (only at the very start)
            k = ease_out(t / INTRO)
            zz = z * (1.5 - 0.5 * k)
            blur = max(0.0, 1 - t / 0.2)
            samples = [crop_zoom(img, zz * (1 + 0.04 * j * blur), FACE_Y) for j in range(4)]
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
                    o.alpha_composite(p, (OUT_W // 2 - p.width // 2, int(OUT_H * 0.62) - p.height // 2))
                    out = o.convert("RGB")
        enc.stdin.write(out.tobytes())
    enc.stdin.close(); enc.wait()


# ----------------------------------------------------------------------------
# 5. Audio
#    Two passes with static gain. (loudnorm inside a split/sidechain graph
#    swallowed its last 3 s look-ahead buffer -> voice missing at the end.)
# ----------------------------------------------------------------------------
SFX = f"{ROOT}/sfx"
XF = 0.02

def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

def lufs(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])

# pass 1: voice only
fc, vl = [], ""
for i, c in enumerate(clips):
    d = c["b"] - c["a"]
    fc.append(f"[0:a]atrim={c['a']:.3f}:{c['b']:.3f},asetpts=PTS-STARTPTS,aresample=44100,"
              f"afade=t=in:d={XF}:curve=tri,afade=t=out:st={d - XF:.3f}:d={XF}:curve=tri[v{i}]")
    vl += f"[v{i}]"
fc.append(vl + f"concat=n={len(clips)}:v=0:a=1,"
          "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=250:t=q:w=1:g=-1.5,"
          "acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4[o]")
ff("-i", RAW, "-filter_complex", ";".join(fc), "-map", "[o]", "-c:a", "pcm_f32le", f"{HERE}/voice_raw.wav")
g = -12.0 - lufs(f"{HERE}/voice_raw.wav")
ff("-i", f"{HERE}/voice_raw.wav", "-af", f"volume={g:.2f}dB", "-c:a", "pcm_f32le", f"{HERE}/voice.wav")

# SFX events
sfx_events = []  # (file, time, gain_db)
for ri, s in enumerate(sections):
    r = EDL[ri]
    if r.get("impact"):
        sfx_events.append(("impact.wav", 0.0, -13))
        sfx_events.append(("whoosh.wav", 0.0, -18))
    elif r.get("sec"):
        sfx_events.append(("whoosh.wav", max(0, s - 0.26), -20))
for ri, r in enumerate(EDL):
    if r.get("ding"):
        w = [x for x in words if x["r"] == ri and x["w"] == r["ding"]][0]
        sfx_events.append(("ding.wav", w["s"], -20))
for ps, pe in pills:
    sfx_events.append(("pop.wav", ps, -12))

# pass 2: mix (voice + ducked music + sfx), then static gain + limiter
inputs = ["-i", f"{HERE}/voice.wav"]
fc, sl = [], ""
for j, (f, t, gdb) in enumerate(sfx_events):
    inputs += ["-i", f"{SFX}/{f}"]
    fc.append(f"[{j + 1}:a]aresample=44100,volume={gdb}dB,adelay={int(t * 1000)}|{int(t * 1000)},apad=whole_dur={TOTAL:.3f}[s{j}]")
    sl += f"[s{j}]"
mi = len(sfx_events) + 1
inputs += ["-i", f"{SFX}/music.wav"]
fc.append(f"[{mi}:a]atrim=0:{TOTAL:.3f},volume=-27dB,afade=t=in:d=0.4,afade=t=out:st={TOTAL - 1.0:.2f}:d=1.0[mus]")
fc.append(f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={TOTAL:.3f},asplit=2[vo][vsc]")
fc.append("[mus][vsc]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=350[musd]")
fc.append(f"[vo][musd]{sl}amix=inputs={2 + len(sfx_events)}:normalize=0:duration=longest,atrim=0:{TOTAL:.3f}[aout]")
open(f"{HERE}/audio_graph.txt", "w").write(";\n".join(fc))
ff(*inputs, "-filter_complex", ";".join(fc), "-map", "[aout]", "-c:a", "pcm_f32le", f"{HERE}/mix_raw.wav")
g2 = -10.0 - lufs(f"{HERE}/mix_raw.wav")
ff("-i", f"{HERE}/mix_raw.wav", "-af", f"volume={g2:.2f}dB,alimiter=limit=0.79:attack=3:release=60:level=disabled",
   "-ar", "44100", "-c:a", "pcm_s16le", f"{HERE}/audio.wav")

# ----------------------------------------------------------------------------
# 6. Burn captions + mux
# ----------------------------------------------------------------------------
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{HERE}/video_noaudio.mp4", "-i", f"{HERE}/audio.wav",
                "-vf", f"unsharp=5:5:0.5:5:5:0.0,ass={HERE}/captions.ass:fontsdir={ROOT}/fonts/ttf",
                "-c:v", "libx264", "-preset", "slow", "-maxrate", "5M", "-bufsize", "10M", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
                f"{HERE}/final.mp4"], check=True)
print("done", TOTAL)
