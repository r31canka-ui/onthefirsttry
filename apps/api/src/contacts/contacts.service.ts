import { BadRequestException, ForbiddenException, Injectable, NotFoundException } from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { AuditService } from '../audit/audit.service';
import { USER_SAFE_SELECT } from '../common/prisma-selects';
import {
  AddTagDto,
  CreateActivityDto,
  CreateContactDto,
  ListContactsQueryDto,
  MoveStageDto,
  UpdateContactDto,
} from './dto/contact.dto';

@Injectable()
export class ContactsService {
  constructor(
    private readonly tenant: TenantPrismaService,
    private readonly audit: AuditService,
  ) {}

  private canReadClinicalNotes(): boolean {
    return this.tenant.permissions.includes('clinical_notes.read');
  }

  async list(query: ListContactsQueryDto) {
    const page = query.page ?? 1;
    const pageSize = query.pageSize ?? 25;

    const where: Prisma.ContactWhereInput = {
      organizationId: this.tenant.organizationId,
      deletedAt: null,
      ...(query.status && { status: query.status }),
      ...(query.stage && { pipelineStageId: query.stage }),
      ...(query.assignedTo && { assignedToUserId: query.assignedTo }),
      ...(query.locationId && { primaryLocationId: query.locationId }),
      ...(query.tag && { tags: { some: { tagId: query.tag } } }),
      ...(query.q && {
        OR: [
          { firstName: { contains: query.q, mode: 'insensitive' } },
          { lastName: { contains: query.q, mode: 'insensitive' } },
          { email: { contains: query.q, mode: 'insensitive' } },
          { phone: { contains: query.q, mode: 'insensitive' } },
        ],
      }),
    };

    const [items, total] = await Promise.all([
      this.tenant.client.contact.findMany({
        where,
        include: { pipelineStage: true, assignedTo: { select: USER_SAFE_SELECT }, tags: { include: { tag: true } } },
        orderBy: { updatedAt: 'desc' },
        skip: (page - 1) * pageSize,
        take: pageSize,
      }),
      this.tenant.client.contact.count({ where }),
    ]);

    return { items, total, page, pageSize };
  }

  async findOne(id: string, logView = true) {
    const contact = await this.tenant.client.contact.findFirst({
      where: { id, organizationId: this.tenant.organizationId },
      include: { pipelineStage: true, assignedTo: { select: USER_SAFE_SELECT }, tags: { include: { tag: true } }, primaryLocation: true },
    });
    if (!contact) {
      throw new NotFoundException('Contact not found.');
    }
    if (logView) {
      await this.audit.log('view', 'contact', id);
    }
    return contact;
  }

  async create(dto: CreateContactDto) {
    const { consentRecorded, customFields, ...rest } = dto;
    const data: Prisma.ContactUncheckedCreateInput = {
      ...rest,
      organizationId: this.tenant.organizationId,
      customFields: customFields as Prisma.InputJsonValue | undefined,
      consentRecordedAt: consentRecorded ? new Date() : undefined,
    };
    const contact = await this.tenant.client.contact.create({ data });
    await this.audit.log('create', 'contact', contact.id);
    return contact;
  }

  async update(id: string, dto: UpdateContactDto) {
    await this.findOne(id, false);
    const { consentRecorded, customFields, ...rest } = dto;
    const data: Prisma.ContactUncheckedUpdateInput = {
      ...rest,
      customFields: customFields as Prisma.InputJsonValue | undefined,
      ...(consentRecorded !== undefined && {
        consentRecordedAt: consentRecorded ? new Date() : null,
      }),
    };
    const contact = await this.tenant.client.contact.update({ where: { id }, data });
    await this.audit.log('update', 'contact', id);
    return contact;
  }

  async deactivate(id: string) {
    await this.findOne(id, false);
    await this.tenant.client.contact.update({ where: { id }, data: { status: 'inactive' } });
    await this.audit.log('delete', 'contact', id);
  }

  async moveStage(id: string, dto: MoveStageDto) {
    await this.findOne(id, false);
    const stage = await this.tenant.client.pipelineStage.findFirst({
      where: { id: dto.pipelineStageId, organizationId: this.tenant.organizationId },
    });
    if (!stage) {
      throw new BadRequestException('Invalid pipeline stage.');
    }

    // No inner $transaction: `tenant.client` is already the interactive
    // transaction opened for this whole request, so these two writes are
    // already atomic together with everything else in the request.
    const contact = await this.tenant.client.contact.update({
      where: { id },
      data: {
        pipelineStageId: stage.id,
        status: stage.isWonStage ? 'active_patient' : undefined,
      },
    });
    await this.tenant.client.contactActivity.create({
      data: {
        organizationId: this.tenant.organizationId,
        contactId: id,
        authorUserId: this.tenant.userId,
        type: 'stage_change',
        body: `Moved to "${stage.name}"`,
      },
    });
    return contact;
  }

  async listActivity(contactId: string) {
    await this.findOne(contactId, false);
    return this.tenant.client.contactActivity.findMany({
      where: {
        contactId,
        organizationId: this.tenant.organizationId,
        // Front-desk (no clinical_notes.read) never sees is_clinical rows -
        // filtered here at the query layer, not hidden client-side.
        ...(this.canReadClinicalNotes() ? {} : { isClinical: false }),
      },
      include: { author: { select: USER_SAFE_SELECT } },
      orderBy: { createdAt: 'desc' },
    });
  }

  async addActivity(contactId: string, dto: CreateActivityDto) {
    await this.findOne(contactId, false);
    if (dto.isClinical && !this.tenant.permissions.includes('clinical_notes.write')) {
      throw new ForbiddenException('Missing required permission(s): clinical_notes.write');
    }
    return this.tenant.client.contactActivity.create({
      data: {
        organizationId: this.tenant.organizationId,
        contactId,
        authorUserId: this.tenant.userId,
        type: 'note',
        body: dto.body,
        isClinical: dto.isClinical ?? false,
      },
    });
  }

  async addTag(contactId: string, dto: AddTagDto) {
    await this.findOne(contactId, false);
    const tag = await this.tenant.client.tag.findFirst({
      where: { id: dto.tagId, organizationId: this.tenant.organizationId },
    });
    if (!tag) {
      throw new BadRequestException('Invalid tag.');
    }
    await this.tenant.client.contactTag.upsert({
      where: { contactId_tagId: { contactId, tagId: dto.tagId } },
      update: {},
      create: { contactId, tagId: dto.tagId },
    });
  }

  async removeTag(contactId: string, tagId: string) {
    await this.findOne(contactId, false);
    await this.tenant.client.contactTag.deleteMany({ where: { contactId, tagId } });
  }

  async exportContact(id: string) {
    const contact = await this.tenant.client.contact.findFirst({
      where: { id, organizationId: this.tenant.organizationId },
      include: {
        tags: { include: { tag: true } },
        activities: { include: { author: { select: USER_SAFE_SELECT } } },
        appointments: { include: { service: true, provider: { select: USER_SAFE_SELECT }, location: true } },
      },
    });
    if (!contact) {
      throw new NotFoundException('Contact not found.');
    }
    await this.audit.log('export', 'contact', id);
    return contact;
  }

  /** GDPR right to erasure: hard delete, cascades to activities/tags/appointments references. */
  async erase(id: string) {
    await this.findOne(id, false);
    // Written before the row disappears, proving erasure happened.
    await this.audit.log('delete', 'contact', id);
    await this.tenant.client.contact.delete({ where: { id } });
  }
}
