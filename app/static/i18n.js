/**
 * Complete Marathi (मराठी) & English (English) Localization Engine
 * Covers every single UI label, form, button, metric, task title, step description,
 * document checklist, and department name across the entire application.
 */

const UI_STRINGS = {
  en: {
    // Top Bar
    topbar_status: "Government of Maharashtra Citizen Services Portal • Verified Statutory Standards",
    topbar_helpline: "Toll-Free Helpline: 1800-120-8040",
    topbar_antitout: "Zero Bribery / Anti-Tout Guarantee",

    // Header & Nav
    brand_title: "Civic Task Navigator",
    brand_state: "MAHARASHTRA",
    brand_sub: "Simple Step-by-Step Municipal & State Service Guides (नागरिक कार्य मार्गदर्शक)",
    find_service: "Find Service",
    step_roadmap: "Step Roadmap",
    step_details: "Step Details & Apply",
    my_progress: "My Progress",
    admin: "Admin",

    // View 1: Intake
    hero_tag: "Citizen Wayfinder",
    hero_title: "Navigate Maharashtra Government Services with Ease",
    hero_desc: "Enter what you want to accomplish in plain English or Marathi (मराठी). We will break it down into an easy, ordered checklist with required forms, documents, official fees, and direct application links.",
    search_label: "What civic or government procedure do you need to complete?",
    search_placeholder: "e.g. I want to register a small business, or Apply for 7/12 land extract",
    popular_label: "Popular:",
    pill_small_biz: "🏪 Register a Small Business",
    pill_bakery: "☕ Open Bakery / Cafe",
    pill_mutation: "📜 7/12 Land Mutation",
    pill_water: "💧 New Water Connection",
    pill_rts: "🆔 Income & Domicile Certificate",
    pill_marathi_shop: "🏪 दुकान नोंदणी (गुमास्ता)",
    city_label: "City / Municipal Corporation (महानगरपालिका)",
    applicant_label: "Applicant Type (अर्जदाराचा प्रकार)",
    rts_guarantee: "All procedures follow the Maharashtra Right to Public Services Act (RTS 2015)",
    btn_show_roadmap: "Show My Roadmap",
    catalog_heading: "Verified Maharashtra Government Procedures (प्रक्रिया निर्देशिका)",
    catalog_desc: "Click any verified procedure below to view its complete step-by-step roadmap, required documents, and official government application links.",
    load_route_btn: "Load Route",

    // View 2: Roadmap
    route_badge_prefix: "ROUTE #",
    route_active_badge: "Active Maharashtra Roadmap",
    btn_subway: "🚇 Subway Map",
    btn_dag: "🕸️ DAG Topology",
    btn_fit: "Fit",
    btn_reset: "Reset",
    critical_path: "Highlight Critical Path",
    critical_path_active: "Highlighting Critical Path",
    share_route: "Share Route",
    print: "Print",
    stat_time: "Total Estimated Time",
    stat_fees: "Total Government Fees",
    stat_steps: "Steps Completed",
    stat_docs: "Documents Gathered",
    working_days: "Working Days",
    steps_cleared: "Steps Cleared",
    docs_ready: "Ready in Locker",
    checklist_heading: "Your Step-by-Step Compliance Checklist",
    checklist_desc: "Complete these stages in order. Click 'View Details & Apply' to access the official portal links and required forms.",
    toggle_subway_btn: "Toggle Visual Subway Map",
    sla_label: "Days SLA",
    free_nil: "Free / Nil",
    critical_path_tag: "⚡ Critical Path",
    btn_view_details: "View Details & Apply",
    btn_mark_done: "Mark Done",
    btn_completed: "Completed ✓",
    status_ready: "Ready to Start",
    status_in_progress: "● Ready to Apply",
    status_prereq_wait: "Waiting on Prerequisite",

    // View 3: Step Details
    back_to_roadmap: "Back to Step Roadmap",
    dossier_sla_label: "Government Guaranteed SLA",
    dossier_prov_text: "Verified against official Government of Maharashtra portal",
    dossier_apply_btn: "Apply on Official Portal ↗",
    req_docs_heading: "Required Documents Checklist",
    req_docs_sub: "Check off documents as you gather them. Your checklist is saved automatically:",
    gov_forms_heading: "Official Government Application Forms",
    prior_prereqs_heading: "Prior Prerequisites",
    fees_heading: "Official Statutory Fees",
    payment_channel_label: "Payment Channel:",
    office_help_heading: "Office & Counter Help",
    office_addr_label: "Office Address",
    office_hours_label: "Public Working Hours",
    office_hours_val: "Mon-Fri 10:00 AM - 5:00 PM",
    office_helpline_label: "Helpline / Ombudsman",
    track_app_heading: "Track Existing Application Status",
    track_app_desc: "Already submitted an application or paid an e-challan? Check your live status on the official portal:",
    track_token_label: "Application Token / Challan No.",
    track_portal_label: "Select Official Department Portal",
    track_btn: "Check Status on Official Portal ↗",
    mandatory_tag: "Mandatory",
    optional_tag: "Optional",

    // View 4: Citizen Ledger
    ledger_heading: "My Civic Progress & Document Locker",
    ledger_desc: "Track your progress across completed steps, monitor fees paid, and manage required documents. Your status is saved in SQLite and local storage.",
    ledger_active_proc: "Active Procedure",
    ledger_steps_cleared_of: "steps completed",
    ledger_fees_tally: "Fees Tally",
    ledger_paid: "Paid",
    ledger_pending: "Pending",
    ledger_days_rem: "Estimated Days Remaining",
    ledger_rts_guar: "Guaranteed under RTS Act 2015",
    ledger_milestones: "Procedure Milestones",
    ledger_doc_bag: "Consolidated Document Bag",
    ledger_doc_sub: "Keep these ready in digital format (PDF/JPEG < 500KB) for portal uploads:",

    // View 5: Admin
    admin_heading: "Administrative Registry & Verification Portal",
    admin_desc: "Municipal officer console for reviewing extracted government information, testing portal crawlers, and inspecting SQLite databases.",
    subtab_scraper: "🌐 Live Portal Scraper",
    subtab_moderation: "🛡️ Verify Steps & Fees",
    subtab_audit: "📜 Audit Trail",
    subtab_feedback: "💬 Citizen Feedback",
    subtab_regulatory: "🏛️ Statutory Portal Audit Cache",
    admin_crawler_title: "Live Maharashtra Portal Crawler & Extractor",
    admin_crawler_desc: "Gathers text, downloadable application forms, fees, SLAs, and candidate steps directly from official government URLs.",
    admin_quick_presets: "Quick Portal Presets:",
    admin_portal_url: "Official Portal URL",
    admin_service_hint: "Service Hint",
    admin_scrape_btn: "Scrape & Extract Government Rules",
    admin_terminal_ready: "System ready. Click \"Scrape & Extract Government Rules\" to initiate extraction.",
    admin_verify_title: "Verify Steps & Statutory Fees",
    admin_verify_desc: "Review extracted procedural steps, confirm statutory fees, and stamp official verification provenance.",
    admin_th_step: "Step Name",
    admin_th_dept: "Department",
    admin_th_fee: "Fee (₹)",
    admin_th_sla: "SLA Days",
    admin_th_status: "Status",
    admin_th_actions: "Actions",
    admin_audit_title: "Administrative Audit Trail",
    admin_audit_desc: "Timestamped log of all procedural updates, scrapings, and verification changes saved in SQLite.",
    admin_feedback_title: "Citizen Problem Reports & Feedback",
    admin_feedback_desc: "Field reports from citizens on outdated forms, changed fees, or broken portal links.",

    // Footer
    footer_title: "Civic Task Navigator — Maharashtra Portal",
    footer_sub: "Built in accordance with Maharashtra Right to Public Services Act 2015 & GIGW Standards",
    footer_source: "All fees and documents are directly sourced from official portals:",

    // Subway
    subway_line_title: "Subway Transit Line Sequence",
    subway_line_sub: "1 Station = 1 Government Clearance Stage",

    // Share Modal
    share_modal_title: "Share Compliance Route",
    share_modal_desc: "Share this verified Maharashtra statutory procedure, document checklist, and official links with partners, clients, or family members.",
    share_direct_link: "Direct Web Link",
    share_copy_btn: "Copy",
    share_whatsapp_btn: "Share Summary via WhatsApp",
    share_toast: "Link copied to clipboard!"
  },

  mr: {
    // Top Bar
    topbar_status: "महाराष्ट्र शासन नागरिक सेवा पोर्टल • प्रमाणित वैधानिक मानके",
    topbar_helpline: "टोल-फ्री हेल्पलाईन: १८००-१२०-८०४०",
    topbar_antitout: "शून्य लाच / दलाल मुक्त हमी",

    // Header & Nav
    brand_title: "नागरिक कार्य मार्गदर्शक",
    brand_state: "महाराष्ट्र शासन",
    brand_sub: "सोपे टप्प्याटप्प्याने महानगरपालिका व राज्य सेवा मार्गदर्शक",
    find_service: "सेवा शोधा",
    step_roadmap: "प्रक्रिया मार्ग",
    step_details: "तपशील व अर्ज",
    my_progress: "माझी प्रगती",
    admin: "प्रशासन",

    // View 1: Intake
    hero_tag: "नागरिक सहाय्यक",
    hero_title: "महाराष्ट्र शासकीय सेवा सहज व सोप्या पद्धतीने पूर्ण करा",
    hero_desc: "तुम्हाला कोणती शासकीय सेवा हवी आहे ते साध्या मराठी किंवा इंग्रजीत लिहा. आम्ही आवश्यक अर्ज, कागदपत्रे, अधिकृत शुल्क आणि थेट अर्जाची लिंक यांसह टप्प्याटप्प्याने संपूर्ण मार्गदर्शन करू.",
    search_label: "तुम्हाला कोणती नागरिक किंवा शासकीय सेवा हवी आहे?",
    search_placeholder: "उदा. मला दुकान नोंदणी करायची आहे, किंवा सातबारा फेरफार अर्ज",
    popular_label: "लोकप्रिय:",
    pill_small_biz: "🏪 दुकान व व्यवसाय नोंदणी (गुमास्ता)",
    pill_bakery: "☕ हॉटेल, कॅफे व बेकरी परवाना",
    pill_mutation: "📜 सातबारा फेरफार व वारस नोंद",
    pill_water: "💧 नवीन नळ जोडणी",
    pill_rts: "🆔 उत्पन्न व अधिवास दाखला",
    pill_marathi_shop: "🏪 दुकान नोंदणी (गुमास्ता परवाना)",
    city_label: "शहर / महानगरपालिका",
    applicant_label: "अर्जदाराचा प्रकार",
    rts_guarantee: "सर्व सेवा महाराष्ट्र लोकसेवा हक्क अधिनियम (RTS २०१५) अंतर्गत वेळेत उपलब्ध",
    btn_show_roadmap: "माझा प्रक्रिया मार्ग दाखवा",
    catalog_heading: "प्रमाणित महाराष्ट्र शासकीय प्रक्रिया निर्देशिका",
    catalog_desc: "सविस्तर टप्प्याटप्प्याचा मार्ग, आवश्यक कागदपत्रे आणि अधिकृत अर्ज लिंक्स पाहण्यासाठी खालील कोणत्याही सेवेवर क्लिक करा.",
    load_route_btn: "मार्ग पहा",

    // View 2: Roadmap
    route_badge_prefix: "प्रक्रिया मार्ग #",
    route_active_badge: "सक्रिय महाराष्ट्र प्रक्रिया मार्ग",
    btn_subway: "🚇 सबवे मार्ग नकाशा",
    btn_dag: "🕸️ डीएजी आकृती",
    btn_fit: "स्क्रीनवर बसवा",
    btn_reset: "रीसेट करा",
    critical_path: "महत्त्वाचा मार्ग दाखवा",
    critical_path_active: "महत्त्वाचा मार्ग दर्शविला आहे",
    share_route: "मार्ग सामायिक करा",
    print: "प्रिंट करा",
    stat_time: "अंदाजे एकूण कालावधी",
    stat_fees: "अधिकृत शासकीय शुल्क",
    stat_steps: "पूर्ण झालेले टप्पे",
    stat_docs: "तयार कागदपत्रे",
    working_days: "कामाचे दिवस",
    steps_cleared: "टप्पे पूर्ण",
    docs_ready: "लॉकरमध्ये तयार",
    checklist_heading: "तुमची टप्प्याटप्प्याची अनुपालन यादी",
    checklist_desc: "हे टप्पे क्रमाने पूर्ण करा. अधिकृत पोर्टल लिंक आणि आवश्यक अर्जासाठी 'तपशील व अर्ज' वर क्लिक करा.",
    toggle_subway_btn: "सबवे मार्ग नकाशा दाखवा/लपवा",
    sla_label: "दिवस कालावधी",
    free_nil: "विनामूल्य / शून्य शुल्क",
    critical_path_tag: "⚡ महत्त्वाचा मार्ग",
    btn_view_details: "तपशील व अर्ज",
    btn_mark_done: "पूर्ण झाले",
    btn_completed: "पूर्ण ✓",
    status_ready: "सुरू करण्यास सज्ज",
    status_in_progress: "● अर्ज करण्यास सज्ज",
    status_prereq_wait: "मागील टप्प्यांची प्रतीक्षा",

    // View 3: Step Details
    back_to_roadmap: "← प्रक्रिया मार्गावर परत जा",
    dossier_sla_label: "शासकीय हमी कालावधी (SLA)",
    dossier_prov_text: "महाराष्ट्र शासनाच्या अधिकृत पोर्टलद्वारे प्रमाणित",
    dossier_apply_btn: "अधिकृत पोर्टलवर अर्ज करा ↗",
    req_docs_heading: "आवश्यक कागदपत्रांची यादी",
    req_docs_sub: "कागदपत्रे गोळा केल्यावर खूण करा. तुमची यादी आपोआप जतन केली जाते:",
    gov_forms_heading: "शासकीय विहित नमुने व अर्ज",
    prior_prereqs_heading: "मागील आवश्यक टप्पे",
    fees_heading: "अधिकृत शासकीय शुल्क",
    payment_channel_label: "शुल्क भरण्याची पद्धत:",
    office_help_heading: "कार्यालय व मदत केंद्र",
    office_addr_label: "कार्यालयाचा पत्ता",
    office_hours_label: "कार्यालयीन वेळ",
    office_hours_val: "सोम-शुक्र सकाळी १०:०० ते संध्याकाळी ५:००",
    office_helpline_label: "हेल्पलाईन / लोकपाल",
    track_app_heading: "तुमच्या अर्जाची सद्यस्थिती तपासा",
    track_app_desc: "तुम्ही अर्ज सादर केला आहे किंवा चलन भरले आहे का? अधिकृत पोर्टलवर थेट स्थिती तपासा:",
    track_token_label: "अर्ज टोकन / चलन क्रमांक",
    track_portal_label: "अधिकृत विभाग पोर्टल निवडा",
    track_btn: "अधिकृत पोर्टलवर स्थिती तपासा ↗",
    mandatory_tag: "अनिवार्य",
    optional_tag: "ऐच्छिक",

    // View 4: Citizen Ledger
    ledger_heading: "माझी प्रगती व कागदपत्र लॉकर",
    ledger_desc: "पूर्ण झालेल्या टप्प्यांचा मागोवा घ्या, भरलेले शुल्क तपासा आणि आवश्यक कागदपत्रे व्यवस्थापित करा. तुमची माहिती सुरक्षित जतन केली जाते.",
    ledger_active_proc: "सक्रिय प्रक्रिया",
    ledger_steps_cleared_of: "टप्पे पूर्ण झाले",
    ledger_fees_tally: "एकूण शुल्क",
    ledger_paid: "भरलेले",
    ledger_pending: "शिल्लक",
    ledger_days_rem: "अंदाजे शिल्लक दिवस",
    ledger_rts_guar: "लोकसेवा हक्क अधिनियम २०१५ अंतर्गत हमी",
    ledger_milestones: "प्रक्रियेचे महत्त्वाचे टप्पे",
    ledger_doc_bag: "एकत्रित कागदपत्रे",
    ledger_doc_sub: "पोर्टलवर अपलोड करण्यासाठी ही कागदपत्रे डिजिटल स्वरूपात (PDF/JPEG) तयार ठेवा:",

    // View 5: Admin
    admin_heading: "प्रशासकीय नोंदवही व पडताळणी पोर्टल",
    admin_desc: "शासकीय नियमांची पडताळणी, थेट पोर्टल स्क्रॅपर आणि डेटाबेस व्यवस्थापन.",
    subtab_scraper: "🌐 थेट पोर्टल स्क्रॅपर",
    subtab_moderation: "🛡️ टप्पे व शुल्क पडताळणी",
    subtab_audit: "📜 ऑडिट नोंदी",
    subtab_feedback: "💬 नागरिकांचा अभिप्राय",
    subtab_regulatory: "🏛️ वैधानिक पोर्टल ऑडिट कॅश",
    admin_crawler_title: "थेट महाराष्ट्र पोर्टल स्क्रॅपर व माहिती संकलन",
    admin_crawler_desc: "शासकीय संकेतस्थळांवरून विहित नमुने, शुल्क, मुदत व प्रक्रियांची माहिती थेट संकलित करते.",
    admin_quick_presets: "पोर्टल निवडा:",
    admin_portal_url: "अधिकृत पोर्टल URL",
    admin_service_hint: "सेवेचे नाव",
    admin_scrape_btn: "माहिती संकलित करा",
    admin_terminal_ready: "प्रणाली सज्ज. माहिती संकलनासाठी वरील बटणावर क्लिक करा.",
    admin_verify_title: "टप्पे व अधिकृत शुल्क पडताळणी",
    admin_verify_desc: "संकलित केलेले टप्पे तपासा, अधिकृत शुल्क निश्चित करा आणि पडताळणी नोंदवा.",
    admin_th_step: "टप्प्याचे नाव",
    admin_th_dept: "विभाग",
    admin_th_fee: "शुल्क (₹)",
    admin_th_sla: "कालावधी (दिवस)",
    admin_th_status: "स्थिती",
    admin_th_actions: "कृती",
    admin_audit_title: "प्रशासकीय ऑडिट नोंदी",
    admin_audit_desc: "सर्व प्रक्रिया बदल आणि पडताळणी नोंदींची सुरक्षित नोंद.",
    admin_feedback_title: "नागरिकांच्या तक्रारी व अभिप्राय",
    admin_feedback_desc: "अद्ययावत नसलेले अर्ज, बदललेले शुल्क किंवा बंद लिंक्सबद्दल नागरिकांचा अभिप्राय.",

    // Footer
    footer_title: "नागरिक कार्य मार्गदर्शक — महाराष्ट्र शासन",
    footer_sub: "महाराष्ट्र लोकसेवा हक्क अधिनियम २०१५ व GIGW मानकांनुसार विकसित",
    footer_source: "सर्व शुल्क व कागदपत्रे अधिकृत संकेतस्थळांवरून घेतलेली आहेत:",

    // Subway
    subway_line_title: "सबवे मेट्रो मार्ग क्रम",
    subway_line_sub: "१ स्थानक = १ शासकीय मंजुरी टप्पा",

    // Share Modal
    share_modal_title: "प्रक्रिया मार्ग सामायिक करा",
    share_modal_desc: "हा प्रमाणित महाराष्ट्र शासकीय मार्ग आणि कागदपत्रांची यादी भागीदार किंवा कुटुंबीयांसोबत सामायिक करा.",
    share_direct_link: "थेट वेब लिंक",
    share_copy_btn: "कॉपी करा",
    share_whatsapp_btn: "व्हॉट्सॲपवर माहिती पाठवा",
    share_toast: "लिंक क्लिपबोर्डवर कॉपी झाली आहे!"
  }
};

/**
 * Procedural Tasks & Steps Full Marathi Translations
 * Keyed exactly to database task IDs and step IDs
 */
const TASK_TRANSLATIONS = {
  "task-mah-small-biz": {
    title: "लहान व्यवसाय किंवा किरकोळ दुकान नोंदणी (महाराष्ट्र गुमास्ता व दुकाने अधिनियम)",
    description: "महाराष्ट्र दुकाने व आस्थापना अधिनियम २०१७ अंतर्गत नोंदणी, उद्यम एमएसएमई प्रमाणपत्र आणि नामफलक नियमावलीचे संपूर्ण टप्पे.",
    municipality: "मुंबई व महाराष्ट्र राज्यव्यापी (LMS / आपले सरकार)",
    category: "व्यापार व वाणिज्य",
    steps: {
      "mah-biz-1": {
        title: "पॅन (PAN) व केंद्र शासन उद्यम एमएसएमई विनामूल्य नोंदणी",
        description: "आधार ओटीपी पडताळणीद्वारे केंद्र शासनाच्या उद्यम नोंदणी पोर्टलवर विनामूल्य राष्ट्रीय एमएसएमई प्रमाणपत्र व व्यवसाय पॅन कार्ड मिळवणे.",
        department: "केंद्रीय सूक्ष्म, लघु व मध्यम उद्योग मंत्रालय (उद्यम महाराष्ट्र)"
      },
      "mah-biz-2": {
        title: "व्यावसायिक जागा पडताळणी, नोंदणीकृत भाडेकरार व कर पावती",
        description: "महाराष्ट्रात व्यावसायिक जागेचा नोंदणीकृत भाडेकरार, मालमत्ता कर पावती किंवा वीज बिलाद्वारे अधिकृत जागेची पडताळणी करणे.",
        department: "नोंदणी महानिरीक्षक व मुद्रांक नियंत्रक (IGR महाराष्ट्र)"
      },
      "mah-biz-3": {
        title: "महाराष्ट्र गुमास्ता परवाना / नमुना 'अ' सूचना (LMS महाऑनलाइन)",
        description: "महाराष्ट्र दुकाने व आस्थापना अधिनियम २०१७ अंतर्गत नोंदणी. ० ते ९ कर्मचाऱ्यांसाठी तात्काळ नमुना 'अ' सूचना पावती; १० किंवा अधिक कर्मचाऱ्यांसाठी नमुना 'फ' नोंदणी प्रमाणपत्र.",
        department: "महाराष्ट्र कामगार विभाग (LMS महाऑनलाइन व आपले सरकार)"
      },
      "mah-biz-4": {
        title: "महाराष्ट्र व्यवसाय कर नोंदणी (PTEC व PTRC - महाजीएसटी)",
        description: "महाराष्ट्र व्यवसाय, व्यापार, उपजीविका व नोकऱ्यांवरील कर अधिनियम १९७५ अन्वये नोंदणी. आस्थापनेसाठी PTEC आणि पगारी कर्मचाऱ्यांसाठी PTRC अनिवार्य.",
        department: "वस्तू व सेवा कर विभाग, महाराष्ट्र शासन (MahaGST)"
      },
      "mah-biz-5": {
        title: "महानगरपालिका नामफलक परवानगी व मराठी देवनागरी ठळक अक्षरे",
        description: "महाराष्ट्र महानगरपालिका नियमांनुसार दुकानाचा मुख्य नामफलक ठळक मराठी देवनागरी लिपीत असणे अनिवार्य; नामफलकाचे आकारमान इतर कोणत्याही भाषेपेक्षा लहान असू नये.",
        department: "बीएमसी परवाना व मालमत्ता खाते (कलम ३२८/३९४)"
      },
      "mah-biz-6": {
        title: "व्यावसायिक चालू बँक खाते व ई-पेमेंट मर्चंट सुविधा",
        description: "प्रमाणित उद्यम प्रमाणपत्र, गुमास्ता नमुना 'अ'/'फ' आणि पॅन कार्डच्या आधारे अधिकृत बँकेत व्यावसायिक चालू खाते व डिजिटल पेमेंट सुविधा सुरू करणे.",
        department: "कॉर्पोरेट व्यवहार मंत्रालय (RoC मुंबई) व बँकिंग प्रणाली"
      }
    }
  },

  "task-mum-bakery": {
    title: "वांद्रे, मुंबई येथे व्यावसायिक बेकरी व कॅफे नोंदणी (BMC प्रभाग H/West)",
    description: "मुंबई महानगरपालिका (BMC) प्रभाग एच/वेस्ट अंतर्गत व्यावसायिक बेकरी व कॅफे सुरू करण्यासाठी आरोग्य परवाना, अग्निशामक दल एनओसी आणि अन्न सुरक्षा परवान्याचे संपूर्ण टप्पे.",
    municipality: "मुंबई (MCGM / BMC)",
    category: "अन्न व आतिथ्य",
    steps: {
      "stop-01": {
        title: "कंपनी नोंदणी (MCA SPICe+), RoC मुंबई व पॅन क्रमांक",
        description: "कंपनी नोंदणीसाठी कॉर्पोरेट व्यवहार मंत्रालयाच्या SPICe+ प्रणालीद्वारे नोंदणी आणि महाराष्ट्र कर अधिकार क्षेत्राशी जोडलेले पॅन (PAN) व टॅन (TAN) मिळवणे.",
        department: "कॉर्पोरेट व्यवहार मंत्रालय (RoC मुंबई) व GSTN"
      },
      "stop-02": {
        title: "व्यावसायिक भाडेकरार नोंदणी व गुमास्ता परवाना (प्रभाग H/West)",
        description: "दुय्यम निबंधक कार्यालयात नोंदणीकृत भाडेकरार, बीएमसी मालमत्ता कर SAC क्रमांक पडताळणी आणि आपले सरकार/LMS द्वारे महाराष्ट्र गुमास्ता नोंदणी.",
        department: "बीएमसी कामगार व दुकाने विभाग (प्रभाग H/West)"
      },
      "stop-03": {
        title: "मुंबई अग्निशामक दल (MFB) आग सुरक्षा तपासणी एनओसी",
        description: "महाराष्ट्र आग प्रतिबंधक व जीवन सुरक्षा उपाययोजना अधिनियम २००६ अंतर्गत बेकिंग ओव्हन, गॅस पाईपलाईन आणि आपत्कालीन मार्गांची अनिवार्य सुरक्षा तपासणी एनओसी.",
        department: "मुंबई अग्निशामक दल (मुख्य अग्निशमन अधिकारी MFB)"
      },
      "stop-03a": {
        title: "एफएसएसएआय (FSSAI) राज्य अन्न व्यवसाय परवाना (FoSCoS महाराष्ट्र)",
        description: "FSSAI पश्चिम प्रादेशिक कार्यालय आणि महाराष्ट्र अन्न व औषध प्रशासन (FDA) द्वारे व्यावसायिक बेकरी उत्पादन व विक्रीसाठी अधिकृत राज्य अन्न परवाना.",
        department: "भारतीय अन्न सुरक्षा व मानके प्राधिकरण (FSSAI) व एफडीए महाराष्ट्र"
      },
      "stop-03b": {
        title: "महाराष्ट्र प्रदूषण नियंत्रण मंडळ (MPCB) हरित श्रेणी संमती (CTE/CTO)",
        description: "व्यावसायिक बेकरी, ओव्हन धूर नळकांडी आणि सांडपाणी निचरा यासाठी जल व वायू प्रदूषण नियंत्रण अधिनियमांनुसार MPCB ची स्थापना व संचलन संमती.",
        department: "महाराष्ट्र प्रदूषण नियंत्रण मंडळ (MPCB प्रादेशिक कार्यालय)"
      },
      "stop-04": {
        title: "बीएमसी कलम ३९४ आरोग्य व्यापार परवाना (MOH प्रभाग H/West)",
        description: "बृहन्मुंबई महानगरपालिका कायदा १८८८ च्या कलम ३९४ अन्वये ग्रेटर मुंबईत भोजनालय व खाद्यपदार्थ निर्मितीसाठी मुख्य नागरी आरोग्य व्यापार परवाना.",
        department: "सार्वजनिक आरोग्य खाते, बीएमसी (वैद्यकीय आरोग्य अधिकारी - प्रभाग H/West)"
      },
      "stop-05": {
        title: "खुल्या जागेत भोजनालय बैठक व देवनागरी नामफलक मंजुरी (प्रभाग H/West)",
        description: "बीएमसी ओपन-टू-स्काय डायनिंग धोरणांतर्गत बाहेर बसण्याची परवानगी आणि ठळक मराठी देवनागरी अक्षरांसह कायदेशीर नामफलक मंजुरी.",
        department: "बीएमसी परवाना व मालमत्ता खाते (कलम ३२८/३९४)"
      },
      // Aliases for backward compatibility
      "mum-bakery-1": {
        title: "कंपनी नोंदणी (MCA SPICe+), RoC मुंबई व पॅन क्रमांक",
        description: "कंपनी नोंदणीसाठी कॉर्पोरेट व्यवहार मंत्रालयाच्या SPICe+ प्रणालीद्वारे नोंदणी आणि पॅन क्रमांक मिळवणे.",
        department: "कॉर्पोरेट व्यवहार मंत्रालय (RoC मुंबई) व जीएसटी"
      },
      "mum-bakery-2": {
        title: "व्यावसायिक भाडेकरार नोंदणी व गुमास्ता परवाना (प्रभाग H/West)",
        description: "दुय्यम निबंधक कार्यालयात नोंदणीकृत भाडेकरार व महाराष्ट्र गुमास्ता नोंदणी.",
        department: "बीएमसी कामगार व दुकाने विभाग (प्रभाग H/West)"
      },
      "mum-bakery-3": {
        title: "मुंबई अग्निशामक दल (MFB) आग सुरक्षा तपासणी एनओसी",
        description: "अग्निशामक उपकरणांची तपासणी आणि मुख्य अग्निशमन अधिकाऱ्यांची (CFO) एनओसी घेणे.",
        department: "मुंबई अग्निशामक दल (मुख्य अग्निशमन अधिकारी MFB)"
      },
      "mum-bakery-3a": {
        title: "एफएसएसएआय (FSSAI) राज्य अन्न व्यवसाय परवाना (FoSCoS महाराष्ट्र)",
        description: "FSSAI आणि महाराष्ट्र अन्न व औषध प्रशासन द्वारे अधिकृत राज्य अन्न परवाना.",
        department: "भारतीय अन्न सुरक्षा व मानके प्राधिकरण (FSSAI) व एफडीए महाराष्ट्र"
      },
      "mum-bakery-3b": {
        title: "महाराष्ट्र प्रदूषण नियंत्रण मंडळ (MPCB) हरित श्रेणी संमती (CTE/CTO)",
        description: "प्रदूषण नियंत्रण मंडळाची स्थापना व संचलन संमती.",
        department: "महाराष्ट्र प्रदूषण नियंत्रण मंडळ (MPCB प्रादेशिक कार्यालय)"
      },
      "mum-bakery-4": {
        title: "बीएमसी कलम ३९४ आरोग्य व्यापार परवाना (MOH प्रभाग H/West)",
        description: "मुंबई महानगरपालिका कायदा १८८८ च्या कलम ३९४ अन्वये अधिकृत अंतिम व्यापार परवाना.",
        department: "सार्वजनिक आरोग्य खाते, बीएमसी (वैद्यकीय आरोग्य अधिकारी - प्रभाग H/West)"
      },
      "mum-bakery-5": {
        title: "खुल्या जागेत भोजनालय बैठक व देवनागरी नामफलक मंजुरी (प्रभाग H/West)",
        description: "खुल्या जागेत बैठक आणि मराठी नामफलक मंजुरी.",
        department: "बीएमसी परवाना व मालमत्ता खाते (कलम ३२८/३९४)"
      }
    }
  },

  "task-pune-restaurant": {
    title: "पुणे येथे रेस्टॉरंट, कॅफे किंवा भोजनालय सुरू करणे (PMC)",
    description: "पुणे महानगरपालिका (PMC) हद्दीत अधिकृत अन्न व्यवसाय सुरू करण्यासाठी गुमास्ता, अग्निशामक एनओसी, अन्न परवाना व आरोग्य परवान्याची नियमावली.",
    municipality: "पुणे (PMC / PMRDA)",
    category: "अन्न व आतिथ्य",
    steps: {
      "pune-food-1": {
        title: "कंपनी नोंदणी व पुणे मनपा (PMC) गुमास्ता सूचना",
        description: "संस्थेची अधिकृत नोंदणी आणि महाराष्ट्र LMS पोर्टलद्वारे पुणे महानगरपालिका (PMC) दुकाने व आस्थापना नोंदणी/सूचना पावती प्राप्त करणे.",
        department: "महाराष्ट्र कामगार विभाग (LMS महाऑनलाइन व आपले सरकार)"
      },
      "pune-food-2": {
        title: "पुणे मनपा (PMC) मालमत्ता कर खाते व थकबाकी नसलेला दाखला",
        description: "पीएमसी Ptis पोर्टलवर मालमत्ता कर खात्याची पडताळणी आणि व्यावसायिक जागेसाठी शून्य थकबाकी दाखला (No Dues Certificate) मिळवणे.",
        department: "पुणे महानगरपालिका (PMC मालमत्ता कर व आरोग्य विभाग)"
      },
      "pune-food-3": {
        title: "पुणे मध्यवर्ती अग्निशामक दल एनओसी (टिंबर मार्केट मुख्यालय)",
        description: "व्यावसायिक स्वयंपाकघर, गॅस पाईपलाईन आणि आपत्कालीन निर्गमन मार्गांची पुणे महानगरपालिका अग्निशमन विभागाकडून सुरक्षितता तपासणी व एनओसी.",
        department: "पुणे अग्निशामक दल (PMC मध्यवर्ती अग्निशमन कमान)"
      },
      "pune-food-4": {
        title: "एफएसएसएआय (FSSAI) महाराष्ट्र राज्य अन्न परवाना व MPCB संमती",
        description: "FoSCoS महाराष्ट्र एफडीए कडून अन्न सुरक्षा परवाना आणि MPCB पुणे प्रादेशिक कार्यालयाकडून हरित श्रेणी प्रदूषण संमती मिळवणे.",
        department: "भारतीय अन्न सुरक्षा व मानके प्राधिकरण (FSSAI) व एफडीए महाराष्ट्र"
      },
      "pune-food-5": {
        title: "पुणे मनपा आरोग्य विभाग भोजनालय व व्यापार परवाना",
        description: "महाराष्ट्र महानगरपालिका अधिनियम कलम ३७६ अन्वये पुणे मनपा हद्दीत रेस्टॉरंट व भोजनालय चालवण्यासाठी अंतिम वैधानिक आरोग्य परवाना.",
        department: "पुणे महानगरपालिका (PMC आरोग्य विभाग)"
      },
      // Aliases
      "pune-rest-1": {
        title: "कंपनी नोंदणी व पुणे मनपा (PMC) गुमास्ता सूचना",
        description: "पुणे महानगरपालिकेच्या कामगार विभागाकडून दुकाने नोंदणी.",
        department: "महाराष्ट्र कामगार विभाग (LMS महाऑनलाइन व आपले सरकार)"
      },
      "pune-rest-2": {
        title: "पुणे मध्यवर्ती अग्निशामक दल एनओसी",
        description: "पुणे अग्निशमन दलाकडून तात्पुरती व अंतिम एनओसी घेणे.",
        department: "पुणे अग्निशामक दल (PMC मध्यवर्ती अग्निशमन कमान)"
      },
      "pune-rest-3": {
        title: "एफएसएसएआय (FSSAI) महाराष्ट्र राज्य अन्न परवाना व MPCB संमती",
        description: "अन्न व औषध प्रशासन महाराष्ट्र अंतर्गत पुणे जिल्ह्यासाठी रेस्टॉरंट अन्न सुरक्षा परवाना मिळवणे.",
        department: "भारतीय अन्न सुरक्षा व मानके प्राधिकरण (FSSAI) व एफडीए महाराष्ट्र"
      },
      "pune-rest-4": {
        title: "पुणे मनपा आरोग्य विभाग भोजनालय व व्यापार परवाना",
        description: "पुणे महानगरपालिकेचा अंतिम व्यापार परवाना घेणे.",
        department: "पुणे महानगरपालिका (PMC आरोग्य विभाग)"
      }
    }
  },

  "task-mum-construction": {
    title: "व्यावसायिक इमारत बांधकाम नकाशा मंजुरी व भोगवटा प्रमाणपत्र (AutoDCR BMC)",
    description: "बृहन्मुंबई विकास नियंत्रण व संवर्धन नियमावली (DCPR-2034) अंतर्गत ऑटो-डीसीआर इमारत नकाशा मंजुरी, आयओडी, जोते प्रमाणपत्र व पूर्णत्व दाखला.",
    municipality: "मुंबई (MCGM / BMC)",
    category: "इमारत व नगरविकास",
    steps: {
      "mum-bp-1": {
        title: "प्रॉपर्टी कार्ड (PR Card), सीटीएस नकाशा व आयजीआर मालकी हक्क तपासणी",
        description: "नगर भूमापन कार्यालयाकडून (CTSO) प्रमाणित डिजिटल प्रॉपर्टी कार्ड, सीटीएस नकाशा आणि आयजीआर महाराष्ट्र वर ३० वर्षांचा बोजा नसलेला दाखला तपासणे.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      "mum-bp-2": {
        title: "वास्तुविशारद ऑटो-डीसीआर (AutoDCR) आराखडा व नामंजुरी सूचना (IOD)",
        description: "नोंदणीकृत वास्तुविशारदाद्वारे बीएमसी ऑटो-डीसीआर पोर्टलवर कॅड ब्लूप्रिंट सादर करणे, एफएसआय तपासणी आणि वैधानिक IOD अटी मिळवणे.",
        department: "बीएमसी इमारत प्रस्ताव विभाग (AutoDCR कक्ष)"
      },
      "mum-bp-3": {
        title: "एकात्मिक वैधानिक मंजुऱ्या (CFO आग एनओसी, वाहतूक व पर्जन्य जलवाहिन्या)",
        description: "बांधकाम सुरू करण्यापूर्वी IOD अटींची पूर्तता: मुख्य अग्निशमन अधिकारी एनओसी, वाहतूक पोलीस परवानगी आणि पर्जन्य जलवाहिन्या (SWD) शेरे घेणे.",
        department: "मुंबई अग्निशामक दल (मुख्य अग्निशमन अधिकारी MFB)"
      },
      "mum-bp-4": {
        title: "जोते बांधकाम प्रारंभ प्रमाणपत्र (Plinth CC)",
        description: "इमारतीचा पाया/जोते पूर्ण झाल्यावर कार्यकारी अभियंत्यांकडून प्रत्यक्ष जागेची तपासणी, हद्दीची खात्री आणि प्लिंथ सीसी मंजुरी.",
        department: "बीएमसी इमारत प्रस्ताव विभाग (AutoDCR कक्ष)"
      },
      "mum-bp-5": {
        title: "अंतिम इमारत पूर्णत्व तपासणी व भोगवटा प्रमाणपत्र (OC)",
        description: "संपूर्ण बांधकाम पूर्ण झाल्यावर लिफ्ट तपासणी, पाणी जोडणी चाचणी आणि संयुक्त पाहणीनंतर अंतिम पूर्ण भोगवटा प्रमाणपत्र (OC) जारी करणे.",
        department: "बीएमसी इमारत प्रस्ताव विभाग (AutoDCR कक्ष)"
      },
      // Aliases
      "mum-bld-1": {
        title: "प्रॉपर्टी कार्ड (PR Card), सीटीएस नकाशा व आयजीआर मालकी हक्क तपासणी",
        description: "जमिनीचे स्पष्ट मालकी शीर्षक, ७/१२ किंवा पीआर कार्ड तपासणे.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      "mum-bld-2": {
        title: "वास्तुविशारद ऑटो-डीसीआर (AutoDCR) आराखडा व नामंजुरी सूचना (IOD)",
        description: "DCPR-2034 नियमांनुसार ऑनलाइन कॉम्प्युटर तपासणी आणि मंजुरी सूचना (IOD) आदेश प्राप्त करणे.",
        department: "बीएमसी इमारत प्रस्ताव विभाग (AutoDCR कक्ष)"
      },
      "mum-bld-3": {
        title: "एकात्मिक वैधानिक मंजुऱ्या (CFO आग एनओसी, वाहतूक व पर्जन्य जलवाहिन्या)",
        description: "मुख्य अग्निशमन अधिकारी (CFO), राज्य पर्यावरण समिती (SEAC) आणि वाहतूक पोलिसांकडून ना-हरकत प्रमाणपत्रे.",
        department: "मुंबई अग्निशामक दल (मुख्य अग्निशमन अधिकारी MFB)"
      },
      "mum-bld-4": {
        title: "जोते बांधकाम प्रारंभ प्रमाणपत्र (Plinth CC)",
        description: "इमारतीचा पाया पूर्ण झाल्यावर बीएमसी अभियंत्यांकडून प्रत्यक्ष जागेची तपासणी व प्लिंथ सीसी.",
        department: "बीएमसी इमारत प्रस्ताव विभाग (AutoDCR कक्ष)"
      },
      "mum-bld-5": {
        title: "अंतिम इमारत पूर्णत्व तपासणी व भोगवटा प्रमाणपत्र (OC)",
        description: "इमारत पूर्ण झाल्यावर प्रत्यक्ष पाहणी करून नागरिकांना वापरण्यासाठी अधिकृत भोगवटा प्रमाणपत्र जारी करणे.",
        department: "बीएमसी इमारत प्रस्ताव विभाग (AutoDCR कक्ष)"
      }
    }
  },

  "task-mah-712-mutation": {
    title: "कृषी व जमिनीचा ७/१२ (सातबारा) फेरफार व वारस नोंद (ई-फेरफार)",
    description: "महाराष्ट्र जमीन महसूल संहिता (MLRC) कलम १५० अन्वये ई-फेरफार पोर्टलद्वारे ऑनलाइन फेरफार नोंद, १५ दिवसांची जाहीर नोटीस व डिजिटल स्वाक्षरीचा सातबारा.",
    municipality: "महाराष्ट्र राज्यव्यापी (महाभूमी / ई-फेरफार)",
    category: "जमीन महसूल व मालमत्ता",
    steps: {
      "mah-mut-1": {
        title: "नोंदणीकृत खरेदीखत व आयजीआर सूची-२ (Index-II) पडताळणी",
        description: "IGR महाराष्ट्र ई-सर्च वर अधिकृत नोंदणीकृत खरेदीखत, बक्षीसपत्र किंवा वाटपपत्राची तपासणी, दस्त क्रमांक आणि भरलेले मुद्रांक शुल्क तपासणे.",
        department: "नोंदणी महानिरीक्षक व मुद्रांक नियंत्रक (IGR महाराष्ट्र)"
      },
      "mah-mut-2": {
        title: "महाभूमी ई-हक्क पोर्टलवर ऑनलाइन ई-फेरफार अर्ज दाखल करणे",
        description: "महाराष्ट्र जमीन महसूल संहिता (MLRC) १९६६ च्या कलम १४९ अंतर्गत महाभूमी ई-हक्क प्रणालीवर फेरफार नोंद अर्ज दाखल करणे.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      "mah-mut-3": {
        title: "कलम १५० अन्वये जाहीर नोटीस जारी करणे (१५ दिवसांची हरकत मुदत)",
        description: "७/१२ उताऱ्यातील सर्व हितसंबंधी व्यक्ती, कायदेशीर वारस व सह-खातेदारांना तलाठ्यांकडून वैधानिक नोटीस बजावणे; १५ दिवसांची जाहीर मुदत.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      "mah-mut-4": {
        title: "तलाठी स्थळ पाहणी, पंचनामा व पडताळणी अहवाल",
        description: "तलाठ्यांकडून जागेवर प्रत्यक्ष पाहणी, प्रत्यक्ष ताबा खात्री, शेती/अकृषिक जमीन वर्गीकरण तपासणी आणि अहवाल सादर करणे.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      "mah-mut-5": {
        title: "मंडळ अधिकारी / तहसीलदार मंजुरी व डिजिटल स्वाक्षरीचा ७/१२ उतारा",
        description: "मंडळ अधिकाऱ्यांद्वारे डिजिटल स्वाक्षरीने फेरफार नोंद प्रमाणित करणे; महाभूमीवर मालकी हक्काची अद्ययावत नोंद व डिजिटल स्वाक्षरीचा ७/१२ आणि ८-अ उतारा जारी.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      // Aliases
      "mah-712-1": {
        title: "नोंदणीकृत खरेदीखत व आयजीआर सूची-२ (Index-II) पडताळणी",
        description: "दुय्यम निबंधक कार्यालयात नोंदणीकृत खरेदीखत तयार करणे.",
        department: "नोंदणी महानिरीक्षक व मुद्रांक नियंत्रक (IGR महाराष्ट्र)"
      },
      "mah-712-2": {
        title: "महाभूमी ई-हक्क पोर्टलवर ऑनलाइन ई-फेरफार अर्ज दाखल करणे",
        description: "महाभूमी ई-फेरफार प्रणालीवर फेरफार नोंद क्रमांक मिळवणे.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      "mah-712-3": {
        title: "कलम १५० अन्वये जाहीर नोटीस जारी करणे (१५ दिवसांची हरकत मुदत)",
        description: "संबंधित गावच्या तलाठ्याकडून स्थळ पाहणी आणि १५ दिवसांची नोटीस.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      },
      "mah-712-4": {
        title: "मंडळ अधिकारी / तहसीलदार मंजुरी व डिजिटल स्वाक्षरीचा ७/१२ उतारा",
        description: "मंडळ अधिकाऱ्यांद्वारे फेरफार नोंदीची तपासणी व अंतिम मंजुरी.",
        department: "महसूल व वन विभाग, महाराष्ट्र शासन (महाभूमी ई-फेरफार)"
      }
    }
  },

  "task-mum-water-connection": {
    title: "नवीन व्यावसायिक / घरगुती नळ जोडणी (MCGM जल अभियंता विभाग)",
    description: "मुंबई महानगरपालिका कायदा १८८८ च्या कलम १४० अंतर्गत परवानाधारक प्लंबर नकाशा, रस्ता खोदणे परवानगी, पाईप जोडणी व अधिकृत वॉटर मीटर वाटप.",
    municipality: "मुंबई (MCGM / BMC)",
    category: "नागरी पाणीपुरवठा व उपयोगिता",
    steps: {
      "mum-wat-1": {
        title: "बीएमसी मालमत्ता कर SAC क्रमांक व इमारत आराखडा पडताळणी",
        description: "बीएमसी नागरिक पोर्टलवर एसएसी (SAC) ग्राहक क्रमांकाची पडताळणी आणि अंतर्गत प्लंबिंग डिझाइन मंजुरीची खातरजमा करणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      "mum-wat-2": {
        title: "परवानाधारक प्लंबर नकाशा व ऑनलाइन अर्ज (आपले सरकार / बीएमसी)",
        description: "बीएमसी परवानाधारक प्लंबरकडून जलवाहिनी जोडणी आराखडा तयार करणे आणि आवश्यक कनेक्शन व्यासाची (१५ मिमी ते १०० मिमी) गणना सादर करणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      "mum-wat-3": {
        title: "सहाय्यक अभियंता (जलकामे) स्थळ पाहणी व तांत्रिक व्यवहार्यता तपासणी",
        description: "प्रभाग सहाय्यक अभियंत्यांद्वारे मुख्य जलवाहिनीची पाहणी, पाण्याचा दाब व पुरवठा तपासणी आणि जोडणी बिंदूस (Tapping Point) मंजुरी.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      "mum-wat-4": {
        title: "रस्ता खोदणे (Trenching) परवानगी व रस्ता दुरुस्ती शुल्क भरणा",
        description: "पाईपलाईन टाकण्यासाठी बीएमसी परिरक्षण विभागाकडून रस्ता/फूटपाथ खोदण्याची परवानगी घेणे व रस्ता पूर्ववत करण्याचे शुल्क भरणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      "mum-wat-5": {
        title: "मुख्य जलवाहिनी टॅपिंग, वॉटर मीटर कॅलिब्रेशन व पाणीपुरवठा सुरू",
        description: "बीएमसी जलकामे पथकाद्वारे मुख्य जलवाहिनी जोडणे, प्रमाणित कॅलिब्रेटेड वॉटर मीटर बसवणे आणि अधिकृत पाणीपुरवठा सुरू करणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      // Aliases
      "mum-water-1": {
        title: "बीएमसी मालमत्ता कर SAC क्रमांक व इमारत आराखडा पडताळणी",
        description: "बीएमसी परवानाधारक प्लंबरकडून प्लंबिंग लेआउट तयार करणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      "mum-water-2": {
        title: "रस्ता खोदणे (Trenching) परवानगी व रस्ता दुरुस्ती शुल्क भरणा",
        description: "पाईप टाकण्यासाठी रस्ते विभागाकडून रस्ता खोदणे परवानगी घेणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      "mum-water-3": {
        title: "मुख्य जलवाहिनी टॅपिंग, वॉटर मीटर कॅलिब्रेशन व पाणीपुरवठा सुरू",
        description: "महानगरपालिकेच्या मुख्य पाईपलाईनमधून अधिकृत कनेक्शन जोडणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      },
      "mum-water-4": {
        title: "अंतिम जल जोडणी मंजुरी आदेश व जल बिल ग्राहक क्रमांक",
        description: "जल अभियंत्यांकडून अंतिम मंजुरी आदेश जारी होणे.",
        department: "बीएमसी जल अभियंता खाते (पाणीपुरवठा विभाग)"
      }
    }
  },

  "task-mah-rts-certificates": {
    title: "नागरिक वैधानिक प्रमाणपत्रे (उत्पन्न, अधिवास व जात दाखला - आपले सरकार)",
    description: "महाराष्ट्र लोकसेवा हक्क अधिनियम (RTS २०१५) अंतर्गत तहसीलदार कार्यालयाकडून १५ दिवसांच्या वैधानिक हमीसह अधिकृत प्रमाणपत्रे मिळवण्याचा मार्ग.",
    municipality: "महाराष्ट्र राज्यव्यापी (आपले सरकार RTS)",
    category: "नागरिक व महसूल दाखले",
    steps: {
      "mah-rts-1": {
        title: "आपले सरकार पोर्टल नागरिक नोंदणी व मोबाईल आधार ई-केवायसी",
        description: "महाराष्ट्र शासनाच्या अधिकृत आपले सरकार पोर्टलवर आधार ओटीपीद्वारे नागरिक खाते उघडून ई-केवायसी प्रमाणीकरण पूर्ण करणे.",
        department: "आपले सरकार नागरिक सेवा (महाराष्ट्र लोकसेवा हक्क आयोग)"
      },
      "mah-rts-2": {
        title: "उत्पन्न प्रमाणपत्र अर्ज व तलाठी पडताळणी (हमी मुदत: १५ दिवस)",
        description: "लोकसेवा हक्क अधिनियम २०१५ अंतर्गत फॉर्म १६ / वेतन प्रमाणपत्र / तलाठी उत्पन्न अहवालासह महसूल विभागाकडे वैधानिक उत्पन्न दाखल्यासाठी अर्ज.",
        department: "आपले सरकार नागरिक सेवा (महाराष्ट्र लोकसेवा हक्क आयोग)"
      },
      "mah-rts-3": {
        title: "वय, राष्ट्रीयत्व व अधिवास प्रमाणपत्र (हमी मुदत: १५ दिवस)",
        description: "महसूल व वन विभागाच्या नियमांनुसार महाराष्ट्रात १५ वर्षे सलग वास्तव्याचा पुरावा सादर करून अधिवास (Domicile) प्रमाणपत्रासाठी अर्ज.",
        department: "आपले सरकार नागरिक सेवा (महाराष्ट्र लोकसेवा हक्क आयोग)"
      },
      "mah-rts-4": {
        title: "तहसीलदार डिजिटल स्वाक्षरी व बारकोड दाखला वाटप",
        description: "सक्षम अधिकाऱ्यांद्वारे (नायब तहसीलदार / तहसीलदार) अर्जाची तपासणी आणि तात्काळ पडताळणीसाठी क्यूआर कोडयुक्त डिजिटल स्वाक्षरीचा अधिकृत दाखला जारी करणे.",
        department: "आपले सरकार नागरिक सेवा (महाराष्ट्र लोकसेवा हक्क आयोग)"
      }
    }
  }
};

/**
 * Common Marathi Document Name Translations
 * Comprehensive coverage of all 59 procedural documents and statutory filings
 */
const DOC_TRANSLATIONS = {
  // Exact Document Names from Database
  "15 Years Residence Proof in Maharashtra": "महाराष्ट्रात १५ वर्षे वास्तव्याचा पुरावा (अधिवास)",
  "Aadhaar Card Linked to Mobile": "मोबाईल क्रमांकाशी जोडलेले आधार कार्ड",
  "Aadhaar Cards of All New Purchasers / Heirs": "सर्व खरेदीदार व वारसांचे आधार कार्ड",
  "Affidavit of Uncontested Possession": "बिनतक्रार प्रत्यक्ष ताबा प्रतिज्ञापत्र",
  "Applicant Self-Certified KYC & Passport Photo": "अर्जदाराचे स्व-प्रमाणित ई-केवायसी व पासपोर्ट फोटो",
  "Approved Building Proposal Sanction Plan": "बीएमसी मंजूर इमारत प्रस्ताव नकाशा",
  "Architect & Structural Engineer Supervision Undertaking": "वास्तुविशारद व स्ट्रक्चरल अभियंता देखरेख हमीपत्र",
  "Architect Fire Escape Blueprint": "वास्तुविशारद अग्निशमन निर्गमन आराखडा",
  "Architectural Kitchen & Seating Fire Evacuation Plan": "स्वयंपाकघर व बैठक व्यवस्था आपत्कालीन नकाशा",
  "AutoDCR Pre-Checked Architectural CAD Plans": "ऑटो-डीसीआर तपासलेले वास्तुविशारद कॅड नकाशे",
  "BMC Property Tax Last Paid Receipt (SAC No.)": "बीएमसी मालमत्ता कर चालू पावती (SAC क्रमांक)",
  "Baking Process Flowchart & Raw Material Matrix": "बेकिंग प्रक्रिया प्रवाह तक्ता व कच्चा माल तपशील",
  "Building Cooperative Society (CHS) No Objection Certificate": "गृहनिर्माण संस्था (CHS) ना-हरकत प्रमाणपत्र (NOC)",
  "Cancelled Cheque or Bank Passbook Front Page": "रद्द केलेला धनादेश किंवा बँक पासबुक पहिले पान",
  "Certified Digital Property Card (PR Card)": "प्रमाणित डिजिटल प्रॉपर्टी कार्ड (PR Card)",
  "Certified Index II from IGR Portal": "नोंदणी महानिरीक्षक (IGR) पोर्टलची प्रमाणित सूची-२ (Index-II)",
  "Citizen Digital Passport Photograph": "नागरिकाचे डिजिटल पासपोर्ट आकाराचे छायाचित्र",
  "Color Elevation & Signboard Artwork Layout": "रंगीत इमारत देखावा व मराठी नामफलक आराखडा",
  "Comprehensive Fire Fighting System Schematic": "सर्वसमावेशक अग्निशमन यंत्रणा लेआउट",
  "Consolidated Civic Dossier (Gumasta + Udyam + PAN + PTEC)": "एकत्रित नागरी कागदपत्र संच (गुमास्ता + उद्यम + पॅन + PTEC)",
  "Consolidated Inter-Agency Clearances Bundle": "एकत्रित आंतर-शासकीय मंजुरी संच",
  "Current BMC Property Tax Paid Receipt (SAC)": "चालू बीएमसी मालमत्ता कर भरणा पावती (SAC)",
  "Current Digital 7/12 (Satbara) & 8A Extract": "चालू डिजिटल स्वाक्षरीचा ७/१२ (सातबारा) व ८-अ उतारा",
  "Demarcated CTS Sheet from Superintendent of Land Records": "भूमी अभिलेख अधीक्षकांकडून सीमांकित सीटीएस शीट",
  "Directors KYC & Digital Signature (DSC Class III)": "संचालकांचे केवायसी व डिजिटल स्वाक्षरी (DSC वर्ग-३)",
  "Draft Memorandum & Articles of Association (e-MOA/AOA)": "संस्थेची घटना व नियमावली (e-MOA व AOA)",
  "Entity PAN Card & Gumasta Intimation": "संस्थेचे पॅन कार्ड व गुमास्ता सूचना पावती",
  "Facade Photo of Shop Building": "दुकानाच्या इमारतीचा दर्शनी भागाचा फोटो",
  "Final CFO Fire Operational NOC": "मुख्य अग्निशमन अधिकारी (CFO) अंतिम संचलन एनओसी",
  "Food Handler Medical Fitness Certificates (Form IX)": "अन्न हाताळणाऱ्या कर्मचाऱ्यांचे वैद्यकीय प्रमाणपत्र (नमुना ९)",
  "Food Safety Management System (FSMS) Plan & SOP": "अन्न सुरक्षा व्यवस्थापन प्रणाली (FSMS) आराखडा व एसओपी",
  "Government Approved Water Meter Calibration Certificate": "शासकीय प्रमाणित वॉटर मीटर कॅलिब्रेशन दाखला",
  "Grease Trap & Kitchen Exhaust Blueprint": "ग्रीस ट्रॅप व स्वयंपाकघर एक्झॉस्ट डक्ट आराखडा",
  "Grease Trap Installation Scheme": "ग्रीस ट्रॅप स्थापना योजना",
  "LPG / PNG Gas Pipeline Installation Certificate": "एलपीजी/पीएनजी गॅस पाईपलाईन सुरक्षा प्रमाणपत्र",
  "Last Paid PMC Property Tax Receipt": "पुणे मनपा (PMC) चालू मालमत्ता कर भरणा पावती",
  "Licensed Plumber Undertaking & License Copy": "परवानाधारक प्लंबरचे हमीपत्र व परवाना प्रत",
  "MCGM Municipal Water Connection Sanction Card": "बीएमसी महानगरपालिका पाणी जोडणी मंजुरी कार्ड",
  "MCGM Pest Control Officer (PCO) Certificate": "बीएमसी कीटक नियंत्रण अधिकारी (PCO) प्रमाणपत्र",
  "Maharashtra PWD Lift Inspector License": "महाराष्ट्र सार्वजनिक बांधकाम (PWD) लिफ्ट तपासणी परवाना",
  "Municipal Birth Certificate": "महानगरपालिका जन्म दाखला",
  "NABL Potable Water Testing Report": "एनएबीएल प्रमाणित पिण्याच्या पाण्याचा तपासणी अहवाल",
  "NOC from Landlord / Society": "जागा मालक / सोसायटीचे ना-हरकत प्रमाणपत्र (NOC)",
  "Outdoor Seating Boundary & Pedestrian Clearance Plan": "बाहेर बसण्याची जागा व पादचारी मार्ग मंजुरी नकाशा",
  "Photo of Shop / Establishment with Signboard": "मराठी नामफलकासह दुकानाचा प्रत्यक्ष फोटो",
  "Plinth Completion Certificate by Structural Engineer": "स्ट्रक्चरल अभियंत्यांचे जोते पूर्णत्व प्रमाणपत्र (Plinth CC)",
  "Potable Water Test Microbiological Analysis Report": "पिण्याच्या पाण्याचा सूक्ष्मजीव वैज्ञानिक चाचणी अहवाल",
  "Proprietor / Managing Partner PAN Card": "मालक / व्यवस्थापकीय भागीदाराचे पॅन कार्ड",
  "Proprietor / Partners KYC & PAN": "मालक / भागीदारांचे केवायसी व पॅन कार्ड",
  "Ration Card / Electricity Bill": "रेशन कार्ड / विद्युत बिल",
  "Recent Commercial Electricity Bill (MSEDCL / Tata / Adani)": "व्यावसायिक वीज बिल (महावितरण / टाटा / अदानी)",
  "Registered Commercial Lease Deed": "नोंदणीकृत व्यावसायिक भाडेकरार",
  "Registered Commercial Lease Deed in Pune": "पुणे येथे नोंदणीकृत व्यावसायिक भाडेकरार",
  "Registered Commercial Leave & License Agreement": "नोंदणीकृत व्यावसायिक लिव्ह अँड लायसन्स करार",
  "Registered Conveyance / Sale Deed Copy": "नोंदणीकृत खरेदीखत / हस्तांतरण दस्त प्रत",
  "Salary Slip / Form 16 / ITR / Talathi Income Report": "वेतन पावती / फॉर्म १६ / आयकर विवरणपत्र / तलाठी उत्पन्न अहवाल",
  "Signboard Graphic Layout with Devanagari Font Prominence": "ठळक मराठी देवनागरी अक्षरांसह नामफलकाचा डिझाइन आराखडा",
  "Trenching Route Map with Traffic Police NOC": "रस्ता खोदणे मार्ग नकाशा व वाहतूक पोलीस एनओसी",
  "Verified Fire NOC & FSSAI License": "प्रमाणित अग्निशामक एनओसी व अन्न परवाना",

  // Keyword / Substring Fallbacks
  "aadhaar": "आधार कार्ड (Aadhaar Card)",
  "pan": "पॅन कार्ड (PAN Card)",
  "electricity bill": "विद्युत बिल (३ महिन्यांपेक्षा जुने नाही)",
  "rent agreement": "नोंदणीकृत भाडेकरार / जागा मालकी पुरावा",
  "lease agreement": "नोंदणीकृत भाडेकरार / भाडेपट्टी करार",
  "passport photo": "पासपोर्ट आकाराचे रंगीत छायाचित्र",
  "property tax": "चालू वर्षाची मालमत्ता कर भरणा पावती",
  "bank account": "बँक खाते पुरावा / रद्द केलेला धनादेश",
  "partnership deed": "नोंदणीकृत भागीदारी करारपत्र (Partnership Deed)",
  "incorporation": "कंपनी नोंदणी प्रमाणपत्र (COI / RoC)",
  "satbara": "७/१२ (सातबारा) व ८-अ उतारा",
  "7/12": "७/१२ (सातबारा) व ८-अ उतारा",
  "sale deed": "नोंदणीकृत खरेदीखत (Registered Sale Deed)",
  "death certificate": "मूळ मृत्यू दाखला (वारस नोंदीसाठी)",
  "legal heir": "कायदेशीर वारसदार शपथपत्र",
  "plumber": "बीएमसी परवानाधारक प्लंबर लेआउट व प्रमाणपत्र",
  "trenching": "रस्ता खोदणे (Trenching) परवानगी",
  "fire": "अग्निशमन सुरक्षा आराखडा व उपकरणे पावती",
  "water test": "पिण्याच्या पाण्याचा प्रयोगशाळा तपासणी अहवाल",
  "kitchen": "किचन व एक्झॉस्ट डक्ट लेआउट नकाशा",
  "income proof": "मागील ३ वर्षांचे उत्पन्न पुरावे / फॉर्म १६",
  "school leaving": "शाळा सोडल्याचा दाखला (LC) / जन्म दाखला",
  "domicile": "महाराष्ट्रातील १५ वर्षे वास्तव्याचा अधिवास पुरावा",
  "ration card": "रेशन कार्ड प्रत",
  "architect": "नोंदणीकृत वास्तुविशारद अधिकृत इमारत नकाशे (AutoDCR)",
  "plinth": "जोते तपासणी अहवाल (Plinth Inspection Report)",
  "cfo": "मुख्य अग्निशमन अधिकारी (CFO) अंतिम ना-हरकत प्रमाणपत्र (NOC)",
  "mpcb": "महाराष्ट्र प्रदूषण नियंत्रण मंडळ संमती पत्र (Consent to Establish)"
};

/**
 * Municipality & Jurisdiction Marathi Names
 */
const MUNI_TRANSLATIONS = {
  "Mumbai (MCGM / BMC)": "मुंबई (BMC / MCGM)",
  "Brihanmumbai (BMC) — Mumbai": "बृहन्मुंबई महानगरपालिका (BMC) — मुंबई",
  "Mumbai & Maharashtra Statewide (LMS / Aaple Sarkar)": "मुंबई व महाराष्ट्र राज्यव्यापी (LMS / आपले सरकार)",
  "Pune (PMC / PMRDA)": "पुणे महानगरपालिका (PMC / PMRDA)",
  "Pune Municipal Corporation": "पुणे महानगरपालिका (PMC)",
  "Thane (TMC)": "ठाणे महानगरपालिका (TMC)",
  "Navi Mumbai (NMMC)": "नवी मुंबई महानगरपालिका (NMMC)",
  "Pimpri Chinchwad (PCMC)": "पिंपरी चिंचवड महानगरपालिका (PCMC)",
  "Nagpur (NMC)": "नागपूर महानगरपालिका (NMC)",
  "Nashik (NMC)": "नाशिक महानगरपालिका (NMC)",
  "Maharashtra Statewide (Aaple Sarkar RTS)": "महाराष्ट्र राज्यव्यापी (आपले सरकार RTS)",
  "Maharashtra Statewide (MahaBhumi / ई-फेरफार)": "महाराष्ट्र राज्यव्यापी (महाभूमी / ई-फेरफार)",
  "Maharashtra Statewide (LMS महाऑनलाइन व स्थानिक स्वराज्य संस्था)": "महाराष्ट्र राज्यव्यापी (LMS महाऑनलाइन)",
  "Maharashtra Statewide (Aaple Sarkar / Revenue Dept)": "महाराष्ट्र राज्यव्यापी (महसूल विभाग)"
};

window.UI_STRINGS = UI_STRINGS;
window.TASK_TRANSLATIONS = TASK_TRANSLATIONS;
window.DOC_TRANSLATIONS = DOC_TRANSLATIONS;
window.MUNI_TRANSLATIONS = MUNI_TRANSLATIONS;
