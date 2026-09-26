import sys

new_task_code = '''        # -------------------------------------------------------------------------
        # TASK 0: Commercial Bakery & Food Service Establishment (Mumbai MCGM / BMC)
        # Route #MCGM-EODB-2024-8842 - Localized for Indian Municipal Administration
        # -------------------------------------------------------------------------
        dept_mca_mum = DepartmentInfo(
            id="dept-mca-mum",
            name="Ministry of Corporate Affairs (RoC Mumbai) & GSTN",
            jurisdiction="Central Government (Maharashtra Desk)",
            office_address="Everest Building, 100 Marine Drive, Nariman Point, Mumbai - 400002",
            contact_phone="022-22812627",
            contact_email="roc.mumbai@mca.gov.in",
            portal_url="https://www.mca.gov.in"
        )
        dept_mcgm_labour = DepartmentInfo(
            id="dept-mcgm-labour",
            name="MCGM Labour & Shops Department (Aaple Sarkar)",
            jurisdiction="Municipal Corporation of Greater Mumbai (Ward H/West)",
            office_address="MCGM Ward H/West Office, Saint Martin Road, Bandra West, Mumbai - 400050",
            contact_phone="022-26422311",
            contact_email="shops.hwest@mcgm.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 2:30 PM IST",
            portal_url="https://aaplesarkar.mahaonline.gov.in"
        )
        dept_mfb = DepartmentInfo(
            id="dept-mfb",
            name="Mumbai Fire Brigade (Chief Fire Officer Command)",
            jurisdiction="Municipal Fire Command (Greater Mumbai)",
            office_address="Byculla Fire Brigade Headquarters, Bapurao Jagtap Marg, Byculla, Mumbai - 400008",
            contact_phone="022-23076111",
            contact_email="fire.noc@mcgm.gov.in",
            working_hours="Monday - Friday: 10:30 AM - 3:30 PM IST",
            portal_url="https://portal.mcgm.gov.in/eodb-fire-noc"
        )
        dept_fssai_mum = DepartmentInfo(
            id="dept-fssai-mum",
            name="Food Safety and Standards Authority of India (FSSAI Western Region)",
            jurisdiction="Central / Maharashtra FDA Regulatory Zone",
            office_address="MHADA Complex, Bandra Kurla Complex (BKC), Bandra East, Mumbai - 400051",
            contact_phone="1800-112-100",
            contact_email="foscos.helpdesk@fssai.gov.in",
            portal_url="https://foscos.fssai.gov.in"
        )
        dept_mpcb = DepartmentInfo(
            id="dept-mpcb",
            name="Maharashtra Pollution Control Board (MPCB Regional Office)",
            jurisdiction="State Environmental Protection Authority",
            office_address="Kalpataru Point, 3rd Floor, Opp. Cine Planet, Sion Circle, Sion East, Mumbai - 400022",
            contact_phone="022-24010437",
            contact_email="ms@mpcb.gov.in",
            portal_url="https://mpcb.gov.in"
        )
        dept_mcgm_health = DepartmentInfo(
            id="dept-mcgm-health",
            name="MCGM Public Health Department (Medical Officer of Health - Ward H/West)",
            jurisdiction="Municipal Corporation of Greater Mumbai (Ward H/West)",
            office_address="Saint Martin Road, Behind Bandra Police Station, Bandra West, Mumbai - 400050",
            contact_phone="022-26422311",
            contact_email="moh.hwest@mcgm.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 2:30 PM IST (Window 4)",
            portal_url="https://portal.mcgm.gov.in/eodb-trade-license"
        )
        dept_mcgm_license = DepartmentInfo(
            id="dept-mcgm-license",
            name="MCGM License & Encroachment Department & Mumbai Police Licensing Branch",
            jurisdiction="Municipal Corporation of Greater Mumbai (Ward H/West)",
            office_address="Plot No. 89, Waterfield Road, Bandra West, Mumbai - 400050",
            contact_phone="022-26422311",
            contact_email="licensing.hwest@mcgm.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 2:30 PM IST",
            portal_url="https://portal.mcgm.gov.in/signboard-license"
        )
        dept_mcgm_comm = DepartmentInfo(
            id="dept-mcgm-comm",
            name="Municipal Corporation of Greater Mumbai (Ward H/West Secretariat)",
            jurisdiction="Brihanmumbai Municipal Corporation",
            office_address="Ward H/West Municipal Headquarters, Saint Martin Road, Bandra West, Mumbai - 400050",
            contact_phone="022-26422311",
            contact_email="eodb.support@mcgm.gov.in",
            portal_url="https://portal.mcgm.gov.in"
        )

        task0_steps = [
            TaskStep(
                id="mum-bakery-1",
                task_id="task-mum-bakery",
                step_number=1,
                title="MCA Certificate of Incorporation & Corporate PAN",
                description="Incorporate commercial entity (Pvt Ltd / LLP) on MCA21 portal via SPICe+ Part A/B, obtain Corporate Identity Number (CIN), and register Corporate PAN.",
                department=dept_mca_mum,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=4,
                fee_amount=1500.0,
                fee_breakdown={"MCA Name Approval & Registration": 1000.0, "Maharashtra Stamp Duty": 500.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-cin", name="Certificate of Incorporation (CIN: U15100MH2024PTC392810)", description="Certified certificate issued by Registrar of Companies, Mumbai", is_mandatory=True),
                    DocumentRequirement(id="doc-pan-mca", name="Corporate PAN & TAN Card", description="Income Tax Department corporate permanent account number confirmation", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="SPICe+ Part A/B", title="Integrated Company Incorporation Instrument", fill_online_url="https://www.mca.gov.in/mcafoportal/showSpicePlus.do")
                ],
                verification_source=VerificationSource(
                    url="https://www.mca.gov.in/mcafoportal/showSpicePlus.do",
                    page_title="Ministry of Corporate Affairs - SPICe+ Integration",
                    last_scraped_at="2026-09-24T12:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Companies Act 2013 & RoC Mumbai Guidelines"
                ),
                tips_and_pitfalls="Directors must ensure DIN and Aadhaar e-KYC credentials match exact spelling across incorporation instruments."
            ),
            TaskStep(
                id="mum-bakery-2",
                task_id="task-mum-bakery",
                step_number=2,
                title="Commercial Premise Lease & Maharashtra Gumasta Intimation",
                description="Execute registered commercial tenancy agreement in Bandra West and file online Gumasta intimation under Maharashtra Shops & Establishments Act 2017 via Aaple Sarkar portal.",
                department=dept_mcgm_labour,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=5,
                fee_amount=1400.0,
                fee_breakdown={"Shops Act Intimation Fee (Aaple Sarkar)": 400.0, "Commercial Tenancy Notarization & Franking": 1000.0},
                prerequisites=["mum-bakery-1"],
                documents=[
                    DocumentRequirement(id="doc-lease-mum", name="Registered Commercial Lease Agreement (Bandra West)", description="Minimum 3-year registered commercial deed specifying retail bakery and kitchen exhaust usage", is_mandatory=True),
                    DocumentRequirement(id="doc-gumasta", name="Maharashtra Gumasta Registration / Form G Intimation", description="Registration #MH-MUM-HW-2024-44109 issued via Aaple Sarkar", is_mandatory=True),
                    DocumentRequirement(id="doc-elec", name="Commercial Electricity Connection Meter Bill (Adani / BEST)", description="Sanctioned power load proof for baking machinery", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="FORM G", title="Application for Registration / Intimation of Commercial Establishment", fill_online_url="https://aaplesarkar.mahaonline.gov.in")
                ],
                verification_source=VerificationSource(
                    url="https://aaplesarkar.mahaonline.gov.in",
                    page_title="Aaple Sarkar - Maharashtra Shops & Establishments Gateway",
                    last_scraped_at="2026-09-22T10:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Act No. LXI of 2017 § 6"
                ),
                tips_and_pitfalls="Commercial lease must clearly delineate kitchen food preparation zone from front retail seating area to avoid CTS inspection queries."
            ),
            TaskStep(
                id="mum-bakery-3",
                task_id="task-mum-bakery",
                step_number=3,
                title="MFB Fire Safety Compliance & Commercial Kitchen NOC",
                description="Mandatory fire protection installation, Class-K commercial exhaust hood duct suppression, LPG pipeline safety valve certificate, and dual emergency escape audit pursuant to Maharashtra Fire Prevention and Life Safety Measures Act 2006.",
                department=dept_mfb,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=18,
                fee_amount=18500.0,
                fee_breakdown={
                    "Chief Fire Officer Scrutiny Fee": 8500.0,
                    "Site Inspection & Kitchen Exhaust Assessment": 6200.0,
                    "Hydrant & Fire Equipment Inspection": 3800.0
                },
                prerequisites=["mum-bakery-2"],
                documents=[
                    DocumentRequirement(id="doc-mep-plans", name="Sealed Architectural Layout & MEP Drawing", description="Prepared and stamped by MCGM registered architect showing customer seating, bakery oven zoning, refuse disposal, and fire exit doors", is_mandatory=True),
                    DocumentRequirement(id="doc-mfb-formb", name="Licensed Fire Agency Form B Certificate", description="Certified installation of Class-K wet chemical fire system and portable ISI fire extinguishers", is_mandatory=True),
                    DocumentRequirement(id="doc-exhaust-spec", name="Kitchen Exhaust & Duct Elevation Schematic", description="Stainless steel duct routing terminating 3 meters above building roof parapet", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="FORM A - MFB", title="Application for Fire Safety NOC for Commercial Eating House", fill_online_url="https://portal.mcgm.gov.in/eodb-fire-noc"),
                    FormRequirement(form_code="ANNEXURE C", title="Mumbai Fire Brigade Fire Safety & Kitchen Ventilation Declaration", download_url="https://portal.mcgm.gov.in/eodb-fire-noc/annexure_c.pdf", fill_online_url="https://portal.mcgm.gov.in/eodb-fire-noc")
                ],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/eodb-fire-noc",
                    page_title="Mumbai Fire Brigade - Commercial Premise NOC Regulations",
                    last_scraped_at="2026-09-24T16:42:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Fire Prevention and Life Safety Measures Act 2006 § 3(1)"
                ),
                tips_and_pitfalls="Maintain minimum 1.5m clearance between commercial exhaust termination and adjacent residential balcony or window openings."
            ),
            TaskStep(
                id="mum-bakery-3a",
                task_id="task-mum-bakery",
                step_number=4,
                title="FSSAI State Food Business Operator License",
                description="Mandatory Food Safety and Standards Authority of India (FSSAI) state operating license for commercial baking, dairy handling, and confectionery production. Concurrent filing alongside MFB Fire audit.",
                department=dept_fssai_mum,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=12,
                fee_amount=7500.0,
                fee_breakdown={"FSSAI State License Fee (3 Years)": 6000.0, "Water Potability Analysis (Municipal Lab Dadar)": 1500.0},
                prerequisites=["mum-bakery-2"],
                documents=[
                    DocumentRequirement(id="doc-fssai-layout", name="Food Safety Blueprint & Equipment Layout", description="Showing separate raw ingredient storage, bakery mixing deck, and refrigeration zones", is_mandatory=True),
                    DocumentRequirement(id="doc-fssai-water", name="Bacteriological Water Potability Lab Report", description="Tested compliant under IS 10500 standards from Dadar Municipal Laboratory", is_mandatory=True),
                    DocumentRequirement(id="doc-fssai-med", name="Food Handlers Medical Fitness Certificate", description="Form IX signed by registered medical practitioner with typhoid vaccination proof", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="FORM FSSAI-B", title="Schedule 2 Form B Application for FSSAI State License", fill_online_url="https://foscos.fssai.gov.in")
                ],
                verification_source=VerificationSource(
                    url="https://foscos.fssai.gov.in",
                    page_title="FSSAI Food Safety Compliance System (FoSCoS)",
                    last_scraped_at="2026-09-22T14:15:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Food Safety and Standards Act 2006 § 31"
                ),
                tips_and_pitfalls="Designate a trained FoSTaC certified supervisor to prevent inspection deferrals during state food auditor visits."
            ),
            TaskStep(
                id="mum-bakery-3b",
                task_id="task-mum-bakery",
                step_number=5,
                title="MPCB Pollution Consent to Establish / Operate (CTE/CTO)",
                description="Maharashtra Pollution Control Board Consent under Water (Prevention and Control of Pollution) Act 1974 and Air Act 1981. Kitchen effluent grease interceptor and acoustic baking oven dampening.",
                department=dept_mpcb,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=10,
                fee_amount=6200.0,
                fee_breakdown={"MPCB Application & Scrutiny Fee": 5000.0, "Pollution Cess Assessment": 1200.0},
                prerequisites=["mum-bakery-2"],
                documents=[
                    DocumentRequirement(id="doc-mpcb-grease", name="Grease Trap & Effluent Treatment Specification", description="Design for commercial three-chamber grease trap treating kitchen sink discharge", is_mandatory=True),
                    DocumentRequirement(id="doc-mpcb-power", name="Bakery Electrical Load & Acoustic Enclosure Plan", description="Showing noise levels under 55 dB(A) for residential mixed zone", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="MPCB FORM I", title="Combined Consent Application under Water & Air Acts", fill_online_url="https://mpcb.gov.in")
                ],
                verification_source=VerificationSource(
                    url="https://mpcb.gov.in",
                    page_title="Maharashtra Pollution Control Board - EODB Consent Management",
                    last_scraped_at="2026-09-20T11:00:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True,
                    gazette_ref="Water Act 1974 § 25 & Air Act 1981 § 21"
                ),
                tips_and_pitfalls="Commercial bakery operations fall under Green Category if capital investment < ₹5 Crore and no coal-fired tandoor is utilized."
            ),
            TaskStep(
                id="mum-bakery-4",
                task_id="task-mum-bakery",
                step_number=6,
                title="BMC Health Trade License under Section 394 (MMC Act 1888)",
                description="Statutory health trade permit authorizing commercial preparation and sale of food items, bakery confectionery, and trade refuse assessment by Medical Officer of Health (Ward H/West).",
                department=dept_mcgm_health,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=14,
                fee_amount=12000.0,
                fee_breakdown={
                    "Section 394 Trade License Fee (Bakery with Power)": 6000.0,
                    "Trade Refuse Charge (TRC) Annual Assessment": 3500.0,
                    "Factory / Power Machinery Inspection (5 HP Baking Deck)": 2500.0
                },
                prerequisites=["mum-bakery-3", "mum-bakery-3a", "mum-bakery-3b"],
                documents=[
                    DocumentRequirement(id="doc-pest-mum", name="Pest Control Contract & Water Potability Certificate", description="Certified contract with MCGM approved pest control operator and Dadar municipal bacteriological test", is_mandatory=True),
                    DocumentRequirement(id="doc-mfb-clearance", name="Chief Fire Officer Final Fire NOC Clearance", description="Verification of compliance from Stop 03", is_mandatory=True),
                    DocumentRequirement(id="doc-fssai-clearance", name="FSSAI State License Grant Letter", description="Food business registration certificate from Stop 03A", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="FORM HTL-1", title="Application for Health Trade License under Section 394 (MMC Act 1888)", fill_online_url="https://portal.mcgm.gov.in/eodb-trade-license")
                ],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/eodb-trade-license",
                    page_title="MCGM Public Health Department - Trade License Portal",
                    last_scraped_at="2026-09-24T16:42:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Mumbai Municipal Corporation Act 1888 Section 394 Schedule M"
                ),
                tips_and_pitfalls="Physical site inspection conducted by Ward MOH within 7 working days of fee payment. Clean water lines must be marked."
            ),
            TaskStep(
                id="mum-bakery-5",
                task_id="task-mum-bakery",
                step_number=7,
                title="Commercial Facade & Signboard License (Section 328 MMC Act)",
                description="Statutory permission for external shopfront signage and illuminated board from MCGM License Department. Must comply with Maharashtra Shops and Establishments Act 2022 amendment for Marathi Devanagari lettering.",
                department=dept_mcgm_license,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=7,
                fee_amount=4800.0,
                fee_breakdown={"Signboard Advertisement Fee (Section 328)": 3800.0, "Scrutiny & Inspection Levy": 1000.0},
                prerequisites=["mum-bakery-2", "mum-bakery-4"],
                documents=[
                    DocumentRequirement(id="doc-sign-photo", name="Signboard Artwork & Facade Photo", description="Scaled elevation drawing demonstrating Marathi Devanagari font in equal or larger size than English lettering", is_mandatory=True),
                    DocumentRequirement(id="doc-soc-noc", name="Building Cooperative Housing Society (CHS) NOC", description="Unconditional consent from building society managing committee for facade mounting", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="FORM LIC-328", title="Application for Sky-Sign / Signboard Permission", fill_online_url="https://portal.mcgm.gov.in/signboard-license")
                ],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/signboard-license",
                    page_title="MCGM License Department - Signboard Permissions",
                    last_scraped_at="2026-09-21T14:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Mumbai Municipal Corporation Act 1888 Section 328 & 328A"
                ),
                tips_and_pitfalls="Devanagari script must precede English text and maintain minimum 50% visual prominence."
            ),
            TaskStep(
                id="mum-bakery-6",
                task_id="task-mum-bakery",
                step_number=8,
                title="Final Health Trade Certificate & Official Municipal Seal (Terminus)",
                description="Issuance of unified composite Municipal Health Trade License Certificate bearing encrypted QR verification code and entry into Municipal Registry.",
                department=dept_mcgm_comm,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=500.0,
                fee_breakdown={"Digital Certificate Issuance & QR Seal": 500.0},
                prerequisites=["mum-bakery-5"],
                documents=[
                    DocumentRequirement(id="doc-final-inspec", name="Ward MOH Satisfactory Inspection Report", description="Final site compliance certificate from Ward H/West health officer", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="CERT-HTL-FINAL", title="Download Official Health Trade License Certificate", fill_online_url="https://portal.mcgm.gov.in")
                ],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in",
                    page_title="Municipal Corporation of Greater Mumbai - Citizen E-Portal",
                    last_scraped_at="2026-09-25T13:00:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Right to Public Services Act 2015"
                ),
                tips_and_pitfalls="Laminated certificate with QR code must be displayed prominently at front customer counter."
            )
        ]

        task0 = CivicTask(
            id="task-mum-bakery",
            title="Register & Commission a Commercial Bakery in Bandra, Mumbai",
            category="Food & Hospitality",
            municipality="Mumbai (MCGM / BMC)",
            state="Maharashtra",
            description="Statutory pathway governing commercial bakery establishment with eating house authorization across MCGM Ward H/West, Mumbai Fire Brigade (MFB), FSSAI FoSCoS, and Maharashtra Pollution Control Board (MPCB) pursuant to Section 394 MMC Act 1888.",
            tags=["commercial bakery", "cafe", "food service", "mcgm", "bmc", "mumbai", "bandra west", "ward h/west", "section 394", "mmc act 1888", "fssai", "foscos", "gumasta", "mfb fire noc", "mpcb", "aaple sarkar"],
            steps=task0_steps
        )
        self._tasks[task0.id] = task0'''

with open('app/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "        # -------------------------------------------------------------------------\n        # TASK 0: Open a Sidewalk Cafe & Bakery"
end_marker = "        self._tasks[task0.id] = task0"

if start_marker in content and end_marker in content:
    start_pos = content.index(start_marker)
    end_pos = content.index(end_marker) + len(end_marker)
    new_content = content[:start_pos] + new_task_code + content[end_pos:]
    with open('app/database.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: database.py updated with task-mum-bakery")
else:
    print("ERROR: Markers not found in database.py")
    sys.exit(1)
