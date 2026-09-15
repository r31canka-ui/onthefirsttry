# Phase 1 — Database Schema & API Contract (Proposal)

Status: **CONFIRMED — implementation in progress.** Decisions locked in: NestJS + Prisma, Postgres RLS + app-layer tenant isolation (both layers, not app-layer-only), GDPR/EU-only compliance scope for now (HIPAA/US revisited if a US clinic signs).

This covers Phase 1 only (Core CRM): org/location setup, staff + RBAC, contact management, appointment scheduling, basic dashboard, search. Communications, billing, subscriptions, and multi-location reporting are intentionally out of scope here — they get their own schema/API proposals when Phase 1 ships.

---

## 1. Tech stack recommendation (needs your sign-off — see §6)

| Layer | Recommendation | Why |
|---|---|---|
| Backend | **NestJS** (TypeScript) | Built-in DI, guards/interceptors map directly onto RBAC + tenant-scoping enforcement, modular structure scales better than raw Express as this grows to 3 phases. |
| ORM | **Prisma** | Type-safe queries, first-class migrations, easy to add a query middleware that injects `organization_id` on every call (defense in depth on top of RLS). |
| DB | **PostgreSQL 15+** | As you specified — relational integrity for appointments/billing. |
| Tenant isolation | **Postgres Row-Level Security (RLS)** + app-layer scoping | Two independent layers: even a buggy/forgotten `WHERE organization_id = ?` in application code can't leak data, because the DB itself refuses cross-tenant rows. This is the strongest answer to "assume this will be audited." |
| Frontend | **Next.js + shadcn/ui + Tailwind** | Matches your spec, good tablet/mobile responsiveness out of the box. |
| Auth | Custom email/password + magic link via **Lucia** or hand-rolled JWT/session, TOTP (e.g. `otplib`) for 2FA on admin roles | Avoids vendor lock-in (Auth0/Clerk) while keeping it simple; can swap later. |
| Jobs | **BullMQ + Redis** | As specified — needed even in Phase 1 for things like invite emails, and sets up Phase 2 reminders cleanly. |
| Hosting | Docker containers, no vendor-specific services in app code | As specified. |

If your dev team already has strong opinions (e.g. Express over NestJS, Drizzle over Prisma), that's a fine swap — flagging that NestJS+Prisma is my default absent constraints, not a hard requirement.

---

## 2. Tenant isolation strategy (the most important section)

Every tenant-scoped table gets:

1. A non-nullable `organization_id UUID REFERENCES organizations(id)`.
2. `ENABLE ROW LEVEL SECURITY` + a policy: `organization_id = current_setting('app.current_org_id')::uuid`.
3. The app sets `SET LOCAL app.current_org_id = '<uuid>'` at the start of every request transaction, derived from the authenticated JWT — never from a client-supplied param.
4. A Prisma middleware that *also* injects `organization_id` into every `where` clause, as a second, independent layer — so a mistake in one layer doesn't equal a breach.
5. The Postgres role the app connects as has **no** `BYPASSRLS` privilege, and there is no code path that uses a superuser/admin connection for normal request handling. There are exactly two narrow, documented exceptions to that, both implemented (see `prisma/roles.sql`):
   - `clinic_crm_auth`: a second, tightly-scoped `BYPASSRLS` role used *only* by `AuthService`, for the one place tenant scoping is structurally impossible — resolving a user's `organization_id` from their email during login/magic-link/registration, before any org context exists. It has grants on `organizations`/`users`/`roles`/`user_roles`/`magic_link_tokens` only — no grant at all on `contacts`, `appointments`, `contact_activities`, or `audit_log`, so a bug in the auth path cannot leak clinical data.
   - A future Phase 3 super-admin connection, not yet implemented, which will log every use to `audit_log`.

**Concrete leak patterns to watch for during code review** (calling these out per your instruction 9.4):
- A report/aggregate query that does a `GROUP BY` or `JOIN` across `contacts`/`appointments` without an `organization_id` filter on *every* joined table (RLS covers this even if the filter is missing, but don't rely on RLS alone as an excuse to be sloppy).
- Any raw SQL (`$queryRaw` in Prisma) — RLS still applies, but confirm the DB session actually has `app.current_org_id` set before it runs; a raw query on a connection that skipped the middleware is the classic gap.
- Background jobs (BullMQ workers) — they run outside the HTTP request lifecycle, so each job payload must carry `organization_id` explicitly and the worker must set the RLS session variable itself before querying.
- Search/autocomplete endpoints — easy to accidentally query an index that isn't org-partitioned.
- The `roles` table's system-default rows (`organization_id IS NULL`) — make sure no query treats "null org_id" as a wildcard match against a tenant's data.

---

## 3. Schema (DDL)

```sql
-- ============ Organizations & Locations ============

CREATE TABLE organizations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  slug            TEXT NOT NULL UNIQUE,
  country_code    CHAR(2) NOT NULL,        -- drives GDPR vs HIPAA handling later
  default_locale  TEXT NOT NULL DEFAULT 'en', -- 'en' | 'sq'
  timezone        TEXT NOT NULL DEFAULT 'Europe/Tirane',
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE locations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  address         TEXT,
  city            TEXT,
  country_code    CHAR(2),
  timezone        TEXT NOT NULL,
  phone           TEXT,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON locations (organization_id);

-- ============ Users, RBAC ============

CREATE TABLE users (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id    UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email              CITEXT NOT NULL UNIQUE,
  password_hash      TEXT,               -- nullable: magic-link-only users
  full_name          TEXT NOT NULL,
  phone              TEXT,
  status             TEXT NOT NULL DEFAULT 'invited', -- invited | active | disabled
  two_factor_enabled BOOLEAN NOT NULL DEFAULT false,
  two_factor_secret  TEXT,               -- encrypted at rest (app-layer AES, not plaintext)
  last_login_at      TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON users (organization_id);

CREATE TABLE staff_locations (          -- which locations a staff member can work at / be scheduled
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, location_id)
);

CREATE TABLE permissions (              -- global catalog, NOT tenant-scoped
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key         TEXT NOT NULL UNIQUE,     -- e.g. 'contacts.read', 'clinical_notes.read', 'billing.read'
  description TEXT NOT NULL
);

CREATE TABLE roles (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id    UUID REFERENCES organizations(id) ON DELETE CASCADE, -- NULL = system default template
  name               TEXT NOT NULL,
  is_system_default  BOOLEAN NOT NULL DEFAULT false,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE role_permissions (
  role_id       UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE, -- denormalized for RLS
  PRIMARY KEY (user_id, role_id)
);

-- ============ Contacts (leads + patients, unified) ============

CREATE TABLE pipeline_stages (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  position        INT NOT NULL,
  is_won_stage    BOOLEAN NOT NULL DEFAULT false, -- reaching this stage flips contact.status -> active_patient
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (organization_id, position)
);

CREATE TABLE contacts (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id       UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  primary_location_id   UUID REFERENCES locations(id),
  first_name            TEXT NOT NULL,
  last_name             TEXT,
  email                 CITEXT,
  phone                 TEXT,
  status                TEXT NOT NULL DEFAULT 'lead', -- lead | active_patient | inactive
  source                TEXT,                          -- referral | ad | walk_in | other
  pipeline_stage_id     UUID REFERENCES pipeline_stages(id),
  assigned_to_user_id   UUID REFERENCES users(id),
  custom_fields         JSONB NOT NULL DEFAULT '{}',
  consent_recorded_at   TIMESTAMPTZ,     -- GDPR: explicit consent timestamp (special-category data)
  consent_notes         TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at            TIMESTAMPTZ      -- soft delete for normal "inactive"; see §5 for GDPR hard-erase
);
CREATE INDEX ON contacts (organization_id, status);
CREATE INDEX ON contacts (organization_id, pipeline_stage_id);
-- pg_trgm, not tsvector: contact search needs to match partial phone
-- numbers/emails ("0692...", "@gmail"), which token-based tsvector
-- search handles poorly; trigram similarity/ILIKE fits this better.
CREATE INDEX ON contacts USING gin ((coalesce(first_name,'') || ' ' || coalesce(last_name,'') || ' ' || coalesce(email,'') || ' ' || coalesce(phone,'')) gin_trgm_ops);

CREATE TABLE tags (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  color           TEXT,
  UNIQUE (organization_id, name)
);

CREATE TABLE contact_tags (
  contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
  tag_id     UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (contact_id, tag_id)
);

-- notes / activity timeline. is_clinical gates visibility per RBAC (front desk excluded by default)
CREATE TABLE contact_activities (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  contact_id      UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
  author_user_id  UUID REFERENCES users(id),
  type            TEXT NOT NULL,   -- note | stage_change | system
  body            TEXT,
  is_clinical     BOOLEAN NOT NULL DEFAULT false,
  metadata        JSONB NOT NULL DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON contact_activities (organization_id, contact_id, created_at DESC);

-- ============ Services & Appointments ============

CREATE TABLE services (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  category        TEXT,
  duration_minutes INT NOT NULL,
  price_cents     INT NOT NULL DEFAULT 0,
  currency        CHAR(3) NOT NULL DEFAULT 'EUR',
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE appointments (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  location_id         UUID NOT NULL REFERENCES locations(id),
  contact_id          UUID NOT NULL REFERENCES contacts(id),
  provider_user_id    UUID NOT NULL REFERENCES users(id),
  service_id          UUID NOT NULL REFERENCES services(id),
  status              TEXT NOT NULL DEFAULT 'scheduled', -- scheduled | completed | cancelled | no_show
  starts_at           TIMESTAMPTZ NOT NULL,
  ends_at             TIMESTAMPTZ NOT NULL,
  created_by_user_id  UUID REFERENCES users(id),
  cancellation_reason TEXT,
  scheduling_note     TEXT,       -- non-clinical note (e.g. "prefers morning")
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT no_double_booking
    EXCLUDE USING gist (
      provider_user_id WITH =,
      tsrange(starts_at, ends_at) WITH &&
    ) WHERE (status <> 'cancelled')
);
CREATE INDEX ON appointments (organization_id, location_id, starts_at);
CREATE INDEX ON appointments (organization_id, provider_user_id, starts_at);
CREATE INDEX ON appointments (organization_id, contact_id);

-- ============ Audit log (compliance — built in Phase 1, not deferred) ============

CREATE TABLE audit_log (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  actor_user_id   UUID REFERENCES users(id),
  action          TEXT NOT NULL,     -- view | create | update | delete | export
  entity_type     TEXT NOT NULL,     -- contact | appointment | contact_activity | user
  entity_id       UUID,
  metadata        JSONB NOT NULL DEFAULT '{}',
  ip_address      INET,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);   -- monthly partitions; this table grows fast
CREATE INDEX ON audit_log (organization_id, entity_type, entity_id);
```

**RLS policies** (one pattern, applied to every tenant table above):

```sql
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON contacts
  USING (organization_id = current_setting('app.current_org_id', true)::uuid);
-- repeat for locations, users, roles(org-scoped rows), user_roles, pipeline_stages,
-- contacts, tags, contact_tags, contact_activities, services, appointments, audit_log
```

Why `audit_log` is in Phase 1, not Phase 2/3: your own compliance requirement (§7 of the brief) says access logging is "often the actual legal requirement." Retrofitting audit logging after Phase 1 ships means you can't prove pre-launch access was logged — cheaper to build the hook into the ORM layer now (one Prisma middleware) than bolt it on later.

---

## 4. RBAC — default roles & permission catalog

Seeded system-default roles (org_id = NULL, cloned into each new org on signup so orgs can customize without affecting the template):

| Role | Key permissions |
|---|---|
| **Owner/Admin** | `*` (all permissions) |
| **Provider** | `contacts.read` (assigned only), `clinical_notes.read/write`, `appointments.read/write` (own schedule), `activity.write` |
| **Front Desk** | `contacts.read/write`, `appointments.read/write` (all providers, own location), `activity.write` (non-clinical only) — **no** `clinical_notes.read`, **no** `billing.read`, **no** `reports.financial.read` |

Permission enforcement happens twice: a NestJS `PermissionsGuard` checks the JWT's resolved permission set before the handler runs, and `contact_activities.is_clinical = true` rows are filtered at the query layer (not just hidden in the UI) for any caller lacking `clinical_notes.read` — this directly satisfies your "don't just hide it in the UI" requirement.

---

## 5. GDPR mechanics built into Phase 1

- `contacts.consent_recorded_at` / `consent_notes` — minimal consent capture now; full consent-workflow UI can wait, but the field must exist from day one so no historical data is missing it.
- **Export**: `GET /contacts/:id/export` returns the full record (contact + activities + appointments + audit trail of who accessed it) as JSON, permission-gated to Owner/Admin.
- **Erasure**: `DELETE /contacts/:id/erase` is a *hard* delete (not the `deleted_at` soft-delete used for normal lifecycle), cascades to `contact_activities`/`contact_tags`, and writes one final `audit_log` row (`action = 'delete'`) before the contact row itself disappears — proving erasure happened without retaining the erased data.
- Every `GET` on a single contact record writes an `audit_log` row with `action = 'view'`. This is the biggest performance/cost tradeoff to flag: high-volume view logging on every dashboard/list render would be noisy and expensive, so **only single-record detail views are logged, not list/search results** — flagging this scope choice explicitly since it's a compliance-relevant decision, not just an implementation detail.

---

## 6. Decisions that materially affect cost/timeline — need your call

See the questions I'm sending alongside this proposal. Short version of what's at stake:

1. **RLS + Prisma middleware (recommended) vs. app-layer-only isolation.** RLS adds setup complexity (one migration step, careful connection-pool handling with `SET LOCAL` inside transactions) but is the difference between "a missed `WHERE` clause is a bug" and "a missed `WHERE` clause is a breach." Given you're building this to be audited, I'd resist cutting this.
2. **NestJS + Prisma vs. your team's existing stack.** No cost if your devs already know NestJS; real ramp-up cost if the team is, say, all-in on Django or Rails and would rather stay there. Say so and I'll re-propose the schema in that idiom (the schema itself is framework-agnostic).
3. **Compliance target market.** Everything above assumes GDPR (EU clinics). If any target client is US-based, HIPAA changes the bar significantly: signed Business Associate Agreements with every subprocessor (hosting, SMS/email providers), stricter encryption-key management, breach-notification timelines, and it likely rules out some hosting/SMS vendors you'd otherwise pick freely for Phase 2. This is worth deciding before Phase 2 vendor selection, not after.

---

## 7. API contract — Phase 1

All endpoints under `/api/v1`, JWT bearer auth, every response scoped to the caller's `organization_id` (never accepted as a request param). Pagination via `?page=&pageSize=` on all list endpoints, filtering via query params.

### Auth
- `POST /auth/register` — creates organization + first Owner user
- `POST /auth/login`
- `POST /auth/magic-link/request` / `POST /auth/magic-link/verify`
- `POST /auth/logout`
- `POST /auth/2fa/setup` / `POST /auth/2fa/verify` (required to be enabled for Owner/Admin role, per spec)
- `GET /auth/me`

### Organizations & Locations
- `GET /organizations/me` / `PATCH /organizations/me` (Owner only)
- `GET /locations` / `POST /locations` / `GET /locations/:id` / `PATCH /locations/:id` / `DELETE /locations/:id`

### Staff & RBAC
- `GET /staff` / `POST /staff/invite` / `GET /staff/:id` / `PATCH /staff/:id` / `DELETE /staff/:id` (disable, not hard-delete)
- `POST /staff/:id/roles` / `DELETE /staff/:id/roles/:roleId`
- `GET /roles` / `POST /roles` / `PATCH /roles/:id` / `DELETE /roles/:id`
- `GET /permissions` (read-only catalog)

### Contacts
- `GET /contacts?status=&stage=&tag=&assignedTo=&q=&locationId=&page=&pageSize=`
- `POST /contacts` / `GET /contacts/:id` / `PATCH /contacts/:id` / `DELETE /contacts/:id` (soft delete → inactive)
- `POST /contacts/:id/stage` `{ pipelineStageId }`
- `GET /contacts/:id/activity` / `POST /contacts/:id/activity` `{ type, body, isClinical }`
- `POST /contacts/:id/tags` `{ tagId }` / `DELETE /contacts/:id/tags/:tagId`
- `GET /contacts/:id/export` (GDPR)
- `DELETE /contacts/:id/erase` (GDPR hard erase, Owner/Admin only)

### Pipeline stages
- `GET /pipeline-stages` / `POST /pipeline-stages` / `PATCH /pipeline-stages/:id` / `DELETE /pipeline-stages/:id`
- `POST /pipeline-stages/reorder` `{ orderedIds: [...] }`

### Services
- `GET /services` / `POST /services` / `GET /services/:id` / `PATCH /services/:id` / `DELETE /services/:id`

### Appointments
- `GET /appointments?from=&to=&providerId=&locationId=&status=`
- `POST /appointments` `{ contactId, providerUserId, serviceId, locationId, startsAt }` — server computes `endsAt` from `service.durationMinutes`, rejects on the DB exclusion-constraint conflict (double booking) with `409`
- `GET /appointments/:id` / `PATCH /appointments/:id` (reschedule)
- `POST /appointments/:id/cancel` `{ reason }`
- `POST /appointments/:id/complete`
- `POST /appointments/:id/no-show`
- `GET /appointments/availability?providerId=&serviceId=&locationId=&date=` — returns open slots for the booking UI

### Dashboard
- `GET /dashboard/summary` — leads this week, conversion rate by stage, appointments booked/completed/no-show this week, today's/upcoming schedule

### Search
- `GET /search?q=` — combined contacts + appointments, tenant-scoped, backed by the `contacts` GIN index above

---

## 8. What's explicitly deferred (not in Phase 1)

`messages`, `invoices`, `payments`, `subscriptions` tables and all Stripe/SMS/WhatsApp integration — these get their own schema/API proposal at the start of Phase 2, per the phased build order you specified.
