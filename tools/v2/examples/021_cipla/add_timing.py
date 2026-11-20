import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.2, lead + k / len(vo) * durs[i] + off), 2)
S[0]["hit_at"] = at(0, "हरा दिया")
S[2]["merge_at"] = at(2, "एक ही गोली", -0.6)
n = at(3, "सिर्फ़ तीन सौ"); S[3].update(slash_at=n - 0.7, new_at=n, stamp_at=at(3, "छियानवे"), chip_at=at(3, "एक डॉलर"))
S[4]["card_at"] = [0.4, at(4, "सिर्फ़ उसे", -0.3)]; S[4]["pirate_at"] = at(4, "समुद्री डाकू", -0.6)
S[5]["drop_at"] = at(5, "केस वापस", -0.3)
S[6]["bar_at"] = [0.5, at(6, "दाम गिरते"), at(6, "एक सौ चालीस", -0.6)]; S[6]["note_at"] = at(6, "एक सौ चालीस", 0.6)
S[8]["grow_at"] = at(8, "तीन करोड़", -0.4)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print({i: {k: v for k, v in s.items() if k.endswith("_at")} for i, s in enumerate(S)})
