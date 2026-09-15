import { Injectable, NotFoundException } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { CreateServiceDto, UpdateServiceDto } from './dto/service.dto';

@Injectable()
export class ServicesService {
  constructor(private readonly tenant: TenantPrismaService) {}

  list() {
    return this.tenant.client.service.findMany({
      where: { organizationId: this.tenant.organizationId },
      orderBy: { name: 'asc' },
    });
  }

  create(dto: CreateServiceDto) {
    return this.tenant.client.service.create({
      data: { ...dto, organizationId: this.tenant.organizationId },
    });
  }

  async findOne(id: string) {
    const service = await this.tenant.client.service.findFirst({
      where: { id, organizationId: this.tenant.organizationId },
    });
    if (!service) {
      throw new NotFoundException('Service not found.');
    }
    return service;
  }

  async update(id: string, dto: UpdateServiceDto) {
    await this.findOne(id);
    return this.tenant.client.service.update({ where: { id }, data: dto });
  }

  async remove(id: string) {
    await this.findOne(id);
    await this.tenant.client.service.update({ where: { id }, data: { isActive: false } });
  }
}
