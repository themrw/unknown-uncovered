import json, os
M = "media/017_upi/"
sc = []
def add(**k): sc.append(k)
add(type="duel", kicker="EVERY DAY IN INDIA", big="82 CRORE", big_label="UPI PAYMENTS A DAY (OCT 2026)",
    rows=[["UPI (India)", 82.2, "82 crore"], ["Visa (200+ countries)", 63.9, "64 crore"]], mystery=["CHEAP INTERNET", "THE QR CODE", "THE ROAD"],
    vo="आज भारत में हर दिन, क़रीब बयासी करोड़ यूपीआई पेमेंट होते हैं, दुनिया की सबसे बड़ी कार्ड कंपनी वीज़ा से भी ज़्यादा। पर दस साल पहले, इसी देश में, ज़्यादातर लोग चाय के दस रुपये भी नकद देते थे। तो सिर्फ़ दस साल में ये हुआ कैसे? इस कहानी में तीन किरदार हैं। एक कंपनी, जिसने इंटरनेट लगभग मुफ़्त कर दिया। एक क्यूआर कोड वाली कंपनी, जिसने देश की हर छोटी-बड़ी दुकान तक डिजिटल पेमेंट पहुँचाया। और एक ऐसी पाइपलाइन, जिसे आज दुनिया के दस से ज़्यादा देश अपना रहे हैं। और ये कहानी हम देखेंगे, एक छोटी सी चाय की दुकान से।")
add(type="stall", year="2016", props=["coins"], kicker="MEET RAJU · A FICTIONAL CHARACTER", big="2016",
    lines=["cash, coins, no change", "1 GB of mobile data ≈ ₹228"],
    vo="मिलिए राजू से। राजू असली इंसान नहीं, एक कहानी का किरदार है, पर उसकी कहानी करोड़ों दुकानदारों जैसी है। साल दो हज़ार सोलह। टपरी पर दिन भर छुट्टे पैसों की खनक। उसके पास एक सस्ता स्मार्टफ़ोन है, पर इंटरनेट किसी अमीरी से कम नहीं। एक जीबी डेटा, क़रीब दो सौ अट्ठाईस रुपये का। फ़ोन ज़्यादातर, बस कॉल के काम आता है।")
add(type="paynet", kicker="11 APRIL 2016 · NPCI · 21 BANKS", hub="UPI", address="raju@bank",
    lines=["any bank → any bank, in seconds, 24×7", "first full month (Aug 2016): ~90,000 payments"],
    vo="पर उसी साल, एक ऐसी चीज़ शुरू हुई, जिसकी तब ज़्यादा चर्चा भी नहीं हुई। ग्यारह अप्रैल दो हज़ार सोलह को, एनपीसीआई ने, सिर्फ़ इक्कीस बैंकों के साथ, यूपीआई का पायलट शुरू किया। आइडिया सीधा था। हर बैंक खाते का, ईमेल जैसा एक आसान पता हो, और किसी भी बैंक से किसी भी बैंक में, सेकंडों में पैसा पहुँचे, दिन हो या रात। पच्चीस अगस्त को ये आम लोगों के लिए खुला, और पहले पूरे महीने में, पूरे देश ने इससे सिर्फ़ क़रीब नब्बे हज़ार लेन-देन किए।")
add(type="jio", kicker="5 SEPTEMBER 2016 · JIO", p0=228, p1=8,
    lines=["7 new customers every second", "100 million users in 170 days"],
    vo="फिर कुछ ही दिन बाद, पाँच सितंबर को, एक तूफ़ान आया। जियो लॉन्च हुआ, और महीनों तक, कॉल भी मुफ़्त, और डेटा भी। जियो के मुताबिक़, वो हर सेकंड औसतन सात नए ग्राहक जोड़ रहा था, और सिर्फ़ एक सौ सत्तर दिनों में, दस करोड़ लोग जुड़ गए। बाक़ी कंपनियों को भी दाम गिराने पड़े, और एक जीबी डेटा, आठ रुपये के आसपास आ गया। राजू के फ़ोन में अब, इंटरनेट चौबीस घंटे चलता था। यूपीआई को सड़क मिल गई थी, अब बस, गाड़ियों की ज़रूरत थी।")
add(type="qrtown", img=M + "queue_0.jpg", kicker="8 NOVEMBER 2016 · 86% OF CASH WITHDRAWN", chip0=5, chip1=10,
    chip="PAYTM MERCHANTS (LAKH) · SEPT → NOV 2016", lines=["no machine, no rent: just a sticker"],
    vo="और फिर आई, आठ नवंबर दो हज़ार सोलह की रात। चलन की क़रीब छियासी प्रतिशत नकदी, एक झटके में बंद। राजू की दुकान पर छुट्टे का संकट। इसी वक़्त, एक कंपनी पहले से तैयार खड़ी थी, पेटीएम, जो सौ मिलियन डाउनलोड छूने वाला पहला भारतीय ऐप बन चुका था। उसके लोग गली-गली जाकर, दुकानों पर क्यूआर स्टिकर चिपकाने लगे। न मशीन, न किराया, बस एक कागज़ का स्टिकर। कुछ ही हफ़्तों में, पेटीएम के मर्चेंट, पाँच लाख से बढ़कर दस लाख हो गए। राजू की टपरी पर भी, एक स्टिकर लग गया।")
add(type="walletpipe", kicker="WALLET vs UPI · OCTOBER 2016", split=[96, 4],
    lines=["96 of every 100 online payments: wallets (one gateway's data)"],
    vo="पर एक बात कम लोग जानते हैं। उस वक़्त ज़्यादातर पैसा, एक वॉलेट में रहता था। पहले बैंक से वॉलेट में डालो, फिर ख़र्च करो। जबकि यूपीआई, सीधे एक बैंक खाते से दूसरे में पैसा भेजता था, बिना बीच के किसी डिब्बे के। अक्टूबर दो हज़ार सोलह में, एक पेमेंट गेटवे के आँकड़ों में, हर सौ में से छियानवे लेन-देन वॉलेट से थे, और सिर्फ़ चार यूपीआई से। लगता था, वॉलेट जीत चुके हैं।")
add(type="events", title="APPS ON ONE ROAD", events=[["2016", "PhonePe", "first big non-bank UPI app"], ["Dec 2016", "BHIM", "government UPI app"],
    ["Sept 2017", "Google Tez", "later Google Pay"], ["Nov 2017", "Paytm UPI", "joins the road"]],
    vo="पर कुछ नई कंपनियों ने, उल्टा दाँव खेला। उस वक़्त फ़्लिपकार्ट का फ़ोनपे, पहला बड़ा गैर-बैंक ऐप बना, जो पूरी तरह यूपीआई पर बना था। सितंबर दो हज़ार सत्रह में गूगल आया, तेज़ के साथ, जो बाद में गूगल पे बना। और नवंबर दो हज़ार सत्रह में, पेटीएम भी यूपीआई से जुड़ गया। अब मुक़ाबला ऐप्स के बीच था, पर सड़क, सबकी एक थी।")
add(type="soundbox", kicker="2019 · THE BOX THAT SPEAKS", say="₹10 प्राप्त हुए", chart=[["Aug 16", 0.0009], ["Nov 18", 0.52], ["Oct 19", 1.15]],
    lines=["Oct 2019: 1 billion UPI payments in a month", "alerts in 11 languages", "2020: UPI made free for shopkeepers"],
    vo="धीरे-धीरे, तस्वीर पलटने लगी। अक्टूबर दो हज़ार उन्नीस में, यूपीआई ने पहली बार, एक महीने में सौ करोड़ लेन-देन पार किए। उसी साल पेटीएम ने एक छोटी मशीन उतारी, साउंडबॉक्स। पैसा आते ही मशीन बोल उठती, कितने रुपये मिले। अब राजू को, भीड़ में ग्राहक का फ़ोन देखकर, पेमेंट जाँचने की ज़रूरत नहीं थी। ये मशीन आज ग्यारह भाषाओं में बोलती है, और कई दुकानदारों के लिए, भरोसे की आवाज़ बन गई। और दो हज़ार बीस से, दुकानदारों के लिए, यूपीआई से पैसा लेना, पूरी तरह मुफ़्त कर दिया गया।")
add(type="paynet", kicker="TODAY · MANY APPS, ONE ROAD", hub="UPI", apps=["PhonePe", "Google Pay", "Paytm", "BHIM", "+ BANK APPS"],
    banks=["700+ BANKS", "PUBLIC", "PRIVATE", "SMALL", "CO-OP"], lines=["1.5 crore shops on Paytm devices", "rivals launched their own soundboxes too"],
    vo="साउंडबॉक्स का आइडिया इतना चला, कि बाद में फ़ोनपे और गूगल पे ने भी, अपने साउंडबॉक्स उतारे। आज क़रीब डेढ़ करोड़ दुकानदार, पेटीएम की डिवाइस और सेवाओं से जुड़े हैं। और यूपीआई किसी एक कंपनी का बाज़ार नहीं। फ़ोनपे, गूगल पे, पेटीएम, भीम, और बहुत सारे बैंक ऐप, सब एक ही सड़क पर चलते हैं, और ग्राहक, जो चाहे वो ऐप चुन सकता है।")
add(type="festive", img=M + "diwali_0.jpg", kicker="OCTOBER 2026 · FESTIVE RECORD", value=25.47, unit="BILLION", label="UPI PAYMENTS IN ONE MONTH",
    items=[["₹1 lakh crore+", "average every single day"], ["≈ 49%", "of the world's real-time payments"]],
    vo="अक्टूबर दो हज़ार छब्बीस, त्योहारों का महीना। एक ही महीने में, पच्चीस अरब से ज़्यादा यूपीआई पेमेंट, और पहली बार, रोज़ाना का औसत, एक लाख करोड़ रुपये से ऊपर। दुनिया के लगभग आधे रियल-टाइम डिजिटल पेमेंट, अब अकेले भारत में होते हैं।")
add(type="growth", kicker="TEN YEARS OF UPI", v0=1.78, v1=24162, unit="CRORE PAYMENTS A YEAR", y0="2016-17", y1="2025-26",
    duel=[["UPI", 650], ["Visa", 639]], duel_label="MILLION PAYMENTS A DAY · JUNE 2025",
    vo="तो असली विजेता कौन? वो सड़क, जिस पर सब चलते हैं। यूपीआई किसी एक कंपनी का नहीं। आज इस पर, सात सौ से ज़्यादा बैंक जुड़े हैं। दो हज़ार सोलह सत्रह में, यूपीआई पर सिर्फ़ एक करोड़ अठहत्तर लाख लेन-देन हुए थे। दो हज़ार पच्चीस छब्बीस में, चौबीस हज़ार करोड़ से ज़्यादा, यानी क़रीब तेरह हज़ार गुना। और जून दो हज़ार पच्चीस में, रोज़ाना लेन-देन में, यूपीआई ने वीज़ा को भी पीछे छोड़ दिया, जो दो सौ से ज़्यादा देशों में चलता है।")
add(type="spread", origin=["India", 22, 79], year0="2021", kicker="INDIA'S DIGITAL SOFT POWER",
    routes=[["Bhutan", 27.5, 90.4, 0, None, 2021], ["Singapore", 1.35, 103.8, 0, None, 2023], ["France", 46.6, 2.3, 0, None, 2024],
            ["UAE", 24.4, 54.4, 0, None, 2024], ["Sri Lanka", 7.9, 80.7, 0, None, 2024], ["Mauritius", -20.2, 57.5, 0, None, 2024],
            ["Nepal", 28.0, 84.0, 0, None, 2024], ["Qatar", 25.3, 51.2, 0, None, 2025], ["Cambodia", 12.6, 104.9, 0, None, 2026],
            ["Greece", 39.0, 22.0, 0, None, 2026]],
    lines=["2023: a German minister pays a Bengaluru vegetable seller by UPI", "UPI is now live in 10+ countries"],
    vo="फिर ये कहानी, भारत की सीमाओं से बाहर निकली। अगस्त दो हज़ार तेईस में, जी-ट्वेंटी बैठक के लिए आए जर्मनी के डिजिटल मंत्री ने, बेंगलुरु में एक सब्ज़ी वाले को यूपीआई से पेमेंट किया, और जर्मन दूतावास ने लिखा, कि वो बेहद प्रभावित हुए। आज यूपीआई, भूटान, नेपाल, श्रीलंका, सिंगापुर, यूएई, क़तर, मॉरीशस, कंबोडिया, फ़्रांस और ग्रीस तक पहुँच चुका है। जो तकनीक कभी हम दूसरे देशों से लेते थे, आज भारत, वो दुनिया को दे रहा है। यही है, भारत की डिजिटल सॉफ़्ट पावर।")
add(type="stall", year="2026", props=["qr", "soundbox", "photo"], kicker="RAJU · TEN YEARS LATER", big="2026",
    lines=["the same QR, now at the Eiffel Tower"],
    vo="और राजू? उसकी टपरी पर, आज भी वही चाय बनती है, पर अब साउंडबॉक्स, दिन में सैकड़ों बार बोलता है। एक शाम, उसके फ़ोन पर एक फ़ोटो आती है। उसकी बेटी, जो पेरिस में पढ़ने गई है, एफ़िल टॉवर पर, अपने फ़ोन से यूपीआई का क्यूआर स्कैन कर रही है। जिस क्यूआर ने कभी राजू की टपरी बदली थी, वही आज, उसकी बेटी के साथ, दुनिया घूम रहा है।")
add(type="outro", lines=["Cheap internet built the road.", "The QR opened every shop.", "UPI connected everyone."],
    vo="तो भारत, दुनिया का सबसे बड़ा रियल-टाइम पेमेंट देश कैसे बना? सस्ते इंटरनेट ने रास्ता बनाया, क्यूआर ने दुकानों के दरवाज़े खोले, और यूपीआई ने, सबको एक सड़क पर ला दिया। आपके हिसाब से, यूपीआई अगले किस देश में पहुँचना चाहिए? कमेंट में ज़रूर बताइए। ऐसी ही छुपी कहानियों के लिए, Unknown Uncovered को अभी सब्सक्राइब और फ़ॉलो करें।")
old = json.load(open("spec.json")) if os.path.exists("spec.json") else {}
spec = {"format": "long", "theme": "money", "look": "cinematic", "tts": "parler", "speed": 1.0, "lead": 0.3, "tail": 0.6,
        "header": "HOW INDIA BUILT THE WORLD'S BIGGEST PAYMENT SYSTEM",
        "source": "Sources: NPCI · RBI · PIB · IMF · ACI Worldwide · company filings · Jio/TRAI data",
        "ticker": "  UPI: 25.47 BN PAYMENTS IN OCT 2026   ///   82 CRORE A DAY   ///   1.78 CRORE (FY17) → 24,162 CRORE (FY26)   ///   LIVE IN 10+ COUNTRIES   ///",
        "credits_from": [M + "credits.json"], "scenes": sc}
for k in ("voice_job", "thumb"):  # then run add_timing.py
    if k in old: spec[k] = old[k]
for s_ in sc:
    for r in s_.get("routes", []): r[5] = str(r[5])
sc[11]["routes"] = [r[:3] + [round(1.0 + i * 0.9, 1)] + r[4:] for i, r in enumerate(sc[11]["routes"])]
for i, s in enumerate(old.get("scenes", [])):
    if i < len(sc):
        for kk, v in s.items():
            if kk.endswith("_at") and kk not in sc[i]: sc[i][kk] = v
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print(sum(len(s["vo"]) for s in sc), [len(s["vo"]) for s in sc])
