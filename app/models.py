from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class SubmissionMode(str, Enum):
    ONLINE = "Online"
    IN_PERSON = "In-Person"
    HYBRID = "Hybrid"

class StepStatus(str, Enum):
    LOCKED = "locked"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class VerificationSource(BaseModel):
    url: str
    page_title: str
    last_scraped_at: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    is_admin_verified: bool = False
    gazette_ref: Optional[str] = None
    portal_section: Optional[str] = None

class DocumentRequirement(BaseModel):
    id: str
    name: str
    description: str
    is_mandatory: bool = True
    category: str = "General"
    validity_rule: Optional[str] = None
    issuing_authority: Optional[str] = None
    sample_template_url: Optional[str] = None

class FormRequirement(BaseModel):
    form_code: str
    title: str
    download_url: Optional[str] = None
    fill_online_url: Optional[str] = None
    instructions: Optional[str] = None

class DepartmentInfo(BaseModel):
    id: str
    name: str
    jurisdiction: str
    office_address: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    working_hours: Optional[str] = "Mon-Fri 10:00 AM - 5:00 PM"
    portal_url: Optional[str] = None

class TaskStep(BaseModel):
    id: str
    task_id: str
    step_number: int
    title: str
    description: str
    department: DepartmentInfo
    submission_mode: SubmissionMode
    estimated_days: int = 7
    fee_amount: float = 0.0
    fee_breakdown: Dict[str, float] = Field(default_factory=dict)
    prerequisites: List[str] = Field(default_factory=list) # List of prerequisite step IDs
    documents: List[DocumentRequirement] = Field(default_factory=list)
    forms: List[FormRequirement] = Field(default_factory=list)
    verification_source: VerificationSource
    tips_and_pitfalls: Optional[str] = None
    anti_tout_advisory: Optional[str] = None
    statutory_payment_channel: Optional[str] = "Official E-Challan / Payment Gateway"
    community_verifications: int = 14
    official_receipt_mandate: Optional[str] = None
    last_gazette_notification: Optional[str] = None
    status: StepStatus = StepStatus.LOCKED
    is_critical_path: bool = False

class CivicTask(BaseModel):
    id: str
    title: str
    category: str
    municipality: str
    state: str
    description: str
    tags: List[str] = Field(default_factory=list)
    steps: List[TaskStep] = Field(default_factory=list)

class GraphNode(BaseModel):
    id: str
    step_number: int
    title: str
    department_name: str
    submission_mode: str
    estimated_days: int
    fee_amount: float
    status: StepStatus
    is_critical_path: bool
    phase_index: int
    x: float = 0.0
    y: float = 0.0
    prerequisites: List[str]
    has_official_source: bool
    confidence_score: float

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    is_critical: bool = False
    dependency_type: str = "Mandatory"

class GraphPhase(BaseModel):
    phase_index: int
    title: str
    description: str
    step_ids: List[str]

class ConsolidatedDocument(BaseModel):
    id: str
    name: str
    category: str = "General"
    description: str
    validity_rule: Optional[str] = None
    issuing_authority: Optional[str] = None
    is_mandatory: bool = True
    required_in_step_ids: List[str] = Field(default_factory=list)
    required_in_step_numbers: List[int] = Field(default_factory=list)

class RoadmapResponse(BaseModel):
    task: CivicTask
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    phases: List[GraphPhase]
    total_estimated_days: int
    total_estimated_fees: float
    critical_path_step_ids: List[str]
    unlocked_count: int
    completed_count: int
    consolidated_documents: List[ConsolidatedDocument] = Field(default_factory=list)
    anti_tout_helpline: str = "Anti-Corruption Bureau (ACB Maharashtra): 1064 / MCGM Vigilance: 022-22694719"

class UserProgressUpdate(BaseModel):
    completed_step_ids: List[str] = Field(default_factory=list)
    in_progress_step_ids: List[str] = Field(default_factory=list)

class ScrapeRequest(BaseModel):
    url: str
    task_hint: Optional[str] = None
    municipality: Optional[str] = None

class ScrapeResult(BaseModel):
    source_url: str
    page_title: str
    scraped_at: str
    confidence_score: float
    extracted_text_snippet: str
    extracted_steps: List[Dict[str, Any]]
    detected_forms: List[Dict[str, str]]
    detected_offices: List[Dict[str, str]]

class AdminVerificationUpdate(BaseModel):
    step_id: str
    is_verified: bool
    notes: Optional[str] = None
    updated_fee: Optional[float] = None
    updated_sla_days: Optional[int] = None
    updated_source_url: Optional[str] = None
