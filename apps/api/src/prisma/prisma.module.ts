import { Global, Module } from '@nestjs/common';
import { PrismaService } from './prisma.service';
import { AuthPrismaService } from './auth-prisma.service';

@Global()
@Module({
  providers: [PrismaService, AuthPrismaService],
  exports: [PrismaService, AuthPrismaService],
})
export class PrismaModule {}
