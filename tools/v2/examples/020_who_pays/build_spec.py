import json, os
M = "media/019_peace/"; M2 = "media/019b_peace/"
CTA = "ऐसी ही छुपी कहानियों के लिए, Unknown Uncovered को अभी सब्सक्राइब और फ़ॉलो करें।"
PAY5 = ["US", "CN", "JP", "DE", "GB"]; SA4 = ["IN", "NP", "BD", "PK"]
spec = {
 "theme": "peace", "tts": "parler", "speed": 1.08, "lead": 0.2, "tail": 0.35, "voice_job": "020_main",
 "header": "WORLD PEACE: WHO PAYS, WHO SERVES?",
 "source": "Source: UN scale of assessments 2025-27 (A/79/318/Add.1) · UN DPO data 31 Jul 2026 · UN fatalities data · Reuters",
 "ticker": "  TOP 5 PAYERS: 67% OF THE BILL, 4.7% OF THE SOLDIERS   ///   INDIA, NEPAL, BANGLADESH, PAKISTAN: 0.25% OF THE BILL, 33% OF THE SOLDIERS   ///   DEATHS SINCE 2000: 77 vs 422   ///",
 "scenes": [
  {"type": "hook", "min": 4.5, "file": ["> FILE 020 // THE PEACE BILL", "> SOURCE: UN DATA 2026"],
   "title": [["WHO PAYS?", "WHITE"], ["WHO", "WHITE"], ["BLEEDS?", "accent"]], "title_at": 0.9,
   "blips": [[38, -97], [35, 103], [36, 138], [51, 10], [54, -2], [22, 79], [28, 84], [24, 90]],
   "vo": "शांति सेना का दो-तिहाई पैसा, सिर्फ़ पाँच अमीर देश देते हैं। पर उनके सैनिक? सौ में पाँच भी नहीं!"},
  {"type": "photo", "img": M + "bluehelmet_0.jpg", "kicker": "UN PEACEKEEPING BUDGET 2026-27", "big": "$5.1 B", "lines": ["a year, split by", "each country's wealth"], "dark": 0.3,
   "vo": "यूएन शांति सेना हर साल क़रीब पाँच अरब डॉलर ख़र्च करती है। ये बिल हर देश उसकी अमीरी के हिसाब से बाँटकर भरता है।"},
  {"type": "split", "title": "THE TOP 5 PAYERS", "kicker": "> US · CHINA · JAPAN · GERMANY · UK", "col_at": [0.8, 3.2],
   "cols": [{"flags": PAY5, "label": "OF THE BILL", "value": "67.3%", "frac": 0.673, "color": "gold", "sub": "pay this share"},
            {"flags": PAY5, "label": "OF SOLDIERS", "value": "4.7%", "frac": 0.047, "color": "accent", "sub": "2,128 of 44,819"}],
   "vo": "अमेरिका, चीन, जापान, जर्मनी और ब्रिटेन मिलकर सड़सठ प्रतिशत बिल भरते हैं। पर सैनिक? सिर्फ़ पौने पाँच प्रतिशत।"},
  {"type": "split", "title": "INDIA · NEPAL · BANGLADESH · PAKISTAN", "kicker": "> four South Asian neighbours", "col_at": [0.8, 3.0],
   "cols": [{"flags": SA4, "label": "OF THE BILL", "value": "0.25%", "frac": 0.01, "color": "gold", "sub": "pay this share"},
            {"flags": SA4, "label": "OF SOLDIERS", "value": "32.6%", "frac": 0.326, "color": "accent", "sub": "14,633 of 44,819"}],
   "vo": "और उल्टी तस्वीर: भारत, नेपाल, बांग्लादेश और पाकिस्तान, बिल का चौथाई प्रतिशत भी नहीं भरते, पर हर तीन में से एक सैनिक इन्हीं का है।"},
  {"type": "ledger", "title": "BILL SHARE vs SOLDIERS", "kicker": "> 2026", "hl": [4],
   "rows": [["US", "USA", "26.1%", 1.0, "17", 0.004], ["JP", "JAPAN", "6.9%", 0.265, "4", 0.001], ["CN", "CHINA", "23.8%", 0.91, "1,651", 0.385],
            ["IN", "INDIA", "0.22%", 0.008, "4,260", 0.994], ["NP", "NEPAL", "0.001%", 0.0, "4,285", 1.0]],
   "note": "Nepal pays almost nothing. Sends the most.",
   "vo": "अमेरिका छब्बीस प्रतिशत बिल देता है, पर उसके सिर्फ़ सत्रह सैनिक हैं। जापान के चार। और नेपाल? बिल का लगभग शून्य, पर सैनिक सबसे ज़्यादा।"},
  {"type": "split", "title": "PEACEKEEPERS KILLED SINCE 2000", "kicker": "> UN fatalities data, all causes", "col_at": [0.8, 2.6],
   "cols": [{"flags": PAY5, "label": "TOP 5 PAYERS", "value": "77", "frac": 0.18, "color": "gold", "sub": "US · CN · JP · DE · GB"},
            {"flags": SA4, "label": "SOUTH ASIA 4", "value": "422", "frac": 1.0, "color": "alert", "sub": "IN · NP · BD · PK"}],
   "vo": "और सबसे बड़ा फ़र्क यहाँ है: सन दो हज़ार से, पाँच सबसे बड़े दाताओं के सतहत्तर लोगों ने जान गँवाई, और इन चार दक्षिण एशियाई देशों के, चार सौ बाईस।"},
  {"type": "photo", "img": M2 + "in_unmiss_3.jpg", "kicker": "WHY THIS SPLIT?", "big": "PAY vs SERVE", "lines": ["UN repays each soldier's cost", "West stepped back after the 1990s"], "dark": 0.35,
   "vo": "ऐसा क्यों? यूएन हर सैनिक का ख़र्च हर महीने लौटाता है, और विकासशील सेनाओं को मिलता है तजुर्बा और इज़्ज़त। वहीं नब्बे के दशक में सोमालिया और बोस्निया के बाद, पश्चिमी देशों ने अपने सैनिक भेजना कम कर दिया।"},
  {"type": "photo", "img": M2 + "in_unmiss_0.jpg", "kicker": "UNPAID PEACEKEEPING DUES · APRIL 2026", "big": "$3.5 B", "lines": ["the biggest payer owes the most", "troop countries wait for their money"], "dark": 0.35,
   "vo": "और एक छुपा मोड़: अप्रैल दो हज़ार छब्बीस तक शांति सेना के साढ़े तीन अरब डॉलर बकाया थे, सबसे ज़्यादा अमेरिका पर। इसका बोझ उठाते हैं सैनिक भेजने वाले देश, जिनका पैसा देर से पहुँचता है।"},
  {"type": "outro", "min": 7.0, "highlight": ["IN", "NP", "BD", "PK"], "lines": [["Rich nations pay.", "WHITE"], ["South Asia", "WHITE"], ["serves.", "accent"]],
   "vo": "दुनिया की शांति का बिल अमीर देश भरते हैं, पर उसे निभाते हैं हमारे जवान। " + CTA},
 ],
 "thumb": {"hook": ["पैसा अमीर देश देते हैं,", "जान कौन देता है?"], "number": "67%", "number_label": "OF THE BILL · 5% OF SOLDIERS",
           "sticker": "भारत का हिस्सा?", "highlight": ["IN", "NP", "BD", "PK"], "view": [25, 75], "mystery": ["US", "CN", "IN"]},
}
os.makedirs("ig", exist_ok=True)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
ig = {k: v for k, v in spec.items() if k not in ("scenes", "thumb")}; ig["voice_job"] = "020_ig"
ig["scenes"] = [
 {"type": "hook", "min": 3.0, "file": ["> FILE 020 // THE PEACE BILL"], "title": [["WHO PAYS?", "WHITE"], ["WHO BLEEDS?", "accent"]], "title_at": 0.6,
  "blips": spec["scenes"][0]["blips"], "vo": "शांति सेना का दो-तिहाई पैसा, पाँच अमीर देश देते हैं।"},
 dict(spec["scenes"][3], vo="पर हर तीन में से एक सैनिक भारत, नेपाल, बांग्लादेश और पाकिस्तान का है, जो बिल का चौथाई प्रतिशत भी नहीं भरते।", col_at=[0.5, 2.0]),
 {"type": "outro", "card": "youtube", "min": 4.0, "highlight": ["IN", "NP", "BD", "PK"], "lines": [["Full story", "WHITE"], ["on YouTube", "accent"]],
  "vo": "और जान गँवाने में भी यही आगे हैं। पूरी वीडियो, यूट्यूब पर देखें।"},
]
json.dump(ig, open("ig/spec.json", "w"), ensure_ascii=False, indent=1)
for s in (spec, ig): print(sum(len(x["vo"]) for x in s["scenes"]), "chars")
