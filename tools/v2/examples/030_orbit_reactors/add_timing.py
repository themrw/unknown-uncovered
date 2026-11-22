import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["fell_at"] = at(0, "आसमान से", -1.0)
S[1]["split_at"] = at(1, "और आज भी", 0.0)
S[2]["rec_at"] = at(2, "सिर्फ़ शून्य", -0.1); S[2]["pay_at"] = 999
S[3]["hit_at"] = at(3, "हिंद महासागर", -0.3)
S[4]["drop_at"] = at(4, "हज़ारों", -0.2)
S[5]["a_at"] = at(5, "अंतरिक्ष में", 0.0)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S):
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
