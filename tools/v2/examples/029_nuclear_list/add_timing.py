import json
spec = json.load(open("spec.json")); durs = json.load(open("vo/durs.json")); lead = spec.get("lead", 0.2); S = spec["scenes"]
def at(i, sub, off=0.0):
    vo = S[i]["vo"]; k = vo.find(sub); assert k >= 0, (i, sub)
    return round(max(0.0, lead + k / len(vo) * durs[i] + off), 2)
S[0]["wrong_at"] = at(0, "तो आप", 0.0)
S[1]["env_at"] = at(1, "दोनों देश", -0.2); S[1]["coord_at"] = at(1, "और उसमें", 0.0)
S[2]["stamp_at"] = at(2, "पहली लिस्ट", 0.3)
S[3]["item_at"] = [at(3, "परमाणु बिजली", -0.2), at(3, "रिसर्च", -0.2), at(3, "यूरेनियम", -0.2), at(3, "ईंधन", -0.2), at(3, "री-प्रोसेसिंग", -0.2)]; S[3]["stamp_at"] = at(3, "पर ये लिस्ट", 0.2)
S[4]["row_at"] = [at(4, "कारगिल", -0.2), at(4, "सीमा पर", -0.2), at(4, "बालाकोट", -0.2), at(4, "या मई", -0.1)]
S[7]["right_at"] = at(7, "तो कुछ", -0.2)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
for i, s in enumerate(S):
    d = {k: v for k, v in s.items() if k.endswith("_at")}
    if d: print(i, s["type"], d)
