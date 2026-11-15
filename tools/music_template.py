import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
sys.argv = ["x", "none"]
import render3 as R

SR = 48000
STARTS = R.STARTS; T = STARTS[-1]; n = int(T * SR) + SR
rng = np.random.default_rng(3)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def add(buf, x, t0, g=1.0):
    s = int(t0 * SR)
    if s >= len(buf): return
    e = min(len(buf), s + len(x)); buf[s:e] += x[: e - s] * g

def snare(v=1.0):
    L = int(0.25 * SR); t = np.arange(L) / SR
    return (bp(rng.standard_normal(L), 1500, 7000) * np.exp(-t * 28) * 0.9 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35) * 0.5) * v
def taiko(v=1.0, f0=95):
    L = int(1.4 * SR); t = np.arange(L) / SR
    f = f0 * np.exp(-t * 3) + 42; ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 4.5) + lp(rng.standard_normal(L), 400) * np.exp(-t * 30) * 0.6) * v
def saw(freq, dur, harm=14):
    t = np.arange(int(dur * SR)) / SR; x = np.zeros_like(t)
    for k in range(1, harm + 1): x += np.sin(2 * np.pi * freq * k * t * (1 + 0.0015 * rng.standard_normal())) / k
    return x

BPM = 92; B = 60 / BPM; BAR = 4 * B
nbars = int(T / BAR) + 1
note = lambda m: 440 * 2 ** ((m - 69) / 12)
prog = [(45, [57, 60, 64]), (41, [53, 57, 60]), (38, [50, 53, 57]), (40, [52, 56, 59])]  # Am F Dm E
t_global, t_burden, t_outro = STARTS[1], STARTS[10], STARTS[11]

drums = np.zeros(n); brass = np.zeros(n); ost = np.zeros(n)
snare_pat = [1, 0, .6, .5, 1, 0, .6, 0, 1, 0, .6, .5, .8, .5, .7, .9]
for b in range(nbars):
    t0 = b * BAR
    root, chord = prog[b % 4]
    section = "intro" if t0 < t_global else "burden" if t_burden <= t0 < t_outro else "main"
    # brass pad
    pad = sum(saw(note(m), BAR + 0.4) for m in chord) * 0.5 + saw(note(root), BAR + 0.4) * 0.8
    tt = np.arange(len(pad)) / SR
    env = np.minimum(1, tt / 0.35) * np.minimum(1, (BAR + 0.4 - tt) / 0.4)
    add(brass, lp(pad * env, 700 if section == "intro" else 1100), t0, 0.06)
    # taiko
    add(drums, taiko(1.0), t0, 0.9)
    if section != "intro": add(drums, taiko(0.6, 80), t0 + 2 * B, 0.8)
    if section == "main" and b % 2 == 1: add(drums, taiko(0.5, 110), t0 + 3.5 * B, 0.7)
    # snare
    if section in ("main",) or (section == "intro" and t0 > t_global - BAR * 1.1):
        for k, v in enumerate(snare_pat):
            if v: add(drums, snare(v * (0.8 + 0.2 * rng.random())), t0 + k * B / 4, 0.33)
    if section == "burden":
        for k in (0, 8): add(drums, snare(0.5), t0 + k * B / 4, 0.25)
    # ostinato 8ths on root
    if section != "intro":
        for k in range(8):
            x = saw(note(root + 12), B / 2 * 0.9, 8); tt = np.arange(len(x)) / SR
            add(ost, lp(x * np.exp(-tt * 9), 900), t0 + k * B / 2, 0.11 * (1.0 if k % 2 == 0 else 0.7))
# snare roll + swell into outro, final hit
L = int(BAR * SR); ramp = np.linspace(0, 1, L) ** 2
for k in range(64):
    add(drums, snare(ramp[min(L - 1, int(k / 64 * L))]), t_outro - BAR + k * BAR / 64, 0.3)
add(drums, bp(rng.standard_normal(L), 3000, 12000) * ramp * 0.25, t_outro - BAR)
end = T - 3.2
add(drums, taiko(1.6, 70), end, 1.0)
music = drums + brass + ost
# simple hall reverb
irL = int(1.6 * SR); ir = rng.standard_normal(irL) * np.exp(-np.arange(irL) / SR * 3.2); ir = lp(ir, 5000)
wet = fftconvolve(music, ir)[:n]; wet /= np.abs(wet).max() / max(1e-9, np.abs(music).max())
music = music * 0.8 + wet * 0.28
t = np.arange(n) / SR
music *= np.clip(np.minimum(t / 1.0, (T - t) / 2.5), 0, 1)
# transition whooshes
for s0 in STARTS[1:-1]:
    Lw = int(0.5 * SR); tw = np.arange(Lw) / SR
    w = bp(rng.standard_normal(Lw), 800, 6000) * np.sin(np.pi * tw / 0.5) ** 2
    add(music, w, s0 - 0.35, 0.18)
music /= np.abs(music).max()
# voice
voice = np.zeros(n)
for i, s0 in enumerate(STARTS[:-1]):
    a, sr = sf.read(f"/home/claude/tts/vo_{i:02d}.wav"); a = resample_poly(a, SR, sr)
    add(voice, a, s0 + R.LEAD)
env = np.convolve(np.abs(voice), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.55 * np.clip(env / 0.08, 0, 1)
mix = voice * 1.0 + music * 0.42 * duck
mix = mix[: int(T * SR)]; mix /= np.abs(mix).max() / 0.92
sf.write("out3/audio.wav", np.stack([mix, mix], 1), SR)
print("ok", round(T, 2))
