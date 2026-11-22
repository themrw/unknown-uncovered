import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.35); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[6]["stamp_at"] = at(6, "पर दुनिया", 0.1)
S[7]["card_at"] = [0.5, at(7, "पर अगर", -0.1)]
S[14]["bar_at"] = [at(14, "जहाँ सिर्फ़", 0.0), at(14, "वहाँ उनके", 0.0)]
S[15]["stamp_at"] = at(15, "ठुकरा", -0.3)
S[25]["card_at"] = [0.8, at(25, "ज़्यादा मीठे", -0.2)]
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S): 
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
