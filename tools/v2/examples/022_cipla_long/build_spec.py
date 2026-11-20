import json
M = "media/022_cipla/"
CTA = "ऐसी ही छुपी कहानियों के लिए, Unknown Uncovered को अभी सब्सक्राइब और फ़ॉलो करें।"
SSA = ["NG", "ET", "CD", "TZ", "KE", "UG", "AO", "MZ", "MW", "ZM", "ZW", "BW", "NA", "ZA", "LS", "SZ", "CM", "CF", "TD", "SS", "SD", "RW", "BI",
       "GA", "CG", "GQ", "GH", "CI", "BF", "ML", "NE", "SN", "GN", "SL", "LR", "TG", "BJ", "GW", "GM", "MG", "SO", "ER", "DJ", "MR"]
S = []
def add(**k): S.append(k)

add(type="ll_hook", hit_at=4.0, title=["ONE INDIAN COMPANY", "vs BIG PHARMA"],
    vo="एक भारतीय कंपनी ने दुनिया की सबसे बड़ी दवा कंपनियों को कैसे हरा दिया? ये कहानी है, एक गोली की, एक क़ानून की, और एक ज़िद की। एक ऐसी ज़िद, जिसने करोड़ों लोगों की ज़िंदगी बदल दी।")
add(type="ll_globe", chap="01 · A DEADLY PRICE", highlight=SSA, view=[0, 20], kicker="THE YEAR 2000", big="~2 MILLION", lines=["deaths from AIDS every year", "epicentre: sub-Saharan Africa"],
    vo="बात है सन दो हज़ार की। उस वक़्त एड्स दुनिया का सबसे बड़ा स्वास्थ्य संकट था, और उसका केंद्र था अफ़्रीका। हर साल क़रीब बीस लाख लोग इससे अपनी जान गँवा रहे थे।")
add(type="ll_stat", kicker="AIDS TRIPLE THERAPY · USA & EUROPE", big="$10,000–15,000", lines=["per patient, per year", "for most of Africa: unaffordable"], icon="tag",
    vo="इलाज मौजूद था: तीन दवाओं का एक कॉकटेल, जो एचआईवी को रोक सकता था। पर अमेरिका और यूरोप में इसकी क़ीमत थी, हर मरीज़ के लिए दस से पंद्रह हज़ार डॉलर सालाना। अफ़्रीका के ज़्यादातर मरीज़ों के लिए, ये दाम मौत का फ़रमान था।")
add(type="ll_photo", img=M + "redribbon_2.jpg", kicker="PATENTED MEDICINE", big="NO COPIES", lines=["only the patent holder", "could make or sell it"],
    vo="इन दवाओं पर बड़ी विदेशी कंपनियों के पेटेंट थे, यानी कोई और इन्हें बना ही नहीं सकता था। लेकिन मुंबई में एक कंपनी थी, जिसकी कहानी आज़ादी की लड़ाई से शुरू होती है।")
add(type="ll_date", chap="02 · A GANDHIAN CHEMIST", date=["17", "AUG", "1935"], label="CIPLA IS FOUNDED IN BOMBAY", sub="The Chemical, Industrial & Pharmaceutical Laboratories",
    vo="सत्रह अगस्त, उन्नीस सौ पैंतीस। रसायनशास्त्री ख़्वाजा अब्दुल हमीद ने बॉम्बे में एक छोटी सी कंपनी शुरू की: केमिकल, इंडस्ट्रियल एंड फ़ार्मास्युटिकल लैबोरेटरीज़, यानी सिप्ला। हमीद गांधीजी के अनुयायी थे, और उनका सपना था, भारत को दवाओं में आत्मनिर्भर बनाना।")
add(type="ll_date", date=["4", "JULY", "1939"], label="MAHATMA GANDHI VISITS CIPLA", sub="During World War II, Cipla supplied essential medicines",
    vo="चार जुलाई, उन्नीस सौ उनतालीस को, ख़ुद महात्मा गांधी सिप्ला की फ़ैक्ट्री देखने आए। दूसरे विश्वयुद्ध के दौरान सिप्ला ने ज़रूरी दवाएँ बनाईं, और ये छोटी सी कंपनी चल निकली।")
add(type="ll_notice", chap="03 · THE LAW THAT CHANGED EVERYTHING", kicker="1960s · INDIA", title="A HEART MEDICINE", lines=["Cipla makes it cheaply in India", "a British company sends a legal notice"],
    vo="उन्नीस सौ इकसठ में, संस्थापक के बेटे यूसुफ़ हमीद कंपनी में आए। उस दौर में भारत ज़्यादातर दवाएँ विदेशी कंपनियों से लेता था। जब सिप्ला ने दिल की एक दवा सस्ते में बनाई, तो एक ब्रिटिश कंपनी ने उसे क़ानूनी नोटिस भेज दिया।")
add(type="ll_quote", quote=["Should Indians be denied a", "life-saving drug because of", "the colour of their skin?"], who="Yusuf Hamied to PM Indira Gandhi (paraphrased)",
    vo="यूसुफ़ हमीद ने प्रधानमंत्री इंदिरा गांधी के सामने सीधा सवाल रखा: क्या भारतीयों को एक जान बचाने वाली दवा, सिर्फ़ इसलिए नहीं मिलनी चाहिए, क्योंकि उसे बनाने वालों को हमारी चमड़ी का रंग पसंद नहीं?")
add(type="ll_law", cards=[["BEFORE", ["the medicine itself was patented:", "no one else could make it"], True, [214, 48, 60]],
                          ["PATENTS ACT 1970", ["only the METHOD is patented, for 7 years:", "new method, same medicine, legal"], False, [0, 140, 130]]],
    vo="जवाब में आया पेटेंट क़ानून, उन्नीस सौ सत्तर, जो उन्नीस सौ बहत्तर में लागू हुआ। इसमें दवा पर नहीं, सिर्फ़ उसे बनाने के तरीक़े पर पेटेंट मिलता था, और वो भी सिर्फ़ सात साल के लिए। यानी नया तरीक़ा खोजो, और वही दवा पूरी तरह क़ानूनी तौर पर बनाओ।")
add(type="ll_photo", img="", kicker="1983–84 · VIKHROLI, MUMBAI", big="US FDA APPROVED", lines=["Cipla's factory: first in India", "approved to make medicine ingredients for the USA"],
    vo="इसी क़ानून ने भारतीय दवा उद्योग की नींव रखी। सिप्ला की विक्रोली फ़ैक्ट्री, दवा का कच्चा माल बनाने के लिए अमेरिकी एफ़डीए की मंज़ूरी पाने वाली भारत की पहली फ़ैक्ट्री बनी। भारत चुपचाप, दुनिया की फ़ार्मेसी बनने की तैयारी कर रहा था।")
add(type="ll_photo", chap="04 · THE OFFER IN BRUSSELS", img=M + "berlaymont_1.jpg", kicker="28 SEPTEMBER 2000", big="BRUSSELS", lines=["European Commission conference", "on AIDS, malaria, TB and poverty"],
    vo="अब लौटते हैं सन दो हज़ार में। कुछ एक्टिविस्ट्स यूसुफ़ हमीद से मिले और पूछा: क्या आप एड्स की दवा सस्ते में बना सकते हैं? हमीद ने हिसाब लगाया, और अट्ठाईस सितंबर को ब्रसेल्स में यूरोपीय आयोग के एक सम्मेलन में खड़े होकर ऐलान कर दिया।")
add(type="ll_price", steps=[["THE GOING PRICE", "$10,000+"], ["CIPLA IN BRUSSELS", "$800"]], kicker="TRIPLE THERAPY · PER PATIENT · PER YEAR", silence=True,
    vo="तीन दवाओं का कॉकटेल, सिर्फ़ आठ सौ डॉलर सालाना में! हॉल में सन्नाटा छा गया। दुनिया की बड़ी दवा कंपनियों के प्रतिनिधि वहीं बैठे थे, पर उस दिन किसी ने ये ऑफ़र नहीं लिया।")
add(type="ll_price", chap="05 · ONE DOLLAR A DAY", steps=[["BRUSSELS, 2000", "$800"], ["CIPLA TO DOCTORS WITHOUT BORDERS", "$350"]], kicker="7 FEBRUARY 2001", chip="LESS THAN $1 A DAY",
    vo="पर हमीद रुके नहीं। सात फ़रवरी दो हज़ार एक को, सिप्ला ने डॉक्टर्स विदाउट बॉर्डर्स को यही इलाज, सिर्फ़ तीन सौ पचास डॉलर सालाना में देने का ऐलान किया। यानी एक डॉलर रोज़ से भी कम! अफ़्रीकी सरकारों के लिए दाम रखा छह सौ डॉलर, जो कंपनी की लागत भर था।")
add(type="ll_pills", names=["STAVUDINE", "LAMIVUDINE", "NEVIRAPINE"], result="TRIOMUNE", lines=["3 medicines in 1 pill", "one tablet morning, one evening"],
    vo="और सिप्ला ने एक और कमाल किया: तीनों दवाओं को मिलाकर एक ही गोली बना दी, ट्रायोम्यून। अब मरीज़ को ढेर सारी गोलियाँ नहीं, बस एक गोली सुबह और एक शाम लेनी थी।")
add(type="ll_stamp", stamp="“PIRATE”", kicker="THE REACTION", lines=["what some called Cipla's chairman", "a British drugmaker questioned how long such low prices could last"],
    vo="बड़ी कंपनियाँ भड़क उठीं। हमीद को समुद्री डाकू तक कहा गया। एक ब्रिटिश दवा कंपनी ने सवाल उठाया, कि इतनी सस्ती दवा आख़िर कब तक चलेगी।")
add(type="ll_court", chap="06 · THE FIGHT", n=39, vs="vs SOUTH AFRICA", result="CASE DROPPED", date="19 APRIL 2001", kicker="39 DRUG COMPANIES sued to stop cheaper medicines",
    vo="उधर दक्षिण अफ़्रीका में, उनतालीस दवा कंपनियाँ वहाँ की सरकार पर मुक़दमा लड़ रही थीं, ताकि वो सस्ती दवाएँ न ला सके। पर दुनिया भर में विरोध हुआ, और उन्नीस अप्रैल दो हज़ार एक को, कंपनियों ने बिना शर्त केस वापस ले लिया।")
add(type="ll_doc", img=M + "doha2001_0.jpg", title="DOHA DECLARATION", date="14 NOVEMBER 2001", line="TRIPS “does not and should not prevent” countries from protecting public health",
    vo="उसी साल चौदह नवंबर को, क़तर के दोहा में, विश्व व्यापार संगठन के देशों ने एक ऐतिहासिक घोषणा की: पेटेंट के नियम, किसी देश को अपने लोगों की सेहत बचाने से नहीं रोक सकते।")
add(type="ll_chart", chap="07 · THE PRICE CRASH", title="TRIPLE THERAPY: PRICE PER PATIENT PER YEAR",
    bars=[["2000", 10000, "$10,000+"], ["SEP 2000", 800, "$800"], ["FEB 2001", 350, "$350"], ["OCT 2003", 140, "<$140"]], note="≈ 38 cents a day",
    vo="अब दाम गिरने लगे। दो हज़ार तीन में, सिप्ला और दूसरी भारतीय कंपनियों के साथ क्लिंटन फ़ाउंडेशन के एक समझौते में, एक साल का इलाज एक सौ चालीस डॉलर से भी कम का हो गया। यानी रोज़ क़रीब अड़तीस सेंट।")
add(type="ll_donut", share=0.87, share2=0.91, kicker="2008 · AIDS MEDICINES BOUGHT FOR POOR COUNTRIES", label="MADE IN INDIA", label2="CHILDREN'S AIDS MEDICINES",
    vo="दो हज़ार आठ तक, ग़रीब देशों के लिए ख़रीदी गई एड्स की सत्तासी प्रतिशत दवाएँ भारत में बनी थीं। बच्चों की एड्स दवाओं में तो ये हिस्सा इक्यानवे प्रतिशत था। दुनिया ने भारत को नाम दिया: विकासशील दुनिया की फ़ार्मेसी।")
add(type="ll_law", chap="08 · INDIA HOLDS THE LINE", cards=[["2005 · NEW RULES", ["India must grant patents", "on medicines again"], True, [214, 48, 60]],
                                                            ["SECTION 3(d)", ["no new patent for a small change", "to an old medicine"], False, [0, 140, 130]]],
    vo="दो हज़ार पाँच में, अंतरराष्ट्रीय समझौतों के चलते भारत को दवाओं पर फिर से पेटेंट देने पड़े। पर भारत ने अपने क़ानून में एक ख़ास धारा जोड़ी, तीन डी: किसी पुरानी दवा में छोटा सा बदलाव करके, नया पेटेंट नहीं मिलेगा।")
add(type="ll_photo", img=M + "sci_0.jpg", kicker="1 APRIL 2013 · SUPREME COURT OF INDIA", big="REJECTED", lines=["Novartis' patent on a cancer drug", "after a seven-year legal battle"],
    vo="इसी धारा के आधार पर, एक अप्रैल दो हज़ार तेरह को, भारत के सुप्रीम कोर्ट ने स्विट्ज़रलैंड की दिग्गज कंपनी नोवार्टिस की कैंसर दवा का पेटेंट ठुकरा दिया। सात साल की क़ानूनी लड़ाई के बाद, सस्ती दवाओं का रास्ता खुला रहा।")
add(type="ll_people", chap="09 · TODAY", **{"from": 7.6, "to": 32.1}, label="MILLION PEOPLE ON HIV TREATMENT", sub="7.6 million in 2010 · 32.1 million in 2025 (UNAIDS)",
    vo="आज दुनिया में तीन करोड़ इक्कीस लाख लोग एचआईवी का इलाज ले रहे हैं। दो हज़ार दस में ये गिनती सिर्फ़ छिहत्तर लाख थी। और इस बदलाव की नींव में हैं, भारत की सस्ती दवाएँ।")
add(type="ll_outro", lines=["A Gandhian chemist's small lab.", "A bold law. A son's stubborn offer.", "Medicine for everyone."],
    vo="एक गांधीवादी केमिस्ट की छोटी सी लैब, एक साहसी क़ानून, और एक बेटे की ज़िद। इन तीनों ने साबित किया, कि जान बचाने वाली दवा सिर्फ़ अमीरों का हक़ नहीं। " + CTA)

spec = {"format": "long", "theme": "pharma", "tts": "parler", "speed": 1.05, "lead": 0.35, "tail": 0.5, "voice_job": "022_long",
        "globe_radius": 380,
        "header": "HOW AN INDIAN COMPANY BEAT BIG PHARMA",
        "source": "Sources: MSF · Nature · WTO · Clinton Foundation · J Int AIDS Soc · Supreme Court of India · UNAIDS · Cambridge Business History Review",
        "ticker": "  CIPLA · MUMBAI · SINCE 1935   ///   7 FEB 2001: AIDS TRIPLE THERAPY FOR $350 A YEAR   ///   DOHA DECLARATION · 14 NOV 2001   ///   2008: 87% OF DONOR-FUNDED AIDS MEDICINES MADE IN INDIA   ///   32.1 MILLION ON HIV TREATMENT (2025)   ///",
        "scenes": S}
json.dump(spec, open("spec.json", "w"), ensure_ascii=False, indent=1)
print(len(S), "scenes", sum(len(x["vo"]) for x in S), "chars")
