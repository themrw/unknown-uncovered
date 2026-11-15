#!/usr/bin/env python3
"""Polished Hindi narration per scene from a spec: <dir>/vo/NN.wav + vo/durs.json.

Two engines, chosen by spec["tts"]:
  "parler" (default, natural): Indic Parler-TTS runs in the GitHub Action (Hugging Face is unreachable from the workspace).
      1) uu_voice.py spec.json request <job>   -> writes <repo>/voice/requests/<job>.json; commit + push it
      2) wait for the "Generate voice" Action, git pull
      3) uu_voice.py spec.json                 -> reads <repo>/voice/out/<spec["voice_job"]>/NN.wav, polishes -> vo/
     Speaker/style caption: spec["voice_desc"] (default: Rohit, documentary narrator). Optional spec["speed"] via atempo.
  "kokoro" (offline fallback, robotic): kokoro-onnx with spec["voice"] (hm_psi) and spec["speed"]; models in $UU_TTS.
Repo path: $UU_REPO (default /home/claude/unknown-uncovered).
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

spec_path = sys.argv[1]; spec = json.load(open(spec_path))
work = os.path.dirname(os.path.abspath(spec_path)); vo = os.path.join(work, "vo"); os.makedirs(vo, exist_ok=True)
REPO = os.environ.get("UU_REPO", "/home/claude/unknown-uncovered")
engine = spec.get("tts", "parler")
DESC = ("Rohit speaks with a confident, expressive and engaging tone at a moderate pace, like a documentary narrator. "
        "The recording is very high quality, with the voice sounding clear and very close up, with no background noise.")
# gentle broadcast polish: no echo, no harsh presence boost (those made Kokoro sound like a phone line)
POLISH = {"parler": "highpass=f=60,lowpass=f=15000,equalizer=f=220:t=q:w=1:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=2",
          "kokoro": "highpass=f=70,lowpass=f=12000,equalizer=f=200:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3"}[engine]

def trim(a, sr, thr=0.01, pad=0.05):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    return a[max(0, idx[0] - int(pad * sr)): min(len(a), idx[-1] + int(pad * sr * 2))]

if len(sys.argv) > 3 and sys.argv[2] == "request":
    job = sys.argv[3]
    req = {"description": spec.get("voice_desc", DESC), "seed": spec.get("voice_seed", 7),
           "items": [{"name": f"{i:02d}", "text": sc["vo"]} for i, sc in enumerate(spec["scenes"])]}
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
