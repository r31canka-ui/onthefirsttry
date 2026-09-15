import { Injectable, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

/**
 * Connects as `clinic_crm_auth` (BYPASSRLS, narrowly GRANTed - see
 * prisma/roles.sql). Used ONLY by AuthService, ONLY for the identity
 * resolution steps that must run before an organization_id is known:
 * find-user-by-email (login, magic link) and organization+owner creation
 * (registration). Never import this into any other module.
 */
@Injectable()
export class AuthPrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  constructor() {
    super({ datasourceUrl: process.env.AUTH_DATABASE_URL });
  }

  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
