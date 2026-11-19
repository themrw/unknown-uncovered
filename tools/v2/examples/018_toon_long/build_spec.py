import json, os
sc = []
def add(**k): sc.append(k)
H_, B_, HY = "haque", "bose", "henry"
add(type="toon", set="street", place="CALCUTTA · 1890s", title=["HAQUE", "& BOSE"],
    cast=[{"who": H_, "x0": 2100, "x1": 760, "walk": [0.3, 3.2], "talk": False}, {"who": B_, "x0": 2300, "x1": 1060, "walk": [0.5, 3.4]}],
    vo="लगभग सौ साल तक, स्कॉटलैंड यार्ड से लेकर अमेरिका तक, दुनिया भर की पुलिस ने, अपराधियों के फ़िंगरप्रिंट जिस तरीक़े से ढूँढ़े, उसके पीछे दो भारतीय दिमाग़ थे। कलकत्ता पुलिस के दो सब-इंस्पेक्टर, अज़ीज़ुल हक़ और हेमचंद्र बोस। ये उन्हीं की कहानी है।")
add(type="toon", set="office", place="BENGAL POLICE RECORDS · 1890s", line="Same criminal. New name. How do you know?",
    cast=[{"who": B_, "x0": 1250, "x1": 1250, "pose": "hold", "face": -1}],
    vo="अठारह सौ नब्बे का दशक। कलकत्ता, अंग्रेज़ों के भारत की राजधानी। पुलिस के दफ़्तरों में, अपराधियों के रिकॉर्ड के पहाड़ लगे थे। और एक बड़ी मुश्किल थी। जो अपराधी नाम बदलकर दोबारा पकड़ा जाए, उसे पहचानें कैसे?")
add(type="toon", set="measure", place="THE WORLD'S METHODS",
    panels=[["FRANCE", "measure the body", "calipers"], ["ENGLAND", "fingerprint patterns, 1892", "book"], ["ARGENTINA", "Vucetich's system", "card"]],
    cast=[{"who": "clerk", "x0": 520, "x1": 520, "pose": "measure", "face": 1}, {"who": "suspect", "x0": 760, "x1": 760}],
    vo="दुनिया कई तरीक़े आज़मा रही थी। फ़्रांस का तरीक़ा था, शरीर नापना। सिर, बाँहें, कान। पर वो धीमा था, और ज़रा सी ग़लती, ग़लत आदमी को दोषी बना देती। इंग्लैंड में, उंगलियों के निशानों के पैटर्न पर किताबें लिखी जा रही थीं, और अर्जेंटीना ने अपना एक तरीक़ा बनाया, जो दक्षिण अमेरिका में चला। सब जानते थे, कि हर इंसान के निशान अलग होते हैं। पर सवाल ये था, हज़ारों कार्डों में से, एक निशान को मिनटों में ढूँढ़ें कैसे?")
add(type="toon", set="river", place="KHULNA, BENGAL · 1870s", line="Azizul Haque, born 1872",
    vo="और यहीं, हमारी कहानी में आता है एक लड़का। अज़ीज़ुल हक़। अठारह सौ बहत्तर में, खुलना के एक गाँव में जन्म। बचपन में ही, एक नाव हादसे में, माँ-बाप दोनों चल बसे।")
add(type="toon", set="college", place="PRESIDENCY COLLEGE, CALCUTTA", line="A gift for mathematics",
    cast=[{"who": "student", "x0": -200, "x1": 700, "walk": [0.3, 3.5], "pose": "books"}, {"who": HY, "x0": 2150, "x1": 1300, "walk": [6.0, 8.5], "face": -1},
          {"who": B_, "x0": 2150, "x1": 1560, "walk": [9.5, 11.5], "face": -1}],
    vo="अकेला लड़का कलकत्ता पहुँचा, प्रेसिडेंसी कॉलेज में पढ़ा, और गणित में ऐसा चमका, कि कॉलेज के प्रिंसिपल ने ख़ुद, उसका नाम पुलिस प्रमुख एडवर्ड हेनरी को सुझाया। वहाँ उसकी मुलाक़ात हुई, हेमचंद्र बोस से, जो अठारह सौ नवासी से बंगाल पुलिस में थे, और गणित के उतने ही पक्के।")
add(type="toon", set="drawers", place="THE FORMULA · 1,024 DRAWERS", line="32 rows × 32 columns",
    cast=[{"who": H_, "x0": 560, "x1": 560, "pose": "point", "face": 1}, {"who": B_, "x0": 1500, "x1": 1500, "pose": "card", "face": -1}],
    vo="हेनरी ने उन्हें एक मुश्किल काम दिया। इन निशानों को ऐसे सजाओ, कि कोई भी कार्ड मिनटों में मिल जाए। हक़ ने एक गणितीय फ़ॉर्मूला बनाया। सोचिए एक लाइब्रेरी। हर किताब का एक शेल्फ़ नंबर हो, तो आप सीधे उसी शेल्फ़ पर जाते हैं। दसों उंगलियों के पैटर्न देखकर, हर कार्ड को एक नंबर मिलता। बत्तीस कतारें, बत्तीस खाने, कुल एक हज़ार चौबीस दराज़। नया कार्ड आए, तो बस उसका नंबर निकालो, और सीधे वही दराज़ खोलो। अठारह सौ सत्तानवे तक, हक़ की अलमारी में, सात हज़ार लोगों के निशान थे।")
add(type="toon", set="committee", place="THE TEST · 1897", bars=[["BODY MEASUREMENT", 0.45], ["FINGERPRINTS", 1.0]],
    vo="फिर आया इम्तिहान। सरकार की एक कमेटी ने, शरीर नापने वाले तरीक़े, और इस नए तरीक़े की तुलना की। फ़ैसला साफ़ था। उंगलियों के निशान, ज़्यादा तेज़, ज़्यादा सस्ते, और ज़्यादा भरोसेमंद।")
add(type="toon", set="writers", place="WRITERS' BUILDING · 12 JUNE 1897", line="Fingerprint Bureau: the first of its kind in the British Empire",
    cast=[{"who": H_, "x0": 700, "x1": 700, "face": 1}, {"who": B_, "x0": 1220, "x1": 1220, "face": -1}],
    vo="बारह जून अठारह सौ सत्तानवे को, सरकार ने मंज़ूरी दी, और कलकत्ता के राइटर्स बिल्डिंग में, फ़िंगरप्रिंट ब्यूरो शुरू हुआ, ब्रिटिश साम्राज्य में, अपनी तरह का पहला।")
add(type="toon", set="teagarden", place="JALPAIGURI · 1898", line="One clue: a thumb mark on a calendar",
    vo="अठारह सौ अट्ठानवे, जलपाईगुड़ी का एक चाय बागान। मैनेजर अपने कमरे में मृत मिला, और पैसे ग़ायब। कोई गवाह नहीं। बस, एक कैलेंडर पर, अंगूठे का एक धुँधला निशान।")
add(type="toon", set="court", place="THE FIRST BIG TEST IN COURT", line="Theft proved by a single thumbprint",
    cast=[{"who": H_, "x0": 520, "x1": 520, "pose": "card", "face": 1}, {"who": "judge", "x0": 1430, "x1": 1430, "face": -1}],
    vo="वो कैलेंडर कलकत्ता पहुँचा। फ़ॉर्मूले से दराज़ खुली, और निशान मिल गया। मैनेजर का पुराना नौकर, जो पहले भी चोरी में पकड़ा जा चुका था। अदालत में हत्या साबित नहीं हुई, पर चोरी, पक्के तौर पर साबित हुई, सिर्फ़ एक अंगूठे के निशान से।")
add(type="toon", set="telegraph", place="BOSE'S TELEGRAPHIC CODE · 1916", line="A thumbprint, sent as letters over the wire",
    cast=[{"who": B_, "x0": 700, "x1": 700, "pose": "tap", "face": 1}],
    vo="और हेमचंद्र बोस, यहीं नहीं रुके। उन्होंने ऐसा कोड बनाया, जिससे फ़िंगरप्रिंट की जानकारी, तार, यानी टेलीग्राफ़ से, दूसरे शहर भेजी जा सके। ईमेल से कई दशक पहले, एक अंगूठे का निशान, अक्षरों में बदलकर, सैकड़ों मील दूर पहुँच सकता था। ये कोड उन्होंने, उन्नीस सौ सोलह में प्रकाशित किया।")
add(type="toon", set="london", place="LONDON · 1901", line="Scotland Yard adopts the Calcutta system",
    cast=[{"who": HY, "x0": -200, "x1": 760, "walk": [0.4, 4.0], "pose": "file"}],
    vo="अब कलकत्ता का ये तरीक़ा, दुनिया की तरफ़ निकला। उन्नीस सौ एक में, लंदन के स्कॉटलैंड यार्ड ने, इसी सिस्टम पर अपना फ़िंगरप्रिंट ब्यूरो शुरू किया।")
add(type="spread", origin=["Calcutta", 22.6, 88.4], year0="1897", kicker="THE WORLD STANDARD FOR ~100 YEARS",
    routes=[["London", 51.5, -0.1, 1.0, None, "1901"], ["New York", 40.7, -74.0, 3.0, None, "1900s"], ["Ottawa", 45.4, -75.7, 4.2, None, "1900s"],
            ["Sydney", -33.9, 151.2, 5.4, None, "1900s"], ["Cape Town", -33.9, 18.4, 6.4, None, "1900s"]],
    lines=["used across the English-speaking world", "until computers took over"],
    vo="फिर अमेरिका, और अंग्रेज़ी बोलने वाली लगभग पूरी दुनिया ने इसे अपनाया। ये फ़िंगरप्रिंट रखने का अंतरराष्ट्रीय मानक बन गया, और कंप्यूटर आने तक, क़रीब सौ साल, दुनिया के रिकॉर्ड, इसी तरीक़े से सजाए जाते रहे।")
add(type="toon", set="credit", place="THE NAME ON THE SYSTEM",
    vo="पर इसका नाम पड़ा, हेनरी क्लासिफ़िकेशन सिस्टम, उनके अंग्रेज़ अफ़सर के नाम पर। सालों बाद, दोनों को पाँच-पाँच हज़ार रुपये का इनाम मिला, और ख़ान बहादुर और राय बहादुर की उपाधियाँ। और ख़ुद हेनरी ने बाद में लिखा, कि अज़ीज़ुल हक़ ही वो इंसान थे, जो इस नए विश्वव्यापी सिस्टम के लिए, सबसे ज़्यादा ज़िम्मेदार थे।")
add(type="toon", set="finale", place="CALCUTTA", title=["THE HAQUE–BOSE", "SYSTEM?"], title_at=8.0,
    cast=[{"who": H_, "x0": 1240, "x1": 1240, "face": 1}, {"who": B_, "x0": 1540, "x1": 1540, "face": -1}],
    vo="तो अगली बार, जब किसी फ़िल्म में फ़िंगरप्रिंट का मिलान देखें, तो याद कीजिए। सौ साल तक, दुनिया की पुलिस ने जिस अलमारी में अपराधियों के निशान सजाए, उसकी चाबी, कलकत्ता के दो भारतीयों ने बनाई थी। क्या इसका नाम, हक़-बोस सिस्टम होना चाहिए? कमेंट में ज़रूर बताइए। ऐसी ही छुपी कहानियों के लिए, Unknown Uncovered को अभी सब्सक्राइब और फ़ॉलो करें।")
old = json.load(open("spec.json")) if os.path.exists("spec.json") else {}
spec = {"format": "long", "theme": "history", "look": "cinematic", "tts": "parler", "speed": 0.95, "lead": 0.4, "tail": 1.0,
        "header": "THE TWO INDIANS BEHIND THE WORLD'S FINGERPRINT SYSTEM", "source": "Sources: Sengoopta, Beavan, Bengal Police records; Wikipedia biographies",
        "ticker": "", "scenes": sc}
for k in ("voice_job", "thumb"):
    if k in old: spec[k] = old[k]
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print(sum(len(s["vo"]) for s in sc), len(sc))
