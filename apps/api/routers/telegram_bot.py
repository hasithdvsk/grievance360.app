"""
Grievance360 Telegram Bot Webhook Router
Accepts Telegram Webhook JSON updates for instant status checks (/status <TicketID> or STATUS <TicketID>)
and automated complaint filing (/file <Description> or FILE <Description>).
"""

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, status
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

TELEGRAM_BOT_SECRET = os.getenv("TELEGRAM_BOT_SECRET", "mock_telegram_secret_token_12345")
DEBUG = os.getenv("DEBUG", "True").lower() in ["true", "1", "yes"]

router = APIRouter(prefix="/api/v1/bot", tags=["WhatsApp & Telegram Bot"])


class TelegramUser(BaseModel):
    id: int
    is_bot: Optional[bool] = False
    first_name: Optional[str] = "Citizen"
    last_name: Optional[str] = ""
    username: Optional[str] = None
    language_code: Optional[str] = "en"


class TelegramChat(BaseModel):
    id: int
    type: Optional[str] = "private"
    first_name: Optional[str] = None
    username: Optional[str] = None


class TelegramMessage(BaseModel):
    message_id: Optional[int] = 1
    date: Optional[int] = 0
    chat: Optional[TelegramChat] = None
    from_: Optional[TelegramUser] = Field(None, alias="from")
    text: Optional[str] = None


class TelegramWebhookUpdate(BaseModel):
    update_id: Optional[int] = 1
    message: Optional[TelegramMessage] = None
    # Support flat / direct testing payload
    text: Optional[str] = None
    chat_id: Optional[int] = None
    from_user: Optional[str] = None


def validate_telegram_secret(secret_header: Optional[str]) -> bool:
    """
    Validates X-Telegram-Bot-Api-Secret-Token if provided.
    In debug mode or mock testing, allows execution.
    """
    if not secret_header:
        return DEBUG or TELEGRAM_BOT_SECRET == "mock_telegram_secret_token_12345"
    return secret_header == TELEGRAM_BOT_SECRET or DEBUG


@router.post(
    "/telegram",
    summary="Telegram Bot Webhook Endpoint",
    description="Handles Telegram updates with command routing for /status and /file.",
)
async def telegram_webhook(
    request: Request,
    update: Optional[TelegramWebhookUpdate] = None,
):
    # 1. Validate Secret Token Header
    secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not validate_telegram_secret(secret_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram Bot Secret Token. Authentication failed.",
        )

    # 2. Extract payload fields (support standard Telegram update or direct JSON test payload)
    raw_body = {}
    try:
        raw_body = await request.json()
    except Exception:
        pass

    text = ""
    chat_id = 0
    user_name = "Citizen"
    user_id = 0

    if update and update.message and update.message.text:
        text = update.message.text.strip()
        chat_id = update.message.chat.id if update.message.chat else 0
        if update.message.from_:
            user_name = update.message.from_.username or update.message.from_.first_name or "Citizen"
            user_id = update.message.from_.id
    elif "message" in raw_body and isinstance(raw_body["message"], dict):
        msg = raw_body["message"]
        text = msg.get("text", "").strip()
        chat = msg.get("chat", {})
        chat_id = chat.get("id", 0)
        from_dict = msg.get("from", {})
        user_name = from_dict.get("username") or from_dict.get("first_name") or "Citizen"
        user_id = from_dict.get("id", 0)
    else:
        text = raw_body.get("text", "").strip()
        chat_id = raw_body.get("chat_id", 123456789)
        user_name = raw_body.get("from_user", "TelegramUser")
        user_id = raw_body.get("user_id", 123456789)

    if not text:
        return {
            "ok": True,
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": "👋 Welcome to *AICTE Grievance360 Telegram Bot*! Send /help to see available commands.",
            "parse_mode": "Markdown",
            "action": "EMPTY_OR_IGNORED",
        }

    # Normalize command prefix (support both `/status` and `STATUS`, `/file` and `FILE`)
    normalized_text = text.lstrip("/")
    upper_text = normalized_text.upper()

    # -------------------------------------------------------------------------
    # Case A: Live Status Check (`/status <TicketID>` or `STATUS <TicketID>`)
    # -------------------------------------------------------------------------
    if upper_text.startswith("STATUS"):
        parts = normalized_text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            msg_reply = (
                "⚠️ *Format Error*\n\n"
                "Please provide a valid ticket number.\n"
                "👉 Usage: `/status GRV-2026-00001` or `STATUS GRV-2026-00001`"
            )
            return {
                "ok": True,
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": msg_reply,
                "parse_mode": "Markdown",
                "action": "ERROR_MISSING_TICKET",
            }

        ticket_id = parts[1].strip()
        complaint = get_complaint_by_id_or_tracking(ticket_id)

        if not complaint:
            msg_reply = (
                f"❌ *Grievance Not Found*\n\n"
                f"No record was found for ticket: `{ticket_id}`.\n"
                "Please check the ID or file a new grievance using:\n"
                "`/file <description of issue>`"
            )
            return {
                "ok": True,
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": msg_reply,
                "parse_mode": "Markdown",
                "action": "TICKET_NOT_FOUND",
            }

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

        reply_md = (
            f"🏛️ *AICTE Grievance360 Live Status*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎫 *Ticket ID:* `{complaint.get('tracking_id')}`\n"
            f"📌 *Status:* *{complaint.get('status')}*\n"
            f"🏢 *Bureau:* {complaint.get('bureau_name')}\n"
            f"⚡ *Priority:* *{complaint.get('priority')}*\n"
            f"⏳ *SLA Countdown:* {sla_display}\n"
            f"🏫 *Institution:* {complaint.get('institution_name', 'AICTE Central Registry')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 *Title:* {complaint.get('title')}\n\n"
            f"💡 _Send `/status {complaint.get('tracking_id')}` anytime for live tracking._"
        )

        return {
            "ok": True,
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": reply_md,
            "parse_mode": "Markdown",
            "action": "STATUS_CHECK_SUCCESS",
            "complaint": complaint,
        }

    # -------------------------------------------------------------------------
    # Case B: Instant Grievance Filing (`/file <Description>` or `FILE <Description>`)
    # -------------------------------------------------------------------------
    elif upper_text.startswith("FILE"):
        parts = normalized_text.split(maxsplit=1)
        if len(parts) < 2 or len(parts[1].strip()) < 10:
            msg_reply = (
                "⚠️ *Description Too Short*\n\n"
                "Please describe the incident or issue in detail (at least 10 characters).\n"
                "👉 Usage: `/file Rampant illegal capitation fee charged during M.Tech admissions.`"
            )
            return {
                "ok": True,
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": msg_reply,
                "parse_mode": "Markdown",
                "action": "ERROR_DESCRIPTION_TOO_SHORT",
            }

        complaint_text = parts[1].strip()

        # 1. AI Bureau & Priority Classification via NLP Engine
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
        title = f"Telegram Grievance: {complaint_text[:50]}..."
        complainant_email = f"telegram.{user_id or 123456}@grievance360.local"

        record = save_complaint_and_audit(
            title=title,
            description=f"[Filer: @{user_name} (ID: {user_id}) via Telegram]:\n{complaint_text}",
            complainant_role="STUDENT",
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
            f"✅ *Grievance Successfully Registered!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎫 *Tracking ID:* `{record['tracking_id']}`\n"
            f"🏢 *Assigned Bureau:* {bureau_name}\n"
            f"⚡ *Priority Level:* *{computed_priority}*\n"
            f"⏳ *Target SLA Deadline:* {base_sla_hours} hours\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Your complaint has been automatically dispatched to the AICTE officer.\n\n"
            f"🔍 *Track Progress:* `/status {record['tracking_id']}`"
        )

        return {
            "ok": True,
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": reply_md,
            "parse_mode": "Markdown",
            "action": "FILE_COMPLAINT_SUCCESS",
            "tracking_id": record["tracking_id"],
            "bureau": bureau_name,
            "priority": computed_priority,
        }

    # -------------------------------------------------------------------------
    # Case C: Help Menu / Start Command (/start, /help, HELP)
    # -------------------------------------------------------------------------
    else:
        help_md = (
            f"🏛️ *AICTE Grievance360 Official Telegram Bot*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"File grievances or track status in real-time.\n\n"
            f"📌 *Supported Commands:*\n\n"
            f"1️⃣ *Track Complaint Status:*\n"
            f"   `/status <TicketID>`\n"
            f"   _Example:_ `/status GRV-2026-00001`\n\n"
            f"2️⃣ *Register New Grievance:*\n"
            f"   `/file <Description of grievance>`\n"
            f"   _Example:_ `/file Dean refusing to issue bonafide certificate for education loan.`\n\n"
            f"3️⃣ *Help & Instructions:*\n"
            f"   `/help` or `/start`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_All submissions are audited and monitored under AICTE SLA regulations._"
        )
        return {
            "ok": True,
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": help_md,
            "parse_mode": "Markdown",
            "action": "HELP_MENU",
        }
