"""
Complaint Data Validation Models & Response Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ComplaintPriorityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ComplaintStatusEnum(str, Enum):
    SUBMITTED = "SUBMITTED"
    AUTO_ASSIGNED = "AUTO_ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    ACTION_TAKEN = "ACTION_TAKEN"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class ComplaintRegisterRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=255, example="Forced late-night roll calls and ragging in hostel")
    description: str = Field(
        ...,
        min_length=15,
        example="Senior students are forcing first-year boarders to undergo physical roll calls and verbal abuse in Block C.",
    )
    complainant_role: str = Field(
        default="STUDENT",
        description="Role of complainant: STUDENT, FACULTY, STAFF, PARENTS, CITIZEN",
        example="STUDENT",
    )
    complainant_email: str = Field(
        ...,
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        example="student.victim@example.org",
    )
    complainant_phone: Optional[str] = Field(None, example="+919876543210")
    institution_id: Optional[str] = Field(
        None,
        description="UUID of institution or AICTE ID (e.g. 1-10001001)",
        example="20000000-0000-0000-0000-000000000001",
    )
    institution_aicte_id: Optional[str] = Field(None, example="1-10001001")


class ComplaintRegisterResponse(BaseModel):
    tracking_id: str
    complaint_id: str
    title: str
    assigned_bureau: str
    bureau_id: str
    priority: str
    status: str
    sla_deadline: str
    is_duplicate: bool
    master_complaint_id: Optional[str] = None
    created_at: str
    message: str


class AuditLogEntry(BaseModel):
    log_id: str
    action_taken: str
    from_bureau_id: Optional[str] = None
    to_bureau_id: Optional[str] = None
    from_bureau_name: Optional[str] = None
    to_bureau_name: Optional[str] = None
    officer_remarks: Optional[str] = None
    actor_id: Optional[str] = None
    timestamp: str


class ComplaintTrackResponse(BaseModel):
    complaint_id: str
    tracking_id: str
    title: str
    description: str
    complainant_role: str
    complainant_email: str
    complainant_phone: Optional[str] = None
    institution_id: str
    institution_name: Optional[str] = None
    institution_city: Optional[str] = None
    institution_state: Optional[str] = None
    bureau_id: str
    bureau_name: str
    priority: str
    status: str
    is_duplicate: bool
    master_complaint_id: Optional[str] = None
    sla_deadline: Optional[str] = None
    created_at: str
    updated_at: str
    timeline: List[AuditLogEntry] = []
