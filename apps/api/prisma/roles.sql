-- ============================================================
-- Database roles for the application. Run once per environment
-- by an operator (not by Prisma migrate - role/credential
-- provisioning is infra, not schema).
--
-- Two roles:
--
-- 1. clinic_crm (the Prisma migration + normal runtime role)
--    Owns the schema. Subject to RLS on every tenant table
--    because those tables use FORCE ROW LEVEL SECURITY.
--
-- 2. clinic_crm_auth (BYPASSRLS, tightly scoped by GRANTs)
--    Used ONLY by AuthService for the identity-resolution step
--    that happens before an organization_id is known: looking up
--    a user by email during login/magic-link, and creating the
--    organization + first owner user during registration. This is
--    an intentional, narrow, audited exception to tenant isolation
--    - it is not used anywhere else in the codebase, and it has no
--    grants on contacts/appointments/contact_activities/audit_log
--    at all, so even a bug in AuthService cannot leak clinical data
--    across tenants through this role - at most it could leak the
--    existence of an email address, which the login flow itself
--    already reveals via "no account with that email" vs generic
--    errors (kept deliberately generic in AuthService to avoid
--    even that).
-- ============================================================

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'clinic_crm_auth') THEN
    CREATE ROLE clinic_crm_auth WITH LOGIN PASSWORD 'clinic_crm_auth' BYPASSRLS;
  END IF;
END
$$;

GRANT SELECT, INSERT, UPDATE ON organizations TO clinic_crm_auth;
GRANT SELECT, INSERT, UPDATE ON users TO clinic_crm_auth;
GRANT SELECT ON roles, permissions, role_permissions TO clinic_crm_auth;
GRANT SELECT, INSERT ON user_roles TO clinic_crm_auth;
GRANT SELECT, INSERT, UPDATE, DELETE ON magic_link_tokens TO clinic_crm_auth;
