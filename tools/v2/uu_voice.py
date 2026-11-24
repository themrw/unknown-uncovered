#!/usr/bin/env python3
"""Polished Hindi narration per scene from a spec: <dir>/vo/NN.wav + vo/durs.json.

Two engines, chosen by spec["tts"]:
  "parler" (default, natural): Indic Parler-TTS runs in the GitHub Action (Hugging Face is unreachable from the workspace).
      1) uu_voice.py spec.json request <job>   -> writes <repo>/voice/requests/<job>.json; commit + push it
      2) wait for the "Generate voice" Action, git pull
      3) uu_voice.py spec.json                 -> reads <repo>/voice/out/<spec["voice_job"]>/NN.wav, polishes -> vo/
     Speaker/style caption: spec["voice_desc"] (default: Aman, energetic documentary narrator). Optional spec["speed"] via atempo.
  "kokoro" (offline fallback, robotic): kokoro-onnx with spec["voice"] (hm_psi) and spec["speed"]; models in $UU_TTS.
Repo path: $UU_REPO (default /home/claude/unknown-uncovered).
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

spec_path = sys.argv[1]; spec = json.load(open(spec_path))
work = os.path.dirname(os.path.abspath(spec_path)); vo = os.path.join(work, "vo"); os.makedirs(vo, exist_ok=True)
REPO = os.environ.get("UU_REPO", "/home/claude/unknown-uncovered")
engine = spec.get("tts", "parler")
DESC = ("Aman speaks with a confident, expressive and engaging tone at a moderate pace, like a documentary narrator. "
        "The recording is very high quality, with the voice sounding clear and very close up, with no background noise.")
# gentle broadcast polish: no echo, no harsh presence boost (those made Kokoro sound like a phone line)
POLISH = {"parler": "highpass=f=60,lowpass=f=15000,equalizer=f=220:t=q:w=1:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=2",
          "kokoro": "highpass=f=70,lowpass=f=12000,equalizer=f=200:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3"}[engine]

# Pronunciation fixes applied to every Parler request. The channel name is read correctly only in Latin letters
# (tested Nov 2026: "अननोन अनकवर्ड" and other Devanagari spellings came out wrong; "Unknown Uncovered" was right).
SAY = {"अननोन अनकवर्ड": "Unknown Uncovered", "अन्नोन अन्कवर्ड": "Unknown Uncovered", "अन-नोन अन-कवर्ड": "Unknown Uncovered"}
def say(text):
    for a, b in SAY.items(): text = text.replace(a, b)
    return text

def trim(a, sr, thr=0.01, pad=0.05):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    return a[max(0, idx[0] - int(pad * sr)): min(len(a), idx[-1] + int(pad * sr * 2))]

MIN_CHARS = 30   # Parler hallucinates extra babble on very short lines (reel 033: "पहला अध्याय। डर।" -> 2.5 s of garbage)
def spoken(text): return len([c for c in text if c.isalpha() or "\u0900" <= c <= "\u097f"])

if len(sys.argv) > 3 and sys.argv[2] == "request":
    job = sys.argv[3]
    short = [(i, sc["vo"]) for i, sc in enumerate(spec["scenes"]) if sc.get("vo") and spoken(sc["vo"]) < MIN_CHARS]
    if short and not os.environ.get("UU_ALLOW_SHORT"):
        for i, t in short: print(f"TOO SHORT scene {i:02d}: {t!r} -> write a full sentence (>= {MIN_CHARS} letters) or leave vo empty")
        sys.exit("refusing to request voice: short lines glitch in Parler (set UU_ALLOW_SHORT=1 to override)")
    req = {"description": spec.get("voice_desc", DESC), "seed": spec.get("voice_seed", 7),
           "items": [{"name": f"{i:02d}", "text": say(sc["vo"])} for i, sc in enumerate(spec["scenes"])]}
    p = os.path.join(REPO, "voice", "requests", f"{job}.json"); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(req, open(p, "w"), ensure_ascii=False, indent=1)
    spec["voice_job"] = job; json.dump(spec, open(spec_path, "w"), ensure_ascii=False, indent=1)
    print("wrote", p, "- commit and push it, wait for the 'Generate voice' Action, then git pull and rerun without 'request'")
    sys.exit(0)

if engine == "kokoro":
    from kokoro_onnx import Kokoro
    tts = os.environ.get("UU_TTS", "/home/claude/tts")
    k = Kokoro(os.path.join(tts, "kokoro-v1.0.onnx"), os.path.join(tts, "voices-v1.0.bin"))

durs = []
speed = spec.get("speed", 1.0)
for i, sc in enumerate(spec["scenes"]):
    if engine == "kokoro":
        a, sr = k.create(sc["vo"], voice=spec.get("voice", "hm_psi"), speed=sc.get("speed", speed), lang="hi")
        tempo = 1.0
    else:
        src = os.path.join(REPO, "voice", "out", spec["voice_job"], f"{i:02d}.wav")
        if not os.path.exists(src): sys.exit(f"missing {src}: run the voice Action first (see docstring)")
        a, sr = sf.read(src, dtype="float32"); tempo = sc.get("speed", speed)
    a = trim(a, sr)
    raw = os.path.join(vo, f"raw_{i:02d}.wav"); sf.write(raw, a, sr)
    out = os.path.join(vo, f"{i:02d}.wav")
    af = (f"atempo={tempo}," if abs(tempo - 1.0) > 0.005 else "") + POLISH
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", af, "-ar", "48000", "-ac", "1", out], check=True)
    durs.append(round(sf.info(out).duration, 3))
json.dump(durs, open(os.path.join(vo, "durs.json"), "w"))
print(durs, round(sum(durs), 1))

# ---- glitch check (mandatory before rendering): speaking rate and silent gaps per scene
def gaps(path, thr_db=-45, win=0.05):
    x, r = sf.read(path, dtype="float32"); x = x.mean(1) if x.ndim > 1 else x; n = int(win * r)
    e = np.array([20 * np.log10(np.sqrt((x[j:j + n] ** 2).mean()) + 1e-9) for j in range(0, max(1, len(x) - n), n)])
    run = best = 0
    for v in e:
        run = run + 1 if v < thr_db else 0; best = max(best, run)
    return best * win
rates = [(i, spoken(sc["vo"]) / d) for i, (sc, d) in enumerate(zip(spec["scenes"], durs)) if sc.get("vo") and d > 0]
med = float(np.median([r for _, r in rates])) if rates else 0
bad = []
for i, r in rates:
    sc = spec["scenes"][i]; g = gaps(os.path.join(vo, f"{i:02d}.wav"))
    why = []
    if spoken(sc["vo"]) < MIN_CHARS: why.append("very short line")
    if r < 0.75 * med: why.append(f"too slow {r:.1f} vs median {med:.1f} letters/s (extra babble?)")
    if r > 1.35 * med: why.append(f"too fast {r:.1f} vs median {med:.1f} letters/s (words dropped?)")
    if g > 1.2: why.append(f"{g:.1f}s silent gap inside")
    if why: bad.append(i); print(f"GLITCH? scene {i:02d}: " + "; ".join(why) + f" | {sc['vo'][:60]}")
if bad: print(f"VOICE CHECK FAILED for scenes {bad}: re-voice them (fuller sentence) before rendering"); sys.exit(2)
print(f"voice check OK ({len(rates)} scenes, median {med:.1f} letters/s)")
