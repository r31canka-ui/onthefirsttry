import {
  CallHandler,
  ExecutionContext,
  ForbiddenException,
  Injectable,
  NestInterceptor,
  UnauthorizedException,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Observable, from } from 'rxjs';
import { lastValueFrom } from 'rxjs';
import { IS_PUBLIC_KEY } from '../common/decorators/public.decorator';
import { REQUIRED_PERMISSIONS_KEY } from '../common/decorators/require-permissions.decorator';
import { PrismaService } from '../prisma/prisma.service';
import { tenantAls, TenantStore } from './tenant-context';
import { PermissionKey } from '../../prisma/permissions';

export interface RequestUser {
  userId: string;
  organizationId: string;
  fullName: string;
  email: string;
  permissions: PermissionKey[];
}

/**
 * The single place tenant isolation and RBAC are enforced for every
 * authenticated request. Order matters and is deliberate:
 *
 * 1. Skip entirely for @Public() routes (register/login/magic-link) -
 *    those have no organization context yet and use AuthPrismaService.
 * 2. Open one Postgres transaction for the whole request and run
 *    `SET LOCAL app.current_org_id` on it. Every query any service makes
 *    for the rest of this request happens on this same transaction/
 *    connection, so RLS policies see the right tenant.
 * 3. Re-fetch the calling user's live status and permission set from the
 *    DB on every request (never trusted from the JWT) - so disabling a
 *    user or editing their role takes effect on their very next request,
 *    not after their token happens to expire.
 * 4. Enforce @RequirePermissions() metadata against that live set before
 *    the route handler runs at all.
 *
 * This runs as a Guard would, but a plain CanActivate can't wrap
 * next.handle() in a transaction (Guards can't hold open a scope around
 * downstream execution) - hence this is an interceptor.
 */
@Injectable()
export class TenantContextInterceptor implements NestInterceptor {
  constructor(
    private readonly prisma: PrismaService,
    private readonly reflector: Reflector,
  ) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) {
      return next.handle();
    }

    const request = context.switchToHttp().getRequest();
    const jwtUser = request.user as { userId: string; organizationId: string } | undefined;
    if (!jwtUser) {
      throw new UnauthorizedException();
    }

    const requiredPermissions = this.reflector.getAllAndOverride<PermissionKey[]>(
      REQUIRED_PERMISSIONS_KEY,
      [context.getHandler(), context.getClass()],
    ) ?? [];

    return from(
      this.prisma.$transaction(async (tx) => {
        await tx.$executeRaw`SELECT set_config('app.current_org_id', ${jwtUser.organizationId}, true)`;

        const store: TenantStore = { tx, organizationId: jwtUser.organizationId, userId: jwtUser.userId };
        return tenantAls.run(store, async () => {
          const user = await tx.user.findUnique({
            where: { id: jwtUser.userId },
            include: {
              userRoles: {
                include: { role: { include: { rolePermissions: { include: { permission: true } } } } },
              },
            },
          });

          if (!user || user.status !== 'active') {
            throw new UnauthorizedException('Account is not active.');
          }

          const permissions = Array.from(
            new Set(
              user.userRoles.flatMap((ur) =>
                ur.role.rolePermissions.map((rp) => rp.permission.key as PermissionKey),
              ),
            ),
          );

          const missing = requiredPermissions.filter((p) => !permissions.includes(p));
          if (missing.length > 0) {
            throw new ForbiddenException(`Missing required permission(s): ${missing.join(', ')}`);
          }

          store.permissions = permissions;

          request.user = {
            userId: user.id,
            organizationId: user.organizationId,
            fullName: user.fullName,
            email: user.email,
            permissions,
          } satisfies RequestUser;

          return lastValueFrom(next.handle());
        });
      }),
    );
  }
}
