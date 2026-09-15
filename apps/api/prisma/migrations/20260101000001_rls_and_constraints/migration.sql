-- ============================================================
-- Double-booking prevention: a provider cannot have two
-- non-cancelled appointments with overlapping time ranges.
-- ============================================================
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE "appointments"
  ADD CONSTRAINT "appointments_no_double_booking"
  EXCLUDE USING gist (
    "provider_user_id" WITH =,
    tstzrange("starts_at", "ends_at") WITH &&
  ) WHERE ("status" <> 'cancelled');

-- ============================================================
-- Row-Level Security: tenant isolation, enforced in the database
-- itself (not just application code), per the multi-tenant
-- architecture requirement.
--
-- FORCE ROW LEVEL SECURITY is used (not just ENABLE) because
-- Postgres normally exempts the table-owning role from RLS.
-- Since Prisma migrations run as the owning role, ENABLE alone
-- would silently let the app's own connection bypass isolation.
-- FORCE closes that gap; only an actual superuser/BYPASSRLS role
-- would still bypass it, and the app's runtime DB user must never
-- be granted that.
--
-- The app sets `app.current_org_id` via `SET LOCAL` at the start
-- of every request transaction (see TenantPrismaService). Prisma
-- middleware also injects `organization_id` filters independently
-- as a second, redundant layer - see prisma.middleware.ts.
--
-- Tables without a direct organization_id column (contact_tags,
-- role_permissions, staff_locations) are pure join tables that are
-- never queried standalone by the API - always scoped through
-- their parent (contact, role, user), which IS RLS-protected.
-- magic_link_tokens is intentionally excluded: it's looked up by
-- an unguessable token hash during the pre-authentication login
-- flow, before any organization context exists.
-- ============================================================

CREATE OR REPLACE FUNCTION current_org_id() RETURNS TEXT AS $$
  SELECT NULLIF(current_setting('app.current_org_id', true), '')
$$ LANGUAGE sql STABLE;

-- organizations: a connection may only see the single org it is scoped to
ALTER TABLE "organizations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "organizations" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "organizations"
  USING ("id" = current_org_id());

ALTER TABLE "locations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "locations" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "locations"
  USING ("organization_id" = current_org_id());

ALTER TABLE "users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "users" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "users"
  USING ("organization_id" = current_org_id());

-- roles: org-owned rows are tenant-scoped; system-default templates
-- (organization_id IS NULL) are visible to every tenant as read-only
-- catalog entries, same as `permissions`.
ALTER TABLE "roles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "roles" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "roles"
  USING ("organization_id" IS NULL OR "organization_id" = current_org_id());

ALTER TABLE "user_roles" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "user_roles" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "user_roles"
  USING ("organization_id" = current_org_id());

ALTER TABLE "pipeline_stages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "pipeline_stages" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "pipeline_stages"
  USING ("organization_id" = current_org_id());

ALTER TABLE "contacts" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "contacts" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "contacts"
  USING ("organization_id" = current_org_id());

ALTER TABLE "tags" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "tags" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "tags"
  USING ("organization_id" = current_org_id());

ALTER TABLE "contact_activities" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "contact_activities" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "contact_activities"
  USING ("organization_id" = current_org_id());

ALTER TABLE "services" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "services" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "services"
  USING ("organization_id" = current_org_id());

ALTER TABLE "appointments" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "appointments" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "appointments"
  USING ("organization_id" = current_org_id());

ALTER TABLE "audit_log" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "audit_log" FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON "audit_log"
  USING ("organization_id" = current_org_id());
