-- =============================================================================
-- Grievance360 - AICTE Grievance Redressal Platform Seed Fixtures
-- Seeds: 5 AICTE Bureaus, 10 Indian Higher Educational Institutions (PostGIS Geographies),
-- Sample Complaints, and Complaint Audit Logs
-- =============================================================================

-- 1. Seed 5 Official AICTE Bureaus
INSERT INTO bureaus (bureau_id, bureau_name, head_officer_email, sla_response_hours)
VALUES
    (
        '10000000-0000-0000-0000-000000000001',
        'Anti-Ragging Bureau',
        'antiragging.head@aicte-india.org',
        24
    ),
    (
        '10000000-0000-0000-0000-000000000002',
        'Approval Bureau',
        'approval.head@aicte-india.org',
        48
    ),
    (
        '10000000-0000-0000-0000-000000000003',
        'Finance Bureau',
        'finance.head@aicte-india.org',
        72
    ),
    (
        '10000000-0000-0000-0000-000000000004',
        'Legal Bureau',
        'legal.head@aicte-india.org',
        96
    ),
    (
        '10000000-0000-0000-0000-000000000005',
        'Generic Bureau',
        'generic.cell@aicte-india.org',
        48
    )
ON CONFLICT (bureau_name) DO UPDATE
SET head_officer_email = EXCLUDED.head_officer_email,
    sla_response_hours = EXCLUDED.sla_response_hours;


-- 2. Seed 10 Prestigious Indian Educational Institutions with Valid PostGIS Spatial Points
-- Coordinate format: ST_SetSRID(ST_MakePoint(Longitude, Latitude), 4326)::geography
INSERT INTO institutions (institution_id, aicte_id, name, state, city, location, compliance_score)
VALUES
    (
        '20000000-0000-0000-0000-000000000001',
        '1-10001001',
        'Indian Institute of Technology Delhi (IIT Delhi)',
        'Delhi',
        'New Delhi',
        ST_SetSRID(ST_MakePoint(77.1926, 28.5450), 4326)::geography,
        98.50
    ),
    (
        '20000000-0000-0000-0000-000000000002',
        '1-10001002',
        'Indian Institute of Technology Bombay (IIT Bombay)',
        'Maharashtra',
        'Mumbai',
        ST_SetSRID(ST_MakePoint(72.9133, 19.1334), 4326)::geography,
        99.10
    ),
    (
        '20000000-0000-0000-0000-000000000003',
        '1-10001003',
        'Indian Institute of Technology Madras (IIT Madras)',
        'Tamil Nadu',
        'Chennai',
        ST_SetSRID(ST_MakePoint(80.2337, 12.9915), 4326)::geography,
        99.60
    ),
    (
        '20000000-0000-0000-0000-000000000004',
        '1-10001004',
        'Indian Institute of Science Bangalore (IISc Bangalore)',
        'Karnataka',
        'Bengaluru',
        ST_SetSRID(ST_MakePoint(77.5671, 13.0219), 4326)::geography,
        99.80
    ),
    (
        '20000000-0000-0000-0000-000000000005',
        '1-10001005',
        'Indian Institute of Technology Kharagpur (IIT KGP)',
        'West Bengal',
        'Kharagpur',
        ST_SetSRID(ST_MakePoint(87.3098, 22.3149), 4326)::geography,
        96.40
    ),
    (
        '20000000-0000-0000-0000-000000000006',
        '1-10001006',
        'Indian Institute of Technology Roorkee (IIT Roorkee)',
        'Uttarakhand',
        'Roorkee',
        ST_SetSRID(ST_MakePoint(77.8961, 29.8649), 4326)::geography,
        95.80
    ),
    (
        '20000000-0000-0000-0000-000000000007',
        '1-10001007',
        'National Institute of Technology Tiruchirappalli (NIT Trichy)',
        'Tamil Nadu',
        'Tiruchirappalli',
        ST_SetSRID(ST_MakePoint(78.8132, 10.7589), 4326)::geography,
        94.20
    ),
    (
        '20000000-0000-0000-0000-000000000008',
        '1-10001008',
        'Birla Institute of Technology and Science (BITS Pilani)',
        'Rajasthan',
        'Pilani',
        ST_SetSRID(ST_MakePoint(75.5873, 28.3639), 4326)::geography,
        93.70
    ),
    (
        '20000000-0000-0000-0000-000000000009',
        '1-10001009',
        'COEP Technological University',
        'Maharashtra',
        'Pune',
        ST_SetSRID(ST_MakePoint(73.8567, 18.5284), 4326)::geography,
        92.50
    ),
    (
        '20000000-0000-0000-0000-000000000010',
        '1-10001010',
        'Jadavpur University Faculty of Engineering & Technology',
        'West Bengal',
        'Kolkata',
        ST_SetSRID(ST_MakePoint(88.3713, 22.4989), 4326)::geography,
        91.80
    )
ON CONFLICT (aicte_id) DO UPDATE
SET name = EXCLUDED.name,
    state = EXCLUDED.state,
    city = EXCLUDED.city,
    location = EXCLUDED.location,
    compliance_score = EXCLUDED.compliance_score;


-- 3. Seed Realistic Sample Complaints
INSERT INTO complaints (
    complaint_id,
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
    sla_deadline,
    created_at
)
VALUES
    (
        '30000000-0000-0000-0000-000000000001',
        'Hostel curfew intimidation and verbal ragging of first-year boarders',
        'Senior hostel residents in Block C subjected new entrants to unpermitted late-night physical roll calls and verbal abuse.',
        'STUDENT',
        'victim.student@example.org',
        '+919811223344',
        '20000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        'CRITICAL',
        'IN_PROGRESS',
        FALSE,
        CURRENT_TIMESTAMP + INTERVAL '24 hours',
        CURRENT_TIMESTAMP - INTERVAL '4 hours'
    ),
    (
        '30000000-0000-0000-0000-000000000002',
        'Delay in disbursement of AICTE Pragati & Saksham Scholarship allowance',
        'Scholarship grant for academic semester 2 has not been credited despite verification from institute nodal officer.',
        'STUDENT',
        'scholarship.student@example.org',
        '+919822334455',
        '20000000-0000-0000-0000-000000000002',
        '10000000-0000-0000-0000-000000000003',
        'HIGH',
        'AUTO_ASSIGNED',
        FALSE,
        CURRENT_TIMESTAMP + INTERVAL '48 hours',
        CURRENT_TIMESTAMP - INTERVAL '8 hours'
    ),
    (
        '30000000-0000-0000-0000-000000000003',
        'Unauthorized intake expansion beyond sanctioned intake seats in CSE branch',
        'Department admitted 45 students over approved ceiling without statutory approval from AICTE Approval Bureau.',
        'FACULTY',
        'faculty.whistleblower@example.org',
        '+919833445566',
        '20000000-0000-0000-0000-000000000009',
        '10000000-0000-0000-0000-000000000002',
        'HIGH',
        'SUBMITTED',
        FALSE,
        CURRENT_TIMESTAMP + INTERVAL '48 hours',
        CURRENT_TIMESTAMP - INTERVAL '1 hour'
    )
ON CONFLICT (complaint_id) DO NOTHING;


-- 4. Seed Audit Logs for Complaint Lifecycle Tracking
INSERT INTO complaint_audit_logs (
    log_id,
    complaint_id,
    action_taken,
    from_bureau_id,
    to_bureau_id,
    officer_remarks,
    actor_id,
    timestamp
)
VALUES
    (
        '40000000-0000-0000-0000-000000000001',
        '30000000-0000-0000-0000-000000000001',
        'AUTO_TRIAGED_BY_AI',
        NULL,
        '10000000-0000-0000-0000-000000000001',
        'NLP semantic classifier detected severity keywords: curfew intimidation, ragging. Priority set to CRITICAL.',
        'SYSTEM_NLP_TRIAGE_WORKER',
        CURRENT_TIMESTAMP - INTERVAL '4 hours'
    ),
    (
        '40000000-0000-0000-0000-000000000002',
        '30000000-0000-0000-0000-000000000001',
        'NOTICE_SERVED_TO_INSTITUTION',
        '10000000-0000-0000-0000-000000000001',
        '10000000-0000-0000-0000-000000000001',
        'Formal inquiry email dispatched to Dean of Student Affairs. Proactive warden report requested within 12 hours.',
        'OFFICER_ANTIRAGGING_04',
        CURRENT_TIMESTAMP - INTERVAL '2 hours'
    )
ON CONFLICT (log_id) DO NOTHING;
