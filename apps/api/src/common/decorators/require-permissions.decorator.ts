import { SetMetadata } from '@nestjs/common';
import { PermissionKey } from '../../../prisma/permissions';

export const REQUIRED_PERMISSIONS_KEY = 'requiredPermissions';

/** Requires the caller to hold ALL of the given permissions (resolved live from DB per request, not from the JWT). */
export const RequirePermissions = (...permissions: PermissionKey[]) =>
  SetMetadata(REQUIRED_PERMISSIONS_KEY, permissions);
