import numpy as np
from scipy.signal import butter, sosfilt, lfilter
from scipy.io import wavfile
SR = 44100
rng = np.random.default_rng(7)

def save(name, x):
    x = np.atleast_2d(x)
    if x.shape[0] == 1: x = np.vstack([x, x])
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    wavfile.write(name, SR, (x.T * 32767).astype(np.int16))

def bp_sweep(noise, f0, f1, q=1.2, block=256):
    out = np.zeros_like(noise); zi = None
    n = len(noise); freqs = np.geomspace(f0, f1, n // block + 1)
    for i, f in enumerate(freqs):
        s = slice(i * block, min(n, (i + 1) * block))
        if s.start >= n: break
        lo, hi = f / (2 ** (1 / (2 * q))), f * (2 ** (1 / (2 * q)))
        sos = butter(2, [lo, min(hi, SR / 2 - 100)], btype='band', fs=SR, output='sos')
        if zi is None: zi = np.zeros((sos.shape[0], 2))
        out[s], zi = sosfilt(sos, noise[s], zi=zi)
    return out

def whoosh(dur=0.42, f0=350, f1=5000, peak=0.62):
    n = int(SR * dur); t = np.linspace(0, 1, n)
    env = np.where(t < peak, (t / peak) ** 2.2, ((1 - t) / (1 - peak)) ** 1.6)
    l = bp_sweep(rng.standard_normal(n), f0, f1) * env
    r = bp_sweep(rng.standard_normal(n), f0 * 1.05, f1 * 0.95) * env
    pan = np.linspace(-0.6, 0.6, n)
    return np.vstack([l * (1 - pan) / 2 * 2, r * (1 + pan) / 2 * 2])

def pop(dur=0.09, f0=1100, f1=280):
    n = int(SR * dur); t = np.arange(n) / SR
    f = np.geomspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 55) * np.minimum(1, t * SR / 40)
    return np.sin(ph) * env

def impact(dur=0.9):
    n = int(SR * dur); t = np.arange(n) / SR
    f = 38 + 70 * np.exp(-t * 18); ph = 2 * np.pi * np.cumsum(f) / SR
    boom = np.sin(ph) * np.exp(-t * 5.5)
    sos = butter(2, 2500, 'low', fs=SR, output='sos')
    burst = sosfilt(sos, rng.standard_normal(n)) * np.exp(-t * 28) * 0.5
    return boom + burst

def ding(dur=0.9, f=1760):
    n = int(SR * dur); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d) for m, a, d in [(1, 1, 5), (2.01, .35, 8), (3.02, .15, 12)])
    return x * np.minimum(1, t * SR / 60)

save('whoosh.wav', whoosh())
save('whoosh_short.wav', whoosh(0.28, 600, 6500, 0.55))
save('pop.wav', pop())
save('impact.wav', impact())
save('ding.wav', ding())

# ---------- music bed: warm, light pop groove, 104 BPM ----------
BPM = 104; beat = 60 / BPM; DUR = 70
N = int(SR * DUR); t = np.arange(N) / SR
mix = np.zeros((2, N))
def add(sig, start, ch_gain=(1, 1)):
    i = int(start * SR); j = min(N, i + len(sig))
    if i >= N: return
    mix[0, i:j] += sig[:j - i] * ch_gain[0]; mix[1, i:j] += sig[:j - i] * ch_gain[1]
nt = lambda m: 440 * 2 ** ((m - 69) / 12)
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]   # Am F C G
bars = int(DUR / (4 * beat)) + 1
for b in range(bars):
    ch = prog[b % 4]; st = b * 4 * beat; L = 4 * beat
    n = int(L * SR); tt = np.arange(n) / SR
    env = np.minimum(1, tt / 0.25) * np.minimum(1, (L - tt) / 0.3)
    pad = sum(np.sin(2 * np.pi * nt(m) * tt + np.sin(2 * np.pi * 0.3 * tt) * 0.3) +
              0.3 * np.sin(2 * np.pi * nt(m) * 2.003 * tt) for m in ch) * env * 0.12
    add(pad, st, (0.9, 1.0))
    # plucked arp on 8ths
    for k in range(8):
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
        nn = int(0.4 * SR); t2 = np.arange(nn) / SR
        pl = (np.sin(2 * np.pi * nt(m) * t2) + 0.25 * np.sin(4 * np.pi * nt(m) * t2)) * np.exp(-t2 * 9) * 0.10
        add(pl, st + k * beat / 2, (1.0, 0.7) if k % 2 else (0.7, 1.0))
    # bass
    for k in range(4):
        nn = int(beat * 0.9 * SR); t2 = np.arange(nn) / SR
        bs = np.sin(2 * np.pi * nt(ch[0] - 24) * t2) * np.minimum(1, t2 / 0.01) * np.exp(-t2 * 2.5) * 0.35
        add(bs, st + k * beat)
    # drums
    for k in range(4):
        kt = np.arange(int(0.3 * SR)) / SR
        kick = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-kt * 35)) / SR) * np.exp(-kt * 11) * 0.55
        if k in (0, 2): add(kick, st + k * beat)
        if k in (1, 3):
            sn = sosfilt(butter(2, [1500, 7000], 'band', fs=SR, output='sos'), rng.standard_normal(int(0.2 * SR))) * np.exp(-np.arange(int(0.2 * SR)) / SR * 22) * 0.22
            add(sn, st + k * beat)
        for h in range(2):
            hh = sosfilt(butter(2, 8000, 'high', fs=SR, output='sos'), rng.standard_normal(int(0.05 * SR))) * np.exp(-np.arange(int(0.05 * SR)) / SR * 80) * 0.08
            add(hh, st + k * beat + h * beat / 2, (0.8, 1.0))
# gentle master lowpass for warmth
mix = sosfilt(butter(2, 9000, 'low', fs=SR, output='sos'), mix, axis=1)
save('music.wav', mix)
print('ok')
