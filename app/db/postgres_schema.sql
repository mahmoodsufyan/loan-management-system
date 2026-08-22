-- ============================================================================
-- Enterprise Loan & Credit Management Platform - Modern PostgreSQL DDL Schema
-- Converted & Modernized from Oracle APEX / PL/SQL Architecture
-- ============================================================================

-- 1. Enable UUID Extension (Optional for UUID Primary Keys)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Loan Applications Core Table
CREATE TABLE IF NOT EXISTS loan_applications (
    id VARCHAR(30) PRIMARY KEY,
    applicant_name VARCHAR(150) NOT NULL,
    national_id VARCHAR(50) NOT NULL,
    product_type VARCHAR(80) NOT NULL DEFAULT 'Microfinance / SME',
    status VARCHAR(40) NOT NULL DEFAULT 'DRAFT',
    principal NUMERIC(14, 2) NOT NULL CHECK (principal > 0),
    annual_rate NUMERIC(6, 2) NOT NULL CHECK (annual_rate >= 0),
    tenor_months INT NOT NULL CHECK (tenor_months > 0),
    method VARCHAR(50) NOT NULL DEFAULT 'EQUAL_INSTALLMENTS',
    frequency VARCHAR(30) NOT NULL DEFAULT 'MONTHLY',
    grace_period_months INT NOT NULL DEFAULT 0 CHECK (grace_period_months >= 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_loan_national_id ON loan_applications(national_id);
CREATE INDEX IF NOT EXISTS idx_loan_status ON loan_applications(status);
CREATE INDEX IF NOT EXISTS idx_loan_created_at ON loan_applications(created_at DESC);

-- 3. Audit Logs & State Transitions Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    loan_id VARCHAR(30) NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    from_status VARCHAR(40),
    to_status VARCHAR(40) NOT NULL,
    actor VARCHAR(80) NOT NULL DEFAULT 'System',
    notes TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_loan_id ON audit_logs(loan_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);

-- 4. Dynamic RBAC Matrix Table (Page/Button level authorization)
CREATE TABLE IF NOT EXISTS dynamic_rbac_rules (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    component_name VARCHAR(100) NOT NULL,
    action_name VARCHAR(50) NOT NULL,
    is_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_role_component_action UNIQUE (role_name, component_name, action_name)
);

CREATE INDEX IF NOT EXISTS idx_rbac_role_comp ON dynamic_rbac_rules(role_name, component_name);

-- 5. Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trg_update_loan_timestamp ON loan_applications;
CREATE TRIGGER trg_update_loan_timestamp
    BEFORE UPDATE ON loan_applications
    FOR EACH ROW
    EXECUTE PROCEDURE update_timestamp_column();

-- 6. Seed Default RBAC Security Matrix
INSERT INTO dynamic_rbac_rules (role_name, component_name, action_name, is_allowed) VALUES
('BRANCH_OFFICER', 'LOAN_APPLICATION_FORM', 'CREATE_DRAFT', TRUE),
('BRANCH_OFFICER', 'LOAN_APPLICATION_FORM', 'SUBMIT', TRUE),
('CREDIT_ANALYST', 'CREDIT_REVIEW_PANEL', 'CREDIT_REVIEW', TRUE),
('BRANCH_MANAGER', 'APPROVAL_WORKFLOW', 'APPROVE', TRUE),
('BRANCH_MANAGER', 'APPROVAL_WORKFLOW', 'REJECT', TRUE),
('DISBURSEMENT_OFFICER', 'TREASURY_PANEL', 'DISBURSE', TRUE),
('FINANCIAL_AUDITOR', 'REPORTS_PANEL', 'EXPORT_PDF', TRUE)
ON CONFLICT (role_name, component_name, action_name) DO NOTHING;
