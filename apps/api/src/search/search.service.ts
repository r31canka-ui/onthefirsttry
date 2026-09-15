import { Injectable } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { USER_SAFE_SELECT } from '../common/prisma-selects';

@Injectable()
export class SearchService {
  constructor(private readonly tenant: TenantPrismaService) {}

  async search(q: string) {
    if (!q || q.trim().length < 2) {
      return { contacts: [], appointments: [] };
    }
    const orgId = this.tenant.organizationId;

    const [contacts, appointments] = await Promise.all([
      this.tenant.client.contact.findMany({
        where: {
          organizationId: orgId,
          deletedAt: null,
          OR: [
            { firstName: { contains: q, mode: 'insensitive' } },
            { lastName: { contains: q, mode: 'insensitive' } },
            { email: { contains: q, mode: 'insensitive' } },
            { phone: { contains: q, mode: 'insensitive' } },
          ],
        },
        take: 20,
      }),
      this.tenant.client.appointment.findMany({
        where: {
          organizationId: orgId,
          contact: {
            OR: [
              { firstName: { contains: q, mode: 'insensitive' } },
              { lastName: { contains: q, mode: 'insensitive' } },
            ],
          },
        },
        include: { contact: true, provider: { select: USER_SAFE_SELECT }, service: true },
        take: 20,
        orderBy: { startsAt: 'desc' },
      }),
    ]);

    return { contacts, appointments };
  }
}
