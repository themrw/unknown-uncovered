import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.2, lead + k / len(vo) * durs[i] + off), 2)
S[2]["squeeze_at"] = at(2, "ऐसा धमाका", -0.9)
S[4]["stamp_at"] = at(4, "और यहाँ", 0.0)
S[6]["bar_at"] = [at(6, "दो हज़ार अट्ठाईस", 0.0), at(6, "क़ानून कहता", 0.0), at(6, "और नया रक्षा", 0.2)]
S[8]["right_at"] = at(8, "पर अमेरिका के ही", -0.2)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for s in S: print(s["type"], {k: v for k, v in s.items() if k.endswith("_at")})
