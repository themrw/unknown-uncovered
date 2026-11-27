import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); S = spec["scenes"]; lead = spec.get("lead", 0.0)
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["f_at"] = [at(0, "नहीं", -0.3), at(0, "पर असली", -0.2), at(0, "दिलचस्प", -0.4)]
S[1]["c_at"] = [at(1, "आईआरजीसी", -0.3), at(1, "अगर उसके", -0.3), at(1, "सात बड़ी", -0.4)]; S[1]["why_at"] = at(1, "निशाने", -0.2)
S[2]["c_at"] = [at(2, "छह सौ", -0.3), at(2, "सिर्फ़ छह", -0.3), at(2, "गुज़रती", -0.1)]; S[2]["why_at"] = at(2, "गुज़रती", 0.6)
S[3]["l_at"] = [at(3, "हर साल", -0.3), at(3, "हर हफ़्ते", -0.3), at(3, "ज़्यादातर", -0.3)]
S[4]["c_at"] = [at(4, "इराक़", -0.3), at(4, "कुछ केबल", -0.3)]; S[4]["why_at"] = at(4, "ईरान को", 0.0)
S[5]["c_at"] = [at(5, "तेरह", -0.4), at(5, "मुंबई के पास", 0.2), at(5, "सितंबर", -0.2)]; S[5]["why_at"] = at(5, "धीमा", -0.2)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print([{k: v for k, v in s.items() if k.endswith("_at")} for s in S])
