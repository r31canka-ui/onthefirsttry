import {
  BadRequestException,
  ConflictException,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as argon2 from 'argon2';
import { authenticator } from 'otplib';
import { createHash, randomBytes } from 'node:crypto';
import { AuthPrismaService } from '../prisma/auth-prisma.service';
import { TenantPrismaService } from '../tenancy/tenant-prisma.service';
import { MailService } from './mail.service';
import { encryptSecret, decryptSecret } from '../common/crypto.util';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { DEFAULT_PIPELINE_STAGES } from './default-pipeline-stages';

function slugify(input: string): string {
  return input
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

function hashToken(token: string): string {
  return createHash('sha256').update(token).digest('hex');
}

const MAGIC_LINK_TTL_MS = 15 * 60 * 1000;
const TWO_FACTOR_PENDING_TTL = '5m';

@Injectable()
export class AuthService {
  constructor(
    private readonly authPrisma: AuthPrismaService,
    private readonly tenantPrisma: TenantPrismaService,
    private readonly jwt: JwtService,
    private readonly mail: MailService,
  ) {}

  async register(dto: RegisterDto) {
    const baseSlug = slugify(dto.organizationName) || 'clinic';
    let slug = baseSlug;
    for (let i = 1; await this.authPrisma.organization.findUnique({ where: { slug } }); i++) {
      slug = `${baseSlug}-${i}`;
    }

    const existingUser = await this.authPrisma.user.findUnique({ where: { email: dto.email } });
    if (existingUser) {
      throw new ConflictException('An account with that email already exists.');
    }

    const ownerRoleTemplate = await this.authPrisma.role.findFirst({
      where: { organizationId: null, isSystemDefault: true, name: 'Owner/Admin' },
    });
    if (!ownerRoleTemplate) {
      throw new BadRequestException('System roles are not seeded. Run `npm run prisma:seed`.');
    }

    const passwordHash = await argon2.hash(dto.password);

    const { organization, user } = await this.authPrisma.$transaction(async (tx) => {
      const organization = await tx.organization.create({
        data: {
          name: dto.organizationName,
          slug,
          countryCode: dto.countryCode.toUpperCase(),
        },
      });

      const user = await tx.user.create({
        data: {
          organizationId: organization.id,
          email: dto.email,
          passwordHash,
          fullName: dto.fullName,
          status: 'active',
        },
      });

      await tx.userRole.create({
        data: { userId: user.id, roleId: ownerRoleTemplate.id, organizationId: organization.id },
      });

      return { organization, user };
    });

    // Default pipeline stages are seeded per-org via the tenant-scoped
    // client (not authPrisma) since pipeline_stages is a normal
    // RLS-protected table and organizationId is now known.
    await this.tenantPrisma.withTenant(organization.id, user.id, async () => {
      await this.tenantPrisma.client.pipelineStage.createMany({
        data: DEFAULT_PIPELINE_STAGES.map((stage, index) => ({
          organizationId: organization.id,
          name: stage.name,
          position: index,
          isWonStage: stage.isWonStage ?? false,
        })),
      });
    });

    return this.issueAccessToken(user.id, organization.id);
  }

  async login(dto: LoginDto) {
    const user = await this.authPrisma.user.findUnique({ where: { email: dto.email } });
    if (!user || !user.passwordHash || user.status !== 'active') {
      throw new UnauthorizedException('Invalid email or password.');
    }

    const valid = await argon2.verify(user.passwordHash, dto.password);
    if (!valid) {
      throw new UnauthorizedException('Invalid email or password.');
    }

    if (user.twoFactorEnabled) {
      const tempToken = await this.jwt.signAsync(
        { sub: user.id, organizationId: user.organizationId, type: '2fa-pending' },
        { expiresIn: TWO_FACTOR_PENDING_TTL },
      );
      return { requiresTwoFactor: true, tempToken };
    }

    await this.authPrisma.user.update({ where: { id: user.id }, data: { lastLoginAt: new Date() } });
    return this.issueAccessToken(user.id, user.organizationId);
  }

  async verifyLoginTwoFactor(tempToken: string, code: string) {
    let payload: { sub: string; organizationId: string; type: string };
    try {
      payload = await this.jwt.verifyAsync(tempToken);
    } catch {
      throw new UnauthorizedException('That sign-in code has expired. Please log in again.');
    }
    if (payload.type !== '2fa-pending') {
      throw new UnauthorizedException();
    }

    const user = await this.authPrisma.user.findUnique({ where: { id: payload.sub } });
    if (!user || !user.twoFactorSecret) {
      throw new UnauthorizedException();
    }

    const secret = decryptSecret(user.twoFactorSecret);
    if (!authenticator.check(code, secret)) {
      throw new UnauthorizedException('Invalid two-factor code.');
    }

    await this.authPrisma.user.update({ where: { id: user.id }, data: { lastLoginAt: new Date() } });
    return this.issueAccessToken(user.id, user.organizationId);
  }

  async requestMagicLink(email: string): Promise<void> {
    const user = await this.authPrisma.user.findUnique({ where: { email } });
    // Deliberately generic: do not reveal whether an account exists.
    if (!user || user.status !== 'active') {
      return;
    }

    const rawToken = randomBytes(32).toString('base64url');
    await this.authPrisma.magicLinkToken.create({
      data: {
        userId: user.id,
        tokenHash: hashToken(rawToken),
        expiresAt: new Date(Date.now() + MAGIC_LINK_TTL_MS),
      },
    });

    const appUrl = process.env.APP_URL ?? 'http://localhost:3000';
    await this.mail.sendMagicLink(email, `${appUrl}/auth/magic-link?token=${rawToken}`);
  }

  async verifyMagicLink(rawToken: string) {
    const tokenHash = hashToken(rawToken);
    const record = await this.authPrisma.magicLinkToken.findUnique({ where: { tokenHash } });
    if (!record || record.usedAt || record.expiresAt < new Date()) {
      throw new UnauthorizedException('This link is invalid or has expired.');
    }

    const user = await this.authPrisma.user.findUnique({ where: { id: record.userId } });
    if (!user || user.status !== 'active') {
      throw new UnauthorizedException('This link is invalid or has expired.');
    }

    await this.authPrisma.magicLinkToken.update({
      where: { id: record.id },
      data: { usedAt: new Date() },
    });

    if (user.twoFactorEnabled) {
      const tempToken = await this.jwt.signAsync(
        { sub: user.id, organizationId: user.organizationId, type: '2fa-pending' },
        { expiresIn: TWO_FACTOR_PENDING_TTL },
      );
      return { requiresTwoFactor: true, tempToken };
    }

    await this.authPrisma.user.update({ where: { id: user.id }, data: { lastLoginAt: new Date() } });
    return this.issueAccessToken(user.id, user.organizationId);
  }

  async setupTwoFactor(userId: string, email: string) {
    const secret = authenticator.generateSecret();
    await this.tenantPrisma.client.user.update({
      where: { id: userId },
      data: { twoFactorSecret: encryptSecret(secret) },
    });
    const otpauthUrl = authenticator.keyuri(email, 'Clinic CRM', secret);
    return { secret, otpauthUrl };
  }

  async enableTwoFactor(userId: string, code: string) {
    const user = await this.tenantPrisma.client.user.findUniqueOrThrow({ where: { id: userId } });
    if (!user.twoFactorSecret) {
      throw new BadRequestException('Call /auth/2fa/setup first.');
    }
    const secret = decryptSecret(user.twoFactorSecret);
    if (!authenticator.check(code, secret)) {
      throw new BadRequestException('Invalid code.');
    }
    await this.tenantPrisma.client.user.update({
      where: { id: userId },
      data: { twoFactorEnabled: true },
    });
  }

  private async issueAccessToken(userId: string, organizationId: string) {
    const accessToken = await this.jwt.signAsync({ sub: userId, organizationId });
    return { accessToken };
  }
}
