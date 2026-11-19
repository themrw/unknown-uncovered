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
def chime(L=2.2, f0=1568.0):
    """Bright metallic clink (gold): inharmonic partials with fast decay."""
    t = np.arange(int(L * SR)) / SR; y = np.zeros_like(t)
    for m, a, d in ((1, 1.0, 3.0), (2.76, 0.5, 4.5), (5.4, 0.25, 6), (8.9, 0.12, 8)):
        y += a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-d * t)
    return y / np.max(np.abs(y))
film = any(sc["type"] == "toon" for sc in spec["scenes"])
def pluck(f, L=1.6, bright=1.0):
    """Plucked string (sitar/tanpura-like): harmonics with faster decay up the series, a little jawari buzz."""
    tt = np.arange(int(L * SR)) / SR; y = np.zeros_like(tt)
    for k in range(1, 12):
        y += np.sin(2 * np.pi * f * k * (1 + 0.0007 * k) * tt) * (0.9 ** k) * np.exp(-tt * (1.2 + 0.9 * k / bright))
    return y * np.minimum(1, tt / 0.004) / 3
if film:   # proud period-film score: tanpura drone, sitar-like phrases, brass swells on the big moments
    music *= 0.4
    sa = 130.81; tan = [sa * 1.5, sa * 2, sa * 2, sa]; tt = 0.2; j = 0
    while tt < T:
        add(music, pluck(tan[j % 4], 2.6, 0.6), tt, 0.10); tt += 1.15; j += 1
    scale = [1, 9 / 8, 5 / 4, 4 / 3, 3 / 2, 5 / 3, 15 / 8, 2]
    phr = [[0, 2, 4, 5, 4], [4, 5, 7, 5, 4, 2], [2, 4, 2, 1, 0], [4, 4, 5, 4, 2, 1, 2], [7, 5, 4, 5, 4, 2, 0]]
    mood = {"river": 0.35, "teagarden": 0.45, "measure": 0.6, "office": 0.6}
    for i, sc in enumerate(spec["scenes"]):
        g = mood.get(sc.get("set"), 1.0); tt = ST[i] + 0.4; p = i
        while tt < ST[i + 1] - 1.0:
            for k, nidx in enumerate(phr[p % len(phr)]):
                add(music, pluck(sa * 2 * scale[nidx] * (0.5 if sc.get("set") in ("river", "teagarden") else 1), 1.4), tt, 0.07 * g)
                tt += 0.36 if k % 3 != 2 else 0.54
            tt += 1.6; p += 1
    for i, sc in enumerate(spec["scenes"]):
        st = sc.get("set")
        if st in ("credit", "finale", "writers"):   # warm brass-like chord swell
            L = D[i]; ch = sum(saw(f, L, 7) for f in (sa / 2, sa * 0.75, sa, sa * 1.25, sa * 1.5)); tq = np.arange(len(ch)) / SR
            add(music, lp(ch, 1800) * np.minimum(1, tq / 2.5) * np.minimum(1, (L - tq) / 2.0), ST[i], 0.03)
        if st in ("street", "finale"):   # horse carriage: clip-clop
            hoof = bp(rng.standard_normal(int(0.05 * SR)), 300, 2500) * np.exp(-np.arange(int(0.05 * SR)) / SR * 70)
            tq = 0.3
            while tq < D[i] - 0.3: add(music, hoof, ST[i] + tq, 0.10); add(music, hoof, ST[i] + tq + 0.17, 0.07); tq += 0.55
        if st == "office":   # ceiling fan hum
            seg = np.arange(int(D[i] * SR)) / SR; add(music, lp(rng.standard_normal(len(seg)), 400) * (0.7 + 0.3 * np.sin(2 * np.pi * 3 * 3 / 6.28 * seg)), ST[i], 0.04)
        if st == "teagarden":   # rain
            seg = int(D[i] * SR); add(music, bp(rng.standard_normal(seg), 1500, 7000) * np.minimum(1, np.arange(seg) / SR / 1.0), ST[i], 0.05)
        if st == "telegraph":   # morse key
            L = int(0.09 * SR); tp = np.arange(L) / SR; beep = np.sin(2 * np.pi * 750 * tp) * np.minimum(1, tp / 0.004)
            tq = 0.6
            while tq < D[i] - 0.5: add(music, beep[: int(L * (2.6 if rng.random() < 0.4 else 1)) if False else L], ST[i] + tq, 0.05); tq += rng.choice([0.14, 0.14, 0.32, 0.5])
        if st == "committee" and sc.get("stamp_at") is not None: add(music, boom(1.0, 60, 7, 1.2), ST[i] + sc["stamp_at"] + 0.3, 0.9)
        if st == "court" and sc.get("hit_at") is not None:
            add(music, boom(0.8, 70, 6, 1.2), ST[i] + sc["hit_at"] - 0.05, 0.8); add(music, chime(2.0, 1046.5), ST[i] + sc["hit_at"] + 0.1, 0.12)
        if st == "drawers" and sc.get("drawer_at") is not None: add(music, boom(0.6, 80, 5, 1.5), ST[i] + sc["drawer_at"], 0.6)
        if st == "credit":
            if sc.get("medal_at") is not None: add(music, chime(2.0, 1568), ST[i] + sc["medal_at"], 0.12)
            if sc.get("reveal_at") is not None: add(music, riser(1.2), ST[i] + sc["reveal_at"] - 1.2, 0.3); add(music, boom(1.0, 80, 3, 2.5), ST[i] + sc["reveal_at"], 0.7)
        if st == "london":   # Big Ben-ish bell
            add(music, chime(4.0, 392.0), ST[i] + 0.5, 0.10)
        if st == "measure":
            for at in sc.get("panel_at", []): add(music, boom(0.4, 90, 8, 0.8), ST[i] + at, 0.4)
# heartbeat, faster as the countdown approaches #1
bt = 0.6 if not film else T
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
if theme == "corporate":
    # office wall clock: soft tick-tock every second, the time running out
    tick = hp(rng.standard_normal(int(0.012 * SR)), 1800) * np.hanning(int(0.012 * SR))
    tock = lp(hp(rng.standard_normal(int(0.016 * SR)), 600), 2500) * np.hanning(int(0.016 * SR))
    tt = 0.5
    while tt < t_end_beats:
        add(music, tick if int(tt) % 2 == 0 else tock, tt, 0.16); tt += 1.0
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
if theme == "desert":   # desert wind: band-passed noise with slow gusts
    wind = bp(rng.standard_normal(n), 250, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * t * 0.07) * np.sin(2 * np.pi * t * 0.031 + 1))
    music += wind * 0.10
if theme == "oil":   # refinery: low industrial drone + slow steam hiss swells
    music += (np.sin(2 * np.pi * 49 * t) + 0.5 * np.sin(2 * np.pi * 98.3 * t)) * 0.02 * (0.7 + 0.3 * np.sin(2 * np.pi * t * 0.11))
    music += hp(rng.standard_normal(n), 3000) * 0.012 * np.clip(np.sin(2 * np.pi * t / 9.0), 0, 1) ** 3
if theme == "forensic":   # lab hum + a soft scanner tick every 2 s
    music += np.sin(2 * np.pi * 120 * t) * 0.012 * (0.6 + 0.4 * np.sin(2 * np.pi * t * 0.2))
    L = int(0.08 * SR); tp = np.arange(L) / SR; tick = np.sin(2 * np.pi * 3200 * tp) * np.exp(-tp * 60)
    for j in range(int(len(t) / SR / 2)): add(music, tick, j * 2.0 + 0.5, 0.05)
for i, sc in enumerate(spec["scenes"]):
    if sc["type"] == "fingerprint":   # scanner sweep, then an impact on the match
        L = int(1.4 * SR); tp = np.arange(L) / SR
        sweep = np.sin(2 * np.pi * (600 + 900 * tp) * tp) * np.sin(np.pi * tp / 1.4) * 0.5
        add(music, sweep, ST[i] + sc.get("scan_at", 0.6), 0.10)
        if sc.get("match_at") is not None: add(music, boom(0.8, 70, 3.5, 2), ST[i] + sc["match_at"], 0.75)
    if sc["type"] == "drawers":   # a click for every lit finger, a boom when the drawer opens
        L = int(0.1 * SR); tp = np.arange(L) / SR; clk = np.sin(2 * np.pi * 2200 * tp) * np.exp(-tp * 45)
        for at in sc.get("finger_at", []): add(music, clk, ST[i] + at, 0.18)
        if sc.get("drawer_at") is not None: add(music, boom(0.6, 80, 5, 1.5), ST[i] + sc["drawer_at"], 0.6)
    if sc["type"] == "spread":   # a ping per destination
        L = int(1.0 * SR); tp = np.arange(L) / SR; ping = np.sin(2 * np.pi * 1320 * tp) * np.exp(-tp * 6)
        for r in sc.get("routes", []): add(music, ping, ST[i] + (r[3] if len(r) > 4 else r[2]), 0.12)
    if sc["type"] == "satellite":   # sonar pings while the satellite sweeps
        L = int(1.2 * SR); tp = np.arange(L) / SR
        ping = np.sin(2 * np.pi * 1760 * tp) * np.exp(-tp * 5)
        for j in range(int(D[i] / 1.4)): add(music, ping, ST[i] + 0.4 + j * 1.4, 0.10)
        if sc.get("status") == "detected": add(music, boom(0.8, 70, 3.5, 2), ST[i] + sc.get("reveal_at", 2.0), 0.7)
    if sc["type"] == "dossier":
        st = sc.get("stamp_at", 0.5 + len(sc.get("rows", [])) * 0.55 + 0.4)
        add(music, boom(0.5, 60, 9, 1.2), ST[i] + st + 0.16, 0.9)
    if sc["type"] == "blast":
        bt = sc.get("blast_at", 1.6)
        add(music, riser(bt), ST[i], 0.4); add(music, boom(2.5, 45, 1.2, 4), ST[i] + bt, 1.0)
    if sc["type"] == "map":
        L = int(1.0 * SR); tp = np.arange(L) / SR
        add(music, np.sin(2 * np.pi * 1320 * tp) * np.exp(-tp * 4), ST[i] + sc.get("zoom_at", 1.6) + 1.2, 0.12)
for i, sc in enumerate(spec["scenes"]):   # payments reel (015) scene sounds
    if sc["type"] == "scanpay":   # scanner chirp, a two-note "payment received" ding, impact on the big number
        L = int(1.0 * SR); tp = np.arange(L) / SR
        add(music, np.sin(2 * np.pi * (900 + 600 * tp) * tp) * np.sin(np.pi * tp) * 0.4, ST[i] + 0.55, 0.08)
        pa = sc.get("pay_at", 1.9)
        add(music, chime(1.4, 1318.5), ST[i] + pa, 0.20); add(music, chime(1.8, 1760.0), ST[i] + pa + 0.16, 0.20)
        add(music, boom(0.8, 80, 3.5, 2), ST[i] + sc.get("count_at", pa + 0.6), 0.6)
    if sc["type"] == "keys":   # a lock click per key, a low hit on the mystery key
        L = int(0.12 * SR); tp = np.arange(L) / SR; clk = hp(rng.standard_normal(L), 1500) * np.exp(-tp * 60)
        ka = sc.get("key_at", [0.6, 1.6, 3.2])
        for at in ka[:2]: add(music, clk, ST[i] + at, 0.35)
        add(music, boom(0.9, 55, 3.0, 2), ST[i] + ka[2], 0.75)
    if sc["type"] == "pricefall":   # falling tone as the price collapses, a rising sweep for data use
        da = sc.get("drop_at", 2.5); L = int(0.7 * SR); tp = np.arange(L) / SR
        add(music, np.sin(2 * np.pi * np.cumsum(1400 * np.exp(-tp * 3.5) + 120) / SR) * np.exp(-tp * 2) * 0.5, ST[i] + da, 0.12)
        add(music, boom(0.6, 70, 4, 1.5), ST[i] + da + 0.55, 0.55)
        ua = sc.get("use_at", da + 2.0); add(music, riser(1.2), ST[i] + ua, 0.25)
    if sc["type"] == "qrshops":   # little pops as the stickers spread, a chime on the merchant count
        qa = sc.get("qr_at", 1.0); L = int(0.05 * SR); tp = np.arange(L) / SR; pop = np.sin(2 * np.pi * 2600 * tp) * np.exp(-tp * 80)
        for j in range(18): add(music, pop, ST[i] + qa + j * 0.09 + rng.uniform(0, 0.04), 0.10)
        add(music, chime(1.6, 1568.0), ST[i] + sc.get("count_at", qa + 2.4), 0.14)
    if sc["type"] == "network":   # riser into the switch lighting up
        la = sc.get("link_at", 1.6); add(music, riser(min(1.5, la)), ST[i] + la - min(1.5, la), 0.35)
        add(music, boom(1.0, 75, 3.0, 2.2), ST[i] + la, 0.8)
    if sc["type"] == "share":
        add(music, boom(0.6, 70, 4, 1.5), ST[i] + sc.get("hl_at", 2.1), 0.5)
        add(music, boom(0.9, 60, 3, 2), ST[i] + sc.get("chip_at", 3.3), 0.7)
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
