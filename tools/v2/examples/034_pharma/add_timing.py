import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.0); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["q_at"] = at(0, "पर क्या")
S[1]["r_at"] = [0.2, at(1, "अफ़्रीका"), at(1, "और ब्रिटेन")]
S[2]["n_at"] = at(2, "उसका करीब", -0.2)
S[3]["r_at"] = [at(3, "टीबी", -0.3), at(3, "टीबी", 0.6), at(3, "भारत, सौ", -0.3), at(3, "भारत, सौ", 0.3)]
S[4]["q_at"] = at(4, "क्या भारत")
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S):
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
