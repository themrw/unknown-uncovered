import json
s = json.load(open("spec.json")); d = json.load(open("vo/durs.json")); L = s.get("lead", 0.2)
def at(i, sub, off=0.0):
    vo = s["scenes"][i]["vo"]; j = vo.find(sub); assert j >= 0, (i, sub)
    return round(L + j / len(vo) * d[i] + off, 2)
S = s["scenes"]
S[0]["title_at"] = max(1.2, at(0, "रिफाइनरियाँ बंद", -0.3))
for i, nm in ((2, "दक्षिण कोरिया"), (3, "भारत।"), (4, "रूस"), (5, "अमेरिका"), (6, "चीन")):
    S[i]["reveal_at"] = at(i, nm, -0.15)
json.dump(s, open("spec.json", "w"), ensure_ascii=False, indent=1)
print([round(x, 1) for x in d], {i: sc.get("reveal_at") for i, sc in enumerate(S)}, S[0]["title_at"])
