"""
Database Service Layer
Handles PostgreSQL persistence, PostGIS queries, dynamic SLA deadline calculations,
and audit timeline logging for Grievance360 complaints.
"""

import os
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
import uuid
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres_secret_password@localhost:5432/grievance360_db"
)

# Reference Bureau definitions matching packages/db/seed.sql
DEFAULT_BUREAUS: Dict[str, Dict[str, Any]] = {
    "Anti-Ragging Bureau": {
        "bureau_id": "10000000-0000-0000-0000-000000000001",
        "name": "Anti-Ragging Bureau",
        "email": "antiragging.head@aicte-india.org",
        "sla_response_hours": 24,
    },
    "Approval Bureau": {
        "bureau_id": "10000000-0000-0000-0000-000000000002",
        "name": "Approval Bureau",
        "email": "approval.head@aicte-india.org",
        "sla_response_hours": 48,
    },
    "Finance Bureau": {
        "bureau_id": "10000000-0000-0000-0000-000000000003",
        "name": "Finance Bureau",
        "email": "finance.head@aicte-india.org",
        "sla_response_hours": 72,
    },
    "Legal Bureau": {
        "bureau_id": "10000000-0000-0000-0000-000000000004",
        "name": "Legal Bureau",
        "email": "legal.head@aicte-india.org",
        "sla_response_hours": 96,
    },
    "Generic Bureau": {
        "bureau_id": "10000000-0000-0000-0000-000000000005",
        "name": "Generic Bureau",
        "email": "generic.cell@aicte-india.org",
        "sla_response_hours": 48,
    },
}

# Reference Institutions matching packages/db/seed.sql
DEFAULT_INSTITUTIONS: Dict[str, Dict[str, Any]] = {
    "20000000-0000-0000-0000-000000000001": {
        "institution_id": "20000000-0000-0000-0000-000000000001",
        "aicte_id": "1-10001001",
        "name": "Indian Institute of Technology Delhi (IIT Delhi)",
        "city": "New Delhi",
        "state": "Delhi",
    },
    "20000000-0000-0000-0000-000000000002": {
        "institution_id": "20000000-0000-0000-0000-000000000002",
        "aicte_id": "1-10001002",
        "name": "Indian Institute of Technology Bombay (IIT Bombay)",
        "city": "Mumbai",
        "state": "Maharashtra",
    },
    "20000000-0000-0000-0000-000000000003": {
        "institution_id": "20000000-0000-0000-0000-000000000003",
        "aicte_id": "1-10001003",
        "name": "Indian Institute of Technology Madras (IIT Madras)",
        "city": "Chennai",
        "state": "Tamil Nadu",
    },
}

# In-memory synchronized store for fallback / fast lookup
MEMORY_COMPLAINTS: Dict[str, Dict[str, Any]] = {}
MEMORY_AUDIT_LOGS: Dict[str, List[Dict[str, Any]]] = {}

# Pre-populate sample complaints from seed.sql into memory store
_SEED_COMPLAINT_ID = "30000000-0000-0000-0000-000000000001"
MEMORY_COMPLAINTS[_SEED_COMPLAINT_ID] = {
    "complaint_id": _SEED_COMPLAINT_ID,
    "tracking_id": "GRV-2026-00001",
    "title": "Hostel curfew intimidation and verbal ragging of first-year boarders",
    "description": "Senior hostel residents in Block C subjected new entrants to unpermitted late-night physical roll calls and verbal abuse.",
    "complainant_role": "STUDENT",
    "complainant_email": "victim.student@example.org",
    "complainant_phone": "+919811223344",
    "institution_id": "20000000-0000-0000-0000-000000000001",
    "institution_name": "Indian Institute of Technology Delhi (IIT Delhi)",
    "institution_city": "New Delhi",
    "institution_state": "Delhi",
    "bureau_id": "10000000-0000-0000-0000-000000000001",
    "bureau_name": "Anti-Ragging Bureau",
    "priority": "CRITICAL",
    "status": "IN_PROGRESS",
    "is_duplicate": False,
    "master_complaint_id": None,
    "sla_deadline": (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat(),
    "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
    "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
}
MEMORY_COMPLAINTS["GRV-2026-00001"] = MEMORY_COMPLAINTS[_SEED_COMPLAINT_ID]

MEMORY_AUDIT_LOGS[_SEED_COMPLAINT_ID] = [
    {
        "log_id": "40000000-0000-0000-0000-000000000001",
        "complaint_id": _SEED_COMPLAINT_ID,
        "action_taken": "AUTO_TRIAGED_BY_AI",
        "from_bureau_id": None,
        "to_bureau_id": "10000000-0000-0000-0000-000000000001",
        "from_bureau_name": None,
        "to_bureau_name": "Anti-Ragging Bureau",
        "officer_remarks": "NLP semantic classifier detected severity keywords: curfew intimidation, ragging. Priority set to CRITICAL.",
        "actor_id": "SYSTEM_NLP_TRIAGE_WORKER",
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
    },
    {
        "log_id": "40000000-0000-0000-0000-000000000002",
        "complaint_id": _SEED_COMPLAINT_ID,
        "action_taken": "NOTICE_SERVED_TO_INSTITUTION",
        "from_bureau_id": "10000000-0000-0000-0000-000000000001",
        "to_bureau_id": "10000000-0000-0000-0000-000000000001",
        "from_bureau_name": "Anti-Ragging Bureau",
        "to_bureau_name": "Anti-Ragging Bureau",
        "officer_remarks": "Formal inquiry email dispatched to Dean of Student Affairs. Proactive warden report requested within 12 hours.",
        "actor_id": "OFFICER_ANTIRAGGING_04",
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
    },
]


def calculate_dynamic_sla(base_sla_hours: int, priority: str) -> datetime:
    """
    Computes SLA resolution deadline dynamically adjusted by priority level:
    - CRITICAL: Compressed to 12 hours (Emergency intervention)
    - HIGH: Compressed by ~30% (e.g. 24h-48h)
    - MEDIUM: Standard bureau SLA (48h-72h)
    - LOW: Standard base + 24 hours
    """
    now = datetime.now(timezone.utc)
    if priority == "CRITICAL":
        return now + timedelta(hours=12)
    elif priority == "HIGH":
        hours = max(24, int(base_sla_hours * 0.65))
        return now + timedelta(hours=hours)
    elif priority == "MEDIUM":
        return now + timedelta(hours=base_sla_hours)
    else:  # LOW
        return now + timedelta(hours=base_sla_hours + 24)


def get_db_connection():
    """
    Attempts to establish connection to PostgreSQL database.
    Returns connection object or None if unreachable.
    """
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        return None


def get_all_complaints_for_duplicate_check() -> List[Dict[str, Any]]:
    """
    Fetches list of existing complaints for semantic duplicate vector comparison.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT complaint_id, title, description FROM complaints ORDER BY created_at DESC LIMIT 500;"
                )
                rows = cur.fetchall()
                conn.close()
                return [{"complaint_id": str(r[0]), "title": r[1], "description": r[2]} for r in rows]
        except Exception:
            conn.close()

    # Fallback to memory store
    return [
        {"complaint_id": c["complaint_id"], "title": c["title"], "description": c["description"]}
        for c in MEMORY_COMPLAINTS.values()
    ]


def resolve_institution(institution_id: Optional[str], aicte_id: Optional[str]) -> Tuple[str, str, str, str]:
    """
    Resolves institution details from ID or AICTE ID.
    Returns (institution_id, name, city, state).
    """
    # 1. Try PostgreSQL lookup
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                if institution_id:
                    cur.execute(
                        "SELECT institution_id, name, city, state FROM institutions WHERE institution_id = %s;",
                        (institution_id,)
                    )
                elif aicte_id:
                    cur.execute(
                        "SELECT institution_id, name, city, state FROM institutions WHERE aicte_id = %s;",
                        (aicte_id,)
                    )
                row = cur.fetchone()
                conn.close()
                if row:
                    return str(row[0]), row[1], row[2], row[3]
        except Exception:
            conn.close()

    # 2. Lookup in default institutions
    if institution_id and institution_id in DEFAULT_INSTITUTIONS:
        inst = DEFAULT_INSTITUTIONS[institution_id]
        return inst["institution_id"], inst["name"], inst["city"], inst["state"]

    for inst in DEFAULT_INSTITUTIONS.values():
        if aicte_id and inst.get("aicte_id") == aicte_id:
            return inst["institution_id"], inst["name"], inst["city"], inst["state"]

    # 3. Fallback default institution
    default_id = "20000000-0000-0000-0000-000000000001"
    inst = DEFAULT_INSTITUTIONS[default_id]
    return inst["institution_id"], inst["name"], inst["city"], inst["state"]


def resolve_bureau(bureau_name: str) -> Tuple[str, str, int]:
    """
    Resolves bureau details by name.
    Returns (bureau_id, bureau_name, sla_response_hours).
    """
    # Try PostgreSQL lookup
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT bureau_id, bureau_name, sla_response_hours FROM bureaus WHERE bureau_name = %s;",
                    (bureau_name,)
                )
                row = cur.fetchone()
                conn.close()
                if row:
                    return str(row[0]), row[1], int(row[2])
        except Exception:
            conn.close()

    # Fallback to configured defaults
    bureau_info = DEFAULT_BUREAUS.get(bureau_name, DEFAULT_BUREAUS["Generic Bureau"])
    return bureau_info["bureau_id"], bureau_info["name"], bureau_info["sla_response_hours"]


def save_complaint_and_audit(
    title: str,
    description: str,
    complainant_role: str,
    complainant_email: str,
    complainant_phone: Optional[str],
    institution_id: str,
    institution_name: str,
    institution_city: str,
    institution_state: str,
    bureau_id: str,
    bureau_name: str,
    priority: str,
    status: str,
    is_duplicate: bool,
    master_complaint_id: Optional[str],
    sla_deadline: datetime,
) -> Dict[str, Any]:
    """
    Saves a registered complaint and initializes its primary audit trail log.
    Executes in PostgreSQL transaction; also updates in-memory registry.
    """
    new_complaint_id = str(uuid.uuid4())
    ticket_seq = len(MEMORY_COMPLAINTS) + 101
    tracking_id = f"GRV-2026-{ticket_seq:05d}"
    now_iso = datetime.now(timezone.utc).isoformat()
    deadline_iso = sla_deadline.isoformat()

    # 1. Attempt PostgreSQL write
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO complaints (
                        complaint_id, title, description, complainant_role,
                        complainant_email, complainant_phone, institution_id,
                        bureau_id, priority, status, is_duplicate,
                        master_complaint_id, sla_deadline, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
                    """,
                    (
                        new_complaint_id,
                        title,
                        description,
                        complainant_role,
                        complainant_email,
                        complainant_phone,
                        institution_id,
                        bureau_id,
                        priority,
                        status,
                        is_duplicate,
                        master_complaint_id,
                        sla_deadline,
                    )
                )

                log_id = str(uuid.uuid4())
                audit_remark = f"AI Triage routed to {bureau_name}. Priority set to {priority}."
                if is_duplicate:
                    audit_remark += f" Flagged as duplicate of master ticket {master_complaint_id}."

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
                        new_complaint_id,
                        "REGISTERED_AND_TRIAGED",
                        bureau_id,
                        audit_remark,
                        "AICTE_NLP_ROUTER_V1",
                    )
                )
                conn.commit()
                conn.close()
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            print(f"[Database Service] Notice: PostgreSQL insert failed ({e}). Storing in local store.")

    # 2. Persist in memory store
    record = {
        "complaint_id": new_complaint_id,
        "tracking_id": tracking_id,
        "title": title,
        "description": description,
        "complainant_role": complainant_role,
        "complainant_email": complainant_email,
        "complainant_phone": complainant_phone,
        "institution_id": institution_id,
        "institution_name": institution_name,
        "institution_city": institution_city,
        "institution_state": institution_state,
        "bureau_id": bureau_id,
        "bureau_name": bureau_name,
        "priority": priority,
        "status": status,
        "is_duplicate": is_duplicate,
        "master_complaint_id": master_complaint_id,
        "sla_deadline": deadline_iso,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    MEMORY_COMPLAINTS[new_complaint_id] = record
    MEMORY_COMPLAINTS[tracking_id] = record

    audit_entry = {
        "log_id": str(uuid.uuid4()),
        "complaint_id": new_complaint_id,
        "action_taken": "REGISTERED_AND_TRIAGED",
        "from_bureau_id": None,
        "to_bureau_id": bureau_id,
        "from_bureau_name": None,
        "to_bureau_name": bureau_name,
        "officer_remarks": f"AI Triage routed to {bureau_name}. Dynamic priority: {priority}.",
        "actor_id": "AICTE_NLP_ROUTER_V1",
        "timestamp": now_iso,
    }
    # 3. Register ticket in Redis SLA Watchtower sorted set
    try:
        from services.watchtower import schedule_ticket_in_watchtower
        schedule_ticket_in_watchtower(new_complaint_id, sla_deadline.timestamp())
    except Exception as e:
        print(f"[Database Service] Notice: Could not schedule in watchtower ({e})")

    return record


def get_complaint_by_id_or_tracking(identifier: str) -> Optional[Dict[str, Any]]:
    """
    Fetches complaint details and audit timeline by complaint_id or tracking_id.
    """
    # 1. Try PostgreSQL lookup
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        c.complaint_id, c.title, c.description, c.complainant_role,
                        c.complainant_email, c.complainant_phone, c.institution_id,
                        i.name AS institution_name, i.city AS institution_city, i.state AS institution_state,
                        c.bureau_id, b.bureau_name, c.priority, c.status,
                        c.is_duplicate, c.master_complaint_id, c.sla_deadline,
                        c.created_at, c.updated_at
                    FROM complaints c
                    LEFT JOIN institutions i ON c.institution_id = i.institution_id
                    LEFT JOIN bureaus b ON c.bureau_id = b.bureau_id
                    WHERE c.complaint_id::text = %s;
                    """,
                    (identifier,)
                )
                row = cur.fetchone()
                if row:
                    complaint_data = {
                        "complaint_id": str(row[0]),
                        "tracking_id": f"GRV-2026-{str(row[0])[:8].upper()}",
                        "title": row[1],
                        "description": row[2],
                        "complainant_role": row[3],
                        "complainant_email": row[4],
                        "complainant_phone": row[5],
                        "institution_id": str(row[6]),
                        "institution_name": row[7],
                        "institution_city": row[8],
                        "institution_state": row[9],
                        "bureau_id": str(row[10]),
                        "bureau_name": row[11],
                        "priority": row[12],
                        "status": row[13],
                        "is_duplicate": row[14],
                        "master_complaint_id": str(row[15]) if row[15] else None,
                        "sla_deadline": row[16].isoformat() if row[16] else None,
                        "created_at": row[17].isoformat() if row[17] else None,
                        "updated_at": row[18].isoformat() if row[18] else None,
                        "timeline": [],
                    }

                    # Fetch timeline audit logs
                    cur.execute(
                        """
                        SELECT 
                            l.log_id, l.action_taken, l.from_bureau_id, l.to_bureau_id,
                            b1.bureau_name AS from_bureau_name, b2.bureau_name AS to_bureau_name,
                            l.officer_remarks, l.actor_id, l.timestamp
                        FROM complaint_audit_logs l
                        LEFT JOIN bureaus b1 ON l.from_bureau_id = b1.bureau_id
                        LEFT JOIN bureaus b2 ON l.to_bureau_id = b2.bureau_id
                        WHERE l.complaint_id::text = %s
                        ORDER BY l.timestamp ASC;
                        """,
                        (identifier,)
                    )
                    log_rows = cur.fetchall()
                    conn.close()

                    complaint_data["timeline"] = [
                        {
                            "log_id": str(lr[0]),
                            "action_taken": lr[1],
                            "from_bureau_id": str(lr[2]) if lr[2] else None,
                            "to_bureau_id": str(lr[3]) if lr[3] else None,
                            "from_bureau_name": lr[4],
                            "to_bureau_name": lr[5],
                            "officer_remarks": lr[6],
                            "actor_id": lr[7],
                            "timestamp": lr[8].isoformat() if lr[8] else None,
                        }
                        for lr in log_rows
                    ]
                    return complaint_data
                conn.close()
        except Exception:
            if conn:
                conn.close()

    # 2. Fallback to memory store
    if identifier in MEMORY_COMPLAINTS:
        complaint_data = dict(MEMORY_COMPLAINTS[identifier])
        actual_id = complaint_data["complaint_id"]
        complaint_data["timeline"] = MEMORY_AUDIT_LOGS.get(actual_id, [])
        return complaint_data

    # Case-insensitive lookup across tracking_id and complaint_id
    id_upper = identifier.strip().upper()
    id_lower = identifier.strip().lower()
    for c in MEMORY_COMPLAINTS.values():
        if c.get("tracking_id", "").upper() == id_upper or c.get("complaint_id", "").lower() == id_lower:
            complaint_data = dict(c)
            actual_id = complaint_data["complaint_id"]
            complaint_data["timeline"] = MEMORY_AUDIT_LOGS.get(actual_id, [])
            return complaint_data

    return None
