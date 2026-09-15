import { BadRequestException, ConflictException, Injectable, NotFoundException, UnauthorizedException } from '@nestjs/common';
import * as argon2 from 'argon2';
import { createHash, randomBytes } from 'node:crypto';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { AuthPrismaService } from '../prisma/auth-prisma.service';
import { MailService } from '../auth/mail.service';
import { USER_SAFE_SELECT } from '../common/prisma-selects';
import { InviteStaffDto, UpdateStaffDto, AcceptInviteDto } from './dto/staff.dto';

const INVITE_TTL_MS = 7 * 24 * 60 * 60 * 1000;

function hashToken(token: string): string {
  return createHash('sha256').update(token).digest('hex');
}

@Injectable()
export class StaffService {
  constructor(
    private readonly tenant: TenantPrismaService,
    private readonly authPrisma: AuthPrismaService,
    private readonly mail: MailService,
  ) {}

  list() {
    return this.tenant.client.user.findMany({
      where: { organizationId: this.tenant.organizationId },
      select: {
        ...USER_SAFE_SELECT,
        userRoles: { include: { role: true } },
        staffLocations: { include: { location: true } },
      },
      orderBy: { fullName: 'asc' },
    });
  }

  async findOne(id: string) {
    const user = await this.tenant.client.user.findFirst({
      where: { id, organizationId: this.tenant.organizationId },
      select: {
        ...USER_SAFE_SELECT,
        userRoles: { include: { role: true } },
        staffLocations: { include: { location: true } },
      },
    });
    if (!user) {
      throw new NotFoundException('Staff member not found.');
    }
    return user;
  }

  async invite(dto: InviteStaffDto) {
    const existing = await this.tenant.client.user.findUnique({ where: { email: dto.email } });
    if (existing) {
      throw new ConflictException('A user with that email already exists.');
    }

    const roles = await this.tenant.client.role.findMany({
      where: { id: { in: dto.roleIds }, OR: [{ organizationId: this.tenant.organizationId }, { organizationId: null }] },
    });
    if (roles.length !== dto.roleIds.length) {
      throw new BadRequestException('One or more role IDs are invalid.');
    }

    const user = await this.tenant.client.user.create({
      data: {
        organizationId: this.tenant.organizationId,
        email: dto.email,
        fullName: dto.fullName,
        status: 'invited',
        userRoles: {
          create: roles.map((r) => ({ roleId: r.id, organizationId: this.tenant.organizationId })),
        },
        staffLocations: dto.locationIds
          ? { create: dto.locationIds.map((locationId) => ({ locationId })) }
          : undefined,
      },
      select: USER_SAFE_SELECT,
    });

    const rawToken = randomBytes(32).toString('base64url');
    await this.tenant.client.magicLinkToken.create({
      data: {
        userId: user.id,
        tokenHash: hashToken(rawToken),
        expiresAt: new Date(Date.now() + INVITE_TTL_MS),
      },
    });

    const appUrl = process.env.APP_URL ?? 'http://localhost:3000';
    await this.mail.sendStaffInvite(dto.email, `${appUrl}/auth/accept-invite?token=${rawToken}`);

    return user;
  }

  async update(id: string, dto: UpdateStaffDto) {
    await this.findOne(id);
    return this.tenant.client.user.update({
      where: { id },
      data: {
        fullName: dto.fullName,
        phone: dto.phone,
        ...(dto.locationIds && {
          staffLocations: {
            deleteMany: {},
            create: dto.locationIds.map((locationId) => ({ locationId })),
          },
        }),
      },
      select: USER_SAFE_SELECT,
    });
  }

  async disable(id: string) {
    await this.findOne(id);
    await this.tenant.client.user.update({ where: { id }, data: { status: 'disabled' } });
  }

  async addRole(id: string, roleId: string) {
    await this.findOne(id);
    const role = await this.tenant.client.role.findFirst({
      where: { id: roleId, OR: [{ organizationId: this.tenant.organizationId }, { organizationId: null }] },
    });
    if (!role) {
      throw new BadRequestException('Invalid role ID.');
    }
    await this.tenant.client.userRole.upsert({
      where: { userId_roleId: { userId: id, roleId } },
      update: {},
      create: { userId: id, roleId, organizationId: this.tenant.organizationId },
    });
  }

  async removeRole(id: string, roleId: string) {
    await this.findOne(id);
    await this.tenant.client.userRole.deleteMany({ where: { userId: id, roleId } });
  }

  async acceptInvite(dto: AcceptInviteDto) {
    const tokenHash = hashToken(dto.token);
    const record = await this.authPrisma.magicLinkToken.findUnique({ where: { tokenHash } });
    if (!record || record.usedAt || record.expiresAt < new Date()) {
      throw new UnauthorizedException('This invite link is invalid or has expired.');
    }

    const passwordHash = await argon2.hash(dto.password);

    await this.authPrisma.$transaction([
      this.authPrisma.user.update({
        where: { id: record.userId },
        data: { passwordHash, status: 'active' },
      }),
      this.authPrisma.magicLinkToken.update({
        where: { id: record.id },
        data: { usedAt: new Date() },
      }),
    ]);

    return { message: 'Account activated. You can now log in.' };
  }
}
