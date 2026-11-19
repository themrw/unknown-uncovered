import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.4)
S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub)
    assert k >= 0, (i, sub)
    return round(lead + k / len(vo) * durs[i] + off, 2)
def D(i): return durs[i]

S[0]["title_at"] = at(0, "अज़ीज़ुल हक़")
S[1]["line_at"] = at(1, "एक बड़ी मुश्किल")
S[2]["panel_at"] = [at(2, "फ़्रांस"), at(2, "इंग्लैंड"), at(2, "अर्जेंटीना")]
S[3]["line_at"] = at(3, "अज़ीज़ुल हक़")
S[4]["line_at"] = at(4, "गणित में")
h = at(4, "एडवर्ड हेनरी", -1.5); S[4]["cast"][1]["walk"] = [h, h + 2.5]
b = at(4, "हेमचंद्र बोस", -1.5); S[4]["cast"][2]["walk"] = [b, b + 2.2]
S[5]["line_at"] = at(5, "बत्तीस कतारें"); S[5]["drawer_at"] = at(5, "सीधे वही दराज़"); S[5]["count_at"] = at(5, "सात हज़ार")
S[6]["bars_at"] = at(6, "तुलना"); S[6]["stamp_at"] = at(6, "ज़्यादा तेज़")
S[7]["line_at"] = at(7, "फ़िंगरप्रिंट ब्यूरो")
S[8]["cal_at"] = at(8, "कैलेंडर"); S[8]["line_at"] = at(8, "बस, एक")
S[9]["hit_at"] = at(9, "निशान मिल गया"); S[9]["line_at"] = at(9, "सिर्फ़ एक अंगूठे")
S[10]["line_at"] = at(10, "ईमेल से")
S[11]["line_at"] = at(11, "स्कॉटलैंड यार्ड")
r = S[12]["routes"]; r[0][3] = 0.8; r[1][3] = at(12, "अमेरिका"); r[2][3] = at(12, "अमेरिका", 1.0)
r[3][3] = at(12, "अंग्रेज़ी बोलने"); r[4][3] = at(12, "अंग्रेज़ी बोलने", 1.0)
S[13]["medal_at"] = at(13, "पाँच-पाँच"); S[13]["reveal_at"] = at(13, "अज़ीज़ुल हक़ ही")
S[14]["title_at"] = at(14, "क्या इसका नाम")
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print([round(d, 1) for d in durs], round(sum(durs), 1))
