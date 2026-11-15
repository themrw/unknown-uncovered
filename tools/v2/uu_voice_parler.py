#!/usr/bin/env python3
"""Indic Parler-TTS (AI4Bharat, Apache-2.0) voice generation, run inside the GitHub Action (the workspace can't reach Hugging Face).

Processes every voice/requests/<name>.json that has no voice/out/<name>/done.json:
  {"description": "Rohit speaks ...",            # default speaker/style caption
   "seed": 7,
   "items": [{"name": "00", "text": "Hindi ...", "description": "(optional override)"}, ...]}
Long texts are split into sentences (। ? !), synthesized one by one and joined with short natural pauses.
Writes voice/out/<name>/<item>.wav (mono, model rate) and done.json with durations. Needs HF_TOKEN (gated model).

Parallel use (the Action runs 4 shards): `uu_voice_parler.py --shard K --of N` synthesizes only the items assigned to shard K
(balanced by text length, deterministic) and skips done.json; `uu_voice_parler.py --finish` then writes done.json for every
pending request whose wavs are all present.
"""
import glob, json, os, re, sys, time
import numpy as np, soundfile as sf

REPO = "ai4bharat/indic-parler-tts"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAUSE = {"।": 0.28, "?": 0.32, "!": 0.3, ",": 0.12}

def sentences(text):
    parts = re.split(r"(?<=[।?!])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]

def shard_items(pending, k, n):
    """Greedy length balancing over every (request, item); identical on every shard."""
    work = []
    for name, req in pending:
        for it in json.load(open(req))["items"]:
            work.append((len(it["text"]), name, it["name"]))
    work.sort(key=lambda w: (-w[0], w[1], w[2]))
    load = [0] * n; mine = set()
    for L, name, item in work:
        j = min(range(n), key=lambda x: (load[x], x)); load[j] += L
        if j == k: mine.add((name, item))
    return mine

def finish(pending):
    for name, req in pending:
        spec = json.load(open(req)); out = os.path.join(ROOT, "voice", "out", name); durs = {}; sr = None
        for it in spec["items"]:
            f = os.path.join(out, f"{it['name']}.wav")
            if not os.path.exists(f): print("incomplete", name, it["name"]); break
            info = sf.info(f); sr = info.samplerate; durs[it["name"]] = round(info.duration, 3)
        else:
            json.dump({"rate": sr, "durations": durs}, open(os.path.join(out, "done.json"), "w"), indent=1)
            print("done", name, durs)

def main():
    args = sys.argv[1:]
    pending = []
    for req in sorted(glob.glob(os.path.join(ROOT, "voice", "requests", "*.json"))):
        name = os.path.splitext(os.path.basename(req))[0]
        if not os.path.exists(os.path.join(ROOT, "voice", "out", name, "done.json")):
            pending.append((name, req))
    if not pending:
        print("nothing to do"); return
    if "--finish" in args:
        finish(pending); return
    mine = None
    if "--shard" in args:
        k, n = int(args[args.index("--shard") + 1]), int(args[args.index("--of") + 1])
        mine = shard_items(pending, k, n); print(f"shard {k}/{n}: {sorted(mine)}", flush=True)
        if not mine: return
    import torch                                             # heavy imports only when synthesizing
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer, set_seed
    torch.set_num_threads(os.cpu_count() or 4)
    t0 = time.time()
    model = ParlerTTSForConditionalGeneration.from_pretrained(REPO).eval()
    tok = AutoTokenizer.from_pretrained(REPO)
    dtok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
    sr = model.config.sampling_rate
    print(f"model loaded in {time.time() - t0:.0f}s, rate {sr}", flush=True)
    for name, req in pending:
        spec = json.load(open(req)); out = os.path.join(ROOT, "voice", "out", name); os.makedirs(out, exist_ok=True)
        durs = {}
        for it in spec["items"]:
            if mine is not None and (name, it["name"]) not in mine: continue
            desc = it.get("description", spec["description"])
            d = dtok(desc, return_tensors="pt")
            chunks = []
            for s in sentences(it["text"]):
                set_seed(it.get("seed", spec.get("seed", 7)))
                p = tok(s, return_tensors="pt")
                t1 = time.time()
                with torch.inference_mode():
                    g = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                                       prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
                a = g.cpu().numpy().squeeze().astype(np.float32)
                # trim leading/trailing silence of each sentence
                idx = np.where(np.abs(a) > 0.01)[0]
                if len(idx): a = a[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.06 * sr)]
                chunks.append(a); chunks.append(np.zeros(int(PAUSE.get(s[-1], 0.2) * sr), np.float32))
                print(f"{name}/{it['name']}: {len(a) / sr:.1f}s audio in {time.time() - t1:.0f}s  {s[:40]}", flush=True)
            audio = np.concatenate(chunks[:-1]) if chunks else np.zeros(1, np.float32)
            sf.write(os.path.join(out, f"{it['name']}.wav"), audio, sr)
            durs[it["name"]] = round(len(audio) / sr, 3)
        if mine is None:
            json.dump({"rate": sr, "durations": durs}, open(os.path.join(out, "done.json"), "w"), indent=1)
        print("finished", name, durs, flush=True)

if __name__ == "__main__":
    main()
