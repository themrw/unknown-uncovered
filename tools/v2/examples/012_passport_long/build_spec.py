import json
M="media/012_passport_long/"; P="media/011_passport/"
sc=[]
def add(**k): sc.append(k)
add(type="image", img=M+"tower_1.jpg", kicker="6 NOVEMBER 1914 · TOWER OF LONDON", lines=["A spy shot at dawn","He had entered Britain on someone else's passport"],
    vo="छह नवंबर उन्नीस सौ चौदह। लंदन का टावर। सुबह सुबह एक जर्मन जासूस को गोली मार दी गई। उसका असली नाम था कार्ल हांस लोडी, लेकिन ब्रिटेन में वो घूम रहा था, चार्ल्स इंगलिस नाम के एक अमेरिकी के पासपोर्ट पर।")
add(type="dossier", file="PASSPORT · USA", ref="CASE 1914", rows=[["ON PASSPORT","CHARLES A. INGLIS"],["REAL NAME","CARL HANS LODY"],["MISSION","WATCH THE BRITISH FLEET"],["FATE","SHOT · 6 NOV 1914"]],
    stamp="FAKE", kicker="THE PASSPORT TRICK", big="1914", lines=["Back then a passport proved little","Britain's own wasn't even made for a photo"],
    vo="उस दौर में पासपोर्ट से पहचान साबित करना आसान नहीं था। ब्रिटेन का अपना पासपोर्ट तो फ़ोटो लगाने के लिए बना ही नहीं था। लोडी के पकड़े जाने के कुछ ही महीनों बाद, एक फ़रवरी उन्नीस सौ पंद्रह को, ब्रिटेन ने अपना पहला पासपोर्ट जारी किया, जो फ़ोटो लगाने के लिए बनाया गया था।")
add(type="booklet", cover="PASSPORT", cover_sub="TRAVEL DOCUMENT", stamp="TEMPORARY", stamp_at=5.0, kicker="THE BOOK IN YOUR POCKET", big="TEMPORARY?", lines=["The world once called it a stopgap","and hoped to abolish it soon"],
    vo="आज वही छोटी सी किताब, हमारी जेब में दुनिया का दरवाज़ा है। लेकिन क्या आप जानते हैं, सौ साल पहले दुनिया के देशों ने इसे एक अस्थायी इंतज़ाम माना था, और उम्मीद की थी कि ये जल्द ख़त्म हो जाएगा? ये है पासपोर्ट की पूरी कहानी।")
add(type="disclaimer", min=9, lines=["Educational content only.","Dates and figures from official records, court judgments and published histories.","Some details of early documents are debated by historians."],
    vo="शुरू करने से पहले, ये वीडियो सिर्फ़ जानकारी के लिए है। सभी तारीख़ें और आँकड़े, सरकारी रिकॉर्ड, अदालती फ़ैसलों और प्रकाशित इतिहास से लिए गए हैं।")
# ch1
add(type="chapter", n=1, title="Kings' Letters", img=M+"safeconduct_2.jpg", min=4, vo="पहला अध्याय। राजाओं की चिट्ठियाँ।")
add(type="image", img=M+"safeconduct_2.jpg", kicker="SAFE CONDUCT · 1522", lines=["A ruler's letter: let this person pass","a favour for a few, not an ID for all"],
    vo="पासपोर्ट से पहले थी, सेफ़ कंडक्ट, यानी सुरक्षित यात्रा की चिट्ठी। कोई राजा लिखता था, कि इस व्यक्ति को बिना रोक-टोक जाने दिया जाए। ये पहचान पत्र नहीं, एक सिफ़ारिश थी, जो ज़्यादातर व्यापारियों, राजदूतों और ख़ास लोगों को मिलती थी।")
add(type="image", img=M+"safeconduct_1.jpg", kicker="ENGLAND · 1414", lines=["Safe conducts appear in an Act of Parliament","under King Henry V"],
    vo="इंग्लैंड में चौदह सौ चौदह में, राजा हेनरी पंचम के दौर में, ऐसी चिट्ठियों का ज़िक्र संसद के एक क़ानून में आया। इसे अक्सर पासपोर्ट का सबसे पुराना लिखित ज़िक्र कहा जाता है, हालाँकि इतिहासकार बताते हैं, कि ऐसी चिट्ठियाँ उससे पहले से दी जा रही थीं।")
add(type="image", img=M+"passport1800_0.jpg", kicker="FRANCE · 17TH CENTURY", lines=["'passe port'","to pass through a port or a city gate"],
    vo="फिर आया शब्द, पासपोर्ट। फ़्रांसीसी में पास, यानी गुज़रना, और पोर्ट, यानी बंदरगाह या शहर का दरवाज़ा। सत्रहवीं सदी में फ़्रांस के राजा लुई चौदहवें, अपने हस्ताक्षर वाली ऐसी चिट्ठियाँ देते थे।")
add(type="image", img=M+"passport1800_1.jpg", kicker="BRITAIN · 1846", lines=["Written in French","the bearer: just 'Gentilhomme Anglais'"],
    vo="उन्नीसवीं सदी तक भी पासपोर्ट बहुत सादा था। अठारह सौ छियालीस का एक ब्रिटिश पासपोर्ट फ़्रेंच भाषा में लिखा था, और धारक की पहचान के लिए उसमें बस दो शब्द थे, अंग्रेज़ सज्जन। न फ़ोटो, न क़द, न आँखों का रंग।")
# ch2
add(type="chapter", n=2, title="A World Without Papers", img=P+"ellis_0.jpg", min=4, vo="दूसरा अध्याय। बिना काग़ज़ों की दुनिया।")
add(type="image", img=P+"ellis_0.jpg", kicker="19TH CENTURY", lines=["Migration was 'generally speaking, unhindered'","International Labour Organization, 1922"],
    vo="आज ये सुनकर हैरानी होगी, लेकिन उन्नीसवीं सदी में ज़्यादातर लोग, बिना पासपोर्ट के देश बदल लेते थे। उन्नीस सौ बाईस की, अंतरराष्ट्रीय श्रम संगठन की एक रिपोर्ट के मुताबिक़, उस दौर में प्रवास पर आम तौर पर कोई रोक नहीं थी। हर व्यक्ति अपनी सुविधा से तय करता था, कब जाना है, कब पहुँचना है, और कब लौटना है।")
add(type="borders", lock_at=99, follow_at=99, lines=["Passports: a rare requirement in peacetime","exceptions: Russian & Ottoman frontiers"],
    vo="शांति के दिनों में, पासपोर्ट शायद ही कहीं माँगा जाता था। कुछ अपवाद ज़रूर थे, जैसे रूस और ऑटोमन साम्राज्य की सरहदें। लेकिन यूरोप का एक आम यात्री, ट्रेन पकड़ता, सरहद पार करता, और ज़्यादातर जगह किसी को कोई काग़ज़ नहीं दिखाना पड़ता।")
# ch3
add(type="chapter", n=3, title="The War That Locked the Doors", img=P+"trench_0.jpg", min=4, vo="तीसरा अध्याय। जंग, जिसने दरवाज़े बंद कर दिए।")
add(type="borders", lock_at=2.0, follow_at=9.0, lines=["Britain, France, Germany, Italy: mandatory","then neutral Spain, Denmark, Switzerland"],
    vo="उन्नीस सौ चौदह में पहला विश्व युद्ध छिड़ा, और सब बदल गया। जंग में सुरक्षा के डर से, ब्रिटेन, फ़्रांस, जर्मनी और इटली ने पासपोर्ट अनिवार्य कर दिया। जल्द ही स्पेन, डेनमार्क और स्विट्ज़रलैंड जैसे तटस्थ देश भी, इसी रास्ते पर चल पड़े।")
add(type="image", img=P+"trench_0.jpg", kicker="1 FEBRUARY 1915 · BRITAIN", lines=["A folded sheet in cardboard covers","photo, signature, and your face in words"],
    vo="ब्रिटेन का नया पासपोर्ट, गत्ते के कवर में मुड़ा हुआ एक काग़ज़ था। उसमें फ़ोटो, दस्तख़त, और धारक का पूरा हुलिया दर्ज होता। माथा कैसा है, नाक कैसी है, चेहरा कैसा है।")
add(type="image", img=P+"stamps_2.jpg", kicker="THE BRITISH WERE OFFENDED", lines=["Written details of their appearance","and then a photograph"],
    vo="कई ब्रिटिश नागरिकों को ये बेहद अपमानजनक लगा, कि सरकार उनके चेहरे का ब्योरा लिखे, और फिर फ़ोटो भी माँगे। लेकिन जंग चल रही थी, और नियम बना रहा।")
# ch4
add(type="chapter", n=4, title="Paris 1920: A Temporary Promise", img=P+"paris1920_0.jpg", min=4, vo="चौथा अध्याय। पेरिस, उन्नीस सौ बीस। एक अस्थायी वादा।")
add(type="booklet", cover="PASSPORT", cover_sub="INTERNATIONAL TYPE · 1920", open_at=9.0, pages=32, pages_at=13.5, dims_at=15.5,
    kicker="PARIS · 15–21 OCTOBER 1920", big="22 NATIONS", lines=["League of Nations conference","the first global passport standard"],
    vo="जंग ख़त्म हुई, लेकिन सरहदों की पाबंदियाँ नहीं हटीं। हर देश का पासपोर्ट अलग था। तब लीग ऑफ़ नेशंस ने, पंद्रह से इक्कीस अक्टूबर उन्नीस सौ बीस, पेरिस में एक सम्मेलन बुलाया, जिसमें बाईस देशों के प्रतिनिधि आए। वहाँ पहली बार, पासपोर्ट का एक अंतरराष्ट्रीय मानक तय हुआ। बत्तीस पन्नों की किताब, साढ़े पंद्रह बाय साढ़े दस सेंटीमीटर, गत्ते की जिल्द, कम से कम दो भाषाएँ, और शुरुआती पन्नों पर धारक का हुलिया, पेशा और पता।")
add(type="image", img=P+"paris1920_0.jpg", kicker="THE CONFERENCE'S OWN WORDS", lines=["Restrictions stay 'for the time being'","pre-war freedom hoped for 'in the near future'"],
    vo="लेकिन सबसे दिलचस्प बात, सम्मेलन ने ख़ुद लिखा, कि ये पाबंदियाँ फ़िलहाल के लिए हैं, और उम्मीद है कि जल्द ही, युद्ध से पहले जैसी आज़ादी धीरे धीरे लौट आएगी। यानी जिस पासपोर्ट को आज हम स्थायी मानते हैं, उसे बनाने वालों ने ख़ुद उसे अस्थायी समझा था।")
add(type="events", title="THE PROMISE THAT NEVER CAME",
    events=[["1920","PARIS","'for the time being'"],["1924","ROME","'abolish as soon as possible'"],["1947","UN EXPERTS","back to pre-1914? not now"],["1980","ICAO","machine-readable passport"],["2026","TODAY","still required at borders"]],
    vo="उन्नीस सौ चौबीस में, रोम के एक अंतरराष्ट्रीय सम्मेलन ने फिर कहा, पासपोर्ट की ज़रूरत जल्द से जल्द ख़त्म होनी चाहिए। उन्नीस सौ सैंतालीस में, संयुक्त राष्ट्र की एक तैयारी बैठक में पहला सवाल यही था, क्या उन्नीस सौ चौदह से पहले वाली व्यवस्था लौट सकती है? जवाब मिला, तभी, जब दुनिया के हालात भी वैसे हो जाएँ। और उन्नीस सौ अस्सी में तो उल्टा ही हुआ, अंतरराष्ट्रीय नागरिक उड्डयन संगठन ने, मशीन से पढ़े जाने वाले पासपोर्ट का मानक बना दिया। अस्थायी इंतज़ाम, अब दुनिया का स्थायी सिस्टम बन चुका था।")
# ch5
add(type="chapter", n=5, title="People Without a Country", img=M+"refugees_2.jpg", min=4, vo="पाँचवाँ अध्याय। जिनका कोई देश नहीं।")
add(type="image", img=M+"refugees_2.jpg", kicker="1921", lines=["~800,000 Russian refugees","stripped of citizenship"],
    vo="पासपोर्ट अनिवार्य हुआ, तो एक नई समस्या खड़ी हो गई। उन्नीस सौ इक्कीस में सोवियत सरकार ने, विदेश में रह रहे रूसियों की नागरिकता छीन ली। करीब आठ लाख शरणार्थी, एक झटके में बिना देश के हो गए। न पासपोर्ट, न किसी सरहद को पार करने का रास्ता।")
add(type="image", img=P+"nansen_0.jpg", kicker="JULY 1922 · GENEVA", lines=["The 'Nansen passport'","~450,000 issued · honoured by 52 countries"],
    vo="तब लीग ऑफ़ नेशंस के शरणार्थी आयुक्त, नॉर्वे के ध्रुवीय खोजकर्ता फ़्रिड्टयॉफ़ नानसेन ने, जुलाई उन्नीस सौ बाईस में जिनेवा में एक सम्मेलन बुलाया। वहीं बना, बिना देश वालों का पहला अंतरराष्ट्रीय यात्रा दस्तावेज़, जिसे नानसेन पासपोर्ट कहा गया। लगभग साढ़े चार लाख लोगों को ये मिला, और बावन देशों ने इसे मान्यता दी।")
add(type="image", img=P+"nansen_1.jpg", kicker="1938 · NOBEL PEACE PRIZE", lines=["Nansen International Office for Refugees","honoured for the Nansen passports"],
    vo="उन्नीस सौ अड़तीस में, नानसेन अंतरराष्ट्रीय शरणार्थी कार्यालय को, इन्हीं पासपोर्ट के लिए नोबेल शांति पुरस्कार मिला। आज शरणार्थियों को मिलने वाले यात्रा दस्तावेज़, इसी विचार से निकले हैं।")
# ch6
add(type="chapter", n=6, title="India's Passport Story", img=M+"indpass_0.jpg", min=4, vo="छठा अध्याय। भारत के पासपोर्ट की कहानी।")
add(type="dossier", file="INDIAN PASSPORT ACT", ref="ACT No. 34 OF 1920", img=M+"indpass_0.jpg",
    rows=[["BEFORE WWI","NO INDIAN PASSPORTS"],["ENACTED","9 SEPTEMBER 1920"],["FORMAT","LEAGUE OF NATIONS TYPE"]], stamp="ENACTED",
    kicker="BRITISH INDIA", big="1920", lines=["Passports become compulsory","a month before the Paris meeting"],
    vo="भारत में, पहले विश्व युद्ध से पहले, पासपोर्ट जारी करने का चलन ही नहीं था। नौ सितंबर उन्नीस सौ बीस को, अंग्रेज़ों ने इंडियन पासपोर्ट एक्ट बनाया, पेरिस बैठक से करीब एक महीना पहले। इससे भारत आने वालों के लिए पासपोर्ट ज़रूरी हुआ, और भारतीयों की विदेश यात्रा पर भी नियंत्रण आया। ब्रिटिश इंडियन पासपोर्ट, लीग ऑफ़ नेशंस वाले फ़ॉर्मेट पर ही बना था।")
add(type="image", img=M+"scindia_0.jpg", kicker="SUPREME COURT · 10 APRIL 1967", lines=["Satwant Singh Sawhney case","'personal liberty' includes the right to go abroad"],
    vo="आज़ादी के बाद भी, बीस साल तक, पासपोर्ट देने का कोई क़ानून ही नहीं था। पासपोर्ट मिलेगा या नहीं, ये पूरी तरह सरकार की मर्ज़ी पर था। फिर आया सतवंत सिंह साहनी का मामला, एक कारोबारी, जिनका पासपोर्ट वापस ले लिया गया था। दस अप्रैल उन्नीस सौ सड़सठ को, सुप्रीम कोर्ट ने बहुमत से कहा, कि अनुच्छेद इक्कीस की निजी स्वतंत्रता में, विदेश जाने का अधिकार भी शामिल है।")
add(type="dossier", file="THE PASSPORTS ACT, 1967", ref="ACT No. 15 OF 1967", img=M+"indpass_1.jpg",
    rows=[["WHY","SUPREME COURT RULING"],["IN FORCE FROM","5 MAY 1967"],["PURPOSE","A LAW FOR PASSPORTS"]], stamp="LAW",
    kicker="PARLIAMENT RESPONDS", big="1967", lines=["Travel abroad can be limited","only by a procedure set in law"],
    vo="यानी अब किसी नागरिक को विदेश जाने से, सिर्फ़ क़ानून के ज़रिए ही रोका जा सकता था। इसलिए संसद ने पासपोर्ट्स एक्ट, उन्नीस सौ सड़सठ बनाया, जो पाँच मई उन्नीस सौ सड़सठ से लागू माना गया। भारत में आज भी, पासपोर्ट इसी क़ानून के तहत बनते हैं।")
add(type="image", img=M+"scindia_2.jpg", kicker="1978 · MANEKA GANDHI v. UNION OF INDIA", lines=["A passport impounded in 1977","a landmark ruling on Article 21"],
    vo="दस साल बाद, उन्नीस सौ सतहत्तर में, मेनका गांधी का पासपोर्ट ज़ब्त किया गया, और मामला फिर सुप्रीम कोर्ट पहुँचा। जनवरी उन्नीस सौ अठहत्तर के इस फ़ैसले ने, अनुच्छेद इक्कीस की व्याख्या को और व्यापक बनाया, और इसे भारत के संवैधानिक इतिहास का एक ऐतिहासिक फ़ैसला माना जाता है।")
add(type="stat", kicker="INDIA · E-PASSPORT ERA", value=80, value_label="80 LAKH+", label="E-PASSPORTS ISSUED IN INDIA BY NOV 2025",
    items=[["28 MAY 2025","every new passport has a chip"],["2035","target: all passports chipped"],["1980","ICAO's first machine-readable standard"]],
    vo="और आज? अठाईस मई दो हज़ार पच्चीस से, भारत में बनने वाला हर नया पासपोर्ट, चिप वाला ई पासपोर्ट है। नवंबर दो हज़ार पच्चीस तक, देश में अस्सी लाख से ज़्यादा ई पासपोर्ट जारी हो चुके थे, और लक्ष्य है कि दो हज़ार पैंतीस तक, हर पासपोर्ट में चिप हो।")
# ch7
add(type="chapter", n=7, title="The Promise, Half-Kept", img=M+"schengen_0.jpg", min=4, vo="सातवाँ अध्याय। आधा निभाया गया वादा।")
add(type="image", img=M+"schengen_1.jpg", kicker="14 JUNE 1985 · SCHENGEN, LUXEMBOURG", lines=["5 countries agree to drop border checks","in force from 26 March 1995"],
    vo="तो क्या उन्नीस सौ बीस का वादा कभी पूरा हुआ? आधा। चौदह जून उन्नीस सौ पचासी को, लक्ज़मबर्ग के छोटे से गाँव शेंगेन में, पाँच देशों ने अपनी साझा सरहदों से जाँच हटाने का समझौता किया। छब्बीस मार्च उन्नीस सौ पचानवे से ये लागू हुआ, और आज यूरोप के बड़े हिस्से में, एक देश से दूसरे देश जाते वक़्त, आम तौर पर पासपोर्ट नहीं दिखाना पड़ता।")
add(type="image", img=M+"egate_0.jpg", kicker="BUT...", lines=["Free movement only inside the zone","at its outer borders, passports remain"],
    vo="लेकिन ये आज़ादी, सिर्फ़ उस इलाक़े के अंदर है। बाहर की सरहदों पर, पासपोर्ट और वीज़ा आज भी ज़रूरी हैं।")
add(type="image", img=M+"nepal_1.jpg", kicker="INDIA · NEPAL · BHUTAN", lines=["Direct travel without a passport","an accepted ID such as a voter ID works"],
    vo="और हमारे पड़ोस में भी, उस पुरानी आज़ादी की एक झलक बची है। भारतीय नागरिक, सीधे नेपाल या भूटान जाने के लिए, पासपोर्ट के बिना, वोटर आईडी जैसे मान्य पहचान पत्र से भी जा सकते हैं।")
add(type="outro", lines=["A 'temporary' rule, now 100+ years old.","Will the world ever travel freely again?","Tell us in the comments."],
    vo="राजाओं की चिट्ठियों से, एक जासूस की कहानी तक, और पेरिस के उस अस्थायी वादे से, आपकी जेब की चिप तक। पासपोर्ट, सौ साल से ज़्यादा पुराना एक अस्थायी नियम है। क्या दुनिया कभी फिर से बिना पासपोर्ट घूमेगी? कमेंट में अपनी राय ज़रूर बताइए। ऐसी ही छुपी कहानियों के लिए, अननोन अनकवर्ड को अभी सब्सक्राइब और फ़ॉलो करें।")
spec={"format":"long","theme":"history","look":"cinematic","grain":0.1,"tts":"parler","speed":1.0,"lead":0.35,"tail":0.6,
 "header":"THE PASSPORT: A 'TEMPORARY' RULE, 100+ YEARS OLD",
 "source":"Sources: League of Nations 1920 · ILO 1922 · UK Home Office · Supreme Court of India · MEA · UNHCR · EU",
 "ticker":"  1414: SAFE CONDUCTS   ///   1915: FIRST BRITISH PHOTO PASSPORT   ///   PARIS 1920: 22 NATIONS · 32 PAGES   ///   1922: NANSEN PASSPORT   ///   1967: RIGHT TO GO ABROAD (SC OF INDIA)   ///   1995: SCHENGEN   ///   2025: INDIA E-PASSPORTS   ///",
 "credits_from":["media/012_passport_long/credits.json","media/011_passport/credits.json"],"scenes":sc}
json.dump(spec,open("spec.json","w"),ensure_ascii=False,indent=1)
t=sum(len(c["vo"]) for c in sc); print(len(sc),"scenes",t,"chars ~",round(t/15.4+len(sc)*0.95),"s")
