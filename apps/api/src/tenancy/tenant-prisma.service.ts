import { Injectable } from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { PrismaService } from '../prisma/prisma.service';
import { requireTenantStore, tenantAls } from './tenant-context';

/**
 * The client feature services should use for all tenant-scoped queries.
 * `.client` resolves to the current request's RLS-scoped transaction
 * (set by TenantInterceptor). This is deliberately the ONLY way feature
 * modules reach Prisma - if there's no tenant context on the async
 * chain, `.client` throws instead of silently falling back to the raw,
 * unscoped connection.
 *
 * This is layer two of tenant isolation: even though Postgres RLS
 * (layer one) already prevents cross-tenant rows at the database level
 * regardless of what this layer does, requiring every query to go
 * through a client that only exists inside a scoped transaction means a
 * missing organization_id filter in a service method is caught by RLS,
 * while a service that forgets to scope tenant context at all fails
 * loudly (a thrown error) instead of silently.
 */
@Injectable()
export class TenantPrismaService {
  constructor(private readonly prisma: PrismaService) {}

  get client(): Prisma.TransactionClient {
    return requireTenantStore().tx;
  }

  get organizationId(): string {
    return requireTenantStore().organizationId;
  }

  get userId(): string | undefined {
    return requireTenantStore().userId;
  }

  /** Live-resolved permission set for the current caller (see TenantContextInterceptor). Empty on service-initiated (non-request) tenant contexts, e.g. background jobs. */
  get permissions(): string[] {
    return requireTenantStore().permissions ?? [];
  }

  /** Escape hatch for background jobs, which run outside HTTP requests and
   * must open their own scoped transaction per job (see BullMQ processors). */
  async withTenant<T>(
    organizationId: string,
    userId: string | undefined,
    fn: () => Promise<T>,
  ): Promise<T> {
    return this.prisma.$transaction(async (tx) => {
      await tx.$executeRaw`SELECT set_config('app.current_org_id', ${organizationId}, true)`;
      return tenantAls.run({ tx, organizationId, userId }, fn);
    });
  }
}
