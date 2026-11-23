import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["f_at"] = [at(0, "आवाज़"), at(0, "क़रीब तीन सौ"), at(0, "और चीन")]
S[1]["c_at"] = [at(1, "भारत तीसरे"), at(1, "इस साल"), at(1, "और रक्षा")]; S[1]["why_at"] = at(1, "जिसका बड़ा")
S[2]["n_at"] = at(2, "नाम बना"); S[2]["s_at"] = at(2, "ये ज़मीन")
S[3]["b_at"] = [at(3, "फ़िलीपींस"), at(3, "वियतनाम"), at(3, "इंडोनेशिया")]; S[3]["dispute_at"] = at(3, "तीनों का")
S[4]["r_at"] = [at(4, "फ़िलीपींस"), at(4, "वियतनाम"), at(4, "इंडोनेशिया")]; S[4]["t_at"] = at(4, "ये कारोबार")
S[5]["l_at"] = [0.6, at(5, "रूस की हाँ"), at(5, "और चीन")]
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S):
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
