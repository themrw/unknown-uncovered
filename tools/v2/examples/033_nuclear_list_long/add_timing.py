import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.35); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[12]["cats_at"] = at(12, "परमाणु बिजली"); S[12]["sites_at"] = at(12, "परमाणु बिजली", 0.5); S[12]["total_at"] = at(12, "असली लिस्ट")
S[19]["row_at"] = [at(19, "इसमें परमाणु"), at(19, "ठिकानों की"), at(19, "और नियम")]; S[19]["line_at"] = at(19, "यानी")
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S):
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
