import { Global, Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { TenantPrismaService } from './tenant-prisma.service';
import { TenantContextInterceptor } from './tenant-context.interceptor';

@Global()
@Module({
  providers: [
    TenantPrismaService,
    { provide: APP_INTERCEPTOR, useClass: TenantContextInterceptor },
  ],
  exports: [TenantPrismaService],
})
export class TenancyModule {}
