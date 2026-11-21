import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["claim_at"] = [0.0, at(0, "लोकसभा में", -0.1), at(0, "और प्रधानमंत्री", -0.1)]; S[0]["q_at"] = at(0, "आख़िर सच", -0.1)
S[2]["bars_at"] = at(2, "और आई-एम-एफ़", -0.2); S[2]["verdict_at"] = at(2, "इसलिए", -0.1)
S[4]["jobs_at"] = at(4, "सरकार के अपने", -0.2); S[4]["urban_at"] = at(4, "शहरों में", -0.1); S[4]["verdict_at"] = at(4, "इसलिए", -0.1)
S[6]["rupee_at"] = at(6, "मई में रुपया", -0.2); S[6]["rank_at"] = at(6, "डॉलर में मापने", -0.1); S[6]["pc_at"] = at(6, "और प्रति व्यक्ति", -0.1); S[6]["verdict_at"] = at(6, "इसलिए", -0.1)
S[7]["row_at"] = [0.3, 0.9, 1.5]; S[7]["line_at"] = at(7, "पर युवाओं", -0.1)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for s in S: print(s["type"], {k: v for k, v in s.items() if k.endswith("_at")})
