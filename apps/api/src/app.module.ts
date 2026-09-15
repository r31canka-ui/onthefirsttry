import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerGuard, ThrottlerModule } from '@nestjs/throttler';
import { PrismaModule } from './prisma/prisma.module';
import { TenancyModule } from './tenancy/tenancy.module';
import { AuditModule } from './audit/audit.module';
import { AuthModule } from './auth/auth.module';
import { JwtAuthGuard } from './auth/jwt-auth.guard';
import { OrganizationsModule } from './organizations/organizations.module';
import { LocationsModule } from './locations/locations.module';
import { StaffModule } from './staff/staff.module';
import { RbacModule } from './rbac/rbac.module';
import { PipelineStagesModule } from './pipeline-stages/pipeline-stages.module';
import { ContactsModule } from './contacts/contacts.module';
import { ServicesModule } from './services/services.module';
import { AppointmentsModule } from './appointments/appointments.module';
import { DashboardModule } from './dashboard/dashboard.module';
import { SearchModule } from './search/search.module';

@Module({
  imports: [
    ThrottlerModule.forRoot([{ ttl: 60_000, limit: 120 }]),
    PrismaModule,
    TenancyModule,
    AuditModule,
    AuthModule,
    OrganizationsModule,
    LocationsModule,
    StaffModule,
    RbacModule,
    PipelineStagesModule,
    ContactsModule,
    ServicesModule,
    AppointmentsModule,
    DashboardModule,
    SearchModule,
  ],
  providers: [
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: APP_GUARD, useClass: ThrottlerGuard },
  ],
})
export class AppModule {}
