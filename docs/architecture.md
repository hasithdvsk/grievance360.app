# 🏛️ System Architecture - Grievance360

This document defines the high-level architecture, data pipeline, and asynchronous task execution model of the Grievance360 platform.

---

## 📐 Architecture Diagram

```mermaid
flowchart TD
    subgraph ClientLayer ["Client Layer"]
        CitizenBrowser["Citizen / Student Web Portal\n(Next.js 14 App Router)"]
        OfficialPortal["AICTE Officer Dashboard\n(Recharts & Framer Motion)"]
    end

    subgraph APILayer ["Backend API Layer"]
        FastAPIServer["FastAPI Async Gateway\n(Port 8000)"]
        CorsAuth["Auth & Validation Middleware\n(Pydantic v2)"]
    end

    subgraph ServiceLayer ["Processing & AI Layer"]
        SentenceTransformers["Semantic NLP Engine\n(all-MiniLM-L6-v2)"]
        CeleryWorker["Celery Distributed Workers\n(Redis Broker)"]
        WatchtowerService["SLA Escalation Watchtower\n(Redis Sorted Set)"]
        DispatchGateway["Alert Dispatch Gateway\n(SMS & Email Mock)"]
    end

    subgraph StorageLayer ["Persistence & Broker Layer"]
        PostgreSQL[("PostgreSQL 16 + PostGIS\n(WGS 84 Geographies)")]
        RedisBroker[("Redis 7\n(Broker & 'sla_watchtower' Set)")]
    end

    CitizenBrowser -->|REST / JSON| FastAPIServer
    OfficialPortal -->|REST / JSON| FastAPIServer
    FastAPIServer --> CorsAuth
    CorsAuth --> SentenceTransformers
    CorsAuth --> PostgreSQL
    FastAPIServer -->|Register Score = SLA Deadline| RedisBroker
    RedisBroker -->|Poll Breached Tickets| WatchtowerService
    WatchtowerService -->|Update Status = ESCALATED| PostgreSQL
    WatchtowerService -->|Trigger Alert Task| CeleryWorker
    CeleryWorker --> DispatchGateway
    DispatchGateway -->|Log Sent Status| PostgreSQL
```

---

## 🔄 Grievance Lifecycle & AI Pipeline

1. **Intake**: Citizen/student submits grievance via Next.js form with institution and category.
2. **Semantic Embedding**: FastAPI passes textual description to `sentence-transformers` (`all-MiniLM-L6-v2`) to generate vector representations.
3. **Duplicate Detection**: Cosine similarity check against recent complaints. If similarity > 0.85, flags ticket as a likely duplicate.
4. **Automated Triage & Routing**:
   - Compares cosine similarity with AICTE Bureau semantic profiles (*Anti-Ragging*, *Approval*, *Finance*, *Legal*, *Generic*).
   - Detects urgent keywords (`suicide`, `ragging`, `threat`, `violence`, `bribe`) to assign **`CRITICAL`** priority.
5. **Redis SLA Watchtower**:
   - Complaint ID is added to Redis sorted set `sla_watchtower` with score equal to epoch timestamp of `sla_deadline`.
   - Celery worker periodically executes `scan_and_escalate_breached_slas()`.
   - Tickets past deadline are escalated to `ESCALATED`, priority set to `CRITICAL`, system audit log inserted, and `send_dispatch_alert()` dispatches SMS/email.
6. **Resolution & Certificate**: Upon officer sign-off, resolution notice and audit trail are finalized.
