from typing import List, Dict, Optional
from datetime import datetime
from app.models import (
    CivicTask, TaskStep, DepartmentInfo, DocumentRequirement,
    FormRequirement, VerificationSource, SubmissionMode, StepStatus
)

class CivicDatabase:
    def __init__(self):
        self._tasks: Dict[str, CivicTask] = {}
        self._audit_logs: List[Dict] = []
        self._citizen_feedback: List[Dict] = []
        self._init_seed_data()

    def get_all_tasks(self) -> List[CivicTask]:
        return list(self._tasks.values())

    def get_task_by_id(self, task_id: str) -> Optional[CivicTask]:
        return self._tasks.get(task_id)

    def search_tasks(self, query: str, municipality: Optional[str] = None) -> List[CivicTask]:
        q = query.lower()
        results = []
        for task in self._tasks.values():
            match_mun = True
            if municipality and municipality.lower() != "all":
                match_mun = municipality.lower() in task.municipality.lower()
            
            match_q = (
                q in task.title.lower() or
                q in task.description.lower() or
                q in task.category.lower() or
                any(q in tag.lower() for tag in task.tags)
            )
            if match_q and match_mun:
                results.append(task)
        return results

    def add_audit_log(self, action: str, details: str, user: str = "Admin"):
        self._audit_logs.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "user": user
        })

    def get_audit_logs(self) -> List[Dict]:
        return list(reversed(self._audit_logs))

    def add_citizen_feedback(self, step_id: str, issue_type: str, notes: str):
        self._citizen_feedback.append({
            "id": f"fb-{len(self._citizen_feedback) + 1}",
            "step_id": step_id,
            "issue_type": issue_type,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_review"
        })

    def get_feedback(self) -> List[Dict]:
        return self._citizen_feedback

    def update_step_verification(self, task_id: str, step_id: str, is_verified: bool, updated_fee: Optional[float] = None, updated_sla: Optional[int] = None, source_url: Optional[str] = None) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        for step in task.steps:
            if step.id == step_id:
                step.verification_source.is_admin_verified = is_verified
                if updated_fee is not None:
                    step.fee_amount = updated_fee
                if updated_sla is not None:
                    step.estimated_days = updated_sla
                if source_url:
                    step.verification_source.url = source_url
                self.add_audit_log(
                    action="STEP_VERIFIED" if is_verified else "STEP_MODIFIED",
                    details=f"Step '{step.title}' ({step_id}) updated. Verified: {is_verified}"
                )
                return True
        return False

    def _init_seed_data(self):
        # -------------------------------------------------------------------------
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
                    DocumentRequirement(
                        id="doc-cin",
                        name="Certificate of Incorporation (CIN)",
                        description="Certified certificate issued by Registrar of Companies, Mumbai",
                        is_mandatory=True,
                        category="Identity & KYC",
                        validity_rule="CIN must be in active status on MCA master records",
                        issuing_authority="Registrar of Companies (RoC Mumbai)"
                    ),
                    DocumentRequirement(
                        id="doc-pan-mca",
                        name="Corporate PAN & TAN Card",
                        description="Income Tax Department corporate permanent account number confirmation",
                        is_mandatory=True,
                        category="Identity & KYC",
                        validity_rule="Linked with active commercial banking account",
                        issuing_authority="Income Tax Department / NSDL"
                    )
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
                tips_and_pitfalls="Directors must ensure DIN and Aadhaar e-KYC credentials match exact spelling across incorporation instruments.",
                anti_tout_advisory="Statutory fee is ₹1,000 + ₹500 stamp duty payable solely via Bharatkosh / MCA21 payment gateway. Never pay private agents for DIN generation.",
                statutory_payment_channel="Ministry of Corporate Affairs (MCA21) Bharatkosh Gateway",
                community_verifications=34,
                official_receipt_mandate="Zero Cash Mandate: Official MCA computerized receipt issued on successful gateway transaction.",
                last_gazette_notification="MCA Notification G.S.R. 107(E) Companies Rules 2024"
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
                    DocumentRequirement(
                        id="doc-lease-mum",
                        name="Registered Commercial Lease Agreement (Bandra West)",
                        description="Minimum 3-year registered commercial deed specifying retail bakery and kitchen exhaust usage",
                        is_mandatory=True,
                        category="Property & Premise",
                        validity_rule="Must be registered with Sub-Registrar of Assurances Bandra; minimum 24 months validity remaining",
                        issuing_authority="Department of Registration & Stamps, Maharashtra"
                    ),
                    DocumentRequirement(
                        id="doc-gumasta",
                        name="Maharashtra Gumasta Registration / Form G Intimation",
                        description="Registration #MH-MUM-HW-2024-44109 issued via Aaple Sarkar",
                        is_mandatory=True,
                        category="Statutory Clearances",
                        validity_rule="Official Form G intimation receipt under Maharashtra Act LXI of 2017",
                        issuing_authority="MCGM Labour Department / Aaple Sarkar"
                    ),
                    DocumentRequirement(
                        id="doc-elec",
                        name="Commercial Electricity Connection Meter Bill (Adani / BEST)",
                        description="Sanctioned power load proof for baking machinery",
                        is_mandatory=True,
                        category="Property & Premise",
                        validity_rule="Must be issued within last 90 days; registered commercial tariff (LT-II)",
                        issuing_authority="Adani Electricity Mumbai Ltd / BEST Undertaking"
                    )
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
                tips_and_pitfalls="Commercial lease must clearly delineate kitchen food preparation zone from front retail seating area to avoid CTS inspection queries.",
                anti_tout_advisory="Maharashtra Shops intimation fee is ₹400 payable exclusively through Aaple Sarkar portal. Zero physical cash handling permitted.",
                statutory_payment_channel="Government of Maharashtra Aaple Sarkar / GRAS Cyber Treasury",
                community_verifications=29,
                official_receipt_mandate="Zero Cash Mandate: All statutory charges deposited into State Treasury Head 0230-Labour & Employment.",
                last_gazette_notification="Maharashtra Govt Gazette No. LXI of 2017 § 6"
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
                    DocumentRequirement(
                        id="doc-mep-plans",
                        name="Sealed Architectural Layout & MEP Drawing",
                        description="Prepared and stamped by MCGM registered architect showing customer seating, bakery oven zoning, refuse disposal, and fire exit doors",
                        is_mandatory=True,
                        category="Technical Plans & Drawings",
                        validity_rule="Signed and blue-ink sealed by MCGM licensed surveyor/architect (CA/XXXX/YYYY)",
                        issuing_authority="Council of Architecture / MCGM Registered Architect"
                    ),
                    DocumentRequirement(
                        id="doc-mfb-formb",
                        name="Licensed Fire Agency Form B Certificate",
                        description="Certified installation of Class-K wet chemical fire system and portable ISI fire extinguishers",
                        is_mandatory=True,
                        category="Statutory Clearances",
                        validity_rule="Issued by Maharashtra Fire Services Directorate licensed agency (valid for 1 year from test date)",
                        issuing_authority="Directorate of Maharashtra Fire Services"
                    ),
                    DocumentRequirement(
                        id="doc-exhaust-spec",
                        name="Kitchen Exhaust & Duct Elevation Schematic",
                        description="Stainless steel duct routing terminating 3 meters above building roof parapet",
                        is_mandatory=True,
                        category="Technical Plans & Drawings",
                        validity_rule="SS-304 food-grade stainless steel with non-return fire damper specification",
                        issuing_authority="Licensed Mechanical / HVAC Engineer"
                    )
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
                tips_and_pitfalls="Maintain minimum 1.5m clearance between commercial exhaust termination and adjacent residential balcony or window openings.",
                anti_tout_advisory="OFFICIAL ANTI-TOUT ADVISORY: Fire Brigade site inspections attract unauthorized liaisons claiming 'expediting fees'. Under Maharashtra Fire Act 2006, all assessment fees (₹18,500) are payable ONLY via MCGM SAP Portal Challan. Direct cash payment is an offense under Prevention of Corruption Act. Report touts to ACB: 1064.",
                statutory_payment_channel="Brihanmumbai Municipal Corporation (MCGM) SAP Treasury Gateway",
                community_verifications=18,
                official_receipt_mandate="Zero Cash Mandate: All fees payable against official computerized Municipal Challan Receipt (MCR). No cash collection permitted at Byculla Fire HQ.",
                last_gazette_notification="Maharashtra Fire Act Notification CFO/P/784/2023"
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
                    DocumentRequirement(
                        id="doc-fssai-layout",
                        name="Food Safety Blueprint & Equipment Layout",
                        description="Showing separate raw ingredient storage, bakery mixing deck, and refrigeration zones",
                        is_mandatory=True,
                        category="Technical Plans & Drawings",
                        validity_rule="Must include pest-control fly killer location schematic and separate hand-wash station",
                        issuing_authority="FSSAI Certified Food Safety Auditor"
                    ),
                    DocumentRequirement(
                        id="doc-fssai-water",
                        name="Bacteriological Water Potability Lab Report",
                        description="Tested compliant under IS 10500 standards from Dadar Municipal Laboratory",
                        is_mandatory=True,
                        category="Statutory Clearances",
                        validity_rule="Issued within last 180 days by NABL/Municipal Accredited Laboratory (IS 10500)",
                        issuing_authority="Dadar Municipal Laboratory (MCGM Public Health Dept)"
                    ),
                    DocumentRequirement(
                        id="doc-fssai-med",
                        name="Food Handlers Medical Fitness Certificate",
                        description="Form IX signed by registered medical practitioner with typhoid vaccination proof",
                        is_mandatory=True,
                        category="Identity & KYC",
                        validity_rule="Annual fitness certificate with chest X-ray and typhoid vaccine endorsement",
                        issuing_authority="Registered Medical Practitioner (MBBS/MD)"
                    )
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
                tips_and_pitfalls="Designate a trained FoSTaC certified supervisor to prevent inspection deferrals during state food auditor visits.",
                anti_tout_advisory="FSSAI State license fee is ₹2,000/year (₹6,000 for 3 years) payable directly through FoSCoS portal gateway. Do not use third-party paid 'fast-track' websites.",
                statutory_payment_channel="Central FoSCoS Payment Gateway (SBI e-Pay / NetBanking)",
                community_verifications=21,
                official_receipt_mandate="Zero Cash Mandate: Official FSSAI Receipt with QR Authenticity Seal generated instantly online.",
                last_gazette_notification="FSSAI Notification No. 1-1371/FSSAI/Imports/2021"
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
                    DocumentRequirement(
                        id="doc-mpcb-grease",
                        name="Grease Trap & Effluent Treatment Specification",
                        description="Design for commercial three-chamber grease trap treating kitchen sink discharge",
                        is_mandatory=True,
                        category="Technical Plans & Drawings",
                        validity_rule="3-stage baffle grease trap with minimum 150L handling capacity",
                        issuing_authority="Environmental Engineering Consultant"
                    ),
                    DocumentRequirement(
                        id="doc-mpcb-power",
                        name="Bakery Electrical Load & Acoustic Enclosure Plan",
                        description="Showing noise levels under 55 dB(A) for residential mixed zone",
                        is_mandatory=True,
                        category="Technical Plans & Drawings",
                        validity_rule="Noise emission < 55 dB(A) acoustic canopy certificate",
                        issuing_authority="CPCB Approved Noise Testing Agency"
                    )
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
                tips_and_pitfalls="Commercial bakery operations fall under Green Category if capital investment < ₹5 Crore and no coal-fired tandoor is utilized.",
                anti_tout_advisory="Consent to Establish fee of ₹5,000 + cess is deposited into MPCB SBI Treasury account through portal gateway. Zero cash collection at Regional Office Sion.",
                statutory_payment_channel="MPCB Centralized Online Consent Gateway",
                community_verifications=16,
                official_receipt_mandate="Zero Cash Mandate: Electronic Treasury Reference generated for all Water/Air Act statutory fees.",
                last_gazette_notification="MPCB Circular No. MPCB/JD(WPC)/B-190424-FTS-0112"
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
                    DocumentRequirement(
                        id="doc-pest-mum",
                        name="Pest Control Contract & Water Potability Certificate",
                        description="Certified contract with MCGM approved pest control operator and Dadar municipal bacteriological test",
                        is_mandatory=True,
                        category="Statutory Clearances",
                        validity_rule="Annual service contract with MCGM licensed pest control operator",
                        issuing_authority="MCGM Licensed Pest Control Agency"
                    ),
                    DocumentRequirement(
                        id="doc-mfb-clearance",
                        name="Chief Fire Officer Final Fire NOC Clearance",
                        description="Verification of compliance from Stop 03",
                        is_mandatory=True,
                        category="Statutory Clearances",
                        validity_rule="Official NOC issued by Chief Fire Officer, Mumbai Fire Brigade",
                        issuing_authority="Chief Fire Officer, Mumbai Fire Brigade"
                    ),
                    DocumentRequirement(
                        id="doc-fssai-clearance",
                        name="FSSAI State License Grant Letter",
                        description="Food business registration certificate from Stop 03A",
                        is_mandatory=True,
                        category="Statutory Clearances",
                        validity_rule="Active FSSAI License Number (14 digits) issued via FoSCoS",
                        issuing_authority="FSSAI Western Regional Office Mumbai"
                    )
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
                tips_and_pitfalls="Physical site inspection conducted by Ward MOH within 7 working days of fee payment. Clean water lines must be marked.",
                anti_tout_advisory="STRICT BMC ANTI-TOUT ADVISORY: Ward H/West Health Department does not authorize brokers or agents. Official Schedule M fee of ₹12,000 must be deposited via MCGM NetBanking or Ward CFC Computerized Counter with official Municipal Computerized Receipt (MCR). Beware of touts claiming inspection waivers.",
                statutory_payment_channel="Brihanmumbai Municipal Corporation (MCGM) Ward CFC E-Challan",
                community_verifications=19,
                official_receipt_mandate="Zero Cash Mandate: Payment receipt must bear the 10-digit MCGM Citizen Receipt Number (MCR). No cash collection permitted by Ward MOH inspectors.",
                last_gazette_notification="MCGM Circular No. CHE/DP/102/2024 dated 14-06-2024"
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
                    DocumentRequirement(
                        id="doc-sign-photo",
                        name="Signboard Artwork & Facade Photo",
                        description="Scaled elevation drawing demonstrating Marathi Devanagari font in equal or larger size than English lettering",
                        is_mandatory=True,
                        category="Technical Plans & Drawings",
                        validity_rule="Marathi Devanagari lettering font size must be >= English font size",
                        issuing_authority="Commercial Signage Fabricator / Architect"
                    ),
                    DocumentRequirement(
                        id="doc-soc-noc",
                        name="Building Cooperative Housing Society (CHS) NOC",
                        description="Unconditional consent from building society managing committee for facade mounting",
                        is_mandatory=True,
                        category="Property & Premise",
                        validity_rule="Original signed resolution on Cooperative Housing Society letterhead",
                        issuing_authority="CHS Managing Committee Secretary/Chairman"
                    )
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
                tips_and_pitfalls="Devanagari script must precede English text and maintain minimum 50% visual prominence.",
                anti_tout_advisory="Section 328 sky-sign fees (₹4,800) are assessed strictly by square meter. Paid via official municipal challan only.",
                statutory_payment_channel="MCGM Citizen Portal License Department Gateway",
                community_verifications=15,
                official_receipt_mandate="Zero Cash Mandate: Computerized MCR Challan generated on area-based calculation formula.",
                last_gazette_notification="MCGM Circular No. Lic/08/2022 (Marathi Signboard Mandate)"
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
                    DocumentRequirement(
                        id="doc-final-inspec",
                        name="Ward MOH Satisfactory Inspection Report",
                        description="Final site compliance certificate from Ward H/West health officer",
                        is_mandatory=True,
                        category="Statutory Clearances",
                        validity_rule="Official digital sign-off by MOH Ward H/West on MCGM Portal",
                        issuing_authority="Medical Officer of Health (MOH Ward H/West)"
                    )
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
                tips_and_pitfalls="Laminated certificate with QR code must be displayed prominently at front customer counter.",
                anti_tout_advisory="Official digital certificate with encrypted QR code is issued free of liaison fees upon clearing statutory milestones. ₹500 digital certification fee only.",
                statutory_payment_channel="MCGM Ward H/West Automated E-Seal Release",
                community_verifications=24,
                official_receipt_mandate="Zero Cash Mandate: Final certificate generated with cryptographically verifiable digital signature of Municipal Commissioner.",
                last_gazette_notification="Maharashtra Right to Public Services Act 2015 Notification"
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
        self._tasks[task0.id] = task0

        # -------------------------------------------------------------------------
        # TASK 1: Food Business & Restaurant Registration (Bengaluru BBMP)
        # -------------------------------------------------------------------------
        dept_mca = DepartmentInfo(
            id="dept-mca",
            name="Ministry of Corporate Affairs / GSTN",
            jurisdiction="Central Government (State Desk: Karnataka)",
            office_address="E-Governance Cell, Kendriya Sadan, Koramangala, Bengaluru - 560034",
            contact_phone="1800-103-4786",
            contact_email="helpdesk.mca@gov.in",
            portal_url="https://www.mca.gov.in"
        )
        dept_bbmp_town = DepartmentInfo(
            id="dept-bbmp-town",
            name="Bruhat Bengaluru Mahanagara Palike (Town Planning Wing)",
            jurisdiction="Municipal (Bengaluru Urban)",
            office_address="BBMP Head Office, NR Square, Hudson Circle, Bengaluru - 560002",
            contact_phone="080-22221188",
            contact_email="townplanning@bbmp.gov.in",
            portal_url="https://bbmp.karnataka.gov.in"
        )
        dept_fssai = DepartmentInfo(
            id="dept-fssai",
            name="Food Safety and Standards Authority of India (FSSAI)",
            jurisdiction="FSSAI Regional Office, Southern Region",
            office_address="CGO Complex, 2nd Floor, Wing-B, Basaveshwara Road, Bengaluru - 560001",
            contact_phone="1800-112-100",
            contact_email="foscos.helpdesk@fssai.gov.in",
            portal_url="https://foscos.fssai.gov.in"
        )
        dept_fire = DepartmentInfo(
            id="dept-fire",
            name="Karnataka Fire & Emergency Services",
            jurisdiction="State Government (Bengaluru Command)",
            office_address="Fire Force Headquarters, Annaswamy Mudaliar Road, Bengaluru - 560042",
            contact_phone="080-22971501",
            contact_email="fire.karnataka@gov.in",
            portal_url="https://ksfes.karnataka.gov.in"
        )
        dept_kspcb = DepartmentInfo(
            id="dept-kspcb",
            name="Karnataka State Pollution Control Board (KSPCB)",
            jurisdiction="Regional Environmental Office",
            office_address="Parisara Bhavan, #49, Church Street, Bengaluru - 560001",
            contact_phone="080-25589112",
            contact_email="memsecy@kspcb.gov.in",
            portal_url="https://kspcb.karnataka.gov.in"
        )
        dept_bbmp_health = DepartmentInfo(
            id="dept-bbmp-health",
            name="BBMP Directorate of Health & Public Licensing",
            jurisdiction="BBMP Zonal / Ward Health Office",
            office_address="Zonal Joint Commissioner Office, Queens Road, Tasker Town, Bengaluru",
            contact_phone="080-22660000",
            contact_email="healthlicensing@bbmp.gov.in",
            portal_url="https://bbmptax.karnataka.gov.in/tradelicense"
        )
        dept_bescom = DepartmentInfo(
            id="dept-bescom",
            name="Bangalore Electricity Supply Company Limited (BESCOM)",
            jurisdiction="Bengaluru Metropolitan Area",
            office_address="BESCOM Corporate Office, K.R. Circle, Bengaluru - 560001",
            contact_phone="1912",
            contact_email="helpline@bescom.org",
            portal_url="https://bescom.karnataka.gov.in"
        )

        task1_steps = [
            TaskStep(
                id="blr-food-1",
                task_id="task-blr-restaurant",
                step_number=1,
                title="Business Legal Structure & GSTIN Registration",
                description="Register entity (Sole Proprietorship, LLP, or Pvt Ltd) and obtain Goods and Services Tax Identification Number (GSTIN) with PAN.",
                department=dept_mca,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=4,
                fee_amount=1500.0,
                fee_breakdown={"MCA Name Approval": 1000.0, "State Stamp Duty": 500.0, "GSTIN Registration": 0.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-pan", name="Director/Proprietor PAN Card", description="Self-attested identity proof", is_mandatory=True),
                    DocumentRequirement(id="doc-aadhaar", name="Aadhaar Card with Mobile Link", description="For e-KYC digital signing", is_mandatory=True),
                    DocumentRequirement(id="doc-bank", name="Cancelled Cheque or Bank Statement", description="Proof of commercial bank account", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="SPICe+ Part A/B", title="Integrated Company Incorporation Form", fill_online_url="https://www.mca.gov.in/mcafoportal/showSpicePlus.do"),
                    FormRequirement(form_code="REG-01", title="Application for Registration under GST Act", fill_online_url="https://reg.gst.gov.in/registration")
                ],
                verification_source=VerificationSource(
                    url="https://services.india.gov.in/service/detail/apply-for-company-incorporation-online",
                    page_title="National Portal of India - Company Incorporation & GST",
                    last_scraped_at="2026-09-24T08:30:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Central Gazette No. GSR 180(E) - Companies Act Rules"
                ),
                tips_and_pitfalls="Ensure your trade name matches exact keywords on electricity bills to avoid query objections.",
                status=StepStatus.READY
            ),
            TaskStep(
                id="blr-food-2",
                task_id="task-blr-restaurant",
                step_number=2,
                title="Commercial Premise Lease & BBMP Zoning NOC",
                description="Obtain notarized registered rental deed for commercial premise and verify land-use zoning (Commercial/Mixed-use under Revised Master Plan 2015).",
                department=dept_bbmp_town,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=7,
                fee_amount=2200.0,
                fee_breakdown={"Zoning Verification Scrutiny": 1200.0, "Notarization & Stamp Fee": 1000.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-lease", name="Registered Commercial Lease Agreement", description="Minimum 11-month registered lease specifying food establishment use", is_mandatory=True),
                    DocumentRequirement(id="doc-khata", name="BBMP Khata Certificate (A-Khata)", description="Property must have valid tax assessment and A-Khata", is_mandatory=True),
                    DocumentRequirement(id="doc-taxrec", name="Latest Municipal Property Tax Paid Receipt", description="SAC code receipt for current assessment year", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="BBMP-TP-Z01", title="Application for Land Use / Zoning Concurrence", download_url="https://bbmp.karnataka.gov.in/forms/zoning_noc.pdf")
                ],
                verification_source=VerificationSource(
                    url="https://bbmp.karnataka.gov.in/page.php?slug=town-planning-guidelines",
                    page_title="BBMP Town Planning - Permissible Land Use Guidelines",
                    last_scraped_at="2026-09-20T11:45:00Z",
                    confidence_score=0.95,
                    is_admin_verified=True,
                    portal_section="RMP-2015 Zonal Regulations"
                ),
                tips_and_pitfalls="Restaurants require road width >= 40 feet in residential mixed zones. Operating in B-Khata or pure residential zone will lead to immediate rejection."
            ),
            TaskStep(
                id="blr-food-3a",
                task_id="task-blr-restaurant",
                step_number=3,
                title="FSSAI State Food License / Registration",
                description="Apply for FSSAI State License (for turnover > 12 Lakhs/year) or Registration on FoSCoS portal with kitchen layout and water testing report.",
                department=dept_fssai,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=10,
                fee_amount=2000.0,
                fee_breakdown={"FSSAI Annual Fee (1 Year)": 2000.0},
                prerequisites=["blr-food-1", "blr-food-2"],
                documents=[
                    DocumentRequirement(id="doc-layout", name="Blueprint / Kitchen Floor Layout Plan", description="Dimensioned plan showing food preparation, storage, and dishwashing zones", is_mandatory=True),
                    DocumentRequirement(id="doc-water", name="Potable Water Testing Lab Report", description="From NABL accredited lab testing bacterial and chemical standards", is_mandatory=True),
                    DocumentRequirement(id="doc-med", name="Staff Medical Fitness Certificates", description="Form IX signed by registered medical practitioner", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="Form B", title="Application for State License under Food Safety Act", fill_online_url="https://foscos.fssai.gov.in/apply-state-license")
                ],
                verification_source=VerificationSource(
                    url="https://foscos.fssai.gov.in/user-manuals/restaurant-food-services-flow.pdf",
                    page_title="FSSAI Food Safety Compliance System - Licensing Guide",
                    last_scraped_at="2026-09-22T14:15:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True
                ),
                tips_and_pitfalls="Mandatory to upload Food Safety Management System (FSMS) plan checklist during initial submission."
            ),
            TaskStep(
                id="blr-food-3b",
                task_id="task-blr-restaurant",
                step_number=4,
                title="Fire & Emergency Services Safety NOC",
                description="Obtain Fire Safety Clearances (Provisional NOC for premise inspection and compliance with National Building Code Part IV).",
                department=dept_fire,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=14,
                fee_amount=3500.0,
                fee_breakdown={"Department Inspection Fee": 2500.0, "Safety Assessment Scrutiny": 1000.0},
                prerequisites=["blr-food-1", "blr-food-2"],
                documents=[
                    DocumentRequirement(id="doc-fire-eq", name="Fire Extinguisher Invoice & ISI Certification", description="CO2 and ABC dry powder canisters with valid hydro test tag", is_mandatory=True),
                    DocumentRequirement(id="doc-evac", name="Premise Evacuation & Exit Route Diagram", description="Highlighted secondary emergency escape exits", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="KFES-NOC-1", title="Application for Fire Safety Verification of Commercial Eating House", download_url="https://ksfes.karnataka.gov.in/downloads/commercial_eating_house_noc.pdf")
                ],
                verification_source=VerificationSource(
                    url="https://ksfes.karnataka.gov.in/page.php?slug=advisory-for-commercial-premises",
                    page_title="Karnataka Fire & Emergency Services - Eating Establishment Safety Rules",
                    last_scraped_at="2026-09-18T10:00:00Z",
                    confidence_score=0.94,
                    is_admin_verified=True,
                    gazette_ref="Karnataka Fire Force Act 1964 Section 13"
                ),
                tips_and_pitfalls="Kitchen exhaust hood must feature automatic fire dampening or certified non-grease filtration."
            ),
            TaskStep(
                id="blr-food-3c",
                task_id="task-blr-restaurant",
                step_number=5,
                title="KSPCB Consent to Establish (CTE - Green Category)",
                description="Pollution control consent for grease trap effluent discharge, exhaust chimney height, and organic waste composter installation.",
                department=dept_kspcb,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=12,
                fee_amount=1800.0,
                fee_breakdown={"Consent Application Fee": 1800.0},
                prerequisites=["blr-food-1", "blr-food-2"],
                documents=[
                    DocumentRequirement(id="doc-grease", name="Oil & Grease Trap Schematic Diagram", description="Specifications of 3-chamber grease trap installation before sewer discharge", is_mandatory=True),
                    DocumentRequirement(id="doc-chimney", name="Kitchen Hood Exhaust Chimney Height Clearance", description="Must discharge minimum 3 meters above surrounding roof level", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="KSPCB-CTE-Form1", title="Combined Consent Mechanism for Hotel & Food Outlets", fill_online_url="https://kspcb.karnataka.gov.in/xgn-online-consent")
                ],
                verification_source=VerificationSource(
                    url="https://kspcb.karnataka.gov.in/category-of-industries-hotel-sector",
                    page_title="KSPCB - Guidelines for Hotels, Restaurants and Bakeries",
                    last_scraped_at="2026-09-15T16:20:00Z",
                    confidence_score=0.92,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="blr-food-4",
                task_id="task-blr-restaurant",
                step_number=6,
                title="BBMP Municipal Health & Trade License",
                description="The master municipal operational permit issued by the Medical Officer of Health (MOH) after verifying FSSAI, Fire NOC, and KSPCB consent.",
                department=dept_bbmp_health,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=15,
                fee_amount=6500.0,
                fee_breakdown={"Trade License Fee": 4000.0, "Solid Waste Management Cess": 1500.0, "Health Scrutiny Fee": 1000.0},
                prerequisites=["blr-food-3a", "blr-food-3b", "blr-food-3c"],
                documents=[
                    DocumentRequirement(id="doc-all-nocs", name="Combined Clearances Bundle (FSSAI + Fire + KSPCB)", description="All prerequisite clearance certificate copies", is_mandatory=True),
                    DocumentRequirement(id="doc-swm", name="BBMP Empanelled Solid Waste Vendor Agreement", description="Agreement with authorized waste aggregator for wet waste processing", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="BBMP-TL-H1", title="Application for Health & Trade License for Eating House", fill_online_url="https://bbmptax.karnataka.gov.in/tradelicense/newapplicant.aspx")
                ],
                verification_source=VerificationSource(
                    url="https://bbmptax.karnataka.gov.in/tradelicense/citizen_charter.pdf",
                    page_title="BBMP Trade License Citizen Charter & SLA",
                    last_scraped_at="2026-09-25T09:10:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True,
                    gazette_ref="BBMP Act 2020 Section 305 - Regulation of Trades & Food Establishments"
                ),
                tips_and_pitfalls="Critical bottleneck! Ensure MOH inspection date is booked immediately upon document upload. Rejection occurs if commercial SWM contract is missing."
            ),
            TaskStep(
                id="blr-food-5",
                task_id="task-blr-restaurant",
                step_number=7,
                title="Commercial Power Load Sanction (BESCOM LT-3)",
                description="Conversion or enhancement of electrical sanction to commercial power tier with separate energy meter and earthing test certificate.",
                department=dept_bescom,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=8,
                fee_amount=4500.0,
                fee_breakdown={"Meter Security Deposit": 3000.0, "Service Line Charge": 1500.0},
                prerequisites=["blr-food-4"],
                documents=[
                    DocumentRequirement(id="doc-tl-cert", name="Approved BBMP Trade License Certificate", description="Proof of lawful municipal operation", is_mandatory=True),
                    DocumentRequirement(id="doc-wiring", name="Licensed Electrical Contractor Wiring Completion Certificate", description="Class 1 contractor testing report", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="BESCOM-A1", title="Application for LT Commercial Power Connection", fill_online_url="https://bescom.karnataka.gov.in/apply-lt-connection")
                ],
                verification_source=VerificationSource(
                    url="https://bescom.karnataka.gov.in/page.php?slug=commercial-tariffs-lt3",
                    page_title="BESCOM Commercial Power Tariff & Service Connections",
                    last_scraped_at="2026-09-12T13:00:00Z",
                    confidence_score=0.93,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="blr-food-6",
                task_id="task-blr-restaurant",
                step_number=8,
                title="Municipal Commercial Signage & Nameboard Permit",
                description="Obtain permit for external building signage, ensuring Kannada language takes at least 60% prominent upper section per BBMP 2024 Ordinance.",
                department=dept_bbmp_town,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=5,
                fee_amount=2000.0,
                fee_breakdown={"Signage Tax Per Sq.Ft": 1500.0, "Scrutiny Fee": 500.0},
                prerequisites=["blr-food-4"],
                documents=[
                    DocumentRequirement(id="doc-sign-mockup", name="Signboard Elevation & Language Proportion Mockup", description="Visual elevation drawing showing 60% Kannada top ratio and dimension specs", is_mandatory=True)
                ],
                forms=[
                    FormRequirement(form_code="BBMP-ADV-02", title="Permission for Non-Illuminated/Illuminated Commercial Signboard", fill_online_url="https://bbmp.karnataka.gov.in/advertisement-portal")
                ],
                verification_source=VerificationSource(
                    url="https://bbmp.karnataka.gov.in/notification_signage_regulations_2024.pdf",
                    page_title="BBMP Official Notification - Signboard Language & Size Regulations",
                    last_scraped_at="2026-09-23T12:00:00Z",
                    confidence_score=0.96,
                    is_admin_verified=True,
                    gazette_ref="Karnataka Official Language (Amendment) Act 2024"
                ),
                tips_and_pitfalls="Violating the 60% Kannada signboard rule will lead to immediate cancellation of Trade License and sealing of premises."
            )
        ]

        task1 = CivicTask(
            id="task-blr-restaurant",
            title="Open a Restaurant, Bakery or Cloud Kitchen",
            category="Food & Hospitality",
            municipality="Bengaluru (BBMP)",
            state="Karnataka",
            description="Complete statutory roadmap to lawfully operate an eating house or food delivery kitchen in Bengaluru: from legal incorporation and kitchen safety NOCs to BBMP Trade License and signage.",
            tags=["restaurant", "food business", "cloud kitchen", "trade license", "fssai", "bbmp", "bengaluru", "commercial permit"],
            steps=task1_steps
        )
        self._tasks[task1.id] = task1

        # -------------------------------------------------------------------------
        # TASK 2: Commercial Construction & Building Plan Sanction (Mumbai BMC)
        # -------------------------------------------------------------------------
        dept_bmc_bldg = DepartmentInfo(
            id="dept-bmc-bldg",
            name="Brihanmumbai Municipal Corporation (Building Proposal Dept)",
            jurisdiction="Greater Mumbai (City / Suburbs)",
            office_address="BMC Head Office Extension, Mahapalika Marg, Fort, Mumbai - 400001",
            contact_phone="022-22620251",
            contact_email="chiefengineer.bp@mcgm.gov.in",
            portal_url="https://autodcr.mcgm.gov.in"
        )
        dept_bmc_tree = DepartmentInfo(
            id="dept-bmc-tree",
            name="BMC Tree Authority & Garden Department",
            jurisdiction="Municipal Corporation of Greater Mumbai",
            office_address="Parijat Building, Veer Savarkar Marg, Dadar West, Mumbai - 400028",
            contact_phone="022-24300301",
            contact_email="treeauthority@mcgm.gov.in",
            portal_url="https://portal.mcgm.gov.in"
        )
        dept_mumbai_fire = DepartmentInfo(
            id="dept-mumbai-fire",
            name="Mumbai Fire Brigade (Headquarters)",
            jurisdiction="Mumbai Fire Brigade Command",
            office_address="Byculla Fire Station, Balaram Street, Byculla, Mumbai - 400008",
            contact_phone="022-23076111",
            contact_email="cfo.fire@mcgm.gov.in",
            portal_url="https://portal.mcgm.gov.in"
        )

        task2_steps = [
            TaskStep(
                id="mum-bldg-1",
                task_id="task-mum-construction",
                step_number=1,
                title="City Survey & Land Ownership Demarcation (PR Card)",
                description="Obtain certified Property Registration Card (PR Card), City Survey demarcation plan, and verify title clearance from Revenue Dept.",
                department=dept_bmc_bldg,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=10,
                fee_amount=3000.0,
                fee_breakdown={"Demarcation Fee": 2000.0, "PR Card Certified Copy": 1000.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-mum-title", name="Certified Title Search Report (30 Years)", description="Advocate search report confirming encumbrance free title", is_mandatory=True),
                    DocumentRequirement(id="doc-mum-prcard", name="PR Card with CTS Number", description="Issued by Superintendent of Land Records (SLR)", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="SLR-CTS-01", title="Application for Certified Demarcation Sheet", fill_online_url="https://mahabhumi.gov.in")],
                verification_source=VerificationSource(
                    url="https://mahabhumi.gov.in/mahabhumihome",
                    page_title="Maharashtra Revenue - City Survey & Land Records",
                    last_scraped_at="2026-09-21T09:00:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mum-bldg-2",
                task_id="task-mum-construction",
                step_number=2,
                title="Development Plan Remark (DP-2034 Zoning Verification)",
                description="Procure official DP Remarks validating reservations, road widening set-backs, and permissible Floor Space Index (FSI).",
                department=dept_bmc_bldg,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=7,
                fee_amount=5000.0,
                fee_breakdown={"DP Scrutiny Fee": 5000.0},
                prerequisites=["mum-bldg-1"],
                documents=[
                    DocumentRequirement(id="doc-cad-layout", name="Cadastral Map Overlay", description="CAD overlay with Google Earth geo-coordinates", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="BMC-DP-REM", title="Application for Development Plan 2034 Remarks", fill_online_url="https://autodcr.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlDP2034",
                    page_title="BMC Development Plan 2034 Public Repository",
                    last_scraped_at="2026-09-19T14:30:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="DCPR 2034 Regulations 9 & 10"
                )
            ),
            TaskStep(
                id="mum-bldg-3a",
                task_id="task-mum-construction",
                step_number=3,
                title="AutoDCR Architectural Plan Scrutiny & Submission",
                description="Upload computer-aided architectural drawing files into BMC AutoDCR software for automatic building bye-law compliance check.",
                department=dept_bmc_bldg,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=14,
                fee_amount=15000.0,
                fee_breakdown={"AutoDCR Scrutiny Fee": 15000.0},
                prerequisites=["mum-bldg-2"],
                documents=[
                    DocumentRequirement(id="doc-dcr-dwg", name="AutoDCR Structured Drawing File (DWG)", description="Layered drawings following BMC AutoDCR color coding standard", is_mandatory=True),
                    DocumentRequirement(id="doc-arch-license", name="Council of Architecture Registered Architect Undertaking", description="Supervision appointment certificate", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="Appendix A-1", title="Notice of Intention to Erect Building under Section 337", fill_online_url="https://autodcr.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://autodcr.mcgm.gov.in/help/autodcr_user_manual.pdf",
                    page_title="BMC Building Proposal AutoDCR Portal",
                    last_scraped_at="2026-09-22T10:15:00Z",
                    confidence_score=0.96,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mum-bldg-3b",
                task_id="task-mum-construction",
                step_number=4,
                title="Mumbai Fire Brigade Chief Fire Officer (CFO) NOC",
                description="Fire safety clearance approving building height, refuge areas, fire lifts, sprinkler layouts, and driveway turning radiuses.",
                department=dept_mumbai_fire,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=21,
                fee_amount=25000.0,
                fee_breakdown={"Fire Service Premium Per Sq.Meter": 25000.0},
                prerequisites=["mum-bldg-2"],
                documents=[
                    DocumentRequirement(id="doc-cfo-dwg", name="CFO Fire Protection Drawings", description="Showing wet risers, fire escape staircase widths, and hydrant network", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="CFO-NOC-APP", title="Online CFO Building Clearance Form", fill_online_url="https://portal.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlfirebrigade",
                    page_title="Mumbai Fire Brigade Building Approvals",
                    last_scraped_at="2026-09-20T17:00:00Z",
                    confidence_score=0.95,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mum-bldg-3c",
                task_id="task-mum-construction",
                step_number=5,
                title="Tree Authority Tree Preservation / Relocation Clearance",
                description="Inspection of on-site trees; mandatory compensatory tree plantation deposit or tree cutting permission from Tree Authority.",
                department=dept_bmc_tree,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=15,
                fee_amount=10000.0,
                fee_breakdown={"Tree Deposit & Afforestation Cess": 10000.0},
                prerequisites=["mum-bldg-2"],
                documents=[
                    DocumentRequirement(id="doc-tree-survey", name="Botanical Tree Census & Geo-Tagged Site Photos", description="Marking botanical names, girth, and height of trees on plot", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="BMC-TA-01", title="Application for Tree Felling/Transplantation Clearance", download_url="https://portal.mcgm.gov.in/tree_authority_form.pdf")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qltreeauthority",
                    page_title="BMC Tree Authority Citizen Charter",
                    last_scraped_at="2026-09-17T11:00:00Z",
                    confidence_score=0.91,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mum-bldg-4",
                task_id="task-mum-construction",
                step_number=6,
                title="Issuance of Intimation of Disapproval (IOD)",
                description="Executive Engineer issues IOD (Conditional Approval) listing 30 to 45 statutory compliance conditions prior to plinth work.",
                department=dept_bmc_bldg,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=30,
                fee_amount=50000.0,
                fee_breakdown={"Development Charges": 35000.0, "Labour Cess (1%)": 15000.0},
                prerequisites=["mum-bldg-3a", "mum-bldg-3b", "mum-bldg-3c"],
                documents=[
                    DocumentRequirement(id="doc-all-consents", name="Consolidated Clearances Dossier", description="Approved AutoDCR + CFO NOC + Tree Authority NOC", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="MMC Section 346", title="Formal Intimation of Disapproval (IOD) Issuance Order", fill_online_url="https://autodcr.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlbuildingproposal",
                    page_title="BMC Building Proposal Manual of Procedures",
                    last_scraped_at="2026-09-24T15:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Mumbai Municipal Corporation Act 1888 Section 346"
                ),
                tips_and_pitfalls="Major milestone! The IOD unlocks right to deposit development cess and proceed to commencement certification."
            ),
            TaskStep(
                id="mum-bldg-5",
                task_id="task-mum-construction",
                step_number=7,
                title="Commencement Certificate (CC - Plinth Level)",
                description="After clearing all 40+ IOD conditions and paying development cess, ward surveyor inspects site and grants formal legal permit to dig and build.",
                department=dept_bmc_bldg,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=18,
                fee_amount=12000.0,
                fee_breakdown={"CC Endorsement Fee": 12000.0},
                prerequisites=["mum-bldg-4"],
                documents=[
                    DocumentRequirement(id="doc-iod-compliance", name="Itemized IOD Compliance Compliance Affidavit", description="Notarized compliance on Rs 500 stamp paper", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="Appendix C", title="Application for Commencement Certificate", fill_online_url="https://autodcr.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://autodcr.mcgm.gov.in/citizen_info/cc_issuance_sop.pdf",
                    page_title="Standard Operating Procedure for CC Issuance",
                    last_scraped_at="2026-09-25T11:20:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mum-bldg-6",
                task_id="task-mum-construction",
                step_number=8,
                title="Building Completion Certificate (BCC) & Occupancy Certificate (OC)",
                description="Final statutory inspection of constructed building, verifying water line, sewerage connection, rainwater harvesting, and fire safety.",
                department=dept_bmc_bldg,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=25,
                fee_amount=20000.0,
                fee_breakdown={"BCC Scrutiny Fee": 10000.0, "Water Connection Assessment": 10000.0},
                prerequisites=["mum-bldg-5"],
                documents=[
                    DocumentRequirement(id="doc-as-built", name="As-Built Architectural Drawings", description="Final plans reflecting exact physical construction on ground", is_mandatory=True),
                    DocumentRequirement(id="doc-cfo-final", name="CFO Final Fire Safety NOC", description="On-site water sprinkler and fire hose functional certificate", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="Appendix D", title="Completion Certificate & Notice of Completion", fill_online_url="https://autodcr.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qloccupancycertificate",
                    page_title="BMC Guidelines for Grant of Occupancy Certificate",
                    last_scraped_at="2026-09-24T18:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                )
            )
        ]

        task2 = CivicTask(
            id="task-mum-construction",
            title="Commercial Building Plan Sanction & Occupancy (OC)",
            category="Construction & Real Estate",
            municipality="Mumbai (BMC / MCGM)",
            state="Maharashtra",
            description="Comprehensive municipal clearance path to obtain Building Plan Sanction, IOD, Plinth Commencement Certificate (CC), and Occupancy Certificate (OC) under BMC DCPR-2034.",
            tags=["building permit", "construction", "autodcr", "iod", "commencement certificate", "occupancy certificate", "bmc", "mumbai"],
            steps=task2_steps
        )
        self._tasks[task2.id] = task2

        # -------------------------------------------------------------------------
        # TASK 3: Property Tax Mutation & Khata Transfer (Delhi MCD)
        # -------------------------------------------------------------------------
        dept_mcd_revenue = DepartmentInfo(
            id="dept-mcd-revenue",
            name="Municipal Corporation of Delhi (Assessment & Collection Dept)",
            jurisdiction="NCT of Delhi (North/South/East Zones)",
            office_address="Dr. S.P. Mukherjee Civic Centre, JLN Marg, New Delhi - 110002",
            contact_phone="011-23225227",
            contact_email="propertytax@mcd.nic.in",
            portal_url="https://mcdonline.nic.in"
        )
        dept_delhi_rev = DepartmentInfo(
            id="dept-delhi-rev",
            name="Revenue Department, GNCTD (Sub-Registrar Office)",
            jurisdiction="Government of NCT of Delhi",
            office_address="Zonal Sub-Registrar Office, Mehrauli Road, New Delhi",
            contact_phone="011-23935222",
            contact_email="doris.helpdesk@delhi.gov.in",
            portal_url="https://esearch.delhigovt.nic.in"
        )

        task3_steps = [
            TaskStep(
                id="del-mut-1",
                task_id="task-del-mutation",
                step_number=1,
                title="Sub-Registrar Sale Deed Verification & E-Search",
                description="Verify registration index of registered title deed or gift deed on Delhi Online Registration Information System (DORIS).",
                department=dept_delhi_rev,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=2,
                fee_amount=200.0,
                fee_breakdown={"E-Search Inspection Fee": 200.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-reg-deed", name="Registered Conveyance / Sale Deed Copy", description="With Sub-Registrar stamp and volume number", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="DORIS-INDEX-II", title="Certified Copy of Book No. 1 Index II", fill_online_url="https://esearch.delhigovt.nic.in")],
                verification_source=VerificationSource(
                    url="https://esearch.delhigovt.nic.in/CompleteDetails.aspx",
                    page_title="GNCTD Revenue - Online Registered Document Verification",
                    last_scraped_at="2026-09-23T10:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="del-mut-2",
                task_id="task-del-mutation",
                step_number=2,
                title="Property Tax Nil Dues Certificate (NDC)",
                description="Clear all outstanding municipal property taxes up to the current financial year and generate automated NDC from MCD portal.",
                department=dept_mcd_revenue,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=0.0,
                fee_breakdown={"Tax Arrears": 0.0, "NDC Generation": 0.0},
                prerequisites=["del-mut-1"],
                documents=[
                    DocumentRequirement(id="doc-upic", name="Unique Property Identification Code (UPIC) Card", description="15-digit alphanumeric property identifier", is_mandatory=True),
                    DocumentRequirement(id="doc-tax-challan", name="Last 3 Years Property Tax Receipts", description="Self-assessment receipts with transaction UTR", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="MCD-PTR-NDC", title="Application for No Dues Certificate", fill_online_url="https://mcdonline.nic.in/ptax/public/ndc")],
                verification_source=VerificationSource(
                    url="https://mcdonline.nic.in/ptax/public/guidelines_mutation.pdf",
                    page_title="MCD Property Tax Guidelines - Section on NDC & Mutation",
                    last_scraped_at="2026-09-22T13:40:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="del-mut-3",
                task_id="task-del-mutation",
                step_number=3,
                title="Online MCD Property Mutation Application (Form A)",
                description="File electronic mutation application on MCD portal attaching sale deed, NDC, indemnity bond, and NOC from co-owners.",
                department=dept_mcd_revenue,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=5,
                fee_amount=1500.0,
                fee_breakdown={"Mutation Scrutiny Fee": 1000.0, "Document Processing Fee": 500.0},
                prerequisites=["del-mut-1", "del-mut-2"],
                documents=[
                    DocumentRequirement(id="doc-indemnity", name="Notarized Indemnity Bond on Rs 100 Stamp", description="In prescribed format indemnifying MCD against future claims", is_mandatory=True),
                    DocumentRequirement(id="doc-affidavit", name="Affidavit regarding Legal Heirship / Title", description="Attested by Notary Public or Oath Commissioner", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="MCD Form A", title="Application for Mutation of Name in Property Tax Records", fill_online_url="https://mcdonline.nic.in/ptax/citizen/mutation")],
                verification_source=VerificationSource(
                    url="https://mcdonline.nic.in/ptax/citizen/citizen_charter.pdf",
                    page_title="MCD Citizen Charter - Property Tax Mutation SLA",
                    last_scraped_at="2026-09-24T16:15:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Delhi Municipal Corporation Act 1957 Section 128"
                )
            ),
            TaskStep(
                id="del-mut-4",
                task_id="task-del-mutation",
                step_number=4,
                title="Public Notice & Objection Period (15 Days)",
                description="Statutory publication of intention to mutate property record on MCD public notice portal to invite objections from legal heirs/lenders.",
                department=dept_mcd_revenue,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=15,
                fee_amount=500.0,
                fee_breakdown={"Public Notice Hosting Fee": 500.0},
                prerequisites=["del-mut-3"],
                documents=[],
                forms=[FormRequirement(form_code="Notice-Sec-128", title="Public Notice of Property Record Transfer", fill_online_url="https://mcdonline.nic.in/public_notices")],
                verification_source=VerificationSource(
                    url="https://mcdonline.nic.in/public_notices/mutation_notices",
                    page_title="MCD Portal - Public Notices under Section 128",
                    last_scraped_at="2026-09-25T08:00:00Z",
                    confidence_score=0.95,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="del-mut-5",
                task_id="task-del-mutation",
                step_number=5,
                title="Zonal Assessor & Collector Approval & Digital Mutation Certificate",
                description="Joint Assessor and Collector signs digital order transferring property ownership in municipal assessment books and issues QR-verified Mutation Certificate.",
                department=dept_mcd_revenue,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=5,
                fee_amount=1000.0,
                fee_breakdown={"Certificate Generation Fee": 1000.0},
                prerequisites=["del-mut-4"],
                documents=[],
                forms=[FormRequirement(form_code="MCD-MUT-CERT", title="Digital Property Tax Mutation Certificate", fill_online_url="https://mcdonline.nic.in/download_mutation_cert")],
                verification_source=VerificationSource(
                    url="https://mcdonline.nic.in/ptax/public/mutation_certificate_verification",
                    page_title="MCD Online Digital Certificate Verification",
                    last_scraped_at="2026-09-25T14:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True
                )
            )
        ]

        task3 = CivicTask(
            id="task-del-mutation",
            title="Property Tax Mutation & Title Transfer",
            category="Property & Revenue",
            municipality="Delhi (MCD)",
            state="Delhi (NCT)",
            description="Official statutory sequence for updating property ownership records (Namantaran / Mutation) in Municipal Corporation of Delhi records following purchase, inheritance or gift.",
            tags=["property tax", "mutation", "mcd", "delhi", "namantaran", "khata transfer", "nil dues certificate", "upic"],
            steps=task3_steps
        )
        self._tasks[task3.id] = task3

        # -------------------------------------------------------------------------
        # TASK 4: Tech Services / Retail Micro-Enterprise (Hyderabad GHMC)
        # -------------------------------------------------------------------------
        dept_ghmc = DepartmentInfo(
            id="dept-ghmc",
            name="Greater Hyderabad Municipal Corporation (Citizen Service Centres)",
            jurisdiction="Hyderabad Metropolitan Area",
            office_address="GHMC Head Office, Tank Bund Road, Hyderabad - 500063",
            contact_phone="040-21111111",
            contact_email="comm_ghmc@ghmc.gov.in",
            portal_url="https://www.ghmc.gov.in"
        )
        dept_ts_labour = DepartmentInfo(
            id="dept-ts-labour",
            name="Telangana Labour Department",
            jurisdiction="Government of Telangana",
            office_address="Labour Welfare Centre, RTC X Roads, Musheerabad, Hyderabad",
            contact_phone="040-27602333",
            contact_email="col.labour@telangana.gov.in",
            portal_url="https://labour.telangana.gov.in"
        )

        task4_steps = [
            TaskStep(
                id="hyd-biz-1",
                task_id="task-hyd-tech-biz",
                step_number=1,
                title="Udyam MSME Self-Declaration Registration",
                description="Instant free national registration for Micro, Small and Medium Enterprises based on Aadhaar and PAN.",
                department=dept_mca,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=1,
                fee_amount=0.0,
                fee_breakdown={"Zero Government Fee": 0.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-hyd-aadhaar", name="Aadhaar Linked with Mobile", description="For instant OTP verification", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="Udyam-01", title="Udyam Registration Portal Application", fill_online_url="https://udyamregistration.gov.in")],
                verification_source=VerificationSource(
                    url="https://udyamregistration.gov.in/Government-India/Ministry-MSME-registration.htm",
                    page_title="Official Ministry of MSME Udyam Registration Portal",
                    last_scraped_at="2026-09-24T12:00:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="hyd-biz-2",
                task_id="task-hyd-tech-biz",
                step_number=2,
                title="Telangana Shops & Establishments Registration",
                description="Mandatory statutory registration for any commercial office, shop or service facility under the Telangana Shops and Establishments Act.",
                department=dept_ts_labour,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=500.0,
                fee_breakdown={"Registration Fee (1-5 Employees)": 500.0},
                prerequisites=["hyd-biz-1"],
                documents=[
                    DocumentRequirement(id="doc-hyd-lease", name="Office Lease or Electricity Bill", description="Proof of commercial physical address in Telangana", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="Form A - Shops Act", title="Application for Registration of Commercial Establishment", fill_online_url="https://labour.telangana.gov.in")],
                verification_source=VerificationSource(
                    url="https://ts-bpass.telangana.gov.in/labour-services",
                    page_title="TS-iPASS Telangana Single Window - Labour Clearance",
                    last_scraped_at="2026-09-21T15:30:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="hyd-biz-3",
                task_id="task-hyd-tech-biz",
                step_number=3,
                title="GHMC Instant Self-Certification Trade License (TS-bPASS)",
                description="Under Telangana's TS-bPASS reform, low-risk commercial tech enterprises can obtain instant Trade License via online self-declaration.",
                department=dept_ghmc,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=1,
                fee_amount=2500.0,
                fee_breakdown={"Trade License Fee": 2000.0, "Garbage User Charges": 500.0},
                prerequisites=["hyd-biz-1", "hyd-biz-2"],
                documents=[
                    DocumentRequirement(id="doc-ghmc-self", name="TS-bPASS Self-Certification Declaration", description="Acceptance of fire and safety norms", is_mandatory=True)
                ],
                forms=[FormRequirement(form_code="GHMC-TS-BPASS-TL", title="Instant Trade License Issuance Form", fill_online_url="https://tsbpass.telangana.gov.in/tradelicense")],
                verification_source=VerificationSource(
                    url="https://www.ghmc.gov.in/tradelicense/instant_service.aspx",
                    page_title="GHMC Official Trade License Portal",
                    last_scraped_at="2026-09-25T11:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Telangana Municipalities Act 2019 Section 274"
                )
            ),
            TaskStep(
                id="hyd-biz-4",
                task_id="task-hyd-tech-biz",
                step_number=4,
                title="GHMC External Signboard & Nameboard Clearance",
                description="Self-registration of commercial facade nameplate under permissible size guidelines (within 3x2 meters).",
                department=dept_ghmc,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=2,
                fee_amount=1000.0,
                fee_breakdown={"Signage Fee": 1000.0},
                prerequisites=["hyd-biz-3"],
                documents=[],
                forms=[FormRequirement(form_code="GHMC-ADV-01", title="Signboard Permission Certificate", fill_online_url="https://www.ghmc.gov.in/advt")],
                verification_source=VerificationSource(
                    url="https://www.ghmc.gov.in/advt/rules.pdf",
                    page_title="GHMC Advertisement Fee Schedule",
                    last_scraped_at="2026-09-20T16:00:00Z",
                    confidence_score=0.94,
                    is_admin_verified=True
                )
            )
        ]

        task4 = CivicTask(
            id="task-hyd-tech-biz",
            title="Register an IT & Tech Services Commercial Office",
            category="Business & Enterprise",
            municipality="Hyderabad (GHMC)",
            state="Telangana",
            description="Rapid self-certification pathway under Telangana's TS-bPASS and TS-iPASS single-window system for starting an IT/ITES consultancy or commercial office.",
            tags=["it office", "startup", "ghmc", "hyderabad", "ts-bpass", "trade license", "msme", "shops act"],
            steps=task4_steps
        )
        self._tasks[task4.id] = task4

# Singleton database instance
db = CivicDatabase()
