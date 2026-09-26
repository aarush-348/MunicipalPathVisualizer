-- ====================================================================
-- Municipal Bureaucracy Path Visualizer
-- Database Schema for Aaple Sarkar Maharashtra Government Services
-- Target: PostgreSQL 14+
-- ====================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables in reverse dependency order if recreating
DROP TABLE IF EXISTS service_dependencies CASCADE;
DROP TABLE IF EXISTS sources CASCADE;
DROP TABLE IF EXISTS officers CASCADE;
DROP TABLE IF EXISTS fees CASCADE;
DROP TABLE IF EXISTS service_prerequisites CASCADE;
DROP TABLE IF EXISTS prerequisites CASCADE;
DROP TABLE IF EXISTS service_documents CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- 1. Departments Table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    department_code VARCHAR(50),
    source_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_name ON departments(name);

-- 2. Services Table
CREATE TABLE services (
    id VARCHAR(50) PRIMARY KEY, -- Official Aaple Sarkar Service ID (e.g. '1253', '1284')
    service_name VARCHAR(255) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    sub_department VARCHAR(255),
    description TEXT,
    eligibility TEXT,
    service_type VARCHAR(100) DEFAULT 'Citizen Service',
    application_method VARCHAR(150),
    application_url TEXT,
    processing_time_days INTEGER, -- Normalized statutory SLA in days
    processing_time_raw VARCHAR(100),
    applicable_location VARCHAR(255) DEFAULT 'Maharashtra State',
    status VARCHAR(100) DEFAULT 'Active Notified Service',
    source_url TEXT NOT NULL,
    source_title VARCHAR(255),
    last_scraped_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_services_dept ON services(department_id);
CREATE INDEX idx_services_name ON services(service_name);
CREATE INDEX idx_services_sla ON services(processing_time_days);

-- 3. Documents Master Table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    document_code VARCHAR(100), -- Portal element ID e.g. 'lbl_1_4607'
    document_name VARCHAR(500) NOT NULL,
    category VARCHAR(150), -- 'Proof of Identity', 'Proof of Address', 'Other Documents'
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_document_name_category UNIQUE (document_name, category)
);

CREATE INDEX idx_documents_name ON documents(document_name);
CREATE INDEX idx_documents_category ON documents(category);

-- 4. Service Documents Join Table (Many-to-Many with metadata)
CREATE TABLE service_documents (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    mandatory BOOLEAN DEFAULT TRUE,
    group_rule VARCHAR(100), -- 'Select 1', 'Mandatory', 'Conditional'
    notes TEXT,
    source_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_service_document UNIQUE (service_id, document_id)
);

CREATE INDEX idx_service_docs_service ON service_documents(service_id);
CREATE INDEX idx_service_docs_doc ON service_documents(document_id);

-- 5. Prerequisites Master Table
CREATE TABLE prerequisites (
    id SERIAL PRIMARY KEY,
    prerequisite_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Service Prerequisites Join Table
CREATE TABLE service_prerequisites (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    prerequisite_id INTEGER NOT NULL REFERENCES prerequisites(id) ON DELETE CASCADE,
    mandatory BOOLEAN DEFAULT TRUE,
    notes TEXT,
    source_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_service_prerequisite UNIQUE (service_id, prerequisite_id)
);

CREATE INDEX idx_service_prereq_service ON service_prerequisites(service_id);

-- 7. Fees Table
CREATE TABLE fees (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2), -- NULL if unspecified or free
    currency VARCHAR(10) DEFAULT 'INR',
    description TEXT,
    conditions TEXT,
    source_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fees_service ON fees(service_id);

-- 8. Officers Escalation Matrix Table
CREATE TABLE officers (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    officer_type VARCHAR(100) NOT NULL, -- 'Designated Officer', 'First Appellate Officer', 'Second Appellate Officer'
    officer_name VARCHAR(255), -- NULL if ex-officio statutory title
    designation VARCHAR(255) NOT NULL,
    contact_information TEXT,
    source_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_service_officer_type UNIQUE (service_id, officer_type)
);

CREATE INDEX idx_officers_service ON officers(service_id);
CREATE INDEX idx_officers_type ON officers(officer_type);

-- 9. Sources / Data Provenance Table
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    source_url TEXT NOT NULL,
    source_title VARCHAR(255),
    source_type VARCHAR(100) DEFAULT 'Official Government Portal',
    scraped_at TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_service ON sources(service_id);

-- 10. Service Dependencies Table (The Core Civic Dependency Graph Layer)
-- STRICT RULE: Only established relationships backed by official source citations are stored!
CREATE TABLE service_dependencies (
    id SERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES services(id) ON DELETE CASCADE, -- Dependent Service (B)
    depends_on_service_id VARCHAR(50) REFERENCES services(id) ON DELETE SET NULL, -- Prerequisite Service (A)
    depends_on_service_name VARCHAR(255) NOT NULL,
    dependency_type VARCHAR(100) NOT NULL, -- e.g. 'Prerequisite Certificate', 'Prerequisite Stage', 'Land Record Reference'
    dependency_description TEXT NOT NULL,
    source_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_service_dependency UNIQUE (service_id, depends_on_service_name)
);

CREATE INDEX idx_service_deps_service ON service_dependencies(service_id);
CREATE INDEX idx_service_deps_depends_on ON service_dependencies(depends_on_service_id);
