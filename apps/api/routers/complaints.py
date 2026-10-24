"""
Grievance360 Complaints Router
Endpoints for AI-driven complaint registration, dynamic SLA triage,
duplicate detection, and comprehensive audit timeline tracking.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional

from schemas.complaint import (
    ComplaintRegisterRequest,
    ComplaintRegisterResponse,
    ComplaintTrackResponse,
)
from services.nlp_engine import (
    classify_bureau_and_priority,
    check_duplicate_complaint,
)
from services.db_service import (
    calculate_dynamic_sla,
    get_all_complaints_for_duplicate_check,
    resolve_institution,
    resolve_bureau,
    save_complaint_and_audit,
    get_complaint_by_id_or_tracking,
    MEMORY_COMPLAINTS,
)

router = APIRouter(prefix="/api/v1/complaints", tags=["Complaints"])


@router.post(
    "/register",
    response_model=ComplaintRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register & Auto-Triage Complaint",
    description=(
        "Ingests citizen/student grievance, runs sentence-transformer semantic embedding "
        "to route to appropriate AICTE bureau, computes dynamic priority & SLA deadline, "
        "checks for duplicate complaints, and persists audit logs."
    ),
)
async def register_complaint(payload: ComplaintRegisterRequest):
    combined_text = f"{payload.title}. {payload.description}"

    # 1. Semantic Bureau & Dynamic Priority Classification via NLP Engine
    classification = classify_bureau_and_priority(combined_text)
    assigned_bureau_name = classification["bureau_name"]
    computed_priority = classification["priority"]

    # 2. Semantic Duplicate Detection against active complaints
    recent_complaints = get_all_complaints_for_duplicate_check()
    is_duplicate, master_id, similarity_score = check_duplicate_complaint(
        combined_text, recent_complaints, threshold=0.85
    )

    # 3. Resolve Target Bureau and Base SLA Hours
    bureau_id, bureau_name, base_sla_hours = resolve_bureau(assigned_bureau_name)

    # 4. Resolve Institution Details
    institution_id, inst_name, inst_city, inst_state = resolve_institution(
        payload.institution_id, payload.institution_aicte_id
    )

    # 5. Calculate Dynamic SLA Deadline
    sla_deadline = calculate_dynamic_sla(base_sla_hours, computed_priority)

    # 6. Determine Lifecycle Status
    complaint_status = "SUBMITTED" if is_duplicate else "AUTO_ASSIGNED"

    # 7. Persist Complaint & Audit Trail
    record = save_complaint_and_audit(
        title=payload.title,
        description=payload.description,
        complainant_role=payload.complainant_role,
        complainant_email=str(payload.complainant_email),
        complainant_phone=payload.complainant_phone,
        institution_id=institution_id,
        institution_name=inst_name,
        institution_city=inst_city,
        institution_state=inst_state,
        bureau_id=bureau_id,
        bureau_name=bureau_name,
        priority=computed_priority,
        status=complaint_status,
        is_duplicate=is_duplicate,
        master_complaint_id=master_id,
        sla_deadline=sla_deadline,
    )

    message = f"Grievance filed successfully and auto-assigned to {bureau_name} with {computed_priority} priority."
    if is_duplicate:
        message += f" Notice: Flagged as semantic duplicate of master ticket {master_id} (Similarity: {similarity_score:.2f})."

    return ComplaintRegisterResponse(
        tracking_id=record["tracking_id"],
        complaint_id=record["complaint_id"],
        title=record["title"],
        assigned_bureau=bureau_name,
        bureau_id=bureau_id,
        priority=computed_priority,
        status=complaint_status,
        sla_deadline=record["sla_deadline"],
        is_duplicate=is_duplicate,
        master_complaint_id=master_id,
        created_at=record["created_at"],
        message=message,
    )


@router.get(
    "/track/{complaint_id}",
    response_model=ComplaintTrackResponse,
    summary="Track Complaint Status & Timeline",
    description="Fetches detailed complaint status, SLA deadline, and complete chronological audit log timeline.",
)
async def track_complaint(complaint_id: str):
    complaint = get_complaint_by_id_or_tracking(complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Tracking number '{complaint_id}' was not found.",
        )

    return ComplaintTrackResponse(**complaint)


@router.get(
    "/{complaint_id}/export-atr",
    summary="Export Official Action Taken Report (ATR) PDF",
    description="Generates an official AICTE Action Taken Report (ATR) PDF with complaint details, audit ledger, and digital seal.",
)
async def export_complaint_atr(complaint_id: str):
    complaint = get_complaint_by_id_or_tracking(complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Tracking number '{complaint_id}' was not found.",
        )

    from services.pdf_generator import generate_atr_pdf
    from fastapi.responses import StreamingResponse

    pdf_buffer = generate_atr_pdf(complaint)
    filename = f"AICTE_ATR_{complaint.get('tracking_id', complaint_id)}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/",
    response_model=List[ComplaintTrackResponse],
    summary="List Recent Complaints",
    description="Lists recent complaints with optional filter by bureau or status.",
)
async def list_complaints(
    status: Optional[str] = Query(None, description="Filter by status (e.g. AUTO_ASSIGNED, IN_PROGRESS, RESOLVED)"),
    bureau: Optional[str] = Query(None, description="Filter by bureau name"),
):
    results = []
    # Collect from memory store / database
    for c_id, c in MEMORY_COMPLAINTS.items():
        if len(c_id) == 36:  # Only UUID keys, skip tracking aliases
            complaint_full = get_complaint_by_id_or_tracking(c_id)
            if complaint_full:
                if status and complaint_full["status"].upper() != status.upper():
                    continue
                if bureau and bureau.lower() not in complaint_full["bureau_name"].lower():
                    continue
                results.append(complaint_full)
    return results


@router.post(
    "/watchtower/scan",
    summary="Trigger SLA Watchtower Escalation Scan",
    description=(
        "Executes Celery / Redis sorted set scan for complaints whose SLA deadline "
        "has breached. Escalates status to ESCALATED, upgrades priority to CRITICAL, "
        "logs automated audit records, and triggers dispatch alerts."
    ),
)
async def trigger_watchtower_scan():
    from services.watchtower import scan_and_escalate_breached_slas
    result = scan_and_escalate_breached_slas()
    return result


@router.get(
    "/watchtower/status",
    summary="Get SLA Watchtower Status",
    description="Returns current status of Redis SLA Watchtower and number of actively monitored tickets.",
)
async def get_watchtower_status():
    from services.watchtower import get_redis_client, SLA_WATCHTOWER_KEY, _FALLBACK_WATCHTOWER
    r = get_redis_client()
    redis_count = 0
    if r:
        try:
            redis_count = r.zcard(SLA_WATCHTOWER_KEY) or 0
        except Exception:
            pass

    return {
        "engine": "Redis & Celery SLA Watchtower",
        "redis_connected": r is not None,
        "monitored_in_redis": redis_count,
        "monitored_in_fallback": len(_FALLBACK_WATCHTOWER),
        "target_sorted_set": SLA_WATCHTOWER_KEY,
    }
