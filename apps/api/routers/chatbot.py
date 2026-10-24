"""
Grievance360 In-App AI Chatbot Router
Processes interactive in-app user queries, STATUS tracking commands,
and instant FILE grievance registrations with AICTE SentenceTransformers triage.
"""

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from services.nlp_engine import classify_bureau_and_priority, check_duplicate_complaint
from services.db_service import (
    get_complaint_by_id_or_tracking,
    get_all_complaints_for_duplicate_check,
    resolve_bureau,
    resolve_institution,
    calculate_dynamic_sla,
    save_complaint_and_audit,
)

load_dotenv()

router = APIRouter(prefix="/api/v1/bot", tags=["In-App Chatbot"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User prompt or command string")
    conversation_id: Optional[str] = Field("default-session", description="Client conversation session ID")


class ChatResponse(BaseModel):
    reply: str
    action_type: str = Field(..., description="STATUS | FILE | INFO")
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="In-App AI Chatbot Assistant",
    description="Handles natural language inquiries, STATUS lookups, and instant FILE grievance triage.",
)
async def chat_with_bot(payload: ChatRequest):
    msg_raw = payload.message.strip()
    msg_clean = msg_raw.lstrip("/")
    upper_msg = msg_clean.upper()

    # -------------------------------------------------------------------------
    # Case 1: Status Tracking (STATUS <TicketID> or /status <TicketID>)
    # -------------------------------------------------------------------------
    if upper_msg.startswith("STATUS"):
        parts = msg_clean.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return ChatResponse(
                reply=(
                    "⚠️ **Ticket ID Required**\n\n"
                    "Please provide your Grievance Tracking ID to look up live status.\n\n"
                    "👉 **Example:** `STATUS GRV-2026-00001`"
                ),
                action_type="STATUS",
                metadata={"status": "missing_parameter"},
            )

        ticket_id = parts[1].strip()
        complaint = get_complaint_by_id_or_tracking(ticket_id)

        if not complaint:
            return ChatResponse(
                reply=(
                    f"❌ **Grievance Not Found**\n\n"
                    f"No active or archived record was found for ticket: `{ticket_id}`.\n\n"
                    "💡 *Tip: Ensure the tracking format is correct (e.g. `GRV-2026-XXXXX`), "
                    "or register a new issue using:* `FILE <description>`"
                ),
                action_type="STATUS",
                metadata={"status": "not_found", "queried_id": ticket_id},
            )

        # Compute dynamic SLA hours remaining
        now = datetime.now(timezone.utc)
        sla_deadline_str = complaint.get("sla_deadline")
        sla_display = "Under Assessment"

        if sla_deadline_str:
            try:
                deadline_dt = datetime.fromisoformat(sla_deadline_str.replace("Z", "+00:00"))
                diff_seconds = (deadline_dt - now).total_seconds()
                if diff_seconds > 0:
                    sla_display = f"⏳ **{diff_seconds / 3600:.1f} hours remaining**"
                else:
                    sla_display = f"🚨 **BREACHED ({-diff_seconds / 3600:.1f} hrs overdue)**"
            except Exception:
                pass

        reply_md = (
            f"### 🏛️ AICTE Grievance Live Status\n\n"
            f"- **🎫 Ticket ID:** `{complaint.get('tracking_id')}`\n"
            f"- **📌 Status:** `{complaint.get('status')}`\n"
            f"- **🏢 Assigned Bureau:** **{complaint.get('bureau_name')}**\n"
            f"- **⚡ Priority Level:** `{complaint.get('priority')}`\n"
            f"- **⏱️ SLA Window:** {sla_display}\n"
            f"- **🏫 Institution:** {complaint.get('institution_name', 'AICTE Central Registry')}\n\n"
            f"**Subject:** {complaint.get('title')}\n\n"
            f"_Audit logs and official Action Taken Reports (ATR) are continuously synchronized._"
        )

        return ChatResponse(
            reply=reply_md,
            action_type="STATUS",
            metadata={
                "tracking_id": complaint.get("tracking_id"),
                "status": complaint.get("status"),
                "bureau": complaint.get("bureau_name"),
                "priority": complaint.get("priority"),
                "sla_display": sla_display,
            },
        )

    # -------------------------------------------------------------------------
    # Case 2: Instant Grievance Registration (FILE <Description> or /file <Description>)
    # -------------------------------------------------------------------------
    elif upper_msg.startswith("FILE"):
        parts = msg_clean.split(maxsplit=1)
        if len(parts) < 2 or len(parts[1].strip()) < 10:
            return ChatResponse(
                reply=(
                    "⚠️ **Description Too Short**\n\n"
                    "Please provide a complete description of your complaint (at least 10 characters).\n\n"
                    "👉 **Example:** `FILE Senior students in hostel Block C are imposing unauthorized late-night curfew.`"
                ),
                action_type="FILE",
                metadata={"status": "validation_error"},
            )

        complaint_text = parts[1].strip()

        # 1. AI Bureau & Priority Classification via SentenceTransformers
        classification = classify_bureau_and_priority(complaint_text)
        assigned_bureau_name = classification["bureau_name"]
        computed_priority = classification["priority"]

        # 2. Check for duplicate complaints
        recent_complaints = get_all_complaints_for_duplicate_check()
        is_duplicate, master_id, sim_score = check_duplicate_complaint(
            complaint_text, recent_complaints, threshold=0.85
        )

        # 3. Resolve Bureau, Institution, and Dynamic SLA
        bureau_id, bureau_name, base_sla_hours = resolve_bureau(assigned_bureau_name)
        institution_id, inst_name, inst_city, inst_state = resolve_institution(
            None, "1-10001001"
        )
        sla_deadline = calculate_dynamic_sla(base_sla_hours, computed_priority)
        status_val = "SUBMITTED" if is_duplicate else "AUTO_ASSIGNED"

        # 4. Save complaint & audit trail
        title = f"In-App Chat Grievance: {complaint_text[:50]}..."
        complainant_email = f"chat.{payload.conversation_id[:8]}@grievance360.local"

        record = save_complaint_and_audit(
            title=title,
            description=f"[Chat Session: {payload.conversation_id}]:\n{complaint_text}",
            complainant_role="CITIZEN",
            complainant_email=complainant_email,
            complainant_phone="+910000000000",
            institution_id=institution_id,
            institution_name=inst_name,
            institution_city=inst_city,
            institution_state=inst_state,
            bureau_id=bureau_id,
            bureau_name=bureau_name,
            priority=computed_priority,
            status=status_val,
            is_duplicate=is_duplicate,
            master_complaint_id=master_id,
            sla_deadline=sla_deadline,
        )

        reply_md = (
            f"✅ **Grievance Registered Successfully!**\n\n"
            f"- **🎫 Your Tracking ID:** `{record['tracking_id']}`\n"
            f"- **🏢 Assigned Bureau:** **{bureau_name}**\n"
            f"- **⚡ Priority Level:** `{computed_priority}`\n"
            f"- **⏳ Target SLA Window:** `{base_sla_hours} hours`\n\n"
            f"Your issue has been logged into the AICTE Nodal Escalation Watchtower.\n\n"
            f"💡 *You can track it anytime by typing:* `STATUS {record['tracking_id']}`"
        )

        return ChatResponse(
            reply=reply_md,
            action_type="FILE",
            metadata={
                "tracking_id": record["tracking_id"],
                "bureau": bureau_name,
                "priority": computed_priority,
                "sla_hours": base_sla_hours,
                "is_duplicate": is_duplicate,
            },
        )

    # -------------------------------------------------------------------------
    # Case 3: Generic AI Assistant & Guidance
    # -------------------------------------------------------------------------
    else:
        info_reply = (
            "👋 **Hello! I'm your AICTE Grievance360 Assistant.**\n\n"
            "I can help you monitor existing complaints, file emergency grievances, or connect to messenger bots:\n\n"
            "🔍 **Track an Existing Ticket:**\n"
            "Type `STATUS <TicketID>` (e.g. `STATUS GRV-2026-00001`)\n\n"
            "📝 **File a New Grievance Instantly:**\n"
            "Type `FILE <Description of issue>`\n\n"
            "💬 **Prefer Mobile Messaging?**\n"
            "- Connect directly on **WhatsApp** via the top gateway tab.\n"
            "- Connect on **Telegram** using `/status` or `/file`.\n\n"
            "_All grievances are safeguarded under strict statutory AICTE SLA resolution windows._"
        )

        return ChatResponse(
            reply=info_reply,
            action_type="INFO",
            metadata={
                "supported_commands": ["STATUS <ID>", "FILE <Description>", "HELP"],
                "suggested_actions": [
                    {"label": "Check Status", "command": "STATUS GRV-2026-00001"},
                    {"label": "File Complaint", "command": "FILE "},
                ],
            },
        )
