import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["claim_at"] = [0.0, at(0, "दूसरे ने", -0.1), at(0, "तीसरे ने", -0.1)]; S[0]["q_at"] = at(0, "सच क्या है", -0.1)
S[2]["bars_at"] = at(2, "और IMF", -0.2); S[2]["verdict_at"] = at(2, "ये दावा", -0.1)
S[4]["jobs_at"] = at(4, "सरकार के अपने", -0.2); S[4]["urban_at"] = at(4, "शहरों में", -0.1); S[4]["verdict_at"] = at(4, "यानी", -0.1)
S[6]["rupee_at"] = at(6, "रुपया मई", -0.2); S[6]["rank_at"] = at(6, "डॉलर में मापने", -0.1); S[6]["pc_at"] = at(6, "और प्रति व्यक्ति", -0.1); S[6]["verdict_at"] = at(6, "यानी, सच", -0.1)
S[7]["row_at"] = [0.3, 0.9, 1.5]; S[7]["line_at"] = at(7, "ये सबसे तेज़", -0.1)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for s in S: print(s["type"], {k: v for k, v in s.items() if k.endswith("_at")})
