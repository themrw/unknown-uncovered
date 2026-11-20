import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.35); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.3, lead + k / len(vo) * durs[i] + off), 2)
S[0]["hit_at"] = at(0, "हरा दिया")
S[8]["card_at"] = [0.5, at(8, "इसमें दवा पर नहीं", -0.3)]
S[11]["step_at"] = [0.4, at(11, "आठ सौ", -0.3)]
S[12]["step_at"] = [0.4, at(12, "तीन सौ पचास", -0.3)]; S[12]["chip_at"] = at(12, "एक डॉलर")
S[13]["merge_at"] = at(13, "एक ही गोली", -0.8)
S[14]["stamp_at"] = at(14, "समुद्री डाकू", -0.6)
S[15]["drop_at"] = at(15, "केस वापस", -0.4)
S[16]["hl_at"] = at(16, "पेटेंट के नियम", -0.3)
S[17]["bar_at"] = [0.6, 1.6, 2.6, at(17, "एक सौ चालीस", -0.6)]
S[18]["second_at"] = at(18, "बच्चों", -0.3)
S[19]["card_at"] = [0.5, at(19, "पर भारत ने", -0.3)]
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print({i: {k: v for k, v in s.items() if k.endswith("_at")} for i, s in enumerate(S) if any(k.endswith("_at") for k in s)})
