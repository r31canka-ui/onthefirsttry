import { Injectable } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { USER_SAFE_SELECT } from '../common/prisma-selects';

function startOfWeek(date: Date): Date {
  const d = new Date(date);
  const day = d.getUTCDay();
  const diff = (day === 0 ? -6 : 1) - day; // Monday start
  d.setUTCDate(d.getUTCDate() + diff);
  d.setUTCHours(0, 0, 0, 0);
  return d;
}

@Injectable()
export class DashboardService {
  constructor(private readonly tenant: TenantPrismaService) {}

  async summary() {
    const orgId = this.tenant.organizationId;
    const weekStart = startOfWeek(new Date());
    const now = new Date();

    const [leadsThisWeek, stages, appointmentsThisWeek, upcoming] = await Promise.all([
      this.tenant.client.contact.count({
        where: { organizationId: orgId, status: 'lead', createdAt: { gte: weekStart } },
      }),
      this.tenant.client.pipelineStage.findMany({
        where: { organizationId: orgId },
        orderBy: { position: 'asc' },
        include: { _count: { select: { contacts: true } } },
      }),
      this.tenant.client.appointment.groupBy({
        by: ['status'],
        where: { organizationId: orgId, startsAt: { gte: weekStart } },
        _count: true,
      }),
      this.tenant.client.appointment.findMany({
        where: { organizationId: orgId, status: 'scheduled', startsAt: { gte: now } },
        include: { contact: true, provider: { select: USER_SAFE_SELECT }, service: true, location: true },
        orderBy: { startsAt: 'asc' },
        take: 10,
      }),
    ]);

    const totalContactsInPipeline = stages.reduce((sum, s) => sum + s._count.contacts, 0);
    const wonStage = stages.find((s) => s.isWonStage);
    const conversionRate =
      totalContactsInPipeline > 0 && wonStage
        ? Math.round((wonStage._count.contacts / totalContactsInPipeline) * 100)
        : 0;

    const appointmentCounts = { scheduled: 0, completed: 0, cancelled: 0, no_show: 0 };
    for (const row of appointmentsThisWeek) {
      appointmentCounts[row.status as keyof typeof appointmentCounts] = row._count;
    }

    return {
      leadsThisWeek,
      pipelineByStage: stages.map((s) => ({ name: s.name, count: s._count.contacts })),
      conversionRate,
      appointmentsThisWeek: appointmentCounts,
      upcomingAppointments: upcoming,
    };
  }
}
