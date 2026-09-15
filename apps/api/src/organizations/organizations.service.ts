import { Injectable } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { UpdateOrganizationDto } from './dto/update-organization.dto';

@Injectable()
export class OrganizationsService {
  constructor(private readonly tenant: TenantPrismaService) {}

  getMine() {
    // Scoped implicitly: RLS on `organizations` restricts to
    // id = current_org_id(), so findFirst() can only ever return this org.
    return this.tenant.client.organization.findFirstOrThrow();
  }

  update(dto: UpdateOrganizationDto) {
    return this.tenant.client.organization.update({
      where: { id: this.tenant.organizationId },
      data: dto,
    });
  }
}
