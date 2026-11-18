import json
M="media/014_fingerprint_long/"; P="media/013_fingerprint/"
sc=[]
def add(**k): sc.append(k)
add(type="fingerprint", seed=7, left_label="CALENDAR · 1898", right_label="RECORD SEARCH...", kicker="1898 · A TEA GARDEN, JALPAIGURI", big="WHOSE PRINT?", lines=["No witness. One thumbprint.","The answer was in Calcutta."],
    vo="अठारह सौ अट्ठानवे। बंगाल के जलपाईगुड़ी ज़िले का एक चाय बागान। सुबह मैनेजर अपने कमरे में मृत मिलता है, तिजोरी ख़ाली, और कोई गवाह नहीं। पुलिस के पास बस एक सुराग है, एक कैलेंडर पर, अंगूठे का एक धुँधला सा निशान। सवाल ये था, लाखों लोगों में, ये निशान किसका है? और इसका जवाब, कलकत्ता के एक दफ़्तर में, दो भारतीय पुलिसवालों के पास था।")
add(type="disclaimer", min=8, lines=["Educational content only.","Facts from court records, police histories and published research.","Fingerprint graphics and characters are illustrations."],
    vo="ये वीडियो सिर्फ़ जानकारी के लिए है। तथ्य अदालती रिकॉर्ड, पुलिस के इतिहास और प्रकाशित शोध से लिए गए हैं।")
add(type="image", img=M+"babylon_0.jpg", kicker="ANCIENT WORLD", lines=["Fingerprints pressed into clay and seals","China used them for identification by ~800 CE"],
    vo="लेकिन उस निशान तक पहुँचने के लिए, हमें बहुत पीछे जाना होगा। इंसान हज़ारों सालों से, मिट्टी की तख़्तियों और मुहरों पर, अपनी उंगलियों के निशान छोड़ता आया है। चीन में तो, लगभग आठ सौ ईसवी तक, पहचान के लिए उंगलियों के निशान इस्तेमाल होने लगे थे। पर कोई नहीं जानता था, कि ये निशान, हर इंसान में अलग क्यों होते हैं।")
add(type="events", title="THE RIDGES UNDER THE MICROSCOPE",
    events=[["1684","NEHEMIAH GREW","first paper on skin ridges"],["1788","J.C.A. MAYER","'no two alike'"],["1858","BENGAL","a handprint on a contract"]],
    vo="सत्रहवीं सदी में, वैज्ञानिकों ने इन लकीरों को माइक्रोस्कोप से देखना शुरू किया। सोलह सौ चौरासी में अंग्रेज़ डॉक्टर नेहेमायाह ग्रू ने इन पर पहला वैज्ञानिक लेख लिखा, और सत्रह सौ अठासी में जर्मन वैज्ञानिक मेयर ने पहली बार लिखा, कि दो इंसानों के निशान एक जैसे नहीं होते। पर ये बात किताबों में ही रह गई। इसे असली दुनिया में लाने वाली घटना, हुई भारत में।")
add(type="image", img=M+"herschel_0.jpg", kicker="28 JULY 1858 · JANGIPUR, BENGAL", lines=["William Herschel asks Rajyadhar Konai","for a handprint on a road contract"],
    vo="अठाईस जुलाई अठारह सौ अट्ठावन। बंगाल का जंगीपुर। ब्रिटिश अफ़सर विलियम हर्शेल, सड़क बनाने का एक ठेका कर रहे थे, राजाधर कोनाई नाम के एक व्यापारी के साथ। हर्शेल को डर था, कि कोनाई बाद में अपने दस्तख़त से मुकर सकता है। इसलिए उन्होंने कहा, काग़ज़ पर अपनी पूरी हथेली की छाप लगाओ।")
add(type="image", img=M+"herschel_1.jpg", kicker="HERSCHEL'S HABIT", lines=["Prints instead of signatures","but not yet for catching criminals"],
    vo="उस दिन ये बस एक एहतियात थी, पर हर्शेल को इसमें कुछ और दिखा। आगे चलकर वो ठेकों पर, लोगों की उंगलियों के निशान लेने लगे, और अपने ख़ुद के निशान भी सालों तक दर्ज करते रहे, ये देखने के लिए, कि लकीरें बदलती हैं या नहीं। पर उन्होंने इनका इस्तेमाल, दस्तख़त की तरह किया, अपराधी पकड़ने के लिए नहीं।")
add(type="image", img=M+"tsukiji_0.jpg", kicker="TOKYO · 28 OCTOBER 1880", lines=["Dr Henry Faulds writes in 'Nature':","bloody finger-marks may identify criminals"],
    vo="अपराधी पकड़ने का विचार आया, हज़ारों किलोमीटर दूर, जापान से। टोक्यो में काम कर रहे स्कॉटिश डॉक्टर हेनरी फ़ॉल्ड्स ने, पुराने मिट्टी के बर्तनों पर कारीगरों की उंगलियों के निशान देखे। अट्ठाईस अक्टूबर अठारह सौ अस्सी को, विज्ञान पत्रिका नेचर में उन्होंने लिखा, कि ख़ून से सने निशान, अपराधी की वैज्ञानिक पहचान तक ले जा सकते हैं।")
add(type="dossier", file="LETTER · 1880", ref="FAULDS → DARWIN", rows=[["FROM","DR HENRY FAULDS"],["TO","CHARLES DARWIN"],["PASSED TO","FRANCIS GALTON"],["RESULT","LITTLE INTEREST"]],
    stamp="IGNORED", kicker="THE FIRST CREDIT FIGHT", big="WHO WAS FIRST?", lines=["Herschel replies: 'I've used prints for years'","a dispute that lasted decades"],
    vo="फ़ॉल्ड्स ने चार्ल्स डार्विन को भी चिट्ठी लिखी। डार्विन बूढ़े और बीमार थे, उन्होंने वो चिट्ठी अपने चचेरे भाई फ़्रांसिस गैल्टन को भेज दी, और गैल्टन ने तब उसमें ख़ास दिलचस्पी नहीं ली। उधर हर्शेल ने भी नेचर में लिखा, कि ये तरीक़ा तो वो बरसों से इस्तेमाल कर रहे हैं। श्रेय की ये लड़ाई, इस कहानी में बार बार लौटेगी।")
add(type="image", img=M+"bertillon_0.jpg", kicker="PARIS · 1880s", big="11 MEASUREMENTS", lines=["Bertillonage: head, arm span, ear, foot","claimed odds: over 4 million to 1"],
    vo="पर उस दौर की पुलिस का भरोसा, किसी और तरीक़े पर था। पेरिस पुलिस के क्लर्क अल्फ़ोंस बर्टिलॉन ने, अपराधियों के शरीर के ग्यारह नाप लेने का सिस्टम बनाया, सिर, बाँहों का फैलाव, कान, पैर। उनका दावा था, कि दो लोगों के सारे नाप एक जैसे होने की संभावना, चालीस लाख में एक से भी कम है। दुनिया भर की पुलिस ने इसे अपनाया, और बंगाल की पुलिस ने भी।")
add(type="image", img=M+"bertillon_1.jpg", kicker="THE PROBLEM", lines=["A small error in measuring","could point to the wrong person"],
    vo="लेकिन इस सिस्टम में मुश्किलें थीं। नापने में ज़रा सी चूक, और पहचान ग़लत हो सकती थी। हर कैदी को ध्यान से नापना, धीमा और महँगा काम था। बंगाल के पुलिस प्रमुख एडवर्ड हेनरी को, कुछ बेहतर चाहिए था, और अठारह सौ छियानवे में, उन्होंने कैदियों के नाप के साथ, उनकी उंगलियों के निशान भी लेने का आदेश दिया।")
add(type="image", img=M+"galton_0.jpg", kicker="LONDON · 1892", big="1 IN 64 BILLION", lines=["Galton's book 'Finger Prints'","arches · loops · whorls"],
    vo="इसी बीच, गैल्टन ने आख़िरकार फ़िंगरप्रिंट पर गंभीरता से काम किया। अठारह सौ बानवे में उनकी किताब आई, फ़िंगर प्रिंट्स। उन्होंने निशानों को तीन तरह में बाँटा, मेहराब जैसे, लूप जैसे, और भँवर जैसे। और हिसाब लगाया, कि दो लोगों के निशान एक जैसे होने की संभावना, चौंसठ अरब में एक है।")
add(type="image", img=M+"laplata_0.jpg", kicker="ARGENTINA · 1891–92", lines=["Juan Vucetich builds his own system","still used in Spanish-speaking countries"],
    vo="और दुनिया के दूसरे छोर पर, अर्जेंटीना में, पुलिस अफ़सर हुआन वुचेटिच ने, गैल्टन के काम से प्रेरित होकर अपना अलग सिस्टम बना लिया था, और अठारह सौ बानवे में फ़िंगरप्रिंट का एक दफ़्तर भी शुरू कर दिया। उसी साल जून में, नेकोचिया नाम के शहर में, दो छोटे बच्चों की हत्या हुई।")
add(type="fingerprint", seed=19, left_label="DOOR FRAME · NECOCHEA", right_label="MATCH: NOT THE NEIGHBOUR", stamp="MATCH",
    kicker="JUNE 1892 · NECOCHEA", big="THE DOOR", lines=["A bloody print cut out of a door frame","the first murder solved by a fingerprint"],
    vo="बच्चों की माँ, फ़्रांसिस्का रोहास ने, इल्ज़ाम एक पड़ोसी पर लगाया। लेकिन इंस्पेक्टर एदुआर्दो अल्वारेज़ को, दरवाज़े पर ख़ून से सना एक निशान मिला। उन्होंने दरवाज़े का वो टुकड़ा ही काट लिया। निशान पड़ोसी का नहीं, ख़ुद रोहास का निकला। उसने जुर्म क़बूल किया, और इसे फ़िंगरप्रिंट से सुलझा, पहला हत्या का मामला माना जाता है।")
add(type="image", img=P+"calcutta1890_0.jpg", kicker="BUT ONE PROBLEM REMAINED", lines=["How do you find one card","among thousands, quickly?"],
    vo="पर हर पुलिस के सामने, एक बड़ी समस्या अब भी थी। एक निशान मिल भी जाए, तो उसे हज़ारों कार्डों में से, जल्दी कैसे ढूँढ़ा जाए? बड़े रिकॉर्ड के लिए, गैल्टन का तरीक़ा बहुत धीमा था। और यहीं, हमारी कहानी लौटती है, कलकत्ता।")
add(type="dossier", file="ANTHROPOMETRIC BUREAU", ref="CALCUTTA · 1890s", img=P+"writers_2.jpg",
    rows=[["SUB-INSPECTOR","AZIZUL HAQUE"],["STRENGTH","MATHS & STATISTICS"],["SUB-INSPECTOR","HEM CHANDRA BOSE"],["BOSS","E. R. HENRY, IG POLICE"]],
    stamp="ASSIGNED", kicker="THE TWO MEN", big="HAQUE & BOSE", lines=["A statistics student from Presidency College","and a postman's son from Nadia"],
    vo="कलकत्ता का एंथ्रोपोमेट्रिक ब्यूरो। अठारह सौ बानवे में, एडवर्ड हेनरी ने प्रेसिडेंसी कॉलेज के प्रिंसिपल से, आँकड़ों में तेज़ एक छात्र माँगा। जवाब में मिले, अज़ीज़ुल हक़। उनके साथ थे हेमचंद्र बोस, एक डाकिए के बेटे, जो अठारह सौ चौरानवे में, सीआईडी मुख्यालय कलकत्ता आए थे।")
add(type="drawers", kicker="THE HAQUE–BOSE FORMULA", whorls=[1,4,7], lines=["A sea of cards, cut into 1,024 drawers","find the drawer, not the needle"],
    vo="उन्होंने समस्या को गणित से हल किया। दस उंगलियों के पाँच जोड़े बनाए। जिस उंगली पर भँवर जैसा गोल निशान हो, उसे जोड़े के हिसाब से एक नंबर मिला, सोलह, आठ, चार, दो या एक। सम उंगलियों का जोड़ ऊपर, विषम का नीचे, दोनों में एक जोड़कर बनता एक भिन्न। हर भिन्न का अपना दराज़, कुल एक हज़ार चौबीस दराज़। हज़ारों कार्डों का समंदर, अब छोटे छोटे दराज़ों में बँट गया था।")
add(type="stat", kicker="CALCUTTA · 1897", value=7000, value_label="7,000", label="FINGERPRINT SETS IN HAQUE'S CABINET",
    items=[["1896","Henry orders prisoners' prints taken"],["1897","committee: cheaper, simpler, more accurate"],["12 JUNE 1897","Fingerprint Bureau, Writers' Building"]],
    vo="अठारह सौ सत्तानवे तक, हक़ की अलमारी में सात हज़ार सेट जमा हो चुके थे। उसी साल एक कमेटी ने, नाप वाले तरीक़े और फ़िंगरप्रिंट की तुलना की, और फ़िंगरप्रिंट को सस्ता, आसान और ज़्यादा सटीक पाया। बारह जून अठारह सौ सत्तानवे को, कलकत्ता के राइटर्स बिल्डिंग में, फ़िंगरप्रिंट ब्यूरो शुरू हुआ, जिसे अक्सर दुनिया का पहला ऐसा ब्यूरो कहा जाता है, हालाँकि अर्जेंटीना में वुचेटिच का दफ़्तर भी, कुछ साल पहले शुरू हो चुका था।")
add(type="fingerprint", seed=7, left_label="CALENDAR · 1898", right_label="KANGALI CHARAN", stamp="MATCH",
    kicker="BACK TO THE TEA GARDEN", big="THE MATCH", lines=["the manager's former servant","released from jail weeks earlier"],
    vo="और अब, लौटते हैं उस चाय बागान पर। कैलेंडर पर मिला निशान, ब्यूरो के कार्डों से मिलाया गया। वो निकला कंगाली चरण का, मैनेजर का पुराना नौकर, जिसे मैनेजर ने चोरी के जुर्म में जेल भिजवाया था, और जो कुछ हफ़्ते पहले ही छूटा था। उसे बीरभूम से गिरफ़्तार कर, कलकत्ता लाया गया।")
add(type="image", img=P+"teagarden_0.jpg", kicker="MAY 1898 · THE VERDICT", big="CONVICTED", lines=["murder: no eyewitness, not proven","theft: proven by the thumbprint"],
    vo="मई अठारह सौ अट्ठानवे में मुक़दमा चला। अदालत ने कहा, क़त्ल किसी ने होते नहीं देखा, इसलिए हत्या साबित नहीं होती। लेकिन चोरी, पक्के तौर पर साबित है, अंगूठे के निशान से। ब्रिटिश साम्राज्य में, फ़िंगरप्रिंट सबूत पर सज़ा के, ये सबसे शुरुआती मामलों में से एक था। और इसके बाद, कलकत्ता का ये तरीक़ा, दुनिया की तरफ़ निकल पड़ा।")
add(type="spread", origin=["CALCUTTA",22.57,88.36], year0="1900",
    routes=[["LONDON",51.5,-0.13,4.5,None,"1901"],["SOUTH AFRICA",-26.2,28.0,7.5,None,"1900s"],["USA",40.7,-74.0,8.5,"LONDON",""]],
    kicker="CALCUTTA → THE WORLD", lines=["Scotland Yard bureau: 1 July 1901","then the English-speaking world"],
    vo="उन्नीस सौ में, हेनरी ने इस सिस्टम पर किताब छापी, और लंदन पहुँचकर, एक जुलाई उन्नीस सौ एक को, स्कॉटलैंड यार्ड में फ़िंगरप्रिंट ब्यूरो शुरू किया। जल्द ही, ये अंग्रेज़ी बोलने वाली दुनिया का मानक बन गया। लेकिन असली परीक्षा तो, अदालतों में होनी थी।")
add(type="image", img=M+"oldbailey_0.jpg", kicker="13 SEPTEMBER 1902 · OLD BAILEY", big="BILLIARD BALLS", lines=["Harry Jackson: Britain's first fingerprint conviction","a thumbprint on fresh paint"],
    vo="ब्रिटेन में पहला मामला, थोड़ा मज़ेदार था। उन्नीस सौ दो में, लंदन के एक घर से, कुछ बिलियर्ड की गेंदें चोरी हुईं। चोर हैरी जैक्सन ने, ताज़ा पेंट की हुई खिड़की पर, अपने अंगूठे का निशान छोड़ दिया। तेरह सितंबर को उसे सात साल की सज़ा हुई, ब्रिटेन में फ़िंगरप्रिंट से पहली सज़ा।")
add(type="image", img=M+"deptford_0.jpg", kicker="1905 · DEPTFORD, LONDON", lines=["a thumbprint on a cash box","first British murder conviction by fingerprint"],
    vo="और तीन साल बाद, उन्नीस सौ पाँच में, एक दुकान के पैसों वाले बक्से पर मिले अंगूठे के निशान ने, स्ट्रैटन भाइयों को, ब्रिटेन में फ़िंगरप्रिंट सबूत पर हत्या के दोषी ठहराए जाने वाले, पहले लोग बना दिया। अब फ़िंगरप्रिंट, अदालत का सबसे भरोसेमंद गवाह बन रहा था।")
add(type="image", img=M+"leavenworth_0.jpg", kicker="1903 · LEAVENWORTH, USA", lines=["Will West & William West","near-identical measurements, different fingerprints"],
    vo="बर्टिलॉन का सिस्टम फिर भी कई जगह चल रहा था। फिर अमेरिका की लेवनवर्थ जेल का एक किस्सा मशहूर हुआ। उन्नीस सौ तीन में, नए कैदी विल वेस्ट के नाप, पहले से दर्ज विलियम वेस्ट से लगभग पूरी तरह मिलते थे, और चेहरे भी मिलते जुलते थे। लेकिन उंगलियों के निशान, बिल्कुल अलग निकले। बाद में इतिहासकारों ने बताया कि नाप में भी थोड़ा फ़र्क़ था, पर इस कहानी ने, बर्टिलॉन के सिस्टम का अंत तय कर दिया।")
add(type="stat", kicker="FBI · USA", value=200, value_label="200 MILLION", label="FINGERPRINT CARDS PROCESSED BY 1971",
    items=[["1924","FBI Identification Division"],["1946","100 million cards"],["1924–1999","the same kind of card index"]],
    vo="उन्नीस सौ चौबीस में, अमेरिका की एफ़बीआई ने अपना पहचान विभाग बनाया। उन्नीस सौ छियालीस तक वहाँ, दस करोड़ से ज़्यादा फ़िंगरप्रिंट कार्ड आ चुके थे, और उन्नीस सौ इकहत्तर तक, बीस करोड़। बड़े बड़े कमरों में अलमारियाँ ही अलमारियाँ, और उन्हें ढूँढ़ने का आधार, वही हेनरी वाला वर्गीकरण, कुछ बदलावों के साथ।")
add(type="image", img=M+"scanner_0.jpg", kicker="1980s → 28 JULY 1999", lines=["Computers take over the search","FBI's IAFIS goes fully digital"],
    vo="फिर आए कंप्यूटर। अस्सी और नब्बे के दशक में, अपने आप मिलान करने वाले फ़िंगरप्रिंट सिस्टम आए, और अट्ठाईस जुलाई उन्नीस सौ निन्यानवे को, एफ़बीआई का पूरा सिस्टम डिजिटल हो गया। अब जो मिलान, हफ़्तों में होता था, वो घंटों में होने लगा। और नब्बे के दशक तक, इन कंप्यूटर सिस्टमों का वर्गीकरण भी, हेनरी सिस्टम पर टिका रहा।")
add(type="dossier", file="HENRY CLASSIFICATION SYSTEM", ref="1897", rows=[["NAMED AFTER","SIR EDWARD HENRY"],["MATHS","AZIZUL HAQUE"],["TABLES & TESTS","HEM CHANDRA BOSE"],["LATER REWARD","Rs 5,000 EACH + TITLES"]],
    stamp="CREDIT?", kicker="BACK TO THE QUESTION", big="WHOSE NAME?", lines=["Khan Bahadur & Rai Bahadur titles","but the name stayed: 'Henry'"],
    vo="अब लौटते हैं, उसी पुराने सवाल पर, श्रेय किसे मिला? सिस्टम का नाम पड़ा, हेनरी क्लासिफ़िकेशन सिस्टम। सालों बाद, हक़ ने अपने योगदान की पहचान माँगी। ब्रिटिश सरकार ने हक़ और बोस, दोनों को पाँच पाँच हज़ार रुपये का इनाम दिया, और ख़ान बहादुर और राय बहादुर की उपाधियाँ। पर नाम, हेनरी का ही रहा।")
add(type="image", img=M+"tsukiji_1.jpg", kicker="THE FORGOTTEN", lines=["Faulds too died without full credit","a story of science, and of forgotten people"],
    vo="और हेनरी फ़ॉल्ड्स, जिन्होंने सबसे पहले अपराधी पकड़ने की बात लिखी थी, उन्हें भी ज़िंदगी भर पूरा श्रेय नहीं मिला। फ़िंगरप्रिंट की कहानी, जितनी विज्ञान की है, उतनी ही भुला दिए गए लोगों की भी।")
add(type="stat", kicker="INDIA · TODAY", value=144, value_label="144 CRORE+", label="AADHAAR NUMBERS GENERATED (UIDAI)",
    items=[["~134 crore","live Aadhaar holders"],["fingerprints + iris","captured at enrolment"],["under 5","no fingerprints taken"]],
    vo="और आज, उसी देश में जहाँ ये सब शुरू हुआ, दुनिया का सबसे बड़ा बायोमेट्रिक पहचान सिस्टम है। आधार के एक सौ चौवालीस करोड़ से ज़्यादा नंबर बन चुके हैं, जिनमें लोगों की उंगलियों के निशान दर्ज हैं। राशन से लेकर बैंक तक, आज आपका अंगूठा ही आपकी पहचान है।")
add(type="outro", lines=["1858: a handprint in Bengal. 1897: a bureau in Calcutta.","Next time you use your thumb, remember Haque & Bose.","Should it be called the Haque–Bose system?"],
    vo="अठारह सौ अट्ठावन में बंगाल की एक हथेली की छाप, अठारह सौ सत्तानवे में कलकत्ता का ब्यूरो, और आज आपके फ़ोन का सेंसर। अगली बार जब अंगूठा लगाएँ, तो याद कीजिए, अज़ीज़ुल हक़ और हेमचंद्र बोस को। क्या इस सिस्टम का नाम, हक़ बोस सिस्टम होना चाहिए? कमेंट में ज़रूर बताइए। ऐसी ही छुपी कहानियों के लिए, अननोन अनकवर्ड को अभी सब्सक्राइब और फ़ॉलो करें।")
spec={"format":"long","theme":"forensic","look":"cinematic","grain":0.1,"tts":"parler","speed":0.98,"lead":0.35,"tail":0.55,
 "header":"THE FINGERPRINT: FROM A BENGAL HANDPRINT TO THE WORLD",
 "source":"Sources: Britannica · E. R. Henry (1913) · Bengal CID · FBI · UIDAI · Nature (1880)",
 "ticker":"  1858: HERSCHEL'S HANDPRINT, JANGIPUR   ///   1880: FAULDS IN 'NATURE'   ///   1892: GALTON · VUCETICH   ///   1897: CALCUTTA BUREAU · HAQUE & BOSE   ///   1898: KANGALI CHARAN CASE   ///   1901: SCOTLAND YARD   ///   1999: FBI GOES DIGITAL   ///",
 "credits_from":["media/014_fingerprint_long/credits.json","media/013_fingerprint/credits.json"],"scenes":sc}
json.dump(spec,open("spec.json","w"),ensure_ascii=False,indent=1)
t=sum(len(c["vo"]) for c in sc); print(len(sc),"scenes",t,"chars ~",round(t/15.4/0.98+len(sc)*0.9),"s")
