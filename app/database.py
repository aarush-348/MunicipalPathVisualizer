from typing import List, Dict, Optional
from datetime import datetime
from app.models import (
    CivicTask, TaskStep, DepartmentInfo, DocumentRequirement,
    FormRequirement, VerificationSource, SubmissionMode, StepStatus
)
from app.database_sqlite import sqlite_db
import os

class CivicDatabase:
    def __init__(self):
        self._tasks: Dict[str, CivicTask] = {}
        self._audit_logs: List[Dict] = []
        self._citizen_feedback: List[Dict] = []
        self._regulatory_audits: Dict[str, Dict] = {
            "aaple_sarkar": {
                "portal_id": "aaple_sarkar",
                "name": "Maharashtra Aaple Sarkar (RTS)",
                "url": "https://aaplesarkar.mahaonline.gov.in",
                "status_code": 200,
                "page_title": "Aaple Sarkar - Government of Maharashtra Citizen Services Portal",
                "last_scraped_at": "2026-09-26T15:30:00Z",
                "confidence_score": 0.99,
                "gazette_ref": "Maharashtra Right to Public Services Act 2015",
                "verified_sla_days": 15,
                "fee_schedule": "Statutory fees ₹20 - ₹100 via Gras MahaKosh",
                "is_active": True
            },
            "eci_voters": {
                "portal_id": "eci_voters",
                "name": "Election Commission of India (ECI / NVSP)",
                "url": "https://voters.eci.gov.in",
                "status_code": 200,
                "page_title": "Election Commission of India - Voters' Service Portal",
                "last_scraped_at": "2026-09-26T14:20:00Z",
                "confidence_score": 0.98,
                "gazette_ref": "Representation of the People Act 1950",
                "verified_sla_days": 30,
                "fee_schedule": "Free of cost (₹0 statutory fee)",
                "is_active": True
            },
            "parivahan": {
                "portal_id": "parivahan",
                "name": "MoRTH Parivahan Sarathi & Vahan",
                "url": "https://parivahan.gov.in",
                "status_code": 200,
                "page_title": "Parivahan Sewa - Ministry of Road Transport and Highways",
                "last_scraped_at": "2026-09-26T13:45:00Z",
                "confidence_score": 0.99,
                "gazette_ref": "Motor Vehicles Act 1988 & CMVR 1989",
                "verified_sla_days": 21,
                "fee_schedule": "Rule 32 CMVR Statutory Fee Schedule (LL ₹150, DL ₹200)",
                "is_active": True
            },
            "fssai_foscos": {
                "portal_id": "fssai_foscos",
                "name": "FSSAI FoSCoS Food Safety Portal",
                "url": "https://foscos.fssai.gov.in",
                "status_code": 200,
                "page_title": "Food Safety Compliance System (FoSCoS) - FSSAI",
                "last_scraped_at": "2026-09-26T12:15:00Z",
                "confidence_score": 0.97,
                "gazette_ref": "Food Safety and Standards Act 2006",
                "verified_sla_days": 30,
                "fee_schedule": "Registration ₹100/yr, State License ₹2000-₹5000/yr",
                "is_active": True
            },
            "mcd_online": {
                "portal_id": "mcd_online",
                "name": "Municipal Corporation of Delhi (MCD)",
                "url": "https://mcdonline.nic.in",
                "status_code": 200,
                "page_title": "MCD Online Services - Property Tax, Health Trade, AutoDCR",
                "last_scraped_at": "2026-09-26T11:00:00Z",
                "confidence_score": 0.96,
                "gazette_ref": "Delhi Municipal Corporation Act 1957",
                "verified_sla_days": 15,
                "fee_schedule": "Municipal Health Trade & General Trade Bye-laws 2024",
                "is_active": True
            },
            "incometax": {
                "portal_id": "incometax",
                "name": "Income Tax Department & NSDL PAN",
                "url": "https://incometax.gov.in",
                "status_code": 200,
                "page_title": "Income Tax E-Filing & PAN Allotment System",
                "last_scraped_at": "2026-09-26T16:00:00Z",
                "confidence_score": 0.99,
                "gazette_ref": "Income Tax Act 1961 Section 139A",
                "verified_sla_days": 7,
                "fee_schedule": "Form 49A PAN fee ₹107 (Physical), ₹72 (e-PAN only)",
                "is_active": True
            }
        }
        self._init_seed_data()
        self._sync_sqlite()

    def _sync_sqlite(self):
        try:
            # Seed 18 Aaple Sarkar official services
            sample_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_services.json")
            sqlite_db.seed_aaple_sarkar_services(sample_json)
            # Persist curated Maharashtra tasks
            for task in self._tasks.values():
                sqlite_db.persist_task(task.model_dump())
        except Exception as e:
            print(f"[SQLite Warning] Sync failed: {e}")

    def add_task(self, task: CivicTask):
        self._tasks[task.id] = task
        try:
            sqlite_db.persist_task(task.model_dump())
        except Exception as e:
            print(f"[SQLite Warning] Failed to persist task {task.id}: {e}")

    def get_all_tasks(self) -> List[CivicTask]:
        return list(self._tasks.values())

    def get_task_by_id(self, task_id: str) -> Optional[CivicTask]:
        return self._tasks.get(task_id)

    def get_regulatory_audits(self) -> List[Dict]:
        return list(self._regulatory_audits.values())

    def update_regulatory_audit(self, portal_id: str, data: Dict):
        if portal_id in self._regulatory_audits:
            self._regulatory_audits[portal_id].update(data)
        else:
            self._regulatory_audits[portal_id] = data

    def search_tasks(self, query: str, municipality: Optional[str] = None) -> List[CivicTask]:
        q = query.lower()
        results = []
        for task in self._tasks.values():
            match_mun = True
            if municipality and municipality.lower() not in ("all", "any", "maharashtra statewide"):
                match_mun = (
                    municipality.lower() in task.municipality.lower() or
                    task.municipality.lower() in municipality.lower() or
                    "maharashtra" in task.municipality.lower()
                )
            
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
        try:
            sqlite_db.record_audit(action=action, details=details, user_name=user)
        except Exception:
            pass

    def get_audit_logs(self) -> List[Dict]:
        return list(reversed(self._audit_logs))

    def add_citizen_feedback(self, step_id: str, issue_type: str, notes: str):
        fb_id = f"fb-{len(self._citizen_feedback) + 1}"
        self._citizen_feedback.append({
            "id": fb_id,
            "step_id": step_id,
            "issue_type": issue_type,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_review"
        })
        try:
            sqlite_db.record_feedback(fb_id=fb_id, step_id=step_id, issue_type=issue_type, notes=notes)
        except Exception:
            pass

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
                try:
                    sqlite_db.persist_task(task.model_dump())
                except Exception:
                    pass
                return True
        return False

    def _init_seed_data(self):
        # =========================================================================
        # REUSABLE MAHARASHTRA GOVERNMENT DEPARTMENTS MASTER
        # =========================================================================
        dept_mca_mum = DepartmentInfo(
            id="dept-mca-mum",
            name="Ministry of Corporate Affairs (RoC Mumbai) & GSTN",
            jurisdiction="Central Government (Maharashtra Desk)",
            office_address="Everest Building, 100 Marine Drive, Nariman Point, Mumbai - 400002",
            contact_phone="022-22812627",
            contact_email="roc.mumbai@mca.gov.in",
            working_hours="Monday - Friday: 9:30 AM - 5:30 PM IST",
            portal_url="https://www.mca.gov.in"
        )
        dept_msme = DepartmentInfo(
            id="dept-msme",
            name="Ministry of Micro, Small & Medium Enterprises (Udyam Maharashtra)",
            jurisdiction="Government of India & Maharashtra MSME Facilitation Cell",
            office_address="MSME-DFO, Kurla-Andheri Road, Saki Naka, Mumbai - 400072",
            contact_phone="022-28576090",
            contact_email="dcdi-mumbai@dcmsme.gov.in",
            working_hours="Monday - Friday: 9:30 AM - 6:00 PM IST",
            portal_url="https://udyamregistration.gov.in"
        )
        dept_mah_labour = DepartmentInfo(
            id="dept-mah-labour",
            name="Maharashtra Labour Department (LMS MahaOnline & Aaple Sarkar)",
            jurisdiction="Government of Maharashtra (Statewide Labour Commissionerate)",
            office_address="Kamgar Bhavan, C-20, E-Block, Bandra Kurla Complex (BKC), Bandra East, Mumbai - 400051",
            contact_phone="022-26572631",
            contact_email="labour.comm@maharashtra.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 5:30 PM IST",
            portal_url="https://lms.mahaonline.gov.in"
        )
        dept_mcgm_labour = DepartmentInfo(
            id="dept-mcgm-labour",
            name="MCGM Labour & Shops Department (Ward H/West)",
            jurisdiction="Brihanmumbai Municipal Corporation (BMC / MCGM)",
            office_address="MCGM Ward H/West Office, Saint Martin Road, Bandra West, Mumbai - 400050",
            contact_phone="022-26422311",
            contact_email="shops.hwest@mcgm.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 2:30 PM IST",
            portal_url="https://portal.mcgm.gov.in"
        )
        dept_mfb = DepartmentInfo(
            id="dept-mfb",
            name="Mumbai Fire Brigade (Chief Fire Officer Command)",
            jurisdiction="Brihanmumbai Municipal Corporation (Greater Mumbai Command)",
            office_address="Byculla Fire Brigade Headquarters, Bapurao Jagtap Marg, Byculla, Mumbai - 400008",
            contact_phone="022-23076111",
            contact_email="fire.noc@mcgm.gov.in",
            working_hours="Monday - Friday: 10:30 AM - 3:30 PM IST",
            portal_url="https://portal.mcgm.gov.in"
        )
        dept_fssai_mum = DepartmentInfo(
            id="dept-fssai-mum",
            name="Food Safety and Standards Authority of India (FSSAI Western Region) & FDA Maharashtra",
            jurisdiction="Central / Maharashtra FDA Regulatory Zone",
            office_address="Food & Drug Administration Maharashtra, Survey No 341, Bandra Kurla Complex (BKC), Bandra East, Mumbai - 400051",
            contact_phone="1800-112-100",
            contact_email="foscos.helpdesk@fssai.gov.in",
            working_hours="Monday - Friday: 9:30 AM - 6:00 PM IST",
            portal_url="https://foscos.fssai.gov.in"
        )
        dept_mpcb = DepartmentInfo(
            id="dept-mpcb",
            name="Maharashtra Pollution Control Board (MPCB Regional Office)",
            jurisdiction="State Environmental Protection Authority (Government of Maharashtra)",
            office_address="Kalpataru Point, 3rd Floor, Opp. Cine Planet, Sion Circle, Sion East, Mumbai - 400022",
            contact_phone="022-24010437",
            contact_email="ms@mpcb.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 5:30 PM IST",
            portal_url="https://mpcb.gov.in"
        )
        dept_mcgm_health = DepartmentInfo(
            id="dept-mcgm-health",
            name="MCGM Public Health Department (Medical Officer of Health - Ward H/West)",
            jurisdiction="Brihanmumbai Municipal Corporation (Ward H/West)",
            office_address="Saint Martin Road, Behind Bandra Police Station, Bandra West, Mumbai - 400050",
            contact_phone="022-26422311",
            contact_email="moh.hwest@mcgm.gov.in",
            working_hours="Monday - Friday: 10:30 AM - 3:00 PM IST",
            portal_url="https://portal.mcgm.gov.in"
        )
        dept_mcgm_estate = DepartmentInfo(
            id="dept-mcgm-estate",
            name="MCGM License & Estate Department (Section 328/394)",
            jurisdiction="Brihanmumbai Municipal Corporation (Headquarters)",
            office_address="Municipal Corporation Building, Mahapalika Marg, Fort, Mumbai - 400001",
            contact_phone="022-22620251",
            contact_email="licenses.hq@mcgm.gov.in",
            working_hours="Monday - Friday: 10:30 AM - 4:30 PM IST",
            portal_url="https://portal.mcgm.gov.in"
        )
        dept_mahagst = DepartmentInfo(
            id="dept-mahagst",
            name="Department of Goods and Services Tax, Maharashtra (MahaGST)",
            jurisdiction="Government of Maharashtra",
            office_address="GST Bhavan, Mazgaon, Mumbai - 400010",
            contact_phone="1800-225-900",
            contact_email="helpdesk@mahagst.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 5:30 PM IST",
            portal_url="https://mahagst.gov.in"
        )
        dept_pmc_health = DepartmentInfo(
            id="dept-pmc-health",
            name="Pune Municipal Corporation (PMC Health Department)",
            jurisdiction="Pune Municipal Corporation (PMC)",
            office_address="PMC Main Building, Shivajinagar, Pune - 411005",
            contact_phone="020-25501000",
            contact_email="health@punecorporation.org",
            working_hours="Monday - Friday: 10:00 AM - 5:00 PM IST",
            portal_url="https://pmc.gov.in"
        )
        dept_pmc_fire = DepartmentInfo(
            id="dept-pmc-fire",
            name="Pune Fire Brigade (PMC Central Fire Command)",
            jurisdiction="Pune Municipal Corporation",
            office_address="Central Fire Station, New Timber Market, Ganj Peth, Pune - 411042",
            contact_phone="020-26451707",
            contact_email="fire@punecorporation.org",
            working_hours="Monday - Friday: 10:00 AM - 5:00 PM IST",
            portal_url="https://pmc.gov.in"
        )
        dept_mcgm_bp = DepartmentInfo(
            id="dept-mcgm-bp",
            name="BMC Building Proposals Department (AutoDCR Cell)",
            jurisdiction="Municipal Corporation of Greater Mumbai",
            office_address="Engineering Hub, Dr. E. Moses Road, Worli, Mumbai - 400018",
            contact_phone="022-24958000",
            contact_email="che.bp@mcgm.gov.in",
            working_hours="Monday - Friday: 10:30 AM - 4:00 PM IST",
            portal_url="https://autodcr.mcgm.gov.in"
        )
        dept_mahabhumi = DepartmentInfo(
            id="dept-mahabhumi",
            name="Revenue & Forest Department, Maharashtra (MahaBhumi E-Ferfar Cell)",
            jurisdiction="Government of Maharashtra (State Land Records)",
            office_address="Settlement Commissioner & Director of Land Records, Central Building, Pune - 411001",
            contact_phone="020-26050009",
            contact_email="dlr.pune@mahabhumi.gov.in",
            working_hours="Monday - Friday: 10:00 AM - 5:30 PM IST",
            portal_url="https://mahabhumi.gov.in"
        )
        dept_igr = DepartmentInfo(
            id="dept-igr",
            name="Inspector General of Registration & Controller of Stamps (IGR Maharashtra)",
            jurisdiction="Government of Maharashtra",
            office_address="IGR Office, Ground Floor, Central Building, Station Road, Pune - 411001",
            contact_phone="020-26050011",
            contact_email="complaint@igrmaharashtra.gov.in",
            working_hours="Monday - Friday: 9:45 AM - 5:30 PM IST",
            portal_url="https://igrmaharashtra.gov.in"
        )
        dept_mcgm_he = DepartmentInfo(
            id="dept-mcgm-he",
            name="MCGM Hydraulic Engineer Department (Water Works)",
            jurisdiction="Brihanmumbai Municipal Corporation",
            office_address="Hydraulic Engineer Office, Worli Water Works, Dr. E. Moses Road, Worli, Mumbai - 400018",
            contact_phone="022-24958100",
            contact_email="he@mcgm.gov.in",
            working_hours="Monday - Friday: 10:30 AM - 4:30 PM IST",
            portal_url="https://portal.mcgm.gov.in"
        )
        dept_aaple_sarkar = DepartmentInfo(
            id="dept-aaple-sarkar",
            name="Aaple Sarkar Citizen Services (Maharashtra Right to Public Services Commission)",
            jurisdiction="Government of Maharashtra (Statewide RTS Portal)",
            office_address="General Administration Department, Mantralaya, Nariman Point, Mumbai - 400032",
            contact_phone="1800-120-8040",
            contact_email="support.aaplesarkar@mahaonline.gov.in",
            working_hours="24x7 Digital Portal / Helpline: Mon-Sat 8:00 AM - 8:00 PM IST",
            portal_url="https://aaplesarkar.mahaonline.gov.in"
        )

        # -------------------------------------------------------------------------
        # TASK 1: Register a Small Business / Retail Enterprise in Maharashtra (Gumasta)
        # Direct Answer to: "I want to register a small business"
        # -------------------------------------------------------------------------
        task_small_biz_steps = [
            TaskStep(
                id="mah-biz-1",
                task_id="task-mah-small-biz",
                step_number=1,
                title="PAN & Udyam MSME Zero-Fee Registration",
                description="Obtain Indian Business Permanent Account Number (PAN) and free National MSME recognition via Government of India Udyam Portal using Aadhaar OTP verification.",
                department=dept_msme,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=1,
                fee_amount=0.0,
                fee_breakdown={"Statutory Government Fee": 0.0, "Udyam Certificate Generation": 0.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-pan-aadhaar", name="Aadhaar Card Linked to Mobile", description="Required for electronic biometric e-KYC and digital signing", is_mandatory=True, category="Identity Proof"),
                    DocumentRequirement(id="doc-prop-pan", name="Proprietor / Managing Partner PAN Card", description="Permanent Account Number for tax linkage", is_mandatory=True, category="Tax Identity")
                ],
                forms=[FormRequirement(form_code="Udyam-01", title="Udyam Registration Portal Application", fill_online_url="https://udyamregistration.gov.in")],
                verification_source=VerificationSource(
                    url="https://udyamregistration.gov.in/Government-India/Ministry-MSME-registration.htm",
                    page_title="Official Ministry of MSME Udyam Registration Portal",
                    last_scraped_at="2026-09-26T10:00:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True,
                    gazette_ref="Micro, Small and Medium Enterprises Development Act, 2006"
                ),
                tips_and_pitfalls="Beware of fraudulent commercial websites charging money for Udyam registration; the official government portal is 100% free.",
                anti_tout_advisory="Do not pay touts or unofficial agencies. Udyam is paperless, free of cost, and instant."
            ),
            TaskStep(
                id="mah-biz-2",
                task_id="task-mah-small-biz",
                step_number=2,
                title="Commercial Premises Verification & Registered Lease / Tax Index",
                description="Verify lawful tenancy or title of the commercial premise with registered rent agreement or property tax receipt / electricity bill in Maharashtra.",
                department=dept_igr,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=2,
                fee_amount=1300.0,
                fee_breakdown={"E-Search Inspection Fee": 300.0, "Document Attestation Stamp": 1000.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-rent-lease", name="Registered Commercial Leave & License Agreement", description="Notarized or registered under Maharashtra Rent Control Act", is_mandatory=True, category="Premise Title"),
                    DocumentRequirement(id="doc-elec-bill", name="Recent Commercial Electricity Bill (MSEDCL / Tata / Adani)", description="Issued within last 2 months showing consumer number and commercial tariff", is_mandatory=True, category="Premise Address Proof"),
                    DocumentRequirement(id="doc-owner-noc", name="NOC from Landlord / Society", description="No Objection Certificate for commercial usage of property", is_mandatory=True, category="Clearance NOC")
                ],
                forms=[FormRequirement(form_code="IGR-INDEX-II", title="E-Registration Certified Index-II Copy", fill_online_url="https://esearchigr.maharashtra.gov.in/esearch/")],
                verification_source=VerificationSource(
                    url="https://esearchigr.maharashtra.gov.in/esearch/",
                    page_title="IGR Maharashtra - Public Data & Registered Document Verification",
                    last_scraped_at="2026-09-25T11:30:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Stamp Act 1958 Section 30"
                )
            ),
            TaskStep(
                id="mah-biz-3",
                task_id="task-mah-small-biz",
                step_number=3,
                title="Maharashtra Gumasta License / Form A Intimation (LMS MahaOnline)",
                description="Statutory registration under Maharashtra Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2017. For 0-9 employees: Form A Intimation (Zero Statutory Fee, instant deemed receipt); for 10+ employees: Form F Registration Certificate.",
                department=dept_mah_labour,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=1,
                fee_amount=0.0,
                fee_breakdown={"Zero Fee for <10 Workers (Form A)": 0.0, "MahaOnline Form F Scrutiny (>=10 Workers)": 650.0},
                prerequisites=["mah-biz-1", "mah-biz-2"],
                documents=[
                    DocumentRequirement(id="doc-shop-photo", name="Photo of Shop / Establishment with Signboard", description="Clear photo showing front facade of shop with signboard in Marathi (Devanagari script)", is_mandatory=True, category="Premise Proof"),
                    DocumentRequirement(id="doc-aadhaar-biz", name="Applicant Self-Certified KYC & Passport Photo", description="High-resolution digital scan", is_mandatory=True, category="Identity Proof", is_alternative_group=True, group_name="Applicant Identity (Any 1)", alternative_options=["Aadhaar Card", "Voter ID Card", "Passport", "Driving License"])
                ],
                forms=[
                    FormRequirement(form_code="Form A (Intimation)", title="Intimation of Establishment (0-9 Employees)", fill_online_url="https://lms.mahaonline.gov.in", offline_fallback_url="/static/forms/form_a_gumasta.pdf"),
                    FormRequirement(form_code="Form F (Registration)", title="Application for Registration (10+ Employees)", fill_online_url="https://lms.mahaonline.gov.in")
                ],
                verification_source=VerificationSource(
                    url="https://lms.mahaonline.gov.in/",
                    page_title="Maharashtra Labour Management System - Citizen Charter",
                    last_scraped_at="2026-09-26T14:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Act No. LXI of 2017 (Shops & Establishments)"
                ),
                tips_and_pitfalls="Under the 2017 amended Act, establishments with 0-9 workers do not need periodic renewal; Form A intimation is valid perpetually.",
                anti_tout_advisory="Do not pay middlemen ₹3,000-₹5,000 for Gumasta. Form A for under 10 employees is 100% free of charge on LMS MahaOnline."
            ),
            TaskStep(
                id="mah-biz-4",
                task_id="task-mah-small-biz",
                step_number=4,
                title="Maharashtra Professional Tax (PTEC & PTRC Enrollment via MahaGST)",
                description="Statutory registration under the Maharashtra State Tax on Professions, Trades, Callings and Employments Act, 1975. PTEC is mandatory for the business entity; PTRC is mandatory if hiring salaried employees.",
                department=dept_mahagst,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=2,
                fee_amount=2500.0,
                fee_breakdown={"Annual PTEC Statutory Tax Rate": 2500.0, "Portal Enrollment Fee": 0.0},
                prerequisites=["mah-biz-1", "mah-biz-3"],
                documents=[
                    DocumentRequirement(id="doc-ptec-pan", name="Entity PAN Card & Gumasta Intimation", description="Mandatory for linking PT tax account", is_mandatory=True, category="Tax Identity"),
                    DocumentRequirement(id="doc-bank-proof", name="Cancelled Cheque or Bank Passbook Front Page", description="Showing IFSC and account number", is_mandatory=True, category="Banking")
                ],
                forms=[FormRequirement(form_code="Form II (PTEC)", title="Application for Certificate of Enrolment under PT Act", fill_online_url="https://mahagst.gov.in/en/e-services/pt-services")],
                verification_source=VerificationSource(
                    url="https://mahagst.gov.in/en/e-services/pt-services",
                    page_title="MahaGST - Professional Tax Registration Guidelines",
                    last_scraped_at="2026-09-25T16:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra State Tax on Professions Act 1975 Section 5"
                ),
                tips_and_pitfalls="PTEC must be paid annually before June 30 to avoid 1.25% monthly statutory interest penalty."
            ),
            TaskStep(
                id="mah-biz-5",
                task_id="task-mah-small-biz",
                step_number=5,
                title="Municipal Signboard Permission & Marathi Devanagari Prominence Clearance",
                description="Statutory authorization for outdoor business nameboard pursuant to Maharashtra Municipal rules and BMC Section 328. The name of the establishment in Marathi (Devanagari script) must be in front and in lettering font no smaller than any other language.",
                department=dept_mcgm_estate,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=1200.0,
                fee_breakdown={"Nameboard Scrutiny Fee": 800.0, "Administrative Processing": 400.0},
                prerequisites=["mah-biz-3"],
                documents=[
                    DocumentRequirement(id="doc-board-layout", name="Color Elevation & Signboard Artwork Layout", description="Specifying dimensions and verified Marathi Devanagari lettering font ratio", is_mandatory=True, category="Layout & Graphics"),
                    DocumentRequirement(id="doc-loc-photo", name="Facade Photo of Shop Building", description="Showing proposed mounting location", is_mandatory=True, category="Site Proof")
                ],
                forms=[FormRequirement(form_code="MMC-SEC-328", title="Application for External Signage / Nameboard", fill_online_url="https://portal.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlsignboard",
                    page_title="BMC Guidelines for Display of Business Signboards & Marathi Mandate",
                    last_scraped_at="2026-09-24T12:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Shops & Establishments (Amendment) Act 2022 Section 35"
                ),
                tips_and_pitfalls="Violating the Marathi Devanagari signboard mandate attracts immediate penalty of ₹2,000 per day under municipal spot inspection notices."
            ),
            TaskStep(
                id="mah-biz-6",
                task_id="task-mah-small-biz",
                step_number=6,
                title="Commercial Current Bank Account & E-Payment Merchant Integration",
                description="Open business current account with authorized scheduled commercial bank in Maharashtra using verified Udyam, Gumasta Form A/F, and PAN.",
                department=DepartmentInfo(id="dept-banking", name="Reserve Bank of India & Scheduled Commercial Banks", jurisdiction="Maharashtra & Nationwide", office_address="Commercial Bank Branch", portal_url="https://rbi.org.in"),
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=2,
                fee_amount=0.0,
                fee_breakdown={"Zero Account Opening Fee": 0.0},
                prerequisites=["mah-biz-1", "mah-biz-3", "mah-biz-4"],
                documents=[
                    DocumentRequirement(id="doc-full-dossier", name="Consolidated Civic Dossier (Gumasta + Udyam + PAN + PTEC)", description="Complete verified regulatory bundle", is_mandatory=True, category="Banking KYC")
                ],
                forms=[],
                verification_source=VerificationSource(
                    url="https://rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=9861",
                    page_title="RBI Master Direction - KYC Guidelines for Commercial Business Accounts",
                    last_scraped_at="2026-09-25T09:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                )
            )
        ]

        task_small_biz = CivicTask(
            id="task-mah-small-biz",
            title="Register a Small Business or Retail Enterprise (Maharashtra Gumasta & Shops Act)",
            category="Business & Commercial",
            municipality="Mumbai & Maharashtra Statewide (LMS / Aaple Sarkar)",
            state="Maharashtra",
            description="Complete statutory multi-agency procedure to lawfully register, incorporate, and open a small business, retail store, consultancy, or commercial establishment in Maharashtra under the Maharashtra Shops & Establishments Act 2017, Udyam MSME, MahaGST, and Municipal Signage regulations.",
            tags=["small business", "register a small business", "gumasta", "shop act license", "lms mahaonline", "aaple sarkar", "mumbai", "pune", "thane", "navi mumbai", "maharashtra", "retail shop", "business registration", "dukan"],
            steps=task_small_biz_steps
        )
        self._tasks[task_small_biz.id] = task_small_biz

        # -------------------------------------------------------------------------
        # TASK 2: Commercial Bakery & Food Service (Mumbai MCGM / BMC)
        # Flagship Stitch Screen Route #MCGM-EODB-2024-8842
        # -------------------------------------------------------------------------
        task_bakery_steps = [
            TaskStep(
                id="stop-01",
                task_id="task-mum-bakery",
                step_number=1,
                title="MCA Incorporation, RoC Mumbai & Entity PAN",
                description="Secure statutory corporate legal entity identity via Ministry of Corporate Affairs SPICe+ single window system and obtain permanent Income Tax PAN & TAN mapped to Maharashtra state tax jurisdiction.",
                department=dept_mca_mum,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=4,
                fee_amount=1000.0,
                fee_breakdown={"RoC Name Reservation (RUN)": 1000.0, "SPICe+ Incorporation Fee": 0.0, "MCA Portal Stamp Duty": 0.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-dir-kyc", name="Directors KYC & Digital Signature (DSC Class III)", description="Self-attested Aadhaar, PAN card, and DSC token of designated directors", is_mandatory=True, category="Corporate Identity"),
                    DocumentRequirement(id="doc-moa-aoa", name="Draft Memorandum & Articles of Association (e-MOA/AOA)", description="Stating commercial baking, cafe operations, and retail confectionery trade as primary object clause", is_mandatory=True, category="Legal Governance")
                ],
                forms=[FormRequirement(form_code="SPICe+ (INC-32)", title="Simplified Proforma for Incorporating Company Electronically Plus", fill_online_url="https://www.mca.gov.in")],
                verification_source=VerificationSource(
                    url="https://www.mca.gov.in/content/mca/global/en/home.html",
                    page_title="Ministry of Corporate Affairs - SPICe+ Integration Handbook",
                    last_scraped_at="2026-09-24T08:30:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Companies Act 2013 Section 7"
                ),
                tips_and_pitfalls="Ensure your designated primary business object strictly covers food manufacturing, baking, and sit-down cafe seating.",
                anti_tout_advisory="SPICe+ is a unified central government portal. Zero government fee for incorporation up to ₹15 Lakh authorized capital."
            ),
            TaskStep(
                id="stop-02",
                task_id="task-mum-bakery",
                step_number=2,
                title="Commercial Lease Registration & Gumasta License (Ward H/West)",
                description="Register commercial tenancy lease deed at Sub-Registrar Office, verify BMC property tax SAC number, and obtain Maharashtra Shops & Establishments Registration (Gumasta) via Aaple Sarkar / LMS.",
                department=dept_mcgm_labour,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=7,
                fee_amount=3400.0,
                fee_breakdown={"Sub-Registrar Registration Fee": 1000.0, "BMC Gumasta Inspection & Application Fee": 2400.0},
                prerequisites=["stop-01"],
                documents=[
                    DocumentRequirement(id="doc-reg-lease", name="Registered Commercial Lease Deed", description="Minimum 3-year registered lease deed with stamp duty payment challan", is_mandatory=True, category="Premise Title"),
                    DocumentRequirement(id="doc-sac-receipt", name="BMC Property Tax Last Paid Receipt (SAC No.)", description="Showing nil tax arrears and commercial property assessment classification", is_mandatory=True, category="Municipal Revenue"),
                    DocumentRequirement(id="doc-owner-noc-bakery", name="Building Cooperative Society (CHS) No Objection Certificate", description="Unconditional resolution permitting commercial kitchen and bakery operations", is_mandatory=True, category="Premises Clearance")
                ],
                forms=[FormRequirement(form_code="Form F / Form A", title="Application for Registration of Shops & Establishments", fill_online_url="https://lms.mahaonline.gov.in")],
                verification_source=VerificationSource(
                    url="https://lms.mahaonline.gov.in/",
                    page_title="Maharashtra Labour Dept - Shops & Establishments Portal",
                    last_scraped_at="2026-09-23T14:15:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Shops & Establishments Act 2017 Section 6"
                ),
                tips_and_pitfalls="Verify that the premise has sanctioned commercial user status under BMC Development Control & Promotion Regulations (DCPR-2034)."
            ),
            TaskStep(
                id="stop-03",
                task_id="task-mum-bakery",
                step_number=3,
                title="Mumbai Fire Brigade (MFB) Fire Safety Inspection NOC",
                description="Mandatory fire safety audit and compliance clearance from Mumbai Fire Brigade Headquarters under Maharashtra Fire Prevention and Life Safety Measures Act, 2006 for baking ovens, gas pipelines, and emergency egress.",
                department=dept_mfb,
                submission_mode=SubmissionMode.IN_PERSON,
                estimated_days=14,
                fee_amount=12500.0,
                fee_breakdown={"MFB Fire Scrutiny Fee": 7500.0, "Fire Equipment Inspection Levy": 5000.0},
                prerequisites=["stop-02"],
                documents=[
                    DocumentRequirement(id="doc-fire-plan", name="Architectural Kitchen & Seating Fire Evacuation Plan", description="Scale 1:100 layout detailing fire exits, smoke extraction, and extinguisher points signed by Licensed Fire Consultant", is_mandatory=True, category="Safety Engineering"),
                    DocumentRequirement(id="doc-gas-noc", name="LPG / PNG Gas Pipeline Installation Certificate", description="Certificate from approved authorized gas provider certifying kitchen piping safety and shut-off valves", is_mandatory=True, category="Utility Safety")
                ],
                forms=[FormRequirement(form_code="MFB-NOC-APP-1", title="Application for Fire Safety Verification & Final NOC", fill_online_url="https://portal.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlfirenoc",
                    page_title="Mumbai Fire Brigade - Standard Operating Procedures for Food Establishments",
                    last_scraped_at="2026-09-24T11:45:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Fire Prevention & Life Safety Act 2006"
                ),
                tips_and_pitfalls="Emergency egress doors must open outwards and remain unlocked during all working hours; failure results in immediate rejection of MFB NOC.",
                is_critical_path=True
            ),
            TaskStep(
                id="stop-03a",
                task_id="task-mum-bakery",
                step_number=4,
                title="FSSAI State Food License (FoSCoS Maharashtra)",
                description="State food safety manufacturing and food service license issued by Food Safety and Standards Authority of India (FSSAI) Western Regional Office / Maharashtra FDA.",
                department=dept_fssai_mum,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=15,
                fee_amount=7500.0,
                fee_breakdown={"FSSAI State License Annual Fee": 5000.0, "Food Testing & Sampling Deposit": 2500.0},
                prerequisites=["stop-02", "stop-03"],
                documents=[
                    DocumentRequirement(id="doc-fsms", name="Food Safety Management System (FSMS) Plan & SOP", description="Documented hygiene protocols, pest control contract, and Hazard Analysis Critical Control Point (HACCP) layout", is_mandatory=True, category="Food Hygiene"),
                    DocumentRequirement(id="doc-water-test", name="Potable Water Test Microbiological Analysis Report", description="Chemical and bacterial potability report from NABL-accredited laboratory for kitchen water", is_mandatory=True, category="Quality Testing"),
                    DocumentRequirement(id="doc-med-fit", name="Food Handler Medical Fitness Certificates (Form IX)", description="Medical fitness certification for all bakery chefs and kitchen staff", is_mandatory=True, category="Staff Health")
                ],
                forms=[FormRequirement(form_code="FSSAI Form B", title="Application for State Food License under FSS Act", fill_online_url="https://foscos.fssai.gov.in")],
                verification_source=VerificationSource(
                    url="https://foscos.fssai.gov.in/userguide",
                    page_title="FSSAI FoSCoS - State Licensing Standard Operating Procedures",
                    last_scraped_at="2026-09-25T16:20:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Food Safety and Standards (Licensing and Registration of Food Businesses) Regulations, 2011"
                ),
                tips_and_pitfalls="Potable water test report must not be older than 30 calendar days at time of FoSCoS filing."
            ),
            TaskStep(
                id="stop-03b",
                task_id="task-mum-bakery",
                step_number=5,
                title="MPCB Green Category Consent to Establish & Operate (CTE/CTO)",
                description="Statutory environmental clearance for commercial bakery, oven ventilation, and effluent discharge under the Water and Air (Prevention & Control of Pollution) Acts from Maharashtra Pollution Control Board.",
                department=dept_mpcb,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=12,
                fee_amount=10000.0,
                fee_breakdown={"Consent to Establish (CTE) Scrutiny Fee": 5000.0, "Consent to Operate (CTO) 5-Year Fee": 5000.0},
                prerequisites=["stop-02", "stop-03"],
                documents=[
                    DocumentRequirement(id="doc-grease-trap", name="Grease Trap & Kitchen Exhaust Blueprint", description="Engineering diagram showing grease interceptor on kitchen wastewater line and chimney flue height", is_mandatory=True, category="Environmental Engineering"),
                    DocumentRequirement(id="doc-mpcb-chart", name="Baking Process Flowchart & Raw Material Matrix", description="Itemized consumption of flour, sugar, butter, power, and estimated daily organic solid waste generation", is_mandatory=True, category="Process Audit")
                ],
                forms=[FormRequirement(form_code="MPCB-Form-I", title="Combined Application for CTE & CTO under Water & Air Acts", fill_online_url="https://mpcb.gov.in")],
                verification_source=VerificationSource(
                    url="https://mpcb.gov.in/node/69",
                    page_title="MPCB Comprehensive Categorization of Industries - Bakeries & Confectioneries (Green Category)",
                    last_scraped_at="2026-09-22T09:10:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Pollution Control Board Notification MPCB/JD(WPC)/B-190328-FTS-0012"
                ),
                tips_and_pitfalls="Commercial ovens with power load exceeding 10 HP must connect to grease traps before discharging kitchen waste to municipal sewers."
            ),
            TaskStep(
                id="stop-04",
                task_id="task-mum-bakery",
                step_number=6,
                title="MCGM Section 394 Health Trade License (MOH Ward H/West)",
                description="Core municipal trade permit to operate an eating house and food preparation establishment in Greater Mumbai pursuant to Section 394 of the Mumbai Municipal Corporation Act (MMC Act 1888).",
                department=dept_mcgm_health,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=10,
                fee_amount=14000.0,
                fee_breakdown={"Section 394 Health License Scheduled Fee": 8500.0, "Trade Refuse Charges (TRC) Annual": 4000.0, "PCO Rat Proofing & Sanitation Inspection Fee": 1500.0},
                prerequisites=["stop-03", "stop-03a", "stop-03b"],
                documents=[
                    DocumentRequirement(id="doc-moh-dossier", name="Consolidated Inter-Agency Clearances Bundle", description="Verified MFB Fire NOC, FSSAI State Food License, and MPCB Consent certificates", is_mandatory=True, category="Statutory Clearances"),
                    DocumentRequirement(id="doc-pco-cert", name="MCGM Pest Control Officer (PCO) Certificate", description="Rat proofing and vector control compliance certificate issued by Ward H/West PCO", is_mandatory=True, category="Public Sanitation"),
                    DocumentRequirement(id="doc-water-sanction", name="MCGM Municipal Water Connection Sanction Card", description="Sanctioned water meter number under Section 140 MMC Act", is_mandatory=True, category="Utilities")
                ],
                forms=[FormRequirement(form_code="MMC Form 394", title="Application for Grant of Health License under Section 394 MMC Act", fill_online_url="https://portal.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlhealthlicense",
                    page_title="MCGM Public Health Department - Citizen Charter for Health Licenses",
                    last_scraped_at="2026-09-25T13:30:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Mumbai Municipal Corporation Act 1888 Section 394 Schedule M"
                ),
                tips_and_pitfalls="Premises must have minimum 10-foot ceiling clearance in bakery production area and washable ceramic wall tiles up to 7 feet.",
                is_critical_path=True
            ),
            TaskStep(
                id="stop-05",
                task_id="task-mum-bakery",
                step_number=7,
                title="Outdoor Dining Permission & Devanagari Signage Clearance (Ward H/West)",
                description="Secure outdoor seating / sidewalk cafe permission under MCGM Open-to-Sky Dining Policy and statutory nameboard authorization with prominent Marathi Devanagari lettering.",
                department=dept_mcgm_estate,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=7,
                fee_amount=4000.0,
                fee_breakdown={"Outdoor Seating Annual User Fee": 2500.0, "Devanagari Signage Scrutiny Fee": 1500.0},
                prerequisites=["stop-04"],
                documents=[
                    DocumentRequirement(id="doc-outdoor-plan", name="Outdoor Seating Boundary & Pedestrian Clearance Plan", description="Scale diagram demonstrating 2.5-meter unobstructed pedestrian sidewalk passage", is_mandatory=True, category="Urban Planning"),
                    DocumentRequirement(id="doc-signage-marathi", name="Signboard Graphic Layout with Devanagari Font Prominence", description="Demonstrating compliance with Maharashtra Shops & Establishments Amendment Act 2022", is_mandatory=True, category="Signage Compliance")
                ],
                forms=[FormRequirement(form_code="MCGM-OTS-2024", title="Application for Outdoor Customer Seating & Signage", fill_online_url="https://portal.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlrooftopdining",
                    page_title="BMC Policy Guidelines for Outdoor Food Seating & Commercial Signage",
                    last_scraped_at="2026-09-24T17:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="MCGM Circular No. CHE/DP/3241/Gen (Outdoor Dining)"
                ),
                tips_and_pitfalls="Permanent structural roofing or glass enclosures over outdoor seating are strictly prohibited; only removable fabric awnings are allowed."
            )
        ]

        task_bakery = CivicTask(
            id="task-mum-bakery",
            title="Register & Commission a Commercial Bakery in Bandra, Mumbai",
            category="Food & Hospitality",
            municipality="Mumbai (MCGM / BMC)",
            state="Maharashtra",
            description="Statutory pathway governing commercial bakery establishment with eating house authorization across MCGM Ward H/West, Mumbai Fire Brigade (MFB), FSSAI FoSCoS, and Maharashtra Pollution Control Board (MPCB) pursuant to Section 394 MMC Act 1888.",
            tags=["commercial bakery", "cafe", "food service", "mcgm", "bmc", "mumbai", "bandra west", "ward h/west", "section 394", "mmc act 1888", "fssai", "foscos", "gumasta", "mfb fire noc", "mpcb", "aaple sarkar"],
            steps=task_bakery_steps
        )
        self._tasks[task_bakery.id] = task_bakery

        # -------------------------------------------------------------------------
        # TASK 3: Open a Restaurant, Cafe or Food Outlet in Pune (PMC)
        # Major Maharashtra Metropolitan City
        # -------------------------------------------------------------------------
        task_pune_steps = [
            TaskStep(
                id="pune-food-1",
                task_id="task-pune-restaurant",
                step_number=1,
                title="Business Incorporation & PMC Gumasta Intimation",
                description="Complete legal entity creation and obtain Pune Municipal Corporation (PMC) Shops & Establishments Intimation / Registration via Maharashtra LMS portal.",
                department=dept_mah_labour,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=650.0,
                fee_breakdown={"LMS Registration Fee": 500.0, "Portal Charges": 150.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-pune-kyc", name="Proprietor / Partners KYC & PAN", description="Aadhaar and PAN of business owners", is_mandatory=True, category="Identity"),
                    DocumentRequirement(id="doc-pune-lease", name="Registered Commercial Lease Deed in Pune", description="Registered with Sub-Registrar Pune", is_mandatory=True, category="Premises")
                ],
                forms=[FormRequirement(form_code="Form A / Form F", title="PMC Gumasta Registration Form", fill_online_url="https://lms.mahaonline.gov.in")],
                verification_source=VerificationSource(
                    url="https://pmc.gov.in/en/shops-and-establishments",
                    page_title="Pune Municipal Corporation - Shops and Establishments Section",
                    last_scraped_at="2026-09-24T10:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Municipal Corporations Act Section 376"
                )
            ),
            TaskStep(
                id="pune-food-2",
                task_id="task-pune-restaurant",
                step_number=2,
                title="PMC Property Tax Khata & No Arrears Certificate",
                description="Verify property tax account on PMC Ptis portal and obtain No Dues Certificate for commercial premises.",
                department=dept_pmc_health,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=2,
                fee_amount=0.0,
                fee_breakdown={"Zero Arrears Clearance Fee": 0.0},
                prerequisites=["pune-food-1"],
                documents=[
                    DocumentRequirement(id="doc-pmc-tax", name="Last Paid PMC Property Tax Receipt", description="Showing zero tax dues for current financial year", is_mandatory=True, category="Property Tax")
                ],
                forms=[FormRequirement(form_code="PMC-NDC", title="Property Tax Clearance Application", fill_online_url="https://pmc.gov.in/ptis")],
                verification_source=VerificationSource(
                    url="https://pmc.gov.in/en/property-tax",
                    page_title="PMC Property Tax Assessment & Collection",
                    last_scraped_at="2026-09-25T12:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="pune-food-3",
                task_id="task-pune-restaurant",
                step_number=3,
                title="Pune Central Fire Brigade NOC (New Timber Market HQ)",
                description="Fire safety audit and inspection for commercial kitchen, gas piping, and seating exits by Pune Municipal Corporation Fire Department.",
                department=dept_pmc_fire,
                submission_mode=SubmissionMode.IN_PERSON,
                estimated_days=12,
                fee_amount=8500.0,
                fee_breakdown={"PMC Fire Scrutiny Fee": 5500.0, "Inspection & Safety Levy": 3000.0},
                prerequisites=["pune-food-2"],
                documents=[
                    DocumentRequirement(id="doc-pune-fireplan", name="Architect Fire Escape Blueprint", description="Approved by certified PMC fire architect", is_mandatory=True, category="Fire Safety")
                ],
                forms=[FormRequirement(form_code="PMC-FIRE-01", title="Application for Commercial Kitchen Fire NOC", fill_online_url="https://pmc.gov.in")],
                verification_source=VerificationSource(
                    url="https://pmc.gov.in/en/fire-department",
                    page_title="PMC Fire Department - Fire Safety Inspection Guidelines",
                    last_scraped_at="2026-09-25T14:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Fire Prevention and Life Safety Measures Act 2006"
                ),
                is_critical_path=True
            ),
            TaskStep(
                id="pune-food-4",
                task_id="task-pune-restaurant",
                step_number=4,
                title="FSSAI Maharashtra State Food License & MPCB Consent",
                description="Obtain Food Safety license from FoSCoS Maharashtra FDA and Green Category pollution consent from MPCB Pune Regional Office.",
                department=dept_fssai_mum,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=14,
                fee_amount=12500.0,
                fee_breakdown={"FSSAI State License": 7500.0, "MPCB Consent Fee": 5000.0},
                prerequisites=["pune-food-2", "pune-food-3"],
                documents=[
                    DocumentRequirement(id="doc-pune-water", name="NABL Potable Water Testing Report", description="Authorized bacteriological and chemical test report", is_mandatory=True, category="Food Safety"),
                    DocumentRequirement(id="doc-pune-etp", name="Grease Trap Installation Scheme", description="Effluent mitigation scheme for commercial kitchen sink", is_mandatory=True, category="Pollution")
                ],
                forms=[FormRequirement(form_code="FSSAI Form B", title="State Food License Application", fill_online_url="https://foscos.fssai.gov.in")],
                verification_source=VerificationSource(
                    url="https://fda.maharashtra.gov.in",
                    page_title="FDA Maharashtra - Food Safety Administration",
                    last_scraped_at="2026-09-24T15:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="pune-food-5",
                task_id="task-pune-restaurant",
                step_number=5,
                title="PMC Health Department Trade / Eating House License",
                description="Final statutory license to operate an eating house and restaurant within Pune municipal limits pursuant to Section 376 of Maharashtra Municipal Corporations Act.",
                department=dept_pmc_health,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=10,
                fee_amount=10500.0,
                fee_breakdown={"PMC Trade License Fee": 7000.0, "Refuse Charges": 3500.0},
                prerequisites=["pune-food-3", "pune-food-4"],
                documents=[
                    DocumentRequirement(id="doc-pune-bundle", name="Verified Fire NOC & FSSAI License", description="Approved certificates bundle", is_mandatory=True, category="Statutory Clearances")
                ],
                forms=[FormRequirement(form_code="PMC-EAT-LIC", title="Application for Eating House License", fill_online_url="https://pmc.gov.in")],
                verification_source=VerificationSource(
                    url="https://pmc.gov.in/en/health-department",
                    page_title="PMC Citizen Charter - Health & Trade Licenses",
                    last_scraped_at="2026-09-26T11:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Municipal Corporations Act (Act LIX of 1949)"
                ),
                is_critical_path=True
            )
        ]

        task_pune = CivicTask(
            id="task-pune-restaurant",
            title="Open a Restaurant, Cafe or Food Outlet in Pune (PMC)",
            category="Food & Hospitality",
            municipality="Pune (PMC / PMRDA)",
            state="Maharashtra",
            description="Statutory municipal and state clearance pathway to commission an eating house or food delivery kitchen in Pune under the Maharashtra Municipal Corporations Act, PMC Health Department, and PMRDA.",
            tags=["restaurant", "cafe", "food business", "pune", "pmc", "pmrda", "trade license", "fssai", "gumasta", "fire noc", "maharashtra"],
            steps=task_pune_steps
        )
        self._tasks[task_pune.id] = task_pune

        # -------------------------------------------------------------------------
        # TASK 4: Commercial & Residential Building Plan Sanction (AutoDCR BMC)
        # Infrastructure & Urban Development in Maharashtra
        # -------------------------------------------------------------------------
        task_construction_steps = [
            TaskStep(
                id="mum-bp-1",
                task_id="task-mum-construction",
                step_number=1,
                title="Property Card, CTS Plan & IGR Title Clearance",
                description="Extract verified digital Property Card (PR Card) from City Survey Office (CTSO), extract CTS plan, and clear 30-year non-encumbrance on IGR Maharashtra.",
                department=dept_mahabhumi,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=1500.0,
                fee_breakdown={"Digital PR Card Fee": 500.0, "IGR E-Search Non-Encumbrance": 1000.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-pr-card", name="Certified Digital Property Card (PR Card)", description="Showing current CTS number, area in sq. meters, and registered holder names", is_mandatory=True, category="Land Title"),
                    DocumentRequirement(id="doc-cts-sheet", name="Demarcated CTS Sheet from Superintendent of Land Records", description="Authenticated land boundary coordinates", is_mandatory=True, category="Survey Map")
                ],
                forms=[FormRequirement(form_code="PR-CARD-ONLINE", title="Digital Property Card Download", fill_online_url="https://mahabhumi.gov.in/mahabhumilink/")],
                verification_source=VerificationSource(
                    url="https://mahabhumi.gov.in/mahabhumilink/",
                    page_title="MahaBhumi - Digital Land Records & Property Cards",
                    last_scraped_at="2026-09-24T16:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Land Revenue Code 1966 Section 148"
                )
            ),
            TaskStep(
                id="mum-bp-2",
                task_id="task-mum-construction",
                step_number=2,
                title="Architectural AutoDCR Plan Submission & Intimation of Disapproval (IOD)",
                description="Licensed architect submits standardized CAD blueprints on BMC AutoDCR portal to evaluate FSI, road widening reservations, and generate statutory IOD conditions.",
                department=dept_mcgm_bp,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=21,
                fee_amount=45000.0,
                fee_breakdown={"AutoDCR Scrutiny Fee": 25000.0, "Development Cess": 20000.0},
                prerequisites=["mum-bp-1"],
                documents=[
                    DocumentRequirement(id="doc-cad-drawings", name="AutoDCR Pre-Checked Architectural CAD Plans", description="Pre-validated by AutoDCR scrutiny software conforming to DCPR-2034 rules", is_mandatory=True, category="Building Plans"),
                    DocumentRequirement(id="doc-super-arch", name="Architect & Structural Engineer Supervision Undertaking", description="Form of supervision under Section 342 MMC Act", is_mandatory=True, category="Professional Undertakings")
                ],
                forms=[FormRequirement(form_code="AutoDCR Form A", title="Application for Development Permission & Building Sanction", fill_online_url="https://autodcr.mcgm.gov.in/bpams/")],
                verification_source=VerificationSource(
                    url="https://autodcr.mcgm.gov.in/bpams/",
                    page_title="BMC AutoDCR Portal - Ease of Doing Business Dashboard",
                    last_scraped_at="2026-09-25T17:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="BMC DCPR-2034 Regulation 10"
                ),
                is_critical_path=True
            ),
            TaskStep(
                id="mum-bp-3",
                task_id="task-mum-construction",
                step_number=3,
                title="Integrated Statutory Clearances (CFO Fire NOC, Traffic & SWD)",
                description="Comply with pre-commencement IOD conditions by obtaining Chief Fire Officer NOC, Traffic Police clearance, and Storm Water Drain remarks.",
                department=dept_mfb,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=20,
                fee_amount=35000.0,
                fee_breakdown={"CFO Fire Scrutiny Premium": 25000.0, "SWD Storm Drain Scrutiny": 10000.0},
                prerequisites=["mum-bp-2"],
                documents=[
                    DocumentRequirement(id="doc-fire-cfo-layout", name="Comprehensive Fire Fighting System Schematic", description="Wet riser, fire booster pump, and refuge floor calculations", is_mandatory=True, category="Fire Safety")
                ],
                forms=[],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlEODBOBPS",
                    page_title="BMC Single Window Clearances for Building Proposals",
                    last_scraped_at="2026-09-24T18:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mum-bp-4",
                task_id="task-mum-construction",
                step_number=4,
                title="Plinth Commencement Certificate (CC)",
                description="Executive Engineer (BP) inspects completed plinth foundation, verifies boundary setback offsets, and grants Commencement Certificate.",
                department=dept_mcgm_bp,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=10,
                fee_amount=15000.0,
                fee_breakdown={"Plinth Checking Inspection Fee": 15000.0},
                prerequisites=["mum-bp-2", "mum-bp-3"],
                documents=[
                    DocumentRequirement(id="doc-plinth-survey", name="Plinth Completion Certificate by Structural Engineer", description="Certifying foundation conforms to structural safety and earthquake resistant design", is_mandatory=True, category="Structural Integrity")
                ],
                forms=[FormRequirement(form_code="Appendix C", title="Notice of Completion of Plinth", fill_online_url="https://autodcr.mcgm.gov.in/bpams/", offline_fallback_url="/static/forms/cc_procedure.pdf")],
                verification_source=VerificationSource(
                    url="https://autodcr.mcgm.gov.in/bpams/",
                    page_title="BMC AutoDCR Guidelines - Grant of Commencement Certificate",
                    last_scraped_at="2026-09-23T11:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True
                ),
                is_critical_path=True
            ),
            TaskStep(
                id="mum-bp-5",
                task_id="task-mum-construction",
                step_number=5,
                title="Final Building Completion & Occupancy Certificate (OC)",
                description="Final joint municipal inspection following full building construction, lift inspection, water connection test, and issuance of Full Occupancy Certificate (OC).",
                department=dept_mcgm_bp,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=15,
                fee_amount=25000.0,
                fee_breakdown={"OC Inspection Fee": 15000.0, "Drainage Completion Assessment": 10000.0},
                prerequisites=["mum-bp-4"],
                documents=[
                    DocumentRequirement(id="doc-final-cfo", name="Final CFO Fire Operational NOC", description="Confirming functional fire hydrants and alarms", is_mandatory=True, category="Clearances"),
                    DocumentRequirement(id="doc-lift-lic", name="Maharashtra PWD Lift Inspector License", description="Safety operational license for passenger elevators", is_mandatory=True, category="Safety")
                ],
                forms=[FormRequirement(form_code="Appendix D", title="Completion Certificate & Notice of Completion", fill_online_url="https://autodcr.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qloccupancycertificate",
                    page_title="BMC Guidelines for Grant of Occupancy Certificate",
                    last_scraped_at="2026-09-24T18:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                ),
                is_critical_path=True
            )
        ]

        task_construction = CivicTask(
            id="task-mum-construction",
            title="Commercial Building Plan Sanction & Occupancy (OC)",
            category="Construction & Real Estate",
            municipality="Mumbai (BMC / MCGM)",
            state="Maharashtra",
            description="Comprehensive municipal clearance path to obtain Building Plan Sanction, IOD, Plinth Commencement Certificate (CC), and Occupancy Certificate (OC) under BMC DCPR-2034.",
            tags=["building permit", "construction", "autodcr", "iod", "commencement certificate", "occupancy certificate", "bmc", "mumbai", "dcpr-2034", "maharashtra"],
            steps=task_construction_steps
        )
        self._tasks[task_construction.id] = task_construction

        # -------------------------------------------------------------------------
        # TASK 5: Land 7/12 (Satbara) Mutation & Title Transfer (MahaBhumi / E-Ferfar)
        # Critical Maharashtra Land & Revenue Process
        # -------------------------------------------------------------------------
        task_mutation_steps = [
            TaskStep(
                id="mah-mut-1",
                task_id="task-mah-712-mutation",
                step_number=1,
                title="Registered Title Deed & IGR Index-II Verification",
                description="Verify official registered sale deed, gift deed, or partition deed on IGR Maharashtra E-Search to extract volume, document number, and stamp duty paid.",
                department=dept_igr,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=2,
                fee_amount=300.0,
                fee_breakdown={"E-Search Inspection Fee": 300.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-reg-deed", name="Registered Conveyance / Sale Deed Copy", description="With Sub-Registrar stamp and volume number", is_mandatory=True, category="Title Deed"),
                    DocumentRequirement(id="doc-index-ii", name="Certified Index II from IGR Portal", description="Showing transaction summary and consideration", is_mandatory=True, category="Title Deed")
                ],
                forms=[FormRequirement(form_code="IGR-INDEX-II", title="Certified Copy of Book No. 1 Index II", fill_online_url="https://esearchigr.maharashtra.gov.in/esearch/")],
                verification_source=VerificationSource(
                    url="https://esearchigr.maharashtra.gov.in/esearch/",
                    page_title="IGR Maharashtra - Online Registered Document Verification",
                    last_scraped_at="2026-09-25T10:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Registration Act 1908 Section 51"
                )
            ),
            TaskStep(
                id="mah-mut-2",
                task_id="task-mah-712-mutation",
                step_number=2,
                title="E-Ferfar (Online Mutation) Filing on MahaBhumi E-Hakk Portal",
                description="Citizen submits mutation entry request on Maharashtra Government E-Hakk portal under Section 149 of the Maharashtra Land Revenue Code 1966.",
                department=dept_mahabhumi,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=150.0,
                fee_breakdown={"E-Hakk Application Processing Fee": 150.0},
                prerequisites=["mah-mut-1"],
                documents=[
                    DocumentRequirement(id="doc-curr-712", name="Current Digital 7/12 (Satbara) & 8A Extract", description="Showing current seller/transferor name in Gaon Namuna 7", is_mandatory=True, category="Land Record"),
                    DocumentRequirement(id="doc-aadhaar-buyer", name="Aadhaar Cards of All New Purchasers / Heirs", description="For recording legal names in land records", is_mandatory=True, category="Identity")
                ],
                forms=[FormRequirement(form_code="E-Hakk-Form-149", title="Application for E-Ferfar Mutation Entry", fill_online_url="https://pune.mahabhumi.gov.in/ehakk/", offline_fallback_url="/static/forms/form_8_mutation.pdf")],
                verification_source=VerificationSource(
                    url="https://mahabhumi.gov.in/mahabhumilink/",
                    page_title="MahaBhumi - E-Ferfar Citizen Portal Guidelines",
                    last_scraped_at="2026-09-26T12:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Land Revenue Code 1966 Section 149"
                ),
                tips_and_pitfalls="Enter the exact Sub-Registrar Office SRO code and document year so the system fetches the deed automatically via API."
            ),
            TaskStep(
                id="mah-mut-3",
                task_id="task-mah-712-mutation",
                step_number=3,
                title="Statutory Notice Issuance under Section 150 (15-Day Public Objection)",
                description="Talathi issues statutory notice to all interested parties, legal heirs, and co-owners listed in the 7/12 extract; 15-day mandatory public waiting window.",
                department=dept_mahabhumi,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=15,
                fee_amount=0.0,
                fee_breakdown={"Public Notice Mandate": 0.0},
                prerequisites=["mah-mut-2"],
                documents=[],
                forms=[FormRequirement(form_code="Notice-Sec-150", title="Public Notice of Property Record Transfer", fill_online_url="https://bhulekh.mahabhumi.gov.in")],
                verification_source=VerificationSource(
                    url="https://bhulekh.mahabhumi.gov.in",
                    page_title="MahaBhumi - Public Notices & E-Dispute Registry",
                    last_scraped_at="2026-09-25T08:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Land Revenue Code 1966 Section 150"
                ),
                is_critical_path=True
            ),
            TaskStep(
                id="mah-mut-4",
                task_id="task-mah-712-mutation",
                step_number=4,
                title="Talathi Field Inquiry & Verification Report",
                description="Talathi conducts on-site verification, confirms actual physical possession, checks agricultural/NA land classification, and submits verification report.",
                department=dept_mahabhumi,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=7,
                fee_amount=500.0,
                fee_breakdown={"Field Scrutiny Fee": 500.0},
                prerequisites=["mah-mut-3"],
                documents=[
                    DocumentRequirement(id="doc-possession-receipt", name="Affidavit of Uncontested Possession", description="Affirming undisturbed boundary and physical possession", is_mandatory=True, category="Possession")
                ],
                forms=[],
                verification_source=VerificationSource(
                    url="https://mahabhumi.gov.in",
                    page_title="MahaBhumi - Revenue Officer Inspection Standards",
                    last_scraped_at="2026-09-24T14:00:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mah-mut-5",
                task_id="task-mah-712-mutation",
                step_number=5,
                title="Circle Officer / Tehsildar Approval & Digital 7/12 Satbara Issuance",
                description="Circle Officer certifies the Ferfar entry with digital signature; title is formally updated in the live Mahabhumi registry and digitally signed 7/12 & 8A is generated.",
                department=dept_mahabhumi,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=4,
                fee_amount=15.0,
                fee_breakdown={"Certified Digital 7/12 Download Fee": 15.0},
                prerequisites=["mah-mut-4"],
                documents=[],
                forms=[FormRequirement(form_code="DIGI-712", title="Digitally Signed 7/12 & 8A Extract", fill_online_url="https://digitalsatbara.mahabhumi.gov.in")],
                verification_source=VerificationSource(
                    url="https://digitalsatbara.mahabhumi.gov.in",
                    page_title="MahaBhumi - Digital Satbara Download & Verification Portal",
                    last_scraped_at="2026-09-26T15:00:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Right to Public Services Act 2015"
                ),
                is_critical_path=True
            )
        ]

        task_mutation = CivicTask(
            id="task-mah-712-mutation",
            title="Agricultural & Land 7/12 (Satbara) Mutation & Title Transfer",
            category="Property & Land Records",
            municipality="Maharashtra Statewide (Revenue & Forest Dept / MahaBhumi)",
            state="Maharashtra",
            description="Statutory online process for E-Ferfar (Mutation), entry of rights in 7/12 Extract, Village Form 6, and Property Card under Maharashtra Land Revenue Code (MLRC 1966) via MahaBhumi and IGR Maharashtra.",
            tags=["7/12", "satbara", "ferfar", "mutation", "mahabhumi", "land records", "bhulekh", "e-hakk", "igr maharashtra", "pune", "mumbai", "nagpur", "nashik"],
            steps=task_mutation_steps
        )
        self._tasks[task_mutation.id] = task_mutation

        # -------------------------------------------------------------------------
        # TASK 6: New Commercial / Domestic Water Supply Connection (MCGM BMC)
        # Municipal Utility & Citizen Public Works
        # -------------------------------------------------------------------------
        task_water_steps = [
            TaskStep(
                id="mum-wat-1",
                task_id="task-mum-water-connection",
                step_number=1,
                title="MCGM Property Tax SAC & Building Plan Verification",
                description="Verify SAC (Section Applied Customer) number on BMC citizen portal and confirm sanction of internal plumbing design.",
                department=dept_mcgm_he,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=2,
                fee_amount=0.0,
                fee_breakdown={"SAC Scrutiny": 0.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(id="doc-water-sac", name="Current BMC Property Tax Paid Receipt (SAC)", description="Proof of lawful assessed municipal premise", is_mandatory=True, category="Revenue"),
                    DocumentRequirement(id="doc-bldg-sanction", name="Approved Building Proposal Sanction Plan", description="Sanction plan showing water storage overhead and underground tank sizes", is_mandatory=True, category="Building Plans")
                ],
                forms=[FormRequirement(form_code="BMC-WAT-01", title="Application for Fresh Municipal Water Supply", fill_online_url="https://portal.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlwaterconnection",
                    page_title="MCGM Hydraulic Engineer Department - Water Connection Guidelines",
                    last_scraped_at="2026-09-25T14:30:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Mumbai Municipal Corporation Act 1888 Section 140"
                )
            ),
            TaskStep(
                id="mum-wat-2",
                task_id="task-mum-water-connection",
                step_number=2,
                title="Licensed Plumber Layout & Online Filing (Aaple Sarkar / BMC)",
                description="Licensed BMC plumber submits hydraulic pipeline connection diagram and calculates required connection diameter (15mm to 100mm).",
                department=dept_mcgm_he,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=1500.0,
                fee_breakdown={"Water Scrutiny Fee": 1500.0},
                prerequisites=["mum-wat-1"],
                documents=[
                    DocumentRequirement(id="doc-plumber-cert", name="Licensed Plumber Undertaking & License Copy", description="Empaneled with Municipal Corporation of Greater Mumbai", is_mandatory=True, category="Professional Undertakings")
                ],
                forms=[FormRequirement(form_code="Form W-2", title="Plumber Certificate of Internal Water Fitting", fill_online_url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlservices")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlservices",
                    page_title="BMC Hydraulic Engineer Dept - Water Connection Forms",
                    last_scraped_at="2026-09-24T12:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                )
            ),
            TaskStep(
                id="mum-wat-3",
                task_id="task-mum-water-connection",
                step_number=3,
                title="Assistant Engineer (Water Works) Site Survey & Feasibility Inspection",
                description="Ward Assistant Engineer (Water Works) inspects street municipal water main line, pressure gradients, and approves connection tapping point.",
                department=dept_mcgm_he,
                submission_mode=SubmissionMode.IN_PERSON,
                estimated_days=7,
                fee_amount=2500.0,
                fee_breakdown={"Site Inspection Charge": 2500.0},
                prerequisites=["mum-wat-2"],
                documents=[],
                forms=[],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in",
                    page_title="BMC Water Works Field Inspection SLA",
                    last_scraped_at="2026-09-25T16:00:00Z",
                    confidence_score=0.97,
                    is_admin_verified=True
                ),
                is_critical_path=True
            ),
            TaskStep(
                id="mum-wat-4",
                task_id="task-mum-water-connection",
                step_number=4,
                title="Road Opening / Trenching Permission & Restoration Charges",
                description="Secure road opening permission from BMC Maintenance Department to trench road/sidewalk for laying pipeline; pay street reinstatement fee.",
                department=dept_mcgm_he,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=5,
                fee_amount=12000.0,
                fee_breakdown={"Road Reinstatement Deposit": 10000.0, "Trenching Permit Fee": 2000.0},
                prerequisites=["mum-wat-3"],
                documents=[
                    DocumentRequirement(id="doc-trench-plan", name="Trenching Route Map with Traffic Police NOC", description="If trenching along major arterial carriageway", is_mandatory=True, category="Traffic & Roads")
                ],
                forms=[FormRequirement(form_code="RoW-Trench-01", title="Right of Way Road Opening Permission", fill_online_url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlEODBWater")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in/irj/portal/anonymous/qlEODBWater",
                    page_title="BMC Road Opening & Trenching Policy",
                    last_scraped_at="2026-09-23T15:00:00Z",
                    confidence_score=0.98,
                    is_admin_verified=True
                ),
                is_critical_path=True
            ),
            TaskStep(
                id="mum-wat-5",
                task_id="task-mum-water-connection",
                step_number=5,
                title="Main Pipeline Tapping, Water Meter Calibration & Supply Activation",
                description="Municipal water works team taps water main, installs certified calibrated AMR/mechanical water meter, and releases water supply to premises.",
                department=dept_mcgm_he,
                submission_mode=SubmissionMode.IN_PERSON,
                estimated_days=5,
                fee_amount=8500.0,
                fee_breakdown={"Water Meter Security Deposit": 5000.0, "Tapping Execution Fee": 3500.0},
                prerequisites=["mum-wat-4"],
                documents=[
                    DocumentRequirement(id="doc-meter-calib", name="Government Approved Water Meter Calibration Certificate", description="Calibrated at BMC Water Meter Testing Lab, Dadar", is_mandatory=True, category="Equipment Test")
                ],
                forms=[FormRequirement(form_code="BMC-CAN-ORDER", title="Water Supply Release & Meter Connection Order", fill_online_url="https://portal.mcgm.gov.in")],
                verification_source=VerificationSource(
                    url="https://portal.mcgm.gov.in",
                    page_title="BMC Hydraulic Engineer Dept - Water Supply Release Order",
                    last_scraped_at="2026-09-26T17:00:00Z",
                    confidence_score=0.99,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Right to Public Services Act 2015"
                ),
                is_critical_path=True
            )
        ]

        task_water = CivicTask(
            id="task-mum-water-connection",
            title="New Commercial / Domestic Water Supply Connection (MCGM Hydraulic Dept)",
            category="Public Utilities & Water",
            municipality="Mumbai (MCGM / BMC)",
            state="Maharashtra",
            description="Statutory municipal pathway to secure fresh piped municipal water supply, road opening permission, water meter calibration, and drainage connection under Section 140 of the Mumbai Municipal Corporation Act.",
            tags=["water connection", "bmc water", "mcgm", "hydraulic engineer", "water meter", "road opening", "mumbai", "maharashtra", "nal connection", "water supply"],
            steps=task_water_steps
        )
        self._tasks[task_water.id] = task_water

        # -------------------------------------------------------------------------
        # TASK 7: Citizen Statutory Certificates (Income, Domicile & Caste - Aaple Sarkar)
        # -------------------------------------------------------------------------
        task_rts_steps = [
            TaskStep(
                id="mah-rts-1",
                task_id="task-mah-rts-certificates",
                step_number=1,
                title="Aaple Sarkar Citizen Profile & Mobile Aadhaar e-KYC",
                description="Register authenticated user profile on official Government of Maharashtra Aaple Sarkar portal with Aadhaar OTP authentication.",
                department=dept_aaple_sarkar,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=1,
                fee_amount=0.0,
                fee_breakdown={"Zero Registration Fee": 0.0},
                prerequisites=[],
                documents=[
                    DocumentRequirement(
                        id="doc-rts-poi",
                        name="Proof of Identity (Choose Any 1)",
                        description="Any 1 valid government photo identification",
                        is_mandatory=True,
                        category="Proof of Identity",
                        is_alternative_group=True,
                        group_name="Proof of Identity (Choose Any 1)",
                        alternative_options=["Aadhaar Card", "Voter ID Card", "Passport", "Driving License", "PAN Card"]
                    ),
                    DocumentRequirement(
                        id="doc-rts-poa",
                        name="Proof of Address (Choose Any 1)",
                        description="Any 1 valid residential address proof in Maharashtra",
                        is_mandatory=True,
                        category="Proof of Address",
                        is_alternative_group=True,
                        group_name="Proof of Address (Choose Any 1)",
                        alternative_options=["Electricity Bill", "Ration Card", "Registered Rent Agreement", "Telephone Bill", "Water Bill"]
                    ),
                    DocumentRequirement(id="doc-rts-photo", name="Citizen Digital Passport Photograph", description="File size between 20KB-50KB", is_mandatory=True, category="Mandatory Photo")
                ],
                forms=[FormRequirement(form_code="Aaple-Register", title="Citizen Registration Portal Form", fill_online_url="https://aaplesarkar.mahaonline.gov.in/en/Registration/Register")],
                verification_source=VerificationSource(
                    url="https://aaplesarkar.mahaonline.gov.in",
                    page_title="Aaple Sarkar Portal - Official Maharashtra Citizen Portal",
                    last_scraped_at="2026-09-26T15:29:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra Right to Public Services Act, 2015"
                ),
                designated_officer="Assistant Project Manager / Helpdesk In-Charge (1 Day)",
                designated_officer_sla_days=1,
                first_appellate_officer="District e-Governance Project Manager (DePM) (15 Days)",
                second_appellate_officer="MahaOnline State Operations Head (30 Days)",
                appeal_form_url="https://aaplesarkar.mahaonline.gov.in/en/RTSAppeals",
                is_hybrid_setu=False,
                portal_navigation_guide=[
                    "1. Click 'Apply on Official Portal ↗' to access the Aaple Sarkar registration gateway.",
                    "2. Select Option 1 (Aadhaar OTP verification) for instant profile creation.",
                    "3. Enter the 6-digit Aadhaar OTP received on your mobile and complete profile registration."
                ]
            ),
            TaskStep(
                id="mah-rts-2",
                task_id="task-mah-rts-certificates",
                step_number=2,
                title="Income Certificate Application & Talathi Verification (SLA: 15 Days)",
                description="Apply for statutory Income Certificate from Revenue Department under RTS Act 2015 with Form 16 / salary certificate / Talathi income report.",
                department=dept_aaple_sarkar,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=15,
                fee_amount=57.0,
                fee_breakdown={"Statutory Certificate Fee": 33.60, "MahaOnline Service Charge": 23.40},
                prerequisites=["mah-rts-1"],
                documents=[
                    DocumentRequirement(
                        id="doc-income-proof",
                        name="Proof of Income (Choose Any 1)",
                        description="Proof of family income for preceding financial year",
                        is_mandatory=True,
                        category="Income Proof",
                        is_alternative_group=True,
                        group_name="Proof of Income (Choose Any 1)",
                        alternative_options=["Employer Salary Certificate / Form 16", "Income Tax Return (ITR) Acknowledgment", "Talathi Income Verification Report", "Self-Declaration Affidavit before Tahsildar"]
                    ),
                    DocumentRequirement(id="doc-ration-card", name="Ration Card / Family Proof", description="Family tree and residence proof", is_mandatory=True, category="Address Proof")
                ],
                forms=[
                    FormRequirement(form_code="ServiceId-1251", title="Income Certificate Application Form", fill_online_url="https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1251", offline_fallback_url="/static/forms/income_declaration.pdf")
                ],
                verification_source=VerificationSource(
                    url="https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1251",
                    page_title="Aaple Sarkar Portal - Income Certificate Guidelines & Designated Officers",
                    last_scraped_at="2026-09-26T15:30:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra RTS Notified Service ID 1251"
                ),
                designated_officer="Tahsildar / Nayab Tahsildar (15 Days)",
                designated_officer_sla_days=15,
                first_appellate_officer="Sub-Divisional Officer (SDO) (30 Days)",
                second_appellate_officer="District Collector / Divisional Commissioner (30 Days)",
                appeal_form_url="https://aaplesarkar.mahaonline.gov.in/en/RTSAppeals",
                is_hybrid_setu=True,
                portal_navigation_guide=[
                    "1. Click 'Apply on Official Portal ↗' and log in with your Aadhaar OTP on Aaple Sarkar.",
                    "2. In the left navigation menu, select 'Revenue Department' -> 'Revenue Services'.",
                    "3. Click Service ID #1251 (Issue of Income Certificate) and upload your income proof.",
                    "4. If Talathi panchnama is required, visit your local Aaple Sarkar Seva Kendra (Setu Kendra) for biometric recording."
                ],
                is_critical_path=True
            ),
            TaskStep(
                id="mah-rts-3",
                task_id="task-mah-rts-certificates",
                step_number=3,
                title="Age, Nationality and Domicile Certificate (SLA: 15 Days)",
                description="Apply for Domicile Certificate confirming 15 years continuous residence in Maharashtra state under Revenue & Forest Department rules.",
                department=dept_aaple_sarkar,
                submission_mode=SubmissionMode.HYBRID,
                estimated_days=15,
                fee_amount=57.0,
                fee_breakdown={"Government Fee": 33.60, "Portal Service Charge": 23.40},
                prerequisites=["mah-rts-1"],
                documents=[
                    DocumentRequirement(
                        id="doc-res-15yrs",
                        name="15 Years Residence Proof (Choose Any 1)",
                        description="Continuous 15-year residence proof in Maharashtra state",
                        is_mandatory=True,
                        category="Residence Proof",
                        is_alternative_group=True,
                        group_name="15 Years Residence Proof (Choose Any 1)",
                        alternative_options=["School / College Leaving Certificate showing 15 years", "Consecutive 15-Year Electricity Bills", "Registered Sale Deed / Property Card over 15 years old", "Ration Card showing continuous stay"]
                    ),
                    DocumentRequirement(id="doc-birth-cert", name="Municipal Birth Certificate", description="Showing place of birth in Maharashtra", is_mandatory=True, category="Birth Proof")
                ],
                forms=[FormRequirement(form_code="ServiceId-1253", title="Age Nationality and Domicile Certificate Form", fill_online_url="https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1253", offline_fallback_url="/static/forms/income_declaration.pdf")],
                verification_source=VerificationSource(
                    url="https://aaplesarkar.mahaonline.gov.in/en/Login/Certificate_Documents?ServiceId=1253",
                    page_title="Aaple Sarkar Portal - Age Nationality and Domicile Certificate",
                    last_scraped_at="2026-09-26T15:31:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True,
                    gazette_ref="Maharashtra RTS Notified Service ID 1253"
                ),
                designated_officer="Tahsildar / Executive Magistrate (15 Days)",
                designated_officer_sla_days=15,
                first_appellate_officer="Sub-Divisional Officer (SDO) (30 Days)",
                second_appellate_officer="District Collector / Divisional Commissioner (30 Days)",
                appeal_form_url="https://aaplesarkar.mahaonline.gov.in/en/RTSAppeals",
                is_hybrid_setu=True,
                portal_navigation_guide=[
                    "1. Click 'Apply on Official Portal ↗' and log in with your credentials on Aaple Sarkar.",
                    "2. Select 'Revenue Department' -> 'Age, Nationality & Domicile Certificate (Service ID 1253)'.",
                    "3. Upload 15-year continuous residence proof and school leaving certificate.",
                    "4. If requested for verification, present originals at your Taluka Setu Kendra / Tahsil Office."
                ],
                is_critical_path=True
            ),
            TaskStep(
                id="mah-rts-4",
                task_id="task-mah-rts-certificates",
                step_number=4,
                title="Tahsildar Digital Signature & Barcoded Certificate Issuance",
                description="Designated Officer (Nayab Tahsildar / Tahsildar) verifies application data and issues digitally signed certificate with QR code for instant public verification.",
                department=dept_aaple_sarkar,
                submission_mode=SubmissionMode.ONLINE,
                estimated_days=3,
                fee_amount=0.0,
                fee_breakdown={"Zero Issuance Fee": 0.0},
                prerequisites=["mah-rts-2", "mah-rts-3"],
                documents=[],
                forms=[FormRequirement(form_code="DIGI-CERT", title="Barcoded Maharashtra State Certificate PDF", fill_online_url="https://aaplesarkar.mahaonline.gov.in/en/TrackApplicationStatus", offline_fallback_url="/static/forms/income_declaration.pdf")],
                verification_source=VerificationSource(
                    url="https://aaplesarkar.mahaonline.gov.in/en/TrackApplicationStatus",
                    page_title="Aaple Sarkar - Online Digital Certificate Authenticity Verification",
                    last_scraped_at="2026-09-26T15:32:00Z",
                    confidence_score=1.0,
                    is_admin_verified=True
                ),
                # Statutory RTS Act 2015 & Hybrid Submission Enhancements
                designated_officer="Tahsildar / Nayab Tahsildar (15 Days)",
                designated_officer_sla_days=15,
                first_appellate_officer="Sub-Divisional Officer (SDO) / Sub-Divisional Magistrate (30 Days)",
                second_appellate_officer="District Collector / Maharashtra State RTS Commission (30 Days)",
                appeal_form_url="https://aaplesarkar.mahaonline.gov.in/en/RTSAppeals",
                is_hybrid_setu=True,
                portal_navigation_guide=[
                    "1. Click 'Apply on Official Portal ↗' and log in with your Aadhaar OTP on Aaple Sarkar.",
                    "2. In the left navigation menu, select 'Revenue Department' -> 'Revenue Services'.",
                    "3. Select Service ID #1251 (Income Certificate) or Service ID #1253 (Domicile Certificate).",
                    "4. If Talathi demands physical verification or genealogy proof, visit your local Aaple Sarkar Seva Kendra (Setu Kendra)."
                ]
            )
        ]

        task_rts = CivicTask(
            id="task-mah-rts-certificates",
            title="Citizen Statutory Certificates Package (Income, Domicile & Caste via Aaple Sarkar)",
            category="Citizen & Vital Records",
            municipality="Maharashtra Statewide (Aaple Sarkar RTS)",
            state="Maharashtra",
            description="Integrated service roadmap under the Maharashtra Right to Public Services Act (RTS 2015) for obtaining Income Certificate, Age-Nationality-Domicile Certificate, and Caste Certificate with guaranteed statutory SLAs.",
            tags=["aaple sarkar", "income certificate", "domicile", "caste certificate", "rts act 2015", "tehsildar", "maharashtra", "dakhla", "utpanna dakhla", "rahiwasi dakhla"],
            steps=task_rts_steps
        )
        self._tasks[task_rts.id] = task_rts

# Singleton database instance
db = CivicDatabase()
