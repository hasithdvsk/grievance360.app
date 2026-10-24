# 🗄️ Database Schemas & Geospatial Migrations (`packages/db`)

This package houses the PostgreSQL + PostGIS database schema, spatial indexes, DDL definitions, and seed data for the **Grievance360 AICTE Grievance Redressal Platform**.

---

## 🗺️ Geospatial Features (PostGIS)

- **EPSG:4326 (WGS 84)**: All institution locations are stored as `GEOGRAPHY(POINT, 4326)` for accurate ellipsoidal spatial distance calculations across India.
- **Spatial Indexing**: Indexed via PostGIS **GIST** index (`idx_institutions_location`) enabling sub-millisecond proximity lookups, bounding box queries, and regional density clustering.

---

## 🗂️ Relational Schema Details

### 1. `bureaus`
Stores the central administrative divisions of AICTE responsible for grievance redressal:
- `bureau_id` (UUID, Primary Key)
- `bureau_name` (VARCHAR, Unique): Anti-Ragging Bureau, Approval Bureau, Finance Bureau, Legal Bureau, Generic Bureau
- `head_officer_email` (VARCHAR)
- `sla_response_hours` (INT): Default resolution threshold (e.g. 24h, 48h, 72h)
- `created_at` / `updated_at` (TIMESTAMPTZ)

### 2. `institutions`
AICTE-approved educational institutions with geographic coordinates:
- `institution_id` (UUID, Primary Key)
- `aicte_id` (VARCHAR, Unique): Official AICTE institution identifier (e.g., `1-10001001`)
- `name` (VARCHAR)
- `state` (VARCHAR)
- `city` (VARCHAR)
- `location` (`GEOGRAPHY(POINT, 4326)`): Longitude and Latitude point
- `compliance_score` (NUMERIC(5, 2)): Current institution compliance rating (0 - 100)
- `created_at` / `updated_at` (TIMESTAMPTZ)

### 3. `complaints`
Central grievance log with priority enums and bureau routing:
- `complaint_id` (UUID, Primary Key)
- `title` (VARCHAR)
- `description` (TEXT)
- `complainant_role` (VARCHAR): STUDENT, FACULTY, STAFF, PARENTS, CITIZEN
- `complainant_email` (VARCHAR)
- `complainant_phone` (VARCHAR)
- `institution_id` (UUID, FK -> `institutions.institution_id`)
- `bureau_id` (UUID, FK -> `bureaus.bureau_id`)
- `priority` (`complaint_priority` ENUM: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- `status` (`complaint_status` ENUM: `SUBMITTED`, `AUTO_ASSIGNED`, `IN_PROGRESS`, `ACTION_TAKEN`, `RESOLVED`, `ESCALATED`)
- `is_duplicate` (BOOLEAN)
- `master_complaint_id` (UUID, Self-referential FK -> `complaints.complaint_id`)
- `sla_deadline` (TIMESTAMPTZ)
- `created_at` / `updated_at` (TIMESTAMPTZ)

### 4. `complaint_audit_logs`
Chronological event ledger and inter-bureau escalation timeline:
- `log_id` (UUID, Primary Key)
- `complaint_id` (UUID, FK -> `complaints.complaint_id`)
- `action_taken` (VARCHAR)
- `from_bureau_id` (UUID, FK -> `bureaus.bureau_id`)
- `to_bureau_id` (UUID, FK -> `bureaus.bureau_id`)
- `officer_remarks` (TEXT)
- `actor_id` (VARCHAR)
- `timestamp` (TIMESTAMPTZ)

---

## ⚡ Useful PostGIS Query Examples

### Find All Institutions within 50km of a Given Point
```sql
SELECT 
    aicte_id,
    name,
    city,
    state,
    ROUND((ST_Distance(location, ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326)::geography) / 1000)::numeric, 2) AS distance_km
FROM institutions
WHERE ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326)::geography,
    50000 -- 50 km in meters
)
ORDER BY distance_km ASC;
```

### Find Closest Institution to a Given Location
```sql
SELECT 
    name,
    city,
    ST_AsText(location) AS coordinates,
    ST_Distance(location, ST_SetSRID(ST_MakePoint(72.8777, 19.0760), 4326)::geography) AS distance_meters
FROM institutions
ORDER BY location <-> ST_SetSRID(ST_MakePoint(72.8777, 19.0760), 4326)::geography
LIMIT 1;
```

---

## 🚀 Running Locally with Docker Compose

When launching via `docker-compose up`, the PostGIS image automatically executes both SQL scripts in sequence:
1. `01_schema.sql` -> creates extensions, enums, tables, and spatial GIST indexes.
2. `02_seed.sql` -> seeds 5 AICTE Bureaus, 10 Indian educational institutions, sample complaints, and audit logs.
