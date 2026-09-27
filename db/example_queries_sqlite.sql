-- ====================================================================
-- Municipal Bureaucracy Path Visualizer
-- SQLite Analytical & Procedural Dependency Graph Queries
-- Target Database: db/civic_maharashtra.db
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Search official Aaple Sarkar services by natural language keyword
-- --------------------------------------------------------------------
SELECT 
    s.service_id,
    s.service_name,
    s.department,
    s.sub_department,
    s.applicable_location,
    s.processing_time_days AS statutory_sla_days,
    s.application_method,
    s.application_url
FROM aaple_sarkar_services s
WHERE s.service_name LIKE '%Caste%' OR s.description LIKE '%Caste%'
ORDER BY s.processing_time_days ASC;

-- --------------------------------------------------------------------
-- 2. List all civic services grouped by department with SLA
-- --------------------------------------------------------------------
SELECT 
    d.name AS department_name,
    s.sub_department,
    s.service_id,
    s.service_name,
    s.processing_time_days AS statutory_sla_days,
    s.applicable_location
FROM aaple_sarkar_services s
JOIN departments d ON s.department = d.name
ORDER BY d.name, s.processing_time_days ASC;

-- --------------------------------------------------------------------
-- 3. End-to-End Procedural Pathway Query (Service -> Task -> Steps)
-- Example: Apply for Municipal Birth Certificate (BMC)
-- --------------------------------------------------------------------
SELECT 
    t.id AS task_id,
    t.title AS citizen_task_title,
    t.municipality,
    s.step_number,
    s.title AS step_title,
    d.name AS handling_department,
    s.submission_mode,
    s.estimated_days,
    s.fee_amount,
    s.prerequisites
FROM tasks t
JOIN steps s ON s.task_id = t.id
JOIN departments d ON s.department_id = d.id
WHERE t.id = 'task-bmc-birth-cert'
ORDER BY s.step_number ASC;

-- --------------------------------------------------------------------
-- 4. Retrieve complete Document Locker requirements for a Citizen Task
-- Example: Trade License (Section 394 MMC Act)
-- --------------------------------------------------------------------
SELECT 
    t.title AS task_name,
    s.step_number,
    s.title AS step_title,
    doc.name AS document_name,
    doc.category AS document_category,
    CASE doc.is_mandatory WHEN 1 THEN 'Mandatory' ELSE 'Optional' END AS requirement_type,
    doc.description AS document_description
FROM tasks t
JOIN steps s ON s.task_id = t.id
JOIN documents doc ON doc.step_id = s.id
WHERE t.id = 'task-trade-license'
ORDER BY s.step_number, doc.category, doc.name;

-- --------------------------------------------------------------------
-- 5. Retrieve Statutory Application Forms and Online Fill URLs
-- Example: Register a Small Business / Shop (Gumasta Act)
-- --------------------------------------------------------------------
SELECT 
    t.title AS task_name,
    s.step_number,
    s.title AS step_title,
    f.form_code,
    f.title AS form_title,
    f.fill_online_url,
    f.download_url
FROM tasks t
JOIN steps s ON s.task_id = t.id
JOIN forms f ON f.step_id = s.id
WHERE t.id = 'task-mah-small-biz'
ORDER BY s.step_number, f.form_code;

-- --------------------------------------------------------------------
-- 6. Rapid Citizen Services (Statutory SLA <= 3 days)
-- --------------------------------------------------------------------
SELECT 
    service_id,
    service_name,
    department,
    sub_department,
    processing_time_days,
    applicable_location,
    application_url
FROM aaple_sarkar_services
WHERE processing_time_days <= 3
ORDER BY processing_time_days ASC, service_name ASC;

-- --------------------------------------------------------------------
-- 7. Municipal Corporation (BMC) Specific Services
-- --------------------------------------------------------------------
SELECT 
    service_id,
    service_name,
    sub_department,
    processing_time_days,
    application_method,
    status
FROM aaple_sarkar_services
WHERE applicable_location LIKE '%BMC%' OR sub_department LIKE '%BMC%'
ORDER BY processing_time_days ASC;

-- --------------------------------------------------------------------
-- 8. Dependency Chain Traversal (Unlocking downstream steps)
-- Identifies steps that depend on prerequisite completion
-- --------------------------------------------------------------------
SELECT 
    s.task_id,
    s.step_number,
    s.title AS step_title,
    s.prerequisites,
    CASE 
        WHEN s.prerequisites = '[]' OR s.prerequisites IS NULL THEN 'ROOT STEP (Instantly Ready)'
        ELSE 'LOCKED (Requires ' || s.prerequisites || ')'
    END AS initial_state
FROM steps s
WHERE s.task_id = 'task-caste-certificate'
ORDER BY s.step_number ASC;

-- --------------------------------------------------------------------
-- 9. Database Integrity & Relational Verification (Zero Violations)
-- --------------------------------------------------------------------
-- Foreign key consistency:
PRAGMA foreign_keys = ON;
PRAGMA foreign_key_check;

-- Orphan steps check:
SELECT s.id, s.title FROM steps s
LEFT JOIN tasks t ON s.task_id = t.id
WHERE t.id IS NULL;

-- Orphan documents check:
SELECT d.id, d.name FROM documents d
LEFT JOIN steps s ON d.step_id = s.id
WHERE s.id IS NULL;

-- Orphan forms check:
SELECT f.id, f.title FROM forms f
LEFT JOIN steps s ON f.step_id = s.id
WHERE s.id IS NULL;
