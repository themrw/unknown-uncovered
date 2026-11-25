import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.0); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[1]["people_at"] = at(1, "इसका क्यूब", -0.3); S[1]["dim_at"] = at(1, "सिर्फ़ करीब"); S[1]["gate_at"] = at(1, "यानी इंडिया", -0.2)
S[4]["slab_at"] = at(4, "यानी हर साल", -0.6)
S[5]["res_at"] = at(5, "उसका क्यूब", -1.0)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S):
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
