import { Injectable, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

/**
 * Raw client bound to the app's normal runtime Postgres role. Every tenant
 * table has FORCE ROW LEVEL SECURITY, so queries run directly against this
 * client (outside of a request's tenant transaction) see zero rows unless
 * `app.current_org_id` has been set on that same connection/transaction.
 *
 * Feature modules should not use this directly for tenant data - they go
 * through `TenantPrismaService.client`, which resolves to the request's
 * RLS-scoped transaction. This raw client exists for: the tenant
 * interceptor (which opens that transaction), scripts (seed/migrate), and
 * background jobs (which must open their own scoped transaction per job,
 * same as the interceptor does per request).
 */
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
