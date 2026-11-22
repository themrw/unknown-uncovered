import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[3]["stamp_at"] = at(3, "उसके बाद", -0.3)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print(S[3]["stamp_at"], durs[3])
