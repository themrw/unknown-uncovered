import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["eq_at"] = at(0, "सिर्फ़ इसलिए", 0.0)
S[1]["h_at"] = at(1, "पूरे देश", 0.0)
S[2]["s2_at"] = at(2, "और दो हज़ार", 0.0)
S[3]["d1_at"] = at(3, "लॉटरी खुली", 0.0); S[3]["d2_at"] = at(3, "आख़िर तक", -0.3)
S[4]["q_at"] = 0.4; S[4]["y_at"] = at(4, "यानी", 0.0)
S[5]["doc_at"] = at(5, "तुवालु ने", 0.0); S[5]["note_at"] = at(5, "कि अगर", 0.0)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S):
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
