import re
import os

swot_entries = {
    'hi': '''    swot: {
      title: "व्यावसायिक कारक (Business Factors)",
      subtitle: "आपके पक्ष में क्या काम कर रहा है — और ऋण लेने से पहले किन बातों पर ध्यान देना आवश्यक है।",
      badge: "SWOT • साक्ष्य-आधारित",
      strengths: "मजबूतियाँ (Strengths)",
      weaknesses: "कमजोरियाँ (Weaknesses)",
      opportunities: "अवसर (Opportunities)",
      threats: "चुनौतियाँ व जोखिम (Threats)",
      strengthsSub: "सकारात्मक आंतरिक कारक और वित्तीय सुरक्षा बफर",
      weaknessesSub: "आंतरिक सीमाएं और परिचालन संबंधी कमजोरियां",
      opportunitiesSub: "बाजार की मांग और सरकारी योजनाओं का समर्थन",
      threatsSub: "मौसमी, आपूर्ति और स्थानीय बाजार के जोखिम",
      emptyState: "इस विश्लेषण के लिए व्यावसायिक कारक उपलब्ध नहीं हैं।",
      emptyQuadrant: "कोई साक्ष्य-आधारित कारक नहीं पाया गया।",
      viewEvidence: "साक्ष्य देखें →",
      confidence: "विश्वसनीयता",
      needsVerification: "सत्यापन आवश्यक",
      needsVerificationDesc: "कुछ बाजार साक्ष्यों का वर्तमान में सत्यापन आवश्यक है।",
    },''',
    'mr': '''    swot: {
      title: "व्यावसायिक घटक (Business Factors)",
      subtitle: "तुमच्या बाजूने काय काम करत आहे — आणि कर्ज घेण्यापूर्वी कशाकडे लक्ष देणे आवश्यक आहे.",
      badge: "SWOT • पुराव्यावर आधारित",
      strengths: "सामर्थ्य (Strengths)",
      weaknesses: "उणिवा (Weaknesses)",
      opportunities: "संधी (Opportunities)",
      threats: "धोके (Threats)",
      strengthsSub: "सकारात्मक अंतर्गत घटक आणि आर्थिक सुरक्षितता",
      weaknessesSub: "अंतर्गत मर्यादा आणि कामकाजातील कमकुवतपणा",
      opportunitiesSub: "बाजारपेठेतील मागणी आणि शासकीय योजनांचे साहाय्य",
      threatsSub: "हंगामी, पुरवठा आणि बाह्य बाजारातील जोखीम",
      emptyState: "या विश्लेषणासाठी व्यावसायिक घटक उपलब्ध नाहीत.",
      emptyQuadrant: "कोणतेही पुराव्यावर आधारित घटक आढळले नाहीत.",
      viewEvidence: "पुरावा पहा →",
      confidence: "विश्वासार्हता",
      needsVerification: "पडताळणी आवश्यक",
      needsVerificationDesc: "काही बाजार पुराव्यांची सध्या पडताळणी आवश्यक आहे.",
    },''',
    'bn': '''    swot: {
      title: "ব্যবসায়িক কারণসমূহ (Business Factors)",
      subtitle: "আপনার পক্ষে কী কাজ করছে — এবং ঋণ নেওয়ার আগে কী বিষয়ে নজর দেওয়া জরুরি।",
      badge: "SWOT • প্রমাণ-ভিত্তিক",
      strengths: "শক্তি (Strengths)",
      weaknesses: "দুর্বলতা (Weaknesses)",
      opportunities: "সুযোগ (Opportunities)",
      threats: "ঝুঁকি ও হুমকি (Threats)",
      strengthsSub: "ইতিবাচক অভ্যন্তরীণ বিষয় ও আর্থিক বাফার",
      weaknessesSub: "অভ্যন্তরীণ সীমাবদ্ধতা ও পরিচালনার দুর্বলতা",
      opportunitiesSub: "বাজারের চাহিদা ও সরকারি প্রকল্পের সহায়তা",
      threatsSub: "মৌসুমি, সরবরাহ ও বাহ্যিক বাজারের ঝুঁকি",
      emptyState: "এই বিশ্লেষণের জন্য ব্যবসায়িক কারণসমূহ উপলব্ধ নেই।",
      emptyQuadrant: "কোনো প্রমাণ-ভিত্তিক কারণ পাওয়া যায়নি।",
      viewEvidence: "প্রমাণ দেখুন →",
      confidence: "নির্ভরযোগ্যতা",
      needsVerification: "যাচাই প্রয়োজন",
      needsVerificationDesc: "কিছু বাজারের তথ্যের বর্তমানে যাচাইকরণ প্রয়োজন।",
    },''',
    'te': '''    swot: {
      title: "వ్యాపార కారకాలు (Business Factors)",
      subtitle: "మీకు అనుకూలంగా ఉన్న అంశాలు — మరియు రుణం తీసుకునే ముందు శ్రద్ధ వహించాల్సిన విషయాలు.",
      badge: "SWOT • ఆధారాలతో కూడిన విశ్లేషణ",
      strengths: "బలాలు (Strengths)",
      weaknesses: "బలహీనతలు (Weaknesses)",
      opportunities: "అవకాశాలు (Opportunities)",
      threats: "ముప్పులు మరియు ప్రమాదాలు (Threats)",
      strengthsSub: "అనుకూల అంతర్గత అంశాలు మరియు ఆర్థిక నిల్వలు",
      weaknessesSub: "అంతర్గత పరిమితులు మరియు నిర్వహణ లోపాలు",
      opportunitiesSub: "మార్కెట్ డిమాండ్ మరియు ప్రభుత్వ పథకాల సహకారం",
      threatsSub: "సీజనల్, సరఫరా మరియు స్థానిక మార్కెట్ రిస్కులు",
      emptyState: "ఈ విశ్లేషణకు వ్యాపార కారకాలు అందుబాటులో లేవు.",
      emptyQuadrant: "ఎటువంటి ఆధారాలతో కూడిన కారకాలు కనుగొనబడలేదు.",
      viewEvidence: "సాక్ష్యం చూడండి →",
      confidence: "విశ్వసనీయత",
      needsVerification: "ధృవీకరణ అవసరం",
      needsVerificationDesc: "కొన్ని మార్కెట్ ఆధారాలు ఇంకా ధృవీకరించబడలేదు.",
    },''',
    'ta': '''    swot: {
      title: "வணிக காரணிகள் (Business Factors)",
      subtitle: "உங்களுக்கு சாதகமாக இருப்பது என்ன — மற்றும் கடன் வாங்குவதற்கு முன் கவனிக்க வேண்டியவை.",
      badge: "SWOT • சான்று அடிப்படையிலானது",
      strengths: "பலங்கள் (Strengths)",
      weaknesses: "பலவீனங்கள் (Weaknesses)",
      opportunities: "வாய்ப்புகள் (Opportunities)",
      threats: "அச்சுறுத்தல்கள் (Threats)",
      strengthsSub: "சாதகமான உள் காரணிகள் மற்றும் நிதி பாதுகாப்பு",
      weaknessesSub: "உள் தடைகள் மற்றும் செயல்பாட்டு குறைபாடுகள்",
      opportunitiesSub: "சந்தை தேவை மற்றும் அரசு திட்ட ஆதரவு",
      threatsSub: "பருவகால, விநியோக மற்றும் வெளிச் சந்தை அபாயங்கள்",
      emptyState: "இந்த ஆய்வுக்கு வணிகக் காரணிகள் கிடைக்கவில்லை.",
      emptyQuadrant: "சான்று அடிப்படையிலான காரணிகள் எதுவும் காணப்படவில்லை.",
      viewEvidence: "சான்றைக் காண்க →",
      confidence: "நம்பகத்தன்மை",
      needsVerification: "சரிபார்ப்பு தேவை",
      needsVerificationDesc: "சில சந்தை சான்றுகள் தற்போது சரிபார்க்கப்படவில்லை.",
    },'''
}

for lang, snippet in swot_entries.items():
    filepath = os.path.join('frontend', 'lib', 'i18n', 'dictionaries', f'{lang}.ts')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'swot:' in content:
        print(f'{lang}.ts already has swot')
        continue
    
    # insert before 'empty: {'
    pattern = r'(\n\s+empty:\s*\{)'
    match = re.search(pattern, content)
    if match:
        new_content = content[:match.start()] + '\n' + snippet + content[match.start():]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Successfully updated {lang}.ts')
    else:
        print(f'Could not find empty: {{ in {lang}.ts')
