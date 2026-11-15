#!/usr/bin/env python3
"""Generate polished Hindi narration per scene from a spec: <dir>/vo/NN.wav + durs.json.
usage: uu_voice.py spec.json            (voice/speed from spec: "voice", "speed")
Needs kokoro-onnx + model files in $UU_TTS (default /home/claude/tts)."""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

spec_path = sys.argv[1]; spec = json.load(open(spec_path))
work = os.path.dirname(os.path.abspath(spec_path)); vo = os.path.join(work, "vo"); os.makedirs(vo, exist_ok=True)
tts = os.environ.get("UU_TTS", "/home/claude/tts")
k = Kokoro(os.path.join(tts, "kokoro-v1.0.onnx"), os.path.join(tts, "voices-v1.0.bin"))
voice, speed = spec.get("voice", "hm_omega"), spec.get("speed", 1.0)
POLISH = ("highpass=f=70,lowpass=f=11000,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.2:g=2.5,"
          "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,aecho=0.8:0.6:28:0.12")

def trim(a, sr, thr=0.012, pad=0.06):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    s = max(0, idx[0] - int(pad * sr)); e = min(len(a), idx[-1] + int(pad * sr * 2))
    return a[s:e]

durs = []
for i, sc in enumerate(spec["scenes"]):
    text = sc["vo"]
    a, sr = k.create(text, voice=voice, speed=sc.get("speed", speed), lang="hi")
    a = trim(a, sr)
    raw = os.path.join(vo, f"raw_{i:02d}.wav"); sf.write(raw, a, sr)
    out = os.path.join(vo, f"{i:02d}.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", POLISH, "-ar", "48000", "-ac", "1", out], check=True)
    d = sf.info(out).duration; durs.append(round(d, 3))
json.dump(durs, open(os.path.join(vo, "durs.json"), "w"))
print(durs, round(sum(durs), 1))
