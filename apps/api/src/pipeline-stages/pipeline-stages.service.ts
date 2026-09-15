import { BadRequestException, Injectable, NotFoundException } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import {
  CreatePipelineStageDto,
  ReorderPipelineStagesDto,
  UpdatePipelineStageDto,
} from './dto/pipeline-stage.dto';

@Injectable()
export class PipelineStagesService {
  constructor(private readonly tenant: TenantPrismaService) {}

  list() {
    return this.tenant.client.pipelineStage.findMany({ orderBy: { position: 'asc' } });
  }

  async create(dto: CreatePipelineStageDto) {
    const last = await this.tenant.client.pipelineStage.findFirst({
      where: { organizationId: this.tenant.organizationId },
      orderBy: { position: 'desc' },
    });
    return this.tenant.client.pipelineStage.create({
      data: {
        name: dto.name,
        isWonStage: dto.isWonStage ?? false,
        position: (last?.position ?? -1) + 1,
        organizationId: this.tenant.organizationId,
      },
    });
  }

  private async findOwnOrThrow(id: string) {
    const stage = await this.tenant.client.pipelineStage.findFirst({
      where: { id, organizationId: this.tenant.organizationId },
    });
    if (!stage) {
      throw new NotFoundException('Pipeline stage not found.');
    }
    return stage;
  }

  async update(id: string, dto: UpdatePipelineStageDto) {
    await this.findOwnOrThrow(id);
    return this.tenant.client.pipelineStage.update({ where: { id }, data: dto });
  }

  async remove(id: string) {
    await this.findOwnOrThrow(id);
    const inUse = await this.tenant.client.contact.count({ where: { pipelineStageId: id } });
    if (inUse > 0) {
      throw new BadRequestException('Cannot delete a stage that still has contacts in it.');
    }
    await this.tenant.client.pipelineStage.delete({ where: { id } });
  }

  async reorder(dto: ReorderPipelineStagesDto) {
    const stages = await this.tenant.client.pipelineStage.findMany({
      where: { organizationId: this.tenant.organizationId },
    });
    if (
      stages.length !== dto.orderedIds.length ||
      !stages.every((s) => dto.orderedIds.includes(s.id))
    ) {
      throw new BadRequestException('orderedIds must include exactly this org\'s current stage IDs.');
    }

    // Two-phase update avoids transiently violating the
    // (organizationId, position) unique constraint while reordering.
    for (const [index, id] of dto.orderedIds.entries()) {
      await this.tenant.client.pipelineStage.update({
        where: { id },
        data: { position: -(index + 1) },
      });
    }
    for (const [index, id] of dto.orderedIds.entries()) {
      await this.tenant.client.pipelineStage.update({ where: { id }, data: { position: index } });
    }

    return this.list();
  }
}
