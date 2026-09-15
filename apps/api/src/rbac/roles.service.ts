import { BadRequestException, Injectable, NotFoundException } from '@nestjs/common';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { CreateRoleDto, UpdateRoleDto } from './dto/role.dto';

@Injectable()
export class RolesService {
  constructor(private readonly tenant: TenantPrismaService) {}

  listPermissions() {
    return this.tenant.client.permission.findMany({ orderBy: { key: 'asc' } });
  }

  listRoles() {
    // RLS already restricts to this org's rows + system-default (org_id
    // IS NULL) templates, since @@map("roles") carries that policy.
    return this.tenant.client.role.findMany({
      include: { rolePermissions: { include: { permission: true } } },
      orderBy: { name: 'asc' },
    });
  }

  async createRole(dto: CreateRoleDto) {
    const permissions = await this.tenant.client.permission.findMany({
      where: { key: { in: dto.permissionKeys } },
    });
    if (permissions.length !== dto.permissionKeys.length) {
      throw new BadRequestException('One or more permission keys are invalid.');
    }

    return this.tenant.client.role.create({
      data: {
        name: dto.name,
        organizationId: this.tenant.organizationId,
        rolePermissions: { create: permissions.map((p) => ({ permissionId: p.id })) },
      },
      include: { rolePermissions: { include: { permission: true } } },
    });
  }

  private async getOwnRoleOrThrow(id: string) {
    const role = await this.tenant.client.role.findUnique({ where: { id } });
    if (!role || role.organizationId !== this.tenant.organizationId) {
      throw new NotFoundException('Role not found.');
    }
    if (role.isSystemDefault) {
      throw new BadRequestException('System default roles cannot be modified.');
    }
    return role;
  }

  async updateRole(id: string, dto: UpdateRoleDto) {
    await this.getOwnRoleOrThrow(id);

    if (dto.permissionKeys) {
      const permissions = await this.tenant.client.permission.findMany({
        where: { key: { in: dto.permissionKeys } },
      });
      if (permissions.length !== dto.permissionKeys.length) {
        throw new BadRequestException('One or more permission keys are invalid.');
      }
      await this.tenant.client.rolePermission.deleteMany({ where: { roleId: id } });
      await this.tenant.client.rolePermission.createMany({
        data: permissions.map((p) => ({ roleId: id, permissionId: p.id })),
      });
    }

    return this.tenant.client.role.update({
      where: { id },
      data: dto.name ? { name: dto.name } : {},
      include: { rolePermissions: { include: { permission: true } } },
    });
  }

  async deleteRole(id: string) {
    await this.getOwnRoleOrThrow(id);
    const assignedCount = await this.tenant.client.userRole.count({ where: { roleId: id } });
    if (assignedCount > 0) {
      throw new BadRequestException('Cannot delete a role that is still assigned to staff.');
    }
    await this.tenant.client.role.delete({ where: { id } });
  }
}
