import json
s = json.load(open("spec.json")); d = json.load(open("vo/durs.json")); L = s.get("lead", 0.3)
def at(i, sub, off=0.0):
    vo = s["scenes"][i]["vo"]; j = vo.find(sub); assert j >= 0, (i, sub)
    return round(L + j / len(vo) * d[i] + off, 2)
S = s["scenes"]
S[0]["card_at"] = [at(0, "एक कंपनी, जिसने"), at(0, "एक क्यूआर"), at(0, "और एक ऐसी पाइपलाइन")]
S[2]["link_at"] = at(2, "आइडिया सीधा"); S[2]["addr_at"] = at(2, "ईमेल जैसा")
S[3]["price_at"] = at(3, "बाक़ी कंपनियों")
S[4]["town_at"] = at(4, "उसके लोग", -0.6); S[4]["chip_at"] = at(4, "कुछ ही हफ़्तों")
S[5]["split_at"] = at(5, "अक्टूबर दो हज़ार सोलह")
S[7]["chart_at"] = 0.5
S[8]["link_at"] = 1.0
S[9]["items_at"] = [at(9, "पहली बार"), at(9, "दुनिया के")]
S[10]["grow_at"] = at(10, "दो हज़ार सोलह सत्रह"); S[10]["visa_at"] = at(10, "और जून")
HI = {"Bhutan": "भूटान", "Singapore": "सिंगापुर", "France": "फ़्रांस", "UAE": "यूएई", "Sri Lanka": "श्रीलंका", "Mauritius": "मॉरीशस",
      "Nepal": "नेपाल", "Qatar": "क़तर", "Cambodia": "कंबोडिया", "Greece": "ग्रीस"}
for r in S[11]["routes"]: r[3] = at(11, HI[r[0]]); r[5] = None
S[11]["routes"].sort(key=lambda r: r[3]); S[11]["year0"] = "10+"
S[12]["photo_at"] = at(12, "एक शाम")
json.dump(s, open("spec.json", "w"), ensure_ascii=False, indent=1)
print({i: {k: v for k, v in sc.items() if k.endswith("_at")} for i, sc in enumerate(S)})
