import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(lead + k / len(vo) * durs[i] + off, 2)
S[2]["col_at"] = [1.0, at(2, "पर सैनिक")]
S[3]["col_at"] = [1.2, at(3, "पर हर तीन")]
j = at(4, "जापान")
S[4]["row_at"] = [at(4, "अमेरिका"), j, j + 0.7, j + 1.4, at(4, "नेपाल")]; S[4]["note_at"] = at(4, "पर सैनिक सबसे")
S[5]["col_at"] = [at(5, "सतहत्तर", -0.4), at(5, "चार सौ", -0.3)]
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print([(s["type"], s.get("col_at") or s.get("row_at")) for s in S])
