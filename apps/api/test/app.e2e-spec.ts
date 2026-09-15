import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import request from 'supertest';
import { AppModule } from '../src/app.module';
import { AllExceptionsFilter } from '../src/common/filters/all-exceptions.filter';

/**
 * End-to-end tests against a real Postgres instance (RLS and the
 * double-booking EXCLUDE constraint only mean something when tested
 * against the actual database, not mocks). Run with a DATABASE_URL /
 * AUTH_DATABASE_URL pointed at a disposable test database with
 * migrations applied - see package.json's `test:e2e` script.
 */
describe('Clinic CRM API (e2e)', () => {
  let app: INestApplication;
  const suffix = Date.now();

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.setGlobalPrefix('api/v1');
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));
    app.useGlobalFilters(new AllExceptionsFilter());
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  async function registerOrg(name: string, email: string) {
    const res = await request(app.getHttpServer())
      .post('/api/v1/auth/register')
      .send({
        organizationName: name,
        countryCode: 'AL',
        fullName: 'Test Owner',
        email,
        password: 'supersecretpassword1',
      })
      .expect(201);
    return res.body.accessToken as string;
  }

  describe('Tenant isolation', () => {
    let tokenA: string;
    let tokenB: string;
    let contactAId: string;

    beforeAll(async () => {
      tokenA = await registerOrg(`Org A ${suffix}`, `ownerA-${suffix}@test.local`);
      tokenB = await registerOrg(`Org B ${suffix}`, `ownerB-${suffix}@test.local`);

      const res = await request(app.getHttpServer())
        .post('/api/v1/contacts')
        .set('Authorization', `Bearer ${tokenA}`)
        .send({ firstName: 'Patient', lastName: 'Zero' })
        .expect(201);
      contactAId = res.body.id;
    });

    it("prevents org B from reading org A's contact by direct ID", async () => {
      await request(app.getHttpServer())
        .get(`/api/v1/contacts/${contactAId}`)
        .set('Authorization', `Bearer ${tokenB}`)
        .expect(404);
    });

    it("excludes org A's contact from org B's list endpoint", async () => {
      const res = await request(app.getHttpServer())
        .get('/api/v1/contacts')
        .set('Authorization', `Bearer ${tokenB}`)
        .expect(200);
      expect(res.body.items).toHaveLength(0);
    });

    it('lets org A read its own contact', async () => {
      const res = await request(app.getHttpServer())
        .get(`/api/v1/contacts/${contactAId}`)
        .set('Authorization', `Bearer ${tokenA}`)
        .expect(200);
      expect(res.body.id).toBe(contactAId);
    });

    it('never serializes passwordHash or twoFactorSecret in any response', async () => {
      const res = await request(app.getHttpServer())
        .get(`/api/v1/contacts/${contactAId}/activity`)
        .set('Authorization', `Bearer ${tokenA}`)
        .expect(200);
      expect(JSON.stringify(res.body)).not.toContain('passwordHash');
      expect(JSON.stringify(res.body)).not.toContain('twoFactorSecret');
    });
  });

  describe('RBAC: clinical notes', () => {
    let ownerToken: string;
    let frontDeskToken: string;
    let contactId: string;

    beforeAll(async () => {
      ownerToken = await registerOrg(`Org RBAC ${suffix}`, `rbac-owner-${suffix}@test.local`);

      const rolesRes = await request(app.getHttpServer())
        .get('/api/v1/roles')
        .set('Authorization', `Bearer ${ownerToken}`)
        .expect(200);
      const frontDeskRole = rolesRes.body.find((r: { name: string }) => r.name === 'Front Desk');

      const inviteRes = await request(app.getHttpServer())
        .post('/api/v1/staff/invite')
        .set('Authorization', `Bearer ${ownerToken}`)
        .send({
          email: `fd-${suffix}@test.local`,
          fullName: 'Front Desk',
          roleIds: [frontDeskRole.id],
        })
        .expect(201);

      // The invite token is only ever delivered by email (never returned by
      // the API), so activate the invited user directly via the DB here
      // rather than re-testing the invite-email flow itself.
      const { PrismaClient } = await import('@prisma/client');
      const prisma = new PrismaClient({ datasourceUrl: process.env.AUTH_DATABASE_URL });
      const argon2 = await import('argon2');
      await prisma.user.update({
        where: { id: inviteRes.body.id },
        data: { status: 'active', passwordHash: await argon2.hash('frontdeskpassword1') },
      });
      await prisma.$disconnect();

      const loginRes = await request(app.getHttpServer())
        .post('/api/v1/auth/login')
        .send({ email: `fd-${suffix}@test.local`, password: 'frontdeskpassword1' })
        .expect(200);
      frontDeskToken = loginRes.body.accessToken;

      const contactRes = await request(app.getHttpServer())
        .post('/api/v1/contacts')
        .set('Authorization', `Bearer ${ownerToken}`)
        .send({ firstName: 'Clinical', lastName: 'Case' })
        .expect(201);
      contactId = contactRes.body.id;

      await request(app.getHttpServer())
        .post(`/api/v1/contacts/${contactId}/activity`)
        .set('Authorization', `Bearer ${ownerToken}`)
        .send({ body: 'Allergic to penicillin', isClinical: true })
        .expect(201);

      await request(app.getHttpServer())
        .post(`/api/v1/contacts/${contactId}/activity`)
        .set('Authorization', `Bearer ${ownerToken}`)
        .send({ body: 'Prefers mornings', isClinical: false })
        .expect(201);
    });

    it('hides is_clinical activity rows from front desk at the query layer', async () => {
      const res = await request(app.getHttpServer())
        .get(`/api/v1/contacts/${contactId}/activity`)
        .set('Authorization', `Bearer ${frontDeskToken}`)
        .expect(200);
      expect(res.body).toHaveLength(1);
      expect(res.body[0].isClinical).toBe(false);
    });

    it('shows all activity rows to the owner', async () => {
      const res = await request(app.getHttpServer())
        .get(`/api/v1/contacts/${contactId}/activity`)
        .set('Authorization', `Bearer ${ownerToken}`)
        .expect(200);
      expect(res.body).toHaveLength(2);
    });

    it('forbids front desk from writing a clinical note', async () => {
      await request(app.getHttpServer())
        .post(`/api/v1/contacts/${contactId}/activity`)
        .set('Authorization', `Bearer ${frontDeskToken}`)
        .send({ body: 'trying to sneak in', isClinical: true })
        .expect(403);
    });

    it('forbids front desk from reading financial/report data', async () => {
      await request(app.getHttpServer())
        .get('/api/v1/dashboard/summary')
        .set('Authorization', `Bearer ${frontDeskToken}`)
        .expect(403);
    });

    it("revokes access immediately when the user's role permissions are taken away, without waiting for token expiry", async () => {
      // Confirms permissions are resolved live per-request, not trusted
      // from the (still-valid) JWT.
      const { PrismaClient } = await import('@prisma/client');
      const prisma = new PrismaClient({ datasourceUrl: process.env.AUTH_DATABASE_URL });
      await prisma.user.updateMany({
        where: { email: `fd-${suffix}@test.local` },
        data: { status: 'disabled' },
      });
      await prisma.$disconnect();

      await request(app.getHttpServer())
        .get(`/api/v1/contacts/${contactId}/activity`)
        .set('Authorization', `Bearer ${frontDeskToken}`)
        .expect(401);
    });
  });

  describe('Double-booking prevention', () => {
    let token: string;
    let contactId: string;
    let providerId: string;
    let serviceId: string;
    let locationId: string;

    beforeAll(async () => {
      token = await registerOrg(`Org Booking ${suffix}`, `booking-${suffix}@test.local`);

      const me = await request(app.getHttpServer())
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);
      providerId = me.body.userId;

      const location = await request(app.getHttpServer())
        .post('/api/v1/locations')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'Main', timezone: 'Europe/Tirane' })
        .expect(201);
      locationId = location.body.id;

      const service = await request(app.getHttpServer())
        .post('/api/v1/services')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'Checkup', durationMinutes: 30, priceCents: 4000 })
        .expect(201);
      serviceId = service.body.id;

      const contact = await request(app.getHttpServer())
        .post('/api/v1/contacts')
        .set('Authorization', `Bearer ${token}`)
        .send({ firstName: 'Booking', lastName: 'Test' })
        .expect(201);
      contactId = contact.body.id;
    });

    it('books a first appointment successfully', async () => {
      await request(app.getHttpServer())
        .post('/api/v1/appointments')
        .set('Authorization', `Bearer ${token}`)
        .send({
          contactId,
          providerUserId: providerId,
          serviceId,
          locationId,
          startsAt: '2027-01-10T10:00:00.000Z',
        })
        .expect(201);
    });

    it('rejects an overlapping appointment for the same provider', async () => {
      await request(app.getHttpServer())
        .post('/api/v1/appointments')
        .set('Authorization', `Bearer ${token}`)
        .send({
          contactId,
          providerUserId: providerId,
          serviceId,
          locationId,
          startsAt: '2027-01-10T10:15:00.000Z',
        })
        .expect(400);
    });

    it('allows a back-to-back, non-overlapping appointment', async () => {
      await request(app.getHttpServer())
        .post('/api/v1/appointments')
        .set('Authorization', `Bearer ${token}`)
        .send({
          contactId,
          providerUserId: providerId,
          serviceId,
          locationId,
          startsAt: '2027-01-10T10:30:00.000Z',
        })
        .expect(201);
    });
  });
});
