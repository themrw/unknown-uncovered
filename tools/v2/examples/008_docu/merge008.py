"""Merge the 26 voiced main scenes + 6 voiced extra scenes into /home/claude/work/008full (spec + vo/)."""
import json, shutil, os, sys
A, B, O = "/home/claude/work/008", "/home/claude/work/008add", "/home/claude/work/008full"
main = json.load(open(f"{A}/spec.json")); new = json.load(open(f"{B}/new.json"))
da = json.load(open(f"{A}/vo/durs.json"))
db = json.load(open(f"{B}/vo/durs.json")) if os.path.exists(f"{B}/vo/durs.json") else [max(3, len(s["vo"]) / 14) for s in new]
items = [(s, f"{A}/vo/{i:02d}.wav", da[i], s.get("kicker") or s.get("title")) for i, s in enumerate(main["scenes"])]
for j, s in enumerate(new):
    pos = next(k for k, it in enumerate(items) if it[3] == s["after"]) + 1
    sc = {k: v for k, v in s.items() if k not in ("id", "after")}
    items.insert(pos, (sc, f"{B}/vo/{j:02d}.wav", db[j], s["id"]))
os.makedirs(f"{O}/vo", exist_ok=True)
for k, (sc, wav, d, _) in enumerate(items):
    if os.path.exists(wav): shutil.copy(wav, f"{O}/vo/{k:02d}.wav")
json.dump([it[2] for it in items], open(f"{O}/vo/durs.json", "w"))
main["scenes"] = [it[0] for it in items]; main.pop("voice_job", None)
json.dump(main, open(f"{O}/spec.json", "w"), ensure_ascii=False, indent=1)
print(len(items), round(sum(it[2] for it in items), 1))
