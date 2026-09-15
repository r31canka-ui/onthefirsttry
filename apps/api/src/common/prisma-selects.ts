import { Prisma } from '@prisma/client';

/**
 * Every place a User is nested into another entity's response (contact
 * activity author, appointment provider, staff assignment, etc.) must use
 * this instead of `include: { user: true }` / `select: true` - otherwise
 * passwordHash and the encrypted twoFactorSecret get serialized straight
 * into the API response.
 */
export const USER_SAFE_SELECT = {
  id: true,
  fullName: true,
  email: true,
  phone: true,
  status: true,
  twoFactorEnabled: true,
  lastLoginAt: true,
  createdAt: true,
  updatedAt: true,
  organizationId: true,
} satisfies Prisma.UserSelect;
