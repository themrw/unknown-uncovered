import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); S = spec["scenes"]; lead = spec.get("lead", 0.0)
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["f_at"] = [at(0, "अड़सठ", -0.3), at(0, "पर इस", -0.2), at(0, "शर्त", -0.3)]
S[1]["c_at"] = [at(1, "तीन सौ", -0.3), at(1, "दी गई", -0.2), at(1, "अफ़्रीका", -0.3)]; S[1]["why_at"] = at(1, "बारह", 0.2)
S[2]["i_at"] = [at(2, "मालदीव", -0.2), at(2, "नेपाल", -0.2), at(2, "श्रीलंका", -0.2), at(2, "बांग्लादेश", -0.2)]; S[2]["note_at"] = at(2, "सात दशमलव", 0.3)
S[3]["l_at"] = [at(3, "भारत के", -0.3), at(3, "कम से कम", -0.3), at(3, "भारत से ही", -0.4)]
S[4]["c_at"] = [at(4, "गयाना", -0.3), at(4, "मालदीव", -0.3)]; S[4]["why_at"] = at(4, "यही", -0.2)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print([{k: v for k, v in s.items() if k.endswith("_at")} for s in S])
