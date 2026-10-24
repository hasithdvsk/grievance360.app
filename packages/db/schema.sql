-- =============================================================================
-- Grievance360 - AICTE Grievance Redressal Platform Database Schema
-- Production PostgreSQL DDL with PostGIS Geospatial Capabilities
-- =============================================================================

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- 2. Define Custom Enumerated Types
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'complaint_priority') THEN
        CREATE TYPE complaint_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'complaint_status') THEN
        CREATE TYPE complaint_status AS ENUM (
            'SUBMITTED',
            'AUTO_ASSIGNED',
            'IN_PROGRESS',
            'ACTION_TAKEN',
            'RESOLVED',
            'ESCALATED'
        );
    END IF;
END $$;

-- 3. AICTE Bureaus Table
CREATE TABLE IF NOT EXISTS bureaus (
    bureau_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bureau_name VARCHAR(255) UNIQUE NOT NULL,
    head_officer_email VARCHAR(255) NOT NULL,
    sla_response_hours INT NOT NULL DEFAULT 48,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Institutions Table with PostGIS Geography Point (EPSG:4326 WGS 84)
CREATE TABLE IF NOT EXISTS institutions (
    institution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aicte_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    state VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    compliance_score NUMERIC(5, 2) DEFAULT 100.00 CHECK (compliance_score >= 0.00 AND compliance_score <= 100.00),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. Complaints Main Table
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    complainant_role VARCHAR(64) NOT NULL DEFAULT 'STUDENT',
    complainant_email VARCHAR(255) NOT NULL,
    complainant_phone VARCHAR(32),
    institution_id UUID NOT NULL REFERENCES institutions(institution_id) ON DELETE RESTRICT,
    bureau_id UUID NOT NULL REFERENCES bureaus(bureau_id) ON DELETE RESTRICT,
    priority complaint_priority NOT NULL DEFAULT 'MEDIUM',
    status complaint_status NOT NULL DEFAULT 'SUBMITTED',
    is_duplicate BOOLEAN NOT NULL DEFAULT FALSE,
    master_complaint_id UUID REFERENCES complaints(complaint_id) ON DELETE SET NULL,
    sla_deadline TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. Complaint Audit Logs & Bureau Escalation Timeline
CREATE TABLE IF NOT EXISTS complaint_audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    complaint_id UUID NOT NULL REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    action_taken VARCHAR(128) NOT NULL,
    from_bureau_id UUID REFERENCES bureaus(bureau_id) ON DELETE SET NULL,
    to_bureau_id UUID REFERENCES bureaus(bureau_id) ON DELETE SET NULL,
    officer_remarks TEXT,
    actor_id VARCHAR(128),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. Performance & Geospatial Indexes
-- PostGIS Spatial GIST Index on Institutions Location
CREATE INDEX IF NOT EXISTS idx_institutions_location ON institutions USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_institutions_aicte_id ON institutions (aicte_id);
CREATE INDEX IF NOT EXISTS idx_institutions_state_city ON institutions (state, city);

-- Standard & Composite Query Optimization Indexes on Complaints
CREATE INDEX IF NOT EXISTS idx_complaints_bureau_id ON complaints (bureau_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints (status);
CREATE INDEX IF NOT EXISTS idx_complaints_sla_deadline ON complaints (sla_deadline);
CREATE INDEX IF NOT EXISTS idx_complaints_bureau_status ON complaints (bureau_id, status);
CREATE INDEX IF NOT EXISTS idx_complaints_institution_id ON complaints (institution_id);
CREATE INDEX IF NOT EXISTS idx_complaints_is_duplicate ON complaints (is_duplicate);
CREATE INDEX IF NOT EXISTS idx_complaints_created_at ON complaints (created_at DESC);

-- Audit Log Indexes
CREATE INDEX IF NOT EXISTS idx_complaint_audit_logs_complaint_id ON complaint_audit_logs (complaint_id);
CREATE INDEX IF NOT EXISTS idx_complaint_audit_logs_timestamp ON complaint_audit_logs (timestamp DESC);

-- Trigger function for automated updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_bureaus_updated_at ON bureaus;
CREATE TRIGGER trg_bureaus_updated_at
BEFORE UPDATE ON bureaus
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_institutions_updated_at ON institutions;
CREATE TRIGGER trg_institutions_updated_at
BEFORE UPDATE ON institutions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_complaints_updated_at ON complaints;
CREATE TRIGGER trg_complaints_updated_at
BEFORE UPDATE ON complaints
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
