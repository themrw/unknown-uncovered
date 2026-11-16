#!/usr/bin/env python3
"""Themed score + voice mix for a v2 spec. usage: uu_music.py spec.json  -> out/audio.wav
Timeline mirrors uu_render.py (scene length = max(min, voice + lead + tail + extra))."""
import json, os, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly

spec_path = sys.argv[1]; spec = json.load(open(spec_path)); work = os.path.dirname(os.path.abspath(spec_path))
FPS = 30; SR = 48000
durs = json.load(open(os.path.join(work, "vo", "durs.json")))
LEAD, TAIL = spec.get("lead", 0.25), spec.get("tail", 0.35)
D = [round(max(sc.get("min", 3.0), durs[i] + LEAD + TAIL + sc.get("extra", 0.0)) * FPS) / FPS for i, sc in enumerate(spec["scenes"])]
ST = np.cumsum([0] + D).tolist(); T = ST[-1]; n = int(T * SR) + SR
rng = np.random.default_rng(5); t = np.arange(n) / SR
theme = spec.get("theme", "war")

def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
def add(buf, x, t0, g=1.0):
    s = int(t0 * SR)
    if s < 0: x = x[-s:]; s = 0
    if s >= len(buf): return
    e = min(len(buf), s + len(x)); buf[s:e] += x[: e - s] * g
def saw(f, dur, harm=10):
    tt = np.arange(int(dur * SR)) / SR; return sum(np.sin(2 * np.pi * f * k * tt) / k for k in range(1, harm + 1))
def boom(g=1.0, f0=70, dec=4.0, L=2.0):
    tt = np.arange(int(L * SR)) / SR; f = f0 * np.exp(-tt * 2.5) + 30
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * dec) + lp(rng.standard_normal(len(tt)), 900) * np.exp(-tt * 18) * 0.5) * g
def riser(L):
    tt = np.arange(int(L * SR)) / SR; x = rng.standard_normal(len(tt)); out = np.zeros_like(x); seg = int(0.05 * SR)
    for i in range(0, len(x), seg):
        fr = 300 + 5000 * (i / len(x)) ** 2
        out[i:i + seg] = bp(x[i:i + seg + 2000], fr, fr * 1.6)[: len(out[i:i + seg])]
    return out * (tt / L) ** 2 * 0.6

music = np.zeros(n)
# drone bed
drone = (saw(55, T + 1, 8) + saw(55.35, T + 1, 8) * 0.8 + saw(82.4, T + 1, 6) * 0.35)[:n]
drone = lp(drone, 260) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 9) ** 2)
music += drone * 0.05
pad = (np.sin(2 * np.pi * 880 * t) * 0.4 + np.sin(2 * np.pi * 1318.5 * t) * 0.25) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t))
music += lp(pad, 3000) * 0.006

ranks = [i for i, sc in enumerate(spec["scenes"]) if sc["type"] == "rank"]
outro = [i for i, sc in enumerate(spec["scenes"]) if sc["type"] == "outro"]
t_end_beats = ST[outro[0]] if outro else T
# heartbeat, faster as the countdown approaches #1
bt = 0.6
while bt < t_end_beats - 0.5:
    k = sum(1 for i in ranks if ST[i] <= bt)
    bpm = 66 + 6 * k
    add(music, boom(0.55, 60, 9, 0.5), bt); add(music, boom(0.35, 55, 10, 0.4), bt + 0.22)
    bt += 60 / bpm
if theme == "nuclear":
    # Geiger counter: density rises during each hidden phase, spikes before the reveal
    clicks = np.zeros(n); L = int(0.003 * SR); c = hp(rng.standard_normal(L), 2500) * np.hanning(L)
    for i, sc in enumerate(spec["scenes"]):
        base = 1.5 if sc["type"] in ("hook", "tease", "stat") else 3
        rev = sc.get("reveal_at", 1.4) if sc["type"] == "rank" else None
        tt = ST[i]
        while tt < ST[i + 1]:
            loc = tt - ST[i]
            rate = base + (14 * (loc / rev) if rev and loc < rev else 0) + (3 if sc["type"] == "rank" else 0)
            add(clicks, c * rng.uniform(0.4, 1.0), tt); tt += rng.exponential(1 / rate)
    music += clicks * 0.22
def chime(L=2.2, f0=1568.0):
    """Bright metallic clink (gold): inharmonic partials with fast decay."""
    t = np.arange(int(L * SR)) / SR; y = np.zeros_like(t)
    for m, a, d in ((1, 1.0, 3.0), (2.76, 0.5, 4.5), (5.4, 0.25, 6), (8.9, 0.12, 8)):
        y += a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-d * t)
    return y / np.max(np.abs(y))
if theme == "gold":
    reveals = [ST[i] + spec["scenes"][i].get("reveal_at", 1.4) for i in ranks]
    for i, sc in enumerate(spec["scenes"]):
        if sc["type"] == "roll":
            ni = len(sc["items"]); a = sc.get("first_at", 0.5); b = max(a + 0.1, D[i] - sc.get("hold", 1.2))
            reveals += [ST[i] + a + j * (b - a) / max(1, ni - 1) for j in range(ni)]
        if sc.get("twist"):   # the big surprise: a cascade of coins
            for j in range(9):
                add(music, chime(1.6, 1318.5 * 2 ** (j % 5 / 12)), ST[i] + 0.35 + j * 0.07, 0.10)
    for tt in reveals:
        add(music, chime(), tt, 0.16)
# risers + impacts at reveals; whooshes at cuts
for i in ranks:
    rev = spec["scenes"][i].get("reveal_at", 1.4)
    add(music, riser(rev), ST[i], 0.35)
    add(music, boom(1.0, 80, 3.2, 2.5), ST[i] + rev, 0.9)
for i, sc in enumerate(spec["scenes"]):   # short edits: an impact on every roll reveal
    if sc["type"] == "roll":
        ni = len(sc["items"]); a = sc.get("first_at", 0.5); b = max(a + 0.1, D[i] - sc.get("hold", 1.2))
        for j in range(ni):
            tj = ST[i] + (a + j * (b - a) / max(1, ni - 1) if ni > 1 else a)
            add(music, riser(0.5), tj - 0.5, 0.25); add(music, boom(0.9 if j == ni - 1 else 0.6, 80, 3.5, 1.5), tj, 0.8)
for s0 in ST[1:-1]:
    Lw = int(0.45 * SR); tw = np.arange(Lw) / SR
    add(music, bp(rng.standard_normal(Lw), 700, 5000) * np.sin(np.pi * tw / 0.45) ** 2, s0 - 0.3, 0.16)
if outro:   # resolve: warm chord swell
    o = ST[outro[0]]; L = T - o + 1
    ch = sum(saw(f, L, 6) for f in (110, 164.8, 220, 261.6)); tt = np.arange(len(ch)) / SR
    add(music, lp(ch, 1400) * np.minimum(1, tt / 2.0) * np.minimum(1, (L - tt) / 2.5), o, 0.035)
add(music, boom(1.2, 90, 2.5, 3), 0.05, 0.6)
ir = rng.standard_normal(int(1.8 * SR)) * np.exp(-np.arange(int(1.8 * SR)) / SR * 3); ir = lp(ir, 4500)
wet = fftconvolve(music, ir)[:n]; wet *= np.abs(music).max() / (np.abs(wet).max() + 1e-9)
music = music * 0.8 + wet * 0.3
music *= np.clip(np.minimum(t / 0.8, (T - t) / 1.5), 0, 1)
music /= np.abs(music).max() + 1e-9
voice = np.zeros(n)
for i in range(len(spec["scenes"])):
    a, sr = sf.read(os.path.join(work, "vo", f"{i:02d}.wav")); a = resample_poly(a, SR, sr) if sr != SR else a
    add(voice, a, ST[i] + LEAD)
env = np.convolve(np.abs(voice), np.ones(4800) / 4800, mode="same")
duck = 1 - 0.6 * np.clip(env / 0.06, 0, 1)
mix = voice * 1.0 + music * 0.38 * duck
mix = mix[: int(T * SR)]; mix /= np.abs(mix).max() / 0.93
os.makedirs(os.path.join(work, "out"), exist_ok=True)
sf.write(os.path.join(work, "out", "audio.wav"), np.stack([mix, mix], 1), SR)
print("audio", round(T, 2))
