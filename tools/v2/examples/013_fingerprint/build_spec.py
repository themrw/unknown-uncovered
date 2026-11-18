import json
M="media/013_fingerprint/"
sc=[
 dict(type="fingerprint", seed=7, scan_at=0.8, match_at=8.0, left_label="ALMANAC · 1898", right_label="RECORD: EX-CONVICT", stamp="MATCH",
      kicker="1898 · A TEA GARDEN IN BENGAL", lines=["No witness. Just a thumbprint.","and a match among thousands of cards"],
      vo="अठारह सौ अट्ठानवे, बंगाल का एक चाय बागान। मैनेजर का गला कटा मिला, और कोई गवाह नहीं। बस एक कैलेंडर पर, ख़ून से सना अंगूठे का एक निशान। और हज़ारों रिकॉर्ड कार्ड में से, उस निशान का मिलान हो गया।"),
 dict(type="photo", img=M+"writers_0.jpg", dark=0.35, kicker="12 JUNE 1897 · CALCUTTA", big="WORLD'S FIRST", lines=["Fingerprint Bureau, Writers' Building","built on the work of two Indian policemen"],
      vo="ये मुमकिन हुआ, कलकत्ता के राइटर्स बिल्डिंग में बने, दुनिया के पहले फ़िंगरप्रिंट ब्यूरो से। और इसके पीछे थे, बंगाल पुलिस के दो भारतीय सब-इंस्पेक्टर।"),
 dict(type="dossier", file="ANTHROPOMETRIC BUREAU", ref="CALCUTTA · 1890s",
      rows=[["SUB-INSPECTOR","AZIZUL HAQUE"],["STUDIED","MATHS & SCIENCE"],["SUB-INSPECTOR","HEM CHANDRA BOSE"],["THE TASK","FIND 1 CARD IN 1,000s"]],
      stamp="ASSIGNED", kicker="THE TWO MEN", lines=["Their boss: Edward Henry, IG of Police","the problem: searching thousands of records"],
      vo="अज़ीज़ुल हक़, जिन्होंने प्रेसिडेंसी कॉलेज में गणित और विज्ञान पढ़ा था, और हेमचंद्र बोस, एक डाकिए के बेटे। उनके अफ़सर एडवर्ड हेनरी ने उन्हें एक मुश्किल काम दिया, हज़ारों अपराधियों के उंगलियों के निशान, ऐसे सजाओ, कि कोई भी कार्ड जल्दी ढूँढ़ा जा सके।"),
 dict(type="drawers", kicker="THE HAQUE–BOSE FORMULA", whorls=[1,4,7], lines=["Find the drawer, not the needle","by 1897: about 7,000 cards on file"],
      vo="जवाब निकला गणित से। दस उंगलियों के पाँच जोड़े बने, और जिस उंगली पर भँवर जैसा गोल निशान हो, उसे मिला एक नंबर, सोलह, आठ, चार, दो या एक। इन नंबरों से बनता एक भिन्न, और हर भिन्न का अपना दराज़। कुल एक हज़ार चौबीस दराज़। अठारह सौ सत्तानवे तक, हक़ ऐसे सात हज़ार कार्ड जमा कर चुके थे।"),
 dict(type="photo", img=M+"teagarden_0.jpg", dark=0.35, kicker="1898 · KANGALI CHARAN CASE", big="CONVICTED", lines=["no eyewitness to the murder","theft proven by a thumbprint"],
      vo="कैलेंडर वाला निशान मिला, कंगाली चरण नाम के एक पुराने नौकर से। क़त्ल का कोई चश्मदीद नहीं था, इसलिए अदालत ने उसे चोरी का दोषी माना। ब्रिटिश साम्राज्य में, फ़िंगरप्रिंट सबूत पर सज़ा के, ये सबसे शुरुआती मामलों में गिना जाता है।"),
 dict(type="spread", origin=["CALCUTTA",22.57,88.36], year0="1897",
      routes=[["LONDON",51.5,-0.13,1.0,None,"1901"],["SOUTH AFRICA",-26.2,28.0,3.6,None,"1900s"],["USA",40.7,-74.0,4.6,"LONDON",""]],
      kicker="CALCUTTA → THE WORLD", lines=["Scotland Yard adopts it in 1901","then the English-speaking world"],
      vo="फिर ये तरीक़ा लंदन पहुँचा। उन्नीस सौ एक में स्कॉटलैंड यार्ड ने इसे अपनाया, और जल्द ही ये अंग्रेज़ी बोलने वाली दुनिया का मानक बन गया। नब्बे के दशक तक, कंप्यूटर वाले फ़िंगरप्रिंट सिस्टम भी, इसी वर्गीकरण पर टिके थे।"),
 dict(type="dossier", file="HENRY CLASSIFICATION SYSTEM", ref="1897",
      rows=[["NAMED AFTER","SIR EDWARD HENRY"],["MATHS","AZIZUL HAQUE"],["TABLES & TESTS","HEM CHANDRA BOSE"],["LATER REWARD","Rs 5,000 EACH + TITLES"]],
      stamp="CREDIT?", kicker="BUT WHOSE NAME?", lines=["Khan Bahadur & Rai Bahadur titles came later","the name stayed: 'Henry'"],
      vo="लेकिन इस सिस्टम का नाम पड़ा, हेनरी क्लासिफ़िकेशन सिस्टम। बाद में दोनों भारतीयों को, पाँच पाँच हज़ार रुपये का इनाम, और ख़ान बहादुर और राय बहादुर की उपाधियाँ मिलीं। पर दुनिया आज भी, इसे एक अंग्रेज़ अफ़सर के नाम से जानती है।"),
 dict(type="outro", lines=[["Next time you unlock your phone,","WHITE"],["remember Haque & Bose.","accent"]],
      vo="अगली बार जब अंगूठे से फ़ोन खोलें, तो इन दो नामों को याद कीजिए, अज़ीज़ुल हक़ और हेमचंद्र बोस। ऐसी ही छुपी कहानियों के लिए, अननोन अनकवर्ड को अभी सब्सक्राइब और फ़ॉलो करें।"),
]
spec={"format":"story","theme":"forensic","look":"cinematic","grain":0.1,"tts":"parler","speed":1.0,"lead":0.2,"tail":0.4,
 "header":"TWO INDIAN POLICEMEN BEHIND THE WORLD'S FINGERPRINT SYSTEM",
 "source":"Sources: Britannica · Bengal CID · E. R. Henry (1913) · West Bengal Police · published histories",
 "ticker":"  12 JUNE 1897: WORLD'S FIRST FINGERPRINT BUREAU, CALCUTTA   ///   1,024 PRIMARY GROUPS   ///   1898: KANGALI CHARAN CASE   ///   1901: SCOTLAND YARD   ///",
 "credits_from":["media/013_fingerprint/credits.json"],"scenes":sc}
json.dump(spec,open("spec.json","w"),ensure_ascii=False,indent=1)
t=sum(len(c["vo"]) for c in sc); print(t,"chars ~",round(t/15.4+len(sc)*0.6),"s")
