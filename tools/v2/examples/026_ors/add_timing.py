import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[2]["stamp_at"] = at(2, "पर दुनिया ने", 0.0)
S[4]["row_at"] = [at(4, "दूसरे कैंपों", 0.0), at(4, "उनके कैंप में", 0.0)]; S[4]["stamp_at"] = at(4, "फिर भी", 0.1)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for s in S: print(s["type"], {k: v for k, v in s.items() if k.endswith("_at")})
