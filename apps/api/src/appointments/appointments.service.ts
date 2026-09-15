import { BadRequestException, ForbiddenException, Injectable, NotFoundException } from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { USER_SAFE_SELECT } from '../common/prisma-selects';
import {
  AvailabilityQueryDto,
  CancelAppointmentDto,
  CreateAppointmentDto,
  ListAppointmentsQueryDto,
  UpdateAppointmentDto,
} from './dto/appointment.dto';

// Placeholder business hours until a real working-hours/schedule entity
// exists (out of the confirmed Phase 1 schema - flagging rather than
// quietly inventing a bigger feature). Every provider is treated as
// available 09:00-18:00 UTC, every day - NOT location-local time, since
// per-location timezone-aware business hours is exactly the kind of
// scope this placeholder is standing in for. Fine for a single-timezone
// pilot clinic; needs the real schedule entity before Phase 3
// multi-location rollout where locations span timezones.
const WORKDAY_START_HOUR = 9;
const WORKDAY_END_HOUR = 18;
const SLOT_STEP_MINUTES = 15;

@Injectable()
export class AppointmentsService {
  constructor(private readonly tenant: TenantPrismaService) {}

  private canReadAll(): boolean {
    return this.tenant.permissions.includes('appointments.read.all');
  }

  async list(query: ListAppointmentsQueryDto) {
    const where: Prisma.AppointmentWhereInput = {
      organizationId: this.tenant.organizationId,
      ...(query.from && { startsAt: { gte: new Date(query.from) } }),
      ...(query.to && { endsAt: { lte: new Date(query.to) } }),
      ...(query.locationId && { locationId: query.locationId }),
      ...(query.status && { status: query.status }),
      ...(query.providerId && { providerUserId: query.providerId }),
    };

    // Providers without appointments.read.all only ever see their own
    // schedule, enforced here (not just in the UI).
    if (!this.canReadAll()) {
      where.providerUserId = this.tenant.userId;
    }

    return this.tenant.client.appointment.findMany({
      where,
      include: { contact: true, provider: { select: USER_SAFE_SELECT }, service: true, location: true },
      orderBy: { startsAt: 'asc' },
    });
  }

  async findOne(id: string) {
    const appointment = await this.tenant.client.appointment.findFirst({
      where: { id, organizationId: this.tenant.organizationId },
      include: { contact: true, provider: { select: USER_SAFE_SELECT }, service: true, location: true },
    });
    if (!appointment) {
      throw new NotFoundException('Appointment not found.');
    }
    if (!this.canReadAll() && appointment.providerUserId !== this.tenant.userId) {
      throw new ForbiddenException('You can only view your own appointments.');
    }
    return appointment;
  }

  async create(dto: CreateAppointmentDto) {
    const service = await this.tenant.client.service.findFirst({
      where: { id: dto.serviceId, organizationId: this.tenant.organizationId, isActive: true },
    });
    if (!service) {
      throw new BadRequestException('Invalid service.');
    }

    const startsAt = new Date(dto.startsAt);
    const endsAt = new Date(startsAt.getTime() + service.durationMinutes * 60_000);

    // The DB's EXCLUDE constraint (appointments_no_double_booking) is the
    // actual source of truth for conflict prevention - this pre-check just
    // gives a fast, friendly error before hitting it.
    const conflict = await this.tenant.client.appointment.findFirst({
      where: {
        providerUserId: dto.providerUserId,
        status: { not: 'cancelled' },
        startsAt: { lt: endsAt },
        endsAt: { gt: startsAt },
      },
    });
    if (conflict) {
      throw new BadRequestException('This provider already has an appointment that overlaps this time range.');
    }

    return this.tenant.client.appointment.create({
      data: {
        organizationId: this.tenant.organizationId,
        contactId: dto.contactId,
        providerUserId: dto.providerUserId,
        serviceId: dto.serviceId,
        locationId: dto.locationId,
        startsAt,
        endsAt,
        schedulingNote: dto.schedulingNote,
        createdByUserId: this.tenant.userId,
      },
    });
  }

  async update(id: string, dto: UpdateAppointmentDto) {
    const appointment = await this.findOne(id);
    let endsAt = appointment.endsAt;
    let startsAt = appointment.startsAt;
    if (dto.startsAt) {
      const service = await this.tenant.client.service.findFirstOrThrow({
        where: { id: appointment.serviceId },
      });
      startsAt = new Date(dto.startsAt);
      endsAt = new Date(startsAt.getTime() + service.durationMinutes * 60_000);
    }

    return this.tenant.client.appointment.update({
      where: { id },
      data: {
        startsAt,
        endsAt,
        providerUserId: dto.providerUserId,
        locationId: dto.locationId,
        schedulingNote: dto.schedulingNote,
      },
    });
  }

  async cancel(id: string, dto: CancelAppointmentDto) {
    await this.findOne(id);
    return this.tenant.client.appointment.update({
      where: { id },
      data: { status: 'cancelled', cancellationReason: dto.reason },
    });
  }

  async complete(id: string) {
    await this.findOne(id);
    return this.tenant.client.appointment.update({ where: { id }, data: { status: 'completed' } });
  }

  async noShow(id: string) {
    await this.findOne(id);
    return this.tenant.client.appointment.update({ where: { id }, data: { status: 'no_show' } });
  }

  async availability(query: AvailabilityQueryDto) {
    const service = await this.tenant.client.service.findFirst({
      where: { id: query.serviceId, organizationId: this.tenant.organizationId },
    });
    if (!service) {
      throw new BadRequestException('Invalid service.');
    }

    const dayStart = new Date(`${query.date}T00:00:00.000Z`);
    const workStart = new Date(dayStart);
    workStart.setUTCHours(WORKDAY_START_HOUR, 0, 0, 0);
    const workEnd = new Date(dayStart);
    workEnd.setUTCHours(WORKDAY_END_HOUR, 0, 0, 0);

    const existing = await this.tenant.client.appointment.findMany({
      where: {
        providerUserId: query.providerId,
        status: { not: 'cancelled' },
        startsAt: { lt: workEnd },
        endsAt: { gt: workStart },
      },
      orderBy: { startsAt: 'asc' },
    });

    const slots: { startsAt: string; endsAt: string }[] = [];
    const durationMs = service.durationMinutes * 60_000;
    for (
      let slotStart = workStart.getTime();
      slotStart + durationMs <= workEnd.getTime();
      slotStart += SLOT_STEP_MINUTES * 60_000
    ) {
      const slotEnd = slotStart + durationMs;
      const overlaps = existing.some(
        (a) => slotStart < a.endsAt.getTime() && slotEnd > a.startsAt.getTime(),
      );
      if (!overlaps) {
        slots.push({ startsAt: new Date(slotStart).toISOString(), endsAt: new Date(slotEnd).toISOString() });
      }
    }
    return slots;
  }
}
