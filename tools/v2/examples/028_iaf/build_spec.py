import json
CTA = "ऐसी ही छुपी कहानियों के लिए, Unknown Uncovered को अभी सब्सक्राइब और फ़ॉलो करें।"
M = "media/028_iaf/"
SAYMAP = {"आई-ए-एफ़": "IAF", "एल-ए-सी": "LAC"}
spec = {
 "format": "story", "theme": "war", "tts": "parler", "speed": 1.08, "lead": 0.2, "tail": 0.35, "voice_job": "028_v2",
 "punch": True, "captions": True, "caption_y": 1520, "siren": [0, 3, 7],
 "header": "WHY JETS ROARED OVER NORTH INDIA", "source": "Reports: NewsBytes · Indian Defence News · Tribune · All India Radio", "ticker": "",
 "credits_from": [M + "credits.json"],
 "scenes": [
  {"type": "photo", "img": M + "su30_1.jpg", "cap_y": 860, "cap_lead": 1.0, "dark": 0.3, "kicker": "CHANDIGARH · MOHALI · UTTARAKHAND", "big": "WHY THE ROAR?", "lines": ["fighter jets, again and again", "near the China border: what's going on?"],
   "vo": "चंडीगढ़, मोहाली और उत्तराखंड के आसमान में, लड़ाकू विमानों की गड़गड़ाहट, बार-बार। लोग पूछने लगे, क्या कुछ बड़ा होने वाला है? चीन सीमा के पास, आख़िर हो क्या रहा था?"},
  {"type": "photo", "img": M + "himalaya_0.jpg", "cap_y": 860, "dark": 0.3, "kicker": "13–21 NOVEMBER 2026", "big": "9-DAY AIR EXERCISE", "lines": ["near the LAC, Middle Sector (Uttarakhand)", "airspace across J&K, Ladakh, HP & Punjab"],
   "vo": "तेरह से इक्कीस नवंबर तक, भारतीय वायुसेना ने, चीन से लगी वास्तविक नियंत्रण रेखा के मध्य सेक्टर, यानी उत्तराखंड के पास, नौ दिन का बड़ा हवाई अभ्यास किया। रिपोर्ट्स के मुताबिक, इसका हवाई दायरा, जम्मू-कश्मीर, लद्दाख, हिमाचल और पंजाब तक फैला था।"},
  {"type": "photo", "img": M + "rafale_0.jpg", "cap_y": 860, "dark": 0.3, "kicker": "REPORTED IN THE EXERCISE", "big": "SUKHOI · RAFALE · TEJAS", "lines": ["plus transport aircraft", "and helicopters"],
   "vo": "इसमें सुखोई-तीस, राफेल, और स्वदेशी तेजस जैसे फ़्रंटलाइन लड़ाकू विमान, और साथ में, ट्रांसपोर्ट विमान और हेलिकॉप्टर शामिल बताए गए।"},
  {"type": "dossier", "file": "LAC // EASTERN LADAKH", "ref": "GALWAN", "stamp": "20 MARTYRED",
   "rows": [["DATE", "15 JUNE 2020"], ["PLACE", "GALWAN VALLEY, LADAKH"], ["KILLED", "20 INDIAN SOLDIERS"], ["HOW", "HAND-TO-HAND, NO SHOTS"], ["AFTER", "~50,000 TROOPS EACH SIDE"]],
   "vo": "और ये अभ्यास, ऐसी सीमा पर हुआ, जहाँ ख़तरा कोई कहानी नहीं। पंद्रह जून दो हज़ार बीस को, लद्दाख की गलवान घाटी में, चीनी सैनिकों से हिंसक झड़प में, बीस भारतीय जवान शहीद हुए। उसके बाद, दोनों देशों ने, लगभग पचास-पचास हज़ार सैनिक, टैंक और तोपें, सीमा पर उतार दीं।"},
  {"type": "photo", "img": M + "tejas_0.jpg", "cap_y": 860, "dark": 0.3, "kicker": "WHY SO LOUD IN CHANDIGARH?", "big": "AIRBASE COUNTRY", "lines": ["Chandigarh, Ambala, Halwara, Adampur, Pathankot", "the same bases were active in Operation Sindoor (May 2025)"],
   "vo": "और चंडीगढ़-मोहाली में इतनी आवाज़ क्यों? क्योंकि ये इलाक़ा, वायुसेना के कई बड़े एयरबेस से घिरा है: चंडीगढ़, अंबाला, हलवारा, आदमपुर, पठानकोट। मई दो हज़ार पच्चीस में, ऑपरेशन सिंदूर के दौरान, यही एयरबेस, जवाबी कार्रवाई के केंद्र में थे। और अभ्यास के दिनों में, यहाँ से उड़ानें, और बढ़ जाती हैं।"},
  {"type": "photo", "img": M + "himalaya_1.jpg", "cap_y": 860, "dark": 0.35, "kicker": "THE REAL CHALLENGE", "big": "THIN AIR", "lines": ["less engine thrust at high altitude", "less agility: so pilots train right here"],
   "vo": "पर असली चुनौती, पहाड़ों में है। ऊँचाई पर हवा पतली होती है, जिससे इंजन की ताक़त, और विमान की फुर्ती, दोनों घट जाती हैं। इसलिए पायलटों को, इन्हीं हालात में, अभ्यास करना पड़ता है।"},
  {"type": "photo", "img": M + "c295_0.jpg", "cap_y": 860, "dark": 0.3, "kicker": "UTTARKASHI · NEAR THE CHINA BORDER", "big": "CHINYALISAUR", "lines": ["advanced landing ground in the making", "for transport aircraft like this C-295"],
   "vo": "उत्तरकाशी का, चिन्यालीसौड़ हवाई अड्डा, चीन सीमा के क़रीब होने के कारण, वायुसेना के लिए ख़ास है, और इसे, एडवांस्ड लैंडिंग ग्राउंड के रूप में, विकसित किया जा रहा है।"},
  {"type": "photo", "img": M + "rafale_1.jpg", "cap_y": 860, "dark": 0.35, "kicker": "IS WAR COMING?", "big": "READY FOR ANYTHING", "lines": ["no public sign of a new clash; drill ended 21 Nov", "but Galwan showed how fast things can change"],
   "vo": "तो क्या जंग का ख़तरा है? सार्वजनिक जानकारी में, अभी किसी नए टकराव का संकेत नहीं, और ये अभ्यास, इक्कीस नवंबर को पूरा हो चुका है। पर गलवान ने दिखा दिया था, कि पहाड़ों में हालात, एक रात में बदल सकते हैं। इसीलिए, आसमान में ये तैयारी।"},
  {"type": "outro", "min": 7.5, "highlight": ["IN"], "lines": [["The roar overhead?", "WHITE"], ["Readiness.", "alert"]],
   "vo": "तो अगली बार, आसमान में गड़गड़ाहट सुनें, तो समझिए, कोई हमारी सरहद पर, जाग रहा है। क्या आपने अपने शहर में, जेट देखे? कमेंट में बताइए। " + CTA},
 ],
}
for sc in spec["scenes"]:
    c = sc["vo"]
    for a, b in SAYMAP.items(): c = c.replace(a, b)
    sc["caption"] = c
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
n = sum(len(x["vo"]) for x in spec["scenes"]); print(n, "chars ≈", round(n / 15.5 + len(spec["scenes"]) * 0.55), "s")
