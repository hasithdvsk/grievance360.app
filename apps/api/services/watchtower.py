"""
Grievance360 SLA Escalation Watchtower Service
Redis & Celery background worker engine that continuously monitors grievance SLA deadlines,
escalates breached tickets to CRITICAL, logs audit actions, and dispatches automated alerts.
"""

import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Redis Sorted Set Key for SLA Deadline Watchtower
SLA_WATCHTOWER_KEY = "sla_watchtower"

# In-memory sorted fallback store when Redis is temporarily offline during testing
_FALLBACK_WATCHTOWER: Dict[str, float] = {}

# -----------------------------------------------------------------------------
# Celery Application Configuration
# -----------------------------------------------------------------------------
try:
    from celery import Celery

    celery_app = Celery(
        "grievance360_watchtower",
        broker=CELERY_BROKER_URL,
        backend=CELERY_RESULT_BACKEND,
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Kolkata",
        enable_utc=True,
        beat_schedule={
            "scan-escalate-breached-slas-every-minute": {
                "task": "scan_and_escalate_breached_slas",
                "schedule": 60.0,
            },
        },
    )
    HAS_CELERY = True
except Exception:
    HAS_CELERY = False

    class CeleryMock:
        """Lightweight Celery task proxy fallback if library is initializing."""
        def task(self, *args, **kwargs):
            def decorator(fn):
                fn.delay = fn
                return fn
            return decorator

    celery_app = CeleryMock()


# -----------------------------------------------------------------------------
# Redis Client Helper
# -----------------------------------------------------------------------------
def get_redis_client():
    """
    Returns an active Redis client or None if Redis service is unreachable.
    """
    try:
        import redis
        client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
        client.ping()
        return client
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Watchtower Registry Methods
# -----------------------------------------------------------------------------
def schedule_ticket_in_watchtower(complaint_id: str, deadline_timestamp: float) -> bool:
    """
    Registers or updates a complaint in the Redis sorted set 'sla_watchtower'.
    The score is the UNIX epoch timestamp of the SLA deadline.
    """
    _FALLBACK_WATCHTOWER[complaint_id] = float(deadline_timestamp)

    r = get_redis_client()
    if r:
        try:
            r.zadd(SLA_WATCHTOWER_KEY, {complaint_id: float(deadline_timestamp)})
            return True
        except Exception as e:
            print(f"[Watchtower] Notice: Could not register ticket {complaint_id} in Redis ({e}). Stored in fallback.")
    return False


def remove_ticket_from_watchtower(complaint_id: str) -> bool:
    """
    Removes a ticket from the Watchtower when resolved or closed.
    """
    _FALLBACK_WATCHTOWER.pop(complaint_id, None)
    r = get_redis_client()
    if r:
        try:
            r.zrem(SLA_WATCHTOWER_KEY, complaint_id)
            return True
        except Exception:
            pass
    return False


# -----------------------------------------------------------------------------
# Celery Tasks: SLA Breach Scanner & Dispatch Alerts
# -----------------------------------------------------------------------------
@celery_app.task(name="scan_and_escalate_breached_slas")
def scan_and_escalate_breached_slas() -> Dict[str, Any]:
    """
    Queries Redis sorted set 'sla_watchtower' for tickets past their 'sla_deadline'.
    - Updates database status from IN_PROGRESS / AUTO_ASSIGNED to ESCALATED.
    - Sets priority to CRITICAL.
    - Inserts an automated log into complaint_audit_logs detailing the system SLA breach.
    - Triggers send_dispatch_alert background task.
    """
    from services.db_service import (
        get_db_connection,
        get_complaint_by_id_or_tracking,
        MEMORY_COMPLAINTS,
        MEMORY_AUDIT_LOGS,
    )
    import uuid

    now_ts = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    breached_ids: List[str] = []

    # 1. Query Redis sorted set: ZRANGEBYSCORE sla_watchtower -inf now_ts
    r = get_redis_client()
    if r:
        try:
            # Query all items whose score <= current timestamp
            redis_breached = r.zrangebyscore(SLA_WATCHTOWER_KEY, 0, now_ts)
            if redis_breached:
                breached_ids.extend([str(item) for item in redis_breached])
        except Exception as e:
            print(f"[Watchtower] Notice: Redis query failed ({e}). Checking memory queue.")

    # Check fallback memory sorted queue
    for cid, d_ts in list(_FALLBACK_WATCHTOWER.items()):
        if d_ts <= now_ts and cid not in breached_ids:
            breached_ids.append(cid)

    escalated_tickets: List[Dict[str, Any]] = []

    for complaint_id in breached_ids:
        complaint = get_complaint_by_id_or_tracking(complaint_id)
        if not complaint:
            remove_ticket_from_watchtower(complaint_id)
            continue

        current_status = str(complaint.get("status", "")).upper()
        # If already resolved or closed, drop from watchtower
        if current_status in ["RESOLVED", "CLOSED", "REJECTED"]:
            remove_ticket_from_watchtower(complaint_id)
            continue

        # If not yet escalated, execute escalation procedure
        if current_status != "ESCALATED":
            log_id = str(uuid.uuid4())
            remarks = (
                f"SLA Breach Escalation: Ticket exceeded statutory SLA deadline "
                f"({complaint.get('sla_deadline')}). Automatic Watchtower cron escalated status "
                f"from {current_status} to ESCALATED and upgraded priority to CRITICAL."
            )

            # A. Update PostgreSQL database
            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE complaints
                            SET status = 'ESCALATED', priority = 'CRITICAL', updated_at = CURRENT_TIMESTAMP
                            WHERE complaint_id::text = %s;
                            """,
                            (complaint_id,)
                        )
                        cur.execute(
                            """
                            INSERT INTO complaint_audit_logs (
                                log_id, complaint_id, action_taken, to_bureau_id,
                                officer_remarks, actor_id, timestamp
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                            """,
                            (
                                log_id,
                                complaint_id,
                                "SLA_BREACH_ESCALATED",
                                complaint.get("bureau_id"),
                                remarks,
                                "AICTE_SLA_WATCHTOWER_CRON",
                            )
                        )
                        conn.commit()
                        conn.close()
                except Exception as e:
                    if conn:
                        conn.rollback()
                        conn.close()
                    print(f"[Watchtower] Notice: Database escalation write failed ({e}). Updating memory record.")

            # B. Update In-Memory / Cached Record
            if complaint_id in MEMORY_COMPLAINTS:
                MEMORY_COMPLAINTS[complaint_id]["status"] = "ESCALATED"
                MEMORY_COMPLAINTS[complaint_id]["priority"] = "CRITICAL"
                MEMORY_COMPLAINTS[complaint_id]["updated_at"] = now_iso

            tracking_key = complaint.get("tracking_id")
            if tracking_key and tracking_key in MEMORY_COMPLAINTS:
                MEMORY_COMPLAINTS[tracking_key]["status"] = "ESCALATED"
                MEMORY_COMPLAINTS[tracking_key]["priority"] = "CRITICAL"
                MEMORY_COMPLAINTS[tracking_key]["updated_at"] = now_iso

            audit_entry = {
                "log_id": log_id,
                "complaint_id": complaint_id,
                "action_taken": "SLA_BREACH_ESCALATED",
                "from_bureau_name": complaint.get("bureau_name"),
                "to_bureau_name": complaint.get("bureau_name"),
                "officer_remarks": remarks,
                "actor_id": "AICTE_SLA_WATCHTOWER_CRON",
                "timestamp": now_iso,
            }
            if complaint_id in MEMORY_AUDIT_LOGS:
                MEMORY_AUDIT_LOGS[complaint_id].append(audit_entry)
            else:
                MEMORY_AUDIT_LOGS[complaint_id] = [audit_entry]

            # C. Remove ticket from sorted set so it does not trigger duplicate escalations
            remove_ticket_from_watchtower(complaint_id)

            # D. Trigger Dispatch Alert Task
            recipient_email = complaint.get("complainant_email", "nodal.officer@aicte-india.org")
            recipient_phone = complaint.get("complainant_phone")
            send_dispatch_alert(
                complaint_id=complaint_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                reason="SLA_BREACH_ESCALATION",
            )

            escalated_tickets.append({
                "complaint_id": complaint_id,
                "tracking_id": complaint.get("tracking_id"),
                "bureau_name": complaint.get("bureau_name"),
                "previous_status": current_status,
                "new_status": "ESCALATED",
                "new_priority": "CRITICAL",
                "escalated_at": now_iso,
            })

    result = {
        "status": "success",
        "scanned_at": now_iso,
        "scanned_count": len(breached_ids),
        "escalated_count": len(escalated_tickets),
        "escalated_tickets": escalated_tickets,
    }
    print(f"[Watchtower] Scan complete at {now_iso}. Breached tickets escalated: {len(escalated_tickets)}")
    return result


@celery_app.task(name="send_dispatch_alert")
def send_dispatch_alert(
    complaint_id: str,
    recipient_email: str,
    recipient_phone: Optional[str] = None,
    reason: str = "SLA_BREACH",
) -> Dict[str, Any]:
    """
    Mock SMS/Email background task that logs sent dispatch alert messages
    to console and persists an audit entry into complaint_audit_logs.
    """
    from services.db_service import get_db_connection, MEMORY_AUDIT_LOGS
    import uuid

    now_iso = datetime.now(timezone.utc).isoformat()
    log_id = str(uuid.uuid4())
    phone_display = recipient_phone if recipient_phone else "None Provided"

    # 1. Print structured log to console
    alert_banner = (
        f"\n================================================================================\n"
        f"[WATCHTOWER DISPATCH ALERT GATEWAY]\n"
        f"--------------------------------------------------------------------------------\n"
        f"Timestamp      : {now_iso}\n"
        f"Complaint ID   : {complaint_id}\n"
        f"Alert Trigger  : {reason}\n"
        f"Email Recipient: {recipient_email}\n"
        f"SMS Recipient  : {phone_display}\n"
        f"Status         : SENT / DELIVERED (Mock Gateway)\n"
        f"Notice Content : URGENT: Grievance {complaint_id} has exceeded statutory SLA threshold.\n"
        f"                 Escalated to AICTE Chief Nodal Officer for immediate intervention.\n"
        f"================================================================================\n"
    )
    print(alert_banner)

    # 2. Persist audit log record
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO complaint_audit_logs (
                        log_id, complaint_id, action_taken, officer_remarks,
                        actor_id, timestamp
                    )
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                    """,
                    (
                        log_id,
                        complaint_id,
                        "DISPATCH_ALERT_SENT",
                        f"Automated {reason} email alert dispatched to {recipient_email}. SMS dispatched to {phone_display}.",
                        "MOCK_DISPATCH_ALERT_GATEWAY",
                    )
                )
                conn.commit()
                conn.close()
        except Exception:
            if conn:
                conn.close()

    # Memory store audit trail update
    audit_entry = {
        "log_id": log_id,
        "complaint_id": complaint_id,
        "action_taken": "DISPATCH_ALERT_SENT",
        "officer_remarks": f"Automated {reason} email alert dispatched to {recipient_email}. SMS dispatched to {phone_display}.",
        "actor_id": "MOCK_DISPATCH_ALERT_GATEWAY",
        "timestamp": now_iso,
    }
    if complaint_id in MEMORY_AUDIT_LOGS:
        MEMORY_AUDIT_LOGS[complaint_id].append(audit_entry)
    else:
        MEMORY_AUDIT_LOGS[complaint_id] = [audit_entry]

    return {
        "status": "SENT",
        "complaint_id": complaint_id,
        "recipient_email": recipient_email,
        "recipient_phone": recipient_phone,
        "dispatched_at": now_iso,
    }
