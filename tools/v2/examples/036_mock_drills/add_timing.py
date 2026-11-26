import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); S = spec["scenes"]; lead = spec.get("lead", 0.0)
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["f_at"] = [at(0, "सायरन", -0.2), at(0, "बत्तियाँ", -0.2), at(0, "चौवन", -0.3)]
S[1]["c_at"] = [at(1, "उन्नीस", -0.3), at(1, "पूरे चौवन", -0.3), at(1, "सात मई", -0.3)]; S[1]["why_at"] = at(1, "सायरन बज", -0.2)
S[2]["events"] = [[at(2, "दिल्ली", -0.2), "delhi", "DELHI", "2 APR · 13 DISTRICTS", 120, -95],
                  [at(2, "पंजाब", -0.2), "punjab", "PUNJAB", "24 APR · ALL DISTRICTS", 230, -60],
                  [at(2, "मेघालय", -0.2), "meghalaya", "MEGHALAYA", "24 APR · ALL DISTRICTS", 250, -120],
                  [at(2, "बिहार", -0.2), "bihar", "BIHAR", "14 MAY · 6 DISTRICTS", 90, 70],
                  [at(2, "उत्तर प्रदेश", -0.2), "up", "UTTAR PRADESH", "22 NOV · ALL 75 DISTRICTS", 160, 10]]
S[3]["l_at"] = [at(3, "गृह मंत्रालय", -0.4), at(3, "सायरन", -0.3), at(3, "बचाव", -0.3)]; S[3]["q_at"] = at(3, "पर आपको", -0.2)
S[4]["w_at"] = at(4, "ऊपर-नीचे", -0.3); S[4]["c_at"] = at(4, "और लगातार", -0.2)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print([{k: v for k, v in s.items() if k.endswith("_at")} for s in S])
