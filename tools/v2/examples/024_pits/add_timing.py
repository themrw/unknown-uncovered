import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.15); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.2, lead + k / len(vo) * durs[i] + off), 2)
S[0]["reveal_at"] = at(0, "लक्ष्य?", -0.1); S[0]["stamp_at"] = at(0, "और अमेरिका-रूस", 0.2)
S[1]["squeeze_at"] = at(1, "ऐसा धमाका", -0.9)
S[3]["stamp_at"] = at(3, "और यहाँ", 0.0)
S[4]["date_at"] = at(4, "फिर एक अक्टूबर", -0.1)
S[5]["bar_at"] = [at(5, "दो हज़ार अट्ठाईस", -0.2), at(5, "क़ानून कहता", 0.0), at(5, "और नया रक्षा", 0.2)]
S[6]["now_at"] = at(6, "अब उसी में", -0.15); S[6]["stamp_at"] = at(6, "पिछले ही महीने", -0.1); S[6]["cost_at"] = at(6, "ख़र्च?", 0.4)
S[7]["right_at"] = at(7, "पर अमेरिका के ही", -0.2)
S[8]["tear_at"] = at(8, "आख़िरी परमाणु", -0.3); S[8]["stamp_at"] = at(8, "ख़त्म हो चुकी", -0.1); S[8]["big_at"] = at(8, "उन्नीस सौ", -0.2)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for s in S: print(s["type"], {k: v for k, v in s.items() if k.endswith("_at")})
