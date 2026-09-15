# Clinic CRM — Phase 1 (Core CRM)

Multi-tenant CRM for dental/wellness clinics. See [`docs/phase1-schema-and-api.md`](docs/phase1-schema-and-api.md) for the full schema, API contract, and the tenant-isolation design this is built on.

## Stack

- **API**: NestJS + Prisma + PostgreSQL (`apps/api`)
- **Web**: Next.js (App Router) + Tailwind (`apps/web`)
- **Jobs/cache**: Redis (wired via `docker-compose.yml`; not yet used by Phase 1 code — reserved for Phase 2 reminders)

## Tenant isolation (read this before touching the schema)

Every tenant table has **Postgres Row-Level Security**, forced even for the owning role (`FORCE ROW LEVEL SECURITY`), keyed off `app.current_org_id` — set once per request by `TenantContextInterceptor` inside a transaction that wraps the whole request. Application code additionally repeats `organizationId` filters explicitly as a second, redundant layer. See `prisma/migrations/20260101000001_rls_and_constraints/migration.sql` and `src/tenancy/` in `apps/api`.

Two Postgres roles exist (`apps/api/prisma/roles.sql`):
- `clinic_crm` — normal app runtime role, subject to RLS.
- `clinic_crm_auth` — narrowly-scoped `BYPASSRLS` role used *only* by `AuthService`, for the one place tenant scoping is structurally impossible (resolving a user's org from their email before login).

## Local setup

Requires Node 22+, PostgreSQL 16+ (with `citext`, `pg_trgm`, `btree_gist` extensions), and Redis (optional for Phase 1).

```bash
npm install

# 1. Create the database, extensions, and the auth-bypass role
createdb clinic_crm
psql -d clinic_crm -c "CREATE EXTENSION IF NOT EXISTS citext; CREATE EXTENSION IF NOT EXISTS pg_trgm; CREATE EXTENSION IF NOT EXISTS btree_gist;"
psql -d clinic_crm -f apps/api/prisma/roles.sql

# 2. Configure env vars
cp apps/api/.env.example apps/api/.env      # edit DATABASE_URL/AUTH_DATABASE_URL if needed
cp apps/web/.env.local.example apps/web/.env.local

# 3. Run migrations + seed the permissions/system-roles catalog
cd apps/api
npx prisma migrate deploy
npx prisma generate
npm run prisma:seed
cd ../..

# 4. Run both apps
npm run dev:api   # http://localhost:3001/api/v1
npm run dev:web   # http://localhost:3000
```

Or bring up Postgres/Redis via Docker instead of a local install: `docker compose up -d`.

## Tests

```bash
cd apps/api
npm run test:e2e   # tenant isolation, RBAC (incl. live permission revocation), double-booking
```

The e2e suite runs against a real Postgres database (RLS and the appointments EXCLUDE constraint only mean something against the real thing) — point `DATABASE_URL`/`AUTH_DATABASE_URL` at a disposable database before running it against anything you care about.

## What's deliberately out of scope for Phase 1

- `messages`, `invoices`, `payments`, `subscriptions` and all SMS/WhatsApp/Stripe integration — Phase 2.
- Real working-hours/schedule entity — `AppointmentsService.availability()` uses a placeholder fixed 09:00–18:00 UTC window; see the comment there.
- Cross-location reporting, SaaS subscription billing, super-admin panel — Phase 3.
- Production transactional email — `MailService` logs magic-link/invite links to the console when `SMTP_HOST` isn't set; wiring a real provider is a Phase 2 decision (see `docs/phase1-schema-and-api.md`).
