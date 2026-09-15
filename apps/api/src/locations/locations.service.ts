import { NotFoundException } from '@nestjs/common';
import { Injectable } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { CreateLocationDto, UpdateLocationDto } from './dto/location.dto';

@Injectable()
export class LocationsService {
  constructor(private readonly tenant: TenantPrismaService) {}

  list() {
    return this.tenant.client.location.findMany({ orderBy: { name: 'asc' } });
  }

  create(dto: CreateLocationDto) {
    return this.tenant.client.location.create({
      data: { ...dto, organizationId: this.tenant.organizationId },
    });
  }

  async findOne(id: string) {
    // organizationId is included explicitly (not just relied on via RLS)
    // as the second, app-layer isolation check called for in the schema
    // proposal - RLS makes this redundant but a reviewer shouldn't have
    // to trust that alone to see this query is tenant-scoped.
    const location = await this.tenant.client.location.findFirst({
      where: { id, organizationId: this.tenant.organizationId },
    });
    if (!location) {
      throw new NotFoundException('Location not found.');
    }
    return location;
  }

  async update(id: string, dto: UpdateLocationDto) {
    await this.findOne(id);
    return this.tenant.client.location.update({ where: { id }, data: dto });
  }

  async remove(id: string) {
    await this.findOne(id);
    // Soft-deactivate rather than hard delete: appointments/staff history
    // reference this location and must stay intact.
    await this.tenant.client.location.update({ where: { id }, data: { isActive: false } });
  }
}
