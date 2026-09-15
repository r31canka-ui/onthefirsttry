import { AsyncLocalStorage } from 'node:async_hooks';
import { Prisma } from '@prisma/client';

export interface TenantStore {
  tx: Prisma.TransactionClient;
  organizationId: string;
  userId?: string;
  permissions?: string[];
}

/**
 * Carries the current request's RLS-scoped transaction client and
 * identity down through every service call, without threading it through
 * every function signature. Populated by TenantInterceptor at the top of
 * each authenticated request; read by TenantPrismaService.client and by
 * anything that needs "who is making this call" (audit logging, RBAC).
 */
export const tenantAls = new AsyncLocalStorage<TenantStore>();

export function getTenantStore(): TenantStore | undefined {
  return tenantAls.getStore();
}

export function requireTenantStore(): TenantStore {
  const store = tenantAls.getStore();
  if (!store) {
    throw new Error(
      'No tenant context available. This code path must run inside an authenticated request (TenantInterceptor) or an explicit withTenant() block.',
    );
  }
  return store;
}
