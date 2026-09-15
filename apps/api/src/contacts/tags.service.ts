import { ConflictException, Injectable } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';

@Injectable()
export class TagsService {
  constructor(private readonly tenant: TenantPrismaService) {}

  list() {
    return this.tenant.client.tag.findMany({
      where: { organizationId: this.tenant.organizationId },
      orderBy: { name: 'asc' },
    });
  }

  async create(name: string, color?: string) {
    const existing = await this.tenant.client.tag.findFirst({
      where: { organizationId: this.tenant.organizationId, name },
    });
    if (existing) {
      throw new ConflictException('A tag with that name already exists.');
    }
    return this.tenant.client.tag.create({
      data: { name, color, organizationId: this.tenant.organizationId },
    });
  }
}
