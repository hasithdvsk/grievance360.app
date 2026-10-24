"""
Grievance360 Twilio WhatsApp Bot Webhook Router
Parses incoming WhatsApp webhook messages for instant status checks (STATUS <TicketID>)
and automated complaint filing (FILE <Description>) with Twilio signature validation.
"""

import os
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Form, Response, HTTPException, status
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

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "mock_auth_token_secret_12345")
DEBUG = os.getenv("DEBUG", "True").lower() in ["true", "1", "yes"]

router = APIRouter(prefix="/api/v1/bot", tags=["WhatsApp & Telegram Bot"])


def validate_twilio_signature(
    request_url: str,
    form_params: Dict[str, str],
    signature_header: Optional[str],
    auth_token: str = TWILIO_AUTH_TOKEN,
) -> bool:
    """
    Validates Twilio webhook authenticity using HMAC-SHA1 signature.
    If signature is valid or running in local dev/debug mode without a real secret, returns True.
    """
    if not signature_header:
        # Allow bypass in debug or test environments
        return DEBUG or auth_token == "mock_auth_token_secret_12345"

    try:
        from twilio.request_validator import RequestValidator
        validator = RequestValidator(auth_token)
        return validator.validate(request_url, form_params, signature_header)
    except Exception:
        # Native Python HMAC-SHA1 fallback matching Twilio specification
        # 1. Sort post parameters alphabetically by key
        s = request_url
        for key in sorted(form_params.keys()):
            s += f"{key}{form_params[key]}"
        computed = hmac.new(auth_token.encode("utf-8"), s.encode("utf-8"), hashlib.sha1)
        expected = base64.b64encode(computed.digest()).decode("utf-8")
        return hmac.compare_digest(expected, signature_header)


def build_twiml_response(message_text: str) -> Response:
    """
    Wraps text inside standard Twilio TwiML Messaging XML.
    """
    # Escape XML entities in message
    safe_text = (
        message_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<Response>\n"
        f"    <Message>{safe_text}</Message>\n"
        "</Response>"
    )
    return Response(content=twiml, media_type="application/xml")


@router.post(
    "/whatsapp",
    summary="Twilio WhatsApp Webhook",
    description="Handles WhatsApp user messages for STATUS lookups and FILE complaint registration.",
)
async def twilio_whatsapp_webhook(
    request: Request,
    Body: str = Form(..., description="Message text content from WhatsApp"),
    From: str = Form(..., description="Sender WhatsApp phone ID e.g. whatsapp:+919876543210"),
    To: Optional[str] = Form(None),
    MessageSid: Optional[str] = Form(None),
    AccountSid: Optional[str] = Form(None),
):
    # 1. Security Signature Validation
    sig_header = request.headers.get("X-Twilio-Signature")
    raw_form = {"Body": Body, "From": From}
    if To:
        raw_form["To"] = To
    if MessageSid:
        raw_form["MessageSid"] = MessageSid
    if AccountSid:
        raw_form["AccountSid"] = AccountSid

    is_valid = validate_twilio_signature(str(request.url), raw_form, sig_header)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Twilio Webhook Signature. Authentication Failed.",
        )

    msg_clean = Body.strip()
    clean_phone = From.replace("whatsapp:", "").strip()

    # -------------------------------------------------------------------------
    # Case A: Live Status Check (`STATUS <TicketID>`)
    # -------------------------------------------------------------------------
    if msg_clean.upper().startswith("STATUS"):
        parts = msg_clean.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return build_twiml_response(
                "⚠️ *Format Error*\n\n"
                "Please provide a ticket number.\n"
                "Example: *STATUS GRV-2026-00001*"
            )

        ticket_id = parts[1].strip()
        complaint = get_complaint_by_id_or_tracking(ticket_id)

        if not complaint:
            return build_twiml_response(
                f"❌ *Grievance Not Found*\n\n"
                f"No record was found for ticket: *{ticket_id}*.\n"
                "Please verify the number or submit a new grievance by typing:\n"
                "*FILE <description of your grievance>*"
            )

        # Calculate SLA remaining hours
        now = datetime.now(timezone.utc)
        sla_deadline_str = complaint.get("sla_deadline")
        sla_display = "Under Assessment"

        if sla_deadline_str:
            try:
                deadline_dt = datetime.fromisoformat(sla_deadline_str.replace("Z", "+00:00"))
                diff_seconds = (deadline_dt - now).total_seconds()
                if diff_seconds > 0:
                    sla_display = f"{diff_seconds / 3600:.1f} hours remaining"
                else:
                    sla_display = f"BREACHED ({-diff_seconds / 3600:.1f} hrs overdue)"
            except Exception:
                pass

        reply = (
            f"🏛️ *AICTE Grievance360 Update*\n"
            f"----------------------------------------\n"
            f"🎫 *Ticket ID:* {complaint.get('tracking_id')}\n"
            f"📌 *Status:* {complaint.get('status')}\n"
            f"🏢 *Bureau:* {complaint.get('bureau_name')}\n"
            f"⚡ *Priority:* {complaint.get('priority')}\n"
            f"⏳ *SLA Window:* {sla_display}\n"
            f"🏫 *Institution:* {complaint.get('institution_name', 'AICTE Central Registry')}\n"
            f"----------------------------------------\n"
            f"📝 *Subject:* {complaint.get('title')}\n\n"
            f"_Reply STATUS {complaint.get('tracking_id')} anytime for live status updates._"
        )
        return build_twiml_response(reply)

    # -------------------------------------------------------------------------
    # Case B: Instant Grievance Filing (`FILE <Description>`)
    # -------------------------------------------------------------------------
    elif msg_clean.upper().startswith("FILE"):
        parts = msg_clean.split(maxsplit=1)
        if len(parts) < 2 or len(parts[1].strip()) < 10:
            return build_twiml_response(
                "⚠️ *Description Too Short*\n\n"
                "Please provide a complete description of the issue.\n"
                "Example:\n"
                "*FILE Senior students in hostel Block C are imposing verbal and physical harassment.*"
            )

        complaint_text = parts[1].strip()

        # 1. AI Bureau & Priority Classification
        classification = classify_bureau_and_priority(complaint_text)
        assigned_bureau_name = classification["bureau_name"]
        computed_priority = classification["priority"]

        # 2. Check for duplicate complaints
        recent_complaints = get_all_complaints_for_duplicate_check()
        is_duplicate, master_id, sim = check_duplicate_complaint(
            complaint_text, recent_complaints, threshold=0.85
        )

        # 3. Resolve Bureau, Institution, and Dynamic SLA
        bureau_id, bureau_name, base_sla_hours = resolve_bureau(assigned_bureau_name)
        institution_id, inst_name, inst_city, inst_state = resolve_institution(
            None, "1-10001001"
        )
        sla_deadline = calculate_dynamic_sla(base_sla_hours, computed_priority)
        status_val = "SUBMITTED" if is_duplicate else "AUTO_ASSIGNED"

        # 4. Synthesize title and save record
        title = f"WhatsApp Grievance: {complaint_text[:50]}..."
        complainant_email = f"whatsapp.{clean_phone.replace('+', '')}@grievance360.local"

        record = save_complaint_and_audit(
            title=title,
            description=f"[Filer Mobile: {clean_phone} via WhatsApp]:\n{complaint_text}",
            complainant_role="CITIZEN",
            complainant_email=complainant_email,
            complainant_phone=clean_phone,
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

        reply = (
            f"✅ *Grievance Registered Successfully!*\n"
            f"----------------------------------------\n"
            f"🎫 *Your Tracking ID:* {record['tracking_id']}\n"
            f"🏢 *Assigned Bureau:* {bureau_name}\n"
            f"⚡ *Priority Level:* {computed_priority}\n"
            f"⏳ *Target SLA Deadline:* {base_sla_hours} hours\n"
            f"----------------------------------------\n"
            f"Your issue has been routed to the AICTE Nodal Officer.\n\n"
            f"Track anytime by replying:\n"
            f"*STATUS {record['tracking_id']}*"
        )
        return build_twiml_response(reply)

    # -------------------------------------------------------------------------
    # Case C: Help Menu / Greeting
    # -------------------------------------------------------------------------
    else:
        welcome_reply = (
            f"🏛️ *Welcome to AICTE Grievance360 WhatsApp Bot*\n"
            f"----------------------------------------\n"
            f"You can track existing tickets or file complaints instantly.\n\n"
            f"📌 *Supported Commands:*\n\n"
            f"1️⃣ *Check Status:*\n"
            f"Type: `STATUS <TicketID>`\n"
            f"Example: `STATUS GRV-2026-00001`\n\n"
            f"2️⃣ *Register Grievance:*\n"
            f"Type: `FILE <Description of issue>`\n"
            f"Example: `FILE Delayed scholarship disbursement for semester 2`\n\n"
            f"3️⃣ *Help:*\n"
            f"Type: `HELP` to view this menu again.\n"
            f"----------------------------------------\n"
            f"_AICTE Autonomous Monitoring Cell, New Delhi_"
        )
        return build_twiml_response(welcome_reply)
