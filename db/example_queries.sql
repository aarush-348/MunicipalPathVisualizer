-- ====================================================================
-- Municipal Bureaucracy Path Visualizer
-- Example PostgreSQL Analytical and Graph Queries
-- ====================================================================

-- 1. List all services grouped by department with statutory SLA
SELECT 
    d.name AS department_name,
    s.sub_department,
    s.id AS service_id,
    s.service_name,
    s.processing_time_days AS statutory_sla_days,
    s.status
FROM services s
JOIN departments d ON s.department_id = d.id
ORDER BY d.name, s.processing_time_days ASC NULLS LAST;

-- 2. Retrieve statutory officer escalation matrix for a specific service
-- (Example: Caste Certificate, Service ID '1284')
SELECT 
    s.id AS service_id,
    s.service_name,
    o.officer_type,
    o.designation,
    o.contact_information,
    s.processing_time_days AS time_limit_days,
    o.source_url
FROM services s
JOIN officers o ON s.id = o.service_id
WHERE s.id = '1284'
ORDER BY 
    CASE o.officer_type
        WHEN 'Designated Officer' THEN 1
        WHEN 'First Appellate Officer' THEN 2
        WHEN 'Second Appellate Officer' THEN 3
        ELSE 4
    END;

-- 3. Retrieve all required documents for a service grouped by category and selection rule
-- (Example: Caste Certificate, Service ID '1284')
SELECT 
    d.category AS document_group,
    sd.group_rule,
    d.document_name,
    d.document_code,
    sd.mandatory,
    sd.source_url
FROM service_documents sd
JOIN documents d ON sd.document_id = d.id
WHERE sd.service_id = '1284'
ORDER BY d.category, d.document_name;

-- 4. Find all explicit service dependencies (Civic Procedural Graph Edges)
-- STRICT RULE: Only official citations established by government sources
SELECT 
    sd.service_id AS dependent_service_id,
    s1.service_name AS dependent_service_name,
    sd.depends_on_service_id AS prerequisite_service_id,
    sd.depends_on_service_name AS prerequisite_service_name,
    sd.dependency_type,
    sd.dependency_description,
    sd.source_url AS official_provenance_url
FROM service_dependencies sd
JOIN services s1 ON sd.service_id = s1.id
LEFT JOIN services s2 ON sd.depends_on_service_id = s2.id;

-- 5. Data Provenance & Verification Audit Trail
-- Verifies that every single record is traceable to official Aaple Sarkar URLs
SELECT 
    s.id AS service_id,
    s.service_name,
    d.name AS department,
    src.source_url,
    src.source_type,
    src.scraped_at,
    src.verified_at
FROM services s
JOIN departments d ON s.department_id = d.id
JOIN sources src ON s.id = src.service_id
ORDER BY s.id;

-- 6. Identify rapid citizen services (SLA <= 7 days)
SELECT 
    s.service_name,
    d.name AS department,
    s.sub_department,
    s.processing_time_days,
    o.designation AS designated_officer,
    s.source_url
FROM services s
JOIN departments d ON s.department_id = d.id
LEFT JOIN officers o ON s.id = o.service_id AND o.officer_type = 'Designated Officer'
WHERE s.processing_time_days <= 7
ORDER BY s.processing_time_days ASC;

-- 7. Recursive CTE: Full Dependency Hierarchy Path Visualizer
-- Traverses dependencies from prerequisite root to final outcome
WITH RECURSIVE dependency_chain AS (
    -- Anchor: Base prerequisites (services that other services depend on)
    SELECT 
        sd.service_id,
        s_dep.service_name,
        sd.depends_on_service_id,
        sd.depends_on_service_name,
        1 AS dependency_level,
        sd.depends_on_service_name || ' -> ' || s_dep.service_name AS path_trace
    FROM service_dependencies sd
    JOIN services s_dep ON sd.service_id = s_dep.id
    
    UNION ALL
    
    -- Recursive Step: Multi-hop dependencies
    SELECT 
        next_sd.service_id,
        next_s.service_name,
        next_sd.depends_on_service_id,
        next_sd.depends_on_service_name,
        dc.dependency_level + 1,
        dc.path_trace || ' -> ' || next_s.service_name
    FROM service_dependencies next_sd
    JOIN services next_s ON next_sd.service_id = next_s.id
    JOIN dependency_chain dc ON next_sd.depends_on_service_id = dc.service_id
)
SELECT 
    service_id,
    service_name,
    dependency_level,
    path_trace
FROM dependency_chain
ORDER BY dependency_level ASC;
