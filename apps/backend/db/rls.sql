-- =========================================================================
-- SecureCopilot 365 — Row-Level Security (RLS) Configuration Schema
-- Targeted DBMS: Azure SQL Database / Microsoft SQL Server
-- =========================================================================

-- 1. Create a Schema for Security Functions
CREATE SCHEMA Security;
GO

-- 2. Create the Tenant Filter Predicate Function
-- This inline table-valued function checks if the current database session user context
-- matches the tenant_id of the row, or if the session is running under a global Super Admin scope.
CREATE FUNCTION Security.fn_TenantFilterPredicate(@tenant_id NVARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS fn_TenantFilterPredicate_Result
WHERE 
    -- Allow the row if it matches the current session context tenant_id
    DATABASE_PRINCIPAL_ID() = 1 -- System/SA override if necessary
    OR SESSION_CONTEXT(N'tenant_id') = @tenant_id
    -- Allow global operations from SaaS Super Admin context
    OR SESSION_CONTEXT(N'role') = N'Super Admin';
GO

-- 3. Apply the Security Policy to Telemetry Tables
CREATE SECURITY POLICY Security.TenantSecurityPolicy
    -- Employees
    ADD FILTER PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.employees,
    ADD BLOCK PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.employees AFTER INSERT,
    -- Vendors
    ADD FILTER PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.vendors,
    ADD BLOCK PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.vendors AFTER INSERT,
    -- Phishing Incidents
    ADD FILTER PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.phishing_incidents,
    ADD BLOCK PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.phishing_incidents AFTER INSERT,
    -- Compliance Queries
    ADD FILTER PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.compliance_queries,
    ADD BLOCK PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.compliance_queries AFTER INSERT,
    -- Audit Readiness
    ADD FILTER PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.audit_readiness,
    ADD BLOCK PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.audit_readiness AFTER INSERT,
    -- Training Completions
    ADD FILTER PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.training_completions,
    ADD BLOCK PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.training_completions AFTER INSERT,
    -- Audit Logs
    ADD FILTER PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.audit_logs,
    ADD BLOCK PREDICATE Security.fn_TenantFilterPredicate(tenant_id) ON dbo.audit_logs AFTER INSERT
    WITH (STATE = ON);
GO

-- =========================================================================
-- Developer Verification Queries
-- =========================================================================
-- To set session context in application code before running query:
-- EXEC sp_set_session_context 'tenant_id', 'tenant-alpha';
-- EXEC sp_set_session_context 'role', 'CISO';
-- SELECT * FROM dbo.vendors; -- Only alpha vendors are returned
-- =========================================================================
