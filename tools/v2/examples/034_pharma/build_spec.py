import json
M = "media/034_pharma/"
S = [
 dict(type="ph_hook", bg=M+"pills_0.jpg", big="1 IN 5", l1="GENERIC MEDICINES ON EARTH", l2="ARE MADE IN INDIA", q="BUT WHERE DOES THE RAW MATERIAL COME FROM?",
      src="PIB, Govt of India", caption="दुनिया की हर पाँच में से एक जेनेरिक दवा, भारत बनाता है। पर क्या आप जानते हैं, उसका कच्चा माल कहाँ से आता है?",
      vo="दुनिया की हर पाँच में से एक जेनेरिक दवा, भारत बनाता है। पर क्या आप जानते हैं, उसका कच्चा माल कहाँ से आता है?"),
 dict(type="ph_flow", bg=M+"port_0.jpg", kicker="THE WORLD DEPENDS ON INDIA", rows=[["US", "UNITED STATES", 40, "40%"], ["ZA", "AFRICA", 50, "~50%"], ["GB", "UNITED KINGDOM", 25, "25%"]],
      foot="share of generic-medicine needs met by India · NITI Aayog", vo="अमेरिका की चालीस प्रतिशत, अफ़्रीका की करीब आधी, और ब्रिटेन की एक-चौथाई जेनेरिक दवाओं की ज़रूरत, भारत पूरी करता है।"),
 dict(type="ph_china", bg=M+"powder_0.jpg", kicker="BUT INDIA DEPENDS ON CHINA", n=74, lbl="OF INDIA'S API IMPORTS CAME FROM CHINA", sub="APIs, bulk drugs & intermediates · FY2024-25 · $4.35 bn",
      src="DGCIS / Ministry of Chemicals & Fertilizers", caption="पर इन दवाओं का असली तत्व, यानी API, जो भारत बाहर से मँगाता है, उसका करीब चौहत्तर प्रतिशत, चीन से आता है।",
      vo="पर इन दवाओं का असली तत्व, यानी ए-पी-आई, जो भारत बाहर से मँगाता है, उसका करीब चौहत्तर प्रतिशत, चीन से आता है।"),
 dict(type="ph_tb", bg=M+"sansad_0.jpg", file="RAJYA SABHA · 10 MARCH 2026", ref="WRITTEN REPLY · MoS CHEMICALS & FERTILIZERS",
      rows=[["RIFAMPICIN (TB) INTERMEDIATES", 100], ["METHYLDOPA (BP) INTERMEDIATES", 100], ["ERYTHROMYCIN", 98], ["PENICILLIN & SALTS", 93]], lbl="DEPENDENCE ON CHINA",
      vo="और सरकार ने, राज्यसभा में बताया, कि टीबी की दवा रिफ़ैम्पिसिन बनाने वाले कच्चे माल के लिए, भारत, सौ प्रतिशत चीन पर निर्भर है।"),
 dict(type="ph_end", bg=M+"factory_0.jpg", kicker="THE FIGHT BACK", big="₹6,940 CRORE", sub="PLI scheme · 41 key ingredients to be made in India", q="CAN INDIA BREAK THIS CHAIN?",
      vo="इसे बदलने के लिए, सरकार ने छह हज़ार नौ सौ चालीस करोड़ रुपये की योजना शुरू की है। क्या भारत ये निर्भरता तोड़ पाएगा? कमेंट में बताइए, और Unknown Uncovered को सब्सक्राइब करें।"),
]
spec = dict(format="story", theme="forensic", look="cinematic", speed=1.08, lead=0.0, tail=0.3, voice_job="034_main", punch=True, captions=True, caption_y=1540,
            siren=[], header="UNKNOWN UNCOVERED", source="Sources: PIB · NITI Aayog · DGCIS · Rajya Sabha (10 Mar 2026)", ticker="INDIA · PHARMACY OF THE WORLD",
            credits_from=[M + "credits.json"], scenes=S)
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print(sum(len(x["vo"]) for x in S))
