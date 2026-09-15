import { Injectable } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';

export type AuditAction = 'view' | 'create' | 'update' | 'delete' | 'export';

/**
 * Writes to `audit_log`. Called explicitly from services at the specific
 * points that matter (single-contact detail view, create/update/delete,
 * GDPR export) rather than from a blanket global interceptor, because
 * logging every list/search result row would be noisy and expensive
 * without adding real compliance value - see docs/phase1-schema-and-api.md
 * §5 for that scope call.
 */
@Injectable()
export class AuditService {
  constructor(private readonly tenant: TenantPrismaService) {}

  async log(action: AuditAction, entityType: string, entityId: string, ipAddress?: string) {
    await this.tenant.client.auditLog.create({
      data: {
        organizationId: this.tenant.organizationId,
        actorUserId: this.tenant.userId,
        action,
        entityType,
        entityId,
        ipAddress,
      },
    });
  }
}
