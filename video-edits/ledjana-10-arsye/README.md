# Ledjana – "10 arsye" short (edited)

`ledjana-10-arsye-final.mp4`: 1080×1920, 30 fps, **55.4 s**, about −11 LUFS.
Cut from a 2:09 raw take, styled after the two reference edits.

## What the references do, and how this edit copies it

| Pattern in references | Applied here |
|---|---|
| Jump cuts only at real pauses, never mid-word | Every cut edge sits on a measured quiet point. 9 cuts across 55 s |
| Steady chest-up framing, only a subtle shift at each jump cut | 1.22× base framing with a ~6% shift on each cut. One clear punch-in on the "8 kg" line, slow push-in on the closing line |
| Zoom-in only on the opening | 0.5 s zoom-out at the very start, hard cuts after that |
| Captions: rounded sans (Quicksand), golden yellow, centred mid-frame, 1–3 words, quick fade | Same font, colour `#ECC400`, centred at 50 %, max 3 words / 15 chars, 70 ms fade in / 170 ms fade out |
| Instagram "Follow" pill when the brand is named | Pops in on "Ledjanën" and again on the last word |
| Whoosh on transitions, pops on graphics, music bed far under the voice | Soft whoosh on section changes, pop on the pill, light impact on the hook, ding on "8", music bed about 15 dB under the voice with sidechain ducking. Two-pass static-gain mix, so the voice runs right to the last word |

## Structure (55 s)
1. Hook: "Do ju listoj 10 arsye…"
2. Experience (6+ years online, 5 years of groups)
3. Results: up to 8 kg in a month
4. Price: 50% cheaper, very affordable
5. Coached only by her, no staff
6. Limited spots, so she can answer every message
7. Accountability: daily meal photos and steps
8. Workouts at home or in the gym, recorded, from anywhere
9. Close: "only one problem…", "within less than a month you'll see the groups work" (ends on "funksionojnë")

Cut entirely: the "it depends how much you want it" qualifier, the meal-plan section (the audio was unclear), weekly weigh-ins, Q&A, weekly topics, postpartum, analyses, and every restart or pause.

## ⚠️ Proofread before posting
The audio is Gheg-accented Albanian, and only a small offline speech model was available, so the captions are my reconstruction. Lines to check carefully:
- **"mbi 6 vite"** (years of online training). Could be a different number.
- **"deri në 8 kilogramë brenda muajit"**. Could be 10.
- **"50% më lirë"**. The percentage is uncertain.
- **"Grupi ka llogaridhënie"** and **"edhe hapat tuaj ditorë"**
- Closing: **"ju vini vetëm për një qëllim … se sa e kishit menduar"** and **"Brenda më pak se një muaj do ta shihni…"**

The phrase after "funksionojnë" in the raw take was too unclear to caption, so the video ends there.

Captions live in `captions.ass`. Fix the text there or in the `EDL` in `tools/edit.py`, then re-run to re-render.

## Rebuild
`tools/edit.py` (needs ffmpeg with libass, Python with numpy and Pillow, and the Quicksand Medium TTF). `tools/make_sfx.py` synthesizes the whoosh, pop, impact and ding SFX and the music bed. No stock assets were available offline. Swap in your own licensed music or SFX for a more polished sound.
