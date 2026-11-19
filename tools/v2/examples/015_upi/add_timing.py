import json
s = json.load(open("spec.json")); d = json.load(open("vo/durs.json")); L = s.get("lead", 0.2)
def at(i, sub, off=0.0):
    vo = s["scenes"][i]["vo"]; j = vo.find(sub); assert j >= 0, (i, sub)
    return round(L + j / len(vo) * d[i] + off, 2)
S = s["scenes"]
S[0]["count_at"] = at(0, "पच्चीस", -0.1); S[0]["pay_at"] = round(max(1.0, S[0]["count_at"] - 0.7), 2); S[0]["lines_at"] = at(0, "दुनिया")
S[1]["key_at"] = [at(1, "जियो"), at(1, "पेटीएम"), at(1, "तीसरी")]
S[2]["drop_at"] = at(2, "दो सौ", -0.2); S[2]["use_at"] = at(2, "इंटरनेट, हर", -0.2)
S[3]["qr_at"] = at(3, "दुकानों", -0.3); S[3]["count_at"] = at(3, "नोटबंदी")
S[4]["link_at"] = at(4, "जो हर बैंक", -0.2)
S[6]["hl_at"] = at(6, "बस आठ", -0.2); S[6]["chip_at"] = at(6, "दो हज़ार चौबीस")
json.dump(s, open("spec.json", "w"), ensure_ascii=False, indent=1)
print({i: {k: v for k, v in sc.items() if k.endswith("_at")} for i, sc in enumerate(S)})
